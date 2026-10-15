#!/usr/bin/env python3
"""Generate per-residue ESM-IF1 encoder embeddings from backbone coordinates.

Use esm_if1_gvp4_t16_142M_UR50. Check the residue count against coarse_graph_nodes.csv.
Write data/embedding_ESMIF1/<stem>_ESMIF1.pkl for --esmif1_replace_esm3.

The environment needs fair-esm, biotite < 1.0 and torch_scatter. The project setup
also pins scipy < 1.14. See the environment configuration before installing.

    <venv>/bin/python preprocessing/embed_protein_esmif1.py
"""

import argparse
import pickle
from pathlib import Path

import pandas
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "esm3_input"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "embedding_ESMIF1"
EMBEDDING_DIM = 512


def graph_node_count(stem):
    node_path = PROJECT_ROOT / "data" / "graphs" / stem / "coarse_graph_nodes.csv"
    if not node_path.is_file():
        raise FileNotFoundError(f"Protein graph nodes not found: {node_path}")
    return len(pandas.read_csv(node_path))


def structure_chain(pdb_path):
    """The single chain letter present in the file."""
    letters = sorted({
        line[21]
        for line in open(pdb_path)
        if line.startswith("ATOM") and line[21] != " "
    })
    if len(letters) != 1:
        raise ValueError(
            f"{pdb_path.stem}: expected one chain, found {letters}; the graph node "
            "order assumes a single chain"
        )
    return letters[0]


def embed_one(pdb_path, output_dir, model, alphabet):
    from esm.inverse_folding.util import load_coords, get_encoder_output

    coords, _ = load_coords(str(pdb_path), structure_chain(pdb_path))
    with torch.inference_mode():
        representation = get_encoder_output(model, alphabet, coords).float().cpu()

    expected_rows = graph_node_count(pdb_path.stem)
    if tuple(representation.shape) != (expected_rows, EMBEDDING_DIM):
        raise ValueError(
            f"{pdb_path.stem}: ESM-IF1 produced {tuple(representation.shape)}, "
            f"expected ({expected_rows}, {EMBEDDING_DIM}); the structure and "
            "coarse_graph_nodes.csv disagree about which residues exist"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdb_path.stem}_ESMIF1.pkl"
    with open(output_path, "wb") as handle:
        pickle.dump(representation, handle)
    print(f"{pdb_path.stem}: {tuple(representation.shape)} -> {output_path}")


def main():
    import esm

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdbs", nargs="*", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    pdbs = args.pdbs or sorted(DEFAULT_INPUT_DIR.glob("*.pdb"))
    if not pdbs:
        raise FileNotFoundError(f"No PDB inputs found in {DEFAULT_INPUT_DIR}")

    model, alphabet = esm.pretrained.esm_if1_gvp4_t16_142M_UR50()
    model.eval()
    for pdb_path in pdbs:
        embed_one(pdb_path, args.output_dir, model, alphabet)


if __name__ == "__main__":
    main()
