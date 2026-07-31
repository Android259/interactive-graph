import pytest

from plot_group_learning_curve import aggregate_histories, best_validation_window
from plot_group_learning_curve import window_mean_at_epoch
from analysis.plot_group_learning_curve import (
    baseline_lines,
    epoch_prevalence,
    estimate_prevalence,
    random_baseline,
)


def test_aggregate_histories_uses_available_seeds_per_epoch():
    histories = [
        {"valid": {1: 0.4, 2: 0.6}},
        {"valid": {1: 0.8}},
    ]

    curve = aggregate_histories(histories, "valid")

    assert curve[0]["epoch"] == 1
    assert curve[0]["mean"] == pytest.approx(0.6)
    assert curve[0]["count"] == 2
    assert curve[1] == {"epoch": 2, "mean": 0.6, "std": 0.0, "count": 1}


def test_best_validation_window_uses_trailing_mean():
    curve = [
        {"epoch": 1, "mean": 0.2, "count": 5},
        {"epoch": 2, "mean": 0.9, "count": 5},
        {"epoch": 3, "mean": 0.2, "count": 5},
        {"epoch": 4, "mean": 0.7, "count": 5},
        {"epoch": 5, "mean": 0.8, "count": 5},
    ]

    best = best_validation_window(curve, window=2)

    assert best["epoch"] == 5
    assert best["value"] == pytest.approx(0.8)
    assert best["window_mean"] == pytest.approx(0.75)
    assert best["window_count"] == 2


def test_best_validation_window_ignores_low_coverage_tail():
    curve = [
        {"epoch": 1, "mean": 0.6, "count": 5},
        {"epoch": 2, "mean": 0.7, "count": 5},
        {"epoch": 3, "mean": 0.95, "count": 1},
        {"epoch": 4, "mean": 0.96, "count": 1},
    ]

    best = best_validation_window(curve, window=2, min_count=3)

    assert best["epoch"] == 2
    assert best["window_mean"] == pytest.approx(0.65)
    assert best["min_seed_count"] == 5


def test_window_mean_at_epoch_requires_coverage():
    curve = [
        {"epoch": 1, "mean": 0.4, "count": 3},
        {"epoch": 2, "mean": 0.6, "count": 2},
        {"epoch": 3, "mean": 0.8, "count": 3},
    ]

    assert window_mean_at_epoch(curve, 3, window=2, min_count=2) == pytest.approx(0.7)
    assert window_mean_at_epoch(curve, 3, window=2, min_count=3) is None


def confusion_metrics(true_positive, false_positive, true_negative, false_negative):
    positives = true_positive + false_negative
    negatives = true_negative + false_positive
    return {
        "accuracy": (true_positive + true_negative) / (positives + negatives),
        "sensitivity": true_positive / positives,
        "specificity": true_negative / negatives,
        "precision": true_positive / (true_positive + false_positive),
    }


def test_epoch_prevalence_recovers_class_prior():
    # 300 positives, 700 negatives.
    metrics = confusion_metrics(
        true_positive=240,
        false_positive=140,
        true_negative=560,
        false_negative=60,
    )

    prevalence = epoch_prevalence(**metrics)

    assert prevalence == pytest.approx(0.3)


def test_epoch_prevalence_falls_back_to_precision_when_recalls_match():
    # sensitivity == specificity leaves accuracy uninformative about the prior.
    metrics = confusion_metrics(
        true_positive=240,
        false_positive=140,
        true_negative=560,
        false_negative=60,
    )
    metrics["accuracy"] = None

    assert epoch_prevalence(**metrics) == pytest.approx(0.3)


def test_epoch_prevalence_rejects_degenerate_epochs():
    assert epoch_prevalence(1.0, 1.0, 1.0, 1.0) is None
    assert epoch_prevalence(0.5, 0.5, 0.5, 0.0) is None


def test_estimate_prevalence_takes_median_over_epochs():
    series_by_tag = {
        "accuracy": {1: 0.8, 2: 0.75, 3: 0.85},
        "sensitivity": {1: 0.9, 2: 0.9, 3: 0.9},
        "specificity": {1: 0.7, 2: 0.7, 3: 0.7},
        "precision": {1: 0.0, 2: 0.0, 3: 0.0},
    }

    assert estimate_prevalence(series_by_tag) == pytest.approx(0.5)


def test_random_baseline_coin_flip():
    assert random_baseline("balanced_accuracy", 0.2) == pytest.approx(0.5)
    assert random_baseline("sensitivity", 0.2) == pytest.approx(0.5)
    assert random_baseline("specificity", 0.2) == pytest.approx(0.5)
    assert random_baseline("precision", 0.2) == pytest.approx(0.2)
    assert random_baseline("F1", 0.2) == pytest.approx(2 * 0.5 * 0.2 / 0.7)
    assert random_baseline("loss", 0.2) is None


def test_random_baseline_at_class_prior():
    assert random_baseline("sensitivity", 0.2, "prevalence") == pytest.approx(0.2)
    assert random_baseline("specificity", 0.2, "prevalence") == pytest.approx(0.8)
    assert random_baseline("F1", 0.2, "prevalence") == pytest.approx(0.2)
    assert random_baseline("accuracy", 0.2, "prevalence") == pytest.approx(0.68)


def test_random_baseline_without_prevalence_drops_prior_dependent_metrics():
    assert random_baseline("balanced_accuracy", None) == pytest.approx(0.5)
    assert random_baseline("sensitivity", None) == pytest.approx(0.5)
    assert random_baseline("precision", None) is None
    assert random_baseline("sensitivity", None, "prevalence") is None


def test_baseline_lines_merge_when_splits_agree():
    lines = baseline_lines("balanced_accuracy", {"train": 0.5, "valid": 0.3})

    assert lines == [("random baseline", 0.5, "#404040")]


def test_baseline_lines_split_when_prevalence_differs():
    lines = baseline_lines("precision", {"train": 0.5, "valid": 0.3})

    assert [label for label, _, _ in lines] == [
        "random baseline (train)",
        "random baseline (valid)",
    ]
    assert [value for _, value, _ in lines] == pytest.approx([0.5, 0.3])
