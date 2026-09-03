#!/usr/bin/env python3
"""Rank unlabeled (Interaction=0) protein-lipid pairs by Kron-RLS out-of-sample score.

Reuses analysis/kronrls_baseline.py's per-(family, seed) cold-split fit exactly as
it evaluates test_auc (same lambda-grid selection by validation-block AUC), but
keeps the scored held-out pool instead of discarding it after computing AUC. Looping
--split_mode double over every family means every row in the table eventually gets
scored while its own family was held out of training -- an honest out-of-sample
score, not an in-sample fit that could just be memorizing the row.

A candidate's score is averaged across --seeds (a pair can land in the valid or the
test half of the held pool depending on the seed's random split_held_pairs draw;
both count, tagged separately for reference). Ranking, not classification: there is
no ground truth for which unlabeled pair is actually a false negative, so attribution
is gated by three independent, tunable strictness knobs rather than one fixed cutoff
-- default is deliberately conservative (few, high-confidence candidates), loosen
only deliberately:

  --positive_percentile (default 0.9): threshold = this percentile of the table's
      own known-positive scores in the same scored pools. 0.9 means "scores as high
      as the TOP 10% of real, confirmed positives" -- far stricter than "beats a
      typical positive" (percentile 0.5).
  --min_family_auc (default 0.65): a family's held-out test_auc (mean over seeds)
      below this excludes ALL its candidates outright, not just flags them -- a
      family near chance (~0.5, see per-family table below, e.g. CRAL-TRIO/
      IP_trans/START in this dataset) has no ranking signal, so any "high score"
      there is noise, not evidence.
  --min_seed_consistency (default 0.8): a pair must clear the score threshold in at
      least this fraction of the seeds it was scored under (not just on average) --
      guards against one lucky seed's fit inflating a single pair.

Treat the output as a prioritized list for follow-up (wet-lab or further PU-loss
weighting), never as verified labels -- run analysis/chemistry_null_model.py on any
shortlisted family before trusting it further, since a protein-blind lipid-Tanimoto
null can produce the same-looking ranking for the wrong (marginal, not learned-pair)
reason.

    python3 analysis/kronrls_false_negative_candidates.py \\
        --protein_kernel pocket_subset \\
        --protein_descriptor_names=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim \\
        --lipid_kernel tanimoto --lambda_grid 0.01,0.1,1,10,100 --top 50 --out candidates.csv
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import lipid_class_series  # noqa: E402
from training.pair_baseline_common import (  # noqa: E402
    aggregate_pair_labels,
    build_lipid_kernel,
    build_protein_kernel,
    raw_double_cold_pool,
    raw_single_cold_pool,
    split_held_pairs,
    two_step_kronrls,
)
from kronrls_baseline import (  # noqa: E402
    DEFAULT_FAMILIES,
    _parse_lambda_grid,
    _score_pool,
)


def fit_and_score_block(
    table: pd.DataFrame, family: str, seed: int, args: argparse.Namespace
) -> tuple[dict, pd.DataFrame]:
    """Same fit as kronrls_baseline.evaluate_block, but returns the scored held-out
    pool (valid + test, each tagged) alongside the summary row instead of discarding it."""
    if args.split_mode == "double":
        train_pool, held_pool, _ = raw_double_cold_pool(table, family, args.share)
    else:
        train_pool, held_pool = raw_single_cold_pool(table, family)
    valid_pool, test_pool = split_held_pairs(held_pool, seed)

    train_proteins = sorted(train_pool["LTPProtein"].unique())
    train_lipids = sorted(train_pool["FullIdentityOfLipid"].unique())
    all_proteins = sorted(
        set(train_proteins) | set(valid_pool["LTPProtein"]) | set(test_pool["LTPProtein"])
    )
    all_lipids = sorted(
        set(train_lipids)
        | set(valid_pool["FullIdentityOfLipid"])
        | set(test_pool["FullIdentityOfLipid"])
    )

    protein_kernel, protein_index = build_protein_kernel(
        args.protein_kernel, all_proteins, train_proteins,
        kernel_type=args.protein_kernel_type,
        descriptor_names=args.protein_descriptor_names,
        features_path=args.protein_features,
        kernel_path=args.protein_kernel_matrix,
        names_path=args.protein_kernel_names,
    )
    lipid_kernel, lipid_index = build_lipid_kernel(
        args.lipid_kernel, table, all_lipids, train_lipids,
        kernel_type=args.lipid_kernel_type,
        descriptor_names=args.lipid_descriptor_names,
        features_path=args.lipid_features,
        kernel_path=args.lipid_kernel_matrix,
        names_path=args.lipid_kernel_names,
    )

    labels = aggregate_pair_labels(
        train_pool, lipid_class_targets=args.lipid_class_targets
    ).reindex(index=train_proteins, columns=train_lipids)
    kp_train = protein_kernel[
        np.ix_(
            [protein_index[name] for name in train_proteins],
            [protein_index[name] for name in train_proteins],
        )
    ]
    kl_train = lipid_kernel[
        np.ix_(
            [lipid_index[name] for name in train_lipids],
            [lipid_index[name] for name in train_lipids],
        )
    ]

    grid = args.lambda_grid or [(args.protein_lambda, args.lipid_lambda)]
    best = None
    for protein_lambda, lipid_lambda in grid:
        coefficients = two_step_kronrls(
            kp_train, kl_train, labels.to_numpy(), protein_lambda, lipid_lambda
        )
        valid_auc, valid_scored = _score_pool(
            valid_pool, coefficients, protein_kernel, protein_index,
            lipid_kernel, lipid_index, train_proteins, train_lipids,
        )
        candidate = (valid_auc, protein_lambda, lipid_lambda, coefficients, valid_scored)
        if best is None or (not np.isnan(valid_auc) and (np.isnan(best[0]) or valid_auc > best[0])):
            best = candidate
    valid_auc, protein_lambda, lipid_lambda, coefficients, valid_scored = best

    test_auc, test_scored = _score_pool(
        test_pool, coefficients, protein_kernel, protein_index,
        lipid_kernel, lipid_index, train_proteins, train_lipids,
    )

    scored = pd.concat(
        [valid_scored.assign(block="valid"), test_scored.assign(block="test")],
        ignore_index=True,
    )
    scored["family"] = family
    scored["seed"] = seed

    summary = {
        "family": family, "seed": seed,
        "protein_lambda": protein_lambda, "lipid_lambda": lipid_lambda,
        "valid_auc": valid_auc, "test_auc": test_auc,
    }
    return summary, scored


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--csv", default=None)
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--split_mode", default="double", choices=("single", "double"))
    parser.add_argument("--share", type=float, default=0.8)
    parser.add_argument("--lipid_class_targets", action="store_true")
    parser.add_argument("--protein_kernel", default="pocket13",
                         choices=("pocket13", "pocket23", "pocket_subset", "custom_features", "custom_kernel"))
    parser.add_argument("--protein_kernel_type", default="rbf", choices=("rbf", "linear", "cosine"))
    parser.add_argument("--protein_descriptor_names",
                         type=lambda text: [n for n in text.split(",") if n], default=None)
    parser.add_argument("--protein_features")
    parser.add_argument("--protein_kernel_matrix")
    parser.add_argument("--protein_kernel_names")
    parser.add_argument("--lipid_kernel", default="tanimoto",
                         choices=("tanimoto", "explicit", "explicit_subset", "custom_features", "custom_kernel"))
    parser.add_argument("--lipid_kernel_type", default="rbf", choices=("rbf", "linear", "cosine"))
    parser.add_argument("--lipid_descriptor_names",
                         type=lambda text: [n for n in text.split(",") if n], default=None)
    parser.add_argument("--lipid_features")
    parser.add_argument("--lipid_kernel_matrix")
    parser.add_argument("--lipid_kernel_names")
    parser.add_argument("--protein_lambda", type=float, default=1.0)
    parser.add_argument("--lipid_lambda", type=float, default=1.0)
    parser.add_argument("--lambda_grid", type=_parse_lambda_grid, default=None)
    parser.add_argument("--top", type=int, default=50, help="how many top candidates to print")
    parser.add_argument("--out", help="write the full scored unlabeled pool (all candidates) to this CSV")
    parser.add_argument(
        "--positive_percentile", type=float, default=0.9,
        help="threshold = this percentile of known-positive scores; higher = stricter (default 0.9)",
    )
    parser.add_argument(
        "--min_family_auc", type=float, default=0.65,
        help="families with mean held-out test_auc below this contribute NO candidates (default 0.65)",
    )
    parser.add_argument(
        "--min_seed_consistency", type=float, default=0.8,
        help="fraction of scored seeds a pair must clear the threshold in (default 0.8)",
    )
    args = parser.parse_args()

    csv_path = args.csv or interaction_csv_path(os.path.join(PROJECT_ROOT, "data"))
    table = pd.read_csv(csv_path)
    table["pair_id"] = table.index.astype(int)

    families = [name for name in args.families.split(",") if name]
    seeds = [int(value) for value in args.seeds.split(",")]

    summaries = []
    scored_blocks = []
    for family in families:
        for seed in seeds:
            summary, scored = fit_and_score_block(table, family, seed, args)
            summaries.append(summary)
            scored_blocks.append(scored)

    summary_df = pd.DataFrame(summaries)
    family_auc = summary_df.groupby("family")["test_auc"].mean()

    all_scored = pd.concat(scored_blocks, ignore_index=True)

    # Threshold is set from known positives ONLY -- never from the candidate
    # (Interaction=0) rows themselves, so tightening --positive_percentile can only
    # make attribution stricter, never data-snoop the answer it is trying to find.
    positive_scores = all_scored.loc[all_scored["Interaction"] == 1, "_score"]
    threshold = positive_scores.quantile(args.positive_percentile)
    all_scored["_clears_threshold"] = all_scored["_score"] >= threshold

    # One row per (protein, lipid): how many of the --seeds runs scored it, and in
    # how many of those it individually cleared the threshold (seed_consistency) --
    # a pair always keeps the same family, so grouping on it too is safe.
    per_pair = (
        all_scored.groupby(["LTPProtein", "FullIdentityOfLipid", "family", "Interaction"])
        .agg(mean_score=("_score", "mean"),
             n_seeds=("_score", "count"),
             n_seeds_pass=("_clears_threshold", "sum"))
        .reset_index()
    )
    per_pair["seed_consistency"] = per_pair["n_seeds_pass"] / per_pair["n_seeds"]
    per_pair["family_test_auc"] = per_pair["family"].map(family_auc)

    positives = per_pair[per_pair["Interaction"] == 1]
    candidates = per_pair[per_pair["Interaction"] == 0].copy()

    # The three gates, applied together -- all three must pass. Relaxing any one
    # (lower --positive_percentile / --min_family_auc / --min_seed_consistency)
    # is the deliberate way to loosen this; the defaults are the conservative end.
    candidates["family_reliable"] = candidates["family_test_auc"] >= args.min_family_auc
    candidates["score_high_enough"] = candidates["mean_score"] >= threshold
    candidates["seed_consistent"] = candidates["seed_consistency"] >= args.min_seed_consistency
    candidates["attributed_false_negative"] = (
        candidates["family_reliable"]
        & candidates["score_high_enough"]
        & candidates["seed_consistent"]
    )
    attributed = candidates[candidates["attributed_false_negative"]]
    share_of_pool = len(attributed) / len(candidates) if len(candidates) else float("nan")
    share_of_reliable_pool = (
        attributed.shape[0] / candidates[candidates["family_reliable"]].shape[0]
        if candidates["family_reliable"].any() else float("nan")
    )

    print(f"=== Kron-RLS false-negative candidates ({args.split_mode}, "
          f"protein={args.protein_kernel}/{args.protein_kernel_type}, "
          f"lipid={args.lipid_kernel}/{args.lipid_kernel_type}) ===\n")
    print("per-family held-out test AUC (families below --min_family_auc contribute nothing):")
    print(family_auc.round(3).to_string())
    print()
    print(f"attribution gates: score >= P{args.positive_percentile:.0%} of known positives "
          f"(threshold={threshold:.4f}), family test_auc >= {args.min_family_auc}, "
          f"seed_consistency >= {args.min_seed_consistency}")
    print()
    print(f"known positives scored (threshold source):              {len(positives)}")
    print(f"unlabeled pairs scored (full candidate pool):            {len(candidates)}")
    print(f"  -- from families clearing --min_family_auc:            "
          f"{int(candidates['family_reliable'].sum())}")
    print(f"attributed false-negative candidates (all 3 gates pass): {len(attributed)}")
    print(f"  share of full scored unlabeled pool:                   {share_of_pool:.2%}")
    print(f"  share of the reliable-family subset:                   {share_of_reliable_pool:.2%}")
    print()

    per_family = (
        candidates.groupby("family")
        .agg(n_candidates=("attributed_false_negative", "size"),
             n_attributed=("attributed_false_negative", "sum"),
             test_auc=("family_test_auc", "first"))
        .assign(share=lambda d: d["n_attributed"] / d["n_candidates"])
        .sort_values("share", ascending=False)
    )
    print("per family: candidates scored, attributed count/share, held-out reliability:")
    print(per_family.round(3).to_string())
    print()

    top = attributed.sort_values("mean_score", ascending=False).head(args.top)
    cols = ["LTPProtein", "FullIdentityOfLipid", "family", "family_test_auc",
            "mean_score", "seed_consistency", "n_seeds"]
    print(f"top {min(args.top, len(attributed))} attributed candidates "
          f"(of {len(attributed)} passing all gates):")
    print(top[cols].to_string(index=False) if len(top) else "(none pass all three gates)")

    if args.out:
        candidates.sort_values(
            ["attributed_false_negative", "mean_score"], ascending=[False, False]
        ).to_csv(args.out, index=False)
        print(f"\nwrote all {len(candidates)} scored candidates "
              f"({len(attributed)} attributed) to {args.out}")


if __name__ == "__main__":
    main()
