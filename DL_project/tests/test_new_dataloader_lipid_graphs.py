from types import SimpleNamespace

import pandas as pd
import pytest
import torch
from torch_geometric.loader import DataLoader

from dataloader.New_dataloader import LipidGraphData, PLIDataset, ProteinGraphData


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
    "source",
    "target",
    "bond_type",
    "is_conjugated",
    "is_in_ring",
    "stereo",
    "bond_dir",
    "is_aromatic",
]


def make_dataset(config=None, graph_dir=None):
    dataset = object.__new__(PLIDataset)
    dataset.config = config or SimpleNamespace(
        lipid_concat=True,
        lipid_random_choice=False,
        lipid_fragments_mask=False,
    )
    dataset.lipid_graph_dir = str(graph_dir) if graph_dir is not None else ""
    dataset.lipid_graph_index = {}
    dataset.labelOH = {"PC": [1, 0, 0]}
    # The real __init__ creates these; this fixture builds the object with
    # object.__new__, so the per-lipid caches have to be supplied here.
    dataset._lipid_graph_cache = {}
    dataset._lipid_graph_table_cache = {}
    dataset._lipid_encoding_cache = {}
    dataset._lipid_candidate_key_cache = {}
    return dataset


def write_graph(graph_dir, graph_id, num_nodes):
    path = graph_dir / graph_id
    path.mkdir(parents=True)
    nodes = pd.DataFrame([
        {
            "atomic_num": 6,
            "formal_charge": 0,
            "degree": 1,
            "hybridization": 4,
            "is_aromatic": 0,
            "is_in_ring": 0,
            "chiral_tag": 0,
            "chirality_possible": 0,
            "total_num_hs": 3,
            "mass": 12.011,
            "gasteiger_charge": 0.0,
        }
        for _ in range(num_nodes)
    ])
    edges = pd.DataFrame([
        {
            "source": 0,
            "target": 1,
            "bond_type": 1.0,
            "is_conjugated": 0,
            "is_in_ring": 0,
            "stereo": 0,
            "bond_dir": 0,
            "is_aromatic": 0,
        },
        {
            "source": 1,
            "target": 0,
            "bond_type": 1.0,
            "is_conjugated": 0,
            "is_in_ring": 0,
            "stereo": 0,
            "bond_dir": 0,
            "is_aromatic": 0,
        },
    ])
    nodes.to_csv(path / "nodes.csv", index=False)
    edges.to_csv(path / "edges.csv", index=False)


def make_embedding_dataset(**overrides):
    values = {
        "lipid_concat": False,
        "lipid_random_choice": False,
        "lipid_fragments_mask": False,
        "lipid_isomers": False,
        "lipid_first_fragment_only": True,
    }
    values.update(overrides)
    config = SimpleNamespace(**values)
    dataset = make_dataset(config)
    dataset.smiles_encoding = {
        "CC": torch.arange(6, dtype=torch.float32).reshape(1, 2, 3),
        "CCC": torch.arange(6, 12, dtype=torch.float32).reshape(1, 2, 3),
    }
    return dataset


def test_lipid_encoding_preserves_single_smiles_lookup():
    dataset = make_embedding_dataset()

    encoding = dataset.lipid_encoding("CC", "0")

    assert torch.equal(encoding, dataset.smiles_encoding["CC"].squeeze())


def test_lipid_encoding_uses_first_fragment_for_concat():
    dataset = make_embedding_dataset(lipid_concat=True)

    encoding = dataset.lipid_encoding("0", "CC;CCC")

    assert torch.equal(encoding, dataset.smiles_encoding["CC"].squeeze())


def test_lipid_encoding_preserves_fragment_mask_shape():
    dataset = make_embedding_dataset(lipid_fragments_mask=True)

    encoding, fragment_batch = dataset.lipid_encoding("0", "CC;CCC")

    assert torch.equal(encoding, dataset.smiles_encoding["CC"].squeeze())
    assert fragment_batch.tolist() == [0, 0]


def test_lipid_encoding_concatenates_every_fragment_when_flag_is_off():
    dataset = make_embedding_dataset(
        lipid_concat=True, lipid_first_fragment_only=False
    )

    encoding = dataset.lipid_encoding("0", "CC;CCC")

    expected = torch.cat(
        [dataset.smiles_encoding["CC"], dataset.smiles_encoding["CCC"]], dim=1
    ).squeeze()
    assert torch.equal(encoding, expected)


def test_lipid_encoding_marks_every_fragment_when_flag_is_off():
    dataset = make_embedding_dataset(
        lipid_fragments_mask=True, lipid_first_fragment_only=False
    )

    encoding, fragment_batch = dataset.lipid_encoding("0", "CC;CCC")

    expected = torch.cat(
        [dataset.smiles_encoding["CC"], dataset.smiles_encoding["CCC"]], dim=1
    ).squeeze()
    assert torch.equal(encoding, expected)
    assert fragment_batch.tolist() == [0, 0, 1, 1]


def test_lipid_encoding_random_choice_draws_among_all_fragments(monkeypatch):
    dataset = make_embedding_dataset(
        lipid_random_choice=True, lipid_first_fragment_only=False
    )
    monkeypatch.setattr(
        "dataloader.lipid_graph_builder.random.choice", lambda values: values[-1]
    )

    encoding = dataset.lipid_encoding("0", "CC;CCC")

    assert torch.equal(encoding, dataset.smiles_encoding["CCC"].squeeze())


def test_cached_lipid_encoding_redraws_on_every_access(monkeypatch):
    dataset = make_embedding_dataset(
        lipid_random_choice=True, lipid_first_fragment_only=False
    )
    drawn = iter([0, 1, 1, 0])
    monkeypatch.setattr(
        "dataloader.lipid_graph_builder.random.choice",
        lambda values: values[next(drawn)],
    )

    seen = [
        dataset.cached_lipid_encoding("0", "CC;CCC") for _ in range(4)
    ]

    # The draw must not be frozen by the cache: persistent workers would keep the
    # first pick for the whole run and random_choice would stop augmenting.
    picked = [int(torch.equal(e, dataset.smiles_encoding["CCC"].squeeze())) for e in seen]
    assert picked == [0, 1, 1, 0]
    assert dataset._lipid_encoding_cache == {}
    assert dataset._lipid_candidate_key_cache == {("0", "CC;CCC"): ("CC", "CCC")}


def test_warm_lipid_encoding_does_not_draw_under_random_choice(monkeypatch):
    dataset = make_embedding_dataset(
        lipid_random_choice=True, lipid_first_fragment_only=False
    )

    def fail(values):
        raise AssertionError("warming must not consume the random stream")

    monkeypatch.setattr("dataloader.lipid_graph_builder.random.choice", fail)

    dataset.warm_lipid_encoding("0", "CC;CCC")

    assert dataset._lipid_candidate_key_cache == {("0", "CC;CCC"): ("CC", "CCC")}


def test_lipid_encoding_skips_empty_and_duplicate_fragments():
    dataset = make_embedding_dataset(
        lipid_concat=True, lipid_first_fragment_only=False
    )

    encoding = dataset.lipid_encoding("0", "CC; CCC; CC; ")

    expected = torch.cat(
        [dataset.smiles_encoding["CC"], dataset.smiles_encoding["CCC"]], dim=1
    ).squeeze()
    assert torch.equal(encoding, expected)


def test_lipid_encoding_reports_a_fragment_missing_from_the_embedding_table():
    dataset = make_embedding_dataset(
        lipid_concat=True, lipid_first_fragment_only=False
    )

    with pytest.raises(KeyError, match="missing from the embedding table"):
        dataset.lipid_encoding("0", "CC;CCCC")


def test_lipid_encoding_rejects_fragments_without_a_parsable_smiles():
    dataset = make_embedding_dataset(lipid_concat=True)

    with pytest.raises(ValueError, match="no parsable lipid SMILES"):
        dataset.lipid_encoding("0", "0; ")


def test_canonical_lipid_smiles_list_skips_invalid_and_deduplicates():
    dataset = make_dataset()

    smiles = dataset.canonical_lipid_smiles_list("CCO;not a smiles;CCO;0")

    assert smiles == ["CCO"]


def test_lipid_graph_smiles_uses_random_fragment(monkeypatch):
    config = SimpleNamespace(
        lipid_concat=False,
        lipid_random_choice=True,
        lipid_fragments_mask=False,
    )
    dataset = make_dataset(config)
    monkeypatch.setattr("dataloader.New_dataloader.random.choice", lambda values: values[-1])
    row = pd.Series({"SmileGlobal": "CCO", "SmileFragment": "CC;CCC"})

    assert dataset.lipid_graph_smiles(row) == ["CCC"]


def test_lipid_graph_id_raises_when_graph_is_missing(tmp_path):
    dataset = make_dataset(graph_dir=tmp_path)

    with pytest.raises(FileNotFoundError, match="Lipid isomer graph not found"):
        dataset.lipid_graph_id("CCO")


def test_make_graph_lipid_concats_fragments_and_offsets_edges(tmp_path):
    config = SimpleNamespace(
        lipid_concat=True,
        lipid_random_choice=False,
        lipid_fragments_mask=False,
    )
    dataset = make_dataset(config, tmp_path)
    dataset.lipid_graph_index = {"CC": "frag_a", "CCC": "frag_b"}
    write_graph(tmp_path, "frag_a", 2)
    write_graph(tmp_path, "frag_b", 2)
    row = pd.Series({"SmileGlobal": "0", "SmileFragment": "CC;CCC"})

    graph = dataset.make_graph_lipid(row)

    assert graph.x.shape == (4, len(NODE_COLUMNS))
    assert graph.edge_attr.shape == (4, len(EDGE_COLUMNS) - 2)
    assert graph.edge_index.tolist() == [[0, 1, 2, 3], [1, 0, 3, 2]]
    assert not hasattr(graph, "lipid_batch")


def test_make_graph_lipid_adds_fragment_mask_for_mask_mode(tmp_path):
    config = SimpleNamespace(
        lipid_concat=False,
        lipid_random_choice=False,
        lipid_fragments_mask=True,
    )
    dataset = make_dataset(config, tmp_path)
    dataset.lipid_graph_index = {"CC": "frag_a", "CCC": "frag_b"}
    write_graph(tmp_path, "frag_a", 2)
    write_graph(tmp_path, "frag_b", 2)
    row = pd.Series({"SmileGlobal": "0", "SmileFragment": "CC;CCC"})

    graph = dataset.make_graph_lipid(row)

    assert graph.lipid_batch.tolist() == [0, 0, 1, 1]


def test_lipid_graph_data_offsets_lipid_batch_when_batched():
    first = LipidGraphData(
        x=torch.ones((2, 1)),
        edge_index=torch.tensor([[0, 1], [1, 0]]),
        lipid_batch=torch.tensor([0, 0]),
    )
    second = LipidGraphData(
        x=torch.ones((2, 1)),
        edge_index=torch.tensor([[0, 1], [1, 0]]),
        lipid_batch=torch.tensor([0, 1]),
    )

    batch = next(iter(DataLoader([first, second], batch_size=2)))

    assert batch.lipid_batch.tolist() == [0, 0, 1, 2]


def test_protein_graph_data_preserves_original_pair_ids_when_batched():
    first = ProteinGraphData(
        x=torch.ones((2, 1)),
        pair_id=torch.tensor([10]),
    )
    second = ProteinGraphData(
        x=torch.ones((3, 1)),
        pair_id=torch.tensor([20]),
    )

    batch = next(iter(DataLoader([first, second], batch_size=2)))

    assert batch.pair_id.tolist() == [10, 20]


def test_grab_graph_uses_only_train_sources(tmp_path):
    dataset = make_dataset()
    dataset.ROOT_DIR = str(tmp_path)
    dataset.csv = pd.DataFrame({
        "pair_id": [0, 1],
        "Interaction": [0, 1],
    })
    pd.DataFrame({
        "source_pair_id": [1, 2, 2],
        "target_pair_id": [0, 0, 1],
        "edge_weight": [1.0, 100.0, 100.0],
    }).to_csv(tmp_path / "grab_pair_graph_edges.csv", index=False)

    graph = dataset.build_current_pair_graph()

    assert graph.pair_id.tolist() == [0, 1]
    assert graph.edge_index.tolist() == [[1], [0]]
    assert graph.label_coefficients_by_target[0].tolist() == [0.0, 1.0]
    assert graph.label_coefficients_by_target[1].tolist() == [0.0, 0.0]


def test_get_grab_batch_inputs_preserves_order_and_shape():
    dataset = make_dataset()
    dataset.pair_graph = SimpleNamespace(
        label_coefficients_by_target={
            10: torch.tensor([1.0, 2.0]),
            20: torch.tensor([3.0, 4.0]),
        }
    )

    coefficients = dataset.get_grab_batch_inputs(
        torch.tensor([20, 10]),
        torch.device("cpu"),
    )

    assert coefficients.tolist() == [[3.0, 4.0], [1.0, 2.0]]


def test_get_grab_batch_inputs_reports_missing_pair_ids():
    dataset = make_dataset()
    dataset.pair_graph = SimpleNamespace(
        label_coefficients_by_target={10: torch.tensor([1.0, 2.0])}
    )

    with pytest.raises(ValueError, match=r"absent.*\[20\]"):
        dataset.get_grab_batch_inputs(
            torch.tensor([10, 20]),
            torch.device("cpu"),
        )
