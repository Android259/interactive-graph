#!/usr/bin/env python3
"""Rebuilds the four tables of files/results_section.tex, given only a sweep label.

files/results_section.tex reports bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120
(lipid_random_choice on) over five seeds. This script is the single place that turns a
label's saved checkpoints into the four tables: BA at the checkpoint epoch (from
metrics_summary.csv directly, since only the five dynamics milestones -- 1, 10, 49, 51,
120 -- have saved weights, and the checkpoint epoch is usually none of them), AUC
pooled/in-protein against the chemistry null model at a fixed epoch (120 by default; see
--by_best_checkpoint), the in-sample increment at that same epoch, and the scp2
net_prot-chem_prot trajectory over all five epochs.

Reads only (scoring a checkpoint is a forward pass, no gradient, nothing written back).

    scripts/env.sh python3 analysis/build_rand_results_tables.py \
        --label bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120

Scores every requested (family, seed, epoch) from models/<label>/groups_<family>/
dynamics/seed<seed>_epoch<epoch>.pt the same way analysis/checkpoint_scores.py does --
missing checkpoints (a sweep still in flight) are skipped, not fatal, same as there. Pass
an existing CSV via --scores (from analysis/checkpoint_scores.py, or a previous
--save-scores here) to reuse it instead of re-scoring, e.g. while iterating on the tables
themselves; --seeds/--families/--epochs then only filter which of ITS rows are used and
are not re-scored.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from analysis.checkpoint_scores import (  # noqa: E402
    DEFAULT_EPOCHS,
    label_descriptor_features,
    score_checkpoints,
)
from analysis.null_model import DEFAULT_FAMILIES, TANIMOTO, resolve_similarity  # noqa: E402
from analysis.interaction_increment import increment_table, print_increment_report  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402


def ba_table(metrics_csv, label, families, seeds):
    rows = pd.read_csv(metrics_csv)
    rows = rows[rows["label"] == label]
    rows = rows[rows["seed"].isin(seeds)]
    print("=== Balanced accuracy at the checkpoint epoch, test split (tab:randba) ===")
    means = []
    for family in families:
        key = f'["{family}"]'
        vals = rows.loc[rows["excluded_groups"] == key, "balanced_accuracy"].astype(float)
        means.append(vals.mean())
        print(f"{family:15s} {vals.mean():.3f}  n={len(vals)}  per-seed={[round(v, 3) for v in vals]}")
    print(f"{'mean':15s} {np.mean(means):.3f}")
    print()


def rows_pos_counts(scores, families, split, epoch=120):
    sub = scores[(scores["split"] == split) & (scores["epoch"] == epoch)]
    print(f"--- {split} block sizes (seed-invariant check) ---")
    for family in families:
        fam_sub = sub[sub["fam"] == family]
        by_seed = fam_sub.groupby("seed").agg(rows=("pair_id", "size"), pos=("label_value", "sum"))
        print(family, by_seed.to_dict("index"))
    print()


def auc_and_increment_tables(csv, similarity, index, entity_column, scores, families, seeds,
                              split, epoch=120):
    table = increment_table(
        csv, similarity, index, scores, families=families, seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split=split, epochs=[epoch],
        entity_column=entity_column,
    )
    print_increment_report(table, split, neighbours=15, entity_column=entity_column)
    return table


def select_best_epoch(csv, similarity, index, entity_column, scores, families, seeds):
    """The single saved epoch with the best mean in-protein AUC, VALID split only.

    "Best" is judged the way the rest of this file already reports: net_prot averaged
    per family, then over families (equal weight regardless of how many rows a family
    has), never on test -- picking an epoch by test performance would be exactly the
    leak this project's checkpoint rule exists to avoid. One epoch for every family and
    seed, not a per-family pick: the point is a single, honestly-comparable reporting
    point for the whole panel, standing in for the fixed epoch 120 the tables otherwise
    use -- which scp2_epoch_trajectory's own table already shows can be well past the
    point where a family's in-protein signal peaked.
    """
    candidates = sorted(int(e) for e in scores["epoch"].unique())
    print(f"=== --by_best_checkpoint: mean valid net_prot AUC per candidate epoch {candidates} ===")
    scored = {}
    for epoch in candidates:
        table = increment_table(
            csv, similarity, index, scores, families=families, seeds=seeds,
            neighbours=15, share=0.8, ratio=2, split="valid", epochs=[epoch],
            entity_column=entity_column,
        )
        per_family_mean = table.groupby("fam")["net_prot"].mean()
        scored[epoch] = float(per_family_mean.mean())
        print(f"  epoch {epoch:>4d} : mean net_prot (valid, over {len(per_family_mean)} families) = {scored[epoch]:.4f}")
    best_epoch = max(scored, key=scored.get)
    print(f"selected epoch {best_epoch} (highest mean valid net_prot)")
    print()
    return best_epoch


def scp2_epoch_trajectory(csv, similarity, index, entity_column, scores, seeds):
    table = increment_table(
        csv, similarity, index, scores, families=["scp2"], seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split="valid", epochs=None,
        entity_column=entity_column,
    )
    table_test = increment_table(
        csv, similarity, index, scores, families=["scp2"], seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split="test", epochs=None,
        entity_column=entity_column,
    )
    print("=== scp2 net_prot - chem_prot, every saved epoch, every seed (tab:scp2epochs) ===")
    for name, tbl in (("valid", table), ("test", table_test)):
        tbl = tbl.copy()
        tbl["delta"] = tbl["net_prot"] - tbl["chem_prot"]
        pivot = tbl.pivot(index="seed", columns="epoch", values="delta")
        print(f"--- {name} ---")
        print(pivot.round(3).to_string())
        print("mean over seeds:")
        print(pivot.mean(axis=0).round(3).to_string())
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scores", default=None,
        help="CSV from analysis/checkpoint_scores.py (or a previous --save-scores here); "
        "if omitted, checkpoints are scored directly from models/<label>/",
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--metrics-csv", default=os.path.join(PROJECT_ROOT, "metrics_summary.csv"))
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument(
        "--epochs", default=DEFAULT_EPOCHS,
        help="only used when --scores is omitted -- which saved checkpoints to score",
    )
    parser.add_argument(
        "--batch", type=int, default=16,
        help="only used when --scores is omitted -- affects only the split's sampler",
    )
    parser.add_argument(
        "--save-scores", default=None,
        help="only used when --scores is omitted -- also write the freshly scored rows here, "
        "so a repeat run (e.g. while iterating on the tables) can pass them back via --scores",
    )
    parser.add_argument(
        "--by_best_checkpoint", action="store_true",
        help="build the AUC/increment tables at the single saved epoch with the best mean "
        "valid in-protein AUC across every excluded group and seed, instead of the fixed "
        "epoch 120 -- see select_best_epoch. Never looks at test to choose it.",
    )
    parser.add_argument(
        "--features", default=None,
        help=(
            "Default: --good_descriptors/--bad_descriptors read off --label's own args "
            "file (see analysis.checkpoint_scores.label_descriptor_features), so the null "
            f'model runs on exactly the descriptor set the network was trained to see -- '
            f'falling back to "{TANIMOTO}" (this file\'s original, unconditional default) '
            "when the label sets neither flag. Pass an explicit comma-separated "
            "descriptor-name list, or \"tanimoto\", to override -- see null_model.py "
            "--features."
        ),
    )
    parser.add_argument("--features-label", help="short name for --features, see null_model.py --label")
    args = parser.parse_args()

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]

    ba_table(args.metrics_csv, args.label, families, seeds)

    features, features_label = args.features, args.features_label
    if features is None:
        features = label_descriptor_features(args.label, families)
        if features:
            features_label = features_label or "label_descriptors"
        else:
            features = TANIMOTO
            features_label = features_label or TANIMOTO

    csv = pd.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    similarity, index, entity_column, _, _ = resolve_similarity(
        csv, os.path.join(PROJECT_ROOT, "data"), features, features_label,
    )

    if args.scores:
        scores = pd.read_csv(args.scores)
    else:
        print(
            f"No --scores given; scoring {args.label}'s own checkpoints directly "
            f"(epochs={args.epochs}, seeds={args.seeds}, families={args.families})."
        )
        scores = score_checkpoints(
            args.label,
            epochs=[int(e) for e in args.epochs.split(",")],
            seeds=seeds,
            families=families,
            batch=args.batch,
        )
        if args.save_scores:
            scores.to_csv(args.save_scores, index=False)
            print(f"wrote scores : {args.save_scores}")

    rows_pos_counts(scores, families, "valid")
    rows_pos_counts(scores, families, "test")

    epoch = 120
    if args.by_best_checkpoint:
        epoch = select_best_epoch(csv, similarity, index, entity_column, scores, families, seeds)

    auc_and_increment_tables(
        csv, similarity, index, entity_column, scores, families, seeds, "valid", epoch
    )
    auc_and_increment_tables(
        csv, similarity, index, entity_column, scores, families, seeds, "test", epoch
    )

    scp2_epoch_trajectory(csv, similarity, index, entity_column, scores, seeds)


if __name__ == "__main__":
    main()
