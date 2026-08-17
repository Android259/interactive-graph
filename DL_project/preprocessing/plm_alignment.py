"""Validate that ESM3 per-residue embeddings line up with protein graph nodes.

The protein encoder concatenates ESM3 row ``i`` onto graph node ``i``
(``node = torch.cat((node, plm), -1)`` in architecture/protein_encoder.py), so a
stored embedding must have **exactly one row per graph residue** once its BOS/EOS pair
is removed, *and those rows must be in the graph's order*.

Scope / honesty: this checks both the count and the ORDER, the latter by comparing
the FASTA that ESM3 was actually run on against the graph's own residue names. That
is a real order check for the v1 pipeline, whose embeddings come from
preprocessing/pdb2fasta.py output. It is not a UniProt->PDB alignment: if a protein's
FASTA ever stops being structure-derived, the counts could still agree while the
residue comparison starts reporting mismatches -- which is exactly the intended signal.

A count-only check is what let the GM2A/PITPNA selenomethionine bug survive: MSE
residues were kept by pdb2fasta.py and deleted by Voronota, so the embedding had two
(resp. eight) extra rows in the MIDDLE of the sequence, and the symmetric end-trim that
used to compensate restored the count while shifting the order. That is fixed at the
source now -- preprocessing/convert_mse_to_met.py, then a graph rebuild -- so no row
selection survives in the loader beyond dropping BOS/EOS, and this check is what keeps
it that way.
"""
from __future__ import annotations

import csv
import glob
import os
import pickle as pkl
from pathlib import Path

DATA_ROOT = str(Path(__file__).resolve().parent.parent / "data")

# MSE (selenomethionine) is the non-standard residue this project's structures
# actually contain; pdb2fasta.py maps it to 'M' the same way.
THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V", "MSE": "M", "SEC": "U", "PYL": "O",
}


def embedding_stem_from_filename(path: str) -> str:
    """Stem from an embedding filename, e.g. 'ATCAY_AF-..._ESM3.pkl' -> 'ATCAY'."""
    return os.path.basename(path).split("_")[0]


def embedding_path_for_stem(stem: str, root: str = DATA_ROOT) -> str:
    hits = sorted(glob.glob(os.path.join(root, "embedding_ESM3", stem + "_*")))
    if not hits:
        raise FileNotFoundError(f"no ESM3 embedding for stem {stem!r} under {root}")
    return hits[0]


def fasta_path_for_stem(stem: str, root: str = DATA_ROOT) -> str:
    """The FASTA v1 ESM3 was run on ('<stem>_<pdb>.fasta' or '<stem>-<uniprot>...')."""
    hits = [
        path
        for path in sorted(glob.glob(os.path.join(root, "fasta", "*.fasta")))
        if os.path.basename(path).split(".")[0].replace("-", "_").split("_")[0] == stem
    ]
    if len(hits) != 1:
        raise FileNotFoundError(
            f"expected one FASTA for stem {stem!r} under {root}/fasta, found {len(hits)}"
        )
    return hits[0]


def node_csv_for_stem(stem: str, root: str = DATA_ROOT) -> str:
    return os.path.join(root, "graphs", stem, "coarse_graph_nodes.csv")


def has_graph(stem: str, root: str = DATA_ROOT) -> bool:
    return os.path.isfile(node_csv_for_stem(stem, root))


def fasta_sequence(stem: str, root: str = DATA_ROOT) -> str:
    """One-letter sequence ESM3 embedded (one row per character, plus BOS/EOS)."""
    with open(fasta_path_for_stem(stem, root)) as handle:
        return "".join(line.strip() for line in handle if not line.startswith(">"))


def graph_sequence(stem: str, root: str = DATA_ROOT) -> str:
    """One-letter residues of the coarse graph, in node order."""
    with open(node_csv_for_stem(stem, root), newline="") as handle:
        return "".join(
            THREE_TO_ONE.get(row["ID_resName"].strip(), "X")
            for row in csv.DictReader(handle)
        )


def _raw_embedding_rows(path: str) -> int:
    with open(path, "rb") as handle:
        tensor = pkl.load(handle)
    return int(tensor.shape[0])


def trimmed_embedding_rows(stem: str, root: str = DATA_ROOT) -> int:
    """Embedding rows the loader keeps: raw minus the BOS/EOS pair."""
    raw = _raw_embedding_rows(embedding_path_for_stem(stem, root))
    return raw - 2


def graph_node_count(stem: str, root: str = DATA_ROOT) -> int:
    """Number of residue rows in the coarse graph (CSV lines minus the header)."""
    with open(node_csv_for_stem(stem, root)) as handle:
        return sum(1 for _ in handle) - 1


def rows_match_nodes(trimmed_rows: int, node_csv_lines: int) -> bool:
    """Loader invariant: node CSV lines (incl. header) minus trimmed rows == 1."""
    return node_csv_lines - trimmed_rows == 1


def check_alignment(stem: str, root: str = DATA_ROOT) -> dict:
    """Count AND order check for one protein stem.

    ``mismatches`` holds the graph node indices whose residue differs from the residue
    of the embedding row the loader attaches to it -- empty when the mapping is right.
    """
    trimmed = trimmed_embedding_rows(stem, root)
    nodes = graph_node_count(stem, root)

    sequence = fasta_sequence(stem, root)
    graph = graph_sequence(stem, root)
    mismatches = [i for i, (a, b) in enumerate(zip(sequence, graph)) if a != b]

    return {
        "stem": stem,
        "trimmed_rows": trimmed,
        "node_rows": nodes,
        "fasta_residues": len(sequence),
        "mismatches": mismatches,
        "ok": trimmed == nodes and len(sequence) == len(graph) and not mismatches,
    }


def assert_alignment(stem: str, root: str = DATA_ROOT) -> None:
    result = check_alignment(stem, root)
    if not result["ok"]:
        raise ValueError(
            f"ESM3<->graph node misalignment for {stem!r}: "
            f"{result['trimmed_rows']} kept embedding rows vs "
            f"{result['node_rows']} graph nodes, "
            f"{len(result['mismatches'])} residue mismatches "
            f"(first at {result['mismatches'][:5]}). If the structure contains "
            f"selenomethionine, rebuild its graph from a "
            f"preprocessing/convert_mse_to_met.py output."
        )


def stems_with_graphs(root: str = DATA_ROOT) -> list[str]:
    """Every embedding stem that also has a protein graph (for bulk validation)."""
    out = []
    for path in sorted(glob.glob(os.path.join(root, "embedding_ESM3", "*_ESM3.pkl"))):
        stem = embedding_stem_from_filename(path)
        if has_graph(stem, root):
            out.append(stem)
    return out
