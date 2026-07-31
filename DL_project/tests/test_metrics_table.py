import csv
from pathlib import Path
from types import SimpleNamespace

from add_new_metrics_to_table import add_new_metrics
from append_metric_to_table import append_metric
from analyze_metrics_table import build_analysis
from build_metrics_table import (
    CONFIG_FIELDS,
    metric_row,
    parse_metric_filename,
    read_tensorboard_summary,
    summarize_epoch_scalars,
    upsert_row,
)
from training.read_configuration import ModelConfig


REPORT = """\
best_epoch: 3
third_layers_in_mlps: 1
cross_attention: 0
protein_self_attention: 1
lipid_self_attention: 0
double_attention: 0
m: 4
lr: 0.001
hiddim: 128
ep: 3
seed: 0
excluded_groups: []
excluded_subgroups: ["RLBP1","GLTPD1"]
batch: 32
num_workers: 4
lipid_fragments_treatment: 0
protein_pooling: 0
lipid_concat: 1
lipid_random_choice: 0
lipid_fragments_mask: 0
lipid_isomers: 1
ordinary_prot_pooling: 1
prot_attention_pos_bias: 0
prot_pooling_by_pockets: 0
tanimoto_weight: 1
protein_group_weight: 0
grab_loss: 1
type_opt: 0
plmon: 1
buryon: 1
loss_type: 1
pool_type: 1
HEADS: 8
best_valid_balanced_accuracy: 0.750000
training_duration_sec: 12.500000
epochs_completed: 3
best_valid_F1: 0.700000
final_train_balanced_accuracy: 0.800000
final_valid_balanced_accuracy: 0.700000
best_to_final_drop: 0.050000
mean_valid_balanced_accuracy: 0.700000
auc_valid_balanced_accuracy: 0.710000
valid_balanced_accuracy_std: 0.020000
min_train_loss: 0.400000
final_train_loss: 0.400000
min_valid_loss: 0.600000
final_valid_loss: 0.650000
train_loss_reduction: 0.500000
valid_loss_reduction: 0.300000
epochs_to_best: 2
epochs_without_improvement: 1
mean_train_valid_gap: 0.100000
max_train_valid_gap: 0.150000
overfitting_onset_epoch: 3
overfitting_epochs: 1
nan_epoch_count: 0
collapse_epoch_count: 0
converged: 0
run_status: complete
total: 10
real_positive: 6
real_negative: 4
predicted_positive: 10
predicted_negative: 0
TP: 6
FP: 4
TN: 0
FN: 0
accuracy: 0.600000
sensitivity: 1.000000
precision: 0.600000
specificity: 0.000000
IoU: 0.600000
FAR: 1.000000
F1: 0.750000
balanced_accuracy: 0.500000
loss: 0.700000

per_protein_subgroup_metrics:
subgroup total
"""


def make_metric_file(root: Path) -> Path:
    path = (
        root
        / "base___"
        / "subgroups_RLBP1-GLTPD1"
        / "test_metrics_20260526_110112_3251086parameters_4_8_0_0.001_32_128.txt"
    )
    path.parent.mkdir(parents=True)
    path.write_text(REPORT, encoding="utf-8")
    return path


def test_parse_metric_filename():
    values = parse_metric_filename(
        Path("test_metrics_20260526_110112_3251086parameters_4_8_0_0.001_32_128.txt")
    )

    assert values["timestamp"] == "20260526_110112"
    assert values["number_of_parameters"] == "3251086"
    assert values["seed"] == "0"
    assert values["batch"] == "32"


def test_metric_row_extracts_configuration_and_warnings(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)

    row = metric_row(metric_file, metrics_root, tmp_path / "run", include_tensorboard=False)

    # The leading path part is still read to resolve the run directory, but runs are
    # identified by label now and it is no longer emitted as a column of its own.
    assert "architecture" not in row
    assert row["datetime"] == "2026-05-26 11:01:12"
    assert row["additional_layers"] == "1"
    assert row["third_layers_in_mlps"] == "1"
    assert row["protein_self_attention"] == "1"
    assert row["lipid_self_attention"] == "0"
    assert row["cross_attention"] == "0"
    assert row["pocket_attention"] == "0"
    assert row["lipid_isomers"] == "1"
    assert row["grab_loss"] == "1"
    assert row["class_weights"] == "1"
    assert row["HEADS"] == "8"
    assert row["exclusion_set"] == "subgroups_RLBP1-GLTPD1"
    assert row["balanced_accuracy"] == "0.500000"
    assert row["epochs_completed"] == "3"
    assert row["auc_valid_balanced_accuracy"] == "0.710000"
    assert row["training_sec_per_epoch"] == "4.166667"
    assert row["checkpoint_epoch"] == "3"
    assert row["checkpoint_valid_balanced_accuracy"] == "0.750000"
    assert row["checkpoint_to_final_drop"] == "0.050000"
    assert row["epochs_to_checkpoint"] == "2"
    assert row["epochs_since_checkpoint"] == "1"
    assert row["time_to_checkpoint_sec"] == "12.500000"
    assert row["collapse_fraction"] == "0.000000"
    assert row["label_positive_fraction"] == "0.600000"
    assert row["prediction_positive_fraction"] == "1.000000"
    assert "constant_positive" in row["warnings"]
    assert "class_imbalance>=1.5" in row["warnings"]


def test_summarize_epoch_scalars_calculates_stability_metrics():
    def events(values):
        return [
            SimpleNamespace(step=step, value=value)
            for step, value in enumerate(values, start=1)
        ]

    scalar_events = {
        "epoch/train balanced_accuracy": events(
            [0.55, 0.65, 0.75, 0.80, 0.85, 0.90]
        ),
        "epoch/valid balanced_accuracy": events(
            [0.50, 0.60, 0.70, 0.65, 0.55, 0.50]
        ),
        "epoch/valid F1": events([0.45, 0.55, 0.68, 0.60, 0.50, 0.45]),
        "epoch/valid loss": events([0.80, 0.70, 0.62, 0.65, 0.75, 0.85]),
        "epoch/valid sensitivity": events([0.50, 0.60, 0.80, 0.70, 0.50, 0.40]),
        "epoch/valid specificity": events([0.50, 0.60, 0.60, 0.60, 0.60, 0.60]),
    }

    summary = summarize_epoch_scalars(scalar_events)

    assert summary["checkpoint_epoch"] == "4"
    assert summary["checkpoint_valid_balanced_accuracy"] == "0.650000"
    assert (
        summary["checkpoint_rolling_valid_balanced_accuracy"]
        == "0.612500"
    )
    assert summary["max_valid_balanced_accuracy_epoch"] == "3"
    assert summary["max_valid_balanced_accuracy"] == "0.700000"
    assert summary["max_valid_epoch_F1"] == "0.680000"
    assert summary["max_valid_epoch_loss"] == "0.620000"
    assert summary["max_valid_epoch_train_valid_gap"] == "0.050000"
    assert (
        summary["max_valid_epoch_centered_window_balanced_accuracy_mean"]
        == "0.600000"
    )
    assert summary["top5_valid_balanced_accuracy_mean"] == "0.600000"
    assert summary["peak_width_001"] == "1"
    assert summary["post_best_balanced_accuracy_slope"] == "-0.070000"
    assert summary["valid_balanced_accuracy_oscillation"] == "0.080000"
    assert summary["max_valid_epoch_min_class_recall"] == "0.600000"
    assert summary["max_valid_epoch_class_recall_gap"] == "0.200000"
    assert summary["max_valid_epoch_gmean_recall"] == "0.692820"


def test_tensorboard_summary_rejects_ambiguous_event_directories(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "events.out.tfevents.first").touch()
    (run_dir / "events.out.tfevents.second").touch()

    summary = read_tensorboard_summary(run_dir)

    assert summary["tb_status"] == "ambiguous_multiple_event_files:2"
    assert (
        summary["max_valid_epoch_centered_window_balanced_accuracy_mean"]
        == ""
    )


def test_metric_row_maps_legacy_pocket_attention_field(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    metric_file.write_text(
        REPORT.replace(
            "prot_attention_pos_bias: 0",
            "prot_CA_for_pockets: 1",
        ),
        encoding="utf-8",
    )

    row = metric_row(
        metric_file,
        metrics_root,
        tmp_path / "run",
        include_tensorboard=False,
    )

    assert row["prot_attention_pos_bias"] == "1"
    assert row["pocket_attention"] == "1"


def test_metric_row_does_not_infer_config_from_filename_or_path(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    report_without_config = "\n".join(
        line for line in REPORT.splitlines()
        if not line.startswith(("m:", "lr:", "hiddim:", "seed:", "batch:", "HEADS:"))
    )
    metric_file.write_text(report_without_config, encoding="utf-8")

    row = metric_row(metric_file, metrics_root, tmp_path / "run", include_tensorboard=False)

    assert row["m"] == ""
    assert row["lr"] == ""
    assert row["hiddim"] == ""
    assert row["batch"] == ""
    assert row["HEADS"] == ""
    # seed is the documented exception: dedupe keys on the filename seed, so leaving the
    # column empty makes every rescan re-append the same row instead of matching it.
    assert row["seed"] == "0"


def test_upsert_replaces_existing_source_row(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    table = tmp_path / "metrics_summary.csv"
    row = metric_row(metric_file, metrics_root, tmp_path / "run", include_tensorboard=False)

    upsert_row(table, row)
    row["loss"] = "0.123000"
    upsert_row(table, row)

    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["loss"] == "0.123000"


def test_append_metric_writes_shared_table(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    table = tmp_path / "metrics_summary.csv"

    append_metric(
        metric_file,
        metrics_root=metrics_root,
        run_root=tmp_path / "run",
        table=table,
        include_tensorboard=False,
    )

    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["datetime"] == "2026-05-26 11:01:12"
    assert (tmp_path / "metrics_analysis.txt").exists()
    assert (tmp_path / "feature_contributions.csv").exists()


def test_append_metric_writes_values_from_config_object(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    metric_file.write_text(
        "\n".join(
            line for line in REPORT.splitlines()
            if not line.startswith(("grab_loss:", "lipid_isomers:", "batch:", "HEADS:"))
        ),
        encoding="utf-8",
    )
    table = tmp_path / "metrics_summary.csv"
    config = ModelConfig(grab_loss=True, lipid_isomers=True, batch=64, HEADS=4)

    append_metric(
        metric_file,
        metrics_root=metrics_root,
        run_root=tmp_path / "run",
        table=table,
        include_tensorboard=False,
        config=config,
    )

    with table.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
    # The table now mirrors every ModelConfig field, so run-environment settings like
    # num_workers come along too rather than being filtered out.
    assert "num_workers" in reader.fieldnames
    assert row["grab_loss"] == "1"
    assert row["lipid_isomers"] == "1"
    assert row["batch"] == "64"
    assert row["HEADS"] == "4"


def test_add_new_metrics_only_processes_reports_absent_from_table(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    metric_file = make_metric_file(metrics_root)
    table = tmp_path / "metrics_summary.csv"

    first_added = add_new_metrics(
        metrics_root,
        tmp_path / "run",
        table,
        include_tensorboard=False,
    )
    second_added = add_new_metrics(
        metrics_root,
        tmp_path / "run",
        table,
        include_tensorboard=False,
    )

    assert first_added == [metric_file]
    assert second_added == []
    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert (tmp_path / "metrics_analysis.txt").exists()
    assert (tmp_path / "feature_contributions.csv").exists()


def test_add_new_metrics_accepts_explicit_session_files(tmp_path):
    metrics_root = tmp_path / "test_metrics"
    first_metric = make_metric_file(metrics_root)
    second_metric = (
        metrics_root
        / "base___"
        / "groups_START"
        / "test_metrics_20260527_120000_3251086parameters_4_8_1_0.001_32_128.txt"
    )
    second_metric.parent.mkdir(parents=True)
    second_metric.write_text(REPORT, encoding="utf-8")
    table = tmp_path / "metrics_summary.csv"

    added = add_new_metrics(
        metrics_root,
        tmp_path / "run",
        table,
        include_tensorboard=False,
        metric_paths=[second_metric],
    )

    assert added == [second_metric]
    with table.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["exclusion_set"] == "groups_START"
    assert first_metric.exists()


def test_analysis_uses_validation_and_compares_exact_repeated_runs():
    base = {field: "0" for field in CONFIG_FIELDS}
    base.update({
        "architecture": "base___",
        "exclusion_set": "random",
        "seed": "0",
        "m": "4",
        "heads": "8",
        "lr": "0.001",
        "batch": "16",
        "hiddim": "128",
        "F1": "0.60",
        "loss": "0.70",
        "checkpoint_valid_balanced_accuracy": "0.55",
        "auc_valid_balanced_accuracy": "0.54",
        "checkpoint_to_final_drop": "0.02",
        "valid_balanced_accuracy_std": "0.03",
        "training_duration_sec": "10",
        "warnings": "",
        "epochs_completed": "3",
        "run_status": "complete",
    })
    previous = {
        **base,
        "datetime": "2026-01-01 10:00:00",
        "balanced_accuracy": "0.90",
        "checkpoint_valid_balanced_accuracy": "0.55",
    }
    current = {
        **base,
        "datetime": "2026-01-02 10:00:00",
        "balanced_accuracy": "0.60",
        "checkpoint_valid_balanced_accuracy": "0.65",
    }

    analysis = build_analysis([previous, current])

    assert "delta +0.100000, улучшение" in analysis
    assert "2026-01-01 10:00:00 -> 2026-01-02 10:00:00" in analysis
    assert "Модели ранжируются по validation-метрикам" in analysis


def test_analysis_reports_single_parameter_effect_per_dataset():
    base = {field: "0" for field in CONFIG_FIELDS}
    base.update({
        "exclusion_set": "dataset_A",
        "seed": "3",
        "grab_loss": "0",
        "checkpoint_valid_balanced_accuracy": "0.60",
        "balanced_accuracy": "0.95",
        "warnings": "",
        "run_status": "complete",
    })
    grab = {
        **base,
        "grab_loss": "1",
        "checkpoint_valid_balanced_accuracy": "0.70",
        "balanced_accuracy": "0.50",
    }

    analysis = build_analysis([base, grab])

    assert "dataset_A: grab_loss 0 -> 1: mean delta valid BA +0.100000" in analysis


def test_analysis_treats_linked_mode_flags_as_one_characteristic():
    base = {field: "0" for field in CONFIG_FIELDS}
    base.update({
        "exclusion_set": "dataset_A",
        "seed": "3",
        "lipid_fragments_treatment": "0",
        "lipid_concat": "1",
        "lipid_random_choice": "0",
        "checkpoint_valid_balanced_accuracy": "0.60",
        "run_status": "complete",
        "warnings": "",
    })
    random_fragment = {
        **base,
        "lipid_fragments_treatment": "1",
        "lipid_concat": "0",
        "lipid_random_choice": "1",
        "checkpoint_valid_balanced_accuracy": "0.70",
    }

    analysis = build_analysis([base, random_fragment])

    assert (
        "lipid_fragments_treatment 0 -> 1: mean delta valid BA +0.100000"
        in analysis
    )


def test_analysis_aggregates_latest_completed_run_per_seed():
    base = {field: "0" for field in CONFIG_FIELDS}
    base.update({
        "exclusion_set": "dataset_A",
        "run_status": "complete",
        "balanced_accuracy": "0.50",
        "warnings": "",
    })
    rows = [
        {**base, "seed": "1", "datetime": "2026-01-01", "checkpoint_valid_balanced_accuracy": "0.40"},
        {**base, "seed": "1", "datetime": "2026-01-02", "checkpoint_valid_balanced_accuracy": "0.60"},
        {**base, "seed": "2", "datetime": "2026-01-01", "checkpoint_valid_balanced_accuracy": "0.80"},
        {
            **base,
            "seed": "3",
            "datetime": "2026-01-03",
            "checkpoint_valid_balanced_accuracy": "0.99",
            "run_status": "interrupted",
        },
    ]

    analysis = build_analysis(rows)

    assert "valid BA=0.700000" in analysis
    assert "std=0.141421" in analysis
    assert "seeds=2 (1=0.600000, 2=0.800000)" in analysis
    assert "исключённые из рейтинга: 1" in analysis


def test_analysis_does_not_compare_incomplete_historical_configs():
    base = {
        "exclusion_set": "dataset_A",
        "seed": "0",
        "batch": "16",
        "checkpoint_valid_balanced_accuracy": "0.60",
        "warnings": "",
        "run_status": "complete",
    }
    changed = {
        **base,
        "batch": "32",
        "checkpoint_valid_balanced_accuracy": "0.70",
    }

    analysis = build_analysis([base, changed])

    assert "Нет matched-пар" in analysis
    assert "Повторных запусков с полностью совпадающими флагами" in analysis
