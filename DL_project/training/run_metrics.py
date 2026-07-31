"""Pure helpers for summarizing an entire training run."""

from __future__ import annotations

import math
import statistics


RUN_METRIC_FIELDS = (
    "training_duration_sec",
    "epochs_completed",
    "checkpoint_epoch",
    "checkpoint_valid_balanced_accuracy",
    "checkpoint_rolling_valid_balanced_accuracy",
    "max_valid_balanced_accuracy_epoch",
    "max_valid_balanced_accuracy",
    "best_valid_F1",
    "final_train_balanced_accuracy",
    "final_valid_balanced_accuracy",
    "checkpoint_to_final_drop",
    "mean_valid_balanced_accuracy",
    "auc_valid_balanced_accuracy",
    "valid_balanced_accuracy_std",
    "min_train_loss",
    "final_train_loss",
    "min_valid_loss",
    "final_valid_loss",
    "train_loss_reduction",
    "valid_loss_reduction",
    "epochs_to_checkpoint",
    "epochs_since_checkpoint",
    "mean_train_valid_gap",
    "max_train_valid_gap",
    "overfitting_onset_epoch",
    "overfitting_epochs",
    "nan_epoch_count",
    "collapse_epoch_count",
    "converged",
    "run_status",
)


def _finite(value):
    """Return whether a metric value exists and is finite."""
    return value is not None and math.isfinite(value)


def _series(history, section, metric):
    """Extract finite values for one metric from an epoch history."""
    return [
        epoch[section].get(metric)
        for epoch in history
        if _finite(epoch[section].get(metric))
    ]


def _normalized_auc(values):
    """Compute trapezoidal AUC normalized by the number of epoch intervals."""
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    area = sum((left + right) / 2 for left, right in zip(values, values[1:]))
    return area / (len(values) - 1)


def rolling_metric_mean(epoch_history, section, metric, window=5):
    """Return the mean of the latest finite metric values within one window."""
    values = _series(epoch_history[-window:], section, metric)
    return statistics.fmean(values) if values else None


def metric_has_positive_trend(epoch_history, section, metric, window=30):
    """Return whether the metric has a positive least-squares trend over a full window."""
    values = _series(epoch_history[-window:], section, metric)
    if len(values) < window:
        return False
    center = (window - 1) / 2
    numerator = sum((index - center) * value for index, value in enumerate(values))
    denominator = sum((index - center) ** 2 for index in range(window))
    return numerator / denominator > 0


def summarize_training_run(epoch_history, training_duration_sec, run_status="complete"):
    """Summarize convergence, performance, and overfitting across all epochs."""
    summary = {field: None for field in RUN_METRIC_FIELDS}
    summary["training_duration_sec"] = training_duration_sec
    summary["epochs_completed"] = len(epoch_history)
    summary["run_status"] = run_status
    if not epoch_history:
        summary["nan_epoch_count"] = 0
        summary["collapse_epoch_count"] = 0
        summary["overfitting_epochs"] = 0
        summary["converged"] = False
        return summary

    valid_balanced = _series(epoch_history, "valid", "balanced_accuracy")
    valid_f1 = _series(epoch_history, "valid", "F1")
    train_loss = _series(epoch_history, "train", "loss")
    valid_loss = _series(epoch_history, "valid", "loss")

    selection_metric = (
        "checkpoint_balanced_accuracy"
        if any(
            _finite(epoch["valid"].get("checkpoint_balanced_accuracy"))
            for epoch in epoch_history
        )
        else "balanced_accuracy"
    )
    checkpoint_candidates = [
        (index, epoch["valid"].get(selection_metric))
        for index, epoch in enumerate(epoch_history)
        if _finite(epoch["valid"].get(selection_metric))
    ]
    if checkpoint_candidates:
        checkpoint_index, checkpoint_score = max(
            checkpoint_candidates, key=lambda item: item[1]
        )
        checkpoint_value = epoch_history[checkpoint_index]["valid"].get(
            "balanced_accuracy"
        )
        summary["checkpoint_epoch"] = checkpoint_index + 1
        summary["epochs_to_checkpoint"] = checkpoint_index + 1
        summary["epochs_since_checkpoint"] = (
            len(epoch_history) - checkpoint_index - 1
        )
        summary["checkpoint_valid_balanced_accuracy"] = checkpoint_value
        if selection_metric == "checkpoint_balanced_accuracy":
            summary["checkpoint_rolling_valid_balanced_accuracy"] = checkpoint_score

    max_candidates = [
        (index, epoch["valid"].get("balanced_accuracy"))
        for index, epoch in enumerate(epoch_history)
        if _finite(epoch["valid"].get("balanced_accuracy"))
    ]
    if max_candidates:
        max_index, max_value = max(max_candidates, key=lambda item: item[1])
        summary["max_valid_balanced_accuracy_epoch"] = max_index + 1
        summary["max_valid_balanced_accuracy"] = max_value

    if valid_f1:
        summary["best_valid_F1"] = max(valid_f1)
    if valid_balanced:
        final_valid = epoch_history[-1]["valid"].get("balanced_accuracy")
        summary["final_valid_balanced_accuracy"] = final_valid if _finite(final_valid) else None
        if _finite(summary["checkpoint_valid_balanced_accuracy"]) and _finite(final_valid):
            summary["checkpoint_to_final_drop"] = (
                summary["checkpoint_valid_balanced_accuracy"] - final_valid
            )
        summary["mean_valid_balanced_accuracy"] = statistics.fmean(valid_balanced)
        summary["auc_valid_balanced_accuracy"] = _normalized_auc(valid_balanced)
        summary["valid_balanced_accuracy_std"] = (
            statistics.pstdev(valid_balanced) if len(valid_balanced) > 1 else 0.0
        )

    final_train_balanced = epoch_history[-1]["train"].get("balanced_accuracy")
    summary["final_train_balanced_accuracy"] = (
        final_train_balanced if _finite(final_train_balanced) else None
    )

    if train_loss:
        summary["min_train_loss"] = min(train_loss)
        summary["final_train_loss"] = train_loss[-1]
        summary["train_loss_reduction"] = train_loss[0] - train_loss[-1]
    if valid_loss:
        summary["min_valid_loss"] = min(valid_loss)
        summary["final_valid_loss"] = valid_loss[-1]
        summary["valid_loss_reduction"] = valid_loss[0] - valid_loss[-1]

    gaps = []
    overfitting_epochs = []
    for index, epoch in enumerate(epoch_history):
        train_value = epoch["train"].get("balanced_accuracy")
        valid_value = epoch["valid"].get("balanced_accuracy")
        if _finite(train_value) and _finite(valid_value):
            gaps.append(train_value - valid_value)
        if index > 0:
            previous = epoch_history[index - 1]
            previous_train = previous["train"].get("balanced_accuracy")
            previous_valid = previous["valid"].get("balanced_accuracy")
            if (
                _finite(train_value)
                and _finite(valid_value)
                and _finite(previous_train)
                and _finite(previous_valid)
                and train_value > previous_train
                and valid_value < previous_valid
            ):
                overfitting_epochs.append(index + 1)

    if gaps:
        summary["mean_train_valid_gap"] = statistics.fmean(gaps)
        summary["max_train_valid_gap"] = max(gaps)
    summary["overfitting_epochs"] = len(overfitting_epochs)
    summary["overfitting_onset_epoch"] = overfitting_epochs[0] if overfitting_epochs else None

    summary["nan_epoch_count"] = sum(
        any(
            value is not None and isinstance(value, (int, float)) and not math.isfinite(value)
            for section in ("train", "valid")
            for value in epoch[section].values()
        )
        for epoch in epoch_history
    )
    summary["collapse_epoch_count"] = sum(
        epoch["valid"].get("predicted_positive") == 0
        or epoch["valid"].get("predicted_negative") == 0
        for epoch in epoch_history
    )
    recent = valid_balanced[-3:]
    summary["converged"] = len(recent) == 3 and max(recent) - min(recent) <= 0.01
    return summary
