#!/usr/bin/env python3
# Pairwise Tanimoto similarity of positive-interaction lipids between SUBGROUPS of one
# protein domain. Same matrix and long-form outputs as the between-groups version.
import argparse
import os

import numpy as np
import pandas as pd


def subgroup_positions(csv, batch, protein_domain, positives_only):
    subset = csv[csv["ProteinDomain"] == protein_domain]
    if positives_only:
        subset = subset[subset["Interaction"] == 1]

    groups = {}
    for subgroup, subgroup_df in subset.groupby("LTPProtein", dropna=False):
        row_indexes = subgroup_df.index.to_numpy()
        positions = np.flatnonzero(np.isin(batch, row_indexes))
        groups[subgroup] = {
            "positions": positions,
            "row_count": len(subgroup_df),
            "positive_count": int((subgroup_df["Interaction"] == 1).sum()),
            "negative_count": int((subgroup_df["Interaction"] == 0).sum()),
            "unique_lipid_count": int(subgroup_df["Lipid"].nunique(dropna=True)),
            "unique_full_identity_count": int(subgroup_df["FullIdentityOfLipid"].nunique(dropna=True)),
        }
    return groups


def sample_positions(positions, sample_size, rng):
    if sample_size is None or len(positions) <= sample_size:
        return positions
    return rng.choice(positions, size=sample_size, replace=False)


def mean_tanimoto(matrix, positions_a, positions_b, block_size):
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
        description="Compute pairwise mean Tanimoto between protein subgroups inside one ProteinDomain."
    )
    parser.add_argument("--protein-domain", default="START")
    parser.add_argument("--include-negatives", action="store_true")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--csv", default="Processed_Negative_Interaction_Without_Duplicates.csv")
    parser.add_argument("--matrix", default="Total_tanimoto_matrix_uint8.npy")
    parser.add_argument("--batch", default="Total_multiple_lipid_batch.npy")
    parser.add_argument("--out-dir", default="tanimoto_group_analysis")
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    csv = pd.read_csv(os.path.join(args.data_dir, args.csv))
    matrix = np.load(os.path.join(args.data_dir, args.matrix), mmap_mode="r")
    batch = np.load(os.path.join(args.data_dir, args.batch), mmap_mode="r")
    rng = np.random.default_rng(args.seed)

    positives_only = not args.include_negatives
    groups = subgroup_positions(csv, batch, args.protein_domain, positives_only)
    subgroup_names = sorted(groups)
    sampled = {
        subgroup: sample_positions(groups[subgroup]["positions"], args.sample_size, rng)
        for subgroup in subgroup_names
    }

    long_rows = []
    matrix_rows = []
    for subgroup_a in subgroup_names:
        matrix_row = {"LTPProtein": subgroup_a}
        for subgroup_b in subgroup_names:
            value = mean_tanimoto(
                matrix,
                sampled[subgroup_a],
                sampled[subgroup_b],
                block_size=args.block_size,
            )
            matrix_row[subgroup_b] = value
            long_rows.append({
                "ProteinDomain": args.protein_domain,
                "subgroup_a": subgroup_a,
                "subgroup_b": subgroup_b,
                "mean_tanimoto": value,
                "encoded_lipids_a": len(groups[subgroup_a]["positions"]),
                "encoded_lipids_b": len(groups[subgroup_b]["positions"]),
                "sampled_encoded_lipids_a": len(sampled[subgroup_a]),
                "sampled_encoded_lipids_b": len(sampled[subgroup_b]),
                "row_count_a": groups[subgroup_a]["row_count"],
                "row_count_b": groups[subgroup_b]["row_count"],
                "positive_count_a": groups[subgroup_a]["positive_count"],
                "positive_count_b": groups[subgroup_b]["positive_count"],
                "negative_count_a": groups[subgroup_a]["negative_count"],
                "negative_count_b": groups[subgroup_b]["negative_count"],
                "unique_lipid_count_a": groups[subgroup_a]["unique_lipid_count"],
                "unique_lipid_count_b": groups[subgroup_b]["unique_lipid_count"],
                "unique_full_identity_count_a": groups[subgroup_a]["unique_full_identity_count"],
                "unique_full_identity_count_b": groups[subgroup_b]["unique_full_identity_count"],
            })
        matrix_rows.append(matrix_row)

    suffix = "positive_only" if positives_only else "all"
    safe_domain = args.protein_domain.replace("/", "-")
    out_prefix = f"{safe_domain}_subgroups_{suffix}_pairwise_tanimoto"
    os.makedirs(args.out_dir, exist_ok=True)
    long_path = os.path.join(args.out_dir, f"{out_prefix}_long.csv")
    matrix_path = os.path.join(args.out_dir, f"{out_prefix}_matrix.csv")

    pd.DataFrame(long_rows).to_csv(long_path, index=False)
    pd.DataFrame(matrix_rows).to_csv(matrix_path, index=False)
    print(f"wrote {long_path}")
    print(f"wrote {matrix_path}")


if __name__ == "__main__":
    main()
