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
import copy
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
    block_tanimoto_headgroup_similarity,
    block_tanimoto_similarity,
    cold_split_pools,
    predict_kronrls,
    resolve_family_excluded_lipids,
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


def _protein_kernel_cache_key(
    args: argparse.Namespace, all_proteins: list[str], train_proteins: list[str]
) -> tuple:
    """Keyed on the ACTUAL entity lists, not on (family, seed) -- under
    --split_mode lipid_coldsplit every protein always stays in train (only lipid
    head-group classes are excluded), so all_proteins/train_proteins come out
    IDENTICAL for every family and every seed; keying on entity content (rather
    than on the family/seed label that produced it) lets one single protein-kernel
    build serve the whole run instead of one per (family, seed) block.
    """
    return (
        tuple(all_proteins), tuple(train_proteins),
        args.protein_kernel, args.protein_kernel_type,
        tuple(args.protein_descriptor_names) if args.protein_descriptor_names else None,
        args.protein_features, args.protein_kernel_matrix, args.protein_kernel_names,
    )


def _lipid_kernel_cache_key(
    args: argparse.Namespace, all_lipids: list[str], train_lipids: list[str]
) -> tuple:
    """Lipid-side counterpart of _protein_kernel_cache_key. all_lipids/train_lipids
    differ by family (each excludes a different head-group class) but train_lipids
    is seed-invariant within a family (balance_pool_negatives never touches train),
    so this still collapses the 5-seeds-per-family case down to one lipid-kernel
    build per family.
    """
    return (
        tuple(all_lipids), tuple(train_lipids),
        args.lipid_kernel, args.lipid_kernel_type,
        tuple(args.lipid_descriptor_names) if args.lipid_descriptor_names else None,
        args.lipid_features, args.lipid_kernel_matrix, args.lipid_kernel_names,
    )


def evaluate_block(
    table: pd.DataFrame,
    family: str,
    seed: int,
    args: argparse.Namespace,
    kernel_cache: dict | None = None,
) -> dict:
    """Fit and score one (family, seed) cold-split block.

    `family` names a protein family for --split_mode single/double, or a
    LIPID_COLDSPLIT_SETS key (e.g. "sphingolipids") for --split_mode lipid_coldsplit --
    the loop variable is generic across axes, only what it indexes into changes.

    `kernel_cache`, when given, memoizes the protein_kernel and lipid_kernel builds
    below separately, each keyed on its own actual entity lists (not on family/seed
    labels -- see _protein_kernel_cache_key/_lipid_kernel_cache_key). Neither kernel
    depends on protein_lambda/lipid_lambda, and under --split_mode lipid_coldsplit
    the protein side does not depend on family or seed either (every protein always
    stays in train), so build_report and select_global_lambda both pass one shared
    dict across their whole (family, seed[, lambda candidate]) loop -- without it,
    the identical protein/lipid kernel gets rebuilt from scratch on every single
    block, which used to be cheap enough not to notice and got much more visible
    once the descriptor sets it builds from (chain/hbond/heavy/unsaturation,
    POCKET_EXTRA_NAMES, molformer) got heavier to compute. None (the default)
    preserves the old always-rebuild behaviour for any other caller.
    """
    excluded_species = resolve_family_excluded_lipids(args, family)
    # No --lambda_grid means nothing is actually selected on valid (evaluate_block's
    # own grid loop below has exactly one candidate either way) -- the only thing left
    # for valid to do is fit a decision threshold that a threshold-free metric
    # (AUC_within_protein) never reads. Merging valid into test then hands the WHOLE
    # held-out block to the metric that matters instead of halving it away for nothing,
    # same reasoning behind cold_split_pools' own merge_valid_test docstring. A real
    # --lambda_grid still needs the honest split: picking a lambda ON test would leak
    # into the very AUC being reported.
    train_pool, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share,
        excluded_lipids=excluded_species,
        merge_valid_test=not bool(args.lambda_grid),
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

    protein_key = (
        _protein_kernel_cache_key(args, all_proteins, train_proteins)
        if kernel_cache is not None else None
    )
    if protein_key is not None and protein_key in kernel_cache:
        protein_kernel, protein_index = kernel_cache[protein_key]
    else:
        # One kernel over train + held-out entities, computed once and sliced below --
        # an out-of-sample protein/lipid is just another row of the same kernel,
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
        if protein_key is not None:
            kernel_cache[protein_key] = (protein_kernel, protein_index)

    lipid_key = (
        _lipid_kernel_cache_key(args, all_lipids, train_lipids)
        if kernel_cache is not None else None
    )
    if lipid_key is not None and lipid_key in kernel_cache:
        lipid_kernel, lipid_index = kernel_cache[lipid_key]
    else:
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
        if lipid_key is not None:
            kernel_cache[lipid_key] = (lipid_kernel, lipid_index)

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

    # Threshold comes from TRAIN, never from the held-out block. The held-out lipid
    # group stands in for a genuinely new lipid, whose labels do not exist at
    # prediction time -- so nothing about it may feed the cutoff either, or its
    # reported BA/F1 would be "the best cutoff achievable knowing the answer", not
    # what the model would actually do on an unseen lipid. Train rows are the only
    # labels a production run would legitimately have. (A fixed 0.5 cut is still not
    # an option -- a Kron-RLS score is not a calibrated probability, see
    # best_threshold_for_metric's own docstring.)
    # Kp @ A @ Kl over the train entities themselves -- one small rectangle
    # (n_train_proteins x n_train_lipids), then a VECTORISED gather of one cell per
    # train row. The row-at-a-time Python loop this replaces dominated the whole fit
    # (measured: ~70 CPU-seconds per descriptor combination against ~14 without it) --
    # train_pool is the big pool here, thousands of rows, scored once per block.
    train_score_matrix = predict_kronrls(coefficients, kp_train, kl_train)
    train_protein_position = {name: position for position, name in enumerate(train_proteins)}
    train_lipid_position = {name: position for position, name in enumerate(train_lipids)}
    train_scores = train_score_matrix[
        train_pool["LTPProtein"].map(train_protein_position).to_numpy(),
        train_pool["FullIdentityOfLipid"].map(train_lipid_position).to_numpy(),
    ]
    threshold, _ = best_threshold_for_metric(
        train_pool["Interaction"].to_numpy(), train_scores, metric=threshold_metric,
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

    # Constant across seeds (the excluded species set doesn't change with `seed`) --
    # kernel_cache makes repeated calls within one run free after the first. Both
    # reported side by side: whole-molecule and head-group-only can disagree (a
    # block isolated on its head group can still resemble something in train on its
    # acyl tails, or vice versa).
    block_similarity = block_tanimoto_similarity(table, excluded_species, units_cache=kernel_cache)
    block_headgroup_similarity = block_tanimoto_headgroup_similarity(
        table, excluded_species, units_cache=kernel_cache
    )

    return {
        "family": family,
        "seed": seed,
        "protein_lambda": protein_lambda,
        "lipid_lambda": lipid_lambda,
        "threshold": threshold,
        "valid_ba": valid_metrics["balanced_accuracy"],
        "valid_f1": valid_metrics["F1"],
        "valid_sensitivity": valid_metrics["sensitivity"],
        "valid_specificity": valid_metrics["specificity"],
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
        "block_tanimoto_similarity": block_similarity,
        "block_tanimoto_headgroup_similarity": block_headgroup_similarity,
        "train_proteins": len(train_proteins),
        "train_lipids": len(train_lipids),
        "valid_rows": len(valid_pool),
        "test_rows": len(test_pool),
        # Full test-block confusion matrix at `threshold` -- report-file-compatible
        # bare keys (scripts/tools/run_cron.py), not duplicated under a test_ prefix
        # since these ARE test-only concepts (same convention a network's own
        # test_metrics_*.txt report uses).
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


def _parse_lambda_grid(text: str) -> list[tuple[float, float]]:
    values = [float(part) for part in text.split(",") if part.strip()]
    return list(itertools.product(values, values))


def select_global_lambda(
    table: pd.DataFrame, families: list[str], seeds: list[int], args: argparse.Namespace
) -> tuple[tuple[float, float], float]:
    """One (protein_lambda, lipid_lambda) pair for EVERY (family, seed) block --
    --lambda_selection=global's counterpart to the per-block grid search
    evaluate_block otherwise does on its own.

    For each candidate in --lambda_grid, forces every block to fit with exactly
    that pair (by handing it a copy of `args` whose lambda_grid is that one
    candidate) and averages the block's own --select_metric valid score across
    ALL of them -- not just one block's valid set, so the winner is universal
    across every group AND every seed, not tuned per block the way the default
    (per_group) mode is. Re-fits every block once per candidate (the same total
    work the per_group grid search already does, just aggregated the other way),
    then whichever candidate wins is handed back to build_report to fit the real,
    reported pass with a single-candidate grid.
    """
    grid = args.lambda_grid or [(args.protein_lambda, args.lipid_lambda)]
    metric_column = {"auc": "valid_auc", "ba": "valid_ba", "f1": "valid_f1"}[args.select_metric]
    probe_args = copy.copy(args)
    best_lambda, best_score = None, None
    # Shared across every candidate below: the kernel a (family, seed) block needs
    # does not depend on protein_lambda/lipid_lambda at all, so without this cache
    # evaluate_block would rebuild the identical protein/lipid kernel len(grid)
    # times per block -- pure waste that used to be cheap enough not to notice, and
    # got much more visible once the descriptor sets it builds from (chain/hbond/
    # heavy/unsaturation, POCKET_EXTRA_NAMES, molformer) got heavier to compute.
    kernel_cache: dict = {}
    for candidate in grid:
        probe_args.lambda_grid = [candidate]
        scores = [
            evaluate_block(table, family, seed, probe_args, kernel_cache=kernel_cache)[
                metric_column
            ]
            for family in families
            for seed in seeds
        ]
        scores = [score for score in scores if not np.isnan(score)]
        if not scores:
            continue
        aggregate = float(np.mean(scores))
        if best_score is None or aggregate > best_score:
            best_score, best_lambda = aggregate, candidate
    if best_lambda is None:
        raise ValueError(
            "select_global_lambda: no --lambda_grid candidate produced a valid "
            f"{args.select_metric} score on any (family, seed) block"
        )
    return best_lambda, best_score


def build_report(table: pd.DataFrame, families: list[str], seeds: list[int], args) -> pd.DataFrame:
    if getattr(args, "lambda_selection", "per_group") == "global":
        if not args.lambda_grid:
            raise ValueError(
                "--lambda_selection=global has nothing to choose between without "
                "--lambda_grid (with it unset, both per_group and global trivially "
                "reduce to the same single --protein_lambda/--lipid_lambda default "
                "-- pass e.g. --lambda_grid=0.01,0.1,1,10,100)"
            )
        chosen_lambda, chosen_score = select_global_lambda(table, families, seeds, args)
        print(
            f"--lambda_selection=global: protein_lambda={chosen_lambda[0]}, "
            f"lipid_lambda={chosen_lambda[1]} (mean {args.select_metric}={chosen_score:.4f} "
            "across every family/seed block)\n"
        )
        args = copy.copy(args)
        args.lambda_grid = [chosen_lambda]
    # Shared across every (family, seed) block: under lipid_coldsplit the protein
    # kernel is identical for all of them (no protein is ever excluded), and a
    # family's lipid kernel is identical across all its seeds (train is untouched by
    # balance_pool_negatives) -- without this, each block paid the full descriptor
    # computation (chain/hbond/heavy/unsaturation, POCKET_EXTRA_NAMES, molformer)
    # from scratch every single time. See _protein_kernel_cache_key/
    # _lipid_kernel_cache_key for exactly what is/isn't shared.
    kernel_cache: dict = {}
    rows = [
        evaluate_block(table, family, seed, args, kernel_cache=kernel_cache)
        for family in families for seed in seeds
    ]
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


def build_parser() -> argparse.ArgumentParser:
    """The full kronrls_baseline.py CLI, minus `.parse_args()` -- shared with
    scripts/tools/run_cron.py so a label-driven runner does not duplicate every flag
    (and cannot silently drift from this file's own set of them).
    """
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
            "tanimoto", "tanimoto_headgroup", "molformer", "explicit", "explicit_subset",
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
        "--lambda_selection", default="per_group", choices=("per_group", "global"),
        help=(
            "per_group (default): each (family, seed) block picks its own best "
            "--lambda_grid candidate independently -- lets each held-out block's "
            "regularization fit its own valid set, but is not one fixed deployed "
            "model. global: one (protein_lambda, lipid_lambda) pair for EVERY "
            "family and EVERY seed (select_global_lambda), chosen by the mean "
            "--select_metric valid score averaged across all of them -- the "
            "question 'would ONE regularization strength, not retuned per unknown "
            "lipid class, still generalize'. Only takes effect with --lambda_grid."
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
    args = build_parser().parse_args()
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
