#!/usr/bin/env python3
"""Add metric reports that are not yet represented in the shared CSV table.

Lives in training/, not analysis/: scripts/wait_and_sync.sh runs this (as a CLI) right
after syncing a cluster's finished runs, to write every newly-arrived report into the
shared table before anything else reads it -- a result-recording step of the run
pipeline, not a read-only analysis/ report over a table assumed already complete.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from analysis.build_metrics_table import (  # noqa: E402
    PROJECT_ROOT,
    format_datetime,
    metric_row,
    parse_metric_filename,
    read_table,
    write_table,
)
from training.results_layout import in_family_layout  # noqa: E402


SOURCE_KEY_FIELDS = (
    "datetime",
    "exclusion_set",
    "number_of_parameters",
    "seed",
)


def metric_source_key(metric_path: Path, metrics_root: Path) -> tuple[str, ...]:
    relative_path = metric_path.resolve().relative_to(metrics_root.resolve())
    # test_metrics/<family>/<label>/<exclusion set...>/<report>
    if len(relative_path.parts) < 4:
        raise ValueError(
            f"Metric path lacks family/label/exclusion directories: {relative_path}"
        )

    filename_values = parse_metric_filename(metric_path)
    values = {
        "datetime": format_datetime(filename_values["timestamp"]),
        "exclusion_set": "/".join(relative_path.parts[2:-1]),
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

    skipped_layout = 0
    for metric_path in metric_paths:
        metric_path = Path(metric_path)
        relative_parts = metric_path.resolve().relative_to(metrics_root.resolve()).parts
        if not in_family_layout(relative_parts):
            # Old <root>/<label>/... layout (e.g. synced from a cluster not migrated
            # yet): reading it would take the label for a family. Skipped, counted.
            skipped_layout += 1
            continue
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

    if skipped_layout:
        print(
            f"Skipped {skipped_layout} reports outside the <family>/<label>/ layout; "
            "move them with scripts/tools/migrate_results_to_families.py"
        )
    if added_paths:
        write_table(table, rows)
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
        default=PROJECT_ROOT / "results" / "tables" / "metrics_summary.csv",
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
