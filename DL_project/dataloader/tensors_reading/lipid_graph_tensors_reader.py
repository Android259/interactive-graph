"""Validate and read the binary cache for precomputed lipid isomer graph CSVs.

See dataloader/cache_builders/lipid_graph_tensor_cache_writer.py for the builder.
"""

import json
from pathlib import Path

import torch


CACHE_FORMAT_VERSION = 1
CACHE_FILE = "lipid_graph_tensors.pt"
MANIFEST_FILE = "lipid_graph_tensors.manifest.json"
CACHE_SUBDIR = "cache"


def _paths(root_dir):
    root_dir = Path(root_dir).resolve() / CACHE_SUBDIR
    return root_dir / CACHE_FILE, root_dir / MANIFEST_FILE


def load_lipid_graph_tensor_cache(root_dir):
    root_dir = Path(root_dir).resolve()
    cache_path, manifest_path = _paths(root_dir)
    if not cache_path.exists() or not manifest_path.exists():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != CACHE_FORMAT_VERSION:
            return {}
        for source in manifest["sources"]:
            path = root_dir / source["path"]
            stat = path.stat()
            if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
                return {}
        # mmap so concurrent training jobs share one copy of these tensors through the
        # page cache instead of each materializing its own -- same reasoning as
        # protein_graph_tensor_cache.load_protein_graph_tensor_cache.
        try:
            return torch.load(
                cache_path, map_location="cpu", weights_only=True, mmap=True
            )
        except (RuntimeError, ValueError):
            return torch.load(cache_path, map_location="cpu", weights_only=True)
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return {}
