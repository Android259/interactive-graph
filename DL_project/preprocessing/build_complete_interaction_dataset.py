#!/usr/bin/env python3

import argparse
from itertools import product
from pathlib import Path

import pandas as pd


PAIR_COLUMNS = ["LTPProtein", "FullIdentityOfLipid"]
LIPID_METADATA_COLUMNS = [
    "SmileGlobal",
    "SmileFragment",
    "Lipid",
    "ChainFragments",
]
OUTPUT_COLUMNS = [
    "SmileGlobal",
    "SmileFragment",
    "LTPProtein",
    "ProteinDomain",
    "FullIdentityOfLipid",
    "Lipid",
    "ChainFragments",
    "Screen",
    "Interaction",
    "index",
]


def stable_unique(values):
    result = []
    seen = set()
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if not text or text.lower() == "nan" or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def join_unique(values):
    return "; ".join(stable_unique(values))


def join_unique_list_items(values):
    items = []
    for value in stable_unique(values):
        items.extend(part.strip() for part in value.split(";"))
    return "; ".join(stable_unique(items))


def validate_input(frame):
    required = set(PAIR_COLUMNS)
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if frame[PAIR_COLUMNS].isna().any().any():
        raise ValueError("Protein and lipid identifiers must not be empty")


def infer_protein_domains(positive_frame):
    if "ProteinDomain" not in positive_frame.columns:
        raise ValueError("Missing required column: ProteinDomain")

    domains = {}
    for protein, group in positive_frame.groupby("LTPProtein", sort=False):
        values = stable_unique(group["ProteinDomain"])
        if len(values) != 1:
            raise ValueError(
                f"Expected one ProteinDomain for {protein}, found: {values}"
            )
        domains[protein] = values[0]
    return domains


def aggregate_lipid_metadata(frame, lipids):
    available = [
        column for column in LIPID_METADATA_COLUMNS if column in frame.columns
    ]
    grouped = frame.groupby("FullIdentityOfLipid", sort=False)
    metadata = {}

    for lipid in lipids:
        group = grouped.get_group(lipid)
        values = {}
        for column in available:
            aggregate = join_unique if column == "Lipid" else join_unique_list_items
            values[column] = aggregate(group[column])
        for column in LIPID_METADATA_COLUMNS:
            values.setdefault(column, "")
        metadata[lipid] = values

    return metadata


def build_complete_dataset(frame):
    validate_input(frame)

    if "Interaction" in frame.columns:
        labels = pd.to_numeric(frame["Interaction"], errors="raise")
        positive_frame = frame.loc[labels.eq(1)].copy()
    else:
        positive_frame = frame.copy()

    if positive_frame.empty:
        raise ValueError("Input contains no positive interactions")

    proteins = stable_unique(positive_frame["LTPProtein"])
    lipids = stable_unique(positive_frame["FullIdentityOfLipid"])
    protein_domains = infer_protein_domains(positive_frame)
    lipid_metadata = aggregate_lipid_metadata(positive_frame, lipids)

    positive_pairs = set(
        positive_frame[PAIR_COLUMNS].itertuples(index=False, name=None)
    )
    screens = (
        positive_frame.groupby(PAIR_COLUMNS, sort=False)["Screen"]
        .agg(join_unique)
        .to_dict()
        if "Screen" in positive_frame.columns
        else {}
    )

    rows = []
    for protein, lipid in product(proteins, lipids):
        pair = (protein, lipid)
        row = dict(lipid_metadata[lipid])
        row.update(
            {
                "LTPProtein": protein,
                "ProteinDomain": protein_domains[protein],
                "FullIdentityOfLipid": lipid,
                "Screen": screens.get(pair, ""),
                "Interaction": int(pair in positive_pairs),
            }
        )
        rows.append(row)

    result = pd.DataFrame(rows)
    result = result.sort_values(
        ["Interaction"], ascending=False, kind="stable"
    ).reset_index(drop=True)
    result["index"] = result.index
    return result[OUTPUT_COLUMNS]


def read_table(path):
    frame = pd.read_csv(path)
    if len(frame.columns) == 1 and ";" in frame.columns[0]:
        frame = pd.read_csv(path, sep=";")
    return frame


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Build one row for every unique protein-lipid pair without "
            "duplicate pairs or copied protein metadata."
        )
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    frame = read_table(args.input_csv)
    result = build_complete_dataset(frame)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output_csv, index=False)

    print(f"Wrote {len(result)} rows to {args.output_csv}")
    print(
        f"Positive: {int(result['Interaction'].sum())}; "
        f"negative: {int(result['Interaction'].eq(0).sum())}"
    )


if __name__ == "__main__":
    main()
