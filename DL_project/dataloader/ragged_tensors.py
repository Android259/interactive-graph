"""Per-row-tuple <-> flat-tensor-plus-offsets helpers.

A row has one to thirty-seven candidate structures; these helpers keep that ragged
shape through DataFrame columns (`candidate_column`), through flat tensors indexed by
row offsets (`_ragged_tensor`, `_candidate_position`), and through plain row lookups
(`ragged_rows`). Shared by Dataloader.py (both the construction and per-sample-serving
halves of PLIDataset) and frozen_prior.py, which may not import these back from
Dataloader.py without creating a cycle.
"""

import numpy as np
import torch


def candidate_column(values):
    """Per-candidate values as one DataFrame column, one tuple per row.

    A row has one to thirty-seven candidate structures; a tuple per row keeps its values
    attached to the row through splitting and sampling, with nothing padded.
    """
    return [tuple(float(value) for value in row) for row in values]


def _ragged_tensor(columns):
    """One flat tensor plus row offsets for a column (or columns) of per-row tuples.

    (None, None) when the column is absent.
    """
    if columns is None:
        return None, None
    if not isinstance(columns, list):
        columns = [columns]
    rows = [np.asarray(row, dtype="float32") for row in columns[0].to_numpy()]
    lengths = [len(row) for row in rows]
    stacked = np.stack(
        [np.concatenate([np.asarray(row, dtype="float32") for row in column.to_numpy()])
         for column in columns],
        axis=-1,
    )
    offsets = np.zeros(len(rows) + 1, dtype=np.int64)
    np.cumsum(lengths, out=offsets[1:])
    return torch.from_numpy(stacked), torch.from_numpy(offsets)


def _candidate_position(offsets, idx, candidate_index):
    """Where this row's chosen candidate sits in the flat tensor (clamped to its last one)."""
    start = int(offsets[idx])
    count = int(offsets[idx + 1]) - start
    return start + min(candidate_index or 0, count - 1)


def ragged_rows(values, rows):
    """The per-row arrays at the given positions of the original table."""
    return [values[int(row)] for row in rows]
