#!/usr/bin/env python3
"""Plot whole-group learning curves averaged across matched seeds."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path

from analyze_common_epoch import (
    canonical_value,
    value_matches,
)
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


METRIC_SERIES = {
    "balanced_accuracy": (
        "epoch/train balanced_accuracy",
        "epoch/valid balanced_accuracy",
    ),
    "F1": ("epoch/train F1", "epoch/valid F1"),
    "sensitivity": ("epoch/train sensitivity", "epoch/valid sensitivity"),
    "specificity": ("epoch/train specificity", "epoch/valid specificity"),
    "precision": ("epoch/train precision", "epoch/valid precision"),
    "loss": ("epoch/train loss", "epoch/valid loss"),
}


def latest_matching_rows(table, filters, seeds):
    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    matching = []
    for row in rows:
        if row.get("run_status") != "complete":
            continue
        if not row.get("final_m"):
            row["final_m"] = row.get("m", "")
        if not row.get("final_dropout"):
            row["final_dropout"] = "0.0"
        for field in ("protein_class_weight", "protein_class_sqrt_weight"):
            if not row.get(field):
                row[field] = "0"
        if canonical_value(row.get("seed")) not in seeds:
            continue
        if all(
            value_matches(row.get(column, ""), expected)
            for column, expected in filters
        ):
            matching.append(row)

    latest = {}
    for row in sorted(matching, key=lambda item: item["datetime"]):
        key = (row["exclusion_set"], canonical_value(row["seed"]))
        latest[key] = row
    return list(latest.values())


def resolve_exact_run_dir(run_root, row):
    timestamp = row["datetime"].replace("-", "").replace(":", "").replace(" ", "_")
    name = (
        f"train{timestamp}_{row['number_of_parameters']}parameters_"
        f"{row['m']}_{row['heads']}_{row['seed']}_{row['lr']}_"
        f"{row['batch']}_{row['hiddim']}"
    )
    run_dir = run_root / row["architecture"] / row["exclusion_set"] / name
    if not run_dir.is_dir():
        raise ValueError(f"Run directory not found: {run_dir}")
    return run_dir


def read_series(run_dir, tag):
    event_files = list(run_dir.glob("events.out.tfevents.*"))
    if len(event_files) != 1:
        raise ValueError(f"Expected one event file in {run_dir}, found {len(event_files)}")
    accumulator = EventAccumulator(str(run_dir), size_guidance={"scalars": 0})
    accumulator.Reload()
    if tag not in accumulator.Tags().get("scalars", []):
        raise ValueError(f"Missing TensorBoard tag {tag!r} in {run_dir}")
    return {
        event.step: event.value
        for event in accumulator.Scalars(tag)
        if math.isfinite(event.value)
    }


def aggregate_histories(histories, series_name):
    """Return per-epoch mean, SD, and seed count for one TensorBoard series."""
    epochs = sorted(
        {
            epoch
            for history in histories
            for epoch in history.get(series_name, {})
        }
    )
    result = []
    for epoch in epochs:
        values = [
            history[series_name][epoch]
            for history in histories
            if epoch in history.get(series_name, {})
            and math.isfinite(history[series_name][epoch])
        ]
        if not values:
            continue
        result.append(
            {
                "epoch": epoch,
                "mean": statistics.fmean(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "count": len(values),
            }
        )
    return result


def best_validation_window(valid_curve, window=5, min_count=3):
    """Return the best validation epoch selected by a shared trailing window."""
    if not valid_curve:
        return None
    best = None
    for index, item in enumerate(valid_curve):
        window_points = valid_curve[max(0, index - window + 1) : index + 1]
        if item["count"] < min_count or any(
            point["count"] < min_count for point in window_points
        ):
            continue
        values = [point["mean"] for point in window_points if math.isfinite(point["mean"])]
        window_mean = statistics.fmean(values)
        candidate = {
            "epoch": item["epoch"],
            "value": item["mean"],
            "window_mean": window_mean,
            "window_count": len(values),
            "seed_count": item["count"],
            "min_seed_count": min(point["count"] for point in window_points),
        }
        if best is None or window_mean > best["window_mean"]:
            best = candidate
    return best


def window_mean_at_epoch(curve, epoch, window=5, min_count=1):
    """Return trailing window mean ending at one epoch when coverage is sufficient."""
    epoch_to_index = {item["epoch"]: index for index, item in enumerate(curve)}
    if epoch not in epoch_to_index:
        return None
    index = epoch_to_index[epoch]
    window_points = curve[max(0, index - window + 1) : index + 1]
    if any(point["count"] < min_count for point in window_points):
        return None
    values = [point["mean"] for point in window_points if math.isfinite(point["mean"])]
    if not values:
        return None
    return statistics.fmean(values)


def plot_curve(
    train_curve,
    valid_curve,
    metric,
    group,
    config_label,
    output,
    histories=None,
    min_window_seeds=3,
    selection_curve=None,
):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(11, 6.5))
    if histories:
        labeled = False
        for history in histories:
            valid_history = history.get("valid", {})
            epochs = sorted(valid_history)
            if not epochs:
                continue
            axis.plot(
                epochs,
                [valid_history[epoch] for epoch in epochs],
                color="#C00000",
                linestyle=(0, (2, 2)),
                linewidth=0.8,
                alpha=0.32,
                label="validation seeds" if not labeled else None,
            )
            labeled = True

    for curve, label, color in (
        (train_curve, "train", "#4472C4"),
        (valid_curve, "validation", "#C00000"),
    ):
        if not curve:
            continue
        epochs = [item["epoch"] for item in curve]
        means = [item["mean"] for item in curve]
        stds = [item["std"] for item in curve]
        axis.plot(epochs, means, label=label, color=color, linewidth=2)
        axis.fill_between(
            epochs,
            [mean - std for mean, std in zip(means, stds)],
            [mean + std for mean, std in zip(means, stds)],
            color=color,
            alpha=0.18,
        )

    if selection_curve is None:
        selection_curve = valid_curve
    best_window = best_validation_window(
        selection_curve,
        min_count=min_window_seeds,
    )
    if best_window is not None:
        metric_window_mean = window_mean_at_epoch(
            valid_curve,
            best_window["epoch"],
            min_count=1,
        )
        annotation = (
            f"best shared BA epoch {best_window['epoch']}\n"
            f"BA window mean={best_window['window_mean']:.4f}\n"
            f"seeds>={best_window['min_seed_count']}"
        )
        if metric != "balanced_accuracy" and metric_window_mean is not None:
            annotation = f"{annotation}\n{metric} mean={metric_window_mean:.4f}"
        axis.axvline(
            best_window["epoch"],
            color="#404040",
            linestyle="--",
            linewidth=1.4,
            alpha=0.9,
            label="best validation window",
        )
        axis.annotate(
            annotation,
            xy=(best_window["epoch"], 0),
            xycoords=("data", "axes fraction"),
            xytext=(0, -32),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
            color="#404040",
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": "white",
                "edgecolor": "#BFBFBF",
                "alpha": 0.92,
            },
        )

    axis.set_xlabel("Epoch")
    axis.set_ylabel(metric)
    axis.set_ylim(top=1.0)
    axis.set_title(
        f"{group}: mean {metric} learning curve across seeds\n{config_label}",
        fontsize=10,
    )
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.subplots_adjust(bottom=0.18)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=Path("metrics_summary.csv"))
    parser.add_argument("--run-root", type=Path, default=Path("run"))
    parser.add_argument("--group")
    parser.add_argument("--all-groups", action="store_true")
    parser.add_argument(
        "--metric",
        action="append",
        choices=METRIC_SERIES,
        default=[],
    )
    parser.add_argument("--seed", action="append", default=[])
    parser.add_argument("--filter", action="append", default=[])
    parser.add_argument(
        "--min-window-seeds",
        type=int,
        default=3,
        help=(
            "Minimum seed count required for every epoch in the selected "
            "validation window."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("group_learning_curve.pdf"),
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--output-format",
        choices=("pdf",),
        default="pdf",
        help="Output format. Only PDF is supported.",
    )
    args = parser.parse_args()

    if not args.seed:
        parser.error("provide at least one --seed")
    if args.all_groups == bool(args.group):
        parser.error("provide exactly one of --group or --all-groups")
    if args.all_groups and args.output_dir is None:
        parser.error("--all-groups requires --output-dir")
    if args.min_window_seeds < 1:
        parser.error("--min-window-seeds must be at least 1")

    filters = []
    for expression in args.filter:
        if "=" not in expression:
            parser.error(f"expected FIELD=VALUE filter, got {expression!r}")
        filters.append(expression.split("=", 1))
    seeds = {canonical_value(seed) for seed in args.seed}
    groups = (
        [
            "groups_CRAL-TRIO",
            "groups_GLTP",
            "groups_IP_trans",
            "groups_LBP_BPI_CETP",
            "groups_ML",
            "groups_OSBP",
            "groups_START",
            "groups_lipocalin",
            "groups_scp2",
        ]
        if args.all_groups
        else [
            args.group
            if args.group.startswith("groups_")
            else f"groups_{args.group}"
        ]
    )
    metrics = args.metric or ["balanced_accuracy"]

    for group in groups:
        rows = latest_matching_rows(
            args.table,
            [*filters, ("exclusion_set", group)],
            seeds,
        )
        if not rows:
            parser.error(f"no completed runs matched {group}")
        found_seeds = {canonical_value(row["seed"]) for row in rows}
        if found_seeds != seeds:
            parser.error(f"{group} missing seeds: {sorted(seeds - found_seeds)}")

        run_dirs = [resolve_exact_run_dir(args.run_root, row) for row in rows]
        first = rows[0]
        weight_mode = "no class weights"
        if first.get("class_weights") == "1":
            weight_mode = "class weights"
        elif first.get("protein_class_weight") == "1":
            weight_mode = "protein class weights: inverse"
        elif first.get("protein_class_sqrt_weight") == "1":
            weight_mode = "protein class weights: sqrt"
        config_label = (
            f"{first['architecture']} | {weight_mode} | lr={first['lr']} | "
            f"weight_decay={first['weight_decay']} | final_m={first['final_m']} | "
            f"final_dropout={first['final_dropout']} | hiddim={first['hiddim']} | "
            f"heads={first['heads']} | batch={first['batch']} | "
            f"seeds={','.join(sorted(seeds))}"
        )
        _, selection_tag = METRIC_SERIES["balanced_accuracy"]
        selection_histories = [
            {"valid": read_series(run_dir, selection_tag)}
            for run_dir in run_dirs
        ]
        selection_curve = aggregate_histories(selection_histories, "valid")

        for metric in metrics:
            train_tag, valid_tag = METRIC_SERIES[metric]
            histories = [
                {
                    "train": read_series(run_dir, train_tag),
                    "valid": read_series(run_dir, valid_tag),
                }
                for run_dir in run_dirs
            ]
            train_curve = aggregate_histories(histories, "train")
            valid_curve = aggregate_histories(histories, "valid")
            if args.output_dir is not None:
                output = (
                    args.output_dir
                    / group.removeprefix("groups_")
                    / f"{metric}.{args.output_format}"
                )
            else:
                output = args.output.with_suffix(f".{args.output_format}")
            plot_curve(
                train_curve,
                valid_curve,
                metric,
                group.removeprefix("groups_"),
                config_label,
                output,
                histories=histories,
                min_window_seeds=args.min_window_seeds,
                selection_curve=selection_curve,
            )
            print(
                f"Wrote {output}; runs={len(histories)}; "
                f"validation_epochs={len(valid_curve)}"
            )


if __name__ == "__main__":
    main()
