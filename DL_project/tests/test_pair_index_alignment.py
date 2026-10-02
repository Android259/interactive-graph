from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch
from torch_geometric.loader import DataLoader

from dataloader.Dataloader import (
    PLIDataset,
    ProteinGraphData,
    sample_family_balanced_negatives,
    sample_protein_balanced_negatives,
    split_and_sample_family_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
    split_and_sample_interactions,
)


def make_dataset(rows, ordered_pair_ids):
    dataset = object.__new__(PLIDataset)
    dataset.csvtrain = pd.DataFrame(rows)
    dataset.csv = dataset.csvtrain
    dataset.id2pos = {
        pair_id: position
        for position, pair_id in enumerate(ordered_pair_ids)
    }
    return dataset


def test_interaction_sampling_uses_labels_instead_of_row_positions():
    table = pd.DataFrame(
        {
            "Interaction": [1, 0, 1, 0, 0, 1],
            "pair": ["p0", "u1", "p2", "u3", "u4", "p5"],
        },
        index=[10, 11, 12, 13, 14, 15],
    )

    positives, unlabeled = split_and_sample_interactions(
        table,
        seed=7,
        unlabeled_fraction=1.0,
    )

    assert positives["pair"].tolist() == ["p0", "p2", "p5"]
    assert set(unlabeled["pair"]) == {"u1", "u3", "u4"}
    assert positives["Interaction"].eq(1).all()
    assert unlabeled["Interaction"].eq(0).all()
    assert positives.index.tolist() == [10, 12, 15]


def _family_balanced_table():
    # Family A: 2 positives / 5 negatives ; Family B: 1 positive / 3 negatives.
    return pd.DataFrame(
        {
            "Interaction": [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "ProteinDomain": (
                ["A", "A", "A", "A", "A", "A", "A", "B", "B", "B", "B"]
            ),
            "pair": [
                "a_p0", "a_p1", "a_u0", "a_u1", "a_u2", "a_u3", "a_u4",
                "b_p0", "b_u0", "b_u1", "b_u2",
            ],
        },
        index=[100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    )


def test_family_balanced_negatives_match_positive_count_per_family():
    table = _family_balanced_table()

    negatives = sample_family_balanced_negatives(table, seed=3)

    assert negatives["Interaction"].eq(0).all()
    per_family = negatives["ProteinDomain"].str.lower().value_counts().to_dict()
    # 2 positives in A -> 2 negatives; 1 positive in B -> 1 negative.
    assert per_family == {"a": 2, "b": 1}
    # Preserves original interaction-CSV row index and draws only from negatives.
    assert set(negatives.index).issubset({102, 103, 104, 105, 106, 108, 109, 110})


def test_family_balanced_negatives_are_seed_reproducible():
    table = _family_balanced_table()

    first = sample_family_balanced_negatives(table, seed=11)
    same = sample_family_balanced_negatives(table, seed=11)
    other = sample_family_balanced_negatives(table, seed=12)

    assert first.index.tolist() == same.index.tolist()
    # Different seeds should generally draw a different negative subset.
    assert first.index.tolist() != other.index.tolist()


def test_split_family_balanced_keeps_all_positives_and_1to1_totals():
    table = _family_balanced_table()

    positives, negatives = split_and_sample_family_balanced_interactions(table, seed=5)

    assert positives["Interaction"].eq(1).all()
    assert positives["pair"].tolist() == ["a_p0", "a_p1", "b_p0"]
    # Globally 1:1 because every family is balanced 1:1.
    assert len(negatives) == len(positives) == 3


def _protein_balanced_table():
    # Family A holds two proteins: p1 has 2 positives / 3 negatives, p2 has no
    # positives and 2 negatives. Family B holds p3 with 1 positive / 3 negatives.
    # Balancing per family lets A's two draws land on p2, leaving p1 skewed.
    return pd.DataFrame(
        {
            "Interaction": [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "ProteinDomain": ["A"] * 7 + ["B"] * 4,
            "LTPProtein": (
                ["p1", "p1", "p1", "p1", "p1", "p2", "p2"] + ["p3"] * 4
            ),
            "pair": [
                "p1_a0", "p1_a1", "p1_u0", "p1_u1", "p1_u2", "p2_u0", "p2_u1",
                "p3_p0", "p3_u0", "p3_u1", "p3_u2",
            ],
        },
        index=[100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    )


def test_protein_balanced_negatives_match_positive_count_per_protein():
    table = _protein_balanced_table()

    negatives = sample_protein_balanced_negatives(table, seed=3)

    assert negatives["Interaction"].eq(0).all()
    per_protein = negatives["LTPProtein"].str.lower().value_counts().to_dict()
    # 2 positives for p1 -> 2 negatives; 1 for p3 -> 1; p2 has none -> absent.
    assert per_protein == {"p1": 2, "p3": 1}
    # Drawn only from that protein's own negatives, original index preserved.
    assert set(negatives.index).issubset({102, 103, 104, 108, 109, 110})


def test_protein_balance_implies_family_balance():
    table = _protein_balanced_table()

    negatives = sample_protein_balanced_negatives(table, seed=3)

    per_family = negatives["ProteinDomain"].str.lower().value_counts().to_dict()
    # A has 2 positives and B has 1, so a sum of balanced proteins balances both.
    assert per_family == {"a": 2, "b": 1}


def test_protein_balanced_negatives_are_seed_reproducible():
    table = _protein_balanced_table()

    first = sample_protein_balanced_negatives(table, seed=11)
    same = sample_protein_balanced_negatives(table, seed=11)
    other = sample_protein_balanced_negatives(table, seed=12)

    assert first.index.tolist() == same.index.tolist()
    assert first.index.tolist() != other.index.tolist()


def test_split_protein_balanced_keeps_all_positives_and_1to1_totals():
    table = _protein_balanced_table()

    positives, negatives = split_and_sample_protein_balanced_interactions(table, seed=5)

    assert positives["Interaction"].eq(1).all()
    assert positives["pair"].tolist() == ["p1_a0", "p1_a1", "p3_p0"]
    assert len(negatives) == len(positives) == 3


def test_pair_id_position_mapping_is_bijective_and_contiguous():
    dataset = make_dataset(
        {
            "pair_id": [30, 10, 20],
            "LTPProtein": ["P3", "P1", "P2"],
            "Interaction": [1, 0, 1],
        },
        ordered_pair_ids=[10, 20, 30],
    )

    assert set(dataset.id2pos) == set(
        dataset.csvtrain["pair_id"].astype(int)
    )
    assert sorted(dataset.id2pos.values()) == list(range(len(dataset.id2pos)))
    assert [
        pair_id
        for pair_id, _ in sorted(dataset.id2pos.items(), key=lambda item: item[1])
    ] == [10, 20, 30]


def test_protein_weights_are_indexed_by_tanimoto_position_not_csv_row_order():
    dataset = make_dataset(
        {
            "pair_id": [30, 10, 20, 40],
            "LTPProtein": ["RARE", "COMMON", "COMMON", "COMMON"],
            "Interaction": [1, 0, 1, 0],
        },
        ordered_pair_ids=[10, 20, 30, 40],
    )

    weights = dataset.get_protein_weights()

    assert weights.tolist() == pytest.approx([0.25, 0.25, 0.75, 0.25])
    for pair_id, protein_name in zip(
        dataset.csvtrain["pair_id"],
        dataset.csvtrain["LTPProtein"],
    ):
        position = dataset.id2pos[int(pair_id)]
        expected = 0.75 if protein_name.lower() == "rare" else 0.25
        assert weights[position].item() == pytest.approx(expected)


@pytest.mark.parametrize(
    ("square_root", "expected"),
    [
        (
            False,
            {
                10: 2.0 / 3.0,
                20: 4.0 / 3.0,
                30: 4.0 / 3.0,
                40: 2.0 / 3.0,
            },
        ),
        (
            True,
            {
                10: 2.0 / (1.0 + 2.0 ** 0.5),
                20: 2.0 * 2.0 ** 0.5 / (1.0 + 2.0 ** 0.5),
                30: 2.0 * 2.0 ** 0.5 / (1.0 + 2.0 ** 0.5),
                40: 2.0 / (1.0 + 2.0 ** 0.5),
            },
        ),
    ],
)
def test_protein_class_weights_are_normalized_and_position_aligned(
    square_root,
    expected,
):
    dataset = make_dataset(
        {
            "pair_id": [30, 10, 20, 40],
            "LTPProtein": ["RARE", "COMMON", "COMMON", "COMMON"],
            "Interaction": [1, 0, 1, 0],
        },
        ordered_pair_ids=[10, 20, 30, 40],
    )

    weights = dataset.get_protein_class_weights(square_root=square_root)

    assert weights.mean().item() == pytest.approx(1.0)
    for pair_id, expected_weight in expected.items():
        position = dataset.id2pos[pair_id]
        assert weights[position].item() == pytest.approx(expected_weight)


def test_batched_pair_metadata_preserves_sample_position_and_protein_ids():
    first = ProteinGraphData(
        x=torch.ones((2, 1)),
        pair_id=torch.tensor([10]),
        tanimoto_pos=torch.tensor([2]),
        protein_id=torch.tensor([7]),
    )
    second = ProteinGraphData(
        x=torch.ones((3, 1)),
        pair_id=torch.tensor([20]),
        tanimoto_pos=torch.tensor([0]),
        protein_id=torch.tensor([4]),
    )

    batch = next(iter(DataLoader([first, second], batch_size=2)))

    assert batch.pair_id.tolist() == [10, 20]
    assert batch.tanimoto_pos.tolist() == [2, 0]
    assert batch.protein_id.tolist() == [7, 4]


def test_batch_positions_resolve_back_to_the_same_pair_ids():
    id2pos = {10: 0, 20: 1, 30: 2}
    pair_ids_by_position = torch.tensor([10, 20, 30])
    batch_pair_ids = torch.tensor([30, 10])
    batch_positions = torch.tensor([id2pos[int(pair_id)] for pair_id in batch_pair_ids])

    assert pair_ids_by_position[batch_positions].tolist() == batch_pair_ids.tolist()


def test_tanimoto_matrix_is_optional_and_only_the_weights_need_it():
    """The 2.8 GB similarity matrix must not be a dependency of every run.

    Only get_tanimoto_weights reads it, so PLIDataset leaves train_tanimoto_matrix as
    None unless tanimoto_weight is set. Loading it unconditionally once made all 45 jobs
    of a cluster batch die in __init__ on a file that is excluded from the project sync,
    including the ones that never asked for Tanimoto weights.
    """
    dataset = object.__new__(PLIDataset)
    dataset.train_tanimoto_matrix = None

    with pytest.raises(RuntimeError, match="tanimoto_weight"):
        dataset.get_tanimoto_weights()


def test_tanimoto_weights_align_with_id2pos_positions():
    """The weights vector is indexed by tanimoto_pos, so it must be one entry per pair.

    This is what lets the no-weighting fallback in new_train.py size itself from
    len(id2pos) instead of having to build the Tanimoto weights just to copy their shape.
    """
    dataset = object.__new__(PLIDataset)
    # Three rows over two distinct pair ids.
    dataset.train_tanimoto_batch = torch.tensor([10, 20, 10])
    dataset.train_tanimoto_matrix = torch.full((3, 3), 255, dtype=torch.uint8)
    dataset.id2pos = {10: 0, 20: 1}

    weights = dataset.get_tanimoto_weights()

    assert weights.shape == (len(dataset.id2pos),)
    # Identical fingerprints (255 everywhere) mean zero distinctiveness.
    assert torch.allclose(weights, torch.zeros(2))


def test_marginal_balance_weights_flatten_protein_class_and_lipid_rates():
    # Protein A is 3:1 positive, protein B 1:3 -- a live protein prior. Every lipid
    # carries one label of each kind, and the weights that flatten all three margins
    # exist (the PE(36:1) pair must weigh as much as A's three positives together).
    lipids = [
        "Phosphatidylcholine (34:1)", "Phosphatidylcholine (36:1)",
        "Phosphatidylethanolamine (34:1)", "Phosphatidylethanolamine (36:1)",
    ]
    rows = {
        "pair_id": list(range(8)),
        "LTPProtein": ["A"] * 4 + ["B"] * 4,
        "FullIdentityOfLipid": lipids + lipids,
        "Interaction": [1, 1, 1, 0, 0, 0, 0, 1],
    }
    dataset = make_dataset(rows, ordered_pair_ids=[7, 6, 5, 4, 3, 2, 1, 0])

    weights = dataset.get_marginal_balance_weights()

    assert weights.shape == (8,)
    assert weights.mean().item() == pytest.approx(1.0)
    row_weight = pd.Series(
        [weights[dataset.id2pos[pair_id]].item() for pair_id in rows["pair_id"]]
    )
    table = pd.DataFrame(rows).assign(
        weight=row_weight,
        lipid_class=lambda frame: frame["FullIdentityOfLipid"].str.split(" ").str[0],
    )
    for key in ("LTPProtein", "lipid_class", "FullIdentityOfLipid"):
        weighted_rate = (
            (table["weight"] * table["Interaction"]).groupby(table[key]).sum()
            / table["weight"].groupby(table[key]).sum()
        )
        assert weighted_rate.to_numpy() == pytest.approx(0.5, abs=1e-3), key


def _chemistry_table():
    # One protein, one positive on L0, four negative candidates at known Tanimoto
    # distances from it: L1/L2 close, L3/L4 far.
    return pd.DataFrame(
        {
            "Interaction": [1, 0, 0, 0, 0],
            "LTPProtein": ["P1"] * 5,
            "ProteinDomain": ["A"] * 5,
            "FullIdentityOfLipid": ["L0", "L1", "L2", "L3", "L4"],
        },
        index=[200, 201, 202, 203, 204],
    )


def _chemistry_pool():
    names = ["L0", "L1", "L2", "L3", "L4"]
    similarity = np.array(
        [
            [1.00, 0.95, 0.90, 0.00, 0.05],
            [0.95, 1.00, 0.92, 0.02, 0.03],
            [0.90, 0.92, 1.00, 0.01, 0.04],
            [0.00, 0.02, 0.01, 1.00, 0.10],
            [0.05, 0.03, 0.04, 0.10, 1.00],
        ],
        dtype=np.float32,
    )
    return similarity, {name: position for position, name in enumerate(names)}


def test_dissimilar_negatives_draw_the_chemistry_farthest_from_the_positives():
    negatives = sample_protein_balanced_negatives(
        _chemistry_table(),
        seed=3,
        ratio=2,
        hard_negative_pool=_chemistry_pool(),
        hard_negative_share=1.0,
        negative_mode="dissimilar",
    )

    # All the steered mass on 1 - similarity, so the two far lipids take the quota.
    assert sorted(negatives["FullIdentityOfLipid"]) == ["L3", "L4"]


def test_hard_negatives_draw_the_opposite_end_of_the_same_pool():
    negatives = sample_protein_balanced_negatives(
        _chemistry_table(),
        seed=3,
        ratio=2,
        hard_negative_pool=_chemistry_pool(),
        hard_negative_share=1.0,
        negative_mode="hard",
    )

    assert sorted(negatives["FullIdentityOfLipid"]) == ["L1", "L2"]


def test_dissimilar_negatives_keep_the_per_protein_class_balance():
    table = _protein_balanced_table().assign(
        FullIdentityOfLipid=lambda frame: "L" + frame["pair"]
    )
    names = sorted(table["FullIdentityOfLipid"].unique())
    pool = (
        np.eye(len(names), dtype=np.float32),
        {name: position for position, name in enumerate(names)},
    )

    negatives = sample_protein_balanced_negatives(
        table,
        seed=3,
        hard_negative_pool=pool,
        negative_mode="dissimilar",
    )

    per_protein = negatives["LTPProtein"].str.lower().value_counts().to_dict()
    assert per_protein == {"p1": 2, "p3": 1}


def test_unknown_negative_mode_is_refused():
    with pytest.raises(ValueError, match="negative_mode"):
        sample_protein_balanced_negatives(
            _chemistry_table(), seed=3, negative_mode="sideways"
        )
