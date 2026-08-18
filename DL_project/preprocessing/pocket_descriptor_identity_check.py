#!/usr/bin/env python3
"""How much of a pocket descriptor is the protein's identity, rewritten in a few numbers.

A descriptor that is constant per protein is a fingerprint whenever it is wide enough,
and on a cold-family split a fingerprint is the exact shortcut the split exists to
withhold: the model can key on "which protein is this" instead of "what does this site
look like". Sites of related proteins genuinely do resemble each other, so correlation
with family is not by itself a defect -- the defect is a descriptor that carries
NOTHING BUT family. These three measurements separate the two cases.

1. Mantel test against the PLM embedding. Two distance matrices over the same 35
   proteins -- one from the descriptor, one from the mean ESM3 embedding, which is
   identity in its purest available form -- correlated across all pairs, with a
   permutation test because matrix entries are not independent observations. A high
   correlation says the descriptor orders proteins the way identity does, i.e. it is
   identity in disguise.

2. Variance decomposition per entry (eta^2). Of one descriptor's spread across the 35
   proteins, how much lies between family means and how much inside families. Near 1:
   the entry says which family and nothing else. Near 0: family does not determine it.
   Reported per entry, so what has to go is named rather than guessed.

3. Leave-one-protein-out nearest neighbour. For each protein, its nearest other protein
   by descriptor; how often that neighbour shares its family. Read against two anchors:
   the rate a random neighbour would give, and the same test on the ESM embedding, which
   is the ceiling of pure identity.

Usage:
    python3 preprocessing/pocket_descriptor_identity_check.py
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
from dataloader.protein_graph_builder import (  # noqa: E402
    KYTE_DOOLITTLE,
    POCKET_DESCRIPTOR_NAMES,
    pocket_descriptor,
)
from dataloader.protein_graph_tensor_cache import _pocket_tensor  # noqa: E402

# The set as it stood before the shape rewrite, kept here and nowhere else: the point of
# this script is to say whether the replacement traded one fingerprint for another, and
# that cannot be answered without both. Not imported from anywhere -- it no longer
# exists in the code that runs.
LEGACY_NAMES = (
    "log_pocket_residues", "pocket_residue_share", "log_pocket_volume",
    "pocket_volume_share", "log_pocket_sasa", "pocket_sasa_share",
    "apolar_sasa_share", "mean_hydropathy", "mean_ev14", "mean_ev28",
    "mean_ev56", "mean_buriedness", "mean_voromqa_depth", "max_voromqa_depth",
)


def legacy_descriptor(vertices, pocket):
    """The pre-rewrite 14 numbers, reproduced from dataloader/protein_graph_builder.py."""
    mask = pocket.bool().numpy()
    site = vertices[mask]
    hydropathy = numpy.asarray(KYTE_DOOLITTLE)[site["residue_type"].to_numpy(dtype=int)]
    sasa = site["residue_sas_area"].values
    pocket_sasa = float(sasa.sum())
    pocket_volume = float(site["residue_volume"].sum())
    return numpy.array([
        numpy.log1p(len(site)),
        len(site) / max(len(vertices), 1),
        numpy.log1p(pocket_volume),
        pocket_volume / max(float(vertices["residue_volume"].sum()), 1e-9),
        numpy.log1p(pocket_sasa),
        pocket_sasa / max(float(vertices["residue_sas_area"].sum()), 1e-9),
        sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9),
        hydropathy.mean(),
        site["residue_mean_ev14"].mean(),
        site["residue_mean_ev28"].mean(),
        site["residue_mean_ev56"].mean(),
        site["residue_mean_buriedness"].mean(),
        site["residue_mean_voromqa_depth"].mean(),
        site["residue_mean_voromqa_depth"].max(),
    ], dtype=float)


def protein_families():
    """Family of each protein, as the majority ProteinDomain of its interaction rows."""
    table = pandas.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    return table.groupby("LTPProtein")["ProteinDomain"].agg(
        lambda values: values.value_counts().index[0]
    )


def mean_plm_embedding(protein):
    """One vector per protein: the ESM3 rows averaged over residues.

    Averaging is what the identity reference needs to be comparable to a per-protein
    descriptor. BOS/EOS are trimmed exactly as the dataloader trims them.
    """
    matches = glob.glob(str(PROJECT_ROOT / "data" / "embedding_ESM3" / f"{protein}_*"))
    if len(matches) != 1:
        return None
    with open(matches[0], "rb") as handle:
        rows = pickle.load(handle)
    rows = torch.as_tensor(rows)[1:-1]
    return rows.mean(dim=0).numpy().astype(float)


def standardise(matrix):
    """Zero mean, unit spread per column, so no entry dominates a distance by its units."""
    centred = matrix - matrix.mean(axis=0)
    spread = centred.std(axis=0)
    spread[spread < 1e-9] = 1.0
    return centred / spread


def pair_distances(matrix):
    """Condensed vector of euclidean distances between every pair of rows."""
    difference = matrix[:, None, :] - matrix[None, :, :]
    distances = numpy.sqrt((difference ** 2).sum(axis=-1))
    upper = numpy.triu_indices(len(matrix), k=1)
    return distances[upper], distances


def mantel(first, second, permutations=999, seed=0):
    """Spearman correlation of two distance matrices, with a label-permutation p.

    Entries of a distance matrix are not independent -- one moved protein shifts a whole
    row and column -- so significance is taken by shuffling the proteins themselves and
    rebuilding the matrix, not by a formula that assumes independent pairs.
    """
    from scipy import stats

    condensed_first, _ = pair_distances(first)
    condensed_second, full_second = pair_distances(second)
    observed = stats.spearmanr(condensed_first, condensed_second).statistic
    generator = numpy.random.default_rng(seed)
    count = 0
    upper = numpy.triu_indices(len(second), k=1)
    for _ in range(permutations):
        order = generator.permutation(len(second))
        shuffled = full_second[numpy.ix_(order, order)][upper]
        if abs(stats.spearmanr(condensed_first, shuffled).statistic) >= abs(observed):
            count += 1
    return observed, (count + 1) / (permutations + 1)


def eta_squared(values, families):
    """Share of a single descriptor's variance that lies between family means."""
    grand_mean = values.mean()
    total = ((values - grand_mean) ** 2).sum()
    if total <= 0:
        return float("nan")
    between = 0.0
    for family in numpy.unique(families):
        group = values[families == family]
        between += len(group) * (group.mean() - grand_mean) ** 2
    return float(between / total)


def nearest_neighbour_family_rate(matrix, families):
    """How often a protein's nearest OTHER protein shares its family, and by chance."""
    _, distances = pair_distances(matrix)
    numpy.fill_diagonal(distances, numpy.inf)
    hits = 0
    chance = 0.0
    counts = {family: int((families == family).sum()) for family in numpy.unique(families)}
    for index, family in enumerate(families):
        nearest = int(numpy.argmin(distances[index]))
        hits += families[nearest] == family
        chance += (counts[family] - 1) / (len(families) - 1)
    return hits / len(families), chance / len(families)


def main():
    families_by_protein = protein_families()
    proteins, new_rows, legacy_rows, plm_rows = [], [], [], []
    for protein_dir in sorted((PROJECT_ROOT / "data" / "graphs").iterdir()):
        name = protein_dir.name
        if not (protein_dir / "pocketness.pdb").is_file() or name not in families_by_protein:
            continue
        embedding = mean_plm_embedding(name)
        if embedding is None:
            continue
        vertices = pandas.read_csv(protein_dir / "coarse_graph_nodes.csv")
        pocket = _pocket_tensor(protein_dir / "pocketness.pdb")
        new_rows.append(
            pocket_descriptor(
                vertices, pocket, None, pocketness_path=str(protein_dir / "pocketness.pdb")
            )[0].numpy().astype(float)
        )
        legacy_rows.append(legacy_descriptor(vertices, pocket))
        plm_rows.append(embedding)
        proteins.append(name)

    families = numpy.array([families_by_protein[name] for name in proteins])
    sets = {
        f"new ({len(POCKET_DESCRIPTOR_NAMES)})": (numpy.array(new_rows), POCKET_DESCRIPTOR_NAMES),
        f"legacy ({len(LEGACY_NAMES)})": (numpy.array(legacy_rows), LEGACY_NAMES),
    }
    plm = standardise(numpy.array(plm_rows))
    print(f"{len(proteins)} proteins, {len(numpy.unique(families))} families\n")

    print("1. Mantel against the mean ESM3 embedding (identity)")
    print(f"{'descriptor set':<16}{'rho':>8}{'p':>8}")
    for label, (matrix, _) in sets.items():
        rho, p = mantel(standardise(matrix), plm)
        print(f"{label:<16}{rho:>8.3f}{p:>8.3f}")

    print("\n3. Nearest other protein shares the family")
    print(f"{'set':<16}{'rate':>8}{'chance':>8}")
    for label, (matrix, _) in sets.items():
        rate, chance = nearest_neighbour_family_rate(standardise(matrix), families)
        print(f"{label:<16}{rate:>8.3f}{chance:>8.3f}")
    rate, chance = nearest_neighbour_family_rate(plm, families)
    print(f"{'ESM3 (ceiling)':<16}{rate:>8.3f}{chance:>8.3f}")

    # eta^2 is not zero for a number with no family structure at all: splitting n points
    # into k groups puts (k-1)/(n-1) of the variance between the groups by arithmetic
    # alone. With 9 families over 35 proteins that floor is 0.24, so an entry scoring
    # near it carries no family information whatever the bar length suggests.
    floor = (len(numpy.unique(families)) - 1) / (len(families) - 1)
    print("\n2. Share of each entry's variance lying between families (eta^2)")
    print(f"   a number with no family structure scores {floor:.2f} here, not 0")
    for label, (matrix, names) in sets.items():
        print(f"\n  {label}")
        scores = sorted(
            ((eta_squared(matrix[:, i], families), name) for i, name in enumerate(names)),
            reverse=True,
        )
        for score, name in scores:
            bar = "#" * int(round(score * 30))
            print(f"    {name:<24}{score:>6.2f}  {bar}")


if __name__ == "__main__":
    main()
