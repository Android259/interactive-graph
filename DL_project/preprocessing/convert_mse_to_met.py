#!/usr/bin/env python3
"""Rewrite selenomethionine (MSE) as ordinary methionine (MET) in a PDB file.

WHY

MSE is a methionine whose sulfur is replaced by selenium -- introduced during
expression to phase the crystallographic data, not a property of the protein. The PDB
format stores it as a HETATM with residue name MSE, so
preprocessing/voronota-js-receptor-data-graph drops it: its line

    voronota_restrict_atoms("-use", "[-protein]");

keeps only atoms typed as protein, and MSE is not one. The result is a graph with a
hole where a real residue sits: GM2A loses 2 residues, PITPNA loses 8, and their
sequence neighbours end up contacting each other directly across the gap.

preprocessing/pdb2fasta.py already treats MSE as 'M' (its ca_pattern matches the MSE
HETATM explicitly), so the FASTA -- and therefore the ESM3 v1 embedding -- always had
these residues. Converting them here makes the graph agree with the sequence at the
source, instead of patching the mismatch downstream.

WHAT IS CHANGED (only these four fields, only on MSE records)

    record name   HETATM -> ATOM
    residue name  MSE    -> MET
    atom name     SE     -> SD    (methionine's sulfur is named SD)
    element       SE     -> S

Coordinates, chain, residue number, occupancy and B-factor are copied verbatim; every
non-MSE line, including other HETATM groups (waters, buffer molecules, ligands), is
passed through untouched so that Voronota keeps excluding them.

USAGE
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
