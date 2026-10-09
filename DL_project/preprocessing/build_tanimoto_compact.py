#!/usr/bin/env python3

# Build the compact Tanimoto artifacts from the interaction table.
#
# The only Tanimoto builder in the project. It stores one row per DISTINCT candidate
# structure (roughly twelve hundred) plus the index that expands it back to one entry
# per candidate instance, so the per-candidate similarity is
# compact[structure_index[i], structure_index[j]] -- byte-identical to the old
# per-candidate square matrix (2.89 GB, Total_tanimoto_matrix_uint8.npy), which is no
# longer built or read. Why byte-identity holds: dataloader/tanimoto_compact_reader.py.
#
# The candidate rule here (row_candidates/collect) is the loader's: SmileGlobal unless it
# is "0", candidates split on ";", canonicalized, deduplicated within the row.
# preprocessing/build_tanimoto_headgroup.py and analysis/probes/split_similarity_vs_metric.py
# import it from here, so there is one transcription of it.
#
# Output (dataloader/tanimoto_compact_reader.py reads them):
#   Tanimoto_compact_matrix_uint8.npy      structures x structures
#   Tanimoto_compact_structure_index.npy   candidate -> structure row
#   Tanimoto_compact_row_ids.npy           candidate -> interaction table row
#   Tanimoto_compact.manifest.json         counts + the source table's size and mtime
#
# Usage:
#     python3 preprocessing/build_tanimoto_compact.py [--data-dir DIR] [--input CSV]
#                                                     [--isomeric]

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV
from dataloader.cache_builders.tanimoto_compact_writer import write_compact


DEFAULT_DATA_DIR = Path("data")


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


def distinct_structures(smiles):
    """Distinct canonical SMILES in first-appearance order, and each candidate's row.

    First-appearance order rather than sorted: it is stable for a fixed table, needs no
    comparison of chemistry strings, and keeps the compact matrix's row order traceable
    to the table it came from.
    """
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
