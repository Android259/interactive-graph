#!/usr/bin/env python3
"""Estimate the PU prior ``rho`` from saved model weights via the Elkan-Noto method.

Background
----------
In this project ``rho`` is the class prior of the training pool and is derived in
``training/read_configuration.py`` as::

    effective_pu_rho = (P + f * U) / (P + U)

where ``P`` = labeled positives in the train pool, ``U`` = sampled unlabeled, and
``f = pu_unlabeled_positive_fraction`` = the fraction of the unlabeled that are
*actually* positive. So estimating ``rho`` reduces to estimating ``f``.

Elkan-Noto (2008), "Learning classifiers from only positive and unlabeled data":
let ``s = 1`` mark a labeled positive and ``s = 0`` an unlabeled example. Train a
classifier ``g(x) = P(s = 1 | x)`` (here: ``softmax(model_logits)[:, 1]`` from a
saved checkpoint). Under SCAR (labeled positives are a random sample of all
positives) the labeling propensity ``c = P(labeled | positive)`` is constant, and:

    c_hat = mean over HELD-OUT KNOWN POSITIVES of g(x)          # estimator "e1"
    P(y = 1 | x) = g(x) / c_hat
    f_hat = mean over HELD-OUT UNLABELED of ( g(x) / c_hat )    # hidden-pos rate

We estimate ``c_hat`` and ``f_hat`` on held-out data (the excluded-group
validation/test split), because ``g`` is optimistically biased on rows the model
trained on. We then plug ``f_hat`` and the TRAIN-pool counts ``P``/``U`` into the
project's own rho formula, so the printed ``rho`` matches what training would use
with ``--pu_unlabeled_positive_fraction=f_hat``.

Assumptions / caveats
---------------------
* SCAR: labeled positives are representative of all positives. If positive
  sampling is biased, ``c_hat`` (and thus ``rho``) is biased.
* Reasonable calibration of ``g``. nnPU models are not perfectly calibrated, so
  treat the estimate as the CENTER of a small grid, not an exact value.
* Because the held-out split is seed-dependent, run this across seeds and inspect
  the spread before trusting a single number.

Usage
-----
Pass the SAME training args used to produce the checkpoint (typically the arg
file), plus ``--weights`` (or let it default to the ``--save_model`` location)::

    python3 analysis/estimate_rho_elkan_noto.py \
        $(cat scripts/arg_files/<label>.md) --seed 0 \
        --excluded_groups gltp \
        --weights models/<label>/groups_gltp/seed0.pt

Only estimation-specific flags below are consumed by this script; every other
argument is forwarded verbatim to ``read_configuration`` so the model and the
dataset split are reconstructed exactly as in training.
"""

from __future__ import annotations

import glob
import json
import math
import os
import statistics
import sys
from collections import defaultdict

import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRAINING_DIR = os.path.join(PROJECT_ROOT, "training")
sys.path.insert(0, TRAINING_DIR)
sys.path.insert(0, PROJECT_ROOT)

from pandas import read_csv  # noqa: E402
import torch_geometric  # noqa: E402

from read_configuration import read_configuration  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402


# --- Estimation-specific flags (stripped before building the training config) ---
SCRIPT_FLAGS_WITH_VALUE = {"--weights", "--pool", "--device", "--label", "--models_root"}


def split_script_args(argv):
    """Separate this script's own flags from the training-config arguments.

    Returns (script_opts, config_argv). ``config_argv`` is prefixed with a dummy
    program name because ``read_configuration`` parses ``argv[1:]``. In --label
    mode the config comes from each checkpoint's saved args.json, so config_argv
    is unused.
    """
    script_opts = {"weights": None, "pool": "test", "device": None,
                   "label": None, "models_root": None}
    config_args = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in SCRIPT_FLAGS_WITH_VALUE:
            script_opts[token.lstrip("-")] = argv[i + 1]
            i += 2
        elif any(token.startswith(flag + "=") for flag in SCRIPT_FLAGS_WITH_VALUE):
            key, value = token[2:].split("=", 1)
            script_opts[key] = value
            i += 1
        elif not token.startswith("-") and script_opts["label"] is None:
            # A bare positional token is the label (single-checkpoint config args
            # are always --flag/--flag=value), so `... LABEL` alone runs the sweep.
            script_opts["label"] = token
            i += 1
        else:
            config_args.append(token)
            i += 1
    return script_opts, ["estimate_rho_elkan_noto.py", *config_args]


def excluded_set_name(conf):
    """Reproduce new_train.py's directory name for the excluded set."""
    parts = []
    if conf.excluded_groups:
        parts.append("groups_" + "-".join(conf.excluded_groups))
    if conf.excluded_subgroups:
        parts.append("subgroups_" + "-".join(conf.excluded_subgroups))
    return "_".join(parts) if parts else "random"


def default_weights_path(conf):
    """Where --save_model writes the checkpoint: models/<label>/<set>/seed<seed>.pt."""
    return os.path.join(
        PROJECT_ROOT, "models", conf.label.strip(), excluded_set_name(conf),
        f"seed{conf.seed}.pt",
    )


def build_forward_args(conf, prot, lipid):
    """Assemble the model kwargs exactly as the training/eval loop does."""
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
    return forward_args


@torch.no_grad()
def collect_scores(model, conf, loader, device):
    """Return (g, labels): g[i] = P(labeled=1 | x_i) and its 0/1 interaction label.

    We use the RAW softmax of the model logits (no logit-adjustment bias): that
    bias is a decision-time shift, whereas Elkan-Noto needs the model's estimate
    of P(labeled | x).
    """
    softmax = torch.nn.Softmax(dim=-1)
    all_scores = []
    all_labels = []
    model.eval()
    for prot, lipid in loader:
        prot = prot.to(device)
        lipid = lipid.to(device)
        labels = prot.inter.to(device).long()
        outl = model(**build_forward_args(conf, prot, lipid))
        scores = softmax(outl)[:, 1]  # P(labeled = 1 | x)
        all_scores.append(scores.detach().cpu())
        all_labels.append(labels.detach().cpu())
    if not all_scores:
        return torch.empty(0), torch.empty(0)
    return torch.cat(all_scores), torch.cat(all_labels)


def estimate_rho_from_scores(scores, labels, train_positive_count, train_unlabeled_count):
    """Core Elkan-Noto math. Pure function so it can be unit-tested in isolation.

    Args:
        scores: g(x) = P(labeled | x) on a HELD-OUT pool.
        labels: matching 0/1 interaction labels (1 = known positive).
        train_positive_count (P), train_unlabeled_count (U): TRAIN-pool sizes,
            used to convert the hidden-positive rate f into the project's rho.

    Returns dict with c_hat, f_hat (== pu_unlabeled_positive_fraction) and rho.
    """
    positive_scores = scores[labels == 1]
    unlabeled_scores = scores[labels == 0]
    if positive_scores.numel() == 0:
        raise ValueError("No held-out positives in the pool; cannot estimate c.")
    if unlabeled_scores.numel() == 0:
        raise ValueError("No held-out unlabeled in the pool; cannot estimate f.")

    # c = P(labeled | positive): mean model score over known positives.
    c_hat = float(positive_scores.mean())
    if c_hat <= 1e-6:
        raise ValueError(
            f"c_hat={c_hat:.6g} is ~0: the model scores its own positives near 0, "
            "so it is too poorly calibrated for Elkan-Noto here."
        )

    # f = hidden-positive rate among unlabeled = mean( P(y=1|x) ) = mean(g/c),
    # clamped to a valid probability.
    f_hat = float((unlabeled_scores / c_hat).clamp(0.0, 1.0).mean())

    P = float(train_positive_count)
    U = float(train_unlabeled_count)
    rho = (P + f_hat * U) / (P + U)
    return {
        "c_hat": c_hat,
        "f_hat": f_hat,  # feed straight into --pu_unlabeled_positive_fraction
        "rho": rho,
        "n_positives": int(positive_scores.numel()),
        "n_unlabeled": int(unlabeled_scores.numel()),
    }


def load_full_csv(conf):
    """Load the interaction dataset used by this config."""
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    return read_csv(interaction_csv_path(data_dir))


def config_group_key(conf):
    """Out-of-fold group a checkpoint estimates for (test group in cold-split)."""
    if getattr(conf, "test_group", ""):
        return str(conf.test_group).lower()
    return "-".join(conf.excluded_groups).lower() if conf.excluded_groups else "random"


def estimate_for_config(conf, weights_path, pool_name, device):
    """Run Elkan-Noto for one checkpoint; returns the estimate dict + group/seed.

    Rebuilds the exact (seed, split) dataset the checkpoint was trained under,
    loads the weights, scores the chosen held-out pool, and applies the core
    Elkan-Noto estimator. Slow (one full dataset build per call), but correct.
    """
    seed_everything(conf.seed)
    csv = load_full_csv(conf)
    train_dataset, valid_dataset, test_dataset = PLIDataset(
        root_dir=os.path.join(PROJECT_ROOT, "data") + os.sep, csv=csv, seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )
    train_interaction = train_dataset.csv["Interaction"]
    train_positive_count = int((train_interaction == 1).sum())
    train_unlabeled_count = int((train_interaction == 0).sum())

    model = InteractionClassification(conf).to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))

    pools = {"valid": [valid_dataset], "test": [test_dataset],
             "both": [valid_dataset, test_dataset]}[pool_name]
    scores_parts, labels_parts = [], []
    for dataset in pools:
        loader = torch_geometric.loader.DataLoader(
            dataset, batch_size=conf.batch, shuffle=False, num_workers=0,
        )
        s, l = collect_scores(model, conf, loader, device)
        scores_parts.append(s)
        labels_parts.append(l)
    scores = torch.cat(scores_parts)
    labels = torch.cat(labels_parts)

    result = estimate_rho_from_scores(
        scores, labels, train_positive_count, train_unlabeled_count
    )
    result["group"] = config_group_key(conf)
    result["seed"] = conf.seed
    return result


def dataset_group_counts(csv):
    """Per-group (n_positives, n_unlabeled) from the full dataset, for weighting."""
    domain = csv["ProteinDomain"].astype(str).str.lower()
    counts = {}
    for group in sorted(domain.dropna().unique()):
        mask = domain == group
        counts[group] = (
            int(((csv["Interaction"] == 1) & mask).sum()),
            int(((csv["Interaction"] == 0) & mask).sum()),
        )
    return counts


def aggregate_label_rho(records, group_counts, balance_by_family):
    """Aggregate per-checkpoint estimates into per-group and overall rho + SE.

    Pure function (no torch/IO) so it can be unit-tested. ``records`` is a list of
    dicts with 'group','seed','f_hat'. Groups are weighted by their contribution
    to the training NEGATIVE pool: positive count under balance_negatives_by_family
    (each family draws negatives == its positives), else the unlabeled-pool size.
    rho = (P + f*U)/(P+U); SE is propagated from the between-seed spread only.
    """
    by_group = defaultdict(list)
    for record in records:
        by_group[record["group"]].append(record["f_hat"])

    per_group = {}
    for group, values in by_group.items():
        mean_f = statistics.mean(values)
        sd = statistics.stdev(values) if len(values) > 1 else 0.0
        per_group[group] = {
            "f_mean": mean_f,
            "f_sd": sd,
            "f_se": sd / math.sqrt(len(values)),
            "n_seeds": len(values),
        }

    groups = list(per_group)
    weight = {
        g: group_counts.get(g, (0, 0))[0 if balance_by_family else 1] for g in groups
    }
    total_weight = sum(weight.values()) or 1.0
    f_bal = sum(weight[g] * per_group[g]["f_mean"] for g in groups) / total_weight
    # Independent-group error propagation of the weighted mean.
    f_se = math.sqrt(
        sum((weight[g] / total_weight) ** 2 * per_group[g]["f_se"] ** 2 for g in groups)
    )

    total_pos = sum(c[0] for c in group_counts.values())
    if balance_by_family:
        pool_unlabeled = float(total_pos)  # negatives == positives per family
    else:
        pool_unlabeled = 0.056 * sum(c[1] for c in group_counts.values())
    rho = (total_pos + f_bal * pool_unlabeled) / (total_pos + pool_unlabeled)
    rho_se = (pool_unlabeled / (total_pos + pool_unlabeled)) * f_se

    return {
        "per_group": per_group,
        "weight": weight,
        "weight_by": "n_pos (balance_by_family)" if balance_by_family else "n_unlabeled",
        "f_bal": f_bal,
        "f_se": f_se,
        "P": total_pos,
        "U": pool_unlabeled,
        "rho": rho,
        "rho_se": rho_se,
    }


def run_label_mode(label, models_root, pool_name, device):
    """Run every models/<label>/*/seed*.pt checkpoint and report rho + SE."""
    checkpoints = sorted(glob.glob(os.path.join(models_root, label, "*", "seed*.pt")))
    if not checkpoints:
        raise SystemExit(
            f"No checkpoints under {os.path.join(models_root, label)!r} "
            "(train the label with --save_model)."
        )
    print(f"label: {label}  |  checkpoints: {len(checkpoints)}  |  pool: {pool_name}")
    print("--- per checkpoint ---")

    records = []
    balance_by_family = None
    counts_csv = None
    for weights_path in checkpoints:
        args_path = weights_path[: -len(".pt")] + ".args.json"
        rel = os.path.relpath(weights_path, models_root)
        if not os.path.exists(args_path):
            print(f"  skip (no args.json): {rel}")
            continue
        with open(args_path) as handle:
            argv = json.load(handle)
        conf = read_configuration(["estimate_rho_elkan_noto.py", *argv])
        if conf.final_m is None:
            conf.final_m = conf.m
        try:
            result = estimate_for_config(conf, weights_path, pool_name, device)
        except (ValueError, KeyError) as exc:
            print(f"  {config_group_key(conf):18s} seed{conf.seed}  SKIP: {exc}")
            continue
        if balance_by_family is None:
            balance_by_family = bool(getattr(conf, "balance_negatives_by_family", False))
        if counts_csv is None:
            counts_csv = load_full_csv(conf)
        print(
            f"  {result['group']:18s} seed{result['seed']}  "
            f"c_hat={result['c_hat']:.3f}  f_hat={result['f_hat']:.3f}  "
            f"n_pos={result['n_positives']:4d} n_unl={result['n_unlabeled']:4d}"
        )
        records.append(result)

    if not records:
        raise SystemExit("No usable checkpoints produced an estimate.")

    group_counts = dataset_group_counts(counts_csv)
    agg = aggregate_label_rho(records, group_counts, balance_by_family)

    print("\n--- per group (f_hat mean +/- SE over seeds) ---")
    for group in sorted(per_group_order(agg, group_counts)):
        stats = agg["per_group"][group]
        npos, _ = group_counts.get(group, (0, 0))
        print(
            f"  {group:18s} f={stats['f_mean']:.3f} +/- {stats['f_se']:.3f}  "
            f"(sd={stats['f_sd']:.3f}, seeds={stats['n_seeds']}, weight={agg['weight'][group]})"
        )

    print("\n--- overall ---")
    print(f"  weighting            : {agg['weight_by']}")
    print(f"  dataset P / U        : {agg['P']} / {agg['U']:.0f}")
    print(f"  f (hidden-pos rate)  : {agg['f_bal']:.4f} +/- {agg['f_se']:.4f}")
    print(f"  rho                  : {agg['rho']:.4f} +/- {agg['rho_se']:.4f}  (statistical SE only)")
    print("  note: SE reflects seed/group sampling only. Systematic bias (model")
    print("        calibration, SCAR non-representative positives) is NOT captured")
    print("        and can exceed it -- treat rho as the center of a small grid.")


def per_group_order(agg, group_counts):
    """Groups sorted by descending weight (most-informative first)."""
    return sorted(agg["per_group"], key=lambda g: -group_counts.get(g, (0, 0))[0])


def main():
    script_opts, config_argv = split_script_args(sys.argv[1:])
    device = torch.device(
        script_opts["device"] or ("cuda" if torch.cuda.is_available() else "cpu")
    )

    if script_opts["label"]:
        models_root = script_opts["models_root"] or os.path.join(PROJECT_ROOT, "models")
        run_label_mode(script_opts["label"], models_root, script_opts["pool"], device)
        return

    # Single-checkpoint mode.
    conf = read_configuration(config_argv)
    if conf.final_m is None:
        conf.final_m = conf.m
    weights_path = script_opts["weights"] or default_weights_path(conf)
    if not os.path.exists(weights_path):
        raise SystemExit(
            f"Weights not found at {weights_path!r}. Train with --save_model, "
            "pass --weights PATH, or use --label to sweep a whole label."
        )
    result = estimate_for_config(conf, weights_path, script_opts["pool"], device)
    print(f"Loaded weights: {weights_path}")
    print(f"pool                         : {script_opts['pool']}")
    print(f"held-out positives / unlab   : {result['n_positives']} / {result['n_unlabeled']}")
    print(f"c_hat  P(labeled | positive) : {result['c_hat']:.4f}")
    print(f"f_hat  hidden-positive rate  : {result['f_hat']:.4f}   "
          f"(use as --pu_unlabeled_positive_fraction)")
    print(f"rho    estimated PU prior    : {result['rho']:.4f}")


if __name__ == "__main__":
    main()
