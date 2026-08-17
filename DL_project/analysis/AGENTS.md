# Analysis Contract

Read-only reporting over completed runs. These scripts **consume** artifacts
(`metrics_summary.csv`, test reports, TensorBoard runs) and **produce** tables,
text summaries, and figures. They do not train.

- This `analysis/` package is the **canonical** location. Root-level
  `analyze_*.py` / `plot_*.py` are older siblings — prefer these.
- Do not run training, GPU work, or regenerate the aggregated tables casually;
  most scripts append to or overwrite shared files (see Side Effects).

## Metrics-Table Pipeline

```text
test reports + TensorBoard runs
  -> build_metrics_table.py        # (re)build normalized metrics_summary.csv
  -> append_metric_to_table.py     # add/replace ONE completed test report
  -> add_new_metrics_to_table.py   # add reports not yet in the table
metrics_summary.csv
  -> analyze_metrics_table.py      # validation-based comparison report
  -> analyze_common_epoch.py       # single epoch best across matched groups/seeds
  -> analyze_feature_contributions.py  # matched configuration-feature effects -> feature_contributions.csv
  -> summarize_standard_metrics.py / summarize_label.py / analyze_label_metrics.py
  -> compare_labels.py             # matched (exclusion_set, seed) diff of two labels
```

## Plots

- `plot_group_learning_curve.py` — whole-group learning curves averaged over
  matched seeds (reads TensorBoard runs).
- `plot_metric_by_subgroup.py` — per-protein-subgroup metrics from test reports.
- Both are invoked by `scripts/tools/generate_config_graphics.sh`; figures land
  in `graphics/`.

## Not Here

Tanimoto similarity of the lipids each protein group binds lives in
`tanimoto_group_analysis/`, next to the CSVs it produces.

## One-Offs

- `scratch_count.py` — rebuilds a run's `ModelConfig` from its test report and
  counts the parameters the discovered gate widths would remove. Reads paths
  relative to the project root, so run it from there:
  `python3 analysis/scratch_count.py`.

## Run Reorganizers

- `reorganize_runs_by_label.py` — label-first view of TensorBoard run dirs.
- `reorganize_test_metrics_by_label.py` — label-first view of test reports
  (feeds `test_metrics_by_label/`).

## Matching Convention

Configurations are compared by **matched keys** — typically `(label,
exclusion_set, seed)` — so only like-for-like runs are averaged or differenced.
Preserve this matching; do not average across mismatched exclusion sets or seeds.

## Side Effects (guard these)

- `build_metrics_table.py` overwrites `metrics_summary.csv`; `append_*` /
  `add_new_*` mutate it in place. Confirm before running.
- `analyze_feature_contributions.py` writes `feature_contributions.csv`.
- `analyze_label_metrics.py` / `summarize_*` append to text files
  (e.g. `metrics_summary_label_analysis.txt`).

Run these only when explicitly requested, and prefer a copy of the CSV for
exploratory analysis.
