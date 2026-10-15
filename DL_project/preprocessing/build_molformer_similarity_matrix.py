#!/usr/bin/env python3
"""Build a lipid-species similarity matrix from cached MoLFormer embeddings.

Use dataloader.chemistry_prior.species_embeddings to pool token embeddings and
candidate structures per species. Standardise the feature columns and compute
similarity as 1 / (1 + Euclidean distance). Embeddings are not recomputed.

Read the interaction table and data/lipid_SMILES_embedding_deterministic.pkl
(or its tensor store). Write:
    data/molformer_species_similarity_matrix.npy
    data/molformer_species_index.json

The index lists species in matrix order. chemistry_prior and the k-NN baseline
read these files.

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
from dataloader.tensors_reading.lipid_embedding_tensors_reader import load_lipid_embedding_store  # noqa: E402
from dataloader.chemistry_prior import (  # noqa: E402
    MOLFORMER_EMBEDDING_FILE as EMBEDDING_FILE, species_embeddings,
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
