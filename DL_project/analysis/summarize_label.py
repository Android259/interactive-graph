#!/usr/bin/env python3
"""Summarize a single `label` configuration across (exclusion_set, seed) runs.

Usage: python3 summarize_label.py LABEL [--table PATH] [--by-groups]

For every metric in METRICS, computes mean/median/std over the latest row
per (exclusion_set, seed) pair for the given label and reports:
  - overall: mean, median, std, n
  - by group: mean, median, std, n when --by-groups is passed

Same metric set and confusion-rate derivations (FPR, FNR, sensitivity-
specificity gap) as compare_labels.py, but for a single label instead of a
candidate/baseline diff.

Prints to stdout; does not write any file.
"""

from __future__ import annotations

import argparse
import statistics
from collections import defaultdict
from pathlib import Path

from build_metrics_table import PROJECT_ROOT
from compare_labels import (
    RATE_METRICS,
    METRICS,
    column_index,
    latest_rows_for_label,
    numeric,
    read_table_rows,
)


def stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def values_for_metric(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
    metric: str,
) -> list[float]:
    idx = column_index(header, metric)
    values = []
    for key in keys:
        v = numeric(rows[key][idx])
        if v is not None:
            values.append(v)
    return values


def rate_values(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
    numerator_field: str,
    denominator_fields: tuple[str, str],
) -> list[float]:
    idx_num = column_index(header, numerator_field)
    idx_den = [column_index(header, f) for f in denominator_fields]
    values = []
    for key in keys:
        row = rows[key]
        num = numeric(row[idx_num])
        den = sum(numeric(row[i]) or 0.0 for i in idx_den)
        if num is None or den == 0:
            continue
        values.append(num / den)
    return values


def format_metrics_table(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
    indent: str = "",
) -> str:
    lines = [
        f"{indent}{'metric':22s}  {'mean':>10s}  {'median':>10s}  {'std':>9s}  n"
    ]
    for field, label, _higher_better in METRICS:
        values = values_for_metric(header, rows, keys, field)
        if not values:
            continue
        lines.append(
            f"{indent}{label:22s}  {statistics.mean(values):10.4f}  "
            f"{statistics.median(values):10.4f}  {stddev(values):9.4f}  {len(values)}"
        )
    for label, numerator_field, denominator_fields, _higher_better in RATE_METRICS:
        values = rate_values(header, rows, keys, numerator_field, denominator_fields)
        if not values:
            continue
        lines.append(
            f"{indent}{label:22s}  {statistics.mean(values):10.4f}  "
            f"{statistics.median(values):10.4f}  {stddev(values):9.4f}  {len(values)}"
        )
    return "\n".join(lines)


def format_class_recall_gap(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    idx_sens = column_index(header, "sensitivity")
    idx_spec = column_index(header, "specificity")
    gaps = []
    for key in keys:
        s, sp = numeric(rows[key][idx_sens]), numeric(rows[key][idx_spec])
        if s is not None and sp is not None:
            gaps.append(abs(s - sp))
    if not gaps:
        return "abs(sensitivity-specificity) gap: no rows with both metrics"
    return (
        f"abs(sensitivity-specificity) gap: mean={statistics.mean(gaps):.4f} "
        f"median={statistics.median(gaps):.4f} n={len(gaps)}"
    )


def format_by_group(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key in keys:
        by_group[key[0]].append(key)

    sections = []
    for group in sorted(by_group):
        group_keys = by_group[group]
        lines = [f"{group} (n={len(group_keys)}):"]
        lines.append(format_metrics_table(header, rows, group_keys, indent="  "))
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("label")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument(
        "--by-groups",
        "--by_groups",
        action="store_true",
        help="Print per-exclusion-group summary sections.",
    )
    args = parser.parse_args()

    header, all_rows = read_table_rows(args.table)
    rows = latest_rows_for_label(header, all_rows, args.label)

    if not rows:
        raise SystemExit(f"No rows found with label={args.label!r} in {args.table}")

    keys = sorted(rows)

    print(f"Summary: {args.label!r}")
    print(f"rows: {len(rows)}")
    print()
    print("=== Overall ===")
    print(format_metrics_table(header, rows, keys))
    print()
    print("===", format_class_recall_gap(header, rows, keys), "===")
    if args.by_groups:
        print()
        print("=== By group ===")
        print(format_by_group(header, rows, keys))


if __name__ == "__main__":
    main()
