"""The interaction table shared by all runs.

lipid_isomers selects embeddings and stereochemistry handling, not the CSV.
The stereo-corrected table has completed candidate sets and merged repeated
measurements (preprocessing/complete_lipid_candidate_sets.py). Each lipid has
one candidate set and each (protein, lipid) cell appears once.

Merging 92 repeated cells removed 98 rows and changed pair IDs (row positions).
Rebuild row-indexed artifacts: compact Tanimoto files, the full matrix, and its
row-ID vector. The compact manifest records the source; stale files are rejected.
"""

import os


INTERACTION_CSV = (
    "Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed"
    "_CandidatesCompleted_Deduplicated.csv"
)


def interaction_csv_path(data_dir):
    """Absolute path of the interaction table inside a data directory."""
    return os.path.join(data_dir, INTERACTION_CSV)
