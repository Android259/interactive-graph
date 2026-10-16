# Pairs CSV pipeline

This pipeline builds the training table from positive protein-lipid measurements.
To add measurements, update the positive table, run the four commands below, and
rebuild the affected caches.

Input: `data/unpreprocessed_files/Processed_dataset_smiles_completed.csv`.
It has one row per measurement, with `Interaction=1` and uncorrected SMILES.
The documented input has 756 rows.

Output: `data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv`.
The documented output has 9905 rows. `dataloader/Dataloader.py` reads this file.
Keep its name: the loader and cache manifests use it. The name comes from an older
version of the pipeline.

## Run

Run these commands from the project root:

```bash
python3 preprocessing/pairs_csv_pipeline/fix_lipid_smiles_from_linda.py \
    --input  data/unpreprocessed_files/Processed_dataset_smiles_completed.csv \
    --output data/unpreprocessed_files/pairs_1_smiles_fixed.csv

python3 preprocessing/pairs_csv_pipeline/complete_lipid_candidate_sets.py \
    --input  data/unpreprocessed_files/pairs_1_smiles_fixed.csv \
    --output data/unpreprocessed_files/pairs_2_candidates.csv \
    --report data/unpreprocessed_files/pairs_2_completion_report.csv \
    --duplicate-report data/unpreprocessed_files/pairs_2_merge_report.csv \
    --keep-spelling-variants --keep-duplicate-pairs --keep-head-group-names

python3 preprocessing/pairs_csv_pipeline/expand_positives_to_full_table.py \
    --input  data/unpreprocessed_files/pairs_2_candidates.csv \
    --output data/unpreprocessed_files/pairs_3_full.csv

python3 preprocessing/pairs_csv_pipeline/complete_lipid_candidate_sets.py \
    --input  data/unpreprocessed_files/pairs_3_full.csv \
    --output data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv
```

1. Correct SMILES using the 27 OLD-to-NEW groups in
  `$U/lipid_data_iso_correct_FROM_LINDA.csv`. Match rows by `(Lipid, ChainFragments)`.
  Also replace a `//` typo in five sphingolipid SMILES. The recorded run changed 78 entries across 71 rows.

2. Complete candidate sets. Give every row of a lipid all candidates listed for that lipid anywhere in the table.
The three `--keep-*` flags postpone head-group correction, spelling standardisation, and merging until step 4.

3. Add one negative row for each unmeasured protein-lipid pair, with `Interaction=0`.
Copy the lipid columns from its first positive row.
The recorded table had 11018 rows after this step.

4. Run the postponed corrections and merging on the full table.
In the recorded run, this completed 35 remaining rows, merged 1071 cells, and removed 1113 rows. The table went from 11018 to 9905 rows.

## Caches

The protein and lipid descriptor tables mostly rebuild themselves. The protein one
notices a new protein in `data/graphs/`. The lipid one notices the interaction
table's new size and mtime, and computes missing values directly until it is
rebuilt. The pair table does not: it holds one row per (candidate, protein) pair,
so new pairs need an explicit rebuild. `data/build_descriptor_cache.py` builds all
three together.

Tanimoto does not rebuild itself either, and `--tanimoto_weight` fails with
`FileNotFoundError` when its artifacts are older than the table.

```bash
python3 data/build_descriptor_cache.py --force
python3 preprocessing/similarity/build_tanimoto_compact.py
python3 preprocessing/similarity/build_tanimoto_compact.py --isomeric
```

For new MoLFormer embeddings see `../embeddings/AN_INSTRUCTION.md`:
`--skip-embedded` and `--merge` there encode only the ones that are new.
