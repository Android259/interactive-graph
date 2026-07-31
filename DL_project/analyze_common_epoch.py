#!/usr/bin/env python3
"""Find one validation epoch that performs best across matched groups and seeds."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


EPOCH_TAGS = {
    "train_balanced_accuracy": "epoch/train balanced_accuracy",
    "valid_balanced_accuracy": "epoch/valid balanced_accuracy",
    "valid_F1": "epoch/valid F1",
    "valid_sensitivity": "epoch/valid sensitivity",
    "valid_specificity": "epoch/valid specificity",
    "valid_loss": "epoch/valid loss",
}


def rolling_mean(values: dict[int, float], epoch: int, window: int) -> float:
    start = max(1, epoch - window + 1)
    return statistics.fmean(values[step] for step in range(start, epoch + 1))


def select_common_epoch(histories, window=5):
    """Select by mean group rolling BA, then worst group, then lower group std."""
    common_last_epoch = min(max(history["valid_balanced_accuracy"]) for history in histories)
    candidates = []
    for epoch in range(1, common_last_epoch + 1):
        run_scores = defaultdict(list)
        for history in histories:
            run_scores[history["group"]].append(
                rolling_mean(history["valid_balanced_accuracy"], epoch, window)
            )
        group_scores = {
            group: statistics.fmean(scores)
            for group, scores in run_scores.items()
        }
        values = list(group_scores.values())
        candidates.append(
            {
                "epoch": epoch,
                "mean": statistics.fmean(values),
                "worst": min(values),
                "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
                "group_scores": group_scores,
            }
        )
    return max(
        candidates,
        key=lambda item: (item["mean"], item["worst"], -item["std"], -item["epoch"]),
    )


def parse_filter(expression):
    if "=" not in expression:
        raise ValueError(f"Expected COLUMN=VALUE filter, got: {expression}")
    return expression.split("=", 1)


def value_matches(actual, expected):
    if actual == expected:
        return True
    try:
        return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=1e-12)
    except (TypeError, ValueError):
        return False


def canonical_value(value):
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else str(number)
    except (TypeError, ValueError):
        return str(value)


def latest_matching_rows(table, filters, seeds):
    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    matching = []
    for row in rows:
        if row.get("run_status") != "complete":
            continue
        if canonical_value(row.get("seed")) not in seeds:
            continue
        if all(value_matches(row.get(column, ""), expected) for column, expected in filters):
            matching.append(row)

    latest = {}
    for row in sorted(matching, key=lambda item: item["datetime"]):
        latest[(row["exclusion_set"], canonical_value(row["seed"]))] = row
    return list(latest.values())


def resolve_run_dir(run_root, row):
    timestamp = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").strftime(
        "%Y%m%d_%H%M%S"
    )
    parent = run_root / row["architecture"] / row["exclusion_set"]
    candidates = sorted(parent.glob(f"train{timestamp}_*"))
    if len(candidates) != 1:
        raise ValueError(
            f"Expected one run for {row['exclusion_set']} seed={row['seed']} "
            f"at {timestamp}, found {len(candidates)}"
        )
    return candidates[0]


def read_history(run_dir, group, seed):
    event_files = list(run_dir.glob("events.out.tfevents.*"))
    if len(event_files) != 1:
        raise ValueError(f"Expected one event file in {run_dir}, found {len(event_files)}")
    accumulator = EventAccumulator(str(run_dir), size_guidance={"scalars": 0})
    accumulator.Reload()
    available = set(accumulator.Tags().get("scalars", []))
    missing = set(EPOCH_TAGS.values()) - available
    if missing:
        raise ValueError(f"Missing epoch tags in {run_dir}: {sorted(missing)}")

    history = {"group": group, "seed": seed, "run_dir": run_dir}
    for name, tag in EPOCH_TAGS.items():
        history[name] = {
            event.step: event.value
            for event in accumulator.Scalars(tag)
            if math.isfinite(event.value)
        }
    valid_steps = set(history["valid_balanced_accuracy"])
    for name in EPOCH_TAGS:
        if name == "valid_balanced_accuracy":
            continue
        valid_steps &= set(history[name])
    last_complete = max(valid_steps)
    for name in EPOCH_TAGS:
        history[name] = {
            step: value
            for step, value in history[name].items()
            if step <= last_complete
        }
    return history


def metric_at(history, metric, epoch):
    return history[metric][epoch]


def print_report(histories, selected, window):
    epoch = selected["epoch"]
    print(
        f"selected_epoch={epoch} common_epoch_limit="
        f"{min(max(h['valid_balanced_accuracy']) for h in histories)} "
        f"rolling_window={window}"
    )
    print(
        f"group_mean_rolling_BA={selected['mean']:.6f} "
        f"worst_group_rolling_BA={selected['worst']:.6f} "
        f"group_std={selected['std']:.6f}"
    )
    print(
        "group\tseed\tepochs\trolling_BA\tvalid_BA\tvalid_F1\t"
        "sensitivity\tspecificity\tmin_recall\tvalid_loss\ttrain_BA\tgap"
    )
    for history in sorted(histories, key=lambda item: (item["group"], item["seed"])):
        valid_ba = metric_at(history, "valid_balanced_accuracy", epoch)
        sensitivity = metric_at(history, "valid_sensitivity", epoch)
        specificity = metric_at(history, "valid_specificity", epoch)
        train_ba = metric_at(history, "train_balanced_accuracy", epoch)
        print(
            f"{history['group']}\t{history['seed']}\t"
            f"{max(history['valid_balanced_accuracy'])}\t"
            f"{rolling_mean(history['valid_balanced_accuracy'], epoch, window):.6f}\t"
            f"{valid_ba:.6f}\t{metric_at(history, 'valid_F1', epoch):.6f}\t"
            f"{sensitivity:.6f}\t{specificity:.6f}\t"
            f"{min(sensitivity, specificity):.6f}\t"
            f"{metric_at(history, 'valid_loss', epoch):.6f}\t"
            f"{train_ba:.6f}\t{train_ba - valid_ba:.6f}"
        )

    print("\ngroup aggregates across seeds")
    print("group\trolling_BA\tvalid_BA\tF1\tmin_recall\tvalid_loss\ttrain_valid_gap")
    groups = sorted({history["group"] for history in histories})
    for group in groups:
        group_histories = [history for history in histories if history["group"] == group]
        valid_values = [
            metric_at(history, "valid_balanced_accuracy", epoch)
            for history in group_histories
        ]
        train_values = [
            metric_at(history, "train_balanced_accuracy", epoch)
            for history in group_histories
        ]
        min_recalls = [
            min(
                metric_at(history, "valid_sensitivity", epoch),
                metric_at(history, "valid_specificity", epoch),
            )
            for history in group_histories
        ]
        print(
            f"{group}\t{selected['group_scores'][group]:.6f}\t"
            f"{statistics.fmean(valid_values):.6f}\t"
            f"{statistics.fmean(metric_at(h, 'valid_F1', epoch) for h in group_histories):.6f}\t"
            f"{statistics.fmean(min_recalls):.6f}\t"
            f"{statistics.fmean(metric_at(h, 'valid_loss', epoch) for h in group_histories):.6f}\t"
            f"{statistics.fmean(t - v for t, v in zip(train_values, valid_values)):.6f}"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=Path("metrics_summary.csv"))
    parser.add_argument("--run-root", type=Path, default=Path("run"))
    parser.add_argument("--seed", action="append", default=[])
    parser.add_argument("--filter", action="append", default=[])
    parser.add_argument("--window", type=int, default=5)
    args = parser.parse_args()

    if not args.seed:
        parser.error("provide at least one --seed")
    if not args.filter:
        parser.error("provide filters identifying one matched configuration")
    if args.window < 1:
        parser.error("--window must be positive")

    filters = [parse_filter(expression) for expression in args.filter]
    rows = latest_matching_rows(args.table, filters, set(args.seed))
    if not rows:
        parser.error("no completed runs matched")

    expected_seeds = {canonical_value(seed) for seed in args.seed}
    group_seeds = defaultdict(set)
    for row in rows:
        group_seeds[row["exclusion_set"]].add(canonical_value(row["seed"]))
    incomplete = {
        group: expected_seeds - seeds
        for group, seeds in group_seeds.items()
        if seeds != expected_seeds
    }
    if incomplete:
        parser.error(f"incomplete seed coverage: {incomplete}")

    histories = [
        read_history(
            resolve_run_dir(args.run_root, row),
            row["exclusion_set"],
            row["seed"],
        )
        for row in rows
    ]
    selected = select_common_epoch(histories, args.window)
    print(
        f"runs={len(histories)} groups={len(group_seeds)} "
        f"seeds={','.join(sorted(expected_seeds))}"
    )
    print_report(histories, selected, args.window)


if __name__ == "__main__":
    main()
