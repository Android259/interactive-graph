#!/usr/bin/env python3
"""How much of each protein representation is the protein's fold, and how much its binding.

The companion to pocket_descriptor_identity_check.py, which asks this of hand-built
pocket descriptors and uses ESM3 only as the ceiling of pure identity. This asks it of
the LEARNED representations the model can actually be given -- ESM3, ESM-IF1,
ProteinMPNN -- because "replace the sequence embedding with a structural one" is the
obvious next idea once ESM3 is found to collapse all 35 proteins onto one point, and it
is cheap to measure before it is expensive to build.

Four measurements, all on the same 35 proteins and the same mean-pooled vectors the
model would receive:

1. Nearest-neighbour family rate. For each protein, its nearest OTHER protein by the
   representation; how often that neighbour shares its family. Read against the rate a
   random neighbour gives. High means the representation is largely a fold label -- the
   exact thing a cold-family split exists to withhold.

2. Spread. The median and minimum cosine between proteins. ESM3 sits at 0.974 with a
   floor of 0.905: every protein is nearly every other one. A representation that
   spreads them apart has solved that, which is worth knowing separately from whether
   spreading them apart helps.

3. Correlation with the binding profile. Over all pairs, does representation similarity
   track similarity of what the proteins actually bind? This is the question the model
   needs answered yes; 1 and 2 only describe the geometry.

4. Family-holdout profile prediction -- the test the model itself faces. Hold out a
   whole family, predict each held protein's 34-class binding profile as the mean of its
   three nearest TRAINING proteins, score by cosine against truth. The reference to beat
   is not zero but "ignore the protein and output the mean training profile": profiles
   are sparse (median 3 non-zero classes of 34), so their mean is a dense smear that
   overlaps everything a little and scores ~0.17 for free.

Usage:
    scripts/env.sh python3 preprocessing/protein_representation_identity_check.py
"""

import glob
import pickle
import sys
from pathlib import Path

import numpy
import pandas
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import lipid_class_series  # noqa: E402

# Each representation, its directory, its filename suffix, and whether the stored rows
# carry BOS/EOS tokens to trim. ESM3 writes them and the dataloader trims them, so the
# pooled vector here has to be built the same way or it is not what the model sees; the
# two structural encoders emit one row per residue and nothing else.
REPRESENTATIONS = {
    "ESM3": ("embedding_ESM3", "_*", True),
    "ESM-IF1": ("embedding_ESMIF1", "_ESMIF1.pkl", False),
    "ProteinMPNN": ("embedding_PROTEINMPNN", "_PROTEINMPNN.pkl", False),
}

# The seven families a block can be built for. ML and OSBP have 10 and 8 positives in
# total, too few to hold out, and are skipped by every other analysis here too.
HOLDOUT_FAMILIES = [
    "CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "lipocalin", "scp2", "START",
]


def binding_profiles(csv):
    """One row per protein: the share of each head-group class's lipids it binds."""
    frame = csv.copy()
    frame["lipid_class"] = lipid_class_series(frame)
    return frame.pivot_table(
        index="LTPProtein",
        columns="lipid_class",
        values="Interaction",
        aggfunc="mean",
        fill_value=0.0,
    )


def protein_families(csv):
    """Family of each protein, as the majority ProteinDomain of its interaction rows."""
    return csv.groupby("LTPProtein")["ProteinDomain"].agg(
        lambda values: values.value_counts().index[0]
    )


def cosine(first, second):
    left, right = numpy.linalg.norm(first), numpy.linalg.norm(second)
    if left == 0 or right == 0:
        return 0.0
    return float(first @ second / (left * right))


def mean_pooled(directory, suffix, trim, proteins):
    """One vector per protein: the stored rows averaged over residues."""
    vectors = {}
    for protein in proteins:
        matches = glob.glob(str(PROJECT_ROOT / "data" / directory / f"{protein}{suffix}"))
        if len(matches) != 1:
            continue
        with open(matches[0], "rb") as handle:
            rows = torch.as_tensor(pickle.load(handle))
        if rows.ndim == 3:
            rows = rows[0]
        vectors[protein] = rows[1:-1].mean(dim=0).float().numpy().astype(float) if trim \
            else rows.mean(dim=0).float().numpy().astype(float)
    return vectors


def nearest_neighbour_family_rate(matrix, families):
    """How often a protein's nearest OTHER protein shares its family, and by chance."""
    difference = matrix[:, None, :] - matrix[None, :, :]
    distances = numpy.sqrt((difference ** 2).sum(axis=-1))
    numpy.fill_diagonal(distances, numpy.inf)
    counts = {family: int((families == family).sum()) for family in numpy.unique(families)}
    hits = sum(
        families[int(numpy.argmin(distances[index]))] == family
        for index, family in enumerate(families)
    )
    chance = numpy.mean([(counts[family] - 1) / (len(families) - 1) for family in families])
    return hits / len(families), float(chance)


def main():
    csv = pandas.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    profiles = binding_profiles(csv)
    families_by_protein = protein_families(csv)
    proteins = list(profiles.index)
    profile_matrix = profiles.to_numpy()
    position = {name: index for index, name in enumerate(proteins)}

    non_zero = (profile_matrix > 0).sum(axis=1)
    print(f"proteins {len(proteins)}, head-group classes {profile_matrix.shape[1]}")
    print(
        f"non-zero classes per protein: median {int(numpy.median(non_zero))}, "
        f"range {non_zero.min()}-{non_zero.max()}"
    )

    # Why the "ignore the protein" reference is not 0: profiles barely overlap pairwise,
    # but their MEAN is dense and overlaps every one of them a little.
    pairs = [(i, j) for i in range(len(proteins)) for j in range(i + 1, len(proteins))]
    pairwise = numpy.array([cosine(profile_matrix[i], profile_matrix[j]) for i, j in pairs])
    to_centroid = numpy.array(
        [cosine(row, profile_matrix.mean(axis=0)) for row in profile_matrix]
    )
    print(
        f"\npairwise profile cosine over {len(pairwise)} pairs: median "
        f"{numpy.median(pairwise):.3f}, mean {pairwise.mean():.3f}, "
        f"exactly zero for {100 * (pairwise < 1e-9).mean():.0f}% of pairs"
    )
    print(
        f"cosine of a profile to the MEAN of all {len(proteins)}: median "
        f"{numpy.median(to_centroid):.3f}, mean {to_centroid.mean():.3f}"
    )

    loaded = {
        label: mean_pooled(directory, suffix, trim, proteins)
        for label, (directory, suffix, trim) in REPRESENTATIONS.items()
    }

    print("\n1-3. Geometry of each representation")
    header = f"{'representation':<14}{'dim':>6}{'NN same family':>16}{'chance':>8}"
    print(header + f"{'median cos':>12}{'min cos':>9}{'r vs profile':>14}")
    for label, vectors in loaded.items():
        usable = [name for name in proteins if name in vectors]
        matrix = numpy.stack([vectors[name] for name in usable])
        families = families_by_protein.loc[usable].to_numpy()
        rate, chance = nearest_neighbour_family_rate(matrix, families)
        usable_pairs = [
            (a, b) for index, a in enumerate(usable) for b in usable[index + 1:]
        ]
        embedding_cos = numpy.array([cosine(vectors[a], vectors[b]) for a, b in usable_pairs])
        profile_cos = numpy.array(
            [cosine(profile_matrix[position[a]], profile_matrix[position[b]])
             for a, b in usable_pairs]
        )
        correlation = numpy.corrcoef(embedding_cos, profile_cos)[0, 1]
        print(
            f"{label:<14}{matrix.shape[1]:>6}{rate:>16.3f}{chance:>8.3f}"
            f"{numpy.median(embedding_cos):>12.3f}{embedding_cos.min():>9.3f}"
            f"{correlation:>14.3f}"
        )

    print("\n4. Profile prediction with a WHOLE FAMILY held out (3 nearest training proteins)")
    rows = []
    for family in HOLDOUT_FAMILIES:
        held = [name for name in proteins if families_by_protein[name] == family]
        train = [name for name in proteins if families_by_protein[name] != family]
        train_mean = profile_matrix[[position[name] for name in train]].mean(axis=0)
        row = {
            "family": family,
            "n": len(held),
            "ignore protein": numpy.mean(
                [cosine(profile_matrix[position[name]], train_mean) for name in held]
            ),
        }
        for label, vectors in loaded.items():
            scores = []
            for name in held:
                if name not in vectors:
                    continue
                neighbours = sorted(
                    (t for t in train if t in vectors),
                    key=lambda other: -cosine(vectors[name], vectors[other]),
                )[:3]
                predicted = profile_matrix[[position[n] for n in neighbours]].mean(axis=0)
                scores.append(cosine(profile_matrix[position[name]], predicted))
            row[label] = numpy.mean(scores) if scores else float("nan")
        rows.append(row)

    table = pandas.DataFrame(rows)
    print(table.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    columns = ["ignore protein"] + list(REPRESENTATIONS)
    print("\nmean over the seven families")
    for label in columns:
        print(f"  {label:<16}{table[label].mean():.3f}")
    print(
        "\nA representation earns its place only by beating 'ignore protein'. "
        "Averaging these seven is itself a compression -- read the per-family rows too."
    )


if __name__ == "__main__":
    main()
