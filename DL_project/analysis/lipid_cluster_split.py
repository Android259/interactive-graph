#!/usr/bin/env python3
"""A lipid cold split cut by fingerprint distance instead of by head-group name.

LIPID_COLDSPLIT_SETS (dataloader/sampler.py) names its four held-out blocks by
chemistry -- "sphingolipids", "choline" -- and its isolation is a consequence of
that naming, measured afterwards: 0.458, 0.553, 0.653, 0.766 mean best Tanimoto
from the block to what stays in training. `anionic`'s own comment says its 0.766
is what the chemistry allows, because a fingerprint sees mostly the two acyl
chains while PA/PI/PS/PG differ from the phosphatidylcholines that stay behind
only in the head group.

That argument is about the fingerprint, not about the head group, so it invites
the opposite construction: cut the structures by fingerprint distance directly
and let the head groups fall where they fall. This script builds that split and
reports whether it buys isolation the named sets cannot, at a block size the
evaluation can still read.

It only describes splits. Nothing here trains, and no run reads it.

    python3 analysis/lipid_cluster_split.py
    python3 analysis/lipid_cluster_split.py --clusters 6,8,12 --linkage complete

Read the output as: a candidate block is usable when `isolation` is lower than
the named set you would otherwise run, `positives` is at least
COLDSPLIT_MINIMUM_TEST_POSITIVES (20), and `train pos` is still enough to learn
from. `dropped` rows are the ones whose candidate structures straddle the cut --
they can go neither to train (their chemistry is held out) nor to the block
(their chemistry is also in training), the same trade --double_coldsplit makes.
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analysis.coldsplit_geometry import isolation  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    COLDSPLIT_MINIMUM_TEST_POSITIVES,
    LIPID_COLDSPLIT_SETS,
)
from dataloader.tanimoto_compact import load_compact  # noqa: E402


def cluster_structures(compact, count, method):
    """Cluster distinct structures by 1 - Tanimoto, returning a label per structure.

    The compact matrix is already the similarity between distinct structures, so
    this is a plain hierarchical clustering of it -- no fingerprint is recomputed
    and rdkit is never imported.
    """
    similarity = np.asarray(compact.matrix, dtype=np.float32) / 255.0
    distance = 1.0 - similarity
    # squareform demands exact symmetry and a zero diagonal; the stored matrix is
    # symmetric by construction but round-trips through uint8, so force both
    # rather than trip its tolerance check.
    distance = (distance + distance.T) / 2.0
    np.fill_diagonal(distance, 0.0)
    tree = linkage(squareform(distance, checks=False), method=method)
    return fcluster(tree, t=count, criterion="maxclust")


def rows_by_cluster(compact, labels):
    """Split table rows three ways per cluster: wholly inside, straddling, outside.

    A table row lists one or more candidate structures, so it does not have to
    fall on one side of a structure-level cut. A row every one of whose
    structures is in the cluster is a clean block row; a row with structures on
    both sides is contaminated in both directions and is reported separately.
    """
    frame = pd.DataFrame(
        {
            "row": compact.row_ids,
            "cluster": labels[compact.structure_index],
        }
    )
    per_row = frame.groupby("row")["cluster"].agg(distinct="nunique", first="min")
    touching = frame.groupby("cluster")["row"].unique()
    held, straddling = {}, {}
    for cluster, rows in touching.items():
        rows = np.asarray(rows)
        clean = per_row.loc[rows, "distinct"].to_numpy() == 1
        held[cluster] = rows[clean]
        straddling[cluster] = rows[~clean]
    return held, straddling


def dominant_classes(csv, rows, classes, limit=3):
    """The head-group classes a cluster's rows are actually made of."""
    present = classes.loc[classes.index.intersection(rows)]
    if present.empty:
        return "--"
    counts = present.value_counts()
    total = int(counts.sum())
    parts = [
        f"{name}({100 * count / total:.0f}%)" for name, count in counts.head(limit).items()
    ]
    if len(counts) > limit:
        parts.append(f"+{len(counts) - limit}")
    return " ".join(parts)


def report_named_sets(csv, compact, classes):
    """The four existing sets, measured here so the cluster numbers have a scale."""
    print("named sets (dataloader/sampler.py), measured on this table")
    print(f"{'set':18s} {'isolation':>9s} {'positives':>9s} {'rows':>7s}")
    for name, members in LIPID_COLDSPLIT_SETS.items():
        held = classes.isin({member.lower() for member in members})
        held_rows = csv.index[held].to_numpy()
        train_rows = csv.index[~held].to_numpy()
        print(
            f"{name:18s} {isolation(compact, held_rows, train_rows):9.3f} "
            f"{int(csv.loc[held, 'Interaction'].sum()):9d} {int(held.sum()):7d}"
        )
    print()


def report_clusters(csv, compact, classes, labels, count):
    held, straddling = rows_by_cluster(compact, labels)
    total_positives = int(csv["Interaction"].sum())
    print(f"=== {count} clusters ===")
    print(
        f"{'cl':>3s} {'struct':>6s} {'rows':>6s} {'pos':>5s} {'dropped':>7s} "
        f"{'trainpos':>8s} {'isolation':>9s}  head-group composition"
    )
    usable = []
    for cluster in sorted(held):
        block_rows = held[cluster]
        dropped = straddling[cluster]
        touched = np.concatenate([block_rows, dropped])
        train_rows = csv.index.difference(pd.Index(touched)).to_numpy()
        block_positives = int(csv.loc[block_rows, "Interaction"].sum())
        train_positives = int(csv.loc[train_rows, "Interaction"].sum())
        score = isolation(compact, block_rows, train_rows)
        print(
            f"{cluster:3d} {int((labels == cluster).sum()):6d} {len(block_rows):6d} "
            f"{block_positives:5d} {len(dropped):7d} {train_positives:8d} "
            f"{score:9.3f}  {dominant_classes(csv, block_rows, classes)}"
        )
        if block_positives >= COLDSPLIT_MINIMUM_TEST_POSITIVES:
            usable.append((cluster, score, block_positives, train_positives))
    kept = 100 * sum(item[2] for item in usable) / max(total_positives, 1)
    print(
        f"    {len(usable)} of {len(held)} clusters hold at least "
        f"{COLDSPLIT_MINIMUM_TEST_POSITIVES} positives, {kept:.0f}% of all positives\n"
    )
    return usable


def report_family_coverage(csv, compact, labels, count):
    """Which families a cluster block could actually be scored on.

    A block only answers "does this protein take a lipid it has never seen" for a
    family with positives in it; per-family counts are what decide whether a
    per-family read of the split is possible at all.
    """
    held, _ = rows_by_cluster(compact, labels)
    families = sorted(csv["ProteinDomain"].str.lower().unique())
    print(f"positives per family in each {count}-cluster block")
    header = f"{'cl':>3s} " + "".join(f"{family[:11]:>12s}" for family in families)
    print(header)
    for cluster in sorted(held):
        block = csv.loc[held[cluster]]
        block = block[block["Interaction"] == 1]
        counts = block["ProteinDomain"].str.lower().value_counts()
        line = f"{cluster:3d} " + "".join(
            f"{int(counts.get(family, 0)):12d}" for family in families
        )
        print(line)
    print()


def report_specificity(csv, compact, labels, count, key, floor_block, floor_train):
    """Whether a single protein can be both trained and tested under a cluster cut.

    A cluster block answers "does this protein take a lipid it has never seen"
    for one protein only if that protein has positives IN the block (something to
    score) and positives LEFT in training (something to learn its preference
    from). A protein whose positives all sit in one cluster can never have both:
    hold that cluster out and training keeps none of its positives, hold any
    other out and the block scores none. `top share` is that concentration -- the
    fraction of the protein's positives in its single largest cluster -- so 1.00
    means no cluster cut can ever test it.
    """
    held, straddling = rows_by_cluster(compact, labels)
    cluster_of_row = {}
    for cluster, rows in held.items():
        for row in rows:
            cluster_of_row[row] = cluster
    positives = csv[csv["Interaction"] == 1]
    assigned = positives.index.map(lambda row: cluster_of_row.get(row, -1))
    frame = pd.DataFrame(
        {"name": positives[key].to_numpy(), "cluster": np.asarray(assigned)}
    )
    frame = frame[frame["cluster"] >= 0]

    print(f"per-{key} specificity over {count} clusters")
    print(
        f"(usable cell = at least {floor_block} positives in the block and "
        f"{floor_train} left in training)"
    )
    print(
        f"{key[:22]:22s} {'pos':>5s} {'clusters':>8s} {'top share':>9s} {'usable cells':>12s}"
    )
    rows_out = []
    for name, group in frame.groupby("name"):
        counts = group["cluster"].value_counts()
        total = int(counts.sum())
        usable = int(
            sum(
                1
                for value in counts
                if value >= floor_block and total - value >= floor_train
            )
        )
        rows_out.append((name, total, len(counts), counts.iloc[0] / total, usable))
    for name, total, clusters, top, usable in sorted(
        rows_out, key=lambda item: -item[1]
    ):
        print(f"{str(name)[:22]:22s} {total:5d} {clusters:8d} {top:9.2f} {usable:12d}")
    testable = sum(1 for item in rows_out if item[4] > 0)
    print(f"    {testable} of {len(rows_out)} have at least one usable cell\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clusters",
        default="4,6,8,12",
        help="comma-separated cluster counts to compare",
    )
    parser.add_argument(
        "--linkage",
        default="average",
        help="scipy linkage method: average, complete, ward, single",
    )
    parser.add_argument(
        "--families_for",
        type=int,
        default=0,
        help="also print the per-family positive table for this cluster count",
    )
    parser.add_argument(
        "--specificity_for",
        type=int,
        default=0,
        help="also print the per-protein/per-family specificity table for this count",
    )
    parser.add_argument("--specificity_key", default="LTPProtein")
    parser.add_argument("--floor_block", type=int, default=5)
    parser.add_argument("--floor_train", type=int, default=10)
    arguments = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, "data")
    source = interaction_csv_path(data_dir + os.sep)
    csv = pd.read_csv(source)
    classes = lipid_class_series(csv).str.lower()
    print(
        f"table: {os.path.basename(source)}\n"
        f"rows {len(csv)}, positives {int(csv['Interaction'].sum())}, "
        f"species {csv['FullIdentityOfLipid'].nunique()}, "
        f"head-group classes {classes.nunique()}\n"
    )

    compact = load_compact(data_dir, source_csv=source)
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts are missing or stale for this table; "
            "rebuild them with preprocessing/build_tanimoto_compact.py"
        )
    print(
        f"compact Tanimoto: {compact.structures} distinct structures, "
        f"{compact.candidates} candidate instances, linkage '{arguments.linkage}'\n"
    )

    report_named_sets(csv, compact, classes)

    for count in [int(value) for value in arguments.clusters.split(",") if value]:
        labels = cluster_structures(compact, count, arguments.linkage)
        report_clusters(csv, compact, classes, labels, count)
        if arguments.families_for == count:
            report_family_coverage(csv, compact, labels, count)
        if arguments.specificity_for == count:
            report_specificity(
                csv,
                compact,
                labels,
                count,
                arguments.specificity_key,
                arguments.floor_block,
                arguments.floor_train,
            )


if __name__ == "__main__":
    main()
