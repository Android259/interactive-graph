"""Measure label-prior baselines on protein-family and lipid-class splits.

Reproduce sampling and validation/test splitting with the selected seed. Compare
three predictors: training positive rate per lipid species, positive rate per lipid
class, and the global majority label. Threshold positive rates at 0.5.
These baselines measure how much prediction is possible from lipid labels alone.
"""

import argparse
import os
import sys

import pandas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Provide the sampler base-class placeholder when torch is unavailable.
try:  # pragma: no cover - depends on the machine, not on the code path
    import torch  # noqa: F401
except ModuleNotFoundError:
    import types

    _torch = types.ModuleType("torch")
    _torch.utils = types.ModuleType("torch.utils")
    _torch.utils.data = types.ModuleType("torch.utils.data")
    _torch.utils.data.Sampler = object
    sys.modules.update(
        {
            "torch": _torch,
            "torch.utils": _torch.utils,
            "torch.utils.data": _torch.utils.data,
        }
    )

from dataloader.dataset_source import interaction_csv_path
from dataloader.sampler import (
    lipid_class_series,
    split_and_sample_interactions,
    split_and_sample_lipid_class_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
)
from dataloader.splitting_on_blocks.lipid_coldsplit_blocks import lipid_classes_for_holdout

SAMPLERS = {
    "balanced_proteins": split_and_sample_protein_balanced_interactions,
    # the plain sampler takes no strata: it matches nothing per group to begin with
    "plain": lambda csv, seed, ratio=1, strata=None: split_and_sample_interactions(
        csv, seed
    ),
    "balanced_lipid_classes": lambda csv, seed, ratio=1, strata=None: (
        split_and_sample_lipid_class_balanced_interactions(csv, seed, ratio=ratio)
    ),
}


def working_set(csv, seed, sampler, ratio=1, lipid_classes=()):
    """Combine positives and sampled negatives, with row indices 0..N-1.

    Use lipid-class strata when requested to match the loader's sampling.
    """
    strata = None
    if lipid_classes and sampler != "balanced_lipid_classes":
        held = {name.lower() for name in lipid_classes}
        strata = lipid_class_series(csv).str.lower().isin(held)
    csvtrue, csvfalse = SAMPLERS[sampler](csv, seed, ratio, strata)
    both = pandas.concat([csvtrue.copy(), csvfalse.copy()])
    return both.set_index(pandas.Index(list(range(len(both)))))


def split(sampled_split, family, seed, lipid_classes=(), double=False):
    """Split by protein family and optional lipid classes, then divide the excluded block."""
    train = sampled_split[sampled_split["ProteinDomain"].str.lower() != family.lower()]
    if lipid_classes:
        held = {name.lower() for name in lipid_classes}
        train = train[~lipid_class_series(train).str.lower().isin(held)]
    excluded = sampled_split.drop(train.index)
    if double and lipid_classes:
        # For double-cold evaluation, keep only held-out-family rows in held-out lipid classes.
        held = {name.lower() for name in lipid_classes}
        excluded = excluded[
            lipid_class_series(excluded).str.lower().isin(held)
            & (excluded["ProteinDomain"].str.lower() == family.lower())
        ]
    return (train,) + halve_excluded_block(excluded, seed)


def halve_excluded_block(excluded, seed, merge_valid_test=False):
    """Split the excluded block into validation/test sets, stratified by label."""
    if merge_valid_test:
        return excluded, excluded
    positive_validate = excluded[excluded["Interaction"] == 1].sample(frac=0.5, random_state=seed)
    negative_validate = excluded[excluded["Interaction"] == 0].sample(frac=0.5, random_state=seed)
    valid = pandas.concat([positive_validate, negative_validate]).sample(frac=1, random_state=seed)
    test = excluded.drop(valid.index).sample(frac=1)
    return valid, test


def lipid_split(sampled_split, lipid_classes, seed, merge_valid_test=False):
    """Hold out a fixed set of lipid classes across all proteins.

    Keep other classes in training. Split the excluded rows with halve_excluded_block().
    No protein family is held out in this mode.
    """
    held = {name.lower() for name in lipid_classes}
    if not held:
        raise ValueError("lipid_split needs a non-empty lipid class set")
    train = sampled_split[~lipid_class_series(sampled_split).str.lower().isin(held)]
    excluded = sampled_split.drop(train.index)
    return (train,) + halve_excluded_block(excluded, seed, merge_valid_test=merge_valid_test)


def lipid_isolation_split(sampled_split, species, seed, merge_valid_test=False):
    """Hold out fixed FullIdentityOfLipid species across all proteins.

    Use the same split as lipid_split(), with species names instead of lipid classes.
    """
    held = set(species)
    if not held:
        raise ValueError("lipid_isolation_split needs a non-empty species set")
    train = sampled_split[~sampled_split["FullIdentityOfLipid"].isin(held)]
    excluded = sampled_split.drop(train.index)
    return (train,) + halve_excluded_block(excluded, seed, merge_valid_test=merge_valid_test)


def balanced_accuracy(truth, prediction):
    positive = truth == 1
    negative = ~positive
    if not positive.any() or not negative.any():
        return float("nan"), float("nan"), float("nan")
    sensitivity = float((prediction[positive] == 1).mean())
    specificity = float((prediction[negative] == 0).mean())
    return (sensitivity + specificity) / 2, sensitivity, specificity


def marginal_predictor(train, held, key_train, key_held):
    """Threshold each key's train positive rate at 0.5; unseen keys take the majority."""
    rate = train.groupby(key_train)["Interaction"].mean()
    fallback = int(train["Interaction"].mean() > 0.5)
    predicted = key_held.map(rate).fillna(-1.0)
    seen = predicted >= 0.0
    prediction = (predicted > 0.5).astype(int).where(seen, fallback)
    return prediction, float(seen.mean())


def report(csv, families, seeds, sampler, ratio=1, share=None, double=False):
    rows = []
    for family in families:
        for seed in seeds:
            held = []
            if share is not None:
                held = lipid_classes_for_holdout(csv, family, share)[0]
            sampled_split = working_set(csv, seed, sampler, ratio, held)
            train, valid, test = split(sampled_split, family, seed, held, double)
            if len(test) == 0:
                continue
            for split_name, held in (("valid", valid), ("test", test)):
                identity, coverage = marginal_predictor(
                    train, held, train["FullIdentityOfLipid"], held["FullIdentityOfLipid"]
                )
                klass, class_coverage = marginal_predictor(
                    train, held, lipid_class_series(train), lipid_class_series(held)
                )
                id_ba, id_sens, id_spec = balanced_accuracy(held["Interaction"], identity)
                cl_ba, cl_sens, cl_spec = balanced_accuracy(held["Interaction"], klass)
                rows.append(
                    {
                        "family": family,
                        "seed": seed,
                        "held_classes": len(held),
                        "split": split_name,
                        "n": len(held),
                        "positive_rate": float((held["Interaction"] == 1).mean()),
                        "lipid_seen": coverage,
                        "class_seen": class_coverage,
                        "identity_BA": id_ba,
                        "identity_sens": id_sens,
                        "identity_spec": id_spec,
                        "class_BA": cl_ba,
                        "class_sens": cl_sens,
                        "class_spec": cl_spec,
                    }
                )
    return pandas.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--sampler", default="balanced_proteins", choices=sorted(SAMPLERS))
    parser.add_argument("--families", default="")
    parser.add_argument(
        "--negatives_per_positive",
        type=int,
        default=1,
        help="negatives drawn per positive inside each balancing group",
    )
    parser.add_argument(
        "--share",
        type=float,
        default=None,
        help="hold lipid classes out too, covering this share of the family's "
             "positives (see preprocessing/lipid_class_holdout.py). Omit for the "
             "one-axis split.",
    )
    parser.add_argument(
        "--double",
        action="store_true",
        help="--double_coldsplit: also drop the held-out family's rows in classes that "
             "stayed in train (needs --share)",
    )
    parser.add_argument("--csv_out", default="")
    arguments = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(arguments.data_dir))
    families = (
        [f for f in arguments.families.split(",") if f]
        or sorted(csv["ProteinDomain"].dropna().unique().tolist())
    )
    seeds = [int(s) for s in arguments.seeds.split(",") if s]
    table = report(
        csv,
        families,
        seeds,
        arguments.sampler,
        arguments.negatives_per_positive,
        arguments.share,
        arguments.double,
    )

    with pandas.option_context("display.width", 200, "display.max_columns", 40):
        print(table.round(3).to_string(index=False))
        print()
        for split_name in ("valid", "test"):
            part = table[table["split"] == split_name]
            print(
                f"{split_name}: mean lipid-identity BA {part['identity_BA'].mean():.3f} | "
                f"mean lipid-class BA {part['class_BA'].mean():.3f} | "
                f"lipids seen in train {part['lipid_seen'].mean():.3f}"
            )
    if arguments.csv_out:
        table.to_csv(arguments.csv_out, index=False)


if __name__ == "__main__":
    main()
