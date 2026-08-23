"""The single interaction table every run reads.

`lipid_isomers` used to pick the CSV as well as the embedding table, so the two lipid
representations ran on different files. It no longer does: this one file serves both,
and the flag now selects only the embedding table and whether canonicalization keeps
stereochemistry.

The file is the stereo-corrected table with its candidate lists completed and its
repeated measurements merged (`preprocessing/complete_lipid_candidate_sets.py`), so every
row of a lipid lists the same isomer set and every (protein, lipid) cell appears exactly
once: 10920 rows, the full 35 x 312 grid, 658 of them positive.

Row order and row count are NOT those of the earlier table -- merging the 92 repeatedly
measured cells removed 98 rows -- so pair IDs, which are original row positions, changed
with it. Everything indexed by them has to be rebuilt against this file: the compact
Tanimoto artifacts (their manifest records the source and the loader refuses a stale
one), the full Tanimoto matrix and its row-id vector, and the GRAB pair-graph edges.
"""

import os


INTERACTION_CSV = (
    "Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed"
    "_CandidatesCompleted_Deduplicated.csv"
)


def interaction_csv_path(data_dir):
    """Absolute path of the interaction table inside a data directory."""
    return os.path.join(data_dir, INTERACTION_CSV)
