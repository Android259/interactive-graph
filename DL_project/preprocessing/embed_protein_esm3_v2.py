#!/usr/bin/env python3
"""Generate one ESM3 embedding from real structure + real confidence (v2 pipeline).

WHY A SEPARATE SCRIPT (does not touch or replace preprocessing/EmbedProtein.py or
its output in data/embedding_ESM3/):

The original pipeline (EmbedProtein.py) calls `ESMProtein(sequence=seq)` with ONLY a
sequence string read from an independently-generated FASTA file. ESM3 is a multi-track
model (sequence, structure/coordinates, SASA, secondary structure, function); with
only the sequence track populated, it runs in exactly the information regime of a
plain sequence-only model (no better than ESM2 for this input) despite the extra
architecture. See proposals_plm.md for the full analysis.

This script instead builds the ESMProtein from data/esm3_input/<stem>.pdb, the
consistent PDB produced by preprocessing/build_consistent_esm3_pdb.py, which carries:
  - sequence + coordinates, both derived from the SAME structure (no separate-FASTA
    alignment risk -- see plm_alignment risk that motivated preprocessing/plm_alignment.py)
  - a real per-residue B-factor/pLDDT in the B-factor column (pocketness.pdb's own
    B-factor column is a binary pocket flag, not usable as confidence -- see the
    header of build_consistent_esm3_pdb.py for how this was verified)
  - is_predicted correctly set per protein via is_predicted_manifest.csv, so
    experimental vs AlphaFold confidence semantics are not conflated

SASA track: uses Voronota's `residue_sas_area` from coarse_graph_nodes.csv (already
feeding the GNN branch) rather than recomputing it independently, so the PLM and GNN
branches see the same solvent-accessibility signal. This is a deliberate choice, not
the only valid one: Voronota's tangent-sphere SASA and freesasa's Shrake-Rupley SASA
were checked (analysis/check_sasa_correspondence.py) and agree almost perfectly
(Pearson r=0.9997 across 7794 residues from 35 proteins, linear fit
voronota=1.006*freesasa-0.73), so recomputing via freesasa/ProteinChain.sasa() instead
would give essentially the same values after that rescaling -- prefer Voronota's here
for GNN-branch consistency; switch to freesasa if matching ESM3's own SASA-tokenizer
calibration turns out to matter more in practice.

NOT ADDED (see proposals_plm.md for why): secondary_structure (would need an mkdssp
run, not present in this repo's data) and function_annotations (would need real
InterPro/GO annotations; the family label used elsewhere in this project, e.g.
CRAL-TRIO, is not that vocabulary and would misuse the track).

CHECKPOINT: the exact checkpoint this project has always used is "esm3-sm-open-v1"
(confirmed in preprocessing/EmbedProtein.py, and in this project's own dossier
dossier_GENCI_LTP-learning.md). The `esm` package resolves this name internally
(esm.utils.constants.esm3.data_root, read from the installed package source) to the
gated Hugging Face repo `EvolutionaryScale/esm3-sm-open-v1` and downloads it with
`huggingface_hub.snapshot_download(repo_id=...)` -- with NO explicit cache_dir, so it
uses whatever huggingface_hub's default cache is (governed by the HF_HOME env var).
This script sets HF_HOME to a project-local folder (CHECKPOINT_DIR below) BEFORE
importing esm, so both this script's own download check and ESM3's internal
data_root() call resolve to the same place, and re-running this script never
re-downloads an already-present checkpoint. Requires a Hugging Face token that has
accepted the esm3-sm-open-v1 license, via the HF_TOKEN or HF_API_TOKEN env var (the
`#HF_API_TOKEN=...` left as a comment in EmbedProtein.py was NOT reused here --
treat any token found in source as potentially compromised/stale and rotate it
rather than relying on it).

USAGE: takes ONE input .pdb path as a CLI argument (a file produced by
build_consistent_esm3_pdb.py, i.e. data/esm3_input/<stem>.pdb) and writes
data/embedding_ESM3_v2/<stem>_ESM3v2.pkl. Run once per protein, or loop the shell
over data/esm3_input/*.pdb to do all of them:

    python preprocessing/embed_protein_esm3_v2.py data/esm3_input/ATCAY.pdb
    for f in data/esm3_input/*.pdb; do
        python preprocessing/embed_protein_esm3_v2.py "$f"
    done
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

# Must be set before `esm` (and therefore huggingface_hub's default cache
# resolution) is imported, so ESM3.from_pretrained's internal, cache_dir-less
# snapshot_download() call agrees with the explicit check in
# ensure_checkpoint_downloaded() below on where the checkpoint lives.
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
