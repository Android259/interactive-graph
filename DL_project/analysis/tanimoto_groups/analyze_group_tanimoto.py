#!/usr/bin/env python3
"""Tanimoto similarity of groups of interactions, two different questions, one shared
loader (`load_candidate_tanimoto`, the only thing the two former separate scripts --
analyze_pairwise_tanimoto.py and analyze_tanimoto_by_protein_groups.py -- had in
common; everything past that point answers a different statistic over a different
shape, so this is one file with two modes, not one merged function).

MODE `between` (default) -- BETWEEN-group similarity: a group x group matrix, mean
Tanimoto over every cross pair of two groups' candidates (or a --sample-size draw of
them). Printed to the terminal, nothing written. Two readings, selected by
--restrict-domain:

    (default) between every pair of --group-column values (ProteinDomain by default)
        -- "if a whole family is held out, how close is its chemistry to a DIFFERENT
        family's?"
    --restrict-domain=NAME  between the LTPProtein subgroups inside one ProteinDomain
        -- "if one protein of a family is held out while its relatives stay in
        training, how close is its chemistry to each sibling's?"

MODE `within` -- WITHIN-group similarity: for each group on its own, the spread
(mean/median/p10/p90/min/max) of Tanimoto between that one group's OWN candidates --
"how chemically alike are the lipids this group binds, to each other". Always runs all
four jobs (ProteinDomain/LTPProtein x all-rows/positives-only) and writes one CSV per
job under --out-dir.

NEITHER mode is the isolation formula in analysis/coldsplit_geometry.py. That formula
is MAX, not mean, and one-sided: mean over a HELD-OUT block's structures of the BEST
similarity to a structure that STAYS in training -- it answers "does training still
have something close to what was excluded", for one designated held/kept split. Both
modes here answer a different question with a different statistic and no held/kept
split at all: `between` is the full matrix of every named group against every other
named group (not one block against "everything else"), and `within` has no second
group at all, only one group's own internal spread. A worked contrast: if a family's
candidates are tightly clustered around one of three sub-clusters, `within` reports a
WIDE spread (its own three sub-clusters sit far from each other), `between` can still
report a HIGH mean against a neighbouring family (most cross pairs land near the
closest sub-cluster), while coldsplit_geometry.isolation on the same family would
report a value close to whichever of this family's structures has the single closest
relative anywhere in training -- three numbers, three different questions, none of
them redundant with either of the others.

Positions compared are the candidates of positive-interaction rows only, unless
--include-negatives (mode `between`) / unless all-rows is the job (mode `within`,
which always runs both). Read from the compact Tanimoto artifacts
(preprocessing/build_tanimoto_compact.py) -- no RDKit, no model.

    python3 analysis/tanimoto_groups/analyze_group_tanimoto.py between
    python3 analysis/tanimoto_groups/analyze_group_tanimoto.py between --restrict-domain=START
    python3 analysis/tanimoto_groups/analyze_group_tanimoto.py between --group-column=LTPProtein
    python3 analysis/tanimoto_groups/analyze_group_tanimoto.py within
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dataloader.dataset_source import INTERACTION_CSV  # noqa: E402
from dataloader.tensors_reading.tanimoto_compact_tensors_reader import load_compact  # noqa: E402


def load_candidate_tanimoto(data_dir, csv_path, isomeric):
    """(per-candidate similarity view, candidate -> table row) from the compact artifacts.

    Shared by both modes: one compact-artifact read regardless of which question is
    then asked of it.
    """
    compact = load_compact(data_dir, source_csv=csv_path, isomeric=isomeric)
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts missing or older than the table; rebuild with "
            "python3 preprocessing/build_tanimoto_compact.py" + (" --isomeric" if isomeric else "")
        )
    return compact.candidate_view(), compact.row_ids


# ======================================================================== mode `between`


def group_positions(csv, batch, group_column, restrict_domain, include_negatives):
    """name -> {positions into `batch`, and the row/lipid counts behind them}.

    `restrict_domain`, when given, keeps only ProteinDomain == restrict_domain before
    grouping by `group_column` -- grouping an already-restricted table by LTPProtein is
    exactly "subgroups inside one domain"; grouping the unrestricted table by
    ProteinDomain (the default) is "between domains". One function either way: which
    rows are IN SCOPE and which column SPLITS them are orthogonal questions.
    """
    subset = csv
    if restrict_domain is not None:
        subset = subset[subset["ProteinDomain"] == restrict_domain]
    if not include_negatives:
        subset = subset[subset["Interaction"] == 1]

    groups = {}
    for name, group_df in subset.groupby(group_column, dropna=False):
        row_indexes = group_df.index.to_numpy()
        positions = np.flatnonzero(np.isin(batch, row_indexes))
        groups[name] = {
            "positions": positions,
            "row_count": len(group_df),
            "positive_count": int((group_df["Interaction"] == 1).sum()),
            "negative_count": int((group_df["Interaction"] == 0).sum()),
            "unique_lipid_count": int(group_df["Lipid"].nunique(dropna=True)),
            "unique_full_identity_count": int(group_df["FullIdentityOfLipid"].nunique(dropna=True)),
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


def print_between_report(group_column, label, groups, sampled, pairwise, suffix):
    group_names = sorted(groups)
    print(f"{label}, {suffix} interactions, {len(group_names)} {group_column} groups\n")

    # Per-group counts, once each -- a CSV would cross-join these onto every pairwise
    # row for spreadsheet convenience; on a terminal that is just noise.
    name_width = max((len(name) for name in group_names), default=12)
    header = (
        f"{group_column:{name_width}}  {'rows':>5}  {'pos':>5}  {'neg':>5}  "
        f"{'lipids':>7}  {'identities':>10}  {'sampled':>7}"
    )
    print(header)
    print("-" * len(header))
    for name in group_names:
        group = groups[name]
        print(
            f"{name:{name_width}}  {group['row_count']:5d}  {group['positive_count']:5d}  "
            f"{group['negative_count']:5d}  {group['unique_lipid_count']:7d}  "
            f"{group['unique_full_identity_count']:10d}  {len(sampled[name]):7d}"
        )

    print(f"\nmean Tanimoto (rows/cols = {group_column}):\n")
    col_width = max(name_width, 6)
    print(" " * name_width + "".join(f"  {name:>{col_width}}" for name in group_names))
    for name_a in group_names:
        row = f"{name_a:{name_width}}"
        for name_b in group_names:
            value = pairwise[(name_a, name_b)]
            row += f"  {value:{col_width}.3f}" if not np.isnan(value) else f"  {'--':>{col_width}}"
        print(row)


def run_between(args):
    group_column = args.group_column or ("LTPProtein" if args.restrict_domain else "ProteinDomain")

    csv = pd.read_csv(os.path.join(args.data_dir, args.csv))
    matrix, batch = load_candidate_tanimoto(args.data_dir, os.path.join(args.data_dir, args.csv), args.isomeric)
    rng = np.random.default_rng(args.seed)

    groups = group_positions(csv, batch, group_column, args.restrict_domain, args.include_negatives)
    group_names = sorted(groups)
    sampled = {
        name: sample_positions(groups[name]["positions"], args.sample_size, rng)
        for name in group_names
    }
    pairwise = {
        (name_a, name_b): mean_tanimoto(matrix, sampled[name_a], sampled[name_b], args.block_size)
        for name_a in group_names
        for name_b in group_names
    }

    label = f"{args.restrict_domain} subgroups" if args.restrict_domain else group_column
    suffix = "positive_only" if not args.include_negatives else "all"
    print_between_report(group_column, label, groups, sampled, pairwise, suffix)


# ========================================================================= mode `within`


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


def run_within(args):
    csv_path = os.path.join(args.data_dir, args.csv)
    csv = pd.read_csv(csv_path)
    matrix, batch = load_candidate_tanimoto(args.data_dir, csv_path, args.isomeric)

    os.makedirs(args.out_dir, exist_ok=True)

    jobs = [
        ("protein_domains_all", "ProteinDomain", False),
        ("protein_domains_positive_only", "ProteinDomain", True),
        ("protein_subgroups_all", "LTPProtein", False),
        ("protein_subgroups_positive_only", "LTPProtein", True),
    ]

    for name, column, positives_only in jobs:
        summary = summarize_groups(
            csv, matrix, batch, group_column=column,
            sample_size=args.within_sample_size, seed=args.seed,
            positives_only=positives_only,
        )
        output_path = os.path.join(args.out_dir, f"{name}.csv")
        summary.to_csv(output_path, index=False)
        print(f"wrote {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    modes = parser.add_subparsers(dest="mode", required=True)

    between = modes.add_parser("between", help="group x group mean cross-Tanimoto, printed")
    between.add_argument(
        "--restrict-domain", default=None,
        help="ProteinDomain to restrict to; with this set, --group-column defaults to "
             "LTPProtein (subgroups inside the domain) instead of ProteinDomain",
    )
    between.add_argument(
        "--group-column", default=None,
        help="column whose values become the compared groups "
             "(default: LTPProtein with --restrict-domain, ProteinDomain without it)",
    )
    between.add_argument("--include-negatives", action="store_true")
    between.add_argument("--sample-size", type=int, default=None)
    between.add_argument("--block-size", type=int, default=512)

    within = modes.add_parser("within", help="per-group own-candidate Tanimoto spread, written as CSV")
    within.add_argument("--out-dir", default="analysis/tanimoto_groups")
    within.add_argument("--within-sample-size", type=int, default=400)

    for sub in (between, within):
        sub.add_argument("--data-dir", default="data")
        sub.add_argument("--csv", default=INTERACTION_CSV)
        sub.add_argument("--isomeric", action="store_true",
                         help="use the isomeric compact artifacts (Tanimoto_compact_isomeric_*)")
        sub.add_argument("--seed", type=int, default=0)

    args = parser.parse_args()
    {"between": run_between, "within": run_within}[args.mode](args)


if __name__ == "__main__":
    main()
