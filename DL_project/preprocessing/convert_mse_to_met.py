#!/usr/bin/env python3
"""Convert MSE residues to MET before building protein graphs.

Voronota's protein filter excludes MSE HETATM records. For each MSE record, change:
    HETATM -> ATOM
    residue MSE -> MET
    atom SE -> SD
    element SE -> S

Preserve coordinates, residue identifiers, occupancy and B-factors. Copy non-MSE
records unchanged. pdb2fasta.py also reads MSE as methionine.

    python3 preprocessing/convert_mse_to_met.py input.pdb output.pdb
"""
from __future__ import annotations

import argparse
import sys


def convert_line(line: str) -> tuple[str, bool]:
    """Return (line, changed) with one MSE atom record rewritten as MET."""
    if not line.startswith("HETATM") or line[17:20] != "MSE":
        return line, False

    atom_name = line[12:16]
    element = line[76:78]
    if atom_name.strip() == "SE":
        atom_name = " SD "
    if element.strip() == "SE":
        element = " S"

    return (
        "ATOM  " + line[6:12] + atom_name + line[16:17] + "MET" + line[20:76]
        + element + line[78:]
    ), True


def convert_file(source: str, destination: str) -> int:
    changed = 0
    with open(source) as handle_in, open(destination, "w") as handle_out:
        for line in handle_in:
            new_line, was_changed = convert_line(line)
            changed += was_changed
            handle_out.write(new_line)
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()

    count = convert_file(args.source, args.destination)
    print(f"{args.source} -> {args.destination}: {count} MSE atom records rewritten as MET")
    if count == 0:
        print("nothing to convert (no MSE records)", file=sys.stderr)
