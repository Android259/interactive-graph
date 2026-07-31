#!/usr/bin/env python3

import argparse
import pickle as pkl
from pathlib import Path

import pandas as pd
from rdkit import Chem


DEFAULT_INPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv"
)
DEFAULT_OUTPUT = Path("preprocessing/isomeric_smiles_before_encoding.pkl")
DEFAULT_CSV_OUTPUT = Path("preprocessing/isomeric_smiles_before_encoding.csv")
SMILES_COLUMNS = ("SmileGlobal", "SmileFragment")
EMPTY_VALUES = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def normalize_smiles_text(value):
    return "" if pd.isna(value) else str(value).strip()


def iter_raw_smiles(row):
    for column in SMILES_COLUMNS:
        text = normalize_smiles_text(row[column])
        if text in EMPTY_VALUES:
            continue
        for part in text.split(";"):
            candidate = part.strip()
            if candidate and candidate not in EMPTY_VALUES:
                yield candidate


def canonical_isomeric_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def collect_isomeric_smiles(table):
    smiles = []
    seen = set()
    invalid = []

    for row_index, row in table.iterrows():
        for raw_smiles in iter_raw_smiles(row):
            canonical = canonical_isomeric_smiles(raw_smiles)
            if canonical is None:
                invalid.append((row_index, raw_smiles))
                continue
            if canonical not in seen:
                smiles.append(canonical)
                seen.add(canonical)

    return smiles, invalid


def main():
    parser = argparse.ArgumentParser(
        description="Collect canonical isomeric lipid SMILES for MolFormer embedding."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    args = parser.parse_args()

    table = pd.read_csv(args.input)
    missing = [column for column in SMILES_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    smiles, invalid = collect_isomeric_smiles(table)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "wb") as handle:
        pkl.dump(smiles, handle)

    if args.csv_output:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"smile": smiles}).to_csv(args.csv_output, index=False)

    print(f"input rows: {len(table)}")
    print(f"unique canonical isomeric SMILES: {len(smiles)}")
    print(f"pickle output: {args.output}")
    if args.csv_output:
        print(f"csv output: {args.csv_output}")
    if invalid:
        print(f"invalid SMILES skipped: {len(invalid)}")
        for row_index, raw_smiles in invalid[:10]:
            print(f"  row {row_index}: {raw_smiles}")


if __name__ == "__main__":
    main()
