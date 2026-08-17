# Data Contract

## Safety

- Treat the active inputs listed below as persistent research artifacts.
- Do not edit, delete, regenerate, or reformat artifacts unless explicitly requested.
- Never change generated data merely to make tests pass.
- Use temporary directories and small fixtures for tests.

## Active Inputs

`dataloader/New_dataloader.py` consumes:

```text
Processed_Negative_Interaction_Without_Duplicates.csv
Total_tanimoto_matrix_uint8.npy
Total_multiple_lipid_batch.npy
lipid_SMILES_embedding.pkl
grab_pair_graph_edges.csv
embedding_ESM3/*
graphs/*
lipid_graphs/*
```

`build_protein_graph_tensor_cache.py` derives `protein_graph_tensors.pt` and
`protein_graph_tensors.manifest.json` from the protein graph CSV/PDB artifacts.
The loader rejects a stale cache when a source size or mtime differs.

Per-protein metadata lives in the interaction table itself: `LTPProtein` is the name
every artifact is filed under (`graphs/<name>/`, `embedding_*/<name>_*`,
`esm3_input/<name>.pdb`) and `ProteinDomain` is the family the model one-hots. There is
no separate registry file, no artifact-stem mapping and no per-protein trim metadata --
if a new protein does not fit this layout, rename its artifacts rather than adding a
mapping.

Preserve row order in the processed interaction CSV: pair IDs and Tanimoto indices depend on original row positions.

The following cross-file relationships are part of the data contract:

- every pair ID used by the sampled train split must occur in
  `Total_multiple_lipid_batch.npy`;
- both dimensions of `Total_tanimoto_matrix_uint8.npy` align with
  `Total_multiple_lipid_batch.npy`;
- every endpoint in `grab_pair_graph_edges.csv` is an original interaction CSV
  row position;
- protein graph edge residue IDs must exist in the matching node table;
- protein node rows, `embedding_ESM3` residues, and `pocketness.pdb` residues
  must have equal lengths and order.

Do not hide cross-file inconsistencies by coercing an unknown identifier to a
valid index. Report and correct the generating artifact only when explicitly
requested.

## Lipid Graph Generator

- `build_lipid_isomer_graphs.py` is the active generator.
- Input: processed interaction CSV columns `SmileGlobal` and `SmileFragment`.
- Output:
  - `lipid_graphs/<sha1-prefix>/nodes.csv`
  - `lipid_graphs/<sha1-prefix>/edges.csv`
  - `lipid_graphs/lipid_graph_index.csv`
- Keep SMILES normalization and CSV column order synchronized with `PLIDataset.make_graph_lipid`.
- Canonicalization must preserve isomeric SMILES.
- Each covalent bond is written in both directions.
- Report invalid/skipped SMILES after generation.

Verify code without regenerating data:

```bash
python3 -m pytest tests/test_build_lipid_isomer_graphs.py
```

Generate only when requested:

```bash
python3 data/build_lipid_isomer_graphs.py
```
