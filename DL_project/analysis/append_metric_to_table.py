#!/usr/bin/env python3
"""Add or replace one completed test metric report in the shared CSV table."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_metrics_table import PROJECT_ROOT, metric_row, upsert_row
from training.read_configuration import ModelConfig


def append_metric(
    metric_file: str | Path,
    metrics_root: Path = PROJECT_ROOT / "test_metrics",
    run_root: Path = PROJECT_ROOT / "run",
    table: str | Path = PROJECT_ROOT / "results" / "tables" / "metrics_summary.csv",
    include_tensorboard: bool = True,
    config: ModelConfig | None = None,
    script_logs_root: Path = PROJECT_ROOT / "script_logs",
) -> dict[str, str]:
    row = metric_row(
        Path(metric_file),
        metrics_root,
        run_root,
        include_tensorboard,
        config=config,
        script_logs_root=script_logs_root,
    )
    # Path(), like metric_row's above: training/run_paths.py's RunPaths is all-str
    # (every field an os.path.join), so the run that finishes hands `table` over as
    # text while upsert_row works on it as a path.
    upsert_row(Path(table), row)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metric_file", type=Path)
    parser.add_argument("--metrics-root", type=Path, default=PROJECT_ROOT / "test_metrics")
    parser.add_argument("--run-root", type=Path, default=PROJECT_ROOT / "run")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "results" / "tables" / "metrics_summary.csv")
    parser.add_argument("--script-logs-root", type=Path, default=PROJECT_ROOT / "script_logs")
    parser.add_argument("--no-tensorboard", action="store_true")
    args = parser.parse_args()

    row = append_metric(
        args.metric_file,
        args.metrics_root,
        args.run_root,
        args.table,
        not args.no_tensorboard,
        script_logs_root=args.script_logs_root,
    )
    print(f"Upserted {row['datetime']} into {args.table}")


if __name__ == "__main__":
    main()
