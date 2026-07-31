import pandas as pd
from rdkit import Chem

from data import build_lipid_isomer_graphs as graphs


def test_iter_smiles_skips_empty_values_and_normalizes_slashes():
    assert list(graphs.iter_smiles("0")) == []
    assert list(graphs.iter_smiles("")) == []
    assert list(graphs.iter_smiles(" C//C ; C\\\\C ")) == ["C/C", "C\\C"]


def test_canonical_isomeric_smiles_returns_canonical_and_mol():
    canonical, mol = graphs.canonical_isomeric_smiles("CCO")

    assert canonical == "CCO"
    assert mol is not None


def test_canonical_isomeric_smiles_handles_invalid_smiles():
    canonical, mol = graphs.canonical_isomeric_smiles("not a smiles")

    assert canonical is None
    assert mol is None


def test_graph_id_from_smiles_is_stable_sha1_prefix():
    assert graphs.graph_id_from_smiles("CCO") == graphs.graph_id_from_smiles("CCO")
    assert len(graphs.graph_id_from_smiles("CCO")) == 16


def test_write_lipid_graph_writes_nodes_and_directed_edges(tmp_path):
    graph_dir = tmp_path / "ethanol"
    mol = Chem.MolFromSmiles("CCO")

    graphs.write_lipid_graph(graph_dir, mol)

    nodes = pd.read_csv(graph_dir / "nodes.csv")
    edges = pd.read_csv(graph_dir / "edges.csv")
    assert list(nodes.columns) == graphs.NODE_COLUMNS
    assert list(edges.columns) == graphs.EDGE_COLUMNS
    assert len(nodes) == 3
    assert len(edges) == 4
    assert set(map(tuple, edges[["source", "target"]].values.tolist())) == {
        (0, 1),
        (1, 0),
        (1, 2),
        (2, 1),
    }
