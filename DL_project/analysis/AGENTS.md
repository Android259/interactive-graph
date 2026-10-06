# Analysis Contract

Read-only reporting over completed runs. These scripts **consume** artifacts
(`results/tables/metrics_summary.csv`, test reports, TensorBoard runs) and **produce**
tables, text summaries, and figures. They do not train.

- `analysis/` holds the shared pipeline below plus two subfolders:
  `baselines/` (non-neural reference models: Kron-RLS, GBM, the label-level
  marginal baselines) and `probes/` (one-off research scripts, each reading the
  table or checkpoints read-only). `tanimoto_groups/` is its own thing (see "Not
  Here"). Nothing lives outside `analysis/` any more — there are no root-level
  `analyze_*.py` / `plot_*.py` siblings to prefer against.
- Do not run training, GPU work, or regenerate the aggregated tables casually;
  most scripts append to or overwrite shared files (see Side Effects).

## Metrics-Table Pipeline

```text
test reports + TensorBoard runs
  -> build_metrics_table.py        # (re)build normalized metrics_summary.csv
  -> append_metric_to_table.py     # add/replace ONE completed test report
  -> add_new_metrics_to_table.py   # add reports not yet in the table
results/tables/metrics_summary.csv
  -> analyze_common_epoch.py       # single epoch best across matched groups/seeds
  -> summarize_standard_metrics.py / summarize_label.py / analyze_label_metrics.py
  -> compare_labels.py             # matched (exclusion_set, seed) diff of two labels
```

Every report path and run directory is `<root>/<family>/<label>/...`, where
`<family>` is the `arg_files/` subdirectory the label's config lives under
(`training/results_layout.py`). `build_metrics_table.py` / `add_new_metrics_to_table.py`
skip anything outside that layout rather than misreading the family as a label.

## Plots

- `plot_group_learning_curve.py` — whole-group learning curves averaged over
  matched seeds (reads TensorBoard runs).
- `plot_metric_by_subgroup.py` — per-protein-subgroup metrics from test reports.
- Both are invoked by `scripts/tools/generate_config_graphics.sh`; figures land
  in `graphics/`.

## Not Here

Tanimoto similarity of the lipids each protein group binds lives in
`analysis/tanimoto_groups/`, next to the CSVs it produces.

## One-Offs

- `scratch_count.py` — rebuilds a run's `ModelConfig` from its test report and
  counts the parameters the discovered gate widths would remove. Reads paths
  relative to the project root, so run it from there:
  `python3 analysis/probes/scratch_count.py`.

## Run Reorganizers

- `reorganize_runs_by_label.py` — label-first view of TensorBoard run dirs.
- `reorganize_test_metrics_by_label.py` — label-first view of test reports
  (feeds `test_metrics_by_label/`).

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
