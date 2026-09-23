#!/usr/bin/env python3
"""checkpoint_scores.py, but scoring only ONE epoch per (family, seed) instead of
every --save_model_in_dynamics milestone: whichever of DYNAMICS_CHECKPOINT_EPOCHS is
nearest to that run's own true selected checkpoint (metrics_summary.csv's
"checkpoint_epoch" -- the epoch new_train.py's best_model_state actually came from,
new_train.py:2404-2453). Scoring all five milestones for every combination, the way a
first pass at this might do, is 5x the CPU a --lipid_subclass sweep (nine blocks, five
seeds) needs for nothing: only the nearest milestone to each run's own selected epoch
is ever kept downstream (analysis/lipid_subclass_within_block_report.py's own
select_checkpoint_epochs does the same nearest-pick AFTER scoring all five -- this
script does the pick BEFORE scoring, so the four unwanted epochs are never scored at
all).

Reads only. Trains nothing, writes only --out.

    python3 analysis/checkpoint_scores_at_selected_epoch.py --label <label> \
        --seeds=0,1,2,3,4 --out /tmp/<label>_scores.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from checkpoint_scores import (  # noqa: E402
    DEFAULT_EPOCHS,
    default_groups_for_label,
    score_checkpoints,
)


def nearest_epoch_by_run(metrics_summary_path: Path, label: str, milestones: list[int]) -> dict:
    """{(family, seed): nearest milestone epoch to that run's true checkpoint_epoch}."""
    summary = pd.read_csv(metrics_summary_path)
    summary = summary[summary["label"] == label]
    picks = {}
    for _, row in summary.iterrows():
        fam = str(row["exclusion_set"])
        if fam.startswith("groups_"):
            fam = fam[len("groups_"):]
        seed = int(row["seed"])
        checkpoint_epoch = row.get("checkpoint_epoch")
        if pd.isna(checkpoint_epoch):
            continue
        checkpoint_epoch = int(checkpoint_epoch)
        nearest = min(milestones, key=lambda e: abs(e - checkpoint_epoch))
        picks[(fam, seed)] = (nearest, checkpoint_epoch)
    return picks


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument(
        "--families", default=None,
        help="held-out group names; default follows the label's own axis",
    )
    parser.add_argument("--metrics_summary", type=Path, default=PROJECT_ROOT.parent / "metrics_summary.csv")
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    milestones = [int(e) for e in DEFAULT_EPOCHS.split(",")]
    families = (
        [f for f in args.families.split(",") if f]
        if args.families is not None
        else default_groups_for_label(args.label)
    )
    seeds = [int(s) for s in args.seeds.split(",")]

    picks = nearest_epoch_by_run(args.metrics_summary, args.label, milestones)

    frames = []
    exact, approximated, missing = 0, 0, 0
    for family in families:
        for seed in seeds:
            pick = picks.get((family, seed))
            if pick is None:
                missing += 1
                print(f"no metrics_summary.csv checkpoint_epoch for {family}/seed{seed}, skipping", file=sys.stderr)
                continue
            nearest, true_epoch = pick
            if nearest == true_epoch:
                exact += 1
            else:
                approximated += 1
            frame = score_checkpoints(
                args.label, epochs=[nearest], seeds=[seed], families=[family],
                batch=args.batch, verbose=True,
            )
            frames.append(frame)

    print(
        f"checkpoint selection: {exact} exact, {approximated} approximated by nearest "
        f"saved milestone, {missing} skipped (no metrics_summary.csv row)",
        file=sys.stderr,
    )
    if not frames:
        raise SystemExit("nothing scored")
    table = pd.concat(frames)
    table.to_csv(args.out, index=False)
    print(f"wrote : {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
