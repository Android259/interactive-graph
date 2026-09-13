#!/usr/bin/env python3
"""Per-(label, excluded lipid class) test-metric aggregates from metrics_summary.csv.

Reads only: metrics_summary.csv. Never touches a checkpoint, model, or
training loop -- pure CSV arithmetic, same rows `compare_labels.py` and
`summarize_label.py` already read.

Answers, for an arbitrary list of `--lipid_coldsplit` labels: for each
excluded lipid-class group (anionic/choline/phosphorus_free/sphingolipids),
mean/std/SEM over the 5 seeds of the primary ranking metric
(`AUC_within_protein_pairs`, plus the per-protein-average companion and their
protein counts), pooled test BA/sens/spec/AUC as context, and stability flags
(`converged`, `collapse_epoch_count`, `nan_epoch_count`, loss range) needed to
catch pathological seeds the way `files/lipid_coldsplit_architecture_direction.md`
already flags them for `geometric_edge_mlp_protgeom_full_lcs`.

Usage:
    python3 analysis/lcs_new_configs_summary.py LABEL [LABEL ...]

Prints one block per label to stdout; writes nothing.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_metrics_table import PROJECT_ROOT  # noqa: E402
from compare_labels import (  # noqa: E402
    column_index,
    latest_rows_for_label,
    numeric,
    read_table_rows,
)

GROUP_ORDER = (
    "groups_anionic",
    "groups_choline",
    "groups_phosphorus_free",
    "groups_sphingolipids",
)

# metric column -> display name
METRIC_COLS = (
    ("AUC_within_protein_pairs", "AUC_within_protein_pairs"),
    ("AUC_within_protein_pairs_proteins", "  proteins_contributing"),
    ("AUC_within_protein", "AUC_within_protein (per-protein mean)"),
    ("AUC_within_protein_proteins", "  proteins_averaged"),
    ("balanced_accuracy", "pooled test BA"),
    ("sensitivity", "pooled test sensitivity"),
    ("specificity", "pooled test specificity"),
    ("AUC", "pooled test AUC"),
    ("loss", "test loss"),
)

STABILITY_COLS = (
    "converged",
    "collapse_epoch_count",
    "nan_epoch_count",
    "run_status",
    "final_train_loss",
    "min_valid_loss",
)


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def sem(values: list[float]) -> float | None:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values) / (len(values) ** 0.5)


def fmt(value: float | None, digits: int = 4) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def summarize_label(header: list[str], rows: list[list[str]], label: str) -> None:
    latest = latest_rows_for_label(header, rows, label)
    print(f"\n=== {label} ({len(latest)} rows) ===")
    if not latest:
        print("  no rows found")
        return

    idx_group = column_index(header, "exclusion_set")
    by_group: dict[str, list[list[str]]] = {}
    for (group, _seed), row in latest.items():
        by_group.setdefault(group, []).append(row)

    groups_present = [g for g in GROUP_ORDER if g in by_group] + [
        g for g in by_group if g not in GROUP_ORDER
    ]

    # Per-metric table, one row per group + ALL (pooled).
    for col, name in METRIC_COLS:
        try:
            idx = column_index(header, col)
        except ValueError:
            print(f"  {name}: column not in table")
            continue
        line = [f"  {name:38s}"]
        pooled_vals: list[float] = []
        for group in groups_present:
            vals = [numeric(r[idx]) for r in by_group[group]]
            vals = [v for v in vals if v is not None]
            pooled_vals.extend(vals)
            m, s = mean(vals), sem(vals)
            n = len(vals)
            line.append(f"{group.replace('groups_', ''):>16s}={fmt(m)}±{fmt(s)}(n={n})")
        m, s = mean(pooled_vals), sem(pooled_vals)
        line.append(f"{'ALL':>16s}={fmt(m)}±{fmt(s)}(n={len(pooled_vals)})")
        print(" ".join(line))

    # Stability flags, pooled and per group.
    print("  -- stability --")
    idx_conv = column_index(header, "converged")
    idx_collapse = column_index(header, "collapse_epoch_count")
    idx_nan = column_index(header, "nan_epoch_count")
    idx_status = column_index(header, "run_status")
    idx_ftl = column_index(header, "final_train_loss")
    idx_mvl = column_index(header, "min_valid_loss")
    idx_tloss = column_index(header, "loss")
    for group in groups_present:
        rs = by_group[group]
        n = len(rs)
        n_converged = sum(1 for r in rs if r[idx_conv] in ("True", "1"))
        collapse = [numeric(r[idx_collapse]) for r in rs]
        collapse = [v for v in collapse if v is not None]
        nan_ep = [numeric(r[idx_nan]) for r in rs]
        nan_ep = [v for v in nan_ep if v is not None]
        non_complete = [r[idx_status] for r in rs if r[idx_status] != "complete"]
        test_loss = [numeric(r[idx_tloss]) for r in rs]
        test_loss = [v for v in test_loss if v is not None]
        print(
            f"    {group.replace('groups_', ''):>16s}: converged={n_converged}/{n}"
            f"  collapse_epochs(mean/max)={fmt(mean(collapse),1)}/{fmt(max(collapse) if collapse else None,1)}"
            f"  nan_epochs(mean/max)={fmt(mean(nan_ep),1)}/{fmt(max(nan_ep) if nan_ep else None,1)}"
            f"  non_complete={len(non_complete)}"
            f"  test_loss(mean/max)={fmt(mean(test_loss))}/{fmt(max(test_loss) if test_loss else None)}"
        )


def per_seed_dump(header: list[str], rows: list[list[str]], label: str) -> None:
    """Print one raw line per (group, seed): sens/spec/loss/converged/AUC_wp_pairs.

    For flagging pathological seeds (sens/spec collapsed near 0/1, loss far
    above ~0.69 cross-entropy at chance, or `converged` unset) the same way
    `files/geometric_edge_descriptors_baseline_selection_results.md` section
    4.2 already did for `geometric_edge_mlp_protgeom_full_lcs`.
    """
    latest = latest_rows_for_label(header, rows, label)
    print(f"\n=== {label}: per-seed raw ===")
    idx_group = column_index(header, "exclusion_set")
    idx_seed = column_index(header, "seed")
    idx_sens = column_index(header, "sensitivity")
    idx_spec = column_index(header, "specificity")
    idx_loss = column_index(header, "loss")
    idx_conv = column_index(header, "converged")
    idx_pairs = column_index(header, "AUC_within_protein_pairs")
    for group in GROUP_ORDER:
        for (g, seed), row in sorted(latest.items()):
            if g != group:
                continue
            print(
                f"  {group.replace('groups_', ''):>16s} seed={seed}"
                f"  sens={fmt(numeric(row[idx_sens]))}"
                f"  spec={fmt(numeric(row[idx_spec]))}"
                f"  loss={fmt(numeric(row[idx_loss]))}"
                f"  AUC_wp_pairs={fmt(numeric(row[idx_pairs]))}"
                f"  converged={row[idx_conv]}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="+")
    parser.add_argument(
        "--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv"
    )
    parser.add_argument(
        "--per-seed",
        action="store_true",
        help="also print one raw line per (group, seed) for spotting collapsed runs",
    )
    args = parser.parse_args()

    header, rows = read_table_rows(args.table)
    for label in args.labels:
        summarize_label(header, rows, label)
        if args.per_seed:
            per_seed_dump(header, rows, label)


if __name__ == "__main__":
    main()
