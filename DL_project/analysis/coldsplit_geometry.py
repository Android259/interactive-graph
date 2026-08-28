#!/usr/bin/env python3
"""What the cold splits look like on the current interaction table.

Two things the report states as properties of the split rather than of a model, and
both of which move when the table does -- the deduplicated table changed the row count,
the positive count and, through them, the compact Tanimoto artifacts:

  * the isolation of each lipid cold-split set: how close the chemistry it holds out
    still is to the chemistry left in training, measured as the mean over the set's
    structures of the highest fingerprint similarity to any structure that stays;
  * the geometry of the two-axis split per family: which classes leave, what the block
    holds, what training loses, and how the rows divide between train, validation and
    test -- with the row count an averaged evaluation actually scores.

Nothing here trains anything or reads a label the split does not already use.

    python3 analysis/coldsplit_geometry.py
    python3 analysis/coldsplit_geometry.py --share 0.5 --seeds 0,1,2
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    LIPID_COLDSPLIT_SETS,
    lipid_class_series,
)
from dataloader.tanimoto_compact import load_compact  # noqa: E402

FAMILIES = (
    "CRAL-TRIO",
    "GLTP",
    "IP_trans",
    "LBP_BPI_CETP",
    "lipocalin",
    "scp2",
    "START",
)


def structures_of_rows(compact, rows):
    """The distinct structure ids the given table rows contribute candidates for."""
    wanted = np.isin(compact.row_ids, np.asarray(sorted(rows), dtype=compact.row_ids.dtype))
    return np.unique(compact.structure_index[wanted])


def isolation(compact, held_rows, train_rows):
    """Mean over the held-out structures of the best similarity to a training one.

    The same reading the report gives: 0 would mean the held-out chemistry has no
    relative left in training, 1 that every held-out structure has a twin there.
    """
    held = structures_of_rows(compact, held_rows)
    kept = structures_of_rows(compact, train_rows)
    if not len(held) or not len(kept):
        return float("nan")
    block = np.asarray(compact.matrix[np.ix_(held, kept)], dtype=np.float32) / 255.0
    return float(block.max(axis=1).mean())


def report_lipid_sets(csv, compact):
    classes = lipid_class_series(csv).str.lower()
    positives = int(csv["Interaction"].sum())
    print("lipid cold-split sets")
    print(f"{'set':18s} {'isolation':>9s} {'positives held out':>19s} {'rows held out':>13s}")
    for name, members in LIPID_COLDSPLIT_SETS.items():
        held = classes.isin({member.lower() for member in members})
        held_rows = csv.index[held].to_numpy()
        train_rows = csv.index[~held].to_numpy()
        held_positives = int(csv.loc[held, "Interaction"].sum())
        print(
            f"{name:18s} {isolation(compact, held_rows, train_rows):9.3f} "
            f"{held_positives:9d} ({100 * held_positives / max(positives, 1):4.1f}%) "
            f"{int(held.sum()):13d}"
        )
    print()


def evaluation_rows(csv, rows, cap):
    """How many rows an averaged evaluation scores for the given table rows.

    One per candidate structure, capped the way Dataloader caps it, so the number
    is the work a validation pass does rather than the size of the block.
    """
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    total = 0
    for _, row in csv.loc[rows].iterrows():
        count = max(len(candidates_for_row(row)), 1)
        total += count if cap <= 0 or count <= cap else cap
    return total


def report_double_split(csv, share, seeds, cap):
    from dataloader.sampler import lipid_classes_for_holdout

    print(f"two-axis split, share {share}, negatives 2 per positive, seeds {seeds}")
    header = (
        f"{'family':14s} {'classes':>7s} {'block pos':>9s} {'train pos lost':>14s} "
        f"{'train':>6s} {'valid':>6s} {'test':>6s} {'train pos share':>15s} "
        f"{'valid scored':>12s} {'test scored':>11s}"
    )
    print(header)
    from dataloader.Dataloader import PLIDataset
    from read_configuration import ModelConfig

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    for family in FAMILIES:
        sizes = []
        for seed in seeds:
            config = ModelConfig()
            config.excluded_groups = [family.lower()]
            config.double_coldsplit = True
            config.balanced_proteins = True
            config.negatives_per_positive = 2
            config.coldsplit_share = share
            config.num_workers = 0
            config.validate()
            train, valid, test = PLIDataset(
                root_dir=data_dir,
                csv=csv.copy(),
                seed=seed,
                excluded_subgroups=set(),
                config=config,
                excluded_groups=config.excluded_groups,
            )
            sizes.append(
                (
                    len(train.csv),
                    len(valid.csv),
                    len(test.csv),
                    float(train.csv["Interaction"].mean()),
                    evaluation_rows(csv, valid.csv["pair_id"].to_numpy(), cap),
                    evaluation_rows(csv, test.csv["pair_id"].to_numpy(), cap),
                )
            )
        mean = np.mean(np.array(sizes, dtype=float), axis=0)

        classes, _, _ = lipid_classes_for_holdout(csv, family.lower(), share)
        held = lipid_class_series(csv).str.lower().isin({c.lower() for c in classes})
        family_rows = csv["ProteinDomain"].str.lower() == family.lower()
        block_positives = int(csv.loc[held & family_rows, "Interaction"].sum())
        train_lost = int(csv.loc[held & ~family_rows, "Interaction"].sum())
        print(
            f"{family:14s} {len(classes):7d} {block_positives:9d} {train_lost:14d} "
            f"{mean[0]:6.0f} {mean[1]:6.0f} {mean[2]:6.0f} {mean[3]:15.3f} "
            f"{mean[4]:12.0f} {mean[5]:11.0f}"
        )
    print()


def sweep_shares(csv, compact, shares, seed, families):
    """Per family and share: what leaves, what is left, and how far apart the two are.

    The share decides how much of a family's own positives the held-out classes have to
    cover, and the report fixed one value for every family. Whether that is the right
    value is a per-family question: a family whose positives sit in one large class
    reaches any share with that class alone, and the classes it would add next are its
    lipids' closest relatives -- which is exactly what decides whether the block is an
    extrapolation or a lookup.

    Reported per (family, share):
      classes / block positives -- the size of the question;
      train positives           -- what is left to learn from;
      similarity                -- mean over the block's structures of the best Tanimoto
                                   to a structure still in training, so LOWER is a
                                   harder, more isolated block;
      lipid BA / class BA       -- the protein-blind lookup baselines on the block, which
                                   must stay at 0.5 or the split is not two-sided.
    """
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))
    from lipid_marginal_baseline import report as marginal_report

    from dataloader.sampler import lipid_classes_for_holdout

    print(f"share sweep, seed {seed}, negatives 2 per positive")
    print(
        f"{'family':14s} {'share':>5s} {'classes':>7s} {'block pos':>9s} "
        f"{'train pos':>9s} {'similarity':>10s} {'lipid BA':>8s} {'class BA':>8s}"
    )
    best = {}
    for family in families:
        for share in shares:
            classes, covered, cost = lipid_classes_for_holdout(csv, family.lower(), share)
            if not classes:
                continue
            held = lipid_class_series(csv).str.lower().isin({c.lower() for c in classes})
            family_rows = csv["ProteinDomain"].str.lower() == family.lower()
            block_rows = csv.index[held & family_rows].to_numpy()
            train_rows = csv.index[~held & ~family_rows].to_numpy()
            train_positives = int(csv.loc[~held & ~family_rows, "Interaction"].sum())
            similarity = isolation(compact, block_rows, train_rows)

            frame = marginal_report(
                csv, [family.lower()], [seed], "balanced_proteins",
                ratio=2, share=share, double=True,
            )
            if frame.empty:
                continue
            lipid_ba = float(frame["identity_BA"].mean())
            class_ba = float(frame["class_BA"].mean())
            print(
                f"{family:14s} {share:5.2f} {len(classes):7d} {covered:9d} "
                f"{train_positives:9d} {similarity:10.3f} {lipid_ba:8.3f} {class_ba:8.3f}"
            )
            usable = (
                abs(lipid_ba - 0.5) <= 0.03
                and abs(class_ba - 0.5) <= 0.03
                and covered >= 30
                and train_positives >= 200
            )
            if usable and (family not in best or similarity < best[family][1]):
                best[family] = (share, similarity, len(classes), covered, train_positives)
        print()

    print("lowest similarity among the shares that keep both baselines at 0.5,")
    print("hold at least 30 positives in the block and leave at least 200 in training:")
    print(
        f"{'family':14s} {'share':>5s} {'classes':>7s} {'block pos':>9s} "
        f"{'train pos':>9s} {'similarity':>10s}"
    )
    for family in families:
        if family not in best:
            print(f"{family:14s} {'--':>5s}   no share satisfies the constraints")
            continue
        share, similarity, classes, covered, train_positives = best[family]
        print(
            f"{family:14s} {share:5.2f} {classes:7d} {covered:9d} "
            f"{train_positives:9d} {similarity:10.3f}"
        )
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument(
        "--eval_candidates_per_pair",
        type=int,
        default=4,
        help="candidates an averaged evaluation scores per pair; 0 for all of them",
    )
    parser.add_argument("--skip_double", action="store_true")
    parser.add_argument(
        "--sweep",
        default="",
        help="comma-separated shares to compare per family, e.g. 0.5,0.6,0.7,0.8",
    )
    arguments = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pd.read_csv(interaction_csv_path(data_dir + os.sep))
    print(
        f"table: {os.path.basename(interaction_csv_path(data_dir))}\n"
        f"rows {len(csv)}, positives {int(csv['Interaction'].sum())}, "
        f"proteins {csv['LTPProtein'].nunique()}, species {csv['FullIdentityOfLipid'].nunique()}\n"
    )

    compact = load_compact(data_dir, source_csv=interaction_csv_path(data_dir + os.sep))
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts are missing or stale for this table; "
            "rebuild them with preprocessing/build_tanimoto_compact.py"
        )
    report_lipid_sets(csv, compact)

    if arguments.sweep:
        shares = [float(value) for value in arguments.sweep.split(",") if value]
        seeds = [int(seed) for seed in arguments.seeds.split(",") if seed]
        sweep_shares(csv, compact, shares, seeds[0], FAMILIES)

    if not arguments.skip_double:
        seeds = [int(seed) for seed in arguments.seeds.split(",") if seed]
        report_double_split(
            csv, arguments.share, seeds, arguments.eval_candidates_per_pair
        )


if __name__ == "__main__":
    main()
