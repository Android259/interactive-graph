# Pairs CSV pipeline

Turns a table of positive protein-lipid pairs into the table training reads.
Add new measurements to the positive table, re-run the four commands, rebuild the
caches.

IN   `data/unpreprocessed_files/Processed_dataset_smiles_completed.csv`
     One row per measurement, `Interaction=1`, SMILES uncorrected. 756 rows now.

OUT  `data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv`
     9905 rows, read by `dataloader/Dataloader.py`. Its name records the steps of an
     older chain, not the ones below; the loader and every cache manifest key off that
     name, so it stays.

## Run

```bash
P=preprocessing/pairs_csv_pipeline
U=data/unpreprocessed_files

python3 $P/fix_lipid_smiles_from_linda.py \
    --input  $U/Processed_dataset_smiles_completed.csv \
    --output $U/pairs_1_smiles_fixed.csv

python3 $P/complete_lipid_candidate_sets.py \
    --input  $U/pairs_1_smiles_fixed.csv \
    --output $U/pairs_2_candidates.csv \
    --report $U/pairs_2_completion_report.csv \
    --duplicate-report $U/pairs_2_merge_report.csv \
    --keep-spelling-variants --keep-duplicate-pairs --keep-head-group-names

python3 $P/expand_positives_to_full_table.py \
    --input  $U/pairs_2_candidates.csv \
    --output $U/pairs_3_full.csv

python3 $P/complete_lipid_candidate_sets.py \
    --input  $U/pairs_3_full.csv \
    --output data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv
```

On today's input this reproduces the current table byte for byte: sha256
`a4d4eaece44b8cfca4f59eec4b87584a535e5fc6be041b2285efd2e391ccfc7b`, size 6330853 --
the size the Tanimoto and descriptor manifests pin, so it is the table every run so
far used. Check it with `sha256sum` before and after touching anything here.

## The four steps

1. **SMILES corrections.** The 27 OLD->NEW groups in
   `$U/lipid_data_iso_correct_FROM_LINDA.csv`, matched per row by
   `(Lipid, ChainFragments)`; also collapses a `//` typo in 5 sphingolipid SMILES.
   78 entries in 71 rows.

2. **Candidate completion.** Every row of a lipid gets the whole candidate set anyone
   listed for it, so the table stops depending on how thoroughly a row was annotated.
   81 rows.

   The three `--keep-*` flags hold back the script's other three stages -- head-group
   repair, spelling canonicalisation, cell merge -- for step 4. Those change what a row
   is called and whether it exists (312 spellings -> 283 species, 756 rows -> 634), and
   the complement is built over the spellings, so they have to run after it.

3. **Negative complement.** One row per unmeasured (protein, lipid) cell,
   `Interaction=0`, lipid columns copied verbatim from the lipid's first positive row.
   11018 rows.

4. **The three deferred stages**, now on the full table. Completes 35 remaining rows,
   merges 1071 cells, drops 1113 rows: 11018 -> 9905.

## Adding data

Append rows to the positive table. Required columns, in this order:
`Unnamed: 0, SmileGlobal, SmileFragment, LTPProtein, ProteinDomain,
FullIdentityOfLipid, Lipid, ChainFragments, Screen, Interaction, index`.

- `Unnamed: 0` continues the row numbering; `index` stays empty on positives. Neither
  is read by anything, but step 3 numbers the complement after them.
- Exactly one of `SmileGlobal` / `SmileFragment` holds the structures, the other holds
  `0`. Several candidate isomers of one species go in one field, separated by `; `.
  **New lipids need their SMILES supplied here** -- the script that fetched them from
  LIPID MAPS (`lipid_maps_fetch.py`) no longer runs: its input, its cached responses
  and its output are gone from the repository.
- `FullIdentityOfLipid` is the species name, `ChainFragments` the chain assignment
  (`(18:1/16:0)`) or empty. In the raw annotation they are one field split on `=>`.
- `ProteinDomain` must be the same for every row of a protein; step 3 refuses otherwise.
- A new protein also needs its graph and embeddings under `data/graphs/` and
  `data/esm3*/`; this pipeline only writes the table.

After rerunning: row positions are pair IDs, so **every artifact indexed by them has to
be rebuilt** -- the compact Tanimoto tables, the descriptor caches. Their manifests
record the source file's size and mtime and the loader refuses a stale one, but refusing
is not rebuilding.

## Notes

- `Processed_dataset_smiles_completed.csv` is the 756 `Interaction==1` rows of
  `$U/Processed_Negative_Interaction_Corrected_Domains.csv`, cut out unchanged. That
  table is the only surviving file of the older chain; the copy there was recovered
  from a LibreOffice backup.
- Also in this folder and not part of the above: `lipid_maps_fetch.py` (the dead
  LIPID MAPS fetch), `build_complete_interaction_dataset.py` and
  `correct_protein_domains.py` (the older chain's first two steps; step 3 above replaces
  the first, and the input already satisfies the second -- it corrects 0 cells).
