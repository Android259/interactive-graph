#!/usr/bin/env python3
"""Subclass composition of --lipid_species_coldsplit's valid/test blocks, per seed.

Why this exists
----------------
--lipid_species_coldsplit holds out a seeded, structure-disjoint set of individual
lipid SPECIES (dataloader/lipid_species_blocks.py), not named subclasses the way
--lipid_coldsplit/--lipid_subclass do. Nobody has read off which subclasses (Titeca et
al.'s head-group rows, data/lipid_article_classification.json) that draw actually lands
in valid vs test, how much a subclass straddles both, or how consistent the draw is
across the five seeds a grid runs.

Two things this script is careful to get right, because the split is NOT simply "some
species held out, split in half by species":

1. Which species are held out is decided from the FULL, unsampled interaction table
   (dataloader/Dataloader.py's _derive_lipid_class_holdout runs before negative
   sampling) -- species_coldsplit_block below is called on that table directly, not on
   a PLIDataset's sampled pool.
2. Valid and test are NOT a species-level split of the held-out block: each LABEL
   (positive/negative) of the held-out rows in the SAMPLED table is independently
   halved by ROW (dataloader/Dataloader.py._split_interactions, the pandas.sample(frac=
   0.5) branch), so a species with more than one row in the block can straddle valid
   and test. This script reads the real valid/test frames off an actual PLIDataset
   build (the same machinery every run uses) rather than re-deriving that row split by
   hand, to avoid reproducing it wrong.

Reads only: the interaction CSV, data/lipid_article_classification.json, and builds a
PLIDataset per seed (lean-loading descriptor_mlp path, no protein graphs/lipid
encodings -- see dataloader/AGENTS.md). Writes nothing.

Usage:
  python3 analysis/lipid_species_coldsplit_subclass_report.py
  python3 analysis/lipid_species_coldsplit_subclass_report.py --seeds 0,1,2,3,4
  python3 analysis/lipid_species_coldsplit_subclass_report.py --label ge_s15_prothid32_hid64_noreg
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd  # noqa: E402
import torch_geometric  # noqa: E402,F401

from read_configuration import read_configuration  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_species_blocks import species_coldsplit_block  # noqa: E402
from dataloader.lipid_subclass_blocks import article_subclass_species  # noqa: E402

DEFAULT_LABEL = "mlp_s15_nomb_hid64"
DEFAULT_SEEDS = (0, 1, 2, 3, 4)


def arg_lines(label):
    """Same convention analysis/checkpoint_scores.py::arg_lines uses: parse
    scripts/arg_files/<label>.md into read_configuration-ready tokens, stripping the
    quotes the shell would otherwise strip around e.g. --pool_type="add".
    """
    path = os.path.join(PROJECT_ROOT, "scripts", "arg_files", f"{label}.md")
    lines = []
    for raw in open(path):
        stripped = raw.strip()
        if not stripped.startswith("--"):
            continue
        if "=" in stripped:
            key, value = stripped.split("=", 1)
            lines.append(key + "=" + value.strip().strip('"').strip("'"))
        else:
            lines.append(stripped)
    return lines


def species_to_subclass_map():
    """{FullIdentityOfLipid: subclass abbreviation}, from the article classification."""
    mapping = {}
    for subclass, species in article_subclass_species().items():
        for name in species:
            mapping[name] = subclass
    return mapping


def subclasses_for(frame, subclass_of):
    """(subclass -> (rows, positives) Counter pair) over one split frame's species."""
    rows = Counter()
    positives = Counter()
    unclassified_species = set()
    for name, group in frame.groupby("FullIdentityOfLipid"):
        subclass = subclass_of.get(name)
        if subclass is None:
            unclassified_species.add(name)
            continue
        rows[subclass] += len(group)
        positives[subclass] += int(group["Interaction"].sum())
    return rows, positives, unclassified_species


def report_seed(seed, label, base_lines, full_csv, subclass_of):
    argv = ["lipid_species_coldsplit_subclass_report"] + base_lines + [
        f"--seed={seed}", "--num_workers=0",
    ]
    conf = read_configuration(argv)
    if not conf.lipid_species_coldsplit:
        raise SystemExit(f"{label} does not set --lipid_species_coldsplit")

    # Independent of the sampled pool -- same call _derive_lipid_class_holdout makes,
    # on the same full table, so this reports exactly what that run's own log line
    # ("lipid species cold split ... N lipids in M components ...") means.
    species, stats = species_coldsplit_block(
        full_csv, conf.lipid_species_coldsplit, seed,
        isomeric=bool(getattr(conf, "lipid_isomers", False)),
    )
    block_subclasses = Counter(subclass_of.get(name, "?unclassified") for name in species)

    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    train_dataset, valid_dataset, test_dataset = PLIDataset(
        root_dir=data_dir, csv=full_csv.copy(), seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )

    valid_rows, valid_pos, valid_unclassified = subclasses_for(valid_dataset.csv, subclass_of)
    test_rows, test_pos, test_unclassified = subclasses_for(test_dataset.csv, subclass_of)

    all_subclasses = sorted(set(valid_rows) | set(test_rows))
    both = sorted(set(valid_rows) & set(test_rows))

    print(f"\n===== seed {seed} =====")
    print(
        f"block: {stats['species']} lipids in {stats['components_used']}/"
        f"{stats['components']} components, {stats['block_positives']} positives in "
        f"{stats['block_rows']} full-table rows over {stats['block_proteins']} proteins "
        f"(full table, pre-sampling); train keeps {stats['train_positives']} positives"
    )
    print(f"block subclasses ({len(block_subclasses)}): "
          + ", ".join(f"{name}={count}" for name, count in sorted(block_subclasses.items())))
    print(
        f"sampled pool actually split: valid {len(valid_dataset.csv)} rows "
        f"({int(valid_dataset.csv['Interaction'].sum())} pos), "
        f"test {len(test_dataset.csv)} rows "
        f"({int(test_dataset.csv['Interaction'].sum())} pos)"
    )
    print(f"{'subclass':16s} {'valid rows':>10s} {'valid pos':>9s} "
          f"{'test rows':>9s} {'test pos':>8s}  in both?")
    for subclass in all_subclasses:
        vr, vp = valid_rows.get(subclass, 0), valid_pos.get(subclass, 0)
        tr, tp = test_rows.get(subclass, 0), test_pos.get(subclass, 0)
        flag = "yes" if subclass in both else ("valid only" if vr else "test only")
        print(f"{subclass:16s} {vr:10d} {vp:9d} {tr:9d} {tp:8d}  {flag}")
    if valid_unclassified or test_unclassified:
        print(
            f"unclassified species (not in lipid_article_classification.json): "
            f"{len(valid_unclassified | test_unclassified)} "
            f"(valid {len(valid_unclassified)}, test {len(test_unclassified)})"
        )
    print(
        f"subclasses: {len(all_subclasses)} total in valid+test, "
        f"{len(both)} present in BOTH, "
        f"{len(set(valid_rows) - set(test_rows))} valid-only, "
        f"{len(set(test_rows) - set(valid_rows))} test-only"
    )
    return all_subclasses, both


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument(
        "--seeds", default=",".join(str(s) for s in DEFAULT_SEEDS),
        help="comma-separated seeds (default: the standard grid, 0-4)",
    )
    args = parser.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    base_lines = arg_lines(args.label)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    full_csv = pd.read_csv(interaction_csv_path(data_dir))
    subclass_of = species_to_subclass_map()

    print(f"label={args.label} seeds={seeds}")
    print(
        f"catalog: {len(set(subclass_of.values()))} subclasses over "
        f"{len(subclass_of)} classified species "
        f"(table has {full_csv['FullIdentityOfLipid'].nunique()} distinct species total)"
    )

    per_seed_subclasses = {}
    per_seed_both = {}
    for seed in seeds:
        all_subclasses, both = report_seed(seed, args.label, base_lines, full_csv, subclass_of)
        per_seed_subclasses[seed] = set(all_subclasses)
        per_seed_both[seed] = set(both)

    print("\n===== across seeds =====")
    frequency = Counter()
    for subclasses in per_seed_subclasses.values():
        frequency.update(subclasses)
    print(f"{'subclass':16s} {'in N/' + str(len(seeds)) + ' seeds':>14s}  seeds where BOTH valid&test hold it")
    for subclass, count in frequency.most_common():
        both_seeds = sorted(s for s in seeds if subclass in per_seed_both[s])
        print(f"{subclass:16s} {count:14d}  {both_seeds}")


if __name__ == "__main__":
    main()
