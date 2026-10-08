#!/usr/bin/env python3
"""What the cold splits look like on the current interaction table, and the Tanimoto
isolation formula every other split report in this project reads from here.

ISOLATION, the formula (library part of this module, imported by
analysis/lipid_block_search.py, analysis/probes/lipid_cluster_split.py,
analysis/probes/lipid_leak_ladder.py and scripts/graphics_generation/split_similarity_
vs_metric.py -- it used to live in its own analysis/compute_valid_test_tanimoto_
isolation.py):

    isolation = mean over the held-out block's distinct chemical structures of the
                highest Tanimoto similarity to any structure that stays in training

0 means the held-out chemistry has no relative left in training, 1 that every held-out
structure has a twin there. NOT specific to any one way of choosing the block and not
a cold-split-only notion: the same formula measures a --lipid_coldsplit class set, a
--lipid_isolation generated block, a --lipid_subclass/--lipid_species_coldsplit block,
a --family_only protein block, or a block a search script is still building. Every
place in this project that computes this number reads it from here; do not reimplement
the formula at a new call site -- grep this file's name before writing a
held/kept/matrix/255/max(axis=1) block anywhere else.

Two entry shapes, same underlying formula:
  * isolation(compact, held_rows, train_rows) / best_similarities(...) /
    isolation_and_cross_mean(...) -- the interaction-table-row view: start from two
    row-id arrays (what a Dataloader split, a cold-split block definition, or a
    reconstructed run's own split hands you) and let this module resolve which compact
    structures they touch.
  * isolation_from_structures(matrix, held, kept) -- the low-level, structure-indexed
    view, for a tight search loop (analysis/lipid_block_search.py): resolving rows to
    structures costs a table scan, too slow to repeat at every step, so that caller
    maintains its own masks and calls straight into the formula. `matrix` need not be
    the compact Tanimoto matrix either -- any symmetric similarity matrix in the same
    layout (raw uint8 0-255, or an already-normalized float) works.

THE REPORTS. Default run: the two things that are properties of the split rather than
of a model, and both of which move when the table does (the deduplicated table changed
the row count, the positive count and, through them, the compact Tanimoto artifacts):

  * the isolation of each lipid cold-split set: how close the chemistry it holds out
    still is to the chemistry left in training;
  * the geometry of the two-axis split per family: which classes leave, what the block
    holds, what training loses, and how the rows divide between train, validation and
    test -- with the row count an averaged evaluation actually scores.

--blocks adds the per-block detail that the one isolation number per named set does
not answer (it was analysis/lipid_coldsplit_isolation.py):

  * the VALID and TEST halves separately. The loader halves the held-out block per
    label (`Dataloader._split_interactions`, mirrored by `preprocessing.lipid_marginal_
    baseline.halve_excluded_block`), so "the block's isolation" is a property of valid
    + test together and nothing otherwise reports what the epoch-selection half on its
    own is isolated from. Reported per seed, along with how much valid and test share
    with EACH OTHER -- the part that decides whether a checkpoint chosen on valid is
    chosen on the rows it will be read on.
  * the ethanolamine classes (PE, LPE). They are in no set by design, so no loop over
    LIPID_COLDSPLIT_SETS reaches them, and the one number the project quotes for them
    (0.778, dataloader/sampler.py) is not produced by anything else in the repository.
    Measured as a hypothetical fifth block, exactly as the four real ones are.
  * what the mean hides. The statistic is a mean over block structures of the BEST
    similarity to a training structure, so one twin in training is enough to put a
    structure at 1.0. The median and the share of block structures above 0.9 say
    whether the mean describes the block or a handful of twins.

--tanimoto headgroup runs --blocks against head-group-only fingerprints
(data/cache/Tanimoto_headgroup_compact_*, preprocessing/build_tanimoto_headgroup.py)
instead of whole structures (it was analysis/probes/lipid_coldsplit_isolation_
headgroup.py). The whole-structure artifact is dominated by the two acyl chains, which
data_section.tex already notes: the anionic set isolates at only 0.766 there precisely
because its head groups differ from the retained phosphatidylcholines while their
chain chemistry does not. Everything downstream of the matrix choice is the same code.

--classes/--species/--proteins measures ONE block named on the command line instead of
the project's own sets (it was compute_valid_test_tanimoto_isolation.py's own CLI):
whichever rows match stay out of training. It touches no real split logic in
dataloader/, so it is not what a run trains and tests on, only an estimate of how
isolated that chemistry or that protein's rows would be if held out.

Nothing here trains anything or reads a label the split does not already use.

    python3 analysis/coldsplit_geometry.py
    python3 analysis/coldsplit_geometry.py --share 0.5 --seeds 0,1,2
    python3 analysis/coldsplit_geometry.py --blocks
    python3 analysis/coldsplit_geometry.py --blocks --tanimoto headgroup
    python3 analysis/coldsplit_geometry.py --classes PC,PE
    python3 analysis/coldsplit_geometry.py --species "Ceramide (d34:1)"
    python3 analysis/coldsplit_geometry.py --proteins GLTP,scp2
"""

import argparse
import os
import sys
from pathlib import Path

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
from dataloader.tanimoto_compact import CompactTanimoto, load_compact  # noqa: E402
from preprocessing.lipid_marginal_baseline import halve_excluded_block  # noqa: E402

FAMILIES = (
    "CRAL-TRIO",
    "GLTP",
    "IP_trans",
    "LBP_BPI_CETP",
    "lipocalin",
    "scp2",
    "START",
)

# PE and LPE are deliberately in no set (see the LIPID_COLDSPLIT_SETS comment). Measured
# as a block anyway by --blocks, because "we did not hold them out because they isolate
# no better than anionic" is a claim about a number nothing else in the repository
# computes.
ETHANOLAMINE = ("Phosphatidylethanolamine", "Lysophosphatidylethanolamine")


def structures_of_rows(compact, rows):
    """The distinct structure ids the given table rows contribute candidates for."""
    wanted = np.isin(compact.row_ids, np.asarray(sorted(rows), dtype=compact.row_ids.dtype))
    return np.unique(compact.structure_index[wanted])


def best_similarities(compact, held_rows, train_rows):
    """One value per held structure: its best Tanimoto similarity to a kept one.

    `isolation` below means over this vector; `similarity_profile` reads
    mean/median/share>=0.9 off the same vector instead of resolving held/kept and
    building the block a second time. Empty when either side resolves to no structures.
    """
    held = structures_of_rows(compact, held_rows)
    kept = structures_of_rows(compact, train_rows)
    if not len(held) or not len(kept):
        return np.empty(0, dtype=np.float32)
    block = np.asarray(compact.matrix[np.ix_(held, kept)], dtype=np.float32) / 255.0
    return block.max(axis=1)


def isolation(compact, held_rows, train_rows):
    """Mean over the held-out structures of the best similarity to a training one."""
    best = best_similarities(compact, held_rows, train_rows)
    return float(best.mean()) if len(best) else float("nan")


def isolation_and_cross_mean(compact, held_rows, train_rows):
    """Both similarity readings of one held-out block against training.

    `isolation` is the number above (mean of the row maxima); `cross_mean` is the
    plain mean over all cross pairs, which is what analysis/tanimoto_groups/ reported
    for protein groups before this formula had a home. They answer different questions
    -- "is there a relative left in training" versus "how similar is the chemistry on
    average" -- and disagree most exactly where a block has a few close relatives and
    many distant ones, so scripts/graphics_generation/split_similarity_vs_metric.py
    carries both.
    """
    held = structures_of_rows(compact, held_rows)
    kept = structures_of_rows(compact, train_rows)
    if not len(held) or not len(kept):
        return {
            "isolation": float("nan"),
            "cross_mean": float("nan"),
            "block_structures": int(len(held)),
            "train_structures": int(len(kept)),
        }
    block = np.asarray(compact.matrix[np.ix_(held, kept)], dtype=np.float32) / 255.0
    return {
        "isolation": float(block.max(axis=1).mean()),
        "cross_mean": float(block.mean()),
        "block_structures": int(len(held)),
        "train_structures": int(len(kept)),
    }


def isolation_from_structures(matrix, held, kept):
    """The same formula from structure-indexed masks or index arrays a caller already
    holds, rather than row ids -- what a search loop needs when it maintains `held`/
    `kept` incrementally over many steps and cannot afford a row lookup at each one
    (analysis/lipid_block_search.py's Units.isolation_from_masks).

    `held`/`kept` may be boolean masks over the matrix's structure axis, or integer
    index arrays -- both work unchanged inside `np.ix_`. `matrix` may be the raw uint8
    compact matrix (0-255, normalized here) or an already-normalized float matrix.
    """
    held = np.asarray(held)
    kept = np.asarray(kept)
    held_empty = not held.any() if held.dtype == bool else held.size == 0
    kept_empty = not kept.any() if kept.dtype == bool else kept.size == 0
    if held_empty or kept_empty:
        return float("nan")
    block = matrix[np.ix_(held, kept)]
    if np.issubdtype(block.dtype, np.integer):
        block = block.astype(np.float32) / 255.0
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


def load_headgroup_compact(data_dir, source_csv, isomeric=False):
    """The head-group compact artifact, or None if missing/stale.

    Mirrors dataloader.tanimoto_compact.load_compact's staleness check (source table
    size + mtime against the manifest) but reads preprocessing/build_tanimoto_
    headgroup.py's own files and format, which load_compact does not know about.
    """
    import json

    from preprocessing.build_tanimoto_headgroup import compact_paths

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


def similarity_profile(compact, held_rows, train_rows):
    """Mean / median / share>=0.9 of the best training similarity per block structure.

    The mean is `isolation` -- recomputed here from the same vector
    (best_similarities) rather than called twice, so the three numbers are guaranteed
    to describe one distribution and not two.
    """
    best = best_similarities(compact, held_rows, train_rows)
    if not len(best):
        return float("nan"), float("nan"), float("nan"), 0
    return float(best.mean()), float(np.median(best)), float((best >= 0.9).mean()), len(best)


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


def report_blocks(csv, compact, classes_lower, seeds, headgroup=False):
    """Per --lipid_coldsplit block: size, isolation with its median and twin share, and
    the valid/test halves separately -- what one isolation number per named set cannot
    say. `headgroup` only changes the wording; `compact` decides what was measured.
    """
    axis = "head-group-only Tanimoto" if headgroup else "whole-structure Tanimoto"
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
    print(f"blocks, {axis} (* = never actually held out; measured as a hypothetical)")
    print(
        f"{'set':16s} {'cls':>3s} {'rows':>5s} {'species':>7s} {'struct':>6s} "
        f"{'pos':>4s} {'%pos':>5s} {'isolation':>9s} {'median':>6s} {'>=0.9':>6s}"
    )
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

    print(f"valid / test halves of each block, {axis}, seeds {seeds}")
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
    print()


def held_mask_from_selector(csv, species=None, classes=None, proteins=None):
    """Which rows of the table the command line put in the held-out block.

    Exactly one of the three selectors is given; a row matches when its species / its
    head-group class / its protein is one of the named values. Everything else is
    "training" for this one-off check.
    """
    if species is not None:
        return csv["FullIdentityOfLipid"].isin(species)
    if classes is not None:
        wanted = {name.lower() for name in classes}
        return lipid_class_series(csv).str.lower().isin(wanted)
    wanted = {name.lower() for name in proteins}
    return csv["ProteinDomain"].str.lower().isin(wanted)


def report_named_block(csv, compact, held):
    """Isolation and cross-mean of one block named on the command line."""
    held_rows = csv.index[held].to_numpy()
    train_rows = csv.index[~held].to_numpy()
    if not len(held_rows):
        raise SystemExit("no rows matched the given selector")
    result = isolation_and_cross_mean(compact, held_rows, train_rows)
    positives = int(csv.loc[held, "Interaction"].sum())
    total_positives = int(csv["Interaction"].sum())
    print(f"rows held out      : {int(held.sum())} ({len(held_rows)})")
    print(f"positives held out : {positives} / {total_positives} "
          f"({100 * positives / max(total_positives, 1):.1f}%)")
    print(f"block structures   : {result['block_structures']}")
    print(f"train structures   : {result['train_structures']}")
    print(f"isolation          : {result['isolation']:.3f}")
    print(f"cross_mean         : {result['cross_mean']:.3f}")


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
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--share", type=float, default=0.8)
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
    parser.add_argument(
        "--blocks", action="store_true",
        help="per --lipid_coldsplit block: size, isolation with its median and twin "
             "share, the ethanolamine hypothetical, and the valid/test halves per seed. "
             "Printed instead of the default two reports.",
    )
    parser.add_argument(
        "--tanimoto", choices=("whole", "headgroup"), default="whole",
        help="which fingerprints --blocks measures against: whole structures "
             "(default) or head groups only (preprocessing/build_tanimoto_headgroup.py).",
    )
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--species", help="comma-separated FullIdentityOfLipid values to hold out")
    selector.add_argument("--classes", help="comma-separated lipid head-group classes to hold out")
    selector.add_argument("--proteins", help="comma-separated ProteinDomain values to hold out")
    parser.add_argument("--data_dir", default="data")
    arguments = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, arguments.data_dir)
    csv_path = interaction_csv_path(data_dir + os.sep)
    csv = pd.read_csv(csv_path)
    seeds = [int(seed) for seed in arguments.seeds.split(",") if seed]
    one_block = arguments.species or arguments.classes or arguments.proteins

    print(
        f"table: {os.path.basename(csv_path)}\n"
        f"rows {len(csv)}, positives {int(csv['Interaction'].sum())}, "
        f"proteins {csv['LTPProtein'].nunique()}, species {csv['FullIdentityOfLipid'].nunique()}\n"
    )

    if arguments.tanimoto == "headgroup":
        compact = load_headgroup_compact(Path(data_dir), Path(csv_path))
        if compact is None:
            raise SystemExit(
                "head-group compact Tanimoto artifacts are missing or stale; build them "
                "with preprocessing/build_tanimoto_headgroup.py"
            )
        print(
            f"head-group compact Tanimoto: {compact.structures} distinct head groups "
            f"over {compact.candidates} candidates\n"
        )
    else:
        # The mtime guard in load_compact is deliberately NOT used for --blocks. It
        # compares the table's nanosecond mtime against the manifest, so a table that
        # was re-copied without changing reads as stale even when its bytes are the ones
        # the artifacts were built from. What actually has to hold is that the artifacts
        # index THIS table, which is what the assertion below checks; a content mismatch
        # changes the candidate count and cannot survive it.
        compact = (
            load_compact(data_dir) if arguments.blocks
            else load_compact(data_dir, source_csv=csv_path)
        )
        if compact is None:
            raise SystemExit(
                "compact Tanimoto artifacts are missing or stale for this table; "
                "rebuild them with preprocessing/build_tanimoto_compact.py"
            )
    if int(compact.row_ids.max()) + 1 != len(csv) or len(
        np.unique(compact.row_ids)
    ) != len(csv):
        raise SystemExit(
            f"compact artifacts index {len(np.unique(compact.row_ids))} rows, the table "
            f"has {len(csv)}: they were built from a different table, rebuild them"
        )

    if one_block:
        report_named_block(csv, compact, held_mask_from_selector(
            csv,
            species=arguments.species.split(",") if arguments.species else None,
            classes=arguments.classes.split(",") if arguments.classes else None,
            proteins=arguments.proteins.split(",") if arguments.proteins else None,
        ))
        return

    if arguments.blocks:
        report_blocks(
            csv, compact, lipid_class_series(csv).str.lower(), seeds,
            headgroup=arguments.tanimoto == "headgroup",
        )
        return

    report_lipid_sets(csv, compact)

    if arguments.sweep:
        shares = [float(value) for value in arguments.sweep.split(",") if value]
        sweep_shares(csv, compact, shares, seeds[0], FAMILIES)

    if not arguments.skip_double:
        report_double_split(
            csv, arguments.share, seeds, arguments.eval_candidates_per_pair
        )


if __name__ == "__main__":
    main()
