#!/usr/bin/env python3
"""Compute protein, lipid and pair descriptors.

Tables:
    data/protein_descriptors.csv: one row per protein
    data/lipid_descriptors.csv: one row per canonical candidate SMILES and isomeric mode
    data/pair_descriptors.csv: one row per candidate-protein pair

Protein inputs come from data/graphs/<protein>/. Lipid inputs come from the
interaction table. Pair descriptors combine the two descriptor tables.
The dataloader and cache builders also call the functions in this module.

HOW TO ADD A DESCRIPTOR : name it in dataloader/descriptors.py, write a function of that
same name in this file's matching section below, and register it. Nothing to run --
the table fills the new column on its own.

    protein : PROTEIN_DESCRIPTOR_NAMES; (vertices, pocket, pocketness_path=None);
              _PROTEIN_MEASURES
    lipid   : LIPID_DESCRIPTOR_NAMES; (smiles); _LIPID_MEASURES
    pair    : PAIR_DESCRIPTOR_NAMES; @_pair_measure(kind) on (lipid, protein) --
              a value no formula read before also goes in PAIR_DESCRIPTOR_LIPID_INPUTS,
              or gbm_baseline.PAIR_DESCRIPTOR_PROTEIN_INPUTS on the protein side

tests/test_descriptor_catalog.py fails on a name with no function, or the reverse.

The CLI updates one column of one table -- protein, lipid or pair alike -- and
preserves the other columns and modes. --force rebuilds that side's whole table
instead, which is also how each table is first built.

    python3 preprocessing/compute_descriptors.py --list
    python3 preprocessing/compute_descriptors.py tpsa
    python3 preprocessing/compute_descriptors.py tpsa --isomeric
    python3 preprocessing/compute_descriptors.py pocket_extent
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
    PROTEIN_DESCRIPTOR_NAMES,
)

######################################################################################
# PROTEIN DESCRIPTORS
# one row per protein in data/protein_descriptors.csv
######################################################################################


# ----------------------------------------------------------------------------------
# helpers: residue tables, pocket geometry, shared per-pocket quantities
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


def _pocket_site(vertices, pocket):
    """Pocket-only rows of vertices, from pocket's boolean/tensor residue mask --
    every pocket measure function below starts from this, the way every lipid
    measure starts from Chem.MolFromSmiles(smiles).
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket descriptors require at least one pocket residue")
    return site


def _pocket_core_rim(site):
    """Boolean core/rim masks split at this pocket's median residue burial."""
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    core = burial >= numpy.median(burial)
    return core, ~core


def _pocket_hydropathy(site):
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    return numpy.asarray(KYTE_DOOLITTLE)[residue_types]


def _pocket_aromatic(site):
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    return numpy.isin(residue_types, AROMATIC_RESIDUE_TYPES)


def _pocket_shape_spans(pocketness_path):
    coordinates = (
        pocket_atom_coordinates(pocketness_path)
        if pocketness_path is not None
        else numpy.empty((0, 3))
    )
    return pocket_shape(coordinates)


def _pocket_shape_spans_lambda_sqrt(pocketness_path):
    coordinates = (
        pocket_atom_coordinates(pocketness_path)
        if pocketness_path is not None
        else numpy.empty((0, 3))
    )
    return pocket_shape_lambda_sqrt(coordinates)


def read_pocket_atoms(pocketness_path):
    """Pocket side-chain coordinates, pocket residue keys and all residue keys.

    One pass over the file: the residue key of every ATOM/HETATM record in order,
    then the same backbone/flag filters pocket_atom_coordinates applies, so the
    coordinates are identical and the residue keys mask coarse_graph_nodes.csv.
    """
    coordinates = []
    pocket_residues = set()
    all_residues = []
    seen = set()
    with open(pocketness_path) as handle:
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
            coordinates.append(
                (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            )
    return numpy.array(coordinates, dtype=float), pocket_residues, all_residues


def descriptors_for(protein_dir):
    """The research catalog: every pocket column this project can compute, promoted
    or not.
    """
    protein_dir = Path(protein_dir)
    nodes = pandas.read_csv(protein_dir / "coarse_graph_nodes.csv")
    coordinates, pocket_residues, all_residues = read_pocket_atoms(
        protein_dir / "pocketness.pdb"
    )
    if not pocket_residues:
        return None

    key = [str(int(value)) if float(value).is_integer() else str(value)
           for value in nodes["ID_resSeq"]]
    mask = numpy.array([residue in pocket_residues for residue in key])
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
    row["pocket_volume_per_sasa"] = volume / max(sasa, 1e-9)

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
            row[f"{name}_q{quantile}"] = float(numpy.percentile(values, quantile))

    hydropathy = numpy.asarray(KYTE_DOOLITTLE)[site["residue_type"].to_numpy(dtype=int)]
    aromatic = numpy.isin(site["residue_type"].to_numpy(dtype=int), AROMATIC_RESIDUE_TYPES)
    if "residue_mean_buriedness" in site:
        burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
        core = burial >= numpy.median(burial)
        row["hydropathy_core"] = float(hydropathy[core].mean())
        row["hydropathy_rim"] = float(hydropathy[~core].mean()) if (~core).any() else float("nan")
        row["aromatic_share_core"] = float(aromatic[core].mean())
        row["aromatic_share_rim"] = float(aromatic[~core].mean()) if (~core).any() else float("nan")
    row["aromatic_share"] = float(aromatic.mean())
    row["hydropathy_mean"] = float(hydropathy.mean())
    return row


def pocket_cavity_volume(pocketness_path):
    """Estimate pocket free volume (A^3) and free fraction.

    Build the pocket atom cloud's convex hull. Subtract van der Waals volumes of atoms
    whose centres lie inside it. The only implementation of this formula: the
    Kron-RLS baseline used to carry its own copy and now reads this table instead.
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


def _residue_class_share(types, which):
    """One residue-class-share measure, same (vertices, pocket, pocketness_path)
    signature as every other one -- built from _RESIDUE_CLASS_TYPES instead of
    written out ten times. `which` is "core" or "rim"; an empty rim falls back to
    the whole site, the fallback this formula has always used.
    """
    def measure(vertices, pocket, pocketness_path=None):
        site = _pocket_site(vertices, pocket)
        member = numpy.isin(site["residue_type"].to_numpy(copy=True).astype(int), types)
        core, rim = _pocket_core_rim(site)
        mask = core if which == "core" else (rim if rim.any() else numpy.ones(len(site), dtype=bool))
        return float(member[mask].mean())
    return measure


# ----------------------------------------------------------------------------------
# one function per descriptor, named after the descriptor it computes
# ----------------------------------------------------------------------------------

# PROTEIN_DESCRIPTOR_NAMES, one function each,

def pocket_residue_share(vertices, pocket, pocketness_path=None):
    return len(_pocket_site(vertices, pocket)) / max(len(vertices), 1)


def pocket_sasa_share(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    pocket_sasa = float(site["residue_sas_area"].sum())
    return pocket_sasa / max(float(vertices["residue_sas_area"].sum()), 1e-9)


def pocket_volume_per_sasa(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    pocket_sasa = float(site["residue_sas_area"].sum())
    return float(site["residue_volume"].sum()) / max(pocket_sasa, 1e-9)


def pocket_extent(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans(pocketness_path)[0]


def pocket_elongation(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans(pocketness_path)[1]


def pocket_flatness(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans(pocketness_path)[2]


def ev14_q50(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.median(site["residue_mean_ev14"].to_numpy(dtype=float)))


def buriedness_q50(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.median(site["residue_mean_buriedness"].to_numpy(dtype=float)))


def depth_q10(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 10))


def apolar_sasa_share(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    hydropathy = _pocket_hydropathy(site)
    sasa = site["residue_sas_area"].values
    pocket_sasa = float(sasa.sum())
    return float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9))


def aromatic_share(vertices, pocket, pocketness_path=None):
    return float(_pocket_aromatic(_pocket_site(vertices, pocket)).mean())


def hydropathy_core(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    core, _ = _pocket_core_rim(site)
    return float(_pocket_hydropathy(site)[core].mean())


def hydropathy_rim(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    hydropathy = _pocket_hydropathy(site)
    _, rim = _pocket_core_rim(site)
    return float(hydropathy[rim].mean()) if rim.any() else float(hydropathy.mean())


def ev28_q10(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_ev28"].to_numpy(dtype=float), 10))


def aromatic_share_rim(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    aromatic = _pocket_aromatic(site)
    _, rim = _pocket_core_rim(site)
    return float(aromatic[rim].mean()) if rim.any() else float(aromatic.mean())


def hydropathy_mean(vertices, pocket, pocketness_path=None):
    return float(_pocket_hydropathy(_pocket_site(vertices, pocket)).mean())


def ev14_q10(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_ev14"].to_numpy(dtype=float), 10))


def pocket_extent_lambda_sqrt(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans_lambda_sqrt(pocketness_path)[0]


def pocket_elongation_lambda_sqrt(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans_lambda_sqrt(pocketness_path)[1]


def pocket_flatness_lambda_sqrt(vertices, pocket, pocketness_path=None):
    return _pocket_shape_spans_lambda_sqrt(pocketness_path)[2]


def ev14_q90(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_ev14"].to_numpy(dtype=float), 90))


def ev28_q50(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.median(site["residue_mean_ev28"].to_numpy(dtype=float)))


def ev28_q90(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_ev28"].to_numpy(dtype=float), 90))


def ev56_q10(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_ev56"].to_numpy(dtype=float), 10))


def buriedness_q10(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_buriedness"].to_numpy(dtype=float), 10))


def buriedness_q90(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_buriedness"].to_numpy(dtype=float), 90))


def depth_q50(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.median(site["residue_mean_voromqa_depth"].to_numpy(dtype=float)))


def depth_q90(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    return float(numpy.percentile(site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 90))


def aromatic_share_core(vertices, pocket, pocketness_path=None):
    site = _pocket_site(vertices, pocket)
    core, _ = _pocket_core_rim(site)
    return float(_pocket_aromatic(site)[core].mean())


def pocket_free_volume(vertices, pocket, pocketness_path=None):
    return pocket_cavity_volume(pocketness_path)[0] if pocketness_path is not None else 0.0


def pocket_packing_density(vertices, pocket, pocketness_path=None):
    return pocket_cavity_volume(pocketness_path)[1] if pocketness_path is not None else 0.0


# Derived instead of measured, same signature as every measure above, so its
# column is written exactly like any other.
def polar_share(vertices, pocket, pocketness_path=None):
    return 1.0 - apolar_sasa_share(vertices, pocket, pocketness_path)


# ----------------------------------------------------------------------------------
# registry: every protein name -> the function above that computes it
# ----------------------------------------------------------------------------------

# Every protein-side name and the one function computing it -- the counterpart of
# the lipid _LIPID_MEASURES dict. The name tuples of dataloader/descriptors.py select out
# of this one registry; they do not each get their own.
_PROTEIN_MEASURES = {
    "pocket_residue_share": pocket_residue_share,
    "pocket_sasa_share": pocket_sasa_share,
    "pocket_volume_per_sasa": pocket_volume_per_sasa,
    "pocket_extent": pocket_extent,
    "pocket_elongation": pocket_elongation,
    "pocket_flatness": pocket_flatness,
    "ev14_q50": ev14_q50,
    "buriedness_q50": buriedness_q50,
    "depth_q10": depth_q10,
    "apolar_sasa_share": apolar_sasa_share,
    "aromatic_share": aromatic_share,
    "hydropathy_core": hydropathy_core,
    "hydropathy_rim": hydropathy_rim,
    "ev28_q10": ev28_q10,
    "aromatic_share_rim": aromatic_share_rim,
    "hydropathy_mean": hydropathy_mean,
    "ev14_q10": ev14_q10,
    "pocket_extent_lambda_sqrt": pocket_extent_lambda_sqrt,
    "pocket_elongation_lambda_sqrt": pocket_elongation_lambda_sqrt,
    "pocket_flatness_lambda_sqrt": pocket_flatness_lambda_sqrt,
    "ev14_q90": ev14_q90,
    "ev28_q50": ev28_q50,
    "ev28_q90": ev28_q90,
    "ev56_q10": ev56_q10,
    "buriedness_q10": buriedness_q10,
    "buriedness_q90": buriedness_q90,
    "depth_q50": depth_q50,
    "depth_q90": depth_q90,
    "aromatic_share_core": aromatic_share_core,
    "pocket_free_volume": pocket_free_volume,
    "pocket_packing_density": pocket_packing_density,
    "polar_share": polar_share,
}
# The ten residue-class shares, from _RESIDUE_CLASS_TYPES instead of ten bodies.
for _class_name, _class_types in _RESIDUE_CLASS_TYPES.items():
    _PROTEIN_MEASURES[f"{_class_name}_share_core"] = _residue_class_share(_class_types, "core")
    _PROTEIN_MEASURES[f"{_class_name}_share_rim"] = _residue_class_share(_class_types, "rim")
del _class_name, _class_types


def protein_measure_function(name):
    """The callable behind one protein name -- the counterpart of lipid_measure_function."""
    return _PROTEIN_MEASURES[name]


# ----------------------------------------------------------------------------------
# the table: build, cache, write one column
# ----------------------------------------------------------------------------------

# Increment the format version when descriptor definitions or columns change.
_PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION = 8


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


def _protein_names(data_dir):
    """Proteins carrying both graph inputs under data/graphs/, in table row order."""
    graphs_dir = os.path.join(data_dir, "graphs")
    return sorted(
        protein for protein in os.listdir(graphs_dir)
        if os.path.isfile(os.path.join(graphs_dir, protein, "pocketness.pdb"))
        and os.path.isfile(os.path.join(graphs_dir, protein, "coarse_graph_nodes.csv"))
    )


def _protein_graph_inputs(data_dir, protein):
    """(vertices, pocket, pocketness_path) for one protein -- the raw input every
    protein measure function reads, the way a lipid measure reads one SMILES.
    """
    from dataloader.tensors_reading.protein_graph_tensors_reader import _pocket_tensor

    protein_dir = os.path.join(data_dir, "graphs", protein)
    pocketness_path = os.path.join(protein_dir, "pocketness.pdb")
    vertices = pandas.read_csv(os.path.join(protein_dir, "coarse_graph_nodes.csv"))
    return vertices, _pocket_tensor(Path(pocketness_path)), pocketness_path


def _protein_descriptor_manifest_is_current(data_dir, protein_names):
    """True when the manifest matches the format version and the current source
    sizes/mtimes -- what lets the table be reused, or one column patched into it.
    """
    try:
        manifest = json.loads(_protein_descriptor_table_manifest_path(data_dir).read_text())
    except (OSError, ValueError):
        return False
    return (
        manifest.get("format_version") == _PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION
        and manifest.get("sources") == _protein_descriptor_table_sources(data_dir, protein_names)
    )


def _fill_missing_columns(data_dir, table, names, csv_path):
    """Compute `names` for every protein already in `table` and append them.

    A new descriptor adds a column to a table whose graph sources are unchanged, so
    the manifest still matches and a full rebuild would never be triggered. Filling
    the gap here is what makes adding a descriptor "write the function, register it"
    with no third command -- the lipid cache fills a newly added measure the same way.
    """
    values = {name: [] for name in names}
    for protein in table.index:
        vertices, pocket, pocketness_path = _protein_graph_inputs(data_dir, protein)
        for name in names:
            values[name].append(
                _PROTEIN_MEASURES[name](vertices, pocket, pocketness_path)
            )
    for name in names:
        table[name] = values[name]
    try:
        table.to_csv(csv_path)
    except OSError:
        pass  # as in the full build: unpersisted is fine, a wrong value is not
    return table


def protein_descriptor_table(data_dir, force=False):
    """Return {protein: {descriptor: value}} from protein graph files.

    Read coarse_graph_nodes.csv and pocketness.pdb. Reuse data/protein_descriptors.csv
    when its manifest matches the format version and source sizes/mtimes. Otherwise
    recompute and save the table. Include derived and pocket chemistry descriptors.
    """
    import pandas as pd

    protein_names = _protein_names(data_dir)
    csv_path = _protein_descriptors_csv_path(data_dir)
    manifest_path = _protein_descriptor_table_manifest_path(data_dir)
    if (
        csv_path.exists() and not force
        and _protein_descriptor_manifest_is_current(data_dir, protein_names)
    ):
        try:
            # Use round_trip parsing to preserve the floats written by to_csv().
            table = pandas.read_csv(
                csv_path, index_col="protein", float_precision="round_trip"
            )
            if sorted(table.index) == protein_names:
                missing = [
                    name for name in PROTEIN_DESCRIPTOR_NAMES if name not in table.columns
                ]
                if missing:
                    table = _fill_missing_columns(data_dir, table, missing, csv_path)
                return {
                    protein: table.loc[protein].to_dict() for protein in table.index
                }
        except (OSError, ValueError, pandas.errors.ParserError, KeyError):
            pass  # fall through and recompute, same as any other stale/corrupt cache

    values = {}
    for protein in protein_names:
        vertices, pocket, pocketness_path = _protein_graph_inputs(data_dir, protein)
        # Every column through the same function a single-column write would use.
        values[protein] = {
            name: _PROTEIN_MEASURES[name](vertices, pocket, pocketness_path)
            for name in PROTEIN_DESCRIPTOR_NAMES
        }

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


def compute_protein_descriptor(data_dir, name, force=False):
    """Update one protein descriptor column for every protein under data/graphs/.

    Require an existing data/protein_descriptors.csv: this patches one column and
    preserves the others. --force rebuilds the whole table instead, which is also
    how it is first built.
    """
    table_path = _protein_descriptors_csv_path(data_dir)
    if force:
        return table_path, len(protein_descriptor_table(data_dir, force=True))

    protein_names = _protein_names(data_dir)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            f"`python3 preprocessing/compute_descriptors.py {name} --force` "
            "before writing one column"
        )

    function = protein_measure_function(name)
    values = {}
    for protein in protein_names:
        vertices, pocket, pocketness_path = _protein_graph_inputs(data_dir, protein)
        values[(protein,)] = function(vertices, pocket, pocketness_path)

    written = _write_column(table_path, values, name, ("protein",))
    # A column update leaves the manifest valid: its graph sources are untouched.
    return table_path, written


######################################################################################
# LIPID DESCRIPTORS
# one row per canonical candidate SMILES and isomeric mode
######################################################################################


# ----------------------------------------------------------------------------------
# helpers: acyl-chain walks, conformer ensemble, measured-volume lookup
# ----------------------------------------------------------------------------------

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


def _median_over_conformers(smiles, per_conformer_fn):
    """Return the median measure over the cached conformer ensemble."""
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(numpy.median(values))


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


# ----------------------------------------------------------------------------------
# one function per descriptor, named after the descriptor it computes
# ----------------------------------------------------------------------------------

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


def chain(smiles):
    """Return the longest non-ring, non-aromatic carbon path, or None for invalid/empty input."""
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:  # None (unparseable) or [] (no qualifying carbon) alike
        return None
    return max(lengths)


def tail_count(smiles):
    """Count components with at least _MINIMUM_TAIL_CARBONS; return None for invalid/empty input."""
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:
        return None
    return float(sum(1 for length in lengths if length >= _MINIMUM_TAIL_CARBONS))


def unsaturation(smiles):
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


def hbond(smiles):
    """RDKit H-bond donor + acceptor count -- a headgroup polarity proxy, not a pose."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.NumHDonors(mol) + Descriptors.NumHAcceptors(mol))


def heavy(smiles):
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


def experimental_lipid_volume(smiles):
    """Look up canonical SMILES in data/Lipid_Volumes.csv; return None for missing keys."""
    return _experimental_lipid_volume_table().get(smiles)


# ----------------------------------------------------------------------------------
# registry: every lipid name -> the function above that computes it
# ----------------------------------------------------------------------------------

LIPID_SHAPE_DESCRIPTOR_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "rotatable_fraction",
    "npr1", "npr2",
)

# These measures share a cached conformer ensemble and use the parallel build path.
CONFORMER_MEASURE_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "npr1", "npr2",
)


_LIPID_MEASURES = {
    "chain": chain,
    "unsaturation": unsaturation,
    "hbond": hbond,
    "heavy": heavy,
    "tail_count": tail_count,
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


LIPID_SIDE_NAMES = tuple(_LIPID_MEASURES)


def lipid_measure_function(name):
    """The callable behind one lipid name -- the counterpart of protein_measure_function."""
    return _LIPID_MEASURES[name]


# ----------------------------------------------------------------------------------
# the table: per-row values, write one column
# ----------------------------------------------------------------------------------

def descriptor_values_by_row(csv, measure, isomeric=False, cache=None):
    """Return per-candidate values in the encoder's candidate order.

    Use None for unavailable values and [None] for a row without usable candidates.
    Match isomeric mode to chain_lengths_by_row so candidate lists have equal lengths.
    Use cached canonical keys and values when available; compute missing entries.
    """
    from dataloader.pocket_lipid_compatibility import candidate_fields_by_row

    fn = _LIPID_MEASURES[measure]
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


def compute_lipid_descriptor(data_dir, name, isomeric=False, force=False):
    """Update one lipid descriptor column for interaction-table candidates.

    Require an existing data/lipid_descriptors.csv: this patches one column and
    preserves the others. --force rebuilds this isomeric variant's whole table
    through the cache builder instead, which is also how it is first built.
    """
    from dataloader.dataset_source import interaction_csv_path
    from dataloader.descriptor_cache_reader import lipid_descriptors_csv_path

    table_path = lipid_descriptors_csv_path(data_dir)
    csv_path = interaction_csv_path(str(data_dir) + os.sep)
    if force:
        from dataloader.cache_builders.descriptor_csv_builder import (
            build_lipid_descriptor_cache,
        )

        csv = pandas.read_csv(csv_path)
        protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
        path, written, _ = build_lipid_descriptor_cache(
            data_dir, csv, protein_names, csv_path, isomeric=isomeric
        )
        return path, written
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            f"`python3 preprocessing/compute_descriptors.py {name} --force` "
            "before writing one column"
        )

    csv = pandas.read_csv(csv_path)
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


######################################################################################
# PAIR DESCRIPTORS
# one row per candidate-protein pair, from the two tables above
######################################################################################


# ----------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------

# Tanford, The Hydrophobic Effect (1980): extended hydrocarbon-chain length.
# L = 1.5 + 1.265 * (n - 1) angstrom for n carbons.
# Convert carbon counts before comparing them with pocket lengths.
_CHAIN_BOND_PROJECTION_A = 1.265
_CHAIN_TERMINAL_A = 1.5


def chain_length_angstrom(carbons):
    """Estimate extended-chain length in angstrom from carbon count using Tanford's formula."""
    return _CHAIN_TERMINAL_A + _CHAIN_BOND_PROJECTION_A * (carbons - 1.0)


# ----------------------------------------------------------------------------------
# every pair descriptor, by name, in one function
# ----------------------------------------------------------------------------------

# The lipid values every PAIR_DESCRIPTOR_NAMES formula below reads. Named once: the
# pair table builder, the dataloader and the GBM baseline all assemble this same dict.
PAIR_DESCRIPTOR_LIPID_INPUTS = (
    "chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2",
)


_PAIR_MEASURES = {}


def _pair_measure(kind):
    """Register one pair formula under its own name, with the kind that says how
    dataloader/chemistry_prior.py's feature_similarity standardises its INPUTS.

    The kind governs that one function and nothing else. Training never standardises
    a pair formula's inputs: Dataloader computes the column from raw values and then
    z-scores the finished column on train statistics, the same as every other
    descriptor token. So a "bottleneck" formula reads standardised values in the kNN
    null model and raw ones in the model's own input -- see the kinds below.

    product : two DIFFERENT-unit quantities multiplied, so their relative
            contribution is whatever their raw scales happen to be --
            feature_similarity standardises both sides when --zscore.
    bottleneck : min(A, B), which compares nothing unless A and B are already on
            one scale, so feature_similarity standardises it with or without
            --zscore. On raw values the smaller-ranged side wins the min
            every time, which is a units artefact instead of a bottleneck.
    never : nothing to reconcile, so the inputs are left alone. Either both
            sides are already ONE physical quantity in angstrom
            (occupancy, chain_extent_gap), where standardising would
            replace "does the cavity reach as far as the chain" with an
            abstract distance; or the formula is a ratio instead of a
            product or a difference (tail_elongation_fit).

    pair_names_of_kind reads these back; nothing re-lists them by hand.
    """
    def register(function):
        function.kind = kind
        _PAIR_MEASURES[function.__name__] = function
        return function
    return register


@_pair_measure("never")
def occupancy(lipid, protein):
    return max(0.0, chain_length_angstrom(lipid["chain"]) - protein["pocket_extent"])


@_pair_measure("never")
def chain_extent_gap(lipid, protein):
    return protein["pocket_extent"] - chain_length_angstrom(lipid["chain"])


@_pair_measure("product")
def aromatic_contact(lipid, protein):
    return protein["aromatic_share"] * lipid["unsaturation"]


@_pair_measure("product")
def hbond_match(lipid, protein):
    return protein["polar_share"] * lipid["hbond"]


@_pair_measure("product")
def volume_fit(lipid, protein):
    return protein["pocket_volume_per_sasa"] * lipid["heavy"]


@_pair_measure("product")
def buriedness_match(lipid, protein):
    return protein["buriedness_q50"] * lipid["heavy"]


@_pair_measure("product")
def depth_bulk_match(lipid, protein):
    return protein["depth_q10"] * lipid["heavy"]


@_pair_measure("product")
def hydropathy_chain_match(lipid, protein):
    return protein["hydropathy_core"] * lipid["chain"]


@_pair_measure("bottleneck")
def aromatic_contact_min(lipid, protein):
    return min(protein["aromatic_share"], lipid["unsaturation"])


@_pair_measure("bottleneck")
def hbond_match_min(lipid, protein):
    return min(protein["polar_share"], lipid["hbond"])


@_pair_measure("never")
def tail_elongation_fit(lipid, protein):
    return lipid["tail_count"] / max(protein["pocket_elongation"], 1.0)


@_pair_measure("product")
def hydropathy_rim_match(lipid, protein):
    return protein["hydropathy_rim"] * lipid["hbond"]


@_pair_measure("product")
def elongation_shape_match(lipid, protein):
    return protein["pocket_elongation"] * lipid["npr1"]


@_pair_measure("product")
def flatness_shape_match(lipid, protein):
    return protein["pocket_flatness"] * lipid["npr2"]


def pair_names_of_kind(kind):
    """The pair descriptors registered under one kind -- what dataloader/descriptors.py
    builds MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES and MIN_PAIR_DESCRIPTOR_NAMES from.
    """
    return tuple(name for name, fn in _PAIR_MEASURES.items() if fn.kind == kind)


def pair_descriptor_value(name, lipid_values, protein_values):
    """One pair descriptor from the lipid and protein value dictionaries."""
    try:
        function = _PAIR_MEASURES[name]
    except KeyError:
        raise ValueError(
            f"Unknown pair descriptor: {name}. Known: {tuple(_PAIR_MEASURES)}"
        ) from None
    return function(lipid_values, protein_values)


# ----------------------------------------------------------------------------------
# the table: per-row values, write one column
# ----------------------------------------------------------------------------------

def pair_values_by_row(csv, name, protein_table, isomeric=False, lipid_cache=None, pair_cache=None):
    """Return per-row candidate values of one pair descriptor, in encoder order.

    Prefer data/pair_descriptors.csv (pair_cache, descriptor_cache_reader.
    load_pair_value_cache's {(smiles, protein): {name: value}}). A (candidate,
    protein) pair absent from it -- a new candidate, or no pair cache at all --
    falls back to pair_descriptor_value on lipid_cache's own per-SMILES values,
    the same fallback descriptor_values_by_row uses for a candidate missing from
    the lipid cache.

    Return per-row lists, with None for a row without usable candidates.
    """
    from dataloader.pocket_lipid_compatibility import candidate_fields_by_row

    raw_to_canonical = lipid_cache["raw_to_canonical"] if lipid_cache else {}
    lipid_values = lipid_cache["values"] if lipid_cache else {}
    pair_values = pair_cache or {}
    protein_column = csv["LTPProtein"].to_numpy()
    by_field = {}
    per_row = []
    for row_position, field in enumerate(candidate_fields_by_row(csv)):
        protein = protein_column[row_position]
        field_key = (field, protein)
        values = by_field.get(field_key)
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
                    key = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=isomeric)
                if key in seen:
                    continue
                seen.add(key)
                cached_pair = pair_values.get((key, protein))
                if cached_pair is not None and name in cached_pair:
                    values.append(cached_pair[name])
                    continue
                cached_lipid = lipid_values.get(key)
                lipid_input = {
                    measure: (
                        cached_lipid[measure]
                        if cached_lipid is not None and measure in cached_lipid
                        else _LIPID_MEASURES[measure](key)
                    )
                    for measure in PAIR_DESCRIPTOR_LIPID_INPUTS
                }
                values.append(pair_descriptor_value(name, lipid_input, protein_table[protein]))
            values = values or [None]
            by_field[field_key] = values
        per_row.append(values)
    return per_row


# ----------------------------------------------------------------------------------
# the table: write one column
# ----------------------------------------------------------------------------------

def compute_pair_descriptor(data_dir, name, isomeric=False, force=False):
    """Update one pair descriptor column from the cached lipid and protein tables.

    Patch that one column and preserve the others. --force rebuilds this isomeric
    variant's whole table instead, which is also how it is first built.
    """
    from dataloader.dataset_source import interaction_csv_path
    from dataloader.descriptor_cache_reader import (
        load_lipid_descriptor_cache,
        pair_descriptors_csv_path,
    )

    table_path = pair_descriptors_csv_path(data_dir)
    if force:
        from dataloader.cache_builders.descriptor_csv_builder import build_pair_value_cache

        csv = pandas.read_csv(interaction_csv_path(str(data_dir) + os.sep))
        return build_pair_value_cache(data_dir, csv, isomeric=isomeric)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            f"`python3 preprocessing/compute_descriptors.py {name} --force` "
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
        lipid_input = {key: lv[key] for key in PAIR_DESCRIPTOR_LIPID_INPUTS}
        values[(smiles, protein, bool(isomeric))] = pair_descriptor_value(
            name, lipid_input, pv
        )

    written = _write_column(
        table_path, values, name, ("smiles", "protein", "isomeric"), isomeric
    )
    return table_path, written


######################################################################################
# SHARED: WHICH TABLE A NAME BELONGS TO, AND THE CLI
# no descriptor formulas below this line
######################################################################################

def descriptor_side(name):
    """"protein" / "lipid" / "pair" for `name`, or None when no table defines it."""
    if name in PROTEIN_DESCRIPTOR_NAMES:
        return "protein"
    if name in LIPID_SIDE_NAMES:
        return "lipid"
    if name in PAIR_DESCRIPTOR_NAMES:
        return "pair"
    return None


def _write_column(table_path, new_values, name, key_columns, isomeric=None):
    """Update one descriptor column, in one isomeric mode when the table has modes.

    Match new_values by key_columns. Preserve other columns and the other mode's rows.
    The protein table carries no isomeric column: isomeric=None makes every row the
    request's own.
    """
    table = pandas.read_csv(table_path, float_precision="round_trip")
    mask = (
        pandas.Series(True, index=table.index) if isomeric is None
        else table["isomeric"] == bool(isomeric)
    )
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


def _print_catalog():
    for side, names in (
        ("protein", PROTEIN_DESCRIPTOR_NAMES),
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
        help="rebuild that side's whole table instead of writing one column",
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
        path, written = compute_protein_descriptor(
            arguments.data_dir, name, force=arguments.force
        )
        print(f"{name}: protein side, {written} proteins -> {path}")
        return 0

    if side == "lipid":
        path, written = compute_lipid_descriptor(
            arguments.data_dir, name, isomeric=arguments.isomeric, force=arguments.force
        )
        variant = "isomeric" if arguments.isomeric else "deterministic"
        print(f"{name}: lipid side, {written} {variant} rows -> {path}")
        return 0

    path, written = compute_pair_descriptor(
        arguments.data_dir, name, isomeric=arguments.isomeric, force=arguments.force
    )
    variant = "isomeric" if arguments.isomeric else "deterministic"
    print(f"{name}: pair side, {written} {variant} rows -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
