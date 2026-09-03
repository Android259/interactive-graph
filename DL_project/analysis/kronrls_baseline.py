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

Both kernels are pluggable and accept arbitrary externally supplied vectors, not just
the two built-in descriptor sets:

    --protein_kernel {pocket13,pocket23,pocket_subset,custom_features,custom_kernel}
    --lipid_kernel   {tanimoto,explicit,explicit_subset,custom_features,custom_kernel}

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
    python3 analysis/kronrls_baseline.py --lipid_kernel custom_features \\
        --lipid_features my_lipid_vectors.csv --lambda_grid 0.01,0.1,1,10,100
    python3 analysis/kronrls_baseline.py --lipid_kernel explicit_subset \\
        --lipid_descriptor_names=logp,tpsa,molar_refractivity,rotatable_bond_count,\\
aromatic_ring_count,ring_count --lambda_grid 0.01,0.1,1,10,100

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
from dataloader.sampler import lipid_class_series  # noqa: E402
from null_model import per_lipid_auc, per_pair_auc, per_protein_auc  # noqa: E402
from training.pair_baseline_common import (  # noqa: E402
    aggregate_pair_labels,
    auc_p_vs_u,
    build_lipid_kernel,
    build_protein_kernel,
    predict_kronrls,
    raw_double_cold_pool,
    raw_single_cold_pool,
    split_held_pairs,
    two_step_kronrls,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")


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
    """Fit and score one (family, seed) cold-split block."""
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

    labels = aggregate_pair_labels(train_pool).reindex(index=train_proteins, columns=train_lipids)
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
        valid_auc, _ = _score_pool(
            valid_pool, coefficients, protein_kernel, protein_index,
            lipid_kernel, lipid_index, train_proteins, train_lipids,
        )
        candidate = (valid_auc, protein_lambda, lipid_lambda, coefficients)
        if best is None:
            best = candidate
            continue
        best_auc = best[0]
        if not np.isnan(valid_auc) and (np.isnan(best_auc) or valid_auc > best_auc):
            best = candidate
    valid_auc, protein_lambda, lipid_lambda, coefficients = best

    test_auc, test_scored = _score_pool(
        test_pool, coefficients, protein_kernel, protein_index,
        lipid_kernel, lipid_index, train_proteins, train_lipids,
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
    summary = report.groupby("family")[
        ["valid_auc", "test_auc", "pair_auc", "per_protein_auc", "per_lipid_auc"]
    ].agg(["mean", "std"])
    print(summary)
    print()
    if args.show_per_block:
        group_sizes = report.groupby("family")[
            ["n_pair_groups", "n_proteins", "n_lipid_classes"]
        ].mean()
        print(group_sizes)
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
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument(
        "--split_mode", default="double", choices=("single", "double"),
        help=(
            "single: hold out only the protein family (--excluded_groups parity, "
            "lipid classes stay in training). double: also hold out lipid head-group "
            "classes (--double_coldsplit parity)."
        ),
    )
    parser.add_argument(
        "--share", type=float, default=0.8,
        help="lipid-class positive-coverage share held out, for --split_mode double",
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
        choices=("tanimoto", "explicit", "explicit_subset", "custom_features", "custom_kernel"),
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
            "0.01,0.1,1,10,100; picked per (family, seed) by validation-block AUC, "
            "then re-scored on the test block. Overrides --protein_lambda/--lipid_lambda."
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

    families = [name for name in args.families.split(",") if name]
    seeds = [int(value) for value in args.seeds.split(",")]

    report = build_report(table, families, seeds, args)
    print_report(report, args)

    if args.out:
        report.to_json(args.out, orient="records", indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
