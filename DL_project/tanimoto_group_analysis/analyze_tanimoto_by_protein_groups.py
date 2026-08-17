#!/usr/bin/env python3
# Tanimoto similarity of positive-interaction lipids WITHIN each protein group, sampled.
# Reports how chemically alike the lipids a group binds are, group by group.
import argparse
import os

import numpy as np
import pandas as pd


def sample_pairwise_tanimoto(matrix, positions, sample_size, seed):
    positions = np.asarray(positions)
    if len(positions) < 2:
        return {
            "encoded_lipid_count": len(positions),
            "tanimoto_mean": np.nan,
            "tanimoto_median": np.nan,
            "tanimoto_p10": np.nan,
            "tanimoto_p90": np.nan,
            "tanimoto_min": np.nan,
            "tanimoto_max": np.nan,
        }

    rng = np.random.default_rng(seed)
    chosen_count = min(sample_size, len(positions))
    chosen = rng.choice(positions, size=chosen_count, replace=False)
    submatrix = matrix[np.ix_(chosen, chosen)].astype(np.float32) / 255.0
    values = submatrix[np.triu_indices(chosen_count, k=1)]

    return {
        "encoded_lipid_count": len(positions),
        "tanimoto_mean": float(values.mean()),
        "tanimoto_median": float(np.median(values)),
        "tanimoto_p10": float(np.quantile(values, 0.10)),
        "tanimoto_p90": float(np.quantile(values, 0.90)),
        "tanimoto_min": float(values.min()),
        "tanimoto_max": float(values.max()),
    }


def summarize_groups(csv, matrix, batch, group_column, sample_size, seed, positives_only):
    if positives_only:
        csv = csv[csv["Interaction"] == 1]

    rows = []
    for group_name, group_df in csv.groupby(group_column, dropna=False):
        row_indexes = group_df.index.to_numpy()
        encoded_positions = np.flatnonzero(np.isin(batch, row_indexes))
        tanimoto_stats = sample_pairwise_tanimoto(
            matrix,
            encoded_positions,
            sample_size=sample_size,
            seed=seed,
        )
        label_counts = group_df["Interaction"].value_counts()

        rows.append({
            group_column: group_name,
            "row_count": len(group_df),
            "positive_count": int(label_counts.get(1, 0)),
            "negative_count": int(label_counts.get(0, 0)),
            "unique_lipid_count": int(group_df["Lipid"].nunique(dropna=True)),
            "unique_full_identity_count": int(group_df["FullIdentityOfLipid"].nunique(dropna=True)),
            **tanimoto_stats,
        })

    return pd.DataFrame(rows).sort_values(group_column)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize within-group Tanimoto similarity by protein domain and protein subgroup."
    )
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--csv", default="Processed_Negative_Interaction_Without_Duplicates.csv")
    parser.add_argument("--matrix", default="Total_tanimoto_matrix_uint8.npy")
    parser.add_argument("--batch", default="Total_multiple_lipid_batch.npy")
    parser.add_argument("--out-dir", default="tanimoto_group_analysis")
    parser.add_argument("--sample-size", type=int, default=400)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    csv_path = os.path.join(args.data_dir, args.csv)
    matrix_path = os.path.join(args.data_dir, args.matrix)
    batch_path = os.path.join(args.data_dir, args.batch)

    csv = pd.read_csv(csv_path)
    matrix = np.load(matrix_path, mmap_mode="r")
    batch = np.load(batch_path, mmap_mode="r")

    os.makedirs(args.out_dir, exist_ok=True)

    jobs = [
        ("protein_domains_all", "ProteinDomain", False),
        ("protein_domains_positive_only", "ProteinDomain", True),
        ("protein_subgroups_all", "LTPProtein", False),
        ("protein_subgroups_positive_only", "LTPProtein", True),
    ]

    for name, column, positives_only in jobs:
        summary = summarize_groups(
            csv,
            matrix,
            batch,
            group_column=column,
            sample_size=args.sample_size,
            seed=args.seed,
            positives_only=positives_only,
        )
        output_path = os.path.join(args.out_dir, f"{name}.csv")
        summary.to_csv(output_path, index=False)
        print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
