"""Builder for the compact Tanimoto artifacts.

dataloader/tensors_reading/tanimoto_compact_tensors_reader.py holds the reader, the shared
path/format logic, and the explanation of why this compact form is byte-identical to
the retired full matrix.
"""

import json
from pathlib import Path

import numpy as np
import torch

from dataloader.tensors_reading.tanimoto_compact_tensors_reader import (
    COMPACT_FORMAT_VERSION,
    compact_paths,
)


def write_compact(
    root_dir, matrix, structure_index, row_ids, source_csv, isomeric=False
):
    """Write the three arrays plus the manifest that ties them to their source table."""
    matrix_path, index_path, row_path, manifest_path = compact_paths(
        root_dir, isomeric=isomeric
    )
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(torch.from_numpy(np.ascontiguousarray(matrix)), matrix_path)
    torch.save(torch.from_numpy(np.ascontiguousarray(structure_index)), index_path)
    torch.save(torch.from_numpy(np.ascontiguousarray(row_ids)), row_path)
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
