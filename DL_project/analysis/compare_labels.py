#!/usr/bin/env python3
"""Compare two `label` configurations via matched (exclusion_set, seed) pairs.

Usage: python3 compare_labels.py CANDIDATE_LABEL BASELINE_LABEL [--table PATH]

For every metric in METRICS, computes candidate - baseline over matched
(exclusion_set, seed) pairs (latest row per pair, per label) and reports:
  - overall: mean diff, median diff, std delta, improved/worsened counts, n
  - by group: mean diff, median diff, std delta, improved/worsened counts, n
    when --by-groups is passed

Higher-is-better metrics count diff > 0 as improved; for `loss`
(lower is better) diff < 0 counts as improved.

Prints to stdout; does not write any file.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from build_metrics_table import PROJECT_ROOT

METRICS = (
    ("checkpoint_valid_balanced_accuracy", "checkpoint valid BA", True),
    ("max_valid_balanced_accuracy", "max valid BA", True),
    ("best_valid_F1", "best valid F1", True),
    ("balanced_accuracy", "test BA", True),
    ("F1", "test F1", True),
    ("sensitivity", "test sensitivity", True),
    ("specificity", "test specificity", True),
    ("precision", "test precision", True),
    ("loss", "test loss", False),
    ("TP", "test TP", True),
    ("FP", "test FP", False),
    ("FN", "test FN", False),
    ("TN", "test TN", True),
)

# Computed rate metrics derived from confusion-matrix counts, keyed by
# label -> (numerator_field, denominator_fields, higher_is_better).
# FPR/FNR complement specificity/sensitivity but are normalized by class
# size, so they stay comparable across exclusion groups of different sizes
# (unlike raw TP/FP/FN/TN diffs above).
RATE_METRICS = (
    ("FPR (FP/(FP+TN))", "FP", ("FP", "TN"), False),
    ("FNR (FN/(FN+TP))", "FN", ("FN", "TP"), False),
)


def read_table_rows(table_path: Path) -> tuple[list[str], list[list[str]]]:
    with table_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def column_index(header: list[str], name: str) -> int:
    return header.index(name)


def latest_rows_for_label(
    header: list[str], rows: list[list[str]], label: str
) -> dict[tuple[str, str], list[str]]:
    idx_label = column_index(header, "label")
    idx_exclusion = column_index(header, "exclusion_set")
    idx_seed = column_index(header, "seed")
    idx_datetime = column_index(header, "datetime")

    latest: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        if row[idx_label] != label:
            continue
        key = (row[idx_exclusion], row[idx_seed])
        if key not in latest or row[idx_datetime] > latest[key][idx_datetime]:
            latest[key] = row
    return latest


def numeric(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None  # filter NaN


def paired_values_for_metric(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
    metric: str,
) -> tuple[list[float], list[float], list[float]]:
    idx = column_index(header, metric)
    baseline_values = []
    candidate_values = []
    diffs = []
    for key in common:
        a = numeric(baseline[key][idx])
        b = numeric(candidate[key][idx])
        if a is not None and b is not None:
            baseline_values.append(a)
            candidate_values.append(b)
            diffs.append(b - a)
    return baseline_values, candidate_values, diffs


def stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def paired_rate_values(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
    numerator_field: str,
    denominator_fields: tuple[str, str],
) -> tuple[list[float], list[float], list[float]]:
    idx_num = column_index(header, numerator_field)
    idx_den = [column_index(header, f) for f in denominator_fields]
    baseline_rates = []
    candidate_rates = []
    diffs = []
    for key in common:
        row_a, row_b = baseline[key], candidate[key]
        num_a, num_b = numeric(row_a[idx_num]), numeric(row_b[idx_num])
        den_a = sum(numeric(row_a[i]) or 0.0 for i in idx_den)
        den_b = sum(numeric(row_b[i]) or 0.0 for i in idx_den)
        if num_a is None or num_b is None or den_a == 0 or den_b == 0:
            continue
        rate_a, rate_b = num_a / den_a, num_b / den_b
        baseline_rates.append(rate_a)
        candidate_rates.append(rate_b)
        diffs.append(rate_b - rate_a)
    return baseline_rates, candidate_rates, diffs


def format_overall(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
) -> str:
    lines = [
        f"{'metric':22s}  {'mean_diff':>10s}  {'median_diff':>11s}  {'std_delta':>9s}  improved  worsened  n"
    ]
    for field, label, higher_better in METRICS:
        baseline_values, candidate_values, values = paired_values_for_metric(
            header, baseline, candidate, common, field
        )
        if not values:
            continue
        improved = (
            sum(1 for d in values if d > 0)
            if higher_better
            else sum(1 for d in values if d < 0)
        )
        worsened = len(values) - improved
        std_delta = stddev(candidate_values) - stddev(baseline_values)
        lines.append(
            f"{label:22s}  {statistics.mean(values):+10.4f}  "
            f"{statistics.median(values):+11.4f}  {std_delta:+9.4f}  "
            f"{improved:8d}  {worsened:8d}  {len(values)}"
        )
    return "\n".join(lines)


def format_by_group(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
) -> str:
    by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key in common:
        by_group[key[0]].append(key)

    sections = []
    for group in sorted(by_group):
        keys = by_group[group]
        lines = [f"{group} (n={len(keys)}):"]
        lines.append(
            f"  {'metric':22s}  {'mean_diff':>10s}  {'median_diff':>11s}  {'std_delta':>9s}  improved  worsened  n"
        )
        for field, label, higher_better in METRICS:
            baseline_values, candidate_values, values = paired_values_for_metric(
                header, baseline, candidate, keys, field
            )
            if not values:
                continue
            improved = (
                sum(1 for d in values if d > 0)
                if higher_better
                else sum(1 for d in values if d < 0)
            )
            worsened = len(values) - improved
            std_delta = stddev(candidate_values) - stddev(baseline_values)
            lines.append(
                f"  {label:22s}  {statistics.mean(values):+10.4f}  "
                f"{statistics.median(values):+11.4f}  {std_delta:+9.4f}  "
                f"{improved:8d}  {worsened:8d}  {len(values)}"
            )
        for label, numerator_field, denominator_fields, higher_better in RATE_METRICS:
            baseline_rates, candidate_rates, values = paired_rate_values(
                header, baseline, candidate, keys, numerator_field, denominator_fields
            )
            if not values:
                continue
            improved = (
                sum(1 for d in values if d > 0)
                if higher_better
                else sum(1 for d in values if d < 0)
            )
            worsened = len(values) - improved
            std_delta = stddev(candidate_rates) - stddev(baseline_rates)
            lines.append(
                f"  {label:22s}  {statistics.mean(values):+10.4f}  "
                f"{statistics.median(values):+11.4f}  {std_delta:+9.4f}  "
                f"{improved:8d}  {worsened:8d}  {len(values)}"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def format_rate_metrics(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
) -> str:
    lines = [
        f"{'metric':22s}  {'mean_diff':>10s}  {'median_diff':>11s}  {'std_delta':>9s}  improved  worsened  n"
    ]
    for label, numerator_field, denominator_fields, higher_better in RATE_METRICS:
        baseline_rates, candidate_rates, values = paired_rate_values(
            header, baseline, candidate, common, numerator_field, denominator_fields
        )
        if not values:
            continue
        improved = (
            sum(1 for d in values if d > 0)
            if higher_better
            else sum(1 for d in values if d < 0)
        )
        worsened = len(values) - improved
        std_delta = stddev(candidate_rates) - stddev(baseline_rates)
        lines.append(
            f"{label:22s}  {statistics.mean(values):+10.4f}  "
            f"{statistics.median(values):+11.4f}  {std_delta:+9.4f}  "
            f"{improved:8d}  {worsened:8d}  {len(values)}"
        )
    return "\n".join(lines)


def format_class_recall_gap(
    header: list[str],
    baseline: dict[tuple[str, str], list[str]],
    candidate: dict[tuple[str, str], list[str]],
    common: list[tuple[str, str]],
) -> str:
    idx_sens = column_index(header, "sensitivity")
    idx_spec = column_index(header, "specificity")
    diffs = []
    for key in common:
        sa, spa = numeric(baseline[key][idx_sens]), numeric(baseline[key][idx_spec])
        sb, spb = numeric(candidate[key][idx_sens]), numeric(candidate[key][idx_spec])
        if None not in (sa, spa, sb, spb):
            diffs.append(abs(sb - spb) - abs(sa - spa))
    if not diffs:
        return "abs(sensitivity-specificity) gap: no matched pairs with both metrics"
    increased = sum(1 for d in diffs if d > 0)
    decreased = sum(1 for d in diffs if d < 0)
    return (
        f"abs(sensitivity-specificity) gap: mean_diff={statistics.mean(diffs):+.4f} "
        f"n={len(diffs)} increased={increased} decreased={decreased}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_label")
    parser.add_argument("baseline_label")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument(
        "--by-groups",
        "--by_groups",
        action="store_true",
        help="Print per-exclusion-group comparison sections.",
    )
    args = parser.parse_args()

    header, rows = read_table_rows(args.table)
    baseline = latest_rows_for_label(header, rows, args.baseline_label)
    candidate = latest_rows_for_label(header, rows, args.candidate_label)

    if not baseline:
        raise SystemExit(f"No rows found with label={args.baseline_label!r} in {args.table}")
    if not candidate:
        raise SystemExit(f"No rows found with label={args.candidate_label!r} in {args.table}")

    common = sorted(set(baseline) & set(candidate))
    if not common:
        raise SystemExit(
            f"No matched (exclusion_set, seed) pairs between "
            f"{args.candidate_label!r} ({len(candidate)} rows) and "
            f"{args.baseline_label!r} ({len(baseline)} rows)"
        )

    print(f"Comparison: {args.candidate_label!r} vs {args.baseline_label!r} (baseline)")
    print(
        f"baseline rows: {len(baseline)} | candidate rows: {len(candidate)} | "
        f"matched pairs: {len(common)}"
    )
    print()
    print("=== Overall ===")
    print(format_overall(header, baseline, candidate, common))
    print()
    print("=== Confusion rates ===")
    print(format_rate_metrics(header, baseline, candidate, common))
    print()
    print("===", format_class_recall_gap(header, baseline, candidate, common), "===")
    if args.by_groups:
        print()
        print("=== By group ===")
        print(format_by_group(header, baseline, candidate, common))


if __name__ == "__main__":
    main()
