#!/usr/bin/env python3
"""What the pocket/chain compatibility feature contributes, and what the network adds on top.

Why this exists. `--pocket_compat_prior` and `--compatibility_input` both hand the model
`compatibility(p, l) = pocket_extent(p) - chain_length(l)`
(files/pocket_lipid_compatibility.md), and both lift the held-out AUC a long way above the
base run. `analysis/interaction_increment.py` cannot say whether that lift is a pair term,
because it only ever asks "does the network add anything over CHEMISTRY" -- and the
compatibility feature is not chemistry. A network handed a strong feature and asked to
beat a baseline that was not handed it will win without having learned anything.

The observation that makes this worth measuring separately: inside one protein
`pocket_extent(p)` is a CONSTANT, so within-protein the compatibility feature is exactly
`-chain_length(l)` -- a lipid-only quantity, with no pair term in it at all. Whatever a
within-protein AUC gains from this feature is therefore a chain-length marginal, in the
same sense that `analysis/null_model.py`'s null model is a chemistry marginal,
and files/interaction_signal_plan.md 3.4 already warns that within-protein AUC is not a
clean pair measurement for exactly this reason.

So the design matrix grows by one column, and the questions become three instead of one:

1. `compat` alone -- AUC of the feature with no network at all, pooled and inside
   protein. `chain` alone is reported beside it; the two are identical inside protein by
   the argument above, which is also a check that nothing is wired wrong.
2. `fit_chem_compat` -- chemistry AND the feature, both fitted in-sample. This is the
   honest baseline for a run that was given the feature: everything obtainable from the
   two quantities the model did not have to learn.
3. `increment_over_both` -- what the network's score adds on top of THAT. This is the
   number that says whether the network learned a pair term or is re-expressing its
   input. Same in-sample fit as interaction_increment.py, so the same caveat applies and
   points the same way: fitting on the block being scored is an UPPER BOUND, and a
   network that adds nothing even with a coefficient fitted on the answers has nothing.

Reads only. Trains nothing, appends to no shared table.

    scripts/env.sh python3 analysis/compatibility_probe.py --label <label>
    scripts/env.sh python3 analysis/compatibility_probe.py --label <label> --split test
    # the feature on its own, no checkpoints needed and no label required
    scripts/env.sh python3 analysis/compatibility_probe.py --feature_only

`--scores` reuses a CSV analysis/checkpoint_scores.py already wrote; `--out` saves the
one this run produces, which is what makes a second question about the same label cheap.
"""
import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from analysis.null_model import (  # noqa: E402
    DEFAULT_FAMILIES,
    WORKING,
    auc,
    null_scores,
    per_protein_auc,
    species_similarity,
    working_set,
)
from analysis.interaction_increment import logistic_auc, standardise  # noqa: E402
from lipid_marginal_baseline import split as split_func  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pocket_lipid_compatibility import (  # noqa: E402
    chain_length_by_species,
    pocket_extent_by_protein,
)
from dataloader.sampler import lipid_classes_for_holdout  # noqa: E402


def compatibility_columns(csv, data_dir):
    """`chain_length` per species and `pocket_extent` per protein, computed once.

    The loader recomputes these per family/seed inside `raw_compatibility`; both are
    functions of the interaction table and the pocket PDBs alone, identical across
    splits, so a probe that walks fourteen splits computes them once instead.
    """
    lengths = chain_length_by_species(csv)
    extents = pocket_extent_by_protein(
        data_dir, sorted(csv["LTPProtein"].dropna().unique().tolist())
    )
    return lengths, extents


def block_features(block, train, lengths, extents):
    """`(compat, chain)` for one held-out block, missing chain lengths filled from train.

    The fill is the train mean, matching `_compute_compatibility_input` in
    dataloader/Dataloader.py -- on this table no row needs it (all 312 species
    parse), but a probe that silently differed from the loader on the one path that is
    hard to notice would be worse than useless.
    """
    chain = block["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
    extent = block["LTPProtein"].map(extents).to_numpy(dtype=float)
    train_chain = train["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
    train_extent = train["LTPProtein"].map(extents).to_numpy(dtype=float)
    chain = np.where(np.isnan(chain), np.nanmean(train_chain), chain)
    compat = extent - chain
    compat = np.where(np.isnan(compat), np.nanmean(train_extent - train_chain), compat)
    return compat, chain


def probe_table(csv, similarity, index, lengths, extents, network, families, seeds,
                 neighbours=15, share=0.7, ratio=2, split="valid", epoch=None):
    """One row per (family, seed): every AUC and every in-sample fit, side by side.

    `network=None` runs the feature-only half -- no checkpoints, no label, and the
    `net`/`increment` columns are simply absent rather than filled with nan, so a caller
    cannot average them by accident.
    """
    if network is not None:
        network = network[network["split"] == split]
        if epoch is not None:
            network = network[network["epoch"] == epoch]

    rows = []
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, ratio, held_classes)
            train, valid, test = split_func(csvt, family, seed, held_classes, double=True)
            block = valid if split == "valid" else test
            labels = block["Interaction"].to_numpy()
            if len(set(labels)) < 2:
                continue

            chemistry = null_scores(
                train, block["FullIdentityOfLipid"], similarity, index, neighbours
            )
            compat, chain = block_features(block, train, lengths, extents)

            record = {
                "fam": family, "seed": seed, "rows": len(block),
                "pos": int(labels.sum()),
                "chem": auc(labels, chemistry),
                "compat": auc(labels, compat),
                "chain": auc(labels, -chain),
            }
            record["chem_prot"], _ = per_protein_auc(block, chemistry)
            record["compat_prot"], record["proteins"] = per_protein_auc(block, compat)
            record["chain_prot"], _ = per_protein_auc(block, -chain)

            chem_s = standardise(chemistry)
            compat_s = standardise(compat)
            groups = block["LTPProtein"]
            record["fit_chem"] = logistic_auc(chem_s[:, None], labels)
            record["fit_chem_compat"] = logistic_auc(
                np.column_stack([chem_s, compat_s]), labels
            )
            record["fit_chem_prot"] = logistic_auc(chem_s[:, None], labels, groups=groups)
            record["fit_chem_compat_prot"] = logistic_auc(
                np.column_stack([chem_s, compat_s]), labels, groups=groups
            )

            if network is not None:
                mine = network[
                    (network["fam"] == family) & (network["seed"] == seed)
                ]
                if len(mine) == 0:
                    continue
                if set(mine["pair_id"]) != set(block["pair_id"]):
                    raise SystemExit(
                        f"{family}/seed{seed}: the split reproduced here does not match "
                        "the scored rows"
                    )
                merged = block.assign(_c=chemistry, _k=compat).merge(
                    mine[["pair_id", "prob"]], on="pair_id", how="left",
                    validate="one_to_one",
                )
                labels = merged["Interaction"].to_numpy()
                net_raw = merged["prob"].to_numpy()
                net_s = standardise(net_raw)
                chem_s = standardise(merged["_c"].to_numpy())
                compat_s = standardise(merged["_k"].to_numpy())
                groups = merged["LTPProtein"]
                record["net"] = auc(labels, net_raw)
                record["net_prot"], _ = per_protein_auc(merged, net_raw)
                # How much of the network's own score is the feature read back out.
                record["corr_net_compat"] = float(
                    np.corrcoef(net_s, compat_s)[0, 1]
                )
                record["fit_chem_net"] = logistic_auc(
                    np.column_stack([chem_s, net_s]), labels
                )
                record["fit_all"] = logistic_auc(
                    np.column_stack([chem_s, compat_s, net_s]), labels
                )
                record["fit_chem_net_prot"] = logistic_auc(
                    np.column_stack([chem_s, net_s]), labels, groups=groups
                )
                record["fit_all_prot"] = logistic_auc(
                    np.column_stack([chem_s, compat_s, net_s]), labels, groups=groups
                )
            rows.append(record)

    table = pandas.DataFrame(rows)
    table["compat_over_chem"] = table["fit_chem_compat"] - table["fit_chem"]
    table["compat_over_chem_prot"] = (
        table["fit_chem_compat_prot"] - table["fit_chem_prot"]
    )
    if "fit_all" in table.columns:
        table["net_over_chem"] = table["fit_chem_net"] - table["fit_chem"]
        table["net_over_both"] = table["fit_all"] - table["fit_chem_compat"]
        table["net_over_chem_prot"] = (
            table["fit_chem_net_prot"] - table["fit_chem_prot"]
        )
        table["net_over_both_prot"] = (
            table["fit_all_prot"] - table["fit_chem_compat_prot"]
        )
    return table


def print_probe_report(table, split, label=None):
    """Three sections: scores alone, the fits, and the increment that matters."""
    pandas.set_option("display.width", 240)
    header = f"=== {split} block" + (f", {label}" if label else "") + " ==="
    print(header)

    alone = ["chem", "compat", "chain", "chem_prot", "compat_prot", "chain_prot"]
    if "net" in table.columns:
        alone = ["chem", "compat", "chain", "net",
                 "chem_prot", "compat_prot", "chain_prot", "net_prot"]
    print("\n1. Each score on its own, per family (mean over seeds)")
    print(table.groupby("fam")[alone].mean().round(3).to_string())

    print("\n2. Grouped -- never one average over all seven (files/signal_state.md 6.4)")
    print(pandas.DataFrame({
        "all seven": table[alone].mean(),
        "working three": table[table["fam"].isin(WORKING)][alone].mean(),
        "other four": table[~table["fam"].isin(WORKING)][alone].mean(),
        "scp2 only": table[table["fam"] == "scp2"][alone].mean(),
    }).round(3).to_string())

    print("\n3. In-sample fits (UPPER BOUND, fitted on the block being scored)")
    fits = ["fit_chem", "fit_chem_compat", "fit_chem_prot", "fit_chem_compat_prot",
            "compat_over_chem", "compat_over_chem_prot"]
    if "fit_all" in table.columns:
        fits = ["fit_chem", "fit_chem_compat", "fit_chem_net", "fit_all",
                "fit_chem_prot", "fit_chem_compat_prot", "fit_chem_net_prot",
                "fit_all_prot"]
    print(pandas.DataFrame({
        "all seven": table[fits].mean(),
        "working three": table[table["fam"].isin(WORKING)][fits].mean(),
        "other four": table[~table["fam"].isin(WORKING)][fits].mean(),
        "scp2 only": table[table["fam"] == "scp2"][fits].mean(),
    }).round(3).to_string())

    if "net_over_both" in table.columns:
        print("\n4. THE question: what the network adds, over chemistry alone and over")
        print("   chemistry PLUS the feature it was handed")
        increments = ["net_over_chem", "net_over_both",
                      "net_over_chem_prot", "net_over_both_prot", "corr_net_compat"]
        print(pandas.DataFrame({
            "all seven": table[increments].mean(),
            "working three": table[table["fam"].isin(WORKING)][increments].mean(),
            "other four": table[~table["fam"].isin(WORKING)][increments].mean(),
            "scp2 only": table[table["fam"] == "scp2"][increments].mean(),
        }).round(3).to_string())
        print("\n   per family")
        print(table.groupby("fam")[increments].mean().round(3).to_string())
    else:
        print("\n4. The feature's own increment over chemistry, per family")
        print(table.groupby("fam")[
            ["compat_over_chem", "compat_over_chem_prot"]
        ].mean().round(3).to_string())
    print()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--label", help="sweep label; omit with --feature_only")
    parser.add_argument(
        "--feature_only", action="store_true",
        help="measure the feature alone -- no checkpoints, no label needed",
    )
    parser.add_argument("--scores", help="reuse a CSV from analysis/checkpoint_scores.py")
    parser.add_argument("--out", help="save the scores this run produces")
    parser.add_argument("--epoch", type=int, default=120)
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--neighbours", type=int, default=15)
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--ratio", type=int, default=2)
    parser.add_argument("--split", default="valid", choices=("valid", "test", "both"))
    args = parser.parse_args()

    if not args.feature_only and not (args.label or args.scores):
        parser.error("give --label or --scores, or pass --feature_only")

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]
    splits = ("valid", "test") if args.split == "both" else (args.split,)

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    similarity, index = species_similarity(csv, os.path.join(PROJECT_ROOT, "data"))
    lengths, extents = compatibility_columns(csv, data_dir)

    parsed = sum(1 for value in lengths.values() if value is not None)
    print(f"chain length : {parsed}/{len(lengths)} species parsed")
    print(f"pocket extent : {len(extents)} proteins\n")

    network = None
    if not args.feature_only:
        if args.scores:
            network = pandas.read_csv(args.scores)
        else:
            from checkpoint_scores import score_checkpoints

            network = score_checkpoints(
                args.label, epochs=[args.epoch], seeds=seeds, families=families,
            )
            if args.out:
                network.to_csv(args.out, index=False)
                print(f"wrote : {args.out}\n")

    for split in splits:
        table = probe_table(
            csv, similarity, index, lengths, extents, network,
            families=families, seeds=seeds, neighbours=args.neighbours,
            share=args.share, ratio=args.ratio, split=split, epoch=args.epoch,
        )
        print_probe_report(table, split, args.label)


if __name__ == "__main__":
    main()
