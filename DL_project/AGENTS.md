# Project Architecture

## Global Rules

- Work only within the explicit request. Do not add adjacent fixes, flags, refactors, warning suppression, formatting passes, or optimizations.
- Preserve existing implementations when adding optional behavior. Delete or replace them only when explicitly requested.
- Never revert user or other-agent changes. Search usages with `rg` before changing shared schemas or signatures.
- Do not run full training, GPU training, TensorBoard, data generators, or modify generated data unless explicitly requested.
- Use sub-agents only when explicitly requested; give them disjoint file ownership.

## Repository Layout

```text
training/                 active entry point, CLI config parser, reproducibility
architecture/             model modules (InteractionClassification + encoders)
dataloader/               active PLIDataset (New_dataloader.py) + GRAB graph; legacy loaders
data/                     input artifacts (CSVs, ESM3/PLM embeddings, graphs) + lipid graph generator
preprocessing/            offline data prep (embeddings, negatives, PDB/FASTA, graphs)
analysis/                 canonical metrics-table build / analysis / plots
scripts/                  cluster job submission, env activation, run lifecycle
tests/                    CPU pytest suite
tanimoto_group_analysis/  Tanimoto similarity scripts + their output CSVs
```

Each code subdirectory has its own `AGENTS.md` with detailed contracts. Read the
closest one before editing files in that tree.

## Generated Outputs (never grep here for source or truth)

- `run/`, `run_old_arch_layout/` (257 dirs) — TensorBoard runs per label / exclusion set.
- `test_metrics/`, `test_metrics_by_label/`, `test_metrics_old_arch_layout/` — test reports.
- `script_logs/`, `testmode_outputs/`, `graphics/` — job logs, smoke outputs, figures.
- `metrics_summary*.csv`, `metrics_analysis.txt`, `feature_contributions.csv` — aggregated tables.
- `OAR.*`, `.bigfoot_session_*`/`.kraken_session_*`, `.bigfoot_job_queue*/`,
  `.kraken_job_queues/` — scheduler artifacts (gitignored; untracked since the
  Kraken port).

## Duplicate / Vendored Traps (ignore unless explicitly asked)

- `DL_project/` — stale nested copy of the whole project. Never edit or trust it.
- `external/molformer/` — vendored MoLFormer submodule.
- Root-level `analyze_*.py`, `plot_*.py`, `append_metric_to_table.py`,
  `add_new_metrics_to_table.py`, `summarize_standard_metrics.py` are **older siblings**
  of the canonical scripts in `analysis/`. Use `analysis/`.
- Root `analyze_*tanimoto*.py` duplicate `tanimoto_group_analysis/`.
- `new_train.py` (root) is only a `runpy` shim to `training/new_train.py`.

## Active Pipeline

```text
training/new_train.py
  -> training/read_configuration.py
  -> training/reproducibility.py
  -> dataloader/New_dataloader.py
  -> architecture/interaction_classification.py
       -> architecture/protein_encoder.py
            -> architecture/self_attention.py
       -> architecture/lipid_encoder.py
            -> architecture/self_attention.py
       -> architecture/cross_attention.py
       -> architecture/final_layer.py
  -> architecture/loss.py

dataloader/GRAB_graph.py
  -> data/grab_pair_graph_edges.csv
  -> dataloader/New_dataloader.py
  -> architecture/loss.py through training/new_train.py

data/build_lipid_isomer_graphs.py
  -> data/lipid_graphs/*
  -> dataloader/New_dataloader.py
```

## Main Modules

- `training/read_configuration.py`: `ModelConfig` and custom CLI parser.
- `training/reproducibility.py`: Python, NumPy, PyTorch, worker, and DataLoader seeds.
- `training/new_train.py`: active train/validation/test entry point; importing it causes runtime side effects.
- `dataloader/New_dataloader.py`: active dataset, protein/lipid loading, pair graph, GRAB coefficient precomputation.
- `dataloader/GRAB_graph.py`: pair-edge generation.
- `architecture/interaction_classification.py`: top-level model.
- `architecture/protein_encoder.py`: protein GATv2 encoder.
- `architecture/lipid_encoder.py`: legacy lipid embeddings and optional chemical-graph GATv2 encoder.
- `architecture/self_attention.py`: lipid and protein self-attention.
- `architecture/cross_attention.py`: bidirectional protein/lipid attention.
- `architecture/final_layer.py`: graph pooling, binary logits, and both gradient-reversal
  heads (per-partner anti-shortcut adversary, family DANN).
- `architecture/loss.py`: active `GRAB_loss`.
- `data/build_lipid_isomer_graphs.py`: offline lipid graph generation.
- `tests/`: unit and synthetic CPU integration tests.

## Active Invariants

- Pair IDs are original rows of the processed interaction CSV and remain stable
  after sampling and splitting.
- `tanimoto_pos` is the compact train-only position used to index Tanimoto and
  protein-group sample-weight vectors.
- GRAB graph sources and targets must both belong to train; validation and test
  labels never contribute to GRAB coefficients.
- `prot_batch` and `lip_batch` identify samples. `lipid_batch` identifies lipid
  fragments and is only an additional attention restriction.
- Attention masks use `True` for forbidden query-key pairs.
- The classifier returns `[batch, 2]` logits aligned one-to-one with labels.
- Reusing a seed reproduces CPU-side sampling and DataLoader order. Do not claim
  bitwise CUDA determinism unless deterministic CUDA algorithms are enabled and
  verified.
- Every trainable module must be reachable in its own configuration.
  `number_of_parameters` names run directories and is a column of
  `metrics_summary.csv`, so a module that is built but never runs corrupts the
  identity of past runs, not just memory use.
- Per-epoch training state (adversary reversal strengths) lives on the model, never on
  `conf`: the run report dumps `vars(conf)`, so anything set there is recorded as if it
  were a hyperparameter of the whole run.
- Adversary penalties stay out of the logged task loss; they are logged as their own
  scalars so `epoch/train loss` remains comparable across configurations.

## Legacy Boundaries

- `architecture/HybridPred.py`, `dataloader/Dataloader.py`, and `dataloader/tanimoto_Dataloader.py` are not used by the active training pipeline.
- Do not mirror active changes into legacy files unless explicitly requested.
- More specific instructions are stored in each major subdirectory's `AGENTS.md`.
