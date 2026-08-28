"""Build and validate the binary cache for precomputed lipid isomer graph CSVs.

Mirrors dataloader/protein_graph_tensor_cache.py: data/build_lipid_isomer_graphs.py
writes one nodes.csv/edges.csv pair per canonical-SMILES lipid under
data/lipid_graphs/<graph_id>/, and LipidIsomerGraphBuilder.make_graph_lipid
otherwise re-reads and re-parses those CSVs (RBF-expanding mean_bond_length in
Python) on every canonical SMILES not yet in its in-process _lipid_graph_cache.
Built once here, the resulting tensors are mmap'd so concurrent training
processes share one copy through the page cache instead of each re-parsing
~1300 CSV pairs, exactly like the protein tensor cache already does.
"""

import json
from pathlib import Path

import pandas
import torch

from architecture.protein_edge_geometry import rbf


CACHE_FORMAT_VERSION = 1
CACHE_FILE = "lipid_graph_tensors.pt"
MANIFEST_FILE = "lipid_graph_tensors.manifest.json"

# Must match LipidIsomerGraphBuilder.make_graph_lipid's node_columns/edge_columns
# and bond-length RBF bounds exactly -- the cache stores the identical tensors
# that method would otherwise build from the same CSVs.
NODE_COLUMNS = [
    "atomic_num",
    "formal_charge",
    "degree",
    "hybridization",
    "is_aromatic",
    "is_in_ring",
    "chiral_tag",
    "chirality_possible",
    "total_num_hs",
    "mass",
    "gasteiger_charge",
]
EDGE_COLUMNS = [
    "bond_type",
    "is_conjugated",
    "is_in_ring",
    "stereo",
    "bond_dir",
    "is_aromatic",
]
BOND_LENGTH_RBF_MIN, BOND_LENGTH_RBF_MAX = 0.8, 2.0


def _source_record(path, root_dir):
    stat = path.stat()
    return {
        "path": str(path.relative_to(root_dir)),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _one_graph(graph_dir):
    nodes = pandas.read_csv(graph_dir / "nodes.csv")
    edges = pandas.read_csv(graph_dir / "edges.csv")
    edge_attr = torch.tensor(edges[EDGE_COLUMNS].values, dtype=torch.float32)
    bond_length = torch.tensor(edges["mean_bond_length"].values, dtype=torch.float32)
    edge_attr = torch.cat(
        (
            edge_attr,
            rbf(bond_length, d_min=BOND_LENGTH_RBF_MIN, d_max=BOND_LENGTH_RBF_MAX),
        ),
        dim=-1,
    )
    return {
        "x": torch.tensor(nodes[NODE_COLUMNS].values, dtype=torch.float32),
        "edge_index": torch.tensor(
            edges[["source", "target"]].values, dtype=torch.long
        ).t().contiguous(),
        "edge_attr": edge_attr,
        "chain_rank": torch.tensor(nodes["chain_rank"].values, dtype=torch.float32),
    }


def build_lipid_graph_tensor_cache(root_dir):
    root_dir = Path(root_dir).resolve()
    lipid_graphs_dir = root_dir / "lipid_graphs"
    payload = {}
    sources = []
    for graph_dir in sorted(path for path in lipid_graphs_dir.iterdir() if path.is_dir()):
        nodes_path = graph_dir / "nodes.csv"
        edges_path = graph_dir / "edges.csv"
        if not (nodes_path.exists() and edges_path.exists()):
            continue
        payload[graph_dir.name] = _one_graph(graph_dir)
        sources.append(_source_record(nodes_path, root_dir))
        sources.append(_source_record(edges_path, root_dir))

    cache_path = root_dir / CACHE_FILE
    manifest_path = root_dir / MANIFEST_FILE
    torch.save(payload, cache_path)
    manifest = {
        "format_version": CACHE_FORMAT_VERSION,
        "graph_ids": sorted(payload),
        "sources": sources,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return cache_path, manifest_path, len(payload)


def load_lipid_graph_tensor_cache(root_dir):
    root_dir = Path(root_dir).resolve()
    cache_path = root_dir / CACHE_FILE
    manifest_path = root_dir / MANIFEST_FILE
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
