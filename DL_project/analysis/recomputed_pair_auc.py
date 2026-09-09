"""Aggregate analysis/cross_sampler_eval.py output into the table a label comparison needs.

Why this exists
---------------
`AUC_within_protein_pairs` is the metric the lipid cold split is judged by, and it is
missing from `metrics_summary.csv` for every label that finished before 2026-09-08 --
those runs' reports carry only confusion counts, and an ordering cannot be recovered
from those. It can be recomputed from the weights `--save_model_in_dynamics` kept, and
`analysis/cross_sampler_eval.py` already does the per-(set, seed) scoring; what was
missing is the step after it, which each writeup then redid by hand: mean, SEM and
spread per label, per held-out set and pooled, out of one CSV per label.

The number this produces is NOT interchangeable with a reported one. The dynamics
milestones are fixed epochs (1, 10, 49, 51, 120); the reported number is measured on the
checkpoint selected by pooled validation balanced accuracy. On the four configs that
have both, the two rules differ by 0.00-0.10 where the SEM is 0.02-0.07
(files/lcs_marginal_removal_and_solo_on_one_metric.md section 2). So recomputed values
compare to each other, and to a reported value only with that caveat stated.

Reads only: reads the CSVs cross_sampler_eval wrote, writes nothing.

Examples
--------
    python analysis/recomputed_pair_auc.py --dir /path/to/recompute
    python analysis/recomputed_pair_auc.py --dir DIR --metric AUC --epoch 120
"""

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


def spread(values):
    values = [value for value in values if value is not None]
    if not values:
        return None, None, None, 0
    if len(values) == 1:
        return values[0], None, 0.0, 1
    std = statistics.stdev(values)
    return statistics.fmean(values), std / math.sqrt(len(values)), std, len(values)


def cell(mean, sem, std, n, width=20, with_n=False):
    if mean is None:
        return f"{'--':>{width}}"
    text = f"{mean:.3f}" if sem is None else f"{mean:.3f} ±{sem:.3f}"
    if with_n:
        text += f" sd{std:.3f} n{n}"
    return f"{text:>{width}}"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dir", required=True,
                        help="directory of per-label CSVs written by cross_sampler_eval.py")
    parser.add_argument("--metric", default="AUC_within_protein_pairs")
    parser.add_argument("--epoch", type=int, default=120,
                        help="which dynamics milestone to read (default: 120, the last)")
    parser.add_argument("--baseline", default="",
                        help="label (or unique suffix of one) to difference every other "
                             "label against, PAIRED inside one (set, seed). Only compare "
                             "labels whose sampler flags leave the same evaluation rows -- "
                             "--balanced_lipid_classes redraws the negatives, so a label "
                             "with it and one without are not measured on the same block "
                             "(the protein-block counts printed below show when that "
                             "happened).")
    args = parser.parse_args()

    by_label_set = defaultdict(list)
    by_label = defaultdict(list)
    blocks = defaultdict(list)
    sets = []
    for path in sorted(Path(args.dir).glob("*.csv")):
        with open(path, newline="") as handle:
            for row in csv.DictReader(handle):
                # Self-pairs only: a cross_sampler_eval CSV may hold weights scored on
                # another label's rows, which is a different question than this one.
                if row["rows_from"] != row["weights_from"]:
                    continue
                if int(row["epoch"]) != args.epoch:
                    continue
                label, held = row["weights_from"], row["set"]
                try:
                    value = float(row[args.metric])
                except (KeyError, TypeError, ValueError):
                    continue
                by_label_set[(label, held)].append(value)
                by_label[label].append(value)
                if row.get("AUC_within_protein_pairs_proteins"):
                    blocks[(label, held)].append(float(row["AUC_within_protein_pairs_proteins"]))
                if held not in sets:
                    sets.append(held)

    if not by_label:
        raise SystemExit(f"no rows for epoch {args.epoch} in {args.dir}")

    sets = sorted(sets)
    order = sorted(by_label, key=lambda label: -spread(by_label[label])[0])
    width = 34
    header = f"{'label (tail)':{width}}" + "".join(f"{held:>20}" for held in sets)
    header += f"{'pooled':>26}"
    print(f"metric: {args.metric} | epoch {args.epoch} | {len(by_label)} labels\n")
    print(header)
    print("-" * len(header))
    for label in order:
        line = f"{label[-width:]:{width}}"
        for held in sets:
            line += cell(*spread(by_label_set[(label, held)]))
        line += cell(*spread(by_label[label]), width=26, with_n=True)
        print(line)

    if args.baseline:
        matches = [name for name in by_label if name.endswith(args.baseline) or name == args.baseline]
        if len(matches) != 1:
            raise SystemExit(f"--baseline matched {len(matches)} labels: {matches}")
        base = matches[0]
        base_cells = {}
        for path in sorted(Path(args.dir).glob("*.csv")):
            with open(path, newline="") as handle:
                for row in csv.DictReader(handle):
                    if (row["rows_from"] == row["weights_from"] == base
                            and int(row["epoch"]) == args.epoch):
                        base_cells[(row["set"], row["seed"])] = float(row[args.metric])
        print(f"\nPAIRED deltas against {base[-42:]} (same set and seed)")
        print(f"{'label (tail)':{width}}" + "".join(f"{held:>20}" for held in sets)
              + f"{'pooled':>26}")
        for label in order:
            if label == base:
                continue
            line = f"{label[-width:]:{width}}"
            pooled_deltas = []
            for held in sets:
                deltas = []
                for path in sorted(Path(args.dir).glob("*.csv")):
                    with open(path, newline="") as handle:
                        for row in csv.DictReader(handle):
                            if (row["rows_from"] == row["weights_from"] == label
                                    and int(row["epoch"]) == args.epoch
                                    and row["set"] == held
                                    and (held, row["seed"]) in base_cells):
                                deltas.append(float(row[args.metric])
                                              - base_cells[(held, row["seed"])])
                pooled_deltas += deltas
                mean, sem, std, n = spread(deltas)
                line += (f"{'--':>20}" if mean is None
                         else f"{f'{mean:+.3f} ±{sem:.3f}' if sem else f'{mean:+.3f}':>20}")
            mean, sem, std, n = spread(pooled_deltas)
            sigma = f" {abs(mean)/sem:.1f}s" if mean is not None and sem else ""
            line += (f"{'--':>26}" if mean is None
                     else f"{f'{mean:+.3f} ±{sem:.3f}{sigma}':>26}")
            print(line)

    print(f"\nprotein blocks carrying a pair, mean over seeds")
    print(f"{'label (tail)':{width}}" + "".join(f"{held:>20}" for held in sets))
    for label in order:
        line = f"{label[-width:]:{width}}"
        for held in sets:
            values = blocks[(label, held)]
            line += f"{statistics.fmean(values):>20.1f}" if values else f"{'--':>20}"
        print(line)


if __name__ == "__main__":
    main()
