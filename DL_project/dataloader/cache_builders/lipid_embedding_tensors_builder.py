"""Builder for the lipid-embedding memory-mapped store.

dataloader/tensors_reading/lipid_embedding_tensors_reader.py holds the reader and the shared path/format logic,
and explains why the mmap'd archive computes exactly what the source pickle computes.
"""

import json
from pathlib import Path

import torch

from dataloader.tensors_reading.lipid_embedding_tensors_reader import STORE_FORMAT_VERSION, store_paths


def _source_record(path):
    stat = path.stat()
    return {"path": path.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def build_lipid_embedding_store(root_dir, source_name):
    """Convert one embedding pickle into its memory-mappable archive.

    Returns (store_path, manifest_path, entry_count). Rebuilds unconditionally: the
    caller decides whether it is needed, so that a forced rebuild after an odd
    filesystem event stays possible.
    """
    import pickle

    root_dir = Path(root_dir).resolve()
    source_path = root_dir / source_name
    with open(source_path, "rb") as handle:
        table = pickle.load(handle)

    if not isinstance(table, dict):
        raise TypeError(
            f"{source_path}: expected a dict of SMILES -> tensor, got {type(table)!r}"
        )
    for key, value in table.items():
        if not isinstance(value, torch.Tensor):
            raise TypeError(
                f"{source_path}: value for {key!r} is {type(value)!r}, not a tensor"
            )

    store_path, manifest_path = store_paths(root_dir, source_name)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    # contiguous() so each entry owns a tight storage in the archive: a tensor saved as
    # a view of a bigger storage drags the whole storage into the file, and mmap would
    # then fault in pages no run ever reads. The values here are already contiguous, so
    # this is a no-op that documents the requirement rather than a transformation.
    torch.save({key: value.contiguous() for key, value in table.items()}, store_path)
    manifest_path.write_text(
        json.dumps(
            {
                "format_version": STORE_FORMAT_VERSION,
                "store_file": store_path.name,
                "entries": len(table),
                "source": _source_record(source_path),
            },
            indent=2,
        )
        + "\n"
    )
    return store_path, manifest_path, len(table)
