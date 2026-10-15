#!/usr/bin/env python3

# Build the compact Tanimoto artifacts from the interaction table.
#
# Store one row per distinct candidate structure. Candidate similarity is
# compact[structure_index[i], structure_index[j]]. Morgan radius 2, 1024 bits;
# Tanimoto values are stored as round(similarity * 255).
#
# Use SmileGlobal unless it is "0", then SmileFragment. Split on ";", canonicalize
# and deduplicate within each row. Isomeric mode writes separate artifacts.
#
# Output (dataloader/tensors_reading/tanimoto_compact_tensors_reader.py reads them):
#   Tanimoto_compact_matrix_uint8.pt       structures x structures
#   Tanimoto_compact_structure_index.pt    candidate -> structure row
#   Tanimoto_compact_row_ids.pt            candidate -> interaction table row
#   Tanimoto_compact.manifest.json         counts + the source table's size and mtime
#
# Usage:
#     python3 preprocessing/similarity/build_tanimoto_compact.py [--data-dir DIR] [--input CSV]
#                                                     [--isomeric]

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dataloader.dataset_source import INTERACTION_CSV
from dataloader.cache_builders.tanimoto_compact_tensors_builder import write_compact


DEFAULT_DATA_DIR = Path("data")


def row_candidates(smile_global, smile_fragment, isomeric=False):
    """Canonical candidates in field order, optionally retaining stereochemistry."""
    # Keep the loader's exact "0" comparison before trimming candidate strings.
    text = str(smile_global)
    if text == "0":
        text = str(smile_fragment)

    candidates = []
    for part in text.split(";"):
        part = part.strip()
        if not part or part == "0":
            continue
        mol = Chem.MolFromSmiles(part)
        if mol is None or mol.GetNumAtoms() == 0:
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)
        if canonical not in candidates:
            candidates.append(canonical)
    return candidates


def collect(table, isomeric=False):
    smiles, row_ids, empty_rows = [], [], []
    for position, (smile_global, smile_fragment) in enumerate(
        zip(table["SmileGlobal"], table["SmileFragment"])
    ):
        candidates = row_candidates(smile_global, smile_fragment, isomeric=isomeric)
        if not candidates:
            empty_rows.append(position)
            continue
        smiles.extend(candidates)
        row_ids.extend([position] * len(candidates))
    if empty_rows:
        raise ValueError(
            f"{len(empty_rows)} rows carry no parsable SMILES (first: {empty_rows[0]}); "
            "they would silently drop out of every weighting"
        )
    return smiles, np.asarray(row_ids, dtype=np.int32)


def tanimoto_matrix(smiles, radius=2, n_bits=1024, progress_every=5000):
    fingerprints = [
        AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(item), radius, n_bits)
        for item in smiles
    ]
    size = len(fingerprints)
    matrix = np.zeros((size, size), dtype=np.uint8)
    for index in range(size):
        similarities = DataStructs.BulkTanimotoSimilarity(
            fingerprints[index], fingerprints[index:]
        )
        row = np.round(np.asarray(similarities, dtype=np.float32) * 255).astype(np.uint8)
        matrix[index, index:] = row
        matrix[index:, index] = row
        matrix[index, index] = 255
        if progress_every and index and index % progress_every == 0:
            print(f"  {index}/{size}", flush=True)
    return matrix


def distinct_structures(smiles):
    """Distinct canonical SMILES in first-appearance order, and each candidate's row."""
    order = {}
    for item in smiles:
        if item not in order:
            order[item] = len(order)
    structure_index = np.asarray([order[item] for item in smiles], dtype=np.int32)
    return list(order), structure_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument(
        "--isomeric",
        action="store_true",
        help=(
            "Canonicalize with stereochemistry, matching a run with --lipid_isomers. "
            "Writes a separate set of files: the two modes disagree on how many "
            "candidates a row has, so their artifacts are not interchangeable."
        ),
    )
    args = parser.parse_args()
    RDLogger.DisableLog("rdApp.*")

    input_csv = args.input or (args.data_dir / INTERACTION_CSV)
    table = pd.read_csv(input_csv)
    print(f"input: {input_csv} ({len(table)} rows)")
    print(f"mode: {'isomeric' if args.isomeric else 'non-isomeric'}")

    smiles, row_ids = collect(table, isomeric=args.isomeric)
    structures, structure_index = distinct_structures(smiles)
    print(f"candidates: {len(smiles)} over {len(set(row_ids.tolist()))} rows")
    print(f"distinct structures: {len(structures)}")
    print(
        f"compact matrix: {len(structures)}x{len(structures)} uint8 "
        f"({len(structures) ** 2 / 2**20:.1f} MiB) "
        f"instead of {len(smiles)}x{len(smiles)} ({len(smiles) ** 2 / 1e9:.2f} GB)"
    )

    compact = tanimoto_matrix(structures)

    written = write_compact(
        args.data_dir,
        compact,
        structure_index,
        row_ids,
        input_csv,
        isomeric=args.isomeric,
    )
    for path in written:
        print(f"written: {path}")


if __name__ == "__main__":
    main()
