#!/usr/bin/env python3
"""Per-INDIVIDUAL-subclass F1/BA inside a --lipid_subclass merged block.

Three of the nine FIG3_SUBCLASS_BLOCKS (dataloader/lipid_subclass_blocks.py) merge
several Titeca-et-al. subclasses into one held-out block because no single one of them
has enough proteins-with-a-positive to be its own block (e.g.
"Cer+CerP+HexCer+Hex2Cer+SHexCer+SM"). Training and the run's own reported metrics
never see the six members separately -- they are one block. This script does see them
separately: it reads analysis/checkpoint_scores.py's per-row CSV (one row per
(family, seed, epoch, split, pair_id) with a probability and the row's
FullIdentityOfLipid), maps each row's lipid to its OWN individual article subclass
(data/lipid_article_classification.json, the same file the block itself is built
from), and computes training.pair_baseline_common.binary_confusion_metrics per
individual subclass, pooling rows across every seed that held the block out.

WEIGHTS CAVEAT -- read before trusting a number here. new_train.py selects
`best_model_state` by a ROLLING validation metric and only that epoch's weights are
what run_test() measures (new_train.py:2404-2453); RUN_METRIC_FIELDS' own
"checkpoint_epoch" column in metrics_summary.csv is that epoch. But
--save_model_in_dynamics only ever writes FIVE fixed milestones (1, 10, 49, 51, 120,
training/new_train.py's DYNAMICS_CHECKPOINT_EPOCHS) -- not the selected epoch itself
unless it happens to land on one of those five. Measured on the two --lipid_subclass
labels this script was built for: only 18 of 90 (family, seed) runs (20%) have their
selected epoch land on a saved milestone; the other 80% can only be approximated by
the NEAREST saved milestone, and that approximation is not a small correction -- one
checked example (geometric_edge/.../PC/seed0) was official BA 0.549 at the true
epoch 53 against 0.635 at the nearest saved milestone (49) and 0.430 at epoch 120.
This script always prefers the exact selected epoch when it was saved, and reports
in its stderr summary how many (family, seed) runs got the exact epoch versus an
approximation, so every number here carries that count alongside it.

Reads only. Trains nothing, writes only --out if given.

    python3 analysis/checkpoint_scores.py --label <label> --epochs=1,10,49,51,120 \
        --seeds=0,1,2,3,4 --out /tmp/<label>_scores.csv
    python3 analysis/lipid_subclass_within_block_report.py --label <label> \
        --scores /tmp/<label>_scores.csv --out files/<label>_subclass_breakdown.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "training") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "training"))

from dataloader.lipid_subclass_blocks import article_subclass_species  # noqa: E402
from pair_baseline_common import binary_confusion_metrics  # noqa: E402


def species_to_subclass_map(data_dir=None) -> dict:
    """{FullIdentityOfLipid: its own article subclass}, the reverse of
    article_subclass_species's {subclass: species}."""
    mapping = {}
    for subclass, species in article_subclass_species(data_dir).items():
        for one in species:
            mapping[one] = subclass
    return mapping


def select_checkpoint_epochs(scores: pd.DataFrame, metrics_summary_path: Path, label: str) -> pd.DataFrame:
    """One row of `scores` per (fam, seed): the row at the epoch closest to that run's
    own true selected checkpoint (metrics_summary.csv's "checkpoint_epoch"), among
    whatever epochs this (fam, seed) actually has scored rows for. Exact when the
    selected epoch was one of the saved milestones, nearest-available otherwise --
    both cases, and which one applied, are reported to stderr.
    """
    summary = pd.read_csv(metrics_summary_path)
    summary = summary[summary["label"] == label]
    true_epoch_by_key = {}
    for _, row in summary.iterrows():
        fam = str(row["exclusion_set"])
        if fam.startswith("groups_"):
            fam = fam[len("groups_"):]
        seed = int(row["seed"])
        checkpoint_epoch = row.get("checkpoint_epoch")
        if pd.isna(checkpoint_epoch):
            continue
        true_epoch_by_key[(fam, seed)] = int(checkpoint_epoch)

    kept_frames = []
    exact = 0
    approximated = 0
    unresolved = 0
    for (fam, seed), group in scores.groupby(["fam", "seed"]):
        true_epoch = true_epoch_by_key.get((fam, int(seed)))
        if true_epoch is None:
            unresolved += 1
            continue
        available = sorted(group["epoch"].unique())
        nearest = min(available, key=lambda e: abs(e - true_epoch))
        if nearest == true_epoch:
            exact += 1
        else:
            approximated += 1
        kept_frames.append(group[group["epoch"] == nearest])
    print(
        f"checkpoint selection: {exact} exact, {approximated} approximated by nearest "
        f"saved milestone, {unresolved} with no metrics_summary.csv row -- see this "
        "script's own header for why an approximated run's numbers can differ a lot "
        "from the officially reported ones",
        file=sys.stderr,
    )
    return pd.concat(kept_frames) if kept_frames else scores.iloc[0:0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--scores", type=Path, required=True, help="analysis/checkpoint_scores.py's --out CSV")
    parser.add_argument("--label", required=True)
    parser.add_argument("--metrics_summary", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    scores = pd.read_csv(args.scores)
    scores = scores[scores["split"] == "test"].copy()
    if scores.empty:
        raise SystemExit(f"no test-split rows in {args.scores}")

    scores = select_checkpoint_epochs(scores, args.metrics_summary, args.label)
    if scores.empty:
        raise SystemExit("no (family, seed) run could be matched to a metrics_summary.csv checkpoint_epoch")

    species_map = species_to_subclass_map()
    scores["true_subclass"] = scores["lipid"].map(species_map)

    rows = []
    for fam in sorted(scores["fam"].unique()):
        members = set(fam.split("+"))
        block = scores[(scores["fam"] == fam) & (scores["true_subclass"].isin(members))]
        for subclass in sorted(members):
            sub = block[block["true_subclass"] == subclass]
            if sub.empty:
                continue
            metrics = binary_confusion_metrics(sub["label_value"], sub["prob"], 0.5)
            truth = sub["label_value"].to_numpy()
            probs = sub["prob"].to_numpy()
            # AUC is threshold-free, so BA/F1 near chance WITH a healthy AUC means the
            # 0.5 threshold sits in the wrong place for this subclass, while AUC near
            # 0.5 means the model has no signal here at all. The two call for opposite
            # fixes, and the confusion-matrix columns alone cannot tell them apart --
            # the same reason analysis/checkpoint_scores.py exists.
            auc = float("nan")
            if truth.min() != truth.max():
                order = probs.argsort()
                ranks = pd.Series(probs).rank().to_numpy()
                n_pos = int(truth.sum())
                n_neg = len(truth) - n_pos
                auc = (ranks[truth == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
                del order
            rows.append({
                "block": fam,
                "subclass": subclass,
                "rows": len(sub),
                "positives": int(sub["label_value"].sum()),
                "pos_rate": float(truth.mean()),
                "proteins": sub["protein"].nunique(),
                "seeds_pooled": sub["seed"].nunique(),
                "AUC": auc,
                "mean_p_pos": float(probs[truth == 1].mean()) if (truth == 1).any() else float("nan"),
                "mean_p_neg": float(probs[truth == 0].mean()) if (truth == 0).any() else float("nan"),
                "sensitivity": metrics["sensitivity"],
                "specificity": metrics["specificity"],
                "balanced_accuracy": metrics["balanced_accuracy"],
                "F1": metrics["F1"],
                "TP": metrics["TP"], "FP": metrics["FP"],
                "TN": metrics["TN"], "FN": metrics["FN"],
            })

    result = pd.DataFrame(rows).sort_values(["block", "subclass"])
    with pd.option_context("display.width", 160, "display.max_rows", None):
        print(result.to_string(index=False))
    if args.out:
        result.to_csv(args.out, index=False)
        print(f"wrote : {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
