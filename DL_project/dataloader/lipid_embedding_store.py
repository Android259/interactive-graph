"""Memory-mapped store for the lipid SMILES embedding table.

The table is a dict of canonical SMILES -> (1, tokens, 768) float32 tensor, shipped as
a pickle. A pickle has to be read whole into the process that opens it, so N concurrent
training jobs hold N private copies of the same numbers: 267 MiB each for
``lipid_SMILES_embedding_deterministic.pkl``, and about 1 GiB of transient peak while
the unpickler builds them. On the local 13 GiB machine that peak, not the cores, is what
caps ``scripts/run_local.sh`` at four concurrent jobs.

This module keeps the same values in a ``torch.save`` archive instead, which
``torch.load(..., mmap=True)`` can map straight off disk. Every process then reads the
same page cache, so the table costs RAM once for the machine rather than once per job,
and only for the entries a run actually touches -- an unused entry stays on disk.

What matters for this project: **the tensors are the same objects the pickle held.**
They are re-saved verbatim, same dtype, same shape, same bytes, so a run served by the
store computes exactly what a run served by the pickle computes, down to the last bit.
``scripts/verify_lipid_embedding_store.py`` checks that element by element.

Two further consequences worth knowing, because they are what makes the warm cache
shared as well:

- ``lipid_encoding`` returns ``torch.squeeze(encoding)``, and squeeze is a *view*. Under
  the default ``lipid_first_fragment_only`` a row's cached encoding is therefore a view
  into the mapped file, not a copy -- so ``_lipid_encoding_cache`` (89 MiB, held for the
  whole run) becomes shared too, without touching the cache code at all.
- ``lipid_concat`` / ``lipid_fragments_mask`` build their encodings with ``torch.cat``,
  which copies. Those modes keep a private per-row tensor, as before, and still save the
  267 MiB source table.

The manifest guards staleness the same way ``protein_graph_tensor_cache`` does: the
store is used only while the source pickle's size and nanosecond mtime still match what
it was built from. A regenerated embedding table therefore falls back to the pickle
rather than silently serving stale vectors.
"""

import json
from pathlib import Path

import torch


STORE_FORMAT_VERSION = 1


def store_paths(root_dir, source_name):
    """Archive and manifest paths for one embedding table."""
    root_dir = Path(root_dir).resolve()
    stem = Path(source_name).stem
    return (
        root_dir / f"{stem}.tensors.pt",
        root_dir / f"{stem}.tensors.manifest.json",
    )


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


def store_is_current(root_dir, source_name):
    """True when a store exists and still matches its source pickle."""
    root_dir = Path(root_dir).resolve()
    store_path, manifest_path = store_paths(root_dir, source_name)
    if not (store_path.exists() and manifest_path.exists()):
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != STORE_FORMAT_VERSION:
            return False
        source = manifest["source"]
        stat = (root_dir / source["path"]).stat()
        return (
            stat.st_size == source["size"]
            and stat.st_mtime_ns == source["mtime_ns"]
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return False


def load_lipid_embedding_store(root_dir, source_name):
    """Map the store for one embedding table, or None to fall back to the pickle.

    None is a normal answer, not an error: a checkout that has never run the builder, a
    regenerated pickle, or a filesystem that cannot mmap all end up here, and the caller
    reads the pickle exactly as it did before.
    """
    if not store_is_current(root_dir, source_name):
        return None
    store_path, _ = store_paths(root_dir, source_name)
    try:
        return torch.load(
            store_path, map_location="cpu", weights_only=True, mmap=True
        )
    except (OSError, RuntimeError, ValueError):
        return None
