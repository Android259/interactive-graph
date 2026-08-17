#!/usr/bin/env python3
"""Build a per-protein PDB with a real per-residue confidence column, for ESM3 input.

WHAT THIS FIXES (found while auditing how ESM3 embeddings are produced for this
project -- see proposals_plm.md for the full writeup):

  1. `data/graphs/<stem>/pocketness.pdb` is NOT the original structure file. Its
     B-factor column has been overwritten by the Voronota pocket-detection step with
     a BINARY pocket-membership flag (verified: only values {0.00, 1.00} appear,
     vs 142 distinct real pLDDT values in the matching raw AlphaFold file for the
     same protein). So the real experimental B-factor / AlphaFold pLDDT is LOST in
     pocketness.pdb -- you cannot recover per-residue confidence from it directly.
  2. The real value IS still recoverable, from `data/structures/raw/<stem>*.pdb1`
     (the untouched source structure both pocketness.pdb and the FASTA files were
     derived from), by matching residues on (chain, resSeq). Verified empirically:
     100% of pocketness.pdb residues matched a raw-file residue by this key, across
     4 spot-checked proteins (1 AlphaFold model, 1 experimental structure with many
     alt-conformations, 1 with unresolved-density gaps, 1 with selenomethionine).
  3. Two OTHER divergence mechanisms between the raw structure and pocketness.pdb
     were checked and found to be NON-issues (Voronota already normalizes them):
       - alternate conformations (altLoc): raw BPI has 474 CA records for 456
         residues (18 duplicated by altLoc); pocketness.pdb has exactly 456 CA
         records, i.e. one conformer per residue already.
       - selenomethionine (MSE, a HETATM in raw PDB, chemically an ordinary Met in
         the backbone): raw GM2A/PITPNA contain MSE. CORRECTED -- this note used to
         claim Voronota had collapsed MSE into a plain residue because pocketness.pdb
         showed 0 MSE records and its residue count matched the graph. Voronota had in
         fact DELETED those residues (its "[-protein]" atom filter excludes MSE), and
         the matching count was an artifact of the symmetric end-trim the loader then
         applied. Fixed at the source: preprocessing/convert_mse_to_met.py rewrites MSE
         as MET, the graphs of these two proteins were regenerated from
         data/structures/mse_fixed/, and their node counts now equal their FASTA
         lengths (GM2A 162, PITPNA 269).
     So only the confidence column needed fixing here, not residue identity/count.
  4. Missing/unresolved residues (real gaps in electron density, e.g. CERT_6j81 has
     gaps at PDB residues 492-496 and 534-541) are NOT fixed by this script -- they
     are a genuine physical absence in the crystal, not an artifact of file
     processing. pocketness.pdb (like the raw file) simply omits them; this script
     preserves that (it does not insert placeholder residues).

WHAT THIS SCRIPT PRODUCES (new files only; nothing under data/graphs/ or
data/embedding_ESM3/ is read for writing, or modified, or deleted):

  data/esm3_input/<stem>.pdb
      pocketness.pdb's ATOM records (same coordinates, same already-normalized
      residue set) with the B-factor column replaced by the real value recovered
      from the raw structure (the CA atom's B-factor/pLDDT, applied to every atom
      of that residue -- this matches AlphaFold's own convention of repeating one
      pLDDT value across a residue's atoms; for experimental structures it is an
      approximation of true per-atom B-factors, since only CA's value is recovered).

  data/esm3_input/<stem>_node_confidence.csv
      One row per graph node, in the EXACT SAME ORDER as
      data/graphs/<stem>/coarse_graph_nodes.csv (same (chain, resSeq) source), with
      columns: chain, resSeq, raw_value, confidence.
      `confidence` is a direction-normalized, per-protein-scaled value in [0, 1]
      where HIGHER ALWAYS MEANS "more reliable / more ordered", regardless of
      source, so downstream code does not need to know is_predicted to use it:
        - AlphaFold stems:    confidence = raw pLDDT / 100        (already 0-100,
                              higher = more confident, just rescaled)
        - experimental stems: confidence = 1 - minmax(B-factor)   (B-factor is an
                              arbitrary per-structure scale where HIGHER means MORE
                              disordered, i.e. the opposite direction of pLDDT; this
                              flips and rescales it so "higher confidence" means the
                              same thing for both structure types)

  data/esm3_input/is_predicted_manifest.csv
      stem,is_predicted -- True for AlphaFold-derived raw files (filename contains
      "AF-"), False for experimental structures. Needed by the ESM3-loading script
      (preprocessing/embed_protein_esm3_v2.py) to pass `is_predicted=` correctly to
      the SDK when it re-derives coordinates/sequence from data/esm3_input/<stem>.pdb.

Run: python preprocessing/build_consistent_esm3_pdb.py
"""
from __future__ import annotations

import csv
import glob
import os
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = DATA_ROOT / "esm3_input"

# RBP4's pocketness.pdb ends with a single orphan atom: residue 175 has only its
# backbone N resolved, so Voronota emitted no node for it while still writing that one
# atom. The loader drops that last line before use; mirrored here so the written PDB and
# its confidence CSV describe exactly the residue set the rest of the pipeline sees.
DROP_LAST_LINE_STEM = "RBP4"


def find_raw_pdb(stem: str) -> str | None:
    hits = [
        h for h in glob.glob(str(DATA_ROOT / "structures" / "raw" / f"{stem}*.pdb1"))
        if os.path.basename(h)[len(stem):len(stem) + 1] in ("_", "-", ".")
    ]
    return hits[0] if hits else None


def is_predicted_from_filename(raw_path: str) -> bool:
    return "AF-" in os.path.basename(raw_path)


def ca_bfactor_map(raw_path: str) -> dict[tuple[str, str], float]:
    """(chain, resSeq) -> that residue's CA B-factor / pLDDT, from the raw structure."""
    out = {}
    with open(raw_path, errors="ignore") as handle:
        for line in handle:
            # MSE (selenomethionine) is a HETATM in the raw file but an ordinary
            # methionine in the graph (preprocessing/convert_mse_to_met.py), and its
            # CA carries a real B-factor -- take it, or those residues would be the
            # only ones left without a confidence value.
            is_mse = line.startswith("HETATM") and line[17:20] == "MSE"
            if not (line.startswith("ATOM") or is_mse):
                continue
            if line[12:16].strip() != "CA":
                continue
            chain = line[21]
            resseq = line[22:26].strip()
            out[(chain, resseq)] = float(line[60:66])
    return out


def minmax_confidence(raw_value: float, lo: float, hi: float) -> float:
    """1 - minmax(B-factor): higher output = more ordered, same direction as pLDDT/100."""
    if hi <= lo:
        return 1.0
    return 1.0 - (raw_value - lo) / (hi - lo)


def process_stem(stem: str, pocketness_path: str, raw_path: str, is_predicted: bool):
    bfac_map = ca_bfactor_map(raw_path)

    with open(pocketness_path, errors="ignore") as handle:
        lines = handle.readlines()
    if stem == DROP_LAST_LINE_STEM:
        lines = lines[:-1]

    out_lines = []
    missing = 0
    for line in lines:
        if line.startswith("ATOM"):
            chain = line[21]
            resseq = line[22:26].strip()
            value = bfac_map.get((chain, resseq))
            if value is None:
                missing += 1
            else:
                line = line[:60] + f"{value:6.2f}" + line[66:]
        out_lines.append(line)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{stem}.pdb", "w") as handle:
        handle.writelines(out_lines)

    return bfac_map, missing


def write_node_confidence(stem: str, nodes_csv: str, bfac_map, is_predicted: bool):
    rows = []
    with open(nodes_csv, newline="") as handle:
        for row in csv.DictReader(handle):
            chain = row["ID_chainID"].strip()
            resseq = str(int(row["ID_resSeq"]))
            value = bfac_map.get((chain, resseq))
            rows.append((chain, resseq, value))

    values = [v for _, _, v in rows if v is not None]
    lo, hi = (min(values), max(values)) if values else (0.0, 1.0)

    out_path = OUT_DIR / f"{stem}_node_confidence.csv"
    with open(out_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["chain", "resSeq", "raw_value", "confidence"])
        for chain, resseq, value in rows:
            if value is None:
                writer.writerow([chain, resseq, "", ""])
                continue
            confidence = value / 100.0 if is_predicted else minmax_confidence(value, lo, hi)
            writer.writerow([chain, resseq, value, f"{confidence:.4f}"])

    missing = sum(1 for _, _, v in rows if v is None)
    return len(rows), missing


def main():
    stems = sorted(
        os.path.basename(p) for p in glob.glob(str(DATA_ROOT / "graphs" / "*"))
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "pocketness.pdb"))
    )
    manifest = []
    total_missing_pdb, total_missing_nodes = 0, 0
    print(f"{'stem':>12} {'is_predicted':>13} {'pdb_missing':>12} {'node_missing':>13}")
    for stem in stems:
        raw_path = find_raw_pdb(stem)
        if raw_path is None:
            print(f"{stem:>12}: SKIP -- no matching raw structure file found")
            continue
        pocketness_path = str(DATA_ROOT / "graphs" / stem / "pocketness.pdb")
        nodes_csv = str(DATA_ROOT / "graphs" / stem / "coarse_graph_nodes.csv")
        is_predicted = is_predicted_from_filename(raw_path)

        bfac_map, pdb_missing = process_stem(stem, pocketness_path, raw_path, is_predicted)
        n_nodes, node_missing = write_node_confidence(stem, nodes_csv, bfac_map, is_predicted)
        total_missing_pdb += pdb_missing
        total_missing_nodes += node_missing
        manifest.append((stem, is_predicted))
        print(f"{stem:>12} {str(is_predicted):>13} {pdb_missing:>12} {node_missing:>13}/{n_nodes}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "is_predicted_manifest.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["stem", "is_predicted"])
        writer.writerows(manifest)

    print(f"\n{len(manifest)} proteins processed -> {OUT_DIR}")
    print(f"total unmatched (chain,resSeq) in PDB rewrite: {total_missing_pdb}")
    print(f"total unmatched (chain,resSeq) in node-confidence CSVs: {total_missing_nodes}")
    if total_missing_pdb or total_missing_nodes:
        print("WARNING: non-zero misses -- inspect before trusting the confidence values.")


if __name__ == "__main__":
    main()
