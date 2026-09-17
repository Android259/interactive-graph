#!/usr/bin/env python3
"""Two-step Kron-RLS baseline over the protein x lipid interaction rectangle.

Closed-form kernel ridge regression (van Laarhoven et al. 2011; Pahikkala et al. 2014;
Cichonska et al. 2018's pairwiseMKL family). Given a protein kernel Kp, a lipid kernel
Kl, and the training block's complete label rectangle Y, it fits

    A = (Kp + lambda_p * I)^-1 @ Y @ (Kl + lambda_l * I)^-1

and scores any (protein, lipid) pair -- including pairs whose protein and/or lipid
never appeared in training -- as Kp_query,train @ A @ Kl_train,query (out-of-sample
Kron-RLS extension). Reported as PU-AUC (Interaction=0 is "not assayed", not a
confirmed negative -- see training.pair_baseline_common.auc_p_vs_u), matching this
project's other non-neural baseline (analysis/null_model.py).

Three split modes -- --split_mode {single,double,lipid_coldsplit}. single/double hold
out a protein family (`--excluded_groups`/`--double_coldsplit` parity); lipid_coldsplit
holds out fixed lipid head-group classes with every protein still in training
(`--lipid_coldsplit` parity, dataloader.sampler.LIPID_COLDSPLIT_SETS), reusing
preprocessing.lipid_marginal_baseline.lipid_split -- the same train/valid/test
reconstruction analysis/lipid_coldsplit_null_model.py's nearest-neighbour competitors
are scored against, so a Kron-RLS fit is now comparable on that split, not just the
family-axis ones. --families under lipid_coldsplit takes LIPID_COLDSPLIT_SETS keys
(sphingolipids, phosphorus_free, ...) instead of protein family names.

Both kernels are pluggable and accept arbitrary externally supplied vectors, not just
the two built-in descriptor sets:

    --protein_kernel {pocket13,pocket23,pocket_subset,custom_features,custom_kernel}
    --lipid_kernel   {tanimoto,tanimoto_headgroup,explicit,explicit_subset,custom_features,custom_kernel}

custom_features takes a CSV (id column + numeric feature columns of any kind) and
turns it into a kernel via --protein_kernel_type/--lipid_kernel_type (rbf/linear/
cosine). custom_kernel takes a precomputed square similarity/kernel matrix (.npy) plus
a names file and uses it as-is. This matters because the project's own pooled-ESM3
cosine similarity is known to be nearly constant across all 35 proteins in this
dataset (architecture/final_layer.py's SlicedWassersteinPool docstring: median cosine
0.974 vs. median binding-profile similarity 0.000) -- a weak default protein kernel on
this data, not a reason to hard-code any one feature source.

    python3 analysis/kronrls_baseline.py
    python3 analysis/kronrls_baseline.py --split_mode single --protein_kernel pocket23
    python3 analysis/kronrls_baseline.py --split_mode lipid_coldsplit \\
        --families=sphingolipids,phosphorus_free,anionic,choline \\
        --protein_kernel pocket_subset --protein_descriptor_names=pocket_extent,\\
pocket_elongation --lipid_kernel tanimoto --lambda_grid 0.01,0.1,1,10,100
    python3 analysis/kronrls_baseline.py --lipid_kernel custom_features \\
        --lipid_features my_lipid_vectors.csv --lambda_grid 0.01,0.1,1,10,100
    python3 analysis/kronrls_baseline.py --lipid_kernel explicit_subset \\
        --lipid_descriptor_names=logp,tpsa,molar_refractivity,rotatable_bond_count,\\
aromatic_ring_count,ring_count --lambda_grid 0.01,0.1,1,10,100

Class weighting. Nothing here reweights the LOSS the way training/new_train.py's
--class_weights does. The fit minimizes plain ||Y - Kp A Kl||^2 with a two-sided
Tikhonov penalty, closed-form as A = (Kp+lambda_p I)^-1 Y (Kl+lambda_l I)^-1
(training.pair_baseline_common.two_step_kronrls) -- exact only for UNIFORM per-cell
weight (every train cell equally important), because the trick that makes the two
sequential solves equal one joint solve relies on it. A general per-cell weight W
(needed for "positive cells matter W times more than negative ones", i.e. class
weighting) is not separable as a protein-weight times a lipid-weight -- whether a
cell is positive is a joint (protein, lipid) pattern, not a property of either side
alone -- so it does not fit inside the same two-inverse formula; solving it exactly
needs a different, iterative solver (this file does not have one). Row-deleting to a
balanced 1:1/1:R matrix is not an option either: aggregate_pair_labels requires
every (train protein, train lipid) cell present, and deleting rows to rebalance
punches holes in exactly that rectangle.

--positive_weight is the one lever that stays inside the exact closed form: it
rescales the *target value* of positive cells (1 -> W, negatives stay 0) before the
fit, which widens the score gap the fit tries to produce between positive and
negative cells without touching which cells are present. It is NOT the same
optimization problem as a weighted loss (rescaling changes each positive cell's
target, not the curvature of its penalty -- see the docstring above
best_threshold_for_metric's neighbour, training.pair_baseline_common.
two_step_kronrls, for the exact formula this composes with) -- treat it as a real
but approximate, empirically-tuned lever, not a calibrated class weight.

Reads only. Fits a closed-form regression in memory each run; writes nothing unless
--out is given.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS, lipid_class_series  # noqa: E402
from null_model import per_lipid_auc, per_pair_auc, per_protein_auc  # noqa: E402
from training.pair_baseline_common import (  # noqa: E402
    aggregate_pair_labels,
    auc_p_vs_u,
    balance_pool_negatives,
    best_threshold_for_metric,
    binary_confusion_metrics,
    build_lipid_kernel,
    build_protein_kernel,
    cold_split_pools,
    predict_kronrls,
    two_step_kronrls,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
DEFAULT_LIPID_COLDSPLIT_GROUPS = tuple(LIPID_COLDSPLIT_SETS.keys())


def _score_pool(
    pool: pd.DataFrame,
    coefficients: np.ndarray,
    protein_kernel: np.ndarray,
    protein_index: dict[str, int],
    lipid_kernel: np.ndarray,
    lipid_index: dict[str, int],
    train_proteins: list[str],
    train_lipids: list[str],
) -> tuple[float, pd.DataFrame]:
    """Score one held-out pool via the out-of-sample Kron-RLS extension.

    Returns the pooled PU-AUC and the pool with a `_score` column attached, so a
    caller can also run the within-protein / within-lipid-class / pair diagnostics
    (per_protein_auc, per_lipid_auc, per_pair_auc, all from analysis/null_model.py)
    on the same scores without re-solving the out-of-sample extension.
    """
    query_proteins = sorted(pool["LTPProtein"].unique())
    query_lipids = sorted(pool["FullIdentityOfLipid"].unique())
    kp_query_train = protein_kernel[
        np.ix_(
            [protein_index[name] for name in query_proteins],
            [protein_index[name] for name in train_proteins],
        )
    ]
    kl_train_query = lipid_kernel[
        np.ix_(
            [lipid_index[name] for name in train_lipids],
            [lipid_index[name] for name in query_lipids],
        )
    ]
    scores = predict_kronrls(coefficients, kp_query_train, kl_train_query)
    p_position = {name: position for position, name in enumerate(query_proteins)}
    l_position = {name: position for position, name in enumerate(query_lipids)}
    score_column = np.asarray(
        [
            scores[p_position[p], l_position[l]]
            for p, l in zip(pool["LTPProtein"], pool["FullIdentityOfLipid"])
        ]
    )
    scored_pool = pool.assign(_score=score_column)
    return auc_p_vs_u(pool["Interaction"].to_numpy(), score_column), scored_pool


def evaluate_block(table: pd.DataFrame, family: str, seed: int, args: argparse.Namespace) -> dict:
    """Fit and score one (family, seed) cold-split block.

    `family` names a protein family for --split_mode single/double, or a
    LIPID_COLDSPLIT_SETS key (e.g. "sphingolipids") for --split_mode lipid_coldsplit --
    the loop variable is generic across axes, only what it indexes into changes.
    """
    train_pool, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share
    )

    # Score against the same 1:2 pool the network is scored against, not the held-out
    # block's own raw positive rate -- see balance_pool_negatives. Train is untouched:
    # it must stay the complete rectangle two_step_kronrls's closed form requires
    # (aggregate_pair_labels raises on a single missing (protein, lipid) cell).
    valid_pool = balance_pool_negatives(valid_pool, seed, args.eval_negatives_per_positive)
    test_pool = balance_pool_negatives(test_pool, seed, args.eval_negatives_per_positive)

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

    # One kernel over train + held-out entities, computed once per block and sliced
    # below -- an out-of-sample protein/lipid is just another row of the same kernel,
    # standardized (where applicable) by train statistics only.
    protein_kernel, protein_index = build_protein_kernel(
        args.protein_kernel,
        all_proteins,
        train_proteins,
        kernel_type=args.protein_kernel_type,
        descriptor_names=args.protein_descriptor_names,
        features_path=args.protein_features,
        kernel_path=args.protein_kernel_matrix,
        names_path=args.protein_kernel_names,
    )
    # `table` here must stay the full, unfiltered, original-row-order interaction
    # table -- species_tanimoto_similarity is positionally aligned to the compact
    # Tanimoto artefacts, not to whatever subset a caller passes.
    lipid_kernel, lipid_index = build_lipid_kernel(
        args.lipid_kernel,
        table,
        all_lipids,
        train_lipids,
        kernel_type=args.lipid_kernel_type,
        descriptor_names=args.lipid_descriptor_names,
        features_path=args.lipid_features,
        kernel_path=args.lipid_kernel_matrix,
        names_path=args.lipid_kernel_names,
    )

    labels = aggregate_pair_labels(
        train_pool, lipid_class_targets=args.lipid_class_targets
    ).reindex(index=train_proteins, columns=train_lipids)
    # --positive_weight rescales the {0,1} target itself before the fit -- see the
    # module docstring's "Class weighting" section for why this, and not a per-cell
    # loss weight, is what stays inside two_step_kronrls's exact closed form. 1.0 is a
    # no-op (previous behaviour).
    label_matrix = labels.to_numpy()
    if args.positive_weight != 1.0:
        label_matrix = np.where(label_matrix == 1, args.positive_weight, label_matrix)
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

    # --select_metric picks what the grid search optimizes on valid: "auc" (rank-only,
    # the previous default) or "ba"/"f1" (optimize the same metric the threshold
    # search below will report). These need not agree -- an AUC-best lambda pair can
    # lose to a BA-best one once a decision threshold is imposed on top of it.
    threshold_metric = "balanced_accuracy" if args.threshold_metric == "ba" else "F1"
    grid = args.lambda_grid or [(args.protein_lambda, args.lipid_lambda)]
    best = None
    for protein_lambda, lipid_lambda in grid:
        coefficients = two_step_kronrls(
            kp_train, kl_train, label_matrix, protein_lambda, lipid_lambda
        )
        valid_auc, valid_scored = _score_pool(
            valid_pool, coefficients, protein_kernel, protein_index,
            lipid_kernel, lipid_index, train_proteins, train_lipids,
        )
        if args.select_metric == "auc":
            selection_score = valid_auc
        else:
            select_metric = "balanced_accuracy" if args.select_metric == "ba" else "F1"
            _, selection_score = best_threshold_for_metric(
                valid_pool["Interaction"].to_numpy(), valid_scored["_score"].to_numpy(),
                metric=select_metric,
            )
        candidate = (
            selection_score, valid_auc, protein_lambda, lipid_lambda, coefficients, valid_scored
        )
        if best is None:
            best = candidate
            continue
        best_score = best[0]
        if not np.isnan(selection_score) and (np.isnan(best_score) or selection_score > best_score):
            best = candidate
    _, valid_auc, protein_lambda, lipid_lambda, coefficients, valid_scored = best

    # Threshold, like the lambdas above it, is chosen on valid only and then applied
    # unchanged to test (best_threshold_for_metric's own docstring: a Kron-RLS score
    # is not a calibrated probability, so a fixed 0.5 cut would silently score the
    # all-negative class here).
    threshold, _ = best_threshold_for_metric(
        valid_pool["Interaction"].to_numpy(), valid_scored["_score"].to_numpy(),
        metric=threshold_metric,
    )
    valid_metrics = binary_confusion_metrics(
        valid_pool["Interaction"].to_numpy(), valid_scored["_score"].to_numpy(), threshold
    )

    test_auc, test_scored = _score_pool(
        test_pool, coefficients, protein_kernel, protein_index,
        lipid_kernel, lipid_index, train_proteins, train_lipids,
    )
    test_metrics = binary_confusion_metrics(
        test_pool["Interaction"].to_numpy(), test_scored["_score"].to_numpy(), threshold
    )

    # Pooled test_auc mixes each row's own signal with whatever the protein's and
    # the lipid class' own marginals contribute -- the within-group and two-way-
    # residual diagnostics below (same functions already used for the network and
    # the chemistry null model, see analysis/null_model.py) separate those out.
    test_scored = test_scored.assign(lipid_class=lipid_class_series(test_scored))
    protein_auc, n_proteins = per_protein_auc(test_scored, test_scored["_score"].to_numpy())
    lipid_auc, n_lipid_classes = per_lipid_auc(test_scored, test_scored["_score"].to_numpy())
    pair_auc = per_pair_auc(test_scored, test_scored["_score"].to_numpy())
    n_pair_groups = int(test_scored["lipid_class"].nunique())

    return {
        "family": family,
        "seed": seed,
        "protein_lambda": protein_lambda,
        "lipid_lambda": lipid_lambda,
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
        "train_proteins": len(train_proteins),
        "train_lipids": len(train_lipids),
        "valid_rows": len(valid_pool),
        "test_rows": len(test_pool),
    }


def _parse_lambda_grid(text: str) -> list[tuple[float, float]]:
    values = [float(part) for part in text.split(",") if part.strip()]
    return list(itertools.product(values, values))


def build_report(table: pd.DataFrame, families: list[str], seeds: list[int], args) -> pd.DataFrame:
    rows = [evaluate_block(table, family, seed, args) for family in families for seed in seeds]
    return pd.DataFrame(rows)


def print_report(report: pd.DataFrame, args: argparse.Namespace) -> None:
    print(
        f"=== Kron-RLS ({args.split_mode}, "
        f"protein={args.protein_kernel}/{args.protein_kernel_type}, "
        f"lipid={args.lipid_kernel}/{args.lipid_kernel_type}) ===\n"
    )
    if args.show_per_block:
        print(report.to_string(index=False))
        print()
    # BA/F1 first -- the primary metrics for this analysis, threshold fit on valid
    # only (best_threshold_for_balanced_accuracy); AUC columns stay alongside as the
    # threshold-free ranking view, same convention as the network's own metrics_
    # summary.csv rows.
    summary = report.groupby("family")[
        ["valid_ba", "test_ba", "test_f1", "valid_auc", "test_auc", "pair_auc",
         "per_protein_auc", "per_lipid_auc"]
    ].agg(["mean", "std"])
    print(summary)
    print()
    if args.show_per_block:
        group_sizes = report.groupby("family")[
            ["n_pair_groups", "n_proteins", "n_lipid_classes"]
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
        "--split_mode", default="double", choices=("single", "double", "lipid_coldsplit"),
        help=(
            "single: hold out only the protein family (--excluded_groups parity, "
            "lipid classes stay in training). double: also hold out lipid head-group "
            "classes (--double_coldsplit parity). lipid_coldsplit: hold out fixed lipid "
            "head-group classes with every protein still in training (--lipid_coldsplit "
            "parity, via preprocessing.lipid_marginal_baseline.lipid_split)."
        ),
    )
    parser.add_argument(
        "--share", type=float, default=0.8,
        help="lipid-class positive-coverage share held out, for --split_mode double",
    )
    parser.add_argument(
        "--eval_negatives_per_positive", type=int, default=2,
        help=(
            "keep every valid/test positive, subsample negatives to this many per "
            "positive per protein (dataloader.sampler.sample_protein_balanced_"
            "negatives) before scoring -- matches training/read_configuration.py's "
            "own negatives_per_positive default (2), the pool every current arg file "
            "is actually trained AND evaluated on, not the held-out block's raw "
            "positive rate (~6-7%% on lipid_coldsplit, thinner still on single/"
            "double). Train is never touched by this -- it stays the complete "
            "rectangle the closed-form fit requires. 0 disables it and scores the "
            "full raw held-out block instead."
        ),
    )
    parser.add_argument(
        "--lipid_class_targets", action="store_true",
        help=(
            "fit against the lipid head-group class instead of the exact species: a "
            "training cell is positive whenever its protein has a positive anywhere in "
            "that lipid's class (training.pair_baseline_common.aggregate_pair_labels), "
            "computed from the train pool alone. The held-out valid/test pools are still "
            "scored against their own exact Interaction values, unchanged."
        ),
    )
    parser.add_argument(
        "--positive_weight", type=float, default=1.0,
        help=(
            "rescale positive train cells' target from 1 to this value before the fit "
            "(negative cells stay 0). NOT the same as weighting the loss -- see the "
            "module docstring's Class weighting section -- but it is the one lever that "
            "stays inside two_step_kronrls's exact closed form: it widens the score gap "
            "between predicted-positive and predicted-negative cells without deleting "
            "any train row (unlike a 1:1/1:R row-balanced matrix, which two_step_kronrls "
            "cannot accept -- aggregate_pair_labels requires every train cell present). "
            "1.0 is a no-op (previous behaviour)."
        ),
    )
    parser.add_argument(
        "--protein_kernel", default="pocket13",
        choices=("pocket13", "pocket23", "pocket_subset", "custom_features", "custom_kernel"),
    )
    parser.add_argument(
        "--protein_kernel_type", default="rbf", choices=("rbf", "linear", "cosine"),
        help="how custom_features (or pocket13/23/pocket_subset) vectors become a kernel",
    )
    parser.add_argument(
        "--protein_descriptor_names", type=lambda text: [n for n in text.split(",") if n],
        default=None,
        help=(
            "comma-separated pocket descriptor names, for --protein_kernel=pocket_subset "
            "-- pass the exact list a network run's --pocket_descriptor_names used to "
            "match its protein features, e.g. the project's protgeom8 set: "
            "pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,"
            "aromatic_share,hydropathy_core,hydropathy_rim"
        ),
    )
    parser.add_argument(
        "--protein_features",
        help="CSV: id column + numeric feature columns, for --protein_kernel=custom_features",
    )
    parser.add_argument(
        "--protein_kernel_matrix",
        help=".npy square matrix, for --protein_kernel=custom_kernel",
    )
    parser.add_argument(
        "--protein_kernel_names",
        help="text file, one LTPProtein name per line matching the matrix's row/column order",
    )
    parser.add_argument(
        "--lipid_kernel", default="tanimoto",
        choices=(
            "tanimoto", "tanimoto_headgroup", "explicit", "explicit_subset",
            "custom_features", "custom_kernel",
        ),
        help=(
            "tanimoto: whole-molecule Morgan-fingerprint species similarity. "
            "tanimoto_headgroup: the same fingerprint computed after cutting off "
            "acyl tails (preprocessing/build_tanimoto_headgroup.py) -- isolates "
            "head-group chemistry from chain length/unsaturation, the chemical "
            "counterpart of --lipid_coldsplit's own class-name holdout."
        ),
    )
    parser.add_argument(
        "--lipid_kernel_type", default="rbf", choices=("rbf", "linear", "cosine"),
        help="how custom_features (or explicit/explicit_subset) vectors become a kernel",
    )
    parser.add_argument(
        "--lipid_descriptor_names", type=lambda text: [n for n in text.split(",") if n],
        default=None,
        help=(
            "comma-separated explicit lipid descriptor names, for "
            "--lipid_kernel=explicit_subset -- any column training.pair_baseline_common."
            "explicit_lipid_features produces, e.g. the whole-molecule set: "
            "logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count"
        ),
    )
    parser.add_argument(
        "--lipid_features",
        help="CSV: id column + numeric feature columns, for --lipid_kernel=custom_features",
    )
    parser.add_argument(
        "--lipid_kernel_matrix",
        help=".npy square matrix, for --lipid_kernel=custom_kernel",
    )
    parser.add_argument(
        "--lipid_kernel_names",
        help="text file, one FullIdentityOfLipid name per line matching the matrix's row/column order",
    )
    parser.add_argument("--protein_lambda", type=float, default=1.0)
    parser.add_argument("--lipid_lambda", type=float, default=1.0)
    parser.add_argument(
        "--lambda_grid", type=_parse_lambda_grid, default=None,
        help=(
            "comma-separated values tried on both axes (cartesian product), e.g. "
            "0.01,0.1,1,10,100; picked per (family, seed) by --select_metric on the "
            "validation block, then re-scored on the test block. Overrides "
            "--protein_lambda/--lipid_lambda."
        ),
    )
    parser.add_argument(
        "--select_metric", default="auc", choices=("auc", "ba", "f1"),
        help=(
            "what --lambda_grid maximizes on valid: auc (rank-only, threshold-free), "
            "ba/f1 (the best-threshold value of that metric on valid -- makes the "
            "regularization itself optimize for the metric being reported, not just "
            "ranking quality)."
        ),
    )
    parser.add_argument(
        "--threshold_metric", default="ba", choices=("ba", "f1"),
        help=(
            "which metric the single decision threshold (fit on valid, applied to "
            "test) maximizes. ba and f1 are NOT maximized by the same cut under this "
            "project's class imbalance (~6-7%% train positive rate on lipid_coldsplit) "
            "-- a BA-optimal cut reads as a low F1, not a broken model; pick f1 here "
            "if F1 is what needs to look normal, at BA's expense."
        ),
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
