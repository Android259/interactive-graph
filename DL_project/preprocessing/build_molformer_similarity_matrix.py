#!/usr/bin/env python3
"""Build a species x species similarity matrix from the cached MolFormer lipid
embedding, for use as a third `--features` option in analysis/null_model.py
(alongside `tanimoto` and named hand-built descriptors).

Reuses preprocessing/lipid_embedding_identity_check.py's own embedding-loading and
per-species mean-pooling (`species_embeddings`: mean over MolFormer's token dimension,
then over a species' candidate isomer structures) so this is the SAME 768-dim
per-species vector that session already measured to be ~75% lipid-class variance
(files/descriptors_baseline_leak_confirmed.md) -- this script only turns that vector
into a pairwise similarity matrix, it does not recompute or re-derive the embedding.

Similarity transform: dataloader.chemistry_prior._standardised_similarity (standardise
each of the 768 columns, then 1/(1+euclidean distance)) -- the same transform
feature_similarity() already applies to every named hand-built descriptor set, so a
molformer null model is directly comparable in kind (not just in AUC) to a lipid4 null
model: same k-NN scoring code (dataloader.chemistry_prior.null_scores), same [0, 1]-ish
range, different input vector. This is deliberately NOT the Tanimoto matrix's own
format (uint8/255, per-STRUCTURE not per-species, needs a separate structure_index) --
species_similarity()'s compact-structure format exists to save space for Morgan
fingerprints computed per isomer candidate; MolFormer's embedding is already reduced to
one vector per species by species_embeddings(), so there is nothing to compact.

Output (consumed by dataloader.chemistry_prior.molformer_species_similarity, which
analysis/null_model.py's --features=molformer branch calls):
    data/molformer_species_similarity_matrix.npy  -- float32 (n_species, n_species)
    data/molformer_species_index.json             -- [species name, ...] giving the
                                                       row/column order of the matrix

Reads only from data/lipid_SMILES_embedding_deterministic.pkl (or its mmap .tensors.pt
store) and the interaction CSV; writes only the two files above.

    scripts/env.sh python3 preprocessing/build_molformer_similarity_matrix.py
"""
import json
import sys
from pathlib import Path

import numpy
import pandas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.chemistry_prior import _standardised_similarity  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_embedding_store import load_lipid_embedding_store  # noqa: E402
from preprocessing.lipid_embedding_identity_check import (  # noqa: E402
    EMBEDDING_FILE, species_embeddings,
)

SIMILARITY_PATH = "molformer_species_similarity_matrix.npy"
INDEX_PATH = "molformer_species_index.json"


def build(data_dir):
    csv = pandas.read_csv(interaction_csv_path(str(data_dir) + "/"))

    smiles_encoding = load_lipid_embedding_store(data_dir, EMBEDDING_FILE)
    if smiles_encoding is None:
        import pickle
        with open(data_dir / EMBEDDING_FILE, "rb") as handle:
            smiles_encoding = pickle.load(handle)

    vectors, missing_species, missing_keys = species_embeddings(csv, smiles_encoding)
    if missing_species or missing_keys:
        print(f"WARNING: {len(missing_species)} species with no resolvable candidate "
              f"embedding, {len(missing_keys)} distinct missing keys -- excluded\n")

    species = sorted(vectors)
    matrix = numpy.stack([vectors[name] for name in species]).astype(numpy.float64)
    similarity = _standardised_similarity(matrix)

    numpy.save(data_dir / SIMILARITY_PATH, similarity)
    (data_dir / INDEX_PATH).write_text(json.dumps(species))

    print(f"{len(species)} species, similarity matrix {similarity.shape}, "
          f"range [{similarity.min():.3f}, {similarity.max():.3f}]")
    print(f"wrote {data_dir / SIMILARITY_PATH}")
    print(f"wrote {data_dir / INDEX_PATH}")


if __name__ == "__main__":
    build(PROJECT_ROOT / "data")
