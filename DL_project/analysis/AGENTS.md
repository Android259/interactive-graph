# Analysis Contract

Read-only reporting over completed runs. These scripts **consume** artifacts
(`results/tables/metrics_summary.csv`, test reports, TensorBoard runs) and **produce**
tables, text summaries, and figures. They do not train.

- `analysis/` holds the shared pipeline below plus two subfolders:
  `baselines/` (non-neural reference models: Kron-RLS, GBM, the label-level
  marginal baselines) and `probes/` (one-off research scripts, each reading the
  table or checkpoints read-only). `tanimoto_groups/` is its own thing (see "Not
  Here"). There are no root-level `analyze_*.py` siblings to prefer against; the
  graph-generating `plot_*.py` scripts are the one deliberate exception and live
  under `scripts/graphics_generation/` (see Plots).
- Do not run training, GPU work, or regenerate the aggregated tables casually;
  most scripts append to or overwrite shared files (see Side Effects).

## Metrics-Table Pipeline

```text
test reports + TensorBoard runs
  -> training/append_metric_to_table.py     # add/replace ONE completed test report
  -> training/add_new_metrics_to_table.py   # add reports not yet in the table
  -> build_metrics_table.py                 # (re)build normalized metrics_summary.csv
results/tables/metrics_summary.csv
  -> find_best_epoch_by_all_seeds_and_groups.py  # single epoch best across matched groups/seeds
  -> summarize_standard_metrics.py / summarize_label.py
  -> compare_labels.py             # matched (exclusion_set, seed) diff, or ranked table for 3+ labels
```

`training/append_metric_to_table.py` and `training/add_new_metrics_to_table.py` live
in `training/`, not here: the first is called from `training/final_evaluation.py`
after every test run (a live-pipeline side effect), the second is what
`scripts/wait_and_sync.sh` runs after syncing a cluster's results -- neither is a
read-only report over a table assumed already complete, which is this directory's
own contract. Both still depend on `build_metrics_table.py`'s own `metric_row`/
`upsert_row` parsing, which stays here.

Every report path and run directory is `<root>/<family>/<label>/...`, where
`<family>` is the `arg_files/` subdirectory the label's config lives under
(`training/results_layout.py`). `build_metrics_table.py` / `training/add_new_metrics_
to_table.py` skip anything outside that layout rather than misreading the family as
a label.

## Plots

Graph-generating scripts live under `scripts/graphics_generation/`, not here —
`plot_group_learning_curve.py` (whole-group learning curves averaged over matched
seeds, reads TensorBoard runs), `plot_metric_by_subgroup.py` (per-protein-subgroup
metrics from test reports), `plot_cron_group_metric_vs_tanimoto.py`, and
`split_similarity_vs_metric.py`. The first two are invoked by
`scripts/generate_config_graphics.sh`; figures land in `graphics/`.

## Not Here

Tanimoto similarity of the lipids each protein group binds lives in
`analysis/tanimoto_groups/`, next to the CSVs it produces.

## Parameter Counting

- `calculate_number_of_parameters_of_model_by_label.py` (was `model_parameter_
  breakdown.py`; absorbed the former one-off `probes/scratch_count.py`) — builds
  `InteractionClassification` from an arg_file label (no data/ or GPU needed) and
  prints its parameter count broken down by architectural part.

## Matching Convention

Configurations are compared by **matched keys** — typically `(label,
exclusion_set, seed)` — so only like-for-like runs are averaged or differenced.
Preserve this matching; do not average across mismatched exclusion sets or seeds.

## Side Effects (guard these)

- `build_metrics_table.py` overwrites `results/tables/metrics_summary.csv`; `append_*` /
  `add_new_*` mutate it in place. Confirm before running.
- `analyze_label_metrics.py` / `summarize_*` append to text files
  (e.g. `metrics_summary_label_analysis.txt`).

Run these only when explicitly requested, and prefer a copy of the CSV for
exploratory analysis.
