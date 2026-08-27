#!/usr/bin/env python3
"""What a run's held-out AUC still has after every known shortcut is subtracted.

The problem this solves. A held-out number is not a claim about the pair until you know
what could have produced it WITHOUT the pair. This project has found four such routes,
one at a time, each in its own note and each with its own script:

  the lipid lookup      the train positive rate of this exact lipid
                        (files/marginals_and_cold_split.md 2 -- 0.564 on the one-axis
                        split, closed to 0.500 by --double_coldsplit)
  the class lookup      the same, by head-group class (0.562, closed the same way)
  chemistry             the similarity-weighted positive rate of the nearest train
                        lipids (files/marginals_and_cold_split.md 8.2 -- 0.565, NOT
                        closed by any split, because chemical extrapolation is not a
                        lookup)
  chain length          the longest acyl chain (files/compat_input_audit.md 1.1 -- 0.579
                        inside protein, not closed either: the split holds out head-group
                        classes, and chain length is orthogonal to those)

Every one of them ignores the protein, or ignores the lipid, and none of them is what the
model exists to learn. `analysis/interaction_increment.py` subtracts the third; this
subtracts all of them at once, and any future one by adding a line to SHORTCUTS.

What it reports:

  each shortcut alone, pooled and inside protein -- context, and a running check that the
      ones a split claims to have closed really do sit at 0.500
  the stack, fitted in-sample -- everything jointly obtainable without the pair. This is
      the honest reference point, and it is deliberately generous: fitting the
      coefficients on the block being scored makes it an UPPER bound on the shortcut, so
      the network's increment over it is a LOWER bound on the network. A network that
      still adds something against a reference point tuned on the answers has added it.
  the network's increment over the stack, and its share of the total lift -- pooled and
      with one intercept per protein.

The share is reported against two different denominators because they answer different
questions and a single "share of the gain" hides which one is meant:

  share_over_stack   increment / (fitted stack + network - fitted stack alone), i.e. how
                     much of what the model beats the shortcuts by is its own
  share_over_chance  (network AUC - 0.5) split into the part a shortcut reproduces and
                     the part it does not

Reads only. Trains nothing, appends to no shared table.

    scripts/env.sh python3 analysis/shortcut_increment.py --label <label>
    scripts/env.sh python3 analysis/shortcut_increment.py --label <label> --split test
    scripts/env.sh python3 analysis/shortcut_increment.py --label <label> \\
        --shortcuts=chem,chain,extent
    # the shortcut stack on its own, no checkpoints and no label needed
    scripts/env.sh python3 analysis/shortcut_increment.py --shortcuts_only
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
from dataloader.sampler import lipid_class_series, lipid_classes_for_holdout  # noqa: E402


# Every route to a held-out score that does not need the pair. Order is the order they
# are added to the design matrix, which only affects the printed running total.
SHORTCUTS = ("lipid_prior", "class_prior", "chem", "chain", "extent")
DEFAULT_SHORTCUTS = ("chem", "chain")


def group_positive_rate(train, held, key_train, key_held):
    """Train positive rate of each group, mapped onto the held block.

    A group the block has and training does not falls back to the overall train
    positive rate -- the honest "no information" answer, and the one that makes this
    score exactly 0.500-uninformative on a split that removed the group entirely, which
    is what --double_coldsplit is supposed to do and what this then verifies.
    """
    rate = train.groupby(key_train)["Interaction"].mean()
    overall = float(train["Interaction"].mean()) if len(train) else 0.5
    return key_held.map(rate).fillna(overall).to_numpy(dtype=float)


def shortcut_columns(names, train, held, similarity, index, neighbours,
                      lengths, extents, classes):
    """name -> per-row values for the held block, oriented so larger means more likely 1."""
    built = {}
    for name in names:
        if name == "lipid_prior":
            built[name] = group_positive_rate(
                train, held, train["FullIdentityOfLipid"], held["FullIdentityOfLipid"]
            )
        elif name == "class_prior":
            # By pair_id, never by .index: working_set renumbers its rows 0..N-1, so
            # `classes.loc[train.index]` would silently read whichever rows of the
            # original table happen to sit at those positions. It does not fail, it
            # returns a structured wrong answer -- 0.172 pooled, which looks like a
            # finding rather than a bug.
            built[name] = group_positive_rate(
                train, held,
                classes.loc[train["pair_id"]].to_numpy(),
                pandas.Series(classes.loc[held["pair_id"]].to_numpy(), index=held.index),
            )
        elif name == "chem":
            built[name] = null_scores(
                train, held["FullIdentityOfLipid"], similarity, index, neighbours
            )
        elif name == "chain":
            chain = held["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
            train_chain = train["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
            built[name] = -np.where(np.isnan(chain), np.nanmean(train_chain), chain)
        elif name == "extent":
            built[name] = held["LTPProtein"].map(extents).to_numpy(dtype=float)
        else:
            raise SystemExit(f"unknown shortcut {name!r}; known: {', '.join(SHORTCUTS)}")
    return built


def shortcut_table(csv, similarity, index, lengths, extents, classes, network, names,
                    families, seeds, neighbours=15, share=0.7, ratio=2, split="valid",
                    epoch=None):
    """One row per (family, seed): every shortcut, the stack, and the network beside it."""
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

            built = shortcut_columns(
                names, train, block, similarity, index, neighbours, lengths, extents,
                classes,
            )
            record = {"fam": family, "seed": seed, "rows": len(block),
                      "pos": int(labels.sum())}
            for name, values in built.items():
                record[name] = auc(labels, values)
                record[f"{name}_prot"], record["proteins"] = per_protein_auc(block, values)

            groups = block["LTPProtein"]
            stack = np.column_stack([standardise(built[n]) for n in names])
            record["stack"] = logistic_auc(stack, labels)
            record["stack_prot"] = logistic_auc(stack, labels, groups=groups)

            if network is not None:
                mine = network[(network["fam"] == family) & (network["seed"] == seed)]
                if len(mine) == 0:
                    continue
                if set(mine["pair_id"]) != set(block["pair_id"]):
                    raise SystemExit(
                        f"{family}/seed{seed}: the split reproduced here does not match "
                        "the scored rows"
                    )
                merged = block.merge(
                    mine[["pair_id", "prob"]], on="pair_id", how="left",
                    validate="one_to_one",
                )
                net_raw = merged["prob"].to_numpy()
                labels = merged["Interaction"].to_numpy()
                groups = merged["LTPProtein"]
                with_net = np.column_stack([stack, standardise(net_raw)])
                record["net"] = auc(labels, net_raw)
                record["net_prot"], _ = per_protein_auc(merged, net_raw)
                record["stack_net"] = logistic_auc(with_net, labels)
                record["stack_net_prot"] = logistic_auc(with_net, labels, groups=groups)
            rows.append(record)

    table = pandas.DataFrame(rows)
    if "stack_net" in table.columns:
        table["increment"] = table["stack_net"] - table["stack"]
        table["increment_prot"] = table["stack_net_prot"] - table["stack_prot"]
        # Share of what the model beats chance by that no shortcut reproduces. The
        # denominators are clipped away from zero rather than left to divide: a family
        # whose stack already sits at chance would otherwise produce a share of
        # thousands and drag every mean it enters.
        def share(net, stack):
            lift = np.maximum(net - 0.5, 1e-6)
            return np.clip((net - stack) / lift, -1.0, 1.0)
        table["share_own"] = share(table["net"], table["stack"])
        table["share_own_prot"] = share(table["net_prot"], table["stack_prot"])
    return table


def print_shortcut_report(table, split, names, label=None):
    pandas.set_option("display.width", 240)
    print(f"\n=== {split} block" + (f", {label}" if label else "") + " ===")
    print(f"shortcut stack : {', '.join(names)}\n")

    pooled = list(names) + ["stack"] + (["net"] if "net" in table.columns else [])
    inside = [f"{n}_prot" for n in names] + ["stack_prot"] + (
        ["net_prot"] if "net_prot" in table.columns else []
    )

    print("1. Pooled AUC, per family (mean over seeds)")
    print(table.groupby("fam")[pooled].mean().round(3).to_string())
    print("\n2. Inside protein, per family")
    print(table.groupby("fam")[inside].mean().round(3).to_string())

    def grouped(columns):
        return pandas.DataFrame({
            "all seven": table[columns].mean(),
            "working three": table[table["fam"].isin(WORKING)][columns].mean(),
            "other four": table[~table["fam"].isin(WORKING)][columns].mean(),
            "scp2 only": table[table["fam"] == "scp2"][columns].mean(),
        }).round(3)

    print("\n3. Grouped -- never one average over all seven (files/signal_state.md 6.4)")
    print(grouped(pooled + inside).to_string())

    if "increment" not in table.columns:
        print()
        return

    print("\n4. What the network adds over the whole stack")
    print("   stack is fitted in-sample = UPPER bound on the shortcut, so the")
    print("   increment is a LOWER bound on the network")
    print(grouped(["stack", "stack_net", "increment",
                   "stack_prot", "stack_net_prot", "increment_prot"]).to_string())

    print("\n5. Share of the model's lift over chance that no shortcut reproduces")
    print(grouped(["share_own", "share_own_prot"]).to_string())
    print("\n   per family, inside protein")
    print(table.groupby("fam")[
        ["net_prot", "stack_prot", "increment_prot", "share_own_prot"]
    ].mean().round(3).to_string())
    print()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--label", help="sweep label; omit with --shortcuts_only")
    parser.add_argument(
        "--shortcuts_only", action="store_true",
        help="measure the stack alone -- no checkpoints, no label needed",
    )
    parser.add_argument(
        "--shortcuts", default=",".join(DEFAULT_SHORTCUTS),
        help=f"comma separated, from: {', '.join(SHORTCUTS)}",
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

    if not args.shortcuts_only and not (args.label or args.scores):
        parser.error("give --label or --scores, or pass --shortcuts_only")

    names = tuple(n.strip() for n in args.shortcuts.split(",") if n.strip())
    unknown = [n for n in names if n not in SHORTCUTS]
    if unknown or not names:
        parser.error(f"--shortcuts must name some of {', '.join(SHORTCUTS)}")

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]
    splits = ("valid", "test") if args.split == "both" else (args.split,)

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    similarity, index = species_similarity(csv, os.path.join(PROJECT_ROOT, "data"))
    lengths = chain_length_by_species(csv) if "chain" in names else {}
    extents = (
        pocket_extent_by_protein(
            data_dir, sorted(csv["LTPProtein"].dropna().unique().tolist())
        )
        if "extent" in names else {}
    )
    classes = lipid_class_series(csv)

    network = None
    if not args.shortcuts_only:
        if args.scores:
            network = pandas.read_csv(args.scores)
        else:
            from checkpoint_scores import score_checkpoints

            network = score_checkpoints(
                args.label, epochs=[args.epoch], seeds=seeds, families=families,
            )
            if args.out:
                network.to_csv(args.out, index=False)
                print(f"wrote : {args.out}")

    for split in splits:
        table = shortcut_table(
            csv, similarity, index, lengths, extents, classes, network, names,
            families=families, seeds=seeds, neighbours=args.neighbours,
            share=args.share, ratio=args.ratio, split=split, epoch=args.epoch,
        )
        print_shortcut_report(table, split, names, args.label)


if __name__ == "__main__":
    main()
