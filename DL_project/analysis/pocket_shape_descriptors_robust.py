#!/usr/bin/env python3
"""Candidate fix for three methodological gaps in pocket_shape() and their eta^2 effect.

dataloader/protein_graph_builder.py:pocket_shape() already fixed one robustness problem
(percentile span instead of raw eigenvalue for axis LENGTH) but left three more open,
all flagged in files/pocket_shape_descriptors.md and its own docstring:

1. Axis DIRECTIONS still come from the ordinary sample covariance, which the same
   docstring calls "not robust" -- but only the length got the fix, not the direction.
   One stray rim atom can still tilt v1/v2/v3 themselves.
2. Axes are ranked by eigenvalue (variance) but measured by percentile span (a
   different statistic), so nothing guarantees span[0] >= span[1] >= span[2] once you
   switch the length metric -- "elongation" can come out below 1, which contradicts
   what the name promises.
3. The point cloud is one point per ATOM, not per RESIDUE. A Trp/Phe/Tyr side chain
   contributes ~10-14 atoms, Ala/Gly 1-4 -- so the axes PCA finds are pulled toward
   wherever the pocket happens to be lined with bulky or aromatic residues, i.e. toward
   chemistry/family, not toward the cavity's actual 3D shape.

This script builds seven variants of the same three descriptors (extent, elongation,
flatness) over the same protein/family cohort files/pocket_shape_descriptors.md
section 5 used, and reports each variant's eta^2 against protein family so the
cumulative effect of each fix is visible rather than asserted. Two length metrics are
crossed with the three point-cloud/covariance fixes:

  length_metric="span" (dataloader/protein_graph_builder.py's own choice): elongation
  and flatness are ratios of the 5th-95th percentile span of the projections.
  length_metric="sqrt_eigenvalue" (analysis/pocket_shape_descriptors.py's choice, the
  wider research set, never covered by an eta^2 check before now): elongation and
  flatness are ratios of sqrt(eigenvalue) -- the axis standard deviation. extent itself
  is the percentile span of PC1 in both cases; neither script ever computes extent from
  an eigenvalue.

  v0  production, unmodified -- imported directly from dataloader.protein_graph_builder
      for byte-for-byte parity with what actually feeds the model. span metric.
  v1  v0 + fix 2 (rank axes by their own span, not by eigenvalue). span metric.
  v2  v1 + fix 1 (MinCovDet robust covariance for center and directions). span metric.
  v3  v2 + fix 3 (one point per pocket residue -- centroid of its side-chain atoms --
      instead of one point per atom). span metric.
  v4  same point cloud and covariance as v0, sqrt_eigenvalue metric instead of span --
      isolates what changing ONLY the length formula does, holding everything else
      fixed at production.
  v5  v4 + fix 1 (robust covariance). sqrt_eigenvalue metric.
  v6  v5 + fix 3 (residue cloud). sqrt_eigenvalue metric -- the sqrt_eigenvalue
      counterpart of v3.

Read-only: does not touch data/, metrics_summary.csv, or any training artifact.

Usage:
    scripts/env.sh python3 analysis/pocket_shape_descriptors_robust.py
    scripts/env.sh python3 analysis/pocket_shape_descriptors_robust.py --out pocket_shape_variants.csv
"""

import argparse
import sys
from pathlib import Path

import numpy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.protein_graph_builder import (  # noqa: E402
    POCKET_BACKBONE_ATOMS,
    pocket_atom_coordinates,
    pocket_shape,
)
from analysis.pocket_shape_vs_binding import (  # noqa: E402
    chain_length_per_protein,
    head_classes_per_protein,
    interval,
    partial_spearman,
)
from preprocessing.pocket_descriptor_identity_check import (  # noqa: E402
    eta_squared,
    mean_plm_embedding,
    protein_families,
)

DESCRIPTOR_LABELS = ("extent", "elongation", "flatness")
VARIANT_LABELS = (
    "v0 production",
    "v1 +span-sort",
    "v2 +robust cov",
    "v3 +residue cloud",
    "v4 sqrt(eigval)",
    "v5 +robust cov",
    "v6 +residue cloud",
)
VARIANT_KEYS = ("v0", "v1", "v2", "v3", "v4", "v5", "v6")


def read_pocket_atoms_with_residue(pocketness_pdb):
    """Same pocket definition as pocket_atom_coordinates, plus which residue each atom is in.

    Needed only to build the residue-centroid cloud (fix 3); the filtering logic is
    copied verbatim from pocket_atom_coordinates rather than imported, since that
    function does not expose a residue key and must not be changed here.
    """
    coordinates = []
    residue_keys = []
    with open(pocketness_pdb) as handle:
        for line in handle:
            if len(line) < 63 or not line.startswith(("ATOM", "HETATM")):
                continue
            if line[13:17].strip() in POCKET_BACKBONE_ATOMS:
                continue
            if int(line[62]) <= 0:
                continue
            residue_keys.append(line[22:28].strip())
            coordinates.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return numpy.array(coordinates, dtype=float), numpy.array(residue_keys)


def residue_centroid_cloud(coordinates, residue_keys):
    """One point per pocket residue: the centroid of its own flagged side-chain atoms."""
    if len(coordinates) == 0:
        return coordinates
    unique_keys = numpy.unique(residue_keys)
    return numpy.array([
        coordinates[residue_keys == key].mean(axis=0) for key in unique_keys
    ])


def robust_center_and_directions(coordinates, use_robust, min_robust_points):
    """Ordinary or MinCovDet mean/covariance, whichever fix 1 calls for.

    MinCovDet needs more points than features to be well-conditioned; below
    min_robust_points, or on any numerical failure (singular support, degenerate
    cloud), it falls back to the ordinary estimate rather than raising -- a pocket
    too small for a robust fit still gets a descriptor, just not a robust one.
    """
    if use_robust and len(coordinates) >= min_robust_points:
        try:
            from sklearn.covariance import MinCovDet

            fit = MinCovDet(random_state=0).fit(coordinates)
            return fit.location_, fit.covariance_, True
        except Exception:
            pass
    center = coordinates.mean(axis=0)
    return center, numpy.cov(coordinates - center, rowvar=False), False


def pocket_shape_variant(
    coordinates, *, span_sort, use_robust_cov, length_metric="span", min_robust_points=10,
):
    """extent, elongation, flatness under a chosen combination of fixes and length metric.

    length_metric="span": elongation/flatness are span[0]/span[1], span[1]/span[2] --
    dataloader/protein_graph_builder.py's own formula. span_sort applies here.
    length_metric="sqrt_eigenvalue": elongation/flatness are sqrt(eigenvalue) ratios --
    analysis/pocket_shape_descriptors.py's formula. span_sort has no counterpart here:
    the eigenvalue order already IS the length order by construction, there is nothing
    to re-rank. extent is the percentile span of PC1 either way -- neither source
    formula ever derives extent from an eigenvalue.
    """
    if len(coordinates) < 4:
        return 0.0, 0.0, 0.0, False
    center, cov, used_robust = robust_center_and_directions(
        coordinates, use_robust_cov, min_robust_points
    )
    centered = coordinates - center
    eigenvalues, eigenvectors = numpy.linalg.eigh(cov)
    order = numpy.argsort(eigenvalues)[::-1]
    eigenvalues = numpy.clip(eigenvalues[order], 1e-9, None)
    eigenvectors = eigenvectors[:, order]
    spans = numpy.array([
        numpy.percentile(projection, 95) - numpy.percentile(projection, 5)
        for projection in (centered @ eigenvectors).T
    ])
    extent = float(numpy.clip(spans[0], 1e-9, None))
    if length_metric == "sqrt_eigenvalue":
        lengths = numpy.sqrt(eigenvalues)
        return extent, float(lengths[0] / lengths[1]), float(lengths[1] / lengths[2]), used_robust
    if span_sort:
        spans = numpy.sort(spans)[::-1]
    spans = numpy.clip(spans, 1e-9, None)
    extent = float(spans[0])
    return extent, float(spans[0] / spans[1]), float(spans[1] / spans[2]), used_robust


def descriptors_for_protein(pocketness_path, min_robust_atoms, min_robust_residues):
    atom_coordinates = pocket_atom_coordinates(str(pocketness_path))
    coordinates_check, residue_keys = read_pocket_atoms_with_residue(pocketness_path)
    assert len(coordinates_check) == len(atom_coordinates), (
        "residue-aware reader disagrees with the production reader on atom count -- "
        "the pocket definitions have drifted apart"
    )

    v0 = pocket_shape(atom_coordinates) + (False,)
    v1 = pocket_shape_variant(atom_coordinates, span_sort=True, use_robust_cov=False)
    v2 = pocket_shape_variant(
        atom_coordinates, span_sort=True, use_robust_cov=True,
        min_robust_points=min_robust_atoms,
    )
    residues = residue_centroid_cloud(atom_coordinates, residue_keys)
    v3 = pocket_shape_variant(
        residues, span_sort=True, use_robust_cov=True,
        min_robust_points=min_robust_residues,
    )
    v4 = pocket_shape_variant(
        atom_coordinates, span_sort=False, use_robust_cov=False,
        length_metric="sqrt_eigenvalue",
    )
    v5 = pocket_shape_variant(
        atom_coordinates, span_sort=False, use_robust_cov=True,
        length_metric="sqrt_eigenvalue", min_robust_points=min_robust_atoms,
    )
    v6 = pocket_shape_variant(
        residues, span_sort=False, use_robust_cov=True,
        length_metric="sqrt_eigenvalue", min_robust_points=min_robust_residues,
    )
    return {
        "n_atoms": len(atom_coordinates),
        "n_residues": len(residues),
        "v0": v0, "v1": v1, "v2": v2, "v3": v3, "v4": v4, "v5": v5, "v6": v6,
    }


def report_binding(rows, families_by_protein, protein_residues, targets):
    """Each variant against the lipid targets, protein size controlled.

    eta^2 against family only says whether a number is a fold fingerprint. It cannot say
    whether the number describes the SITE in a way that has anything to do with what
    binds there -- a descriptor can be family-neutral and still be noise. That is what
    this second measurement is for, and it is the same one
    analysis/pocket_shape_vs_binding.py already applies to the production set: partial
    Spearman against the lipid target with protein size regressed out, with the
    confidence interval, because at n = 35 the interval is the finding.

    Both targets are reported. Chain length is the physically direct one (a longer
    cavity should hold a longer chain) but is itself half family (eta^2 = 0.48). Head
    classes is the one family barely determines (0.22), so a descriptor that tracks it
    cannot be explained away as fold identity.
    """
    names = [row["protein"] for row in rows]
    control = numpy.array([protein_residues[name] for name in names], dtype=float)
    families = numpy.array([families_by_protein[name] for name in names])

    for target_name, target_series in targets.items():
        available = [i for i, name in enumerate(names) if name in target_series.index]
        target_values = numpy.array(
            [target_series[names[i]] for i in available], dtype=float
        )
        print(f"\n=== partial Spearman against {target_name} "
              f"(n = {len(available)}, protein size controlled) ===")
        print(f"{'variant':<20}" + "".join(f"{name:>26}" for name in DESCRIPTOR_LABELS))
        for variant, label in zip(VARIANT_KEYS, VARIANT_LABELS):
            line = f"{label:<20}"
            for descriptor_index in range(len(DESCRIPTOR_LABELS)):
                values = numpy.array(
                    [rows[i][variant][descriptor_index] for i in available], dtype=float
                )
                partial, n = partial_spearman(
                    values, target_values, control[available]
                )
                lo, hi, p = interval(partial, n)
                line += f"{partial:>8.3f} [{lo:>6.3f},{hi:>6.3f}]"
            print(line)

        # Within the two families large enough to look at, where family is constant by
        # construction. Nothing can reach significance at n = 8-9 -- what is readable is
        # whether a variant keeps its sign there, which a pooled-only family artifact
        # would not.
        large = [f for f in numpy.unique(families)
                 if (families == f).sum() >= 8]
        if not large:
            continue
        print(f"\n  within families (sign agreement, not significance), "
              f"target: {target_name}")
        print(f"  {'variant':<18}" + "".join(
            f"{f'{family} (n={int((families == family).sum())})':>22}"
            for family in large
        ))
        for variant, label in zip(VARIANT_KEYS, VARIANT_LABELS):
            for descriptor_index, descriptor_name in enumerate(DESCRIPTOR_LABELS):
                if descriptor_name == "extent":
                    continue
                cells = ""
                for family in large:
                    subset = [i for i in available if families[i] == family]
                    values = numpy.array(
                        [rows[i][variant][descriptor_index] for i in subset], dtype=float
                    )
                    target_subset = numpy.array(
                        [target_series[names[i]] for i in subset], dtype=float
                    )
                    from scipy import stats

                    rho = float(stats.spearmanr(values, target_subset).statistic)
                    cells += f"{rho:>22.3f}"
                print(f"  {label + ' ' + descriptor_name:<18}{cells}")


def report_divergent_proteins(rows, families_by_protein, targets, count):
    """The proteins where the span metric and the sqrt(eigenvalue) metric disagree most.

    An aggregate eta^2 cannot say WHY two formulas differ; a protein where they differ by
    a factor can. Divergence is measured on the ratio itself (v0 vs v4, same cloud and
    same covariance -- only the length formula changes), so what shows up is the effect
    of the formula alone, with every other choice held fixed.
    """
    for descriptor_index, descriptor_name in enumerate(("elongation", "flatness"), start=1):
        scored = []
        for row in rows:
            span_value = row["v0"][descriptor_index]
            sqrt_value = row["v4"][descriptor_index]
            scored.append((abs(span_value - sqrt_value), row, span_value, sqrt_value))
        scored.sort(key=lambda entry: -entry[0])
        print(f"\n=== {descriptor_name}: largest span vs sqrt(eigenvalue) disagreement ===")
        print(f"{'protein':<12}{'family':<22}{'atoms':>7}{'residues':>10}"
              f"{'span (v0)':>11}{'sqrt (v4)':>11}{'robust (v2)':>13}"
              f"{'chain len':>11}{'heads':>7}")
        for _, row, span_value, sqrt_value in scored[:count]:
            name = row["protein"]
            chain = targets["mean_chain_length"].get(name, float("nan"))
            heads = targets["head_classes"].get(name, float("nan"))
            print(f"{name:<12}{str(families_by_protein[name])[:21]:<22}"
                  f"{row['n_atoms']:>7}{row['n_residues']:>10}"
                  f"{span_value:>11.3f}{sqrt_value:>11.3f}{row['v2'][descriptor_index]:>13.3f}"
                  f"{chain:>11.1f}{heads:>7.0f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphs", type=Path, default=PROJECT_ROOT / "data" / "graphs")
    parser.add_argument("--min-robust-atoms", type=int, default=10)
    parser.add_argument("--min-robust-residues", type=int, default=8)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--cases", type=int, default=8,
                        help="how many most-divergent proteins to list per ratio")
    args = parser.parse_args()

    families_by_protein = protein_families()
    proteins, rows, protein_residues = [], [], {}
    for protein_dir in sorted(Path(args.graphs).iterdir()):
        name = protein_dir.name
        pocketness_path = protein_dir / "pocketness.pdb"
        if not pocketness_path.is_file() or name not in families_by_protein:
            continue
        # Same embedding-availability filter preprocessing/pocket_descriptor_identity_check.py
        # uses, kept only so this script's cohort matches the one the documented eta^2=0.62
        # baseline (files/pocket_shape_descriptors.md section 5) was computed on -- the
        # embedding itself plays no role in what follows.
        if mean_plm_embedding(name) is None:
            continue
        row = descriptors_for_protein(
            pocketness_path, args.min_robust_atoms, args.min_robust_residues
        )
        row["protein"] = name
        rows.append(row)
        proteins.append(name)
        # Protein size is the control variable the binding test regresses out -- a bigger
        # protein has a bigger pocket, which is not a finding about lipids.
        import pandas as pd

        protein_residues[name] = len(pd.read_csv(protein_dir / "coarse_graph_nodes.csv"))

    families = numpy.array([families_by_protein[name] for name in proteins])
    floor = (len(numpy.unique(families)) - 1) / (len(families) - 1)
    print(f"{len(proteins)} proteins, {len(numpy.unique(families))} families, "
          f"eta^2 floor = {floor:.3f}\n")

    robust_used_v2 = sum(row["v2"][3] for row in rows)
    robust_used_v3 = sum(row["v3"][3] for row in rows)
    print(f"MinCovDet actually used: v2 (atom cloud) {robust_used_v2}/{len(rows)}, "
          f"v3 (residue cloud) {robust_used_v3}/{len(rows)} "
          f"(rest fell back to ordinary covariance -- too few points)\n")

    print(f"{'descriptor':<14}" + "".join(f"{label:>18}" for label in VARIANT_LABELS))
    for descriptor_index, descriptor_name in enumerate(DESCRIPTOR_LABELS):
        line = f"{descriptor_name:<14}"
        for variant in VARIANT_KEYS:
            values = numpy.array([row[variant][descriptor_index] for row in rows])
            score = eta_squared(values, families)
            line += f"{score:>18.3f}"
        print(line)

    targets = {
        "mean_chain_length": chain_length_per_protein(),
        "head_classes": head_classes_per_protein(),
    }
    report_binding(rows, families_by_protein, protein_residues, targets)
    report_divergent_proteins(rows, families_by_protein, targets, args.cases)

    if args.out:
        import pandas as pd

        flat = []
        for row in rows:
            entry = {"protein": row["protein"], "n_atoms": row["n_atoms"],
                     "n_residues": row["n_residues"]}
            for variant in VARIANT_KEYS:
                for descriptor_index, descriptor_name in enumerate(DESCRIPTOR_LABELS):
                    entry[f"{descriptor_name}_{variant}"] = row[variant][descriptor_index]
            flat.append(entry)
        pd.DataFrame(flat).to_csv(args.out, index=False)
        print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
