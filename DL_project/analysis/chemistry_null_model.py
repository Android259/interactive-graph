#!/usr/bin/env python3
"""The chemistry-only null model for the doubly-cold block, and the network beside it.

The question this answers. `--double_coldsplit` leaves the held-out block with no lipid
that training ever saw, so the per-lipid label prior that used to carry the one-axis
split scores 0.500 by construction. That closes the *lookup* leak but not the weaker
one underneath it: a lipid the model has never seen can still resemble one it has, and
"resembles a training positive" is a prediction that needs no protein at all. Everything
the project is built to measure -- pocket, attention, pair -- lives above that line, so
the line has to be drawn before any number above it means anything.

The null model. For a row (protein p, lipid l) it ignores p entirely and scores l by the
similarity-weighted train positive rate of its k nearest training lipids, nearest by
Morgan-fingerprint Tanimoto (`data/Tanimoto_compact_isomeric_*`, the same artifacts the
loader's `--tanimoto_weight` uses). Held-out classes have no training rows whatsoever, so
every neighbour is necessarily from a different class -- this is extrapolation across
chemistry, not the class lookup the split already closed.

Reported as AUC, not balanced accuracy. At a fixed 0.5 threshold the null model scores
BA 0.512 while ranking the block at AUC 0.589: nearly all of its measured weakness is
threshold placement, and a comparison against a network at the same fixed threshold
would credit the network for a decision boundary rather than for information. AUC
compares what each one knows.

    python3 analysis/chemistry_null_model.py
    python3 analysis/chemistry_null_model.py --scores /tmp/scores_small27k.csv --epoch 120

With `--scores` (the CSV `analysis/checkpoint_scores.py` writes) the network's AUC is
computed on exactly the rows it was evaluated on, matched by `pair_id`, and the null
model is restricted to those same rows -- so the two numbers are the same measurement of
the same block and the difference between them is the network's own contribution.

Reads only. Trains nothing, appends to no shared table.
"""
import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from lipid_marginal_baseline import split  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    lipid_class_series,
    lipid_classes_for_holdout,
    split_and_sample_protein_balanced_interactions,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
# The three families whose validation sits above 0.5 in every dcs run, from
# files/signal_state.md section 4.1. Named here so the summary can report them apart:
# averaging across all seven hides both halves of the split.
WORKING = ("LBP_BPI_CETP", "scp2", "IP_trans")


def working_set(csv, seed, ratio, lipid_classes):
    """The loader's `csvt`, carrying the loader's `pair_id`.

    `lipid_marginal_baseline.working_set` builds the same rows in the same order but
    renumbers them 0..N-1 and keeps no trace of where they came from, and `pair_id` --
    the original row of the interaction table -- is assigned by
    `New_dataloader.__init__` *before* that renumbering. Matching rows against the
    scores `analysis/checkpoint_scores.py` writes needs that id, so the two lines are
    reproduced here rather than in the baseline, whose own numbers do not use it.
    """
    held = {name.lower() for name in lipid_classes}
    strata = lipid_class_series(csv).str.lower().isin(held) if held else None
    positives, negatives = split_and_sample_protein_balanced_interactions(
        csv, seed, ratio, strata
    )
    positives = positives.copy()
    negatives = negatives.copy()
    positives["pair_id"] = positives.index
    negatives["pair_id"] = negatives.index
    both = pandas.concat([positives, negatives])
    return both.set_index(pandas.Index(list(range(len(both)))))


def species_similarity(csv):
    """Species x species Tanimoto, max over each species' candidate structures.

    A row of the interaction table can list several isomer candidates, and the compact
    matrix is indexed per distinct structure; a species therefore owns a set of rows of
    it. Taking the max is the same reduction the loader applies when it turns candidate
    similarities into one number per pair.
    """
    data = os.path.join(PROJECT_ROOT, "data")
    matrix = np.load(
        os.path.join(data, "Tanimoto_compact_isomeric_matrix_uint8.npy")
    ).astype(np.float32) / 255.0
    structure_index = np.load(
        os.path.join(data, "Tanimoto_compact_isomeric_structure_index.npy")
    )
    row_ids = np.load(os.path.join(data, "Tanimoto_compact_isomeric_row_ids.npy"))

    structures_of_row = {}
    for row, structure in zip(row_ids, structure_index):
        structures_of_row.setdefault(int(row), set()).add(int(structure))
    structures_of_species = {}
    for position, species in enumerate(csv["FullIdentityOfLipid"]):
        structures_of_species.setdefault(species, set()).update(
            structures_of_row.get(position, set())
        )

    species = sorted(structures_of_species)
    index = {name: position for position, name in enumerate(species)}
    similarity = np.zeros((len(species), len(species)), dtype=np.float32)
    for position, name in enumerate(species):
        rows = matrix[sorted(structures_of_species[name]), :].max(axis=0)
        similarity[position] = [
            rows[sorted(structures_of_species[other])].max() for other in species
        ]
    return similarity, index


def auc(truth, score):
    """Rank-based AUC; nan when the block is single-class."""
    truth = np.asarray(truth)
    score = np.asarray(score, dtype=float)
    positives = truth.sum()
    negatives = len(truth) - positives
    if positives == 0 or negatives == 0:
        return float("nan")
    ranks = pandas.Series(score).rank().to_numpy()
    return float((ranks[truth == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def proximity_to_train_positives(train, held, similarity, index):
    """How close the block's positives sit to the nearest positive left in training.

    Mean over the block's positive rows of the highest Tanimoto to any lipid that is
    positive somewhere in train. This is the input the null model runs on, and it is
    also what predicts a run's sensitivity: below ~0.77 the model calls nothing
    positive on that family, above ~0.82 it calls roughly half. See section 7 of
    files/marginals_and_cold_split.md.
    """
    positives = train[train["Interaction"] == 1]["FullIdentityOfLipid"].unique()
    if len(positives) == 0:
        return float("nan")
    positive_positions = np.array([index[name] for name in positives])
    held_positives = held[held["Interaction"] == 1]["FullIdentityOfLipid"]
    if held_positives.empty:
        return float("nan")
    per_species = {
        name: float(similarity[index[name], positive_positions].max())
        for name in held_positives.unique()
    }
    return float(held_positives.map(per_species).mean())


def null_scores(train, held_species, similarity, index, neighbours):
    """Similarity-weighted train positive rate of the k nearest training lipids."""
    rate = train.groupby("FullIdentityOfLipid")["Interaction"].mean()
    train_positions = np.array([index[name] for name in rate.index])
    rates = rate.to_numpy()
    scores = []
    for name in held_species:
        similarities = similarity[index[name], train_positions]
        nearest = np.argsort(-similarities)[:neighbours]
        weights = np.clip(similarities[nearest], 0.0, None)
        scores.append(float((weights * rates[nearest]).sum() / max(weights.sum(), 1e-9)))
    return np.array(scores)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--neighbours", default="5,15,40", help="k, comma separated")
    parser.add_argument("--share", type=float, default=0.7, help="--coldsplit_share of the run")
    parser.add_argument("--ratio", type=int, default=2, help="--negatives_per_positive of the run")
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument(
        "--scores",
        help="CSV from analysis/checkpoint_scores.py; adds the network's AUC on the same rows",
    )
    parser.add_argument("--epoch", type=int, default=120, help="which checkpoint epoch to read")
    args = parser.parse_args()

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]
    neighbour_counts = [int(k) for k in args.neighbours.split(",")]

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    similarity, index = species_similarity(csv)

    network = None
    if args.scores:
        network = pandas.read_csv(args.scores)
        network = network[(network["epoch"] == args.epoch) & (network["split"] == args.split)]

    rows = []
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, args.share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, args.ratio, held_classes)
            train, valid, test = split(csvt, family, seed, held_classes, double=True)
            held = valid if args.split == "valid" else test

            record = {
                "fam": family,
                "seed": seed,
                "rows": len(held),
                "pos": int(held["Interaction"].sum()),
                "sim_to_train_pos": proximity_to_train_positives(
                    train, held, similarity, index
                ),
            }
            if network is not None:
                mine = network[(network["fam"] == family) & (network["seed"] == seed)]
                # The loader renumbers csvt 0..N-1 before splitting, and both sides of
                # this comparison carry that number, so equal pair_id sets mean the two
                # reproductions of the split agree row for row.
                if set(mine["pair_id"]) != set(held["pair_id"]):
                    raise SystemExit(
                        f"{family}/seed{seed}: split reproduced here does not match the scored rows"
                    )
                held = held.merge(
                    mine[["pair_id", "prob"]], on="pair_id", how="left", validate="one_to_one"
                )
                record["net_AUC"] = auc(held["Interaction"].to_numpy(), held["prob"].to_numpy())

            for neighbours in neighbour_counts:
                scores = null_scores(
                    train, held["FullIdentityOfLipid"], similarity, index, neighbours
                )
                record[f"null_AUC_k{neighbours}"] = auc(held["Interaction"].to_numpy(), scores)
            rows.append(record)

    table = pandas.DataFrame(rows)
    pandas.set_option("display.width", 200)
    print(f"=== {args.split} block, epoch {args.epoch} ===")
    print(table.round(3).to_string(index=False))
    print()
    by_family = table.groupby("fam").mean(numeric_only=True).drop(columns=["seed"])
    print("=== mean over seeds ===")
    print(by_family.round(3).to_string())
    print()
    columns = [c for c in table.columns if c.endswith("AUC") or "AUC_k" in c]
    working = table[table["fam"].isin(WORKING)]
    other = table[~table["fam"].isin(WORKING)]
    print("=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===")
    print(pandas.DataFrame({
        "all seven": table[columns].mean(),
        "working three": working[columns].mean(),
        "other four": other[columns].mean(),
    }).round(3).to_string())


if __name__ == "__main__":
    main()
