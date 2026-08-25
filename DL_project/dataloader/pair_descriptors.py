"""Cheap, docking-free descriptors for --pair_descriptors (architecture/pair_descriptor_head.py).

Motivated by Lipovsky et al., "Systematic analyses of lipid mobilization by human lipid
transfer proteins" (Nature 2025, s41586-025-10040-y), whose measured LTP-lipid complexes
this project's interaction table draws on. That paper reports acyl-chain-length and
unsaturation preferences per LTP, aromatic (Phe) clusters contacting acyl double bonds in
MD-simulated poses, headgroup hydrogen bonding, and a pocket-occupancy ("buffer zone")
ratio between bound-ligand and cavity volume.

Two of those need a bound POSE (which residue sits near which double bond, which residue
H-bonds which headgroup atom) -- this project has no docking pipeline and the paper's own
solved poses cover only the ~110 purified complexes, not the ~9905-row candidate grid this
model scores. Building them here would mean fabricating a pose for every candidate, which
is worse than not having the feature. What IS computed here, per row, from 2D structure
alone (same discipline as pocket_lipid_compatibility.longest_acyl_chain -- no 3D
embedding, which is slow and fails unpredictably across ~10k rows of stereo-ambiguous
candidates):

    unsaturation_count(l)  : non-aromatic C=C bonds -- the paper's chain-saturation axis.
    hbond_capacity(l)      : RDKit NumHDonors + NumHAcceptors -- a headgroup H-bonding
                              PROXY, not the pose-specific pattern the paper measured.
    heavy_atom_count(l)    : a cheap, robust size proxy standing in for the paper's
                              bound-ligand volume (no 3D embedding).

architecture/pair_descriptor_head.py combines these with the pocket's own aromatic_share
and (1 - apolar_sasa_share) (POCKET_DESCRIPTOR_NAMES, already scale-free) as multiplicative
pair terms -- proxies for "aromatic residues near double bonds" and "polar pocket surface
meets an H-bonding headgroup" that need no pose because they use pocket-wide chemistry
shares instead of a specific residue-double-bond contact. New_dataloader.py separately
builds the occupancy term (heavy_atom_count vs the SAME coarsened pocket_extent
--compatibility_split_input's "clash" term uses) with pocket_lipid_compatibility's own
coarsen_to_levels, so a held-out protein's raw cavity size still cannot leak through it
(files/compat_input_audit.md).
"""
import numpy

from rdkit import Chem
from rdkit.Chem import Descriptors

from dataloader.pocket_lipid_compatibility import candidates_for_row


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


_MEASURES = {
    "unsaturation": unsaturation_count,
    "hbond": hbond_capacity,
    "heavy_atoms": heavy_atom_count,
}


def descriptor_values_by_row(csv, measure, isomeric=False):
    """One of `_MEASURES`, per candidate, in the order the encoder numbers them.

    Same shape and the same per-field/per-SMILES caching discipline as
    pocket_lipid_compatibility.chain_lengths_by_row: entries are None where RDKit
    cannot parse the candidate, and a row with no usable candidate gets [None].
    `isomeric` MUST match chain_lengths_by_row's own -- it controls which candidates
    within a row collapse into one canonical-SMILES entry, so a mismatch would make
    this function's per-row list a different length than chain's, and
    New_dataloader._ragged_tensor stacks columns on the assumption they agree.
    """
    fn = _MEASURES[measure]
    by_field = {}
    by_smiles = {}
    per_row = []
    for _, row in csv.iterrows():
        field = tuple(candidates_for_row(row))
        values = by_field.get(field)
        if values is None:
            values = []
            seen = set()
            for raw in field:
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
