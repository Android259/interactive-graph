#!/usr/bin/env python3
"""Build ESM3 input structures with per-residue confidence values.

Read data/graphs/<stem>/pocketness.pdb and the matching raw structure under
data/structures/raw/. Match residues by (chain, resSeq). Replace the pocket flag
in the B-factor field with the raw CA atom's B-factor or pLDDT for that residue.
Keep the input coordinates and residue order, apart from the RBP4 trim below.
Missing residues are not inserted. Run convert_mse_to_met.py before rebuilding
protein graphs that contain MSE residues.

Write under data/esm3_input/:
    <stem>.pdb
    <stem>_node_confidence.csv: chain, resSeq, raw_value, confidence
    is_predicted_manifest.csv: stem, is_predicted

Confidence is pLDDT / 100 for AlphaFold structures and 1 - minmax(B-factor) for
experimental structures. These are source-dependent scales, not calibrated
probabilities. AlphaFold files are identified by "AF-" in the raw filename.

    python3 preprocessing/build_consistent_esm3_pdb.py
"""
from __future__ import annotations

import csv
import glob
import os
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = DATA_ROOT / "esm3_input"

# Drop RBP4's trailing orphan atom to match the loader's residue set.
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
            # Read confidence from MSE CA records too; converted graphs use MET for these residues.
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
