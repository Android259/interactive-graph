#!/usr/bin/env python3

# Complete every row's SMILES candidate list to the full candidate set of its lipid.
#
# What the ambiguity is:
# - A ";"-separated SMILES field is a bag of candidate structures for one measured
#   lipid species -- sn-positional and double-bond isomers a mass spectrum cannot
#   separate -- not the pieces of one molecule.
# - The same lipid is annotated at different depth in different rows. Measured on
#   Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv: 27 groups of
#   rows share candidates while listing different numbers of them, e.g.
#   Phosphatidylinositol (38:4) appears with 2 candidates in 34 rows and with 14 in
#   one other row. Downstream that makes the input depend on how thoroughly the row
#   was annotated rather than on chemistry.
#
# What this script does:
# - Groups candidates into connected components (two candidates are connected when
#   they appear in the same row), so a component is one lipid with every isomer
#   anyone listed for it.
# - Rewrites each row's field to its whole component.
#
# Safety rules:
# - The input file is never overwritten; the result goes to a new CSV.
# - Row order is preserved: original row positions are active pair IDs used by
#   Tanimoto weights and GRAB edges.
# - A component whose candidates do not all share one molecular formula is NOT a
#   single lipid. Those are left untouched and reported, rather than silently
#   merged. On the current file there are none.
# - The row's own candidates keep their original order at the front, so the FIRST
#   candidate never changes. A run with lipid_first_fragment_only (the default) is
#   therefore unaffected by this rewrite; only the multi-candidate treatments see it.
# - Added candidates are written with the spelling they already have elsewhere in
#   the file, so no new SMILES string enters the dataset and the existing embedding
#   table keeps covering every key.

import argparse
import collections
from pathlib import Path

import pandas as pd

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
SMILES_COLUMNS = ("SmileGlobal", "SmileFragment")
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
        rows.append((column, canonical_candidates))
    return rows, spelling


def candidate_components(rows):
    """Connected components of candidates that co-occur in a row.

    Union-find over the candidates rather than over the sets: two rows listing the
    same isomer are annotations of the same lipid, so their candidates belong to one
    component, and that component is exactly the completed candidate set.
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

    for _, candidates in rows:
        for candidate in candidates:
            find(candidate)
        for candidate in candidates[1:]:
            union(candidates[0], candidate)

    components = collections.defaultdict(list)
    for candidate in parent:
        components[find(candidate)].append(candidate)
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
    for position, (column, own_candidates) in enumerate(rows):
        if not own_candidates:
            continue
        root = find(own_candidates[0])
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


def report_groups(rows, components, find, mixed):
    """Print one line per lipid whose rows disagree about the candidate list."""
    sizes = collections.defaultdict(set)
    for _, candidates in rows:
        if candidates:
            sizes[find(candidates[0])].add(len(candidates))

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
    args = parser.parse_args()

    if Chem is None or rdMolDescriptors is None:
        raise SystemExit("RDKit is required: conda install -c conda-forge rdkit")
    RDLogger.DisableLog("rdApp.*")

    table = pd.read_csv(args.input)
    missing = [column for column in SMILES_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

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


if __name__ == "__main__":
    main()
