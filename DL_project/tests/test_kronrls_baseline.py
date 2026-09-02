"""Unit tests for the Kron-RLS baseline building blocks.

Synthetic, small, deterministic -- no dependency on the generated dataset (graphs,
Tanimoto artefacts). Pocket13/23/tanimoto/explicit feature sources are exercised
elsewhere (test_pocket_shape.py, test_descriptor_catalog.py); this file covers only
the code added for Kron-RLS: the solver/out-of-sample extension, the single-axis cold
pool, and the generic custom-vector / custom-kernel loaders.
"""

import numpy as np
import pandas as pd
import pytest

from dataloader.dataset_source import interaction_csv_path
from training.pair_baseline_common import (
    DEFAULT_CSV,
    build_lipid_kernel,
    build_protein_kernel,
    cosine_kernel,
    linear_kernel,
    load_feature_table,
    load_precomputed_kernel,
    predict_kronrls,
    raw_single_cold_pool,
    two_step_kronrls,
)


def _random_psd_kernel(rng, n):
    basis = rng.normal(size=(n, n))
    kernel = basis @ basis.T
    kernel /= np.diag(kernel).max()
    return kernel


def test_default_csv_matches_canonical_dataset_source():
    assert str(DEFAULT_CSV) == interaction_csv_path(str(DEFAULT_CSV.parent))


def test_two_step_kronrls_reconstructs_training_labels_when_lambda_is_zero():
    # Identity kernels make the closed form exact and condition-number-free: with
    # lambda=0, A = I^-1 Y I^-1 = Y, so this checks the solver's algebra rather than
    # numerical conditioning of some particular kernel.
    protein_kernel = np.eye(3)
    lipid_kernel = np.eye(2)
    labels = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    coefficients = two_step_kronrls(protein_kernel, lipid_kernel, labels, 0.0, 0.0)
    assert np.allclose(coefficients, labels)

    reconstructed = predict_kronrls(coefficients, protein_kernel, lipid_kernel)
    assert np.allclose(reconstructed, labels)


def test_predict_kronrls_out_of_sample_matches_manual_formula():
    rng = np.random.default_rng(1)
    kp_train = _random_psd_kernel(rng, 3)
    kl_train = _random_psd_kernel(rng, 3)
    labels = rng.normal(size=(3, 3))
    coefficients = two_step_kronrls(kp_train, kl_train, labels, 0.5, 0.5)

    kp_query_train = rng.normal(size=(2, 3))  # 2 out-of-sample proteins
    kl_train_query = rng.normal(size=(3, 1))  # 1 out-of-sample lipid

    expected = kp_query_train @ coefficients @ kl_train_query
    actual = predict_kronrls(coefficients, kp_query_train, kl_train_query)
    assert np.allclose(actual, expected)


def test_two_step_kronrls_rejects_mismatched_labels():
    protein_kernel = np.eye(3)
    lipid_kernel = np.eye(2)
    labels = np.zeros((3, 3))
    with pytest.raises(ValueError):
        two_step_kronrls(protein_kernel, lipid_kernel, labels, 1.0, 1.0)


def _synthetic_domain_table():
    return pd.DataFrame(
        {
            "LTPProtein": ["A", "A", "B", "B", "C", "C"],
            "ProteinDomain": ["fam1", "fam1", "fam1", "fam1", "fam2", "fam2"],
            "FullIdentityOfLipid": ["l1", "l2", "l1", "l2", "l1", "l2"],
            "Interaction": [1, 0, 0, 1, 0, 0],
        }
    )


def test_raw_single_cold_pool_holds_out_only_the_protein_family():
    table = _synthetic_domain_table()
    train, held = raw_single_cold_pool(table, "fam2")
    assert set(train["LTPProtein"]) == {"A", "B"}
    assert set(held["LTPProtein"]) == {"C"}
    # unlike the double axis split, every lipid stays available in training
    assert set(train["FullIdentityOfLipid"]) == {"l1", "l2"}


def test_raw_single_cold_pool_rejects_unknown_family():
    table = _synthetic_domain_table()
    with pytest.raises(ValueError):
        raw_single_cold_pool(table, "does-not-exist")


def test_load_feature_table_round_trips_arbitrary_vectors(tmp_path):
    path = tmp_path / "protein_vectors.csv"
    pd.DataFrame(
        {"protein": ["A", "B"], "dim0": [1.0, 2.0], "dim1": [3.0, 4.0]}
    ).to_csv(path, index=False)

    features = load_feature_table(path, index_name="LTPProtein")
    assert list(features.columns) == ["dim0", "dim1"]
    assert features.loc["A"].tolist() == [1.0, 3.0]
    assert features.index.name == "LTPProtein"


def test_load_feature_table_rejects_non_numeric_values(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"protein": ["A"], "dim0": ["not-a-number"]}).to_csv(path, index=False)
    with pytest.raises(ValueError):
        load_feature_table(path, index_name="LTPProtein")


def test_load_precomputed_kernel_round_trips(tmp_path):
    matrix_path = tmp_path / "kernel.npy"
    names_path = tmp_path / "names.txt"
    matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
    np.save(matrix_path, matrix)
    names_path.write_text("A\nB\n")

    loaded, index = load_precomputed_kernel(matrix_path, names_path)
    assert np.array_equal(loaded, matrix)
    assert index == {"A": 0, "B": 1}


def test_load_precomputed_kernel_rejects_shape_mismatch(tmp_path):
    matrix_path = tmp_path / "kernel.npy"
    names_path = tmp_path / "names.txt"
    np.save(matrix_path, np.eye(3))
    names_path.write_text("A\nB\n")
    with pytest.raises(ValueError):
        load_precomputed_kernel(matrix_path, names_path)


def test_build_protein_kernel_custom_features(tmp_path):
    path = tmp_path / "proteins.csv"
    pd.DataFrame(
        {"protein": ["A", "B", "C"], "dim0": [0.0, 1.0, 5.0]}
    ).to_csv(path, index=False)

    kernel, index = build_protein_kernel(
        "custom_features", ["A", "B", "C"], ["A", "B"],
        kernel_type="rbf", features_path=path,
    )
    assert kernel.shape == (3, 3)
    assert index == {"A": 0, "B": 1, "C": 2}
    assert np.allclose(np.diag(kernel), 1.0)  # RBF is unit-diagonal
    assert kernel[0, 1] > kernel[0, 2]  # A is closer to B than to C


def test_build_protein_kernel_custom_features_reports_missing_entities(tmp_path):
    path = tmp_path / "proteins.csv"
    pd.DataFrame({"protein": ["A"], "dim0": [0.0]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="B"):
        build_protein_kernel(
            "custom_features", ["A", "B"], ["A"], features_path=path,
        )


def test_build_protein_kernel_custom_kernel(tmp_path):
    matrix_path = tmp_path / "kernel.npy"
    names_path = tmp_path / "names.txt"
    np.save(matrix_path, np.array([[1.0, 0.2], [0.2, 1.0]]))
    names_path.write_text("A\nB\n")

    kernel, index = build_protein_kernel(
        "custom_kernel", ["B", "A"], ["A", "B"],
        kernel_path=matrix_path, names_path=names_path,
    )
    # entity order follows the requested `entities`, independent of the file's order
    assert index == {"B": 0, "A": 1}
    assert kernel[0, 1] == pytest.approx(0.2)


def test_build_lipid_kernel_custom_features(tmp_path):
    path = tmp_path / "lipids.csv"
    pd.DataFrame(
        {"lipid": ["l1", "l2"], "dim0": [0.0, 10.0]}
    ).to_csv(path, index=False)
    table = _synthetic_domain_table()

    kernel, index = build_lipid_kernel(
        "custom_features", table, ["l1", "l2"], ["l1", "l2"],
        kernel_type="linear", features_path=path,
    )
    assert kernel.shape == (2, 2)
    assert index == {"l1": 0, "l2": 1}


def test_build_protein_kernel_rejects_unknown_kind():
    with pytest.raises(ValueError):
        build_protein_kernel("not-a-kind", ["A"], ["A"])


def test_build_lipid_kernel_rejects_unknown_kind():
    table = _synthetic_domain_table()
    with pytest.raises(ValueError):
        build_lipid_kernel("not-a-kind", table, ["l1"], ["l1"])


def test_linear_and_cosine_kernel_are_symmetric():
    features = pd.DataFrame(
        {"dim0": [0.0, 1.0, 5.0], "dim1": [2.0, 1.0, -1.0]}, index=["A", "B", "C"]
    )
    names = ["A", "B", "C"]
    for kernel_function in (linear_kernel, cosine_kernel):
        kernel = kernel_function(features, names, names, names)
        assert np.allclose(kernel, kernel.T)


def test_cosine_kernel_self_similarity_is_one():
    features = pd.DataFrame({"dim0": [0.0, 3.0], "dim1": [2.0, -1.0]}, index=["A", "B"])
    names = ["A", "B"]
    kernel = cosine_kernel(features, names, names, names)
    assert np.allclose(np.diag(kernel), 1.0)
