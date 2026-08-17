"""Compact form of the pairwise Tanimoto artifacts.

``Total_tanimoto_matrix_uint8.npy`` is indexed per *candidate structure instance*: a row
of the interaction table that lists five isomer candidates contributes five entries, and
the same structure recurs across rows. The current table yields tens of thousands of
instances over about twelve hundred distinct structures, so the square matrix stores
each distinct pair of structures hundreds of times over -- 2.89 GB of almost entirely
repeated bytes.

Every one of those bytes is a pure function of the two structures. ``build_tanimoto_matrix``
computes them as ``round(BulkTanimotoSimilarity(fp_a, fp_b) * 255)`` over Morgan
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
                                            the same content as Total_multiple_lipid_batch.npy
"""

import json
from pathlib import Path

import numpy as np


COMPACT_FORMAT_VERSION = 1
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


def compact_paths(root_dir, isomeric=False):
    root_dir = Path(root_dir).resolve()
    prefix = ISOMERIC_COMPACT_PREFIX if isomeric else COMPACT_PREFIX
    return (
        root_dir / f"{prefix}_matrix_uint8.npy",
        root_dir / f"{prefix}_structure_index.npy",
        root_dir / f"{prefix}_row_ids.npy",
        root_dir / f"{prefix}.manifest.json",
    )


def write_compact(
    root_dir, matrix, structure_index, row_ids, source_csv, isomeric=False
):
    """Write the three arrays plus the manifest that ties them to their source table."""
    matrix_path, index_path, row_path, manifest_path = compact_paths(
        root_dir, isomeric=isomeric
    )
    np.save(matrix_path, matrix)
    np.save(index_path, structure_index)
    np.save(row_path, row_ids)
    source_csv = Path(source_csv)
    stat = source_csv.stat()
    manifest_path.write_text(
        json.dumps(
            {
                "format_version": COMPACT_FORMAT_VERSION,
                "isomeric": bool(isomeric),
                "structures": int(matrix.shape[0]),
                "candidates": int(row_ids.shape[0]),
                "rows": int(len(set(row_ids.tolist()))),
                "source": {
                    "path": source_csv.name,
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                },
            },
            indent=2,
        )
        + "\n"
    )
    return matrix_path, index_path, row_path, manifest_path


def load_compact(root_dir, source_csv=None, isomeric=False):
    """Map the compact artifacts, or None when they are absent or stale.

    ``source_csv``, when given, is checked against the manifest by size and nanosecond
    mtime, so a rebuilt interaction table falls back to the old full-matrix path instead
    of silently weighting by similarities computed for a different candidate list --
    which is the failure the current on-disk matrix is an example of.
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
