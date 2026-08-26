"""Build and validate the binary cache for precomputed protein graph CSVs."""

import json
import os
from pathlib import Path

import pandas
import torch

from dataloader.protein_graph_builder import BASE_NODE_COLUMNS


CACHE_FORMAT_VERSION = 1
CACHE_FILE = "protein_graph_tensors.pt"
MANIFEST_FILE = "protein_graph_tensors.manifest.json"


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


def _source_record(path, root_dir):
    stat = path.stat()
    return {
        "path": str(path.relative_to(root_dir)),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


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


def _base_graph(nodes_path, edges_path, pocket_path, node_columns):
    vertices = pandas.read_csv(nodes_path)
    edges = pandas.read_csv(edges_path)
    residue_to_node = {
        int(residue_id): index
        for index, residue_id in enumerate(vertices["ID_resSeq"])
    }
    edge_index = torch.tensor(
        edges[["ID1_resSeq", "ID2_resSeq"]].values,
        dtype=torch.long,
    )
    edge_index.apply_(lambda value: residue_to_node.get(value, 0))
    return {
        "x": torch.tensor(
            vertices[list(node_columns)].values,
            dtype=torch.float32,
        ),
        "edge_index": edge_index.t().contiguous(),
        "edge_attr": torch.tensor(
            edges[["distance", "area", "boundary"]].values,
            dtype=torch.float32,
        ),
        "bury": torch.tensor(
            vertices["residue_mean_buriedness"].values,
            dtype=torch.float32,
        ),
        "pocket": _pocket_tensor(pocket_path),
    }, vertices


def _geometric_graph(path, vertices):
    geometric = pandas.read_csv(path)
    expected_ids = vertices[
        ["ID_chainID", "ID_resSeq", "ID_iCode"]
    ].astype(str).reset_index(drop=True)
    actual_ids = geometric[
        ["ID_chainID", "ID_resSeq", "ID_iCode"]
    ].astype(str).reset_index(drop=True)
    if not expected_ids.equals(actual_ids):
        raise ValueError(f"{path}: residue rows do not align with protein nodes")

    identifier_columns = {"ID_chainID", "ID_resSeq", "ID_iCode"}
    return {
        column: torch.tensor(geometric[column].values)
        for column in geometric.columns
        if column not in identifier_columns
        and pandas.api.types.is_numeric_dtype(geometric[column])
    }


def build_protein_graph_tensor_cache(root_dir, node_columns=BASE_NODE_COLUMNS):
    root_dir = Path(root_dir).resolve()
    graphs_dir = root_dir / "graphs"
    payload = {}
    sources = []
    for protein_dir in sorted(path for path in graphs_dir.iterdir() if path.is_dir()):
        nodes_path = protein_dir / "coarse_graph_nodes.csv"
        edges_path = protein_dir / "coarse_graph_links.csv"
        pocket_path = protein_dir / "pocketness.pdb"
        if not (nodes_path.exists() and edges_path.exists() and pocket_path.exists()):
            continue
        base, vertices = _base_graph(nodes_path, edges_path, pocket_path, node_columns)
        entry = {"base": base}
        source_paths = [nodes_path, edges_path, pocket_path]
        geometric_path = protein_dir / "geometric_transformer_nodes.csv"
        if geometric_path.exists():
            entry["geometric"] = _geometric_graph(geometric_path, vertices)
            source_paths.append(geometric_path)
        payload[protein_dir.name] = entry
        sources.extend(_source_record(path, root_dir) for path in source_paths)

    cache_file, manifest_file = _cache_files(node_columns)
    cache_path = root_dir / cache_file
    manifest_path = root_dir / manifest_file
    torch.save(payload, cache_path)
    manifest = {
        "format_version": CACHE_FORMAT_VERSION,
        "cache_file": cache_file,
        "node_columns": list(node_columns),
        "proteins": sorted(payload),
        "sources": sources,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return cache_path, manifest_path, len(payload)


def load_protein_graph_tensor_cache(root_dir, node_columns=BASE_NODE_COLUMNS):
    root_dir = Path(root_dir).resolve()
    cache_file, manifest_file = _cache_files(node_columns)
    cache_path = root_dir / cache_file
    manifest_path = root_dir / manifest_file
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
