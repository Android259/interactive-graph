#!/usr/bin/env python3
"""Inference-time ablation of the --descriptor_mlp input vector, from saved checkpoints.

For every (excluded group, seed) of a --descriptor_mlp label, loads models/<label>/
groups_<g>/seed<N>.pt (the weights run_test measures), rebuilds the split from the
seed<N>.args.json stored beside it, and re-scores the held-out block with ONE input
column (or a named group of columns) of DescriptorMLPHead replaced:

    zero     the column is set to 0. Inputs are standardised on train, so 0 is the train mean.
    permute  the column's values are shuffled across the block's rows (fixed RNG): keeps the
             feature's marginal distribution, breaks its link to the row.

Reads only; trains nothing, appends to no shared table.

What it answers: how much the TRAINED model relies on a feature. It does not answer what a
model trained without the feature would score -- other inputs can compensate there, and the
13 pocket descriptors are constants of the protein and correlated, so zeroing one gives an
input combination never seen in training. For redundant features this underestimates
importance; the `pocket` and `lipid` groups below are the cleaner reading.

    python3 analysis/mlp_feature_ablation.py --label mlp_sub_pb6 --out /tmp/ablation.csv

`baseline` rows are the unmodified checkpoint; `--check_table` compares their BA/F1 with the
latest metrics_summary.csv row of the same (label, group, seed).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
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
from dataloader.pair_descriptors import LIPID_DESCRIPTOR_NAMES  # noqa: E402

torch.set_flush_denormal(True)


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
    models_dir = os.path.join(PROJECT_ROOT, "models", label, f"groups_{group}")
    argv = json.load(open(os.path.join(models_dir, f"seed{seed}.args.json")))
    conf = read_configuration(["mlp_feature_ablation"] + argv)
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
        probs, labels = score_split(model, conf, test_dataset, torch.device("cpu"))
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
    table = pd.read_csv(os.path.join(PROJECT_ROOT, "metrics_summary.csv"), low_memory=False)
    table = table[table["label"] == label].sort_values("datetime")
    latest = table.groupby(["exclusion_set", "seed"]).tail(1)
    base = frame[frame["feature"] == "baseline"].copy()
    base["exclusion_set"] = "groups_" + base["group"]
    merged = base.merge(latest, on=["exclusion_set", "seed"], suffixes=("", "_table"))
    gap = (merged["BA"] - merged["balanced_accuracy"].astype(float)).abs()
    print(f"\ncheck vs metrics_summary.csv: {len(merged)} (group, seed) matched; "
          f"max |BA diff| = {gap.max():.4f}, mean = {gap.mean():.4f}, "
          f"{int((gap > 0.005).sum())} differ by > 0.005")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--groups", default=None, help="comma list; default every group with a checkpoint")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--out", required=True)
    parser.add_argument("--check_table", action="store_true")
    parser.add_argument("--modes", default="zero,permute", help="comma list of zero,permute")
    parser.add_argument("--pairs", action="store_true", help="also ablate every pair of features together")
    parser.add_argument("--only_pairs", action="store_true", help="pairs only; skip the single features and groups")
    args = parser.parse_args()

    root = os.path.join(PROJECT_ROOT, "models", args.label)
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


if __name__ == "__main__":
    main()
