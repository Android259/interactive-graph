#!/usr/bin/env python3
"""eta^2 against family for the pocket descriptors NOT in production.

pocket_descriptor_identity_check.py (same directory) measured how much of each of the
13 POCKET_DESCRIPTOR_NAMES entries is family identity in disguise, and that measurement
is what selected POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES (dataloader/protein_graph_
builder.py) -- the 7 entries scoring at or near the no-structure floor.

analysis/pocket_shape_descriptors.py's research catalog computes several more numbers
from the exact same on-disk files (pocketness.pdb, coarse_graph_nodes.csv) that never
went into POCKET_DESCRIPTOR_NAMES at all: pocket_width, pocket_thickness, pocket_
gyration, the full ev14/ev28/ev56 quantile triplets (production keeps only ev14_q50),
buriedness_q10/q90 and depth_q50/q90 (production keeps only buriedness_q50/depth_q10),
hydropathy_mean, and aromatic_share_core/aromatic_share_rim. None of these has ever been
through the eta^2 check -- this script runs it, on the identical protein/family universe
identity_check.py uses, so a result here is directly comparable to files/pocket_shape_
descriptors.md section 5's table.

This is eta^2 only (measurement 2 of identity_check.py's three) -- the Mantel test and
nearest-neighbour checks need the SAME matrix for every column at once and are already
answered for the production set; a candidate that clears eta^2 here still wants that
before it goes anywhere near the model, same as section 5's own caveat.

Usage:
    python3 preprocessing/pocket_descriptor_candidate_identity_check.py
"""

import sys
from pathlib import Path

import numpy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.pocket_shape_descriptors import descriptors_for  # noqa: E402
from dataloader.protein_graph_builder import POCKET_DESCRIPTOR_NAMES  # noqa: E402
from pocket_descriptor_identity_check import (  # noqa: E402
    eta_squared,
    mean_plm_embedding,
    protein_families,
)

# Every research-catalog column NOT already in POCKET_DESCRIPTOR_NAMES. Order matches
# files/pocket_shape_descriptors.md's own COLUMN_BLOCKS grouping.
CANDIDATE_NAMES = tuple(
    name for name in (
        "pocket_width", "pocket_thickness", "pocket_gyration",
        "ev14_q10", "ev14_q90",
        "ev28_q10", "ev28_q50", "ev28_q90",
        "ev56_q10", "ev56_q50", "ev56_q90",
        "buriedness_q10", "buriedness_q90",
        "depth_q50", "depth_q90",
        "hydropathy_mean", "aromatic_share_core", "aromatic_share_rim",
    )
    if name not in POCKET_DESCRIPTOR_NAMES
)


def main():
    families_by_protein = protein_families()
    proteins, rows = [], []
    for protein_dir in sorted((PROJECT_ROOT / "data" / "graphs").iterdir()):
        name = protein_dir.name
        if not (protein_dir / "pocketness.pdb").is_file() or name not in families_by_protein:
            continue
        # Same ESM3-availability filter identity_check.py uses, kept only so this
        # script's protein set is the identical 35 -- eta^2 itself does not need the
        # embedding, but a floor/count comparable to section 5's table does.
        if mean_plm_embedding(name) is None:
            continue
        row = descriptors_for(protein_dir)
        if row is None:
            continue
        proteins.append(name)
        rows.append(row)

    families = numpy.array([families_by_protein[name] for name in proteins])
    floor = (len(numpy.unique(families)) - 1) / (len(families) - 1)
    print(f"{len(proteins)} proteins, {len(numpy.unique(families))} families")
    print(f"a number with no family structure scores {floor:.3f} here, not 0\n")

    scored = []
    for name in CANDIDATE_NAMES:
        values = numpy.array([row.get(name, float("nan")) for row in rows], dtype=float)
        finite = numpy.isfinite(values)
        if finite.sum() < len(values):
            missing = len(values) - int(finite.sum())
            note = f"({missing} protein(s) missing this column)"
        else:
            note = ""
        spread = values[finite].std() if finite.any() else 0.0
        if not finite.any() or spread < 1e-9:
            scored.append((float("nan"), name, "saturated/constant -- eta^2 undefined", note))
            continue
        score = eta_squared(values[finite], families[finite])
        scored.append((score, name, "", note))

    scored.sort(key=lambda item: (-item[0] if item[0] == item[0] else float("inf"), item[1]))
    print(f"{'descriptor':<24}{'eta^2':>8}  vs floor")
    for score, name, flag, note in scored:
        if score != score:
            print(f"  {name:<22}{'nan':>8}  {flag} {note}")
            continue
        bar = "#" * int(round(score * 30))
        above = "above floor" if score > floor else "at/below floor"
        print(f"  {name:<22}{score:>8.3f}  {above:<15}{bar} {note}")


if __name__ == "__main__":
    main()
