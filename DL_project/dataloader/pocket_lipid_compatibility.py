"""How well a pocket's own dimensions match a candidate lipid's own dimensions.

Every descriptor in POCKET_DESCRIPTOR_NAMES describes the protein alone, and every one
of them turns out to be a family fingerprint to some degree (η² 0.28-0.85,
preprocessing/pocket_descriptor_identity_check.py) -- on 35 proteins / 9 families,
almost any sufficiently informative protein-only summary is. A quantity that depends on
BOTH the protein and the candidate lipid together cannot collapse to a protein label the
same way, because it is not a function of the protein alone.

The one built here: pocket_extent(p) - chain_length(l), where pocket_extent is the same
PCA-axis span POCKET_DESCRIPTOR_NAMES already computes (dataloader/protein_graph_builder)
and chain_length is the longest unbranched aliphatic run of the candidate lipid --
literally "does the cavity reach as far as the tail is long". Documented in
files/pocket_lipid_compatibility.md, which also carries the measurement of whether it
adds anything over files/interaction_signal_plan.md's chemistry prior.

Two independent consumers of the raw value, wired in New_dataloader:
  --pocket_compat_prior : frozen, calibrated, added to the logit outside the network
                          (same mechanism as --chem_prior, and jointly calibrated with
                          it when both are on -- see dataloader/chemistry_prior.py).
  --compatibility_input : standardised (not calibrated) and concatenated into the
                          fused representation, so the network's own weights decide
                          how to use it.
Neither requires the other; both read the same raw_compatibility() output.
"""
import os

import numpy
import pandas
from rdkit import Chem

from dataloader.protein_graph_builder import pocket_atom_coordinates, pocket_shape

# Sentinels this project's SMILES columns use for "no structure recorded", matching
# analysis/pocket_shape_vs_binding.py, which imports EMPTY from here rather than
# keeping its own copy.
EMPTY = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def smiles_for_row(row):
    """The first usable SMILES string for one interaction-table row, or None.

    SmileGlobal first, SmileFragment as fallback -- the same preference order
    chain_length_per_protein used before this was factored out. A cell can carry
    several candidates separated by ';'; only the first is used, matching how the
    rest of the project treats multi-candidate cells (e.g. species_similarity's
    per-structure max, not an average over candidates).
    """
    for column in ("SmileGlobal", "SmileFragment"):
        text = str(row.get(column, "")).strip()
        if text in EMPTY:
            continue
        return text.split(";")[0].strip()
    return None


def longest_acyl_chain(smiles):
    """Carbons in the longest unbranched aliphatic run of a molecule.

    The lipid's tail is what a cavity has to accommodate lengthwise, so the measure is
    the longest path through non-aromatic, non-ring carbons -- head groups, rings and
    sugars drop out by construction. Returns None for anything RDKit cannot parse.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    carbons = [
        atom.GetIdx() for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic() and not atom.IsInRing()
    ]
    if not carbons:
        return None
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

    longest = 0
    unvisited = set(neighbours)
    while unvisited:
        start = next(iter(unvisited))
        end, _, component = farthest(start)
        _, distance, _ = farthest(end)
        longest = max(longest, distance + 1)
        unvisited -= component
    return longest


def chain_length_by_species(csv):
    """Longest acyl chain per distinct FullIdentityOfLipid, computed once each.

    A species can appear hundreds of times (once per protein it was screened against);
    computing longest_acyl_chain per ROW would redo the same RDKit parse and BFS that
    many times. None for a species RDKit cannot parse or that carries no qualifying
    carbon at all -- the caller decides how to fill that in (see raw_compatibility).
    """
    lengths = {}
    for species, rows in csv.groupby("FullIdentityOfLipid"):
        smiles = None
        for _, row in rows.iterrows():
            smiles = smiles_for_row(row)
            if smiles is not None:
                break
        lengths[species] = longest_acyl_chain(smiles) if smiles is not None else None
    return lengths


def pocket_extent_by_protein(root_dir, protein_names):
    """pocket_extent(p) for each named protein, reusing the model-facing geometry.

    Same pocket_atom_coordinates + pocket_shape that POCKET_DESCRIPTOR_NAMES' own
    pocket_extent entry uses -- this is that entry, not a second measurement of it.
    """
    extents = {}
    for protein in protein_names:
        path = os.path.join(root_dir, "graphs", protein, "pocketness.pdb")
        extents[protein] = pocket_shape(pocket_atom_coordinates(path))[0]
    return extents


def raw_compatibility(csv, root_dir):
    """pocket_extent(protein) - chain_length(lipid) for every row of `csv`.

    Both terms are pure geometry/chemistry -- neither reads Interaction -- so unlike
    dataloader/chemistry_prior.py's leave-one-out score, there is no label to leak and
    no special handling is needed for rows that are themselves part of a reference set.

    Returns (values, missing_chain_mask): a lipid whose SMILES RDKit cannot parse, or
    that has no non-aromatic non-ring carbon at all, gets NaN rather than a silently
    wrong number; the mask says which rows those are so the caller can impute
    explicitly (raw_compatibility itself has no notion of "train", so it cannot decide
    what a safe fill value is) and log how many were affected rather than losing them
    quietly.
    """
    lengths = chain_length_by_species(csv)
    protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
    extents = pocket_extent_by_protein(root_dir, protein_names)

    chain = csv["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
    extent = csv["LTPProtein"].map(extents).to_numpy(dtype=float)
    missing = numpy.isnan(chain)
    values = extent - chain
    return values, missing
