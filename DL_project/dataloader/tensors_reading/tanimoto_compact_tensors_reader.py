"""Read compact pairwise Tanimoto artifacts without changing values.

The retired Total_tanimoto_matrix_uint8.npy indexed candidate instances,
including repeated structures across interaction rows. Five candidates gave
five entries. Tens of thousands of instances covered ~1200 structures,
repeating pairs hundreds of times in a 2.89 GB matrix.

preprocessing/similarity/build_tanimoto_compact.py computes
round(BulkTanimotoSimilarity(fp_a, fp_b) * 255) from Morgan fingerprints.
Canonical SMILES determine fingerprints, so repeated structures have identical
rows. Retain one row per structure:

    full[i, j] == compact[structure_of[i], structure_of[j]]

This includes the diagonal: similarity 1 rounds to the forced full-matrix 255.
Materialize the same K x K candidate block before unchanged weight arithmetic.
Computing weights directly from compact rows would change summation order
and possibly the last digits.

Three files form one set, validated by the manifest:
Tanimoto_compact_matrix_uint8.pt: structure-by-structure similarities;
Tanimoto_compact_structure_index.pt: candidate instance to structure row;
Tanimoto_compact_row_ids.pt: instance to interaction row, as in the old
Total_multiple_lipid_batch.npy.

torch.save archives replace .npy for torch.load(..., mmap=True) sharing.
Elementwise checks confirmed identical uint8 matrix and int32 index/row-ID
arrays. Tensor.numpy() gives zero-copy ndarray views for CompactTanimoto
and _CandidateView, so only the disk container changes.
"""

import json
from pathlib import Path

import numpy as np
import torch


COMPACT_FORMAT_VERSION = 1
CACHE_SUBDIR = "cache"
TANIMOTO_SUBDIR = "tanimoto"
# Keep separate artifact sets for lipid_isomers: preserving stereochemistry
# changes candidate counts and row-ID vector lengths, not just similarities.
# The two modes cannot share files.
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
        """Gather the full-equivalent K x K uint8 block for selected candidate instances.

        Expand by indexing the compact matrix, without recomputing similarities.
        """
        structure_rows = self.structure_index[selected]
        return np.array(
            self.matrix[np.ix_(structure_rows, structure_rows)], copy=True
        )

    def candidate_view(self):
        """Return a candidate-indexed view compatible with the retired full matrix.

        view[np.ix_(a, b)] gathers the same uint8 block as full[np.ix_(a, b)].
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
    """Cache-file paths under ``<root_dir>/cache/tanimoto`` -- see
    dataloader/cache_builders/tanimoto_compact_tensors_builder.py for the builder that writes
    them."""
    root_dir = Path(root_dir).resolve() / CACHE_SUBDIR / TANIMOTO_SUBDIR
    prefix = ISOMERIC_COMPACT_PREFIX if isomeric else COMPACT_PREFIX
    return (
        root_dir / f"{prefix}_matrix_uint8.pt",
        root_dir / f"{prefix}_structure_index.pt",
        root_dir / f"{prefix}_row_ids.pt",
        root_dir / f"{prefix}.manifest.json",
    )


def load_compact(root_dir, source_csv=None, isomeric=False):
    """Map compact artifacts, or return None for missing or stale files.

    If source_csv is given, check size and nanosecond mtime against the manifest.
    The loader rejects rebuilt-table mismatches and requests a rebuild instead of using similarities for another candidate list.
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
            # Map the matrix and slice only the needed K x K block; jobs share other pages.
            # Tensor.numpy() preserves this mapping as a zero-copy ndarray view.
            torch.load(
                matrix_path, map_location="cpu", weights_only=True, mmap=True
            ).numpy(),
            torch.load(index_path, map_location="cpu", weights_only=True).numpy(),
            torch.load(row_path, map_location="cpu", weights_only=True).numpy(),
        )
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError):
        return None
