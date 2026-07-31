"""Aggregate discovered hyperparameters across a series of discovery runs.

A bilevel/gate discovery run (``--gate_all_mlp_hidden [--bilevel] [--bilevel_dropout]``)
records, per run, the surviving gate widths (``discovered_widths``) and the per-layer
Concrete Dropout rates (``discovered_dropout``) into the metrics table
(``metrics_summary.csv``). Both are compact JSON keyed by module path
(``{module_name: value}``), so each value says which layer it belongs to.

This script reads that table and, grouping over the series (different seeds and different
excluded groups), reports the "relatively optimal" hyperparameters:

  * per gate: the median surviving width (robust to per-run noise),
  * per dropout site: the mean learned dropout rate.

Usage:
    python analysis/aggregate_discovered_hparams.py [--table metrics_summary.csv]
                                                    [--group-by label|all]
"""
import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read_discovery_rows(table_path):
    """Return table rows that carry discovered hyperparameters."""
    with table_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            row
            for row in reader
            if (row.get("discovered_widths") or "").strip()
            or (row.get("discovered_dropout") or "").strip()
        ]


def _group_key(row, group_by):
    if group_by == "all":
        return "all"
    return row.get("label", "") or "(unlabeled)"


def _load_json_field(row, field):
    raw = (row.get(field) or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def aggregate(rows, group_by="label"):
    """Aggregate widths (median) and dropout (mean) per module path, per group."""
    widths_by_group = defaultdict(lambda: defaultdict(list))
    dropout_by_group = defaultdict(lambda: defaultdict(list))
    counts = defaultdict(int)

    for row in rows:
        key = _group_key(row, group_by)
        counts[key] += 1
        for gate_name, active in _load_json_field(row, "discovered_widths").items():
            try:
                widths_by_group[key][gate_name].append(int(active))
            except (ValueError, TypeError):
                pass
        for site_name, p in _load_json_field(row, "discovered_dropout").items():
            try:
                dropout_by_group[key][site_name].append(float(p))
            except (ValueError, TypeError):
                pass

    result = {}
    for key in counts:
        widths = {
            gate: int(statistics.median(values))
            for gate, values in sorted(widths_by_group[key].items())
        }
        dropout = {
            site: statistics.mean(values)
            for site, values in sorted(dropout_by_group[key].items())
        }
        result[key] = {"runs": counts[key], "widths": widths, "dropout": dropout}
    return result


def format_report(aggregated):
    lines = []
    for key, info in sorted(aggregated.items()):
        lines.append(f"=== {key}  ({info['runs']} runs) ===")
        if info["dropout"]:
            lines.append("  per-layer dropout (mean):")
            for site, value in info["dropout"].items():
                lines.append(f"    {site}: {value:.4f}")
        if info["widths"]:
            lines.append("  surviving widths (median active units):")
            for gate, width in info["widths"].items():
                lines.append(f"    {gate}: {width}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv",
        help="Metrics table CSV produced by analysis/build_metrics_table.py",
    )
    parser.add_argument(
        "--group-by", choices=("label", "all"), default="label",
        help="Aggregate per experiment label, or pool the whole series ('all').",
    )
    args = parser.parse_args()

    if not args.table.exists():
        raise SystemExit(f"Metrics table not found: {args.table}")
    rows = _read_discovery_rows(args.table)
    if not rows:
        raise SystemExit(
            f"No discovery rows (non-empty discovered_widths/dropout) in {args.table}"
        )
    aggregated = aggregate(rows, group_by=args.group_by)
    print(format_report(aggregated))


if __name__ == "__main__":
    main()
