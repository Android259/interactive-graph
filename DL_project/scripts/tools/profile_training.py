#!/usr/bin/env python3
"""Profile one training step of InteractionClassification with torch.profiler.

Builds the real model/dataset/optimizer exactly like training/new_train.py (same
--key=value config flags) and runs a handful of real batches through the actual
per-step training (or eval) body under torch.profiler, then writes:

  - trace.json            Chrome/Perfetto trace (chrome://tracing or ui.perfetto.dev)
  - ops_by_time.txt        top ops by self CPU/CUDA time
  - ops_by_memory.txt      top ops by self CPU/CUDA memory
  - summary.txt            human-readable report: throughput, top ops, peak memory (RSS,
                            plus CUDA allocated/reserved when run on GPU)
  - memory_timeline.html   memory-over-time breakdown, only with --with_stack (adds
  - stacks_*.txt           flamegraph-ready stack dumps  overhead and a much bigger trace.json)

train_dataset.warm_caches() is deliberately skipped: it eagerly reads every protein
graph and lipid encoding in the split (the largest files in data/, e.g. the ESM3
embeddings), which a handful of profiled batches never need. PLIDataset.get() caches
lazily per row, so only what the sampled batches actually touch gets loaded.

Usage:
    python scripts/tools/profile_training.py [profiler options] [-- model config flags]

Examples:
    python scripts/tools/profile_training.py --active_steps=10
    python scripts/tools/profile_training.py --phase=eval --active_steps=5 -- --batch=32 --hiddim=128
"""

from __future__ import annotations

import argparse
import os
import resource
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

# parents[2]: this file sits in scripts/tools/, so the project root is two levels up.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TRAINING_DIR = str(ROOT / "training")
if TRAINING_DIR not in sys.path:
    sys.path.insert(0, TRAINING_DIR)

import torch
import torch.nn.functional as F
import torch_geometric
from pandas import read_csv

from architecture.final_layer import family_dann_loss
from architecture.interaction_classification import InteractionClassification
from architecture.loss import (
    GRAB_loss,
    Non_Negative_Positive_Unlabeled_loss,
    focal_loss,
    logit_adjustment_bias,
)
from architecture.mlp_utils import (
    ConcreteDropout,
    collect_concrete_dropout_reg,
    collect_gate_parameters,
    collect_sparsity_penalty,
)
from dataloader.sampler import ClassBalancedBatchSampler
from dataloader.dataset_source import interaction_csv_path
from dataloader.Dataloader import PLIDataset
from read_configuration import read_named_configuration
from reproducibility import seed_everything, seed_worker, seeded_generator


def parse_args(argv):
    """Split profiler-only flags from the model config flags.

    Everything after a literal "--" (or simply not recognized here) is forwarded
    verbatim to read_named_configuration, exactly like new_train.py's own CLI.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phase", choices=["train", "eval"], default="train",
                         help="Profile a full train step (forward+loss+backward+optimizer) "
                              "or a forward-only eval step.")
    parser.add_argument("--wait_steps", type=int, default=2)
    parser.add_argument("--warmup_steps", type=int, default=3)
    parser.add_argument("--active_steps", type=int, default=5)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--num_workers", type=int, default=0,
                         help="DataLoader workers for the profiling run itself. Kept at 0 "
                              "by default so all data-loading time is attributed to the "
                              "main process in the trace, instead of hiding in a worker.")
    parser.add_argument("--device", choices=["cpu", "cuda"], default=None,
                         help="Override device autodetection.")
    parser.add_argument("--output_dir", default=str(ROOT / "profiler_runs"))
    parser.add_argument("--row_limit", type=int, default=40)
    parser.add_argument("--sort_by", default=None,
                         help="Override the ops_by_time.txt sort key "
                              "(default: self_cuda_time_total on GPU, else self_cpu_time_total).")
    parser.add_argument("--with_stack", action="store_true",
                         help="Record Python call stacks. Unlocks memory_timeline.html and "
                              "stacks_*.txt (flamegraph input), at the cost of noticeably "
                              "more overhead and a much larger trace.json (stacks get "
                              "embedded in the trace too -- tens to hundreds of MB even for "
                              "a handful of steps). ops_by_memory.txt and peak-memory "
                              "figures in summary.txt do not need this flag.")
    parser.add_argument("--no_record_shapes", action="store_true",
                         help="Disable input-shape recording (small speedup, less context).")
    parser.add_argument("--no_memory_timeline", action="store_true",
                         help="Skip the memory_timeline.html export.")
    args, model_args = parser.parse_known_args(argv)
    if model_args and model_args[0] == "--":
        model_args = model_args[1:]
    return args, model_args


def build_forward_args(conf, prot, lipid):
    """Assemble model forward kwargs for a protein/lipid batch (mirrors new_train.py)."""
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
    # These three were in new_train.py and not here, so profiling any run with
    # --geometric_transformer or --rnabang_frozen_node_adapter died inside the protein
    # encoder ("requires precomputed node features") -- a stale duplicate presenting
    # itself as a broken config. Keep them in step with new_train.py's loops.
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


def main():
    args, model_args = parse_args(sys.argv[1:])

    conf = read_named_configuration(["profile_training.py"] + model_args)
    if conf.final_m is None:
        conf.final_m = conf.m

    seed_everything(conf.seed)

    if args.device is not None:
        device = torch.device(args.device)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device : {device}")

    model = InteractionClassification(conf).to(device)
    number_of_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"number of parameters : {number_of_parameters}")

    path = os.path.join(ROOT, "data") + os.sep
    csv = read_csv(interaction_csv_path(path))

    train_dataset, valid_dataset, _test_dataset = PLIDataset(
        root_dir=path, csv=csv, seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )
    # No warm_caches() here on purpose -- see module docstring: a short profiling run
    # only needs the handful of rows its sampled batches draw, not the whole split's
    # protein graphs and lipid encodings.

    common_weights_parts = []
    if conf.tanimoto_weight:
        common_weights_parts.append(train_dataset.get_tanimoto_weights().to(device))
    if conf.protein_group_weight:
        common_weights_parts.append(train_dataset.get_protein_weights().to(device))
    if conf.protein_class_weight:
        common_weights_parts.append(train_dataset.get_protein_class_weights().to(device))
    if conf.protein_class_sqrt_weight:
        common_weights_parts.append(train_dataset.get_protein_class_weights(square_root=True).to(device))
    common_weights = (
        torch.stack(common_weights_parts).mean(dim=0)
        if common_weights_parts
        else torch.ones(len(train_dataset.id2pos), dtype=torch.float32, device=device)
    )
    train_labels = torch.as_tensor(train_dataset.csvtrain["Interaction"].values, dtype=torch.long)
    class_counts = torch.bincount(train_labels, minlength=2).float()
    if conf.pu_loss:
        conf.pu_rho = conf.effective_pu_rho(
            positive_count=class_counts[1].item(), unlabeled_count=class_counts[0].item(),
        )
    class_weights = None
    if conf.class_weights:
        class_weights = (class_counts.sum() / (2.0 * class_counts.clamp_min(1.0))).to(device)
    logit_adjustment_bias_tensor = None
    if conf.logit_adjustment:
        logit_adjustment_bias_tensor = logit_adjustment_bias(class_counts, tau=conf.logit_adjustment_tau).to(device)

    loader_kwargs = {
        "batch_size": conf.batch,
        "shuffle": True,
        "pin_memory": device.type == "cuda",
        "num_workers": args.num_workers,
        "persistent_workers": args.num_workers > 0,
        "worker_init_fn": seed_worker,
    }
    if args.num_workers > 0:
        loader_kwargs["prefetch_factor"] = 4

    train_loader_kwargs = dict(loader_kwargs)
    if conf.balanced_batches:
        del train_loader_kwargs["batch_size"], train_loader_kwargs["shuffle"]
        train_loader_kwargs["batch_sampler"] = ClassBalancedBatchSampler(
            train_labels, conf.batch, generator=seeded_generator(conf.seed),
        )

    train_loader = torch_geometric.loader.DataLoader(
        train_dataset, generator=seeded_generator(conf.seed), **train_loader_kwargs,
    )
    valid_loader = torch_geometric.loader.DataLoader(
        valid_dataset, generator=seeded_generator(conf.seed + 1), **loader_kwargs,
    )

    gate_params = collect_gate_parameters(model)
    gate_param_ids = {id(p) for p in gate_params}
    dropout_logit_params = [m.logit for m in model.modules() if isinstance(m, ConcreteDropout)]
    dropout_logit_ids = {id(p) for p in dropout_logit_params}
    theta_params = [p for p in model.parameters() if id(p) not in gate_param_ids and id(p) not in dropout_logit_ids]

    hyper_optimizer = None
    if conf.bilevel and gate_params:
        main_groups = [{"params": theta_params, "weight_decay": conf.weight_decay}]
        if dropout_logit_params:
            main_groups.append({"params": dropout_logit_params, "weight_decay": 0.0})
        optimizer = torch.optim.Adam(main_groups, lr=conf.lr)
        hyper_optimizer = torch.optim.Adam(gate_params, lr=conf.bilevel_lr)
    elif dropout_logit_params:
        optimizer = torch.optim.Adam(
            [
                {"params": theta_params + gate_params, "weight_decay": conf.weight_decay},
                {"params": dropout_logit_params, "weight_decay": 0.0},
            ],
            lr=conf.lr,
        )
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=conf.lr, weight_decay=conf.weight_decay)

    use_amp = conf.type_opt and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    if conf.adversarial_grl:
        model.final_layer.adv_lambda_now = conf.adv_lambda
    if conf.dann_family:
        model.final_layer.dann_lambda_now = conf.dann_lambda

    def endless_batches(loader):
        while True:
            for batch in loader:
                yield batch

    train_iter = endless_batches(train_loader)
    hyper_val_iter = endless_batches(valid_loader) if hyper_optimizer is not None else None

    def bilevel_lambda_step():
        prot_v, lipid_v = next(hyper_val_iter)
        prot_v = prot_v.to(device, non_blocking=True)
        lipid_v = lipid_v.to(device, non_blocking=True)
        labels_v = prot_v.inter.to(device, non_blocking=True)
        hyper_optimizer.zero_grad()
        outl_v = model(**build_forward_args(conf, prot_v, lipid_v))
        if conf.pu_loss:
            val_loss = Non_Negative_Positive_Unlabeled_loss(
                outl_v, labels_v.long(), conf.pu_rho, beta=conf.pu_beta,
                gamma=conf.pu_gamma, tau=conf.pu_tau, cap=conf.pu_loss_cap,
            )
        else:
            val_loss = conf.loss(outl_v, labels_v.long())
        val_loss = val_loss + conf.sparsity_lambda * collect_sparsity_penalty(model).to(val_loss.device)
        val_loss.backward()
        hyper_optimizer.step()

    def train_step():
        """One real training step: forward, task loss (+ any extra penalty terms),
        backward, optimizer step -- exactly the body training/new_train.py runs per
        batch, minus TensorBoard/metric bookkeeping that is not what we're timing here.
        """
        with torch.profiler.record_function("dataloader_next"):
            prot, lipid = next(train_iter)
        with torch.profiler.record_function("batch_to_device"):
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter.to(device, non_blocking=True)

        optimizer.zero_grad()

        with torch.profiler.record_function("forward"):
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                outl = model(**build_forward_args(conf, prot, lipid))
                sample_count = outl.shape[0]
                loss_logits = outl + logit_adjustment_bias_tensor if conf.logit_adjustment else outl

                with torch.profiler.record_function("loss"):
                    if conf.grab_loss:
                        batch_pair_ids = prot.pair_id.view(-1)[:sample_count]
                        grab_label_coefficients = train_dataset.get_grab_batch_inputs(batch_pair_ids, device)
                        pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                        sample_weights = common_weights[pos]
                        los = GRAB_loss(
                            loss_logits, interaction_labels.long(), grab_label_coefficients,
                            class_weights=class_weights, sample_weights=sample_weights,
                            focal_gamma=conf.focal_gamma if conf.focal_loss else None,
                        )
                    elif conf.pu_loss:
                        pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                        sample_weights = common_weights[pos]
                        los = Non_Negative_Positive_Unlabeled_loss(
                            loss_logits, interaction_labels.long(), conf.pu_rho,
                            beta=conf.pu_beta, gamma=conf.pu_gamma, tau=conf.pu_tau,
                            cap=conf.pu_loss_cap, sample_weights=sample_weights,
                        )
                    elif conf.loss_type == "cross_entropy":
                        pos = prot.tanimoto_pos.view(-1).to(device, non_blocking=True)[:sample_count]
                        sample_weights = common_weights[pos]
                        if conf.focal_loss:
                            los_unred = focal_loss(
                                loss_logits, interaction_labels.long(), gamma=conf.focal_gamma,
                                class_weights=class_weights, reduction="none",
                            )
                        else:
                            los_unred = F.cross_entropy(
                                loss_logits, interaction_labels.long(),
                                weight=class_weights, reduction="none",
                            )
                        los = (los_unred * sample_weights).sum() / sample_weights.sum().clamp_min(1e-8)
                    else:
                        los = conf.loss(outl, interaction_labels.long())

                if gate_params and conf.sparsity_lambda > 0.0 and not conf.bilevel:
                    los = los + conf.sparsity_lambda * collect_sparsity_penalty(model).to(los.device)
                if conf.bilevel_dropout:
                    los = los + collect_concrete_dropout_reg(model).to(los.device)
                if conf.adversarial_grl:
                    adv = model.final_layer._adv
                    if adv is not None:
                        terms = [
                            F.cross_entropy(logits, interaction_labels.long())
                            for logits in adv if logits is not None
                        ]
                        if terms:
                            los = los + conf.adv_weight * torch.stack(terms).mean()
                if conf.dann_family:
                    dann_features = model.final_layer._dann_features
                    if dann_features is not None:
                        dann_loss = family_dann_loss(
                            dann_features, prot.family.view(dann_features.shape[0], -1),
                            interaction_labels.long(), model.final_layer.family_adversaries,
                            conf.dann_class_conditional,
                        )
                        los = los + conf.dann_weight * dann_loss

        with torch.profiler.record_function("backward"):
            if use_amp:
                scaler.scale(los).backward()
            else:
                los.backward()

        with torch.profiler.record_function("optimizer_step"):
            if use_amp:
                scaler.step(optimizer)
                scaler.update()
            else:
                optimizer.step()

        if hyper_optimizer is not None:
            with torch.profiler.record_function("bilevel_lambda_step"):
                bilevel_lambda_step()

    valid_iter = endless_batches(valid_loader)

    def eval_step():
        """One forward-only pass over a validation batch (no grad, no optimizer)."""
        with torch.profiler.record_function("dataloader_next"):
            prot, lipid = next(valid_iter)
        with torch.profiler.record_function("batch_to_device"):
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter.to(device, non_blocking=True)
        with torch.profiler.record_function("forward"), torch.no_grad():
            outl = model(**build_forward_args(conf, prot, lipid))
            with torch.profiler.record_function("loss"):
                if conf.pu_loss:
                    Non_Negative_Positive_Unlabeled_loss(
                        outl, interaction_labels.long(), conf.pu_rho, beta=conf.pu_beta,
                        gamma=conf.pu_gamma, tau=conf.pu_tau, cap=conf.pu_loss_cap,
                    )
                else:
                    conf.loss(outl, interaction_labels.long())

    if args.phase == "train":
        model.train(True)
        step_fn = train_step
    else:
        model.eval()
        step_fn = eval_step

    activities = [torch.profiler.ProfilerActivity.CPU]
    if device.type == "cuda":
        activities.append(torch.profiler.ProfilerActivity.CUDA)
        torch.cuda.reset_peak_memory_stats(device)

    prof_schedule = torch.profiler.schedule(
        wait=args.wait_steps, warmup=args.warmup_steps,
        active=args.active_steps, repeat=max(args.repeat, 1),
    )
    total_steps = (args.wait_steps + args.warmup_steps + args.active_steps) * max(args.repeat, 1)
    record_shapes = not args.no_record_shapes
    with_stack = args.with_stack

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = conf.label.strip() or "profile"
    out_dir = Path(args.output_dir) / run_name / f"{args.phase}_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"profiling {args.phase} phase : {total_steps} steps "
        f"(wait={args.wait_steps} warmup={args.warmup_steps} active={args.active_steps} repeat={args.repeat}) "
        f"on batch={conf.batch}, num_workers={args.num_workers}"
    )
    started_at = time.perf_counter()
    with torch.profiler.profile(
        activities=activities,
        schedule=prof_schedule,
        record_shapes=record_shapes,
        profile_memory=True,
        with_stack=with_stack,
        # verbose=True is what actually attaches a Python call stack to each op event
        # on this torch build -- without it export_stacks()/memory_timeline silently
        # produce an empty/frame-less output even with with_stack=True.
        experimental_config=torch.profiler._ExperimentalConfig(verbose=True) if with_stack else None,
        # Without this, the profiler drops every cycle but the last when repeat > 1
        # (see UserWarning "Profiler clears events at the end of each cycle").
        acc_events=True,
    ) as prof:
        for _ in range(total_steps):
            step_fn()
            prof.step()
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    wall_time = time.perf_counter() - started_at

    trace_path = out_dir / "trace.json"
    prof.export_chrome_trace(str(trace_path))

    time_sort_by = args.sort_by or ("self_cuda_time_total" if device.type == "cuda" else "self_cpu_time_total")
    mem_sort_by = "self_cuda_memory_usage" if device.type == "cuda" else "self_cpu_memory_usage"

    averages = prof.key_averages(group_by_input_shape=False)
    ops_by_time_table = averages.table(sort_by=time_sort_by, row_limit=args.row_limit)
    ops_by_memory_table = averages.table(sort_by=mem_sort_by, row_limit=args.row_limit)

    (out_dir / "ops_by_time.txt").write_text(ops_by_time_table + "\n")
    (out_dir / "ops_by_memory.txt").write_text(ops_by_memory_table + "\n")

    if with_stack:
        prof.export_stacks(str(out_dir / "stacks_cpu.txt"), "self_cpu_time_total")
        if device.type == "cuda":
            prof.export_stacks(str(out_dir / "stacks_cuda.txt"), "self_cuda_time_total")

    memory_timeline_path = None
    if not args.no_memory_timeline and not with_stack:
        print("memory_timeline export skipped: pass --with_stack to enable it")
    elif not args.no_memory_timeline:
        memory_timeline_path = out_dir / "memory_timeline.html"
        try:
            with warnings.catch_warnings():
                # export_memory_timeline is deprecated in favor of the CUDA-only
                # torch.cuda.memory._record_memory_history snapshot API, which has no
                # CPU equivalent -- keep using the deprecated call so this also works
                # for CPU-only profiling runs.
                warnings.filterwarnings("ignore", category=FutureWarning)
                prof.export_memory_timeline(str(memory_timeline_path), device=str(device))
        except Exception as exc:  # pragma: no cover - depends on torch build/platform
            print(f"memory_timeline export skipped: {exc}")
            memory_timeline_path = None

    peak_rss_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    cuda_lines = []
    if device.type == "cuda":
        cuda_lines = [
            f"CUDA peak allocated : {torch.cuda.max_memory_allocated(device) / 2**20:.1f} MiB",
            f"CUDA peak reserved  : {torch.cuda.max_memory_reserved(device) / 2**20:.1f} MiB",
        ]

    active_steps_total = args.active_steps * max(args.repeat, 1)
    summary_lines = [
        f"phase                 : {args.phase}",
        f"device                : {device}",
        f"config                : batch={conf.batch} hiddim={conf.hiddim} m={conf.m} "
        f"HEADS={conf.HEADS} amp={use_amp}",
        f"parameters            : {number_of_parameters}",
        f"steps profiled        : {total_steps} total, {active_steps_total} active "
        f"(wait={args.wait_steps} warmup={args.warmup_steps} active={args.active_steps} repeat={args.repeat})",
        f"wall time             : {wall_time:.3f} s for {total_steps} steps "
        f"({wall_time / total_steps * 1000:.1f} ms/step average, includes wait+warmup)",
        f"process peak RSS      : {peak_rss_mib:.1f} MiB",
        *cuda_lines,
        "",
        f"trace                 : {trace_path}",
        f"ops by time           : {out_dir / 'ops_by_time.txt'}",
        f"ops by memory         : {out_dir / 'ops_by_memory.txt'}",
    ]
    if memory_timeline_path is not None:
        summary_lines.append(f"memory timeline       : {memory_timeline_path}")
    if with_stack:
        summary_lines.append(f"stacks                : {out_dir / 'stacks_cpu.txt'}"
                              + (f", {out_dir / 'stacks_cuda.txt'}" if device.type == "cuda" else ""))
    summary_lines += [
        "",
        f"top {args.row_limit} ops by self time ({time_sort_by}):",
        ops_by_time_table,
        "",
        f"top {args.row_limit} ops by self memory ({mem_sort_by}):",
        ops_by_memory_table,
    ]
    summary_text = "\n".join(summary_lines)
    (out_dir / "summary.txt").write_text(summary_text + "\n")

    print(summary_text)
    print(f"\nfull artifacts written to {out_dir}")
    print("open trace.json at chrome://tracing or https://ui.perfetto.dev for the interactive timeline")


if __name__ == "__main__":
    main()
