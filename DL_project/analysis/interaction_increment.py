#!/usr/bin/env python3
"""Does the network add anything the chemistry null model does not already say?

files/interaction_signal_plan.md 3 establishes that neither AUC answers this on its own.
The pooled AUC is dominated by the chemical marginal -- "does this lipid bind anything" --
which a protein-blind predictor answers well. Ranking inside one protein removes the
protein marginal but not the lipid one: the null model ignores the protein entirely and
still reaches 0.586 there, because lipids that bind everything also bind this one.

So the question is not "which score is higher" but "does the network's score carry
anything ON TOP OF the chemistry score". Three readings, weakest evidence first:

1. AUC of each score alone, pooled and inside protein. Context, not the answer.

2. Increment, in-sample. Logistic regression of the label on the standardised chemistry
   score alone, then on chemistry plus the network score, both fitted on the held block
   itself, compared by AUC. Fitting on the block being scored is deliberate and its
   direction is known: it is an UPPER BOUND. A network that cannot beat chemistry even
   when its coefficient is fitted on the answers has nothing to contribute, and that is
   a conclusion the optimistic direction of the bias makes safe to draw.

3. Increment inside protein, with per-protein intercepts, which is the same regression
   with a(p) absorbed so only the pair term can move the fit.

Reads only: consumes checkpoint scores that already exist and trains nothing.

    scripts/env.sh python3 analysis/interaction_increment.py --scores scores.csv
    scripts/env.sh python3 analysis/interaction_increment.py --scores scores.csv --split test
"""

import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from analysis.chemistry_null_model import (  # noqa: E402
    DEFAULT_FAMILIES,
    WORKING,
    auc,
    null_scores,
    per_protein_auc,
    species_similarity,
    working_set,
)
from lipid_marginal_baseline import split as split_func  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import lipid_classes_for_holdout  # noqa: E402


def standardise(values):
    values = np.asarray(values, dtype=float)
    spread = values.std()
    return (values - values.mean()) / (spread if spread > 1e-12 else 1.0)


def logistic_auc(design, labels, groups=None, steps=400, learning_rate=0.5):
    """AUC of a logistic fit, optionally with one intercept per group.

    Plain gradient descent rather than a solver dependency: the designs here are at most
    a few columns over a few hundred rows, and separation is not a concern because the
    fit is only ever read as an AUC, never as a coefficient to interpret.
    """
    design = np.asarray(design, dtype=float)
    labels = np.asarray(labels, dtype=float)
    if groups is None:
        columns = [np.ones(len(labels))]
    else:
        codes = pandas.Categorical(groups).codes
        columns = [(codes == value).astype(float) for value in np.unique(codes)]
    matrix = np.column_stack(columns + [design[:, i] for i in range(design.shape[1])])
    weights = np.zeros(matrix.shape[1])
    for _ in range(steps):
        prediction = 1.0 / (1.0 + np.exp(-matrix @ weights))
        weights -= learning_rate * (matrix.T @ (prediction - labels)) / len(labels)
    return auc(labels, matrix @ weights)


def increment_table(csv, similarity, index, network, families, seeds, neighbours,
                     share=0.7, ratio=2, split="valid", epochs=None):
    """One row per (family, seed, epoch): the increment measurement.

    `network` is the RAW (unfiltered) scores DataFrame from
    analysis/checkpoint_scores.py; filtered here by `split`, matching
    null_model_table's contract in analysis/chemistry_null_model.py. `epochs=None`
    means every epoch present in `network`. Returns the table main() used to print --
    factored out so analysis/full_label_report.py can build it without a --scores
    CSV round-trip.
    """
    network = network[network["split"] == split]
    if epochs is None:
        epochs = sorted(network["epoch"].unique())

    rows = []
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, ratio, held_classes)
            train, valid, test = split_func(csvt, family, seed, held_classes, double=True)
            block = valid if split == "valid" else test
            chemistry = null_scores(
                train, block["FullIdentityOfLipid"], similarity, index, neighbours
            )
            for epoch in epochs:
                mine = network[
                    (network["fam"] == family)
                    & (network["seed"] == seed)
                    & (network["epoch"] == epoch)
                ]
                if len(mine) == 0:
                    continue
                if set(mine["pair_id"]) != set(block["pair_id"]):
                    raise SystemExit(
                        f"{family}/seed{seed}/epoch{epoch}: the split reproduced here "
                        "does not match the scored rows"
                    )
                merged = block.assign(_chem=chemistry).merge(
                    mine[["pair_id", "prob"]], on="pair_id", how="left", validate="one_to_one"
                )
                labels = merged["Interaction"].to_numpy()
                if len(set(labels)) < 2:
                    continue
                chem = standardise(merged["_chem"].to_numpy())
                net = standardise(merged["prob"].to_numpy())
                chem_prot, _ = per_protein_auc(merged, merged["_chem"].to_numpy())
                net_prot, proteins = per_protein_auc(merged, merged["prob"].to_numpy())
                rows.append({
                    "fam": family,
                    "seed": seed,
                    "epoch": epoch,
                    "proteins": proteins,
                    "chem": auc(labels, chem),
                    "net": auc(labels, net),
                    "chem_prot": chem_prot,
                    "net_prot": net_prot,
                    "fit_chem": logistic_auc(chem[:, None], labels),
                    "fit_chem_net": logistic_auc(np.column_stack([chem, net]), labels),
                    "fit_chem_prot": logistic_auc(
                        chem[:, None], labels, groups=merged["LTPProtein"]
                    ),
                    "fit_chem_net_prot": logistic_auc(
                        np.column_stack([chem, net]), labels, groups=merged["LTPProtein"]
                    ),
                })

    table = pandas.DataFrame(rows)
    table["increment"] = table["fit_chem_net"] - table["fit_chem"]
    table["increment_prot"] = table["fit_chem_net_prot"] - table["fit_chem_prot"]
    return table


def print_increment_report(table, split, neighbours):
    """The four-section printout main() used to produce, given a table from increment_table."""
    pandas.set_option("display.width", 220)
    print(f"=== {split} block, k={neighbours} ===\n")
    print("1. Each score on its own")
    alone = table.groupby("epoch")[["chem", "net", "chem_prot", "net_prot"]].mean()
    print(alone.round(3).to_string())

    print("\n2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)")
    print("   pooled, then with one intercept per protein")
    grown = table.groupby("epoch")[
        ["fit_chem", "fit_chem_net", "increment", "fit_chem_prot", "fit_chem_net_prot",
         "increment_prot"]
    ].mean()
    print(grown.round(3).to_string())

    print("\n3. Increment per family, last epoch")
    last = table[table["epoch"] == table["epoch"].max()]
    per_family = last.groupby("fam")[
        ["chem", "net", "chem_prot", "net_prot", "increment", "increment_prot"]
    ].mean()
    print(per_family.round(3).to_string())

    print("\n4. Never averaged over all seven at once (files/signal_state.md 6.4)")
    columns = ["chem", "net", "chem_prot", "net_prot", "increment", "increment_prot"]
    print(pandas.DataFrame({
        "all seven": last[columns].mean(),
        "working three": last[last["fam"].isin(WORKING)][columns].mean(),
        "other four": last[~last["fam"].isin(WORKING)][columns].mean(),
        "scp2 only": last[last["fam"] == "scp2"][columns].mean(),
    }).round(3).to_string())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", required=True, help="CSV from analysis/checkpoint_scores.py")
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--neighbours", type=int, default=15)
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--ratio", type=int, default=2)
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument("--epochs", default="", help="default: every epoch in the file")
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    similarity, index = species_similarity(csv, os.path.join(PROJECT_ROOT, "data"))
    network = pandas.read_csv(args.scores)

    table = increment_table(
        csv, similarity, index, network,
        families=[f for f in args.families.split(",") if f],
        seeds=[int(s) for s in args.seeds.split(",")],
        neighbours=args.neighbours, share=args.share, ratio=args.ratio, split=args.split,
        epochs=[int(e) for e in args.epochs.split(",") if e] or None,
    )
    print_increment_report(table, args.split, args.neighbours)


if __name__ == "__main__":
    main()
