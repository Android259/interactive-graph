"""Map canonical SMILES to (1, tokens, 768) float32 embeddings.

The source pickle loads entirely per process: 267 MiB for
lipid_SMILES_embedding_deterministic.pkl.
On the local 13 GiB machine, that peak limited run_local.sh to four jobs.

A torch.save archive loaded with mmap=True shares the OS page cache across
jobs and faults in only requested entries. Dtype, shape, and bytes are saved
unchanged; scripts/verify_lipid_embedding_store.py checks elementwise equality.
Runs therefore compute the same values as with the pickle.

lipid_encoding uses squeeze, a view. With default lipid_first_fragment_only,
_lipid_encoding_cache (89 MiB per run) also shares mapped storage.
lipid_concat/fragments_mask use torch.cat, retaining private per-row tensors,
but still avoid private copies of the 267 MiB source table.

Use the store only while source-pickle size and nanosecond mtime match the
manifest, as for protein_graph_tensor_cache. Regenerated sources fall back
to the pickle instead of stale vectors.
"""

import json
from pathlib import Path

import torch


STORE_FORMAT_VERSION = 1
CACHE_SUBDIR = "cache"


def store_paths(root_dir, source_name):
    """Archive and manifest paths for one embedding table, under ``<root_dir>/cache`` --
    see dataloader/cache_builders/lipid_embedding_tensors_builder.py for the builder."""
    root_dir = Path(root_dir).resolve() / CACHE_SUBDIR
    stem = Path(source_name).stem
    return (
        root_dir / f"{stem}.tensors.pt",
        root_dir / f"{stem}.tensors.manifest.json",
    )


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
    """Map the store, or return None so callers load the source pickle.

    None covers a missing build, a regenerated pickle, or unavailable mmap.
    These are normal fallback cases, not errors.
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
