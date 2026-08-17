"""The single interaction table every run reads.

`lipid_isomers` used to pick the CSV as well as the embedding table, so the two lipid
representations ran on different files. It no longer does: this one file serves both,
and the flag now selects only the embedding table and whether canonicalization keeps
stereochemistry.

The file is the stereo-corrected table with its candidate lists completed, so every row
of a lipid lists the same isomer set (`preprocessing/complete_lipid_candidate_sets.py`).
Row order and row count are those of the stereo-corrected table it was built from, so
pair IDs -- original row positions, used by Tanimoto weights and GRAB edges -- are
unchanged.
"""

import os


INTERACTION_CSV = (
    "Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed"
    "_CandidatesCompleted.csv"
)


def interaction_csv_path(data_dir):
    """Absolute path of the interaction table inside a data directory."""
    return os.path.join(data_dir, INTERACTION_CSV)
