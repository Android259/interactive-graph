#!/usr/bin/env python3
"""Which protein descriptor, if any, singles out LBP_BPI_CETP the way pocket_extent
singles out lipocalin -- without training anything.

Why this exists
---------------
On --double_coldsplit, LBP_BPI_CETP is the one family where the descriptor baseline
clears its null model by a wide margin (test BA 0.677 on
dh_family_neutral_lipprop, 0.796-0.826 on the earlier descriptors_path
line), and files/results/signal_state.md section 8 calls that an unexplained leak rather than
chemistry: pocket shares (raw/split/coarse) and pocket_extent have each been ruled out
as its channel. analysis/probes/pocket_extent_lbp_lipocalin_check.py did exactly one descriptor,
pocket_extent, and found the separation statistic at 0.48 for LBP_BPI_CETP (0.5 = no
separation) against 0.05 for lipocalin.

This is that same check generalised to EVERY protein-side descriptor the table holds, so
the search does not proceed one suspect per session. lipocalin rides along as a positive
control: a statistic that cannot reproduce its known pocket_extent separation is not
measuring what it claims to.

Two statistics per descriptor, both over the same 35 proteins:

  outrank  the mean fraction of the OTHER families' proteins that a suspect-family
           protein exceeds on this descriptor. 0.5 = no separation, 0.0/1.0 = the
           suspect family sits entirely below/above everyone else. This is the
           Mann-Whitney statistic, and it is the one to read: it says whether a
           family is identifiable from the descriptor, which is what a leak needs.
  eta^2    variance of the descriptor explained by the binary {suspect} vs {rest}
           split, with a label-permutation p-value. Its floor for a 2-way split over
           35 proteins is 1/34 = 0.029, not 0.

A descriptor with outrank near 0 or 1 is a candidate channel: the head can recover
"this is LBP_BPI_CETP" from it, and under --double_coldsplit that family's rows are
exactly the held-out ones.

Reads only: data/protein_descriptor_table.json (written by its own first caller, present
here) and the interaction CSV. Writes nothing, runs no model.

Usage: python3 analysis/probes/lbp_family_descriptor_separation.py
       python3 analysis/probes/lbp_family_descriptor_separation.py --family scp2
"""

import argparse
import sys
from pathlib import Path

import numpy
import pandas

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.chemistry_prior import protein_descriptor_table  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402

# The protein-side half of dh_family_neutral_lipprop's --descriptor_names
# (the other four -- chain/unsaturation/hbond/heavy -- are lipid-only tokens and carry no
# per-protein value to separate anything with).
LABEL_PROTEIN_DESCRIPTORS = (
    "pocket_volume_per_sasa", "pocket_elongation", "pocket_flatness", "buriedness_q50",
    "apolar_sasa_share", "aromatic_share", "hydropathy_rim",
)
PERMUTATIONS = 9999


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


def permutation_p(values, is_suspect, seed=0):
    observed = eta_squared(values, is_suspect)
    if not numpy.isfinite(observed):
        return observed, float("nan")
    generator = numpy.random.default_rng(seed)
    count = 0
    n_suspect = int(is_suspect.sum())
    for _ in range(PERMUTATIONS):
        shuffled = numpy.zeros_like(is_suspect)
        shuffled[generator.choice(len(is_suspect), n_suspect, replace=False)] = True
        if eta_squared(values, shuffled) >= observed:
            count += 1
    return observed, (count + 1) / (PERMUTATIONS + 1)


def outrank(values, is_suspect):
    """Mean fraction of the other proteins a suspect protein exceeds; ties count half."""
    suspect, other = values[is_suspect], values[~is_suspect]
    if len(suspect) == 0 or len(other) == 0:
        return float("nan")
    greater = (suspect[:, None] > other[None, :]).astype(float)
    tied = (suspect[:, None] == other[None, :]).astype(float)
    return float((greater + 0.5 * tied).mean())


def report(family, values_by_name, families, proteins):
    is_suspect = families == family
    print(f"===== {family}: {int(is_suspect.sum())} of {len(proteins)} proteins "
          f"({', '.join(numpy.array(proteins)[is_suspect])}) =====")
    print(f"eta^2 floor for a 2-way split over {len(proteins)} proteins: "
          f"{1.0 / (len(proteins) - 1):.3f}\n")
    rows = []
    for name, values in values_by_name.items():
        separation = outrank(values, is_suspect)
        observed, p = permutation_p(values, is_suspect)
        rows.append((abs(separation - 0.5), name, separation, observed, p))
    rows.sort(reverse=True)
    print(f"{'descriptor':34s} {'outrank':>8s} {'eta^2':>7s} {'p':>7s}  in label")
    for _, name, separation, observed, p in rows:
        flag = "yes" if name in LABEL_PROTEIN_DESCRIPTORS else ""
        print(f"{name:34s} {separation:8.2f} {observed:7.3f} {p:7.4f}  {flag}")
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family", action="append", default=None,
        help="family to test (repeatable); default LBP_BPI_CETP plus lipocalin as control",
    )
    arguments = parser.parse_args()
    suspects = arguments.family or ["LBP_BPI_CETP", "lipocalin"]

    families_by_protein = protein_families()
    table = protein_descriptor_table(str(PROJECT_ROOT / "data") + "/")
    proteins = sorted(name for name in families_by_protein.index if name in table)
    families = numpy.array([families_by_protein[name] for name in proteins])

    names = sorted({name for protein in proteins for name in table[protein]})
    values_by_name = {}
    for name in names:
        values = numpy.array(
            [float(table[protein].get(name, numpy.nan)) for protein in proteins]
        )
        if not numpy.isfinite(values).all() or values.std() == 0.0:
            continue
        values_by_name[name] = values
    print(f"{len(values_by_name)} usable protein descriptors over {len(proteins)} proteins "
          f"({len(names) - len(values_by_name)} skipped as constant or incomplete)\n")

    for family in suspects:
        if family not in set(families):
            raise SystemExit(f"unknown family {family}; known: {sorted(set(families))}")
        report(family, values_by_name, families, proteins)


if __name__ == "__main__":
    main()
