import pytest

from training.run_metrics import (
    metric_has_positive_trend,
    rolling_metric_mean,
    summarize_training_run,
)


def epoch(train_ba, valid_ba, train_loss, valid_loss, predicted_positive=5, predicted_negative=5):
    return {
        "train": {
            "balanced_accuracy": train_ba,
            "loss": train_loss,
        },
        "valid": {
            "balanced_accuracy": valid_ba,
            "F1": valid_ba,
            "loss": valid_loss,
            "predicted_positive": predicted_positive,
            "predicted_negative": predicted_negative,
        },
    }


def test_summarize_training_run_uses_whole_history():
    history = [
        epoch(0.55, 0.52, 0.90, 0.95),
        epoch(0.65, 0.61, 0.70, 0.75),
        epoch(0.75, 0.58, 0.50, 0.80),
    ]

    summary = summarize_training_run(history, 12.5)

    assert summary["epochs_completed"] == 3
    assert summary["checkpoint_epoch"] == 2
    assert summary["checkpoint_valid_balanced_accuracy"] == pytest.approx(0.61)
    assert summary["checkpoint_rolling_valid_balanced_accuracy"] is None
    assert summary["max_valid_balanced_accuracy_epoch"] == 2
    assert summary["max_valid_balanced_accuracy"] == pytest.approx(0.61)
    assert summary["final_valid_balanced_accuracy"] == pytest.approx(0.58)
    assert summary["checkpoint_to_final_drop"] == pytest.approx(0.03)
    assert summary["mean_valid_balanced_accuracy"] == pytest.approx(0.57)
    assert summary["auc_valid_balanced_accuracy"] == pytest.approx(0.58)
    assert summary["train_loss_reduction"] == pytest.approx(0.40)
    assert summary["valid_loss_reduction"] == pytest.approx(0.15)
    assert summary["epochs_since_checkpoint"] == 1
    assert summary["overfitting_onset_epoch"] == 3
    assert summary["overfitting_epochs"] == 1
    assert summary["run_status"] == "complete"


def test_summarize_training_run_counts_collapsed_epochs():
    history = [
        epoch(0.5, 0.5, 0.8, 0.8, predicted_positive=10, predicted_negative=0),
        epoch(0.5, 0.5, 0.7, 0.7, predicted_positive=0, predicted_negative=10),
    ]

    summary = summarize_training_run(history, 2.0)

    assert summary["collapse_epoch_count"] == 2
    assert summary["valid_balanced_accuracy_std"] == 0.0


def test_rolling_metric_mean_uses_shorter_initial_window():
    history = [
        {"valid": {"balanced_accuracy": 0.5}},
        {"valid": {"balanced_accuracy": 0.6}},
        {"valid": {"balanced_accuracy": 0.7}},
    ]

    assert rolling_metric_mean(
        history, "valid", "balanced_accuracy", window=5
    ) == pytest.approx(0.6)


def test_rolling_metric_mean_uses_latest_five_epochs():
    history = [
        {"valid": {"balanced_accuracy": value}}
        for value in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
    ]

    assert rolling_metric_mean(
        history, "valid", "balanced_accuracy", window=5
    ) == pytest.approx(0.4)


def test_metric_has_positive_trend_requires_full_window():
    short_history = [
        {"valid": {"loss": float(value)}}
        for value in range(29)
    ]
    rising_history = [
        {"valid": {"loss": float(value)}}
        for value in range(30)
    ]
    falling_history = [
        {"valid": {"loss": float(30 - value)}}
        for value in range(30)
    ]

    assert not metric_has_positive_trend(
        short_history, "valid", "loss", window=30
    )
    assert metric_has_positive_trend(
        rising_history, "valid", "loss", window=30
    )
    assert not metric_has_positive_trend(
        falling_history, "valid", "loss", window=30
    )


def test_summary_uses_checkpoint_score_to_select_best_epoch():
    history = [
        epoch(0.5, 0.8, 0.8, 0.8),
        epoch(0.5, 0.6, 0.8, 0.8),
        epoch(0.5, 0.7, 0.8, 0.8),
    ]
    history[0]["valid"]["checkpoint_balanced_accuracy"] = 0.8
    history[1]["valid"]["checkpoint_balanced_accuracy"] = 0.7
    history[2]["valid"]["checkpoint_balanced_accuracy"] = 0.9

    summary = summarize_training_run(history, 3.0)

    assert summary["checkpoint_epoch"] == 3
    assert summary["checkpoint_valid_balanced_accuracy"] == pytest.approx(0.7)
    assert summary["checkpoint_rolling_valid_balanced_accuracy"] == pytest.approx(0.9)
    assert summary["max_valid_balanced_accuracy_epoch"] == 1
    assert summary["max_valid_balanced_accuracy"] == pytest.approx(0.8)
