"""Training-free check that ESM3 embeddings line up with protein graph nodes.

The protein encoder concatenates ESM3 row ``i`` onto graph node ``i``, so after
special-token trimming and drop-row removal the embedding must have exactly one row
per graph residue, in the graph's order. These tests assert both -- the count and,
by comparing the embedded FASTA against the graph's residue names, the order -- for
every stored embedding that has a protein graph. Pure file reads, no model and no
training involved.

Run: pytest tests/test_esm3_alignment.py
"""
import pytest

from preprocessing.plm_alignment import (
    check_alignment,
    stems_with_graphs,
)

STEMS = stems_with_graphs()


def test_there_are_embeddings_with_graphs_to_check():
    assert STEMS, "no ESM3 embeddings with matching protein graphs were found"


@pytest.mark.parametrize("stem", STEMS)
def test_esm3_embedding_aligns_with_graph_nodes(stem):
    result = check_alignment(stem)
    assert result["ok"], (
        f"{stem}: {result['trimmed_rows']} kept ESM3 rows vs "
        f"{result['node_rows']} graph nodes, "
        f"{len(result['mismatches'])} residue mismatches "
        f"(first node indices {result['mismatches'][:5]})"
    )


def test_report_all_misaligned_stems():
    """Aggregate view: list every stem whose count or order invariant fails at once."""
    bad = [
        (s, r["trimmed_rows"], r["node_rows"], len(r["mismatches"]))
        for s in STEMS
        for r in [check_alignment(s)]
        if not r["ok"]
    ]
    assert not bad, (
        "misaligned (stem, kept_rows, graph_nodes, residue_mismatches): "
        + ", ".join(f"{s}({t} vs {n}, {m} mismatched)" for s, t, n, m in bad)
    )
