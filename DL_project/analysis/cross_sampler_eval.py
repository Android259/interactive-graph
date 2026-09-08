#!/usr/bin/env python3
"""One model's weights, another run's evaluation rows -- the 2x2 that separates
"the flag changed the block" from "the flag changed what was learned".

Why this exists. A sampler flag (--balanced_lipid_classes, --balanced_proteins,
--balance_negatives_by_family, --negatives_per_positive) is applied BEFORE the split
(dataloader/Dataloader.py:1416), so turning one on changes the evaluation rows as well as
the training signal. Two labels differing by such a flag are therefore not measured on
the same question, and the difference between their reported numbers mixes the two
effects. Measured on the lipid cold split: --balanced_lipid_classes moves the test block
from 244 to 276 rows on anionic and from 88 to 74 on sphingolipids, keeps the positive
count identical (it redraws only the negatives), and changes the per-class positive-rate
spread inside the block -- and the sign of that change matches the sign of the reported
BA change on 4 sets out of 4.

What it does. For every (weights label, rows label) pair it rebuilds the rows label's
split, loads the weights label's checkpoint into a model built from the rows label's
configuration, and scores that block. Holding the weights fixed across two row sets
isolates the block effect; holding the rows fixed across two weight sets isolates the
training-signal effect.

Why this is legitimate here, and when it is NOT. It is only meaningful if the weights
label never trained on the rows label's evaluation rows. Under --lipid_coldsplit that
holds by construction -- the held-out classes leave training for every protein under any
sampler -- and it is CHECKED per (set, seed) rather than assumed: any overlap is reported
and, unless --allow_leakage is passed, aborts. On a random or protein-axis split the
overlap is generally NOT zero and the check will (correctly) refuse.

The two labels must share an architecture: the checkpoint is loaded strictly into a model
built from the rows label's config, so a shape mismatch raises rather than silently
loading part of the state.

On which epoch. The weights a run actually tested (`best_model_state`, selected by pooled
validation balanced accuracy, training/new_train.py:2219,2281) are saved only under
--save_checkpoint, which no lipid-cold-split label sets; --save_model_in_dynamics keeps
DYNAMICS_CHECKPOINT_EPOCHS (1, 10, 49, 51, 120) instead. That does not damage this
comparison: every contrast here holds the weights constant across row sets (or the rows
constant across weight sets), so a fixed, arbitrary epoch cancels inside a contrast --
but it does mean the ABSOLUTE numbers are not the ones the run reported. Pass several
--epochs and read whether the contrast is stable across them.

Reads only. Trains nothing, touches no shared table; writes only --out.

    scripts/env.sh python3 analysis/cross_sampler_eval.py \
        --labels A,B --sets anionic,choline --seeds 0,1,2,3,4 --epochs 49,51,120 \
        --out /tmp/cross.csv
    scripts/env.sh python3 analysis/cross_sampler_eval.py --weights A --rows B ...
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

# Same reason as new_train.py/checkpoint_scores.py: set before any thread exists.
torch.set_flush_denormal(True)

import torch_geometric  # noqa: E402,F401

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from checkpoint_scores import (  # noqa: E402
    arg_lines, default_groups_for_label, score_split, split_argv,
)

DEFAULT_EPOCHS = "49,51,120"


def binary_auc(labels, scores):
    labels = np.asarray(labels)
    scores = np.asarray(scores, dtype=float)
    positive, negative = scores[labels == 1], scores[labels != 1]
    if not len(positive) or not len(negative):
        return float("nan")
    difference = positive[:, None] - negative[None, :]
    return float(((difference > 0).sum() + 0.5 * (difference == 0).sum()) / difference.size)


def within_protein_pair_auc(proteins, labels, scores):
    """training/new_train.py::within_protein_pair_auc, over the columns available here.

    Every (positive, negative) pair of rows SHARING a protein, concordant over total,
    ties half. Comparisons never cross a protein boundary, which is the whole reason the
    metric exists on this split.
    """
    frame = pd.DataFrame({
        "protein": proteins,
        "label": np.asarray(labels),
        "score": np.asarray(scores, dtype=float),
    })
    concordant, total, blocks = 0.0, 0, 0
    for _, group in frame.groupby("protein"):
        positive = group.score[group.label == 1].to_numpy()
        negative = group.score[group.label != 1].to_numpy()
        if not len(positive) or not len(negative):
            continue
        blocks += 1
        difference = positive[:, None] - negative[None, :]
        concordant += (difference > 0).sum() + 0.5 * (difference == 0).sum()
        total += difference.size
    return (concordant / total if total else float("nan")), blocks


def balanced_accuracy(labels, scores, threshold=0.5):
    labels = np.asarray(labels)
    predicted = (np.asarray(scores, dtype=float) >= threshold).astype(int)
    true_positive = int(((predicted == 1) & (labels == 1)).sum())
    false_negative = int(((predicted == 0) & (labels == 1)).sum())
    true_negative = int(((predicted == 0) & (labels != 1)).sum())
    false_positive = int(((predicted == 1) & (labels != 1)).sum())
    if not (true_positive + false_negative) or not (true_negative + false_positive):
        return float("nan")
    return 0.5 * (
        true_positive / (true_positive + false_negative)
        + true_negative / (true_negative + false_positive)
    )


def build_split(label, group, seed, batch, data_dir):
    """(config, train pair ids, test dataset) for one label's own (group, seed) split."""
    argv = ["cross_sampler_eval"] + split_argv(arg_lines(label), group) + [
        f"--seed={seed}", f"--batch={batch}", "--num_workers=0",
    ]
    conf = read_configuration(argv)
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    csv = pd.read_csv(interaction_csv_path(data_dir))
    train_dataset, _, test_dataset = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )
    del csv
    return conf, set(train_dataset.csv["pair_id"]), test_dataset


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--labels", help="comma-separated labels; every (weights, rows) "
                                         "combination of them is evaluated")
    parser.add_argument("--weights", help="labels to take weights from (default: --labels)")
    parser.add_argument("--rows", help="labels to take evaluation rows from (default: --labels)")
    parser.add_argument("--sets", help="excluded-group names (default: the labels' own axis)")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--epochs", default=DEFAULT_EPOCHS,
                        help="dynamics epochs to load; a contrast is read within one epoch")
    parser.add_argument("--batch", type=int, default=16, help="only affects the split's sampler")
    parser.add_argument("--allow_leakage", action="store_true",
                        help="do not abort when a weights label trained on the rows label's "
                             "evaluation rows -- the result is then not interpretable")
    parser.add_argument("--out", help="write the per-(rows, weights, epoch, set, seed) table here")
    args = parser.parse_args()

    weights_labels = [x for x in (args.weights or args.labels or "").split(",") if x]
    rows_labels = [x for x in (args.rows or args.labels or "").split(",") if x]
    if not weights_labels or not rows_labels:
        raise SystemExit("pass --labels, or both --weights and --rows")
    groups = ([x for x in args.sets.split(",") if x] if args.sets
              else default_groups_for_label(rows_labels[0]))
    seeds = [int(s) for s in args.seeds.split(",") if s]
    epochs = [int(e) for e in args.epochs.split(",") if e]
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep

    records = []
    for rows_label in rows_labels:
        for group in groups:
            for seed in seeds:
                conf, _, test_dataset = build_split(rows_label, group, seed, args.batch, data_dir)
                proteins = test_dataset.csv["LTPProtein"].to_numpy()
                evaluated = set(test_dataset.csv["pair_id"])
                model = InteractionClassification(conf)
                for weights_label in weights_labels:
                    if weights_label != rows_label:
                        _, other_train, _ = build_split(
                            weights_label, group, seed, args.batch, data_dir
                        )
                        overlap = evaluated & other_train
                        if overlap:
                            message = (
                                f"{weights_label} trained on {len(overlap)} of the "
                                f"{len(evaluated)} rows {rows_label}/{group}/seed{seed} "
                                "is scored on -- the contrast is not interpretable"
                            )
                            if not args.allow_leakage:
                                raise SystemExit("leakage: " + message)
                            print("WARNING leakage: " + message, flush=True)
                    for epoch in epochs:
                        checkpoint = os.path.join(
                            PROJECT_ROOT, "models", weights_label, f"groups_{group}",
                            "dynamics", f"seed{seed}_epoch{epoch}.pt",
                        )
                        if not os.path.exists(checkpoint):
                            print(f"missing : {checkpoint}", flush=True)
                            continue
                        model.load_state_dict(
                            torch.load(checkpoint, map_location="cpu", weights_only=True)
                        )
                        scores, labels = score_split(model, conf, test_dataset, torch.device("cpu"))
                        pair_auc, blocks = within_protein_pair_auc(proteins, labels, scores)
                        records.append({
                            "rows_from": rows_label, "weights_from": weights_label,
                            "epoch": epoch, "set": group, "seed": seed,
                            "rows": len(labels), "positives": int(np.sum(labels)),
                            "BA": balanced_accuracy(labels, scores),
                            "AUC": binary_auc(labels, scores),
                            "AUC_within_protein_pairs": pair_auc,
                            "AUC_within_protein_pairs_proteins": blocks,
                        })
                    print(f"{rows_label[-28:]} rows | {weights_label[-28:]} weights | "
                          f"{group} seed{seed} : scored", flush=True)
                del test_dataset, model

    if not records:
        raise SystemExit("nothing scored")
    table = pd.DataFrame(records)
    if args.out:
        table.to_csv(args.out, index=False)
        print(f"wrote : {args.out}")

    short = {label: label[-24:] for label in set(rows_labels) | set(weights_labels)}
    for metric in ("BA", "AUC", "AUC_within_protein_pairs"):
        for epoch in epochs:
            block = table[table["epoch"] == epoch]
            if block.empty:
                continue
            print(f"\n=== {metric} | epoch {epoch} | rows down, weights across ===")
            pivot = block.pivot_table(index=["set", "rows_from"], columns="weights_from",
                                      values=metric)
            pivot.columns = [short[column] for column in pivot.columns]
            pivot.index = pd.MultiIndex.from_tuples(
                [(one_set, short[one_label]) for one_set, one_label in pivot.index],
                names=["set", "rows"],
            )
            print(pivot.round(4).to_string())


if __name__ == "__main__":
    main()
