#!/usr/bin/env python3

# Rebuild the two Tanimoto artifacts from the interaction table.
#
# Both are indexed per *candidate SMILES*, not per row: a row that lists five isomer
# candidates contributes five entries, all carrying that row's id. So completing the
# candidate lists (preprocessing/complete_lipid_candidate_sets.py) changes their length
# -- 54627 entries for the table before completion, 59033 after -- and the two files
# only mean anything as a matched pair.
#
#   Total_multiple_lipid_batch.npy   the row id behind every candidate. Read by every
#                                    run: id2pos is built from it.
#   Total_tanimoto_matrix_uint8.npy  pairwise similarities over those same candidates,
#                                    similarity * 255. Read only under --tanimoto_weight.
#
# Which row's SMILES column is used, and the canonicalization, mirror the loader
# (LipidGraphBuilder): SmileGlobal unless it is "0", candidates split on ";",
# deduplicated by canonical non-isomeric SMILES.

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV


DEFAULT_DATA_DIR = Path("data")
BATCH_NAME = "Total_multiple_lipid_batch.npy"
MATRIX_NAME = "Total_tanimoto_matrix_uint8.npy"


def row_candidates(smile_global, smile_fragment, isomeric=False):
    """The canonical candidates of one row, in field order.

    ``isomeric`` mirrors the loader's ``lipid_isomers``: LipidGraphBuilder canonicalizes
    with ``isomericSmiles=self.config.lipid_isomers``, so an isomeric run keeps
    stereoisomers apart where a non-isomeric one collapses them into a single candidate.
    That changes both which structures exist and how many candidates a row contributes,
    which is why the two modes need their own artifacts rather than sharing one set.
    Default False: this is what the function always did, and the non-isomeric artifacts
    on disk were built by it.
    """
    # Exactly the loader's rule (LipidGraphBuilder._select_lipid_embedding_text): an
    # untrimmed comparison, so a stray " 0" picks the same column in both places
    # rather than silently indexing this matrix against a different candidate list.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument(
        "--batch-only",
        action="store_true",
        help=(
            "Write only the row-id vector. It is a matched pair with the matrix, so "
            "this leaves the pair inconsistent -- for inspection, not for a run."
        ),
    )
    args = parser.parse_args()
    RDLogger.DisableLog("rdApp.*")

    input_csv = args.input or (args.data_dir / INTERACTION_CSV)
    table = pd.read_csv(input_csv)
    print(f"input: {input_csv} ({len(table)} rows)")

    smiles, row_ids = collect(table)
    print(f"candidates: {len(smiles)} over {len(set(row_ids.tolist()))} rows")
    print(f"distinct structures: {len(set(smiles))}")

    np.save(args.data_dir / BATCH_NAME, row_ids)
    print(f"written: {args.data_dir / BATCH_NAME}")
    if args.batch_only:
        return

    print(f"matrix: {len(smiles)}x{len(smiles)} uint8 "
          f"({len(smiles) ** 2 / 1e9:.2f} GB)")
    matrix = tanimoto_matrix(smiles)
    np.save(args.data_dir / MATRIX_NAME, matrix)
    print(f"written: {args.data_dir / MATRIX_NAME}")


if __name__ == "__main__":
    main()
