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
    # "random" alongside "groups_*": a --random_split label holds nothing out, so
    # new_train.py files it under that name instead of a "groups_" directory, and a
    # glob for the prefix alone would find none of its reports -- the run would never
    # count as completed and --complete would relaunch it forever.
    reports = sorted(label_root.glob("groups_*/*.txt")) + sorted(
        label_root.glob("random/*.txt")
    )
    for report in reports:
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
            if not isinstance(excluded, list):
                continue
            if excluded:
                if len(excluded) != 1:
                    continue
                group = str(excluded[0])
            else:
                # Three axes leave excluded_groups empty, and each names its grid
                # position with a different field. --lipid_coldsplit holds a set of
                # lipid classes out, --family_only restricts the table to one family,
                # and --random_split holds nothing out at all -- for that last one the
                # position is the single literal the grid iterates. Without this the
                # report is skipped, the run never counts as completed, and --complete
                # relaunches it forever.
                isolation = str(fields.get("lipid_isolation", ""))
                group = (
                    str(fields.get("lipid_coldsplit", ""))
                    or (f"iso{isolation}" if isolation else "")
                    or str(fields.get("family_only", ""))
                    or "random"
                )
        if group:
            completed.add((group, seed))

    for group, seed in sorted(completed):
        print(f"{group}:{seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
