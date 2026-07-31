#!/usr/bin/env python3
import os
import sys
import time
import copy
import json
import re
from datetime import datetime

from pandas import read_csv
import torch
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
from architecture.final_layer import family_dann_loss
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
    reset_pu_loss_diagnostics,
)
from dataloader.sampler import ClassBalancedBatchSampler
from dataloader.New_dataloader import PLIDataset
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

dataset_file = (
    "Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv"
    if conf.lipid_isomers
    else "Processed_Negative_Interaction_Corrected_Domains.csv"
)
csv = read_csv(os.path.join(path, dataset_file))

train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir=path, csv = csv, seed=conf.seed,excluded_subgroups=conf.excluded_subgroups, config=conf, excluded_groups=conf.excluded_groups)
del csv
# Model construction stays after the split so frozen normalization cannot see
# validation/test proteins.
model = InteractionClassification(conf)
if conf.rnabang_frozen_node_adapter:
    model.set_rnabang_normalization(
        train_dataset.rnabang_normalization_stats()
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
if conf.protein_class_weight:
    protein_class_weights = train_dataset.get_protein_class_weights().to(device)
    common_weights_parts.append(protein_class_weights)
if conf.protein_class_sqrt_weight:
    protein_class_sqrt_weights = train_dataset.get_protein_class_weights(
        square_root=True,
    ).to(device)
    common_weights_parts.append(protein_class_sqrt_weights)
common_weights = (
    torch.stack(common_weights_parts).mean(dim=0)
    if common_weights_parts
    else torch.ones(len(train_dataset.id2pos), dtype=torch.float32, device=device)
)
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
    print(
        f"balanced batches : {len(train_loader_kwargs['batch_sampler'])} per epoch "
        f"covering all {train_labels.numel()} train rows, "
        f"target {conf.batch // 2} positive + {conf.batch // 2} unlabeled"
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

hyper_optimizer = None
if conf.bilevel and gate_params:
    # theta (with weight decay) + dropout logits (no weight decay) on train; the main
    # optimizer never touches the gate params -- those are stepped on validation below.
    main_groups = [{"params": theta_params, "weight_decay": conf.weight_decay}]
    if dropout_logit_params:
        main_groups.append({"params": dropout_logit_params, "weight_decay": 0.0})
    optimizer = torch.optim.Adam(main_groups, lr=conf.lr)
    hyper_optimizer = torch.optim.Adam(gate_params, lr=conf.bilevel_lr)
elif dropout_logit_params:
    # Not bilevel: everything trains on the train objective, but keep dropout logits out
    # of weight decay. Gates (if any) are learned via the train-loss penalty below.
    optimizer = torch.optim.Adam(
        [
            {"params": theta_params + gate_params, "weight_decay": conf.weight_decay},
            {"params": dropout_logit_params, "weight_decay": 0.0},
        ],
        lr=conf.lr,
    )
else:
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=conf.lr,
        weight_decay=conf.weight_decay,
    )


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
    stats["TP"] += int(((pred_class == labels) & (pred_class == 1)).sum().item())
    stats["FP"] += int(((pred_class != labels) & (pred_class == 1)).sum().item())
    stats["TN"] += int(((pred_class == labels) & (pred_class == 0)).sum().item())
    stats["FN"] += int(((pred_class != labels) & (pred_class == 0)).sum().item())
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
    ln 9 = 2.197. Logging the lambdas alongside them makes a ramped run readable after
    the fact -- otherwise the schedule is invisible and the loss curve uninterpretable.
    """
    for key, batches_key, name in (
        ("adv", "adv_batches", "adversary loss"),
        ("dann", "dann_batches", "family dann loss"),
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
    validate_prediction_label_shapes(outl_v, labels_v, "bilevel", 0)
    val_loss = _eval_task_loss(outl_v, labels_v)
    val_loss = val_loss + conf.sparsity_lambda * collect_sparsity_penalty(model).to(val_loss.device)
    val_loss.backward()
    hyper_optimizer.step()


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
    adversary_stats = {"adv": 0.0, "adv_batches": 0, "dann": 0.0, "dann_batches": 0}
    for i, graph in enumerate(train_loader):
        #dataset is reduced because of high variety of experience parameters 
        if i < train_batches_to_run:
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)

            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            optimizer.zero_grad()

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
                    batch_pair_ids = prot.sample_index.view(-1)[:sample_count]
                    grab_label_coefficients = train_dataset.get_grab_batch_inputs(batch_pair_ids, device)
                    pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                    if pos.shape[0] != sample_count:
                        raise ValueError(
                            f"GRAB tanimoto positions count {pos.shape[0]} "
                            f"does not match batch size {sample_count}"
                        )
                    if (pos < 0).any() or (pos >= common_weights.shape[0]).any():
                        invalid_positions = pos[
                            (pos < 0) | (pos >= common_weights.shape[0])
                        ].detach().cpu().tolist()
                        raise ValueError(
                            "GRAB tanimoto positions are outside the train weight table: "
                            f"{invalid_positions}"
                        )
                    sample_weights = common_weights[pos]
                    los = GRAB_loss(
                        loss_logits,
                        interaction_labels.long(),
                        grab_label_coefficients,
                        class_weights=class_weights,
                        sample_weights=sample_weights,
                        focal_gamma=conf.focal_gamma if conf.focal_loss else None)
                elif conf.pu_loss:
                    pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                    sample_weights = common_weights[pos]
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
                elif conf.loss_type == "cross_entropy":
                    pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                    sample_weights = common_weights[pos]
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
                    los = (los_unred * sample_weights).sum() / sample_weights.sum().clamp_min(1e-8)
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

            if use_amp:
                scaler.scale(los).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                los.backward()
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
    with torch.no_grad():
        print("VALIDATION")
        for i , graph in enumerate(valid_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)
    
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

            outl = model(**forward_args)
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
            else:
                los = conf.loss(outl, interaction_labels.long())
            # log_tb(writer_tb, countval, los,"valid",outl,interaction_labels.to(torch.float))
            pred_class = outl.argmax(dim=1)
            labels = interaction_labels.long()
            update_aggregate(valid_stats, pred_class, labels, los, sample_count)
            countval +=1
    train_metrics = aggregate_values(train_stats)
    valid_metrics = aggregate_values(valid_stats)
    log_epoch_metrics(writer_tb, idx, "train", train_metrics)
    log_epoch_metrics(writer_tb, idx, "valid", valid_metrics)
    log_adversary_metrics(writer_tb, idx, adversary_stats)
    if (idx + 1) % TENSORBOARD_FLUSH_EVERY_EPOCHS == 0:
        writer_tb.flush()
    print(f"valid epoch balanced_accuracy: {format_metric(valid_metrics['balanced_accuracy'])}")
    
    return counttrain, countval, train_metrics, valid_metrics


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

    with torch.no_grad():
        for i , graph in enumerate(test_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

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

            outl = model(**forward_args)
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
uses_fit_ramp = (conf.adversarial_grl and conf.adv_lambda_ramp_by_fit) or (
    conf.dann_family and conf.dann_lambda_ramp_by_fit
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
    model.train(True)
    countrain, countval, train_metrics, valid_metrics = epoch(epoch_number,countrain,countval)
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
