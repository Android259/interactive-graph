"""Three solo arms on one metric: frozen pretraining vs scratch vs unfrozen pretraining.

Why this measurement exists
---------------------------
The two-stage ("solo") line ran with exactly two arms: `structural_pretrain_family` (a
structurally pretrained protein tower loaded and then FROZEN, so only the head trains)
and `structural_pretrain_family_scratch` (everything trains from random init). Its
headline conclusion -- "pretraining does not help, it hurts" -- was therefore
confounded: the arms differ in TWO things at once, where the protein tower's weights
started AND which parameters are optimised. On a warm split with 100-400 training rows
training everything is the better deal regardless of initialisation, so what was
measured is "frozen reconstruction encoders are worse than task-trained ones", not
"pretraining is useless" (files/lipid_coldsplit_architecture_direction.md section 9,
files/geometric_edge_and_solo_next_architecture.md sections 4.1 and 5.1).

The third arm `structural_pretrain_family_unfrozen` closes that: it keeps
`--pretrained_checkpoint` and drops `--freeze_pretrained_encoders`, so it optimises the
same parameter set as `scratch` (1 071 238 trainable against `frozen`'s 512 197, from
the run logs) and differs from it in exactly one thing -- where the protein tower's
weights started.

This script reads the three arms off the canonical table on the metric both project
lines are now judged by, `AUC_within_protein_pairs`: the AUC over every (positive,
negative) pair of rows sharing a protein, so no comparison crosses a protein boundary
(training/new_train.py::within_protein_pair_auc).

What it prints
--------------
1. Per family, per arm: mean +- SEM over seeds, with the number of protein blocks that
   carried a pair, then the same pooled over the readable families.
2. PAIRED deltas between arms, differenced inside one (family, seed) and only where both
   arms ran. The split is shared there, so the split-to-split variance that dominates
   this data cancels; unpaired differences of the same numbers are much noisier.
3. Context columns (pooled AUC, balanced accuracy, final train/valid BA) -- the train
   number is what says whether an arm fits its training rows harder, which is the
   mechanism the frozen/unfrozen contrast is about.
4. A reproducibility control against a second batch date, and an explicit note when that
   batch has the column empty (the solo runs before 2026-09-09 predate the column, so
   the published 0.907/0.874 for `scratch`/`frozen` came from post-hoc recomputation by
   analysis/checkpoint_scores.py, not from this table).

Pooling follows the published solo table: an unweighted mean over the (family, seed)
rows of the readable families, SEM = std/sqrt(n) over those same rows. ML and OSBP have
two test rows and about one protein block, so the default --min-blocks drops them; that
leaves the same seven families the published pool used.

Reads only: opens metrics_summary.csv, writes nothing, touches no checkpoint, runs no
model.

Examples
--------
    python analysis/solo_pretraining_arms.py
    python analysis/solo_pretraining_arms.py --metric AUC_within_protein
    python analysis/solo_pretraining_arms.py --min-blocks 0 --show-unreadable
"""

import argparse
import csv
import math
import statistics
from collections import defaultdict

ARMS = [
    ("structural_pretrain_family", "frozen"),
    ("structural_pretrain_family_scratch", "scratch"),
    ("structural_pretrain_family_unfrozen", "unfrozen"),
]
ARM_OF_LABEL = dict(ARMS)
ARM_NAMES = [arm for _, arm in ARMS]
DELTA_PAIRS = [("unfrozen", "scratch"), ("unfrozen", "frozen"), ("scratch", "frozen")]
CONTEXT_COLUMNS = [
    "AUC_within_protein",
    "AUC",
    "balanced_accuracy",
    "final_train_balanced_accuracy",
    "final_valid_balanced_accuracy",
]


def read_rows(path, date):
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if row["label"] in ARM_OF_LABEL and (not date or row["datetime"].startswith(date)):
                yield row


def to_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def mean_sem(values):
    values = [v for v in values if v is not None]
    if not values:
        return None, None, 0
    if len(values) == 1:
        return values[0], None, 1
    return statistics.fmean(values), statistics.stdev(values) / math.sqrt(len(values)), len(values)


def cell(mean, sem, n, with_sigma=False):
    if mean is None:
        return "--"
    text = f"{mean:.3f}" if sem is None else f"{mean:+.3f} +- {sem:.3f}" if with_sigma else f"{mean:.3f} +- {sem:.3f}"
    if with_sigma and sem:
        text += f" {abs(mean) / sem:.1f}s" if sem > 0 else " --"
    return f"{text} (n={n})"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--table", default="metrics_summary.csv")
    parser.add_argument("--date", default="2026-09-09",
                        help="keep only rows whose datetime starts with this prefix, so all "
                             "three arms come from one batch (default: 2026-09-09)")
    parser.add_argument("--metric", default="AUC_within_protein_pairs",
                        help="column to rank by (default: the within-protein pair AUC)")
    parser.add_argument("--min-blocks", type=float, default=1.5,
                        help="drop a family whose mean AUC_within_protein_pairs_proteins is "
                             "below this; 1.5 leaves the seven families of the published "
                             "solo pool and drops ML and OSBP (default: 1.5)")
    parser.add_argument("--show-unreadable", action="store_true",
                        help="print dropped families too, marked, instead of hiding them")
    parser.add_argument("--control-date", default="2026-09-08",
                        help="second batch date for the reproducibility control; '' to skip")
    args = parser.parse_args()

    rows = list(read_rows(args.table, args.date))
    if not rows:
        raise SystemExit(f"no rows for date prefix {args.date!r} in {args.table}")

    by_cell = defaultdict(dict)      # (family, seed) -> arm -> row
    blocks = defaultdict(list)       # family -> protein blocks carrying a pair
    for row in rows:
        family = row["exclusion_set"].replace("groups_", "")
        by_cell[(family, row["seed"])][ARM_OF_LABEL[row["label"]]] = row
        count = to_float(row["AUC_within_protein_pairs_proteins"])
        if count is not None:
            blocks[family].append(count)

    families = sorted({family for family, _ in by_cell})
    readable = sorted(f for f in families
                      if blocks.get(f) and statistics.fmean(blocks[f]) >= args.min_blocks)

    def values_of(column, family=None, arm=None):
        return [to_float(cells[arm][column])
                for (fam, _), cells in by_cell.items()
                if (family is None and fam in readable or fam == family) and arm in cells]

    def deltas_of(column, left, right, family=None):
        out = []
        for (fam, _), cells in by_cell.items():
            if not (family is None and fam in readable or fam == family):
                continue
            if left in cells and right in cells:
                a, b = to_float(cells[left][column]), to_float(cells[right][column])
                if a is not None and b is not None:
                    out.append(a - b)
        return out

    print(f"batch {args.date} | metric {args.metric} | table {args.table}")
    print(f"readable families (mean protein blocks >= {args.min_blocks}): {', '.join(readable)}\n")

    width = 24
    header = f"{'family':16}{'blocks':>7}" + "".join(f"{arm:>{width}}" for arm in ARM_NAMES)
    print(header)
    print("-" * len(header))
    for family in (families if args.show_unreadable else readable):
        line = f"{family:16}{statistics.fmean(blocks.get(family, [0])):>7.1f}"
        for arm in ARM_NAMES:
            line += f"{cell(*mean_sem(values_of(args.metric, family, arm))):>{width}}"
        print(line + ("" if family in readable else "  (not readable)"))
    pooled = f"{'POOLED':16}{'':>7}"
    for arm in ARM_NAMES:
        pooled += f"{cell(*mean_sem(values_of(args.metric, None, arm))):>{width}}"
    print(pooled)

    print("\nPAIRED deltas on the same (family, seed)")
    width = 26
    header = f"{'family':16}" + "".join(f"{a + ' - ' + b:>{width}}" for a, b in DELTA_PAIRS)
    print(header)
    print("-" * len(header))
    for family in readable:
        line = f"{family:16}"
        for left, right in DELTA_PAIRS:
            line += f"{cell(*mean_sem(deltas_of(args.metric, left, right, family)), with_sigma=True):>{width}}"
        print(line)
    line = f"{'POOLED':16}"
    for left, right in DELTA_PAIRS:
        line += f"{cell(*mean_sem(deltas_of(args.metric, left, right)), with_sigma=True):>{width}}"
    print(line)

    print("\nContext, pooled over readable families")
    width = 24
    print(f"{'column':38}" + "".join(f"{arm:>{width}}" for arm in ARM_NAMES))
    for column in CONTEXT_COLUMNS:
        line = f"{column:38}"
        for arm in ARM_NAMES:
            line += f"{cell(*mean_sem(values_of(column, None, arm))):>{width}}"
        print(line)

    print("\nHow much room the metric has on this split (readable families)")
    print(f"{'arm':10}{'cells':>7}{'at 1.000':>10}{'>= 0.99':>9}{'distinct values':>17}{'min':>8}")
    for arm in ARM_NAMES:
        values = sorted(v for v in values_of(args.metric, None, arm) if v is not None)
        if not values:
            continue
        print(f"{arm:10}{len(values):>7}{sum(1 for v in values if v >= 0.9999):>10}"
              f"{sum(1 for v in values if v >= 0.99):>9}{len(set(round(v, 6) for v in values)):>17}"
              f"{min(values):>8.3f}")
    print("  A family here carries 1-5 protein blocks and a handful of same-protein pairs, so "
          "the\n  metric takes few discrete values and sits near its ceiling -- see the "
          "writeup for what\n  that does to any comparison made on it.")

    missing = [(family, seed, arm) for (family, seed), cells in sorted(by_cell.items())
               for arm in ARM_NAMES if arm not in cells]
    if missing:
        print("\nCells missing from this batch (no row reported):")
        for family, seed, arm in missing:
            print(f"  {arm:10} {family:16} seed {seed}")

    if args.control_date:
        print(f"\nReproducibility control on {args.metric}: {args.control_date} vs {args.date}")
        control = list(read_rows(args.table, args.control_date))
        for label, arm in ARMS:
            for date, source in ((args.control_date, control), (args.date, rows)):
                present = [r for r in source if r["label"] == label
                           and r["exclusion_set"].replace("groups_", "") in readable]
                mean, sem, n = mean_sem([to_float(r[args.metric]) for r in present])
                note = "" if n else f"  (column empty in {len(present)} rows of that batch)"
                print(f"  {arm:10} {date}  {cell(mean, sem, n)}{note}")


if __name__ == "__main__":
    main()
