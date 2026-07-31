#!/usr/bin/env python3
"""Generate frozen per-residue RNA-BAnG protein representations.

The official repository and ICML checkpoint are kept in external/RNA-BAnG.
Run this script from the RNA-BAnG conda environment:

    conda env create -f external/RNA-BAnG/environment.yml
    conda run -n rnabang python preprocessing/embed_protein_rnabang.py

By default every PDB in data/esm3_input is encoded and written as
data/embedding_RNABANG/<stem>_RNABANG.pkl. These PDBs were already normalized
against coarse_graph_nodes.csv, which is the alignment required by the loader.
No RNA is supplied: MainNetwork.forward_aa() stops after the pretrained protein
embedder and all ten protein self/geometric-attention blocks.
"""

import argparse
import pickle
import sys
import tempfile
from pathlib import Path

import gemmi
import pandas
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RNABANG_ROOT = PROJECT_ROOT / "external" / "RNA-BAnG"
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "esm3_input"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "embedding_RNABANG"
DEFAULT_CHECKPOINT = RNABANG_ROOT / "ckpt" / "icml.pth"


def load_model(checkpoint_path, device):
    if not RNABANG_ROOT.is_dir():
        raise FileNotFoundError(
            f"Official RNA-BAnG checkout not found at {RNABANG_ROOT}"
        )
    sys.path.insert(0, str(RNABANG_ROOT))

    from data import cif_processor, tokenizer
    from experiments import utils as experiment_utils
    from model import main_network

    checkpoint = experiment_utils.read_pkl(
        str(checkpoint_path), use_torch=True, map_location=device
    )
    model_conf = checkpoint["conf"].model
    tokenizer_conf = checkpoint["conf"].tokenizer
    tokenizer_conf.vocab_path = str(RNABANG_ROOT / "data" / "tokenizer.json")
    tok = tokenizer.Tokenizer(tokenizer_conf)
    processor = cif_processor.Processor(tok)
    model = main_network.MainNetwork(model_conf, tok)
    state = {
        key.replace("module.", ""): value
        for key, value in checkpoint["model"].items()
    }
    model.load_state_dict(state)
    model.to(device).eval()
    return model, processor, int(model_conf.c_s)


def graph_node_count(stem):
    node_path = PROJECT_ROOT / "data" / "graphs" / stem / "coarse_graph_nodes.csv"
    if not node_path.is_file():
        raise FileNotFoundError(f"Protein graph nodes not found: {node_path}")
    return len(pandas.read_csv(node_path))


def embed_one(pdb_path, output_dir, model, processor, embedding_dim, device):
    # The project PDBs have already had alternate conformations resolved, but some
    # experimental structures retain the selected conformer's fractional occupancy.
    # RNA-BAnG rejects any backbone/CB occupancy below 1 even when no altloc remains.
    # Normalize occupancy only in a disposable inference copy; coordinates, residue
    # order and the source PDB stay unchanged.
    structure = gemmi.read_structure(str(pdb_path))
    structure.remove_alternative_conformations()
    first_model = structure[0]
    chain_names = [chain.name for chain in first_model]
    if "A" not in chain_names:
        if len(chain_names) != 1:
            raise ValueError(
                f"{pdb_path.stem}: RNA-BAnG requires chain A, but the structure "
                f"contains {chain_names}"
            )
        first_model[0].name = "A"
    for model_part in structure:
        for chain in model_part:
            for residue in chain:
                for atom in residue:
                    atom.occ = 1.0
    with tempfile.TemporaryDirectory(prefix="rnabang_") as temp_dir:
        normalized_path = Path(temp_dir) / pdb_path.name
        structure.write_pdb(str(normalized_path))
        features = processor.process_cif(str(normalized_path))
    features = {
        key: value.to(device) if hasattr(value, "to") else value
        for key, value in features.items()
    }
    with torch.inference_mode():
        representation = model.forward_aa(features).squeeze(0).float().cpu()

    expected_rows = graph_node_count(pdb_path.stem)
    if tuple(representation.shape) != (expected_rows, embedding_dim):
        raise ValueError(
            f"{pdb_path.stem}: RNA-BAnG produced "
            f"{tuple(representation.shape)}, expected "
            f"({expected_rows}, {embedding_dim}); check chain A, missing backbone "
            f"atoms and coarse_graph_nodes.csv alignment"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdb_path.stem}_RNABANG.pkl"
    with open(output_path, "wb") as handle:
        pickle.dump(representation, handle)
    print(f"{pdb_path.stem}: {tuple(representation.shape)} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdbs",
        nargs="*",
        type=Path,
        help="Specific chain-A PDB files; defaults to data/esm3_input/*.pdb",
    )
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
    )
    args = parser.parse_args()

    pdbs = args.pdbs or sorted(DEFAULT_INPUT_DIR.glob("*.pdb"))
    if not pdbs:
        raise FileNotFoundError(f"No PDB inputs found in {DEFAULT_INPUT_DIR}")

    device = torch.device(args.device)
    model, processor, embedding_dim = load_model(args.checkpoint, device)
    for pdb_path in pdbs:
        embed_one(
            pdb_path,
            args.output_dir,
            model,
            processor,
            embedding_dim,
            device,
        )


if __name__ == "__main__":
    main()
