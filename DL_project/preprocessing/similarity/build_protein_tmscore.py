#!/usr/bin/env python3

# Build the structural protein-similarity matrix: TM-align's TM-score over every pair.
#
# TM-score: Zhang & Skolnick (2004).
# https://aideepmed.com/TM-score/TM-score.pdf
# TM-align: Zhang & Skolnick (2005).
# https://pmc.ncbi.nlm.nih.gov/articles/PMC1084323/
#
# Align CA coordinates with tmtools.tm_align and select the TM-score normalized
# by the longer chain. Each unordered pair is aligned once and copied to both
# matrix triangles; the search itself need not be symmetric.
#
# Output (format and rationale: preprocessing/similarity/protein_similarity_common.py):
#   data/cache/protein_similarity/Protein_tmscore_matrix_uint8.pt   proteins x proteins
#   data/cache/protein_similarity/Protein_tmscore_protein_index.pt  table row -> matrix row
#   data/cache/protein_similarity/Protein_tmscore.manifest.json     names, parameters, sources
#
# Usage:
#     python3 preprocessing/similarity/build_protein_tmscore.py [--data-dir DIR] [--input CSV]
#         [--proteins A,B,C --dry-run]

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dataloader.dataset_source import INTERACTION_CSV  # noqa: E402
from preprocessing.similarity.protein_similarity_common import (  # noqa: E402
    encode_uint8,
    load_structures,
    protein_order,
    report_matrix,
    structure_provenance,
    write_similarity,
)

try:
    from tmtools import tm_align
except ModuleNotFoundError:  # pragma: no cover - reported by main()
    tm_align = None


DEFAULT_DATA_DIR = Path("data")
NORMALIZATION = "longer chain"


def pair_tmscore(structure_a, structure_b):
    """(TM-score normalized by the longer chain, RMSD, aligned length) of two folds."""
    result = tm_align(
        structure_a.coords,
        structure_b.coords,
        structure_a.sequence,
        structure_b.sequence,
    )
    score = (
        result.tm_norm_chain2
        if len(structure_a) <= len(structure_b)
        else result.tm_norm_chain1
    )
    aligned = sum(
        1
        for left, right in zip(result.seqxA, result.seqyA)
        if left != "-" and right != "-"
    )
    return score, result.rmsd, aligned


def tmscore_matrix(structures, names, progress_every=50):
    """The symmetric TM-score matrix, one structural alignment per unordered pair."""
    size = len(names)
    scores = np.eye(size, dtype=np.float64)
    rmsds, aligned_lengths = [], []
    pairs = list(itertools.combinations(range(size), 2))
    for position, (row, col) in enumerate(pairs):
        score, rmsd, aligned = pair_tmscore(
            structures[names[row]], structures[names[col]]
        )
        scores[row, col] = scores[col, row] = score
        rmsds.append(rmsd)
        aligned_lengths.append(aligned)
        if progress_every and position and position % progress_every == 0:
            print(f"  {position}/{len(pairs)} pairs", flush=True)
    return scores, np.asarray(rmsds), np.asarray(aligned_lengths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument(
        "--proteins",
        default=None,
        help="Comma-separated subset to align, for inspecting a few pairs. A subset "
        "cannot be written (the matrix would not cover the table), so it requires "
        "--dry-run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and report without writing the artifacts.",
    )
    args = parser.parse_args()

    if tm_align is None:
        raise SystemExit("tmtools is required: pip install tmtools")

    input_csv = args.input or (args.data_dir / INTERACTION_CSV)
    table = pd.read_csv(input_csv)
    names, protein_index = protein_order(table)
    print(f"input: {input_csv} ({len(table)} rows, {len(names)} proteins)")

    if args.proteins:
        if not args.dry_run:
            raise SystemExit("--proteins describes a partial matrix; add --dry-run")
        requested = [name.strip() for name in args.proteins.split(",") if name.strip()]
        unknown = [name for name in requested if name not in names]
        if unknown:
            raise SystemExit(f"not in the interaction table: {', '.join(unknown)}")
        names = requested
        print(f"subset: {', '.join(names)}")

    structures = load_structures(args.data_dir, names)
    lengths = [len(structures[name]) for name in names]
    print(
        f"residues: {min(lengths)}-{max(lengths)} per protein, "
        f"{sum(lengths)} in total"
    )
    print(f"pairs: {len(names) * (len(names) - 1) // 2} structural alignments")

    scores, rmsds, aligned_lengths = tmscore_matrix(structures, names)
    print()
    print("[tmscore]")
    if aligned_lengths.size:
        print(
            f"structural alignment: {aligned_lengths.min()}-{aligned_lengths.max()} "
            f"residues aligned, RMSD {rmsds.min():.2f}-{rmsds.max():.2f} A"
        )
    report_matrix(scores, names)

    if args.dry_run:
        print()
        print("dry run: nothing written")
        return

    written = write_similarity(
        args.data_dir,
        "tmscore",
        encode_uint8(scores),
        protein_index,
        names,
        input_csv,
        structure_provenance(args.data_dir, names),
        {
            "normalization": NORMALIZATION,
            "method": "TM-align (tmtools bindings to the Zhang-lab C++ source)",
            "alignment": "sequence-independent structural",
            "structure_source": "data/esm3_input/<protein>.pdb CA atoms",
        },
    )
    for path in written:
        print(f"written: {path}")


if __name__ == "__main__":
    main()
