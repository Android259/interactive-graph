#!/usr/bin/env python3
"""Calculate matched configuration-feature effects from metrics_summary.csv."""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import tempfile
from collections import defaultdict
from pathlib import Path

from analyze_metrics_table import COMPARISON_FIELDS, CONFIG_FIELD_GROUPS
from analysis.build_metrics_table import CONFIG_FIELDS, PROJECT_ROOT


OUTPUT_FIELDS = (
    "dataset",
    "metric",
    "feature_group",
    "feature",
    "baseline_value",
    "comparison_value",
    "matched_pairs",
    "seed_count",
    "seeds",
    "mean_delta",
    "median_delta",
    "std_delta",
    "min_delta",
    "max_delta",
    "improved_pairs",
    "worsened_pairs",
    "unchanged_pairs",
    "improved_fraction",
    "worsened_fraction",
)
FEATURE_GROUP = {
    field: group
    for group, fields in CONFIG_FIELD_GROUPS.items()
    for field in fields
}


def _number(row, field):
    try:
        value = float(row.get(field, ""))
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _key(row, fields):
    return tuple(row.get(field, "") for field in fields)


def _has_complete_config(row):
    return all(row.get(field, "") != "" for field in CONFIG_FIELDS)


def _value_sort_key(value):
    try:
        return 0, float(value)
    except (TypeError, ValueError):
        return 1, str(value)


def _latest_completed_rows(rows, metric):
    latest = {}
    fields = ("exclusion_set", *COMPARISON_FIELDS, "seed")
    for row in sorted(rows, key=lambda item: item.get("datetime", "")):
        if row.get("run_status", "") != "complete":
            continue
        if not _has_complete_config(row) or _number(row, metric) is None:
            continue
        latest[_key(row, fields)] = row
    return list(latest.values())


def calculate_feature_contributions(
    rows, metric="checkpoint_valid_balanced_accuracy"
):
    effects = defaultdict(list)
    usable = _latest_completed_rows(rows, metric)

    for index, left in enumerate(usable):
        for right in usable[index + 1:]:
            if left.get("exclusion_set", "") != right.get("exclusion_set", ""):
                continue
            if left.get("seed", "") != right.get("seed", ""):
                continue

            differing = [
                field for field in COMPARISON_FIELDS
                if left.get(field, "") != right.get(field, "")
            ]
            if len(differing) != 1:
                continue

            feature = differing[0]
            baseline_value = left[feature]
            comparison_value = right[feature]
            baseline_score = _number(left, metric)
            comparison_score = _number(right, metric)
            if _value_sort_key(baseline_value) > _value_sort_key(comparison_value):
                baseline_value, comparison_value = comparison_value, baseline_value
                baseline_score, comparison_score = comparison_score, baseline_score

            key = (
                left.get("exclusion_set", ""),
                FEATURE_GROUP[feature],
                feature,
                baseline_value,
                comparison_value,
            )
            effects[key].append({
                "delta": comparison_score - baseline_score,
                "seed": left.get("seed", ""),
            })

    result = []
    for key, observations in sorted(effects.items()):
        dataset, feature_group, feature, baseline_value, comparison_value = key
        deltas = [observation["delta"] for observation in observations]
        improved = sum(delta > 0 for delta in deltas)
        worsened = sum(delta < 0 for delta in deltas)
        unchanged = len(deltas) - improved - worsened
        seeds = sorted(
            {observation["seed"] for observation in observations},
            key=_value_sort_key,
        )
        result.append({
            "dataset": dataset,
            "metric": metric,
            "feature_group": feature_group,
            "feature": feature,
            "baseline_value": baseline_value,
            "comparison_value": comparison_value,
            "matched_pairs": str(len(deltas)),
            "seed_count": str(len(seeds)),
            "seeds": ",".join(seeds),
            "mean_delta": f"{statistics.fmean(deltas):.6f}",
            "median_delta": f"{statistics.median(deltas):.6f}",
            "std_delta": f"{statistics.stdev(deltas):.6f}" if len(deltas) > 1 else "",
            "min_delta": f"{min(deltas):.6f}",
            "max_delta": f"{max(deltas):.6f}",
            "improved_pairs": str(improved),
            "worsened_pairs": str(worsened),
            "unchanged_pairs": str(unchanged),
            "improved_fraction": f"{improved / len(deltas):.6f}",
            "worsened_fraction": f"{worsened / len(deltas):.6f}",
        })
    return result


def write_feature_contributions(table_path, output_path, metric):
    with Path(table_path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = calculate_feature_contributions(rows, metric)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        delete=False,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(result)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, output_path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "feature_contributions.csv",
    )
    parser.add_argument(
        "--metric", default="checkpoint_valid_balanced_accuracy"
    )
    args = parser.parse_args()

    rows = write_feature_contributions(args.table, args.output, args.metric)
    print(f"Wrote {len(rows)} feature effects to {args.output}")


if __name__ == "__main__":
    main()
