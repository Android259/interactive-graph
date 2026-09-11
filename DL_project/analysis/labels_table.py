#!/usr/bin/env python3
"""Side-by-side metrics table for an arbitrary list of labels.

Usage: python3 labels_table.py LABEL [LABEL ...] [--table PATH]

For each label, pulls from metrics_summary.csv (mean over that label's rows,
no forward pass): test BA, test sensitivity, test specificity, mean
train-valid gap. Then, if a full_label_report.py report already exists at
graphics/<label>/<label>.md, parses its "AUC vs chemistry null model" section
for the network's own in-protein and pair-pooled AUC (net_AUC_prot,
net_AUC_pair -- see analysis/null_model.py). Those two columns are blank for
any label whose report hasn't been generated, or was generated with
SKIP_AUC=1 -- this script never launches a forward pass to fill them in; run
`scripts/env.sh python3 analysis/full_label_report.py --label LABEL` first.

"pair AUC" and "in-protein AUC" have two possible sources, tried in this
order: (1) metrics_summary.csv's own AUC_within_protein_pairs /
AUC_within_protein columns -- populated for lipid_coldsplit labels, where the
network's per-run eval already computes them (no forward pass needed here);
(2) the full_label_report.py-generated null-model comparison in
graphics/<label>/<label>.md (net_AUC_pair / net_AUC_prot) -- the only source
for double_coldsplit labels, where the csv columns are always empty. The two
are different metrics (csv: network's own AUC, no null-model adjustment;
report: also the network's own AUC, from null_model.py's per_protein_auc/
per_pair_auc on freshly-scored checkpoints) that should read close to each
other when both exist, not a null-adjusted "increment" -- for that, read the
report's "chem"/"net" or "null_AUC_k15"/"net_AUC" lines directly.

Prints one row per label, ranked by test BA. Does not write any file.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHICS_DIR = PROJECT_ROOT / "graphics"

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
    report_path = GRAPHICS_DIR / label / f"{label}.md"
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="+", help="label names, space separated")
    parser.add_argument(
        "--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv"
    )
    args = parser.parse_args()

    rows = []
    for label in args.labels:
        csv_metrics, csv_auc_fallback = read_csv_metrics(args.table, label)
        if all(v is None for v in csv_metrics.values()):
            print(f"# WARNING: no rows for label={label!r} in {args.table}")
        auc_metrics = read_null_model_aucs(label)
        for key in ("pair_AUC", "in_protein_AUC"):
            if auc_metrics[key] is None:
                auc_metrics[key] = csv_auc_fallback[key]
        rows.append((label, csv_metrics, auc_metrics))

    rows.sort(
        key=lambda r: r[1]["test_BA"] if r[1]["test_BA"] is not None else -1,
        reverse=True,
    )

    header = f"{'label':70s}  {'gap':>7s}  {'sens':>7s}  {'spec':>7s}  {'test_BA':>7s}  {'pair_AUC':>8s}  {'in_prot_AUC':>11s}"
    print(header)
    for label, csv_metrics, auc_metrics in rows:
        print(
            f"{label:70s}  "
            f"{format_cell(csv_metrics['gap']):>7s}  "
            f"{format_cell(csv_metrics['test_sens']):>7s}  "
            f"{format_cell(csv_metrics['test_spec']):>7s}  "
            f"{format_cell(csv_metrics['test_BA']):>7s}  "
            f"{format_cell(auc_metrics['pair_AUC']):>8s}  "
            f"{format_cell(auc_metrics['in_protein_AUC']):>11s}"
        )


if __name__ == "__main__":
    main()
