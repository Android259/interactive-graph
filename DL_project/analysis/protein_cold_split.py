#!/usr/bin/env python3
"""A protein cold split cut by sequence identity instead of by domain name.

The nine `ProteinDomain` families are the split axis every cross-protein run
currently uses. They are a curated annotation, not a measurement, so nothing in
them guarantees that a held-out protein has no close homologue left in training
-- and a paralogue in training is the protein-side version of the leak the lipid
cold split exists to close: the model can answer from the homologue's binding
profile without reading the held-out protein's own structure.

This script measures that. It aligns the 35 sequences in `data/fasta`, clusters
them by identity, and reports for each candidate fold how far the held-out
proteins actually are from what stays in training -- for the sequence-identity
clusters and, on the same scale, for the nine annotated families.

Pair with a PU-style ranking metric, not accuracy: `Interaction=0` is unlabelled
rather than a confirmed non-binder (preprocessing/complete_lipid_candidate_sets.py,
training/pair_baseline_common.py:184), so a fold is scored by whether the held-out
proteins' known positives rank above their own unlabelled pool.

It only describes splits. Nothing here trains, and no run reads it.

    python3 analysis/protein_cold_split.py
    python3 analysis/protein_cold_split.py --thresholds 0.25,0.30,0.40
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.Align import PairwiseAligner, substitution_matrices
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dataloader.dataset_source import interaction_csv_path  # noqa: E402


def read_sequences(fasta_dir):
    """The one sequence per protein, keyed by the name the interaction table uses.

    Files are named `<PROTEIN>_<pdb>.pdb1.fasta` or `<PROTEIN>-<uniprot>.pdb1.fasta`
    and may carry several chains; the chains of these entries are copies of one
    subunit, so the longest record represents the protein.
    """
    sequences = {}
    for path in sorted(Path(fasta_dir).glob("*.fasta")):
        name = path.name.split(".")[0].replace("-", "_").split("_")[0]
        if not name:
            continue
        best = ""
        current = []
        for line in path.read_text().splitlines():
            if line.startswith(">"):
                best = max(best, "".join(current), key=len)
                current = []
            else:
                current.append(line.strip())
        best = max(best, "".join(current), key=len)
        if best:
            sequences[name] = best
    return sequences


def identity_matrix(sequences):
    """Pairwise identity, as identical aligned residues over the shorter sequence.

    Global alignment with BLOSUM62 and affine gaps, the usual choice for judging
    whether two sequences are homologous at all. Dividing by the shorter length
    rather than by the alignment length is the generous reading: a short domain
    fully contained in a longer protein scores high, which is what "the model
    could answer from the homologue" needs it to do.
    """
    aligner = PairwiseAligner()
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -11
    aligner.extend_gap_score = -1
    aligner.mode = "global"

    names = sorted(sequences)
    size = len(names)
    identity = np.eye(size, dtype=np.float32)
    for i in range(size):
        for j in range(i + 1, size):
            first, second = sequences[names[i]], sequences[names[j]]
            alignment = aligner.align(first, second)[0]
            matches = sum(
                1
                for a, b in zip(alignment[0], alignment[1])
                if a == b and a != "-"
            )
            score = matches / min(len(first), len(second))
            identity[i, j] = identity[j, i] = score
    return names, identity


def clusters_at(identity, threshold):
    """Single-linkage clusters: two proteins join when identity reaches threshold.

    Single linkage is the right rule for homology, which is transitive in the way
    that matters here -- if A is close to B and B to C, putting A and C in
    different folds still leaves a bridge through B.
    """
    distance = 1.0 - identity
    np.fill_diagonal(distance, 0.0)
    distance = (distance + distance.T) / 2.0
    tree = linkage(squareform(distance, checks=False), method="single")
    return fcluster(tree, t=1.0 - threshold, criterion="distance")


def fold_report(csv, names, identity, labels, title, positives_by_protein):
    """Per fold: what leaves, what stays, and how close the two still are."""
    index = {name: position for position, name in enumerate(names)}
    total_positives = int(csv["Interaction"].sum())
    print(title)
    print(
        f"{'fold':>4s} {'proteins':>8s} {'held pos':>8s} {'train pos':>9s} "
        f"{'max ident':>9s}  members"
    )
    rows = []
    for fold in sorted(set(labels)):
        members = [name for name, label in zip(names, labels) if label == fold]
        held = [index[name] for name in members]
        kept = [index[name] for name in names if name not in set(members)]
        held_positives = int(sum(positives_by_protein.get(name, 0) for name in members))
        bridge = (
            float(identity[np.ix_(held, kept)].max()) if held and kept else float("nan")
        )
        print(
            f"{fold:4d} {len(members):8d} {held_positives:8d} "
            f"{total_positives - held_positives:9d} {bridge:9.2f}  "
            f"{' '.join(sorted(members))[:60]}"
        )
        rows.append((fold, len(members), held_positives, bridge))
    scoreable = [row for row in rows if row[2] >= 5]
    worst = max((row[3] for row in rows if row[3] == row[3]), default=float("nan"))
    print(
        f"    {len(rows)} folds, {len(scoreable)} with at least 5 held-out positives; "
        f"highest bridge to training {worst:.2f}\n"
    )
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--thresholds",
        default="0.25,0.30,0.40",
        help="identity thresholds at which proteins join one fold",
    )
    parser.add_argument("--fasta_dir", default=os.path.join(PROJECT_ROOT, "data", "fasta"))
    arguments = parser.parse_args()

    source = interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep)
    csv = pd.read_csv(source)
    positives_by_protein = (
        csv[csv["Interaction"] == 1].groupby("LTPProtein").size().to_dict()
    )

    sequences = read_sequences(arguments.fasta_dir)
    in_table = set(csv["LTPProtein"].unique())
    missing = in_table - set(sequences)
    extra = set(sequences) - in_table
    print(
        f"table: {os.path.basename(source)}, {len(csv)} rows, "
        f"{int(csv['Interaction'].sum())} positives, {len(in_table)} proteins\n"
        f"sequences read: {len(sequences)}"
        + (f", missing from fasta: {sorted(missing)}" if missing else "")
        + (f", not in table: {sorted(extra)}" if extra else "")
        + "\n"
    )
    sequences = {name: seq for name, seq in sequences.items() if name in in_table}

    names, identity = identity_matrix(sequences)
    upper = identity[np.triu_indices(len(names), k=1)]
    print(
        f"pairwise identity over {len(names)} proteins: median {np.median(upper):.2f}, "
        f"max {upper.max():.2f}; pairs above 0.30: {int((upper >= 0.30).sum())}, "
        f"above 0.40: {int((upper >= 0.40).sum())}\n"
    )

    family_of = (
        csv.drop_duplicates("LTPProtein").set_index("LTPProtein")["ProteinDomain"].to_dict()
    )
    family_labels = np.array(
        [sorted(set(family_of.values())).index(family_of[name]) for name in names]
    )
    fold_report(
        csv,
        names,
        identity,
        family_labels,
        "the nine annotated ProteinDomain families, as folds",
        positives_by_protein,
    )

    for threshold in [float(value) for value in arguments.thresholds.split(",") if value]:
        labels = clusters_at(identity, threshold)
        fold_report(
            csv,
            names,
            identity,
            labels,
            f"sequence-identity clusters at {threshold:.2f}, as folds",
            positives_by_protein,
        )


if __name__ == "__main__":
    main()
