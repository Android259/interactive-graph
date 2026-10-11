#!/usr/bin/env python3
"""Rewrite each protein's ProteinDomain to the single value its positive rows agree on.

Used as a one-time cleanup pass over an interaction CSV whose ProteinDomain column
is inconsistent for some LTPProtein (e.g. copied inconsistently across rows): this
infers the correct domain per protein from its Interaction==1 rows and overwrites
every row of that protein with it. Raises if a protein's positive rows disagree
on ProteinDomain, or if a protein has no positive rows to infer from.

Usage:
    python3 preprocessing/correct_protein_domains.py input.csv output.csv
"""

import argparse
from pathlib import Path

import pandas as pd


def correct_protein_domains(frame):
    required = {"LTPProtein", "ProteinDomain", "Interaction"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    positive = frame[frame["Interaction"].eq(1)]
    if positive.empty:
        raise ValueError("No positive rows found")

    domain_counts = positive.groupby("LTPProtein")["ProteinDomain"].nunique(
        dropna=False
    )
    ambiguous = domain_counts[domain_counts.ne(1)].index.tolist()
    if ambiguous:
        raise ValueError(
            "Positive rows contain ambiguous ProteinDomain values for: "
            + ", ".join(ambiguous)
        )

    domain_map = (
        positive.groupby("LTPProtein", sort=False)["ProteinDomain"]
        .first()
        .to_dict()
    )
    missing_proteins = sorted(set(frame["LTPProtein"]) - set(domain_map))
    if missing_proteins:
        raise ValueError(
            "No positive-row domain mapping for: "
            + ", ".join(missing_proteins)
        )

    corrected = frame.copy()
    corrected["ProteinDomain"] = corrected["LTPProtein"].map(domain_map)
    return corrected


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create a copy of an interaction CSV with ProteinDomain inferred "
            "from positive rows for each LTPProtein."
        )
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.input_csv.resolve() == args.output_csv.resolve():
        raise ValueError("Input and output paths must be different")

    original = pd.read_csv(args.input_csv)
    corrected = correct_protein_domains(original)
    changed = int(
        original["ProteinDomain"].ne(corrected["ProteinDomain"]).sum()
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    corrected.to_csv(args.output_csv, index=False)

    print(f"Wrote: {args.output_csv}")
    print(f"Rows: {len(corrected)}")
    print(f"Corrected ProteinDomain cells: {changed}")


if __name__ == "__main__":
    main()
