#!/usr/bin/env python3
"""Append a mean/median/std analysis for one `label` to a text file.

Usage: python3 analyze_label_metrics.py LABEL [--output PATH] [--table PATH]

Selects the latest row per (exclusion_set, seed) with the given `label`
value in metrics_summary.csv, then reports:
  - overall mean/median/std/n for run-level metrics
  - per-group mean/std for the same metrics
  - per-subgroup mean/std, read from test_metrics/*.txt reports

The result is appended to --output (default metrics_summary_label_analysis.txt),
not overwritten, so repeated runs for different labels accumulate in one file.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from build_metrics_table import PROJECT_ROOT
from plot_metric_by_subgroup import (
    SUBGROUP_COLUMNS,
    aggregate_subgroups,
    parse_report,
)

RUN_METRICS = (
    "checkpoint_valid_balanced_accuracy",
    "max_valid_balanced_accuracy",
    "best_valid_F1",
    "balanced_accuracy",
    "F1",
    "sensitivity",
    "specificity",
    "precision",
    "loss",
)
SUBGROUP_METRICS = tuple(
    metric for metric in SUBGROUP_COLUMNS[1:] if metric in RUN_METRICS
) or ("balanced_accuracy", "F1", "sensitivity", "specificity", "precision", "loss")


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


def summarize_overall(
    header: list[str], selected: list[list[str]], metrics: tuple[str, ...]
) -> list[dict[str, object]]:
    rows = []
    for metric in metrics:
        idx = column_index(header, metric)
        values = [v for v in (numeric(row[idx]) for row in selected) if v is not None]
        if not values:
            continue
        rows.append(
            {
                "metric": metric,
                "mean": statistics.fmean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
                "n": len(values),
            }
        )
    return rows


def summarize_by_group(
    header: list[str], selected: list[list[str]], metrics: tuple[str, ...]
) -> list[dict[str, object]]:
    idx_exclusion = column_index(header, "exclusion_set")
    idx_seed = column_index(header, "seed")
    by_group: dict[str, list[list[str]]] = defaultdict(list)
    for row in selected:
        by_group[row[idx_exclusion]].append(row)

    rows = []
    for group in sorted(by_group):
        group_rows = by_group[group]
        entry: dict[str, object] = {
            "group": group,
            "n": len(group_rows),
            "seeds": ",".join(sorted({row[idx_seed] for row in group_rows})),
        }
        for metric in metrics:
            idx = column_index(header, metric)
            values = [
                v for v in (numeric(row[idx]) for row in group_rows) if v is not None
            ]
            if values:
                mean = statistics.fmean(values)
                std = statistics.stdev(values) if len(values) > 1 else 0.0
                entry[metric] = f"{mean:.4f}+/-{std:.4f}"
            else:
                entry[metric] = "n/a"
        rows.append(entry)
    return rows


def report_timestamp_to_datetime(timestamp: str) -> str:
    return datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")


def load_subgroup_reports(
    reports_root: Path, selected_datetimes: set[str]
) -> list[dict[str, object]]:
    reports = []
    for path in sorted(reports_root.rglob("test_metrics_*.txt")):
        try:
            report = parse_report(path, reports_root)
        except ValueError:
            continue
        if report_timestamp_to_datetime(report["timestamp"]) in selected_datetimes:
            reports.append(report)
    return reports


def format_overall(rows: list[dict[str, object]]) -> str:
    lines = ["Overall (mean / median / std / min / max / n):"]
    for row in rows:
        lines.append(
            f"  {row['metric']:32s} mean={row['mean']:.4f} median={row['median']:.4f} "
            f"std={row['std']:.4f} min={row['min']:.4f} max={row['max']:.4f} n={row['n']}"
        )
    return "\n".join(lines)


def format_by_group(rows: list[dict[str, object]], metrics: tuple[str, ...]) -> str:
    lines = ["By group (mean+/-std):"]
    for row in rows:
        metric_text = "  ".join(f"{m}={row[m]}" for m in metrics)
        lines.append(f"  {row['group']:24s} n={row['n']:2d} seeds={row['seeds']:12s} {metric_text}")
    return "\n".join(lines)


def format_by_subgroup(aggregates: list[dict[str, object]], metric: str) -> str:
    lines = [f"By subgroup, metric={metric} (mean+/-std, n, seeds, groups):"]
    for entry in aggregates:
        seeds = ",".join(entry["seeds"])
        groups = ",".join(entry["groups"])
        lines.append(
            f"  {entry['subgroup']:16s} {entry['mean']:.4f}+/-{entry['std']:.4f} "
            f"n={entry['count']:2d} seeds={seeds} groups={groups}"
        )
    return "\n".join(lines)


def build_report(label: str, table_path: Path, reports_root: Path) -> str:
    header, rows = read_table_rows(table_path)
    latest = latest_rows_for_label(header, rows, label)
    if not latest:
        raise SystemExit(f"No rows found with label={label!r} in {table_path}")

    selected = list(latest.values())
    idx_exclusion = column_index(header, "exclusion_set")
    idx_seed = column_index(header, "seed")
    groups = sorted({row[idx_exclusion] for row in selected})
    seeds = sorted({row[idx_seed] for row in selected})

    overall = summarize_overall(header, selected, RUN_METRICS)
    by_group = summarize_by_group(header, selected, RUN_METRICS)

    idx_datetime = column_index(header, "datetime")
    selected_datetimes = {row[idx_datetime] for row in selected}
    reports = load_subgroup_reports(reports_root, selected_datetimes)
    subgroup_sections = []
    for metric in SUBGROUP_METRICS:
        try:
            aggregates = aggregate_subgroups(reports, metric)
        except ValueError:
            continue
        if aggregates:
            subgroup_sections.append(format_by_subgroup(aggregates, metric))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        f"{'=' * 72}",
        f"label: {label}",
        f"generated: {timestamp}",
        f"rows (latest per group+seed): {len(selected)}",
        f"groups ({len(groups)}): {', '.join(g.removeprefix('groups_') for g in groups)}",
        f"seeds ({len(seeds)}): {', '.join(seeds)}",
        "",
        format_overall(overall),
        "",
        format_by_group(by_group, RUN_METRICS),
        "",
        *subgroup_sections,
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("label")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument(
        "--reports-root", type=Path, default=PROJECT_ROOT / "test_metrics"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "metrics_summary_label_analysis.txt",
    )
    args = parser.parse_args()

    report = build_report(args.label, args.table, args.reports_root)
    with args.output.open("a", encoding="utf-8") as handle:
        handle.write(report)
    print(f"Appended analysis for label={args.label!r} to {args.output}")


if __name__ == "__main__":
    main()
