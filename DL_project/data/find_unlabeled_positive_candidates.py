#!/usr/bin/env python3
"""Rank unlabeled protein-lipid pairs using known interactions only."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator


RDLogger.DisableLog("rdApp.error")


REQUIRED_COLUMNS = {
    "SmileGlobal",
    "LTPProtein",
    "ProteinDomain",
    "FullIdentityOfLipid",
    "Lipid",
    "Screen",
    "Interaction",
}


def canonical_smiles_list(value):
    """Return unique valid canonical SMILES from a semicolon-separated cell."""
    canonical = []
    seen = set()
    if pd.isna(value):
        return canonical
    for raw_smiles in str(value).split(";"):
        raw_smiles = raw_smiles.strip()
        if not raw_smiles or raw_smiles == "0":
            continue
        molecule = Chem.MolFromSmiles(raw_smiles)
        if molecule is None:
            continue
        smiles = Chem.MolToSmiles(molecule, isomericSmiles=True)
        if smiles not in seen:
            seen.add(smiles)
            canonical.append(smiles)
    return canonical


def build_lipid_fingerprints(table, radius=2, fingerprint_size=2048):
    """Build all available Morgan fingerprints for each exact lipid identity."""
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=radius,
        fpSize=fingerprint_size,
    )
    fingerprints = {}
    for lipid_id, rows in table.groupby("FullIdentityOfLipid", sort=False):
        smiles = []
        seen = set()
        for value in rows["SmileGlobal"].drop_duplicates():
            for canonical in canonical_smiles_list(value):
                if canonical not in seen:
                    seen.add(canonical)
                    smiles.append(canonical)
        fingerprints[lipid_id] = [
            generator.GetFingerprint(Chem.MolFromSmiles(smile))
            for smile in smiles
        ]
    return fingerprints


def maximum_similarity(left, right):
    """Return the maximum Tanimoto similarity between two fingerprint sets."""
    if not left or not right:
        return None
    return max(
        DataStructs.TanimotoSimilarity(left_fp, right_fp)
        for left_fp in left
        for right_fp in right
    )


def nearest_positive_for_protein(
    candidate_lipid,
    positive_lipids,
    lipid_fingerprints,
):
    """Find the most chemically similar known positive lipid for one protein."""
    best_lipid = None
    best_similarity = None
    candidate_fingerprints = lipid_fingerprints.get(candidate_lipid, [])
    for positive_lipid in positive_lipids:
        similarity = maximum_similarity(
            candidate_fingerprints,
            lipid_fingerprints.get(positive_lipid, []),
        )
        if similarity is None:
            continue
        if best_similarity is None or similarity > best_similarity:
            best_lipid = positive_lipid
            best_similarity = similarity
    return best_lipid, best_similarity


def find_candidates(
    table,
    same_protein_similarity=0.70,
    min_family_exact_proteins=1,
):
    """Return ranked unlabeled pairs supported by both protein and family evidence."""
    missing = sorted(REQUIRED_COLUMNS - set(table.columns))
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")
    labels = set(table["Interaction"].dropna().astype(int).unique())
    if not labels <= {0, 1}:
        raise ValueError(f"Interaction must contain only 0 and 1, found {sorted(labels)}")

    table = table.copy()
    table["pair_id"] = table.index
    positives = table[table["Interaction"].astype(int) == 1]
    unlabeled = table[table["Interaction"].astype(int) == 0]
    lipid_fingerprints = build_lipid_fingerprints(table)
    missing_fingerprint_lipids = sum(
        not fingerprints for fingerprints in lipid_fingerprints.values()
    )

    positive_lipids_by_protein = (
        positives.groupby("LTPProtein")["FullIdentityOfLipid"]
        .apply(lambda values: set(values))
        .to_dict()
    )
    exact_family_proteins = defaultdict(set)
    exact_family_screen_proteins = defaultdict(set)
    for row in positives.itertuples(index=False):
        exact_family_proteins[
            (row.ProteinDomain, row.FullIdentityOfLipid)
        ].add(row.LTPProtein)
        exact_family_screen_proteins[
            (row.ProteinDomain, row.FullIdentityOfLipid, row.Screen)
        ].add(row.LTPProtein)

    records = []
    for row in unlabeled.itertuples(index=False):
        nearest_lipid, similarity = nearest_positive_for_protein(
            row.FullIdentityOfLipid,
            positive_lipids_by_protein.get(row.LTPProtein, set()),
            lipid_fingerprints,
        )
        family_proteins = exact_family_proteins[
            (row.ProteinDomain, row.FullIdentityOfLipid)
        ] - {row.LTPProtein}
        same_screen_proteins = exact_family_screen_proteins[
            (row.ProteinDomain, row.FullIdentityOfLipid, row.Screen)
        ] - {row.LTPProtein}
        protein_supported = (
            similarity is not None
            and similarity >= same_protein_similarity
        )
        family_supported = len(family_proteins) >= min_family_exact_proteins
        if not (protein_supported and family_supported):
            continue

        records.append(
            {
                "pair_id": row.pair_id,
                "LTPProtein": row.LTPProtein,
                "ProteinDomain": row.ProteinDomain,
                "FullIdentityOfLipid": row.FullIdentityOfLipid,
                "Lipid": row.Lipid,
                "Screen": row.Screen,
                "nearest_positive_lipid_same_protein": nearest_lipid,
                "nearest_positive_tanimoto": similarity,
                "exact_lipid_positive_family_protein_count": len(family_proteins),
                "exact_lipid_positive_family_proteins": ";".join(
                    sorted(family_proteins)
                ),
                "same_screen_family_protein_count": len(same_screen_proteins),
                "same_screen_family_proteins": ";".join(
                    sorted(same_screen_proteins)
                ),
            }
        )

    columns = [
        "pair_id",
        "LTPProtein",
        "ProteinDomain",
        "FullIdentityOfLipid",
        "Lipid",
        "Screen",
        "nearest_positive_lipid_same_protein",
        "nearest_positive_tanimoto",
        "exact_lipid_positive_family_protein_count",
        "exact_lipid_positive_family_proteins",
        "same_screen_family_protein_count",
        "same_screen_family_proteins",
    ]
    candidates = pd.DataFrame(records, columns=columns)
    if not candidates.empty:
        candidates = candidates.sort_values(
            [
                "exact_lipid_positive_family_protein_count",
                "same_screen_family_protein_count",
                "nearest_positive_tanimoto",
                "ProteinDomain",
                "LTPProtein",
                "pair_id",
            ],
            ascending=[False, False, False, True, True, True],
        ).reset_index(drop=True)
    candidates.attrs["lipid_identity_count"] = len(lipid_fingerprints)
    candidates.attrs["missing_fingerprint_lipid_count"] = missing_fingerprint_lipids
    return candidates


def print_summary(table, candidates):
    unlabeled = table[table["Interaction"].astype(int) == 0]
    total = len(unlabeled)
    candidate_count = len(candidates)
    fraction = candidate_count / total if total else 0.0
    print(f"Unlabeled pairs: {total}")
    print(f"Candidate pairs: {candidate_count}")
    print(f"Candidate fraction: {fraction:.4%}")
    lipid_count = candidates.attrs.get("lipid_identity_count")
    missing_count = candidates.attrs.get("missing_fingerprint_lipid_count")
    if lipid_count is not None and missing_count is not None:
        print(
            "Lipid identities with valid fingerprints: "
            f"{lipid_count - missing_count}/{lipid_count}"
        )
    print("\nCandidate fraction by protein group:")
    candidate_counts = candidates["ProteinDomain"].value_counts()
    for group, group_rows in unlabeled.groupby("ProteinDomain", sort=True):
        group_candidates = int(candidate_counts.get(group, 0))
        group_total = len(group_rows)
        print(
            f"  {group}: {group_candidates}/{group_total} "
            f"({group_candidates / group_total:.4%})"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/Processed_Negative_Interaction_Corrected_Domains.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/unlabeled_positive_candidates.csv"),
    )
    parser.add_argument(
        "--same-protein-similarity",
        type=float,
        default=0.70,
        help="Minimum Tanimoto similarity to a positive lipid of the same protein.",
    )
    parser.add_argument(
        "--min-family-exact-proteins",
        type=int,
        default=1,
        help=(
            "Minimum number of other proteins in the same family for which the "
            "exact candidate lipid is positive."
        ),
    )
    args = parser.parse_args()
    if not 0.0 <= args.same_protein_similarity <= 1.0:
        parser.error("--same-protein-similarity must be in [0, 1]")
    if args.min_family_exact_proteins < 1:
        parser.error("--min-family-exact-proteins must be at least 1")

    table = pd.read_csv(args.input)
    candidates = find_candidates(
        table,
        same_protein_similarity=args.same_protein_similarity,
        min_family_exact_proteins=args.min_family_exact_proteins,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(args.output, index=False)
    print_summary(table, candidates)
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
