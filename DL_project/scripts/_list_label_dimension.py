#!/usr/bin/env python3
"""Print the sorted unique values of one column for rows matching a label.

Usage: _list_label_dimension.py TABLE LABEL COLUMN [FIELD=VALUE ...]

Any trailing FIELD=VALUE arguments further restrict the rows by exact string
match, e.g. run_status=complete or exclusion_set=groups_ML.
"""

from __future__ import annotations

import csv
import sys


def main() -> None:
    table_path, label, column = sys.argv[1], sys.argv[2], sys.argv[3]
    extra_filters = []
    for expression in sys.argv[4:]:
        if "=" not in expression:
            raise SystemExit(f"expected FIELD=VALUE filter, got {expression!r}")
        field, value = expression.split("=", 1)
        extra_filters.append((field, value))
    with open(table_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    values = sorted(
        {
            row[column]
            for row in rows
            if row.get("label") == label
            and all(row.get(field, "") == value for field, value in extra_filters)
        }
    )
    print("\n".join(values))


if __name__ == "__main__":
    main()
