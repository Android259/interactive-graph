import json

import numpy as np
import pandas as pd
import pytest

from preprocessing.build_protein_sequence_similarity import build_aligner, pair_scores
from preprocessing.build_protein_tmscore import pair_tmscore
from preprocessing.protein_similarity_common import (
    Structure,
    encode_uint8,
    load_similarity,
    protein_order,
    read_structure,
    similarity_paths,
    structure_path,
    write_similarity,
)


def pdb_text(residues, chain="A", start=1):
    """A minimal single-model PDB holding one N and one CA atom per residue."""
    lines, serial = [], 1
    for offset, name in enumerate(residues):
        for atom, element in (("N", "N"), ("CA", "C")):
            x = float(offset)
            lines.append(
                f"ATOM  {serial:>5}  {atom:<3} {name} {chain}{start + offset:>4}    "
                f"{x:>8.3f}{0.0:>8.3f}{0.0:>8.3f}  1.00 10.00          {element:>2}"
            )
            serial += 1
    lines.append("END")
    return "\n".join(lines) + "\n"


def write_pdb(directory, name, residues, **kwargs):
    path = structure_path(directory, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pdb_text(residues, **kwargs))
    return path


def test_read_structure_keeps_sequence_and_coordinates_in_lock_step(tmp_path):
    path = write_pdb(tmp_path, "P1", ["MET", "LYS", "VAL"])

    structure = read_structure(path, "P1")

    assert structure.sequence == "MKV"
    assert structure.coords.shape == (3, 3)
    # One CA per residue, at the x offset pdb_text gave it, so a reordering or a dropped
    # residue is visible rather than silently shifting the TM-align point cloud.
    assert structure.coords[:, 0].tolist() == [0.0, 1.0, 2.0]
    assert structure.unknown == 0


def test_read_structure_counts_non_standard_residues_as_unknown(tmp_path):
    path = write_pdb(tmp_path, "P1", ["MET", "MSE", "VAL"])

    structure = read_structure(path, "P1")

    assert structure.sequence == "MXV"
    assert structure.unknown == 1


def test_read_structure_rejects_a_second_chain(tmp_path):
    path = structure_path(tmp_path, "P1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        pdb_text(["MET", "LYS"], chain="A")
        + pdb_text(["VAL", "ALA"], chain="B")
    )

    with pytest.raises(ValueError, match="single chain"):
        read_structure(path, "P1")


def test_protein_order_is_first_appearance_and_indexes_every_row():
    table = pd.DataFrame({"LTPProtein": ["GLTP", "BPI", "GLTP", "FABP1", "BPI"]})

    names, protein_index = protein_order(table)

    assert names == ["GLTP", "BPI", "FABP1"]
    assert protein_index.tolist() == [0, 1, 0, 2, 1]
    assert protein_index.dtype == np.int32


def test_encode_uint8_matches_the_compact_tanimoto_encoding():
    matrix = np.array([[1.0, 0.5, 0.0], [0.5, 1.0, 1.0 / 255], [0.0, 1.0 / 255, 1.0]])

    encoded = encode_uint8(matrix)

    assert encoded.dtype == np.uint8
    assert encoded[0, 1] == 128
    assert encoded[1, 2] == 1
    assert encoded[0, 2] == 0
    assert np.diag(encoded).tolist() == [255, 255, 255]


def test_encode_uint8_clips_a_rounding_excess_past_one():
    encoded = encode_uint8(np.array([[1.0, 1.0000001], [1.0000001, 1.0]]))

    assert encoded.tolist() == [[255, 255], [255, 255]]


def make_artifacts(tmp_path, names=("GLTP", "BPI")):
    source = tmp_path / "interactions.csv"
    pd.DataFrame({"LTPProtein": list(names)}).to_csv(source, index=False)
    for name in names:
        write_pdb(tmp_path, name, ["MET", "LYS"])
    matrix = encode_uint8(np.array([[1.0, 0.25], [0.25, 1.0]]))
    protein_index = np.arange(len(names), dtype=np.int32)
    from preprocessing.protein_similarity_common import structure_provenance

    write_similarity(
        tmp_path,
        "identity",
        matrix,
        protein_index,
        list(names),
        source,
        structure_provenance(tmp_path, names),
        {"normalization": "max(len_a, len_b)"},
    )
    return source


def test_write_then_load_round_trips_the_matrix_and_the_names(tmp_path):
    source = make_artifacts(tmp_path)

    loaded = load_similarity(tmp_path, "identity", source, data_dir=tmp_path)

    assert loaded.proteins == 2
    assert loaded.names == ["GLTP", "BPI"]
    assert loaded.index == {"GLTP": 0, "BPI": 1}
    assert loaded.of("GLTP", "BPI") == pytest.approx(0.25, abs=1 / 255)
    assert loaded.of("GLTP", "GLTP") == 1.0
    assert loaded.protein_index.tolist() == [0, 1]
    assert loaded.normalization == "max(len_a, len_b)"


def test_load_refuses_artifacts_whose_interaction_table_moved(tmp_path):
    source = make_artifacts(tmp_path)
    pd.DataFrame({"LTPProtein": ["GLTP", "BPI", "FABP1"]}).to_csv(source, index=False)

    assert load_similarity(tmp_path, "identity", source) is None


def test_load_refuses_artifacts_whose_structures_moved(tmp_path):
    source = make_artifacts(tmp_path)
    write_pdb(tmp_path, "BPI", ["MET", "LYS", "VAL"])

    # The table is untouched, so only the structure check can catch this.
    assert load_similarity(tmp_path, "identity", source) is not None
    assert load_similarity(tmp_path, "identity", source, data_dir=tmp_path) is None


def test_manifest_records_the_metric_and_its_parameters(tmp_path):
    make_artifacts(tmp_path)
    _, _, manifest_path = similarity_paths(tmp_path, "identity")

    manifest = json.loads(manifest_path.read_text())

    assert manifest["metric"] == "identity"
    assert manifest["names"] == ["GLTP", "BPI"]
    assert manifest["parameters"]["normalization"] == "max(len_a, len_b)"
    assert set(manifest["structures"]) == {"GLTP", "BPI"}


def sequence_structure(name, sequence):
    coords = np.zeros((len(sequence), 3), dtype=np.float64)
    coords[:, 0] = np.arange(len(sequence), dtype=np.float64)
    return Structure(name, sequence, coords, 0)


def test_identical_sequences_score_one_on_both_sequence_metrics():
    aligner, matrix = build_aligner(-11.0, -1.0)
    structure = sequence_structure("P1", "MKVLAAGIVGQWEYTSRK")

    identity, blosum = pair_scores(aligner, matrix, structure, structure)

    assert identity == pytest.approx(1.0)
    assert blosum == pytest.approx(1.0)


def test_sequence_metrics_divide_by_the_longer_sequence():
    aligner, matrix = build_aligner(-11.0, -1.0)
    # The shorter sequence is contained in the longer one, so every one of its 9 residues
    # aligns identically: 9/18 against the longer sequence, not 9/9 against itself.
    long_structure = sequence_structure("P1", "MKVLAAGIVWWWWWWWWW")
    short_structure = sequence_structure("P2", "MKVLAAGIV")

    identity, blosum = pair_scores(aligner, matrix, long_structure, short_structure)

    assert identity == pytest.approx(9 / 18)
    assert blosum == pytest.approx(9 / 18)


def test_conservative_substitutions_count_only_for_the_blosum_metric():
    aligner, matrix = build_aligner(-11.0, -1.0)
    # I -> L and K -> R are the textbook positive-scoring substitutions; the two
    # sequences differ in exactly those two of their eight columns.
    left = sequence_structure("P1", "MKVLAAIK")
    right = sequence_structure("P2", "MKVLAALR")

    identity, blosum = pair_scores(aligner, matrix, left, right)

    assert identity == pytest.approx(6 / 8)
    assert blosum == pytest.approx(1.0)


def test_a_structure_against_itself_scores_a_tmscore_of_one():
    # A straight line is a degenerate fold, so the coordinates come from a real
    # structure's shape: a helix, which TM-align can superpose unambiguously.
    turn = np.arange(60, dtype=np.float64) * 1.74
    coords = np.stack(
        [2.3 * np.cos(turn), 2.3 * np.sin(turn), np.arange(60) * 1.5], axis=1
    )
    structure = Structure("P1", "A" * 60, coords, 0)

    score, rmsd, aligned = pair_tmscore(structure, structure)

    assert score == pytest.approx(1.0, abs=1e-6)
    # Not exactly zero: TM-align reports the RMSD of the superposition its own heuristic
    # search settled on, which lands 2e-4 A off the identity rotation here.
    assert rmsd == pytest.approx(0.0, abs=1e-3)
    assert aligned == 60
