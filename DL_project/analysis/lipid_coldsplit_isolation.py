#!/usr/bin/env python3
"""Isolation of every --lipid_coldsplit block, its valid/test halves, and the kept set.

`analysis/coldsplit_geometry.py:report_lipid_sets` already prints one isolation number
per named set. Three things it does not answer, and this does:

  * the VALID and TEST halves separately. The loader halves the held-out block per label
    (`Dataloader._split_interactions`, mirrored by
    `preprocessing.lipid_marginal_baseline.halve_excluded_block`), so "the block's
    isolation" is a property of valid + test together and nothing reports what the
    epoch-selection half on its own is isolated from. Reported here per seed, along with
    how much valid and test share with EACH OTHER -- which is the part that decides
    whether a checkpoint chosen on valid is chosen on the rows it will be read on.
  * the ethanolamine classes (PE, LPE). They are in no set by design, so no loop over
    LIPID_COLDSPLIT_SETS can reach them, and the one number the project quotes for them
    (0.778, dataloader/sampler.py) is not produced by anything in the repository.
    Measured here as a hypothetical fifth block, exactly as the four real ones are.
  * what the mean hides. The statistic is a mean over block structures of the BEST
    similarity to a training structure, so one twin in training is enough to put a
    structure at 1.0. The median and the share of block structures above 0.9 say whether
    the mean is a description of the block or of a handful of twins.

Nothing here trains, samples negatives, or writes to data/. It reads the interaction
table and the compact Tanimoto artifacts and prints.

    python3 analysis/lipid_coldsplit_isolation.py
    python3 analysis/lipid_coldsplit_isolation.py --seeds 0,1,2 --data_dir data
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analysis.coldsplit_geometry import isolation, structures_of_rows  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS, lipid_class_series  # noqa: E402
from dataloader.tanimoto_compact import load_compact  # noqa: E402
from preprocessing.lipid_marginal_baseline import halve_excluded_block  # noqa: E402

# PE and LPE are deliberately in no set (see the LIPID_COLDSPLIT_SETS comment). Measured
# as a block anyway, because "we did not hold them out because they isolate no better
# than anionic" is a claim about a number nothing in the repository computes.
ETHANOLAMINE = ("Phosphatidylethanolamine", "Lysophosphatidylethanolamine")


def similarity_profile(compact, held_rows, train_rows):
    """Mean / median / share>=0.9 of the best training similarity per block structure.

    The mean is `coldsplit_geometry.isolation` -- recomputed here from the same vector
    rather than called twice, so the three numbers are guaranteed to describe one
    distribution and not two.
    """
    held = structures_of_rows(compact, held_rows)
    kept = structures_of_rows(compact, train_rows)
    if not len(held) or not len(kept):
        return float("nan"), float("nan"), float("nan"), 0
    block = np.asarray(compact.matrix[np.ix_(held, kept)], dtype=np.float32) / 255.0
    best = block.max(axis=1)
    return float(best.mean()), float(np.median(best)), float((best >= 0.9).mean()), len(held)


def block_report(csv, compact, classes, name, held_mask):
    held_rows = csv.index[held_mask].to_numpy()
    train_rows = csv.index[~held_mask].to_numpy()
    mean, median, twins, structures = similarity_profile(compact, held_rows, train_rows)
    positives = int(csv.loc[held_mask, "Interaction"].sum())
    total_positives = int(csv["Interaction"].sum())
    return {
        "set": name,
        "classes": len(classes),
        "rows": int(held_mask.sum()),
        "species": int(csv.loc[held_mask, "FullIdentityOfLipid"].nunique()),
        "structures": structures,
        "positives": positives,
        "pos_share": 100 * positives / max(total_positives, 1),
        "isolation": mean,
        "median": median,
        "twins": 100 * twins,
    }


def held_mask_for(classes_lower, members):
    return classes_lower.isin({member.lower() for member in members})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    arguments = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, arguments.data_dir)
    csv_path = interaction_csv_path(data_dir + os.sep)
    csv = pd.read_csv(csv_path)
    classes_lower = lipid_class_series(csv).str.lower()

    # The mtime guard in load_compact is deliberately NOT used here. It compares the
    # table's nanosecond mtime against the manifest, so a table that was re-copied
    # without changing reads as stale even when its bytes are the ones the artifacts
    # were built from. What actually has to hold is that the artifacts index THIS table,
    # which is what the two assertions below check; a content mismatch changes the
    # candidate count and cannot survive them.
    compact = load_compact(data_dir)
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts are missing; build them with "
            "preprocessing/build_tanimoto_compact.py"
        )
    if int(compact.row_ids.max()) + 1 != len(csv) or len(
        np.unique(compact.row_ids)
    ) != len(csv):
        raise SystemExit(
            f"compact artifacts index {len(np.unique(compact.row_ids))} rows, the table "
            f"has {len(csv)}: they were built from a different table, rebuild them"
        )

    print(f"table: {os.path.basename(csv_path)}")
    print(
        f"rows {len(csv)}, positives {int(csv['Interaction'].sum())}, "
        f"proteins {csv['LTPProtein'].nunique()}, "
        f"species {csv['FullIdentityOfLipid'].nunique()}, "
        f"head-group classes {classes_lower.nunique()}"
    )
    print(
        f"compact Tanimoto: {compact.structures} distinct structures over "
        f"{compact.candidates} candidates\n"
    )

    named = dict(LIPID_COLDSPLIT_SETS)
    named["ethanolamine*"] = ETHANOLAMINE

    missing = {
        name: [c for c in members if c.lower() not in set(classes_lower)]
        for name, members in named.items()
    }
    missing = {name: absent for name, absent in missing.items() if absent}
    if missing:
        print("class names in a set that no row carries:")
        for name, absent in missing.items():
            print(f"  {name}: {', '.join(absent)}")
        print()

    rows = [
        block_report(csv, compact, members, name, held_mask_for(classes_lower, members))
        for name, members in named.items()
    ]
    covered = held_mask_for(
        classes_lower, [c for members in named.values() for c in members]
    )
    print("blocks (* = never actually held out; measured as a hypothetical)")
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
    print(
        f"{'(in no set)':16s} {classes_lower[~covered].nunique():3d} "
        f"{int((~covered).sum()):5d} {csv.loc[~covered, 'FullIdentityOfLipid'].nunique():7d} "
        f"{'':6s} {int(csv.loc[~covered, 'Interaction'].sum()):4d}"
    )
    print()

    seeds = [int(seed) for seed in arguments.seeds.split(",") if seed]
    print(f"valid / test halves of each block, seeds {seeds}")
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
            shared.append(
                100 * len(valid_species & test_species) / max(len(test_species), 1)
            )
            # The other half is not training, so this is not a leak into train. It is
            # what a checkpoint chosen on valid is chosen on, relative to the rows it is
            # then read on: 1.0 means every test structure has its twin inside valid.
            cross.append(isolation(compact, test.index.to_numpy(), valid.index.to_numpy()))
        block = isolation(compact, csv.index[held_mask].to_numpy(), train_rows)
        print(
            f"{name:16s} {np.mean(valid_scores):9.3f} {np.mean(test_scores):9.3f} "
            f"{block:9.3f} {np.mean(valid_pos):9.1f} {np.mean(test_pos):8.1f} "
            f"{np.mean(shared):13.1f}% {np.mean(cross):11.3f}"
        )
    print(
        "\nvalid/test isolation is measured against the SAME train side (the table "
        "minus the held classes),\nso the two halves differ only by the seed's draw. "
        "'shared species' is the share of test species\nthat also appear in valid; "
        "'valid->test' is the block statistic with valid standing in for train."
    )


if __name__ == "__main__":
    main()
