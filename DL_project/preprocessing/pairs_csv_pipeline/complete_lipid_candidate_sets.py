#!/usr/bin/env python3

# Prepare interaction rows in four stages:
# 1. Repair unambiguous head-group names.
# 2. Choose one spelling per species.
# 3. Complete candidate sets, keeping each row's candidates first.
# 4. Merge duplicate protein-lipid pairs and collect provenance.
#
# Keep conflicting molecular-formula groups unchanged and report them.
# Stages 1-3 preserve row order. Stage 4 changes pair IDs; rebuild Tanimoto artifacts.
# See AN_INSTRUCTION.md for the pipeline order and --keep-* options.
#
#     python3 preprocessing/pairs_csv_pipeline/complete_lipid_candidate_sets.py --help

import argparse
import collections
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataloader.lipid_classes import head_group_class  # noqa: E402

try:
    from rdkit import Chem, RDLogger
except ModuleNotFoundError:  # pragma: no cover - reported by main()
    Chem = None
    RDLogger = None

try:
    from rdkit.Chem import rdMolDescriptors
except ModuleNotFoundError:  # pragma: no cover - reported by main()
    rdMolDescriptors = None


DEFAULT_INPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv"
)
DEFAULT_OUTPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed"
    "_CandidatesCompleted.csv"
)
DEFAULT_REPORT = Path("data/unpreprocessed_files/lipid_candidate_completion_report.csv")
DEFAULT_DUPLICATE_REPORT = Path("data/unpreprocessed_files/duplicate_pair_merge_report.csv")
SMILES_COLUMNS = ("SmileGlobal", "SmileFragment")
PAIR_COLUMNS = ("LTPProtein", "FullIdentityOfLipid")
# Collect provenance from all merged rows.
PROVENANCE_COLUMNS = ("Screen", "ChainFragments", "Lipid")
# Use Lipid short IDs to group species spellings.
SPECIES_COLUMN = "Lipid"
EMPTY_VALUES = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def split_candidates(text):
    """The non-empty ";"-separated parts of one SMILES field, stripped."""
    parts = []
    for part in str(text).split(";"):
        part = part.strip()
        if part and part not in EMPTY_VALUES:
            parts.append(part)
    return parts


def active_column(row):
    """Which column the loader reads for this row (Dataloader picks the same one)."""
    return "SmileFragment" if str(row["SmileGlobal"]) == "0" else "SmileGlobal"


def canonical(smiles, isomeric=True):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)


def molecular_formula(smiles):
    return rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(smiles))


# Expected phosphorus counts for the supported head-group classes.
HEAD_GROUP_PHOSPHORUS = {
    "Bismonoacylglycerolphosphate": 1,
    "Cardiolipin": 2,
    "Ceramide": 0,
    "Ceramide phosphate": 1,
    "Diacylglycerol": 0,
    "Dihexosyl ceramide": 0,
    "Hexosyl ceramide": 0,
    "Lysophosphatidylcholine": 1,
    "Lysophosphatidylethanolamine": 1,
    "Lysophosphatidylglycerol": 1,
    "Phosphatidate": 1,
    "Phosphatidylcholine": 1,
    "Phosphatidylethanolamine": 1,
    "Phosphatidylglycerol": 1,
    "Phosphatidylglycerophosphate": 2,
    "Phosphatidylinositol": 1,
    "Phosphatidylserine": 1,
    "Retinol": 0,
    "Sphingomyelin": 1,
    "Sulfohexosyl ceramide": 0,
    "Triacylglycerol": 0,
}


def phosphorus_count(smiles):
    """Phosphorus atoms in one structure, read off its molecular formula."""
    match = re.search(r"P(\d*)", molecular_formula(smiles))
    if match is None:
        return 0
    return int(match.group(1)) if match.group(1) else 1


def composition_suffix(name):
    """The '(34:2)' part of an entry, or None when the name states no composition."""
    match = re.search(r"\(\d+:\d+\)", str(name))
    return match.group(0) if match else None


def structure_formulas(row):
    """The molecular formulas of one row's candidates."""
    formulas = set()
    for raw in split_candidates(row[active_column(row)]):
        molecule = Chem.MolFromSmiles(raw)
        if molecule is not None:
            formulas.add(molecular_formula(raw))
    return formulas


def repair_head_group_names(table):
    """Repair head-group names when composition and molecular formula identify one class.

    Require a matching species with a compatible head group. Report ambiguous cases
    and leave their names unchanged. Run before candidate completion.
    """
    expected_of = HEAD_GROUP_PHOSPHORUS
    by_name = {name: group for name, group in table.groupby("FullIdentityOfLipid")}
    formulas = {name: structure_formulas(group.iloc[0]) for name, group in by_name.items()}

    renames, unresolved = {}, []
    for name, group in by_name.items():
        head_group = head_group_class(name)
        expected = expected_of.get(head_group)
        if expected is None or not formulas[name]:
            continue
        seen = {phosphorus_count(raw) for raw in split_candidates(
            group.iloc[0][active_column(group.iloc[0])]
        ) if Chem.MolFromSmiles(raw) is not None}
        if not seen or seen == {expected}:
            continue

        suffix = composition_suffix(name)
        targets = set()
        for other, other_formulas in formulas.items():
            if other == name or composition_suffix(other) != suffix:
                continue
            other_head = head_group_class(other)
            if expected_of.get(other_head) is None:
                continue
            if other_formulas != formulas[name]:
                continue
            other_seen = {phosphorus_count(raw) for raw in split_candidates(
                by_name[other].iloc[0][active_column(by_name[other].iloc[0])]
            ) if Chem.MolFromSmiles(raw) is not None}
            if other_seen == {expected_of[other_head]}:
                targets.add(other_head)
        if len(targets) == 1:
            renames[name] = f"{targets.pop()} {suffix}"
        else:
            unresolved.append((name, head_group, expected, sorted(seen), sorted(targets)))

    print(f"head-group names contradicted by their structures: "
          f"{len(renames) + len(unresolved)}")
    for name, new_name in sorted(renames.items()):
        print(f"  {name!r} -> {new_name!r}  ({len(by_name[name])} rows)")
    for name, head_group, expected, seen, targets in sorted(unresolved):
        reason = "no class of this composition matches the formula" if not targets else (
            f"{len(targets)} classes match: {targets}")
        print(f"  {name!r}: {head_group} needs P{expected}, structures carry P{seen} "
              f"- NOT renamed, {reason}")

    if renames:
        table = table.copy()
        # Update the short ID with the head-group name so species grouping stays consistent.
        id_of = {
            new_name: normalise_species_id(
                by_name[new_name][SPECIES_COLUMN].mode().iloc[0]
            )
            for new_name in set(renames.values())
            if new_name in by_name
        }
        renamed_rows = table["FullIdentityOfLipid"].isin(renames)
        table.loc[renamed_rows, SPECIES_COLUMN] = (
            table.loc[renamed_rows, "FullIdentityOfLipid"]
            .map(lambda name: id_of.get(renames[name]))
            .fillna(table.loc[renamed_rows, SPECIES_COLUMN])
        )
        table["FullIdentityOfLipid"] = table["FullIdentityOfLipid"].map(
            lambda name: renames.get(name, name)
        )
    return table, renames, unresolved


def read_row_candidates(table, isomeric=True):
    """Per row: the active column, its canonical candidates, and their spellings.

    Returns (rows, spelling) where rows[i] is (column, [canonical, ...]) and spelling
    maps a canonical SMILES to the first spelling seen for it in the file.
    """
    rows = []
    spelling = {}
    for _, row in table.iterrows():
        column = active_column(row)
        canonical_candidates = []
        for raw in split_candidates(row[column]):
            key = canonical(raw, isomeric)
            if key is None:
                continue
            spelling.setdefault(key, raw)
            if key not in canonical_candidates:
                canonical_candidates.append(key)
        rows.append(
            (column, canonical_candidates, head_group_class(row["FullIdentityOfLipid"]))
        )
    return rows, spelling


def candidate_components(rows):
    """Group co-occurring candidates with union-find.

    Key candidates by (head-group class, canonical SMILES). This prevents a shared
    structure from joining entries with different head-group classes.
    """
    parent = {}

    def find(item):
        parent.setdefault(item, item)
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left, right):
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[left_root] = right_root

    for _, candidates, head_group in rows:
        keys = [(head_group, candidate) for candidate in candidates]
        for key in keys:
            find(key)
        for key in keys[1:]:
            union(keys[0], key)

    components = collections.defaultdict(list)
    for key in parent:
        components[find(key)].append(key[1])
    return {root: sorted(members) for root, members in components.items()}, find


def inconsistent_components(components):
    """Components whose members are not all the same molecule by formula."""
    mixed = {}
    for root, members in components.items():
        formulas = {molecular_formula(member) for member in members}
        if len(formulas) > 1:
            mixed[root] = sorted(formulas)
    return mixed


def completed_field(own_candidates, component, spelling):
    """The rewritten field: own candidates first, in order, then the missing ones."""
    added = [item for item in component if item not in own_candidates]
    ordered = list(own_candidates) + added
    return "; ".join(spelling.get(item, item) for item in ordered), added


def complete_table(table, isomeric=True):
    """Return (completed table, per-row change records, diagnostics)."""
    rows, spelling = read_row_candidates(table, isomeric)
    components, find = candidate_components(rows)
    mixed = inconsistent_components(components)

    completed = table.copy()
    changes = []
    for position, (column, own_candidates, head_group) in enumerate(rows):
        if not own_candidates:
            continue
        root = find((head_group, own_candidates[0]))
        if root in mixed:
            continue
        component = components[root]
        if len(component) == len(own_candidates):
            continue
        text, added = completed_field(own_candidates, component, spelling)
        completed.iloc[position, completed.columns.get_loc(column)] = text
        changes.append(
            {
                "row": int(table.index[position]),
                "column": column,
                "FullIdentityOfLipid": table.iloc[position].get(
                    "FullIdentityOfLipid", ""
                ),
                "candidates_before": len(own_candidates),
                "candidates_after": len(component),
                "added": ";".join(added),
            }
        )

    diagnostics = {
        "components": components,
        "mixed": mixed,
        "rows": rows,
        "find": find,
    }
    return completed, changes, diagnostics


def normalise_species_id(value):
    """The `Lipid` short id with its separator spacing normalised."""
    return ";".join(part.strip() for part in str(value).split(";") if part.strip())


def species_key_by_spelling(table):
    """Map each FullIdentityOfLipid spelling to its majority Lipid short ID.

    Return spellings with disagreeing short IDs for reporting.
    """
    keys = {}
    conflicts = []
    for spelling, group in table.groupby("FullIdentityOfLipid", sort=False):
        counts = collections.Counter(
            normalise_species_id(value) for value in group[SPECIES_COLUMN]
        )
        key, _ = counts.most_common(1)[0]
        keys[spelling] = key
        if len(counts) > 1:
            conflicts.append((spelling, dict(counts), key))
    return keys, conflicts


def canonical_spelling(spellings):
    """Choose a species spelling deterministically.

    Prefer no leading punctuation, more explicit alternatives and no star shorthand.
    Use sorted order to break ties.
    """
    return sorted(
        spellings,
        key=lambda name: (
            not name[:1].isalpha(),
            -name.count(";"),
            "*" in name,
            name,
        ),
    )[0]


def canonicalise_spellings(table):
    """Rewrite FullIdentityOfLipid to one spelling per species, using Lipid to locate groups."""
    keys, conflicts = species_key_by_spelling(table)
    by_species = collections.defaultdict(set)
    for spelling, key in keys.items():
        by_species[key].add(spelling)

    rewrites = {}
    records = []
    for key, spellings in by_species.items():
        if len(spellings) == 1:
            continue
        keeper = canonical_spelling(spellings)
        for spelling in spellings:
            if spelling != keeper:
                rewrites[spelling] = keeper
        records.append(
            {
                "species": key,
                "kept_spelling": keeper,
                "rewritten_spellings": " | ".join(sorted(spellings - {keeper})),
                "rows": int((table["FullIdentityOfLipid"].isin(spellings)).sum()),
            }
        )

    if rewrites:
        table = table.copy()
        table["FullIdentityOfLipid"] = (
            table["FullIdentityOfLipid"].map(lambda name: rewrites.get(name, name))
        )
    return table, records, conflicts


def screen_split_positives(table, group):
    """Return True for two positive measurements from different screens."""
    screens = set()
    for position in group:
        row = table.iloc[position]
        if int(row.get("Interaction", 0)) != 1:
            continue
        value = str(row.get("Screen", "")).strip()
        if value and value not in EMPTY_VALUES:
            screens.add(value)
    return len(screens) > 1


def merge_duplicate_pairs(table, isomeric=True, keep_screen_duplicates=False):
    """Merge repeated protein-lipid pairs, keeping the first row.

    Union candidates with that row's candidates first. Collect provenance and take the
    maximum label. Options can preserve repeated screen measurements.
    Row positions change, so rebuild pair-indexed Tanimoto artifacts afterwards.
    """
    missing = [column for column in PAIR_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    positions = collections.defaultdict(list)
    for position, key in enumerate(
        zip(*(table[column] for column in PAIR_COLUMNS))
    ):
        positions[key].append(position)

    keep = []
    records = []
    merged = table.copy()
    for key, group in positions.items():
        if len(group) > 1 and keep_screen_duplicates and screen_split_positives(
            table, group
        ):
            # Preserve separate screen measurements when requested.
            keep.extend(group)
            continue
        keep.append(group[0])
        if len(group) == 1:
            continue

        first = table.iloc[group[0]]
        column = active_column(first)
        ordered = []
        for position in group:
            row = table.iloc[position]
            for raw in split_candidates(row[active_column(row)]):
                canonical_key = canonical(raw, isomeric)
                if canonical_key is None:
                    continue
                if canonical_key not in {
                    canonical(item, isomeric) for item in ordered
                }:
                    ordered.append(raw)
        if ordered:
            merged.iloc[
                group[0], merged.columns.get_loc(column)
            ] = "; ".join(ordered)

        for provenance in PROVENANCE_COLUMNS:
            if provenance not in table.columns:
                continue
            # Only positive rows carry measured screen provenance; negative rows inherit it.
            sources = group
            if provenance == "Screen":
                positive = [
                    position
                    for position in group
                    if int(table.iloc[position].get("Interaction", 0)) == 1
                ]
                sources = positive or group[:1]
            values = []
            for position in sources:
                value = str(table.iloc[position][provenance]).strip()
                if value in EMPTY_VALUES or value in values:
                    continue
                values.append(value)
            if values:
                merged.iloc[
                    group[0], merged.columns.get_loc(provenance)
                ] = "; ".join(values)

        if "Interaction" in table.columns:
            merged.iloc[group[0], merged.columns.get_loc("Interaction")] = int(
                max(int(table.iloc[position]["Interaction"]) for position in group)
            )

        records.append(
            {
                "LTPProtein": key[0],
                "FullIdentityOfLipid": key[1],
                "rows_merged": len(group),
                "kept_row": int(table.index[group[0]]),
                "dropped_rows": ";".join(
                    str(int(table.index[position])) for position in group[1:]
                ),
                "candidates_after": len(ordered),
                "screens": str(merged.iloc[group[0]].get("Screen", "")),
            }
        )

    keep.sort()
    return merged.iloc[keep].reset_index(drop=True), records


def report_groups(rows, components, find, mixed):
    """Print one line per lipid whose rows disagree about the candidate list."""
    sizes = collections.defaultdict(set)
    for _, candidates, head_group in rows:
        if candidates:
            sizes[find((head_group, candidates[0]))].add(len(candidates))

    disagreeing = {
        root: sorted(seen) for root, seen in sizes.items() if len(seen) > 1
    }
    print(f"candidate components: {len(components)}")
    print(f"components whose rows list different candidate counts: {len(disagreeing)}")
    for root, seen in sorted(disagreeing.items(), key=lambda item: -len(components[item[0]])):
        component = components[root]
        marker = " [MIXED FORMULAS - left untouched]" if root in mixed else ""
        print(
            f"  sets {seen} -> {len(component)} candidates"
            f" ({molecular_formula(component[0])}){marker}"
        )
    if mixed:
        print(f"components with more than one molecular formula: {len(mixed)}")
        for root, formulas in mixed.items():
            print(f"  {formulas} ({len(components[root])} candidates) - not completed")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Complete each row's SMILES candidate list to the full set of isomer "
            "candidates listed for that lipid anywhere in the table."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--non-isomeric",
        action="store_true",
        help=(
            "Canonicalize without stereochemistry, matching a run without "
            "--lipid_isomers. The default matches the isomeric embedding table."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing the completed CSV.",
    )
    parser.add_argument(
        "--duplicate-report", type=Path, default=DEFAULT_DUPLICATE_REPORT
    )
    parser.add_argument(
        "--keep-duplicate-pairs",
        action="store_true",
        help=(
            "Leave repeated measurements of one protein-lipid cell as separate rows. "
            "They are merged by default: as separate rows they weight their cell "
            "twice and can be split across validation and test."
        ),
    )
    parser.add_argument(
        "--keep-head-group-names",
        action="store_true",
        help=(
            "Leave a head-group name in place even where the structures contradict it. "
            "By default such a name is rewritten to the class its structures belong to, "
            "and reported when no class matches them."
        ),
    )
    parser.add_argument(
        "--keep-spelling-variants",
        action="store_true",
        help=(
            "Leave FullIdentityOfLipid as written. By default the four spelling "
            "variants of one species are rewritten to a single entry, which is what "
            "turns them into duplicate pairs the merge can then collapse."
        ),
    )
    parser.add_argument(
        "--keep-screen-duplicates",
        action="store_true",
        help=(
            "Keep a cell recovered in both screens as two rows. By default it becomes "
            "one row whose Screen names both, the form the table already uses."
        ),
    )
    args = parser.parse_args()

    if Chem is None or rdMolDescriptors is None:
        raise SystemExit("RDKit is required: conda install -c conda-forge rdkit")
    RDLogger.DisableLog("rdApp.*")

    table = pd.read_csv(args.input)
    missing = [column for column in SMILES_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Stage 1: repair head-group names before candidate completion.
    if not args.keep_head_group_names:
        print("[1/4] head-group names")
        table, _, _ = repair_head_group_names(table)
        print()

    # Stage 2: canonicalise spellings before merging duplicate pairs.
    if not args.keep_spelling_variants:
        print("[2/4] spelling variants")
        table, spelling_records, spelling_conflicts = canonicalise_spellings(table)
        rows = sum(record["rows"] for record in spelling_records)
        print(
            f"spelling variants rewritten: {len(spelling_records)} species over "
            f"{rows} rows -> {table['FullIdentityOfLipid'].nunique()} distinct "
            "FullIdentityOfLipid"
        )
        for record in sorted(spelling_records, key=lambda item: item["species"]):
            print(f"  {record['species']}: kept {record['kept_spelling']!r}")
            print(f"      rewritten {record['rewritten_spellings']}")
        for spelling, counts, chosen in spelling_conflicts:
            print(
                f"  [{SPECIES_COLUMN} disagrees across the rows of {spelling!r}: "
                f"{counts}, took {chosen!r}]"
            )
        print()

    # Stage 3: complete candidates while keeping the row's own candidates first.
    print("[3/4] candidate completion")
    completed, changes, diagnostics = complete_table(
        table, isomeric=not args.non_isomeric
    )
    report_groups(
        diagnostics["rows"],
        diagnostics["components"],
        diagnostics["find"],
        diagnostics["mixed"],
    )
    print()
    print(f"input rows: {len(table)}")
    print(f"rows completed: {len(changes)} ({100 * len(changes) / max(len(table), 1):.1f}%)")

    # Stage 4: merge duplicate protein-lipid pairs.
    duplicate_records = []
    if not args.keep_duplicate_pairs:
        print("[4/4] duplicate cells")
        completed, duplicate_records = merge_duplicate_pairs(
            completed,
            isomeric=not args.non_isomeric,
            keep_screen_duplicates=args.keep_screen_duplicates,
        )
        dropped = len(table) - len(completed)
        print(
            f"duplicate pairs merged: {len(duplicate_records)} cells, "
            f"{dropped} rows dropped -> {len(completed)} rows"
        )
        if dropped:
            print(
                "row positions changed: rebuild the Tanimoto compact artifacts "
                "against the new table, since they are indexed by row position"
            )

    if args.dry_run:
        print("dry run: nothing written")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed.to_csv(args.output, index=False)
    print(f"completed table: {args.output}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            changes,
            columns=[
                "row",
                "column",
                "FullIdentityOfLipid",
                "candidates_before",
                "candidates_after",
                "added",
            ],
        ).to_csv(args.report, index=False)
        print(f"change report: {args.report}")
    if args.duplicate_report and duplicate_records:
        args.duplicate_report.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            duplicate_records,
            columns=[
                "LTPProtein",
                "FullIdentityOfLipid",
                "rows_merged",
                "kept_row",
                "dropped_rows",
                "candidates_after",
                "screens",
            ],
        ).to_csv(args.duplicate_report, index=False)
        print(f"duplicate merge report: {args.duplicate_report}")


if __name__ == "__main__":
    main()
