#!/usr/bin/env python3
"""Inference-time input ablation: take weights a run already saved, remove one of the
model's inputs, and re-score the held-out block. Four modes, one per kind of input the
project has had to ask this about.

Shared shape, and why these are one script. Every mode does the same four things --
resolve (label, group, seed) to models/<label>/groups_<g>/seed<N>.pt (the weights
run_test measures), rebuild the configuration from the seed<N>.args.json stored beside
it, rebuild the split from that (the loader is deterministic in the seed, so the rows
come back identical), and re-score with something replaced. They used to be four
scripts (analysis/mlp_feature_ablation.py, analysis/probes/mlp_feature_subsets.py,
analysis/probes/ge_feature_ablation.py, analysis/probes/compat_input_ablation.py) with
four copies of that reconstruction, two of which already imported the third's
ColumnOverride/confusion_metrics. `load_checkpoint` below is now the one reconstruction
all of them use; what differs per mode is only WHICH input is replaced and HOW MANY
combinations are swept.

What every mode answers, and what none of them answer: how much a TRAINED model relies
on an input. Not what a model trained without it would score -- other inputs can
compensate there, and the pocket descriptors are constants of the protein and
correlated, so zeroing one gives an input combination never seen in training. For
redundant inputs this underestimates importance.

MODE `descriptors` -- one column (or a named group of columns) of the --descriptor_mlp
input vector at a time:

    zero     the column is set to 0. Inputs are standardised on train, so 0 is the
             train mean.
    permute  the column's values are shuffled across the block's rows (fixed RNG):
             keeps the feature's marginal distribution, breaks its link to the row.

`baseline` rows are the unmodified checkpoint; `--check_table` compares their BA/F1
with the latest metrics_summary.csv row of the same (label, group, seed).

MODE `subsets` -- EVERY subset of the same --descriptor_mlp vector. With n descriptor
names there are 2^n - 1 non-empty subsets (n=17: 131071), scored on the held-out test
AND validation blocks.

    Why it is fast. In a --descriptor_mlp run the whole model is
    `binar(descriptor_mlp_head(x))` with x the n standardised columns of one row, so
    nothing upstream (graphs, ESM3, MolFormer) depends on the ablated columns. The
    loader and the checkpoint are touched ONCE per checkpoint: the standardised input
    matrix of the block is recorded with a forward hook, and every subset is then one
    batched forward of the small MLP over (subsets x rows) -- masks are applied by
    multiplying the recorded matrix, metrics come from matrix products. The row-by-row
    reference path (`descriptors` mode's own ColumnOverride) re-scores a few random
    subsets per checkpoint and must agree (`--verify`).

    A mask is an integer, bit i set = feature i (in head.token_names order) ZEROED;
    mask 0 is the untouched checkpoint, mask 2^n - 1 zeroes everything.

    Outputs (in --out_dir): arrays.npz (per-checkpoint metrics for every mask),
    subsets.csv (mean delta vs the untouched checkpoint, per mask), shapley.csv,
    by_size.csv, and the printed summary.

    Selection warning. Picking the subset with the best mean TEST BA out of 131071 is
    picking a maximum of that many noisy means. The "selected on validation" lines
    choose on the validation block and report the TEST block of that choice: that is
    the number to quote. AUC is not computed here (rank statistic per subset; not
    needed for the 0.5 reading).

MODE `ge` -- the inputs of a geometric_edge (`ge_*`) checkpoint. Per protein node these
models read residue features (`node_x`), the ESM3 embedding (`esm3`), a burial value
(`bury`) and the named pocket descriptors broadcast from `descriptor_catalog_input`
(`--protein_descriptors`); the lipid side reads the MolFormer token embedding
(`molformer`).

    zero   the input is set to 0. For the named descriptors that is the train mean
           (they are standardised on train); for ESM3, MolFormer, `bury` and `node_x`
           it is a literal zero -- ESM3 zeroed means the protein-language-model channel
           is switched off.
    mean   the input is replaced by its mean over the TRAIN proteins' nodes (lipids'
           tokens for `molformer`). Same as `zero` for the descriptors; a less
           off-manifold reading for the four unstandardised inputs.

    Evaluated per checkpoint: the untouched model; every single feature; every pair
    (zero); a few named groups; and a sampled Shapley value of every feature for v(S) =
    metric with exactly S KEPT, estimated from random permutations (the full subset
    sweep `subsets` does for the descriptor MLP is not available here -- one scoring
    pass is a protein-graph forward, ~0.4 s for a 144-row block).

    Speed. In a ge model the protein tower is the whole cost (~90% of a pass) and it is
    a function of ONE protein's inputs only, while the lipid tower, cross-attention and
    head together are cheap. So per ablation the protein tower runs once per UNIQUE
    protein of the block (25 instead of 144 graphs), its node embeddings are cached per
    (protein-side mask), and the per-row passes reuse them through a patched
    `protein1.forward`. `--verify` re-scores random masks through the plain, unpatched
    model and requires the same probabilities. `--workers` runs one process per seed
    (this script re-invokes itself with its own `ge` mode per seed).

MODE `compat` -- the single --compatibility_input scalar, with and without.

    The question. `analysis/probes/compatibility_probe.py` finds that a
    `--compatibility_input` run ranks the held-out block far above the base run (0.751
    vs 0.546 inside protein) while its score correlates with the compatibility feature
    at r = 0.015 -- it does not look like the network is reading the feature out. But a
    near-zero linear correlation does not rule out nonlinear use, and the two readings
    imply opposite conclusions:

      the feature carries the gain    -> the result is the feature, and the same number
                                         is obtainable without a network
      the feature only shaped training -> the gain is in the weights, and the feature is
                                         scaffolding inference no longer needs

    Only an ablation separates them, and it is cheap because it trains nothing: the
    standardised feature has train mean 0 by construction
    (`_compute_compatibility_input` in dataloader/Dataloader.py), so substituting zero
    feeds the classifier exactly the value an average training row carried -- the
    neutral input, not an out-of-range one. Both AUCs are reported on the same rows,
    pooled and inside protein, so the difference is the feature's contribution at
    inference and nothing else.

Reads only. Trains nothing, appends to no shared table.

    python3 analysis/input_ablation.py descriptors --label mlp_sub_pb6 --out /tmp/ablation.csv
    python3 analysis/input_ablation.py subsets --label mlp_sub_pb6 --out_dir /tmp/subsets
    python3 analysis/input_ablation.py ge --label ge_s15_prothid32_hid64_noreg \
        --out_dir /tmp/ge_ablation --workers 5
    python3 analysis/input_ablation.py compat --label <label> --split test
"""
import argparse
import glob
import itertools
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

import torch_geometric  # noqa: E402,F401

from training.results_layout import label_family  # noqa: E402

from checkpoint_scores import (  # noqa: E402
    DEFAULT_FAMILIES,
    InteractionClassification,
    PLIDataset,
    _average_candidate_rows,
    arg_lines,
    interaction_csv_path,
    read_configuration,
    score_split as checkpoint_score_split,
    seed_everything,
)
from forward_args import build_forward_args  # noqa: E402

from architecture.descriptor_mlp_head import DescriptorMLPHead  # noqa: E402
from dataloader.pair_descriptors import LIPID_DESCRIPTOR_NAMES, full_catalog_order  # noqa: E402

from analysis.baselines.null_model import WORKING, auc, per_protein_auc  # noqa: E402

torch.set_flush_denormal(True)


# ==============================================================================
# mode `descriptors` -- was analysis/mlp_feature_ablation.py
# ==============================================================================



def confusion_metrics(probs, labels):
    """BA/F1/sensitivity/specificity at 0.5 (argmax of the two logits), plus AUC."""
    predicted = probs > 0.5
    positive = labels == 1
    tp = float((predicted & positive).sum())
    fn = float((~predicted & positive).sum())
    fp = float((predicted & ~positive).sum())
    tn = float((~predicted & ~positive).sum())
    sensitivity = tp / (tp + fn) if tp + fn else float("nan")
    specificity = tn / (tn + fp) if tn + fp else float("nan")
    precision = tp / (tp + fp) if tp + fp else float("nan")
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else float("nan")
    auc = float("nan")
    if positive.any() and (~positive).any():
        order = np.argsort(probs, kind="mergesort")
        ranks = np.empty(len(probs))
        ranks[order] = np.arange(1, len(probs) + 1)
        # average ranks over ties
        sorted_probs = probs[order]
        start = 0
        for end in range(1, len(probs) + 1):
            if end == len(probs) or sorted_probs[end] != sorted_probs[start]:
                ranks[order[start:end]] = (start + 1 + end) / 2.0
                start = end
        n_pos = positive.sum()
        auc = (ranks[positive].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * (~positive).sum())
    return {
        "BA": (sensitivity + specificity) / 2, "F1": f1, "sens": sensitivity,
        "spec": specificity, "precision": precision, "AUC": auc,
    }


class ColumnOverride:
    """Forward-pre-hook on DescriptorMLPHead replacing chosen columns of its input.

    The head reads `descriptor_catalog_input.view(batch, -1)[:, catalog_columns]`, so the
    columns replaced here are positions in that catalog vector. `mode` None passes through.
    Rows arrive in dataset order (shuffle=False), so a running offset indexes the
    pre-permuted full-block column.
    """

    def __init__(self):
        self.mode = None
        self.columns = []
        self.permuted = None  # {column: tensor over all rows}
        self.offset = 0
        self.record = None  # list of batches, filled during the baseline pass

    def __call__(self, module, args):
        tensor = args[0]
        if self.record is not None:
            self.record.append(tensor.detach().clone())
        if self.mode is None:
            self.offset += tensor.shape[0]
            return None
        changed = tensor.clone()
        batch = tensor.shape[0]
        for column in self.columns:
            if self.mode == "zero":
                changed[:, column] = 0.0
            else:
                changed[:, column] = self.permuted[column][self.offset:self.offset + batch]
        self.offset += batch
        return (changed,)


def run_group(label, group, seed, args, rng):
    modes = args.modes.split(",")
    models_dir = os.path.join(PROJECT_ROOT, "models", label_family(label), label, f"groups_{group}")
    argv = json.load(open(os.path.join(models_dir, f"seed{seed}.args.json")))
    conf = read_configuration(["input_ablation"] + argv)
    if not conf.descriptor_mlp:
        raise SystemExit(f"{label} is not a --descriptor_mlp label")
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    _, _, test_dataset = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed, excluded_subgroups=conf.excluded_subgroups,
        config=conf, excluded_groups=conf.excluded_groups,
    )
    del csv
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(
        os.path.join(models_dir, f"seed{seed}.pt"), map_location="cpu", weights_only=True
    ))
    heads = [m for m in model.modules() if isinstance(m, DescriptorMLPHead)]
    if len(heads) != 1:
        raise SystemExit(f"expected one DescriptorMLPHead, found {len(heads)}")
    head = heads[0]
    names = list(head.token_names)
    columns = head.catalog_columns.tolist()
    override = ColumnOverride()
    head.register_forward_pre_hook(override)

    def score():
        override.offset = 0
        probs, labels = checkpoint_score_split(model, conf, test_dataset, torch.device("cpu"))
        frame = test_dataset.csv
        if "_candidate_index" in frame.columns:
            frame, probs, labels = _average_candidate_rows(frame, probs, labels)
        return probs, labels

    # Baseline pass; also records the standardised input of every row, so a permutation
    # can be built over the whole block rather than inside one batch.
    override.record = []
    probs, labels = score()
    recorded = torch.cat(override.record)
    override.record = None
    rows = [dict(feature="baseline", mode="none", **confusion_metrics(probs, labels))]

    lipid_names = set(LIPID_DESCRIPTOR_NAMES)
    groups = {
        "GROUP:lipid": [n for n in names if n in lipid_names],
        "GROUP:pocket": [n for n in names if n not in lipid_names],
        "GROUP:all": list(names),
    }
    targets = {}
    if not args.only_pairs:
        targets.update({name: [name] for name in names})
        targets.update(groups)
    if args.pairs or args.only_pairs:
        for i, first in enumerate(names):
            for second in names[i + 1:]:
                targets[f"{first}+{second}"] = [first, second]
    for target, members in targets.items():
        cols = [columns[names.index(n)] for n in members]
        for mode in modes:
            override.mode = mode
            override.columns = cols
            if mode == "permute":
                order = torch.as_tensor(rng.permutation(recorded.shape[0]))
                override.permuted = {c: recorded[order, c] for c in cols}
            probs, labels = score()
            rows.append(dict(feature=target, mode=mode, **confusion_metrics(probs, labels)))
    override.mode = None
    for row in rows:
        row.update(label=label, group=group, seed=seed)
    return rows


def check_against_table(frame, label):
    table = pd.read_csv(os.path.join(PROJECT_ROOT, "results", "tables", "metrics_summary.csv"), low_memory=False)
    table = table[table["label"] == label].sort_values("datetime")
    latest = table.groupby(["exclusion_set", "seed"]).tail(1)
    base = frame[frame["feature"] == "baseline"].copy()
    base["exclusion_set"] = "groups_" + base["group"]
    merged = base.merge(latest, on=["exclusion_set", "seed"], suffixes=("", "_table"))
    gap = (merged["BA"] - merged["balanced_accuracy"].astype(float)).abs()
    print(f"\ncheck vs metrics_summary.csv: {len(merged)} (group, seed) matched; "
          f"max |BA diff| = {gap.max():.4f}, mean = {gap.mean():.4f}, "
          f"{int((gap > 0.005).sum())} differ by > 0.005")


def run_descriptors(args):

    root = os.path.join(PROJECT_ROOT, "models", label_family(args.label), args.label)
    groups = (
        args.groups.split(",") if args.groups
        else sorted(os.path.basename(p)[len("groups_"):] for p in glob.glob(os.path.join(root, "groups_*")))
    )
    seeds = [int(s) for s in args.seeds.split(",")]
    all_rows = []
    for group in groups:
        for seed in seeds:
            path = os.path.join(root, f"groups_{group}", f"seed{seed}.pt")
            if not os.path.exists(path):
                print(f"missing : {path}", flush=True)
                continue
            rng = np.random.default_rng(1000 + seed)
            all_rows.extend(run_group(args.label, group, seed, args, rng))
            print(f"{group} seed{seed} : done", flush=True)
    if not all_rows:
        raise SystemExit("no checkpoints scored")
    frame = pd.DataFrame(all_rows)
    frame.to_csv(args.out, index=False)
    print(f"wrote {args.out} ({len(frame)} rows)")
    if args.check_table:
        check_against_table(frame, args.label)


# ==============================================================================
# mode `subsets` -- was analysis/probes/mlp_feature_subsets.py
# ==============================================================================



ROWS_PER_CHUNK = 400_000


def find_head(model):
    heads = [m for m in model.modules() if isinstance(m, DescriptorMLPHead)]
    owners = [m for m in model.modules()
              if hasattr(m, "descriptor_mlp_head") and hasattr(m, "binar")]
    if len(heads) != 1 or len(owners) != 1:
        raise SystemExit(f"expected one descriptor head and one owner, got {len(heads)}/{len(owners)}")
    return heads[0], owners[0]


def record_block(model, conf, head, dataset):
    """(X [rows, n] standardised head input, pair_index [rows], labels [pairs], probs [pairs]).

    pair_index groups candidate-expanded rows into pairs exactly as the training-time
    evaluation does (mean probability over a pair's candidates).
    """
    override = ColumnOverride()
    override.record = []
    handle = head.register_forward_pre_hook(override)
    try:
        probs, labels = checkpoint_score_split(model, conf, dataset, torch.device("cpu"))
    finally:
        handle.remove()
    recorded = torch.cat(override.record)
    x = recorded.index_select(1, head.catalog_columns).float()
    frame = dataset.csv
    if "_candidate_index" in frame.columns:
        pair_index, _ = pd.factorize(frame["pair_id"].to_numpy())
        first = np.zeros(pair_index.max() + 1, dtype=int)
        first[pair_index[::-1]] = np.arange(len(pair_index))[::-1]
        pair_labels = labels[first]
        _, pair_probs, _ = _average_candidate_rows(frame, probs, labels)
    else:
        pair_index = np.arange(len(labels))
        pair_labels = labels
        pair_probs = probs
    return x, torch.as_tensor(pair_index, dtype=torch.long), pair_labels, pair_probs


def score_all_masks(owner, head, x, pair_index, pair_labels, n_features):
    """BA, F1, sensitivity, specificity at 0.5 for every mask 0 .. 2^n - 1, each [2^n]."""
    rows = x.shape[0]
    pairs = int(pair_index.max()) + 1
    counts = torch.zeros(pairs).index_add_(0, pair_index, torch.ones(rows))
    y = torch.as_tensor(pair_labels == 1, dtype=torch.float32)
    positives = y.sum()
    negatives = pairs - positives
    total = 1 << n_features
    bit = torch.arange(n_features)
    out = {name: np.empty(total, dtype=np.float32) for name in ("BA", "F1", "sens", "spec")}
    chunk = max(1, ROWS_PER_CHUNK // rows)
    for start in range(0, total, chunk):
        masks = torch.arange(start, min(start + chunk, total))
        keep = 1.0 - ((masks[:, None] >> bit) & 1).float()          # [C, n]
        masked = (x[None, :, :] * keep[:, None, :]).reshape(-1, n_features)
        logits = owner.binar(head.mlp(masked))
        prob1 = torch.softmax(logits.float(), dim=1)[:, 1].reshape(len(masks), rows)
        if pairs != rows:
            pooled = torch.zeros(len(masks), pairs).index_add_(1, pair_index, prob1) / counts
        else:
            pooled = prob1
        predicted = (pooled > 0.5).float()
        tp = predicted @ y
        fp = predicted.sum(1) - tp
        fn = positives - tp
        tn = negatives - fp
        sens = tp / positives.clamp(min=1)
        spec = tn / negatives.clamp(min=1)
        f1 = 2 * tp / (2 * tp + fp + fn).clamp(min=1)
        sl = slice(start, start + len(masks))
        out["BA"][sl] = ((sens + spec) / 2).numpy()
        out["F1"][sl] = f1.numpy()
        out["sens"][sl] = sens.numpy()
        out["spec"][sl] = spec.numpy()
    return out


def verify(model, conf, head, dataset, names, columns, fast, rng, count):
    """Row-by-row hook path on `count` random masks; max |BA diff| against the batched path."""
    override = ColumnOverride()
    handle = head.register_forward_pre_hook(override)
    worst = 0.0
    try:
        total = 1 << len(names)
        for mask in [0, total - 1] + [int(m) for m in rng.integers(1, total - 1, size=count)]:
            zeroed = [columns[i] for i in range(len(names)) if (mask >> i) & 1]
            override.mode = "zero" if zeroed else None
            override.columns = zeroed
            override.offset = 0
            probs, labels = checkpoint_score_split(model, conf, dataset, torch.device("cpu"))
            frame = dataset.csv
            if "_candidate_index" in frame.columns:
                frame, probs, labels = _average_candidate_rows(frame, probs, labels)
            worst = max(worst, abs(confusion_metrics(probs, labels)["BA"] - float(fast["BA"][mask])))
    finally:
        handle.remove()
    return worst


def shapley(values, n):
    """Exact Shapley value of each feature for v(S) = metric with exactly S KEPT.

    `values` is indexed by the ZEROED mask, so the kept-set array is its reverse
    (kept = ~zeroed = full - zeroed). The values sum to v(all kept) - v(none kept).
    """
    kept_value = values[::-1].astype(np.float64)
    size = 1 << n
    sets = np.arange(size)
    popcount = np.zeros(size, dtype=np.int64)
    for i in range(n):
        popcount += (sets >> i) & 1
    from math import factorial
    weight = np.array([factorial(k) * factorial(n - k - 1) / factorial(n) for k in range(n)])
    result = np.zeros(n)
    for i in range(n):
        without = sets[((sets >> i) & 1) == 0]
        result[i] = (weight[popcount[without]] * (kept_value[without | (1 << i)] - kept_value[without])).sum()
    return result, popcount


def summarise_subsets(arrays, names, out_dir):
    n = len(names)
    size = 1 << n
    ba_t, f1_t, ba_v, f1_v = (arrays[k].mean(axis=0) for k in ("test_BA", "test_F1", "valid_BA", "valid_F1"))
    d_ba_t, d_f1_t, d_ba_v = ba_t - ba_t[0], f1_t - f1_t[0], ba_v - ba_v[0]
    checkpoints = arrays["test_BA"].shape[0]
    print(f"\n{checkpoints} checkpoints x {size - 1} subsets. Untouched: test BA {ba_t[0]:.3f} "
          f"F1 {f1_t[0]:.3f} | valid BA {ba_v[0]:.3f}; everything zeroed: test BA {ba_t[-1]:.3f}")

    shap_ba, popcount = shapley(ba_t, n)
    shap_f1, _ = shapley(f1_t, n)
    shap_bav, _ = shapley(ba_v, n)
    table = pd.DataFrame({"feature": names, "shapley_BA_test": shap_ba, "shapley_F1_test": shap_f1,
                          "shapley_BA_valid": shap_bav}).sort_values("shapley_BA_test", ascending=False)
    table.insert(0, "rank", range(1, n + 1))
    table.to_csv(os.path.join(out_dir, "shapley.csv"), index=False)
    print(f"\nShapley value of each feature (share of test BA it adds, averaged over every "
          f"kept-set order; sums to {ba_t[0] - ba_t[-1]:.3f} = untouched - all zeroed):")
    print(table.round(4).to_string(index=False))

    zeroed_count = popcount  # popcount of the zeroed mask
    by_size = []
    for k in range(1, n + 1):
        sel = np.where(zeroed_count == k)[0]
        d = d_ba_t[sel]
        by_size.append(dict(zeroed=k, kept=n - k, subsets=len(sel), mean_dBA=d.mean(), best_dBA=d.max(),
                            worst_dBA=d.min(), share_within_0p005=(d >= -0.005).mean()))
    by_size = pd.DataFrame(by_size)
    by_size.to_csv(os.path.join(out_dir, "by_size.csv"), index=False)
    print("\nBy number of features zeroed (test dBA vs untouched):")
    print(by_size.round(4).to_string(index=False))

    def names_of(mask):
        return ",".join(names[i] for i in range(n) if (mask >> i) & 1)

    frame = pd.DataFrame({"mask": np.arange(size), "k": zeroed_count, "dBA_test": d_ba_t,
                          "dF1_test": d_f1_t, "dBA_valid": d_ba_v})
    frame["zeroed"] = [names_of(m) for m in range(size)]
    # Most damaging subset first: descending significance of what is removed.
    frame = frame[frame["mask"] != 0].sort_values("dBA_test").reset_index(drop=True)
    frame.to_csv(os.path.join(out_dir, "subsets.csv"), index=False)
    print("\nMost damaging subsets when zeroed, by size 1-3 (test dBA, descending significance):")
    for k in (1, 2, 3):
        top = frame[frame["k"] == k].head(5)
        for _, row in top.iterrows():
            print(f"  k={k} dBA {row.dBA_test:+.3f} dF1 {row.dF1_test:+.3f}  {row.zeroed}")

    print("\nSelected on VALIDATION, reported on TEST (the number to quote):")
    for tolerance in (0.0, 0.005, 0.01):
        ok = np.where(d_ba_v >= -tolerance)[0]
        top_k = zeroed_count[ok].max()
        pool = ok[zeroed_count[ok] == top_k]
        pick = pool[np.argmax(ba_v[pool])]
        print(f"  valid dBA >= -{tolerance}: most features zeroed = {top_k}/{n}; pick valid dBA "
              f"{d_ba_v[pick]:+.3f} -> test dBA {d_ba_t[pick]:+.3f}, dF1 {d_f1_t[pick]:+.3f}\n"
              f"    zeroed: {names_of(pick)}")
    best_valid = int(np.argmax(ba_v))
    print(f"  best valid BA overall: valid dBA {d_ba_v[best_valid]:+.3f} -> test dBA "
          f"{d_ba_t[best_valid]:+.3f} (zeroed {zeroed_count[best_valid]}: {names_of(best_valid)})")
    best_test = int(np.argmax(ba_t))
    print(f"  (for scale, best TEST BA overall: dBA {d_ba_t[best_test]:+.3f} with "
          f"{zeroed_count[best_test]} zeroed -- a maximum of {size} noisy means, optimistic)")
    print(f"\nwrote {out_dir}/shapley.csv, by_size.csv, subsets.csv, arrays.npz")


def run_subsets(args):
    os.makedirs(args.out_dir, exist_ok=True)
    npz_path = os.path.join(args.out_dir, "arrays.npz")

    if args.summarize_only:
        stored = np.load(npz_path, allow_pickle=True)
        summarise_subsets({k: stored[k] for k in ("test_BA", "test_F1", "valid_BA", "valid_F1")},
                  list(stored["names"]), args.out_dir)
        return

    root = os.path.join(PROJECT_ROOT, "models", label_family(args.label), args.label)
    groups = (args.groups.split(",") if args.groups else sorted(
        os.path.basename(p)[len("groups_"):] for p in glob.glob(os.path.join(root, "groups_*"))))
    seeds = [int(s) for s in args.seeds.split(",")]
    collected = {k: [] for k in ("test_BA", "test_F1", "test_sens", "test_spec", "valid_BA", "valid_F1")}
    labels_done, names, worst_gap = [], None, 0.0
    started = time.perf_counter()
    for group in groups:
        for seed in seeds:
            if not os.path.exists(os.path.join(root, f"groups_{group}", f"seed{seed}.pt")):
                print(f"missing : {group} seed{seed}", flush=True)
                continue
            t0 = time.perf_counter()
            conf, model, (_, valid_dataset, test_dataset) = load_checkpoint(
                args.label, group, seed, require_descriptor_mlp=True)
            head, owner = find_head(model)
            these_names = list(head.token_names)
            if names is None:
                names = these_names
            elif names != these_names:
                raise SystemExit("descriptor order differs between checkpoints")
            n = len(names)
            t1 = time.perf_counter()
            result = {}
            for split, dataset in (("test", test_dataset), ("valid", valid_dataset)):
                x, pair_index, pair_labels, base_probs = record_block(model, conf, head, dataset)
                fast = score_all_masks(owner, head, x, pair_index, pair_labels, n)
                # The untouched mask must reproduce the loader-path probabilities.
                base = confusion_metrics(base_probs, pair_labels)["BA"]
                worst_gap = max(worst_gap, abs(base - float(fast["BA"][0])))
                result[split] = (fast, dataset, x)
            if args.verify:
                rng = np.random.default_rng(seed)
                columns = head.catalog_columns.tolist()
                worst_gap = max(worst_gap, verify(model, conf, head, result["test"][1], names, columns,
                                                  result["test"][0], rng, args.verify))
            for key in ("BA", "F1", "sens", "spec"):
                collected[f"test_{key}"].append(result["test"][0][key])
            for key in ("BA", "F1"):
                collected[f"valid_{key}"].append(result["valid"][0][key])
            labels_done.append(f"{group}/seed{seed}")
            print(f"{group} seed{seed}: load {t1 - t0:.1f}s, {1 << n} subsets x 2 splits "
                  f"{time.perf_counter() - t1:.1f}s", flush=True)
            del model, valid_dataset, test_dataset, result
    if not labels_done:
        raise SystemExit("no checkpoints scored")
    arrays = {k: np.stack(v) for k, v in collected.items()}
    np.savez(npz_path, names=np.array(names), checkpoints=np.array(labels_done), **arrays)
    print(f"\nall done in {time.perf_counter() - started:.0f}s; max |BA gap| between batched and "
          f"row-by-row/loader paths over the untouched + verified masks = {worst_gap:.6f}")
    summarise_subsets(arrays, names, args.out_dir)


# ==============================================================================
# mode `ge` -- was analysis/probes/ge_feature_ablation.py
# ==============================================================================



NON_DESCRIPTOR = ("esm3", "bury", "node_x", "molformer")


PROTEIN_SIDE_NON_DESCRIPTOR = ("esm3", "bury", "node_x")


BATCH = 32


def load_checkpoint(label, group, seed, require_descriptor_mlp=False):
    """(conf, model, (train, valid, test)) for one (label, group, seed) checkpoint.

    One loader for every mode below: the per-mode copies this merged from differed
    only in the argv tag, whether they asserted --descriptor_mlp, and whether they
    unpacked the train dataset -- none of which is a reason for two reconstructions of
    the same model to drift apart.
    """
    models_dir = os.path.join(PROJECT_ROOT, "models", label_family(label), label, f"groups_{group}")
    argv = json.load(open(os.path.join(models_dir, f"seed{seed}.args.json")))
    conf = read_configuration(["input_ablation"] + argv)
    if require_descriptor_mlp and not conf.descriptor_mlp:
        raise SystemExit(f"{label} is not a --descriptor_mlp label")
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    datasets = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed, excluded_subgroups=conf.excluded_subgroups,
        config=conf, excluded_groups=conf.excluded_groups,
    )
    del csv
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(
        os.path.join(models_dir, f"seed{seed}.pt"), map_location="cpu", weights_only=True
    ))
    model.eval()
    return conf, model, datasets


def collate(dataset, indices):
    subset = torch.utils.data.Subset(dataset, [int(i) for i in indices])
    loader = torch_geometric.loader.DataLoader(
        subset, batch_size=max(len(indices), 1), shuffle=False, num_workers=0
    )
    return next(iter(loader))


class Block:
    """One held-out split, pre-collated: row batches, a one-graph-per-protein batch, labels."""

    def __init__(self, dataset):
        self.dataset = dataset
        frame = dataset.csv
        self.frame = frame
        loader = torch_geometric.loader.DataLoader(
            dataset, batch_size=BATCH, shuffle=False, num_workers=0
        )
        self.batches = list(loader)
        self.labels = torch.cat([p.inter.view(-1) for p, _ in self.batches]).numpy()
        proteins = frame["LTPProtein"].to_numpy()
        codes, uniques = pd.factorize(proteins)
        self.row_protein = codes
        first = np.zeros(len(uniques), dtype=int)
        first[codes[::-1]] = np.arange(len(codes))[::-1]
        self.unique_batch = collate(dataset, first)
        counts = torch.bincount(self.unique_batch[0].batch)
        self.unique_counts = counts.tolist()
        self.expanded = "_candidate_index" in frame.columns
        if self.expanded:
            self.pair_index, _ = pd.factorize(frame["pair_id"].to_numpy())
            pair_first = np.zeros(self.pair_index.max() + 1, dtype=int)
            pair_first[self.pair_index[::-1]] = np.arange(len(self.pair_index))[::-1]
            self.pair_labels = self.labels[pair_first]
        else:
            self.pair_labels = self.labels

    def pool(self, probs):
        if not self.expanded:
            return probs
        sums = np.zeros(self.pair_index.max() + 1)
        counts = np.zeros_like(sums)
        np.add.at(sums, self.pair_index, probs)
        np.add.at(counts, self.pair_index, 1)
        return sums / counts


def train_means(model, train_dataset):
    """Per-dimension mean over the TRAIN proteins' nodes / lipids' tokens, one graph per unique."""
    frame = train_dataset.csv
    p_codes, p_unique = pd.factorize(frame["LTPProtein"].to_numpy())
    p_first = np.zeros(len(p_unique), dtype=int)
    p_first[p_codes[::-1]] = np.arange(len(p_codes))[::-1]
    l_codes, l_unique = pd.factorize(frame["FullIdentityOfLipid"].to_numpy())
    l_first = np.zeros(len(l_unique), dtype=int)
    l_first[l_codes[::-1]] = np.arange(len(l_codes))[::-1]
    prot, _ = collate(train_dataset, p_first)
    _, lip = collate(train_dataset, l_first)
    present = prot.bury != 2  # 2 marks a missing burial value
    return {
        "esm3": prot.plm.float().mean(0),
        "node_x": prot.x.float().mean(0),
        "bury": prot.bury[present].float().mean() if present.any() else prot.bury.float().mean(),
        "molformer": lip.x.float().mean(0),
    }


class Ablation:
    """Forward-pre-hook on the model: replaces chosen inputs in the kwargs of one forward."""

    def __init__(self, descriptor_columns, descriptor_names, means):
        self.columns = descriptor_columns
        self.names = descriptor_names
        self.means = means
        self.zeroed = frozenset()
        self.mode = "zero"
        self.lipid_only = False  # protein-side replacements are cached instead of applied

    def __call__(self, module, args, kwargs):
        if not self.zeroed:
            return None
        kwargs = dict(kwargs)
        if not self.lipid_only:
            cols = [c for c, n in zip(self.columns, self.names) if n in self.zeroed]
            if cols and kwargs.get("descriptor_catalog_input") is not None:
                catalog = kwargs["descriptor_catalog_input"].clone()
                catalog[:, cols] = 0.0
                kwargs["descriptor_catalog_input"] = catalog
            for name, key in (("esm3", "plm"), ("node_x", "prot"), ("bury", "bury")):
                if name in self.zeroed:
                    tensor = kwargs[key]
                    if self.mode == "mean":
                        kwargs[key] = (self.means[name].to(tensor.dtype)).expand_as(tensor).clone()
                    else:
                        kwargs[key] = torch.zeros_like(tensor)
        if "molformer" in self.zeroed:
            tensor = kwargs["lip"]
            if self.mode == "mean":
                kwargs["lip"] = self.means["molformer"].to(tensor.dtype).expand_as(tensor).clone()
            else:
                kwargs["lip"] = torch.zeros_like(tensor)
        return args, kwargs


class Scorer:
    def __init__(self, conf, model, blocks, means):
        self.conf = conf
        self.model = model
        self.blocks = blocks
        columns = model.protein1.protein_descriptor_columns
        catalog = full_catalog_order(conf)
        self.descriptor_columns = [int(c) for c in columns.tolist()]
        self.descriptor_names = [catalog[c] for c in self.descriptor_columns]
        self.ablation = Ablation(self.descriptor_columns, self.descriptor_names, means)
        model.register_forward_pre_hook(self.ablation, with_kwargs=True)
        self.features = list(self.descriptor_names) + list(NON_DESCRIPTOR)
        self.cache = {}

    def _protein_key(self, zeroed, mode, split):
        protein_side = frozenset(
            z for z in zeroed if z in self.descriptor_names or z in PROTEIN_SIDE_NON_DESCRIPTOR
        )
        uses_mode = any(z in PROTEIN_SIDE_NON_DESCRIPTOR for z in protein_side)
        return (protein_side, mode if uses_mode else "zero", split)

    @torch.no_grad()
    def _protein_embeddings(self, zeroed, mode, split):
        key = self._protein_key(zeroed, mode, split)
        if key in self.cache:
            return self.cache[key]
        block = self.blocks[split]
        captured = []
        handle = self.model.protein1.register_forward_hook(lambda m, a, o: captured.append(o))
        self.ablation.zeroed = key[0]
        self.ablation.mode = key[1]
        self.ablation.lipid_only = False
        try:
            prot, lip = block.unique_batch
            self.model(**build_forward_args(self.conf, prot, lip))
        finally:
            handle.remove()
        embedding = captured[0].detach()
        pieces = list(torch.split(embedding, block.unique_counts))
        self.cache[key] = pieces
        if len(self.cache) > 4096:
            self.cache.pop(next(iter(self.cache)))
        return pieces

    @torch.no_grad()
    def probs(self, zeroed, mode, split, plain=False):
        """Probability of class 1 per row of the block's split (before candidate pooling)."""
        block = self.blocks[split]
        zeroed = frozenset(zeroed)
        out = []
        if plain:
            self.ablation.zeroed = zeroed
            self.ablation.mode = mode
            self.ablation.lipid_only = False
            for prot, lip in block.batches:
                logits = self.model(**build_forward_args(self.conf, prot, lip))
                out.append(torch.softmax(logits.float(), dim=1)[:, 1])
            return torch.cat(out).numpy()
        pieces = self._protein_embeddings(zeroed, mode, split)
        self.ablation.zeroed = frozenset(z for z in zeroed if z == "molformer")
        self.ablation.mode = mode
        self.ablation.lipid_only = True
        offset = 0
        protein_tower = self.model.protein1

        def patched(*args, **kwargs):
            nonlocal offset
            graphs = int(args[5].max()) + 1
            rows = block.row_protein[offset:offset + graphs]
            offset += graphs
            return torch.cat([pieces[j] for j in rows])

        protein_tower.forward = patched
        try:
            for prot, lip in block.batches:
                logits = self.model(**build_forward_args(self.conf, prot, lip))
                out.append(torch.softmax(logits.float(), dim=1)[:, 1])
        finally:
            del protein_tower.__dict__["forward"]
        return torch.cat(out).numpy()

    def metrics(self, zeroed, mode, split, plain=False):
        block = self.blocks[split]
        pooled = block.pool(self.probs(zeroed, mode, split, plain))
        return confusion_metrics(pooled, block.pair_labels)


def run_seed(args, seed):
    started = time.perf_counter()
    torch.set_num_threads(args.threads)
    conf, model, (train_dataset, valid_dataset, test_dataset) = load_checkpoint(
        args.label, args.group, seed
    )
    means = train_means(model, train_dataset)
    blocks = {"test": Block(test_dataset), "valid": Block(valid_dataset)}
    scorer = Scorer(conf, model, blocks, means)
    features = scorer.features
    rng = np.random.default_rng(seed)
    results = {}

    def evaluate(zeroed, mode):
        zeroed = frozenset(zeroed)
        effective = mode if any(z in NON_DESCRIPTOR for z in zeroed) else "zero"
        key = (zeroed, effective)
        if key not in results:
            results[key] = {s: scorer.metrics(zeroed, effective, s) for s in ("test", "valid")}
        return results[key]

    base = evaluate(frozenset(), "zero")
    rows = []

    def record(kind, name, zeroed, mode):
        measured = evaluate(zeroed, mode)
        effective = mode if any(z in NON_DESCRIPTOR for z in zeroed) else "zero"
        for split in ("test", "valid"):
            rows.append(dict(kind=kind, name=name, mode=effective, split=split, seed=seed,
                             **measured[split]))

    record("baseline", "baseline", [], "zero")
    for feature in features:
        record("single", feature, [feature], "zero")
        if feature in NON_DESCRIPTOR:
            record("single", feature, [feature], "mean")
    for a, b in itertools.combinations(features, 2):
        record("pair", f"{a}+{b}", [a, b], "zero")
    descriptors = list(scorer.descriptor_names)
    groups = {
        "all_descriptors": descriptors,
        "esm3+molformer": ["esm3", "molformer"],
        "protein_nondescriptor": list(PROTEIN_SIDE_NON_DESCRIPTOR),
        "protein_all": descriptors + list(PROTEIN_SIDE_NON_DESCRIPTOR),
        "lipid_all": ["molformer"],
        "everything": features,
    }
    for name, members in groups.items():
        record("group", name, members, "zero")
        if any(m in NON_DESCRIPTOR for m in members):
            record("group", name, members, "mean")

    # Sampled Shapley for v(S) = metric with exactly S KEPT, replacement mode args.shapley_mode.
    shapley = {s: {m: np.zeros(len(features)) for m in ("BA", "F1")} for s in ("test", "valid")}
    for _ in range(args.permutations):
        order = rng.permutation(len(features))
        zeroed = set(features)
        previous = evaluate(zeroed, args.shapley_mode)
        for index in order:
            zeroed.discard(features[index])
            current = evaluate(zeroed, args.shapley_mode)
            for split in ("test", "valid"):
                for metric in ("BA", "F1"):
                    shapley[split][metric][index] += current[split][metric] - previous[split][metric]
            previous = current
    shapley_out = {
        f"{split}_{metric}": (values / max(args.permutations, 1)).tolist()
        for split, per in shapley.items() for metric, values in per.items()
    }
    if args.verify:
        worst = 0.0
        for _ in range(args.verify):
            size = int(rng.integers(1, len(features)))
            zeroed = frozenset(rng.choice(features, size=size, replace=False).tolist())
            mode = "mean" if rng.random() < 0.5 else "zero"
            fast = scorer.probs(zeroed, mode, "test")
            slow = scorer.probs(zeroed, mode, "test", plain=True)
            worst = max(worst, float(np.abs(fast - slow).max()))
        print(f"seed {seed}: max |p_fast - p_plain| over {args.verify} random masks = {worst:.2e}",
              flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(os.path.join(args.out_dir, f"scores_seed{seed}.csv"), index=False)
    with open(os.path.join(args.out_dir, f"shapley_seed{seed}.json"), "w") as handle:
        json.dump(dict(features=features, permutations=args.permutations,
                       mode=args.shapley_mode, **shapley_out), handle)
    print(f"seed {seed}: {len(results)} distinct masks scored in "
          f"{time.perf_counter() - started:.0f}s; baseline test BA {base['test']['BA']:.4f} "
          f"F1 {base['test']['F1']:.4f}", flush=True)


def check_table(args, seeds):
    table = pd.read_csv(os.path.join(PROJECT_ROOT, "results", "tables", "metrics_summary.csv"), low_memory=False)
    table = table[table["label"] == args.label].sort_values("datetime")
    latest = table.groupby(["exclusion_set", "seed"]).tail(1)
    scores = pd.concat([pd.read_csv(os.path.join(args.out_dir, f"scores_seed{s}.csv")) for s in seeds])
    base = scores[(scores["kind"] == "baseline") & (scores["split"] == "test")]
    merged = base.merge(latest, on="seed", suffixes=("", "_table"))
    gap = (merged["BA"] - merged["balanced_accuracy"].astype(float)).abs()
    print(f"\ncheck vs metrics_summary.csv: {len(merged)} seeds matched; max |BA diff| "
          f"{gap.max():.4f}, mean {gap.mean():.4f}")


def summarise_ge(args, seeds):
    scores = pd.concat([pd.read_csv(os.path.join(args.out_dir, f"scores_seed{s}.csv")) for s in seeds])
    shapleys = [json.load(open(os.path.join(args.out_dir, f"shapley_seed{s}.json"))) for s in seeds]
    features = shapleys[0]["features"]
    base = scores[scores["kind"] == "baseline"].set_index(["split", "seed"])
    for column in ("BA", "F1"):
        pass

    def delta(frame, split):
        indexed = frame[frame["split"] == split].set_index("seed")
        reference = base.loc[split]
        return pd.DataFrame({
            "dBA": indexed["BA"] - reference["BA"].reindex(indexed.index),
            "dF1": indexed["F1"] - reference["F1"].reindex(indexed.index),
            "dAUC": indexed["AUC"] - reference["AUC"].reindex(indexed.index),
        })

    def aggregate(kind):
        part = scores[scores["kind"] == kind]
        rows = []
        for (name, mode), group in part.groupby(["name", "mode"]):
            test = delta(group, "test")
            valid = delta(group, "valid")
            rows.append(dict(name=name, mode=mode, dBA_test=test.dBA.mean(), dF1_test=test.dF1.mean(),
                             dAUC_test=test.dAUC.mean(), dBA_valid=valid.dBA.mean(),
                             worse=int((test.dBA < -0.005).sum()), better=int((test.dBA > 0.005).sum()),
                             n=len(test)))
        return pd.DataFrame(rows).sort_values("dBA_test").reset_index(drop=True)

    singles, pairs, groups = aggregate("single"), aggregate("pair"), aggregate("group")
    ref_t = base.loc["test"]
    ref_v = base.loc["valid"]
    print(f"\n{len(seeds)} seeds. Untouched: test BA {ref_t['BA'].mean():.3f} F1 {ref_t['F1'].mean():.3f} "
          f"AUC {ref_t['AUC'].mean():.3f} | valid BA {ref_v['BA'].mean():.3f}")

    # Sampled Shapley, mean and sd across seeds, ranked by test BA.
    ba = np.array([s["test_BA"] for s in shapleys])
    f1 = np.array([s["test_F1"] for s in shapleys])
    bav = np.array([s["valid_BA"] for s in shapleys])
    shap = pd.DataFrame({
        "feature": features, "shapley_BA_test": ba.mean(0), "sd_across_seeds": ba.std(0, ddof=1) if len(seeds) > 1 else 0.0,
        "shapley_F1_test": f1.mean(0), "shapley_BA_valid": bav.mean(0),
    }).sort_values("shapley_BA_test", ascending=False)
    shap.insert(0, "rank", range(1, len(features) + 1))
    single_zero = singles[singles["mode"] == "zero"].set_index("name")["dBA_test"]
    single_mean = singles[singles["mode"] == "mean"].set_index("name")["dBA_test"]
    shap["single_zero_dBA"] = shap["feature"].map(single_zero)
    shap["single_mean_dBA"] = shap["feature"].map(single_mean)
    perms = shapleys[0]["permutations"]
    print(f"\nSampled Shapley value of each input for test BA ({perms} permutations per seed, "
          f"replacement mode '{shapleys[0]['mode']}'), ranked by importance; sum over inputs = "
          f"untouched - everything replaced:")
    print(shap.round(4).to_string(index=False))
    print("\nNamed groups replaced together (test dBA, ascending = most damaging first):")
    print(groups.round(4).to_string(index=False))
    print("\nMost damaging pairs (test dBA; zero mode):")
    print(pairs.head(15).round(4).to_string(index=False))
    sums = {row["name"]: row["dBA_test"] for _, row in singles[singles["mode"] == "zero"].iterrows()}
    pairs = pairs.copy()
    pairs["sum_singles"] = [sums[n.split("+")[0]] + sums[n.split("+")[1]] for n in pairs["name"]]
    pairs["extra"] = pairs["dBA_test"] - pairs["sum_singles"]
    print("\nLargest synergy (pair worse than the sum of its singles):")
    print(pairs.sort_values("extra").head(6)[["name", "dBA_test", "sum_singles", "extra"]].round(4).to_string(index=False))
    print("\nLargest redundancy (pair milder than the sum of its singles):")
    print(pairs.sort_values("extra").tail(6)[["name", "dBA_test", "sum_singles", "extra"]].round(4).to_string(index=False))
    shap.to_csv(os.path.join(args.out_dir, "shapley.csv"), index=False)
    singles.to_csv(os.path.join(args.out_dir, "singles.csv"), index=False)
    pairs.to_csv(os.path.join(args.out_dir, "pairs.csv"), index=False)
    groups.to_csv(os.path.join(args.out_dir, "groups.csv"), index=False)
    print(f"\nwrote shapley.csv, singles.csv, pairs.csv, groups.csv in {args.out_dir}")


def run_ge(args):
    os.makedirs(args.out_dir, exist_ok=True)
    root = os.path.join(PROJECT_ROOT, "models", label_family(args.label), args.label)
    if args.group is None:
        found = sorted(d[len("groups_"):] for d in os.listdir(root) if d.startswith("groups_"))
        if len(found) != 1:
            raise SystemExit(f"--group required, found {found}")
        args.group = found[0]
    seeds = [int(s) for s in args.seeds.split(",")]
    if args.threads is None:
        args.threads = max(1, (os.cpu_count() or 4) // max(args.workers, 1) - 1)

    if args.seed_child is not None:
        run_seed(args, args.seed_child)
        return
    if not args.summarize_only:
        started = time.perf_counter()
        pending = list(seeds)
        running = []
        while pending or running:
            while pending and len(running) < args.workers:
                seed = pending.pop(0)
                command = [sys.executable, os.path.abspath(__file__), "ge", "--label", args.label,
                           "--group", args.group, "--out_dir", args.out_dir,
                           "--permutations", str(args.permutations), "--shapley_mode", args.shapley_mode,
                           "--verify", str(args.verify), "--threads", str(args.threads),
                           "--seed_child", str(seed)]
                running.append(subprocess.Popen(command))
            time.sleep(1)
            running = [p for p in running if p.poll() is None]
        print(f"all seeds done in {time.perf_counter() - started:.0f}s")
    check_table(args, seeds)
    summarise_ge(args, seeds)


# ==============================================================================
# mode `compat` -- was analysis/probes/compat_input_ablation.py
# ==============================================================================



def score_split_compat(model, conf, dataset, device, zero_compat):
    """Class-1 probability per row, optionally with compat_input replaced by zero.

    Same loader settings as analysis/checkpoint_scores.py -- `shuffle=False` so the
    scores line up with `dataset.csv` row for row, `eval()` so nothing is order
    dependent.
    """
    loader = torch_geometric.loader.DataLoader(
        dataset, batch_size=32, shuffle=False, num_workers=0
    )
    probs, labels = [], []
    model.eval()
    with torch.no_grad():
        for prot, lipid in loader:
            prot = prot.to(device)
            lipid = lipid.to(device)
            if zero_compat:
                prot.compat_input = torch.zeros_like(prot.compat_input)
            out = model(**build_forward_args(conf, prot, lipid))
            probs.append(torch.softmax(out.float(), dim=1)[:, 1].cpu())
            labels.append(prot.inter.view(-1).cpu())
    return torch.cat(probs).numpy(), torch.cat(labels).numpy()


def ablation_table(label, epoch, seeds, families, split, batch=16, device=None,
                    verbose=True):
    """One row per (family, seed): AUC with the feature and with it zeroed."""
    device = device or torch.device("cpu")
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    base = arg_lines(label)

    rows = []
    for family in families:
        for seed in seeds:
            argv = ["input_ablation"] + base + [
                f"--excluded_groups={family}", f"--seed={seed}",
                f"--batch={batch}", "--num_workers=0",
            ]
            conf = read_configuration(argv)
            if not getattr(conf, "compatibility_input", False):
                raise SystemExit(
                    f"{label} was not trained with --compatibility_input -- there is no "
                    "feature to ablate"
                )
            if conf.final_m is None:
                conf.final_m = conf.m
            seed_everything(conf.seed)
            csv = pandas.read_csv(interaction_csv_path(data_dir))
            _, valid_dataset, test_dataset = PLIDataset(
                root_dir=data_dir, csv=csv, seed=conf.seed,
                excluded_subgroups=conf.excluded_subgroups, config=conf,
                excluded_groups=conf.excluded_groups,
            )
            del csv
            dataset = valid_dataset if split == "valid" else test_dataset

            checkpoint = os.path.join(
                PROJECT_ROOT, "models", label_family(label), label, f"groups_{family}", "dynamics",
                f"seed{seed}_epoch{epoch}.pt",
            )
            if not os.path.exists(checkpoint):
                if verbose:
                    print(f"missing : {checkpoint}", flush=True)
                continue
            model = InteractionClassification(conf).to(device)
            model.load_state_dict(
                torch.load(checkpoint, map_location="cpu", weights_only=True)
            )

            frame = dataset.csv
            with_feature, labels = score_split_compat(model, conf, dataset, device, False)
            without, labels_again = score_split_compat(model, conf, dataset, device, True)
            assert (labels == labels_again).all()
            assert (frame["Interaction"].to_numpy() == labels).all()

            record = {
                "fam": family, "seed": seed, "rows": len(frame),
                "with": auc(labels, with_feature),
                "zeroed": auc(labels, without),
            }
            record["with_prot"], record["proteins"] = per_protein_auc(
                frame, with_feature
            )
            record["zeroed_prot"], _ = per_protein_auc(frame, without)
            rows.append(record)
            if verbose:
                print(
                    f"{family} seed{seed} : {record['with']:.3f} -> "
                    f"{record['zeroed']:.3f} pooled, {record['with_prot']:.3f} -> "
                    f"{record['zeroed_prot']:.3f} inside protein",
                    flush=True,
                )

    table = pandas.DataFrame(rows)
    table["drop"] = table["with"] - table["zeroed"]
    table["drop_prot"] = table["with_prot"] - table["zeroed_prot"]
    return table


def print_ablation_report(table, split, epoch, label):
    pandas.set_option("display.width", 220)
    print(f"\n=== {split} block, epoch {epoch}, {label} ===")
    print(table.round(3).to_string(index=False))

    columns = ["with", "zeroed", "drop", "with_prot", "zeroed_prot", "drop_prot"]
    print("\n=== per family (mean over seeds) ===")
    print(table.groupby("fam")[columns].mean().round(3).to_string())

    print("\n=== grouped (files/results/signal_state.md 6.4) ===")
    print(pandas.DataFrame({
        "all seven": table[columns].mean(),
        "working three": table[table["fam"].isin(WORKING)][columns].mean(),
        "other four": table[~table["fam"].isin(WORKING)][columns].mean(),
        "scp2 only": table[table["fam"] == "scp2"][columns].mean(),
    }).round(3).to_string())
    print()


def run_compat(args):

    table = ablation_table(
        args.label, args.epoch,
        seeds=[int(s) for s in args.seeds.split(",")],
        families=[f for f in args.families.split(",") if f],
        split=args.split, batch=args.batch,
    )
    print_ablation_report(table, args.split, args.epoch, args.label)
    if args.out:
        table.to_csv(args.out, index=False)
        print(f"wrote : {args.out}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    modes = parser.add_subparsers(dest="mode", required=True)

    descriptors = modes.add_parser(
        "descriptors",
        help="one --descriptor_mlp input column (or named group) at a time, zeroed or permuted",
    )
    descriptors.add_argument("--label", required=True)
    descriptors.add_argument("--groups", default=None, help="comma list; default every group with a checkpoint")
    descriptors.add_argument("--seeds", default="0,1,2,3,4")
    descriptors.add_argument("--out", required=True)
    descriptors.add_argument("--check_table", action="store_true")
    descriptors.add_argument("--modes", default="zero,permute", help="comma list of zero,permute")
    descriptors.add_argument("--pairs", action="store_true", help="also ablate every pair of features together")
    descriptors.add_argument("--only_pairs", action="store_true", help="pairs only; skip the single features and groups")

    subsets = modes.add_parser(
        "subsets", help="every one of the 2^n - 1 subsets of the --descriptor_mlp vector",
    )
    subsets.add_argument("--label", required=True)
    subsets.add_argument("--groups", default=None)
    subsets.add_argument("--seeds", default="0,1,2,3,4")
    subsets.add_argument("--out_dir", required=True)
    subsets.add_argument("--verify", type=int, default=3,
                         help="random masks per checkpoint re-scored row by row (0 = skip)")
    subsets.add_argument("--summarize_only", action="store_true", help="re-print from arrays.npz")

    ge = modes.add_parser(
        "ge", help="the node_x / esm3 / bury / descriptor / molformer inputs of a ge_* checkpoint",
    )
    ge.add_argument("--label", required=True)
    ge.add_argument("--group", default=None, help="excluded-group directory name (default: the only one)")
    ge.add_argument("--seeds", default="0,1,2,3,4")
    ge.add_argument("--out_dir", required=True)
    ge.add_argument("--permutations", type=int, default=100, help="Shapley permutations per seed")
    ge.add_argument("--shapley_mode", default="zero", choices=("zero", "mean"))
    ge.add_argument("--verify", type=int, default=4, help="random masks per seed re-scored unpatched")
    ge.add_argument("--workers", type=int, default=1, help="parallel processes (one per seed)")
    ge.add_argument("--threads", type=int, default=None)
    ge.add_argument("--seed_child", type=int, default=None, help=argparse.SUPPRESS)
    ge.add_argument("--summarize_only", action="store_true")

    compat = modes.add_parser(
        "compat", help="the single --compatibility_input scalar, with and without",
    )
    compat.add_argument("--label", required=True)
    compat.add_argument("--epoch", type=int, default=120)
    compat.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    compat.add_argument("--seeds", default="0,1")
    compat.add_argument("--batch", type=int, default=16)
    compat.add_argument("--split", default="valid", choices=("valid", "test"))
    compat.add_argument("--out", help="write the per-split table here")

    args = parser.parse_args()
    return {
        "descriptors": run_descriptors,
        "subsets": run_subsets,
        "ge": run_ge,
        "compat": run_compat,
    }[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
