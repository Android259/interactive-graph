#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")


# Transformation rules:
# 1. Input CSV is not modified; a new output CSV is written.
# 2. Only SmileGlobal and SmileFragment are changed.
# 3. Chiral labels such as [C@], [C@@], [C@H], [C@@H] are not changed.
# 4. Glycerophospholipids (PC, PE, PG, PI, PS, LPC, LPE, LPG, BMP,
#    Cardiolipin/CL, PA, PGP) and fatty acyls (FA) have every C=C double
#    bond forced to cis, mono- or polyunsaturated alike.
# 5. Ceramide-backbone sphingolipids (Cer, CerP, HexCer, Hex2Cer, SHexCer,
#    SM -- the head group doesn't matter, the sphingoid backbone chemistry
#    is the same) are split by sphingoid base type:
#      - d/d* base: the sphingoid C4/C5 double bond is kept trans; every
#        other double bond (additional fatty-acid unsaturation, including
#        further bonds directly conjugated with C4/C5) is forced cis.
#      - DH or t/t* base: there is no C4/C5 unsaturation, so every double
#        bond is forced cis.
#    The C4/C5 bond is located structurally, via RDKit substructure
#    matching on the amide-N/C2/C3(OH)/C4=C5 pattern, rather than by text
#    position: a sugar-ring or fatty-acyl stereocenter appearing earlier in
#    the SMILES text can otherwise be mistaken for it.
# 6. Lipid classes are read from the "Lipid" column; combined names such as
#    "PG/BMP(36:2)" are split only on '/' outside parentheses, so a
#    chain-resolved species like "PC(16:0/18:1)" isn't misparsed into a
#    bogus extra "class".
# 7. Raw SMILES that double up the bond symbol shared between two directly
#    conjugated double bonds (e.g. "/C=C//C=C/", not valid SMILES on its
#    own) are normalized to a single symbol before any other processing.
# 8. Retinol (VA) and any other lipid class not listed above (DAG, TAG,
#    FAL, ...) are left unchanged and reported.


DEFAULT_INPUT = Path("data/Processed_Negative_Interaction_Corrected_Domains.csv")
DEFAULT_OUTPUT = Path(
    "data/Processed_Negative_Interaction_Corrected_Domains_Stereo_Fixed.csv"
)

SMILES_COLUMNS = ["SmileGlobal", "SmileFragment"]

GLYCEROPHOSPHOLIPIDS = {
    "BMP", "CL", "LPC", "LPE", "LPG", "PA", "PC", "PE", "PG", "PGP", "PI",
    "PS",
}
FATTY_ACYLS = {"FA"}
SIMPLE_CIS_LIPIDS = GLYCEROPHOSPHOLIPIDS | FATTY_ACYLS
RECOMMENDED_SPHINGOLIPIDS = {"Cer", "CerP", "Hex2Cer", "HexCer", "SHexCer", "SM"}

TRUE_TRANS = ("/C=C/", "\\C=C\\")

# The sphingoid C4/C5 double bond is the one right after the amide nitrogen's
# adjacent carbon and its own hydroxyl-bearing carbon: N-C(2)-C(3)(OH)-C4=C5.
# A d/d* base can have that bond directly conjugated with further chain
# unsaturation, and the head group (sugar ring, phosphocholine, ...) can
# contain its own hydroxyl-bearing stereocenters earlier in the SMILES text
# -- so locating "the C4/C5 bond" by text pattern alone is unreliable (a
# sugar-ring or fatty-acyl stereocenter can be mistaken for it). RDKit
# substructure matching finds it from the actual molecular graph instead.
C4_C5_SMARTS = Chem.MolFromSmarts("[NX3][CX4][CX4](O)C=C")

# RDKit assigns atom indices in the order atoms appear in the input SMILES,
# except a bare "[H]" branch (used throughout this data to spell out a
# stereocenter's fourth substituent explicitly) is folded into the parent
# atom's implicit valence and gets no index of its own. Tokenizing the same
# way lets a matched atom index be mapped back to its text position.
ATOM_TOKEN = re.compile(r"\[[^\]]*\]|Cl|Br|[BCNOPSFI]|[bcnops]")


def _atom_index_to_text_pos(smiles, atom_index):
    """Map an RDKit atom index back to where that atom starts in the SMILES text."""
    count = 0
    for match in ATOM_TOKEN.finditer(smiles):
        if match.group() == "[H]":
            continue
        if count == atom_index:
            return match.start()
        count += 1
    return None

# A "run" is one double bond, or several directly-conjugated double bonds
# (C=C-C=C, no spacer carbon) that share a bond symbol, e.g. "/C=C\" or
# "/C=C/C=C/". Each run is rewritten symbol-by-symbol from its (unchanged)
# leading anchor so every bond lands on its intended cis/trans state; a
# shared symbol can only carry one direction, so bonds inside a run cannot
# be assigned independently of each other.
RUN_PATTERN = re.compile(r"[/\\]C=C(?:[/\\]C=C)*[/\\]")
RUN_TOKEN = re.compile(r"[/\\]|C=C")

# Raw SMILES occasionally double up the bond symbol shared between two
# directly conjugated double bonds (e.g. "/C=C//C=C/"), which is not valid
# SMILES on its own. Collapsing repeats to one symbol turns it into an
# ordinary run for RUN_PATTERN to then rewrite; the collapsed value itself
# doesn't matter since every symbol in the run gets recomputed anyway.
REDUNDANT_BOND_SYMBOLS = re.compile(r"[/\\]{2,}")


def normalize_redundant_bond_symbols(smiles):
    """Collapse a doubled bond symbol (e.g. "//") down to one, so the text
    becomes valid, parseable SMILES with an ordinary single-symbol run."""
    return REDUNDANT_BOND_SYMBOLS.sub(lambda m: m.group(0)[0], smiles)


def _flip(symbol):
    """Return the opposite bond-direction symbol ("/" <-> "\\")."""
    return "\\" if symbol == "/" else "/"


def _rewrite_run(run_text, trans_bond_indices):
    """Recompute every bond symbol in a run from its unchanged leading
    anchor, so each bond (by position in trans_bond_indices) ends up trans
    or cis as intended -- only touching a symbol if it's not already right."""
    tokens = RUN_TOKEN.findall(run_text)
    symbol_positions = [i for i, tok in enumerate(tokens) if tok in ("/", "\\")]
    for bond_index in range(len(symbol_positions) - 1):
        leading_pos = symbol_positions[bond_index]
        trailing_pos = symbol_positions[bond_index + 1]
        leading = tokens[leading_pos]
        trailing = tokens[trailing_pos]
        want_trans = bond_index in trans_bond_indices
        is_trans = trailing == leading
        if is_trans != want_trans:
            tokens[trailing_pos] = leading if want_trans else _flip(leading)
    return "".join(tokens)


def fix_conjugated_runs(smiles, protected_start=None):
    """Rewrite every double-bond run in the SMILES to cis, except the one
    run starting at protected_start (if given), whose first bond is kept
    trans -- that's the sphingoid C4/C5 bond for a d/d* base."""

    def repl(match):
        trans_indices = {0} if match.start() == protected_start else set()
        return _rewrite_run(match.group(0), trans_indices)

    return RUN_PATTERN.sub(repl, smiles)


def find_c4_c5_run_start(smiles):
    """Return the text position of the run containing the sphingoid C4/C5
    bond (located structurally via C4_C5_SMARTS), or None if this fragment
    has no such bond (e.g. a fully saturated sphingoid tail)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    matches = mol.GetSubstructMatches(C4_C5_SMARTS)
    if not matches:
        return None
    c4_atom_index = matches[0][-2]
    c4_text_pos = _atom_index_to_text_pos(smiles, c4_atom_index)
    if c4_text_pos is None:
        return None
    for run_match in RUN_PATTERN.finditer(smiles):
        if run_match.start() <= c4_text_pos < run_match.end():
            return run_match.start()
    return None


def _split_on_top_level_slash(text):
    """Split on '/' only outside parentheses, e.g. "PG/BMP(36:2)" ->
    ["PG", "BMP(36:2)"], but "PC(16:0/18:1)" stays intact since its '/'
    separates sn-1/sn-2 chains inside the species, not two lipid classes."""
    parts = []
    current = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "/" and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return parts


def lipid_info(lipid):
    """Parse a "Lipid" column value into: its class names (e.g. ["PC"] or
    ["PG", "BMP"] for a combined name), whether it's a ceramide-backbone
    sphingolipid, whether it's a simple-cis class (glycerophospholipid/FA),
    and whether any of its species has a d/d* sphingoid base."""
    text = "" if pd.isna(lipid) else str(lipid)

    classes = []
    for part in _split_on_top_level_slash(text):
        name = part.strip().split("(", 1)[0].strip()
        if name:
            classes.append(name)

    species = []
    start = text.find("(")
    while start != -1:
        end = text.find(")", start + 1)
        if end == -1:
            break
        species.extend(
            part.strip()
            for part in text[start + 1 : end].replace("/", ";").split(";")
            if part.strip()
        )
        start = text.find("(", end + 1)

    is_sphingo = any(name in RECOMMENDED_SPHINGOLIPIDS for name in classes)
    is_simple_cis = bool(classes) and all(
        name in SIMPLE_CIS_LIPIDS for name in classes
    )
    has_d_base = any(
        token.lower().startswith("d") and not token.lower().startswith("dh")
        for token in species
    )
    return classes, is_sphingo, is_simple_cis, has_d_base


def fix_smiles(value, lipid):
    """Apply the stereochemistry rules to one SmileGlobal/SmileFragment
    cell, based on what kind of lipid it is (looked up from `lipid`)."""
    if pd.isna(value):
        return value
    text = str(value)
    if not text.strip() or text.strip().lower() == "nan" or text.strip() == "0":
        return value

    _, is_sphingo, is_simple_cis, has_d_base = lipid_info(lipid)

    if is_simple_cis:
        return fix_conjugated_runs(normalize_redundant_bond_symbols(text))

    if not is_sphingo:
        return value

    fixed_parts = []
    for part in text.split(";"):
        part = normalize_redundant_bond_symbols(part)
        protected_start = find_c4_c5_run_start(part) if has_d_base else None
        part = fix_conjugated_runs(part, protected_start)
        fixed_parts.append(part)
    return ";".join(fixed_parts)


def count_trans(value):
    """Count literal trans-spelled double-bond patterns, for the before/after report."""
    if pd.isna(value):
        return 0
    text = str(value)
    return sum(text.count(pattern) for pattern in TRUE_TRANS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        raise ValueError("Input and output paths must be different")

    table = pd.read_csv(args.input)
    missing = [column for column in ["Lipid", *SMILES_COLUMNS] if column not in table]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    changed = 0
    before = 0
    after = 0
    unknown = set()

    fixed = table.copy()
    for index, row in table.iterrows():
        classes, is_sphingo, is_simple_cis, _ = lipid_info(row["Lipid"])
        if not is_sphingo and not is_simple_cis:
            unknown.update(classes)

        for column in SMILES_COLUMNS:
            old = row[column]
            new = fix_smiles(old, row["Lipid"])
            before += count_trans(old)
            after += count_trans(new)
            if str(old) != str(new):
                fixed.at[index, column] = new
                changed += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fixed.to_csv(args.output, index=False)

    print(f"Wrote: {args.output}")
    print(f"Rows: {len(fixed)}")
    print(f"Changed SMILES cells: {changed}")
    print(f"Trans patterns before: {before}")
    print(f"Trans patterns after: {after}")
    if unknown:
        print("Unchanged unknown lipid classes: " + ", ".join(sorted(unknown)))


if __name__ == "__main__":
    main()
