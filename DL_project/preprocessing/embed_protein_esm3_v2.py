#!/usr/bin/env python3
"""Generate ESM3 embeddings from structure, sequence, SASA and confidence.

Read data/esm3_input/<stem>.pdb from build_consistent_esm3_pdb.py. Read Voronota
SASA from coarse_graph_nodes.csv and the structure type from
is_predicted_manifest.csv. Secondary-structure and function tracks are not supplied.
Write data/embedding_ESM3_v2/<stem>_ESM3v2.pkl.

Use checkpoint esm3-sm-open-v1. Check CHECKPOINT_DIR before downloading it.
HF_TOKEN or HF_API_TOKEN is used when set. Set the default HF_HOME before importing
esm; an existing HF_HOME value is preserved.

    python3 preprocessing/embed_protein_esm3_v2.py data/esm3_input/ATCAY.pdb
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
IN_DIR = DATA_ROOT / "esm3_input"
OUT_DIR = DATA_ROOT / "embedding_ESM3_v2"
CHECKPOINT_DIR = DATA_ROOT / "esm3_checkpoint"
CHECKPOINT_REPO = "EvolutionaryScale/esm3-sm-open-v1"

# Set the default Hugging Face cache location before importing esm.
os.environ.setdefault("HF_HOME", str(CHECKPOINT_DIR))

import pickle as pkl  # noqa: E402

import torch  # noqa: E402
from esm.models.esm3 import ESM3  # noqa: E402
from esm.sdk.api import ESM3InferenceClient, ESMProtein, SamplingConfig  # noqa: E402
from esm.utils.structure.protein_chain import ProteinChain  # noqa: E402
from huggingface_hub import snapshot_download  # noqa: E402


def ensure_checkpoint_downloaded() -> Path:
    """Download esm3-sm-open-v1 into CHECKPOINT_DIR if it isn't already there."""
    token = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
    try:
        path = snapshot_download(
            repo_id=CHECKPOINT_REPO, cache_dir=str(CHECKPOINT_DIR), local_files_only=True
        )
        print(f"checkpoint already downloaded: {path}")
    except Exception:
        print(f"checkpoint not found under {CHECKPOINT_DIR} -- downloading "
              f"{CHECKPOINT_REPO} (requires a HF token that accepted its license)")
        path = snapshot_download(
            repo_id=CHECKPOINT_REPO, cache_dir=str(CHECKPOINT_DIR), token=token
        )
        print(f"downloaded to: {path}")
    return Path(path)


def load_is_predicted_manifest() -> dict[str, bool]:
    manifest = {}
    with open(IN_DIR / "is_predicted_manifest.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            manifest[row["stem"]] = row["is_predicted"] == "True"
    return manifest


def load_sasa(stem: str) -> list[float]:
    """Per-residue Voronota SASA, in the same node order as the consistent PDB."""
    nodes_csv = DATA_ROOT / "graphs" / stem / "coarse_graph_nodes.csv"
    with open(nodes_csv, newline="") as handle:
        return [float(row["residue_sas_area"]) for row in csv.DictReader(handle)]


def embed_one(pdb_path: str, model: ESM3InferenceClient, manifest: dict[str, bool]):
    stem = Path(pdb_path).stem
    if stem not in manifest:
        raise ValueError(
            f"{stem!r} not found in {IN_DIR / 'is_predicted_manifest.csv'} -- "
            f"expected a file produced by build_consistent_esm3_pdb.py"
        )
    is_predicted = manifest[stem]

    chain = ProteinChain.from_pdb(pdb_path, chain_id="detect", is_predicted=is_predicted)
    protein = ESMProtein.from_protein_chain(chain)
    protein.sasa = load_sasa(stem)
    if len(protein.sasa) != len(protein.sequence):
        raise ValueError(
            f"{stem}: sasa length {len(protein.sasa)} != sequence length "
            f"{len(protein.sequence)} -- coarse_graph_nodes.csv row count must "
            f"match the consistent PDB's residue count; re-run "
            f"build_consistent_esm3_pdb.py if this trips."
        )

    protein_tensor = model.encode(protein)
    output = model.forward_and_sample(
        protein_tensor, SamplingConfig(return_per_residue_embeddings=True)
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{stem}_ESM3v2.pkl"
    with open(out_path, "wb") as handle:
        pkl.dump(output.per_residue_embedding, handle)
    print(f"{stem}: {tuple(output.per_residue_embedding.shape)} -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdb", help="Path to a consistent PDB from build_consistent_esm3_pdb.py "
                    "(data/esm3_input/<stem>.pdb)"
    )
    args = parser.parse_args()

    ensure_checkpoint_downloaded()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model: ESM3InferenceClient = ESM3.from_pretrained("esm3-sm-open-v1", device=device)
    manifest = load_is_predicted_manifest()
    embed_one(args.pdb, model, manifest)


if __name__ == "__main__":
    main()
