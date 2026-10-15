#!/usr/bin/env python3
"""Compute protein, lipid and pair descriptors.

Tables:
    data/protein_descriptors.csv: one row per protein
    data/lipid_descriptors.csv: one row per canonical candidate SMILES and isomeric mode
    data/pair_descriptors.csv: one row per candidate-protein pair

Protein inputs come from data/graphs/<protein>/. Lipid inputs come from the
interaction table. Pair descriptors combine the two descriptor tables.
The dataloader and cache builders also call the functions in this module.

The CLI updates one lipid or pair column and preserves other columns and modes.
A protein request rebuilds the protein table because its descriptors share one pass.

    python3 preprocessing/compute_descriptors.py --list
    python3 preprocessing/compute_descriptors.py tpsa
    python3 preprocessing/compute_descriptors.py tpsa --isomeric
    python3 preprocessing/compute_descriptors.py pocket_extent --force
    python3 preprocessing/compute_descriptors.py volume_fit
"""

import argparse
import functools
import json
import os
import sys
from pathlib import Path

import numpy
import pandas
import torch
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.descriptors import (  # noqa: E402
    PAIR_DESCRIPTOR_NAMES,
    POCKET_CHEMISTRY_DESCRIPTOR_NAMES,
    PROTEIN_DERIVED_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
)

# Keep the descriptor-name order used by the graph builder.
POCKET_DESCRIPTOR_NAMES = PROTEIN_DESCRIPTOR_NAMES


# ----------------------------------------------------------------------------------
# Protein side: residue tables, cavity geometry, pocket chemistry.
# ----------------------------------------------------------------------------------

# Kyte & Doolittle (1982) hydropathy, indexed by Voronota residue_type.
# Codes follow three-letter residue-name order:
# ALA=0 ARG=1 ASN=2 ASP=3 CYS=4 GLN=5 GLU=6 GLY=7 HIS=8 ILE=9
# LEU=10 LYS=11 MET=12 PHE=13 PRO=14 SER=15 THR=16 TRP=17 TYR=18 VAL=19
KYTE_DOOLITTLE = (
    1.8, -4.5, -3.5, -3.5, 2.5, -3.5, -3.5, -0.4, -3.2, 4.5,
    3.8, -3.9, 1.9, 2.8, -1.6, -0.8, -0.7, -0.9, -1.3, 4.2,
)
AROMATIC_RESIDUE_TYPES = (13, 17, 18)

# One-letter residue names in the same residue_type order.
RESIDUE_LETTERS = (
    "A", "R", "N", "D", "C", "Q", "E", "G", "H", "I",
    "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V",
)
# Residue-class membership as residue_type codes for NumPy masks.
_RESIDUE_CLASS_TYPES = {
    "basic": tuple(RESIDUE_LETTERS.index(letter) for letter in ("R", "K", "H")),
    "acidic": tuple(RESIDUE_LETTERS.index(letter) for letter in ("D", "E")),
    "polar": tuple(
        RESIDUE_LETTERS.index(letter) for letter in ("N", "Q", "S", "T", "Y", "C")
    ),
    "hbond_donor": tuple(
        RESIDUE_LETTERS.index(letter)
        for letter in ("R", "K", "H", "N", "Q", "S", "T", "Y", "W", "C")
    ),
    "hbond_acceptor": tuple(
        RESIDUE_LETTERS.index(letter)
        for letter in ("D", "E", "H", "N", "Q", "S", "T", "Y", "C")
    ),
}

# Bondi van der Waals radii in angstrom. Unknown elements use the carbon radius.
_VDW_RADII = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "H": 1.20}
# Exclude these atoms from the pocket side-chain mask.
POCKET_BACKBONE_ATOMS = ("C", "CA", "CB", "O", "N")
def pocket_atom_coordinates(pocketness_path):
    """Read coordinates of side-chain atoms flagged as pocket in pocketness.pdb."""
    coordinates = []
    with open(pocketness_path) as handle:
        for line in handle:
            if len(line) < 63 or not line.startswith(("ATOM", "HETATM")):
                continue
            if line[13:17].strip() in POCKET_BACKBONE_ATOMS:
                continue
            if int(line[62]) <= 0:
                continue
            coordinates.append(
                (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            )
    return numpy.array(coordinates, dtype=float)


def _pocket_axis_spans(coordinates):
    """Return principal-axis spans and covariance eigenvalues, or None below four atoms.

    Use covariance eigenvectors for directions. Measure each span between the 5th and
    95th percentiles of its projections. Keep eigenvalues for the gyration radius.
    """
    if len(coordinates) < 4:
        return None
    centered = coordinates - coordinates.mean(axis=0)
    eigenvalues, eigenvectors = numpy.linalg.eigh(numpy.cov(centered, rowvar=False))
    order = numpy.argsort(eigenvalues)[::-1]
    eigenvalues = numpy.clip(eigenvalues[order], 1e-9, None)
    eigenvectors = eigenvectors[:, order]
    spans = numpy.array([
        numpy.percentile(projection, 95) - numpy.percentile(projection, 5)
        for projection in (centered @ eigenvectors).T
    ])
    spans = numpy.clip(spans, 1e-9, None)
    return spans, eigenvalues


def pocket_shape(coordinates):
    """Return cavity extent and axis-span ratios. Return zeros below four atoms."""
    axes = _pocket_axis_spans(coordinates)
    if axes is None:
        return 0.0, 0.0, 0.0
    spans, _ = axes
    return float(spans[0]), float(spans[0] / spans[1]), float(spans[1] / spans[2])


def pocket_shape_full(coordinates):
    """Return extent, width, thickness, axis-span ratios and gyration radius.

    Use _pocket_axis_spans(). Gyration is sqrt(sum(eigenvalues)). Return zeros below
    four atoms.
    """
    axes = _pocket_axis_spans(coordinates)
    if axes is None:
        return {
            "pocket_extent": 0.0, "pocket_width": 0.0, "pocket_thickness": 0.0,
            "pocket_elongation": 0.0, "pocket_flatness": 0.0, "pocket_gyration": 0.0,
        }
    spans, eigenvalues = axes
    return {
        "pocket_extent": float(spans[0]),
        "pocket_width": float(spans[1]),
        "pocket_thickness": float(spans[2]),
        "pocket_elongation": float(spans[0] / spans[1]),
        "pocket_flatness": float(spans[1] / spans[2]),
        "pocket_gyration": float(numpy.sqrt(eigenvalues.sum())),
    }


def pocket_shape_lambda_sqrt(coordinates, min_robust_points=10):
    """Measure cavity shape from square roots of robust covariance eigenvalues.

    Use MinCovDet for directions and variances. Fall back to ordinary covariance for
    small or degenerate clouds. Return zeros below four atoms.
    See files/results/pocket_shape_metric_comparison.md for the method comparison.
    """
    if len(coordinates) < 4:
        return 0.0, 0.0, 0.0
    covariance = None
    if len(coordinates) >= min_robust_points:
        try:
            # Import sklearn only when robust shape is requested; cache results per protein.
            from sklearn.covariance import MinCovDet

            covariance = MinCovDet(random_state=0).fit(coordinates).covariance_
        except Exception:
            covariance = None
    if covariance is None:
        covariance = numpy.cov(coordinates - coordinates.mean(axis=0), rowvar=False)
    eigenvalues = numpy.clip(
        numpy.sort(numpy.linalg.eigvalsh(covariance))[::-1], 1e-9, None
    )
    lengths = numpy.sqrt(eigenvalues)
    return (
        float(lengths[0]),
        float(lengths[0] / lengths[1]),
        float(lengths[1] / lengths[2]),
    )


def pocket_descriptor(vertices, pocket, config=None, pocketness_path=None):
    """Return a [1, len(POCKET_DESCRIPTOR_NAMES)] tensor for one protein pocket.

    Aggregate the residue table over the pocket mask. Read atom coordinates from
    pocketness_path for shape descriptors; use zeros for shape if no PDB is supplied.
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket_descriptor requires at least one pocket residue")
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    hydropathy = numpy.asarray(KYTE_DOOLITTLE)[residue_types]
    aromatic = numpy.isin(residue_types, AROMATIC_RESIDUE_TYPES)
    sasa = site["residue_sas_area"].values
    pocket_sasa = float(sasa.sum())
    pocket_volume = float(site["residue_volume"].sum())
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    # Split core and rim at this pocket's median burial.
    core = burial >= numpy.median(burial)
    rim = ~core
    atom_coordinates = (
        pocket_atom_coordinates(pocketness_path)
        if pocketness_path is not None
        else numpy.empty((0, 3))
    )
    extent, elongation, flatness = pocket_shape(atom_coordinates)
    extent_lambda_sqrt, elongation_lambda_sqrt, flatness_lambda_sqrt = (
        pocket_shape_lambda_sqrt(atom_coordinates)
    )
    ev14 = site["residue_mean_ev14"].to_numpy(dtype=float)
    ev28 = site["residue_mean_ev28"].to_numpy(dtype=float)
    ev56 = site["residue_mean_ev56"].to_numpy(dtype=float)
    depth = site["residue_mean_voromqa_depth"].to_numpy(dtype=float)
    values = {
        "pocket_residue_share": len(site) / max(len(vertices), 1),
        "pocket_sasa_share": pocket_sasa / max(float(vertices["residue_sas_area"].sum()), 1e-9),
        "pocket_volume_per_sasa": pocket_volume / max(pocket_sasa, 1e-9),
        "pocket_extent": extent,
        "pocket_elongation": elongation,
        "pocket_flatness": flatness,
        "ev14_q50": float(numpy.median(ev14)),
        "buriedness_q50": float(numpy.median(burial)),
        "depth_q10": float(numpy.percentile(depth, 10)),
        "apolar_sasa_share": float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9)),
        "aromatic_share": float(aromatic.mean()),
        "hydropathy_core": float(hydropathy[core].mean()),
        "hydropathy_rim": (
            float(hydropathy[rim].mean()) if rim.any() else float(hydropathy.mean())
        ),
        "ev28_q10": float(numpy.percentile(ev28, 10)),
        "aromatic_share_rim": (
            float(aromatic[rim].mean()) if rim.any() else float(aromatic.mean())
        ),
        "hydropathy_mean": float(hydropathy.mean()),
        "ev14_q10": float(numpy.percentile(ev14, 10)),
        "pocket_extent_lambda_sqrt": extent_lambda_sqrt,
        "pocket_elongation_lambda_sqrt": elongation_lambda_sqrt,
        "pocket_flatness_lambda_sqrt": flatness_lambda_sqrt,
        "ev14_q90": float(numpy.percentile(ev14, 90)),
        "ev28_q50": float(numpy.median(ev28)),
        "ev28_q90": float(numpy.percentile(ev28, 90)),
        "ev56_q10": float(numpy.percentile(ev56, 10)),
        "ev56_q50": float(numpy.median(ev56)),
        "ev56_q90": float(numpy.percentile(ev56, 90)),
        "buriedness_q10": float(numpy.percentile(burial, 10)),
        "buriedness_q90": float(numpy.percentile(burial, 90)),
        "depth_q50": float(numpy.median(depth)),
        "depth_q90": float(numpy.percentile(depth, 90)),
        "aromatic_share_core": float(aromatic[core].mean()),
    }
    missing = [name for name in POCKET_DESCRIPTOR_NAMES if name not in values]
    if missing:
        raise ValueError(f"pocket descriptor not computed: {missing}")
    return values


def pocket_cavity_volume(pocketness_path):
    """Estimate pocket free volume (A^3) and free fraction.

    Build the pocket atom cloud's convex hull. Subtract van der Waals volumes of atoms
    whose centres lie inside it. Use the same formula as
    training.pair_baseline_common._cavity_values; importing it would create a cycle.
    """
    from scipy.spatial import ConvexHull, Delaunay

    pocket = pocket_atom_coordinates(pocketness_path)
    if len(pocket) < 4:
        return 0.0, 0.0
    hull = ConvexHull(pocket)
    triangulation = Delaunay(pocket)
    coordinates, elements = [], []
    with open(pocketness_path) as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")) or len(line) < 63:
                continue
            coordinates.append(
                (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            )
            elements.append((line[76:78].strip() or line[13:14]).upper())
    inside = triangulation.find_simplex(numpy.asarray(coordinates)) >= 0
    occupied = sum(
        4.0 / 3.0 * numpy.pi * _VDW_RADII.get(element, 1.70) ** 3
        for element, is_inside in zip(elements, inside) if is_inside
    )
    free = max(hull.volume - occupied, 0.0)
    return float(free), float(free / max(hull.volume, 1e-9))


def pocket_chemistry_descriptor(vertices, pocket, pocketness_path=None):
    """Return named pocket chemistry and cavity-volume descriptors.

    Compute residue-class shares for core and rim. Use the median burial for the split.
    The two cavity entries require pocketness_path; use zeros when it is absent.
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket_chemistry_descriptor requires at least one pocket residue")
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    # Use the same median-burial split and constant-burial fallback as pocket_descriptor().
    core = burial >= numpy.median(burial)
    rim = ~core
    if not rim.any():
        rim = numpy.ones(len(site), dtype=bool)
    values = {}
    for name, types in _RESIDUE_CLASS_TYPES.items():
        member = numpy.isin(residue_types, types)
        values[f"{name}_share_core"] = float(member[core].mean())
        values[f"{name}_share_rim"] = float(member[rim].mean())
    free_volume, packing = (
        pocket_cavity_volume(pocketness_path) if pocketness_path is not None else (0.0, 0.0)
    )
    values["pocket_free_volume"] = free_volume
    values["pocket_packing_density"] = packing
    return values
# Increment the format version when descriptor definitions or columns change.
_PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION = 6


def _protein_descriptors_csv_path(data_dir):
    return Path(data_dir) / "protein_descriptors.csv"


def _protein_descriptor_table_manifest_path(data_dir):
    return Path(data_dir) / "protein_descriptors.manifest.json"


def _protein_descriptor_table_sources(data_dir, protein_names):
    from dataloader.cache_builders.protein_graph_tensors_builder import _source_record

    root_dir = Path(data_dir).resolve()
    paths = []
    for protein in protein_names:
        protein_dir = root_dir / "graphs" / protein
        paths.append(protein_dir / "pocketness.pdb")
        paths.append(protein_dir / "coarse_graph_nodes.csv")
    return [_source_record(path, root_dir) for path in paths if path.exists()]


def protein_descriptor_table(data_dir, force=False):
    """Return {protein: {descriptor: value}} from protein graph files.

    Read coarse_graph_nodes.csv and pocketness.pdb. Reuse data/protein_descriptors.csv
    when its manifest matches the format version and source sizes/mtimes. Otherwise
    recompute and save the table. Include derived and pocket chemistry descriptors.
    """
    import pandas as pd

    from dataloader.tensors_reading.protein_graph_tensors_reader import _pocket_tensor

    graphs_dir = os.path.join(data_dir, "graphs")
    protein_names = sorted(
        protein for protein in os.listdir(graphs_dir)
        if os.path.isfile(os.path.join(graphs_dir, protein, "pocketness.pdb"))
        and os.path.isfile(os.path.join(graphs_dir, protein, "coarse_graph_nodes.csv"))
    )

    csv_path = _protein_descriptors_csv_path(data_dir)
    manifest_path = _protein_descriptor_table_manifest_path(data_dir)
    if csv_path.exists() and manifest_path.exists() and not force:
        try:
            manifest = json.loads(manifest_path.read_text())
            current_sources = _protein_descriptor_table_sources(data_dir, protein_names)
            if (
                manifest.get("format_version") == _PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION
                and manifest.get("sources") == current_sources
            ):
                # Use round_trip parsing to preserve the floats written by to_csv().
                table = pandas.read_csv(
                    csv_path, index_col="protein", float_precision="round_trip"
                )
                if sorted(table.index) == protein_names:
                    return {
                        protein: table.loc[protein].to_dict() for protein in table.index
                    }
        except (OSError, ValueError, pandas.errors.ParserError, KeyError):
            pass  # fall through and recompute, same as any other stale/corrupt cache

    values = {}
    for protein in protein_names:
        protein_dir = os.path.join(graphs_dir, protein)
        pocketness_path = os.path.join(protein_dir, "pocketness.pdb")
        nodes_path = os.path.join(protein_dir, "coarse_graph_nodes.csv")
        vertices = pd.read_csv(nodes_path)
        pocket = _pocket_tensor(Path(pocketness_path))
        raw = dict(
            pocket_descriptor(vertices, pocket, None, pocketness_path=pocketness_path)
        )
        # Add named chemistry descriptors outside the positional descriptor tensor.
        raw.update(pocket_chemistry_descriptor(vertices, pocket, pocketness_path))
        raw["polar_share"] = 1.0 - raw["apolar_sasa_share"]
        raw["aromatic_share_coarse"] = coarse_share(raw["aromatic_share"])
        raw["polar_share_coarse"] = coarse_share(raw["polar_share"])
        values[protein] = raw

    try:
        table = pd.DataFrame.from_dict(values, orient="index")
        table.index.name = "protein"
        table.to_csv(csv_path)
        manifest_path.write_text(json.dumps({
            "format_version": _PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION,
            "sources": _protein_descriptor_table_sources(data_dir, protein_names),
        }))
    except OSError:
        pass  # never fatal -- a read-only data/ (or a race with another process
              # writing the same file) still returns correct values, just unpersisted

    return values
_SHARE_BAND_EDGES = (1.0 / 3, 2.0 / 3)
_SHARE_BAND_CENTRES = (1.0 / 6, 0.5, 5.0 / 6)
def coarse_share(value):
    """Map a share to its fixed-width third centre; an edge value stays in the lower band."""
    band = sum(1 for edge in _SHARE_BAND_EDGES if value > edge)
    return _SHARE_BAND_CENTRES[band]


_MINIMUM_TAIL_CARBONS = 4
# Require at least four carbons to exclude short head-group branches from tail counts.


def _acyl_chain_component_lengths(smiles):
    """Return longest-path carbon counts for non-ring, non-aromatic carbon components.

    Return None for invalid SMILES and [] when no such component exists.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    carbons = [
        atom.GetIdx() for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic() and not atom.IsInRing()
    ]
    if not carbons:
        return []
    index = {atom: position for position, atom in enumerate(carbons)}
    neighbours = {position: [] for position in index.values()}
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a in index and b in index:
            neighbours[index[a]].append(index[b])
            neighbours[index[b]].append(index[a])

    # Find each component's longest path with two breadth-first searches.
    def farthest(start):
        seen = {start: 0}
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in neighbours[node]:
                if neighbour not in seen:
                    seen[neighbour] = seen[node] + 1
                    queue.append(neighbour)
        end = max(seen, key=seen.get)
        return end, seen[end], set(seen)

    lengths = []
    unvisited = set(neighbours)
    while unvisited:
        start = next(iter(unvisited))
        end, _, component = farthest(start)
        _, distance, _ = farthest(end)
        lengths.append(distance + 1)
        unvisited -= component
    return lengths


def _acyl_chain_components(smiles):
    """Describe non-ring, non-aromatic carbon components along their longest paths.

    Return entries with carbons, atoms, double_bonds and position_from_end.
    position_from_end counts from the methyl endpoint to the nearest double bond.
    Choose the endpoint without an outside neighbour; break ties by lower atom index.
    Return None for invalid SMILES, [] for no components, and a None position for
    saturated tails. See Liebisch et al., J Lipid Res 2020 for the (n-x) notation.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    carbons = [
        atom.GetIdx() for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic() and not atom.IsInRing()
    ]
    if not carbons:
        return []
    carbon_set = set(carbons)
    neighbours = {atom: [] for atom in carbons}
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a in carbon_set and b in carbon_set:
            neighbours[a].append(b)
            neighbours[b].append(a)

    def breadth_first(start):
        parent = {start: None}
        order = [start]
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in neighbours[node]:
                if neighbour not in parent:
                    parent[neighbour] = node
                    order.append(neighbour)
                    queue.append(neighbour)
        return parent, order

    def longest_path(start):
        parent, order = breadth_first(start)
        end = order[-1]
        parent, order = breadth_first(end)
        far = order[-1]
        path = [far]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        return path, set(parent)

    def attached_outside(atom):
        """True when this carbon bonds to anything that is not a component carbon --
        an ester oxygen, an amide nitrogen. The chain's own methyl end does not."""
        return any(
            neighbour.GetIdx() not in carbon_set
            for neighbour in mol.GetAtomWithIdx(atom).GetNeighbors()
        )

    components = []
    unvisited = set(neighbours)
    while unvisited:
        path, seen = longest_path(next(iter(unvisited)))
        unvisited -= seen
        # Orient the path so index 0 is the methyl end.
        head_attached, tail_attached = attached_outside(path[0]), attached_outside(path[-1])
        if head_attached and not tail_attached:
            path = list(reversed(path))
        elif head_attached == tail_attached and path[-1] < path[0]:
            path = list(reversed(path))
        double_bonds = 0
        position_from_end = None
        for step, (a, b) in enumerate(zip(path, path[1:])):
            bond = mol.GetBondBetweenAtoms(a, b)
            if bond is not None and bond.GetBondType() == Chem.BondType.DOUBLE:
                double_bonds += 1
                if position_from_end is None:
                    position_from_end = step + 1
        components.append({
            "carbons": len(path),
            "atoms": path,
            "double_bonds": double_bonds,
            "position_from_end": position_from_end,
        })
    return components


def _qualifying_tails(smiles):
    """Keep components with at least _MINIMUM_TAIL_CARBONS; preserve None for invalid SMILES."""
    components = _acyl_chain_components(smiles)
    if not components:
        return components
    return [c for c in components if c["carbons"] >= _MINIMUM_TAIL_CARBONS]


def tail_length_asymmetry(smiles):
    """Return longest minus shortest tail length in carbons; zero for a single tail."""
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    lengths = [tail["carbons"] for tail in tails]
    return float(max(lengths) - min(lengths))


def tail_length_mean(smiles):
    """Mean tail length in carbons -- `chain` reports the longest one only."""
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    return float(sum(tail["carbons"] for tail in tails) / len(tails))


def tail_double_bonds(smiles):
    """Count double bonds in qualifying tails."""
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    return float(sum(tail["double_bonds"] for tail in tails))


def tail_unsaturation_density(smiles):
    """Return tail double-bond count divided by tail carbon count."""
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    carbons = sum(tail["carbons"] for tail in tails)
    if carbons == 0:
        return None
    return float(sum(tail["double_bonds"] for tail in tails) / carbons)


def tail_double_bond_position(smiles):
    """Return the nearest double-bond position from a methyl end, or None for saturated tails."""
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    positions = [
        tail["position_from_end"] for tail in tails
        if tail["position_from_end"] is not None
    ]
    if not positions:
        return None
    return float(min(positions))


def _tail_fragment(smiles):
    """Return qualifying carbon tails as one molecule, or None when none remain."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    atoms = sorted({atom for tail in tails for atom in tail["atoms"]})
    if not atoms:
        return None
    fragment_smiles = Chem.MolFragmentToSmiles(mol, atomsToUse=atoms, canonical=True)
    return Chem.MolFromSmiles(fragment_smiles)


def tail_logp(smiles):
    """Crippen logP of the tails alone -- `logp`'s head-blind counterpart."""
    fragment = _tail_fragment(smiles)
    return None if fragment is None else float(Descriptors.MolLogP(fragment))


def tail_molar_refractivity(smiles):
    """Molar refractivity of the tails alone -- `molar_refractivity`'s counterpart."""
    fragment = _tail_fragment(smiles)
    return None if fragment is None else float(Descriptors.MolMR(fragment))


def tail_heavy_atoms(smiles):
    """Heavy atoms in the tails alone -- `heavy`'s counterpart."""
    fragment = _tail_fragment(smiles)
    return None if fragment is None else float(fragment.GetNumHeavyAtoms())


def longest_acyl_chain(smiles):
    """Return the longest non-ring, non-aromatic carbon path, or None for invalid/empty input."""
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:  # None (unparseable) or [] (no qualifying carbon) alike
        return None
    return max(lengths)


def acyl_chain_count(smiles):
    """Count components with at least _MINIMUM_TAIL_CARBONS; return None for invalid/empty input."""
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:
        return None
    return float(sum(1 for length in lengths if length >= _MINIMUM_TAIL_CARBONS))


def unsaturation_count(smiles):
    """Non-aromatic C=C double bonds in one molecule, or None if RDKit cannot parse it."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(sum(
        1 for bond in mol.GetBonds()
        if bond.GetBondTypeAsDouble() == 2.0
        and not bond.GetIsAromatic()
        and bond.GetBeginAtom().GetSymbol() == "C"
        and bond.GetEndAtom().GetSymbol() == "C"
    ))


def hbond_capacity(smiles):
    """RDKit H-bond donor + acceptor count -- a headgroup polarity proxy, not a pose."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.NumHDonors(mol) + Descriptors.NumHAcceptors(mol))


def heavy_atom_count(smiles):
    """Heavy-atom count -- a cheap, robust size proxy standing in for ligand volume."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(mol.GetNumHeavyAtoms())


# Whole-molecule topological RDKit measures. Return None for invalid SMILES.
def logp(smiles):
    """RDKit Crippen logP -- octanol/water partition coefficient."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.MolLogP(mol))


def tpsa(smiles):
    """Topological polar surface area (Angstrom^2)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.TPSA(mol))


def molar_refractivity(smiles):
    """RDKit molar refractivity."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.MolMR(mol))


def rotatable_bond_count(smiles):
    """Absolute rotatable-bond count."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumRotatableBonds(mol))


def aromatic_ring_count(smiles):
    """Aromatic ring count."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumAromaticRings(mol))


def ring_count(smiles):
    """Total ring count (aromatic + aliphatic)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumRings(mol))


# Generate a shared ETKDG/MMFF ensemble for the optional 3D shape measures.
CONFORMER_COUNT = 10
CONFORMER_SEED = 0xF00D


def generate_conformer_ensemble(mol, n_confs=CONFORMER_COUNT, seed=CONFORMER_SEED):
    """Return an explicit-H molecule and conformer IDs from ETKDG and MMFF.

    Keep the original heavy-atom indices. Retry embedding with random coordinates.
    Raise ValueError if embedding still fails.
    """
    mol_h = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    conf_ids = list(AllChem.EmbedMultipleConfs(mol_h, numConfs=n_confs, params=params))
    if not conf_ids:
        params.useRandomCoords = True
        conf_ids = list(
            AllChem.EmbedMultipleConfs(mol_h, numConfs=n_confs, params=params)
        )
    if not conf_ids:
        raise ValueError(
            f"ETKDG conformer embedding failed for {Chem.MolToSmiles(mol)}"
        )
    try:
        AllChem.MMFFOptimizeMoleculeConfs(mol_h, maxIters=500)
    except Exception:
        pass  # MMFF parameters missing for some atom types -- keep raw ETKDG geometry
    return mol_h, conf_ids


@functools.lru_cache(maxsize=4096)
def _cached_conformer_ensemble(smiles):
    """Cache conformers by canonical SMILES for reuse across shape measures.

    Return None for invalid SMILES. Use the fixed CONFORMER_SEED.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return generate_conformer_ensemble(mol)


def _mean_over_conformers(smiles, per_conformer_fn):
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(sum(values) / len(values))


def radius_of_gyration(smiles):
    """Ensemble-mean radius of gyration (Angstrom) -- overall size/compactness."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: rdMolDescriptors.CalcRadiusOfGyration(
            mol_h, confId=conf_id
        ),
    )


def asphericity(smiles):
    """Ensemble-mean asphericity (unitless, 0=spherical) -- elongated vs globular."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: rdMolDescriptors.CalcAsphericity(mol_h, confId=conf_id),
    )


def molecular_volume(smiles):
    """Ensemble-mean van-der-Waals volume (Angstrom^3) -- real size, not a heavy-atom proxy."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: AllChem.ComputeMolVolume(mol_h, confId=conf_id),
    )


def rotatable_fraction(smiles):
    """Rotatable bonds / total bonds -- conformational flexibility, purely topological
    (does not need a conformer, unlike the three functions above)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    total_bonds = mol.GetNumBonds()
    if total_bonds == 0:
        return 0.0
    return float(rdMolDescriptors.CalcNumRotatableBonds(mol)) / total_bonds


def _median_over_conformers(smiles, per_conformer_fn):
    """Return the median measure over the cached conformer ensemble."""
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(numpy.median(values))


def npr1(smiles):
    """Return median PMI1/PMI3 over the conformer ensemble (Sauer & Schwarz, 2003)."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR1(mol_h, confId=conf_id)
    )


def npr2(smiles):
    """Return median PMI2/PMI3 over the conformer ensemble."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR2(mol_h, confId=conf_id)
    )


LIPID_SHAPE_DESCRIPTOR_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "rotatable_fraction",
    "npr1", "npr2",
)

# These measures share a cached conformer ensemble and use the parallel build path.
CONFORMER_MEASURE_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "npr1", "npr2",
)


# Measured volumes (Angstrom^3), looked up by canonical SMILES in data/Lipid_Volumes.csv.
_LIPID_VOLUME_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "Lipid_Volumes.csv",
)


@functools.lru_cache(maxsize=1)
def _experimental_lipid_volume_table():
    """Canonical SMILES (isomeric or not) -> mean measured volume (Angstrom^3)."""
    import pandas

    frame = pandas.read_csv(_LIPID_VOLUME_CSV)
    volume_column = next(c for c in frame.columns if c.startswith("Lipid Volumes"))
    iso_groups = {}
    flat_groups = {}
    for raw_smiles, volume in zip(frame["Lipid SMILES"], frame[volume_column]):
        molecule = Chem.MolFromSmiles(str(raw_smiles))
        if molecule is None:
            continue
        iso_key = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)
        flat_key = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=False)
        iso_groups.setdefault(iso_key, []).append(float(volume))
        flat_groups.setdefault(flat_key, []).append(float(volume))
    # Insert flat keys first, then let exact isomeric keys take precedence.
    table = {key: sum(values) / len(values) for key, values in flat_groups.items()}
    table.update({key: sum(values) / len(values) for key, values in iso_groups.items()})
    return table


def experimental_lipid_volume(smiles):
    """Look up canonical SMILES in data/Lipid_Volumes.csv; return None for missing keys."""
    return _experimental_lipid_volume_table().get(smiles)


_MEASURES = {
    "unsaturation": unsaturation_count,
    "hbond": hbond_capacity,
    "heavy_atoms": heavy_atom_count,
    "tail_count": acyl_chain_count,
    "radius_of_gyration": radius_of_gyration,
    "asphericity": asphericity,
    "molecular_volume": molecular_volume,
    "rotatable_fraction": rotatable_fraction,
    "npr1": npr1,
    "npr2": npr2,
    "logp": logp,
    "tpsa": tpsa,
    "molar_refractivity": molar_refractivity,
    "rotatable_bond_count": rotatable_bond_count,
    "aromatic_ring_count": aromatic_ring_count,
    "ring_count": ring_count,
    # Candidate measures are registered separately from LIPID_DESCRIPTOR_NAMES.
    "tail_length_asymmetry": tail_length_asymmetry,
    "tail_length_mean": tail_length_mean,
    "tail_double_bonds": tail_double_bonds,
    "tail_unsaturation_density": tail_unsaturation_density,
    "tail_double_bond_position": tail_double_bond_position,
    "tail_logp": tail_logp,
    "tail_molar_refractivity": tail_molar_refractivity,
    "tail_heavy_atoms": tail_heavy_atoms,
    # Look up the measured volume; do not compute it with RDKit.
    "experimental_lipid_volume": experimental_lipid_volume,
}

# Expose candidate names to analysis without adding them to LIPID_DESCRIPTOR_NAMES.
CANDIDATE_LIPID_DESCRIPTOR_NAMES = (
    "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
    "tail_unsaturation_density", "tail_double_bond_position",
    "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
)


def descriptor_values_by_row(csv, measure, isomeric=False, cache=None):
    """Return per-candidate values in the encoder's candidate order.

    Use None for unavailable values and [None] for a row without usable candidates.
    Match isomeric mode to chain_lengths_by_row so candidate lists have equal lengths.
    Use cached canonical keys and values when available; compute missing entries.
    """
    from dataloader.pocket_lipid_compatibility import candidate_fields_by_row

    fn = _MEASURES[measure]
    raw_to_canonical = cache["raw_to_canonical"] if cache else {}
    cached_values = cache["values"] if cache else {}
    by_field = {}
    by_smiles = {}
    per_row = []
    for field in candidate_fields_by_row(csv):
        values = by_field.get(field)
        if values is None:
            values = []
            seen = set()
            for raw in field:
                if raw in raw_to_canonical:
                    key = raw_to_canonical[raw]
                    if key is None:
                        continue
                else:
                    molecule = Chem.MolFromSmiles(raw)
                    if molecule is None or molecule.GetNumAtoms() == 0:
                        continue
                    key = Chem.MolToSmiles(
                        molecule, canonical=True, isomericSmiles=isomeric
                    )
                if key in seen:
                    continue
                seen.add(key)
                if key not in by_smiles:
                    cached = cached_values.get(key)
                    # Check cache membership before calling fn; dict.get would evaluate fn even on a hit.
                    if cached is not None and measure in cached:
                        by_smiles[key] = cached[measure]
                    else:
                        by_smiles[key] = fn(key)
                values.append(by_smiles[key])
            values = values or [None]
            by_field[field] = values
        per_row.append(values)
    return per_row


def as_arrays(per_row):
    """Convert per-row candidate values to NumPy arrays, replacing None with NaN."""
    return [
        numpy.array(
            [numpy.nan if value is None else float(value) for value in row],
            dtype=float,
        )
        for row in per_row
    ]


# Tanford, The Hydrophobic Effect (1980): extended hydrocarbon-chain length.
# L = 1.5 + 1.265 * (n - 1) angstrom for n carbons.
# Convert carbon counts before comparing them with pocket lengths.
_CHAIN_BOND_PROJECTION_A = 1.265
_CHAIN_TERMINAL_A = 1.5


def chain_length_angstrom(chain):
    """Estimate extended-chain length in angstrom from carbon count using Tanford's formula."""
    return _CHAIN_TERMINAL_A + _CHAIN_BOND_PROJECTION_A * (chain - 1.0)


def pair_descriptor_value(name, lipid_values, protein_values):
    """Combine lipid and protein descriptor dictionaries into one pair descriptor.

    Formulas:
        occupancy: max(chain_length_angstrom(chain) - pocket_extent, 0)
        chain_extent_gap: pocket_extent - chain_length_angstrom(chain)
        aromatic_contact: aromatic_share * unsaturation
        hbond_match: polar_share * hbond
        volume_fit: pocket_volume_per_sasa * heavy
        buriedness_match: buriedness_q50 * heavy
        depth_bulk_match: depth_q10 * heavy
        hydropathy_chain_match: hydropathy_core * chain
        aromatic_contact_min: min(aromatic_share, unsaturation)
        hbond_match_min: min(polar_share, hbond)
        tail_elongation_fit: tail_count / max(pocket_elongation, 1)
        hydropathy_rim_match: hydropathy_rim * hbond
        elongation_shape_match: pocket_elongation * npr1
        flatness_shape_match: pocket_flatness * npr2

    The two minimum formulas require standardised inputs from the caller. Length gaps
    use angstroms. Products combine summary features without a bound ligand pose.
    """
    if name == "occupancy":
        return max(
            0.0,
            chain_length_angstrom(lipid_values["chain"]) - protein_values["pocket_extent"],
        )
    if name == "chain_extent_gap":
        return protein_values["pocket_extent"] - chain_length_angstrom(lipid_values["chain"])
    if name == "aromatic_contact":
        return protein_values["aromatic_share"] * lipid_values["unsaturation"]
    if name == "hbond_match":
        return protein_values["polar_share"] * lipid_values["hbond"]
    if name == "volume_fit":
        return protein_values["pocket_volume_per_sasa"] * lipid_values["heavy"]
    if name == "buriedness_match":
        return protein_values["buriedness_q50"] * lipid_values["heavy"]
    if name == "depth_bulk_match":
        return protein_values["depth_q10"] * lipid_values["heavy"]
    if name == "hydropathy_chain_match":
        return protein_values["hydropathy_core"] * lipid_values["chain"]
    if name == "aromatic_contact_min":
        return min(protein_values["aromatic_share"], lipid_values["unsaturation"])
    if name == "hbond_match_min":
        return min(protein_values["polar_share"], lipid_values["hbond"])
    if name == "tail_elongation_fit":
        return lipid_values["tail_count"] / max(protein_values["pocket_elongation"], 1.0)
    if name == "hydropathy_rim_match":
        return protein_values["hydropathy_rim"] * lipid_values["hbond"]
    if name == "elongation_shape_match":
        return protein_values["pocket_elongation"] * lipid_values["npr1"]
    if name == "flatness_shape_match":
        return protein_values["pocket_flatness"] * lipid_values["npr2"]
    raise ValueError(f"Unknown pair descriptor: {name}. Known: {PAIR_DESCRIPTOR_NAMES}")


# ----------------------------------------------------------------------------------
# Which table a name belongs to, and the CLI that writes one name's column into it.
# ----------------------------------------------------------------------------------

PROTEIN_SIDE_NAMES = tuple(
    PROTEIN_DESCRIPTOR_NAMES
    + PROTEIN_DERIVED_DESCRIPTOR_NAMES
    + POCKET_CHEMISTRY_DESCRIPTOR_NAMES
)
# The chain column uses longest_acyl_chain, which is not registered in _MEASURES.
LIPID_SIDE_NAMES = ("chain",) + tuple(_MEASURES)


def descriptor_side(name):
    """"protein" / "lipid" / "pair" for `name`, or None when no table defines it."""
    if name in PROTEIN_SIDE_NAMES:
        return "protein"
    if name in LIPID_SIDE_NAMES:
        return "lipid"
    if name in PAIR_DESCRIPTOR_NAMES:
        return "pair"
    return None


def lipid_measure_function(name):
    """The callable behind one lipid name, "chain" included."""
    return longest_acyl_chain if name == "chain" else _MEASURES[name]


def _write_column(table_path, new_values, name, key_columns, isomeric):
    """Update one descriptor column for one isomeric mode.

    Match new_values by key_columns. Preserve other columns and the other mode's rows.
    """
    table = pandas.read_csv(table_path, float_precision="round_trip")
    mask = table["isomeric"] == bool(isomeric)
    if name not in table.columns:
        table[name] = numpy.nan
    keys = list(zip(*(table[column] for column in key_columns)))
    updated = [
        new_values.get(key) if is_this_variant else current
        for key, is_this_variant, current in zip(keys, mask, table[name])
    ]
    table[name] = updated
    table.to_csv(table_path, index=False)
    return int(mask.sum())


def compute_lipid_descriptor(data_dir, name, isomeric=False):
    """Update one lipid descriptor column for interaction-table candidates.

    Require an existing data/lipid_descriptors.csv. Use the descriptor cache builder
    for the initial table.
    """
    from dataloader.dataset_source import interaction_csv_path
    from dataloader.descriptor_cache_reader import lipid_descriptors_csv_path

    table_path = lipid_descriptors_csv_path(data_dir)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            "`python3 data/build_descriptor_cache.py` before writing one column"
        )

    csv = pandas.read_csv(interaction_csv_path(str(data_dir) + os.sep))
    function = lipid_measure_function(name)
    values = {}
    for key in _canonical_candidate_keys(csv, isomeric):
        values[(key, bool(isomeric))] = function(key)

    written = _write_column(
        table_path, values, name, ("smiles", "isomeric"), isomeric
    )
    # A column update does not change source provenance or raw_to_canonical.
    return table_path, written


def _canonical_candidate_keys(csv, isomeric):
    """Return distinct canonical candidate SMILES in input order, skipping invalid entries."""
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    keys = []
    seen = set()
    for _, row in csv.iterrows():
        for raw in candidates_for_row(row):
            molecule = Chem.MolFromSmiles(raw)
            if molecule is None or molecule.GetNumAtoms() == 0:
                continue
            key = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=isomeric)
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def compute_pair_descriptor(data_dir, name, isomeric=False):
    """Compute one pair column from the cached lipid and protein descriptor tables."""
    from dataloader.descriptor_cache_reader import (
        load_lipid_descriptor_cache,
        pair_descriptors_csv_path,
    )

    table_path = pair_descriptors_csv_path(data_dir)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            "`dataloader.cache_builders.descriptor_csv_builder.build_pair_value_cache` "
            "before writing one column"
        )
    lipid_cache = load_lipid_descriptor_cache(Path(data_dir).resolve(), isomeric)
    if lipid_cache is None:
        raise SystemExit(
            "data/lipid_descriptors.csv is missing or stale -- this reads lipid values "
            "from it rather than recomputing them"
        )
    lipid_values = lipid_cache["values"]
    protein_table = protein_descriptor_table(str(data_dir))

    table = pandas.read_csv(table_path, float_precision="round_trip")
    values = {}
    for smiles, protein, variant in zip(
        table["smiles"], table["protein"], table["isomeric"]
    ):
        if bool(variant) != bool(isomeric):
            continue
        lv = lipid_values.get(smiles)
        pv = protein_table.get(protein)
        if lv is None or pv is None:
            continue
        lipid_input = {
            "chain": lv["chain"],
            "unsaturation": lv["unsaturation"],
            "hbond": lv["hbond"],
            "heavy": lv["heavy_atoms"],
            "tail_count": lv["tail_count"],
            "npr1": lv["npr1"],
            "npr2": lv["npr2"],
        }
        values[(smiles, protein, bool(isomeric))] = pair_descriptor_value(
            name, lipid_input, pv
        )

    written = _write_column(
        table_path, values, name, ("smiles", "protein", "isomeric"), isomeric
    )
    return table_path, written


def _print_catalog():
    for side, names in (
        ("protein", PROTEIN_SIDE_NAMES),
        ("lipid", LIPID_SIDE_NAMES),
        ("pair", PAIR_DESCRIPTOR_NAMES),
    ):
        print(f"\n{side} ({len(names)}):")
        for name in sorted(names):
            print(f"  {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "descriptor",
        nargs="?",
        help="the one descriptor name to compute; its side decides which table is written",
    )
    parser.add_argument("--list", action="store_true", help="print every known name by side")
    parser.add_argument(
        "--isomeric",
        action="store_true",
        help="the isomeric-SMILES half of the lipid/pair tables (--lipid_isomers runs)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="protein side only: recompute even when the cached table is current",
    )
    parser.add_argument("--data_dir", default=str(PROJECT_ROOT / "data"))
    arguments = parser.parse_args(argv)

    if arguments.list:
        _print_catalog()
        return 0
    if not arguments.descriptor:
        parser.error("descriptor NAME is required (or --list)")

    name = arguments.descriptor
    side = descriptor_side(name)
    if side is None:
        raise SystemExit(
            f"Unknown descriptor: {name}. Run --list for every name this project computes."
        )

    if side == "protein":
        # Protein descriptors share one pass, so rebuild the table for a protein-name request.
        table = protein_descriptor_table(arguments.data_dir, force=arguments.force)
        print(
            f"{name}: protein side, {len(table)} proteins -> "
            f"{_protein_descriptors_csv_path(arguments.data_dir)}"
        )
        return 0

    if side == "lipid":
        path, written = compute_lipid_descriptor(
            arguments.data_dir, name, isomeric=arguments.isomeric
        )
        variant = "isomeric" if arguments.isomeric else "deterministic"
        print(f"{name}: lipid side, {written} {variant} rows -> {path}")
        return 0

    path, written = compute_pair_descriptor(
        arguments.data_dir, name, isomeric=arguments.isomeric
    )
    variant = "isomeric" if arguments.isomeric else "deterministic"
    print(f"{name}: pair side, {written} {variant} rows -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
