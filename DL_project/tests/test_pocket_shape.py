import numpy as np

from dataloader.protein_graph_builder import pocket_shape


def _elongated_cloud(rng):
    coords = np.zeros((50, 3))
    coords[:, 0] = rng.normal(0, 5, 50)
    coords[:, 1] = rng.normal(0, 2, 50)
    coords[:, 2] = rng.normal(0, 1, 50)
    return coords


def test_pocket_shape_returns_zeros_below_four_atoms():
    assert pocket_shape(np.zeros((3, 3))) == (0.0, 0.0, 0.0)


def test_extent_and_elongation_agree_on_axis_zero_and_one():
    rng = np.random.default_rng(0)
    coords = _elongated_cloud(rng)
    extent, elongation, flatness = pocket_shape(coords)
    assert extent > 0
    assert elongation > 1  # axis 0 (x, std 5) is longer than axis 1 (y, std 2)
    assert flatness > 1  # axis 1 (y, std 2) is longer than axis 2 (z, std 1)


def test_elongation_and_flatness_are_outlier_robust_like_extent():
    # Regression test: an earlier version measured extent (axis 0's own percentile
    # span) robustly but took elongation/flatness straight from the covariance
    # matrix's eigenvalues, which are NOT robust -- one atom far from the centroid
    # could inflate the variance along its own direction. Percentile-trimming every
    # axis (not just axis 0) closes that gap; this pins the old failure mode so it
    # cannot silently come back.
    rng = np.random.default_rng(0)
    coords = _elongated_cloud(rng)
    base = np.array(pocket_shape(coords))

    outlier_coords = np.vstack([coords, [[100.0, 0.0, 0.0]]])
    with_outlier = np.array(pocket_shape(outlier_coords))

    relative_change = np.abs(with_outlier - base) / base
    # extent (axis 0's own span) necessarily moves some -- the outlier IS on axis 0.
    # elongation/flatness must stay close to their pre-outlier values: an eigenvalue-
    # ratio implementation moved elongation by >200% on this exact input (verified
    # directly), a single far-off atom should not be able to do that here.
    assert relative_change[1] < 0.25  # elongation
    assert relative_change[2] < 0.25  # flatness
