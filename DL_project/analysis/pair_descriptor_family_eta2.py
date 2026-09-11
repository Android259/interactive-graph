#!/usr/bin/env python3
"""Real eta^2 of the ACTUAL COMPUTED pair-descriptor value against protein family.

`descriptors_pair_clean` (scripts/arg_files/descriptors_pair_clean.md) was assembled
from PAIR_DESCRIPTOR_NAMES entries INFERRED safe because their protein-side component
alone is family-neutral-safe (eta^2 0.28-0.48, preprocessing/pocket_descriptor_
identity_check.py) and their lipid-side component is family-independent by
construction. That inference was never checked against the descriptor's own computed
VALUE, which multiplies (or takes min/ratio of) the two sides together -- a
combination CAN reintroduce family structure the protein component alone does not
have (e.g. if the lipid side correlates with which proteins happen to be screened
against which lipid classes in this dataset).

Methodology mirrors preprocessing/pocket_descriptor_identity_check.py exactly, at the
SAME granularity (one value per PROTEIN, not per row): dataloader.chemistry_prior.
raw_feature_matrix computes each descriptor's real value from real (protein, lipid)
pairs in the interaction table (pair_id granularity, one row per interaction), which
is then averaged over every lipid screened against a given protein to collapse back
to one number per protein -- the same thing pocket_descriptor_identity_check.py's own
POCKET_DESCRIPTOR_NAMES values already are (constant per protein). eta^2 of that
per-protein vector against ProteinDomain family, with the (k-1)/(n-1) arithmetic
floor for k=9 families over n=35 proteins, is then the same number, computed the same
way, as every other entry in files/descriptors_baseline_leak_confirmed.md's protein
eta^2 table.

Row-level eta^2 (no per-protein averaging: does a row's own value predict its
protein's family, pooling every lipid together) is printed alongside for context --
it is NOT the number requested by the methodology above (its floor is governed by
thousands of rows, not 35 proteins, so it is not comparable to the protein-side
table), but a row-level number well above ITS OWN floor while the per-protein one
sits at the family floor would say the descriptor's row-to-row variation still
tracks family despite being lipid-driven.

--zscore matches scripts/arg_files/descriptors_pair_clean.md's own --zscore flag, so
the value measured here is the value the config actually feeds the model, not the
unstandardised default.

Reads only. Trains nothing, appends to no shared table.

Usage:
    scripts/env.sh python3 analysis/pair_descriptor_family_eta2.py
    scripts/env.sh python3 analysis/pair_descriptor_family_eta2.py --names hbond_match,volume_fit
"""
import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)

from analysis.feature_identity_check import (  # noqa: E402
    eta_squared, group_floor, protein_family_map,
)
from dataloader.chemistry_prior import raw_feature_matrix  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402

DEFAULT_NAMES = (
    "aromatic_contact", "hbond_match", "volume_fit", "buriedness_match",
    "aromatic_contact_min", "hbond_match_min", "tail_elongation_fit",
    "hydropathy_rim_match", "elongation_shape_match", "flatness_shape_match",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--names", default=",".join(DEFAULT_NAMES))
    parser.add_argument("--zscore", action="store_true", default=True)
    parser.add_argument("--no-zscore", dest="zscore", action="store_false")
    args = parser.parse_args()
    names = [n for n in args.names.split(",") if n]

    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pandas.read_csv(interaction_csv_path(data_dir + "/"))
    protein_family = protein_family_map(csv)
    protein_col = csv["LTPProtein"].to_numpy()
    family_col = np.array([protein_family[p] for p in protein_col])

    proteins = sorted(protein_family)
    families_by_protein = np.array([protein_family[p] for p in proteins])
    floor = group_floor(families_by_protein)
    print(f"{len(proteins)} proteins, {len(pandas.unique(families_by_protein))} families, "
          f"arithmetic floor (k-1)/(n-1) = {floor:.3f}\n")

    rows = []
    for name in names:
        entities, matrix, entity_column, _ = raw_feature_matrix(csv, data_dir, [name], zscore=args.zscore)
        assert entity_column == "pair_id", f"{name}: expected pair_id granularity, got {entity_column}"
        values = matrix[:, 0]

        # Row-level, context only (see module docstring): does the row's own value
        # predict family, pooling every lipid the protein was screened against.
        row_eta2 = eta_squared(values, family_col)
        row_floor = group_floor(family_col)

        # Per-protein, the requested number: collapse to one value per protein by
        # averaging over every lipid screened against it, then eta^2 against family
        # over the 35 proteins -- same granularity as the protein-side table this is
        # compared against.
        frame = pandas.DataFrame({"protein": protein_col, "value": values})
        per_protein = frame.groupby("protein")["value"].mean()
        per_protein_values = np.array([per_protein[p] for p in proteins])
        protein_eta2 = eta_squared(per_protein_values, families_by_protein)

        rows.append({
            "descriptor": name,
            "eta2_per_protein": protein_eta2,
            "above_floor": protein_eta2 - floor,
            "eta2_row_level": row_eta2,
            "row_floor": row_floor,
        })

    table = pandas.DataFrame(rows).set_index("descriptor").sort_values("eta2_per_protein", ascending=False)
    pandas.set_option("display.width", 200)
    print(table.round(4).to_string())


if __name__ == "__main__":
    main()
