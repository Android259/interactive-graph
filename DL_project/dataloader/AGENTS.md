# Dataloader Contract

## Active vs Legacy

- `Dataloader.py` — **active** loader used by `training/new_train.py`.
- `GRAB_graph.py` — pair-edge generation for the GRAB loss (train-only).
- `grab_dataset_graph.py` — train-only GRAB graph filtering and batch coefficients.
- `Dataloader.py`, `tanimoto_Dataloader.py` — **legacy** `PLIDataset` variants, not
  used by the active pipeline. Do not mirror active changes into them.

## PLIDataset (`Dataloader.py`)

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
- There is no protein registry: the interaction table is the only source of
  per-protein metadata. `ProteinGraphBuilder.protein_family` reads `ProteinDomain`
  straight from it, and artifacts are looked up under the `LTPProtein` name itself.
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

Only `--tanimoto_weight` reads any of these. Everything else builds `id2pos` by ranking
the train row ids, which reproduces the file's own mapping rather than an equivalent one
(the row-id vector covers the interaction table completely: 11018 rows, 11018 distinct
ids, none missing), so nothing is opened:

| file | size | needed by |
|---|---|---|
| `Tanimoto_compact_*` (matrix, structure index, row ids, manifest) | 1.4 MiB | `--tanimoto_weight`, **preferred** — one row per distinct structure |
| `Tanimoto_compact_isomeric_*` | 1.7 MiB | `--tanimoto_weight --lipid_isomers` |
| `Total_multiple_lipid_batch.npy` | 214 KB | fallback only, when no compact set is current |
| `Total_tanimoto_matrix_uint8.npy` | 2.8 GB | fallback only |

- The compact form is indexed per *distinct structure* (1226 non-isomeric, 1319
  isomeric) rather than per candidate instance (53762 / 58968). Since every byte is
  `round(BulkTanimotoSimilarity(fp_a, fp_b) * 255)` over Morgan fingerprints, and a
  fingerprint is a pure function of the canonical SMILES, two instances of one structure
  have byte-identical rows — so `full[i,j] == compact[idx[i], idx[j]]` exactly.
  `CompactTanimoto.submatrix` materializes the same `K x K` block the full matrix was
  sliced for, and the weight arithmetic is untouched. Verified against the full matrix
  and against a densely rebuilt block; `preprocessing/build_tanimoto_compact.py
  --verify-candidates N` re-checks it.
- Weights computed *directly* from the compact form would sum the same numbers in a
  different order and shift the last digits. Do not "simplify" it that way.
- The two modes are **not** interchangeable: `lipid_isomers` changes how many candidates
  a row contributes, so the row-id vectors have different lengths. An isomeric run now
  gets the isomeric artifacts; before they existed it silently got the non-isomeric
  similarities, so `--lipid_isomers --tanimoto_weight` results are not comparable across
  that change.

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
| `_lipid_candidate_key_cache` | `(SmileGlobal, SmileFragment)` | the canonicalization only, under `lipid_random_choice` (see below) |
| `_lipid_graph_cache` | canonical SMILES | isomer-graph node/edge CSV parse |
| `_complete_edge_index_cache` | node count | the complete-graph `edge_index` builder |

- Cached tensors are **shared between samples**. Collation copies with `torch.cat`, so
  nothing may mutate them in place; `inter` is the only per-row field and is rebuilt in
  `assemble_protein_graph` for every sample.
- Each train/valid/test clone materializes direct NumPy column views plus scalar
  `interaction`, `pair_id`, `tanimoto_pos`, and `protein_id` tensors.
  `get()` must use these indexed fields rather than constructing a pandas Series.
- `lipid_random_choice` must **never** cache the drawn encoding. `persistent_workers`
  keeps each worker alive for the whole run, so a cached draw is frozen for the whole
  run and the mode degenerates into "one arbitrary fixed candidate per row". The draw
  therefore happens per access in `_drawn_lipid_encoding`, over the canonical keys held
  in `_lipid_candidate_key_cache` — which is also why `smiles_encoding` is not released
  in this mode. The isomer-graph path already had this shape: it draws first, then hits
  a cache keyed by the chosen SMILES.
- Warming is safe in that mode (it fills keys, draws nothing) and goes through
  `warm_lipid_encoding`. Only `lipid_graph_isomers` **plus** `lipid_random_choice` stays
  out of warming, because there the draw happens inside `make_graph_lipid` itself.
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
- Per-protein file lookups in `get()` use the interaction table's own protein name
  directly: `graphs/<name>/`, `embedding_*/<name>_*`, `esm3_input/<name>.pdb`. There
  is no rename map any more -- if a new protein needs one, rename its artifacts
  instead of reintroducing the mapping.
- Do not coerce an unknown identifier to a valid index to hide a cross-file
  mismatch; report it (see `data/AGENTS.md` cross-file contract).

## Change Rules

- A `get()` / shape / signature change must stay synchronized with
  `architecture/interaction_classification.py` and the train/valid/test calls in
  `training/new_train.py`.
- Both lipid paths must survive: `lipid_isomers` / `lipid_graph_isomers` select the
  chemical-graph path; otherwise the legacy embedding path is used.

## SMILES Fragments (`lipid_graph_builder.py`)

A `;`-separated SMILES field is a bag of candidate structures for one measured lipid
species (sn-positional / double-bond isomers), written as `"A; B; C; "`. Parsing strips
each part, drops empty/`0` parts and deduplicates by canonical SMILES; a candidate that
parses but is absent from the embedding table raises rather than being skipped.

| config | embedding path (`lipid_encoding`) |
|---|---|
| `lipid_first_fragment_only` (default **on**) | only the first usable candidate — what this path did before the flag existed, so previous runs stay reproducible; all three treatments collapse to the same input |
| `lipid_concat` | every candidate along the token axis of `(1, tokens, 768)` |
| `lipid_random_choice` | one candidate per `get()`, drawn from the Python RNG |
| `lipid_fragments_mask` | as concat, plus a per-token fragment id in `lipid_batch` |

- `lipid_first_fragment_only` governs the embedding path only; the
  `lipid_graph_isomers` path has always used every candidate.
- Fragment ids are numbered per sample and are **not** offset at collation time
  (the non-isomer path builds a plain `Data`). That is safe only because
  `SelfAttention` combines them as `attn_mask | ~mult_mask`, and `attn_mask`
  already blocks every cross-sample pair.

## Verify (no full data, no GPU)

```bash
python3 -m pytest tests/test_new_dataloader_lipid_graphs.py tests/test_pair_index_alignment.py
python3 -m pytest tests/test_grab_graph.py
```
