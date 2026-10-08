# Data Contract

## Safety

- Treat the active inputs listed below as persistent research artifacts.
- Do not edit, delete, regenerate, or reformat artifacts unless explicitly requested.
- Never change generated data merely to make tests pass.
- Use temporary directories and small fixtures for tests.

## Active Inputs

`dataloader/Dataloader.py` consumes:

```text
Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv
cache/Tanimoto_compact_*            (only under --tanimoto_weight; preprocessing/build_tanimoto_compact.py)
cache/Tanimoto_compact_isomeric_*    (same, under --tanimoto_weight --lipid_isomers)
lipid_SMILES_embedding_deterministic.pkl / lipid_SMILES_isomeric_embedding.pkl
embedding_ESM3/*
graphs/*
lipid_graphs/*
```

The old full-matrix pair (`Total_tanimoto_matrix_uint8.npy`, `Total_multiple_lipid_batch.npy`)
is no longer built or read; see `dataloader/tanimoto_compact.py` for the compact form and
why it is byte-identical.

## Generated Caches (`data/cache/`)

Every file built by one of `data/build_*.py`'s builders lives under `data/cache/`, not
`data/` directly -- plain source artifacts (the interaction CSV, the lipid embedding
pickles, `graphs/`, `lipid_graphs/`) stay in `data/` itself. Builder code lives in
`dataloader/cache_builders/`; the reader half (`load_*`) and the path/format logic stay
in the matching top-level `dataloader/*.py` module (see `dataloader/AGENTS.md`).

| cache file(s) under `data/cache/` | built by | read by |
|---|---|---|
| `Tanimoto_compact_*`, `Tanimoto_compact_isomeric_*` | `preprocessing/build_tanimoto_compact.py` | `dataloader/tanimoto_compact.py` |
| `Tanimoto_headgroup_compact_*` | `preprocessing/build_tanimoto_headgroup.py` | `training/pair_baseline_common.py`, `analysis/coldsplit_geometry.py --blocks --tanimoto headgroup` |
| `lipid_SMILES_embedding_deterministic.tensors.pt` + manifest | `data/build_lipid_embedding_store.py` | `dataloader/lipid_embedding_store.py` |
| `lipid_graph_tensors.pt` + manifest | `data/build_lipid_graph_tensor_cache.py` | `dataloader/lipid_graph_tensor_cache.py` |
| `protein_graph_tensors.pt` (+ `.no_geometry.pt`) + manifests | `data/build_protein_graph_tensor_cache.py` | `dataloader/protein_graph_tensor_cache.py` |
| `pair_descriptor_cache_deterministic_v2.json` (+ older hash-named seeds), `pair_value_cache_deterministic_*.json` | `data/build_pair_descriptor_cache.py` | `dataloader/pair_descriptor_cache.py` |

`build_protein_graph_tensor_cache.py` derives `cache/protein_graph_tensors.pt` and
`cache/protein_graph_tensors.manifest.json` from the protein graph CSV/PDB artifacts.
The loader rejects a stale cache when a source size or mtime differs.

Per-protein metadata lives in the interaction table itself: `LTPProtein` is the name
every artifact is filed under (`graphs/<name>/`, `embedding_*/<name>_*`,
`esm3_input/<name>.pdb`) and `ProteinDomain` is the family the model one-hots. There is
no separate registry file, no artifact-stem mapping and no per-protein trim metadata --
if a new protein does not fit this layout, rename its artifacts rather than adding a
mapping.

Preserve row order in the processed interaction CSV: pair IDs and Tanimoto indices depend on original row positions.

The following cross-file relationships are part of the data contract:

- every pair ID used by the sampled train split must occur in the compact
  Tanimoto artifacts' `row_ids` array;
- `cache/Tanimoto_compact_*`'s `structure_index` must align with its own `row_ids`
  (one entry per candidate instance) and its manifest's recorded source size/mtime
  must match the interaction table on disk, or the loader refuses it;
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
