import csv

from analyze_feature_contributions import (
    OUTPUT_FIELDS,
    calculate_feature_contributions,
    write_feature_contributions,
)
from build_metrics_table import CONFIG_FIELDS


def _row(seed, score, **changes):
    row = {field: "0" for field in CONFIG_FIELDS}
    row.update({
        "datetime": "2026-01-01",
        "exclusion_set": "dataset_A",
        "seed": str(seed),
        "run_status": "complete",
        "checkpoint_valid_balanced_accuracy": str(score),
    })
    row.update({key: str(value) for key, value in changes.items()})
    return row


def test_calculates_feature_effect_statistics_across_seeds():
    rows = [
        _row(1, 0.60, grab_loss=0),
        _row(1, 0.70, grab_loss=1),
        _row(2, 0.50, grab_loss=0),
        _row(2, 0.55, grab_loss=1),
    ]

    result = calculate_feature_contributions(rows)

    assert len(result) == 1
    effect = result[0]
    assert effect["feature_group"] == "objective"
    assert effect["feature"] == "grab_loss"
    assert effect["baseline_value"] == "0"
    assert effect["comparison_value"] == "1"
    assert effect["matched_pairs"] == "2"
    assert effect["seed_count"] == "2"
    assert effect["seeds"] == "1,2"
    assert effect["mean_delta"] == "0.075000"
    assert effect["median_delta"] == "0.075000"
    assert effect["std_delta"] == "0.035355"
    assert effect["improved_pairs"] == "2"
    assert effect["improved_fraction"] == "1.000000"


def test_linked_boolean_mode_flags_do_not_block_canonical_comparison():
    concat = _row(
        1,
        0.60,
        lipid_fragments_treatment=0,
        lipid_concat=1,
        lipid_random_choice=0,
    )
    random_choice = {
        **concat,
        "checkpoint_valid_balanced_accuracy": "0.65",
        "lipid_fragments_treatment": "1",
        "lipid_concat": "0",
        "lipid_random_choice": "1",
    }

    result = calculate_feature_contributions([concat, random_choice])

    assert len(result) == 1
    assert result[0]["feature"] == "lipid_fragments_treatment"
    assert result[0]["mean_delta"] == "0.050000"


def test_uses_latest_completed_run_and_skips_incomplete_rows():
    old = _row(1, 0.40, grab_loss=0)
    latest = {
        **old,
        "datetime": "2026-01-02",
        "checkpoint_valid_balanced_accuracy": "0.60",
    }
    enabled = _row(1, 0.70, grab_loss=1)
    interrupted = _row(2, 0.95, grab_loss=1, run_status="interrupted")

    result = calculate_feature_contributions([old, latest, enabled, interrupted])

    assert len(result) == 1
    assert result[0]["mean_delta"] == "0.100000"
    assert result[0]["seed_count"] == "1"


def test_writes_header_when_no_matched_pairs(tmp_path):
    table = tmp_path / "metrics.csv"
    output = tmp_path / "contributions.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                *CONFIG_FIELDS,
                "datetime",
                "exclusion_set",
                "run_status",
                "checkpoint_valid_balanced_accuracy",
            ],
        )
        writer.writeheader()
        writer.writerow(_row(1, 0.60))

    result = write_feature_contributions(
        table,
        output,
        "checkpoint_valid_balanced_accuracy",
    )

    assert result == []
    with output.open(newline="", encoding="utf-8") as handle:
        assert next(csv.reader(handle)) == list(OUTPUT_FIELDS)
