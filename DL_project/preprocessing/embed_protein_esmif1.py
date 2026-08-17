#!/usr/bin/env python3
"""Generate frozen per-residue ESM-IF1 encoder representations.

ESM-IF1 (esm_if1_gvp4_t16_142M_UR50, ~142M parameters) is an inverse-folding model:
it reads backbone coordinates and predicts which residue belongs at each position. The
encoder output taken here is therefore a description of the local geometry -- "what
kind of site is this" -- with no sequence-family component, which is the property the
cold-family split rewards and ESM3 lacks.

Needs its own environment: fair-esm requires biotite < 1.0 (``filter_backbone`` was
removed in 1.0) and torch_scatter, and biotite < 1.0 pins numpy < 2, which in turn
needs scipy < 1.14. A venv with --system-site-packages plus
``fair-esm 'biotite<1.0' 'scipy<1.14' torch_scatter`` satisfies all of it; the system
interpreter is left alone.

    <venv>/bin/python preprocessing/embed_protein_esmif1.py

Writes data/embedding_ESMIF1/<stem>_ESMIF1.pkl, consumed by --esmif1_replace_esm3.

Alignment is 1:1 here, unlike ProteinMPNN: biotite's load_coords keeps only residues
that exist, so no gap padding has to be undone. It is still checked against
coarse_graph_nodes.csv, because a silent shift would be invisible downstream.
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
