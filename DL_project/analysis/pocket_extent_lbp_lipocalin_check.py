#!/usr/bin/env python3
"""Does pocket_extent single out LBP_BPI_CETP/lipocalin, without training anything.

Cheap first step for [[descriptors-path-fingerprint-leak]]'s next suspect
(training/read_configuration.py:431-435): on descriptors_no_extent_coarse_add_lipprop,
LBP_BPI_CETP's within-protein increment over chemistry is +0.165 and lipocalin's +0.100 --
both far above every other excluded family (files/signal_state.md) -- and pocket_extent
is the one channel among DATALOADER_TOKENS not yet isolated. If pocket_extent alone
already separates these two families from the other five, that is a plausible mechanism
for the outlier and worth a real run (--pair_descriptor_extent); if it does not, the
outlier survives without this channel and the search moves elsewhere.

Two views of the same 35 proteins:

1. Raw pocket_extent (dataloader/pocket_lipid_compatibility.py's pocket_extent_by_protein,
   the same function New_dataloader.py calls) -- eta^2 against the binary split
   {LBP_BPI_CETP, lipocalin} vs the other five families, with a label-permutation p-value.
   eta^2's floor for a 2-way split over 35 proteins is 1/34 = 0.03 (not 0), tighter than
   the 9-family floor of 0.24 pocket_shape_descriptors.md works against.

2. coarse_extent as a --double_coldsplit run actually builds it: quartile edges
   (--compat_extent_bins default 4) fit on the OTHER proteins only -- excluding whichever
   of the two families is currently held out, the same way New_dataloader.py's edges only
   ever see train proteins -- then that family's own proteins banded into those edges.
   Reports which band each suspect family lands in and how it compares to the other five.

Usage: python3 analysis/pocket_extent_lbp_lipocalin_check.py
"""

import sys
from pathlib import Path

import numpy
import pandas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pocket_lipid_compatibility import (  # noqa: E402
    coarsen_to_levels,
    pocket_extent_by_protein,
)

SUSPECT_FAMILIES = ("LBP_BPI_CETP", "lipocalin")
COMPAT_EXTENT_BINS = 4  # ModelConfig.compat_extent_bins default


def protein_families():
    table = pandas.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    return table.groupby("LTPProtein")["ProteinDomain"].agg(
        lambda values: values.value_counts().index[0]
    )


def eta_squared(values, is_suspect):
    grand_mean = values.mean()
    total = ((values - grand_mean) ** 2).sum()
    if total <= 0:
        return float("nan")
    between = 0.0
    for group in (is_suspect, ~is_suspect):
        if group.sum() == 0:
            continue
        subset = values[group]
        between += len(subset) * (subset.mean() - grand_mean) ** 2
    return float(between / total)


def permutation_p(values, is_suspect, permutations=9999, seed=0):
    observed = eta_squared(values, is_suspect)
    generator = numpy.random.default_rng(seed)
    count = 0
    n_suspect = int(is_suspect.sum())
    for _ in range(permutations):
        shuffled = numpy.zeros_like(is_suspect)
        shuffled[generator.choice(len(is_suspect), n_suspect, replace=False)] = True
        if eta_squared(values, shuffled) >= observed:
            count += 1
    return observed, (count + 1) / (permutations + 1)


def main():
    families_by_protein = protein_families()
    root_dir = str(PROJECT_ROOT / "data")
    proteins = sorted(
        name for name in families_by_protein.index
        if (PROJECT_ROOT / "data" / "graphs" / name / "pocketness.pdb").is_file()
    )
    extents_by_protein = pocket_extent_by_protein(root_dir, proteins)

    families = numpy.array([families_by_protein[name] for name in proteins])
    extent = numpy.array([extents_by_protein[name] for name in proteins], dtype=float)
    is_suspect = numpy.isin(families, SUSPECT_FAMILIES)

    print(f"{len(proteins)} proteins, {int(is_suspect.sum())} in {SUSPECT_FAMILIES}\n")

    print("1. Raw pocket_extent, eta^2 against {suspect} vs {other five}")
    floor = 1.0 / (len(proteins) - 1)
    print(f"   no-structure floor for a 2-way split over {len(proteins)} proteins: {floor:.3f}")
    observed, p = permutation_p(extent, is_suspect)
    print(f"   eta^2 = {observed:.3f}  (p = {p:.4f}, {9999} permutations)")
    print(
        f"   mean extent  suspect={extent[is_suspect].mean():.2f}  "
        f"other={extent[~is_suspect].mean():.2f}  "
        f"(range over all 35: {extent.min():.1f}-{extent.max():.1f})\n"
    )

    print("2. coarse_extent as a real double_coldsplit run would build it")
    print(f"   (--compat_extent_bins={COMPAT_EXTENT_BINS}, edges fit on the OTHER proteins)\n")
    for family in SUSPECT_FAMILIES:
        held_out = families == family
        train_extent = extent[~held_out]
        edges = numpy.quantile(train_extent, numpy.linspace(0, 1, COMPAT_EXTENT_BINS + 1))
        edges[0], edges[-1] = -numpy.inf, numpy.inf
        edges = numpy.unique(edges)
        banded = coarsen_to_levels(extent, edges)
        print(f"   held out: {family} ({int(held_out.sum())} proteins)")
        print(f"     edges (fit on the other {int((~held_out).sum())}): "
              + ", ".join(f"{e:.1f}" for e in edges[1:-1]))
        print(f"     {family} bands: "
              + ", ".join(f"{v:.1f}" for v in sorted(banded[held_out])))
        other_bands = banded[~held_out & ~numpy.isin(families, [family])]
        print(f"     other families' bands: min={other_bands.min():.1f} "
              f"median={numpy.median(other_bands):.1f} max={other_bands.max():.1f}")
        rank = (banded[held_out][:, None] > other_bands[None, :]).mean()
        print(f"     mean fraction of the other proteins a {family} protein outranks "
              f"by band: {rank:.2f} (0.5 = no separation)\n")


if __name__ == "__main__":
    main()
