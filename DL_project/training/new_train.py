#!/usr/bin/env python3
import os
import sys
import time
import copy
import ctypes
import gc
import json
import re
from datetime import datetime

from pandas import read_csv
import torch

# Flush denormals to zero, before anything creates a thread. A block that loses its job
# mid-run (the protein FFN under --lipid_path_handicap, say) is shrunk geometrically by
# the coupled weight decay in Adam until its weights fall under 2^-126, where x86 stops
# handling them in the vector units and traps into a microcode assist: measured here at
# 2587 ms against 6 ms for one 256x256 matmul of an epoch-51 checkpoint, and 85 s -> 550 s
# per epoch across a run. The block contributes 2.4e-07 of its residual by then, so the
# arithmetic being skipped changes nothing -- the FFN's output came out bit-identical
# with the flag on. Order matters: MXCSR is per-thread and pthread_create copies the
# creating thread's floating-point environment, so intra-op workers spawned later
# inherit this, while setting it after the pool exists leaves them on the slow path.
torch.set_flush_denormal(True)

import torch.nn.functional as F
import torch_geometric
from torch.optim.swa_utils import AveragedModel, SWALR
from torch.utils.tensorboard import SummaryWriter

TRAINING_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, TRAINING_DIR)
sys.path.insert(0, PROJECT_ROOT)

from read_configuration import read_configuration
from append_metric_to_table import append_metric
from architecture.final_layer import chem_adversary_loss, family_dann_loss
from architecture.interaction_classification import InteractionClassification
from architecture.mlp_utils import (
    collect_sparsity_penalty,
    export_surviving_structure,
    collect_gate_parameters,
    collect_concrete_dropout_reg,
    ConcreteDropout,
)
from architecture.loss import (
    GRAB_loss,
    Non_Negative_Positive_Unlabeled_loss,
    focal_loss,
    get_pu_loss_diagnostics,
    logit_adjustment_bias,
    pairwise_ranking_loss,
    reset_pu_loss_diagnostics,
)
from dataloader.sampler import ClassBalancedBatchSampler
from dataloader.dataset_source import interaction_csv_path
from dataloader.New_dataloader import PLIDataset
from candidate_averaging import (
    CandidateAccumulator,
    average_candidate_predictions,
)
from reproducibility import seed_everything, seed_worker, seeded_generator
from run_metrics import (
    RUN_METRIC_FIELDS,
    metric_has_positive_trend,
    rolling_metric_mean,
    summarize_training_run,
)


conf = read_configuration()
if conf.final_m is None:
    conf.final_m = conf.m

seed_everything(conf.seed)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print()

path=os.path.join(PROJECT_ROOT, "data") + os.sep

csv = read_csv(interaction_csv_path(path))

train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir=path, csv = csv, seed=conf.seed,excluded_subgroups=conf.excluded_subgroups, config=conf, excluded_groups=conf.excluded_groups)
del csv
# Model construction stays after the split so frozen normalization cannot see
# validation/test proteins.
model = InteractionClassification(conf)
if conf.rnabang_frozen_node_adapter:
    model.set_pocket_descriptor_normalization(
        train_dataset.pocket_descriptor_stats()
    )
    model.set_rnabang_normalization(
        train_dataset.rnabang_normalization_stats()
    )
if conf.pair_descriptor_pocket_shares_split:
    model.set_pair_descriptor_pocket_share_normalization(
        train_dataset.pocket_descriptor_stats()
    )
model = model.to(device)
number_of_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"number of parameters : {number_of_parameters}")
common_weights_parts = []
if conf.tanimoto_weight:
    common_weights_parts.append(train_dataset.get_tanimoto_weights().to(device))
if conf.protein_group_weight:
    protein_group_weights = train_dataset.get_protein_weights().to(device)
    common_weights_parts.append(protein_group_weights)
if conf.protein_balance_weight:
    common_weights_parts.append(
        train_dataset.get_protein_balance_weights().to(device)
    )
if conf.protein_class_weight:
    protein_class_weights = train_dataset.get_protein_class_weights().to(device)
    common_weights_parts.append(protein_class_weights)
if conf.protein_class_sqrt_weight:
    protein_class_sqrt_weights = train_dataset.get_protein_class_weights(
        square_root=True,
    ).to(device)
    common_weights_parts.append(protein_class_sqrt_weights)
if conf.lipid_propensity_weight:
    common_weights_parts.append(
        train_dataset.get_lipid_propensity_weights().to(device)
    )
common_weights = (
    torch.stack(common_weights_parts).mean(dim=0)
    if common_weights_parts
    else None
)


def batch_sample_weights(prot, sample_count):
    """Per-row loss weights for this batch, or None when the run weights nothing.

    None rather than a vector of ones. Every loss below already has a None branch that
    takes the plain mean, and that is the *same number*: multiplying by 1.0 is exact in
    IEEE 754, so `(x * ones).sum() / ones.sum().clamp_min(1e-8)` and `x.mean()` agree bit
    for bit -- checked over 8000 random batches at sizes 8, 16, 64 and 1300, zero
    disagreements. What it removes is a weight vector as long as the train split, a
    gather per batch, an elementwise multiply and a second reduction, none of which could
    ever change an unweighted run's result.

    Only reachable from the training loop. Validation and test never pass sample weights,
    which matters because id2pos covers train rows alone: a validation row's tanimoto_pos
    is -1, and -1 indexes the last weight instead of raising.
    """
    if common_weights is None:
        return None
    pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
    if pos.shape[0] != sample_count:
        raise ValueError(
            f"tanimoto positions count {pos.shape[0]} "
            f"does not match batch size {sample_count}"
        )
    if (pos < 0).any() or (pos >= common_weights.shape[0]).any():
        invalid_positions = pos[
            (pos < 0) | (pos >= common_weights.shape[0])
        ].detach().cpu().tolist()
        raise ValueError(
            "tanimoto positions are outside the train weight table: "
            f"{invalid_positions}"
        )
    return common_weights[pos]
train_labels = torch.as_tensor(train_dataset.csvtrain["Interaction"].values, dtype=torch.long)
class_counts = torch.bincount(train_labels, minlength=2).float()
if conf.pu_loss:
    conf.pu_rho = conf.effective_pu_rho(
        positive_count=class_counts[1].item(),
        unlabeled_count=class_counts[0].item(),
    )
    print(f"PU rho : {conf.pu_rho:.6f}")
class_weights = None
if conf.class_weights:
    class_weights = (
        class_counts.sum() / (2.0 * class_counts.clamp_min(1.0))
    ).to(device)
    print(f"class weights : {class_weights.detach().cpu().tolist()}")
else:
    print("class weights : disabled")

logit_adjustment_bias_tensor = None
if conf.logit_adjustment:
    logit_adjustment_bias_tensor = logit_adjustment_bias(
        class_counts, tau=conf.logit_adjustment_tau
    ).to(device)
    print(f"logit adjustment bias : {logit_adjustment_bias_tensor.detach().cpu().tolist()}")


loader_kwargs = {
        "batch_size": conf.batch,
        "shuffle": True,
        # Pinned memory only buys the async host-to-device copy; with no accelerator
        # PyTorch ignores the request and warns once per loader, so ask for it only on
        # CUDA. Same tensors either way.
        "pin_memory": device.type == "cuda",
        "num_workers": conf.num_workers,
        "persistent_workers": conf.num_workers > 0,
        "worker_init_fn": seed_worker,
        }
if conf.num_workers > 0:
    loader_kwargs["prefetch_factor"] = 4

# A batch_sampler carries batch composition itself, so batch_size/shuffle must
# not be passed alongside it.
train_loader_kwargs = dict(loader_kwargs)
if conf.balanced_batches:
    del train_loader_kwargs["batch_size"], train_loader_kwargs["shuffle"]
    train_loader_kwargs["batch_sampler"] = ClassBalancedBatchSampler(
        train_labels,
        conf.batch,
        generator=seeded_generator(conf.seed),
    )
    # What the batches actually hold, not what --batch asked for. The sampler covers
    # every row once per epoch and takes its batch count from the LARGER class, so equal
    # pools give batch//2 of each and unequal pools give batch//2 of the larger class and
    # proportionally less of the smaller: at negatives_per_positive=2 a --batch=8 run
    # yields about 2 positive + 4 unlabeled, not 4 + 4. Printing the requested split
    # instead of the real one made the log say 4 + 4 regardless.
    _sampler = train_loader_kwargs["batch_sampler"]
    _positives = int(_sampler.positive_indices.numel())
    _unlabeled = int(_sampler.unlabeled_indices.numel())
    print(
        f"balanced batches : {len(_sampler)} per epoch "
        f"covering all {train_labels.numel()} train rows, "
        f"{_positives / len(_sampler):.1f} positive + "
        f"{_unlabeled / len(_sampler):.1f} unlabeled per batch "
        f"({(_positives + _unlabeled) / len(_sampler):.1f} rows, --batch={conf.batch})"
    )

train_loader = torch_geometric.loader.DataLoader(
        train_dataset,
        generator=seeded_generator(conf.seed),
        **train_loader_kwargs,
        )
valid_loader = torch_geometric.loader.DataLoader(
        valid_dataset,
        generator=seeded_generator(conf.seed + 1),
        **loader_kwargs,
        )
test_loader = torch_geometric.loader.DataLoader(
        test_dataset,
        generator=seeded_generator(conf.seed + 2),
        **loader_kwargs,
        )
# Build every protein graph and lipid encoding once, here, so the DataLoader workers
# fork with the caches already filled and share them copy-on-write instead of each
# rebuilding its own during the first epoch.
cache_counts = train_dataset.warm_caches(train_dataset.csvt)
released_artifacts = set()
for dataset in (train_dataset, valid_dataset, test_dataset):
    released_artifacts.update(dataset.release_source_artifacts())
print(
    f"cache warmed : {cache_counts['proteins']} proteins, "
    f"{cache_counts['lipid_encodings']} lipid encodings, "
    f"{cache_counts['lipid_graphs']} lipid graphs, "
    f"{train_dataset.cache_memory_bytes() / 2**20:.0f} MiB"
)
print(f"source artifacts released : {sorted(released_artifacts)}")


def _return_freed_heap_to_kernel():
    """Hand the heap freed by release_source_artifacts() back to the OS.

    Releasing those artifacts drops the Python references, but glibc keeps the pages
    in the process heap instead of returning them, so RSS stays far above what the
    run actually holds: measured here, 738 MiB of private heap against 89 MiB of
    live caches, the difference being mostly the 280 MB SMILES embedding pickle
    that was read, consumed and released during __init__. Four concurrent jobs
    carry that four times over on a 13 GiB machine, which is the difference between
    fitting in RAM and paging to disk.

    Pure bookkeeping: nothing is read, written, moved or recomputed, so every number
    the run produces is bit-identical with or without this. Non-glibc systems (musl,
    macOS) have no malloc_trim and simply skip it.
    """
    gc.collect()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except (OSError, AttributeError):
        return False
    return True


_return_freed_heap_to_kernel()
train_batches_to_run = min(len(train_loader), (1740 + conf.batch - 1) // conf.batch)
valid_batches_to_run = len(valid_loader)
test_batches_to_run = len(test_loader)
print("data extracted")
# Parameter split for bilevel width search. Gate params (lambda) are optimized on the
# validation split; theta (weights) on train. ConcreteDropout logits are trained on the
# train objective (like theta) but always excluded from weight decay.
gate_params = collect_gate_parameters(model)
gate_param_ids = {id(p) for p in gate_params}
dropout_logit_params = [
    module.logit for module in model.modules() if isinstance(module, ConcreteDropout)
]
dropout_logit_ids = {id(p) for p in dropout_logit_params}
theta_params = [
    p
    for p in model.parameters()
    if id(p) not in gate_param_ids and id(p) not in dropout_logit_ids
]

lipid_branch_param_ids = (
    {id(p) for p in model.lipid_branch_parameters()}
    if conf.lipid_path_handicap
    else set()
)


def split_lipid_branch(groups):
    """Give the lipid branch its own optimizer group so its lr can be handicapped.

    Splitting by PARAMETER, not by a hook on the graph, is what makes the handicap
    stay off the protein: past cross-attention the lipid activations are a function of
    both partners, so anything attached there would slow the protein encoder too. Each
    split group inherits its parent's settings (weight decay above all) and differs
    only in lr, and is tagged so apply_lipid_path_handicap can find it again.
    """
    if not lipid_branch_param_ids:
        return groups
    split = []
    for group in groups:
        lipid = [p for p in group["params"] if id(p) in lipid_branch_param_ids]
        rest = [p for p in group["params"] if id(p) not in lipid_branch_param_ids]
        if rest:
            split.append({**group, "params": rest})
        if lipid:
            split.append({**group, "params": lipid, "lipid_branch": True})
    return split


hyper_optimizer = None
if conf.bilevel and gate_params:
    # theta (with weight decay) + dropout logits (no weight decay) on train; the main
    # optimizer never touches the gate params -- those are stepped on validation below.
    main_groups = [{"params": theta_params, "weight_decay": conf.weight_decay}]
    if dropout_logit_params:
        main_groups.append({"params": dropout_logit_params, "weight_decay": 0.0})
    optimizer = torch.optim.Adam(split_lipid_branch(main_groups), lr=conf.lr)
    hyper_optimizer = torch.optim.Adam(gate_params, lr=conf.bilevel_lr)
elif dropout_logit_params:
    # Not bilevel: everything trains on the train objective, but keep dropout logits out
    # of weight decay. Gates (if any) are learned via the train-loss penalty below.
    optimizer = torch.optim.Adam(
        split_lipid_branch(
            [
                {
                    "params": theta_params + gate_params,
                    "weight_decay": conf.weight_decay,
                },
                {"params": dropout_logit_params, "weight_decay": 0.0},
            ]
        ),
        lr=conf.lr,
    )
else:
    optimizer = torch.optim.Adam(
        split_lipid_branch([{"params": list(model.parameters())}]),
        lr=conf.lr,
        weight_decay=conf.weight_decay,
    )


# Rewritten at the top of every epoch from conf.ramped_lipid_path_weight; defined here
# so the TensorBoard logger has it whatever order the first epoch runs in.
lipid_path_weight_now = conf.lipid_path_weight
# Resolved once. param_groups is a stable list of stable dicts, so holding the dicts
# themselves saves rescanning it on every epoch and every log line, and keeps the
# handicap's two call sites from each re-deriving which group is which.
lipid_lr_groups = [g for g in optimizer.param_groups if g.get("lipid_branch")]
lipid_lr_reference = next(
    (g for g in optimizer.param_groups if not g.get("lipid_branch")), None
)


def apply_lipid_path_handicap(weight):
    """Set the lipid branch's lr to ``weight`` times the rest of the model's.

    Read off a sibling group rather than off conf.lr so whatever the lr schedule has
    done this epoch is inherited: lr_warmup_cosine rewrites every group's lr from its
    own previous value, so anchoring to conf.lr would silently undo the warm-up and the
    cosine decay for the lipid branch alone. Called at the top of each epoch, after the
    previous epoch's scheduler step.
    """
    for group in lipid_lr_groups:
        group["lr"] = lipid_lr_reference["lr"] * weight


def _endless_batches(loader):
    """Yield validation batches forever for the bilevel lambda step."""
    while True:
        for batch in loader:
            yield batch


hyper_val_iter = _endless_batches(valid_loader) if hyper_optimizer is not None else None

use_amp = conf.type_opt and device.type == "cuda"
scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

lr_scheduler = None
if conf.lr_warmup_cosine:
    warmup_epochs = min(conf.lr_warmup_epochs, max(conf.ep - 1, 0))
    cosine_epochs = max(conf.ep - warmup_epochs, 1)
    cosine_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cosine_epochs, eta_min=conf.lr * conf.lr_min_factor
    )
    if warmup_epochs > 0:
        lr_scheduler = torch.optim.lr_scheduler.SequentialLR(
            optimizer,
            schedulers=[
                torch.optim.lr_scheduler.LinearLR(
                    optimizer, start_factor=0.1, total_iters=warmup_epochs
                ),
                cosine_scheduler,
            ],
            milestones=[warmup_epochs],
        )
    else:
        lr_scheduler = cosine_scheduler

swa_model = None
swa_scheduler = None
swa_start_epoch = None
if conf.swa:
    swa_model = AveragedModel(model)
    swa_scheduler = SWALR(
        optimizer,
        swa_lr=conf.swa_lr if conf.swa_lr is not None else conf.lr * conf.lr_min_factor,
    )
    swa_start_epoch = int(conf.ep * conf.swa_start_frac)

SAFE_PATH_PART = re.compile(r"[^A-Za-z0-9._=-]+")
config_name = f"{'addLayers' if conf.third_layers_in_mlps else 'base'}_{'protSA' if conf.protein_self_attention else ''}_{'lipSA' if conf.lipid_self_attention else ''}_{'CA' if conf.cross_attention else ''}_{'doubleAtt' if conf.double_attention else ''}_{'protPosBias' if conf.prot_attention_pos_bias else ''}"
raw_label = conf.label.strip()
if not raw_label:
    oar_job_name = os.environ.get("OAR_JOB_NAME", "").strip()
    if oar_job_name:
        group_suffix = (
            r"_(CRAL-TRIO|START|lipocalin|GLTP|IP_trans|"
            r"LBP_BPI_CETP|scp2|ML|OSBP)_s-?\d+$"
        )
        raw_label = re.sub(group_suffix, "", oar_job_name)
    else:
        raw_label = config_name
label_name = SAFE_PATH_PART.sub("_", raw_label).strip("._")
if not label_name:
    raise ValueError(f"Invalid label value: {raw_label!r}")
conf.label = label_name
excluded_set_parts = []
if conf.excluded_groups:
    excluded_set_parts.append("groups_" + "-".join(conf.excluded_groups))
if conf.lipid_coldsplit:
    # Under --lipid_coldsplit no protein group is excluded, so without this every set
    # would land in the same "random" directory: four different experiments sharing one
    # test_metrics folder, and a progress table that cannot tell their event files apart
    # and reports n/a for all of them. The "groups_" prefix is deliberate even though a
    # lipid set is not a protein group -- it is the prefix every consumer of this path
    # already keys on (the progress table's dirs_by_set, list_completed_experiments,
    # build_metrics_table, the plotting scripts), and what the directory really names is
    # the exclusion set, whichever axis it lies on.
    excluded_set_parts.append("groups_" + conf.lipid_coldsplit)
if conf.excluded_subgroups:
    excluded_set_parts.append("subgroups_" + "-".join(conf.excluded_subgroups))
excluded_set_name = "_".join(excluded_set_parts) if excluded_set_parts else "random"
artifact_root = os.path.join(PROJECT_ROOT, "testmode_outputs") if conf.testmode else PROJECT_ROOT
run_root = os.path.join(artifact_root, "run")
test_metrics_root = os.path.join(artifact_root, "test_metrics")
checkpoints_root = os.path.join(artifact_root, "checkpoints")
models_root = os.path.join(artifact_root, "models")
metrics_table_path = os.path.join(artifact_root, "metrics_summary.csv")
while True:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = os.path.join(
        run_root,
        label_name,
        excluded_set_name,
        f'train{timestamp}_{number_of_parameters}parameters_{conf.m}_{conf.HEADS}_{conf.seed}_{conf.lr}_{conf.batch}_{conf.hiddim}',
    )
    try:
        os.makedirs(log_dir, exist_ok=False)
        break
    except FileExistsError:
        time.sleep(1)
test_metrics_dir = os.path.join(test_metrics_root, label_name, excluded_set_name)
os.makedirs(test_metrics_dir, exist_ok=True)
writer_tb = SummaryWriter(log_dir)
TENSORBOARD_FLUSH_EVERY_EPOCHS = 5

sig=torch.nn.Sigmoid()

def safe_div(num, denom):
    """Divide two values and return None for a zero denominator."""
    return None if denom == 0 else num / denom

def format_metric(value):
    """Format an optional metric for logs and report files."""
    return "undefined" if value is None else f"{value:.6f}"

def metric_values(tp, fp, tn, fn, total_loss, total_loss_count):
    """Compute aggregate binary-classification metrics from confusion counts."""
    sensitivity = safe_div(tp, tp + fn)
    specificity = safe_div(tn, tn + fp)
    return {
        "total": tp + fp + tn + fn,
        "real_positive": tp + fn,
        "real_negative": tn + fp,
        "predicted_positive": tp + fp,
        "predicted_negative": tn + fn,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "accuracy": safe_div(tp + tn, tp + fp + tn + fn),
        "sensitivity": sensitivity,
        "precision": safe_div(tp, tp + fp),
        "specificity": specificity,
        "IoU": safe_div(tp, tp + fp + fn),
        "FAR": safe_div(fp, fp + tn),
        "F1": safe_div(2 * tp, 2 * tp + fp + fn),
        "balanced_accuracy": None if sensitivity is None or specificity is None else (sensitivity + specificity) / 2,
        "loss": safe_div(total_loss, total_loss_count),
    }

def update_aggregate(
    stats,
    pred_class,
    labels,
    loss,
    sample_count,
    loss_count=None,
):
    """Accumulate confusion counts and sample-weighted loss for one batch."""
    if loss_count is None:
        loss_count = sample_count
    # Two comparisons and three reductions instead of eight and four. Predictions come
    # from argmax over two classes, so "predicted positive" and "correct" each split the
    # batch in two and the four cells are fixed by three of them:
    #   predicted positives = TP + FP,  correct = TP + TN,  batch = TP + FP + TN + FN.
    # Pure integer counting, so this is the same arithmetic identity either way -- there
    # is no rounding here to preserve, only work to skip.
    correct = pred_class == labels
    predicted_positive = pred_class == 1
    true_positive = int((correct & predicted_positive).sum())
    false_positive = int(predicted_positive.sum()) - true_positive
    true_negative = int(correct.sum()) - true_positive
    stats["TP"] += true_positive
    stats["FP"] += false_positive
    stats["TN"] += true_negative
    stats["FN"] += (
        pred_class.numel() - true_positive - false_positive - true_negative
    )
    stats["loss"] += (
        loss.item() if isinstance(loss, torch.Tensor) else loss
    ) * loss_count
    stats["count"] += sample_count
    stats["loss_count"] += loss_count


def aggregate_values(stats):
    """Convert accumulated counts and loss into aggregate metrics."""
    return metric_values(
        stats["TP"],
        stats["FP"],
        stats["TN"],
        stats["FN"],
        stats["loss"],
        stats["loss_count"],
    )


def log_epoch_metrics(writer, epoch_index, mode, metrics):
    """Write aggregate epoch metrics to TensorBoard."""
    for key in ("accuracy", "sensitivity", "precision", "specificity", "F1", "balanced_accuracy", "loss"):
        value = metrics.get(key)
        if value is not None:
            writer.add_scalar(f"epoch/{mode} {key}", value, epoch_index + 1)


def log_adversary_metrics(writer, epoch_index, stats):
    """Write the epoch's mean adversary penalties, plus the reversal strengths in force.

    Read the losses as leakage gauges, not as objectives. Each per-partner adversary is
    a 2-class problem, so ln 2 = 0.693 means the partner alone says nothing about the
    label and there is no shortcut left to suppress; well below that means there is.
    The family head is 9-class, where the corresponding no-information value is
    ln 9 = 2.197. The chem head is a regression, so there is no analogous
    no-information constant -- read it relative to Var(s_chem) on this run's batches
    instead. Logging the lambdas alongside them makes a ramped run readable after the
    fact -- otherwise the schedule is invisible and the loss curve uninterpretable.
    """
    for key, batches_key, name in (
        ("adv", "adv_batches", "adversary loss"),
        ("dann", "dann_batches", "family dann loss"),
        ("chem", "chem_batches", "chem adversary loss"),
    ):
        batches = stats.get(batches_key, 0)
        if batches:
            writer.add_scalar(
                f"epoch/train {name}", stats[key] / batches, epoch_index + 1
            )
    if conf.adversarial_grl:
        writer.add_scalar(
            "epoch/adv lambda", model.final_layer.adv_lambda_now, epoch_index + 1
        )
    if conf.dann_family:
        writer.add_scalar(
            "epoch/dann lambda", model.final_layer.dann_lambda_now, epoch_index + 1
        )
    if conf.chem_adversary:
        writer.add_scalar(
            "epoch/chem lambda", model.final_layer.chem_lambda_now, epoch_index + 1
        )
    if conf.lipid_path_handicap:
        # The lr the handicap actually produced, not just the multiplier: the multiplier
        # alone would hide whatever the lr schedule did underneath it.
        writer.add_scalar(
            "epoch/lipid path weight", lipid_path_weight_now, epoch_index + 1
        )
        writer.add_scalar(
            "epoch/lipid branch lr", lipid_lr_groups[0]["lr"], epoch_index + 1
        )


def log_tb(writer,step,los,mode,pred,label, print_metrics=True):
    """Compute and log per-batch metrics for the requested phase."""
    #might hve to round at this very step
    if mode == "train":
        
        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()

        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 

        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        if print_metrics:
            print(f"train accuracy : {acc}")
            print(
                f"train pred 0/1 : {int((pred_class == 0).sum().item())}/{int((pred_class == 1).sum().item())} "
                f"label 0/1 : {int((label == 0).sum().item())}/{int((label == 1).sum().item())}"
            )
        writer.add_scalar("train sensitivity", sensitivity.item(),step)
        writer.add_scalar("train precision", precision.item(),step)
        writer.add_scalar("train specificity", specificity.item(),step)
        writer.add_scalar("train accuracy",acc.item(),step)
        writer.add_scalar("train F1 score",F1.item(),step)
        writer.add_scalar("train balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("train loss",los,step)
       #writer_tb.flush()
    if mode == "valid":

        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        if print_metrics:
            print(f"valid accuracy : {acc}")
            print(
                f"valid pred 0/1 : {int((pred_class == 0).sum().item())}/{int((pred_class == 1).sum().item())} "
                f"label 0/1 : {int((label == 0).sum().item())}/{int((label == 1).sum().item())}"
            )
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 

        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0

        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        writer.add_scalar("valid sensitivity", sensitivity.item(),step)
        writer.add_scalar("valid precision", precision.item(),step)
        writer.add_scalar("valid specificity", specificity.item(),step)
        writer.add_scalar("valid accuracy",acc.item(),step)
        writer.add_scalar("valid F1 score",F1.item(),step)
        writer.add_scalar("valid balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("valid loss",los,step)

    if mode == "test":

        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        print(f"test accuracy : {acc}")
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 
        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        metrics = {
            "accuracy": acc.item(),
            "sensitivity": sensitivity.item(),
            "precision": precision.item(),
            "specificity": specificity.item(),
            "F1": F1.item(),
            "balanced_accuracy": balanced_acc.item(),
            "loss": los.item() if isinstance(los, torch.Tensor) else los
        }
        return metrics
        #writer_tb.flush()
        
sof2 = torch.nn.Softmax(-1)


def validate_prediction_label_shapes(predictions, labels, phase, batch_index):
    """Validate one-to-one alignment between binary logits and labels."""
    if predictions.ndim != 2 or predictions.shape[1] != 2:
        raise ValueError(
            f"{phase} batch {batch_index}: expected predictions shaped [batch, 2], "
            f"got {tuple(predictions.shape)}"
        )
    if labels.ndim != 1:
        raise ValueError(
            f"{phase} batch {batch_index}: expected labels shaped [batch], "
            f"got {tuple(labels.shape)}"
        )
    if predictions.shape[0] != labels.shape[0]:
        raise ValueError(
            f"{phase} batch {batch_index}: prediction count "
            f"{predictions.shape[0]} does not match label count {labels.shape[0]}"
        )
    return labels.shape[0]


def _build_forward_args(prot, lipid):
    """Assemble the model forward kwargs for a protein/lipid batch."""
    forward_args = dict(
        config=conf,
        plm=prot.plm,
        bury=prot.bury,
        prot=prot.x,
        prot_edgidx=prot.edge_index,
        prot_e_attr=prot.edge_attr,
        prot_batch=prot.batch,
        lip=lipid.x,
        lip_batch=lipid.batch,
    )
    if conf.lipid_fragments_mask:
        forward_args["lipid_batch"] = lipid.lipid_batch
    if getattr(conf, "lipid_graph_isomers", False):
        forward_args["lip_edgidx"] = lipid.edge_index
        forward_args["lip_e_attr"] = lipid.edge_attr
    if conf.prot_attention_pos_bias or conf.prot_pooling_by_pockets:
        forward_args["pocket_mask"] = prot.pocket
    if getattr(conf, "use_esm3_v2_embeddings", False):
        forward_args["node_confidence"] = getattr(prot, "node_confidence", None)
    if getattr(conf, "geometric_transformer", False):
        forward_args["prot_frame_rotation"] = prot.frame_rotation
        forward_args["prot_frame_translation"] = prot.frame_translation
    if (
        getattr(conf, "geometric_transformer", False)
        or getattr(conf, "rnabang_frozen_node_adapter", False)
    ):
        forward_args["prot_geometric_node_attr"] = prot.geometric_node_attr
    if getattr(conf, "rnabang_frozen_node_adapter", False):
        forward_args["prot_edge_node_pairs"] = getattr(
            prot, "edge_node_pairs", None
        )
        forward_args["prot_edge_node_degree"] = prot.edge_node_degree
    if getattr(conf, "pocket_descriptors", False):
        # Protein_encoder raises without it, so the flag used to abort every run that
        # set it: the dataloader attached the descriptor and nothing passed it on. The
        # train, validation and test loops each carried their own copy of this dict,
        # which is how one branch could be missing from all three at once -- they now
        # call this function instead.
        forward_args["pocket_descriptor"] = prot.pocket_descriptor
    if getattr(conf, "chem_prior", False) or getattr(conf, "pocket_compat_prior", False):
        forward_args["frozen_prior"] = prot.frozen_prior
    if (
        getattr(conf, "compatibility_input", False)
        or getattr(conf, "compatibility_split_input", False)
    ):
        forward_args["compat_input"] = prot.compat_input
    if getattr(conf, "pair_descriptors", False):
        forward_args["pair_descriptor_input"] = prot.pair_descriptor_input
    if getattr(conf, "two_pair_descriptors_paths", False):
        forward_args["descriptor_catalog_input"] = prot.descriptor_catalog_input
    return forward_args


def _eval_task_loss(outl, labels):
    """Validation-style task loss (mirrors the validation branch), no sample weighting."""
    if conf.pu_loss:
        return Non_Negative_Positive_Unlabeled_loss(
            outl,
            labels.long(),
            conf.pu_rho,
            beta=conf.pu_beta,
            gamma=conf.pu_gamma,
            tau=conf.pu_tau,
            cap=conf.pu_loss_cap,
        )
    if conf.loss_type == "pairwise_rank":
        # Pooled pairing even under --rank_within_protein: this helper is reached only
        # from _bilevel_lambda_step, which is handed logits and labels without the
        # protein graph they came from. Combining --bilevel with --rank_within_protein
        # therefore tunes lambda against the pooled ranking while training minimises the
        # per-protein one; plumb prot through if that combination is ever run for real.
        return pairwise_ranking_loss(outl, labels.long())
    return conf.loss(outl, labels.long())


def _bilevel_lambda_step():
    """First-order validation update of the width gates (the bilevel lambda params).

    Theta is held fixed: its grads from this step are discarded on the next
    optimizer.zero_grad(); hyper_optimizer only steps the gate params. The gate grads
    left by the preceding train-loss backward are cleared here before the val backward.
    """
    prot_v, lipid_v = next(hyper_val_iter)
    prot_v = prot_v.to(device, non_blocking=True)
    lipid_v = lipid_v.to(device, non_blocking=True)
    labels_v = prot_v.inter.to(device, non_blocking=True)
    hyper_optimizer.zero_grad()
    outl_v = model(**_build_forward_args(prot_v, lipid_v))
    # The bilevel step reads the validation split, so on an expanded one its batches are
    # candidate copies; averaging them here keeps the hyper loss a per-pair quantity,
    # the same one the reported validation loss is.
    outl_v, labels_v, _ = average_candidate_predictions(outl_v, prot_v, labels_v)
    validate_prediction_label_shapes(outl_v, labels_v, "bilevel", 0)
    val_loss = _eval_task_loss(outl_v, labels_v)
    val_loss = val_loss + conf.sparsity_lambda * collect_sparsity_penalty(model).to(val_loss.device)
    val_loss.backward()
    hyper_optimizer.step()


# --- Branch diagnostics (--save_dynamics) ----------------------------------------
#
# One question: does the protein half of the model influence the decision, and if it
# stops, at which epoch and through which mechanism. Answered by scalars written every
# epoch rather than by weights, because the answer is a curve -- the endpoint alone
# cannot distinguish a branch that never learned anything from one that was learning
# and then got out-competed.
#
# Four measurements, each aimed at a different culprit:
#   contribution   what the balanced accuracy loses when one pooled half is zeroed,
#                  i.e. how much the classifier's decision rests on that partner
#   gradient norm  whether the branch is receiving a learning signal at all
#   head weights   whether the classifier itself is discounting the protein columns
#   between-protein variance  whether the protein branch still tells proteins apart
#
# Read them together: a protein contribution of zero with healthy protein gradients and
# a collapsed between-protein variance is a representation problem; the same zero with
# vanishing protein gradients is an optimisation problem; the same zero appearing only
# after the lipid handicap is released is the lipid branch taking the decision over.

# Epochs whose weights --save_model_in_dynamics keeps, placed around the lipid
# handicap's default 50-epoch ramp (ModelConfig.lipid_path_weight_ramp_epochs): the
# first epoch, an early-training point, the two epochs either side of the release, and
# the end of a 120-epoch run. Five files of a few MB, not one per epoch.
DYNAMICS_CHECKPOINT_EPOCHS = (1, 10, 49, 51, 120)

# The model's top-level submodules are lipid1/protein1/cross_attention1 (plus the *2
# twins under double_attention) and final_layer, so a parameter's branch is decided by
# its name prefix and nothing else has to be maintained here.
DYNAMICS_BRANCH_PREFIXES = {
    "protein": ("protein1.", "protein2."),
    "lipid": ("lipid1.", "lipid2."),
    "cross": ("cross_attention1.", "cross_attention2."),
    "head": ("final_layer.",),
}
dynamics_branch_parameters = (
    {
        branch: [
            parameter
            for name, parameter in model.named_parameters()
            if name.startswith(prefixes)
        ]
        for branch, prefixes in DYNAMICS_BRANCH_PREFIXES.items()
    }
    if conf.save_dynamics
    else {}
)
dynamics_grad_stats = {
    branch: {"sum": 0.0, "batches": 0} for branch in dynamics_branch_parameters
}


def reset_dynamics_grad_stats():
    """Start a fresh epoch's gradient-norm average."""
    for accumulator in dynamics_grad_stats.values():
        accumulator["sum"] = 0.0
        accumulator["batches"] = 0


def accumulate_branch_grad_norms():
    """Add this batch's per-branch gradient norm to the epoch's running mean.

    Called between backward() and the optimizer step, so the gradients read are the ones
    the step is about to apply. Under AMP the caller unscales first: otherwise every
    number would carry the loss scaler's factor, which changes on its own schedule and
    would show up as branch dynamics that never happened.
    """
    for branch, parameters in dynamics_branch_parameters.items():
        squared = 0.0
        for parameter in parameters:
            if parameter.grad is not None:
                squared += float(parameter.grad.detach().pow(2).sum())
        accumulator = dynamics_grad_stats[branch]
        accumulator["sum"] += squared ** 0.5
        accumulator["batches"] += 1


def _dynamics_valid_pass(collect_pooled=False):
    """One validation pass under whatever ablation flags are currently set.

    Built from the same update_aggregate/aggregate_values pair the real validation uses,
    so the balanced accuracies compared across these passes are one quantity rather than
    two definitions of it.
    """
    model.eval()
    stats = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
        "loss": 0.0,
        "count": 0,
        "loss_count": 0,
    }
    pooled_lipid = []
    pooled_protein = []
    protein_ids = []
    # On an expanded split the rows are candidates, not pairs, so the pass collects them
    # and the metric is computed once from the per-pair averages (see run_test for the
    # same shape). Without the flag this is None and nothing changes.
    accumulator = CandidateAccumulator() if conf.eval_average_candidates else None
    seen_pairs = set()
    with torch.no_grad():
        for prot, lipid in valid_loader:
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            labels = prot.inter.to(device, non_blocking=True).long()
            outl = model(**_build_forward_args(prot, lipid))
            if accumulator is not None:
                accumulator.add(outl, prot, labels)
            else:
                loss = _eval_task_loss(outl, labels)
                update_aggregate(stats, outl.argmax(dim=1), labels, loss, labels.shape[0])
            partners = model.final_layer._pooled_partners
            if collect_pooled and partners is not None:
                # One pooled vector per candidate on an expanded split; keeping the first
                # row of each pair leaves this diagnostic one row per pair, as it is when
                # nothing is expanded.
                keep = slice(None)
                if accumulator is not None:
                    keep = []
                    for position, pair in enumerate(
                        prot.candidate_group.view(-1).tolist()
                    ):
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            keep.append(position)
                    keep = torch.tensor(keep, dtype=torch.long)
                pooled_lipid.append(partners[0][keep].cpu())
                pooled_protein.append(partners[1][keep].cpu())
                protein_ids.append(prot.protein_id.view(-1)[keep].cpu())
    if accumulator is not None:
        averaged, labels, _ = accumulator.averaged()
        loss = _eval_task_loss(averaged, labels)
        update_aggregate(stats, averaged.argmax(dim=1), labels, loss, labels.shape[0])
    metrics = aggregate_values(stats)
    if not pooled_protein:
        return metrics, None
    return metrics, (
        torch.cat(pooled_lipid),
        torch.cat(pooled_protein),
        torch.cat(protein_ids),
    )


def _dynamics_ablated_valid(field, collect_pooled=False):
    """Validate with one pooled half zeroed, then put the flag back as it was.

    The flags are the ones Final_Layer already implements for whole-run ablations, read
    per forward, so switching them here needs nothing from the architecture. What this
    measures is narrower than a real --lipid_only run: cross-attention stays on, so the
    protein's influence on the lipid representation survives and only the classifier's
    direct protein input is removed. That is the intended question -- does the head use
    the protein channel -- and the narrower reading is the reason it is worth stating.
    """
    previous = getattr(conf, field)
    setattr(conf, field, True)
    try:
        return _dynamics_valid_pass(collect_pooled=collect_pooled)
    finally:
        setattr(conf, field, previous)


def _between_protein_variance_share(vectors, protein_ids):
    """Share of the pooled protein vector's variance that lies between proteins.

    Near zero means the branch hands the classifier nearly the same vector whichever
    protein it was given, and no downstream layer can recover a distinction that is not
    in its input. Total variance is summed over dimensions, so the number cannot be
    carried by one wide dimension, and lands in [0, 1].
    """
    vectors = vectors.double()
    centered = vectors - vectors.mean(dim=0)
    total = float((centered ** 2).sum())
    if total <= 0.0:
        return 0.0
    grand_mean = vectors.mean(dim=0)
    between = 0.0
    for protein in protein_ids.unique():
        rows = vectors[protein_ids == protein]
        between += float(rows.shape[0] * ((rows.mean(dim=0) - grand_mean) ** 2).sum())
    return between / total


def _head_input_weight_norms(lipid_width):
    """Norms of the classifier's first-layer weights on each half of its input.

    The fusion is a concatenation, [lipid | protein] (Final_Layer.forward), so those
    columns split by partner and their norms say how much of the decision each half is
    even allowed to reach. Bilinear fusion mixes the halves before the layer and leaves
    no such split, hence the None.
    """
    if conf.bilinear_fusion:
        return None
    linear = next(
        (
            layer
            for layer in model.final_layer.binar
            if isinstance(layer, torch.nn.Linear)
        ),
        None,
    )
    if linear is None or linear.weight.shape[1] <= lipid_width:
        return None
    weight = linear.weight.detach()
    return float(weight[:, :lipid_width].norm()), float(weight[:, lipid_width:].norm())


def log_branch_dynamics(epoch_index, valid_metrics):
    """Write this epoch's branch diagnostics to TensorBoard and to the run log."""
    full_ba = valid_metrics.get("balanced_accuracy")
    # The pooled halves are collected on the first ablated pass, not on a third full
    # one: the stash in Final_Layer is taken before the zeroing, so an ablated pass
    # reports exactly the vectors the unablated model computed.
    without_protein, pooled = _dynamics_ablated_valid("lipid_only", collect_pooled=True)
    without_lipid, _ = _dynamics_ablated_valid("protein_only")

    scalars = {
        "valid BA without protein": without_protein.get("balanced_accuracy"),
        "valid BA without lipid": without_lipid.get("balanced_accuracy"),
    }
    if full_ba is not None:
        scalars["protein contribution"] = full_ba - without_protein["balanced_accuracy"]
        scalars["lipid contribution"] = full_ba - without_lipid["balanced_accuracy"]

    for branch, accumulator in dynamics_grad_stats.items():
        if accumulator["batches"]:
            scalars[f"grad norm {branch}"] = accumulator["sum"] / accumulator["batches"]

    between_share = None
    if pooled is not None:
        pooled_lipid, pooled_protein, protein_ids = pooled
        between_share = _between_protein_variance_share(pooled_protein, protein_ids)
        scalars["pooled protein between-protein variance"] = between_share
        scalars["pooled protein norm"] = float(pooled_protein.norm(dim=1).mean())
        scalars["pooled lipid norm"] = float(pooled_lipid.norm(dim=1).mean())
        head_norms = _head_input_weight_norms(pooled_lipid.shape[1])
        if head_norms is not None:
            scalars["head weight norm lipid"] = head_norms[0]
            scalars["head weight norm protein"] = head_norms[1]

    for name, value in scalars.items():
        if value is not None:
            writer_tb.add_scalar(f"epoch/{name}", value, epoch_index + 1)

    def show(value):
        return "n/a" if value is None else f"{value:.4f}"

    print(
        "dynamics: "
        f"BA full {show(full_ba)} "
        f"| no protein {show(scalars.get('valid BA without protein'))} "
        f"(delta {show(scalars.get('protein contribution'))}) "
        f"| no lipid {show(scalars.get('valid BA without lipid'))} "
        f"(delta {show(scalars.get('lipid contribution'))}) "
        f"| grad protein {show(scalars.get('grad norm protein'))} "
        f"lipid {show(scalars.get('grad norm lipid'))} "
        f"| head |W| protein {show(scalars.get('head weight norm protein'))} "
        f"lipid {show(scalars.get('head weight norm lipid'))} "
        f"| between-protein variance {show(between_share)}"
    )


def save_dynamics_milestone(epoch_1based):
    """Keep the weights of a milestone epoch, for probes no scalar can anticipate."""
    if epoch_1based not in DYNAMICS_CHECKPOINT_EPOCHS:
        return
    directory = os.path.join(models_root, label_name, excluded_set_name, "dynamics")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"seed{conf.seed}_epoch{epoch_1based}.pt")
    torch.save(model.state_dict(), path)
    print(f"dynamics: saved weights of epoch {epoch_1based} to {path}")


def epoch(idx,counttrain,countval):
    """Run one training epoch followed by full validation."""
    if conf.pu_loss:
        reset_pu_loss_diagnostics()
    train_stats = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
        "loss": 0.0,
        "count": 0,
        "loss_count": 0,
    }
    # Adversary penalties are added to the backward pass after update_aggregate has
    # already banked the task loss, so without their own accumulators they leave no
    # trace in TensorBoard at all. They are what says whether a partner is still
    # individually decodable -- the premise the whole GRL setup rests on -- so they are
    # tracked separately rather than folded into "epoch/train loss".
    adversary_stats = {"adv": 0.0, "adv_batches": 0, "dann": 0.0, "dann_batches": 0, "chem": 0.0, "chem_batches": 0}
    for i, graph in enumerate(train_loader):
        #dataset is reduced because of high variety of experience parameters 
        if i < train_batches_to_run:
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)

            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            optimizer.zero_grad()

            forward_args = _build_forward_args(prot, lipid)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                outl = model(**forward_args)

                sample_count = validate_prediction_label_shapes(
                    outl, interaction_labels, "train", i + 1
                )
                loss_logits = (
                    outl + logit_adjustment_bias_tensor
                    if conf.logit_adjustment
                    else outl
                )

                if conf.grab_loss:
                    batch_pair_ids = prot.pair_id.view(-1)[:sample_count]
                    grab_label_coefficients = train_dataset.get_grab_batch_inputs(batch_pair_ids, device)
                    sample_weights = batch_sample_weights(prot, sample_count)
                    los = GRAB_loss(
                        loss_logits,
                        interaction_labels.long(),
                        grab_label_coefficients,
                        class_weights=class_weights,
                        sample_weights=sample_weights,
                        focal_gamma=conf.focal_gamma if conf.focal_loss else None)
                elif conf.pu_loss:
                    sample_weights = batch_sample_weights(prot, sample_count)
                    los = Non_Negative_Positive_Unlabeled_loss(
                        loss_logits,
                        interaction_labels.long(),
                        conf.pu_rho,
                        beta=conf.pu_beta,
                        gamma=conf.pu_gamma,
                        tau=conf.pu_tau,
                        cap=conf.pu_loss_cap,
                        sample_weights=sample_weights,
                    )
                elif conf.loss_type == "pairwise_rank":
                    sample_weights = batch_sample_weights(prot, sample_count)
                    los = pairwise_ranking_loss(
                        loss_logits,
                        interaction_labels.long(),
                        sample_weights=sample_weights,
                        protein_ids=(
                            prot.protein_id.view(-1)[:sample_count]
                            if conf.rank_within_protein else None
                        ),
                    )
                elif conf.loss_type == "cross_entropy":
                    sample_weights = batch_sample_weights(prot, sample_count)
                    if conf.focal_loss:
                        los_unred = focal_loss(
                            loss_logits,
                            interaction_labels.long(),
                            gamma=conf.focal_gamma,
                            class_weights=class_weights,
                            reduction="none",
                        )
                    else:
                        los_unred = F.cross_entropy(loss_logits, interaction_labels.long(), weight=class_weights, reduction="none")
                    # The None branch is the same number, not an approximation of it:
                    # see batch_sample_weights. It matches what focal_loss, GRAB_loss and
                    # the PU loss already do when handed no weights.
                    los = (
                        los_unred.mean()
                        if sample_weights is None
                        else (los_unred * sample_weights).sum()
                        / sample_weights.sum().clamp_min(1e-8)
                    )
                else:
                    los=conf.loss(outl,interaction_labels.long())
            # Batch-level logging is temporarily disabled; keep it for re-enabling.
            # print(f"epoch : {idx+1}")
            # print(f"batch : {i+1}/{train_batches_to_run}")
            # log_tb(writer_tb, counttrain, los,"train",outl,interaction_labels)
            pred_class = outl.argmax(dim=1)
            update_aggregate(
                train_stats,
                pred_class,
                interaction_labels.long(),
                los,
                sample_count,
                loss_count=1 if conf.grab_loss else sample_count,
            )

            # Gate penalty on the TRAIN loss only when NOT bilevel; in bilevel mode the
            # gate penalty is applied on the validation step (_bilevel_lambda_step).
            if gate_params and conf.sparsity_lambda > 0.0 and not conf.bilevel:
                los = los + conf.sparsity_lambda * collect_sparsity_penalty(model).to(los.device)
            # Per-layer Concrete Dropout KL surrogate is always a train-objective term
            # (its weight_reg/dropout_reg coefficients are baked into each module).
            if conf.bilevel_dropout:
                los = los + collect_concrete_dropout_reg(model).to(los.device)

            # Adversarial anti-shortcut penalty: the per-partner adversary logits
            # stashed by Final_Layer sit behind a gradient-reversal layer, so
            # adding their CE here and one backward() trains the heads to predict
            # the label from one partner while pushing the encoder to make each
            # partner individually uninformative. Kept out of the logged task loss.
            if conf.adversarial_grl:
                adv = model.final_layer._adv
                if adv is not None:
                    # A side disabled by --no_adv_lipid / --no_adv_protein comes back
                    # None and contributes no term. Averaged over the sides in use so
                    # adv_weight means the same pressure whether one or both are on.
                    terms = [
                        F.cross_entropy(logits, interaction_labels.long())
                        for logits in adv
                        if logits is not None
                    ]
                    adv_loss = torch.stack(terms).mean() if terms else None
                if adv is not None and adv_loss is not None:
                    los = los + conf.adv_weight * adv_loss
                    adversary_stats["adv"] += float(adv_loss.detach())
                    adversary_stats["adv_batches"] += 1

            # Family DANN on the fused representation. prot.family is a per-graph 9-wide
            # one-hot, which PyG concatenates flat, so it is reshaped back per sample.
            if conf.dann_family:
                dann_features = model.final_layer._dann_features
                if dann_features is not None:
                    dann_loss = family_dann_loss(
                        dann_features,
                        prot.family.view(dann_features.shape[0], -1),
                        interaction_labels.long(),
                        model.final_layer.family_adversaries,
                        conf.dann_class_conditional,
                    )
                    los = los + conf.dann_weight * dann_loss
                    adversary_stats["dann"] += float(dann_loss.detach())
                    adversary_stats["dann_batches"] += 1

            # Chemistry adversary, same fused representation, s_chem instead of family.
            if conf.chem_adversary:
                chem_features = model.final_layer._chem_features
                if chem_features is not None:
                    chem_loss = chem_adversary_loss(
                        chem_features,
                        prot.frozen_prior.view(chem_features.shape[0]),
                        model.final_layer.chem_head,
                    )
                    los = los + conf.chem_weight * chem_loss
                    adversary_stats["chem"] += float(chem_loss.detach())
                    adversary_stats["chem_batches"] += 1

            if use_amp:
                scaler.scale(los).backward()
                if conf.save_dynamics:
                    # Before the norms are read, never after: scaler.step() would have
                    # unscaled them itself, but only inside its own call.
                    scaler.unscale_(optimizer)
                    accumulate_branch_grad_norms()
                scaler.step(optimizer)
                scaler.update()
            else:
                los.backward()
                if conf.save_dynamics:
                    accumulate_branch_grad_norms()
                optimizer.step()

            if hyper_optimizer is not None:
                _bilevel_lambda_step()
            counttrain+=1
        else:
            break
    if conf.pu_loss:
        pu_diag = get_pu_loss_diagnostics()
        if pu_diag["calls"] > 0:
            print(
                "PU nnPU correction: "
                f"{pu_diag['corrections']}/{pu_diag['calls']} batches, "
                f"negative_risk[min={pu_diag['min_negative_loss']:.6f}, "
                f"mean={pu_diag['sum_negative_loss'] / pu_diag['calls']:.6f}, "
                f"max={pu_diag['max_negative_loss']:.6f}]"
            )
    model.eval()
    valid_stats = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
        "loss": 0.0,
        "count": 0,
        "loss_count": 0,
    }
    valid_accumulator = (
        CandidateAccumulator() if conf.eval_average_candidates else None
    )
    with torch.no_grad():
        print("VALIDATION")
        for i , graph in enumerate(valid_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)
    
            forward_args = _build_forward_args(prot, lipid)
            outl = model(**forward_args)
            if valid_accumulator is not None:
                # Candidates of one pair are scattered over the shuffled batches; the
                # pass collects them and the block is scored once below, so the loss and
                # the counters see pairs rather than candidates.
                valid_accumulator.add(outl, prot, interaction_labels)
                continue
            sample_count = validate_prediction_label_shapes(
                outl, interaction_labels, "valid", i + 1
            )
            # print(f"valid batch : {i+1}/{valid_batches_to_run}")

            if conf.pu_loss:
                los = Non_Negative_Positive_Unlabeled_loss(
                    outl,
                    interaction_labels.long(),
                    conf.pu_rho,
                    beta=conf.pu_beta,
                    gamma=conf.pu_gamma,
                    tau=conf.pu_tau,
                    cap=conf.pu_loss_cap,
                )
            elif conf.loss_type == "pairwise_rank":
                los = pairwise_ranking_loss(
                    outl,
                    interaction_labels.long(),
                    protein_ids=(
                        prot.protein_id.view(-1) if conf.rank_within_protein else None
                    ),
                )
            else:
                los = conf.loss(outl, interaction_labels.long())
            # log_tb(writer_tb, countval, los,"valid",outl,interaction_labels.to(torch.float))
            pred_class = outl.argmax(dim=1)
            labels = interaction_labels.long()
            update_aggregate(valid_stats, pred_class, labels, los, sample_count)
            countval +=1
    if valid_accumulator is not None:
        outl, interaction_labels, averaged_protein_ids = valid_accumulator.averaged()
        sample_count = validate_prediction_label_shapes(
            outl, interaction_labels, "valid", 1
        )
        # Chunked to the training batch size, so a loss defined over a batch keeps its
        # scale; the ranking loss also needs the protein ids that survived the reduction.
        los, _ = _batched_block_loss(outl, interaction_labels, averaged_protein_ids)
        update_aggregate(
            valid_stats,
            outl.argmax(dim=1),
            interaction_labels.long(),
            los,
            sample_count,
        )
        countval += 1
    train_metrics = aggregate_values(train_stats)
    valid_metrics = aggregate_values(valid_stats)
    log_epoch_metrics(writer_tb, idx, "train", train_metrics)
    log_epoch_metrics(writer_tb, idx, "valid", valid_metrics)
    log_adversary_metrics(writer_tb, idx, adversary_stats)
    if (idx + 1) % TENSORBOARD_FLUSH_EVERY_EPOCHS == 0:
        writer_tb.flush()
    print(f"valid epoch balanced_accuracy: {format_metric(valid_metrics['balanced_accuracy'])}")
    
    return counttrain, countval, train_metrics, valid_metrics


def _batched_block_loss(outl, labels, protein_ids=None):
    """The evaluation loss of one averaged block, computed the way a pass computes it.

    Cross-entropy decomposes per row, so cutting the block into chunks changes nothing.
    The ranking loss and the positive-unlabelled risk do not: both are defined over the
    rows in front of them, and evaluating them once over a whole block forms pairs, and
    estimates class priors, on a sample the training loss never sees at once. The block
    is therefore cut into chunks the size of a training batch and the chunk losses are
    averaged by row count -- the same arithmetic the per-batch path performs, so the
    validation curve stays comparable with the training one.

    Returns (weighted mean loss, row count).
    """
    rows = int(labels.shape[0])
    if rows == 0:
        return 0.0, 0
    size = max(1, int(conf.batch))
    total = 0.0
    for start in range(0, rows, size):
        stop = min(start + size, rows)
        chunk_labels = labels[start:stop]
        if (
            conf.loss_type == "pairwise_rank"
            and conf.rank_within_protein
            and protein_ids is not None
        ):
            chunk_loss = pairwise_ranking_loss(
                outl[start:stop],
                chunk_labels.long(),
                protein_ids=protein_ids.view(-1)[start:stop],
            )
        else:
            chunk_loss = _eval_task_loss(outl[start:stop], chunk_labels)
        value = (
            chunk_loss.item() if isinstance(chunk_loss, torch.Tensor) else chunk_loss
        )
        total += value * (stop - start)
    return total / rows, rows


def _score_averaged_block(accumulator):
    """Confusion counts, loss and per-protein counts for one averaged evaluation block.

    The counterpart of the per-batch bookkeeping in run_test, run once on the per-pair
    averages instead of once per batch. The per-row loss is the cross-entropy of the
    averaged probability where the run's loss decomposes per row, and the block loss
    spread evenly over the rows where it does not -- the same substitution the per-batch
    path makes for the ranking and positive-unlabelled losses.
    """
    outl, labels, protein_ids = accumulator.averaged()
    labels = labels.long()
    if conf.loss_type == "cross_entropy" and not conf.pu_loss:
        sample_losses = F.cross_entropy(outl, labels, reduction="none")
        block_loss = float(sample_losses.mean())
    else:
        block_loss, _ = _batched_block_loss(outl, labels, protein_ids)
        sample_losses = torch.full(labels.shape, block_loss, device=outl.device)

    predictions = outl.argmax(dim=1)
    correct = predictions == labels
    positive = predictions == 1
    total_tp = int((correct & positive).sum())
    total_fp = int((~correct & positive).sum())
    total_tn = int((correct & ~positive).sum())
    total_fn = int((~correct & ~positive).sum())

    subgroup_stats = {}
    if protein_ids is not None:
        for protein_id, prediction, label, sample_loss in zip(
            protein_ids.view(-1).cpu().tolist(),
            predictions.cpu().tolist(),
            labels.cpu().tolist(),
            sample_losses.detach().cpu().tolist(),
        ):
            stats = subgroup_stats.setdefault(
                protein_id, {"TP": 0, "FP": 0, "TN": 0, "FN": 0, "loss": 0.0, "count": 0}
            )
            if prediction == label and prediction == 1:
                stats["TP"] += 1
            elif prediction != label and prediction == 1:
                stats["FP"] += 1
            elif prediction == label and prediction == 0:
                stats["TN"] += 1
            else:
                stats["FN"] += 1
            stats["loss"] += sample_loss
            stats["count"] += 1

    return (
        total_tp,
        total_fp,
        total_tn,
        total_fn,
        block_loss * labels.shape[0],
        int(labels.shape[0]),
        subgroup_stats,
    )


def run_test(run_summary):
    """Evaluate the test split and write global and per-protein metrics."""
    
    model.eval()

    total_tp = 0
    total_fp = 0
    total_tn = 0
    total_fn = 0
    total_loss = 0.0
    total_loss_count = 0
    subgroup_stats = {}

    # Expanded split: one row per candidate structure. The pass collects them and the
    # block is scored once, below, so a pair contributes one prediction to the totals and
    # to its protein's subgroup whatever its candidate count.
    test_accumulator = CandidateAccumulator() if conf.eval_average_candidates else None
    with torch.no_grad():
        for i , graph in enumerate(test_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            forward_args = _build_forward_args(prot, lipid)
            outl = model(**forward_args)
            if test_accumulator is not None:
                test_accumulator.add(outl, prot, interaction_labels)
                continue
            sample_count = validate_prediction_label_shapes(
                outl, interaction_labels, "test", i + 1
            )

            if conf.pu_loss:
                los = Non_Negative_Positive_Unlabeled_loss(
                    outl,
                    interaction_labels.long(),
                    conf.pu_rho,
                    beta=conf.pu_beta,
                    gamma=conf.pu_gamma,
                    tau=conf.pu_tau,
                    cap=conf.pu_loss_cap,
                )
                sample_losses = torch.full(
                    (sample_count,),
                    los.item() if isinstance(los, torch.Tensor) else los,
                    device=outl.device,
                )
            elif conf.loss_type == "cross_entropy":
                sample_losses = F.cross_entropy(
                    outl,
                    interaction_labels.long(),
                    reduction="none",
                )
                los = sample_losses.mean()
            elif conf.loss_type == "pairwise_rank":
                los = pairwise_ranking_loss(
                    outl,
                    interaction_labels.long(),
                    protein_ids=(
                        prot.protein_id.view(-1) if conf.rank_within_protein else None
                    ),
                )
                sample_losses = torch.full(
                    (sample_count,),
                    los.item() if isinstance(los, torch.Tensor) else los,
                    device=outl.device,
                )
            else:
                los = conf.loss(outl, interaction_labels.long())
                sample_losses = torch.full(
                    (sample_count,),
                    los.item() if isinstance(los, torch.Tensor) else los,
                    device=outl.device,
                )
            pred_class = outl.argmax(dim=1)
            labels = interaction_labels.long()
            protein_ids = prot.protein_id.view(-1)[:sample_count].detach().cpu().tolist()
            sample_loss_values = sample_losses.detach().cpu().tolist()
            total_tp += int(((pred_class == labels) & (pred_class == 1)).sum().item())
            total_fp += int(((pred_class != labels) & (pred_class == 1)).sum().item())
            total_tn += int(((pred_class == labels) & (pred_class == 0)).sum().item())
            total_fn += int(((pred_class != labels) & (pred_class == 0)).sum().item())
            total_loss += (los.item() if isinstance(los, torch.Tensor) else los) * sample_count
            total_loss_count += sample_count
            for protein_id, pred_value, label_value, sample_loss in zip(
                protein_ids,
                pred_class.detach().cpu().tolist(),
                labels.detach().cpu().tolist(),
                sample_loss_values,
            ):
                stats = subgroup_stats.setdefault(protein_id, {"TP": 0, "FP": 0, "TN": 0, "FN": 0, "loss": 0.0, "count": 0})
                if pred_value == label_value and pred_value == 1:
                    stats["TP"] += 1
                elif pred_value != label_value and pred_value == 1:
                    stats["FP"] += 1
                elif pred_value == label_value and pred_value == 0:
                    stats["TN"] += 1
                elif pred_value != label_value and pred_value == 0:
                    stats["FN"] += 1
                stats["loss"] += sample_loss
                stats["count"] += 1

    if test_accumulator is not None:
        (
            total_tp,
            total_fp,
            total_tn,
            total_fn,
            total_loss,
            total_loss_count,
            subgroup_stats,
        ) = _score_averaged_block(test_accumulator)

    metrics = metric_values(total_tp, total_fp, total_tn, total_fn, total_loss, total_loss_count)

    print(f"accuracy: {format_metric(metrics['accuracy'])}")
    print(f"sensitivity: {format_metric(metrics['sensitivity'])}")
    print(f"precision: {format_metric(metrics['precision'])}")
    print(f"specificity: {format_metric(metrics['specificity'])}")
    print(f"IoU: {format_metric(metrics['IoU'])}")
    print(f"FAR: {format_metric(metrics['FAR'])}")
    print(f"F1: {format_metric(metrics['F1'])}")
    print(f"balanced_accuracy: {format_metric(metrics['balanced_accuracy'])}")
    print(f"loss: {format_metric(metrics['loss'])}")

    test_metrics_path = os.path.join(test_metrics_dir, f"test_metrics_{timestamp}_{number_of_parameters}parameters_{conf.m}_{conf.HEADS}_{conf.seed}_{conf.lr}_{conf.batch}_{conf.hiddim}.txt")
    subgroup_columns = [
        "subgroup",
        "total",
        "real_positive",
        "real_negative",
        "predicted_positive",
        "predicted_negative",
        "TP",
        "FP",
        "TN",
        "FN",
        "accuracy",
        "sensitivity",
        "precision",
        "specificity",
        "IoU",
        "FAR",
        "F1",
        "balanced_accuracy",
        "loss",
    ]
    subgroup_rows = []
    for protein_id, stats in sorted(subgroup_stats.items(), key=lambda item: train_dataset.protein_id_to_name[item[0]]):
        subgroup_metrics = metric_values(stats["TP"], stats["FP"], stats["TN"], stats["FN"], stats["loss"], stats["count"])
        subgroup_name = train_dataset.protein_id_to_name[protein_id]
        subgroup_rows.append([
            subgroup_name,
            str(subgroup_metrics["total"]),
            str(subgroup_metrics["real_positive"]),
            str(subgroup_metrics["real_negative"]),
            str(subgroup_metrics["predicted_positive"]),
            str(subgroup_metrics["predicted_negative"]),
            str(subgroup_metrics["TP"]),
            str(subgroup_metrics["FP"]),
            str(subgroup_metrics["TN"]),
            str(subgroup_metrics["FN"]),
            format_metric(subgroup_metrics["accuracy"]),
            format_metric(subgroup_metrics["sensitivity"]),
            format_metric(subgroup_metrics["precision"]),
            format_metric(subgroup_metrics["specificity"]),
            format_metric(subgroup_metrics["IoU"]),
            format_metric(subgroup_metrics["FAR"]),
            format_metric(subgroup_metrics["F1"]),
            format_metric(subgroup_metrics["balanced_accuracy"]),
            format_metric(subgroup_metrics["loss"]),
        ])
    subgroup_widths = [
        max(len(row[i]) for row in [subgroup_columns] + subgroup_rows)
        for i in range(len(subgroup_columns))
    ]

    def format_subgroup_row(row):
        """Format one fixed-width per-protein metrics table row."""
        formatted = [row[0].ljust(subgroup_widths[0])]
        formatted.extend(row[i].rjust(subgroup_widths[i]) for i in range(1, len(row)))
        return "  ".join(formatted)

    with open(test_metrics_path, "w") as f:
        for key, value in vars(conf).items():
            if isinstance(value, bool):
                value = int(value)
            elif isinstance(value, (list, dict)):
                # Compact JSON (no ": ") so the "key: value" report parser splits cleanly.
                value = json.dumps(value, separators=(",", ":"))
            f.write(f"{key}: {value}\n")
        for key in RUN_METRIC_FIELDS:
            value = run_summary[key]
            if isinstance(value, bool):
                value = int(value)
            if isinstance(value, float):
                value = format_metric(value)
            elif value is None:
                value = "undefined"
            f.write(f"{key}: {value}\n")
        # Discovered hyperparameters (aggregatable across seeds/groups), each keyed by the
        # module path so it is clear which layer it belongs to. Compact JSON (no ": ") so
        # the report parser splits cleanly. Blank when the discovery features are off.
        discovered_widths_value = (
            json.dumps(
                {name: info["active"] for name, info in surviving_structure.items()},
                separators=(",", ":"),
            )
            if surviving_structure
            else ""
        )
        discovered_dropout_value = (
            json.dumps(
                {name: round(p, 6) for name, p in discovered_dropout_report.items()},
                separators=(",", ":"),
            )
            if discovered_dropout_report
            else ""
        )
        f.write(f"discovered_widths: {discovered_widths_value}\n")
        f.write(f"discovered_dropout: {discovered_dropout_value}\n")
        for key in ["total", "real_positive", "real_negative", "predicted_positive", "predicted_negative", "TP", "FP", "TN", "FN"]:
            f.write(f"{key}: {metrics[key]}\n")
        for key in ["accuracy", "sensitivity", "precision", "specificity", "IoU", "FAR", "F1", "balanced_accuracy", "loss"]:
            f.write(f"{key}: {format_metric(metrics[key])}\n")
        f.write("\nper_protein_subgroup_metrics:\n")
        f.write(format_subgroup_row(subgroup_columns) + "\n")
        f.write(format_subgroup_row(["-" * width for width in subgroup_widths]) + "\n")
        for row in subgroup_rows:
            f.write(format_subgroup_row(row) + "\n")
    writer_tb.flush()
    append_metric(
        test_metrics_path,
        metrics_root=test_metrics_root,
        run_root=run_root,
        table=metrics_table_path,
        config=conf,
    )


epoch_number = 0
EPOCHS = conf.ep
countrain =0
countval =0
best_valid_balanced_acc = None
best_epoch = None
best_model_state = None
epoch_history = []
epochs_without_checkpoint_improvement = 0
checkpoint_window = conf.checkpoint_window
early_stopping_patience = 60
training_started_at = time.perf_counter()
# Ratcheted fit progress for the *_lambda_ramp_by_fit schedules: the highest train
# balanced accuracy seen so far, as a [0, 1] fraction. Never decreases, so lambda stays
# a schedule instead of feeding back into the fit it is derived from. One counter serves
# both reversals -- it measures the model, not a head.
fit_progress = 0.0
uses_fit_ramp = (
    (conf.adversarial_grl and conf.adv_lambda_ramp_by_fit)
    or (conf.dann_family and conf.dann_lambda_ramp_by_fit)
    or (conf.chem_adversary and conf.chem_lambda_ramp_by_fit)
)
for eepoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch_number + 1))
    epoch_progress = epoch_number / max(EPOCHS - 1, 1)
    if conf.adversarial_grl:
        # The fit ramp reads the previous epoch's fit (this one has not run yet), so
        # epoch 0 starts at lambda = 0 either way.
        model.final_layer.adv_lambda_now = conf.ramped_adv_lambda(
            fit_progress if conf.adv_lambda_ramp_by_fit else epoch_progress
        )
    if conf.dann_family:
        model.final_layer.dann_lambda_now = conf.ramped_dann_lambda(
            fit_progress if conf.dann_lambda_ramp_by_fit else epoch_progress
        )
    if conf.chem_adversary:
        model.final_layer.chem_lambda_now = conf.ramped_chem_lambda(
            fit_progress if conf.chem_lambda_ramp_by_fit else epoch_progress
        )
    if conf.lipid_path_handicap:
        # Epoch index rather than epoch_progress: this is a warm-up measured in epochs,
        # so its length must not change when EPOCHS does.
        lipid_path_weight_now = conf.ramped_lipid_path_weight(epoch_number)
        apply_lipid_path_handicap(lipid_path_weight_now)
    if conf.save_dynamics:
        reset_dynamics_grad_stats()
    # Rotates the residue subsample when --protein_residue_subsample is set; a no-op
    # otherwise. Before the epoch runs, so the masks belong to the epoch they are
    # numbered with.
    train_dataset.set_epoch(epoch_number)
    model.train(True)
    countrain, countval, train_metrics, valid_metrics = epoch(epoch_number,countrain,countval)
    if conf.save_dynamics:
        # After the epoch's own validation, so the ablated passes are compared against a
        # full-model number measured on the same weights.
        log_branch_dynamics(epoch_number, valid_metrics)
    if conf.save_model_in_dynamics:
        # No longer nested under save_dynamics: the checkpoint itself does not depend on
        # the curve-logging pass above (save_dynamics_milestone only reads model/conf),
        # so a run that wants milestones without the two extra ablated validation passes
        # (e.g. --descriptors_head, where those passes are no-ops -- see read_
        # configuration.py's save_dynamics docstring) can set this flag alone.
        save_dynamics_milestone(epoch_number + 1)
    if uses_fit_ramp:
        fit_progress = max(
            fit_progress,
            conf.adv_fit_progress(train_metrics.get("balanced_accuracy")),
        )
    rolling_valid_balanced_acc = rolling_metric_mean(
        [
            *epoch_history,
            {"train": train_metrics, "valid": valid_metrics},
        ],
        "valid",
        "balanced_accuracy",
        window=checkpoint_window,
    )
    valid_metrics["checkpoint_balanced_accuracy"] = rolling_valid_balanced_acc
    epoch_history.append({"train": train_metrics, "valid": valid_metrics})
    if best_model_state is None or (
        rolling_valid_balanced_acc is not None
        and (
            best_valid_balanced_acc is None
            or rolling_valid_balanced_acc > best_valid_balanced_acc
        )
    ):
        best_valid_balanced_acc = rolling_valid_balanced_acc
        best_epoch = epoch_number
        best_model_state = copy.deepcopy(model.state_dict())
        epochs_without_checkpoint_improvement = 0
    else:
        epochs_without_checkpoint_improvement += 1
    if conf.swa and epoch_number >= swa_start_epoch:
        swa_model.update_parameters(model)
        swa_scheduler.step()
    elif lr_scheduler is not None:
        lr_scheduler.step()
    #plot_metrics()
    epoch_number += 1
    torch.cuda.empty_cache()
    if (
        not conf.disable_early_stopping
        and epochs_without_checkpoint_improvement >= early_stopping_patience
        and metric_has_positive_trend(
            epoch_history,
            "valid",
            "loss",
            window=early_stopping_patience,
        )
    ):
        print(
            f"EARLY STOPPING: rolling validation balanced accuracy "
            f"did not improve for {early_stopping_patience} epochs and "
            f"validation loss increased over the same window."
        )
        break

training_duration_sec = time.perf_counter() - training_started_at
run_summary = summarize_training_run(epoch_history, training_duration_sec, run_status="complete")
if conf.swa and swa_model.n_averaged > 0:
    print(f"SWA: using weights averaged over {int(swa_model.n_averaged)} epochs")
    model.load_state_dict(swa_model.module.state_dict())
else:
    model.load_state_dict(best_model_state)
# Discovered hyperparameters (read off the final weights): surviving group widths from
# the gates and per-block Concrete Dropout rates. Empty dicts when the features are off.
# Consumed by run_test() below to record them into the metrics report/table.
surviving_structure = export_surviving_structure(model)
discovered_dropout_report = model.discovered_dropout()
if surviving_structure:
    print("Discovered surviving group widths (pruned architecture):")
    for gate_name, info in surviving_structure.items():
        print(f"  {gate_name}: {info['active']}/{info['total']} active")
if discovered_dropout_report:
    print("Discovered per-layer dropout:")
    for site_name, p in discovered_dropout_report.items():
        print(f"  {site_name}: {p:.4f}")
if conf.save_checkpoint:
    checkpoint_dir = os.path.join(checkpoints_root, label_name, excluded_set_name)
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, f"seed{conf.seed}.pt")
    torch.save(model.state_dict(), checkpoint_path)
    print(f"Saved checkpoint to {checkpoint_path}")
if conf.save_model:
    # Persist the final weights under models/<label>/<excluded_set>/seed<seed>.pt
    # so they can later be replayed for rho estimation (see
    # analysis/estimate_rho_elkan_noto.py). The CLI args are stored alongside as
    # args.json so the exact model + dataset split can be reconstructed.
    model_dir = os.path.join(models_root, label_name, excluded_set_name)
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"seed{conf.seed}.pt")
    torch.save(model.state_dict(), model_path)
    with open(os.path.join(model_dir, f"seed{conf.seed}.args.json"), "w") as f:
        json.dump(sys.argv[1:], f)
    print(f"Saved model to {model_path}")
run_test(run_summary)
