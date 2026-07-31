#!/usr/bin/env python3
"""Check whether Voronota's residue_sas_area agrees with Shrake-Rupley (freesasa) SASA.

Two independent per-residue solvent-accessible-surface-area numbers exist for every
protein: Voronota's tangent-sphere `residue_sas_area` (coarse_graph_nodes.csv, already
feeding the GNN branch) and the classic Shrake-Rupley rolling-probe value freesasa
computes from the same structure file (pocketness.pdb). They use different geometric
definitions, so this reports correlation and scale, not identity -- see the printed
verdict for what "agrees" means here.

Run: python analysis/check_sasa_correspondence.py
"""
from __future__ import annotations

import glob
import os
from pathlib import Path

import freesasa
import numpy as np
import pandas as pd
from scipy import stats

freesasa.setVerbosity(freesasa.nowarnings)

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"


def stem_dirs(root: Path = DATA_ROOT):
    for graph_dir in sorted(glob.glob(str(root / "graphs" / "*"))):
        nodes_csv = os.path.join(graph_dir, "coarse_graph_nodes.csv")
        pdb_path = os.path.join(graph_dir, "pocketness.pdb")
        if os.path.isfile(nodes_csv) and os.path.isfile(pdb_path):
            yield os.path.basename(graph_dir), nodes_csv, pdb_path


def compare_one(stem, nodes_csv, pdb_path):
    df = pd.read_csv(nodes_csv)
    structure = freesasa.Structure(pdb_path)
    residue_areas = freesasa.calc(structure).residueAreas()

    rows = []
    for _, row in df.iterrows():
        chain = str(row["ID_chainID"]).strip()
        resnum = str(int(row["ID_resSeq"]))
        voro = float(row["residue_sas_area"])
        fs = None
        if chain in residue_areas and resnum in residue_areas[chain]:
            fs = residue_areas[chain][resnum].total
        rows.append({"stem": stem, "chain": chain, "resnum": resnum,
                     "voronota": voro, "freesasa": fs})
    return rows


def main():
    all_rows = []
    per_protein = []
    for stem, nodes_csv, pdb_path in stem_dirs():
        try:
            rows = compare_one(stem, nodes_csv, pdb_path)
        except Exception as exc:
            print(f"  SKIP {stem}: {exc}")
            continue
        all_rows.extend(rows)
        matched = [r for r in rows if r["freesasa"] is not None]
        if len(matched) >= 5:
            v = np.array([r["voronota"] for r in matched])
            f = np.array([r["freesasa"] for r in matched])
            r_pearson, _ = stats.pearsonr(v, f)
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios = np.where(f > 0, v / np.where(f == 0, np.nan, f), np.nan)
            per_protein.append((stem, len(rows), len(matched), r_pearson,
                                 float(np.nanmean(ratios))))

    df = pd.DataFrame(all_rows)
    matched = df.dropna(subset=["freesasa"])
    n_total, n_matched = len(df), len(matched)

    print(f"{'stem':>12} {'n_res':>6} {'matched':>8} {'pearson_r':>10} {'mean_ratio(voro/fs)':>20}")
    for stem, n_res, n_match, r_pearson, ratio in per_protein:
        print(f"{stem:>12} {n_res:>6} {n_match:>8} {r_pearson:>10.3f} {ratio:>20.3f}")

    v = matched["voronota"].to_numpy()
    f = matched["freesasa"].to_numpy()
    pearson_r, pearson_p = stats.pearsonr(v, f)
    spearman_rho, spearman_p = stats.spearmanr(v, f)
    slope, intercept, _, _, _ = stats.linregress(f, v)
    ratio = np.mean(v[f > 0] / f[f > 0])
    resid = v - (slope * f + intercept)
    rmse = float(np.sqrt(np.mean(resid ** 2)))

    print(f"\n{'='*72}\nPOOLED across {len(per_protein)} proteins, "
          f"{n_matched}/{n_total} residues matched by (chain, resSeq)\n{'='*72}")
    print(f"  Pearson r      = {pearson_r:.4f}  (p={pearson_p:.2e})")
    print(f"  Spearman rho   = {spearman_rho:.4f}  (p={spearman_p:.2e})")
    print(f"  linear fit     voronota = {slope:.4f} * freesasa + {intercept:.4f}")
    print(f"  mean ratio     voronota / freesasa = {ratio:.4f}")
    print(f"  RMSE after fit = {rmse:.4f} A^2  (voronota range: "
          f"{v.min():.1f}-{v.max():.1f})")

    print("\nVerdict:")
    if n_matched < 0.9 * n_total:
        print(f"  WARNING: only {n_matched}/{n_total} residues matched by "
              f"(chain, resSeq) -- residue-key mismatch, fix before trusting the stats.")
    if pearson_r > 0.8:
        print("  Strongly correlated (rank order agrees) but NOT numerically "
              "identical -- expected, different SASA algorithms. Do not feed "
              "voronota's residue_sas_area into an ESM3 sasa track without "
              "rescaling (see slope/intercept above) or checking the tokenizer's "
              "expected value range; prefer freesasa's own values if matching the "
              "ESM3 tokenizer's calibration matters more than GNN-branch consistency.")
    elif pearson_r > 0.4:
        print("  Weakly-to-moderately correlated: same general trend, but "
              "large per-residue disagreement -- treat as different signals, "
              "not interchangeable.")
    else:
        print("  Little to no correlation -- do not treat these as the same "
              "quantity under any rescaling.")


if __name__ == "__main__":
    main()
