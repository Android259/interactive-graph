#!/usr/bin/env python3
"""Which of the 13 lipid descriptors are head-group-class FINGERPRINTS, not chemistry.

The missing half of the project's identity audit. files/descriptor_catalog.md section 2
carries an eta^2-by-family table for all 15 protein/pocket descriptors, and the
"family-neutral 7" every current geometric_edge_* baseline uses is that table's output:
keep what sits at the arithmetic floor, drop what predicts which family a protein
belongs to. Section 1 of the same file states plainly that no equivalent check was ever
run for LIPID_DESCRIPTOR_NAMES, because the axis being hidden was always the protein
family.

Under --lipid_coldsplit the hidden axis is the other one. Whole head-group classes leave
training for every protein (dataloader/sampler.py's LIPID_COLDSPLIT_SETS), so a lipid
descriptor that mostly encodes "which class is this" is the exact analogue of
pocket_sasa_share (eta^2 = 0.85) on the protein side: it looks informative in training
and has no defined value on a class the model has never seen. Selecting a lipid
descriptor set for a lipid cold split without this table is the mistake the protein-side
table exists to prevent, made once more on the other axis.

Reads only. Trains nothing, writes nothing unless --out is given.

Three axes, because they answer three different questions and can disagree:

1. head_group_class -- the fine classes (Phosphatidylcholine, Sphingomyelin, ...), one
   label per species. "Does this descriptor say which class a lipid is?" The most
   general statement, and the one directly comparable to the protein-side table's
   eta^2-by-family.

2. coldsplit_set -- the four LIPID_COLDSPLIT_SETS plus "kept" for everything held out of
   none. Coarser and closer to what the split actually does, since the split groups
   classes by chemistry rather than holding out one class at a time.

3. is_<set> -- four binary splits, one per set: this set against everything else. The
   most operational of the three, because a run holds out exactly ONE set. A descriptor
   can sit at the floor on axes 1-2 and still separate sphingolipids perfectly from the
   rest, which would matter for the sphingolipids run and for no other.

Every eta^2 is printed with its own arithmetic floor -- (k-1)/(n-1), the share a split
of k groups over n entities puts between groups by arithmetic alone, whatever the values
are (analysis/feature_identity_check.py's group_floor) -- and with a label-permutation
p-value, because a floor tells you what a meaningless number looks like but not whether
this particular one is above it by more than chance. A descriptor is called
class-neutral here only when it clears NEITHER: at or below the floor, p >= 0.05.

joint_eta2 for the whole standardised 13-vector is reported alongside, because a set of
individually-weak descriptors can still pin identity down together -- the reason
feature_identity_check.py reports a joint number at all.

Usage:
    scripts/env.sh python3 analysis/lipid_descriptor_class_identity.py
    scripts/env.sh python3 analysis/lipid_descriptor_class_identity.py --permutations 9999
    scripts/env.sh python3 analysis/lipid_descriptor_class_identity.py --out /tmp/lipid_eta2.csv
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.feature_identity_check import (  # noqa: E402
    eta_squared,
    eta_squared_joint,
    group_floor,
)
from dataloader.chemistry_prior import raw_feature_matrix  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.pair_descriptor_cache import load_pair_descriptor_cache  # noqa: E402
from dataloader.pair_descriptors import (  # noqa: E402
    CANDIDATE_LIPID_DESCRIPTOR_NAMES, LIPID_DESCRIPTOR_NAMES, _MEASURES,
)
from dataloader.pocket_lipid_compatibility import candidates_for_row  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS  # noqa: E402

# The convention files/descriptor_catalog.md section 2 already applies to the protein
# side: "at the floor" is the bar for neutrality, and a permutation p-value guards
# against reading noise above it as structure.
SIGNIFICANCE = 0.05


def candidate_matrix(csv, data_dir, names):
    """(species, matrix) for measure names that are not in LIPID_DESCRIPTOR_NAMES.

    raw_feature_matrix only resolves the catalog the MODEL can be given, and the
    candidates of section 7g are deliberately not in it yet -- measuring a descriptor
    must not require first wiring it into what the network sees. Values come from the
    shared pair-descriptor cache (every _MEASURES entry is always built), averaged over
    a species' candidate structures the same way chemistry_prior's own lipid table does,
    so the two agree on what "this species' value" means.
    """
    cache = load_pair_descriptor_cache(PROJECT_ROOT / "data", isomeric=False)
    if cache is None:
        raise SystemExit(
            "no pair-descriptor cache -- run data/build_pair_descriptor_cache.py first; "
            "computing these from scratch here would re-embed conformers per lipid"
        )
    missing = [name for name in names if name not in _MEASURES]
    if missing:
        raise SystemExit(f"not cached measures: {missing}")

    species, rows = [], []
    seen = set()
    for _, row in csv.iterrows():
        name = row["FullIdentityOfLipid"]
        if name in seen:
            continue
        seen.add(name)
        collected = {measure: [] for measure in names}
        for raw in candidates_for_row(row):
            canonical = cache["raw_to_canonical"].get(raw)
            entry = cache["values"].get(canonical) if canonical else None
            if entry is None:
                continue
            for measure in names:
                value = entry.get(measure)
                if value is not None:
                    collected[measure].append(float(value))
        # np.nan, not 0.0: a species none of whose candidates has this measure has no
        # value, and eta_squared must not read a filler zero as a real one. Only
        # tail_double_bond_position is routinely absent (fully saturated lipids).
        species.append(name)
        rows.append([
            float(np.mean(collected[m])) if collected[m] else np.nan for m in names
        ])
    return species, np.array(rows, dtype=float)


def permutation_p(values, labels, observed, permutations, rng):
    """Share of label reshuffles whose eta^2 reaches `observed`.

    The labels move and the values stay put, so the null being tested is "this
    descriptor is unrelated to which class a lipid belongs to" while every other
    property of the descriptor's own distribution -- its spread, its skew, its ties --
    is preserved exactly. Same construction as analysis/pocket_extent_lbp_lipocalin_
    check.py's, which does this for one protein-side descriptor against one binary
    split.
    """
    if not np.isfinite(observed):
        return float("nan")
    shuffled = np.array(labels, copy=True)
    hits = 0
    for _ in range(permutations):
        rng.shuffle(shuffled)
        if eta_squared(values, shuffled) >= observed:
            hits += 1
    # +1 on both sides: the observed labelling is itself one of the arrangements under
    # the null, so a p-value of exactly 0 is not attainable and should not be reported.
    return (hits + 1) / (permutations + 1)


def coldsplit_set_labels(classes):
    """Which LIPID_COLDSPLIT_SET each class belongs to, "kept" for the classes in none.

    Phosphatidyl- and lysophosphatidylethanolamine are deliberately in no set (see the
    LIPID_COLDSPLIT_SETS comment in dataloader/sampler.py), so "kept" is a real group
    with real members, not a leftover bucket to be dropped.
    """
    membership = {}
    for set_name, class_names in LIPID_COLDSPLIT_SETS.items():
        for class_name in class_names:
            membership[class_name.lower()] = set_name
    return np.array([membership.get(str(c).lower(), "kept") for c in classes])


def axis_table(matrix, column_names, labels, axis_name, permutations, seed):
    """One eta^2 row per descriptor against one identity axis, floor and p-value included."""
    rng = np.random.default_rng(seed)
    rows = []
    for index, name in enumerate(column_names):
        values = matrix[:, index]
        # A descriptor undefined for some species (tail_double_bond_position on a fully
        # saturated lipid) is measured on the species where it IS defined, with the
        # count reported, rather than imputed -- an imputed value would be a constant
        # shared by exactly the saturated lipids, which is itself a class signal.
        defined = ~np.isnan(values)
        values, group_labels = values[defined], np.asarray(labels)[defined]
        observed = eta_squared(values, group_labels)
        floor = group_floor(group_labels)
        rows.append({
            "axis": axis_name,
            "descriptor": name,
            "eta2": observed,
            "floor": floor,
            "above_floor": observed - floor,
            # What the user's question needs alongside neutrality: a descriptor with
            # eta^2 = 0.99 has essentially no variation left INSIDE a class, so it can
            # only ever act as the class label. One at 0.5 still varies within a class
            # and can carry real interaction signal there -- being head-derived is not
            # the same as being a shortcut.
            "within_class_share": 1.0 - observed,
            "p_permutation": permutation_p(values, group_labels, observed, permutations, rng),
            "groups": len(pandas.unique(group_labels)),
            "n": len(group_labels),
        })
    return pandas.DataFrame(rows)


def verdict(row):
    """class-neutral / borderline / fingerprint, on the same bar as the protein side.

    "fingerprint" needs BOTH: measurably above the arithmetic floor AND not explainable
    as a reshuffle. A descriptor above the floor with p >= 0.05 is "borderline" rather
    than neutral because at these entity counts the permutation test is the weaker of
    the two checks, and calling such a column safe is the error this whole table exists
    to avoid.
    """
    if not np.isfinite(row["eta2"]):
        return "degenerate"
    if row["above_floor"] <= 0:
        return "class-neutral"
    if row["p_permutation"] < SIGNIFICANCE:
        return "fingerprint"
    return "borderline"


def print_joint(matrix, column_names, labels):
    """Joint eta^2 over the columns that have a value for every species.

    A degenerate column (aromatic_ring_count: no variance at all) or one undefined for
    some species (tail_double_bond_position on a saturated lipid) makes the whole
    standardised sum-of-squares nan, which reads as "could not be computed" when the
    answer is "these columns cannot take part". Dropped by name, and the drop is
    reported, so a joint number is never quietly over a different set than it says.
    """
    usable = [
        i for i in range(matrix.shape[1])
        if np.isfinite(matrix[:, i]).all() and matrix[:, i].std() > 1e-12
    ]
    dropped = [column_names[i] for i in range(matrix.shape[1]) if i not in usable]
    value = eta_squared_joint(matrix[:, usable], labels) if usable else float("nan")
    note = f"  [dropped: {','.join(dropped)}]" if dropped else ""
    print(f"joint eta2 over {len(usable)} of {len(column_names)} descriptors: "
          f"{value:.4f}  (floor {group_floor(labels):.4f}){note}")


def print_table(frame, title):
    print(f"\n=== {title} ===")
    header = frame.iloc[0]
    print(f"groups: {header['groups']}   entities: {header['n']}   "
          f"arithmetic floor (k-1)/(n-1): {header['floor']:.4f}")
    print(f"{'descriptor':26s} {'eta2':>8s} {'-floor':>8s} {'within':>8s} {'p_perm':>8s} {'n':>5s}  verdict")
    for _, row in frame.sort_values("eta2", ascending=False).iterrows():
        print(f"{row['descriptor']:26s} {row['eta2']:8.4f} {row['above_floor']:8.4f} "
              f"{row['within_class_share']:8.4f} {row['p_permutation']:8.4f} "
              f"{int(row['n']):5d}  {row['verdict']}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--permutations", type=int, default=999,
        help="label reshuffles per descriptor per axis (default 999)",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", help="also write every row of every axis to this CSV")
    parser.add_argument(
        "--set", dest="descriptor_set", default="catalog",
        choices=("catalog", "candidates", "both"),
        help="catalog: LIPID_DESCRIPTOR_NAMES, what the model can be given today. "
             "candidates: the head-group-neutral candidates of section 7g, cached but "
             "not yet model-facing. both: one table over the union.",
    )
    args = parser.parse_args()

    data_dir = str(PROJECT_ROOT / "data") + "/"
    csv = pandas.read_csv(interaction_csv_path(data_dir))

    # One row per distinct lipid species, not per interaction row: an interaction table
    # weighted by how often a species was screened would make eta^2 report which classes
    # were assayed most, not which classes the descriptor can tell apart.
    catalog = list(LIPID_DESCRIPTOR_NAMES)
    candidates = list(CANDIDATE_LIPID_DESCRIPTOR_NAMES)
    if args.descriptor_set == "candidates":
        catalog = []
    elif args.descriptor_set == "catalog":
        candidates = []

    species, matrix, column_names = None, None, []
    if catalog:
        species, matrix, entity_column, column_names = raw_feature_matrix(
            csv, data_dir, catalog, zscore=False
        )
        if entity_column != "FullIdentityOfLipid":
            raise SystemExit(
                f"expected lipid granularity, got {entity_column!r} -- "
                "LIPID_DESCRIPTOR_NAMES should resolve per species"
            )
        column_names = list(column_names)
    if candidates:
        candidate_species, candidate_values = candidate_matrix(csv, data_dir, candidates)
        if species is None:
            species, matrix = candidate_species, candidate_values
        else:
            # Same species, different order: raw_feature_matrix sorts, candidate_matrix
            # keeps first-seen csv order. Reindexed by NAME rather than positionally --
            # zipping two differently ordered lists would silently pair each species'
            # catalog values with another species' tail values, which is the one error
            # here that would look like a result instead of a crash. The SET must still
            # match exactly; a difference there is a real divergence, not an ordering.
            if set(candidate_species) != set(species):
                raise SystemExit(
                    f"catalog and candidate species sets disagree: "
                    f"{len(set(species) ^ set(candidate_species))} differ"
                )
            position = {name: i for i, name in enumerate(candidate_species)}
            reordered = candidate_values[[position[name] for name in species], :]
            matrix = np.hstack([matrix, reordered])
        column_names = column_names + candidates

    species_frame = pandas.DataFrame({"FullIdentityOfLipid": species})
    classes = lipid_class_series(species_frame).to_numpy()
    sets = coldsplit_set_labels(classes)

    print(f"lipid descriptors: {len(column_names)}   species: {len(species)}")
    print(f"head-group classes: {len(pandas.unique(classes))}   "
          f"coldsplit sets: {sorted(pandas.unique(sets))}")

    tables = []
    for axis_name, labels in (("head_group_class", classes), ("coldsplit_set", sets)):
        table = axis_table(matrix, column_names, labels, axis_name,
                           args.permutations, args.seed)
        table["verdict"] = table.apply(verdict, axis=1)
        tables.append(table)
        print_table(table, f"axis: {axis_name}")
        print_joint(matrix, column_names, labels)

    # One binary split per set -- what a single --lipid_coldsplit run actually faces.
    for set_name in LIPID_COLDSPLIT_SETS:
        labels = np.where(sets == set_name, set_name, "rest")
        table = axis_table(matrix, column_names, labels, f"is_{set_name}",
                           args.permutations, args.seed)
        table["verdict"] = table.apply(verdict, axis=1)
        tables.append(table)
        print_table(table, f"axis: {set_name} vs rest")
        print_joint(matrix, column_names, labels)

    everything = pandas.concat(tables, ignore_index=True)

    # The actual deliverable: a descriptor is only proposed as class-neutral if it is
    # neutral on EVERY axis. One run holds out one set, but the same descriptor list is
    # used for all four, so a column that fingerprints any single set disqualifies
    # itself for the whole sweep.
    per_descriptor = everything.groupby("descriptor")["verdict"]
    neutral = sorted(name for name, verdicts in per_descriptor
                     if set(verdicts) <= {"class-neutral"})
    flagged = sorted(name for name, verdicts in per_descriptor
                     if "fingerprint" in set(verdicts))
    borderline = sorted(set(column_names) - set(neutral) - set(flagged))

    print("\n=== proposed split (neutral on EVERY axis above) ===")
    print(f"class-neutral ({len(neutral)}): {','.join(neutral) if neutral else '(none)'}")
    print(f"borderline    ({len(borderline)}): {','.join(borderline) if borderline else '(none)'}")
    print(f"fingerprint   ({len(flagged)}): {','.join(flagged) if flagged else '(none)'}")
    if neutral:
        keep = [column_names.index(name) for name in neutral]
        print("\njoint eta2 of the class-neutral subset alone, per axis:")
        for axis_name, labels in (("head_group_class", classes), ("coldsplit_set", sets)):
            print(f"  {axis_name:20s} {eta_squared_joint(matrix[:, keep], labels):.4f}"
                  f"  (all 13: {eta_squared_joint(matrix, labels):.4f})")

    if args.out:
        everything.to_csv(args.out, index=False)
        print(f"\nwrote {len(everything)} rows to {args.out}")


if __name__ == "__main__":
    main()
