import pandas as pd
import pytest
import torch

from dataloader.GRAB_graph import (
    build_pair_graph_edges,
    edges_from_grouped_pairs,
    keep_top_k_edges_per_pair,
    load_pair_table,
)


def test_load_pair_table_adds_pair_id_and_grab_label(tmp_path):
    csv_path = tmp_path / "pairs.csv"
    pd.DataFrame({
        "LTPProtein": ["P1", "P2"],
        "FullIdentityOfLipid": ["L1", "L2"],
        "Interaction": [1, 0],
    }).to_csv(csv_path, index=False)

    table = load_pair_table(csv_path)

    assert table["pair_id"].tolist() == [0, 1]
    assert table["grab_label"].tolist() == [1, 0]


def test_load_pair_table_raises_for_missing_required_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame({"LTPProtein": ["P1"]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        load_pair_table(csv_path)


def test_edges_from_grouped_pairs_connects_only_pairs_in_same_group():
    table = pd.DataFrame({
        "pair_id": [0, 1, 2],
        "LTPProtein": ["P1", "P1", "P2"],
    })

    edges = edges_from_grouped_pairs(table, "LTPProtein")

    assert sorted(edges) == [(0, 1, 1.0), (1, 0, 1.0)]


def test_keep_top_k_edges_per_pair_keeps_highest_weight_per_target():
    edges = [(0, 2, 0.1), (1, 2, 0.9), (3, 2, 0.5), (0, 1, 1.0)]

    kept = keep_top_k_edges_per_pair(edges, top_k_edges_per_pair=2)

    assert kept == [(0, 1, 1.0), (1, 2, 0.9), (3, 2, 0.5)]


def test_keep_top_k_edges_per_pair_randomizes_equal_weight_ties_reproducibly():
    edges = [(source, 10, 1.0) for source in range(20)]

    first = keep_top_k_edges_per_pair(edges, top_k_edges_per_pair=5, random_seed=7)
    repeated = keep_top_k_edges_per_pair(edges, top_k_edges_per_pair=5, random_seed=7)
    other_seed = keep_top_k_edges_per_pair(edges, top_k_edges_per_pair=5, random_seed=8)

    assert first == repeated
    assert first != other_seed
    assert [source for source, _, _ in first] != list(range(5))


def test_build_pair_graph_edges_sums_weights_limits_targets_and_adds_reverse():
    table = pd.DataFrame({
        "pair_id": [0, 1, 2],
        "LTPProtein": ["P1", "P1", "P2"],
        "FullIdentityOfLipid": ["L1", "L1", "L1"],
    })

    edge_index, edge_weight = build_pair_graph_edges(table, top_k_edges_per_pair=1)
    edges = {
        tuple(edge): float(weight)
        for edge, weight in zip(edge_index.t().tolist(), edge_weight.tolist())
    }

    assert edge_index.dtype == torch.long
    assert edge_weight.dtype == torch.float32
    assert edges[(0, 1)] == 2.0
    assert edges[(1, 0)] == 2.0
    assert all(source != target for source, target in edges)


def test_build_pair_graph_edges_returns_empty_graph_without_connections():
    table = pd.DataFrame({
        "pair_id": [0],
        "LTPProtein": ["P1"],
        "FullIdentityOfLipid": ["L1"],
    })

    edge_index, edge_weight = build_pair_graph_edges(table)

    assert edge_index.shape == (2, 0)
    assert edge_weight.shape == (0,)
