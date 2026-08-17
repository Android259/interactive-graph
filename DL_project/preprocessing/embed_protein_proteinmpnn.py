#!/usr/bin/env python3
"""Generate frozen per-residue ProteinMPNN encoder representations.

The official repository and its vanilla weights are kept in external/ProteinMPNN.
No extra environment is needed: ProteinMPNN is plain PyTorch.

    python3 preprocessing/embed_protein_proteinmpnn.py

Every PDB in data/esm3_input is encoded and written as
data/embedding_PROTEINMPNN/<stem>_PROTEINMPNN.pkl, consumed by
--proteinmpnn_replace_esm3.

What is taken: the output of the ENCODER stack (three message-passing layers over
each residue's 48 nearest neighbours, with N/CA/C/O/Cb distance features), before any
sequence decoding. That vector is a function of local backbone geometry alone, which
is the reason to try it here -- unlike ESM3 it carries no sequence-family signal, and
the cold-family split is precisely what withholds family information.

Two details are load-bearing:

* ``augment_eps=0``. The checkpoint was trained with 0.2 A of Gaussian coordinate
  noise; leaving it on would make the embedding of one protein differ between runs.
* ProteinMPNN's ``parse_PDB`` returns one row per *residue-numbering slot*, padding
  gaps in the numbering, while coarse_graph_nodes.csv has one row per residue that
  actually exists. Four of the 35 project proteins have such gaps (GLTP 205 vs 206,
  HSDL2 273 vs 275, LCN15 149 vs 154, STARD11 226 vs 235), so the rows are selected
  by residue number rather than taken wholesale. Getting this wrong would shift the
  embedding against the graph without any error -- the loader only checks the count.
"""

import argparse
import pickle
import sys
from pathlib import Path

import pandas
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MPNN_ROOT = PROJECT_ROOT / "external" / "ProteinMPNN"
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "esm3_input"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "embedding_PROTEINMPNN"
DEFAULT_CHECKPOINT = MPNN_ROOT / "vanilla_model_weights" / "v_48_020.pt"
EMBEDDING_DIM = 128


def load_model(checkpoint_path, device):
    if not MPNN_ROOT.is_dir():
        raise FileNotFoundError(f"ProteinMPNN checkout not found at {MPNN_ROOT}")
    sys.path.insert(0, str(MPNN_ROOT))
    from protein_mpnn_utils import ProteinMPNN

    checkpoint = torch.load(
        str(checkpoint_path), map_location=device, weights_only=False
    )
    model = ProteinMPNN(
        ca_only=False,
        num_letters=21,
        node_features=EMBEDDING_DIM,
        edge_features=EMBEDDING_DIM,
        hidden_dim=EMBEDDING_DIM,
        num_encoder_layers=3,
        num_decoder_layers=3,
        augment_eps=0.0,
        k_neighbors=checkpoint["num_edges"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device).eval()
    return model


def graph_residue_numbers(stem):
    """Residue numbers of the protein graph, in node order."""
    node_path = PROJECT_ROOT / "data" / "graphs" / stem / "coarse_graph_nodes.csv"
    if not node_path.is_file():
        raise FileNotFoundError(f"Protein graph nodes not found: {node_path}")
    return list(pandas.read_csv(node_path)["ID_resSeq"])


def encoder_representation(model, features):
    """Run only the encoder stack and return its per-residue output."""
    from protein_mpnn_utils import gather_nodes

    X, mask, residue_idx, chain_encoding_all = features
    edge_features, edge_index = model.features(
        X, mask, residue_idx, chain_encoding_all
    )
    nodes = torch.zeros(
        (edge_features.shape[0], edge_features.shape[1], edge_features.shape[-1]),
        device=edge_features.device,
    )
    edges = model.W_e(edge_features)
    mask_attend = gather_nodes(mask.unsqueeze(-1), edge_index).squeeze(-1)
    mask_attend = mask.unsqueeze(-1) * mask_attend
    for layer in model.encoder_layers:
        nodes, edges = layer(nodes, edges, edge_index, mask, mask_attend)
    return nodes.squeeze(0)


def embed_one(pdb_path, output_dir, model, device):
    from protein_mpnn_utils import parse_PDB, tied_featurize

    parsed = parse_PDB(str(pdb_path), ca_only=False)
    # Not every project PDB names its chain "A" (data/esm3_input keeps whatever the
    # source structure used), and tied_featurize raises a bare KeyError on a letter
    # that is not there. Read the letters parse_PDB actually found.
    letters = sorted(
        key[len("seq_chain_"):] for key in parsed[0] if key.startswith("seq_chain_")
    )
    if len(letters) != 1:
        raise ValueError(
            f"{pdb_path.stem}: expected one chain, found {letters}; the graph node "
            "order assumes a single chain"
        )
    chain_dict = {parsed[0]["name"]: (letters, [])}
    featurized = tied_featurize(parsed, device, chain_dict, ca_only=False)
    X, _, mask, _, _, chain_encoding_all = featurized[:6]
    residue_idx = featurized[12]

    with torch.inference_mode():
        representation = encoder_representation(
            model, (X, mask, residue_idx, chain_encoding_all)
        ).float().cpu()

    # Map graph node order onto parse_PDB's gap-padded numbering slots.
    residue_numbers = graph_residue_numbers(pdb_path.stem)
    first_residue = min(
        int(line[22:26])
        for line in open(pdb_path)
        if line.startswith("ATOM") and line[12:16].strip() == "CA"
    )
    rows = torch.tensor(
        [number - first_residue for number in residue_numbers], dtype=torch.long
    )
    if int(rows.min()) < 0 or int(rows.max()) >= representation.shape[0]:
        raise ValueError(
            f"{pdb_path.stem}: graph residue numbers fall outside the "
            f"{representation.shape[0]} slots ProteinMPNN produced; the PDB and "
            "coarse_graph_nodes.csv disagree about numbering"
        )
    representation = representation[rows]

    if tuple(representation.shape) != (len(residue_numbers), EMBEDDING_DIM):
        raise ValueError(
            f"{pdb_path.stem}: produced {tuple(representation.shape)}, expected "
            f"({len(residue_numbers)}, {EMBEDDING_DIM})"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdb_path.stem}_PROTEINMPNN.pkl"
    with open(output_path, "wb") as handle:
        pickle.dump(representation, handle)
    print(f"{pdb_path.stem}: {tuple(representation.shape)} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdbs", nargs="*", type=Path)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu"
    )
    args = parser.parse_args()

    pdbs = args.pdbs or sorted(DEFAULT_INPUT_DIR.glob("*.pdb"))
    if not pdbs:
        raise FileNotFoundError(f"No PDB inputs found in {DEFAULT_INPUT_DIR}")

    device = torch.device(args.device)
    model = load_model(args.checkpoint, device)
    for pdb_path in pdbs:
        embed_one(pdb_path, args.output_dir, model, device)


if __name__ == "__main__":
    main()
