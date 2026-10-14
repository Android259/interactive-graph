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
is no longer built or read; see `dataloader/tensors_reading/tanimoto_compact_tensors_reader.py` for the compact form and
why it is byte-identical.

## Generated Caches (`data/cache/`)

Every file built by one of `data/build_*.py`'s builders lives under `data/cache/`, not
`data/` directly -- plain source artifacts (the interaction CSV, the lipid embedding
pickles, `graphs/`, `lipid_graphs/`) stay in `data/` itself. Builder code lives in
`dataloader/cache_builders/`; the reader half (`load_*`) and the path/format logic stay
in the matching top-level `dataloader/*.py` module (see `dataloader/AGENTS.md`).

| cache file(s) under `data/cache/` | built by | read by |
|---|---|---|
| `Tanimoto_compact_*`, `Tanimoto_compact_isomeric_*` | `preprocessing/build_tanimoto_compact.py` | `dataloader/tensors_reading/tanimoto_compact_tensors_reader.py` |
| `Tanimoto_headgroup_compact_*` | `preprocessing/build_tanimoto_headgroup.py` | `training/pair_baseline_common.py`, `analysis/coldsplit_geometry.py --blocks --tanimoto headgroup` |
| `lipid_SMILES_embedding_deterministic.tensors.pt` + manifest | `data/build_lipid_embedding_store.py` | `dataloader/tensors_reading/lipid_embedding_tensors_reader.py` |
| `lipid_graph_tensors.pt` + manifest | `data/build_lipid_graph_tensor_cache.py` | `dataloader/tensors_reading/lipid_graph_tensors_reader.py` |
| `protein_graph_tensors.pt` (+ `.no_geometry.pt`) + manifests | `data/build_protein_graph_tensor_cache.py` | `dataloader/tensors_reading/protein_graph_tensors_reader.py` |
| `pair_descriptor_cache_deterministic_v2.json` (+ older hash-named seeds), `pair_value_cache_deterministic_*.json` | `data/build_descriptor_cache.py` | `dataloader/descriptor_cache_reader.py` |

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

## Protein Similarity (`data/protein_similarity/`)

Pairwise protein-protein similarity, three metrics, in the compact-Tanimoto format with
the lipid axis replaced by the protein one: `matrix[protein_index[i], protein_index[j]]`
is the similarity of two interaction-table rows' proteins, uint8 (`round(x * 255)`,
diagonal 255), 35 x 35.

| artifact set | metric | built by |
|---|---|---|
| `Protein_identity_*` | sequence identity after global pairwise alignment | `preprocessing/build_protein_sequence_similarity.py` |
| `Protein_blosum62_*` | the same alignment's positive-scoring (conservative) columns | the same script, same alignment pass |
| `Protein_tmscore_*` | TM-align structural TM-score (`tmtools` bindings) | `preprocessing/build_protein_tmscore.py` |

- Read by `--negative_similarity=protein_identity|protein_blosum62|protein_tmscore`,
  which steers `--hard_negative_mining`/`--dissimilar_negative_mining` by protein
  relatedness instead of lipid chemistry (`dataloader/similarity_pool.py`, and see
  `dataloader/AGENTS.md`'s negative-sampling section for the per-axis reference rule that
  makes a protein pool non-degenerate). The reader is
  `preprocessing/protein_similarity_common.load_similarity`; a missing or stale set
  raises at dataset construction naming its builder, rather than quietly drawing
  uniformly.
- All three divide by the LONGER sequence/chain, which is a measured choice, not a
  convention: dividing by the shorter one lets a 127-residue FABP1 score 0.205 identity
  and 0.448 TM-score against a 456-residue BPI it is unrelated to, which erases the
  margin against real distant homologs. The builders' headers carry the numbers.
- Residues come from `esm3_input/<LTPProtein>.pdb`, not `fasta/`, so all three metrics
  and the protein graphs describe the same residues in the same order.
- Each manifest records `names` (the protein per matrix row -- consumers key by
  `LTPProtein`, unlike the positionally-addressed lipid artifacts) plus the interaction
  table's and every structure's size and nanosecond mtime. `load_similarity` returns
  None rather than serving a matrix whose table or structures have moved.
- There is no `row_ids` file: a table row names exactly one protein, so the lipid side's
  candidate-instance axis has no analogue here.

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
