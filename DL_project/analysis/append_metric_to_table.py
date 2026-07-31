#!/usr/bin/env python3
"""Add or replace one completed test metric report in the shared CSV table."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_metrics_table import PROJECT_ROOT, metric_row, upsert_row
from training.read_configuration import ModelConfig


def append_metric(
    metric_file: Path,
    metrics_root: Path = PROJECT_ROOT / "test_metrics",
    run_root: Path = PROJECT_ROOT / "run",
    table: Path = PROJECT_ROOT / "metrics_summary.csv",
    include_tensorboard: bool = True,
    analysis_path: Path | None = None,
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
    upsert_row(table, row)
    from analyze_metrics_table import update_analysis

    if analysis_path is None:
        analysis_path = Path(table).with_name("metrics_analysis.txt")
    update_analysis(table, analysis_path)
    from analyze_feature_contributions import write_feature_contributions

    write_feature_contributions(
        table,
        Path(table).with_name("feature_contributions.csv"),
        "checkpoint_valid_balanced_accuracy",
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metric_file", type=Path)
    parser.add_argument("--metrics-root", type=Path, default=PROJECT_ROOT / "test_metrics")
    parser.add_argument("--run-root", type=Path, default=PROJECT_ROOT / "run")
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
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
