#!/usr/bin/env python3
"""Compare `label` configurations via matched (exclusion_set, seed) pairs.

Usage: python3 compare_labels.py CANDIDATE_LABEL BASELINE_LABEL [--table PATH]
       python3 compare_labels.py LABEL LABEL LABEL... [--by-group] [--sort test_BA]

TWO labels: the original pairwise diff. For every metric in METRICS, computes
candidate - baseline over matched (exclusion_set, seed) pairs (latest row per pair,
per label) and reports:
  - overall: mean diff, median diff, std delta, improved/worsened counts, n
  - by group: mean diff, median diff, std delta, improved/worsened counts, n
    when --by-groups is passed

Higher-is-better metrics count diff > 0 as improved; for `loss`
(lower is better) diff < 0 counts as improved.

Flags and output match analysis/summarize_label.py's own single-label report
(the sibling script this one's METRICS/RATE_METRICS/read_table_rows/column_index/
latest_rows_for_label/numeric are shared with): --table, --by-groups, and --output to
append the report to a file instead of printing it.

MORE THAN TWO labels (folded in from the former analysis/label_summary_table.py, since
that script answered "one row per label, several labels side by side" -- a different
shape from the pairwise diff above, triggered here by how many labels are given rather
than by a separate script): one row per label instead of a diff, each with mean/SEM/std/n
over that label's own matched runs. Three spreads are printed because they answer
different questions and are routinely confused: std is how much the runs of this label
differ from each other (on a label whose runs are (excluded group x seed), this is
dominated by which group was held out, not by seed noise -- use --by-group to separate
the two); SEM = std/sqrt(n) is how well the MEAN is pinned down, the number to compare
labels with; n is how many runs are behind both -- a label with 20 rows and one with 35
are not comparable spreads. Columns are BA, test F1, sensitivity, specificity (the
former script's AUC/AUC_within_protein_pairs columns are dropped here in favour of
these three, which exist for every run regardless of --lipid_coldsplit/
--double_coldsplit, where AUC columns are often blank).

Prints to stdout by default; --output appends instead (two-label mode only).
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from build_metrics_table import PROJECT_ROOT

# Columns for the N>2-label ranked table (was label_summary_table.py's own METRICS,
# which printed BA/AUC/AUC_within_protein_pairs -- AUC is blank for a lot of runs
# outside --lipid_coldsplit, so the replacement set is metrics every run has).
RANKED_METRICS = (
    ("balanced_accuracy", "BA"),
    ("F1", "test F1"),
    ("sensitivity", "sensitivity"),
    ("specificity", "specificity"),
)

METRICS = (
    ("checkpoint_valid_balanced_accuracy", "checkpoint valid BA", True),
    ("max_valid_balanced_accuracy", "max valid BA", True),
    ("best_valid_F1", "best valid F1", True),
    ("balanced_accuracy", "test BA", True),
    # Threshold-free companion to test BA: on the cold splits sensitivity runs at
    # 0.2-0.35 against specificity 0.77, where BA at the fixed 0.5 threshold cannot
    # tell "learned nothing" from "learned something, threshold in the wrong place".
    # Blank for runs written before new_train.py reported it (see build_metrics_table).
    ("AUC", "test AUC", True),
    # Read this one FIRST on a --lipid_coldsplit label. Pooled AUC there is largely the
    # protein marginal (measured: pooled 0.568 against 0.480 within protein), which this
    # cannot express -- comparisons never cross a protein boundary. See
    # files/results/lipid_coldsplit_architecture_direction.md section 7j.
    ("AUC_within_protein", "test AUC in-protein", True),
    ("AUC_within_protein_proteins", "  (proteins averaged)", True),
    # Pair-pooled version of the same question -- read THIS one: the
    # per-protein average above is empty for runs where no protein block
    # clears 6 rows with both classes, which is most of them on the small sets.
    ("AUC_within_protein_pairs", "test AUC in-protein (pairs)", True),
    ("AUC_within_protein_pairs_proteins", "  (proteins contributing)", True),
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
    # A metric column the table predates is "no pairs to compare", not an error --
    # both callers already skip an empty result. column_index stays strict where it
    # is used for the identity fields (label/exclusion_set/seed), whose absence
    # really is a broken table. AUC is the current case: rows written before
    # new_train.py reported it have no such column at all.
    try:
        idx = column_index(header, metric)
    except ValueError:
        return [], [], []
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


# ------------------------------------------------- N>2-label mode (was label_summary_table.py)


def spread(values: list[float | None]) -> tuple[float | None, float | None, float | None, int]:
    """(mean, sem, std, n) over the finite values, or (None, ...) when there are none."""
    values = [value for value in values if value is not None]
    if not values:
        return None, None, None, 0
    if len(values) == 1:
        return values[0], None, 0.0, 1
    std = statistics.stdev(values)
    return statistics.fmean(values), std / math.sqrt(len(values)), std, len(values)


def ranked_cell(mean, sem, std, n, width=26) -> str:
    if mean is None:
        return f"{'--':>{width}}"
    sem_text = "  --  " if sem is None else f"{sem:.3f}"
    return f"{f'{mean:.3f} +/-{sem_text} sd{std:.3f} n{n}':>{width}}"


def print_ranked_table(
    labels: list[str], table_path: Path, by_group: bool, drop_groups: set[str], sort: str,
) -> None:
    rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    with table_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["label"] not in labels:
                continue
            if row["exclusion_set"].replace("groups_", "") in drop_groups:
                continue
            key = (row["label"], row["exclusion_set"]) if by_group else (row["label"], "")
            rows[key].append(row)
            groups[key].add(row["exclusion_set"])

    if not rows:
        raise SystemExit(f"no rows matched any of {labels!r} in {table_path}")
    missing = [label for label in labels if label not in {key[0] for key in rows}]
    if missing:
        print(f"# WARNING: no rows for label(s) {missing!r} in {table_path}")

    summaries = {
        key: {column: spread([numeric(row[column]) for row in group_rows]) for column, _ in RANKED_METRICS}
        for key, group_rows in rows.items()
    }

    order = sorted(rows)
    if sort != "label":
        column = next((c for c, name in RANKED_METRICS if sort in (c, name)), sort)
        order = sorted(rows, key=lambda key: (summaries[key][column][0] is None, -(summaries[key][column][0] or 0)))

    # Labels on one line share a long prefix (the architecture they are all variants
    # of); printing it repeatedly pushes the distinguishing suffix off the right edge,
    # which is the only part anyone reads. Printed once, above the table.
    common = ""
    names = sorted({key[0] for key in rows})
    if len(names) > 1:
        for index, character in enumerate(names[0]):
            if all(len(name) > index and name[index] == character for name in names):
                common += character
            else:
                break
        common = common.rsplit("_", 1)[0] + "_" if "_" in common else ""
    if common:
        print(f"common prefix: {common}\n")
    display = {key: (key[0][len(common):] if key[0].startswith(common) else key[0]) for key in rows}
    name_width = min(max(len(text) for text in display.values()), 64)
    header = f"{'label':{name_width}}"
    if by_group:
        header += f"{'group':18}"
    header += f"{'runs':>6}{'grps':>6}" + "".join(f"{name:>26}" for _, name in RANKED_METRICS)
    print(header)
    print("-" * len(header))
    for key in order:
        text = display[key]
        # Truncated head, not tail: what distinguishes one variant of a line from
        # another is always the suffix (the flag that was changed), never the shared stem.
        if len(text) > name_width:
            text = "…" + text[-(name_width - 1):]
        line = f"{text:{name_width}}"
        if by_group:
            line += f"{key[1].replace('groups_', ''):18}"
        line += f"{len(rows[key]):>6}{len(groups[key]):>6}"
        for column, _ in RANKED_METRICS:
            line += ranked_cell(*summaries[key][column])
        print(line)
    print("\n+/-SEM = std/sqrt(n) -- how well the mean is pinned down; sd = spread of the "
          "runs themselves.\nWithout --by-group the spread mixes excluded groups with seeds.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "labels", nargs="+",
        help="two labels for the pairwise diff (candidate then baseline), or more than "
             "two for a ranked side-by-side table",
    )
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "results" / "tables" / "metrics_summary.csv")
    parser.add_argument(
        "--by-groups",
        "--by_groups",
        action="store_true",
        help="Two-label mode: print per-exclusion-group comparison sections.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Two-label mode: append the comparison to this file instead of printing "
             "it (accumulates across repeated invocations, same convention as "
             "summarize_label.py).",
    )
    parser.add_argument(
        "--by-group", action="store_true",
        help="N>2-label mode: one row per (label, excluded group) instead of one per "
             "label, so group spread and seed spread stop being the same number.",
    )
    parser.add_argument(
        "--drop-groups", default="",
        help="N>2-label mode: comma-separated excluded groups to leave out.",
    )
    parser.add_argument(
        "--sort", default="label",
        help="N>2-label mode: label (default), or a metric column name to sort by, descending.",
    )
    args = parser.parse_args()

    if len(args.labels) == 1:
        raise SystemExit(
            "one label given -- use analysis/summarize_label.py for a single-label "
            "report, or pass two (pairwise diff) or more (ranked table) labels here"
        )

    if len(args.labels) > 2:
        print_ranked_table(
            args.labels, args.table, args.by_group,
            {name for name in args.drop_groups.split(",") if name}, args.sort,
        )
        return

    candidate_label, baseline_label = args.labels
    header, rows = read_table_rows(args.table)
    baseline = latest_rows_for_label(header, rows, baseline_label)
    candidate = latest_rows_for_label(header, rows, candidate_label)

    if not baseline:
        raise SystemExit(f"No rows found with label={baseline_label!r} in {args.table}")
    if not candidate:
        raise SystemExit(f"No rows found with label={candidate_label!r} in {args.table}")

    common = sorted(set(baseline) & set(candidate))
    if not common:
        raise SystemExit(
            f"No matched (exclusion_set, seed) pairs between "
            f"{candidate_label!r} ({len(candidate)} rows) and "
            f"{baseline_label!r} ({len(baseline)} rows)"
        )

    parts = [
        f"Comparison: {candidate_label!r} vs {baseline_label!r} (baseline)",
        f"baseline rows: {len(baseline)} | candidate rows: {len(candidate)} | "
        f"matched pairs: {len(common)}",
        "",
        "=== Overall ===",
        format_overall(header, baseline, candidate, common),
        "",
        "=== Confusion rates ===",
        format_rate_metrics(header, baseline, candidate, common),
        "",
        "=== " + format_class_recall_gap(header, baseline, candidate, common) + " ===",
    ]
    if args.by_groups:
        parts += ["", "=== By group ===", format_by_group(header, baseline, candidate, common)]
    report = "\n".join(parts)

    if args.output:
        with args.output.open("a", encoding="utf-8") as handle:
            handle.write(report + "\n")
        print(f"Appended comparison to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
