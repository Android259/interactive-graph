#!/usr/bin/env python3
"""Compute and report pocket shape and chemistry descriptors.

Read pocketness.pdb and coarse_graph_nodes.csv under data/graphs/<protein>/.
Use flagged side-chain atoms for geometry and pocket residues for summary statistics.
Shared geometry functions come from preprocessing.compute_descriptors.
See files/reference/pocket_shape_descriptors.md for descriptor definitions.

Print grouped tables by default. --full prints one table; --out writes all columns
at full precision. Other modules import read_pocket_atoms() and descriptors_for().

    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py
    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py --full
    scripts/env.sh python3 preprocessing/pocket_shape_descriptors.py --out pocket_shape.csv
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

# Convert shared hydropathy values to an array for residue_type indexing.
_KYTE_DOOLITTLE = np.asarray(KYTE_DOOLITTLE)


def read_pocket_atoms(pocketness_pdb):
    """Return pocket side-chain coordinates, pocket residue keys and all residue keys.

    Use pocket_atom_coordinates() for coordinates. Read residue keys and pocket flags
    from PDB records to mask coarse_graph_nodes.csv.
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

    # Build the node mask from PDB residue keys.
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
    # Pocket residue volume divided by solvent-accessible surface area.
    row["pocket_volume_per_sasa"] = volume / max(sasa, 1e-9)

    # Report quantiles of the pocket residue distributions.
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

    # Report core/rim chemistry separately, split at median burial.
    hydropathy = _KYTE_DOOLITTLE[site["residue_type"].to_numpy(dtype=int)]
    aromatic = np.isin(site["residue_type"].to_numpy(dtype=int), AROMATIC_RESIDUE_TYPES)
    if "residue_mean_buriedness" in site:
        burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
        core = burial >= np.median(burial)
        row["hydropathy_core"] = float(hydropathy[core].mean())
        row["hydropathy_rim"] = float(hydropathy[~core].mean()) if (~core).any() else float("nan")
        row["aromatic_share_core"] = float(aromatic[core].mean())
        row["aromatic_share_rim"] = float(aromatic[~core].mean()) if (~core).any() else float("nan")
    # Report aromatic residue share separately from mean hydropathy.
    row["aromatic_share"] = float(aromatic.mean())
    row["hydropathy_mean"] = float(hydropathy.mean())
    return row


# Group console columns by descriptor type; keep the CSV as one table.
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

# Show units for lengths; ratios and shares are dimensionless.
UNITS = {name: "A" for name in (
    "pocket_extent", "pocket_width", "pocket_thickness", "pocket_gyration",
)}


def saturated_columns(table, tolerance=0.9):
    """Return columns whose most frequent finite value has a share of at least tolerance."""
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
        # Format values before adding the median row so integer counts keep integer formatting.
        block = pd.DataFrame(index=list(table.index) + ["-- median --"])
        for name in present:
            values = table[name]
            whole = bool(values.dropna().apply(lambda v: float(v).is_integer()).all())
            column = pd.concat([values, pd.Series({"-- median --": values.median()})])
            block[
                # Mark near-constant columns in the printed table.
                f"{name}{' [A]' if name in UNITS else ''}{' !flat' if name in flat else ''}"
            ] = column.map(lambda v: "" if pd.isna(v) else (f"{v:.0f}" if whole else f"{v:.3f}"))
        print(f"\n{title}")
        print(block.to_string())

    # Print any columns not assigned to a group.
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
