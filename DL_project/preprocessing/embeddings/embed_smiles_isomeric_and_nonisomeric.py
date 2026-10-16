#!/usr/bin/env python3
"""Collect canonical candidate SMILES from the interaction table.

Read SmileGlobal/SmileFragment, split semicolon-separated candidates, canonicalise
with RDKit and remove duplicates. This script collects inputs; it does not embed them.
embed_isomeric_smiles_molformer.py reads the resulting list.

Writes a SMILES list, not an embedding table:

    default        -> unpreprocessed_files/isomeric_smiles_before_encoding.pkl
    --non-isomeric -> unpreprocessed_files/nonisomeric_smiles_all.pkl

The embedder turns either list into its own table
(lipid_SMILES_isomeric_embedding.pkl / lipid_SMILES_embedding_deterministic.pkl).

    python3 preprocessing/embeddings/embed_smiles_isomeric_and_nonisomeric.py
    python3 preprocessing/embeddings/embed_smiles_isomeric_and_nonisomeric.py --non-isomeric
    python3 preprocessing/embeddings/embed_smiles_isomeric_and_nonisomeric.py --non-isomeric \
        --skip-embedded data/lipid_SMILES_embedding_deterministic.pkl \
        --output data/unpreprocessed_files/nonisomeric_smiles_to_embed.pkl \
        --csv-output data/unpreprocessed_files/nonisomeric_smiles_to_embed.csv
"""

import argparse
import pickle as pkl
import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402

DEFAULT_INPUT = Path(interaction_csv_path(str(PROJECT_ROOT / "data")))
LIST_DIR = PROJECT_ROOT / "data" / "unpreprocessed_files"
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


def canonical_isomeric_smiles(smiles, isomeric=True):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)


def collect_isomeric_smiles(table, isomeric=True):
    smiles = []
    seen = set()
    invalid = []

    for row_index, row in table.iterrows():
        for raw_smiles in iter_raw_smiles(row):
            canonical = canonical_isomeric_smiles(raw_smiles, isomeric)
            if canonical is None:
                invalid.append((row_index, raw_smiles))
                continue
            if canonical not in seen:
                smiles.append(canonical)
                seen.add(canonical)

    return smiles, invalid


def read_embedded_keys(path):
    """The SMILES an existing embedding table already covers."""
    with open(path, "rb") as handle:
        return set(pkl.load(handle))


def main():
    parser = argparse.ArgumentParser(
        description="Collect canonical lipid SMILES for MolFormer embedding (--non-isomeric for the default table)."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--csv-output", type=Path, default=None)
    parser.add_argument(
        "--non-isomeric",
        action="store_true",
        help=(
            "Canonicalize without stereochemistry, for the table every run without "
            "--lipid_isomers reads (data/lipid_SMILES_embedding_deterministic.pkl). "
            "Switches the default output names to nonisomeric_smiles_all.*."
        ),
    )
    parser.add_argument(
        "--skip-embedded",
        type=Path,
        default=None,
        help=(
            "Existing embedding pickle; its keys are dropped from the output, so "
            "only the SMILES still missing are handed to the encoder."
        ),
    )
    args = parser.parse_args()

    stem = "nonisomeric_smiles_all" if args.non_isomeric else "isomeric_smiles_before_encoding"
    if args.output is None:
        args.output = LIST_DIR / f"{stem}.pkl"
    if args.csv_output is None:
        args.csv_output = LIST_DIR / f"{stem}.csv"

    table = pd.read_csv(args.input)
    missing = [column for column in SMILES_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    smiles, invalid = collect_isomeric_smiles(table, isomeric=not args.non_isomeric)
    collected = len(smiles)
    already_embedded = 0
    if args.skip_embedded is not None:
        embedded = read_embedded_keys(args.skip_embedded)
        smiles = [item for item in smiles if item not in embedded]
        already_embedded = collected - len(smiles)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "wb") as handle:
        pkl.dump(smiles, handle)

    if args.csv_output:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"smile": smiles}).to_csv(args.csv_output, index=False)

    kind = "non-isomeric" if args.non_isomeric else "isomeric"
    print(f"input rows: {len(table)}")
    print(f"unique canonical {kind} SMILES: {collected}")
    if args.skip_embedded is not None:
        print(f"already in {args.skip_embedded}: {already_embedded}")
        print(f"still to embed: {len(smiles)}")
    print(f"pickle output: {args.output}")
    if args.csv_output:
        print(f"csv output: {args.csv_output}")
    if invalid:
        print(f"invalid SMILES skipped: {len(invalid)}")
        for row_index, raw_smiles in invalid[:10]:
            print(f"  row {row_index}: {raw_smiles}")


if __name__ == "__main__":
    main()
