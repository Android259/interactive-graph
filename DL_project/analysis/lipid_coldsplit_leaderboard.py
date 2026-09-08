#!/usr/bin/env python3
"""Rank --lipid_coldsplit configurations on the one metric that survives the split.

Usage:
  python3 lipid_coldsplit_leaderboard.py                      # every label with "lcs" in it
  python3 lipid_coldsplit_leaderboard.py --match balanced     # only labels containing "balanced"
  python3 lipid_coldsplit_leaderboard.py --metric AUC         # any column of metrics_summary.csv
  python3 lipid_coldsplit_leaderboard.py --baseline LABEL     # add a delta column against LABEL

Why this exists
---------------
`compare_labels.py` answers "is B better than A"; it needs a pair and prints
eighteen metrics per group. When ten labels are in flight on the same split, the
question is instead "which of these is in front, and on which held-out class" --
one matrix, one metric, all labels at once.

The metric defaults to AUC_within_protein_pairs rather than balanced_accuracy or
pooled AUC on purpose. Under --lipid_coldsplit every protein stays in training,
so "which protein is this" is free to learn and the pooled figures are largely
that protein marginal (measured on
..._lcs_esm3_balanced_lipid_classes: pooled AUC 0.568 against 0.480 within
protein). Only the within-protein columns compare a lipid against another lipid
seen by the same protein, which is the question the product actually asks. The
pairs variant is the default rather than AUC_within_protein because the
per-protein average is blank whenever no protein block clears
WITHIN_PROTEIN_MINIMUM_ROWS with both classes present, which on the smaller
held-out sets is most seeds. See files/lipid_coldsplit_architecture_direction.md,
the RULE box at the top and section 7j.

0.5 is the no-signal line for every AUC column here, so the printed value is
readable on its own: below 0.5 the ordering inside that protein is inverted.

Reads metrics_summary.csv only; writes nothing.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from build_metrics_table import PROJECT_ROOT

DEFAULT_METRIC = "AUC_within_protein_pairs"


def latest_rows(table: Path, match: str) -> dict[str, dict[tuple[str, str], dict]]:
    """Latest row per (label, exclusion_set, seed) for labels containing `match`.

    `exclusion_set` is the held-out block, not `excluded_groups`: under
    --lipid_coldsplit the latter stays empty and every set would collapse
    into one column.
    """
    keep: dict[str, dict[tuple[str, str], dict]] = defaultdict(dict)
    with table.open(newline="") as handle:
        for row in csv.DictReader(handle):
            label = row.get("label", "")
            if match not in label:
                continue
            key = (row.get("exclusion_set", ""), row.get("seed", ""))
            seen = keep[label].get(key)
            if seen is None or row.get("datetime", "") >= seen.get("datetime", ""):
                keep[label][key] = row
    return keep


def cell(rows: list[dict], metric: str) -> tuple[float | None, float | None, int]:
    values = []
    for row in rows:
        raw = row.get(metric, "")
        if raw in ("", None):
            continue
        try:
            value = float(raw)
        except ValueError:
            continue
        if math.isnan(value):
            continue
        values.append(value)
    if not values:
        return None, None, 0
    mean = statistics.fmean(values)
    sem = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None
    return mean, sem, len(values)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument("--match", default="lcs", help="substring a label must contain (default: lcs)")
    parser.add_argument("--metric", default=DEFAULT_METRIC, help=f"column to rank on (default: {DEFAULT_METRIC})")
    parser.add_argument("--baseline", default=None, help="label to subtract, per group, for a delta column")
    parser.add_argument("--sort-by", default="mean", help="group name to sort on, or 'mean' (default)")
    args = parser.parse_args()

    by_label = latest_rows(args.table, args.match)
    if not by_label:
        print(f"no label in {args.table} contains {args.match!r}")
        return

    groups = sorted({key[0] for rows in by_label.values() for key in rows})
    table: dict[str, dict[str, tuple[float | None, float | None, int]]] = {}
    for label, rows in by_label.items():
        table[label] = {
            group: cell([row for key, row in rows.items() if key[0] == group], args.metric)
            for group in groups
        }

    def row_mean(label: str) -> float:
        means = [table[label][g][0] for g in groups if table[label][g][0] is not None]
        return statistics.fmean(means) if means else float("-inf")

    if args.sort_by == "mean":
        order = sorted(table, key=row_mean, reverse=True)
    else:
        order = sorted(table, key=lambda l: table[l].get(args.sort_by, (float("-inf"),))[0] or float("-inf"), reverse=True)

    base = table.get(args.baseline) if args.baseline else None
    if args.baseline and base is None:
        print(f"baseline label {args.baseline!r} not found; showing absolute values only")

    stem = ""
    names = list(table)
    if len(names) > 1:
        common = names[0]
        for name in names[1:]:
            while not name.startswith(common):
                common = common[:-1]
        stem = common
    if stem:
        print(f"common prefix stripped from label names: {stem}")
    print(f"metric: {args.metric}    cells are mean +- sem (n seeds)")
    print()

    width = max(len(label) - len(stem) for label in table) + 2
    header = "label".ljust(width) + "".join(g.replace("groups_", "").ljust(22) for g in groups) + "mean"
    print(header)
    print("-" * len(header))
    for label in order:
        line = (label[len(stem):] or ".").ljust(width)
        for group in groups:
            mean, sem, n = table[label][group]
            if mean is None:
                line += "n/a".ljust(22)
                continue
            text = f"{mean:.3f}"
            if base is not None and base[group][0] is not None:
                text += f" ({mean - base[group][0]:+.3f})"
            elif sem is not None:
                text += f"+-{sem:.3f}"
            text += f" [{n}]"
            line += text.ljust(22)
        line += f"{row_mean(label):.3f}"
        print(line)


if __name__ == "__main__":
    main()
