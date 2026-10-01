#!/usr/bin/env python3
"""No-model baseline: predict binding from (protein, lipid subclass) alone.

"Простая классификация пары белок-подкласс липида" -- the planka GE is measured
against (files/ge_node_volume_descriptor_proposals.md, files/mlp_s15_pu_loss_first_
measurement.md), computed properly here instead of citing it from memory. For each
(LTPProtein, lipid subclass) cell, the prediction is the TRAIN positive rate of that
cell thresholded at 0.5 -- no chemistry beyond the subclass label, no structure, no
model (dataloader/Dataloader.py::_label_only_baseline is the same recipe, generalised
here from a single key -- lipid identity or lipid class -- to the JOINT (protein,
subclass) key, which that method already supports generically via any key Series).

Built on the same real PLIDataset splits every other table in this thread used
(--lipid_species_coldsplit=0.15, --balanced_proteins, the 5 standard seeds), so the
number is directly comparable to the MLP/GE/PU test BA and test F1 already measured.

Reads only. Writes nothing.

Usage:
  python3 analysis/protein_subclass_label_baseline.py
  python3 analysis/protein_subclass_label_baseline.py --label ge_s15_prothid32_hid64_noreg
"""
from __future__ import annotations

import argparse
import math
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd  # noqa: E402
import torch_geometric  # noqa: E402,F401

from read_configuration import read_configuration  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_subclass_blocks import article_subclass_species  # noqa: E402

DEFAULT_LABEL = "mlp_s15_nomb_hid64"
DEFAULT_SEEDS = (0, 1, 2, 3, 4)


def arg_lines(label):
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
    mapping = {}
    for subclass, species in article_subclass_species().items():
        for name in species:
            mapping[name] = subclass
    return mapping


def protein_subclass_key(frame, subclass_of):
    subclass = frame["FullIdentityOfLipid"].map(subclass_of).fillna("?unclassified")
    return frame["LTPProtein"].astype(str) + "|" + subclass.astype(str)


def confusion_metrics(prediction, truth):
    tp = int(((prediction == 1) & (truth == 1)).sum())
    fp = int(((prediction == 1) & (truth == 0)).sum())
    fn = int(((prediction == 0) & (truth == 1)).sum())
    tn = int(((prediction == 0) & (truth == 0)).sum())
    sensitivity = tp / (tp + fn) if (tp + fn) else float("nan")
    specificity = tn / (tn + fp) if (tn + fp) else float("nan")
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    ba = (sensitivity + specificity) / 2
    f1 = (
        2 * precision * sensitivity / (precision + sensitivity)
        if (precision + sensitivity) and precision == precision and sensitivity == sensitivity
        else float("nan")
    )
    return ba, f1, sensitivity, specificity, precision


def one_seed(seed, base_lines, full_csv, subclass_of):
    argv = ["protein_subclass_label_baseline"] + base_lines + [
        f"--seed={seed}", "--num_workers=0",
    ]
    conf = read_configuration(argv)
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    train_dataset, valid_dataset, test_dataset = PLIDataset(
        root_dir=data_dir, csv=full_csv.copy(), seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )
    train_csv = train_dataset.csv
    test_csv = test_dataset.csv

    key_train = protein_subclass_key(train_csv, subclass_of)
    key_test = protein_subclass_key(test_csv, subclass_of)
    rate = train_csv.groupby(key_train)["Interaction"].mean()
    fallback = int(train_csv["Interaction"].mean() > 0.5)
    looked_up = key_test.map(rate)
    seen = looked_up.notna()
    prediction = (looked_up > 0.5).astype(int).where(seen, fallback)
    truth = test_csv["Interaction"].astype(int)

    ba, f1, sens, spec, prec = confusion_metrics(prediction, truth)
    return {
        "seed": seed, "ba": ba, "f1": f1, "sens": sens, "spec": spec,
        "precision": prec, "coverage": float(seen.mean()), "n": len(test_csv),
    }


def mean_sem(values):
    values = [v for v in values if v == v]  # drop nan
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, float("nan"), n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(var) / math.sqrt(n), n


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--seeds", default=",".join(str(s) for s in DEFAULT_SEEDS))
    args = parser.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    base_lines = arg_lines(args.label)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    full_csv = pd.read_csv(interaction_csv_path(data_dir))
    subclass_of = species_to_subclass_map()

    rows = [one_seed(seed, base_lines, full_csv, subclass_of) for seed in seeds]

    print(f"label={args.label} seeds={seeds}")
    print(f"{'seed':>4s} {'BA':>7s} {'F1':>7s} {'sens':>7s} {'spec':>7s} "
          f"{'prec':>7s} {'coverage':>9s} {'n':>5s}")
    for row in rows:
        print(f"{row['seed']:4d} {row['ba']:7.4f} {row['f1']:7.4f} {row['sens']:7.4f} "
              f"{row['spec']:7.4f} {row['precision']:7.4f} {row['coverage']:9.1%} {row['n']:5d}")

    ba_mean, ba_sem, n = mean_sem([row["ba"] for row in rows])
    f1_mean, f1_sem, _ = mean_sem([row["f1"] for row in rows])
    print(f"\nALL (n={n}): test BA = {ba_mean:.3f} +- {ba_sem:.3f}   "
          f"test F1 = {f1_mean:.3f} +- {f1_sem:.3f}")
    print("\nGoogle Sheets paste (tab-separated):")
    print(f"\ttest BA\ttest F1")
    print(f"ALL\t{ba_mean:.3f} ± {ba_sem:.3f}\t{f1_mean:.3f} ± {f1_sem:.3f}".replace(".", ","))


if __name__ == "__main__":
    main()
