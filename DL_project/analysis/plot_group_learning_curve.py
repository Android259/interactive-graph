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


PREVALENCE_TAGS = ("accuracy", "sensitivity", "specificity", "precision")


def discover_groups(table, filters):
    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return sorted(
        {
            row["exclusion_set"]
            for row in rows
            if row.get("run_status") == "complete"
            and all(
                value_matches(row.get(column, ""), expected)
                for column, expected in filters
            )
        }
    )


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
        f"{row['m']}_{row['HEADS']}_{row['seed']}_{row['lr']}_"
        f"{row['batch']}_{row['hiddim']}"
    )
    label = row.get("label", "").strip()
    if not label:
        raise ValueError(f"Missing label for run row: {row}")
    candidates = [
        run_root / label / row["exclusion_set"] / name,
    ]
    if row.get("architecture"):
        candidates.append(run_root / row["architecture"] / row["exclusion_set"] / name)
    for run_dir in candidates:
        if run_dir.is_dir():
            return run_dir
    raise ValueError(
        "Run directory not found. Tried: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


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


def try_read_series(run_dir, tag):
    try:
        return read_series(run_dir, tag)
    except ValueError as error:
        print(f"Skipping {run_dir}: {error}")
        return None


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


def epoch_prevalence(accuracy, sensitivity, specificity, precision):
    """Recover the positive-class fraction pi from one epoch of confusion metrics.

    TensorBoard stores no class counts, so pi = P / (P + N) is solved for
    algebraically from the scalars that are logged. Writing the confusion matrix
    as fractions of the whole split (TP + FP + TN + FN = 1):

        TP = sens * pi           FN = (1 - sens) * pi
        TN = spec * (1 - pi)     FP = (1 - spec) * (1 - pi)

    Primary route -- accuracy is the pi-weighted mix of the two recalls:

        accuracy = TP + TN = sens * pi + spec * (1 - pi)
        =>  pi = (accuracy - spec) / (sens - spec)

    It is used only when |sens - spec| > 0.05. At sens == spec accuracy equals
    both recalls for every pi, so the identity degenerates (0/0) and the value
    carries no information about the prior.

    Fallback route -- precision, which stays informative when the recalls meet:

        precision = TP / (TP + FP) = sens * pi / (sens * pi + (1 - spec) * (1 - pi))
        =>  pi / (1 - pi) = (1 - spec) * precision / (sens * (1 - precision))

    solved through the odds and mapped back with pi = odds / (1 + odds). Epochs
    where that expression is undefined or unbounded (precision 0 or 1, sens 0,
    spec 1 -- a collapsed classifier predicting one class) yield None.

    Both routes describe the sample the metrics were computed on, so the result
    is the *effective* prevalence: with balanced_batches the train split comes
    back at 0.5 while the validation split reports its true composition.
    """
    if None not in (accuracy, sensitivity, specificity) and abs(sensitivity - specificity) > 0.05:
        prevalence = (accuracy - specificity) / (sensitivity - specificity)
    elif (
        None not in (sensitivity, specificity, precision)
        and 0.0 < precision < 1.0
        and sensitivity > 0.0
        and specificity < 1.0
    ):
        odds = (1.0 - specificity) * precision / (sensitivity * (1.0 - precision))
        prevalence = odds / (1.0 + odds)
    else:
        return None
    if not math.isfinite(prevalence) or not 0.0 < prevalence < 1.0:
        return None
    return prevalence


def estimate_prevalence(series_by_tag):
    """Return the median per-epoch positive fraction implied by one split's metrics.

    pi is constant across epochs by construction -- the split does not change --
    so every epoch is an independent estimate of the same quantity. The median
    is taken rather than the mean because early epochs and collapse phases push
    single estimates to the degenerate ends, and it stays robust as long as most
    epochs are well conditioned. Epochs that yield no estimate are dropped.
    """
    epochs = sorted(series_by_tag.get("accuracy", {}) or series_by_tag.get("sensitivity", {}))
    estimates = []
    for epoch in epochs:
        prevalence = epoch_prevalence(
            *(series_by_tag.get(name, {}).get(epoch) for name in PREVALENCE_TAGS)
        )
        if prevalence is not None:
            estimates.append(prevalence)
    if not estimates:
        return None
    return statistics.median(estimates)


def random_baseline(metric, prevalence, positive_rate="half"):
    """Return the value a coin-flipping classifier reaches for one metric.

    The reference classifier ignores its input and calls a sample positive with
    probability p, independently of the true label. Its predictions are then
    independent of y, so with prevalence pi the confusion matrix in fractions of
    the split is exactly the product of the marginals:

        TP = p * pi              FP = p * (1 - pi)
        FN = (1 - p) * pi        TN = (1 - p) * (1 - pi)

    which gives each metric in closed form:

        sensitivity = TP / pi                        = p
        specificity = TN / (1 - pi)                  = 1 - p
        balanced_accuracy = (sens + spec) / 2        = 0.5      (any p, any pi)
        precision = TP / (TP + FP)                   = pi       (any p)
        accuracy = TP + TN     = p * pi + (1 - p) * (1 - pi)
        F1 = 2 * prec * sens / (prec + sens)         = 2 * p * pi / (p + pi)

    Note which baselines move: balanced_accuracy is pinned at 0.5 no matter the
    class balance, and precision is pinned at pi no matter the policy -- so on a
    skewed split a "high" precision or F1 can still sit below chance.

    ``positive_rate`` picks p, it is a choice of reference policy rather than
    something estimated: ``half`` sets p = 0.5 (fair coin, the usual convention),
    ``prevalence`` sets p = pi (a coin weighted to the class prior, under which
    sens = pi, spec = 1 - pi, and F1 = pi).
    """
    if metric == "loss":
        return None
    if prevalence is None:
        # Only prevalence-free baselines remain well defined.
        if metric == "balanced_accuracy":
            return 0.5
        if metric in ("sensitivity", "specificity") and positive_rate == "half":
            return 0.5
        return None
    rate = prevalence if positive_rate == "prevalence" else 0.5
    if metric == "balanced_accuracy":
        return 0.5
    if metric == "sensitivity":
        return rate
    if metric == "specificity":
        return 1.0 - rate
    if metric == "precision":
        return prevalence
    if metric == "accuracy":
        return rate * prevalence + (1.0 - rate) * (1.0 - prevalence)
    if metric == "F1":
        if rate + prevalence == 0.0:
            return 0.0
        return 2.0 * rate * prevalence / (rate + prevalence)
    return None


def baseline_lines(metric, prevalences, positive_rate="half"):
    """Return ``(label, value, color)`` baseline lines, merged when splits agree.

    Train and validation carry their own prevalence, so pi-dependent baselines
    (precision, F1, accuracy) need one line per split, drawn in the colour of the
    curve it applies to. Where the baseline is pi-free the two values coincide
    and a single neutral line is drawn instead of two overlapping ones.
    """
    values = {
        split: random_baseline(metric, prevalence, positive_rate)
        for split, prevalence in prevalences.items()
    }
    train, valid = values.get("train"), values.get("valid")
    if train is not None and valid is not None and abs(train - valid) < 1e-9:
        return [("random baseline", train, "#404040")]
    lines = []
    for split, color in (("train", "#4472C4"), ("valid", "#C00000")):
        value = values.get(split)
        if value is not None:
            lines.append((f"random baseline ({split})", value, color))
    return lines


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
    prevalences=None,
    baseline_rate="half",
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

    if baseline_rate != "none":
        for label, value, color in baseline_lines(
            metric,
            prevalences or {},
            baseline_rate,
        ):
            axis.axhline(
                value,
                color=color,
                linestyle=(0, (1, 2)),
                linewidth=1.6,
                alpha=0.85,
                label=f"{label} = {value:.3f}",
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
    if metric != "loss":
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
        "--baseline-rate",
        choices=("half", "prevalence", "none"),
        default="half",
        help=(
            "Random classifier used for the baseline line: 'half' flips a fair "
            "coin, 'prevalence' predicts positive at the class prior, 'none' "
            "draws no baseline."
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
            f"{first.get('label', '')} | {weight_mode} | lr={first['lr']} | "
            f"weight_decay={first['weight_decay']} | final_m={first['final_m']} | "
            f"final_dropout={first['final_dropout']} | hiddim={first['hiddim']} | "
            f"heads={first['HEADS']} | batch={first['batch']} | "
            f"seeds={','.join(sorted(seeds))}"
        )
        _, selection_tag = METRIC_SERIES["balanced_accuracy"]
        selection_histories = []
        for run_dir in run_dirs:
            valid_series = try_read_series(run_dir, selection_tag)
            if valid_series is not None:
                selection_histories.append({"valid": valid_series})
        selection_curve = aggregate_histories(selection_histories, "valid")

        prevalences = {}
        if args.baseline_rate != "none":
            # Matched seeds share one split, so their estimates differ only by
            # estimation noise and are averaged; train and valid are kept apart
            # because their class balance genuinely differs.
            for split in ("train", "valid"):
                per_run = []
                for run_dir in run_dirs:
                    series_by_tag = {}
                    for name in PREVALENCE_TAGS:
                        try:
                            series_by_tag[name] = read_series(
                                run_dir, f"epoch/{split} {name}"
                            )
                        except ValueError:
                            series_by_tag[name] = {}
                    estimate = estimate_prevalence(series_by_tag)
                    if estimate is not None:
                        per_run.append(estimate)
                if per_run:
                    prevalences[split] = statistics.fmean(per_run)
            missing = [split for split in ("train", "valid") if split not in prevalences]
            if missing:
                print(
                    f"{group}: could not estimate {', '.join(missing)} class "
                    "prevalence; prevalence-dependent baselines are omitted"
                )

        for metric in metrics:
            train_tag, valid_tag = METRIC_SERIES[metric]
            histories = []
            for run_dir in run_dirs:
                train_series = try_read_series(run_dir, train_tag)
                valid_series = try_read_series(run_dir, valid_tag)
                if train_series is None or valid_series is None:
                    continue
                histories.append({"train": train_series, "valid": valid_series})
            if not histories:
                print(f"Skipping {group} {metric}: no runs with required TensorBoard tags")
                continue
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
                prevalences=prevalences,
                baseline_rate=args.baseline_rate,
            )
            print(
                f"Wrote {output}; runs={len(histories)}; "
                f"validation_epochs={len(valid_curve)}"
            )


if __name__ == "__main__":
    main()
