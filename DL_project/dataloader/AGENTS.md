# Dataloader Contract

## Active vs Legacy

- `New_dataloader.py` — **active** loader used by `training/new_train.py`.
- `GRAB_graph.py` — pair-edge generation for the GRAB loss (train-only).
- `grab_dataset_graph.py` — train-only GRAB graph filtering and batch coefficients.
- `Dataloader.py`, `tanimoto_Dataloader.py` — **legacy** `PLIDataset` variants, not
  used by the active pipeline. Do not mirror active changes into them.

## PLIDataset (`New_dataloader.py`)

Constructed once, then unpacked as a 3-tuple:

```python
train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir, csv, seed,
    excluded_subgroups, config, excluded_groups)
```

- `__iter__` returns `(train, valid, test)` — three `copy.copy` clones of the same
  loaded artifacts, each pointing at a different `csv` slice (`csvtrain`,
  `csvalidate`, `csvtest`).
- `pair_graph` (GRAB) is built **only** for the train clone, and only when
  `config.grab_loss`; valid/test get `None`.
- `sampler.py` owns interaction-pool sampling and `ClassBalancedBatchSampler`.
- `lipid_graph_builder.py` owns the legacy SMILES-embedding path.
- `lipid_isomer_graph_builder.py` owns the atom/bond graph path selected by
  `lipid_graph_isomers=True`.
- `protein_graph_builder.py` loads protein artifacts and assembles PyG tensors.
- `protein_registry.py` reads `data/protein_registry.csv`, the single source for
  protein IDs, artifact stems, families, UniProt IDs, and historical ESM3 v1 trims.
- Key classes: `PLIDataset` (PyG dataset), `ProteinGraphData`, `LipidGraphData`.

## Negative Sampling

Every positive is always kept; only negatives are subsampled. Which sampler runs
is decided in `PLIDataset.__init__`, most specific first:

| config | negatives drawn | resulting 1:1 |
|---|---|---|
| `balanced_lipid_classes` | per (`ProteinDomain`, lipid class) cell | per family, per lipid class, globally; **not** per protein |
| `balanced_proteins` | per `LTPProtein`, matching that protein's positives | per protein, per family, globally |
| `balance_negatives_by_family` | per `ProteinDomain`, matching that family's positives | per family and globally, **not** per protein |
| neither | global 5.6% random subsample | none |

- `balanced_proteins` wins over `balance_negatives_by_family`: per-protein matching
  already implies per-family matching, so they compose instead of conflicting.
- `balanced_lipid_classes` currently overrides both, but it is a **trade, not a
  refinement**: it flattens the per-lipid-class prior (per-class positive rate
  0.25–0.68 → 0.50–0.51) at the cost of the per-protein one (0.05–0.92, std 0.26).
  The two cannot both be met — matching per (`LTPProtein`, class) starves the cells
  (376 negatives available against 756 positives) and ends up more skewed than the
  coarser samplers. Lipid class comes from `lipid_class_series`, the head group of
  `FullIdentityOfLipid` (36 classes over 312 lipids); the column is present in both
  the isomer and non-isomer CSVs.
- Per-family balance leaves individual proteins skewed, because the family draws
  from one shared negative pool — a positive-rich protein keeps mostly positives.
- `balance_excluded_group_negatives` runs afterwards and only rewrites the
  excluded groups (validation/test); train rows pass through untouched.
- `balanced_batches` (`dataloader/sampler.py`) is a separate
  layer: these flags balance the pool, that one balances each batch drawn from it.

## Tanimoto Files

Two `.npy` files under `data/`, with very different cost and reach:

| file | size | needed by |
|---|---|---|
| `Total_multiple_lipid_batch.npy` | 214 KB | **every run** — `id2pos` is built from it, and `tanimoto_pos` indexes it for *any* sample weighting (protein group, protein class, …) |
| `Total_tanimoto_matrix_uint8.npy` | 2.8 GB | `get_tanimoto_weights()` only, i.e. `--tanimoto_weight` |

- `train_tanimoto_matrix` is `None` unless `config.tanimoto_weight` is set;
  `get_tanimoto_weights()` raises a named `RuntimeError` rather than an `AttributeError`
  if called anyway. Do not restore the unconditional load. Making a 2.8 GB file a
  dependency of `__init__` means every run dies wherever it is absent: a 45-job Bigfoot
  batch did exactly that, in seconds, with `FileNotFoundError`, jobs that never asked
  for Tanimoto weights included. `scripts/cluster_sync_excludes.sh` now mirrors `data/`
  in full (only the 9.2 GB `lipid_SMILES_isomeric_embedding.pkl` and the 11 GB
  `esm3_checkpoint/` are held back), so the file usually is present — the point is that
  a run which does not need it must not care either way.
- `get_tanimoto_weights()` and `get_protein_weights()` both return one entry per
  `id2pos` position, so the no-weighting fallback can size itself from `len(id2pos)`
  instead of building Tanimoto weights just to copy their shape.
- `dataloader/Dataloader.py` and `dataloader/tanimoto_Dataloader.py` keep their own
  unconditional copies of this logic; they are legacy and out of the active path.

## Split Logic (cold split)

Group-disjoint splitting is driven by `excluded_groups` + `test_group`:

| config | `csvtrain` | `csvalidate` | `csvtest` |
|---|---|---|---|
| `excluded_groups=[A]` (no `test_group`) | all but A | 50% of A (seeded) | other 50% of A |
| `excluded_groups=[T,V]` + `test_group=T` | all but T,V | group V (all rows) | group T (all rows) |
| `+ balance_excluded_group_negatives` | as above | class-stratified 50/50 | remainder |

- `ProteinDomain` is matched **case-insensitively** (lowercased on both sides).
- With `test_group`, validation and test are **whole disjoint groups**, not random
  rows of the same group. `test_group` must be one of `excluded_groups` and
  `excluded_groups` must contain ≥2 groups (enforced in `read_configuration.py`).
- Canonical group names live in `read_configuration.EXCLUDED_SUBGROUPS_BY_NAME`.

## Rebuild Caches (`get()` hot path)

`get()` used to rebuild everything per sample: 89.5 ms each, 98 s per training epoch
against ~33 s of actual tensor maths. Four caches, all created in `__init__` and shared
by the three `copy.copy` clones, now serve what only depends on run-fixed inputs:

| cache | keyed by | replaces |
|---|---|---|
| `_protein_graph_cache` | `LTPProtein` | 2 CSV reads + pocketness PDB + ESM3 pickle + family one-hot (35 proteins back 1331 rows) |
| `_lipid_encoding_cache` | `(SmileGlobal, SmileFragment)` | RDKit canonicalization + embedding lookup (409 distinct lipids) |
| `_lipid_graph_cache` | canonical SMILES | isomer-graph node/edge CSV parse |
| `_complete_edge_index_cache` | node count | the complete-graph `edge_index` builder |

- Cached tensors are **shared between samples**. Collation copies with `torch.cat`, so
  nothing may mutate them in place; `inter` is the only per-row field and is rebuilt in
  `assemble_protein_graph` for every sample.
- Each train/valid/test clone materializes direct NumPy column views plus scalar
  `interaction`, `sample_index`, `tanimoto_pos`, and `protein_id` tensors.
  `get()` must use these indexed fields rather than constructing a pandas Series.
- `lipid_random_choice` stays outside cache warming because pre-touching rows would
  shift its Python RNG stream.
- `warm_caches()` fills them before the DataLoader forks its workers, so the workers
  inherit one warm copy instead of each filling its own. 131 MiB, 0.4 s, reported in the
  run log as `cache warmed : ...`.
- `protein_graph_tensors.pt` is used only while its manifest matches every source
  graph CSV/PDB by size and nanosecond mtime. Rebuild it with
  `data/build_protein_graph_tensor_cache.py`.
- Lipid graph CSV DataFrames are released immediately after tensor construction.
  `release_source_artifacts()` drops initialization-only tables, the consumed
  Tanimoto matrix, and a fully materialized lipid-embedding source dictionary.
- The non-isomer lipid `Data` no longer carries `edge_index`. It held the complete graph
  over the 768 embedding columns (295296 edges) and nothing read it: `lip_edgidx` reaches
  the model only under `lipid_graph_isomers`, which takes the `make_graph_lipid` path,
  and `num_nodes` comes from `x`. It cost 77 of the 89.5 ms per sample, 11.7 ms of
  collation and 76 MB of worker transfer per batch. `complete_graph_edge_index()` still
  builds it, memoized, for any caller that needs the complete graph back.
- Fixtures that build a `PLIDataset` with `object.__new__` must set the cache attributes
  themselves (see `tests/test_new_dataloader_lipid_graphs.py`).
- `num_workers` is **not** a free knob: `_MultiProcessingDataLoaderIter` draws a base
  seed from the loader generator, so switching to `num_workers=0` shifts the shuffle
  stream and changes metrics from the second epoch on (measured: valid balanced accuracy
  0.489583 → 0.500000). It also bought no time once these caches existed.

## Invariants (do not break)

- Pair IDs are original interaction-CSV row positions and stay stable after
  sampling/splitting. `tanimoto_pos` is the compact train-only index into Tanimoto
  and protein-group weight vectors.
- GRAB edge endpoints must both be train rows; validation/test labels never
  contribute to GRAB coefficients.
- `prot_batch` / `lip_batch` identify samples; `lipid_batch` identifies lipid
  fragments (only an extra attention restriction under `lipid_fragments_mask`).
- Per-protein file lookups in `get()` use the `RBP1→RET1` (etc.) rename map; keep
  it in sync with the `graphs/` and `embedding_ESM3/` directory names.
- Do not coerce an unknown identifier to a valid index to hide a cross-file
  mismatch; report it (see `data/AGENTS.md` cross-file contract).

## Change Rules

- A `get()` / shape / signature change must stay synchronized with
  `architecture/interaction_classification.py` and the train/valid/test calls in
  `training/new_train.py`.
- Both lipid paths must survive: `lipid_isomers` / `lipid_graph_isomers` select the
  chemical-graph path; otherwise the legacy embedding path is used.

## Verify (no full data, no GPU)

```bash
python3 -m pytest tests/test_new_dataloader_lipid_graphs.py tests/test_pair_index_alignment.py
python3 -m pytest tests/test_grab_graph.py
```
