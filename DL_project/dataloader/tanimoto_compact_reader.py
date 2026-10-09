"""Compact form of the pairwise Tanimoto artifacts.

The old full form (``Total_tanimoto_matrix_uint8.npy``, no longer built or read) was
indexed per *candidate structure instance*: a row of the interaction table that lists
five isomer candidates contributes five entries, and the same structure recurs across
rows. The current table yields tens of thousands of
instances over about twelve hundred distinct structures, so the square matrix stores
each distinct pair of structures hundreds of times over -- 2.89 GB of almost entirely
repeated bytes.

Every one of those bytes is a pure function of the two structures.
``preprocessing/build_tanimoto_compact.py`` computes them as ``round(BulkTanimotoSimilarity(fp_a, fp_b) * 255)`` over Morgan
fingerprints, and a fingerprint is a pure function of the canonical SMILES string, so two
instances of one structure necessarily have byte-identical rows. Keeping one row per
distinct structure therefore loses nothing:

    full[i, j] == compact[structure_of[i], structure_of[j]]

exactly, byte for byte, including the diagonal (a structure against itself scores 1.0,
which rounds to the same 255 the builder forces onto ``full[i, i]``).

That identity is what makes this a memory change and not a numerical one. The loader does
not compute weights from the compact form -- it materializes precisely the K x K submatrix
it used to slice out of the full file, and hands that to unchanged arithmetic. Weights
computed from the compact form directly would sum the same numbers in a different order
and shift the last digits; this does not.

Three files, written together and only meaningful as a set (see the manifest):

    Tanimoto_compact_matrix_uint8.npy      structures x structures similarities
    Tanimoto_compact_structure_index.npy   candidate instance -> structure row
    Tanimoto_compact_row_ids.npy           candidate instance -> interaction table row,
                                            the same content as the old Total_multiple_lipid_batch.npy
"""

import json
from pathlib import Path

import numpy as np


COMPACT_FORMAT_VERSION = 1
CACHE_SUBDIR = "cache"
# Two disjoint sets, because lipid_isomers changes the candidate list itself, not just
# the similarities: with stereochemistry kept, isomers that collapse into one candidate
# under the non-isomeric rule stay separate, so a row contributes a different number of
# candidates and the row-id vectors of the two modes are different lengths. They can
# never be used interchangeably, hence separate files rather than one with a flag.
COMPACT_PREFIX = "Tanimoto_compact"
ISOMERIC_COMPACT_PREFIX = "Tanimoto_compact_isomeric"


class CompactTanimoto:
    """The three arrays, with the matrix left memory-mapped until it is sliced."""

    def __init__(self, matrix, structure_index, row_ids):
        self.matrix = matrix
        self.structure_index = structure_index
        self.row_ids = row_ids

    @property
    def structures(self):
        return self.matrix.shape[0]

    @property
    def candidates(self):
        return self.row_ids.shape[0]

    def submatrix(self, selected):
        """The similarities among ``selected`` candidates, as the full file would give.

        ``selected`` indexes candidate instances, exactly as it did against the full
        matrix, and the result is the identical K x K uint8 block -- the expansion is a
        gather, not a recomputation.
        """
        structure_rows = self.structure_index[selected]
        return np.array(
            self.matrix[np.ix_(structure_rows, structure_rows)], copy=True
        )

    def candidate_view(self):
        """An object indexed per candidate instance, like the old full matrix.

        ``view[np.ix_(a, b)]`` returns the same uint8 block ``full[np.ix_(a, b)]`` did,
        gathered from the compact matrix, for callers written against the full form.
        """
        return _CandidateView(self)


class _CandidateView:
    def __init__(self, compact):
        self._matrix = compact.matrix
        self._structure_index = compact.structure_index

    def __getitem__(self, key):
        rows, cols = key
        return self._matrix[self._structure_index[rows], self._structure_index[cols]]


def compact_paths(root_dir, isomeric=False):
    """Cache-file paths under ``<root_dir>/cache`` -- see
    dataloader/cache_builders/tanimoto_compact_writer.py for the builder that writes
    them."""
    root_dir = Path(root_dir).resolve() / CACHE_SUBDIR
    prefix = ISOMERIC_COMPACT_PREFIX if isomeric else COMPACT_PREFIX
    return (
        root_dir / f"{prefix}_matrix_uint8.npy",
        root_dir / f"{prefix}_structure_index.npy",
        root_dir / f"{prefix}_row_ids.npy",
        root_dir / f"{prefix}.manifest.json",
    )


def load_compact(root_dir, source_csv=None, isomeric=False):
    """Map the compact artifacts, or None when they are absent or stale.

    ``source_csv``, when given, is checked against the manifest by size and nanosecond
    mtime, so a rebuilt interaction table is refused (the loader then raises and asks for
    a rebuild) instead of silently weighting by similarities computed for a different
    candidate list.
    """
    matrix_path, index_path, row_path, manifest_path = compact_paths(
        root_dir, isomeric=isomeric
    )
    if not all(
        path.exists() for path in (matrix_path, index_path, row_path, manifest_path)
    ):
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != COMPACT_FORMAT_VERSION:
            return None
        if source_csv is not None:
            stat = Path(source_csv).stat()
            source = manifest["source"]
            if (
                stat.st_size != source["size"]
                or stat.st_mtime_ns != source["mtime_ns"]
            ):
                return None
        return CompactTanimoto(
            # The matrix stays mapped: a run slices one K x K block out of it and never
            # needs the rest resident, and concurrent jobs then share the mapping.
            np.load(matrix_path, mmap_mode="r"),
            np.load(index_path),
            np.load(row_path),
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return None
