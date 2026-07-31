#!/usr/bin/env python3
"""Create a label-first view of TensorBoard run directories."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from reorganize_test_metrics_by_label import (
    PROJECT_ROOT,
    metric_context,
    metric_timestamp,
    read_label,
    safe_path_part,
)


RUN_MANIFEST_FIELDS = (
    "timestamp",
    "label",
    "exclusion_set",
    "metric_path",
    "source_path",
    "destination_path",
    "status",
)


def run_id_from_metric(metric_path: Path) -> str:
    return metric_path.stem.removeprefix("test_metrics_")


def find_run_dir(
    metric_path: Path,
    metrics_root: Path,
    run_root: Path,
) -> tuple[Path | None, str, str, str]:
    architecture, exclusion_set = metric_context(metric_path, metrics_root)
    label = safe_path_part(read_label(metric_path))
    run_id = run_id_from_metric(metric_path)
    candidates = (
        run_root / label / exclusion_set / f"train{run_id}",
        run_root / architecture / exclusion_set / f"train{run_id}",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate, label, exclusion_set, run_id
    return None, label, exclusion_set, run_id


def write_manifest(manifest_path: Path, rows: list[dict[str, str]]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def copytree(source: Path, destination: Path, overwrite: bool) -> str:
    if destination.exists():
        if not overwrite:
            return "exists"
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        else:
            shutil.rmtree(destination)
    shutil.copytree(source, destination, symlinks=True)
    return "copy"


def symlink_dir(source: Path, destination: Path, overwrite: bool) -> str:
    if destination.exists() or destination.is_symlink():
        if not overwrite:
            return "exists"
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    destination.symlink_to(source.resolve(), target_is_directory=True)
    return "symlink"


def move_dir(source: Path, destination: Path, overwrite: bool) -> str:
    if destination.exists():
        if not overwrite:
            return "exists"
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    shutil.move(str(source), str(destination))
    return "move"


def apply_mapping(source: Path, destination: Path, mode: str, overwrite: bool) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "copy":
        return copytree(source, destination, overwrite)
    if mode == "symlink":
        return symlink_dir(source, destination, overwrite)
    if mode == "move":
        return move_dir(source, destination, overwrite)
    raise ValueError(f"Unsupported mode: {mode}")


def reorganize_runs(
    metrics_root: Path,
    run_root: Path,
    output_root: Path,
    manifest_path: Path,
    mode: str,
    apply: bool,
    overwrite: bool,
) -> list[dict[str, str]]:
    metrics_root = metrics_root.resolve()
    run_root = run_root.resolve()
    output_root = output_root.resolve()
    rows: list[dict[str, str]] = []

    for metric_path in sorted(metrics_root.rglob("test_metrics_*.txt")):
        source, label, exclusion_set, run_id = find_run_dir(
            metric_path,
            metrics_root,
            run_root,
        )
        destination = output_root / label / exclusion_set / f"train{run_id}"
        status = "missing"
        if source is not None:
            status = "planned"
            if apply:
                status = apply_mapping(source, destination, mode, overwrite)
        rows.append(
            {
                "timestamp": metric_timestamp(metric_path),
                "label": label,
                "exclusion_set": exclusion_set,
                "metric_path": str(metric_path),
                "source_path": "" if source is None else str(source),
                "destination_path": str(destination),
                "status": status,
            }
        )

    if apply:
        write_manifest(manifest_path, rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics-root", type=Path, default=PROJECT_ROOT / "test_metrics")
    parser.add_argument("--run-root", type=Path, default=PROJECT_ROOT / "run")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "run_by_label")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "run_by_label" / "manifest.csv",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "move", "symlink"),
        default="copy",
        help="Operation used with --apply. Default: copy.",
    )
    parser.add_argument("--apply", action="store_true", help="Write files. Omit for dry run.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing destination directories.")
    args = parser.parse_args()

    rows = reorganize_runs(
        args.metrics_root,
        args.run_root,
        args.output_root,
        args.manifest,
        args.mode,
        args.apply,
        args.overwrite,
    )
    statuses = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    status_text = ", ".join(f"{status}:{count}" for status, count in sorted(statuses.items()))
    action = "Applied" if args.apply else "Dry run"
    print(f"{action}: {len(rows)} metric-linked runs. {status_text}")
    if not args.apply:
        print("Use --apply to write output.")


if __name__ == "__main__":
    main()
