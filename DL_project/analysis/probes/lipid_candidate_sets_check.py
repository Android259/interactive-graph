#!/usr/bin/env python3
"""Do all rows of one lipid list the same candidate structures? Prints the lipids where not.

For each FullIdentityOfLipid compares, row by row, the SET of canonical candidate SMILES
(order ignored), and shows how the rows differ. Read-only.

    python3 analysis/probes/lipid_candidate_sets_check.py
"""
import os
import sys

import pandas
from rdkit import Chem

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from dataloader.dataset_source import interaction_csv_path
from dataloader.pocket_lipid_compatibility import candidate_fields_by_row


def canonical(raw):
    molecule = Chem.MolFromSmiles(raw)
    return None if molecule is None else Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=False)


def main():
    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data")))
    fields = candidate_fields_by_row(csv)
    rows_of = {}
    for position, lipid in enumerate(csv["FullIdentityOfLipid"]):
        rows_of.setdefault(lipid, []).append(position)
    different = 0
    for lipid, positions in rows_of.items():
        sets = {}
        for position in positions:
            sets.setdefault(frozenset(canonical(raw) for raw in fields[position]), []).append(position)
        if len(sets) == 1:
            continue
        different += 1
        print(f"\n{lipid}: {len(positions)} rows, {len(sets)} different candidate sets")
        for found, where in sets.items():
            row = csv.iloc[where[0]]
            print(f"  {len(where)} rows (e.g. protein {row['LTPProtein']}), {len(found)} structures, "
                  f"SmileGlobal={str(row['SmileGlobal'])[:30]!r}, SmileFragment={str(row['SmileFragment'])[:30]!r}")
        first_set = frozenset(canonical(raw) for raw in fields[positions[0]])
        print(f"  first row of the lipid is in the group of {len(sets[first_set])} row(s)")
        odd = [w for w in sets.values() if len(w) == 1][0][0]
        majority = [w for w in sets.values() if len(w) > 1][0][0]
        for label, position in (("odd     ", odd), ("majority", majority)):
            row = csv.iloc[position]
            extras = {c: str(row[c])[:40] for c in ("Lipid", "Screen", "Interaction") if c in csv.columns}
            print(f"  {label} row {position}: protein {row['LTPProtein']}, {extras}")
        mine = frozenset(canonical(raw) for raw in fields[odd])
        theirs = frozenset(canonical(raw) for raw in fields[majority])
        print(f"  only in odd row: {len(mine - theirs)} structures; only in majority: {len(theirs - mine)}; shared: {len(mine & theirs)}")
        union = frozenset().union(*sets)
        for found, where in sets.items():
            missing = union - found
            print(f"     missing here vs union: {len(missing)}; has None: {None in found}")
    print(f"\n{len(rows_of)} lipids; {different} have rows with different candidate sets")


if __name__ == "__main__":
    main()
