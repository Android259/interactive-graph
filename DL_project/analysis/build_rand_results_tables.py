#!/usr/bin/env python3
"""Rebuilds the four tables of files/results_section.tex from a checkpoint-scores CSV.

files/results_section.tex reports bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120
(lipid_random_choice on) over five seeds. This script is the single place that turns a
scores CSV from analysis/checkpoint_scores.py into the four tables: BA at the checkpoint
epoch (from metrics_summary.csv directly, since only the five dynamics milestones --
1, 10, 49, 51, 120 -- have saved weights, and the checkpoint epoch is usually none of
them), AUC pooled/in-protein against the chemistry null model at epoch 120, the in-sample
increment at epoch 120, and the scp2 net_prot-chem_prot trajectory over all five epochs.

Reads only.

    scripts/env.sh python3 analysis/build_rand_results_tables.py \
        --scores /path/to/rand_scores_5seed.csv --label bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from analysis.chemistry_null_model import DEFAULT_FAMILIES, species_similarity  # noqa: E402
from analysis.interaction_increment import increment_table  # noqa: E402
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


def auc_and_increment_tables(csv, similarity, index, scores, families, seeds, split):
    table = increment_table(
        csv, similarity, index, scores, families=families, seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split=split, epochs=[120],
    )
    print(f"=== AUC + increment, {split} block, epoch 120, mean over {len(seeds)} seeds ===")
    per_family = table.groupby("fam")[
        ["chem", "net", "chem_prot", "net_prot", "increment", "increment_prot"]
    ].mean()
    print(per_family.round(3).to_string())
    print()
    return table


def scp2_epoch_trajectory(csv, similarity, index, scores, seeds):
    table = increment_table(
        csv, similarity, index, scores, families=["scp2"], seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split="valid", epochs=None,
    )
    table_test = increment_table(
        csv, similarity, index, scores, families=["scp2"], seeds=seeds,
        neighbours=15, share=0.8, ratio=2, split="test", epochs=None,
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
    parser.add_argument("--scores", required=True, help="CSV from analysis/checkpoint_scores.py")
    parser.add_argument("--label", required=True)
    parser.add_argument("--metrics-csv", default=os.path.join(PROJECT_ROOT, "metrics_summary.csv"))
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    args = parser.parse_args()

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]

    ba_table(args.metrics_csv, args.label, families, seeds)

    csv = pd.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    similarity, index = species_similarity(csv, os.path.join(PROJECT_ROOT, "data"))
    scores = pd.read_csv(args.scores)

    rows_pos_counts(scores, families, "valid")
    rows_pos_counts(scores, families, "test")

    auc_and_increment_tables(csv, similarity, index, scores, families, seeds, "valid")
    auc_and_increment_tables(csv, similarity, index, scores, families, seeds, "test")

    scp2_epoch_trajectory(csv, similarity, index, scores, seeds)


if __name__ == "__main__":
    main()
