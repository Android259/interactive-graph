#!/usr/bin/env python3
"""A row-based gradient-boosting baseline over protein x lipid descriptor pairs.

The other two non-neural baselines are matrix-completion methods (analysis/
kronrls_baseline.py's closed-form Kron-RLS) or pure lookups (analysis/null_model.py):
both need the training rectangle complete or a class prior, and neither can weight
positive cells against negative ones (kronrls_baseline.py's own docstring works
through why Kron-RLS's closed form structurally cannot -- Y enters its objective only
linearly, so no per-cell weight has anywhere to attach). This script is the other
kind of baseline: an ordinary supervised ROW classifier,
sklearn.ensemble.HistGradientBoostingClassifier, one row per (protein, lipid) pair,
features = protein_pocket_features(protein) concatenated with
explicit_lipid_features(lipid) (both training/pair_baseline_common.py, the same
descriptor sets Kron-RLS's pocket_subset/explicit kernels use, so the two baselines
are feature-matched). Being row-based rather than matrix-completion, it has none of
Kron-RLS's constraints:

  - Real class weighting. --class_weight=balanced goes straight into
    HistGradientBoostingClassifier's own sample-weighting, not a target-value
    rescaling trick -- there is a genuine per-cell loss weight here because this
    model actually has a per-row residual to attach one to.
  - Train MAY be subsampled. aggregate_pair_labels' "every train cell present" rule
    does not apply to a row classifier; --train_negatives_per_positive can (but need
    not) match the network's own --negatives_per_positive=2 training regime.
  - Generalizes to a novel lipid through its FEATURES, not its identity: a query
    lipid never seen in training just needs its own explicit_lipid_features row,
    exactly the --lipid_coldsplit scenario (known protein family, unseen lipid) this
    project's baselines are built to answer.

Same split/evaluation infrastructure as kronrls_baseline.py: --split_mode
{single,double,lipid_coldsplit} (training.pair_baseline_common.cold_split_pools),
valid/test rescored at --eval_negatives_per_positive (training.pair_baseline_common.
balance_pool_negatives, matching the network's own evaluation pool -- see
kronrls_baseline.py's module docstring for why the raw held-out block's positive rate
is the wrong bar), and threshold/BA/F1 via best_threshold_for_metric/
binary_confusion_metrics (fit on valid only, applied unchanged to test).

    python3 analysis/gbm_baseline.py
    python3 analysis/gbm_baseline.py --split_mode lipid_coldsplit \\
        --families=sphingolipids,phosphorus_free,anionic,choline \\
        --class_weight balanced --max_depth 4 --max_iter 300 \\
        --threshold_metric f1

Reads only (pocket graphs + the interaction table). Fits sklearn models in memory
each run; writes nothing unless --out is given.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dataloader.chemistry_prior import null_scores, null_scores_leave_one_row_out  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS, lipid_class_series  # noqa: E402
from null_model import per_lipid_auc, per_pair_auc, per_protein_auc  # noqa: E402
from training.pair_baseline_common import (  # noqa: E402
    auc_p_vs_u,
    balance_pool_negatives,
    best_threshold_for_metric,
    binary_confusion_metrics,
    cold_split_pools,
    explicit_lipid_features,
    protein_pocket_features,
    species_headgroup_tanimoto_similarity,
    species_tanimoto_similarity,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
DEFAULT_LIPID_COLDSPLIT_GROUPS = tuple(LIPID_COLDSPLIT_SETS.keys())
DEFAULT_NEIGHBOURS = 15


def build_feature_tables(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Protein and lipid feature tables, built once over the whole interaction table.

    Fixed columns regardless of which pool (train/valid/test) later indexes into
    them, so a held-out lipid's row is just another lookup, never a retrain of the
    feature space -- the mechanism that lets this model score a genuinely novel
    lipid at all.
    """
    proteins = sorted(table["LTPProtein"].unique())
    protein_features = protein_pocket_features(proteins).add_prefix("protein__")
    lipid_features = explicit_lipid_features(table).add_prefix("lipid__")
    return protein_features, lipid_features


def build_similarity(table: pd.DataFrame, kind: str) -> tuple[np.ndarray, dict[str, int]] | None:
    """Species x species lipid similarity for --lipid_similarity_feature, or None."""
    if kind == "none":
        return None
    if kind == "tanimoto":
        return species_tanimoto_similarity(table)
    if kind == "tanimoto_headgroup":
        return species_headgroup_tanimoto_similarity(table)
    raise ValueError(f"unknown lipid_similarity_feature {kind!r}")


def similarity_feature_column(
    pool: pd.DataFrame,
    train_pool: pd.DataFrame,
    similarity: tuple[np.ndarray, dict[str, int]],
    neighbours: int,
    is_train: bool,
) -> pd.DataFrame:
    """dataloader.chemistry_prior's k-NN similarity-weighted train positive rate,
    as one more feature column -- the SAME score analysis/lipid_coldsplit_null_
    model.py's "lipid_only" competitor reports standalone, fed in here instead so the
    model can learn how much to trust it against the structural descriptors rather
    than being compared to it after the fact.

    `is_train` selects the leak-safe variant: every train row's own species IS in
    the train reference set with similarity 1.0 to itself
    (null_scores_leave_one_row_out's own docstring), so scoring train against plain
    `null_scores(train_pool, train_pool[...], ...)` would partly score each row
    against its own label. valid/test rows are never in `train_pool`, so the plain
    `null_scores(train_pool, pool[...], ...)` is exact for them.
    """
    matrix, index = similarity
    if is_train:
        scores = null_scores_leave_one_row_out(train_pool, matrix, index, neighbours)
    else:
        scores = null_scores(train_pool, pool["FullIdentityOfLipid"], matrix, index, neighbours)
    return pd.DataFrame({"lipid__similarity_score": scores})


def row_features(
    pool: pd.DataFrame,
    protein_features: pd.DataFrame,
    lipid_features: pd.DataFrame,
    similarity_column: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """One feature row per (protein, lipid) pair in `pool`, index-aligned to it."""
    proteins = protein_features.loc[pool["LTPProtein"]].reset_index(drop=True)
    lipids = lipid_features.loc[pool["FullIdentityOfLipid"]].reset_index(drop=True)
    parts = [proteins, lipids]
    if similarity_column is not None:
        parts.append(similarity_column.reset_index(drop=True))
    return pd.concat(parts, axis=1)


def evaluate_block(
    table: pd.DataFrame,
    family: str,
    seed: int,
    args: argparse.Namespace,
    protein_features: pd.DataFrame,
    lipid_features: pd.DataFrame,
    similarity: tuple[np.ndarray, dict[str, int]] | None,
) -> dict:
    """Fit and score one (family, seed) cold-split block."""
    train_pool, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share
    )
    train_pool = balance_pool_negatives(train_pool, seed, args.train_negatives_per_positive)
    valid_pool = balance_pool_negatives(valid_pool, seed, args.eval_negatives_per_positive)
    test_pool = balance_pool_negatives(test_pool, seed, args.eval_negatives_per_positive)

    train_similarity_column = valid_similarity_column = test_similarity_column = None
    if similarity is not None:
        train_similarity_column = similarity_feature_column(
            train_pool, train_pool, similarity, args.similarity_neighbours, is_train=True
        )
        valid_similarity_column = similarity_feature_column(
            valid_pool, train_pool, similarity, args.similarity_neighbours, is_train=False
        )
        test_similarity_column = similarity_feature_column(
            test_pool, train_pool, similarity, args.similarity_neighbours, is_train=False
        )

    x_train = row_features(train_pool, protein_features, lipid_features, train_similarity_column)
    y_train = train_pool["Interaction"].to_numpy()
    x_valid = row_features(valid_pool, protein_features, lipid_features, valid_similarity_column)
    y_valid = valid_pool["Interaction"].to_numpy()
    x_test = row_features(test_pool, protein_features, lipid_features, test_similarity_column)
    y_test = test_pool["Interaction"].to_numpy()

    model = HistGradientBoostingClassifier(
        learning_rate=args.learning_rate,
        max_iter=args.max_iter,
        max_depth=args.max_depth,
        max_leaf_nodes=args.max_leaf_nodes,
        l2_regularization=args.l2_regularization,
        min_samples_leaf=args.min_samples_leaf,
        class_weight=None if args.class_weight == "none" else args.class_weight,
        early_stopping=True,
        random_state=seed,
    )
    # Early stopping watches THIS run's own valid pool -- never test -- same
    # checkpoint-selection role as the network's own valid-based model selection.
    model.fit(x_train, y_train, X_val=x_valid, y_val=y_valid)

    valid_scores = model.predict_proba(x_valid)[:, 1]
    test_scores = model.predict_proba(x_test)[:, 1]

    threshold_metric = "balanced_accuracy" if args.threshold_metric == "ba" else "F1"
    threshold, _ = best_threshold_for_metric(y_valid, valid_scores, metric=threshold_metric)
    valid_metrics = binary_confusion_metrics(y_valid, valid_scores, threshold)
    test_metrics = binary_confusion_metrics(y_test, test_scores, threshold)

    valid_auc = auc_p_vs_u(y_valid, valid_scores)
    test_auc = auc_p_vs_u(y_test, test_scores)

    test_scored = test_pool.assign(_score=test_scores)
    test_scored = test_scored.assign(lipid_class=lipid_class_series(test_scored))
    protein_auc, n_proteins = per_protein_auc(test_scored, test_scored["_score"].to_numpy())
    lipid_auc, n_lipid_classes = per_lipid_auc(test_scored, test_scored["_score"].to_numpy())
    pair_auc = per_pair_auc(test_scored, test_scored["_score"].to_numpy())
    n_pair_groups = int(test_scored["lipid_class"].nunique())

    return {
        "family": family,
        "seed": seed,
        "threshold": threshold,
        "valid_ba": valid_metrics["balanced_accuracy"],
        "valid_f1": valid_metrics["F1"],
        "test_ba": test_metrics["balanced_accuracy"],
        "test_f1": test_metrics["F1"],
        "test_sensitivity": test_metrics["sensitivity"],
        "test_specificity": test_metrics["specificity"],
        "valid_auc": valid_auc,
        "test_auc": test_auc,
        "pair_auc": pair_auc,
        "n_pair_groups": n_pair_groups,
        "per_protein_auc": protein_auc,
        "n_proteins": n_proteins,
        "per_lipid_auc": lipid_auc,
        "n_lipid_classes": n_lipid_classes,
        "train_rows": len(train_pool),
        "train_proteins": train_pool["LTPProtein"].nunique(),
        "train_lipids": train_pool["FullIdentityOfLipid"].nunique(),
        "valid_rows": len(valid_pool),
        "test_rows": len(test_pool),
    }


def build_report(
    table: pd.DataFrame, families: list[str], seeds: list[int], args: argparse.Namespace
) -> pd.DataFrame:
    protein_features, lipid_features = build_feature_tables(table)
    similarity = build_similarity(table, args.lipid_similarity_feature)
    rows = [
        evaluate_block(table, family, seed, args, protein_features, lipid_features, similarity)
        for family in families
        for seed in seeds
    ]
    return pd.DataFrame(rows)


def print_report(report: pd.DataFrame, args: argparse.Namespace) -> None:
    print(
        f"=== HistGradientBoosting ({args.split_mode}, class_weight={args.class_weight}, "
        f"train_negatives_per_positive={args.train_negatives_per_positive or 'full'}, "
        f"lipid_similarity_feature={args.lipid_similarity_feature}) ===\n"
    )
    if args.show_per_block:
        print(report.to_string(index=False))
        print()
    summary = report.groupby("family")[
        ["valid_ba", "test_ba", "test_f1", "valid_auc", "test_auc", "pair_auc",
         "per_protein_auc", "per_lipid_auc"]
    ].agg(["mean", "std"])
    print(summary)
    print()
    if args.show_per_block:
        group_sizes = report.groupby("family")[
            ["n_pair_groups", "n_proteins", "n_lipid_classes", "train_rows"]
        ].mean()
        print(group_sizes)
    print(
        f"\noverall test BA: mean={report['test_ba'].mean():.4f} "
        f"std={report['test_ba'].std():.4f}"
    )
    print(
        f"overall test F1: mean={report['test_f1'].mean():.4f} "
        f"std={report['test_f1'].std():.4f}"
    )
    print(
        f"overall test sensitivity/specificity: "
        f"{report['test_sensitivity'].mean():.4f} / {report['test_specificity'].mean():.4f}"
    )
    print(
        f"\noverall test AUC: mean={report['test_auc'].mean():.4f} "
        f"std={report['test_auc'].std():.4f}"
    )
    print(
        f"overall pair AUC: mean={report['pair_auc'].mean():.4f} "
        f"std={report['pair_auc'].std():.4f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--csv", default=None,
        help="interaction table path; defaults to the canonical deduplicated CSV",
    )
    parser.add_argument(
        "--families", default=None,
        help=(
            "comma-separated block names: protein families for --split_mode single/"
            "double (default: the project's 7 families), or LIPID_COLDSPLIT_SETS keys "
            f"for --split_mode lipid_coldsplit (default: {','.join(DEFAULT_LIPID_COLDSPLIT_GROUPS)})"
        ),
    )
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument(
        "--split_mode", default="lipid_coldsplit", choices=("single", "double", "lipid_coldsplit"),
        help=(
            "single/double: hold out a protein family (--excluded_groups/"
            "--double_coldsplit parity). lipid_coldsplit: hold out fixed lipid "
            "head-group classes with every protein still in training "
            "(--lipid_coldsplit parity) -- the known-protein/novel-lipid scenario "
            "this baseline is built to answer, hence the default."
        ),
    )
    parser.add_argument(
        "--share", type=float, default=0.8,
        help="lipid-class positive-coverage share held out, for --split_mode double",
    )
    parser.add_argument(
        "--train_negatives_per_positive", type=int, default=0,
        help=(
            "subsample train negatives to this many per positive per protein before "
            "fitting (0: use the full train pool -- every negative there is, the "
            "advantage a row classifier has over the network's own SGD-motivated "
            "subsampling). Composes with --class_weight; set both to compare which "
            "lever (more negatives, or a higher weight on the negatives it keeps) "
            "matters more on this data."
        ),
    )
    parser.add_argument(
        "--eval_negatives_per_positive", type=int, default=2,
        help=(
            "keep every valid/test positive, subsample negatives to this many per "
            "positive per protein before scoring -- matches the network's own "
            "evaluation pool (negatives_per_positive default 2), not the held-out "
            "block's raw positive rate. 0 disables it."
        ),
    )
    parser.add_argument(
        "--class_weight", default="balanced", choices=("none", "balanced"),
        help=(
            "HistGradientBoostingClassifier's own class_weight -- a real per-row "
            "loss weight (unlike kronrls_baseline.py's --positive_weight, which is a "
            "provable no-op for that closed-form estimator). 'balanced': "
            "n_samples/(n_classes*count) per class, computed on --split_mode "
            "lipid_coldsplit's full (unsampled by default) train rectangle's true "
            "~6-7%% positive rate unless --train_negatives_per_positive is also set."
        ),
    )
    parser.add_argument(
        "--lipid_similarity_feature", default="none",
        choices=("none", "tanimoto", "tanimoto_headgroup"),
        help=(
            "add one feature column: the k-NN Tanimoto-weighted train positive rate "
            "of this row's lipid (dataloader.chemistry_prior.null_scores) -- 'tanimoto' "
            "whole-molecule, 'tanimoto_headgroup' with acyl tails cut off first "
            "(training.pair_baseline_common.species_headgroup_tanimoto_similarity). "
            "Leak-safe on train via null_scores_leave_one_row_out. 'none' (default) "
            "omits it -- the model then has only the structural descriptors."
        ),
    )
    parser.add_argument(
        "--similarity_neighbours", type=int, default=DEFAULT_NEIGHBOURS,
        help="k nearest training lipids for --lipid_similarity_feature",
    )
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--max_iter", type=int, default=300)
    parser.add_argument("--max_depth", type=int, default=None)
    parser.add_argument("--max_leaf_nodes", type=int, default=31)
    parser.add_argument("--l2_regularization", type=float, default=0.0)
    parser.add_argument("--min_samples_leaf", type=int, default=20)
    parser.add_argument(
        "--threshold_metric", default="ba", choices=("ba", "f1"),
        help="which metric the decision threshold (fit on valid, applied to test) maximizes.",
    )
    parser.add_argument("--out", help="write the per-block report as JSON records to this path")
    parser.add_argument(
        "--show_per_block", action="store_true",
        help="also print the full per-family/per-seed row table (hidden by default)",
    )
    args = parser.parse_args()

    csv_path = args.csv or interaction_csv_path(os.path.join(PROJECT_ROOT, "data"))
    table = pd.read_csv(csv_path)
    table["pair_id"] = table.index.astype(int)

    if args.families:
        families = [name for name in args.families.split(",") if name]
    elif args.split_mode == "lipid_coldsplit":
        families = list(DEFAULT_LIPID_COLDSPLIT_GROUPS)
    else:
        families = list(DEFAULT_FAMILIES)
    seeds = [int(value) for value in args.seeds.split(",")]

    report = build_report(table, families, seeds, args)
    print_report(report, args)

    if args.out:
        report.to_json(args.out, orient="records", indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
