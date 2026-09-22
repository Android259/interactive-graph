#!/usr/bin/env python3
"""One-time conversion of data/Lipid_Volumes.xlsx to data/Lipid_Volumes.csv.

Every other data artifact in this project is CSV/JSON/npy/pkl -- this sheet was the
lone .xlsx, which cost two things a plain CSV does not: a hard `openpyxl` dependency
(dataloader/pair_descriptors.py's `_experimental_lipid_volume_table` calls
`pandas.read_excel`, which raises ImportError without it -- this machine has neither
`openpyxl` nor the sibling `.xls`'s `xlrd`), and a file that never reaches the cluster
at all -- scripts/lib/cluster_sync_excludes.sh protects the whole data/ directory from
being refreshed by an ordinary code sync, and .xlsx was never one of the handful of
data/ files carved out of that protection (Processed_*.csv, Tanimoto_compact*, ...),
so it silently stayed local-only. That surfaced as a bare FileNotFoundError on Bigfoot
the first time an arg file's descriptor set actually needed it.

Parses the .xlsx directly as what it is -- a zip of small XML files (the OOXML
spreadsheet format) -- rather than importing a spreadsheet library: `zipfile` +
`xml.etree.ElementTree`, both standard library, so this script (and, after this
change, the reader in pair_descriptors.py) needs nothing beyond what every other
script in this project already needs. Reads the workbook's one sheet, resolves
shared-string cells against xl/sharedStrings.xml, and writes every column through
unchanged -- no unit conversion, no filtering.

Not independently checked against a real pandas.read_excel/openpyxl reading of the
same file -- neither is installed on the machine this was written on, which is the
whole reason this script exists. What WAS checked (see preprocessing/verify_lipid_
volumes_csv.py): every value this script emits for a structure already present in
data/pair_descriptor_cache_deterministic_v2.json's experimental_lipid_volume entries
(computed earlier, on whichever machine last had openpyxl and ran that cache build)
agrees with the cached figure. That is real agreement for whatever fraction of this
sheet the cache happened to already cover, not a guarantee for the rest of it -- if
openpyxl becomes available later, running pandas.read_excel once and diffing its
output against data/Lipid_Volumes.csv directly is the check that closes that gap.

Usage:
    python3 preprocessing/convert_lipid_volumes_xlsx.py
    python3 preprocessing/convert_lipid_volumes_xlsx.py --input data/Lipid_Volumes.xlsx \\
        --output data/Lipid_Volumes.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_COLUMN_LETTERS = re.compile(r"[A-Z]+")


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    """xl/sharedStrings.xml -> the strings it holds, in index order.

    A shared string can itself carry rich-text runs (<r><t>...</t></r>) rather than a
    single plain <t>; concatenating every <t> under the entry (regardless of nesting)
    handles both, the same way a spreadsheet application displaying the cell would.
    """
    with archive.open("xl/sharedStrings.xml") as handle:
        root = ElementTree.parse(handle).getroot()
    return [
        "".join(node.text or "" for node in entry.iter(f"{{{NAMESPACE['s']}}}t"))
        for entry in root.findall("s:si", NAMESPACE)
    ]


def _column_letters(cell_reference: str) -> str:
    """"C57" -> "C" -- which column a cell belongs to, for building one CSV row."""
    match = _COLUMN_LETTERS.match(cell_reference)
    if not match:
        raise ValueError(f"cell reference {cell_reference!r} has no column letters")
    return match.group(0)


def _column_index(letters: str) -> int:
    """"A" -> 0, "B" -> 1, ... "AA" -> 26 -- base-26, letters-as-digits."""
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter) - ord("A") + 1)
    return index - 1


def read_sheet(xlsx_path: Path) -> list[list[str]]:
    """Every row of the workbook's first (and, for this file, only) sheet, as plain
    strings -- cell reference gaps (a skipped empty cell) are filled with "", so every
    row comes back the same width as the widest row seen so far.
    """
    with zipfile.ZipFile(xlsx_path) as archive:
        strings = _shared_strings(archive)
        with archive.open("xl/worksheets/sheet1.xml") as handle:
            root = ElementTree.parse(handle).getroot()

    rows: list[list[str]] = []
    width = 0
    for row_node in root.findall(".//s:sheetData/s:row", NAMESPACE):
        cells: dict[int, str] = {}
        for cell_node in row_node.findall("s:c", NAMESPACE):
            column = _column_index(_column_letters(cell_node.get("r")))
            value_node = cell_node.find("s:v", NAMESPACE)
            if value_node is None or value_node.text is None:
                text = ""
            elif cell_node.get("t") == "s":
                text = strings[int(value_node.text)]
            else:
                text = value_node.text
            cells[column] = text
        width = max(width, (max(cells) + 1) if cells else 0)
        rows.append(cells)

    return [[row.get(column, "") for column in range(width)] for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "Lipid_Volumes.xlsx")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "Lipid_Volumes.csv")
    args = parser.parse_args()

    rows = read_sheet(args.input)
    with open(args.output, "w", newline="") as handle:
        csv.writer(handle).writerows(rows)

    print(f"{args.input} -> {args.output}: {len(rows) - 1} data rows, {len(rows[0])} columns")
    print(f"header: {rows[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
