#!/usr/bin/env python3
"""Does STRUCTURAL pocket comparison predict binding profile better than sequence?

files/marginals_and_cold_split.md 9 (C2) records two things that already failed to
improve on ignoring the protein: 13 aggregate pocket descriptors as a direct predictor
of binding profile (0.284, worse than the 0.259 single-protein-holdout mean baseline),
and mean-pooled ESM3 restricted to pocket residues instead of the whole chain (0.192
cosine to ground truth, worse than 0.227 for the whole chain). Both reduce a pocket to a
handful of aggregate numbers -- means, sums, one principal-axis ratio -- which is exactly
the reduction structural pocket-matching literature says throws away the signal: shared
ligand binding correlates with pocket SHAPE, not with sequence or aggregate statistics,
and pairs of near-identical sequence can still differ in what they bind through pocket
geometry alone (Ito et al. 2012; comparative review, Chikhi/Sael/Kihara BMC
Bioinformatics 2018, 10.1186/s12859-018-2109-2; DeeplyTough, Simonovsky & Meyers, JCIM
2020, 10.1021/acs.jcim.9b00554).

What this measures, without training anything. A structural comparison of pocket A
against pocket B, in the PocketMatch spirit (Yeturu & Chandra, BMC Bioinformatics 2008):
describe a pocket by the sorted list of ALL pairwise distances between its own pocket
atoms, resample that sorted list onto a common quantile grid so pockets of different
atom counts become comparable, and take the negative L2 distance between two pockets'
resampled profiles as their similarity. No structural alignment/superposition is
attempted -- the sorted-distance list is already invariant to rotation and translation
by construction, which is the property PocketMatch exploits to skip alignment
altogether. Distances are kept in Angstroms, not rescaled to a unit pocket, because
scale is part of what determines whether an acyl chain fits (this project's own
`pocket_extent` descriptor makes the same choice).

This is then run through the exact test in analysis/protein_profile_probe.py: three
nearest neighbours (now by pocket shape, not ESM3) vote on a held-out family's binding
profile by averaging, scored by cosine to the true profile. Same anchors, so a result
here is directly comparable without adjustment: leaving a whole family out and copying
the training mean scores 0.169, leaving a whole family out and copying the three
nearest ESM3 neighbours scores 0.190 and loses to the mean on four families of seven.

    python3 analysis/pocket_shape_similarity.py
    python3 analysis/pocket_shape_similarity.py --quantiles=100 --neighbours=5
"""
import argparse
import glob
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.protein_graph_builder import pocket_atom_coordinates  # noqa: E402
from read_configuration import EXCLUDED_SUBGROUPS_BY_NAME  # noqa: E402
from protein_profile_probe import class_profiles, cosine, esm3_neighbour_reference  # noqa: E402

# The seven families files/marginals_and_cold_split.md reports throughout -- ML and OSBP
# are excluded from --double_coldsplit for having too few positives for a test block
# (COLDSPLIT_MINIMUM_TEST_POSITIVES in dataloader/sampler.py), so no anchor number exists
# for them and adding them here would not be comparable to anything.
FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")


def pocket_shape_profile(coordinates, quantiles):
    """Sorted intra-pocket atom-pair distances, resampled to `quantiles` order statistics.

    Rotation/translation-invariant by construction (only distances enter), and
    comparable across pockets of different atom counts because each one is read as its
    own empirical quantile function and resampled onto the same grid -- the same
    resampling `architecture.final_layer.SlicedWassersteinPool` applies to residue
    embeddings, applied here to a pocket's internal geometry instead.
    """
    if len(coordinates) < 2:
        raise ValueError("a pocket needs at least two atoms to have an internal distance")
    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distances = np.sqrt((diff ** 2).sum(axis=-1))
    upper = distances[np.triu_indices(len(coordinates), k=1)]
    sorted_distances = np.sort(upper)
    positions = (np.arange(quantiles) + 0.5) / quantiles * len(sorted_distances)
    lower = np.clip(np.floor(positions).astype(int), 0, len(sorted_distances) - 1)
    upper_index = np.clip(lower + 1, 0, len(sorted_distances) - 1)
    weight = np.clip(positions - lower, 0.0, 1.0)
    return sorted_distances[lower] + weight * (sorted_distances[upper_index] - sorted_distances[lower])


def pocket_similarity_matrix(quantiles):
    """Negative-L2-distance similarity between every pair of the 35 proteins' pockets."""
    profiles = {}
    for path in sorted(glob.glob(os.path.join(PROJECT_ROOT, "data", "graphs", "*", "pocketness.pdb"))):
        name = os.path.basename(os.path.dirname(path))
        coordinates = pocket_atom_coordinates(path)
        profiles[name] = pocket_shape_profile(coordinates, quantiles)
    names = sorted(profiles)
    matrix = np.zeros((len(names), len(names)))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            matrix[i, j] = -float(np.linalg.norm(profiles[a] - profiles[b]))
    return pd.DataFrame(matrix, index=names, columns=names)


def neighbour_reference(train_names, held_names, profiles, similarity, neighbours):
    """Profile cosine reached by copying the `neighbours` most pocket-similar proteins.

    Mirrors protein_profile_probe.esm3_neighbour_reference exactly, substituting the
    similarity source -- structural pocket shape instead of mean-pooled ESM3 -- so the
    two numbers differ only in what they read, not in how the test is scored.
    """
    usable = [n for n in train_names if n in similarity.index]
    scores = []
    for name in held_names:
        if name not in similarity.index:
            continue
        nearest = similarity.loc[name, usable].sort_values(ascending=False).index[:neighbours]
        predicted = profiles.loc[nearest].to_numpy().mean(axis=0)
        scores.append(cosine(profiles.loc[name].to_numpy(), predicted))
    return float(np.mean(scores)) if scores else float("nan")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quantiles", type=int, default=50)
    parser.add_argument("--neighbours", type=int, default=3)
    args = parser.parse_args()

    csv = pd.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    profiles = class_profiles(csv)
    similarity = pocket_similarity_matrix(args.quantiles)

    rows = []
    for family in FAMILIES:
        held_names = [
            name for name in EXCLUDED_SUBGROUPS_BY_NAME[family] if name in profiles.index
        ]
        train_names = [name for name in profiles.index if name not in held_names]
        mean_profile = profiles.loc[train_names].to_numpy().mean(axis=0)
        constant = float(np.mean(
            [cosine(profiles.loc[n].to_numpy(), mean_profile) for n in held_names]
        ))
        esm3 = esm3_neighbour_reference(train_names, held_names, profiles)
        pocket = neighbour_reference(
            train_names, held_names, profiles, similarity, args.neighbours
        )
        rows.append({
            "family": family,
            "proteins_held_out": len(held_names),
            "mean_of_train": constant,
            "esm3_3_nearest": esm3,
            "pocket_shape_nearest": pocket,
        })

    table = pd.DataFrame(rows).set_index("family")
    pd.set_option("display.width", 200)
    print(table.round(3).to_string())
    print()
    means = table[["mean_of_train", "esm3_3_nearest", "pocket_shape_nearest"]].mean()
    print("mean over seven families:")
    print(means.round(3).to_string())
    beats_mean = (table["pocket_shape_nearest"] > table["mean_of_train"]).sum()
    beats_esm3 = (table["pocket_shape_nearest"] > table["esm3_3_nearest"]).sum()
    print(f"\npocket shape beats mean-of-train on {beats_mean}/7 families")
    print(f"pocket shape beats ESM3-3-nearest on {beats_esm3}/7 families")


if __name__ == "__main__":
    main()
