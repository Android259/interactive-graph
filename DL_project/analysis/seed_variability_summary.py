#!/usr/bin/env python3
"""Sensitivity/specificity seed-to-seed variability for labels that already have
completed runs in metrics_summary.csv -- read-only, no re-run of summarize_label.py/
generate_label_report.sh needed (those regenerate graphics and, for --summarize,
call full_label_report.py's forward pass over every checkpoint; this only reads the
table).

For each label: per exclusion group, the std of that group's seeds' sensitivity
values and, separately, of specificity; then mean/median of those per-group stds
across groups (analysis.summarize_label.format_seed_variability) -- how much a
group's own sens/spec typically jumps from seed to seed, distinct from
format_class_recall_gap's |sensitivity-specificity| gap (how far the two sit apart
within one run, not how much either moves across runs). Test BA and the gap line are
printed alongside for context, same numbers already in graphics/<label>/<label>.md.

Usage: python3 analysis/seed_variability_summary.py LABEL [LABEL ...] [--exclude-groups=NAME,NAME]
"""
from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from build_metrics_table import PROJECT_ROOT
from compare_labels import latest_rows_for_label, numeric, read_table_rows
from summarize_label import (
    format_class_recall_gap,
    format_seed_variability,
    safe_column_index,
    values_for_metric,
)


def _normalize_group_name(name: str) -> str:
    """Case/separator-insensitive match, same convention as scripts/settings.sh's
    normalize_group_name (- and _ interchangeable) -- also strips a leading
    "groups_" (metrics_summary.csv's own exclusion_set prefix, e.g. "groups_ML"),
    so --exclude-groups=ML matches without spelling out the prefix.
    """
    name = name.lower().replace("-", "_")
    if name.startswith("groups_"):
        name = name[len("groups_"):]
    return name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="+")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument(
        "--exclude-groups",
        "--exclude_groups",
        default="",
        help="Comma-separated exclusion-group names to drop before computing every "
        "stat below (e.g. data-starved groups with too few rows to be meaningful) "
        "-- matched case/separator-insensitively against metrics_summary.csv's own "
        "exclusion_set column.",
    )
    args = parser.parse_args()
    excluded = {_normalize_group_name(n) for n in args.exclude_groups.split(",") if n}

    header, all_rows = read_table_rows(args.table)

    for label in args.labels:
        rows = latest_rows_for_label(header, all_rows, label)
        print(f"=== {label} ===")
        if not rows:
            print(f"No rows found with label={label!r} in {args.table}")
            print()
            continue
        keys = sorted(k for k in rows if _normalize_group_name(k[0]) not in excluded)
        if excluded:
            dropped = sorted(rows.keys() - set(keys))
            print(f"(excluded groups dropped {len(dropped)} rows: {dropped})")
        for metric, field in (("BA", "balanced_accuracy"), ("sensitivity", "sensitivity"), ("specificity", "specificity")):
            values = values_for_metric(header, rows, keys, field)
            if values:
                print(
                    f"test {metric}: mean={statistics.mean(values):.4f} "
                    f"median={statistics.median(values):.4f} n={len(values)}"
                )
        print(format_class_recall_gap(header, rows, keys))
        print(format_seed_variability(header, rows, keys))
        print()


if __name__ == "__main__":
    main()
