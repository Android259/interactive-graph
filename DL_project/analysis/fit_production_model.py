#!/usr/bin/env python3
"""Fit the Kron-RLS model actually meant to be used for predictions -- ALL data in
one fit (no lipid held out, unlike every cold-split test run this project's cron work
has done so far), plus a decision threshold read off that SAME fit's own scores on
its own training rows (training.pair_baseline_common.train_threshold) -- one fit, one
threshold search, no second model, no fold split. The held-out cold-split runs
(scripts/run_cron.py --excluded_lipid_groups) stay exactly as they are -- this script
does not replace them, it is the separate step that comes AFTER a descriptor/kernel
recipe has already been validated that way.

Writes one artifact (--out, default data/production_model.npz) holding everything
needed to score a brand-new lipid later without retraining:
    coefficients        [n_proteins, n_lipids] Kron-RLS A matrix
    protein_kernel       [n_proteins, n_proteins]
    protein_names         ordered to match protein_kernel's rows/columns
    lipid_kernel         [n_lipids, n_lipids]
    lipid_names           ordered to match lipid_kernel's rows/columns
    threshold             single float
plus a config sidecar (same path, .json instead of .npz) with the descriptor names/
kernel types/lambdas, so a later run can tell what produced it.

    python3 analysis/fit_production_model.py \\
        --protein_descriptors pocket_volume_per_sasa,pocket_elongation,... \\
        --lipid_descriptors chain,hbond,experimental_lipid_volume \\
        --out data/production_model.npz
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from training.pair_baseline_common import (  # noqa: E402
    aggregate_pair_labels,
    build_lipid_kernel,
    build_protein_kernel,
    read_interactions,
    train_threshold,
    two_step_kronrls,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--protein_descriptors", required=True,
        help="comma-separated dataloader.pair_descriptors.PROTEIN_DESCRIPTOR_NAMES subset",
    )
    parser.add_argument(
        "--lipid_descriptors", required=True,
        help="comma-separated dataloader.pair_descriptors.LIPID_DESCRIPTOR_NAMES subset",
    )
    parser.add_argument("--protein_lambda", type=float, default=1.0)
    parser.add_argument("--lipid_lambda", type=float, default=1.0)
    parser.add_argument(
        "--threshold_metric", choices=("ba", "f1"), default="ba",
        help="ba/f1 -> balanced_accuracy/F1, same choice run_cron.py's --threshold_metric offers",
    )
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "data" / "production_model.npz")
    args = parser.parse_args()

    protein_names = [name.strip() for name in args.protein_descriptors.split(",") if name.strip()]
    lipid_names = [name.strip() for name in args.lipid_descriptors.split(",") if name.strip()]
    metric = "balanced_accuracy" if args.threshold_metric == "ba" else "F1"

    table = read_interactions()
    all_proteins = sorted(table["LTPProtein"].unique())
    all_lipids = sorted(table["FullIdentityOfLipid"].unique())
    print(f"table: {len(table)} rows, {len(all_proteins)} proteins, {len(all_lipids)} lipids")

    print("fitting on ALL data (nothing held out)...")
    protein_kernel, protein_index = build_protein_kernel(
        "pocket_subset", all_proteins, all_proteins, descriptor_names=protein_names,
    )
    lipid_kernel, lipid_index = build_lipid_kernel(
        "explicit_subset", table, all_lipids, all_lipids, descriptor_names=lipid_names,
    )
    labels = aggregate_pair_labels(table).reindex(index=all_proteins, columns=all_lipids)
    coefficients = two_step_kronrls(
        protein_kernel, lipid_kernel, labels.to_numpy(), args.protein_lambda, args.lipid_lambda
    )

    print("reading threshold off this same fit's own training scores...")
    threshold = train_threshold(
        table, all_proteins, all_lipids, protein_kernel, protein_index,
        lipid_kernel, lipid_index, coefficients, metric=metric,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        args.out,
        coefficients=coefficients,
        protein_kernel=protein_kernel,
        protein_names=np.array(all_proteins),
        lipid_kernel=lipid_kernel,
        lipid_names=np.array(all_lipids),
        threshold=np.array(threshold),
    )
    config_path = args.out.with_suffix(".json")
    config_path.write_text(json.dumps({
        "protein_descriptors": protein_names,
        "lipid_descriptors": lipid_names,
        "protein_lambda": args.protein_lambda,
        "lipid_lambda": args.lipid_lambda,
        "threshold_metric": args.threshold_metric,
        "threshold": threshold,
        "n_proteins": len(all_proteins),
        "n_lipids": len(all_lipids),
    }, indent=2))

    print()
    print("=== production model ===")
    print(f"protein_descriptors ({len(protein_names)}): {','.join(protein_names)}")
    print(f"lipid_descriptors ({len(lipid_names)}): {','.join(lipid_names)}")
    print(f"protein_lambda={args.protein_lambda}  lipid_lambda={args.lipid_lambda}")
    print(f"trained on: {len(all_proteins)} proteins x {len(all_lipids)} lipids (nothing held out)")
    print(f"threshold_metric={args.threshold_metric}")
    print(f"threshold: {threshold:.6f}")
    print(f"artifact: {args.out}")
    print(f"config: {config_path}")


if __name__ == "__main__":
    main()
