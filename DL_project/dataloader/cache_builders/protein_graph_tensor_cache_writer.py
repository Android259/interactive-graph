"""Build the binary cache for precomputed protein graph CSVs.

See dataloader/protein_graph_tensor_cache_reader.py for the reader and the shared path/
format logic.
"""

import json
from pathlib import Path

import pandas
import torch

from dataloader.protein_graph_builder import BASE_NODE_COLUMNS
from dataloader.protein_graph_tensor_cache_reader import CACHE_FORMAT_VERSION, _paths, _pocket_tensor


def _source_record(path, root_dir):
    stat = path.stat()
    return {
        "path": str(path.relative_to(root_dir)),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


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

    cache_path, manifest_path = _paths(root_dir, node_columns)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, cache_path)
    manifest = {
        "format_version": CACHE_FORMAT_VERSION,
        "cache_file": cache_path.name,
        "node_columns": list(node_columns),
        "proteins": sorted(payload),
        "sources": sources,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return cache_path, manifest_path, len(payload)
