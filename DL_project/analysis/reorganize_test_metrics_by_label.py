#!/usr/bin/env python3
"""Create a label-first view of test metric reports."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRIC_FILENAME = re.compile(r"^test_metrics_(?P<timestamp>\d{8}_\d{6})_.*\.txt$")
SAFE_PART = re.compile(r"[^A-Za-z0-9._=-]+")


MANIFEST_FIELDS = (
    "timestamp",
    "label",
    "exclusion_set",
    "source_path",
    "destination_path",
    "status",
)


def safe_path_part(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Empty label")
    value = SAFE_PART.sub("_", value)
    value = value.strip("._")
    if not value:
        raise ValueError("Empty label after path sanitizing")
    return value


def read_label(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line == "per_protein_subgroup_metrics:":
                break
            if line.startswith("label:"):
                label = line.split(":", 1)[1].strip()
                if not label:
                    raise ValueError(f"Empty label in metric file: {path}")
                return label
    raise ValueError(f"Missing label in metric file: {path}")


def metric_timestamp(path: Path) -> str:
    match = METRIC_FILENAME.match(path.name)
    if match is None:
        raise ValueError(f"Unsupported metric filename: {path}")
    return match.group("timestamp")


def metric_context(path: Path, metrics_root: Path) -> tuple[str, str]:
    relative = path.resolve().relative_to(metrics_root.resolve())
    if len(relative.parts) < 3:
        raise ValueError(f"Metric path lacks label/exclusion directories: {relative}")
    exclusion_set = "/".join(relative.parts[1:-1])
    return relative.parts[0], exclusion_set


def destination_for(path: Path, metrics_root: Path, output_root: Path) -> Path:
    label = safe_path_part(read_label(path))
    _, exclusion_set = metric_context(path, metrics_root)
    return output_root / label / exclusion_set / path.name


def write_manifest(manifest_path: Path, rows: list[dict[str, str]]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def apply_mapping(source: Path, destination: Path, mode: str, overwrite: bool) -> str:
    if destination.exists():
        if not overwrite:
            return "exists"
        if destination.is_dir():
            raise IsADirectoryError(destination)
        destination.unlink()

    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "copy":
        shutil.copy2(source, destination)
    elif mode == "move":
        shutil.move(str(source), str(destination))
    elif mode == "symlink":
        destination.symlink_to(source.resolve())
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    return mode


def reorganize_metrics(
    metrics_root: Path,
    output_root: Path,
    manifest_path: Path,
    mode: str,
    apply: bool,
    overwrite: bool,
) -> list[dict[str, str]]:
    metrics_root = metrics_root.resolve()
    output_root = output_root.resolve()
    manifest_path = manifest_path.resolve()
    rows: list[dict[str, str]] = []

    for source in sorted(metrics_root.rglob("test_metrics_*.txt")):
        destination = destination_for(source, metrics_root, output_root)
        _, exclusion_set = metric_context(source, metrics_root)
        label = safe_path_part(read_label(source))
        status = "planned"
        if apply:
            status = apply_mapping(source, destination, mode, overwrite)

        rows.append(
            {
                "timestamp": metric_timestamp(source),
                "label": label,
                "exclusion_set": exclusion_set,
                "source_path": str(source),
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
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "test_metrics_by_label",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "test_metrics_by_label" / "manifest.csv",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "move", "symlink"),
        default="copy",
        help="Operation used with --apply. Default: copy.",
    )
    parser.add_argument("--apply", action="store_true", help="Write files. Omit for dry run.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing destination files.")
    args = parser.parse_args()

    rows = reorganize_metrics(
        args.metrics_root,
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
    print(f"{action}: {len(rows)} metric files. {status_text}")
    if not args.apply:
        print("Use --apply to write output.")


if __name__ == "__main__":
    main()
