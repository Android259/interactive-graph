#!/usr/bin/env python3
"""How much of the MolFormer lipid embedding is the lipid's head-group class.

architecture/lipid_encoder.py's non-graph path feeds MolFormer's per-token SMILES
embedding (preprocessing/embed_isomeric_smiles_molformer.py, IBM's pretrained
transformer, dataloader/lipid_embedding_store.py's cached table) straight into this
project's own self-attention (--lipid_self_attention). This is the lipid-side
analogue of preprocessing/pocket_descriptor_identity_check.py's question on the
protein side ("is this feature already identity in disguise"), never previously asked
of the learned lipid embedding -- analysis/lipid_descriptor_class_identity.py only
covers the 13 hand-built lipid descriptors, not this.

Representation used: one 768-dim vector per lipid SPECIES (FullIdentityOfLipid), mean-
pooled over the MolFormer token dimension, then averaged over that species' candidate
structures (the sn-positional/double-bond isomers one measured species can resolve to,
dataloader/pocket_lipid_compatibility.candidates_for_row) -- the same candidate-
averaging analysis/lipid_descriptor_class_identity.py's candidate_matrix already uses
for the 13 hand-built descriptors, and the same "one vector per entity, spread
resolved by averaging" idea preprocessing/pocket_descriptor_identity_check.py's
mean_plm_embedding applies on the protein side (there: average over residues; here:
average over tokens, then over candidates). Embeddings come from the deterministic,
non-isomeric table (data/lipid_SMILES_embedding_deterministic.pkl / its .tensors.pt
mmap store) -- the one the default (--lipid_isomers unset) training config actually
reads, and the one with full candidate coverage (dataloader/Dataloader.py's own
comment: 1226 entries, every candidate of every row).

Three numbers, read against a chance floor exactly like the protein-side check:

1. eta^2_joint: share of the whole standardised 768-dim vector's variance that lies
   between lipid classes rather than within them (analysis/feature_identity_check.
   eta_squared_joint) -- near 1, the embedding says nothing but class; near the
   arithmetic floor (k-1)/(n-1), class does not determine it.
2. Mantel test: Spearman correlation between the embedding's own pairwise-distance
   matrix and a class-identity distance matrix (one-hot class labels, standardised,
   pair_distances -- preprocessing/pocket_descriptor_identity_check.py's own mantel/
   pair_distances/standardise, reused unchanged), with a label-permutation p. Unlike
   the protein-side check, there is no separate continuous "pure identity" embedding
   to correlate against -- for a lipid species, identity to the class axis is exactly
   the class label itself, so one-hot(class) stands in for what mean-ESM3 embedding
   stood in for on the protein side.
3. Nearest-other-species-shares-class rate (analysis/feature_identity_check.
   nearest_neighbour_identity_rate), against the same-sized random-draw chance rate
   it reports alongside.

Reads only: loads the cached embedding table and the interaction CSV, trains nothing,
writes nothing.

Usage:
    scripts/env.sh python3 preprocessing/lipid_embedding_identity_check.py
"""
import sys
from pathlib import Path

import numpy
import pandas
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.feature_identity_check import (  # noqa: E402
    eta_squared_joint, group_floor, nearest_neighbour_identity_rate, species_class_map,
)
from dataloader.chemistry_prior import _standardised_similarity  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_embedding_store import load_lipid_embedding_store  # noqa: E402
from dataloader.pocket_lipid_compatibility import candidates_for_row  # noqa: E402
from preprocessing.pocket_descriptor_identity_check import (  # noqa: E402
    mantel, pair_distances, standardise,
)
from rdkit import Chem  # noqa: E402

EMBEDDING_FILE = "lipid_SMILES_embedding_deterministic.pkl"


def canonical_key(smiles):
    """Same recipe dataloader/lipid_graph_builder.py's _canonical_embedding_key uses
    under the default (--lipid_isomers unset) config: isomericSmiles=False, so the
    key matches what the deterministic embedding table was built and is looked up
    with.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False)


def species_embeddings(csv, smiles_encoding):
    """{species: 768-dim vector}, mean-pooled over tokens then over candidates.

    One row per distinct FullIdentityOfLipid, its FIRST occurrence's candidate list
    -- same convention analysis/lipid_descriptor_class_identity.py's candidate_matrix
    uses (the candidate SMILES field is a property of the species' identity, constant
    across the rows that share it).
    """
    vectors, missing_species, missing_keys = {}, [], set()
    seen = set()
    for _, row in csv.iterrows():
        species = row["FullIdentityOfLipid"]
        if species in seen:
            continue
        seen.add(species)
        pooled = []
        for candidate in candidates_for_row(row):
            key = canonical_key(candidate)
            if key is None:
                continue
            encoding = smiles_encoding.get(key)
            if encoding is None:
                missing_keys.add(key)
                continue
            pooled.append(torch.as_tensor(encoding).squeeze(0).mean(dim=0).numpy())
        if pooled:
            vectors[species] = numpy.mean(numpy.stack(pooled), axis=0)
        else:
            missing_species.append(species)
    return vectors, missing_species, missing_keys


def main():
    data_dir = PROJECT_ROOT / "data"
    csv = pandas.read_csv(interaction_csv_path(str(data_dir) + "/"))

    smiles_encoding = load_lipid_embedding_store(data_dir, EMBEDDING_FILE)
    if smiles_encoding is None:
        import pickle
        with open(data_dir / EMBEDDING_FILE, "rb") as handle:
            smiles_encoding = pickle.load(handle)

    species_class = species_class_map(csv)
    vectors, missing_species, missing_keys = species_embeddings(csv, smiles_encoding)
    if missing_species or missing_keys:
        print(f"WARNING: {len(missing_species)} species with no resolvable candidate "
              f"embedding, {len(missing_keys)} distinct missing keys -- excluded below\n")

    species = sorted(vectors)
    matrix = numpy.stack([vectors[name] for name in species])
    labels = numpy.array([species_class[name] for name in species])

    print(f"{len(species)} lipid species, {len(pandas.unique(labels))} head-group classes\n")

    floor = group_floor(labels)
    joint = eta_squared_joint(matrix, labels)
    print("1. eta^2_joint (whole 768-dim standardised vector vs lipid class)")
    print(f"   joint eta^2 = {joint:.3f}   arithmetic floor (k-1)/(n-1) = {floor:.3f}\n")

    print("2. Mantel: embedding distance vs one-hot(class) distance")
    class_one_hot = pandas.get_dummies(labels).to_numpy(dtype=float)
    rho, p = mantel(standardise(matrix), standardise(class_one_hot))
    print(f"   rho = {rho:.3f}   p = {p:.3f}\n")

    print("3. Nearest other species shares the class")
    similarity = _standardised_similarity(matrix)
    rate, chance, nn_p = nearest_neighbour_identity_rate(similarity, labels)
    print(f"   rate = {rate:.3f}   chance = {chance:.3f}   p = {nn_p:.3f}")


if __name__ == "__main__":
    main()
