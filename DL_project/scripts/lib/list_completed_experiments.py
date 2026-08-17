#!/usr/bin/env python3
"""List completed group/seed pairs from final test-metric reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(errors="replace").splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--reports-root", default="test_metrics")
    parser.add_argument("--cold-split", action="store_true")
    args = parser.parse_args()

    label_root = Path(args.reports_root) / args.label
    completed: set[tuple[str, int]] = set()
    for report in label_root.glob("groups_*/*.txt"):
        fields = read_fields(report)
        if fields.get("label") != args.label:
            continue
        is_cold = fields.get("cold_split", "0") in {"1", "true", "True"}
        if is_cold != args.cold_split:
            continue
        try:
            seed = int(fields["seed"])
        except (KeyError, ValueError):
            continue

        if args.cold_split:
            group = fields.get("test_group", "")
        else:
            try:
                excluded = json.loads(fields["excluded_groups"])
            except (KeyError, json.JSONDecodeError):
                continue
            if not isinstance(excluded, list) or len(excluded) != 1:
                continue
            group = str(excluded[0])
        if group:
            completed.add((group, seed))

    for group, seed in sorted(completed):
        print(f"{group}:{seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
