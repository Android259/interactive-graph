#!/usr/bin/env python3
"""What a no-training competitor scores on a --lipid_coldsplit block, from any features.

The check files/lipid_coldsplit_architecture_direction.md section 6.1 says has never
run. Every lipid-cold-split number the project has is read against 0.500, which is the
per-lipid label prior and is 0.500 there by construction (no evaluated lipid's class is
in training, so the lookup always falls back). That is a very weak bar. This builds the
competitor that is actually worth beating.

Two competitors, both trained on nothing, both scored on the same held-out rows the
network is scored on:

  lipid_only    For a held row (P, L), how often were the training lipids most similar
                to L bound -- by ANYBODY. Ignores P entirely, so two held rows sharing a
                lipid get the same score. Answers: is the signal in the chemistry alone?

  within_protein  The same, restricted to P's own training rows: did THIS protein bind
                the lipids most like L. The stronger of the two and the one a network
                has to beat before "it learned the pair" means anything, since the
                network also sees both sides.

Read as a pair. lipid_only high and within_protein not: the chemistry carries it and the
protein adds nothing. The reverse: the pairing matters. Both at chance: neither is enough
on this split, and a network above them is doing something neither does.

Similarity comes from --features and can be ANY lipid feature vector, not only chemical
fingerprints: the literal "tanimoto" (Morgan fingerprints over the whole structure), or
any comma-separated subset of LIPID_DESCRIPTOR_NAMES / the protein and pair descriptor
names -- dataloader.chemistry_prior.feature_similarity resolves the mix and picks the
granularity. So "would these 4 descriptors alone have done it" is one flag away, and is
the direct way to ask whether a descriptor set carries the split or just tracks it.

Why this could not reuse analysis/null_model.py. That one rebuilds the split by removing
a PROTEIN FAMILY from training and deriving the held-out classes from it. Under
--lipid_coldsplit no family is removed and the classes are a fixed set. Reconstructing
the wrong split would score the right numbers on the wrong rows, so the reconstruction
lives in preprocessing/lipid_marginal_baseline.lipid_split, next to the family-axis one
and sharing its valid/test halving.

Reads only. Trains nothing, writes nothing unless --out is given.

Usage:
    scripts/env.sh python3 analysis/lipid_coldsplit_null_model.py
    scripts/env.sh python3 analysis/lipid_coldsplit_null_model.py --features tanimoto
    scripts/env.sh python3 analysis/lipid_coldsplit_null_model.py \
        --features chain,unsaturation,hbond,heavy --label lipid4
    scripts/env.sh python3 analysis/lipid_coldsplit_null_model.py \
        --sets sphingolipids --seeds 0,1,2,3,4 --out /tmp/lcs_null.csv

With --scores (a CSV analysis/checkpoint_scores.py wrote for a --lipid_coldsplit label)
the network's own AUC is printed in the same table, on the same rows.
"""

import argparse
import statistics
import sys
from pathlib import Path

import numpy as np
import pandas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from null_model import (  # noqa: E402
    TANIMOTO, auc, per_lipid_auc, per_protein_auc, resolve_similarity, working_set,
)
from dataloader.chemistry_prior import (  # noqa: E402
    null_scores, null_scores_within_protein,
)
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS  # noqa: E402
from preprocessing.lipid_marginal_baseline import lipid_split  # noqa: E402

# ModelConfig defaults for the flags every current --lipid_coldsplit arg file leaves
# alone; the split has to be rebuilt with the same ones the run trained under or the
# rows will not match.
DEFAULT_RATIO = 2
DEFAULT_NEIGHBOURS = 15


def block_records(csv, data_dir, similarity, index, entity_column, set_name, seeds,
                   neighbours, ratio, network=None, balanced_lipid_classes=False):
    records = []
    classes = LIPID_COLDSPLIT_SETS[set_name]
    for seed in seeds:
        # The same pool the loader builds. Which sampler that is depends on the run:
        # --balanced_lipid_classes overrides --balanced_proteins in Dataloader.py's own
        # if/elif chain, and the new lipid-cold-split baseline sets it.
        csvt = working_set(
            csv, seed, ratio, classes, balanced_lipid_classes=balanced_lipid_classes
        )
        train, valid, test = lipid_split(csvt, classes, seed)
        for split_name, held in (("valid", valid), ("test", test)):
            if held.empty:
                continue
            # per_lipid_auc groups on this column by default; attached once here so both
            # score vectors and the network are read the same way, as null_model_table
            # does for the family axis.
            held = held.assign(lipid_class=lipid_class_series(held))
            truth = held["Interaction"].to_numpy()
            lipid_only = null_scores(
                train, held[entity_column], similarity, index, neighbours, entity_column
            )
            within = null_scores_within_protein(
                train, held, similarity, index, neighbours, entity_column
            )
            record = {
                "set": set_name,
                "seed": seed,
                "split": split_name,
                "rows": len(held),
                "pos": int(truth.sum()),
                "proteins": held["LTPProtein"].nunique(),
                "lipid_only_AUC": auc(truth, lipid_only),
            }
            record["within_protein_AUC"], record["within_protein_covered"] = (
                auc_on_scored(truth, within)
            )
            # Within-protein reading of each score vector: a pooled AUC can be carried
            # entirely by which protein a row belongs to, which is not the question.
            record["lipid_only_AUC_prot"], _ = per_protein_auc(held, lipid_only)
            record["within_protein_AUC_prot"], _ = per_protein_auc(held, within)
            # And the mirror: within one lipid, across proteins.
            record["lipid_only_AUC_lipid"], _ = per_lipid_auc(held, lipid_only)
            record["within_protein_AUC_lipid"], _ = per_lipid_auc(held, within)
            if network is not None:
                mine = network[
                    (network["fam"] == set_name)
                    & (network["seed"] == seed)
                    & (network["split"] == split_name)
                ]
                if not mine.empty:
                    if set(mine["pair_id"]) != set(held["pair_id"]):
                        raise SystemExit(
                            f"{set_name}/seed{seed}/{split_name}: the split rebuilt here "
                            "does not match the scored rows -- check --ratio against the "
                            "label's own --negatives_per_positive"
                        )
                    merged = held.merge(
                        mine[["pair_id", "prob"]], on="pair_id", how="left",
                        validate="one_to_one",
                    )
                    probs = merged["prob"].to_numpy()
                    record["net_AUC"] = auc(merged["Interaction"].to_numpy(), probs)
                    record["net_AUC_prot"], _ = per_protein_auc(merged, probs)
                    record["net_AUC_lipid"], _ = per_lipid_auc(merged, probs)
            records.append(record)
    return records


def auc_on_scored(truth, score):
    """(AUC over the rows this competitor could score, share of rows it could score).

    null_scores_within_protein returns nan for a held row whose protein has NO training
    rows left -- real under this split: a protein that only ever binds the held-out
    chemistry keeps nothing once those classes leave training. A single nan poisons the
    pooled AUC (pandas' rank() propagates it), which silently turned three of the four
    sets into "nan" on the first run of this script rather than into a number plus a
    caveat.

    Scoring the covered rows and reporting the coverage is the honest reading: the
    competitor is not wrong on the rows it cannot see, it is absent, and how often it is
    absent is itself worth knowing -- it says how much of the block is out of reach of
    "ask this protein about similar lipids" altogether.
    """
    truth = np.asarray(truth)
    score = np.asarray(score, dtype=float)
    covered = ~np.isnan(score)
    if not covered.any():
        return float("nan"), 0.0
    return auc(truth[covered], score[covered]), float(covered.mean())


def _mean(values):
    numbers = [v for v in values if v == v]  # drop nan
    return statistics.fmean(numbers) if numbers else float("nan")


def print_report(frame, features_label, neighbours, split):
    shown = frame[frame["split"] == split]
    if shown.empty:
        print(f"\nno {split} rows")
        return
    columns = [c for c in (
        "lipid_only_AUC", "within_protein_AUC", "within_protein_covered", "net_AUC",
        "lipid_only_AUC_prot", "within_protein_AUC_prot", "net_AUC_prot",
    ) if c in shown.columns]
    print(f"\n=== {split} | features={features_label} | k={neighbours} ===")
    print("AUC, mean over seeds. 0.500 is chance; the per-lipid label prior this split "
          "already reports is 0.500 by construction.")
    head = f"{'set':18s} {'seeds':>5s} {'rows':>6s} {'pos':>5s}"
    for column in columns:
        head += f" {column.replace('_AUC', ''):>22s}"
    print(head)
    for set_name, group in shown.groupby("set", sort=False):
        line = (f"{set_name:18s} {len(group):5d} {int(_mean(group['rows'])):6d} "
                f"{int(_mean(group['pos'])):5d}")
        for column in columns:
            line += f" {_mean(group[column]):22.4f}"
        print(line)
    line = f"{'ALL (pooled)':18s} {len(shown):5d} {'':6s} {'':5s}"
    for column in columns:
        line += f" {_mean(shown[column]):22.4f}"
    print(line)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--features", default=TANIMOTO,
        help=f'"{TANIMOTO}" (default, Morgan fingerprints over the whole structure) or a '
             "comma-separated descriptor-name list -- any lipid feature vector, see "
             "dataloader.chemistry_prior.feature_similarity",
    )
    parser.add_argument("--label", help="short name for --features in the printout")
    parser.add_argument(
        "--zscore", action="store_true",
        help="standardise the six multiplicative pair descriptors, see null_model.py",
    )
    parser.add_argument(
        "--sets", default=",".join(LIPID_COLDSPLIT_SETS),
        help="which LIPID_COLDSPLIT_SETS to score (default: all four)",
    )
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--neighbours", type=int, default=DEFAULT_NEIGHBOURS,
                        help="k nearest training entities per held row")
    parser.add_argument("--ratio", type=int, default=DEFAULT_RATIO,
                        help="--negatives_per_positive the compared run trained with")
    parser.add_argument("--split", default="test", choices=("valid", "test", "both"))
    parser.add_argument(
        "--scores",
        help="CSV from analysis/checkpoint_scores.py for a --lipid_coldsplit label; "
             "adds that network's AUC on the same rows",
    )
    parser.add_argument("--epoch", type=int, help="which epoch of --scores to read")
    parser.add_argument(
        "--balanced_lipid_classes", action="store_true",
        help="rebuild the pool with the (family, lipid class)-matched sampler -- must "
             "match the compared run's own flag, or the rows will not line up",
    )
    parser.add_argument("--out", help="write every per-(set, seed, split) row here")
    args = parser.parse_args()

    unknown = [s for s in args.sets.split(",") if s and s not in LIPID_COLDSPLIT_SETS]
    if unknown:
        raise SystemExit(
            f"unknown lipid set(s): {unknown}. Known: {list(LIPID_COLDSPLIT_SETS)}"
        )
    sets = [s for s in args.sets.split(",") if s]
    seeds = [int(s) for s in args.seeds.split(",") if s]

    data_dir = str(PROJECT_ROOT / "data") + "/"
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    similarity, index, entity_column, features_label, _ = resolve_similarity(
        csv, data_dir, args.features, args.label, args.zscore
    )

    network = None
    if args.scores:
        network = pandas.read_csv(args.scores)
        if args.epoch is not None:
            network = network[network["epoch"] == args.epoch]
        elif network["epoch"].nunique() > 1:
            raise SystemExit(
                f"--scores holds epochs {sorted(network['epoch'].unique())}; "
                "pass --epoch to choose one"
            )

    records = []
    for set_name in sets:
        records.extend(block_records(
            csv, data_dir, similarity, index, entity_column, set_name, seeds,
            args.neighbours, args.ratio, network,
            balanced_lipid_classes=args.balanced_lipid_classes,
        ))
    frame = pandas.DataFrame(records)

    print(f"entity granularity: {entity_column}")
    splits = ("valid", "test") if args.split == "both" else (args.split,)
    for split in splits:
        print_report(frame, features_label, args.neighbours, split)

    if args.out:
        frame.to_csv(args.out, index=False)
        print(f"\nwrote {len(frame)} rows to {args.out}")


if __name__ == "__main__":
    main()
