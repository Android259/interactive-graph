# Embedding generation

These scripts turn the project's two input kinds into the pickled tensors the
dataloader reads: candidate SMILES into one MoLFormer table, and protein structures
into one per-residue table per protein, per model.

This file is the procedure: what to install, where it goes, what to run.
`../EXTERNAL_TOOLS.md` is the provenance: versions, hashes, and the reproduction
checks already recorded for these tools. Read that one before replacing any stored
output.

Run every command below from the project root.

## What produces what

On the lipid side there are two steps, and only the second one needs a model.
`embed_smiles_isomeric_and_nonisomeric.py` reads `SmileGlobal`/`SmileFragment` from the
interaction table, splits the semicolon-separated candidates, canonicalises them with
RDKit and writes a plain list of SMILES. `embed_isomeric_smiles_molformer.py` reads that
list and writes the embedding table: `data/lipid_SMILES_isomeric_embedding.pkl` for runs
with `--lipid_isomers`, `data/lipid_SMILES_embedding_deterministic.pkl` for runs without.

On the protein side there are four scripts, one per model, and they are alternatives
rather than stages. All four read `data/esm3_input/<stem>.pdb`, the chain-A structures
`build_consistent_esm3_pdb.py` writes, and all four check their residue count against
that protein's `data/graphs/<stem>/coarse_graph_nodes.csv`:

- `embed_protein_esm3_v2.py` uses ESM3 `esm3-sm-open-v1` with sequence, structure, SASA
  and confidence, and writes `data/embedding_ESM3_v2/<stem>_ESM3v2.pkl`. This is the
  default protein input.
- `embed_protein_rnabang.py` uses RNA-BAnG's protein branch with no RNA input, and
  writes `data/embedding_RNABANG/<stem>_RNABANG.pkl`.
- `embed_protein_proteinmpnn.py` takes the ProteinMPNN encoder output before sequence
  decoding, with coordinate noise disabled, and writes
  `data/embedding_PROTEINMPNN/<stem>_PROTEINMPNN.pkl` for `--proteinmpnn_replace_esm3`.
- `embed_protein_esmif1.py` uses ESM-IF1 `esm_if1_gvp4_t16_142M_UR50` on backbone
  coordinates, and writes `data/embedding_ESMIF1/<stem>_ESMIF1.pkl` for
  `--esmif1_replace_esm3`.

ESM3 output carries BOS and EOS rows around the residue rows, and the loader drops the
first and last row before assigning embeddings to graph nodes. The other three write one
row per graph node with no such padding.

## Checkpoints

Two checkpoints are already in the working tree: `external/RNA-BAnG/ckpt/icml.pth`
(56 MB) and `external/ProteinMPNN/vanilla_model_weights/v_48_020.pt` (6.4 MB). Both ship
inside those repositories without an access gate, so nothing needs installing for them.

Two download themselves on first use. `embed_protein_esm3_v2.py` sets `HF_HOME` to
`data/esm3_checkpoint` before importing `esm`, keeping an existing `HF_HOME` if one is
set; the repository is public and ungated, and `HF_TOKEN`/`HF_API_TOKEN` are used only
when present. The recorded cache was 22 files and 5.2 GB. Install the package first with
`pip install esm`. ESM-IF1 is fetched by `fair-esm` the same way; its environment needs
`fair-esm`, `biotite < 1.0` and `torch_scatter`, and this project additionally pins
`scipy < 1.14`, so run it from the interpreter that has those.

MoLFormer is the one that must be installed by hand, and a fresh checkout is missing
both halves of it:

1. The code, as the vendored submodule `external/molformer`. The directory exists but is
  empty, so initialise the submodule.
2. The weights, under `data/Pretrained MoLFormer/`, holding `hparams.yaml` and
  `checkpoints/N-Step-Checkpoint_3_30000.ckpt`.

`--molformer-dir` is required and has no default. The script puts that directory on
`sys.path` and changes into it before loading, which is why the checkpoint defaults are
written relative to it as `../../data/Pretrained MoLFormer/...`: passing
`--molformer-dir external/molformer` makes them resolve inside `data/` as above.
`bert_vocab.txt` is read from inside the MoLFormer directory itself.

Both lipid embedding tables are already committed, so this install is only needed to
rebuild them.

## Run the lipid side

```bash
python3 preprocessing/embeddings/embed_smiles_isomeric_and_nonisomeric.py
python3 preprocessing/embeddings/embed_isomeric_smiles_molformer.py \
    --molformer-dir external/molformer
```

Repeat both with the non-isomeric list to rebuild the table every run without
`--lipid_isomers` reads:

```bash
python3 preprocessing/embeddings/embed_smiles_isomeric_and_nonisomeric.py --non-isomeric
python3 preprocessing/embeddings/embed_isomeric_smiles_molformer.py \
    --molformer-dir external/molformer \
    --input  data/unpreprocessed_files/nonisomeric_smiles_all.pkl \
    --output data/lipid_SMILES_embedding_deterministic.pkl
```

To extend an existing table instead of rebuilding it, pass the old pickle twice: to
`--skip-embedded`, which drops its keys from the collected list, and to `--merge`, which
carries its entries into the new file unchanged. Only the new SMILES are then encoded.

## Run the protein side

ESM3 takes one structure per invocation:

```bash
for pdb in data/esm3_input/*.pdb; do
    python3 preprocessing/embeddings/embed_protein_esm3_v2.py "$pdb"
done
```

The other three default to every `data/esm3_input/*.pdb` when given no arguments, and
take specific files as positional arguments otherwise:

```bash
python3 preprocessing/embeddings/embed_protein_proteinmpnn.py
python3 preprocessing/embeddings/embed_protein_esmif1.py
```

RNA-BAnG needs its own environment. The recorded minimum additions to this project's
PyTorch environment were `gemmi`, `einops` and `omegaconf`:

```bash
conda env create -f external/RNA-BAnG/environment.yml
conda run -n rnabang python preprocessing/embeddings/embed_protein_rnabang.py
```

## After regenerating

A changed lipid embedding table invalidates the caches built from it. Rebuild them with
`data/build_descriptor_cache.py` and `data/build_lipid_embedding_store.py`.
