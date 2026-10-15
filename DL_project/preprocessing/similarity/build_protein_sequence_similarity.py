#!/usr/bin/env python3

# Build the sequence-based protein-similarity matrices from one global alignment pass.
#
# identity counts identical residue pairs; blosum62 counts pairs with a positive
# BLOSUM62 score. Both counts are divided by the longer sequence's length.
# Each unordered pair is aligned once and copied to both matrix triangles.
#
# Global alignment: Needleman & Wunsch (1970).
# https://web.stanford.edu/class/sbio228/public/readings/Bioinformatics_I_Lecture6/Needleman_Wunsch_JMB_70_Global_alignment.pdf
# Algorithm used here: Gotoh (1982).
# https://jaligner.sourceforge.net/references/gotoh1982.pdf
# BLOSUM62: Henikoff & Henikoff (1992).
# https://web.stanford.edu/class/sbio228/public/readings/Bioinformatics_I_Lecture6/Henikoff_PNAS_92_Substitution_matrices.pdf
#
# Alignment: global, BLOSUM62, affine gaps (open -11, extend -1), free end gaps.
#
# Output:
#   data/cache/protein_similarity/Protein_identity_matrix_uint8.pt   proteins x proteins
#   data/cache/protein_similarity/Protein_identity_protein_index.pt  table row -> matrix row
#   data/cache/protein_similarity/Protein_identity.manifest.json     names, parameters, sources
#   data/cache/protein_similarity/Protein_blosum62_*                 the same three
#
# Usage:
#     python3 preprocessing/similarity/build_protein_sequence_similarity.py [--data-dir DIR]
#         [--input CSV] [--gap-open -11] [--gap-extend -1]
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
    """Identical and positive-scoring residue counts divided by the longer length."""
    alignment = aligner.align(structure_a.sequence, structure_b.sequence)[0]
    counts = alignment.counts(matrix)
    longer = max(len(structure_a), len(structure_b))
    return counts.identities / longer, counts.positives / longer


def similarity_matrices(aligner, matrix, structures, names, progress_every=50):
    """Build both symmetric matrices with one alignment per unordered pair."""
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
            "(X/X counts as identical; X pairs have no positive BLOSUM62 score)"
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
    for metric in computed:
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
