"""Validate that ESM3 per-residue embeddings line up with protein graph nodes.

The protein encoder concatenates ESM3 row ``i`` onto graph node ``i``
(``node = torch.cat((node, plm), -1)`` in architecture/protein_encoder.py), so a
stored embedding must have **exactly one row per graph residue** after its special
tokens are trimmed. The loader only ever checked the count and merely *printed* a
warning; this module makes that invariant a real, reusable check that both the
dataloader and a training-free test can call.

Scope / honesty: this verifies the **count** invariant the loader relies on. It does
NOT verify row *order* -- that needs a UniProt->PDB residue alignment (the biotite
alignment commented out in preprocessing/EmbedProtein.py). A passing count is
necessary but not sufficient for correct alignment; a failing count is a definite bug.
"""
from __future__ import annotations

import glob
import os
import pickle as pkl
from pathlib import Path

from dataloader.protein_registry import (
    protein_record,
    protein_record_by_artifact_stem,
)

DATA_ROOT = str(Path(__file__).resolve().parent.parent / "data")

def embedding_stem(prot_file: str) -> str:
    """Map a CSV protein name (LTPProtein) to its embedding/graph stem."""
    return protein_record(prot_file, DATA_ROOT)["artifact_stem"]


def embedding_stem_from_filename(path: str) -> str:
    """Stem from an embedding filename, e.g. 'ATCAY_AF-..._ESM3.pkl' -> 'ATCAY'."""
    return os.path.basename(path).split("_")[0]


def embedding_path_for_stem(stem: str, root: str = DATA_ROOT) -> str:
    hits = sorted(glob.glob(os.path.join(root, "embedding_ESM3", stem + "_*")))
    if not hits:
        raise FileNotFoundError(f"no ESM3 embedding for stem {stem!r} under {root}")
    return hits[0]


def node_csv_for_stem(stem: str, root: str = DATA_ROOT) -> str:
    return os.path.join(root, "graphs", stem, "coarse_graph_nodes.csv")


def has_graph(stem: str, root: str = DATA_ROOT) -> bool:
    return os.path.isfile(node_csv_for_stem(stem, root))


def _raw_embedding_rows(path: str) -> int:
    with open(path, "rb") as handle:
        tensor = pkl.load(handle)
    return int(tensor.shape[0])


def trimmed_embedding_rows(stem: str, root: str = DATA_ROOT) -> int:
    """Embedding rows after the same special-token trimming the loader applies."""
    raw = _raw_embedding_rows(embedding_path_for_stem(stem, root))
    extra_trim = protein_record_by_artifact_stem(
        stem, root
    )["esm3_v1_extra_trim_pairs"]
    return raw - 2 * extra_trim - 2  # -2 for the BOS/EOS pair


def graph_node_count(stem: str, root: str = DATA_ROOT) -> int:
    """Number of residue rows in the coarse graph (CSV lines minus the header)."""
    with open(node_csv_for_stem(stem, root)) as handle:
        return sum(1 for _ in handle) - 1


def rows_match_nodes(trimmed_rows: int, node_csv_lines: int) -> bool:
    """Loader invariant: node CSV lines (incl. header) minus trimmed rows == 1."""
    return node_csv_lines - trimmed_rows == 1


def check_alignment(stem: str, root: str = DATA_ROOT) -> dict:
    """Return {stem, trimmed_rows, node_rows, ok} for one protein stem."""
    trimmed = trimmed_embedding_rows(stem, root)
    nodes = graph_node_count(stem, root)
    return {"stem": stem, "trimmed_rows": trimmed, "node_rows": nodes,
            "ok": trimmed == nodes}


def assert_alignment(stem: str, root: str = DATA_ROOT) -> None:
    result = check_alignment(stem, root)
    if not result["ok"]:
        raise ValueError(
            f"ESM3<->graph node misalignment for {stem!r}: "
            f"{result['trimmed_rows']} trimmed embedding rows vs "
            f"{result['node_rows']} graph nodes (expected equal). Check special-token "
            f"trimming / UniProt->PDB alignment in preprocessing/EmbedProtein.py."
        )


def stems_with_graphs(root: str = DATA_ROOT) -> list[str]:
    """Every embedding stem that also has a protein graph (for bulk validation)."""
    out = []
    for path in sorted(glob.glob(os.path.join(root, "embedding_ESM3", "*_ESM3.pkl"))):
        stem = embedding_stem_from_filename(path)
        if has_graph(stem, root):
            out.append(stem)
    return out
