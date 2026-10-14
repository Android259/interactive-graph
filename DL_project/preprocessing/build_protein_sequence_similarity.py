#!/usr/bin/env python3

# Build the sequence-based protein-similarity matrices from one global alignment pass.
#
# Two metrics come out of the same pairwise alignment, which is why one script writes
# both: aligning twice to score the same columns two ways would only invite the two
# matrices to disagree about which columns those are.
#
#   identity   fraction of aligned columns holding the SAME residue
#   blosum62   fraction of aligned columns holding a POSITIVE BLOSUM62 pair -- identical
#              or a conservative substitution (I/L, K/R, D/E, ...)
#
# Both are divided by the LONGER sequence's length, so each is in [0, 1], is symmetric,
# and is 1.0 only for two identical sequences.
#
# Why the longer one, measured on this panel -- 9 pairs from one protein family against 7
# pairs from different folds, identity on the same alignments:
#
#   / longer sequence    related 0.200-0.777   unrelated 0.004-0.070   margin +0.130
#   / shorter sequence   related 0.210-0.777   unrelated 0.007-0.205   margin +0.005
#   / aligned columns    related 0.222-0.777   unrelated 0.091-0.600   margin -0.378
#
# The shorter sequence is the reading one would reach for first ("how much of the smaller
# protein the larger reproduces") and it is the one that fails: a 127-residue FABP1 placed
# anywhere inside a 456-residue BPI collects 20% identity on noise alone, which is the
# whole margin against genuinely related pairs like FABP1/FABP5 at 0.244. Dividing by the
# longer sequence charges that length difference once and drops the same pair to 0.057.
# The aligned-column count is worse than either: it rewards one short well-matching window
# between otherwise unrelated proteins, and ranks RBP4/SEC14L2 at 0.600.
#
# Alignment: global (Needleman-Wunsch), BLOSUM62, affine gaps, open -11 / extend -1 (the
# BLAST protein defaults), end gaps free. Free end gaps because the panel mixes a
# 127-residue FABP1 with a 456-residue BPI: charged for, the aligner spreads the short
# sequence across the long one instead of hanging its tails off the end, and the
# unrelated pairs rise to 0.323 -- past every distant homolog in the panel.
#
# Output (format and rationale: preprocessing/protein_similarity_common.py):
#   data/protein_similarity/Protein_identity_matrix_uint8.pt   proteins x proteins
#   data/protein_similarity/Protein_identity_protein_index.pt  table row -> matrix row
#   data/protein_similarity/Protein_identity.manifest.json     names, parameters, sources
#   data/protein_similarity/Protein_blosum62_*                 the same three
#
# Usage:
#     python3 preprocessing/build_protein_sequence_similarity.py [--data-dir DIR]
#         [--input CSV] [--metrics identity blosum62] [--gap-open -11] [--gap-extend -1]
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
    from Bio.Align import PairwiseAligner, substitution_matrices
except ModuleNotFoundError:  # pragma: no cover - reported by main()
    PairwiseAligner = None
    substitution_matrices = None


DEFAULT_DATA_DIR = Path("data")
DEFAULT_GAP_OPEN = -11.0
DEFAULT_GAP_EXTEND = -1.0
NORMALIZATION = "max(len_a, len_b)"


def build_aligner(gap_open, gap_extend):
    """A global BLOSUM62 aligner with affine gaps and free end gaps."""
    matrix = substitution_matrices.load("BLOSUM62")
    aligner = PairwiseAligner(
        mode="global",
        substitution_matrix=matrix,
        open_gap_score=gap_open,
        extend_gap_score=gap_extend,
    )
    aligner.end_gap_score = 0.0
    return aligner, matrix


def pair_scores(aligner, matrix, structure_a, structure_b):
    """(identity, blosum62 similarity) of two sequences, both in [0, 1].

    `counts` reads the two numerators off the alignment itself: `identities` is the
    columns whose residues match, `positives` the columns whose BLOSUM62 entry is above
    zero, which is the classic "percent similar" of a pairwise alignment and the reason
    this metric exists next to identity -- it counts a conservative substitution as
    partial agreement instead of as a mismatch.
    """
    alignment = aligner.align(structure_a.sequence, structure_b.sequence)[0]
    counts = alignment.counts(matrix)
    longer = max(len(structure_a), len(structure_b))
    return counts.identities / longer, counts.positives / longer


def similarity_matrices(aligner, matrix, structures, names, progress_every=50):
    """The two symmetric matrices, one alignment per unordered pair.

    Each pair is aligned once and written to both triangles. A global alignment is
    symmetric in principle, but computing both directions would still be two calls to
    hand the same number back, and a single call makes the symmetry a property of the
    file rather than of the aligner.
    """
    size = len(names)
    identity = np.eye(size, dtype=np.float64)
    blosum = np.eye(size, dtype=np.float64)
    pairs = list(itertools.combinations(range(size), 2))
    for position, (row, col) in enumerate(pairs):
        identity_value, blosum_value = pair_scores(
            aligner, matrix, structures[names[row]], structures[names[col]]
        )
        identity[row, col] = identity[col, row] = identity_value
        blosum[row, col] = blosum[col, row] = blosum_value
        if progress_every and position and position % progress_every == 0:
            print(f"  {position}/{len(pairs)} pairs", flush=True)
    return identity, blosum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=("identity", "blosum62"),
        default=("identity", "blosum62"),
        help="Which of the two matrices to write. Both are computed either way: they "
        "come from one alignment, so writing one alone saves nothing.",
    )
    parser.add_argument("--gap-open", type=float, default=DEFAULT_GAP_OPEN)
    parser.add_argument("--gap-extend", type=float, default=DEFAULT_GAP_EXTEND)
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

    if PairwiseAligner is None:
        raise SystemExit("Biopython is required: pip install biopython")

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
    unknown_residues = sum(structures[name].unknown for name in names)
    print(
        f"residues: {min(lengths)}-{max(lengths)} per protein, "
        f"{sum(lengths)} in total"
    )
    if unknown_residues:
        print(
            f"non-standard residues read as 'X': {unknown_residues} "
            "(they count as neither identical nor positive)"
        )
    print(
        f"alignment: global BLOSUM62, gap open {args.gap_open:g} / extend "
        f"{args.gap_extend:g}, end gaps free"
    )

    aligner, matrix = build_aligner(args.gap_open, args.gap_extend)
    identity, blosum = similarity_matrices(aligner, matrix, structures, names)

    computed = {"identity": identity, "blosum62": blosum}
    parameters = {
        "normalization": NORMALIZATION,
        "alignment": "global",
        "substitution_matrix": "BLOSUM62",
        "gap_open": args.gap_open,
        "gap_extend": args.gap_extend,
        "end_gaps": "free",
        "sequence_source": "data/esm3_input/<protein>.pdb CA residues",
    }
    numerator = {
        "identity": "aligned columns with the same residue",
        "blosum62": "aligned columns with a positive BLOSUM62 score",
    }

    provenance = structure_provenance(args.data_dir, names)
    for metric in args.metrics:
        print()
        print(f"[{metric}]")
        report_matrix(computed[metric], names)
        if args.dry_run:
            continue
        written = write_similarity(
            args.data_dir,
            metric,
            encode_uint8(computed[metric]),
            protein_index,
            names,
            input_csv,
            provenance,
            dict(parameters, numerator=numerator[metric]),
        )
        for path in written:
            print(f"written: {path}")

    if args.dry_run:
        print()
        print("dry run: nothing written")


if __name__ == "__main__":
    main()
