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
import pandas as pd

import glob

from preprocessing.plm_alignment import (
    check_alignment,
    has_graph,
    stems_with_graphs,
)
INTERACTIONS = "data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv"

STEMS = stems_with_graphs()


def interaction_proteins():
    return sorted(pd.read_csv(INTERACTIONS)["LTPProtein"].dropna().unique())


def test_protein_domain_is_one_value_per_protein():
    """ProteinDomain is the family the model one-hots, so it must be a protein constant.

    There is no protein registry any more: the interaction table is the only source of
    per-protein metadata, and protein_graph_builder.protein_family reads this column
    directly. A protein whose rows disagreed here would silently change its family
    between samples.
    """
    interactions = pd.read_csv(INTERACTIONS)
    ambiguous = {
        name: sorted(group.unique())
        for name, group in interactions.groupby("LTPProtein")["ProteinDomain"]
        if len(group.unique()) != 1
    }
    assert not ambiguous, f"proteins with more than one ProteinDomain: {ambiguous}"


def test_every_interaction_protein_owns_artifacts_under_its_own_name():
    """No rename map: the interaction table's protein name IS the artifact name."""
    missing = []
    for protein_id in interaction_proteins():
        if not has_graph(protein_id):
            missing.append(f"{protein_id}: no data/graphs/{protein_id}")
        for pattern in (
            f"data/embedding_ESM3/{protein_id}_*_ESM3.pkl",
            f"data/embedding_ESM3_v2/{protein_id}_ESM3v2.pkl",
            f"data/embedding_RNABANG/{protein_id}_RNABANG.pkl",
            f"data/esm3_input/{protein_id}.pdb",
        ):
            if not glob.glob(pattern):
                missing.append(f"{protein_id}: nothing matches {pattern}")
    assert not missing, "artifacts not filed under the protein's own name: " + "; ".join(missing)


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
