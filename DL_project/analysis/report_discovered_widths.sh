#!/usr/bin/env bash
# Print the discovered MLP layer widths of a gate/bilevel discovery series as tables.
#
# One block per excluded group: rows are the gated layers (module paths), columns are the
# seeds, plus a per-group median. A final block aggregates every run of the series
# (median / mean / min / max per layer), which is the value to bake into production runs.
#
# Usage:
#   analysis/report_discovered_widths.sh [LABEL] [options]
#
#   LABEL              run label, e.g. bbp_nps3mlp_dpt01_gm_mlpopt_y001
#                      (default: $DISCOVERY_LABEL, else all labels carrying widths)
#   --table PATH       metrics table (default: metrics_summary.csv at the project root)
#   --csv              emit long-form CSV (label,excluded_group,seed,layer,width) instead
#   --help
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TABLE="$PROJECT_ROOT/metrics_summary.csv"
LABEL="${DISCOVERY_LABEL:-}"
AS_CSV=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --table) TABLE="$2"; shift 2 ;;
        --csv) AS_CSV=1; shift ;;
        -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 0 ;;
        -*) echo "unknown option: $1" >&2; exit 2 ;;
        *) LABEL="$1"; shift ;;
    esac
done

if [[ ! -f "$TABLE" ]]; then
    echo "metrics table not found: $TABLE" >&2
    exit 1
fi

TABLE="$TABLE" LABEL="$LABEL" AS_CSV="$AS_CSV" python3 - <<'PY'
import csv
import json
import os
import signal
import statistics
import sys
from collections import OrderedDict, defaultdict

signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head/less

table = os.environ["TABLE"]
wanted_label = os.environ["LABEL"]
as_csv = os.environ["AS_CSV"] == "1"

csv.field_size_limit(1 << 24)


def excluded_groups(row):
    raw = (row.get("excluded_groups") or "").strip()
    if not raw or raw == "[]":
        return "(none)"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return "+".join(str(g) for g in parsed) if isinstance(parsed, list) else str(parsed)


# widths[label][group][seed][layer] = width, layers kept in first-seen (model) order
widths = defaultdict(lambda: defaultdict(dict))
layer_order = OrderedDict()

with open(table, encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle):
        raw = (row.get("discovered_widths") or "").strip()
        if not raw:
            continue
        label = row.get("label") or "(unlabeled)"
        if wanted_label and label != wanted_label:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        for layer in parsed:
            layer_order.setdefault(layer, None)
        widths[label][excluded_groups(row)][row.get("seed") or "?"] = parsed

if not widths:
    where = f" for label {wanted_label}" if wanted_label else ""
    print(f"no runs with discovered_widths found in {table}{where}", file=sys.stderr)
    sys.exit(1)

layers = list(layer_order)


def seed_key(seed):
    return (0, int(seed)) if seed.lstrip("-").isdigit() else (1, seed)


if as_csv:
    writer = csv.writer(sys.stdout)
    writer.writerow(["label", "excluded_group", "seed", "layer", "width"])
    for label, groups in widths.items():
        for group in sorted(groups):
            for seed in sorted(groups[group], key=seed_key):
                run = groups[group][seed]
                for layer in layers:
                    if layer in run:
                        writer.writerow([label, group, seed, layer, run[layer]])
    sys.exit(0)


def render(headers, rows):
    """Print a left-aligned first column, right-aligned numeric columns."""
    cells = [headers] + rows
    widths_ = [max(len(str(r[i])) for r in cells) for i in range(len(headers))]
    for index, row in enumerate(cells):
        line = [str(row[0]).ljust(widths_[0])]
        line += [str(value).rjust(widths_[i + 1]) for i, value in enumerate(row[1:])]
        print("  ".join(line))
        if index == 0:
            print("  ".join("-" * width for width in widths_))


def fmt(value):
    return "-" if value is None else (f"{value:.1f}" if isinstance(value, float) else str(value))


for label, groups in widths.items():
    print(f"=== {label} ===")
    for group in sorted(groups):
        seeds = sorted(groups[group], key=seed_key)
        print(f"\n--- excluded group: {group}  (seeds: {', '.join(seeds)}) ---")
        rows = []
        for layer in layers:
            values = [groups[group][seed].get(layer) for seed in seeds]
            present = [v for v in values if v is not None]
            rows.append(
                [layer]
                + [fmt(v) for v in values]
                + [fmt(statistics.median(present) if present else None)]
            )
        render(["layer"] + [f"seed {s}" for s in seeds] + ["median"], rows)

    runs = [run for group in groups.values() for run in group.values()]
    print(f"\n--- all runs of {label} ({len(runs)} runs) ---")
    rows = []
    for layer in layers:
        present = [run[layer] for run in runs if layer in run]
        if not present:
            rows.append([layer, "-", "-", "-", "-", 0])
            continue
        rows.append(
            [
                layer,
                fmt(statistics.median(present)),
                f"{statistics.mean(present):.1f}",
                min(present),
                max(present),
                len(present),
            ]
        )
    render(["layer", "median", "mean", "min", "max", "n"], rows)
    print()
PY
