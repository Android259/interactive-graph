#!/usr/bin/env python3
"""One sweep label, every number files/marginals_and_cold_split.md section 8 and
files/interaction_signal_plan.md section 3 report about it -- in one run instead of the
three separate commands (checkpoint_scores.py, then chemistry_null_model.py, then
interaction_increment.py, hand-copying the CSV path between them) that produced them.

What it runs, in order, in one process (no CSV round-trip unless --out is given):

1. checkpoint_scores.score_checkpoints -- per-row probability of class 1 for every
   saved checkpoint of --label, every family x seed x epoch.
2. chemistry_null_model.null_model_table -- the chemical propensity null model on the
   same rows, pooled AND inside-protein AUC for both the network and the null model
   side by side (section 8.3/8.5 of the marginals note).
3. interaction_increment.increment_table -- does the network add anything ON TOP OF
   chemistry, an in-sample logistic fit that is a deliberate upper bound (section 8.3's
   "приращение" measurement).

Each stage's printed report is the same one its own script would print given the same
inputs -- this file does not reformat or re-derive anything, it only removes the need to
manually pass a scores CSV from one command's --out to the next's --scores.

Usage:
    scripts/env.sh python3 analysis/full_label_report.py \\
        --label bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120

    # one family, one seed, only the last epoch, both splits, and keep the raw scores
    scripts/env.sh python3 analysis/full_label_report.py --label <label> \\
        --families=scp2 --seeds=0 --epochs=120 --split=both --out /tmp/scores.csv

Reads model checkpoints and data/ only. Writes nothing unless --out is given.
"""
import argparse
import os
import sys

import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checkpoint_scores import DEFAULT_EPOCHS, arg_lines, score_checkpoints  # noqa: E402
from read_configuration import read_configuration  # noqa: E402
from chemistry_null_model import (  # noqa: E402
    DEFAULT_FAMILIES,
    null_model_table,
    print_null_model_report,
)
from interaction_increment import increment_table, print_increment_report  # noqa: E402
from dataloader.chemistry_prior import species_similarity  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402


def label_coldsplit_params(label, families):
    """coldsplit_share/negatives_per_positive as the label's own args file (plus
    read_configuration.py's defaults for whatever it leaves unset) actually trained
    with -- not a hardcoded guess.

    Both null_model_table's split reconstruction and checkpoint_scores' rebuilt split
    have to agree row for row (chemistry_null_model.py asserts this), and they only do
    when both use the same share/ratio. checkpoint_scores.py already reads these off
    the label; this makes full_label_report.py's defaults do the same instead of
    drifting from read_configuration.py's ModelConfig defaults over time.
    """
    argv = ["full_label_report"] + arg_lines(label) + [
        f"--excluded_groups={families[0]}",
        "--seed=0",
    ]
    conf = read_configuration(argv)
    return conf.coldsplit_share, conf.negatives_per_positive


def run_report(label, epochs, seeds, families, batch, neighbours, share, ratio, splits,
                scores=None, verbose=True):
    """Everything this file does, minus argument parsing -- importable on its own.

    `scores`, if given, is a pre-scored DataFrame (checkpoint_scores.score_checkpoints'
    return value, or a CSV already read with pandas.read_csv) -- skips the expensive
    scoring pass, for iterating on the null-model/increment side alone. Returns
    (scores, {split: null_model_table}, {split: increment_table}) so a caller can
    inspect the numbers programmatically instead of only reading the printout.
    """
    if scores is None:
        scores = score_checkpoints(
            label, epochs=epochs, seeds=seeds, families=families, batch=batch,
            verbose=verbose,
        )

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    similarity, index = species_similarity(csv, os.path.join(PROJECT_ROOT, "data"))

    null_tables, increment_tables = {}, {}
    last_epoch = max(epochs)
    for split in splits:
        print(f"\n{'#' * 10} split = {split} {'#' * 10}")

        print(f"\n--- null model (chemistry_null_model.py), epoch {last_epoch} ---")
        null_table = null_model_table(
            csv, similarity, index, families=families, seeds=seeds,
            neighbour_counts=[neighbours], share=share, ratio=ratio, split=split,
            network=scores, epoch=last_epoch,
        )
        print_null_model_report(null_table, split, last_epoch)
        null_tables[split] = null_table

        print(f"\n--- increment over chemistry (interaction_increment.py) ---")
        increment = increment_table(
            csv, similarity, index, scores, families=families, seeds=seeds,
            neighbours=neighbours, share=share, ratio=ratio, split=split, epochs=epochs,
        )
        print_increment_report(increment, split, neighbours)
        increment_tables[split] = increment

    return scores, null_tables, increment_tables


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--label", required=True, help="sweep label, also the arg-file name")
    parser.add_argument("--epochs", default=DEFAULT_EPOCHS)
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--batch", type=int, default=16, help="only affects the split's sampler")
    parser.add_argument("--neighbours", type=int, default=15, help="k for the null model")
    parser.add_argument(
        "--share", type=float, default=None,
        help="--coldsplit_share of the run; default reads it off --label's own args file",
    )
    parser.add_argument(
        "--ratio", type=int, default=None,
        help="--negatives_per_positive of the run; default reads it off --label's own args file",
    )
    parser.add_argument("--split", default="valid", choices=("valid", "test", "both"))
    parser.add_argument(
        "--scores", help="skip scoring, read a CSV analysis/checkpoint_scores.py already wrote"
    )
    parser.add_argument("--out", help="also write the raw per-row scores here")
    args = parser.parse_args()

    epochs = [int(e) for e in args.epochs.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    families = [f for f in args.families.split(",") if f]
    splits = ("valid", "test") if args.split == "both" else (args.split,)

    share, ratio = args.share, args.ratio
    if share is None or ratio is None:
        label_share, label_ratio = label_coldsplit_params(args.label, families)
        share = label_share if share is None else share
        ratio = label_ratio if ratio is None else ratio

    scores = pd.read_csv(args.scores) if args.scores else None
    scores, _, _ = run_report(
        args.label, epochs, seeds, families, args.batch, args.neighbours,
        share, ratio, splits, scores=scores,
    )

    if args.out:
        scores.to_csv(args.out, index=False)
        print(f"\nwrote : {args.out}")


if __name__ == "__main__":
    main()
