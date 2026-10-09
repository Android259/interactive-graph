#!/usr/bin/env python3
"""Every descriptor VALUE this project computes, and the CLI that writes one into its table.

Three kinds of descriptor, three tables, one formula per name:

    protein : data/protein_descriptors.csv   one row per protein, from
              data/graphs/<protein>/{pocketness.pdb,coarse_graph_nodes.csv}
    lipid   : data/lipid_descriptors.csv     one row per (canonical candidate SMILES,
              isomeric variant), from the interaction table's own SMILES
    pair     : data/pair_descriptors.csv     one row per (candidate, protein), combined
              arithmetically from the two tables above -- never RDKit

The names themselves (which descriptors exist, how an arg file spells one, which are
family-neutral) stay in dataloader/pair_descriptors.py, with the catalog parsing
training/read_configuration.py and architecture/ read to size layers. This module owns
only the arithmetic: given a name, what number comes out. The split is why
dataloader/pair_descriptors.py can import nothing from here -- the arrow runs one way,
this module reads the name lists, never the reverse.

Two readers of this module beyond the CLI below, both already live before any table
exists: dataloader/Dataloader.py._compute_pair_descriptors computes values directly when
a cache is missing (the documented fallback -- a run never fails for want of a prebuilt
table), and dataloader/cache_builders/pair_descriptor_cache_writer.py calls the same functions to
fill a whole table at once.

Editing a formula here does NOT invalidate a stored column: the tables hold numbers, and
dataloader/pair_descriptor_cache_reader.py serves any column that holds one. So a changed formula
and the numbers already on disk will disagree until the column is recomputed on purpose --
`compute_descriptors.py NAME` below is how, and doing it is the editor's job, not the cache's.

Usage:
    python3 preprocessing/compute_descriptors.py --list
    python3 preprocessing/compute_descriptors.py tpsa
    python3 preprocessing/compute_descriptors.py tpsa --isomeric
    python3 preprocessing/compute_descriptors.py pocket_extent --force
    python3 preprocessing/compute_descriptors.py volume_fit

One name at a time, and only that name's column is written: the other columns of the
table, and the other isomeric half of it, are read back and rewritten untouched. A
protein name is the exception -- pocket_descriptor() produces the whole positional
vector in one pass, so asking for one protein name recomputes that table's row set, the
same work dataloader/chemistry_prior.py's self-persisting path does on first use.
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

from dataloader.pair_descriptors import (  # noqa: E402
    PAIR_DESCRIPTOR_NAMES,
    POCKET_CHEMISTRY_DESCRIPTOR_NAMES,
    PROTEIN_DERIVED_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
)

# The pocket formulas below were written against this name and index their own output
# tuple by its length; dataloader/protein_graph_builder.py imports PROTEIN_DESCRIPTOR_
# NAMES under the same alias for the same reason.
POCKET_DESCRIPTOR_NAMES = PROTEIN_DESCRIPTOR_NAMES


# ----------------------------------------------------------------------------------
# Protein side: residue tables, cavity geometry, pocket chemistry.
# ----------------------------------------------------------------------------------

# Kyte & Doolittle (1982) hydropathy index, indexed by Voronota's residue_type code.
# That code is the alphabetical rank of the three-letter name, verified against
# ID_resName over all 35 proteins in data/graphs (one name per code, no collisions):
# ALA=0 ARG=1 ASN=2 ASP=3 CYS=4 GLN=5 GLU=6 GLY=7 HIS=8 ILE=9
# LEU=10 LYS=11 MET=12 PHE=13 PRO=14 SER=15 THR=16 TRP=17 TYR=18 VAL=19
KYTE_DOOLITTLE = (
    1.8, -4.5, -3.5, -3.5, 2.5, -3.5, -3.5, -0.4, -3.2, 4.5,
    3.8, -3.9, 1.9, 2.8, -1.6, -0.8, -0.7, -0.9, -1.3, 4.2,
)
# Voronota's residue_type code is alphabetical by one-letter code (verified against
# ID_resName), the same order KYTE_DOOLITTLE is indexed in; Phe, Trp, Tyr sit here.
AROMATIC_RESIDUE_TYPES = (13, 17, 18)

# The same residue_type code read as a one-letter name, in the same alphabetical-by-
# three-letter-name order KYTE_DOOLITTLE above is indexed in. Only
# pocket_chemistry_descriptor() below needs it: its shares are defined by residue
# CLASS, and a class is a set of names, not a hydropathy threshold.
RESIDUE_LETTERS = (
    "A", "R", "N", "D", "C", "Q", "E", "G", "H", "I",
    "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V",
)
# Residue classes behind POCKET_CHEMISTRY_DESCRIPTOR_NAMES. Spelled as residue_type
# codes rather than letters so the shares are computed by a numpy membership test on
# the column itself. Identical membership to training/pair_baseline_common.py's
# BASIC/ACIDIC/POLAR/HBOND_DONOR/HBOND_ACCEPTOR (the Kron-RLS side's copy, which works
# in letters) -- that equality is what lets a descriptor set found by a Kron-RLS search
# be named in a network arg file and mean the same thing.
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

# Van der Waals radii in angstrom (Bondi), for the cavity's free volume below. Only the
# elements a protein PDB actually carries; anything unlisted falls back to carbon, the
# commonest by far. Same table and same fallback as training/pair_baseline_common.py.
_VDW_RADII = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "H": 1.20}
# Side chains only: a backbone atom is in every residue and says nothing about which
# ones line a cavity. Same set the pocket mask itself is built from.
POCKET_BACKBONE_ATOMS = ("C", "CA", "CB", "O", "N")
def pocket_atom_coordinates(pocketness_path):
    """Coordinates of the side-chain atoms pocketness.pdb marks as pocket.

    The same lines and the same flag column the pocket mask is read from, so the cloud
    measured here is the site the model is given, not a second opinion about it.
    """
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
    """(spans, eigenvalues) along the pocket atom cloud's own principal axes, longest
    first, or None below 4 atoms -- the one eigen-decomposition pocket_shape() and
    pocket_shape_full() both build their public return values from, so there is a
    single place this project computes cavity shape, not two drifting copies (this
    absorbed preprocessing/pocket_shape_descriptors.py's own former shape_from_coordinates,
    which duplicated it).

    The three axes are the principal components of the coordinates (PCA via the
    covariance matrix's eigenvectors -- only the DIRECTIONS are taken from it). Each
    axis' own LENGTH (`spans`) is the 5th-to-95th percentile span of the coordinates'
    projection onto it, not the axis' eigenvalue (or its square root) -- covariance is
    not robust, so a single stray atom at the cavity's rim can inflate the variance
    along its own direction by an amount ordinary PCA has no defence against.
    Percentile-trimming every axis this way, not just the first, closes that: an
    earlier version measured extent (axis 0's own span) exactly this way already, but
    took elongation/flatness straight from the eigenvalues, so the same stray atom that
    could not move extent could still distort the two ratios -- verified: the ratio is
    between LENGTHS, not raw spread, so "twice as long" reads as 2 rather than 4,
    matching the earlier eigenvalue-ratio's own intent. `eigenvalues` (clipped, same
    floor as spans) is kept alongside only for pocket_shape_full()'s gyration radius,
    which needs the RAW variance along each axis rather than its robust-to-outliers
    percentile span.

    Four atoms are the minimum for a covariance worth taking; below that the cavity is
    described by its residue-level entries alone and the shape entries are zeros, which
    the train-only standardisation then leaves at the mean.
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
    """Extent, elongation and flatness of the cavity's atom cloud -- see
    _pocket_axis_spans for the eigen-decomposition this is built from.

    Returns zeros below 4 atoms (_pocket_axis_spans' own floor), which the train-only
    standardisation then leaves at the mean.
    """
    axes = _pocket_axis_spans(coordinates)
    if axes is None:
        return 0.0, 0.0, 0.0
    spans, _ = axes
    return float(spans[0]), float(spans[0] / spans[1]), float(spans[1] / spans[2])


def pocket_shape_full(coordinates):
    """Every span pocket_shape() computes but discards (width, thickness) plus the
    scale-explicit gyration radius, from the SAME eigen-decomposition pocket_shape()
    itself uses (_pocket_axis_spans) -- the research-catalog superset
    preprocessing/pocket_shape_descriptors.py reports, not a second copy of the geometry.

    pocket_gyration = sqrt(sum(eigenvalues)): total spread across all three axes at
    once, for scale where scale is wanted explicitly rather than smuggled into a ratio.
    Zeros below 4 atoms, same floor as pocket_shape().
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
    """The same three axes measured the other way: sqrt(eigenvalue) on a ROBUST covariance.

    pocket_shape() above measures each axis by the percentile span of the projections and
    takes the ratios between those spans. This is the alternative the research catalog
    (preprocessing/pocket_shape_descriptors.py) has always used for the ratios -- sqrt(lambda),
    i.e. the axis' standard deviation -- computed here on a MinCovDet robust covariance
    rather than the ordinary one. That combination is the one of seven measured in
    files/results/pocket_shape_metric_comparison.md that keeps its sign inside BOTH large families
    as well as pooled, against the head-group-class target family does not determine
    (+0.115 CRAL-TRIO / +0.312 lipocalin / +0.401 pooled, CI [0.061, 0.658]). The
    production span formula reverses sign inside both families on that same target
    (-0.071 / -0.156 against pooled +0.288) -- the between-family artifact pattern
    files/reference/pocket_shape_descriptors.md section 4a used to disqualify pocket_volume_per_sasa.

    Robust for the DIRECTIONS too, not only the eigenvalues: pocket_shape()'s own docstring
    notes covariance is not robust, but percentile-trims only the LENGTH, leaving the axes
    themselves free to be tilted by one rim atom. MinCovDet fits the densest subset, so
    directions and eigenvalues both come from it.

    eta^2 against the 9-family split (35 proteins, floor 0.235): extent 0.737,
    elongation 0.479, flatness 0.256. All three sit ABOVE the floor, so none is added to
    POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES -- they are opt-in by name only, exactly as
    ev14_q10 was left out until a real run had been seen.

    Falls back to the ordinary covariance below min_robust_points atoms, or if the robust
    fit fails on a degenerate cloud -- a small pocket still gets a number, just not a robust
    one. Zeros below 4 atoms, the same floor pocket_shape() uses.
    """
    if len(coordinates) < 4:
        return 0.0, 0.0, 0.0
    covariance = None
    if len(coordinates) >= min_robust_points:
        try:
            # Imported here rather than at module scope: the dataloader is imported by
            # every training run, sklearn is not otherwise one of its dependencies, and
            # this value is computed once per protein and then cached in
            # data/protein_descriptor_table.json, never per sample.
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
    """Aggregate one cavity descriptor from a protein's residue table and pocket mask.

    Returns ``[1, len(POCKET_DESCRIPTOR_NAMES)]`` so PyG collation stacks one row per
    sample. Shares and ratios are bounded and the two angstrom quantities span well
    under an order of magnitude across proteins, so nothing here is log-compressed; the
    train-only standardisation installed later handles the rest.

    ``pocketness_path`` supplies the atom coordinates the shape entries need. Without
    it those entries are zero -- a caller that has no PDB gets a usable descriptor
    rather than an exception, but it gets one with no shape in it.
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket_descriptors requires at least one pocket residue")
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    hydropathy = numpy.asarray(KYTE_DOOLITTLE)[residue_types]
    aromatic = numpy.isin(residue_types, AROMATIC_RESIDUE_TYPES)
    sasa = site["residue_sas_area"].values
    pocket_sasa = float(sasa.sum())
    pocket_volume = float(site["residue_volume"].sum())
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    # The pocket's own median splits it into a depth and a mouth. Median, not a fixed
    # threshold: burial is not comparable across proteins, the split within one is.
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
    values = (
        len(site) / max(len(vertices), 1),
        pocket_sasa / max(float(vertices["residue_sas_area"].sum()), 1e-9),
        pocket_volume / max(pocket_sasa, 1e-9),
        extent,
        elongation,
        flatness,
        float(numpy.median(site["residue_mean_ev14"].to_numpy(dtype=float))),
        float(numpy.median(burial)),
        float(numpy.percentile(
            site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 10
        )),
        float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9)),
        float(aromatic.mean()),
        float(hydropathy[core].mean()),
        float(hydropathy[rim].mean()) if rim.any() else float(hydropathy.mean()),
        # Appended, not interleaved with their thematic siblings above: architecture/
        # pair_descriptor_head.py's _AROMATIC_SHARE_INDEX/_APOLAR_SASA_SHARE_INDEX are
        # bare integer literals into this tuple, not name lookups, so every existing
        # position must stay put -- new entries only ever go at the end. The two
        # promoted from preprocessing/pocket_shape_descriptors.py's research catalog after
        # files/reference/pocket_shape_descriptors.md section 7's eta^2 check (both at/near the
        # no-structure floor, unlike the 13 above's own six excluded entries) and
        # section 7's addendum (aromatic_share_rim's sign agrees across both large
        # families AND pooled against head-group-class count; ev28_q10 does not
        # against either target -- neither survives correction, both merely passed
        # the family-fingerprint screen a candidate needs before this promotion, not a
        # proof of transferable pair signal).
        float(numpy.percentile(site["residue_mean_ev28"].to_numpy(dtype=float), 10)),
        float(aromatic[rim].mean()) if rim.any() else float(aromatic.mean()),
        # Third promotion (same section 7 catalog): whole-pocket hydropathy, not split
        # by the core/rim burial median the way hydropathy_core/hydropathy_rim above
        # are. eta^2=0.611 against family -- above the neutral floor, unlike the two
        # entries just above -- so this one is deliberately excluded from
        # POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES; see PROTEIN_DESCRIPTOR_NAMES's own
        # comment in dataloader/pair_descriptors.py for where it is safe to use.
        float(hydropathy.mean()),
        # Fourth promotion (same batch): ev14's own shallow decile, the same recipe
        # ev28_q10 above already uses on the sibling column. eta^2=0.238, at the
        # no-structure floor -- see PROTEIN_DESCRIPTOR_NAMES's own comment.
        float(numpy.percentile(site["residue_mean_ev14"].to_numpy(dtype=float), 10)),
        # The three shape entries measured the other way -- sqrt(eigenvalue) on a robust
        # covariance instead of percentile-span ratios. Not replacements: the span-based
        # pocket_extent/elongation/flatness above keep their positions (load-bearing, see
        # the comment on the first appended block), and these three are separate names an
        # arg file opts into by swapping them in. Full comparison of the two formulas over
        # seven variants, two lipid targets and the within-family sign check:
        # files/results/pocket_shape_metric_comparison.md; the values come from
        # pocket_shape_lambda_sqrt() above, which carries the measured numbers.
        extent_lambda_sqrt,
        elongation_lambda_sqrt,
        flatness_lambda_sqrt,
    )
    if len(values) != len(POCKET_DESCRIPTOR_NAMES):
        raise ValueError("pocket descriptor list and name list disagree")
    expected = getattr(config, "pocket_descriptor_count", None)
    if expected not in (None, 0) and expected != len(values):
        # Caught here rather than as a shape mismatch inside the classifier, where the
        # number would arrive as an unexplained dimension.
        raise ValueError(
            f"pocket_descriptor_count is {expected} but the descriptor has "
            f"{len(values)} entries; ModelConfig and POCKET_DESCRIPTOR_NAMES disagree"
        )
    return torch.tensor(values, dtype=torch.float32).unsqueeze(0)


def pocket_cavity_volume(pocketness_path):
    """(free cavity volume in A^3, free fraction) of the binding pocket.

    The convex hull of the pocket atom cloud MINUS the van der Waals volume of every
    atom in the file whose centre falls inside that hull: the space actually left for a
    ligand. Neither quantity already in POCKET_DESCRIPTOR_NAMES is a cavity volume --
    `residue_volume` is the Voronoi cell of each LINING residue (protein material, not
    empty space) and tracks the residue count at rho=0.993, which is why
    pocket_volume_per_sasa replaced it; the hull on its own still correlates 0.972 with
    residue count over these 35 proteins. The free volume correlates 0.791, and the
    free FRACTION -0.196 -- an axis genuinely independent of pocket size.

    The absolute volume matters for a second reason: it is the only protein-side
    quantity on the same physical scale as the lipid side's experimental_lipid_volume
    (mean 632 A^3), so the cavity-volume-against-lipid-volume relation the source paper
    (Titeca et al., files/literature/Reuter.pdf) actually measures becomes expressible as a pair
    quantity rather than as two incomparable numbers.

    Identical formula to training/pair_baseline_common.py::_cavity_values -- see that
    function for the measurements quoted above. Duplicated rather than imported because
    training.pair_baseline_common imports dataloader.chemistry_prior, which imports
    this module: the arrow only runs one way.
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
    """{name: value} for POCKET_CHEMISTRY_DESCRIPTOR_NAMES -- residue-class shares of
    the pocket, split core/rim, plus the two cavity-volume measures.

    A DICT and not a row of pocket_descriptor()'s tensor, deliberately. Positions in
    that tensor are load-bearing (architecture/pair_descriptor_head.py indexes it by
    bare integer literal) and its length is ModelConfig.pocket_descriptor_count, which
    is part of every --pocket_descriptors run's parameter count and therefore of its
    run-directory identity; appending to it would silently renumber past runs. These
    names are reached by NAME instead -- through --descriptor_names/
    --protein_descriptors and dataloader/chemistry_prior.py's protein_descriptor_table
    -- exactly the way PROTEIN_DERIVED_DESCRIPTOR_NAMES already is, so nothing that
    does not ask for them by name changes at all.

    Why these twelve: files/binding_determinants_literature_and_feature_proposals.md.
    The residue-class shares are the mechanism the head-group-recognition literature
    names first (anionic head groups read by Lys/Arg), and the core/rim split is the
    source paper's own two-channel specificity (mouth reads the head group, depth packs
    the chain). They were added on the Kron-RLS side first and a 16369-subset search
    there (results/tables/cron_test_metrics/exhaustive_protein_side_search.csv) put four of them --
    basic_share_core, pocket_free_volume, basic_share_rim, hbond_donor_share_core -- in
    almost every leading combination, ahead of two of the incumbent seven. All twelve
    are computed here rather than only those four: they come out of one pass over the
    same pocket residues, and keeping the network's pool equal to the Kron-RLS pool is
    what makes a set found by a search there nameable here without a second spelling.

    `pocketness_path` is what the two cavity entries need. Without it they are 0.0,
    matching pocket_descriptor()'s own convention for its shape entries.
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket_chemistry_descriptor requires at least one pocket residue")
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    # The pocket's own median splits it into a depth and a mouth -- the same split
    # pocket_descriptor() uses for hydropathy_core/hydropathy_rim, and with the same
    # fallback when every residue sits at the median.
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
# Bumped to 4 when pocket_extent/elongation/flatness_lambda_sqrt were appended to
# PROTEIN_DESCRIPTOR_NAMES: the cache keys on source-file mtime/size, not on this code,
# so a table written before those three existed would still validate and be served back
# three columns short. Bumped to 5 for POCKET_CHEMISTRY_DESCRIPTOR_NAMES (the ten
# residue-class shares and the two cavity-volume measures), for exactly the same
# reason -- an existing data/protein_descriptor_table.json is twelve columns short of
# what this code now writes, and only the version number says so.
_PROTEIN_DESCRIPTOR_TABLE_FORMAT_VERSION = 5


def _protein_descriptors_csv_path(data_dir):
    return Path(data_dir) / "protein_descriptors.csv"


def _protein_descriptor_table_manifest_path(data_dir):
    return Path(data_dir) / "protein_descriptors.manifest.json"


def _protein_descriptor_table_sources(data_dir, protein_names):
    from dataloader.cache_builders.protein_graph_tensor_cache_writer import _source_record

    root_dir = Path(data_dir).resolve()
    paths = []
    for protein in protein_names:
        protein_dir = root_dir / "graphs" / protein
        paths.append(protein_dir / "pocketness.pdb")
        paths.append(protein_dir / "coarse_graph_nodes.csv")
    return [_source_record(path, root_dir) for path in paths if path.exists()]


def protein_descriptor_table(data_dir, force=False):
    """{protein: {PROTEIN_DESCRIPTOR_NAMES + PROTEIN_DERIVED_DESCRIPTOR_NAMES +
    POCKET_CHEMISTRY_DESCRIPTOR_NAMES: value}},
    read straight off data/graphs/<protein>/{coarse_graph_nodes.csv,pocketness.pdb} --
    the same recipe preprocessing/pocket_descriptor_identity_check.py uses, standalone
    (no ProteinGraphBuilder/ModelConfig instance needed: pocket_descriptor's own
    `config` argument is only used to cross-check pocket_descriptor_count, which is
    skipped when config is None).

    These 35 proteins' worth of values do not depend on --seed/--excluded_groups/the
    interaction table at all -- only on data/graphs/*/{pocketness.pdb,
    coarse_graph_nodes.csv}, which almost never change once built -- yet every
    Dataloader instance (one per (group, seed) job) used to recompute the whole table
    from scratch: ~10ms/protein once imports are warm, ~4s cold on the very first call
    in a process, paid independently by every one of a grid's N processes with nothing
    shared between them (measured; unlike dataloader/pair_descriptor_cache_reader.py, which at
    least amortises the lipid side, this had no persistence at all).

    Self-persisting rather than a build-it-first-or-fall-back-slow cache: the first
    call anywhere (any process, any machine sharing this data/ dir) computes the table
    and writes data/protein_descriptors.csv (plus a small sidecar manifest,
    data/protein_descriptors.manifest.json, carrying only the format version and the
    source files' size/mtime -- never a descriptor value itself); every call after
    that, in any process, reads the CSV back in milliseconds -- no separate prep
    script, no args-file flag to detect, nothing to remember to run before a grid
    launches. Still keyed on each source file's size/mtime (same discipline as
    protein_graph_tensor_cache_reader.py) so a rebuilt data/graphs/<protein>/ is picked up
    rather than served stale.

    The two derived names (aromatic_share_coarse/polar_share_coarse) are computed
    here too, from the raw aromatic_share/apolar_sasa_share this function already
    reads, so a caller can look either kind up by name the same way -- see
    coarse_share/PROTEIN_DERIVED_DESCRIPTOR_NAMES in dataloader/pair_descriptors.py.
    """
    import pandas as pd

    from dataloader.protein_graph_tensor_cache_reader import _pocket_tensor

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
                # float_precision="round_trip": pandas' default C float parser is
                # fast but not always exact (it can read back "0.2356687933206558"
                # for a written "0.23566879332065582", a one-ULP drift on write/read
                # that `to_csv` itself does not introduce) -- round_trip trades a
                # slower parse for serving back exactly the value computed below.
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
        descriptor = pocket_descriptor(
            vertices, pocket, None, pocketness_path=pocketness_path
        )[0]
        raw = {
            name: float(descriptor[position])
            for position, name in enumerate(PROTEIN_DESCRIPTOR_NAMES)
        }
        # Reached by NAME only, never through the positional descriptor tensor above
        # -- see POCKET_CHEMISTRY_DESCRIPTOR_NAMES' own comment for why they are not
        # part of PROTEIN_DESCRIPTOR_NAMES.
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
    """value (already in [0, 1]) -> the centre of its fixed-width third.

    torch.bucketize(value, edges, right=False)'s own rule: a value exactly on an
    edge stays in the LOWER band (edge itself is the band's upper, exclusive, bound).
    """
    band = sum(1 for edge in _SHARE_BAND_EDGES if value > edge)
    return _SHARE_BAND_CENTRES[band]


_MINIMUM_TAIL_CARBONS = 4
# Below this many carbons, a non-aromatic/non-ring component is more likely an
# N-methyl/ethyl branch (e.g. the choline headgroup's three methyls, each its own
# 1-carbon component) than an actual acyl tail -- acyl_chain_count would otherwise
# count every headgroup methyl as its own "tail". 4 is the shortest fatty-acid tail
# this project's SMILES actually carry (butyryl); verified DOPC (2 real C18 tails)
# -> 2, lyso-PC (1 real tail + headgroup methyls) -> 1 at this threshold.


def _acyl_chain_component_lengths(smiles):
    """Carbon count of EVERY connected non-aromatic, non-ring component of a
    molecule's carbon skeleton -- the shared computation longest_acyl_chain and
    acyl_chain_count both read, one taking the max, the other counting how many
    clear _MINIMUM_TAIL_CARBONS. Head groups, rings and sugars drop out by
    construction (same discipline as longest_acyl_chain always used). None for
    anything RDKit cannot parse, [] for a molecule with no such carbon at all.
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

    # Longest shortest-path in each connected component: on a chain that is its length,
    # and a double breadth-first search finds it without enumerating paths.
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
    """Per-tail structure, not just per-tail length: the shared read every tail-only
    descriptor below draws on.

    Same skeleton `_acyl_chain_component_lengths` walks -- non-aromatic, non-ring
    carbons, connected components -- but keeps the LONGEST PATH ITSELF rather than only
    its length, because the tail descriptors need positions along it (where the double
    bonds sit relative to the methyl terminus), not a count.

    Returns a list, one entry per component, of
        {"carbons": int, "atoms": [mol atom indices along the longest path],
         "double_bonds": int, "position_from_end": int | None}
    or None when RDKit cannot parse `smiles`, [] when it has no qualifying carbon --
    the same two "missing" conventions the length helper already uses, so every caller
    keeps testing the same thing.

    `position_from_end` is the (n-x) convention of lipid shorthand notation: carbons
    counted from the METHYL end of the chain to the nearest double bond (Liebisch et
    al., J Lipid Res 2020). It is the double bond CLOSEST to that end, and None for a
    fully saturated tail -- absent rather than zero, since zero is a real position.
    The methyl end is taken as whichever endpoint of the longest path is further from
    the rest of the molecule, i.e. the endpoint whose terminal carbon has no neighbour
    outside the component; with both or neither qualifying the lower-index endpoint is
    used, so the value is at least deterministic where the chain is ambiguous.
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
    """Only the components long enough to be a tail, [] / None otherwise.

    `acyl_chain_count`'s own >= _MINIMUM_TAIL_CARBONS bar, applied once here so every
    tail descriptor counts the same set of tails that flag already reports.
    """
    components = _acyl_chain_components(smiles)
    if not components:
        return components
    return [c for c in components if c["carbons"] >= _MINIMUM_TAIL_CARBONS]


def tail_length_asymmetry(smiles):
    """Longest tail minus shortest, in carbons; 0.0 for a single-tailed lipid.

    Class-neutral BY CONSTRUCTION, which is the point: PC 16:0/18:1 and PE 16:0/18:1
    carry the same asymmetry under different head groups, so this cannot act as the
    head-group label the whole-molecule descriptors turned out to be
    (files/results/lipid_coldsplit_architecture_direction.md section 7f). Not a nuisance
    quantity either -- acyl chain asymmetry, with polyunsaturation, is what lets brain
    phospholipid membranes vesiculate without leaking (Manni et al., eLife 2018).
    """
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
    """Double bonds lying IN the tails, not anywhere in the molecule.

    `unsaturation` counts every non-aromatic C=C the molecule has, so a head group's
    own unsaturation lands in it. This one cannot see the head at all.
    """
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    return float(sum(tail["double_bonds"] for tail in tails))


def tail_unsaturation_density(smiles):
    """Tail double bonds per tail carbon.

    A ratio for the same reason npr1/npr2 are ratios: dividing by the tails' own size
    removes the length scale, which is the part that still tracks class (classes differ
    systematically in typical chain length), and leaves how unsaturated those carbons
    are. Chain length and unsaturation move membrane thickness and fluidity through
    different mechanisms, so separating them is not only a statistical convenience
    (Kucerka et al. on sphingomyelin bilayers).
    """
    tails = _qualifying_tails(smiles)
    if not tails:
        return None
    carbons = sum(tail["carbons"] for tail in tails)
    if carbons == 0:
        return None
    return float(sum(tail["double_bonds"] for tail in tails) / carbons)


def tail_double_bond_position(smiles):
    """Carbons from the methyl end to the nearest double bond, minimum over tails.

    The (n-x) of lipid shorthand notation. Physically load-bearing rather than
    descriptive: the further a double bond sits from the tail terminus the weaker the
    inter-leaflet attraction, and the position sets domain registration
    (Zhang et al., JACS 2019). None for a fully saturated lipid -- the quantity does not
    exist there, the same way `precision` does not exist with no predicted positives.
    """
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
    """The tails alone, as one molecule, or None.

    Everything outside the qualifying components -- head group, backbone, linkers -- is
    dropped, so a descriptor computed on this cannot encode which head group the lipid
    had. The fragment is a bare hydrocarbon skeleton (the components are carbon-only by
    construction), which is exactly the intent: the same RDKit measure, restricted to
    the part of the molecule the cold split does NOT hold out.
    """
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
    """Carbons in the longest unbranched aliphatic run of a molecule.

    The lipid's tail is what a cavity has to accommodate lengthwise, so the measure is
    the longest path through non-aromatic, non-ring carbons -- head groups, rings and
    sugars drop out by construction. Returns None for anything RDKit cannot parse OR
    with no qualifying carbon at all (same convention _acyl_chain_component_lengths'
    other caller, acyl_chain_count, uses, for the two to agree on what "missing" means).
    """
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:  # None (unparseable) or [] (no qualifying carbon) alike
        return None
    return max(lengths)


def acyl_chain_count(smiles):
    """How many SEPARATE acyl tails a molecule has (>= _MINIMUM_TAIL_CARBONS carbons
    each), not just the longest one -- longest_acyl_chain reports one number for a
    diacylglycerol/phospholipid's two esterified tails and a single-tailed lyso lipid
    alike (verified: both report chain=18 for a same-length-tailed pair, see
    dataloader.pair_descriptors.DESCRIPTOR_CATALOG's "tail_count" entry). None for
    anything RDKit cannot parse OR with no qualifying carbon at all -- same convention
    longest_acyl_chain uses (see its own docstring).
    """
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


# Whole-molecule RDKit descriptors (the lipid-side analogues of the protein pocket's own
# family_neutral axes -- pocket_volume_per_sasa/apolar_sasa_share/hydropathy_rim/
# pocket_extent/aromatic_share): logp/tpsa are the two orthogonal hydrophobicity/
# polarity axes, molar_refractivity is the volume/polarizability analogue of
# pocket_volume_per_sasa, rotatable_bond_count is how much the lipid can conform to a
# cavity's shape (an absolute count, unlike rotatable_fraction above), and
# aromatic_ring_count/ring_count are the direct counterparts of the pocket's own
# aromatic_share. All purely topological (no conformer needed), same convention as
# unsaturation_count/hbond_capacity/heavy_atom_count above: None where RDKit cannot
# parse the candidate.
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


# --pair_descriptor_lipid_shape (LIPID_SHAPE_DESCRIPTOR_NAMES below): the one deliberate
# exception to this module's own "no 3D embedding" rule stated in its docstring above --
# ETKDG is indeed slow and fails unpredictably per-molecule, which is why it is opt-in,
# ensemble-averaged (not a single arbitrary conformer -- a flexible acyl tail has many
# near-isoenergetic shapes; one draw would teach the model the generator's seed, not the
# molecule), and wrapped in the same random-coords retry data/build_lipid_isomer_graphs.py
# uses for its own bond-length feature (which reuses generate_conformer_ensemble below,
# rather than duplicating this embed+optimize logic a second time).
CONFORMER_COUNT = 10
CONFORMER_SEED = 0xF00D


def generate_conformer_ensemble(mol, n_confs=CONFORMER_COUNT, seed=CONFORMER_SEED):
    """Explicit-H copy of `mol` with `n_confs` ETKDG+MMFF conformers.

    Returns (mol_h, conf_ids); mol_h's heavy-atom indices match `mol`'s (Chem.AddHs
    appends new atoms after the existing ones). Raises ValueError if ETKDG embedding
    fails even after a useRandomCoords retry -- callers should let that propagate
    rather than silently write a placeholder into the data.
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
    """(mol_h, conf_ids) for `smiles`, memoized by canonical SMILES.

    radius_of_gyration/asphericity/molecular_volume below each want their own mean
    over the SAME 10-conformer ensemble (CONFORMER_SEED is fixed, so it is a pure
    function of `smiles`) -- calling generate_conformer_ensemble independently per
    measure paid the ETKDG embed + MMFF optimize three times over for identical
    geometry. Measured as most of why data/build_pair_descriptor_cache.py's rebuild
    took ~20 minutes on this project's ~1300 unique candidates even after pinning
    OMP_NUM_THREADS=1 (which fixed a separate, smaller BLAS-thread-thrashing cost).
    None (not raised) for anything RDKit cannot parse, matching every other measure
    here's convention.
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
    """Same 10-conformer ensemble as _mean_over_conformers, reduced by MEDIAN instead
    -- npr1/npr2 below live in a bounded triangular shape space (Sauer & Schwarz,
    2003) where one poorly-optimized outlier conformer's ratio can sit far from the
    rest, and a median resists that the way a mean does not.
    """
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(numpy.median(values))


def npr1(smiles):
    """Median normalized principal moment ratio PMI1/PMI3 (Sauer & Schwarz, 2003)
    over the same 10-conformer ensemble radius_of_gyration/asphericity/
    molecular_volume already share -- how elongated the lipid's own 3D conformation
    is, the direct lipid-side counterpart of the pocket's own pocket_elongation
    (unlike chain/tail_count, which only stand in for shape via carbon-count
    topology)."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR1(mol_h, confId=conf_id)
    )


def npr2(smiles):
    """Median normalized principal moment ratio PMI2/PMI3 -- how flat/planar the
    lipid's own 3D conformation is, the counterpart of pocket_flatness."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR2(mol_h, confId=conf_id)
    )


LIPID_SHAPE_DESCRIPTOR_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "rotatable_fraction",
    "npr1", "npr2",
)

# The five _MEASURES entries whose per-candidate cost is a real 10-conformer
# ETKDG+MMFF embed, not microseconds -- dataloader/pair_descriptor_cache_reader.py's build
# routes exactly these through its process pool (_parallel_measures) rather than
# computing every measure serially; npr1/npr2 share the SAME cached ensemble
# radius_of_gyration/asphericity/molecular_volume already pay for, so adding them
# here costs no extra embedding, only two more cheap reductions over conformers
# already generated.
CONFORMER_MEASURE_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "npr1", "npr2",
)


# data/Lipid_Volumes.csv: per-species van-der-Waals volumes (Angstrom^3) from an
# external source, keyed here by the exact bound SMILES structure -- NOT by
# (LTPProtein, Lipid), even though the sheet is laid out per protein.
#
# CSV, not the original .xlsx the source arrived as: converted once by
# preprocessing/convert_lipid_volumes_xlsx.py (a stdlib-only zip/XML parse -- no
# spreadsheet library, see that script's own docstring), for two reasons a plain CSV
# does not have. First, `pandas.read_excel` needs `openpyxl` installed, which this
# .xlsx was the only thing in the whole project requiring -- a machine that runs
# everything else fine can be missing it, and then this one descriptor raises
# ImportError. Second, and the one that actually surfaced in practice:
# scripts/lib/cluster_sync_excludes.sh protects the whole data/ directory from being
# refreshed by an ordinary code sync, and only a short, explicit list of data/ files is
# carved out of that protection (Processed_*.csv, Tanimoto_compact*, ...) -- .xlsx was
# never one of them, so this file quietly never reached the cluster at all, surfacing
# as a bare FileNotFoundError the first time an arg file's descriptor set actually
# needed it. data/Lipid_Volumes.csv is now in that carve-out list; the .xlsx never
# needs to be synced again. Checked directly
# against this project's own candidate SMILES: every one of the sheet's 393 distinct
# isomeric-canonical structures maps to exactly one volume value (0 conflicts), so the
# same molecule gets the same number regardless of which protein's row it came from --
# the sheet's apparent per-protein structure is really "which isomer of a coarse name
# (e.g. PC(34:1)) that protein was observed bound to," not a per-protein volume. Under
# non-isomeric canonicalisation (isomeric=False, this project's default unless
# --lipid_isomers), 391 of those 393 stereo-distinct structures survive as distinct
# keys; the 2 that collapse (one is a pure sn-1/sn-2 relabelling of an identical
# structure) disagree by under 1.3% of the volume scale (max 8.07 Angstrom^3 apart, on
# a ~650-750 Angstrom^3 baseline) -- averaged rather than picked arbitrarily.
#
# Coverage is real but partial: the sheet's 393 structures are a subset of the ~1319
# distinct candidate structures across the WHOLE interaction table (positive and
# negative rows alike). A candidate resolves here, or does not, purely by which
# molecule it is -- every covered structure is a real identified ligand for SOME
# protein in this project's data, and negative rows draw candidates from the exact
# same pool positive rows do, so coverage does not track the Interaction label. Not
# yet in LIPID_DESCRIPTOR_NAMES (see CANDIDATE_LIPID_DESCRIPTOR_NAMES below) --
# whether the ~70% miss rate (as_arrays -> NaN, same convention as an RDKit parse
# failure) is safe to feed the model, and how those NaNs should be filled, has not
# been decided yet.
_LIPID_VOLUME_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "Lipid_Volumes.csv",
)


@functools.lru_cache(maxsize=1)
def _experimental_lipid_volume_table():
    """canonical SMILES (isomeric or not) -> mean measured volume (Angstrom^3).

    Built once from _LIPID_VOLUME_CSV and memoized; see the comment above this
    function's registration in _MEASURES for what "mean" absorbs (2 non-isomeric
    collisions only, out of 393 structures) and why the lookup key is the molecule,
    not the (protein, lipid) pair the sheet is filed under.
    """
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
    # Flat (collapsed, possibly-averaged) keys first, then exact isomeric keys written
    # on top -- the isomeric key for a structure with no stereocentre to strip is the
    # identical string as its flat key, and in that case both dicts agree anyway (an
    # isomeric group is never averaged, see the module comment above), so this ordering
    # never overwrites a real value with a different one.
    table = {key: sum(values) / len(values) for key, values in flat_groups.items()}
    table.update({key: sum(values) / len(values) for key, values in iso_groups.items()})
    return table


def experimental_lipid_volume(smiles):
    """Measured volume (Angstrom^3) for `smiles` from data/Lipid_Volumes.csv, or None
    if this exact structure was never one of the ligands the sheet identifies.

    `smiles` arrives already canonicalized by the caller (descriptor_values_by_row),
    the same way (isomeric or not) _experimental_lipid_volume_table's keys are built,
    so a direct dict lookup is enough here -- no re-canonicalization.
    """
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
    # Candidate head-group-neutral set (files/results/lipid_coldsplit_architecture_direction.md
    # section 7g). Cached and measurable, deliberately NOT added to
    # LIPID_DESCRIPTOR_NAMES: nothing model-facing changes until their eta^2 by
    # head-group class has actually been read.
    "tail_length_asymmetry": tail_length_asymmetry,
    "tail_length_mean": tail_length_mean,
    "tail_double_bonds": tail_double_bonds,
    "tail_unsaturation_density": tail_unsaturation_density,
    "tail_double_bond_position": tail_double_bond_position,
    "tail_logp": tail_logp,
    "tail_molar_refractivity": tail_molar_refractivity,
    "tail_heavy_atoms": tail_heavy_atoms,
    # data/Lipid_Volumes.csv lookup, not an RDKit formula -- see the comment above
    # its definition and its entry in LIPID_DESCRIPTOR_NAMES above for coverage.
    "experimental_lipid_volume": experimental_lipid_volume,
}

# Measured in section 7f/7g, not yet an input to any network. Kept next to _MEASURES so
# analysis/feature_identity_check.py --lipid_classes can name them without either duplicating
# the list or widening LIPID_DESCRIPTOR_NAMES, which would change what the model sees.
CANDIDATE_LIPID_DESCRIPTOR_NAMES = (
    "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
    "tail_unsaturation_density", "tail_double_bond_position",
    "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
)


def descriptor_values_by_row(csv, measure, isomeric=False, cache=None):
    """One of `_MEASURES`, per candidate, in the order the encoder numbers them.

    Same shape and the same per-field/per-SMILES caching discipline as
    pocket_lipid_compatibility.chain_lengths_by_row: entries are None where RDKit
    cannot parse the candidate, and a row with no usable candidate gets [None].
    `isomeric` MUST match chain_lengths_by_row's own -- it controls which candidates
    within a row collapse into one canonical-SMILES entry, so a mismatch would make
    this function's per-row list a different length than chain's, and
    Dataloader._ragged_tensor stacks columns on the assumption they agree.

    `cache`, when given, is a dataloader/pair_descriptor_cache_reader.py load result: a raw
    candidate present in its "raw_to_canonical" skips the canonicalising parse, and a
    canonical key present in its "values" skips `fn`. Same fallback discipline as
    chain_lengths_by_row -- an entry the cache has never seen is computed here exactly
    as without a cache.
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
                    # `measure in cached` first, not cached.get(measure, fn(key)): the
                    # latter's default is evaluated eagerly regardless of the lookup,
                    # which would call fn (an ETKDG embed, for the three lipid_shape
                    # measures) on every candidate even on a cache hit. A cache built
                    # with lipid_shape=False (dataloader/pair_descriptor_cache_reader.py)
                    # carries every OTHER measure for a SMILES it has seen, just not
                    # those three, so this still must fall back per-measure rather than
                    # KeyError.
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
    """`descriptor_values_by_row`'s (or chain_lengths_by_row's) output as NaN-arrays.

    Same conversion pocket_lipid_compatibility._candidate_arrays does for chain
    lengths; shared here since --pair_descriptors needs it for three more measures.
    """
    return [
        numpy.array(
            [numpy.nan if value is None else float(value) for value in row],
            dtype=float,
        )
        for row in per_row
    ]


# Tanford's formula for the maximum extended (all-trans, zig-zag) length of a
# saturated hydrocarbon chain (Tanford, C., "The Hydrophobic Effect", 1980; standard
# in lipid biophysics) -- L = 1.5 + 1.265*(n-1) angstrom for n carbons. Needed
# because `chain` (LIPID_DESCRIPTOR_NAMES, a plain carbon COUNT, unitless) is not
# comparable to `pocket_extent`/`depth_q10` (POCKET_DESCRIPTOR_NAMES, angstrom spans)
# without converting one to the other's units first -- see pair_descriptor_value's
# occupancy/chain_extent_gap, and the bug this fixes: comparing cbrt(heavy_atom_
# count) (a UNITLESS ~2.6-4.6 range) directly against pocket_extent (an ANGSTROM
# ~13.6-32.0 range) meant pocket_extent always won by a wide margin, occupancy's
# relu clipped every single row to exactly 0.0 (verified directly on this project's
# data: 100% of rows), and it silently carried zero information in every null-model
# run AND every trained --pair_descriptors run (dataloader/Dataloader.py uses
# the identical formula for the live training path -- fixed there too, in the same
# commit as this).
_CHAIN_BOND_PROJECTION_A = 1.265
_CHAIN_TERMINAL_A = 1.5


def chain_length_angstrom(chain):
    """`chain` (a carbon count) -> an estimated physical length in angstrom, via
    Tanford's extended-chain formula -- see the module-level comment above it.
    """
    return _CHAIN_TERMINAL_A + _CHAIN_BOND_PROJECTION_A * (chain - 1.0)


def pair_descriptor_value(name, lipid_values, protein_values):
    """One PAIR_DESCRIPTOR_NAMES entry, combined from a lipid's own descriptor dict
    (dataloader.chemistry_prior._lipid_descriptor_table's per-species entry -- every
    LIPID_DESCRIPTOR_NAMES key) and a protein's own (protein_descriptor_table's
    per-protein entry -- every PROTEIN_DESCRIPTOR_NAMES + PROTEIN_DERIVED_DESCRIPTOR_
    NAMES key). Both tables are computed unconditionally in full whenever a pair name
    is requested (see feature_similarity), so every key read here is always present
    regardless of which OTHER names the caller asked for.

    architecture/pair_descriptor_head.py's own module docstring names the two
    remaining pair phenomena the paper (Lipovsky et al., Nature 2025,
    s41586-025-10040-y) reports beyond occupancy -- "aromatic residues near double
    bonds" and "polar pocket surface meets an H-bonding headgroup" -- as things the
    self-attention token set is left to learn to combine on its own, never spelled
    out as an explicit formula anywhere (there is nothing FOR a null model, which has
    no attention weights, to read). aromatic_contact/hbond_match below are that
    formula -- the null-model-usable, unlearned version of what PairDescriptorHead's
    tokens ask the network to discover for itself.

        occupancy         : relu(chain_length_angstrom(chain) - pocket_extent) --
                             the acyl chain's own estimated physical length (see
                             chain_length_angstrom above) against the cavity's own
                             angstrom span, both now the same unit. Bound at 0: a
                             chain shorter than the pocket is not a clash, only a
                             chain LONGER than it is. NOT cbrt(heavy_atom_count)
                             (an earlier version of this formula, and still what
                             architecture/pair_descriptor_head.py's own occupancy
                             token computes) -- that compared a UNITLESS ~2.6-4.6
                             number directly against pocket_extent's ~13.6-32.0
                             angstrom range with no conversion between them, so
                             pocket_extent always won and relu clipped every single
                             row on this project's data to exactly 0.0, carrying
                             zero information (verified directly; see project memory
                             or dataloader/Dataloader.py's matching fix).
        chain_extent_gap   : pocket_extent - chain_length_angstrom(chain), signed (no
                              relu), same angstrom-length conversion as occupancy --
                              positive when the cavity runs longer than the chain,
                              negative when the chain overhangs it. (An earlier
                              version compared pocket_extent directly against the
                              raw carbon COUNT, unitless -- numerically similar
                              enough in raw magnitude on this data to not clip to a
                              constant the way occupancy's old formula did, but not
                              a principled unit match either; fixed the same way.)
        aromatic_contact   : aromatic_share * unsaturation -- an aromatic-rich pocket
                              paired with an unsaturated (kinked, pi-contact-prone)
                              chain scores higher than either alone; zero if the
                              pocket has no aromatics or the chain is fully saturated.
        hbond_match        : polar_share * hbond -- a polar pocket surface paired
                              with a headgroup that has H-bond donors/acceptors to
                              offer scores higher than either alone.
        volume_fit         : pocket_volume_per_sasa * heavy -- an alternative to
                              occupancy on the pocket's volume-to-surface ratio
                              (how enclosed/deep, not how long) against the same
                              ligand-bulk proxy.
        buriedness_match   : buriedness_q50 * heavy -- how enclosed the pocket's
                              lining residues are (median voromqa buriedness)
                              against ligand bulk: a buried, enclosed site may
                              specifically favour (or specifically exclude) a bulkier
                              ligand differently than an exposed one would.
        depth_bulk_match   : depth_q10 * heavy -- how deeply the pocket's shallowest
                              lining residues (10th percentile voromqa burial, a
                              LOCAL per-residue statistic, not a spatial reach the
                              way pocket_extent is) sit, against ligand bulk. NOT a
                              signed gap against chain length (an earlier version of
                              this entry, "depth_chain_gap" = depth_q10 - chain):
                              depth_q10 (~1.0-1.4 on this data) is not a length
                              comparable to a chain's own reach in the first place --
                              subtracting it from chain (~8-30) left depth_q10
                              contributing negligible variance regardless of any
                              rescaling, because the two were never the same kind of
                              quantity to begin with (chain_extent_gap already covers
                              the genuine reach-vs-length question, correctly, using
                              pocket_extent). Multiplication against heavy (like
                              buriedness_match, aromatic_contact, hbond_match) sidesteps
                              needing them to be the same unit at all -- a real
                              alternative to buriedness_match, not a duplicate: this is
                              the SHALLOWEST decile specifically, buriedness_match is
                              the pocket's own median.
        hydropathy_chain_match : hydropathy_core * chain -- core-residue
                              hydrophobicity (Kyte-Doolittle mean) against chain
                              length: a longer hydrophobic tail may specifically
                              favour a more hydrophobic core than a short one would.
        aromatic_contact_min : min(aromatic_share, unsaturation), BOTH STANDARDISED
                              first (always, independent of --zscore -- see
                              MIN_PAIR_DESCRIPTOR_NAMES) -- a bottleneck reading of
                              aromatic_contact: the pair scores no higher than its
                              weaker side, so an aromatic-rich pocket paired with a
                              fully saturated chain scores low regardless of how
                              aromatic-rich, unlike the product which a large enough
                              one side can still inflate.
        hbond_match_min    : min(polar_share, hbond), both standardised first
                              (same always-on standardisation as aromatic_contact_min)
                              -- the bottleneck reading of hbond_match.
        tail_elongation_fit : tail_count / max(pocket_elongation, 1.0) -- how many
                              SEPARATE acyl tails (dataloader.pair_descriptors.
                              acyl_chain_count) a pocket's own SHAPE, not its size,
                              can plausibly hold side by side. pocket_elongation is
                              axis0/axis1 of the cavity's atom cloud (tube vs bowl,
                              >= 1 by construction -- protein_graph_builder.
                              pocket_shape); a long narrow channel (high elongation)
                              has room lengthwise for one chain, not width for a
                              second one alongside it, while a rounder pocket
                              (elongation near 1) is the shape a multi-tailed lipid
                              (a diacylglycerol/phospholipid's two esterified tails,
                              a triacylglycerol's three) could plausibly sit packed
                              into side by side. A RATIO rather than a product
                              (like volume_fit/buriedness_match/depth_bulk_match/
                              hydropathy_chain_match) or a difference (like
                              occupancy/chain_extent_gap) -- a THIRD category of its
                              own -- because the relationship is "elongation divides
                              down how much capacity is usable", not "elongation and
                              tail_count both push the same way" (a product) or "the
                              two measure the same physical quantity" (a
                              difference); --zscore does not touch it for the same
                              reason it does not touch occupancy/chain_extent_gap --
                              standardising elongation first could make the
                              denominator cross zero or go negative, which the ratio
                              has no sensible reading of. max(..., 1.0) guards the
                              one degenerate case pocket_shape's own docstring
                              already flags: fewer than 4 pocket atoms returns
                              elongation = 0.0 rather than a real ratio, which would
                              otherwise divide UP instead of down.

        hydropathy_rim_match : hydropathy_rim * hbond -- mouth/rim hydropathy
                              (Kyte-Doolittle mean over the pocket's SHALLOW half
                              only, distinct from hydropathy_core/hydropathy_chain_
                              match above, which read the DEEP half) against the
                              headgroup's own H-bond donor/acceptor count. Motivated
                              by files/literature/protein_lipid_binding_family_literature.md:
                              IP_trans/START/OSBP's documented specificity mechanism
                              is recognising a polar/charged headgroup AT THE POCKET
                              ENTRANCE (phosphoinositide, choline, PI(4)P respectively)
                              -- a mouth-chemistry-vs-headgroup match hbond_match
                              (which reads whole-pocket polar_share, core+rim
                              undivided) cannot express on its own.
        elongation_shape_match : pocket_elongation * lipid npr1 -- cavity tube-vs-
                              bowl ratio (protein_graph_builder.pocket_shape) against
                              the ligand's own PMI1/PMI3 elongation (npr1, dataloader.
                              pair_descriptors.npr1) -- both are the SAME physical
                              axis (elongated vs compact 3D shape), one for the
                              cavity, one for the ligand. Motivated by the OSBP/ORP
                              literature (files/literature/protein_lipid_binding_family_
                              literature.md): that family's documented specificity
                              mechanism is a hydrophobic TUNNEL whose usable diameter/
                              length, not chemistry, decides whether a given ligand's
                              rigid, elongated ring system fits -- a shape-vs-shape
                              term neither pocket_elongation nor npr1 alone expresses.
        flatness_shape_match : pocket_flatness * lipid npr2 -- cavity slit-vs-tube
                              ratio against the ligand's own PMI2/PMI3 flatness
                              (npr2) -- the second of the same pair-of-shape-axes
                              idea as elongation_shape_match, covering the OTHER
                              cavity/ligand shape axis (protein_graph_builder.
                              pocket_shape's pocket_flatness is a distinct ratio from
                              pocket_elongation, not the same number read twice).

    None of these fourteen needs a bound pose (which residue contacts which double
    bond, which residue H-bonds which headgroup atom) -- same discipline as the rest
    of this module: pocket-wide chemistry shares and lipid-wide scalars, not a
    specific residue-atom contact this project has no docking pipeline to place.
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
# "chain" is longest_acyl_chain, which _MEASURES does not carry (the table writes it as
# its own column) -- same exception dataloader/pair_descriptor_cache_reader.py's
# _measure_functions makes, and for the same reason.
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
    """Replace one column of one isomeric half of a table, leaving everything else.

    `new_values` is {key tuple: value}, keyed by `key_columns`. Rows of the OTHER
    isomeric variant keep the value they already had, rows of this one get the new
    number, and every other column is read back and written out untouched -- a column
    write must never be a silent whole-table rebuild.
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
    """Compute one lipid measure over every candidate SMILES and write its column.

    Reads the interaction table for the candidate set and the existing
    data/lipid_descriptors.csv for the rows to fill -- this writes a column, it does not
    create the table. Build the table first (data/build_pair_descriptor_cache.py) if it
    is missing: that path owns the parallel/incremental machinery a from-scratch build
    needs, and duplicating it here would be a second, divergent builder.
    """
    from dataloader.dataset_source import interaction_csv_path
    from dataloader.pair_descriptor_cache_reader import lipid_descriptors_csv_path

    table_path = lipid_descriptors_csv_path(data_dir)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            "`python3 data/build_pair_descriptor_cache.py` before writing one column"
        )

    csv = pandas.read_csv(interaction_csv_path(str(data_dir) + os.sep))
    function = lipid_measure_function(name)
    values = {}
    for key in _canonical_candidate_keys(csv, isomeric):
        values[(key, bool(isomeric))] = function(key)

    written = _write_column(
        table_path, values, name, ("smiles", "isomeric"), isomeric
    )
    # No manifest write: the manifest carries the source table's size/mtime and
    # raw_to_canonical, neither of which a column recompute changes. The numbers in the
    # CSV are the whole of what makes this column valid.
    return table_path, written


def _canonical_candidate_keys(csv, isomeric):
    """Every distinct canonical candidate SMILES in the interaction table, in order.

    Same canonicalisation (and the same skip of anything RDKit cannot parse) the
    builder uses, so a key written here matches the row the table already has.
    """
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
    """Compute one pair descriptor from the two side tables and write its column.

    Cheap arithmetic, never RDKit: both inputs are read from data/lipid_descriptors.csv
    and data/protein_descriptors.csv, the same division build_pair_value_cache uses.
    """
    from dataloader.pair_descriptor_cache_reader import (
        load_pair_descriptor_cache,
        pair_descriptors_csv_path,
    )

    table_path = pair_descriptors_csv_path(data_dir)
    if not table_path.exists():
        raise SystemExit(
            f"{table_path} does not exist yet -- build it once with "
            "`dataloader.cache_builders.pair_descriptor_cache_writer.build_pair_value_cache` "
            "before writing one column"
        )
    lipid_cache = load_pair_descriptor_cache(Path(data_dir).resolve(), isomeric)
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
        # The whole positional vector comes out of one pass over a protein's residue
        # table, so one name cannot be computed alone here -- the table is rebuilt and
        # this name is one of its columns.
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
