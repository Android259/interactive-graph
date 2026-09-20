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
from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES, pair_descriptor_value  # noqa: E402
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
    resolve_family_excluded_lipids,
    resolve_lipid_feature_subset,
    resolve_protein_feature_subset,
    species_headgroup_tanimoto_similarity,
    species_tanimoto_similarity,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
DEFAULT_LIPID_COLDSPLIT_GROUPS = tuple(LIPID_COLDSPLIT_SETS.keys())
# dataloader.pair_descriptors.pair_descriptor_value's own lipid_values/protein_values
# dict keys, across every PAIR_DESCRIPTOR_NAMES entry -- the fixed set of columns
# build_pair_feature_inputs needs from explicit_lipid_features/protein_pocket_
# features (via resolve_protein_feature_subset) regardless of which pair names are
# actually requested, so one small lookup table serves all of them.
PAIR_DESCRIPTOR_LIPID_INPUTS = ("chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2")
PAIR_DESCRIPTOR_PROTEIN_INPUTS = (
    "pocket_extent", "aromatic_share", "polar_share", "pocket_volume_per_sasa",
    "buriedness_q50", "depth_q10", "hydropathy_core", "hydropathy_rim",
    "pocket_elongation", "pocket_flatness",
)
DEFAULT_NEIGHBOURS = 15


def build_feature_tables(
    table: pd.DataFrame,
    protein_descriptor_names: list[str] | None = None,
    lipid_descriptor_names: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Protein and lipid feature tables, built once over the whole interaction table.

    Fixed columns regardless of which pool (train/valid/test) later indexes into
    them, so a held-out lipid's row is just another lookup, never a retrain of the
    feature space -- the mechanism that lets this model score a genuinely novel
    lipid at all.

    `protein_descriptor_names`/`lipid_descriptor_names`: None (default) keeps every
    column protein_pocket_features/explicit_lipid_features produce, same as before
    this parameter existed. A list restricts to those names -- protein names
    resolved through resolve_protein_feature_subset and lipid names through
    resolve_lipid_feature_subset (the SAME resolution analysis/kronrls_baseline.py's
    --protein_kernel=pocket_subset/--lipid_kernel=explicit_subset use: protein_
    pocket_features'/explicit_lipid_features' own columns first, dataloader.
    pair_descriptors.PROTEIN_DESCRIPTOR_NAMES/LIPID_DESCRIPTOR_NAMES for anything
    they do not hand-implement, "molformer" for the network's own raw lipid
    embedding) -- so this baseline's --lipid_features/--protein_features shorthand
    (scripts/run_gbm.py) can never resolve a name differently than Kron-RLS's does.
    """
    proteins = sorted(table["LTPProtein"].unique())
    if protein_descriptor_names:
        protein_features = resolve_protein_feature_subset(proteins, list(protein_descriptor_names))
    else:
        protein_features = protein_pocket_features(proteins)
    protein_features = protein_features.add_prefix("protein__")

    if lipid_descriptor_names:
        lipid_features = resolve_lipid_feature_subset(table, lipid_descriptor_names)
    else:
        lipid_features = explicit_lipid_features(table)
    lipid_features = lipid_features.add_prefix("lipid__")
    return protein_features, lipid_features


def build_pair_feature_inputs(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(lipid_inputs, protein_inputs): the fixed columns dataloader.pair_descriptors.
    pair_descriptor_value reads off its lipid_values/protein_values dicts, built once
    over the whole table/every protein -- the row-classifier counterpart of
    build_feature_tables, feeding pair_feature_columns below instead of the model
    directly (a --pair_descriptor_names name is a FUNCTION of these, not a column of
    either raw table).
    """
    lipid_inputs = explicit_lipid_features(table).loc[:, list(PAIR_DESCRIPTOR_LIPID_INPUTS)]
    proteins = sorted(table["LTPProtein"].unique())
    protein_inputs = resolve_protein_feature_subset(proteins, list(PAIR_DESCRIPTOR_PROTEIN_INPUTS))
    return lipid_inputs, protein_inputs


def pair_feature_columns(
    pool: pd.DataFrame,
    lipid_inputs: pd.DataFrame,
    protein_inputs: pd.DataFrame,
    names: list[str],
) -> pd.DataFrame:
    """One column per requested PAIR_DESCRIPTOR_NAMES entry, index-aligned to `pool`
    (row order, reset to a plain RangeIndex like row_features' own protein/lipid
    parts) -- --pair_features' actual values, unlike Kron-RLS (see run_cron.py's own
    module docstring for why that one structurally cannot take one at all): a row
    classifier has no separable-kernel constraint, so a joint (protein, lipid) value
    is just one more feature column here.
    """
    lipid_rows = lipid_inputs.loc[pool["FullIdentityOfLipid"]].to_dict("records")
    protein_rows = protein_inputs.loc[pool["LTPProtein"]].to_dict("records")
    values = {
        f"pair__{name}": [
            pair_descriptor_value(name, lipid_row, protein_row)
            for lipid_row, protein_row in zip(lipid_rows, protein_rows)
        ]
        for name in names
    }
    return pd.DataFrame(values).reset_index(drop=True)


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
    pair_columns: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """One feature row per (protein, lipid) pair in `pool`, index-aligned to it."""
    proteins = protein_features.loc[pool["LTPProtein"]].reset_index(drop=True)
    lipids = lipid_features.loc[pool["FullIdentityOfLipid"]].reset_index(drop=True)
    parts = [proteins, lipids]
    if similarity_column is not None:
        parts.append(similarity_column.reset_index(drop=True))
    if pair_columns is not None:
        parts.append(pair_columns.reset_index(drop=True))
    return pd.concat(parts, axis=1)


def evaluate_block(
    table: pd.DataFrame,
    family: str,
    seed: int,
    args: argparse.Namespace,
    protein_features: pd.DataFrame,
    lipid_features: pd.DataFrame,
    similarity: tuple[np.ndarray, dict[str, int]] | None,
    pair_feature_inputs: tuple[pd.DataFrame, pd.DataFrame] | None = None,
) -> dict:
    """Fit and score one (family, seed) cold-split block."""
    # merge_valid_test: nothing is fit on valid any more (threshold and early
    # stopping both come from train now), so halving the excluded block away would
    # only shrink what test measures, for nothing.
    train_pool, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share,
        excluded_lipids=resolve_family_excluded_lipids(args, family),
        merge_valid_test=True,
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

    train_pair = valid_pair = test_pair = None
    if pair_feature_inputs is not None and args.pair_descriptor_names:
        lipid_inputs, protein_inputs = pair_feature_inputs
        train_pair = pair_feature_columns(
            train_pool, lipid_inputs, protein_inputs, args.pair_descriptor_names
        )
        valid_pair = pair_feature_columns(
            valid_pool, lipid_inputs, protein_inputs, args.pair_descriptor_names
        )
        test_pair = pair_feature_columns(
            test_pool, lipid_inputs, protein_inputs, args.pair_descriptor_names
        )

    x_train = row_features(
        train_pool, protein_features, lipid_features, train_similarity_column, train_pair
    )
    y_train = train_pool["Interaction"].to_numpy()
    x_valid = row_features(
        valid_pool, protein_features, lipid_features, valid_similarity_column, valid_pair
    )
    y_valid = valid_pool["Interaction"].to_numpy()
    x_test = row_features(
        test_pool, protein_features, lipid_features, test_similarity_column, test_pair
    )
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
    # Early stopping holds out a slice of TRAIN (sklearn's own validation_fraction),
    # never the excluded block: that block stands in for a genuinely new lipid, so
    # its labels may not pick the stopping iteration any more than they may pick the
    # threshold below -- either one would make the reported BA/F1 "best achievable
    # knowing the answer" rather than what the model does on an unseen lipid.
    model.fit(x_train, y_train)

    train_scores = model.predict_proba(x_train)[:, 1]
    valid_scores = model.predict_proba(x_valid)[:, 1]
    test_scores = model.predict_proba(x_test)[:, 1]

    # Threshold from TRAIN only, same reason as the early-stopping split above.
    threshold_metric = "balanced_accuracy" if args.threshold_metric == "ba" else "F1"
    threshold, _ = best_threshold_for_metric(y_train, train_scores, metric=threshold_metric)
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
        # Full test-block confusion matrix at `threshold` -- same bare keys
        # kronrls_baseline.py's own evaluate_block returns, so scripts/run_gbm.py's
        # report-file writer (mirroring scripts/run_cron.py's) can share the same
        # METRIC_FIELD_MAP shape.
        "total": test_metrics["total"],
        "real_positive": test_metrics["real_positive"],
        "real_negative": test_metrics["real_negative"],
        "predicted_positive": test_metrics["predicted_positive"],
        "predicted_negative": test_metrics["predicted_negative"],
        "TP": test_metrics["TP"],
        "FP": test_metrics["FP"],
        "TN": test_metrics["TN"],
        "FN": test_metrics["FN"],
        "accuracy": test_metrics["accuracy"],
        "precision": test_metrics["precision"],
        "IoU": test_metrics["IoU"],
        "FAR": test_metrics["FAR"],
    }


def build_report(
    table: pd.DataFrame, families: list[str], seeds: list[int], args: argparse.Namespace
) -> pd.DataFrame:
    protein_features, lipid_features = build_feature_tables(
        table, args.protein_descriptor_names, args.lipid_descriptor_names
    )
    similarity = build_similarity(table, args.lipid_similarity_feature)
    pair_feature_inputs = (
        build_pair_feature_inputs(table) if args.pair_descriptor_names else None
    )
    rows = [
        evaluate_block(
            table, family, seed, args, protein_features, lipid_features, similarity,
            pair_feature_inputs,
        )
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


def build_parser() -> argparse.ArgumentParser:
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
    parser.add_argument(
        "--protein_descriptor_names", default=None,
        type=lambda text: [name for name in text.split(",") if name],
        help=(
            "restrict protein features to this comma-separated subset of "
            "POCKET_ALL_NAMES (default: every column protein_pocket_features "
            "produces). scripts/run_gbm.py's --protein_features is a convenience "
            "alias that sets this."
        ),
    )
    parser.add_argument(
        "--lipid_descriptor_names", default=None,
        type=lambda text: [name for name in text.split(",") if name],
        help=(
            "restrict lipid features to this comma-separated subset, resolved via "
            "training.pair_baseline_common.resolve_lipid_feature_subset -- the SAME "
            "name resolution analysis/kronrls_baseline.py's --lipid_kernel="
            "explicit_subset uses (explicit_lipid_features' own columns, "
            "dataloader.pair_descriptors.LIPID_DESCRIPTOR_NAMES for the rest, plus "
            "the special name 'molformer'). Default: every column "
            "explicit_lipid_features produces. scripts/run_gbm.py's --lipid_features "
            "is a convenience alias that sets this."
        ),
    )
    parser.add_argument(
        "--pair_descriptor_names", default=None,
        type=lambda text: [name for name in text.split(",") if name],
        help=(
            "add one feature column per named dataloader.pair_descriptors."
            "PAIR_DESCRIPTOR_NAMES entry (occupancy, aromatic_contact, ...), computed "
            "via pair_descriptor_value from build_pair_feature_inputs' fixed lipid/"
            "protein input columns -- unlike Kron-RLS (see run_cron.py's own module "
            "docstring for why that one structurally cannot), a row classifier has "
            "no separable-kernel constraint, so a joint (protein, lipid) value is "
            "just one more feature here. Default: none (no pair features). scripts/"
            "run_gbm.py's --pair_features is a convenience alias that sets this."
        ),
    )
    return parser


def load_table(args: argparse.Namespace) -> pd.DataFrame:
    csv_path = args.csv or interaction_csv_path(os.path.join(PROJECT_ROOT, "data"))
    table = pd.read_csv(csv_path)
    table["pair_id"] = table.index.astype(int)
    return table


def resolve_families(args: argparse.Namespace) -> list[str]:
    if args.families:
        return [name for name in args.families.split(",") if name]
    if args.split_mode == "lipid_coldsplit":
        return list(DEFAULT_LIPID_COLDSPLIT_GROUPS)
    return list(DEFAULT_FAMILIES)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    table = load_table(args)
    families = resolve_families(args)
    seeds = [int(value) for value in args.seeds.split(",")]

    report = build_report(table, families, seeds, args)
    print_report(report, args)

    if args.out:
        report.to_json(args.out, orient="records", indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
