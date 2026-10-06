#!/usr/bin/env python3
"""Train one configuration, select a checkpoint, test it and record the result.

    python training/new_train.py --label=<name> [options]

Options are parsed by training/read_configuration.py (ModelConfig documents each one).
main() runs these steps; their order is part of reproducibility, because every step
that draws random numbers draws them in this order after seed_everything():

  1. configuration and seeds
  2. dataset split                  dataloader/Dataloader.py (PLIDataset)
  3. model                          architecture/interaction_classification.py
  4. loss weights from train rows   task_losses.py
  5. loaders, cache warm-up         dataloader/sampler.py, dataloader/preassembled_loader.py
  6. optimizer and lr schedule      optimizer_setup.py
  7. run directories, TensorBoard   run_paths.py
  8. epochs + checkpoint selection  epoch_loop.py, run_metrics.py
  9. saved weights, test report     final_evaluation.py -> results/tables/metrics_summary.csv
"""
import os
import sys
import time
import copy
import ctypes
import gc
import json
import re

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

import torch_geometric
from torch.utils.tensorboard import SummaryWriter

TRAINING_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, TRAINING_DIR)
sys.path.insert(0, PROJECT_ROOT)
# Appended, not inserted: analysis/ modules import their siblings by bare name, but
# nothing there may shadow a training/ or architecture/ module of the same name.
sys.path.append(os.path.join(PROJECT_ROOT, 'analysis'))

from read_configuration import read_configuration
from architecture.interaction_classification import InteractionClassification
from architecture.mlp_utils import export_surviving_structure
from dataloader.sampler import (
    ClassBalancedBatchSampler,
    RotatingNegativeBatchSampler,
)
from dataloader.dataset_source import interaction_csv_path
from dataloader.Dataloader import PLIDataset
from dataloader.pair_descriptors import descriptor_catalog_only
from dataloader.preassembled_loader import PreassembledLoader, preassembly_mode
from branch_dynamics import BranchDynamics
from epoch_loop import endless_batches, train_one_epoch
from optimizer_setup import OptimizerSetup, build_lr_scheduler
from reproducibility import seed_everything, seed_worker, seeded_generator
from run_context import RunContext
from run_metrics import (
    metric_has_positive_trend,
    rolling_metric_mean,
    summarize_training_run,
)
from run_paths import create_run_paths, excluded_set_name, run_label
from task_losses import TaskLosses
from final_evaluation import run_test


# Per-epoch cap on training rows: an epoch stops after this many rows' worth of batches.
TRAIN_ROWS_PER_EPOCH_CAP = 1740
EARLY_STOPPING_PATIENCE = 60


def load_pretrained_protein_encoder(conf, model, device):
    """Load --pretrained_checkpoint into the model, refusing any partial protein1 load."""
    # protein1's weights are only meaningful for the exact module structure they were
    # saved with (backend, hiddim, HEADS, single_gat_layer, protein_extra_node_
    # features, ...). Rather than re-deriving and comparing that flag list by hand
    # (easy to leave one out), lean on load_state_dict's own checks: a same-named,
    # differently-shaped parameter (e.g. a different hiddim) raises RuntimeError even
    # under strict=False, and a structural change (e.g. --geometric_transformer on
    # one side only) renames parameters, which shows up as protein1.* keys missing
    # below -- between the two, no silent partial/corrupted load gets through.
    pretrained_state = torch.load(conf.pretrained_checkpoint, map_location=device)
    args_path = re.sub(r"\.pt$", ".args.json", conf.pretrained_checkpoint)
    try:
        load_result = model.load_state_dict(pretrained_state, strict=False)
    except RuntimeError as shape_error:
        raise RuntimeError(
            f"pretrained_checkpoint={conf.pretrained_checkpoint} does not match "
            f"this run's protein1 architecture. Compare encoder flags against "
            f"{args_path} (written alongside the checkpoint by --save_model) if it "
            f"exists.\n{shape_error}"
        ) from shape_error
    missing_protein1 = [
        key for key in load_result.missing_keys if key.startswith("protein1.")
    ]
    if missing_protein1:
        raise RuntimeError(
            f"pretrained_checkpoint={conf.pretrained_checkpoint} is missing "
            f"protein1 weights this run's architecture needs (e.g. "
            f"{missing_protein1[0]}); the checkpoint likely used different "
            f"protein-encoder flags. Compare against {args_path} if it exists."
        )
    print(
        f"Loaded pretrained protein1 from {conf.pretrained_checkpoint} "
        f"({len(load_result.missing_keys)} missing / "
        f"{len(load_result.unexpected_keys)} unexpected keys overall, none of the "
        f"missing ones under protein1.)"
    )


def build_model(conf, train_dataset, device):
    """The classifier, normalised on train statistics, optionally with a pretrained protein1."""
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
    if conf.pretrained_checkpoint:
        load_pretrained_protein_encoder(conf, model, device)
    if conf.freeze_pretrained_encoders:
        for parameter in model.protein1.parameters():
            parameter.requires_grad = False
    return model


def build_loaders(conf, device, train_dataset, valid_dataset, test_dataset, train_labels):
    """(train, valid, test) DataLoaders and the rotating-negatives sampler, if any."""
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
    rotating_sampler = None
    if conf.rotate_train_negatives:
        # Takes precedence over the plain balanced-batch branch below and does not replace
        # it: --balanced_batches is passed through, so batch composition is still decided by
        # ClassBalancedBatchSampler -- over this epoch's active rows instead of over a
        # draw fixed for the whole run. Chunk default: the same number of negatives an epoch
        # would have held without the flag, so the per-epoch cost and class ratio are
        # unchanged and only WHICH negatives is different.
        del train_loader_kwargs["batch_size"], train_loader_kwargs["shuffle"]
        _train_positives = int((train_labels == 1).sum())
        rotating_chunk = conf.rotate_negatives_per_epoch or (
            conf.negatives_per_positive * _train_positives
        )
        rotating_sampler = RotatingNegativeBatchSampler(
            train_labels,
            conf.batch,
            rotating_chunk,
            conf.balanced_batches,
            generator=seeded_generator(conf.seed),
        )
        train_loader_kwargs["batch_sampler"] = rotating_sampler
        print(
            f"rotating negatives : {int(rotating_sampler.negative_order.numel())} train "
            f"negatives, {rotating_sampler.chunk} per epoch, one full pass every "
            f"{rotating_sampler.epochs_per_pass} epochs "
            f"({conf.ep / rotating_sampler.epochs_per_pass:.1f} passes over {conf.ep} "
            f"epochs), {len(rotating_sampler)} batches per epoch, "
            f"balanced_batches={bool(conf.balanced_batches)}"
        )
    elif conf.balanced_batches:
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
    return train_loader, valid_loader, test_loader, rotating_sampler


def warm_caches(train_dataset, valid_dataset, test_dataset):
    """Fill every per-sample cache once, then drop the source artifacts they came from."""
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


def checkpoint_selection_metric(conf):
    """(validation metric that selects the checkpoint, whether lower is better)."""
    # structural_pretrain has no Interaction label, so balanced_accuracy is undefined
    # (whatever the untrained classifier head outputs) -- checkpoint selection tracks
    # the lowest rolling reconstruction loss instead of the highest rolling BA.
    # valid_metrics["loss"] already IS the mean reconstruction MSE in this mode (see
    # TaskLosses.valid_loss), so this needs no new metric, only the opposite comparison
    # direction. --checkpoint_selection_metric overrides the non-structural_pretrain
    # default (validate() refuses it together with structural_pretrain, which always
    # selects by loss); "auc" reads valid_metrics' "AUC" key instead of
    # "balanced_accuracy" -- both are higher-is-better, only loss flips the comparison.
    if conf.structural_pretrain:
        selection_metric_name = "loss"
    elif conf.checkpoint_selection_metric == "auc":
        selection_metric_name = "AUC"
    elif conf.checkpoint_selection_metric:
        selection_metric_name = conf.checkpoint_selection_metric
    else:
        selection_metric_name = "balanced_accuracy"
    return selection_metric_name, selection_metric_name == "loss"


def set_epoch_schedules(run, epoch_number, epoch_progress, fit_progress, rotating_sampler):
    """Everything that changes at the top of an epoch, before its first batch."""
    conf, model = run.conf, run.model
    if rotating_sampler is not None:
        # Before the loader is iterated, the way DistributedSampler.set_epoch is used:
        # the sampler lives in this process and is re-walked at the start of every
        # epoch, so moving its window here is what the workers then receive.
        rotating_sampler.set_epoch(epoch_number)
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
        run.lipid_path_weight_now = conf.ramped_lipid_path_weight(epoch_number)
        run.optim.apply_lipid_path_handicap(run.lipid_path_weight_now)
    if conf.save_dynamics:
        run.dynamics.reset_grad_stats()
    # Rotates the residue subsample when --protein_residue_subsample is set; a no-op
    # otherwise. Before the epoch runs, so the masks belong to the epoch they are
    # numbered with.
    run.train_dataset.set_epoch(epoch_number)
    model.train(True)
    if conf.freeze_pretrained_encoders:
        # requires_grad=False stops protein1's weights from updating, but train(True)
        # above still leaves its own dropout/batchnorm submodules stochastic -- eval()
        # here keeps it acting exactly as it did when structural_pretrain saved it.
        model.protein1.eval()


def save_weights(conf, paths, model, final_model_state):
    """--save_checkpoint / --save_model: the selected weights and the last epoch's."""
    if conf.save_checkpoint:
        # Two files, both under checkpoints/<label>/<excluded_set>/: seed<N>.pt holds the
        # weights this run is judged on (the rolling-valid-BA pick loaded just above),
        # seed<N>_final.pt the last epoch's.
        checkpoint_dir = paths.run_checkpoints_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"seed{conf.seed}.pt")
        torch.save(model.state_dict(), checkpoint_path)
        print(f"Saved checkpoint to {checkpoint_path}")
        final_checkpoint_path = os.path.join(checkpoint_dir, f"seed{conf.seed}_final.pt")
        torch.save(final_model_state, final_checkpoint_path)
        print(f"Saved end-of-training weights to {final_checkpoint_path}")
    if conf.save_model:
        # Persist the weights under models/<label>/<excluded_set>/ so they can later be
        # rescored for a metric added after the run (analysis/checkpoint_scores.py). seed<seed>.pt is
        # the tested pick; seed<seed>_final.pt is the last epoch. The CLI args are stored
        # alongside as args.json so the exact model + dataset split can be reconstructed --
        # one args.json covers both, the weights differ but the run does not.
        model_dir = paths.run_models_dir
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"seed{conf.seed}.pt")
        torch.save(model.state_dict(), model_path)
        final_model_path = os.path.join(model_dir, f"seed{conf.seed}_final.pt")
        torch.save(final_model_state, final_model_path)
        with open(os.path.join(model_dir, f"seed{conf.seed}.args.json"), "w") as f:
            json.dump(sys.argv[1:], f)
        print(f"Saved model to {model_path}")
        print(f"Saved end-of-training weights to {final_model_path}")


def main():
    # 1. configuration and seeds
    conf = read_configuration()
    if conf.final_m is None:
        conf.final_m = conf.m

    seed_everything(conf.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print()

    # 2. dataset split
    path=os.path.join(PROJECT_ROOT, "data") + os.sep

    csv = read_csv(interaction_csv_path(path))

    train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir=path, csv = csv, seed=conf.seed,excluded_subgroups=conf.excluded_subgroups, config=conf, excluded_groups=conf.excluded_groups)
    del csv

    # 3. model
    model = build_model(conf, train_dataset, device)
    number_of_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"number of parameters : {number_of_parameters}")

    # 4. loss weights, priors and class weights from the train split
    losses = TaskLosses(conf, train_dataset, device)

    # 5. loaders and caches
    train_loader, valid_loader, test_loader, rotating_sampler = build_loaders(
        conf, device, train_dataset, valid_dataset, test_dataset, losses.train_labels
    )
    warm_caches(train_dataset, valid_dataset, test_dataset)
    _return_freed_heap_to_kernel()
    train_batches_to_run = min(
        len(train_loader), (TRAIN_ROWS_PER_EPOCH_CAP + conf.batch - 1) // conf.batch
    )
    if rotating_sampler is not None and train_batches_to_run < len(train_loader):
        # The 1740-row cap above predates this flag and is silent: it simply stops the
        # training loop early (`if i < train_batches_to_run`). A rotating epoch larger than
        # the cap is therefore not the epoch that was asked for -- the slice still MOVES, so
        # the pool is still covered, but each epoch trains on the cap's worth of it. Said out
        # loud rather than left to be inferred from the batch counter.
        print(
            f"rotating negatives : --rotate_negatives_per_epoch asks for "
            f"{len(train_loader)} batches, the {TRAIN_ROWS_PER_EPOCH_CAP}-row per-epoch cap allows "
            f"{train_batches_to_run}; the remaining batches of each epoch are skipped"
        )
    if conf.deepclip or descriptor_catalog_only(conf):
        # Each split as a few tensors on the device, batched by indexing, instead of PyG
        # re-collating the same cached samples every batch (dataloader/preassembled_
        # loader.py). Same batches in the same order, and the same lipid candidate drawn
        # for each row: the loader built above still supplies its own sampler and
        # generator, and the draws are replayed on the generator get() would have used
        # (this process's; a split that draws with num_workers > 0 keeps its DataLoader).
        # Skipped for a split whose samples change in any other way per access, and for
        # train when the 1740-row cap cuts epochs short AND workers run -- they prefetch
        # past the stop, which this does not mirror. Without workers both loaders stop the
        # same way: the loop fetches one batch past the cap (drawing its candidates) and
        # breaks, and a generator is left mid-sampler exactly like the DataLoader iterator.
        preassembled_splits = []
        if preassembly_mode(train_dataset, conf.num_workers) and (
            train_batches_to_run == len(train_loader) or conf.num_workers == 0
        ):
            train_loader = PreassembledLoader(train_loader, device)
            preassembled_splits.append("train")
        if preassembly_mode(valid_dataset, conf.num_workers):
            valid_loader = PreassembledLoader(valid_loader, device)
            preassembled_splits.append("valid")
        if preassembly_mode(test_dataset, conf.num_workers):
            test_loader = PreassembledLoader(test_loader, device)
            preassembled_splits.append("test")
        print(f"preassembled splits : {preassembled_splits or 'none'}")
    print("data extracted")

    # 6. optimizer and lr schedule
    optim = OptimizerSetup(conf, model)
    hyper_val_iter = (
        endless_batches(valid_loader) if optim.hyper_optimizer is not None else None
    )
    use_amp = conf.type_opt and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    lr_scheduler = build_lr_scheduler(conf, optim.optimizer)

    # 7. run directories and TensorBoard
    label_name = run_label(conf)
    conf.label = label_name
    paths = create_run_paths(
        PROJECT_ROOT, conf, label_name, excluded_set_name(conf), number_of_parameters
    )
    writer_tb = SummaryWriter(paths.log_dir)

    run = RunContext(
        conf=conf,
        device=device,
        model=model,
        train_dataset=train_dataset,
        train_loader=train_loader,
        valid_loader=valid_loader,
        test_loader=test_loader,
        train_batches_to_run=train_batches_to_run,
        losses=losses,
        optim=optim,
        use_amp=use_amp,
        scaler=scaler,
        hyper_val_iter=hyper_val_iter,
        writer=writer_tb,
        dynamics=BranchDynamics(conf, model, device, valid_loader, writer_tb, losses),
        paths=paths,
        number_of_parameters=number_of_parameters,
        lipid_path_weight_now=conf.lipid_path_weight,
    )

    # 8. epochs, with checkpoint selection on the rolling validation metric
    epoch_number = 0
    EPOCHS = conf.ep
    countrain =0
    countval =0
    best_valid_selection_metric = None
    best_epoch = None
    best_model_state = None
    epoch_history = []
    epochs_without_checkpoint_improvement = 0
    checkpoint_window = conf.checkpoint_window
    early_stopping_patience = EARLY_STOPPING_PATIENCE
    selection_metric_name, lower_selection_metric_is_better = checkpoint_selection_metric(conf)
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
        set_epoch_schedules(run, epoch_number, epoch_progress, fit_progress, rotating_sampler)
        countrain, countval, train_metrics, valid_metrics = train_one_epoch(
            run, epoch_number, countrain, countval
        )
        if conf.save_dynamics:
            # After the epoch's own validation, so the ablated passes are compared against a
            # full-model number measured on the same weights.
            run.dynamics.log(epoch_number, valid_metrics)
        if conf.save_model_in_dynamics:
            # No longer nested under save_dynamics: the checkpoint itself does not depend on
            # the curve-logging pass above (save_milestone only reads model/conf), so a run
            # that wants milestones without the two extra ablated validation passes (e.g.
            # --descriptors_head, where those passes are no-ops -- see read_
            # configuration.py's save_dynamics docstring) can set this flag alone.
            run.dynamics.save_milestone(epoch_number + 1, paths.run_models_dir)
        if uses_fit_ramp:
            fit_progress = max(
                fit_progress,
                conf.adv_fit_progress(train_metrics.get("balanced_accuracy")),
            )
        rolling_valid_selection_metric = rolling_metric_mean(
            [
                *epoch_history,
                {"train": train_metrics, "valid": valid_metrics},
            ],
            "valid",
            selection_metric_name,
            window=checkpoint_window,
        )
        valid_metrics["checkpoint_selection_metric"] = rolling_valid_selection_metric
        epoch_history.append({"train": train_metrics, "valid": valid_metrics})
        is_new_best_metric = (
            rolling_valid_selection_metric is not None
            and best_valid_selection_metric is not None
            and (
                rolling_valid_selection_metric < best_valid_selection_metric
                if lower_selection_metric_is_better
                else rolling_valid_selection_metric > best_valid_selection_metric
            )
        )
        if best_model_state is None or (
            rolling_valid_selection_metric is not None
            and (best_valid_selection_metric is None or is_new_best_metric)
        ):
            best_valid_selection_metric = rolling_valid_selection_metric
            best_epoch = epoch_number
            best_model_state = copy.deepcopy(model.state_dict())
            epochs_without_checkpoint_improvement = 0
        else:
            epochs_without_checkpoint_improvement += 1
        if lr_scheduler is not None:
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

    # 9. selected weights, saved files and the test report
    training_duration_sec = time.perf_counter() - training_started_at
    run_summary = summarize_training_run(epoch_history, training_duration_sec, run_status="complete")
    # The weights as the last epoch left them, captured before the line below overwrites them
    # with the selected ones. Both are written out by --save_checkpoint/--save_model:
    # seed<N>.pt is what run_test actually measures, seed<N>_final.pt is where training was
    # still heading. Keeping only one of the two has already cost this project a result --
    # a past comparison had to score two configs off epoch-120 milestones because their
    # selected weights were never saved, and every comparison against them then carried a
    # weights-rule mismatch as a caveat.
    final_model_state = copy.deepcopy(model.state_dict())
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
    save_weights(conf, paths, model, final_model_state)
    run_test(run, run_summary, surviving_structure, discovered_dropout_report)


if __name__ == "__main__":
    main()
