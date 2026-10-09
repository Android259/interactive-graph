#!/usr/bin/env python3
"""Shape descriptors of each protein's binding cavity, from files already on disk.

Why this exists
---------------
The descriptor the model can already use (POCKET_DESCRIPTOR_NAMES in
dataloader/graphs_builders/protein_graph_builder.py) is 13 sums or means over the pocket residues and
one maximum. An average has no shape: a long narrow channel and a round bowl with the
same total surface and the same mean burial produce the same numbers. What decides
which lipid fits is exactly the shape the averaging removes -- how far the cavity
extends, how narrow it is, and how the enclosure is distributed between its mouth and
its depth.

Everything here is computed from `data/graphs/<protein>/pocketness.pdb` (atom
coordinates, with the pocket flag in the B-factor column) and the Voronota residue
table beside it. No new tool, no new data.

The pocket is defined exactly as the dataloader defines it, so these descriptors
describe the same site the model sees: side-chain atoms only (backbone C, CA, CB, O, N
excluded), a residue counts as pocket if any of its side-chain atoms is flagged.

Documented in files/reference/pocket_shape_descriptors.md, which also carries the measurement
against acyl chain length. Change the descriptor set here and that file changes in the
same commit -- a description that has fallen behind the code is worse than none, since
conclusions get drawn from it without rereading this.

Lives in preprocessing/, not analysis/, because it IS a descriptor calculation path
(this project's own rule: the whole descriptor-computation path lives here, analysis/
only reads and reports) -- it was moved from analysis/pocket_shape_descriptors.py.

Usage:
    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py
    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py --full
    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py --out pocket_shape.csv

The default printout is grouped by section 3 of the note above; --full is the single
wide frame; --out writes every column at full precision either way.
"""

import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.compute_descriptors import (  # noqa: E402
    AROMATIC_RESIDUE_TYPES,
    KYTE_DOOLITTLE,
    POCKET_BACKBONE_ATOMS,
    pocket_atom_coordinates,
    pocket_shape_full,
)

# numpy array for direct fancy indexing (KYTE_DOOLITTLE[residue_types]); preprocessing's
# own tuple is the one source of the 20 values, this is just the local access form.
_KYTE_DOOLITTLE = np.asarray(KYTE_DOOLITTLE)


def read_pocket_atoms(pocketness_pdb):
    """Coordinates of the side-chain atoms flagged as pocket (preprocessing's own
    pocket_atom_coordinates -- identical line format and flag column, read once, not
    duplicated here), plus which residues carry at least one such atom and which
    residues exist at all (both needed to mask coarse_graph_nodes.csv, which
    pocket_atom_coordinates alone does not track since it only returns coordinates).

    Column offsets are the PDB standard ones and the flag is read exactly where the
    dataloader reads it (line[62], the integer digit of the B-factor field), so a
    residue is in the pocket here if and only if it is in the pocket there.
    """
    coordinates = pocket_atom_coordinates(pocketness_pdb)
    pocket_residues = set()
    all_residues = []
    seen = set()
    with open(pocketness_pdb) as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")) or len(line) < 63:
                continue
            residue = line[22:28].strip()
            if residue not in seen:
                seen.add(residue)
                all_residues.append(residue)
            if line[13:17].strip() in POCKET_BACKBONE_ATOMS:
                continue
            if int(line[62]) <= 0:
                continue
            pocket_residues.add(residue)
    return coordinates, pocket_residues, all_residues


def descriptors_for(protein_dir):
    nodes = pd.read_csv(protein_dir / "coarse_graph_nodes.csv")
    coordinates, pocket_residues, all_residues = read_pocket_atoms(protein_dir / "pocketness.pdb")
    if not pocket_residues:
        return None

    # The residue table and the PDB are the same residues in the same order, which is
    # what lets a mask built from residue keys index the table.
    key = [str(int(value)) if float(value).is_integer() else str(value)
           for value in nodes["ID_resSeq"]]
    mask = np.array([residue in pocket_residues for residue in key])
    if mask.sum() == 0:
        return None
    site = nodes[mask]

    row = {"protein": protein_dir.name, "pocket_residues": int(mask.sum()),
           "protein_residues": int(len(nodes))}

    if len(coordinates) < 4:
        return None
    row.update(pocket_shape_full(coordinates))

    sasa = float(site["residue_sas_area"].sum())
    volume = float(site["residue_volume"].sum())
    # Hydraulic radius: shape without scale in the crudest possible form. A wide open
    # bowl and a narrow channel of the same volume differ here and nowhere in the
    # existing descriptor.
    row["pocket_volume_per_sasa"] = volume / max(sasa, 1e-9)

    # Distributions where the current descriptor keeps only a mean. The deep end of the
    # cavity is what holds a chain; the mean mixes it with the rim.
    for column, name in (
        ("residue_mean_ev14", "ev14"),
        ("residue_mean_ev28", "ev28"),
        ("residue_mean_ev56", "ev56"),
        ("residue_mean_buriedness", "buriedness"),
        ("residue_mean_voromqa_depth", "depth"),
    ):
        if column not in site:
            continue
        values = site[column].to_numpy(dtype=float)
        for quantile in (10, 50, 90):
            row[f"{name}_q{quantile}"] = float(np.percentile(values, quantile))

    # Mouth and depth answer different questions -- head-group recognition happens at
    # the entrance, chain packing inside -- so their chemistry is reported apart
    # instead of averaged together. The split is the pocket's own median burial.
    hydropathy = _KYTE_DOOLITTLE[site["residue_type"].to_numpy(dtype=int)]
    aromatic = np.isin(site["residue_type"].to_numpy(dtype=int), AROMATIC_RESIDUE_TYPES)
    if "residue_mean_buriedness" in site:
        burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
        core = burial >= np.median(burial)
        row["hydropathy_core"] = float(hydropathy[core].mean())
        row["hydropathy_rim"] = float(hydropathy[~core].mean()) if (~core).any() else float("nan")
        row["aromatic_share_core"] = float(aromatic[core].mean())
        row["aromatic_share_rim"] = float(aromatic[~core].mean()) if (~core).any() else float("nan")
    # Aromatic cages are characteristic of lipid cavities and the Kyte-Doolittle scale
    # cannot express them: it scores Phe with the aliphatics and Trp near zero.
    row["aromatic_share"] = float(aromatic.mean())
    row["hydropathy_mean"] = float(hydropathy.mean())
    return row


# The printed table is grouped the way files/reference/pocket_shape_descriptors.md section 3
# groups it, because the two get read side by side: 31 columns on one 444-character
# line is a table nobody looks at twice. Header text only -- the CSV keeps every
# column, in one wide frame, so nothing downstream has to know about this.
COLUMN_BLOCKS = (
    ("size (residues)", ["pocket_residues", "protein_residues"]),
    ("shape: cavity axes (3.1)", [
        "pocket_extent", "pocket_width", "pocket_thickness",
        "pocket_elongation", "pocket_flatness", "pocket_gyration",
    ]),
    ("shape without scale (3.2)", ["pocket_volume_per_sasa"]),
    ("enclosure: exposure quantiles (3.3)", [
        "ev14_q10", "ev14_q50", "ev14_q90",
        "ev28_q10", "ev28_q50", "ev28_q90",
        "ev56_q10", "ev56_q50", "ev56_q90",
    ]),
    ("enclosure: burial and depth (3.3)", [
        "buriedness_q10", "buriedness_q50", "buriedness_q90",
        "depth_q10", "depth_q50", "depth_q90",
    ]),
    ("chemistry: core vs rim (3.4)", [
        "hydropathy_core", "hydropathy_rim", "hydropathy_mean",
        "aromatic_share_core", "aromatic_share_rim", "aromatic_share",
    ]),
)

# Angstroms, so the reader is not left guessing which numbers carry a scale. The ratios
# and shares are dimensionless and get nothing.
UNITS = {name: "A" for name in (
    "pocket_extent", "pocket_width", "pocket_thickness", "pocket_gyration",
)}


def saturated_columns(table, tolerance=0.9):
    """Columns pinned at one value for nearly every protein, and by what share.

    Section 3.5 names ev56 and the upper ev28 quantiles as saturated at 2.0, which makes
    them incapable of correlating with anything. Detected rather than hard-coded: the
    point is to catch the NEXT column that goes flat, not to restate a known list.

    0.9 is not a knob to tune. The measured shares fall 1.00, 1.00, 0.94, then 0.20 --
    a gap wide enough that any threshold in between names the same three columns.
    """
    flat = {}
    for name in table.columns:
        values = table[name].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        if len(finite) == 0:
            continue
        commonest = pd.Series(finite).value_counts(normalize=True).iloc[0]
        if commonest >= tolerance:
            flat[name] = float(commonest)
    return flat


def print_blocks(table):
    """One narrow table per group, each with the median across proteins under it."""
    flat = saturated_columns(table)
    shown = set()
    for title, columns in COLUMN_BLOCKS:
        present = [name for name in columns if name in table.columns]
        if not present:
            continue
        shown.update(present)
        # Rendered to strings rather than rounded in place: appending the median row to a
        # numeric frame turns a residue count into "37.0", which is exactly the noise
        # this grouping is meant to remove. Counts print as counts.
        block = pd.DataFrame(index=list(table.index) + ["-- median --"])
        for name in present:
            values = table[name]
            whole = bool(values.dropna().apply(lambda v: float(v).is_integer()).all())
            column = pd.concat([values, pd.Series({"-- median --": values.median()})])
            block[
                # A saturated column is marked where it is read, not in a footnote
                # further away than the number it warns about.
                f"{name}{' [A]' if name in UNITS else ''}{' !flat' if name in flat else ''}"
            ] = column.map(lambda v: "" if pd.isna(v) else (f"{v:.0f}" if whole else f"{v:.3f}"))
        print(f"\n{title}")
        print(block.to_string())

    # Anything a later commit adds lands here instead of disappearing from the printout.
    missing = [name for name in table.columns if name not in shown]
    if missing:
        print("\nnot in any block (add it to COLUMN_BLOCKS)")
        print(table[missing].round(3).to_string())

    if flat:
        named = ", ".join(f"{name} ({100 * share:.0f}%)" for name, share in sorted(flat.items()))
        print(
            "\n!flat = same value for nearly every protein, so the column has almost no "
            f"variance left to correlate with anything: {named}"
        )
    print(f"\n{len(table)} proteins, {len(table.columns)} descriptors."
          " Use --full for the single wide table, --out for the CSV.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphs", type=Path, default=PROJECT_ROOT / "data" / "graphs")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--full", action="store_true",
                        help="print all columns as one wide table instead of by group")
    args = parser.parse_args()

    rows = []
    for protein_dir in sorted(Path(args.graphs).iterdir()):
        if not (protein_dir / "pocketness.pdb").is_file():
            continue
        row = descriptors_for(protein_dir)
        if row is not None:
            rows.append(row)
    table = pd.DataFrame(rows).set_index("protein")

    if args.full:
        pd.set_option("display.width", 200)
        print(table.round(3).to_string())
    else:
        print_blocks(table)

    if args.out:
        table.to_csv(args.out)
        print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
