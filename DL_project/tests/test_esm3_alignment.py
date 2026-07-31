"""Training-free check that ESM3 embeddings line up with protein graph nodes.

The protein encoder concatenates ESM3 row ``i`` onto graph node ``i``, so after
special-token trimming the embedding must have exactly one row per graph residue.
These tests assert that count invariant for every stored embedding that has a
protein graph -- pure file reads, no model and no training involved.

Run: pytest tests/test_esm3_alignment.py
"""
import pytest
import pandas as pd

from dataloader.plm_alignment import (
    check_alignment,
    stems_with_graphs,
)
from dataloader.protein_registry import load_protein_registry

STEMS = stems_with_graphs()


def test_protein_registry_covers_active_interaction_table():
    interactions = pd.read_csv(
        "data/Processed_Negative_Interaction_Without_Duplicates.csv"
    )
    registry = load_protein_registry("data")

    assert set(interactions["LTPProtein"].dropna().unique()) == set(registry)
    assert len({row["artifact_stem"] for row in registry.values()}) == len(registry)


def test_there_are_embeddings_with_graphs_to_check():
    assert STEMS, "no ESM3 embeddings with matching protein graphs were found"


@pytest.mark.parametrize("stem", STEMS)
def test_esm3_embedding_aligns_with_graph_nodes(stem):
    result = check_alignment(stem)
    assert result["ok"], (
        f"{stem}: {result['trimmed_rows']} trimmed ESM3 rows vs "
        f"{result['node_rows']} graph nodes"
    )


def test_report_all_misaligned_stems():
    """Aggregate view: list every stem whose count invariant fails at once."""
    bad = [
        (s, r["trimmed_rows"], r["node_rows"])
        for s in STEMS
        for r in [check_alignment(s)]
        if not r["ok"]
    ]
    assert not bad, "misaligned (stem, trimmed_rows, graph_nodes): " + ", ".join(
        f"{s}({t}!={n})" for s, t, n in bad
    )
