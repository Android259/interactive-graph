"""Validate and read the binary cache for precomputed protein graph CSVs.

See dataloader/cache_builders/protein_graph_tensor_cache_writer.py for the builder.
"""

import json
import os
from pathlib import Path

import torch

from dataloader.protein_graph_builder import BASE_NODE_COLUMNS


CACHE_FORMAT_VERSION = 1
CACHE_FILE = "protein_graph_tensors.pt"
MANIFEST_FILE = "protein_graph_tensors.manifest.json"
CACHE_SUBDIR = "cache"


def _cache_files(node_columns):
    """Cache/manifest filenames for one protein-node column set.

    BASE_NODE_COLUMNS keeps the original CACHE_FILE/MANIFEST_FILE names, so the
    cache built before per-config variants existed is read and overwritten
    exactly as before. Any other column set -- --no_protein_geometry's empty
    tuple, or a future --protein_extra_node_features cache -- gets its own
    pair named after the columns, so it can never collide with or overwrite a
    cache another config still relies on.
    """
    if tuple(node_columns) == BASE_NODE_COLUMNS:
        return CACHE_FILE, MANIFEST_FILE
    suffix = "no_geometry" if not node_columns else "_".join(node_columns)
    return (
        f"protein_graph_tensors.{suffix}.pt",
        f"protein_graph_tensors.{suffix}.manifest.json",
    )


def _paths(root_dir, node_columns):
    """Cache/manifest paths under ``<root_dir>/cache`` for one protein-node column set."""
    cache_file, manifest_file = _cache_files(node_columns)
    cache_dir = Path(root_dir).resolve() / CACHE_SUBDIR
    return cache_dir / cache_file, cache_dir / manifest_file


def _pocket_tensor(path):
    lines = path.read_text().splitlines()
    if os.path.normpath(path).endswith(
        os.path.normpath("graphs/RBP4/pocketness.pdb")
    ):
        lines = lines[:-1]
    residue_has_pocket_atom = {}
    for line in lines:
        residue_has_pocket_atom[line[22:28].strip()] = 0
    for line in lines:
        if line[13:17].strip() in {"C", "CA", "CB", "O", "N"}:
            continue
        residue_has_pocket_atom[line[22:28].strip()] += int(line[62])
    return torch.tensor(
        [value > 0 for value in residue_has_pocket_atom.values()],
        dtype=torch.bool,
    )


def load_protein_graph_tensor_cache(root_dir, node_columns=BASE_NODE_COLUMNS):
    root_dir = Path(root_dir).resolve()
    cache_path, manifest_path = _paths(root_dir, node_columns)
    if not cache_path.exists() or not manifest_path.exists():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != CACHE_FORMAT_VERSION:
            return {}
        for source in manifest["sources"]:
            path = root_dir / source["path"]
            stat = path.stat()
            if (
                stat.st_size != source["size"]
                or stat.st_mtime_ns != source["mtime_ns"]
            ):
                return {}
        # mmap so concurrent training jobs share one copy of these tensors through the
        # page cache instead of each materializing its own. Nothing here is written in
        # place -- _cached_protein_parts only copies the dict and takes views/columns --
        # so the mapping stays shared for the life of the run. Archives written before
        # torch's zipfile format, or a filesystem that cannot map them, raise here and
        # fall back to the ordinary read, which loads the identical tensors.
        try:
            return torch.load(
                cache_path, map_location="cpu", weights_only=True, mmap=True
            )
        except (RuntimeError, ValueError):
            return torch.load(cache_path, map_location="cpu", weights_only=True)
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return {}
