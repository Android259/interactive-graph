#!/usr/bin/env python3

# Ambiguous FullIdentityOfLipid resolution rules.
#
# Input ambiguity syntax:
# - Alternative lipid identities are separated by semicolon:
#   "Sphingomyelin (d42:1);Sphingomyelin (DH42:1)".
# - The lipid class is the text before the first parenthesis:
#   "Sphingomyelin", "Hexosyl ceramide", "Ceramide".
# - The lipid code is the text inside the first parenthesis:
#   "d42:1", "DH42:1", "t42:2", "d42:2-OH".
# - For identities with explicit chains, the part after "=>" is kept as part
#   of the selected identity:
#   "Hexosyl ceramide (d42:2) => (d18:1/24:1)".
#
# Class-level choice:
# - The SMILES is converted to RDKit graph features by
#   audit_lipid_identity_by_smiles.features().
# - infer_class() returns one structural class, for example "HexCer", "SM",
#   "PG", "PC", "Ceramide".
# - If only one semicolon-separated identity has this class, that identity is
#   selected directly.
# - If no identity has this class, the row is not forced. It is reported as
#   "inferred_class_not_in_original".
# - "Unknown" is not treated as a lipid class. It means "not resolved by the
#   current rules".
#
# Isomer-level choice for sphingolipids:
# - If several alternatives have the same class, the script compares the code
#   inside parentheses with SMILES syntax.
# - "d..." means sphingoid base with C4/C5 unsaturation. In SMILES this is
#   recognized by a double bond immediately after the hydroxylated sphingoid
#   carbon, for example:
#     ")(O)/C=C", ")(O)\C=C", "](O)/C=C", "](O)\C=C".
# - "DH..." means dihydro sphingoid base. It is selected when that sphingoid
#   C4/C5 double bond is absent.
# - "t..." means trihydroxy sphingoid base. It is preferred over "d...-OH"
#   when there is no hydroxyl on the amide fatty-acyl chain.
# - "...-OH" means an extra hydroxyl on the amide fatty-acyl chain. In SMILES
#   this is recognized near the amide carbonyl by patterns such as:
#     "NC(C(O)", "NC([C@H](O)", "NC([C@@H](O)",
#     "NC(=O)C(O)", "NC(=O)[C@H](O)", "NC(=O)[C@@H](O)".
# - If the best isomer score is tied, the script does not choose. It reports
#   "ambiguous_unresolved_same_class".
#
# Output policy:
# - The original dataset is never overwritten.
# - RealFullIdentityOfLipid contains the selected identity when rules are
#   decisive.
# - Unresolved rows are written separately for manual review.

import argparse
from pathlib import Path

import pandas as pd

try:
    from rdkit import RDLogger
except ModuleNotFoundError:
    RDLogger = None

from audit_lipid_identity_by_smiles import (
    FATTY_ACYL_NAMES,
    NAME_TO_CLASS,
    SMILES_COLUMNS,
    expected_classes,
    features,
    infer_class,
)


DEFAULT_INPUT = Path("data/Processed_dataset.csv")
DEFAULT_OUTPUT = Path("data/Processed_dataset_real_fullidentity_by_smiles.csv")
DEFAULT_UNRESOLVED_OUTPUT = Path("data/Processed_dataset_real_fullidentity_unresolved.csv")


CLASS_TO_CANONICAL_FULLIDENTITY = {
    "Sphingomyelin": "Sphingomyelin",
    "Ceramide phosphate": "Ceramide phosphate",
    "SHexCer": "Sulfohexosyl ceramide",
    "Hex2Cer": "Dihexosyl ceramide",
    "HexCer": "Hexosyl ceramide",
    "Ceramide": "Ceramide",
    "Cardiolipin": "Cardiolipin",
    "BMP": "Bismonoacylglycerolphosphate",
    "PC": "Phosphatidylcholine",
    "PE": "Phosphatidylethanolamine",
    "PG": "Phosphatidylglycerol",
    "PI": "Phosphatidylinositol",
    "PS": "Phosphatidylserine",
    "LPC": "Lysophosphatidylcholine",
    "LPE": "Lysophosphatidylethanolamine",
    "LPG": "Lysophosphatidylglycerol",
    "TAG": "Triacylglycerol",
    "DAG": "Diacylglycerol",
    "Fatty acyl": "Fatty acyl",
    "Retinol": "Retinol",
}


def valid_smiles(value):
    if pd.isna(value):
        return False
    text = str(value).strip()
    return bool(text) and text != "0" and text.lower() != "nan"


def identity_part_class(identity_part):
    name = identity_part.split("=>", 1)[0].split("(", 1)[0].strip()
    name = name.strip('"').strip()
    if name in NAME_TO_CLASS:
        return NAME_TO_CLASS[name]
    if name in FATTY_ACYL_NAMES:
        return "Fatty acyl"
    return "Unknown"


def has_sphingoid_double_bond(smiles):
    return (
        "](O)/C=C" in smiles
        or "](O)\\C=C" in smiles
        or "](O)C=C" in smiles
        or ")(O)/C=C" in smiles
        or ")(O)\\C=C" in smiles
        or ")(O)C=C" in smiles
        or "](O)/C=C" in smiles.replace("[H]", "")
        or ")(O)/C=C" in smiles.replace("[H]", "")
    )


def has_fatty_acyl_hydroxyl(smiles):
    return (
        "NC(C(O)" in smiles
        or "NC([C@H](O)" in smiles
        or "NC([C@@H](O)" in smiles
        or "NC(=O)C(O)" in smiles
        or "NC(=O)[C@H](O)" in smiles
        or "NC(=O)[C@@H](O)" in smiles
    )


def identity_part_code(identity_part):
    start = identity_part.find("(")
    end = identity_part.find(")", start + 1)
    if start == -1 or end == -1:
        return ""
    return identity_part[start + 1 : end].strip()


def score_sphingolipid_isomer(identity_part, smiles):
    code = identity_part_code(identity_part)
    if not code:
        return 0

    sphingoid_unsaturated = has_sphingoid_double_bond(smiles)
    fatty_acyl_hydroxyl = has_fatty_acyl_hydroxyl(smiles)
    score = 0

    if code.startswith("DH"):
        score += 2 if not sphingoid_unsaturated else -2
    elif code.startswith("d"):
        score += 2 if sphingoid_unsaturated else -2
    elif code.startswith("t"):
        score += 2 if not fatty_acyl_hydroxyl else -2

    if "-OH" in code:
        score += 3 if fatty_acyl_hydroxyl else -3
    elif code.startswith("d") and fatty_acyl_hydroxyl:
        score -= 1

    return score


def choose_by_isomer_rules(matching_parts, inferred_class, smiles):
    if inferred_class not in {
        "Sphingomyelin",
        "Ceramide phosphate",
        "SHexCer",
        "Hex2Cer",
        "HexCer",
        "Ceramide",
    }:
        return ""

    scored = [
        (score_sphingolipid_isomer(part, smiles), part)
        for part in matching_parts
    ]
    scored.sort(reverse=True)
    if not scored or scored[0][0] <= 0:
        return ""
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return ""
    return scored[0][1]


def choose_real_fullidentity(original_identity, inferred_class, smiles):
    parts = [part.strip() for part in str(original_identity).split(";") if part.strip()]
    matching_parts = [
        part for part in parts if identity_part_class(part) == inferred_class
    ]
    if len(matching_parts) == 1:
        return ";".join(matching_parts), "selected_from_original"
    if len(matching_parts) > 1:
        isomer_match = choose_by_isomer_rules(matching_parts, inferred_class, smiles)
        if isomer_match:
            return isomer_match, "selected_by_isomer_rules"
        return original_identity, "ambiguous_unresolved_same_class"

    if inferred_class == "Unknown":
        return original_identity, "unknown_keep_original"

    canonical = CLASS_TO_CANONICAL_FULLIDENTITY.get(inferred_class, inferred_class)
    return canonical, "inferred_class_not_in_original"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Infer real FullIdentityOfLipid from SMILES using the same RDKit "
            "feature rules as audit_lipid_identity_by_smiles.py."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--unresolved-output", type=Path, default=DEFAULT_UNRESOLVED_OUTPUT)
    args = parser.parse_args()

    if RDLogger is not None:
        RDLogger.DisableLog("rdApp.*")

    table = pd.read_csv(args.input, sep=";")
    output = table.copy()

    real_fullidentities = []
    inferred_classes = []
    expected_class_values = []
    identity_statuses = []
    smiles_columns = []

    for _, row in table.iterrows():
        smiles_column = ""
        smiles = ""
        for column in SMILES_COLUMNS:
            if valid_smiles(row[column]):
                smiles_column = column
                smiles = str(row[column]).strip()
                break

        if not smiles:
            inferred_class = "Unknown"
            real_fullidentity = row["FullIdentityOfLipid"]
            identity_status = "no_smiles_keep_original"
        else:
            inferred_class = infer_class(features(smiles))
            real_fullidentity, identity_status = choose_real_fullidentity(
                row["FullIdentityOfLipid"], inferred_class, smiles
            )

        expected = "|".join(expected_classes(row["FullIdentityOfLipid"]))
        expected_class_values.append(expected)
        inferred_classes.append(inferred_class)
        real_fullidentities.append(real_fullidentity)
        identity_statuses.append(identity_status)
        smiles_columns.append(smiles_column)

    output["OriginalFullIdentityOfLipid"] = output["FullIdentityOfLipid"]
    output["RealFullIdentityOfLipid"] = real_fullidentities
    output["InferredClassFromSMILES"] = inferred_classes
    output["OriginalExpectedClasses"] = expected_class_values
    output["IdentityInferenceStatus"] = identity_statuses
    output["IdentitySMILESColumn"] = smiles_columns

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, sep=";", index=False)

    unresolved = output[
        output["IdentityInferenceStatus"].isin(
            [
                "ambiguous_unresolved_same_class",
                "inferred_class_not_in_original",
                "unknown_keep_original",
                "no_smiles_keep_original",
            ]
        )
    ].copy()
    unresolved.to_csv(args.unresolved_output, sep=";", index=False)

    print(f"Wrote: {args.output}")
    print(f"Wrote unresolved: {args.unresolved_output}")
    print(f"Rows: {len(output)}")
    print(f"Unresolved rows: {len(unresolved)}")
    print(output["IdentityInferenceStatus"].value_counts().to_string())


if __name__ == "__main__":
    main()
