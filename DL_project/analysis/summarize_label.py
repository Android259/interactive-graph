#!/usr/bin/env python3
"""Summarize `label` configuration(s) across (exclusion_set, seed) runs. The one
remaining script for this table -- folds in the former labels_table.py (multi-label
ranking) and analyze_label_metrics.py (--output file mode); analyze_label_metrics.py's
own per-protein-SUBGROUP breakdown is dropped, not carried over -- that is a question
about one run's test report, not about a label's runs, and belongs with whatever reads
test_metrics/*.txt directly if it is wanted again.

Usage: python3 summarize_label.py LABEL [--table PATH] [--by-groups] [--output PATH]
       python3 summarize_label.py LABEL [LABEL ...]   # ranked side-by-side table

ONE label (default): for every metric in METRICS, computes mean/median/std over the
latest row per (exclusion_set, seed) pair and reports:
  - a test/train/valid sensitivity+specificity table, one row per group
  - overall: mean, median, std, n (TP/FP/FN/TN excluded -- see EXCLUDED_FROM_TABLE)
  - by group: mean, median, std, n when --by-groups is passed

Same metric set and confusion-rate derivations (FPR, FNR, sensitivity-
specificity gap) as compare_labels.py, but for a single label instead of a
candidate/baseline diff -- compare_labels.py's own --output/format match this script's.

checkpoint-epoch train/valid sensitivity/specificity (checkpoint_train_sensitivity,
checkpoint_train_specificity, checkpoint_valid_sensitivity,
checkpoint_valid_specificity) come from training/run_metrics.py and are only
present for runs finished after that module started recording them -- a run
from before then reads back as n/a in those columns, not zero or an error.

TWO OR MORE labels (was labels_table.py): one row per label instead of the detailed
report above, ranked by test BA -- test BA/sensitivity/specificity/mean train-valid gap
from metrics_summary.csv, plus pair_AUC/in_protein_AUC from TWO possible sources, tried
in this order: (1) metrics_summary.csv's own AUC_within_protein_pairs/AUC_within_protein
columns, populated for lipid_coldsplit labels where the per-run eval already computes
them; (2) full_label_report.py's graphics/<label>/<label>.md null-model comparison
(net_AUC_pair/net_AUC_prot), the only source for double_coldsplit labels. Blank for any
label whose report has not been generated -- this never launches a forward pass to fill
them in.

Prints to stdout by default; --output appends the single-label report to a text file
instead (accumulates across repeated invocations for different labels, does not
overwrite).
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from build_metrics_table import PROJECT_ROOT
from compare_labels import (
    RATE_METRICS,
    METRICS,
    latest_rows_for_label,
    numeric,
    read_table_rows,
)
from training.results_layout import label_dir

GRAPHICS_DIR = PROJECT_ROOT / "graphics"

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


def format_seed_variability(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    """How much a group's own sensitivity/specificity typically jumps from seed
    to seed, not (unlike format_class_recall_gap above) how far sensitivity sits
    from specificity within one run. Per group: std of that group's seeds'
    sensitivity values, and separately of specificity; then mean/median of
    those per-group stds across groups -- std first, only then averaged, same
    per-group-first order as the rest of this project's "not by pool" rule.
    """
    by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key in keys:
        by_group[key[0]].append(key)

    sens_stds = []
    spec_stds = []
    for group_keys in by_group.values():
        sens_values = values_for_metric(header, rows, group_keys, "sensitivity")
        spec_values = values_for_metric(header, rows, group_keys, "specificity")
        if len(sens_values) > 1:
            sens_stds.append(stddev(sens_values))
        if len(spec_values) > 1:
            spec_stds.append(stddev(spec_values))

    lines = []
    if sens_stds:
        lines.append(
            f"sensitivity std across seeds (by group): mean={statistics.mean(sens_stds):.4f} "
            f"median={statistics.median(sens_stds):.4f} n={len(sens_stds)}"
        )
    else:
        lines.append("sensitivity std across seeds (by group): no group with >1 seed")
    if spec_stds:
        lines.append(
            f"specificity std across seeds (by group): mean={statistics.mean(spec_stds):.4f} "
            f"median={statistics.median(spec_stds):.4f} n={len(spec_stds)}"
        )
    else:
        lines.append("specificity std across seeds (by group): no group with >1 seed")
    return "\n".join(lines)


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


# ----------------------------------------------- multi-label mode (was labels_table.py)

CSV_METRICS = (
    ("balanced_accuracy", "test_BA"),
    ("sensitivity", "test_sens"),
    ("specificity", "test_spec"),
    ("mean_train_valid_gap", "gap"),
)

# Fallback source for pair_AUC / in_protein_AUC when the csv already has them
# (lipid_coldsplit labels) -- see module docstring for why this isn't always
# equivalent to the null-model report's net_AUC_pair/net_AUC_prot.
CSV_AUC_FALLBACK = (
    ("AUC_within_protein_pairs", "pair_AUC"),
    ("AUC_within_protein", "in_protein_AUC"),
)

# Matches a "label   0.123   ..." stats line inside one of the report's
# "=== ... ===" blocks; group(1) is the first ("all seven") column.
_STATS_LINE = re.compile(r"^(net_AUC_prot|net_AUC_pair)\s+([0-9.+-]+)")


def read_csv_metrics(table_path: Path, label: str) -> tuple[dict, dict]:
    """Returns (core_metrics, auc_fallback) -- see CSV_METRICS / CSV_AUC_FALLBACK."""
    all_fields = CSV_METRICS + CSV_AUC_FALLBACK
    with table_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    values: dict[str, list[float]] = {field: [] for field, _ in all_fields}
    for row in rows:
        if row.get("label") != label:
            continue
        for field, _ in all_fields:
            raw = row.get(field)
            try:
                parsed = float(raw)
            except (TypeError, ValueError):
                continue
            if parsed == parsed:  # filter NaN
                values[field].append(parsed)
    core = {
        short: (statistics.mean(values[field]) if values[field] else None)
        for field, short in CSV_METRICS
    }
    auc_fallback = {
        short: (statistics.mean(values[field]) if values[field] else None)
        for field, short in CSV_AUC_FALLBACK
    }
    return core, auc_fallback


def read_null_model_aucs(label: str) -> dict[str, float | None]:
    report_path = label_dir(GRAPHICS_DIR, label) / f"{label}.md"
    result = {"in_protein_AUC": None, "pair_AUC": None}
    if not report_path.exists():
        return result
    text = report_path.read_text(encoding="utf-8")
    # Only look inside the first "AUC vs chemistry null model" section (the
    # valid-split one) -- later sections use different, non-comparable
    # in-sample-fit metrics (see interaction_increment.py's "increment").
    section_start = text.find("## AUC vs chemistry null model")
    if section_start == -1:
        return result
    next_section = text.find("\n## ", section_start + 1)
    section = text[section_start : next_section if next_section != -1 else None]
    for line in section.splitlines():
        match = _STATS_LINE.match(line.strip())
        if not match:
            continue
        key = "in_protein_AUC" if match.group(1) == "net_AUC_prot" else "pair_AUC"
        if result[key] is None:  # first split (valid) wins if the section repeats
            result[key] = float(match.group(2))
    return result


def format_cell(value: float | None) -> str:
    return f"{value:.4f}" if value is not None else "  --  "


def build_ranked_table(labels: list[str], table_path: Path) -> str:
    rows = []
    for label in labels:
        csv_metrics, csv_auc_fallback = read_csv_metrics(table_path, label)
        if all(v is None for v in csv_metrics.values()):
            print(f"# WARNING: no rows for label={label!r} in {table_path}")
        auc_metrics = read_null_model_aucs(label)
        for key in ("pair_AUC", "in_protein_AUC"):
            if auc_metrics[key] is None:
                auc_metrics[key] = csv_auc_fallback[key]
        rows.append((label, csv_metrics, auc_metrics))

    rows.sort(
        key=lambda r: r[1]["test_BA"] if r[1]["test_BA"] is not None else -1,
        reverse=True,
    )

    lines = [
        f"{'label':70s}  {'gap':>7s}  {'sens':>7s}  {'spec':>7s}  {'test_BA':>7s}  "
        f"{'pair_AUC':>8s}  {'in_prot_AUC':>11s}"
    ]
    for label, csv_metrics, auc_metrics in rows:
        lines.append(
            f"{label:70s}  "
            f"{format_cell(csv_metrics['gap']):>7s}  "
            f"{format_cell(csv_metrics['test_sens']):>7s}  "
            f"{format_cell(csv_metrics['test_spec']):>7s}  "
            f"{format_cell(csv_metrics['test_BA']):>7s}  "
            f"{format_cell(auc_metrics['pair_AUC']):>8s}  "
            f"{format_cell(auc_metrics['in_protein_AUC']):>11s}"
        )
    return "\n".join(lines)


# ------------------------------------------- single-label report (was analyze_label_
# metrics.py's --output accumulation; the detailed formatting above is this script's own)


def format_stability_by_group(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    """Per group: how many of its runs converged, and collapse_epoch_count mean/max --
    was analysis/probes/lcs_new_configs_summary.py's own stability block, generalised
    to any label's own groups rather than the four --lipid_coldsplit ones it was
    hardcoded to. "n/a" for either column a table predates, same convention as every
    other field here (safe_column_index).
    """
    idx_converged = safe_column_index(header, "converged")
    idx_collapse = safe_column_index(header, "collapse_epoch_count")
    if idx_converged is None and idx_collapse is None:
        return "stability: no converged/collapse_epoch_count column in this table"

    by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key in keys:
        by_group[key[0]].append(key)

    lines = ["stability (converged, collapse_epoch_count mean/max):"]
    for group in sorted(by_group):
        group_keys = by_group[group]
        n = len(group_keys)
        converged_text = "n/a"
        if idx_converged is not None:
            n_converged = sum(1 for key in group_keys if rows[key][idx_converged] in ("True", "1"))
            converged_text = f"{n_converged}/{n}"
        collapse_text = "n/a"
        if idx_collapse is not None:
            collapse_values = [
                v for v in (numeric(rows[key][idx_collapse]) for key in group_keys) if v is not None
            ]
            if collapse_values:
                collapse_text = f"{statistics.mean(collapse_values):.1f}/{max(collapse_values):.1f}"
        lines.append(
            f"  {group:24s} converged={converged_text:8s} "
            f"collapse_epochs(mean/max)={collapse_text}"
        )
    return "\n".join(lines)


def format_per_seed(
    header: list[str],
    rows: dict[tuple[str, str], list[str]],
    keys: list[tuple[str, str]],
) -> str:
    """One raw line per (group, seed): sens/spec/loss/converged/collapse_epoch_count --
    was analysis/probes/lcs_new_configs_summary.py's per_seed_dump, for spotting a
    pathological seed (collapsed sens/spec, loss far above chance, converged unset)
    that a group-level mean can hide.
    """
    idx_sens = safe_column_index(header, "sensitivity")
    idx_spec = safe_column_index(header, "specificity")
    idx_loss = safe_column_index(header, "loss")
    idx_converged = safe_column_index(header, "converged")
    idx_collapse = safe_column_index(header, "collapse_epoch_count")

    def cell(key, idx, digits=4):
        if idx is None:
            return "n/a"
        value = numeric(rows[key][idx])
        return "n/a" if value is None else f"{value:.{digits}f}"

    lines = ["per-seed raw:"]
    for group, seed in keys:
        key = (group, seed)
        converged = rows[key][idx_converged] if idx_converged is not None else "n/a"
        lines.append(
            f"  {group:16s} seed={seed:4s} sens={cell(key, idx_sens)} "
            f"spec={cell(key, idx_spec)} loss={cell(key, idx_loss)} "
            f"collapse_epochs={cell(key, idx_collapse, 1)} converged={converged}"
        )
    return "\n".join(lines)


def build_single_label_report(label: str, table_path: Path, per_seed: bool = False) -> str:
    header, all_rows = read_table_rows(table_path)
    rows = latest_rows_for_label(header, all_rows, label)
    if not rows:
        raise SystemExit(f"No rows found with label={label!r} in {table_path}")
    keys = sorted(rows)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        f"Summary: {label!r}",
        f"generated: {timestamp}",
        f"rows: {len(rows)}",
        "",
        "=== Sensitivity / specificity by group (test / train / valid) ===",
        format_sens_spec_by_group(header, rows, keys),
        "",
        "=== Overall ===",
        format_metrics_table(header, rows, keys),
        "",
        "=== " + format_class_recall_gap(header, rows, keys) + " ===",
        format_seed_variability(header, rows, keys),
        "",
        format_stability_by_group(header, rows, keys),
    ]
    if per_seed:
        parts += ["", format_per_seed(header, rows, keys)]
    return "\n".join(parts), header, rows, keys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("label", nargs="+", help="one label for the detailed report, two or more for a ranked table")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "results" / "tables" / "metrics_summary.csv")
    parser.add_argument(
        "--by-groups",
        "--by_groups",
        action="store_true",
        help="Print per-exclusion-group summary sections. Single-label mode only.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Append the single-label report to this file instead of printing it "
             "(accumulates across repeated invocations for different labels). "
             "Single-label mode only.",
    )
    parser.add_argument(
        "--per-seed",
        "--per_seed",
        dest="per_seed",
        action="store_true",
        help="Also print one raw line per (group, seed): sens/spec/loss/converged/"
             "collapse_epoch_count, for spotting a pathological seed a group mean "
             "hides. Single-label mode only.",
    )
    args = parser.parse_args()

    if len(args.label) > 1:
        if args.by_groups or args.output or args.per_seed:
            raise SystemExit("--by-groups/--output/--per-seed apply only to the single-label report")
        print(build_ranked_table(args.label, args.table))
        return

    label = args.label[0]
    report, header, rows, keys = build_single_label_report(label, args.table, args.per_seed)
    if args.by_groups:
        report += "\n\n=== By group ===\n" + format_by_group(header, rows, keys)

    if args.output:
        with args.output.open("a", encoding="utf-8") as handle:
            handle.write(report + "\n")
        print(f"Appended summary for label={label!r} to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
