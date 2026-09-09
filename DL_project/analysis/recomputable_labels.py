"""Which labels can still have a per-row metric recomputed, and from which weights.

Why this exists
---------------
`AUC_within_protein{,_pairs}` needs the model's per-row SCORES, and a finished run
writes only confusion counts -- so for any label that finished before the metric existed
(everything before 2026-09-08) the number cannot be read off a report, it has to be
recomputed by loading the weights and re-scoring the split
(`analysis/checkpoint_scores.py`). That is possible only where weights were kept, and
this project kept them under two different flags with different meanings:

    groups_<g>/seed<N>.pt              --save_model / --save_checkpoint: the SELECTED
                                       checkpoint, the weights run_test actually
                                       measured. Same weight rule as a fresh run, so a
                                       number recomputed from these is directly
                                       comparable to a reported one.
    groups_<g>/dynamics/seed<N>_epoch<K>.pt
                                       --save_model_in_dynamics: fixed milestones
                                       (DYNAMICS_CHECKPOINT_EPOCHS = 1, 10, 49, 51,
                                       120). A number recomputed from epoch 120 is on a
                                       DIFFERENT weight rule than a reported one -- that
                                       caveat cost this project a comparison already
                                       (files/lcs_marginal_removal_and_solo_on_one_metric.md
                                       section 2: it moves the pair metric by 0.00-0.10
                                       where SEM is 0.02-0.07).

So the answer to "what else can be recomputed" is per label: is the column missing, are
there weights, and which of the two kinds.

Reads only: lists models/ and reads metrics_summary.csv. Loads no checkpoint and runs
no model -- the recompute itself is analysis/checkpoint_scores.py, which is not called
from here.

Examples
--------
    python analysis/recomputable_labels.py
    python analysis/recomputable_labels.py --metric AUC_within_protein_pairs --all
    python analysis/recomputable_labels.py --contains lcs
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# The four --lipid_coldsplit held-out sets (dataloader/sampler.LIPID_COLDSPLIT_SETS),
# spelled out rather than imported so this stays a filesystem/CSV reader with no torch
# import behind it.
LIPID_SETS = {"anionic", "choline", "phosphorus_free", "sphingolipids"}
EPOCH_FILE = re.compile(r"^seed(\d+)_epoch(\d+)\.pt$")
SELECTED_FILE = re.compile(r"^seed(\d+)\.pt$")


def scan_models(models_root):
    """label -> {"selected": {(group, seed)}, "milestones": {(group, seed, epoch)}}."""
    found = defaultdict(lambda: {"selected": set(), "milestones": set()})
    if not models_root.is_dir():
        return found
    for label_dir in sorted(models_root.iterdir()):
        if not label_dir.is_dir():
            continue
        for group_dir in label_dir.iterdir():
            if not group_dir.is_dir() or not group_dir.name.startswith("groups_"):
                continue
            group = group_dir.name[len("groups_"):]
            for path in group_dir.iterdir():
                match = SELECTED_FILE.match(path.name)
                if match:
                    found[label_dir.name]["selected"].add((group, int(match.group(1))))
            dynamics = group_dir / "dynamics"
            if dynamics.is_dir():
                for path in dynamics.iterdir():
                    match = EPOCH_FILE.match(path.name)
                    if match:
                        found[label_dir.name]["milestones"].add(
                            (group, int(match.group(1)), int(match.group(2)))
                        )
    return found


def scan_table(table_path, metric):
    """label -> (rows, rows missing the metric, set of excluded groups seen)."""
    rows = defaultdict(int)
    missing = defaultdict(int)
    groups = defaultdict(set)
    with open(table_path, newline="") as handle:
        for row in csv.DictReader(handle):
            label = row["label"]
            rows[label] += 1
            groups[label].add(row["exclusion_set"].replace("groups_", ""))
            if not row.get(metric):
                missing[label] += 1
    return rows, missing, groups


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--table", default=str(PROJECT_ROOT / "metrics_summary.csv"))
    parser.add_argument("--models", default=str(PROJECT_ROOT / "models"))
    parser.add_argument("--metric", default="AUC_within_protein_pairs",
                        help="the column whose absence makes a label a recompute candidate")
    parser.add_argument("--contains", default="",
                        help="keep only labels containing this substring")
    parser.add_argument("--all", action="store_true",
                        help="also list labels with nothing to recompute (column already "
                             "full) and labels with no weights at all")
    args = parser.parse_args()

    weights = scan_models(Path(args.models))
    rows, missing, groups = scan_table(Path(args.table), args.metric)

    labels = sorted(set(rows) | set(weights))
    if args.contains:
        labels = [label for label in labels if args.contains in label]

    recomputable, no_weights, complete = [], [], []
    for label in labels:
        has_weights = bool(weights[label]["selected"] or weights[label]["milestones"])
        if missing[label] == 0 and rows[label]:
            complete.append(label)
        elif has_weights:
            recomputable.append(label)
        else:
            no_weights.append(label)

    def axis(label):
        seen = groups[label]
        if not seen:
            return "?"
        return "lipid" if seen <= LIPID_SETS else "protein"

    def describe(label):
        selected = weights[label]["selected"]
        milestones = weights[label]["milestones"]
        epochs = sorted({epoch for _, _, epoch in milestones})
        cells = {(group, seed) for group, seed, _ in milestones}
        parts = []
        if selected:
            parts.append(f"selected {len(selected)} cells")
        if milestones:
            parts.append(f"milestones {len(cells)} cells @ {','.join(map(str, epochs))}")
        return "; ".join(parts) or "none"

    width = min(max((len(label) for label in labels), default=10), 62)
    print(f"metric: {args.metric} | models: {args.models}\n")
    print(f"RECOMPUTABLE -- column missing, weights on disk ({len(recomputable)} labels)")
    header = f"{'label':{width}}{'axis':>8}{'rows':>6}{'missing':>9}  weights"
    print(header)
    print("-" * (len(header) + 20))
    for label in sorted(recomputable, key=lambda name: (axis(name), -missing[name])):
        text = label if len(label) <= width else "…" + label[-(width - 1):]
        print(f"{text:{width}}{axis(label):>8}{rows[label]:>6}{missing[label]:>9}  {describe(label)}")

    if args.all:
        print(f"\nNO WEIGHTS -- column missing, nothing kept to rescore ({len(no_weights)})")
        for label in no_weights:
            text = label if len(label) <= width else "…" + label[-(width - 1):]
            print(f"{text:{width}}{axis(label):>8}{rows[label]:>6}{missing[label]:>9}")
        print(f"\nALREADY COMPLETE -- every row has the metric ({len(complete)})")
        for label in complete:
            text = label if len(label) <= width else "…" + label[-(width - 1):]
            print(f"{text:{width}}{axis(label):>8}{rows[label]:>6}")
    else:
        print(f"\n{len(no_weights)} more labels miss the column with no weights kept, "
              f"{len(complete)} already have it -- --all lists them.")


if __name__ == "__main__":
    main()
