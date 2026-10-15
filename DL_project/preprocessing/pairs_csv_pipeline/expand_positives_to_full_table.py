#!/usr/bin/env python3
"""Add the negative complement to the positive-pair table.

Third step of the pipeline (see AN_INSTRUCTION.md). The input is the measured rows
after their corrections; this writes the full protein x lipid table: the positive rows
unchanged and in their own order, then, for every cell nobody measured, one row
labelled `Interaction=0`.

Row order is what pair IDs are, so it is fixed:

  * the positive rows first, in the order they arrive;
  * then the negatives, protein-major in the order proteins first appear among the
    positives, and inside a protein in the order the lipid names first appear.

A negative cell was never measured and has no data of its own, so every lipid column
is copied from the lipid's first positive row exactly as it stands.

The input may still hold a cell as two rows (one per repeated measurement). The
complement is taken over the distinct cells and those rows are passed through, for
`complete_lipid_candidate_sets.py` to merge in the step after this one.

`ProteinDomain` comes from the protein's own positive rows. `index` is the lipid's
position in the lipid order above, left empty on positive rows, and `Unnamed: 0`
continues the numbering the positive rows carry; the loader reads neither, they are
kept because the table has them.

Usage:
    python3 preprocessing/pairs_csv_pipeline/expand_positives_to_full_table.py \
        --input positives.csv --output full_table.csv
"""

import argparse
from pathlib import Path

import pandas as pd


PAIR_COLUMNS = ["LTPProtein", "FullIdentityOfLipid"]


def first_appearance(values):
    """Distinct values in the order they first appear."""
    seen = set()
    order = []
    for value in values:
        if value not in seen:
            seen.add(value)
            order.append(value)
    return order


def validate_positives(table):
    missing = [column for column in PAIR_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if "Interaction" in table.columns:
        labels = pd.to_numeric(table["Interaction"], errors="raise")
        if not labels.eq(1).all():
            raise ValueError(
                "Input must contain positive rows only; found "
                f"{int(labels.ne(1).sum())} rows with Interaction != 1"
            )

    duplicated = int(table.duplicated(PAIR_COLUMNS).sum())
    if duplicated:
        print(
            f"note: {duplicated} repeated (protein, lipid) cells in the input, kept "
            "as they are for complete_lipid_candidate_sets.py to merge"
        )

    domains = table.groupby("LTPProtein", sort=False)["ProteinDomain"].nunique()
    ambiguous = domains[domains.ne(1)].index.tolist()
    if ambiguous:
        raise ValueError("Ambiguous ProteinDomain for: " + ", ".join(ambiguous))


def expand_to_full_table(table):
    validate_positives(table)

    proteins = first_appearance(table["LTPProtein"])
    lipids = first_appearance(table["FullIdentityOfLipid"])
    lipid_position = {lipid: position for position, lipid in enumerate(lipids)}

    domains = table.groupby("LTPProtein", sort=False)["ProteinDomain"].first().to_dict()
    representative = {
        lipid: group.iloc[0]
        for lipid, group in table.groupby("FullIdentityOfLipid", sort=False)
    }
    measured = set(table[PAIR_COLUMNS].itertuples(index=False, name=None))

    if "Unnamed: 0" in table.columns:
        numbers = pd.to_numeric(table["Unnamed: 0"], errors="coerce")
        next_number = int(numbers.max()) + 1 if numbers.notna().any() else len(table)
    else:
        next_number = len(table)

    negatives = []
    for protein in proteins:
        for lipid in lipids:
            if (protein, lipid) in measured:
                continue
            source = representative[lipid]
            row = {column: source[column] for column in table.columns}
            row["LTPProtein"] = protein
            row["ProteinDomain"] = domains[protein]
            row["FullIdentityOfLipid"] = lipid
            row["Interaction"] = 0
            if "index" in table.columns:
                row["index"] = lipid_position[lipid]
            if "Unnamed: 0" in table.columns:
                row["Unnamed: 0"] = next_number
                next_number += 1
            negatives.append(row)

    result = pd.concat(
        [table, pd.DataFrame(negatives, columns=table.columns)], ignore_index=True
    )
    return result[table.columns]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Write the full protein x lipid interaction table from the corrected "
            "positive-pair table."
        )
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.input.resolve() == args.output.resolve():
        raise ValueError("Input and output paths must be different")

    table = pd.read_csv(args.input)
    result = expand_to_full_table(table)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)

    positive = int(pd.to_numeric(result["Interaction"]).eq(1).sum())
    proteins = result["LTPProtein"].nunique()
    lipids = result["FullIdentityOfLipid"].nunique()
    print(f"Wrote {len(result)} rows to {args.output}")
    print(f"Proteins: {proteins}; lipids: {lipids}; grid: {proteins * lipids}")
    print(f"Positive: {positive}; negative: {len(result) - positive}")


if __name__ == "__main__":
    main()
