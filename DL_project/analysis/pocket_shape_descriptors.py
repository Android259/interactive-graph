#!/usr/bin/env python3
"""Shape descriptors of each protein's binding cavity, from files already on disk.

Why this exists
---------------
The descriptor the model can already use (POCKET_DESCRIPTOR_NAMES in
dataloader/protein_graph_builder.py) is 13 sums or means over the pocket residues and
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

Documented in files/pocket_shape_descriptors.md, which also carries the measurement
against acyl chain length. Change the descriptor set here and that file changes in the
same commit -- a description that has fallen behind the code is worse than none, since
conclusions get drawn from it without rereading this.

Usage:
    scripts/env.sh python3 analysis/pocket_shape_descriptors.py
    scripts/env.sh python3 analysis/pocket_shape_descriptors.py --full
    scripts/env.sh python3 analysis/pocket_shape_descriptors.py --out pocket_shape.csv

The default printout is grouped by section 3 of the note above; --full is the single
wide frame; --out writes every column at full precision either way.
"""

import argparse
import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKBONE_ATOMS = {"C", "CA", "CB", "O", "N"}
# Voronota's residue_type code, verified against ID_resName: alphabetical by one-letter
# code, which is also the order KYTE_DOOLITTLE is indexed in.
RESIDUE_ORDER = "A R N D C Q E G H I L K M F P S T W Y V".split()
AROMATIC_CODES = {RESIDUE_ORDER.index(letter) for letter in ("F", "W", "Y")}
KYTE_DOOLITTLE = np.array([
    1.8, -4.5, -3.5, -3.5, 2.5, -3.5, -3.5, -0.4, -3.2, 4.5,
    3.8, -3.9, 1.9, 2.8, -1.6, -0.8, -0.7, -0.9, -1.3, 4.2,
])


def read_pocket_atoms(pocketness_pdb):
    """Coordinates of the side-chain atoms flagged as pocket, and the residues they belong to.

    Column offsets are the PDB standard ones and the flag is read exactly where the
    dataloader reads it (line[62], the integer digit of the B-factor field), so a
    residue is in the pocket here if and only if it is in the pocket there.
    """
    coordinates = []
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
            if line[13:17].strip() in BACKBONE_ATOMS:
                continue
            if int(line[62]) <= 0:
                continue
            pocket_residues.add(residue)
            coordinates.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return np.array(coordinates, dtype=float), pocket_residues, all_residues


def shape_from_coordinates(coordinates):
    """Extent, elongation and flatness of a point cloud, in angstroms and ratios.

    The three principal axes come from the covariance of the atom coordinates. What is
    reported along each axis is the 5th-to-95th percentile span of the projections
    rather than min-to-max: one stray atom at the rim would otherwise set the length of
    the cavity. Ratios are taken between axis LENGTHS (the square roots of the
    eigenvalues), so "twice as long" reads as 2 and not as 4.
    """
    if len(coordinates) < 4:
        return None
    centered = coordinates - coordinates.mean(axis=0)
    eigenvalues, eigenvectors = np.linalg.eigh(np.cov(centered, rowvar=False))
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order], 1e-9, None)
    eigenvectors = eigenvectors[:, order]
    spans = []
    for axis in range(3):
        projection = centered @ eigenvectors[:, axis]
        spans.append(float(np.percentile(projection, 95) - np.percentile(projection, 5)))
    lengths = np.sqrt(eigenvalues)
    return {
        # The most literal analogue of an acyl chain's length: how far the cavity runs.
        "pocket_extent": spans[0],
        "pocket_width": spans[1],
        "pocket_thickness": spans[2],
        # Tube vs bowl vs slab.
        "pocket_elongation": float(lengths[0] / lengths[1]),
        "pocket_flatness": float(lengths[1] / lengths[2]),
        # Overall spread, for scale where scale is wanted explicitly rather than smuggled.
        "pocket_gyration": float(np.sqrt(eigenvalues.sum())),
    }


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

    shape = shape_from_coordinates(coordinates)
    if shape is None:
        return None
    row.update(shape)

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
    hydropathy = KYTE_DOOLITTLE[site["residue_type"].to_numpy(dtype=int)]
    aromatic = np.isin(site["residue_type"].to_numpy(dtype=int), list(AROMATIC_CODES))
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


# The printed table is grouped the way files/pocket_shape_descriptors.md section 3
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
