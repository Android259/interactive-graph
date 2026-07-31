#!/usr/bin/env python3

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_REAL_IDENTITY_INPUT = Path(
    "data/Processed_dataset_real_fullidentity_by_smiles.csv"
)
DEFAULT_NEGATIVE_INPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_Stereo_Fixed.csv"
)
DEFAULT_OUTPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_Stereo_Fixed_RealIdentity.csv"
)
DEFAULT_MAPPING_OUTPUT = Path(
    "data/Processed_dataset_resolved_ambiguous_identity_mapping.csv"
)
DEFAULT_UNAPPLIED_OUTPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_Stereo_Fixed_UnresolvedIdentity.csv"
)

RESOLVED_STATUSES = {
    "selected_from_original",
    "selected_by_isomer_rules",
}


def normalized_identity(value):
    return " ".join(str(value).strip().split())


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Use resolved real FullIdentityOfLipid values to remove wrong "
            "variants from ambiguous identities in the stereo-fixed negative CSV."
        )
    )
    parser.add_argument("--real-identity-input", type=Path, default=DEFAULT_REAL_IDENTITY_INPUT)
    parser.add_argument("--negative-input", type=Path, default=DEFAULT_NEGATIVE_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mapping-output", type=Path, default=DEFAULT_MAPPING_OUTPUT)
    parser.add_argument("--unapplied-output", type=Path, default=DEFAULT_UNAPPLIED_OUTPUT)
    args = parser.parse_args()

    real_identity = pd.read_csv(args.real_identity_input, sep=";")
    negative = pd.read_csv(args.negative_input)

    ambiguous = real_identity[
        real_identity["OriginalFullIdentityOfLipid"].astype(str).str.contains(";", regex=False)
    ].copy()
    resolved = ambiguous[
        ambiguous["IdentityInferenceStatus"].isin(RESOLVED_STATUSES)
        & (
            ambiguous["OriginalFullIdentityOfLipid"].astype(str)
            != ambiguous["RealFullIdentityOfLipid"].astype(str)
        )
    ].copy()

    mapping_rows = []
    mapping = {}
    for _, row in resolved.iterrows():
        original = str(row["OriginalFullIdentityOfLipid"]).strip()
        real = str(row["RealFullIdentityOfLipid"]).strip()
        key = normalized_identity(original)
        if key in mapping and mapping[key] != real:
            continue
        mapping[key] = real
        mapping_rows.append(
            {
                "OriginalFullIdentityOfLipid": original,
                "RealFullIdentityOfLipid": real,
                "Lipid": row["Lipid"],
                "InferredClassFromSMILES": row["InferredClassFromSMILES"],
                "IdentityInferenceStatus": row["IdentityInferenceStatus"],
            }
        )

    mapping_table = pd.DataFrame(mapping_rows).drop_duplicates()
    mapping_table.to_csv(args.mapping_output, sep=";", index=False)

    output = negative.copy()
    output["OriginalFullIdentityOfLipid"] = output["FullIdentityOfLipid"]
    output["IdentityCorrectionStatus"] = "unchanged"

    unresolved_rows = []
    changed_count = 0
    ambiguous_count = 0
    for index, value in output["FullIdentityOfLipid"].items():
        text = str(value).strip()
        if ";" not in text:
            continue
        ambiguous_count += 1
        key = normalized_identity(text)
        if key in mapping:
            output.at[index, "FullIdentityOfLipid"] = mapping[key]
            output.at[index, "IdentityCorrectionStatus"] = "resolved_from_real_identity"
            changed_count += 1
        else:
            output.at[index, "IdentityCorrectionStatus"] = "ambiguous_unresolved_no_mapping"
            unresolved_rows.append(output.loc[index].to_dict())

    output.to_csv(args.output, index=False)
    pd.DataFrame(unresolved_rows).to_csv(args.unapplied_output, index=False)

    print(f"Wrote mapping: {args.mapping_output}")
    print(f"Wrote output: {args.output}")
    print(f"Wrote unresolved: {args.unapplied_output}")
    print(f"Resolved mapping rows: {len(mapping_table)}")
    print(f"Ambiguous rows in negative input: {ambiguous_count}")
    print(f"Changed rows in negative output: {changed_count}")
    print(f"Unresolved ambiguous rows in negative output: {len(unresolved_rows)}")


if __name__ == "__main__":
    main()
