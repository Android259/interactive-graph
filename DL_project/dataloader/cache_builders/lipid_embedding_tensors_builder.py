"""Build the memory-mapped lipid-embedding store.

See tensors_reading/lipid_embedding_tensors_reader.py for paths, format,
and value equivalence with the source pickle.
"""

import json
from pathlib import Path

import torch

from dataloader.tensors_reading.lipid_embedding_tensors_reader import STORE_FORMAT_VERSION, store_paths


def _source_record(path):
    stat = path.stat()
    return {"path": path.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def build_lipid_embedding_store(root_dir, source_name):
    """Convert an embedding pickle to a memory-mappable archive.

    Return (store_path, manifest_path, entry_count). Build unconditionally;
    the caller decides when needed, including forced filesystem recovery.
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
    # Keep contiguous storage so saved views do not include unused backing data
    # or map unneeded pages. Inputs are already contiguous; this call is a no-op.
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
