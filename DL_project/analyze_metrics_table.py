#!/usr/bin/env python3
"""Build a validation-based comparison report from metrics_summary.csv."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from analysis.build_metrics_table import CONFIG_FIELDS, PROJECT_ROOT


DATASET_FIELD = "exclusion_set"
REPLICATE_FIELD = "seed"
CONFIG_FIELD_GROUPS = {
    "architecture": (
        "third_layers_in_mlps",
        "cross_attention",
        "protein_self_attention",
        "lipid_self_attention",
        "double_attention",
        "m",
        "final_m",
        "final_dropout",
        "hiddim",
        "pool_type",
        "heads",
    ),
    "data_representation": (
        "lipid_fragments_treatment",
        "protein_pooling",
        "lipid_isomers",
        "plmon",
        "buryon",
    ),
    "objective": (
        "tanimoto_weight",
        "class_weights",
        "protein_group_weight",
        "grab_loss",
        "loss_type",
    ),
    "optimization": ("lr", "ep", "batch", "type_opt"),
}
COMPARISON_FIELDS = tuple(
    field
    for group in CONFIG_FIELD_GROUPS.values()
    for field in group
)
EXACT_RUN_FIELDS = (DATASET_FIELD, *COMPARISON_FIELDS, REPLICATE_FIELD)
VALIDATION_FIELDS = (
    (
        "checkpoint_rolling_valid_balanced_accuracy",
        "checkpoint rolling valid BA",
        True,
    ),
    ("checkpoint_valid_balanced_accuracy", "checkpoint valid BA", True),
    ("max_valid_balanced_accuracy", "max valid BA", True),
    ("auc_valid_balanced_accuracy", "valid BA AUC", True),
    ("checkpoint_to_final_drop", "checkpoint-to-final drop", False),
    ("valid_balanced_accuracy_std", "valid BA std", False),
)


def _number(row, field):
    try:
        value = float(row.get(field, ""))
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _key(row, fields):
    return tuple(row.get(field, "") for field in fields)


def _has_complete_config(row):
    return all(row.get(field, "") != "" for field in CONFIG_FIELDS)


def _is_complete_run(row):
    return row.get("run_status", "") == "complete"


def _latest_by(rows, fields):
    latest = {}
    for row in sorted(rows, key=lambda item: item.get("datetime", "")):
        latest[_key(row, fields)] = row
    return list(latest.values())


def _format(value):
    return "N/A" if value is None else f"{value:.6f}"


def _validation_score(row):
    value = _number(row, "checkpoint_rolling_valid_balanced_accuracy")
    if value is not None:
        return value, "checkpoint rolling mean"
    value = _number(row, "checkpoint_valid_balanced_accuracy")
    if value is not None:
        return value, "checkpoint epoch"
    value = _number(row, "tb_valid_best_balanced_accuracy")
    if value is not None:
        return value, "TensorBoard legacy"
    return None, "unavailable"


def _config_name(row):
    groups = []
    for group_name, fields in CONFIG_FIELD_GROUPS.items():
        values = [
            f"{field}={row[field]}"
            for field in fields
            if row.get(field, "") != ""
        ]
        if values:
            groups.append(f"{group_name}[{', '.join(values)}]")
    return "; ".join(groups) or "configuration unavailable"


def _aggregate_configurations(rows):
    grouped = defaultdict(list)
    complete_rows = [
        row for row in rows
        if _is_complete_run(row) and _validation_score(row)[0] is not None
    ]
    for row in complete_rows:
        config_key = _key(row, (DATASET_FIELD, *COMPARISON_FIELDS))
        if not _has_complete_config(row):
            config_key = (*config_key, row.get("datetime", ""), row.get("number_of_parameters", ""))
        grouped[config_key].append(row)

    aggregates = []
    for group_rows in grouped.values():
        seed_rows = _latest_by(group_rows, (REPLICATE_FIELD,))
        scores = [_validation_score(row)[0] for row in seed_rows]
        if not scores:
            continue
        test_scores = [
            value for row in seed_rows
            if (value := _number(row, "balanced_accuracy")) is not None
        ]
        aggregates.append({
            "row": seed_rows[0],
            "validation_mean": statistics.fmean(scores),
            "validation_std": statistics.stdev(scores) if len(scores) > 1 else None,
            "test_mean": statistics.fmean(test_scores) if test_scores else None,
            "runs": len(group_rows),
            "seeds": len(seed_rows),
            "seed_values": ", ".join(
                f"{row.get(REPLICATE_FIELD, '?')}={_validation_score(row)[0]:.6f}"
                for row in sorted(seed_rows, key=lambda item: item.get(REPLICATE_FIELD, ""))
            ),
        })
    return aggregates


def _matched_effects(rows):
    effects = defaultdict(list)
    usable = [
        row for row in rows
        if _has_complete_config(row)
        and _is_complete_run(row)
        and _validation_score(row)[0] is not None
    ]
    usable = _latest_by(usable, (DATASET_FIELD, *COMPARISON_FIELDS, REPLICATE_FIELD))
    for index, left in enumerate(usable):
        for right in usable[index + 1:]:
            if left.get(DATASET_FIELD, "") != right.get(DATASET_FIELD, ""):
                continue
            if left.get(REPLICATE_FIELD, "") != right.get(REPLICATE_FIELD, ""):
                continue
            differing = [
                field for field in COMPARISON_FIELDS
                if left.get(field, "") != right.get(field, "")
            ]
            if len(differing) != 1:
                continue
            field = differing[0]
            left_value = left.get(field, "")
            right_value = right.get(field, "")
            if left_value == "" or right_value == "":
                continue
            left_score = _validation_score(left)[0]
            right_score = _validation_score(right)[0]
            if left_value > right_value:
                left_value, right_value = right_value, left_value
                left_score, right_score = right_score, left_score
            delta = right_score - left_score
            effects[(left[DATASET_FIELD], field, left_value, right_value)].append(delta)
    return effects


def _change_line(current, previous, field, label, higher_is_better):
    current_value = _number(current, field)
    previous_value = _number(previous, field)
    if current_value is None or previous_value is None:
        return f"- {label}: сравнение недоступно"
    delta = current_value - previous_value
    if abs(delta) < 1e-12:
        assessment = "без изменения"
    elif (delta > 0) == higher_is_better:
        assessment = "улучшение"
    else:
        assessment = "ухудшение"
    return (
        f"- {label}: {_format(previous_value)} -> {_format(current_value)} "
        f"(delta {delta:+.6f}, {assessment})"
    )


def build_analysis(rows):
    lines = [
        "# Сравнительный анализ моделей",
        "",
        f"Всего экспериментов: {len(rows)}.",
        (
            "Модели ранжируются по validation-метрикам. Test используется только для "
            "описания обобщения уже выбранных конфигураций."
        ),
    ]
    if not rows:
        return "\n".join(lines + ["", "Данных для анализа нет."]) + "\n"

    aggregates = _aggregate_configurations(rows)
    datasets = sorted({row.get(DATASET_FIELD, "") for row in rows})
    lines.extend(["", "## Качество по датасетам"])
    for dataset in datasets:
        dataset_configs = [
            item for item in aggregates
            if item["row"].get(DATASET_FIELD, "") == dataset
        ]
        dataset_configs.sort(key=lambda item: item["validation_mean"], reverse=True)
        lines.extend(["", f"### {dataset or 'dataset не указан'}"])
        if not dataset_configs:
            lines.append("- Validation-метрики отсутствуют; ранжирование невозможно.")
            continue
        for rank, item in enumerate(dataset_configs, start=1):
            std = _format(item["validation_std"])
            lines.append(
                f"- {rank}. valid BA={item['validation_mean']:.6f}, std={std}, "
                f"test BA={_format(item['test_mean'])}, runs={item['runs']}, "
                f"seeds={item['seeds']} ({item['seed_values']}); {_config_name(item['row'])}."
            )

    lines.extend(["", "## Влияние характеристик конфигурации"])
    effects = _matched_effects(rows)
    if not effects:
        lines.append(
            "- Нет matched-пар, которые отличаются ровно одним параметром при одинаковых "
            "датасете, seed и остальных настройках."
        )
    else:
        for (dataset, field, before, after), deltas in sorted(effects.items()):
            mean_delta = statistics.fmean(deltas)
            spread = statistics.stdev(deltas) if len(deltas) > 1 else None
            lines.append(
                f"- {dataset}: {field} {before} -> {after}: mean delta valid BA "
                f"{mean_delta:+.6f}, std={_format(spread)}, matched pairs={len(deltas)}."
            )

    exact_groups = defaultdict(list)
    for row in sorted(rows, key=lambda item: item.get("datetime", "")):
        if not _has_complete_config(row) or not _is_complete_run(row):
            continue
        exact_groups[_key(row, EXACT_RUN_FIELDS)].append(row)
    lines.extend(["", "## Повторные запуски той же конфигурации"])
    repeated = False
    for group_rows in exact_groups.values():
        if len(group_rows) < 2:
            continue
        repeated = True
        current, previous = group_rows[-1], group_rows[-2]
        lines.extend([
            "",
            f"### {current.get(DATASET_FIELD, '')}: {_config_name(current)}",
            f"- {previous.get('datetime', '')} -> {current.get('datetime', '')}",
        ])
        lines.extend(
            _change_line(current, previous, field, label, higher_is_better)
            for field, label, higher_is_better in VALIDATION_FIELDS
        )
    if not repeated:
        lines.append("- Повторных запусков с полностью совпадающими флагами и seed нет.")

    undefined = sum("undefined:" in row.get("warnings", "") for row in rows)
    collapsed = sum(
        "constant_positive" in row.get("warnings", "")
        or "constant_negative" in row.get("warnings", "")
        for row in rows
    )
    incomplete_config = sum(any(row.get(field, "") == "" for field in CONFIG_FIELDS) for row in rows)
    incomplete_runs = sum(not _is_complete_run(row) for row in rows)
    lines.extend([
        "",
        "## Ограничения и контроль качества",
        "",
        f"- Runs с неполным снимком конфигурации: {incomplete_config}.",
        f"- Незавершённые или с неизвестным статусом runs, исключённые из рейтинга: {incomplete_runs}.",
        f"- Runs с undefined-метриками: {undefined}.",
        f"- Runs с константными test-предсказаниями: {collapsed}.",
        (
            "- Старые отчёты без config snapshot не используются для вывода о влиянии "
            "неизвестных флагов."
        ),
        (
            "- Эффект параметра считается только по matched-парам: отличается один параметр, "
            "остальные флаги, датасет и seed совпадают."
        ),
        (
            "- Связанные boolean-флаги режимов не считаются отдельными характеристиками: "
            "используются lipid_fragments_treatment и protein_pooling."
        ),
        (
            "- Статистическая значимость не заявляется без повторов на нескольких seed и "
            "оценки разброса."
        ),
    ])
    return "\n".join(lines) + "\n"


def update_analysis(table_path, output_path):
    with Path(table_path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    text = build_analysis(rows)
    Path(output_path).write_text(text, encoding="utf-8")
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=PROJECT_ROOT / "metrics_summary.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "metrics_analysis.txt")
    args = parser.parse_args()
    count = update_analysis(args.table, args.output)
    print(f"Analyzed {count} rows into {args.output}")


if __name__ == "__main__":
    main()
