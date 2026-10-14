#!/usr/bin/env python3

# Build the structural protein-similarity matrix: TM-align's TM-score over every pair.
#
# TM-score asks the question the two sequence metrics cannot: how much of one protein's
# FOLD the other reproduces. It is computed from a sequence-INDEPENDENT structural
# alignment -- TM-align searches for the residue correspondence and the superposition
# together -- so two proteins that no longer look alike in sequence still score high if
# they share a fold, which on an LTP panel is most of the interesting signal.
#
# The computation is the original Zhang-lab TM-align C++ code, through its `tmtools`
# bindings, rather than a reimplementation: the published algorithm is a heuristic search
# (gapless threading and secondary-structure seeds, then alternating dynamic programming
# and Kabsch superposition), so a reimplementation would not merely be slower but would
# return a slightly different number than everything else that reports a TM-score.
#
# Normalization. TM-score is asymmetric: the sum over aligned residues is divided by a
# reference length, and d0 -- the distance at which a residue pair stops counting -- is
# itself a function of that length. TM-align therefore reports two values per pair. A
# similarity matrix needs one symmetric number, and this takes the one normalized by the
# LONGER chain, the same divisor
# preprocessing/build_protein_sequence_similarity.py uses, so the three matrices answer
# one question three ways instead of three questions.
#
# The longer chain for the same reason it wins there, measured on the same 9 related
# against 7 unrelated pairs:
#
#   / longer chain     related 0.677-0.975   unrelated 0.161-0.309   margin +0.368
#   / shorter chain    related 0.726-0.982   unrelated 0.304-0.448   margin +0.278
#
# A small protein superposed onto part of a large one scores well against the small one's
# length whatever the rest of the large one does -- FABP1's 127 residues reach 0.448
# against BPI's 456, which is most of the way to a real fold match. The same comparison
# normalized by BPI is 0.161.
#
# Those margins are also the reason this matrix is worth building next to the sequence
# ones rather than instead of them: +0.368 against sequence identity's +0.130 on the same
# pairs. Structure separates these folds roughly three times as cleanly, and the pairs it
# rescues are the distant homologs identity leaves in the noise.
#
# Symmetry is a property of the file, not of the search: each unordered pair is aligned
# once and written to both triangles. TM-align's heuristic is not guaranteed to return
# the same correspondence with its arguments swapped, so aligning both directions could
# hand back two slightly different numbers for one pair.
#
# Output (format and rationale: preprocessing/protein_similarity_common.py):
#   data/protein_similarity/Protein_tmscore_matrix_uint8.pt   proteins x proteins
#   data/protein_similarity/Protein_tmscore_protein_index.pt  table row -> matrix row
#   data/protein_similarity/Protein_tmscore.manifest.json     names, parameters, sources
#
# Usage:
#     python3 preprocessing/build_protein_tmscore.py [--data-dir DIR] [--input CSV]
#         [--proteins A,B,C --dry-run]

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV  # noqa: E402
from preprocessing.protein_similarity_common import (  # noqa: E402
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
        np.ascontiguousarray(structure_a.coords),
        np.ascontiguousarray(structure_b.coords),
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
