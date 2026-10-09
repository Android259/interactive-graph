# Dataloader Contract

## Active vs Legacy

- `Dataloader.py` — the loader used by `training/new_train.py`.

## Cache Builders

- `cache_builders/` holds the build-side (`build_*`/`write_*`) half of every disk cache
  in this directory, one `*_builder.py` per cache, named `<cache>_<format>_builder.py`
  (`tanimoto_compact_tensors_builder.py`, `lipid_embedding_tensors_builder.py`,
  `lipid_graph_tensors_builder.py`, `protein_graph_tensors_builder.py`,
  `descriptor_csv_builder.py`). The
  matching reader module keeps the reader (`load_*`), the shared path/format logic, and
  any staleness-validation code the hot training path or a builder both need —
  `Dataloader.py` only ever imports `load_*` names, never from `cache_builders/`.
  Readers for the four tensor-archive caches live under `tensors_reading/`
  (`lipid_embedding_tensors_reader.py`, `lipid_graph_tensors_reader.py`,
  `protein_graph_tensors_reader.py`, `tanimoto_compact_tensors_reader.py`);
  `descriptor_cache_reader.py` (plain CSV tables, not a tensor archive) is the
  only one that stays top-level.
- The cache files themselves live under `data/cache/`, not `data/` directly — see
  `data/AGENTS.md`.

## Split Blocks (`splitting_on_blocks/`)

One module per lipid-axis cut — the definition of **which** chemistry leaves training,
not how negatives are drawn from what stays (that is `sampler.py`):

| module | flag | block is |
|---|---|---|
| `lipid_coldsplit_blocks.py` | `--lipid_coldsplit` | four hand-built project head-group class sets (`LIPID_COLDSPLIT_SETS`); `lipid_classes_for_holdout` derives the per-family form for `--double_coldsplit`/`--mixed_coldsplit` |
| `lipid_isolation_blocks.py` | `--lipid_isolation` | a species set at a requested Tanimoto isolation — **generated**, written by `analysis/lipid_block_search.py --emit_module`, never edited by hand |
| `lipid_subclass_blocks.py` | `--lipid_subclass` | one Titeca et al. subclass (or a `+` merge), membership read from `data/lipid_article_classification.json` |
| `lipid_species_blocks.py` | `--lipid_species_coldsplit` | a seeded draw of structure-disjoint name/structure components, recomputed per run from `(csv, share, seed)` |

- Only `lipid_isolation_blocks.py` is a stored table: its block needs the compact
  Tanimoto matrix to find, and nothing but `--tanimoto_weight` may open that at train
  time. The other three either need no search (`subclass`) or reproduce from inputs the
  run already has (`coldsplit`, `species`).
- The generator side stays outside this directory, exactly as `cache_builders/` sits
  outside the readers: `analysis/lipid_block_search.py` (isolation blocks) and
  `preprocessing/classify_lipids_by_article.py` (the subclass JSON).

## PLIDataset (`Dataloader.py`)

Constructed once, then unpacked as a 3-tuple:

```python
train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir, csv, seed,
    excluded_subgroups, config, excluded_groups)
```

- `__iter__` returns `(train, valid, test)` — three `copy.copy` clones of the same
  loaded artifacts, each pointing at a different `csv` slice (`csvtrain`,
  `csvalidate`, `csvtest`).
- `sampler.py` owns interaction-pool sampling and `ClassBalancedBatchSampler`.
- `graphs_builders/lipid_graph_builder.py` owns the legacy SMILES-embedding path.
- `graphs_builders/lipid_isomer_graph_builder.py` owns the atom/bond graph path selected
  by `lipid_graph_isomers=True`.
- `graphs_builders/protein_graph_builder.py` loads protein artifacts and assembles PyG
  tensors.
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
- `hard_negative_mining` / `dissimilar_negative_mining` only reweight the draw inside a
  **balanced** sampler (so they require one of `balanced_proteins`,
  `balance_negatives_by_family` or `balanced_lipid_classes`, and are mutually exclusive
  with each other). Both read one `species_similarity` pool and steer
  `*_negative_share` of the mass by a group's own positives: toward chemically close
  candidates, or away from them. The quota per group is untouched, so the pool stays
  balanced exactly as it was -- only which negatives fill it changes. Measured on the
  table, seed 42, ratio 2, share 1.0: the mean best Tanimoto from a drawn negative to
  its protein's own positives moves 0.657 (uniform) -> 0.714 (hard) / 0.534
  (dissimilar). Groups whose `ProteinDomain` is in `excluded_groups` are exempt from
  either direction.
- The two steering directions are orthogonal to **which** marginal a sampler flattens,
  not an alternative to it. The per-protein and per-family samplers steer per group
  (`_sample_group_balanced_negatives`); `balanced_lipid_classes` steers per
  (`ProteinDomain`, lipid class) **cell**, in `sample_lipid_class_balanced_negatives`'s
  own loop. Inside a cell every candidate already shares the head group, so what the
  Tanimoto reduction separates there is acyl composition -- a narrower span of chemistry
  than the same flag reaches under `balanced_proteins`, and the per-class matching the
  cell exists for is untouched.

## Tanimoto Files

Only `--tanimoto_weight` reads Tanimoto similarities. Everything else builds `id2pos` by
ranking the train row ids, so nothing is opened.

| file | size | needed by |
|---|---|---|
| `cache/Tanimoto_compact_*` (matrix, structure index, row ids, manifest) | 1.4 MiB | `--tanimoto_weight` |
| `cache/Tanimoto_compact_isomeric_*` | 1.7 MiB | `--tanimoto_weight --lipid_isomers` |

- Built by `preprocessing/build_tanimoto_compact.py` (`--isomeric` for the second set),
  directly from the interaction table's SMILES. It is the only Tanimoto builder: the old
  per-candidate square matrix (`Total_tanimoto_matrix_uint8.npy`, 2.8 GB) and its row-id
  vector (`Total_multiple_lipid_batch.npy`) are no longer built or read.
- The compact form is indexed per *distinct structure* (1226 non-isomeric, 1319
  isomeric); `structure_index` maps each candidate instance to its structure row, so
  `full[i,j] == compact[idx[i], idx[j]]` exactly. `CompactTanimoto.submatrix` gives the
  `K x K` block of the train candidates; `candidate_view()` gives the same per-candidate
  indexing for analysis scripts.
- Missing or stale (older than the interaction table) compact artifacts make a
  `--tanimoto_weight` run fail at `__init__` with a `FileNotFoundError` naming the
  rebuild command. A run without `--tanimoto_weight` never looks for them.
- Weights computed *directly* from the compact form would sum the same numbers in a
  different order and shift the last digits. Do not "simplify" it that way.
- The two modes are **not** interchangeable: `lipid_isomers` changes how many candidates
  a row contributes.
- `get_tanimoto_weights()` and `get_protein_weights()` both return one entry per
  `id2pos` position.

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
- `cache/protein_graph_tensors.pt` is used only while its manifest matches every source
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

## `--deepclip` samples and the preassembled loader

- Under `--deepclip`, `get()` builds no protein graph: the sample's `ProteinGraphData`
  holds `inter`, `family` (from `protein_family_one_hot`, no graph files read) and the
  per-row fields `finish_sample` attaches. `warm_caches` warms only the family one-hots,
  and the protein tensor cache is not loaded.
- `new_train.py` then swaps each split's DataLoader for `preassembled_loader.
  PreassembledLoader`: every (row, candidate) sample collated once onto the device,
  batches cut by indexing. It drives the original loader's batch sampler, replays the
  loader's per-iteration base-seed draw and replays the `lipid_random_choice` draws
  (`random.choice(range(n))`, in-process; a drawn split with `num_workers > 0` keeps
  its DataLoader), so
  batches, order and drawn candidates are those of the DataLoader.
  `get()` = draw + `sample_for_candidate(idx, candidate)`; keep that split if either
  changes. Verified bit-identical end to end with `analysis/probes/compare_run_outputs.py`.
- `--descriptors_head --descriptor_names` (`descriptors.descriptor_catalog_only`)
  takes the same path with less still: no protein graph, no lipid encoding (empty lipid
  `Data`, no MoLFormer table or protein tensor cache loaded) -- the model reads only
  `descriptor_catalog_input`. Train is preassembled under the 1740-row cap too when
  `num_workers=0`. Bit-identical on `dh_s15_mbw_hid32` (2 epochs), ~2x per epoch.
  `--descriptor_mlp --descriptor_names` (architecture/descriptor_mlp_head.py, the plain-
  MLP sibling of `--descriptors_head`) reads `descriptor_catalog_input` through the same
  `descriptor_catalog_only` predicate, so it gets the identical lean-loading/preassembly
  path -- nothing here is specific to which head reads the tensor.

## Invariants (do not break)

- Pair IDs are original interaction-CSV row positions and stay stable after
  sampling/splitting. `tanimoto_pos` is the compact train-only index into Tanimoto
  and protein-group weight vectors.
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

## SMILES Fragments (`graphs_builders/lipid_graph_builder.py`)

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
```
