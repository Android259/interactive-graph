#!/usr/bin/env python3
import argparse
import os

import numpy as np
import pandas as pd


def group_encoded_positions(csv, batch, group_column):
    positive_csv = csv[csv["Interaction"] == 1]
    groups = {}

    for group_name, group_df in positive_csv.groupby(group_column, dropna=False):
        row_indexes = group_df.index.to_numpy()
        positions = np.flatnonzero(np.isin(batch, row_indexes))
        groups[group_name] = {
            "positions": positions,
            "positive_rows": len(group_df),
            "unique_lipids": group_df["Lipid"].nunique(dropna=True),
            "unique_full_identities": group_df["FullIdentityOfLipid"].nunique(dropna=True),
        }

    return groups


def sample_positions(positions, sample_size, rng):
    if sample_size is None or len(positions) <= sample_size:
        return positions
    return rng.choice(positions, size=sample_size, replace=False)


def mean_cross_tanimoto(matrix, positions_a, positions_b, block_size):
    if len(positions_a) == 0 or len(positions_b) == 0:
        return np.nan

    total = 0.0
    count = 0
    for start in range(0, len(positions_a), block_size):
        block_a = positions_a[start:start + block_size]
        values = matrix[np.ix_(block_a, positions_b)].astype(np.float32) / 255.0
        total += float(values.sum())
        count += values.size

    return total / count


def main():
    parser = argparse.ArgumentParser(
        description="Compute positive-only mean Tanimoto similarity between every pair of protein groups."
    )
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--csv", default="Processed_Negative_Interaction_Without_Duplicates.csv")
    parser.add_argument("--matrix", default="Total_tanimoto_matrix_uint8.npy")
    parser.add_argument("--batch", default="Total_multiple_lipid_batch.npy")
    parser.add_argument("--group-column", default="ProteinDomain")
    parser.add_argument("--out-dir", default="tanimoto_group_analysis")
    parser.add_argument("--out-name", default=None)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    csv = pd.read_csv(os.path.join(args.data_dir, args.csv))
    matrix = np.load(os.path.join(args.data_dir, args.matrix), mmap_mode="r")
    batch = np.load(os.path.join(args.data_dir, args.batch), mmap_mode="r")
    rng = np.random.default_rng(args.seed)

    groups = group_encoded_positions(csv, batch, args.group_column)
    group_names = sorted(groups)
    sampled_positions = {
        group_name: sample_positions(groups[group_name]["positions"], args.sample_size, rng)
        for group_name in group_names
    }

    rows = []
    matrix_rows = []
    for group_a in group_names:
        matrix_row = {args.group_column: group_a}
        for group_b in group_names:
            mean_tanimoto = mean_cross_tanimoto(
                matrix,
                sampled_positions[group_a],
                sampled_positions[group_b],
                block_size=args.block_size,
            )
            matrix_row[group_b] = mean_tanimoto

            rows.append({
                "group_a": group_a,
                "group_b": group_b,
                "mean_tanimoto": mean_tanimoto,
                "encoded_lipids_a": len(groups[group_a]["positions"]),
                "encoded_lipids_b": len(groups[group_b]["positions"]),
                "sampled_encoded_lipids_a": len(sampled_positions[group_a]),
                "sampled_encoded_lipids_b": len(sampled_positions[group_b]),
                "positive_rows_a": groups[group_a]["positive_rows"],
                "positive_rows_b": groups[group_b]["positive_rows"],
                "unique_lipids_a": groups[group_a]["unique_lipids"],
                "unique_lipids_b": groups[group_b]["unique_lipids"],
                "unique_full_identities_a": groups[group_a]["unique_full_identities"],
                "unique_full_identities_b": groups[group_b]["unique_full_identities"],
            })
        matrix_rows.append(matrix_row)

    os.makedirs(args.out_dir, exist_ok=True)
    out_prefix = args.out_name or f"{args.group_column}_positive_only_pairwise_tanimoto"
    long_path = os.path.join(args.out_dir, f"{out_prefix}_long.csv")
    matrix_path = os.path.join(args.out_dir, f"{out_prefix}_matrix.csv")

    pd.DataFrame(rows).to_csv(long_path, index=False)
    pd.DataFrame(matrix_rows).to_csv(matrix_path, index=False)

    print(f"wrote {long_path}")
    print(f"wrote {matrix_path}")


if __name__ == "__main__":
    main()
