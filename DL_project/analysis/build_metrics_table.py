#!/usr/bin/env python3
"""Build a normalized CSV table from test reports and matching TensorBoard runs."""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import math
import os
import re
import statistics
import tempfile
from dataclasses import fields
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.pair_descriptors import parse_descriptor_list
from training.read_configuration import ModelConfig
from training.run_metrics import RUN_METRIC_FIELDS
MODEL_CONFIG_REPORT_FIELDS = tuple(field.name for field in fields(ModelConfig))
CONFIG_FIELDS = tuple(
    field_name for field_name in MODEL_CONFIG_REPORT_FIELDS
    if field_name != "label"
)
METRIC_FILENAME = re.compile(
    r"^test_metrics_(?P<timestamp>\d{8}_\d{6})_"
    r"(?P<number_of_parameters>\d+)parameters_"
    r"(?P<m>\d+)_(?P<heads>\d+)_(?P<seed>-?\d+)_"
    r"(?P<lr>[^_]+)_(?P<batch>\d+)_(?P<hiddim>\d+)\.txt$"
)
LOG_FILENAME = re.compile(r"^(?P<variant>.+)_seed(?P<seed>-?\d+)_ep\d+_batch\d+\.log$")

# Discovered hyperparameters written by a bilevel/gate discovery run, each a compact JSON
# keyed by module path ({module_name: value}) so it is clear which layer each value belongs
# to: surviving gate widths and per-layer Concrete Dropout rates. Aggregatable across
# seeds/excluded groups by analysis/aggregate_discovered_hparams.py.
DISCOVERED_FIELDS = (
    "discovered_widths",
    "discovered_dropout",
)

REPORT_FIELDS = (
    "label",
    *MODEL_CONFIG_REPORT_FIELDS,
    "prot_CA_for_pockets",
    *RUN_METRIC_FIELDS,
    *DISCOVERED_FIELDS,
    "best_epoch",
    "best_valid_balanced_accuracy",
    "best_to_final_drop",
    "epochs_to_best",
    "epochs_without_improvement",
    "total",
    "real_positive",
    "real_negative",
    "predicted_positive",
    "predicted_negative",
    "TP",
    "FP",
    "TN",
    "FN",
    "accuracy",
    "sensitivity",
    "precision",
    "specificity",
    "IoU",
    "FAR",
    "F1",
    "balanced_accuracy",
    "loss",
)

RUN_DERIVED_FIELDS = (
    "training_sec_per_epoch",
    "time_to_checkpoint_sec",
    "max_valid_epoch_F1",
    "max_valid_epoch_loss",
    "max_valid_epoch_sensitivity",
    "max_valid_epoch_specificity",
    "max_valid_epoch_train_valid_gap",
    "max_valid_epoch_centered_window_balanced_accuracy_mean",
    "top5_valid_balanced_accuracy_mean",
    "peak_width_001",
    "last10_valid_balanced_accuracy_mean",
    "last10_valid_balanced_accuracy_std",
    "post_best_balanced_accuracy_slope",
    "valid_balanced_accuracy_oscillation",
    "max_valid_epoch_min_class_recall",
    "max_valid_epoch_class_recall_gap",
    "max_valid_epoch_gmean_recall",
    "collapse_fraction",
    # Not ModelConfig fields themselves (protein_descriptors/lipid_descriptors/
    # descriptor_names ARE, and land in CONFIG_FIELDS by reflection already) -- these
    # three are the descriptor COUNT for each of the three named-catalog vectors a run
    # can build, recomputed from the saved name-list columns at table-build time rather
    # than cached anywhere, same reasoning as protein_node_feature_count's own comment
    # ("otherwise invisible" in the table without a dedicated column).
    "protein_descriptor_count",
    "lipid_descriptor_count",
    "pair_descriptor_head_count",
)

CSV_FIELDS = (
    "datetime",
    "label",
    "additional_layers",
    "pocket_attention",
    "exclusion_set",
    "number_of_parameters",
    *CONFIG_FIELDS,
    *RUN_METRIC_FIELDS,
    *RUN_DERIVED_FIELDS,
    *DISCOVERED_FIELDS,
    "total",
    "real_positive",
    "real_negative",
    "label_positive_fraction",
    "predicted_positive",
    "predicted_negative",
    "prediction_positive_fraction",
    "TP",
    "FP",
    "TN",
    "FN",
    "accuracy",
    "sensitivity",
    "precision",
    "specificity",
    "IoU",
    "FAR",
    "F1",
    "balanced_accuracy",
    "loss",
    "tb_status",
    "tb_train_points",
    "tb_valid_points",
    "tb_train_last_accuracy",
    "tb_train_last_balanced_accuracy",
    "tb_train_last_F1",
    "tb_train_last_loss",
    "tb_valid_last_accuracy",
    "tb_valid_last_balanced_accuracy",
    "tb_valid_last_F1",
    "tb_valid_last_loss",
    "tb_valid_best_balanced_accuracy",
    "tb_valid_min_loss",
    "tb_last_balanced_accuracy_gap",
    "warnings",
)

TB_TAGS = {
    "tb_train_last_accuracy": ("epoch/train accuracy", "train accuracy"),
    "tb_train_last_balanced_accuracy": (
        "epoch/train balanced_accuracy",
        "train balanced accuracy",
    ),
    "tb_train_last_F1": ("epoch/train F1", "train F1 score"),
    "tb_train_last_loss": ("epoch/train loss", "train loss"),
    "tb_valid_last_accuracy": ("epoch/valid accuracy", "valid accuracy"),
    "tb_valid_last_balanced_accuracy": (
        "epoch/valid balanced_accuracy",
        "valid balanced accuracy",
    ),
    "tb_valid_last_F1": ("epoch/valid F1", "valid F1 score"),
    "tb_valid_last_loss": ("epoch/valid loss", "valid loss"),
}

EPOCH_TAGS = {
    "train_balanced_accuracy": "epoch/train balanced_accuracy",
    "valid_balanced_accuracy": "epoch/valid balanced_accuracy",
    "valid_F1": "epoch/valid F1",
    "valid_loss": "epoch/valid loss",
    "valid_sensitivity": "epoch/valid sensitivity",
    "valid_specificity": "epoch/valid specificity",
}

ROW_KEY_FIELDS = (
    "datetime",
    "exclusion_set",
    "number_of_parameters",
    *CONFIG_FIELDS,
)


def parse_metric_filename(path: Path) -> dict[str, str]:
    match = METRIC_FILENAME.match(path.name)
    if match is None:
        raise ValueError(f"Unsupported metric filename: {path.name}")
    values = match.groupdict()
    values["run_id"] = path.stem.removeprefix("test_metrics_")
    return values


def resolve_label(
    script_logs_root: Path,
    exclusion_set: str,
    seed: str,
    run_timestamp: datetime,
) -> str:
    if not script_logs_root.is_dir():
        return ""

    exclusion_dir = exclusion_set.removeprefix("groups_")
    best_variant = ""
    best_delta = None
    for log_path in script_logs_root.glob(f"*/{exclusion_dir}/*_seed{seed}_ep*_batch*.log"):
        match = LOG_FILENAME.match(log_path.name)
        if match is None or match.group("seed") != str(seed):
            continue
        variant_dir = log_path.parent.parent.name
        if "_seeds" in variant_dir:
            variant = variant_dir.rsplit("_seeds", 1)[0]
        else:
            variant = match.group("variant")
        try:
            mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
        except OSError:
            continue
        delta = abs((mtime - run_timestamp).total_seconds())
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_variant = variant
    return best_variant


def format_datetime(timestamp: str) -> str:
    return datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")


def parse_report(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    undefined: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line == "per_protein_subgroup_metrics:":
                break
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            if key not in REPORT_FIELDS:
                continue
            value = raw_value.strip()
            if value.lower() in {"undefined", "nan", "none"}:
                values[key] = ""
                undefined.append(key)
            else:
                values[key] = value
    if "prot_CA_for_pockets" in values and "prot_attention_pos_bias" not in values:
        values["prot_attention_pos_bias"] = values.pop("prot_CA_for_pockets")
    legacy_names = {
        "best_epoch": "checkpoint_epoch",
        "best_valid_balanced_accuracy": "checkpoint_valid_balanced_accuracy",
        "best_to_final_drop": "checkpoint_to_final_drop",
        "epochs_to_best": "epochs_to_checkpoint",
        "epochs_without_improvement": "epochs_since_checkpoint",
    }
    for legacy_name, current_name in legacy_names.items():
        if legacy_name in values and current_name not in values:
            values[current_name] = values[legacy_name]
    if not values.get("final_m") and values.get("m"):
        values["final_m"] = values["m"]
        undefined = [key for key in undefined if key != "final_m"]
    return values, undefined


def serialize_config(config: ModelConfig) -> dict[str, str]:
    values = {}
    for field in fields(ModelConfig):
        value = getattr(config, field.name)
        if field.name == "final_m" and value is None:
            value = config.m
        if isinstance(value, bool):
            value = str(int(value))
        elif isinstance(value, list):
            value = json.dumps(value, separators=(",", ":"))
        else:
            value = str(value)
        values[field.name] = value
    return values


def _fraction(numerator: str, denominator: str) -> str:
    try:
        denominator_value = int(denominator)
        if denominator_value == 0:
            return ""
        return f"{int(numerator) / denominator_value:.6f}"
    except (TypeError, ValueError):
        return ""


def _finite_values(events) -> list[float]:
    return [event.value for event in events if math.isfinite(event.value)]


def _format_number(value) -> str:
    return "" if value is None or not math.isfinite(value) else f"{value:.6f}"


def _event_values_by_step(events) -> dict[int, float]:
    return {
        event.step: event.value
        for event in events
        if math.isfinite(event.value)
    }


def _linear_slope(points) -> float | None:
    if len(points) < 2:
        return None
    x_mean = statistics.fmean(step for step, _ in points)
    y_mean = statistics.fmean(value for _, value in points)
    denominator = sum((step - x_mean) ** 2 for step, _ in points)
    if denominator == 0:
        return None
    return sum(
        (step - x_mean) * (value - y_mean)
        for step, value in points
    ) / denominator


def summarize_epoch_scalars(scalar_events) -> dict[str, str]:
    """Calculate diagnostics from aggregate epoch TensorBoard scalars."""
    summary = {field: "" for field in RUN_DERIVED_FIELDS}
    series = {
        name: _event_values_by_step(scalar_events.get(tag, []))
        for name, tag in EPOCH_TAGS.items()
    }
    valid_balanced = series["valid_balanced_accuracy"]
    if not valid_balanced:
        return summary

    ordered = sorted(valid_balanced.items())
    best_step, best_value = max(ordered, key=lambda item: item[1])
    best_index = next(
        index for index, (step, _) in enumerate(ordered) if step == best_step
    )
    rolling_scores = [
        (
            step,
            statistics.fmean(
                value for _, value in ordered[max(0, index - 4):index + 1]
            ),
        )
        for index, (step, _) in enumerate(ordered)
    ]
    checkpoint_step, checkpoint_score = max(
        rolling_scores, key=lambda item: item[1]
    )
    summary["checkpoint_epoch"] = str(checkpoint_step)
    summary["checkpoint_valid_balanced_accuracy"] = _format_number(
        valid_balanced[checkpoint_step]
    )
    summary["checkpoint_rolling_valid_balanced_accuracy"] = _format_number(
        checkpoint_score
    )

    def value_at(name):
        return series[name].get(best_step)

    best_f1 = value_at("valid_F1")
    best_loss = value_at("valid_loss")
    sensitivity = value_at("valid_sensitivity")
    specificity = value_at("valid_specificity")
    train_balanced = value_at("train_balanced_accuracy")
    summary["max_valid_balanced_accuracy_epoch"] = str(best_step)
    summary["max_valid_balanced_accuracy"] = _format_number(best_value)
    summary["max_valid_epoch_F1"] = _format_number(best_f1)
    summary["max_valid_epoch_loss"] = _format_number(best_loss)
    summary["max_valid_epoch_sensitivity"] = _format_number(sensitivity)
    summary["max_valid_epoch_specificity"] = _format_number(specificity)
    if train_balanced is not None:
        summary["max_valid_epoch_train_valid_gap"] = _format_number(
            train_balanced - best_value
        )

    window = ordered[max(0, best_index - 2):best_index + 3]
    summary["max_valid_epoch_centered_window_balanced_accuracy_mean"] = _format_number(
        statistics.fmean(value for _, value in window)
    )
    summary["top5_valid_balanced_accuracy_mean"] = _format_number(
        statistics.fmean(sorted(valid_balanced.values(), reverse=True)[:5])
    )
    summary["peak_width_001"] = str(
        sum(value >= best_value - 0.01 for value in valid_balanced.values())
    )

    recent = [value for _, value in ordered[-10:]]
    summary["last10_valid_balanced_accuracy_mean"] = _format_number(
        statistics.fmean(recent)
    )
    summary["last10_valid_balanced_accuracy_std"] = _format_number(
        statistics.pstdev(recent) if len(recent) > 1 else 0.0
    )
    summary["post_best_balanced_accuracy_slope"] = _format_number(
        _linear_slope(ordered[best_index:])
    )
    summary["valid_balanced_accuracy_oscillation"] = _format_number(
        statistics.fmean(
            abs(current[1] - previous[1])
            for previous, current in zip(ordered, ordered[1:])
        )
        if len(ordered) > 1
        else 0.0
    )

    if sensitivity is not None and specificity is not None:
        summary["max_valid_epoch_min_class_recall"] = _format_number(
            min(sensitivity, specificity)
        )
        summary["max_valid_epoch_class_recall_gap"] = _format_number(
            abs(sensitivity - specificity)
        )
        summary["max_valid_epoch_gmean_recall"] = _format_number(
            math.sqrt(sensitivity * specificity)
        )
    return summary


def read_tensorboard_summary(run_dir: Path) -> dict[str, str]:
    summary = {
        field: ""
        for field in CSV_FIELDS
        if field.startswith("tb_")
        or field in RUN_DERIVED_FIELDS
        or field in {
            "max_valid_balanced_accuracy_epoch",
            "max_valid_balanced_accuracy",
        }
    }
    if not run_dir.is_dir():
        summary["tb_status"] = "missing"
        return summary

    event_files = list(run_dir.glob("events.out.tfevents.*"))
    if len(event_files) > 1:
        summary["tb_status"] = f"ambiguous_multiple_event_files:{len(event_files)}"
        return summary

    try:
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    except ImportError:
        summary["tb_status"] = "tensorboard_unavailable"
        return summary

    try:
        accumulator = EventAccumulator(str(run_dir), size_guidance={"scalars": 0})
        accumulator.Reload()
        available = set(accumulator.Tags().get("scalars", []))
        requested_tags = {
            tag
            for candidates in TB_TAGS.values()
            for tag in candidates
        } | set(EPOCH_TAGS.values())
        scalar_events = {
            tag: accumulator.Scalars(tag)
            for tag in requested_tags
            if tag in available
        }
    except Exception as error:
        summary["tb_status"] = f"read_error:{type(error).__name__}"
        return summary

    if not scalar_events:
        summary["tb_status"] = "no_scalars"
        return summary

    summary["tb_status"] = "ok"
    summary.update(summarize_epoch_scalars(scalar_events))
    summary["tb_train_points"] = str(
        next(
            (
                len(scalar_events[tag])
                for tag in (
                    "epoch/train balanced_accuracy",
                    "train balanced accuracy",
                )
                if tag in scalar_events
            ),
            0,
        )
    )
    summary["tb_valid_points"] = str(
        next(
            (
                len(scalar_events[tag])
                for tag in (
                    "epoch/valid balanced_accuracy",
                    "valid balanced accuracy",
                )
                if tag in scalar_events
            ),
            0,
        )
    )

    for field, candidates in TB_TAGS.items():
        finite = next(
            (
                values
                for tag in candidates
                if (values := _finite_values(scalar_events.get(tag, [])))
            ),
            [],
        )
        if finite:
            summary[field] = f"{finite[-1]:.6f}"

    valid_balanced = next(
        (
            values
            for tag in TB_TAGS["tb_valid_last_balanced_accuracy"]
            if (values := _finite_values(scalar_events.get(tag, [])))
        ),
        [],
    )
    valid_loss = next(
        (
            values
            for tag in TB_TAGS["tb_valid_last_loss"]
            if (values := _finite_values(scalar_events.get(tag, [])))
        ),
        [],
    )
    if valid_balanced:
        summary["tb_valid_best_balanced_accuracy"] = f"{max(valid_balanced):.6f}"
    if valid_loss:
        summary["tb_valid_min_loss"] = f"{min(valid_loss):.6f}"

    try:
        train_value = float(summary["tb_train_last_balanced_accuracy"])
        valid_value = float(summary["tb_valid_last_balanced_accuracy"])
        summary["tb_last_balanced_accuracy_gap"] = f"{train_value - valid_value:.6f}"
    except ValueError:
        pass
    return summary


def _safe_path_part(value: str) -> str:
    value = value.strip()
    if not value:
        return "unknown_label"
    value = re.sub(r"[^A-Za-z0-9._=-]+", "_", value)
    value = value.strip("._")
    if not value:
        return "unknown_label"
    return value


def _resolve_run_dir(
    run_root: Path,
    label: str,
    architecture: str,
    exclusion_set: str,
    run_id: str,
) -> Path:
    new_dir = run_root.resolve() / _safe_path_part(label) / exclusion_set / f"train{run_id}"
    if new_dir.is_dir():
        return new_dir
    return run_root.resolve() / architecture / exclusion_set / f"train{run_id}"


def metric_row(
    metric_path: Path,
    metrics_root: Path,
    run_root: Path,
    include_tensorboard: bool = True,
    config: ModelConfig | None = None,
    script_logs_root: Path | None = None,
) -> dict[str, str]:
    metric_path = Path(metric_path)
    metrics_root = Path(metrics_root)
    run_root = Path(run_root)
    metric_path = metric_path.resolve()
    metrics_root = metrics_root.resolve()
    relative_path = metric_path.relative_to(metrics_root)
    if len(relative_path.parts) < 3:
        raise ValueError(f"Metric path lacks label/exclusion directories: {relative_path}")

    filename_values = parse_metric_filename(metric_path)
    report_values, undefined = parse_report(metric_path)
    architecture = relative_path.parts[0]
    exclusion_set = "/".join(relative_path.parts[1:-1])
    label = report_values.get("label", "")
    if config is not None:
        label = str(getattr(config, "label", "") or label)
    run_dir = _resolve_run_dir(
        run_root,
        label,
        architecture,
        exclusion_set,
        filename_values["run_id"],
    )

    row = {field: "" for field in CSV_FIELDS}
    row.update(
        {
            "exclusion_set": exclusion_set,
            "datetime": format_datetime(filename_values["timestamp"]),
            "number_of_parameters": filename_values["number_of_parameters"],
            **report_values,
        }
    )
    if "class_weights" not in report_values:
        # Legacy runs always applied class weights before the option was configurable.
        row["class_weights"] = "1"
    if config is not None:
        row.update(serialize_config(config))
        label = getattr(config, "label", "")
        if label and not row.get("label"):
            row["label"] = str(label)
    if not row.get("seed"):
        # Reports written before the seed line existed leave this empty, but the
        # filename always encodes the seed. add_new_metrics_to_table dedupes on
        # the FILENAME seed, so an empty column here never matches the computed
        # key and every rescan re-appends the same rows -- once per poll, forever.
        row["seed"] = filename_values["seed"]
    if not row.get("label") and script_logs_root is not None:
        row["label"] = resolve_label(
            Path(script_logs_root),
            exclusion_set,
            filename_values["seed"],
            datetime.strptime(filename_values["timestamp"], "%Y%m%d_%H%M%S"),
        )
    row["additional_layers"] = row["third_layers_in_mlps"]
    row["pocket_attention"] = row["prot_attention_pos_bias"]
    row["label_positive_fraction"] = _fraction(row["real_positive"], row["total"])
    row["prediction_positive_fraction"] = _fraction(row["predicted_positive"], row["total"])
    # protein_descriptors/lipid_descriptors/descriptor_names are ModelConfig fields
    # (CONFIG_FIELDS above) and land in the row by serialize_config's reflection
    # already -- these three are just their COUNT, recomputed from that same string at
    # table-build time so it does not need its own ModelConfig field.
    row["protein_descriptor_count"] = str(
        len(parse_descriptor_list(row.get("protein_descriptors", "")))
    )
    row["lipid_descriptor_count"] = str(
        len(parse_descriptor_list(row.get("lipid_descriptors", "")))
    )
    row["pair_descriptor_head_count"] = (
        str(len(parse_descriptor_list(row.get("descriptor_names", ""))))
        if row.get("pair_descriptors") == "1" and row.get("descriptor_names")
        else ""
    )

    warnings = []
    if undefined:
        warnings.append("undefined:" + ",".join(sorted(undefined)))
    if row["total"] and row["predicted_positive"] == row["total"]:
        warnings.append("constant_positive")
    if row["total"] and row["predicted_negative"] == row["total"]:
        warnings.append("constant_negative")
    try:
        positive = int(row["real_positive"])
        negative = int(row["real_negative"])
        if min(positive, negative) > 0 and max(positive, negative) / min(positive, negative) >= 1.5:
            warnings.append("class_imbalance>=1.5")
    except ValueError:
        pass

    if include_tensorboard:
        row.update(read_tensorboard_summary(run_dir))
        if row["tb_status"] == "ok" and row["tb_valid_points"] == "0":
            warnings.append("no_validation_history")
        if row["tb_status"].startswith("ambiguous_multiple_event_files:"):
            warnings.append(row["tb_status"])
    else:
        row["tb_status"] = "not_read"

    try:
        epochs_completed = int(row["epochs_completed"])
        training_duration = float(row["training_duration_sec"])
        if epochs_completed > 0 and math.isfinite(training_duration):
            row["training_sec_per_epoch"] = (
                f"{training_duration / epochs_completed:.6f}"
            )
            checkpoint_epoch = int(row["checkpoint_epoch"])
            row["time_to_checkpoint_sec"] = (
                f"{training_duration * checkpoint_epoch / epochs_completed:.6f}"
            )
    except (TypeError, ValueError):
        pass

    try:
        epochs_completed = int(row["epochs_completed"])
        collapse_epochs = int(row["collapse_epoch_count"])
        if epochs_completed > 0:
            row["collapse_fraction"] = (
                f"{collapse_epochs / epochs_completed:.6f}"
            )
    except (TypeError, ValueError):
        pass

    row["warnings"] = ";".join(warnings)
    return row


def read_table(table_path: Path) -> list[dict[str, str]]:
    if not table_path.exists():
        return []
    with table_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    legacy_names = {
        "best_epoch": "checkpoint_epoch",
        "best_valid_balanced_accuracy": "checkpoint_valid_balanced_accuracy",
        "best_to_final_drop": "checkpoint_to_final_drop",
        "epochs_to_best": "epochs_to_checkpoint",
        "epochs_without_improvement": "epochs_since_checkpoint",
        "time_to_best_sec": "time_to_checkpoint_sec",
        "best_epoch_valid_F1": "max_valid_epoch_F1",
        "best_epoch_valid_loss": "max_valid_epoch_loss",
        "best_epoch_valid_sensitivity": "max_valid_epoch_sensitivity",
        "best_epoch_valid_specificity": "max_valid_epoch_specificity",
        "best_epoch_train_valid_gap": "max_valid_epoch_train_valid_gap",
        "best_epoch_window_balanced_accuracy_mean": (
            "max_valid_epoch_centered_window_balanced_accuracy_mean"
        ),
        "best_epoch_valid_min_class_recall": (
            "max_valid_epoch_min_class_recall"
        ),
        "best_epoch_valid_class_recall_gap": (
            "max_valid_epoch_class_recall_gap"
        ),
        "best_epoch_valid_gmean_recall": "max_valid_epoch_gmean_recall",
    }
    for row in rows:
        for legacy_name, current_name in legacy_names.items():
            if row.get(legacy_name, "") and not row.get(current_name, ""):
                row[current_name] = row[legacy_name]
    return rows


def write_table(table_path: Path, rows: list[dict[str, str]]) -> None:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda row: tuple(row.get(field, "") for field in ROW_KEY_FIELDS))
    with tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        encoding="utf-8",
        dir=table_path.parent,
        prefix=f".{table_path.name}.",
        delete=False,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, table_path)
    table_path.chmod(0o664)


def upsert_row(table_path: Path, row: dict[str, str]) -> None:
    """Read-modify-write table_path with one row inserted or replaced by its key.

    Locked with flock on a sibling file: write_table's tempfile+os.replace already
    makes one write atomic, but without this lock two processes finishing close
    together (scripts/run_local.sh runs several training jobs at once, each
    calling this on completion) can both read the table before either writes,
    and the second write silently drops the first process's row.
    """
    table_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(f"{table_path}.lock")
    with open(lock_path, "w") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        try:
            rows = read_table(table_path)
            by_key = {
                tuple(existing.get(field, "") for field in ROW_KEY_FIELDS): existing
                for existing in rows
            }
            row_key = tuple(row.get(field, "") for field in ROW_KEY_FIELDS)
            by_key[row_key] = row
            write_table(table_path, list(by_key.values()))
        finally:
            fcntl.flock(lock_handle, fcntl.LOCK_UN)


def build_table(
    metrics_root: Path,
    run_root: Path,
    output: Path,
    include_tensorboard: bool = True,
    script_logs_root: Path | None = None,
) -> list[dict[str, str]]:
    rows = [
        metric_row(
            path,
            metrics_root,
            run_root,
            include_tensorboard,
            script_logs_root=script_logs_root,
        )
        for path in sorted(metrics_root.rglob("test_metrics_*.txt"))
    ]
    write_table(output, rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics-root", type=Path, default=PROJECT_ROOT / "test_metrics")
    parser.add_argument("--run-root", type=Path, default=PROJECT_ROOT / "run")
    parser.add_argument("--script-logs-root", type=Path, default=PROJECT_ROOT / "script_logs")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument("--no-tensorboard", action="store_true")
    args = parser.parse_args()

    rows = build_table(
        args.metrics_root,
        args.run_root,
        args.output,
        include_tensorboard=not args.no_tensorboard,
        script_logs_root=args.script_logs_root,
    )
    from analyze_metrics_table import update_analysis
    from analyze_feature_contributions import write_feature_contributions

    update_analysis(args.output, args.output.with_name("metrics_analysis.txt"))
    write_feature_contributions(
        args.output,
        args.output.with_name("feature_contributions.csv"),
        "checkpoint_valid_balanced_accuracy",
    )
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
