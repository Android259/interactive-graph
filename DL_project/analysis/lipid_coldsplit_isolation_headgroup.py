#!/usr/bin/env python3
"""Same report as analysis/lipid_coldsplit_isolation.py, on head-group-only Tanimoto.

lipid_coldsplit_isolation.py measures isolation from the WHOLE-STRUCTURE compact
Tanimoto artifact (data/Tanimoto_compact_*), which data_section.tex already notes is
dominated by the two acyl chains -- the anionic set isolates at only 0.766 there
precisely because its head groups differ from the retained phosphatidylcholines while
their chain chemistry does not. This script reads the same interaction table and the
same four --lipid_coldsplit sets plus the ethanolamine hypothetical, but against
data/Tanimoto_headgroup_compact_* (preprocessing/build_tanimoto_headgroup.py), where
every candidate has been reduced to its head group first. Everything downstream --
structures_of_rows, isolation, the valid/test halving -- is the unchanged code
lipid_coldsplit_isolation.py uses; only which compact matrix is read differs.

    python3 analysis/lipid_coldsplit_isolation_headgroup.py
    python3 analysis/lipid_coldsplit_isolation_headgroup.py --seeds 0,1,2 --data_dir data
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analysis.coldsplit_geometry import isolation, structures_of_rows  # noqa: E402
from analysis.lipid_coldsplit_isolation import (  # noqa: E402
    ETHANOLAMINE,
    block_report,
    held_mask_for,
)
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS, lipid_class_series  # noqa: E402
from dataloader.tanimoto_compact import CompactTanimoto  # noqa: E402
from preprocessing.build_tanimoto_headgroup import compact_paths  # noqa: E402
from preprocessing.lipid_marginal_baseline import halve_excluded_block  # noqa: E402


def load_headgroup_compact(data_dir, source_csv, isomeric=False):
    """The head-group compact artifact, or None if missing/stale.

    Mirrors dataloader.tanimoto_compact.load_compact's staleness check (source table
    size + mtime against the manifest) but reads build_tanimoto_headgroup.py's own
    files and format, which load_compact does not know about.
    """
    matrix_path, index_path, row_path, manifest_path = compact_paths(data_dir, isomeric=isomeric)
    if not all(p.exists() for p in (matrix_path, index_path, row_path, manifest_path)):
        return None
    manifest = json.loads(manifest_path.read_text())
    stat = source_csv.stat()
    source = manifest["source"]
    if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
        return None
    return CompactTanimoto(
        np.load(matrix_path, mmap_mode="r"),
        np.load(index_path),
        np.load(row_path),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    arguments = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, arguments.data_dir)
    csv_path = interaction_csv_path(data_dir + os.sep)
    csv = pd.read_csv(csv_path)
    classes_lower = lipid_class_series(csv).str.lower()

    from pathlib import Path
    compact = load_headgroup_compact(Path(data_dir), Path(csv_path))
    if compact is None:
        raise SystemExit(
            "head-group compact Tanimoto artifacts are missing or stale; build them "
            "with preprocessing/build_tanimoto_headgroup.py"
        )
    if int(compact.row_ids.max()) + 1 != len(csv) or len(np.unique(compact.row_ids)) != len(csv):
        raise SystemExit(
            f"head-group compact artifacts index {len(np.unique(compact.row_ids))} rows, "
            f"the table has {len(csv)}: they were built from a different table, rebuild them"
        )

    print(f"table: {os.path.basename(csv_path)}")
    print(
        f"rows {len(csv)}, positives {int(csv['Interaction'].sum())}, "
        f"proteins {csv['LTPProtein'].nunique()}, "
        f"species {csv['FullIdentityOfLipid'].nunique()}, "
        f"head-group classes {classes_lower.nunique()}"
    )
    print(
        f"head-group compact Tanimoto: {compact.structures} distinct head groups over "
        f"{compact.candidates} candidates\n"
    )

    named = dict(LIPID_COLDSPLIT_SETS)
    named["ethanolamine*"] = ETHANOLAMINE

    rows = [
        block_report(csv, compact, members, name, held_mask_for(classes_lower, members))
        for name, members in named.items()
    ]
    print("blocks, head-group-only Tanimoto (* = never actually held out; measured as a hypothetical)")
    header = (
        f"{'set':16s} {'cls':>3s} {'rows':>5s} {'species':>7s} {'struct':>6s} "
        f"{'pos':>4s} {'%pos':>5s} {'isolation':>9s} {'median':>6s} {'>=0.9':>6s}"
    )
    print(header)
    for row in rows:
        print(
            f"{row['set']:16s} {row['classes']:3d} {row['rows']:5d} "
            f"{row['species']:7d} {row['structures']:6d} {row['positives']:4d} "
            f"{row['pos_share']:5.1f} {row['isolation']:9.3f} {row['median']:6.3f} "
            f"{row['twins']:5.1f}%"
        )
    print()

    seeds = [int(seed) for seed in arguments.seeds.split(",") if seed]
    print(f"valid / test halves of each block, head-group-only Tanimoto, seeds {seeds}")
    print(
        f"{'set':16s} {'valid iso':>9s} {'test iso':>9s} {'block iso':>9s} "
        f"{'valid pos':>9s} {'test pos':>8s} {'shared species':>14s} "
        f"{'valid->test':>11s}"
    )
    for name, members in named.items():
        held_mask = held_mask_for(classes_lower, members)
        train_rows = csv.index[~held_mask].to_numpy()
        excluded = csv[held_mask]
        valid_scores, test_scores, valid_pos, test_pos, shared, cross = [], [], [], [], [], []
        for seed in seeds:
            valid, test = halve_excluded_block(excluded, seed)
            valid_scores.append(isolation(compact, valid.index.to_numpy(), train_rows))
            test_scores.append(isolation(compact, test.index.to_numpy(), train_rows))
            valid_pos.append(int(valid["Interaction"].sum()))
            test_pos.append(int(test["Interaction"].sum()))
            valid_species = set(valid["FullIdentityOfLipid"])
            test_species = set(test["FullIdentityOfLipid"])
            shared.append(100 * len(valid_species & test_species) / max(len(test_species), 1))
            cross.append(isolation(compact, test.index.to_numpy(), valid.index.to_numpy()))
        block = isolation(compact, csv.index[held_mask].to_numpy(), train_rows)
        print(
            f"{name:16s} {np.mean(valid_scores):9.3f} {np.mean(test_scores):9.3f} "
            f"{block:9.3f} {np.mean(valid_pos):9.1f} {np.mean(test_pos):8.1f} "
            f"{np.mean(shared):13.1f}% {np.mean(cross):11.3f}"
        )
    print(
        "\nSame reading as lipid_coldsplit_isolation.py, computed against head groups "
        "only: valid/test isolation uses the SAME train side (the table minus the held "
        "classes); 'shared species' is the share of test species that also appear in "
        "valid; 'valid->test' is the block statistic with valid standing in for train."
    )


if __name__ == "__main__":
    main()
