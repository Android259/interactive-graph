"""Replace incorrect lipid SMILES in Processed_Negative_Interaction_Corrected_Domains.csv
using the OLD -> NEW corrections supplied in lipid_data_iso_correct_FROM_LINDA.xls.

Writes the result to a new copy of the CSV; the original input file is left untouched.

Matching key: (Lipid, chain suffix, OLD SMILES) -> NEW SMILES. Verified against the xls
file that this key is *always* unique (27 groups, 0 conflicts) -- unlike grouping by OLD
SMILES text alone, which has exactly one conflict (a PC(34:1) OLD SMILES shared by 6 rows:
5 agree on a plain cis/trans fix, STARD11 does not). The chain suffix (the part of Linda's
"Lipid Chains" column after "=>", e.g. "(18:1/16:0)", or None if absent) is the reason: the
5 agreeing rows all have chain suffix "(18:1/16:0)" (their acyl-chain composition is
experimentally resolved), STARD11's row has none (its composition is unresolved) -- so it is
legitimately choosing a different representative isomer from the same nominal lipid class,
not making a copy/paste error.

This chain suffix corresponds exactly to the CSV's own `ChainFragments` column (format
verified to match byte-for-byte, e.g. "(18:1/16:0)"; rows with ChainFragments == NaN
correspond to Linda's "Lipid Chains" rows with no "=>" suffix). Critically, this isn't a
property Linda invented per (LTP, Lipid) -- both chain-resolved and chain-unresolved
variants of the same nominal lipid (e.g. PC(34:1)) are independently present across many
different LTPs' own rows, in both the positive and negative pool (for PC(34:1) specifically:
7 rows chain-resolved to "(18:1/16:0)", 30 rows -- including but not limited to STARD11 --
unresolved). So every CSV row, whatever its LTP or Interaction label, can be matched to the
correct NEW value using only its own (Lipid, ChainFragments) pair -- no notion of "which LTP
Linda happened to review" or majority voting is needed at all.

One data-quality issue is normalized before matching: 5 GLTPD1-linked conjugated-diene
sphingolipids (SM(t*34:2), CerP(d*32:2)/(d*34:2)/(d*36:2)/(d*42:3)) are stored in the CSV
with a stray doubled slash ("/C=C//C=C/") where valid SMILES has a single slash
("/C=C/C=C/"). This is unrelated to Linda's stereo correction (which only concerns the last
bond of the diene) and is a pure syntax bug -- confirmed to occur nowhere else in the file --
so it is normalized (collapse "//" -> "/") globally before any matching happens.
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
XLS_PATH = REPO_ROOT / "lipid_data_iso_correct_FROM_LINDA.xls"
CSV_PATH = REPO_ROOT / "data" / "Processed_Negative_Interaction_Corrected_Domains.csv"
OUT_PATH = REPO_ROOT / "data" / "Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed.csv"

SMILES_COLUMNS = ["SmileGlobal", "SmileFragment"]
LIST_SEP = "; "

DOUBLE_SLASH_BUG = "//"
SINGLE_SLASH = "/"


def split_entries(value):
    return value.split(LIST_SEP)


def parse_chain_suffix(lipid_chains):
    """Extract the "(...)" part after "=>" in Linda's "Lipid Chains" column, or None."""
    if pd.isna(lipid_chains) or "=>" not in lipid_chains:
        return None
    return lipid_chains.split("=>", 1)[1].strip()


def load_corrections():
    xls = pd.read_excel(XLS_PATH)
    expected_cols = {"LTP", "Lipid", "Lipid Chains", "OLD Lipid SMILES", "NEW Lipid SMILES"}
    missing = expected_cols - set(xls.columns)
    if missing:
        raise ValueError(f"xls file missing expected columns: {missing}")

    for col in ("LTP", "Lipid", "OLD Lipid SMILES", "NEW Lipid SMILES"):
        n_null = xls[col].isnull().sum()
        if n_null:
            print(f"[warn] xls column {col!r} has {n_null} null values")

    changed = xls[xls["OLD Lipid SMILES"] != xls["NEW Lipid SMILES"]].copy()

    # (Lipid, chain_suffix) -> {old: new}
    # NOTE: chain_suffix is computed inline (not via a precomputed DataFrame column) because
    # Series.apply() silently coerces a returned Python None into float NaN when assigned back
    # to a column, and NaN != NaN breaks the dict-key matching against the CSV side below.
    corrections = {}
    conflicts = []
    for _, row in changed.iterrows():
        key = (row["Lipid"], parse_chain_suffix(row["Lipid Chains"]))
        old, new = row["OLD Lipid SMILES"], row["NEW Lipid SMILES"]
        bucket = corrections.setdefault(key, {})
        if old in bucket and bucket[old] != new:
            conflicts.append((key, old, bucket[old], new))
        bucket[old] = new

    if conflicts:
        print(f"[warn] {len(conflicts)} conflicts found even with (Lipid, chain_suffix) key:")
        for key, old, new1, new2 in conflicts:
            print(f"    {key}: {old!r} -> {new1!r} OR {new2!r}")

    return corrections, changed


def normalize_double_slash_bug(df):
    """Collapse the pre-existing "//" typo (invalid SMILES syntax) to "/", dataset-wide."""
    n_fixed = 0
    for col in SMILES_COLUMNS:
        mask = df[col].astype(str).str.contains(DOUBLE_SLASH_BUG, regex=False)
        n_fixed += int(mask.sum())
        df.loc[mask, col] = df.loc[mask, col].str.replace(
            DOUBLE_SLASH_BUG, SINGLE_SLASH, regex=False
        )
    return n_fixed


def apply_corrections(df, corrections):
    """Apply OLD->NEW fixes, matched per-row by (Lipid, ChainFragments), any Interaction."""
    n_rows_touched = 0
    n_replacements = 0
    found = set()  # (Lipid, chain_suffix, old)

    for idx, row in df.iterrows():
        chain_suffix = row["ChainFragments"] if pd.notna(row["ChainFragments"]) else None
        key = (row["Lipid"], chain_suffix)
        old_to_new = corrections.get(key)
        if not old_to_new:
            continue

        row_touched = False
        for col in SMILES_COLUMNS:
            val = df.at[idx, col]
            if not isinstance(val, str):
                continue
            entries = split_entries(val)
            replaced = False
            for i, entry in enumerate(entries):
                new = old_to_new.get(entry)
                if new is not None:
                    entries[i] = new
                    replaced = True
                    n_replacements += 1
                    found.add((*key, entry))
            if replaced:
                df.at[idx, col] = LIST_SEP.join(entries)
                row_touched = True
        if row_touched:
            n_rows_touched += 1

    unmatched = []
    for key, old_to_new in corrections.items():
        for old, new in old_to_new.items():
            if (*key, old) not in found:
                unmatched.append((*key, old, new))

    return n_rows_touched, n_replacements, unmatched


def main():
    corrections, changed = load_corrections()

    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    required_cols = {"Lipid", "ChainFragments", "Interaction", *SMILES_COLUMNS}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing expected columns: {missing}")

    n_normalized = normalize_double_slash_bug(df)
    n_rows, n_repl, unmatched = apply_corrections(df, corrections)

    n_correction_pairs = sum(len(v) for v in corrections.values())
    print(f"Normalized {n_normalized} '//' typo entries.")
    print(f"Loaded {len(changed)} corrected xls rows ({n_correction_pairs} OLD->NEW pairs, "
          f"{len(corrections)} distinct (Lipid, chain_suffix) keys).")
    print(f"Applied: {n_repl} entries replaced in {n_rows} rows (any LTP, any Interaction).")

    if unmatched:
        print(f"[warn] {len(unmatched)} corrections never matched any row:")
        for lipid, chain_suffix, old, new in unmatched:
            print(f"    {lipid} / {chain_suffix}: {old!r} -> {new!r}")

    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
