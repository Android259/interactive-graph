#!/usr/bin/env python3
"""Add metric reports that are not yet represented in the shared CSV table."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_metrics_table import (
    PROJECT_ROOT,
    format_datetime,
    metric_row,
    parse_metric_filename,
    read_table,
    write_table,
)


SOURCE_KEY_FIELDS = (
    "datetime",
    "exclusion_set",
    "number_of_parameters",
    "seed",
)


def metric_source_key(metric_path: Path, metrics_root: Path) -> tuple[str, ...]:
    relative_path = metric_path.resolve().relative_to(metrics_root.resolve())
    if len(relative_path.parts) < 3:
        raise ValueError(
            f"Metric path lacks label/exclusion directories: {relative_path}"
        )

    filename_values = parse_metric_filename(metric_path)
    values = {
        "datetime": format_datetime(filename_values["timestamp"]),
        "exclusion_set": "/".join(relative_path.parts[1:-1]),
        "number_of_parameters": filename_values["number_of_parameters"],
        "seed": filename_values["seed"],
    }
    return tuple(values[field] for field in SOURCE_KEY_FIELDS)


def add_new_metrics(
    metrics_root: Path,
    run_root: Path,
    table: Path,
    include_tensorboard: bool = True,
    metric_paths: list[Path] | None = None,
) -> list[Path]:
    rows = read_table(table)
    existing_keys = {
        tuple(row.get(field, "") for field in SOURCE_KEY_FIELDS)
        for row in rows
    }
    added_paths = []

    if metric_paths is None:
        metric_paths = sorted(metrics_root.rglob("test_metrics_*.txt"))

    for metric_path in metric_paths:
        metric_path = Path(metric_path)
        source_key = metric_source_key(metric_path, metrics_root)
        if source_key in existing_keys:
            continue

        rows.append(
            metric_row(
                metric_path,
                metrics_root,
                run_root,
                include_tensorboard=include_tensorboard,
            )
        )
        existing_keys.add(source_key)
        added_paths.append(metric_path)

    if added_paths:
        write_table(table, rows)
        from analyze_metrics_table import update_analysis
        from analyze_feature_contributions import write_feature_contributions

        update_analysis(table, Path(table).with_name("metrics_analysis.txt"))
        write_feature_contributions(
            table,
            Path(table).with_name("feature_contributions.csv"),
            "checkpoint_valid_balanced_accuracy",
        )
    return added_paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metrics-root",
        type=Path,
        default=PROJECT_ROOT / "test_metrics",
    )
    parser.add_argument("--run-root", type=Path, default=PROJECT_ROOT / "run")
    parser.add_argument(
        "--table",
        type=Path,
        default=PROJECT_ROOT / "metrics_summary.csv",
    )
    parser.add_argument("--no-tensorboard", action="store_true")
    parser.add_argument("metric_files", nargs="*", type=Path)
    args = parser.parse_args()

    added_paths = add_new_metrics(
        args.metrics_root,
        args.run_root,
        args.table,
        include_tensorboard=not args.no_tensorboard,
        metric_paths=args.metric_files or None,
    )
    print(f"Added {len(added_paths)} new metric rows to {args.table}")


if __name__ == "__main__":
    main()
