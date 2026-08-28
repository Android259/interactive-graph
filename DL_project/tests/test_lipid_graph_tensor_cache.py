from types import SimpleNamespace

import pandas as pd
import torch

from dataloader.lipid_graph_tensor_cache import (
    build_lipid_graph_tensor_cache,
    load_lipid_graph_tensor_cache,
)
from dataloader.lipid_isomer_graph_builder import LipidIsomerGraphBuilder
from tests.test_dataloader_lipid_graphs import make_dataset, write_graph


def test_build_and_load_round_trips_every_graph(tmp_path):
    graphs_dir = tmp_path / "lipid_graphs"
    write_graph(graphs_dir, "graph_a", 2)
    write_graph(graphs_dir, "graph_b", 3)

    cache_path, manifest_path, count = build_lipid_graph_tensor_cache(tmp_path)

    assert count == 2
    assert cache_path.exists() and manifest_path.exists()

    cache = load_lipid_graph_tensor_cache(tmp_path)
    assert set(cache) == {"graph_a", "graph_b"}
    assert cache["graph_a"]["x"].shape == (2, 11)
    assert cache["graph_a"]["edge_attr"].shape == (2, 6 + 16)
    assert cache["graph_a"]["chain_rank"].shape == (2,)
    assert cache["graph_b"]["x"].shape == (3, 11)


def test_cache_hit_matches_direct_csv_parse(tmp_path):
    graphs_dir = tmp_path / "lipid_graphs"
    write_graph(graphs_dir, "graph_a", 2)
    build_lipid_graph_tensor_cache(tmp_path)
    cache = load_lipid_graph_tensor_cache(tmp_path)

    dataset = make_dataset(graph_dir=graphs_dir)
    dataset.lipid_graph_index = {"CC": "graph_a"}
    dataset._lipid_graph_tensor_cache = cache
    from_cache = LipidIsomerGraphBuilder._one_lipid_graph_parts(dataset, "CC")

    dataset_no_cache = make_dataset(graph_dir=graphs_dir)
    dataset_no_cache.lipid_graph_index = {"CC": "graph_a"}
    dataset_no_cache._lipid_graph_tensor_cache = {}
    from_disk = LipidIsomerGraphBuilder._one_lipid_graph_parts(dataset_no_cache, "CC")

    for key in ("x", "edge_index", "edge_attr", "chain_rank"):
        assert torch.equal(from_cache[key], from_disk[key]), key


def test_missing_cache_files_fall_back_to_empty_dict(tmp_path):
    assert load_lipid_graph_tensor_cache(tmp_path) == {}


def test_stale_source_invalidates_cache(tmp_path):
    graphs_dir = tmp_path / "lipid_graphs"
    write_graph(graphs_dir, "graph_a", 2)
    build_lipid_graph_tensor_cache(tmp_path)
    assert load_lipid_graph_tensor_cache(tmp_path) != {}

    # Rewriting a source CSV changes its size/mtime, which the manifest guards --
    # same staleness contract as protein_graph_tensor_cache.
    import shutil

    shutil.rmtree(graphs_dir / "graph_a")
    write_graph(graphs_dir, "graph_a", 4)
    assert load_lipid_graph_tensor_cache(tmp_path) == {}


def test_release_source_artifacts_keeps_cache_for_the_drawing_split():
    from dataloader.Dataloader import PLIDataset

    dataset = object.__new__(PLIDataset)
    dataset.config = SimpleNamespace(lipid_graph_isomers=True, lipid_random_choice=True)
    dataset._draw_lipid_candidate = True
    dataset._lipid_graph_tensor_cache = {"graph_a": {}}
    dataset.smiles_encoding = None

    released = dataset.release_source_artifacts()

    assert "lipid_graph_tensor_cache" not in released
    assert dataset._lipid_graph_tensor_cache == {"graph_a": {}}


def test_release_source_artifacts_drops_cache_for_a_non_drawing_split():
    from dataloader.Dataloader import PLIDataset

    dataset = object.__new__(PLIDataset)
    dataset.config = SimpleNamespace(lipid_graph_isomers=True, lipid_random_choice=True)
    dataset._draw_lipid_candidate = False
    dataset._lipid_graph_tensor_cache = {"graph_a": {}}
    dataset.smiles_encoding = None

    released = dataset.release_source_artifacts()

    assert "lipid_graph_tensor_cache" in released
    assert dataset._lipid_graph_tensor_cache == {}
