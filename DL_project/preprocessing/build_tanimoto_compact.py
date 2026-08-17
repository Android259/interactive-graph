#!/usr/bin/env python3

# Build the compact Tanimoto pair from the interaction table.
#
# preprocessing/build_tanimoto_matrix.py writes one row per candidate structure
# *instance*, so the square matrix repeats every distinct pair of structures as many
# times as those structures recur across rows -- 2.89 GB for the current table, over
# roughly twelve hundred distinct structures. This writes one row per distinct structure
# instead, plus the index needed to expand it back, and the expansion is exact: see
# dataloader/tanimoto_compact.py for why byte-identity holds by construction.
#
# The candidate rule and the similarity arithmetic are IMPORTED from build_tanimoto_matrix
# rather than copied, so the two cannot drift apart. That matters more than it looks:
# these files are only meaningful when their candidate list matches the loader's, and a
# second transcription of "split on ';', canonicalize non-isomeric, dedup within the row"
# is exactly how they would stop matching.
#
# Output (dataloader/tanimoto_compact.py reads them):
#   Tanimoto_compact_matrix_uint8.npy      structures x structures
#   Tanimoto_compact_structure_index.npy   candidate -> structure row
#   Tanimoto_compact_row_ids.npy           candidate -> interaction table row
#   Tanimoto_compact.manifest.json         counts + the source table's size and mtime
#
# Usage:
#     python3 preprocessing/build_tanimoto_compact.py [--data-dir DIR] [--input CSV]
#                                                     [--verify-candidates N]
#
#     --verify-candidates N  Also build the first N candidates the old way, densely, and
#                             assert the compact form expands to the identical block.
#                             Costs N^2 bytes and one extra fingerprint pass; 3000 is a
#                             good check at 9 MB.

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import RDLogger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV
from dataloader.tanimoto_compact import write_compact
from preprocessing.build_tanimoto_matrix import collect, tanimoto_matrix


DEFAULT_DATA_DIR = Path("data")


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


def verify_against_dense(smiles, structure_index, compact, count):
    """Assert the compact form expands to the matrix the old builder would have written."""
    subset = smiles[:count]
    dense = tanimoto_matrix(subset, progress_every=0)
    rows = structure_index[:count]
    expanded = compact[np.ix_(rows, rows)]
    if not np.array_equal(dense, expanded):
        differing = int((dense != expanded).sum())
        raise SystemExit(
            f"VERIFY FAILED: {differing} of {dense.size} bytes differ between the dense "
            "matrix and the expanded compact form"
        )
    print(
        f"verify: first {count} candidates, {dense.size} bytes, "
        "dense and expanded compact forms are byte-identical"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--verify-candidates", type=int, default=0)
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
    if args.verify_candidates > 0:
        verify_against_dense(
            smiles,
            structure_index,
            compact,
            min(args.verify_candidates, len(smiles)),
        )

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
