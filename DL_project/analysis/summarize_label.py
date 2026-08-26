#!/usr/bin/env python3
"""Summarize a single `label` configuration across (exclusion_set, seed) runs.

Usage: python3 summarize_label.py LABEL [--table PATH] [--by-groups]

For every metric in METRICS, computes mean/median/std over the latest row
per (exclusion_set, seed) pair for the given label and reports:
  - a test/train/valid sensitivity+specificity table, one row per group
  - overall: mean, median, std, n (TP/FP/FN/TN excluded -- see EXCLUDED_FROM_TABLE)
  - by group: mean, median, std, n when --by-groups is passed

Same metric set and confusion-rate derivations (FPR, FNR, sensitivity-
specificity gap) as compare_labels.py, but for a single label instead of a
candidate/baseline diff.

checkpoint-epoch train/valid sensitivity/specificity (checkpoint_train_sensitivity,
checkpoint_train_specificity, checkpoint_valid_sensitivity,
checkpoint_valid_specificity) come from training/run_metrics.py and are only
present for runs finished after that module started recording them -- a run
from before then reads back as n/a in those columns, not zero or an error.

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
    latest_rows_for_label,
    numeric,
    read_table_rows,
)

# Dropped from the default metric table: raw confusion counts are not
# comparable across groups of different sizes (a small held-out group's TP=3
# and a large one's TP=30 say nothing side by side), and every ratio they are
# useful for -- sensitivity, specificity, FPR, FNR -- is already reported.
EXCLUDED_FROM_TABLE = {"TP", "FP", "FN", "TN"}

# (train field, valid field, test field) for the by-group sensitivity/
# specificity table. Test reuses METRICS' plain "sensitivity"/"specificity"
# (the checkpoint-epoch test-split values); train and valid are
# training/run_metrics.py's final-epoch and checkpoint-epoch equivalents.
TRAIN_VALID_TEST_SENS_SPEC = (
    ("test", "sensitivity", "specificity"),
    ("train", "checkpoint_train_sensitivity", "checkpoint_train_specificity"),
    ("valid", "checkpoint_valid_sensitivity", "checkpoint_valid_specificity"),
)


def stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def safe_column_index(header: list[str], name: str) -> int | None:
    """header.index(name), or None for a column this table does not have.

    A plain .index() raises for a field a run predates (e.g.
    checkpoint_train_sensitivity, added after some already-completed runs) --
    every caller here treats "column absent" the same as "no rows have a
    value for it", not as an error.
    """
    try:
        return header.index(name)
    except ValueError:
        return None


def values_for_metric(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
    metric: str,
) -> list[float]:
    idx = safe_column_index(header, metric)
    if idx is None:
        return []
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
    idx_num = safe_column_index(header, numerator_field)
    idx_den = [safe_column_index(header, f) for f in denominator_fields]
    if idx_num is None or any(i is None for i in idx_den):
        return []
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
        if field in EXCLUDED_FROM_TABLE:
            continue
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
    idx_sens = safe_column_index(header, "sensitivity")
    idx_spec = safe_column_index(header, "specificity")
    gaps = []
    if idx_sens is not None and idx_spec is not None:
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


def format_sens_spec_by_group(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    """One row per group, test/train/valid sensitivity+specificity side by
    side -- the mean across that group's seeds in each cell, "n/a" where the
    column does not exist for this table (see TRAIN_VALID_TEST_SENS_SPEC).
    """
    by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key in keys:
        by_group[key[0]].append(key)

    columns = [f"{split}_{stat}" for split, *_ in TRAIN_VALID_TEST_SENS_SPEC for stat in ("sens", "spec")]
    col_width = 10
    group_names = sorted(by_group) + ["ALL"]
    name_width = max(len("group"), *(len(name) for name in group_names))
    header_line = (
        f"{'group':{name_width}s}  {'n':>3s}  "
        + "  ".join(f"{c:>{col_width}s}" for c in columns)
    )

    def cell(group_keys, field):
        if field is None:
            return "n/a"
        values = values_for_metric(header, rows, group_keys, field)
        return f"{statistics.mean(values):.4f}" if values else "n/a"

    lines = [header_line]
    all_keys = keys
    for group in group_names:
        group_keys = by_group[group] if group != "ALL" else all_keys
        cells = []
        for _split, sens_field, spec_field in TRAIN_VALID_TEST_SENS_SPEC:
            sens_idx = safe_column_index(header, sens_field)
            spec_idx = safe_column_index(header, spec_field)
            cells.append(cell(group_keys, sens_field if sens_idx is not None else None))
            cells.append(cell(group_keys, spec_field if spec_idx is not None else None))
        lines.append(
            f"{group:{name_width}s}  {len(group_keys):>3d}  "
            + "  ".join(f"{c:>{col_width}s}" for c in cells)
        )
    return "\n".join(lines)


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
    print("=== Sensitivity / specificity by group (test / train / valid) ===")
    print(format_sens_spec_by_group(header, rows, keys))
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
