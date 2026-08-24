#!/usr/bin/env python3

# Build the interaction table the loader reads, in four stages.
#
# Each stage answers a different question about a row, and they are ordered so that a
# stage never has to guess at something a later one settles:
#
#   [1] what the lipid IS        repair_head_group_names
#         A name whose structures cannot be that head group is rewritten to the class
#         they do belong to. First, because stage 3 spreads a wrong name across the
#         class it collides with.
#
#   [2] how it is WRITTEN        canonicalise_spellings
#         One species, one FullIdentityOfLipid. Four spelling variants -- stray
#         punctuation, spacing, the order of two alternative head groups, and the '*'
#         shorthand -- otherwise turn 285 species into 312 lipids. Before stage 4,
#         which collapses the duplicate rows this uncovers.
#
#   [3] which STRUCTURES it may be   complete_table
#         Every row of a lipid gets the whole candidate set anyone listed for it, so
#         the input stops depending on how thoroughly a row was annotated.
#
#   [4] one ROW per cell         merge_duplicate_pairs
#         A (protein, lipid) cell measured more than once becomes one row naming every
#         screen it was recovered in.
#
# Stages 1 and 2 were checked in both orders and agree, since a rename carries the
# `Lipid` short id with it. Stage 3 before stage 4 keeps a row's own candidates at the
# front of its list, so the first candidate never moves and a run with
# lipid_first_fragment_only is unaffected.
#
# What the candidate ambiguity is:
# - A ";"-separated SMILES field is a bag of candidate structures for one measured
#   lipid species -- sn-positional and double-bond isomers a mass spectrum cannot
#   separate -- not the pieces of one molecule.
# - The same lipid is annotated at different depth in different rows. Downstream that
#   makes the input depend on how thoroughly the row was annotated rather than on
#   chemistry.
#
# Safety rules:
# - The input file is never overwritten; the result goes to a new CSV.
# - Row order is preserved through stages 1-3: original row positions are active pair
#   IDs used by Tanimoto weights and GRAB edges. Stage 4 changes them, and says so.
# - A component whose candidates do not all share one molecular formula is NOT a single
#   lipid. Those are left untouched and reported, rather than silently merged. There are
#   9 on this table, every one a CxHyNO8 against a CxHyNO9 -- a sphingolipid annotated
#   both with and without an extra oxygen, which are not isomers and cannot be one
#   species. They predate the stages above (a run with --keep-head-group-names
#   --keep-spelling-variants reports the same 9) and are left for the source to settle.
# - A head group the structures contradict is only renamed when the structures name
#   their class unambiguously; otherwise it is reported and left alone.
# - Added candidates are written with the spelling they already have elsewhere in
#   the file, so no new SMILES string enters the dataset and the existing embedding
#   table keeps covering every key.

import argparse
import collections
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
DEFAULT_REPORT = Path("preprocessing/lipid_candidate_completion_report.csv")
DEFAULT_DUPLICATE_REPORT = Path("preprocessing/duplicate_pair_merge_report.csv")
SMILES_COLUMNS = ("SmileGlobal", "SmileFragment")
PAIR_COLUMNS = ("LTPProtein", "FullIdentityOfLipid")
# Columns whose values are collected from every row of a merged pair rather than taken
# from the kept one, so the provenance of a repeated measurement survives the merge.
PROVENANCE_COLUMNS = ("Screen", "ChainFragments", "Lipid")
# The column naming the measured species, as opposed to the spelling
# `FullIdentityOfLipid` gives it. See `species_key_by_spelling`.
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
    """Which column the loader reads for this row (New_dataloader picks the same one)."""
    return "SmileFragment" if str(row["SmileGlobal"]) == "0" else "SmileGlobal"


def canonical(smiles, isomeric=True):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)


def molecular_formula(smiles):
    return rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(smiles))


# How many phosphorus atoms each head group carries. Chemistry, not something the table
# can be asked, because a class can be wrong in all of its rows at once -- and one is.
# Only the classes this panel contains are listed; a class absent from the table is not
# checked rather than guessed at.
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
    """Rename a species whose structures cannot be the head group its name claims.

    The formula check inside a component asks whether its members agree with each other.
    This asks the other question -- whether they agree with the name -- and it is the one
    that catches a head group assigned wrongly. Phosphatidylglycerophosphate carries two
    phosphorus atoms; all three of its species here are annotated with one-phosphorus
    structures. No within-component check can see that: the members agree with each other
    perfectly, they simply are not the lipid the name says.

    Left as it was, the error spread. Phosphatidylglycerophosphate (32:1)'s one structure
    is also one of Phosphatidylglycerol (32:1)'s, so the two joined into a component and
    PGP came out of an earlier run of this script holding all 15 PG structures. Keying
    components by head group stops the spread; this repairs the cause, and it has to run
    first, before the structure that carries the wrong name is completed under it.

    The name gives way to the structure, and only when the structure names its own class
    unambiguously: some other species of this table must state the same composition and
    carry the same molecular formula, and its head group must be one the formula agrees
    with. That holds for PGP (32:1), whose structure is a C38O10P1 phosphatidylglycerol
    exactly like PG (32:1)'s. It does not hold for PGP (34:2) and (36:2), whose structures
    are C40O9P1 and C42O9P1 against the C40O10P1 and C42O10P1 of the phosphatidylglycerols
    of the same composition -- an oxygen short of a PG and a phosphorus short of a PGP,
    so they are neither. Those are reported and left alone: naming them would be inventing
    a measurement, and what they really are has to come from whoever assigned them.
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
        # `Lipid` travels with the name. It is what `species_key_by_spelling` groups on,
        # so leaving the old short id behind would make the renamed rows and the rows they
        # just joined disagree about which species they are -- 35 rows saying PGP(32:1)
        # against 36 saying PG(32:1), settled by a majority vote that should never have
        # been asked for.
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
    """Connected components of candidates that co-occur in a row.

    Union-find over the candidates rather than over the sets: two rows listing the
    same isomer are annotations of the same lipid, so their candidates belong to one
    component, and that component is exactly the completed candidate set.

    Keyed by (head-group class, candidate), not by the candidate alone. Sharing an
    isomer says two rows describe one lipid only when they agree about the head group,
    and one pair here does not: Phosphatidylglycerophosphate (32:1) was annotated with a
    single structure carrying one phosphorus -- a phosphatidylglycerol, since PGP has
    two -- and that structure is also one of PG (32:1)'s. Keyed by the candidate alone
    the two joined, and PGP came out of this script holding all 15 PG structures instead
    of its own one. The formula guard below cannot see it: both sides are C38O10P1, which
    is the whole reason they got confused in the first place.

    Splitting the key costs nothing where the merge was right. The other five completions
    on this table are between entries of one class -- a spelling variant, or the ';'
    ambiguity of PG against BMP, which `head_group_class` already resolves to one side --
    so they still meet in one component.
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
    """Map every `FullIdentityOfLipid` spelling to the species it names.

    `FullIdentityOfLipid` is a spelling, not an identity. The same measured species is
    written four different ways in this table, and each way became a separate lipid:

      A  a stray ': ' prefix          ': Phosphatidylcholine (32:2)'
      B  spacing around the ';'       'PC (O-36:5); LPC (36:5)' vs '...;LPC (36:5)'
      C  the two alternative head-group assignments in either order
      D  the '*' shorthand against the alternatives spelled out,
         'Sphingomyelin (d*34:1)' vs 'Sphingomyelin (d34:1);Sphingomyelin (DH34:1)'

    28 short ids carry more than one spelling this way -- 2 of type A, 2 of B, 6 of C
    and 18 of D -- so the 312 spellings the grid is built on are 285 species, and 1960
    rows describe a cell some other row already describes. The candidate sets inside
    every one of the 28 groups are identical, so nothing chemical distinguishes them.

    Type C is the one that also breaks the cold split rather than merely inflating it:
    the head-group class is read off the name, so a species written one way round
    landed in a class that left training and the other way round in a class that
    stayed. `dataloader.sampler.lipid_class_series` now resolves that independently, but
    the duplicate rows remain, and a duplicated cell is weighted twice in the loss and
    can be scored in validation and in test at once.

    The `Lipid` column already names the species -- it is what makes the four types
    recognisable at all -- but one of the 35 rows of PE(34:1) carries 'PE(32:1);
    PE(34:1)' instead, so it cannot be read row by row. Each spelling therefore takes
    the id the majority of its 35 rows agree on, and any spelling whose rows disagree
    is returned for the caller to report rather than silently repaired.
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
    """The one spelling a species keeps, chosen without reference to row order.

    The cleanest, most explicit entry wins: one that starts with the head group rather
    than with stray punctuation, then the one naming the most alternatives, then the one
    without the '*' shorthand, then sorted order. So 'Sphingomyelin (d*34:1)' gives way to
    'Sphingomyelin (d34:1);Sphingomyelin (DH34:1)', which says the same thing without a
    convention the reader has to know, and ': Phosphatidylglycerol (32:1)' gives way to
    'Phosphatidylglycerol (32:1)'.

    Sorted order alone would keep the damaged spelling of that last pair, since ':' sorts
    ahead of every letter, and `repair_head_group_names` would then rename a species onto
    a clean spelling that no longer exists in the table. Leading punctuation is therefore
    ranked before anything else.

    The choice no longer decides the head-group class -- `lipid_class_series` reads every
    name in the entry and resolves the alternatives itself -- so beyond that this only has
    to be deterministic.
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
    """Rewrite `FullIdentityOfLipid` so one species is written one way.

    The repair belongs in the column, not in the code that reads it. Every consumer of
    this table -- the class holdout, the balancer, the per-lipid baselines, the report's
    own species counts -- reads `FullIdentityOfLipid` and takes it for an identity, and
    each of them would otherwise need its own copy of the rule. Rewritten here, the four
    spelling variants stop existing and `merge_duplicate_pairs` collapses what is left
    through the key it already uses.

    `Lipid` locates the groups; it does not replace the column. It is not written out as
    the identity because one of its own cells is corrupt (see `species_key_by_spelling`)
    and because the long name is what the rest of the pipeline reads.
    """
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
    """True when the group holds two positives recovered in different screens.

    Those rows are two measurements of one cell, not one measurement written twice: a
    zero row's `Screen` is inherited from the species' positive rows and records
    nothing, so only positives carry a screen worth keeping apart. 23 cells are like
    this, every one of them an 'in cellulo' result beside an 'in vitro' one. The merge
    keeps both by writing 'in cellulo; in vitro' into the kept row, which is the form
    the table already uses for the cells it merged before; --keep-screen-duplicates
    leaves them as two rows instead.
    """
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
    """One row per (protein, lipid): merge repeated measurements of the same cell.

    A protein-lipid cell measured more than once carries one row per measurement, and
    those rows agree on the label -- what differs is the chain-level assignment and,
    through it, the order of the candidate list, plus the screen the result came from.
    Keeping them as separate rows weights those cells twice in the loss, drags twice as
    many sampled negatives in behind them, and lets the two copies land on opposite
    sides of the validation/test division, so the same cell is scored in both blocks.

    The merge keeps the first row of the cell, unions the candidate lists of all its
    rows into the column that row's own SMILES sit in (its own order stays at the
    front, so the first candidate does not move), collects the provenance columns, and
    takes the label as the maximum -- positive wins over unlabelled, which matters if
    this is ever run on a table whose repeated rows disagree.

    Row positions change, and they are the pair IDs the Tanimoto artifacts and the GRAB
    edges are indexed by, so both have to be rebuilt against the new file. The Tanimoto
    loader checks its manifest against the table and falls back rather than serving
    weights for the wrong rows, but the fallback is no substitute for a rebuild.
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
            # Two screens recovered this cell. Asked to, leave them as two rows rather
            # than as one row naming both screens.
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
            # Screen is collected from the positive rows alone. On a zero row it is
            # inherited from the species' positives and records no measurement, so
            # joining it across a merged cell invents a second screen: done blindly it
            # marked 800 cells as recovered in both, against the 50 that really were.
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

    # Stage 1 of 4 -- what the lipid IS. A structure carrying the wrong head-group name
    # pulls the class it really belongs to into its component, and stage 3 then writes
    # that whole class onto it, so this has to be settled first.
    if not args.keep_head_group_names:
        print("[1/4] head-group names")
        table, _, _ = repair_head_group_names(table)
        print()

    # Stage 2 of 4 -- how it is WRITTEN. Independent of stage 1 now that a rename carries
    # the `Lipid` short id with it (the two orders were checked and agree), and it has to
    # precede stage 4, which is what collapses the duplicate rows this uncovers.
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

    # Stage 3 of 4 -- which STRUCTURES it may be. Runs on rows whose identity is settled,
    # and before stage 4 so that a row's own candidates stay at the front of its list and
    # the first candidate never moves.
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

    # Stage 4 of 4 -- one ROW per cell.
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
                "row positions changed: rebuild the Tanimoto compact artifacts and "
                "the GRAB pair-graph edges against the new table, since both are "
                "indexed by row position"
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
