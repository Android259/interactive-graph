#!/usr/bin/env python3
"""Do the cavity's SHAPE descriptors say anything about what a protein binds?

The question the older measurement could not answer. It correlated three size-like
descriptors (pocket SASA, volume, residue count) with the mean acyl chain length of
each protein's positives, controlling for protein size, and reported that only SASA
survived -- on 32 proteins, where the 0.05 threshold sits at |r| = 0.355 and the three
candidates landed at 0.57, 0.33 and 0.32. That is a threshold being crossed or missed,
not three different findings.

Here the candidates are the shape descriptors from
analysis/pocket_shape_descriptors.py -- how far the cavity extends, how elongated it
is, how its enclosure is distributed -- which is the part an average over pocket
residues cannot express. Every correlation is reported with its confidence interval,
because on 32 points the interval is the finding and the point estimate is decoration.

The confound this has to survive: within a family, proteins have similar pockets AND
bind similar lipids, so "longer cavity, longer chain" reads equally well as "this is a
GLTP". Two designs answer it, and both are run below.

* A target family does not determine. Measured as the share of a target's variance
  lying between family means (with 9 families over 33 proteins, a target with no family
  structure at all still scores 0.25 by arithmetic): mean chain length 0.48, share of
  sphingolipids 0.83 -- both partly or wholly family in disguise -- against the number
  of distinct head-group classes a protein accepts, 0.22, i.e. nothing. A descriptor
  that predicts THAT cannot be explained by family.
* Within one family, where family is constant by construction. Only lipocalin (10
  proteins) and CRAL-TRIO (9) are large enough to try, and at those sizes nothing can
  reach significance -- what is worth reading is whether a descriptor points the same
  way in both families as it does in the pooled analysis.

Usage:
    python3 analysis/pocket_shape_vs_binding.py
"""

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.pocket_shape_descriptors import descriptors_for  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pocket_lipid_compatibility import (  # noqa: E402
    EMPTY,
    longest_acyl_chain,
)


def chain_length_per_protein():
    """Mean longest-chain length over the positives of each protein."""
    table = pd.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    positives = table[table["Interaction"] == 1]
    lengths = {}
    for protein, rows in positives.groupby("LTPProtein"):
        values = []
        for _, row in rows.iterrows():
            for column in ("SmileGlobal", "SmileFragment"):
                text = str(row[column]).strip()
                if text in EMPTY:
                    continue
                first = text.split(";")[0].strip()
                length = longest_acyl_chain(first)
                if length:
                    values.append(length)
                break
        if values:
            lengths[protein] = float(np.mean(values))
    return pd.Series(lengths, name="mean_chain_length")


def legacy_size_descriptors(protein_dir):
    """The size-like descriptors the model already has, for comparison on the same data.

    Recomputed here rather than imported so the old and the new are measured against
    the same target, on the same proteins, with the same test -- the whole point of the
    comparison. Definitions follow pocket_descriptor() in
    dataloader/protein_graph_builder.py.
    """
    from analysis.pocket_shape_descriptors import read_pocket_atoms

    nodes = pd.read_csv(protein_dir / "coarse_graph_nodes.csv")
    _, pocket_residues, _ = read_pocket_atoms(protein_dir / "pocketness.pdb")
    key = [str(int(value)) if float(value).is_integer() else str(value)
           for value in nodes["ID_resSeq"]]
    mask = np.array([residue in pocket_residues for residue in key])
    if mask.sum() == 0:
        return None
    site = nodes[mask]
    sasa = float(site["residue_sas_area"].sum())
    volume = float(site["residue_volume"].sum())
    return {
        "protein": protein_dir.name,
        "OLD_pocket_sasa": sasa,
        "OLD_pocket_volume": volume,
        "OLD_pocket_residue_count": float(mask.sum()),
        "OLD_pocket_sasa_share": sasa / max(float(nodes["residue_sas_area"].sum()), 1e-9),
        "OLD_pocket_volume_share": volume / max(float(nodes["residue_volume"].sum()), 1e-9),
    }


def head_classes_per_protein():
    """How many distinct head-group classes each protein's positives cover.

    The class is the shorthand prefix of the lipid name -- PC(34:1) is a
    phosphatidylcholine -- so this counts chemistry types, not molecules. Chosen as the
    second target because family barely determines it (0.22 against a 0.25 no-structure
    floor), unlike chain length (0.48) or the share of sphingolipids (0.83), which is
    the family itself: sphingolipid transfer proteins are a family.
    """
    table = pd.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    positives = table[table["Interaction"] == 1].copy()
    positives["head"] = (
        positives["Lipid"].astype(str).str.extract(r"^\s*([A-Za-z][A-Za-z0-9\-]*)\s*\(")[0]
    )
    positives = positives.dropna(subset=["head"])
    counts = positives.groupby("LTPProtein")["head"].nunique()
    counts.name = "head_classes"
    return counts


def protein_families():
    """Family of each protein, as the majority ProteinDomain of its rows."""
    table = pd.read_csv(interaction_csv_path(str(PROJECT_ROOT / "data") + "/"))
    families = table.groupby("LTPProtein")["ProteinDomain"].agg(
        lambda values: values.value_counts().index[0]
    )
    families.name = "family"
    return families


def partial_spearman(x, y, control):
    """Spearman correlation of x and y with `control` regressed out of both (on ranks)."""
    rx, ry, rc = (stats.rankdata(v) for v in (x, y, control))
    rc = np.column_stack([np.ones_like(rc), rc])
    resid_x = rx - rc @ np.linalg.lstsq(rc, rx, rcond=None)[0]
    resid_y = ry - rc @ np.linalg.lstsq(rc, ry, rcond=None)[0]
    r = float(np.corrcoef(resid_x, resid_y)[0, 1])
    n = len(x)
    return r, n


def interval(r, n, controls=1):
    """Fisher confidence interval and two-sided p for a (partial) correlation."""
    if abs(r) >= 1 or n - 3 - controls <= 0:
        return float("nan"), float("nan"), float("nan")
    se = 1 / math.sqrt(n - 3 - controls)
    z = 0.5 * math.log((1 + r) / (1 - r))
    lo, hi = (math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se))
    df = n - 2 - controls
    t = r * math.sqrt(df / max(1 - r * r, 1e-12))
    p = 2 * stats.t.sf(abs(t), df)
    return lo, hi, p


TARGET_COLUMNS = ("mean_chain_length", "head_classes")
SKIP_AS_CANDIDATE = TARGET_COLUMNS + ("family",)


def report_pooled(data, target_column):
    """Every descriptor against one target over all proteins, protein size controlled."""
    candidates = [c for c in data.columns if c not in SKIP_AS_CANDIDATE]
    control = data["protein_residues"].to_numpy(dtype=float)
    target_values = data[target_column].to_numpy(dtype=float)
    threshold = stats.t.ppf(0.975, len(data) - 3)
    print(f"\n=== all proteins, target: {target_column} (n = {len(data)}, "
          f"|r| for p<0.05 is "
          f"{threshold / math.sqrt(len(data) - 3 + threshold ** 2):.3f}) ===")

    results = []
    for name in candidates:
        values = data[name].to_numpy(dtype=float)
        if np.allclose(values, values[0]) or np.isnan(values).any():
            continue
        raw = stats.spearmanr(values, target_values).statistic
        partial, n = partial_spearman(values, target_values, control)
        lo, hi, p = interval(partial, n)
        results.append((name, raw, partial, lo, hi, p))
    results.sort(key=lambda row: -abs(row[2]))

    print(f"{'descriptor':<26}{'raw rho':>9}{'partial':>9}{'95% CI':>20}{'p':>9}{'BH':>7}")
    # Benjamini-Hochberg over everything tested here: with this many candidates on this
    # few proteins, the smallest p is expected to look impressive even under pure noise,
    # and the column says whether it still does after that is accounted for.
    tested = len(results)
    for rank, (name, raw, partial, lo, hi, p) in enumerate(results[:12], start=1):
        survives = "yes" if p <= 0.05 * rank / tested else "no"
        print(f"{name:<26}{raw:>9.3f}{partial:>9.3f}   [{lo:>6.3f},{hi:>6.3f}]"
              f"{p:>9.4f}{survives:>7}")
    print(f"top 12 of {tested} tested; BH at q = 0.05 over all {tested}.")
    return {name: partial for name, _, partial, _, _, _ in results}


def report_within_family(data, target_column, pooled, minimum=8):
    """The same descriptors inside single families, where family cannot explain anything.

    No control variable and no partial correlation here: family is held constant by
    construction, which is the whole point, and protein size within one family is not
    the confound it is across families.

    Nothing can be significant at these sizes -- the thresholds are printed to make that
    concrete rather than to be cleared. What carries information is agreement: a
    descriptor pointing the same way inside both families and in the pooled result is
    saying something family cannot account for.
    """
    families = data["family"]
    large = [f for f, count in families.value_counts().items() if count >= minimum]
    if not large:
        print("\nno family has enough proteins for a within-family look")
        return
    print(f"\n=== within families, target: {target_column} ===")
    header = f"{'descriptor':<26}" + "".join(
        f"{f'{family} (n={int((families == family).sum())})':>18}" for family in large
    ) + f"{'pooled':>10}"
    print(header)
    for family in large:
        n = int((families == family).sum())
        threshold = stats.t.ppf(0.975, n - 2)
        print(f"   {family}: |rho| would need {threshold / math.sqrt(n - 2 + threshold ** 2):.2f} "
              f"to be significant at n = {n}")

    candidates = [c for c in data.columns if c not in SKIP_AS_CANDIDATE]
    rows = []
    for name in candidates:
        per_family = []
        for family in large:
            subset = data[families == family]
            values = subset[name].to_numpy(dtype=float)
            target_values = subset[target_column].to_numpy(dtype=float)
            if np.allclose(values, values[0]) or np.isnan(values).any():
                per_family.append(float("nan"))
                continue
            per_family.append(float(stats.spearmanr(values, target_values).statistic))
        if any(np.isnan(per_family)):
            continue
        agreement = min(abs(v) for v in per_family) if len(set(np.sign(per_family))) == 1 else 0.0
        rows.append((name, per_family, pooled.get(name, float("nan")), agreement))
    # Strongest first among those that at least agree in sign across the families.
    rows.sort(key=lambda row: -row[3])
    for name, per_family, pooled_value, _ in rows[:10]:
        cells = "".join(f"{value:>18.3f}" for value in per_family)
        print(f"{name:<26}{cells}{pooled_value:>10.3f}")


def main():
    rows = []
    legacy_rows = []
    graphs = PROJECT_ROOT / "data" / "graphs"
    for protein_dir in sorted(graphs.iterdir()):
        if (protein_dir / "pocketness.pdb").is_file():
            row = descriptors_for(protein_dir)
            if row:
                rows.append(row)
                legacy = legacy_size_descriptors(protein_dir)
                if legacy:
                    legacy_rows.append(legacy)
    shape = pd.DataFrame(rows).set_index("protein")
    shape = shape.join(pd.DataFrame(legacy_rows).set_index("protein"))
    data = (
        shape.join(chain_length_per_protein(), how="inner")
        .join(head_classes_per_protein(), how="inner")
        .join(protein_families(), how="inner")
        .dropna(subset=list(TARGET_COLUMNS))
    )
    for target_column in TARGET_COLUMNS:
        pooled = report_pooled(data, target_column)
        report_within_family(data, target_column, pooled)


if __name__ == "__main__":
    main()
