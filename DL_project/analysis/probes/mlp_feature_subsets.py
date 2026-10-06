#!/usr/bin/env python3
"""Zero EVERY subset of a --descriptor_mlp label's input features, from saved checkpoints.

With n descriptor names there are 2^n - 1 non-empty subsets (n=17: 131071). For each
(excluded group, seed) checkpoint (models/<label>/groups_<g>/seed<N>.pt, the weights
run_test measures) this scores the held-out test AND validation blocks under every subset
zeroed -- zero is the train mean, the inputs being train-standardised -- and writes the
per-checkpoint BA / F1 / sensitivity / specificity at the 0.5 threshold.

Why it is fast. In a --descriptor_mlp run the whole model is
`binar(descriptor_mlp_head(x))` with x the n standardised columns of one row, so nothing
upstream (graphs, ESM3, MolFormer) depends on the ablated columns. The loader and the
checkpoint are touched ONCE per checkpoint: the standardised input matrix of the block is
recorded with a forward hook, and every subset is then one batched forward of the small
MLP over (subsets x rows) -- masks are applied by multiplying the recorded matrix, metrics
come from matrix products. A row-by-row reference path (mlp_feature_ablation.ColumnOverride)
re-scores a few random subsets per checkpoint and must agree (`--verify`).

A mask is an integer, bit i set = feature i (in head.token_names order) ZEROED; mask 0 is
the untouched checkpoint, mask 2^n - 1 zeroes everything.

Outputs (in --out_dir): arrays.npz (per-checkpoint metrics for every mask), subsets.csv
(mean delta vs the untouched checkpoint, per mask), shapley.csv, by_size.csv, and the
printed summary. Reads only; trains nothing, appends to no shared table.

Selection warning. Picking the subset with the best mean TEST BA out of 131071 is picking
a maximum of that many noisy means. The "selected on validation" lines choose on the
validation block and report the TEST block of that choice: that is the number to quote.
AUC is not computed here (rank statistic per subset; not needed for the 0.5 reading).

    python3 analysis/probes/mlp_feature_subsets.py --label mlp_sub_pb6 --out_dir /tmp/subsets
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
from training.results_layout import label_family  # noqa: E402
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

from checkpoint_scores import (  # noqa: E402
    _average_candidate_rows,
    read_configuration,
    seed_everything,
    score_split,
    PLIDataset,
    InteractionClassification,
    interaction_csv_path,
)
from architecture.descriptor_mlp_head import DescriptorMLPHead  # noqa: E402
from mlp_feature_ablation import ColumnOverride, confusion_metrics  # noqa: E402

torch.set_flush_denormal(True)

ROWS_PER_CHUNK = 400_000  # (masks x rows) per batched forward; ~27 MB of float32 input


def load_checkpoint(label, group, seed):
    models_dir = os.path.join(PROJECT_ROOT, "models", label_family(label), label, f"groups_{group}")
    argv = json.load(open(os.path.join(models_dir, f"seed{seed}.args.json")))
    conf = read_configuration(["mlp_feature_subsets"] + argv)
    if not conf.descriptor_mlp:
        raise SystemExit(f"{label} is not a --descriptor_mlp label")
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    _, valid_dataset, test_dataset = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed, excluded_subgroups=conf.excluded_subgroups,
        config=conf, excluded_groups=conf.excluded_groups,
    )
    del csv
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(
        os.path.join(models_dir, f"seed{seed}.pt"), map_location="cpu", weights_only=True
    ))
    model.eval()
    return conf, model, valid_dataset, test_dataset


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
        probs, labels = score_split(model, conf, dataset, torch.device("cpu"))
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


@torch.no_grad()
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
            probs, labels = score_split(model, conf, dataset, torch.device("cpu"))
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


def summarise(arrays, names, out_dir):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--groups", default=None)
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--verify", type=int, default=3,
                        help="random masks per checkpoint re-scored row by row (0 = skip)")
    parser.add_argument("--summarize_only", action="store_true", help="re-print from arrays.npz")
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    npz_path = os.path.join(args.out_dir, "arrays.npz")

    if args.summarize_only:
        stored = np.load(npz_path, allow_pickle=True)
        summarise({k: stored[k] for k in ("test_BA", "test_F1", "valid_BA", "valid_F1")},
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
            conf, model, valid_dataset, test_dataset = load_checkpoint(args.label, group, seed)
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
    summarise(arrays, names, args.out_dir)


if __name__ == "__main__":
    main()
