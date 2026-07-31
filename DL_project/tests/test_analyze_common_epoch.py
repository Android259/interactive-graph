import pytest

from analyze_common_epoch import rolling_mean, select_common_epoch


def history(group, seed, values):
    return {
        "group": group,
        "seed": seed,
        "valid_balanced_accuracy": {
            epoch: value for epoch, value in enumerate(values, start=1)
        },
    }


def test_rolling_mean_uses_trailing_window():
    values = {1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8}

    assert rolling_mean(values, 2, 3) == pytest.approx(0.3)
    assert rolling_mean(values, 4, 3) == pytest.approx(0.6)


def test_common_epoch_weights_groups_equally_after_averaging_seeds():
    histories = [
        history("A", "0", [0.5, 0.9, 0.4]),
        history("A", "1", [0.5, 0.7, 0.4]),
        history("B", "0", [0.5, 0.6, 0.9]),
    ]

    selected = select_common_epoch(histories, window=1)

    assert selected["epoch"] == 2
    assert selected["group_scores"]["A"] == pytest.approx(0.8)
    assert selected["group_scores"]["B"] == pytest.approx(0.6)
    assert selected["mean"] == pytest.approx(0.7)


def test_common_epoch_is_limited_to_shortest_run():
    histories = [
        history("A", "0", [0.5, 0.6]),
        history("B", "0", [0.5, 0.6, 1.0]),
    ]

    selected = select_common_epoch(histories, window=1)

    assert selected["epoch"] == 2
