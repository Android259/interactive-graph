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

from analysis.null_model import (  # noqa: E402
    DEFAULT_FAMILIES,
    TANIMOTO,
    _group_stats,
    auc,
    null_scores,
    per_lipid_auc,
    per_pair_auc,
    per_protein_auc,
    resolve_similarity,
    working_set,
)
from lipid_marginal_baseline import split as split_func  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import lipid_class_series, lipid_classes_for_holdout  # noqa: E402


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
                     share=0.7, ratio=2, split="valid", epochs=None,
                     entity_column="FullIdentityOfLipid"):
    """One row per (family, seed, epoch): the increment measurement.

    `network` is the RAW (unfiltered) scores DataFrame from
    analysis/checkpoint_scores.py; filtered here by `split`, matching
    null_model_table's contract in analysis/null_model.py. `epochs=None`
    means every epoch present in `network`. `entity_column` must match whatever
    `similarity`/`index` are keyed by -- see
    dataloader.chemistry_prior.feature_similarity/null_model.
    resolve_similarity. Returns the table main() used to print -- factored out so
    analysis/full_label_report.py can build it without a --scores CSV round-trip.
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
            # per_lipid_auc's default grouping -- attached once here so every epoch's
            # merge (below) carries it, same as null_model_table does for `held`.
            block = block.assign(lipid_class=lipid_class_series(block))
            chemistry = null_scores(
                train, block[entity_column], similarity, index, neighbours, entity_column
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
                # prot/lipid/pair all computed unconditionally, regardless of
                # entity_column -- cheap either way, and which of prot/lipid is
                # mechanically degenerate (always exactly 0.5, see per_protein_auc/
                # per_lipid_auc) depends on entity_column, so print_increment_report
                # decides which to show rather than this function guessing on its
                # behalf -- same split of responsibility as null_model_table/
                # print_null_model_report.
                chem_prot, _ = per_protein_auc(merged, merged["_chem"].to_numpy())
                net_prot, proteins = per_protein_auc(merged, merged["prob"].to_numpy())
                chem_lipid, _ = per_lipid_auc(merged, merged["_chem"].to_numpy())
                net_lipid, lipids = per_lipid_auc(merged, merged["prob"].to_numpy())
                rows.append({
                    "fam": family,
                    "seed": seed,
                    "epoch": epoch,
                    "proteins": proteins,
                    "lipids": lipids,
                    "chem": auc(labels, chem),
                    "net": auc(labels, net),
                    "chem_prot": chem_prot,
                    "net_prot": net_prot,
                    "chem_lipid": chem_lipid,
                    "net_lipid": net_lipid,
                    "chem_pair": per_pair_auc(merged, merged["_chem"].to_numpy()),
                    "net_pair": per_pair_auc(merged, merged["prob"].to_numpy()),
                    "fit_chem": logistic_auc(chem[:, None], labels),
                    "fit_chem_net": logistic_auc(np.column_stack([chem, net]), labels),
                    "fit_chem_prot": logistic_auc(
                        chem[:, None], labels, groups=merged["LTPProtein"]
                    ),
                    "fit_chem_net_prot": logistic_auc(
                        np.column_stack([chem, net]), labels, groups=merged["LTPProtein"]
                    ),
                    "fit_chem_lipid": logistic_auc(
                        chem[:, None], labels, groups=merged["lipid_class"]
                    ),
                    "fit_chem_net_lipid": logistic_auc(
                        np.column_stack([chem, net]), labels, groups=merged["lipid_class"]
                    ),
                })

    table = pandas.DataFrame(rows)
    table["increment"] = table["fit_chem_net"] - table["fit_chem"]
    table["increment_prot"] = table["fit_chem_net_prot"] - table["fit_chem_prot"]
    table["increment_lipid"] = table["fit_chem_net_lipid"] - table["fit_chem_lipid"]
    return table


def print_increment_report(table, split, neighbours, entity_column="FullIdentityOfLipid"):
    """The printout main()/full_label_report.py use, given a table from increment_table --
    same reporting shape as null_model.py's print_null_model_report (mean over seeds
    per family, then mean/median/std over all seven at once, no WORKING-three/
    other-four split -- see files/signal_state.md 6.4 and null_model.py's own
    _group_stats), plus the within-entity rankings (per_protein_auc/per_lipid_auc)
    and per_pair_auc, gated by `entity_column` exactly the way null_model.py's report
    would gate them for the SAME similarity/index/entity_column increment_table was
    given (chem_prot/chem_lipid here are built from that same null model, so they are
    degenerate under the identical condition null_AUC_prot_k*/null_AUC_lipid_k* are).
    net_prot/net_lipid are never degenerate -- the network sees both axes regardless
    of the null model's own granularity -- so they print whenever their group does.

    Unlike null_model.py's report, `table` also carries an epoch axis (this project's
    saved dynamics checkpoints): sections 1-2 keep that axis (mean over family+seed,
    one row per epoch, the trajectory); sections from 3 on fix it at the LAST epoch,
    the same checkpoint build_rand_results_tables.py/full_label_report.py otherwise
    report at.
    """
    pandas.set_option("display.width", 220)
    is_pair = entity_column == "pair_id"
    show_prot = entity_column != "LTPProtein" and not is_pair
    show_lipid = entity_column != "FullIdentityOfLipid" and not is_pair
    show_pair = is_pair

    alone_cols = ["chem", "net"]
    grown_cols = ["fit_chem", "fit_chem_net", "increment"]
    prot_cols = ["chem_prot", "net_prot", "fit_chem_prot", "fit_chem_net_prot", "increment_prot"]
    lipid_cols = [
        "chem_lipid", "net_lipid", "fit_chem_lipid", "fit_chem_net_lipid", "increment_lipid",
    ]
    pair_cols = ["chem_pair", "net_pair"]
    if show_prot:
        alone_cols += prot_cols[:2]
        grown_cols += prot_cols[2:]
    if show_lipid:
        alone_cols += lipid_cols[:2]
        grown_cols += lipid_cols[2:]
    if show_pair:
        alone_cols += pair_cols

    print(f"=== {split} block, k={neighbours}, null-model entity = {entity_column} ===\n")
    print("1. Each score on its own, mean over family+seed, by epoch")
    print(table.groupby("epoch")[alone_cols].mean().round(3).to_string())

    print(
        "\n2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), "
        "mean over family+seed, by epoch"
    )
    print(table.groupby("epoch")[grown_cols].mean().round(3).to_string())

    last_epoch = int(table["epoch"].max())
    last = table[table["epoch"] == last_epoch]
    print(f"\n3. mean over seeds, epoch {last_epoch}")
    print(last.groupby("fam")[alone_cols + grown_cols].mean().round(3).to_string())

    print(
        f"\n=== mean AUC + increment, epoch {last_epoch} (files/signal_state.md 6.4: "
        "fam column in the raw table carries the WORKING-three/other-four split) ==="
    )
    pooled_cols = ["chem", "net", "fit_chem", "fit_chem_net", "increment"]
    print(_group_stats({"all seven": last}, pooled_cols).round(3).to_string())

    def within_entity(header, count_col, columns):
        print(f"\n=== the same rows ranked INSIDE each {header}, epoch {last_epoch} ===")
        if count_col is not None:
            print(f"{int(last[count_col].sum())} {header} blocks across {len(last)} "
                  f"family-seed splits carry a usable ranking "
                  f"(median {last[count_col].median():.0f} {header} groups per split)")
        print(_group_stats({"all seven": last}, columns).round(3).to_string())

    if show_prot:
        within_entity("protein", "proteins", prot_cols)
    if show_lipid:
        # "lipid class" (dataloader.lipid_classes.lipid_class_series), not species --
        # see null_model.py's per_lipid_auc docstring for why species-level grouping
        # is structurally unusable on this dataset's split shape.
        within_entity("lipid class", "lipids", lipid_cols)
    if show_pair:
        within_entity(
            "protein AND inside each lipid class jointly (per_pair_auc)", None, pair_cols
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", required=True, help="CSV from analysis/checkpoint_scores.py")
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--neighbours", type=int, default=15)
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--ratio", type=int, default=2)
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument("--epochs", default="", help="default: every epoch in the file")
    parser.add_argument(
        "--features", default=TANIMOTO,
        help=(
            f'"{TANIMOTO}" (default): full-structure Morgan-fingerprint similarity, '
            "the original null model. Otherwise a comma-separated descriptor-name "
            "list -- lipid-only, protein-only, pair, or any combination -- see "
            "null_model.py --features. analysis/full_label_report.py resolves this "
            "automatically off a label's own --good_descriptors/--bad_descriptors "
            "when called via --label instead of --scores."
        ),
    )
    parser.add_argument("--features-label", help="short name for --features, see null_model.py --label")
    parser.add_argument(
        "--zscore", action="store_true",
        help="see null_model.py --zscore -- standardises the six multiplicative pair descriptors",
    )
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    similarity, index, entity_column, _, _ = resolve_similarity(
        csv, os.path.join(PROJECT_ROOT, "data"), args.features, args.features_label,
        zscore=args.zscore,
    )
    network = pandas.read_csv(args.scores)

    table = increment_table(
        csv, similarity, index, network,
        families=[f for f in args.families.split(",") if f],
        seeds=[int(s) for s in args.seeds.split(",")],
        neighbours=args.neighbours, share=args.share, ratio=args.ratio, split=args.split,
        epochs=[int(e) for e in args.epochs.split(",") if e] or None,
        entity_column=entity_column,
    )
    print_increment_report(table, args.split, args.neighbours, entity_column=entity_column)


if __name__ == "__main__":
    main()
