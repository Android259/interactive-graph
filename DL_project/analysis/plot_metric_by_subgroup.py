#!/usr/bin/env python3
"""Plot per-protein subgroup metrics from completed test reports."""

from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from build_metrics_table import CONFIG_FIELDS, PROJECT_ROOT, ModelConfig, serialize_config


REPORT_TIMESTAMP = re.compile(r"test_metrics_(\d{8}_\d{6})_")
SUBGROUP_MARKER = "per_protein_subgroup_metrics:"
SUBGROUP_COLUMNS = (
    "subgroup",
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
# Reports only list the configuration fields that existed when they were written, so a
# field added later is absent from older reports. Backfilling its dataclass default keeps
# runs of the same configuration comparable across report-format versions.
CONFIG_DEFAULTS = serialize_config(ModelConfig())
IDENTITY_FIELDS = (
    *(
        field
        for field in CONFIG_FIELDS
        if field not in {"seed", "excluded_groups", "excluded_subgroups"}
    ),
)
DISPLAY_CONFIG_FIELDS = (
    "label",
    "class_weights",
    "protein_class_weight",
    "protein_class_sqrt_weight",
    "lr",
    "weight_decay",
    "final_m",
    "final_dropout",
    "hiddim",
    "heads",
    "batch",
    "ep",
)
PROTEIN_GROUP_ORDER = (
    "CRAL-TRIO",
    "GLTP",
    "IP_trans",
    "LBP_BPI_CETP",
    "ML",
    "OSBP",
    "START",
    "lipocalin",
    "scp2",
)
PROTEIN_GROUP_COLORS = {
    "CRAL-TRIO": "#4E79A7",
    "GLTP": "#F28E2B",
    "IP_trans": "#59A14F",
    "LBP_BPI_CETP": "#E15759",
    "ML": "#B07AA1",
    "OSBP": "#9C755F",
    "START": "#76B7B2",
    "lipocalin": "#EDC948",
    "scp2": "#BAB0AC",
}


def parse_filter(expression: str) -> tuple[str, str]:
    if "=" not in expression:
        raise argparse.ArgumentTypeError(
            f"Filter must have FIELD=VALUE form: {expression!r}"
        )
    field, value = expression.split("=", 1)
    if not field:
        raise argparse.ArgumentTypeError("Filter field cannot be empty")
    return field, value


def _finite_number(value: str) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def parse_report(path: Path, reports_root: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        marker_index = lines.index(SUBGROUP_MARKER)
    except ValueError:
        raise ValueError(f"{path} has no {SUBGROUP_MARKER} section") from None

    config = {}
    for line in lines[:marker_index]:
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        config[key] = value
    if "HEADS" in config:
        config["heads"] = config["HEADS"]
    if not config.get("final_m"):
        config["final_m"] = config.get("m", "")
    if not config.get("final_dropout"):
        config["final_dropout"] = "0.0"
    for field in ("protein_class_weight", "protein_class_sqrt_weight"):
        if not config.get(field):
            config[field] = "0"
    for field in CONFIG_FIELDS:
        if field not in config:
            config[field] = CONFIG_DEFAULTS.get(field, "")

    relative = path.relative_to(reports_root)
    if len(relative.parts) < 3:
        raise ValueError(f"Unexpected report path: {path}")
    config.setdefault("label", relative.parts[0])
    config["exclusion_set"] = "/".join(relative.parts[1:-1])

    timestamp_match = REPORT_TIMESTAMP.match(path.name)
    if timestamp_match is None:
        raise ValueError(f"Cannot read timestamp from {path.name}")

    if marker_index + 2 >= len(lines):
        raise ValueError(f"Incomplete subgroup table in {path}")
    header = re.split(r"\s{2,}", lines[marker_index + 1].strip())
    if tuple(header) != SUBGROUP_COLUMNS:
        raise ValueError(f"Unexpected subgroup columns in {path}")

    subgroup_rows = []
    for line in lines[marker_index + 3 :]:
        if not line.strip():
            continue
        values = re.split(r"\s{2,}", line.strip())
        if len(values) != len(header):
            raise ValueError(f"Malformed subgroup row in {path}: {line}")
        subgroup_rows.append(dict(zip(header, values)))

    return {
        "path": path,
        "timestamp": timestamp_match.group(1),
        "config": config,
        "subgroups": subgroup_rows,
    }


def select_reports(
    reports: list[dict[str, object]],
    filters: list[tuple[str, str]],
    groups: list[str],
    seeds: list[str] | None = None,
) -> list[dict[str, object]]:
    selected = []
    normalized_groups = {
        group if group.startswith("groups_") else f"groups_{group}"
        for group in groups
    }
    for report in reports:
        config = report["config"]
        if config.get("run_status") != "complete":
            continue
        if normalized_groups and config.get("exclusion_set") not in normalized_groups:
            continue
        if seeds and config.get("seed", "") not in seeds:
            continue
        if any(config.get(field, "") != value for field, value in filters):
            continue
        selected.append(report)

    by_group_seed = defaultdict(list)
    for report in selected:
        config = report["config"]
        key = (config["exclusion_set"], config.get("seed", ""))
        by_group_seed[key].append(report)

    latest = []
    for (group, seed), candidates in sorted(by_group_seed.items()):
        identities = {
            tuple(candidate["config"].get(field, "") for field in IDENTITY_FIELDS)
            for candidate in candidates
        }
        if len(identities) > 1:
            raise ValueError(
                "Filters match multiple configurations for "
                f"{group}, seed={seed or 'N/A'}. Add more --filter arguments."
            )
        latest.append(max(candidates, key=lambda report: report["timestamp"]))
    return latest


def aggregate_subgroups(
    reports: list[dict[str, object]], metric: str
) -> list[dict[str, object]]:
    if metric not in SUBGROUP_COLUMNS[1:]:
        available = ", ".join(SUBGROUP_COLUMNS[1:])
        raise ValueError(f"Unknown subgroup metric {metric!r}. Available: {available}")

    grouped = defaultdict(list)
    seeds = defaultdict(set)
    groups = defaultdict(set)
    for report in reports:
        config = report["config"]
        for row in report["subgroups"]:
            value = _finite_number(row[metric])
            if value is None:
                continue
            subgroup = row["subgroup"]
            grouped[subgroup].append(value)
            seeds[subgroup].add(config.get("seed", ""))
            groups[subgroup].add(config["exclusion_set"].removeprefix("groups_"))

    result = []
    for subgroup, values in sorted(grouped.items()):
        result.append(
            {
                "subgroup": subgroup,
                "mean": statistics.fmean(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "count": len(values),
                "seeds": sorted(seeds[subgroup]),
                "groups": sorted(groups[subgroup]),
            }
        )
    return result


def read_positive_counts(dataset: Path) -> dict[str, int]:
    counts = defaultdict(int)
    with dataset.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                is_positive = int(float(row.get("Interaction", ""))) == 1
            except (TypeError, ValueError):
                continue
            if is_positive:
                counts[row.get("LTPProtein", "")] += 1
    return dict(counts)


def read_subgroup_domains(dataset: Path) -> dict[str, str]:
    """Map each subgroup (protein) to its protein family (ProteinDomain).

    Coloring keys on the family, not on the exclusion set: the two coincide
    only for simple leave-one-family-out runs, so compound/random/subgroup
    exclusion sets would otherwise fall back to the neutral gray.
    """
    domains: dict[str, str] = {}
    with dataset.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            protein = row.get("LTPProtein", "")
            domain = row.get("ProteinDomain", "")
            if protein and domain:
                domains.setdefault(protein, domain)
    return domains


def configuration_label(reports: list[dict[str, object]]) -> str:
    configs = [report["config"] for report in reports]
    parts = []
    labels = sorted({config.get("label", "") for config in configs})
    if len(labels) == 1 and labels[0]:
        parts.append(labels[0])
    weight_labels = []
    if {config.get("class_weights", "") for config in configs} == {"1"}:
        weight_labels.append("class weights")
    if {config.get("protein_class_weight", "") for config in configs} == {"1"}:
        weight_labels.append("protein class weights: inverse")
    if {config.get("protein_class_sqrt_weight", "") for config in configs} == {"1"}:
        weight_labels.append("protein class weights: sqrt")
    if not weight_labels:
        weight_labels.append("no class weights")
    parts.extend(weight_labels)

    hidden_fields = {
        "label",
        "class_weights",
        "protein_class_weight",
        "protein_class_sqrt_weight",
    }
    for field in DISPLAY_CONFIG_FIELDS:
        if field in hidden_fields:
            continue
        values = sorted({config.get(field, "") for config in configs})
        if len(values) == 1 and values[0] != "":
            parts.append(f"{field}={values[0]}")
    seeds = sorted({config.get("seed", "") for config in configs})
    if seeds:
        parts.append(f"seeds={','.join(seeds)}")
    return " | ".join(parts)


def _group_sort_key(group_name: str) -> tuple[int, str]:
    try:
        return PROTEIN_GROUP_ORDER.index(group_name), group_name
    except ValueError:
        return len(PROTEIN_GROUP_ORDER), group_name


def _group_color(group_name: str) -> str:
    return PROTEIN_GROUP_COLORS.get(group_name, "#7F7F7F")


def plot_aggregates(
    aggregates: list[dict[str, object]],
    metric: str,
    output: Path,
    title: str | None = None,
    random_baseline: float | None = None,
    config_label: str | None = None,
    positive_counts: dict[str, int] | None = None,
    subgroup_domains: dict[str, str] | None = None,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def family_of(item: dict[str, object]) -> str:
        subgroup = str(item["subgroup"])
        if subgroup_domains and subgroup in subgroup_domains:
            return subgroup_domains[subgroup]
        return ",".join(str(group) for group in item["groups"])

    ordered = sorted(
        aggregates,
        key=lambda item: (_group_sort_key(family_of(item)), str(item["subgroup"])),
    )
    labels = [str(item["subgroup"]) for item in ordered]
    counts = [
        positive_counts.get(subgroup, 0)
        for subgroup in labels
    ] if positive_counts is not None else None
    means = [float(item["mean"]) for item in ordered]
    errors = [float(item["std"]) for item in ordered]
    group_names = [family_of(item) for item in ordered]

    positions = []
    group_ranges = []
    current_group = None
    group_start = 0.0
    position = 0.0
    for index, group_name in enumerate(group_names):
        if current_group is not None and group_name != current_group:
            group_ranges.append((current_group, group_start, positions[-1]))
            position += 1.0
            group_start = position
        elif current_group is None:
            group_start = position
        positions.append(position)
        current_group = group_name
        position += 1.0
    if current_group is not None:
        group_ranges.append((current_group, group_start, positions[-1]))

    group_colors = {
        group_name: _group_color(group_name)
        for group_name, _, _ in group_ranges
    }
    colors = [group_colors[group_name] for group_name in group_names]
    width = max(18.0, 0.85 * position)

    figure, axis = plt.subplots(figsize=(width, 7))
    bars = axis.bar(
        positions,
        means,
        yerr=errors,
        capsize=3,
        color=colors,
        edgecolor="black",
        linewidth=0.6,
    )
    axis.set_ylabel(metric)
    axis.set_ylim(top=1.0)
    plot_title = title or f"{metric} by protein subgroup"
    if config_label:
        plot_title = f"{plot_title}\n{config_label}"
    axis.set_title(plot_title, fontsize=11, pad=12)
    axis.grid(axis="y", alpha=0.25)
    axis.set_xticks(positions, labels, rotation=45, ha="right")
    if counts is not None:
        for x_position, count in zip(positions, counts):
            axis.text(
                x_position,
                -0.20,
                str(count),
                transform=axis.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=9,
            )
    if random_baseline is not None:
        axis.axhline(
            random_baseline,
            color="black",
            linestyle="--",
            linewidth=1.5,
            label=f"Random baseline = {random_baseline:g}",
        )
        axis.legend(loc="upper right")

    offset = max(max(means, default=1.0) * 0.01, 0.005)
    for bar, item in zip(bars, ordered):
        label_y = min(bar.get_height() + offset, 0.985)
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            label_y,
            f"{float(item['mean']):.3f}",
            ha="center",
            va="bottom" if label_y > bar.get_height() else "top",
            fontsize=9,
            fontweight="bold",
            bbox={
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.75,
                "pad": 0.5,
            },
        )

    for index, (group_name, start, end) in enumerate(group_ranges):
        center = (start + end) / 2
        axis.text(
            center,
            -0.34,
            group_name,
            transform=axis.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color=group_colors[group_name],
        )
        if index < len(group_ranges) - 1:
            next_start = group_ranges[index + 1][1]
            axis.axvline((end + next_start) / 2, color="0.65", linewidth=1)

    figure.subplots_adjust(bottom=0.38, top=0.86)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reports-root",
        type=Path,
        default=PROJECT_ROOT / "test_metrics",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=PROJECT_ROOT
        / "data"
        / "Processed_Negative_Interaction_Corrected_Domains.csv",
    )
    parser.add_argument("--metric", default="balanced_accuracy")
    parser.add_argument(
        "--filter",
        action="append",
        type=parse_filter,
        default=[],
        metavar="FIELD=VALUE",
        help="Exact run-parameter filter; may be repeated.",
    )
    parser.add_argument(
        "--group",
        action="append",
        default=[],
        help="Include one excluded group; may be repeated. Default: all matched groups.",
    )
    parser.add_argument(
        "--seed",
        action="append",
        default=[],
        help="Include one seed; may be repeated. Default: all matched seeds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "metric_by_subgroup.pdf",
    )
    parser.add_argument(
        "--output-format",
        choices=("pdf",),
        default="pdf",
        help="Output format. Only PDF is supported.",
    )
    parser.add_argument("--title")
    parser.add_argument(
        "--random-baseline",
        type=float,
        help="Horizontal random-guessing baseline. Defaults to 0.5 for balanced_accuracy.",
    )
    args = parser.parse_args()

    reports = []
    parse_errors = []
    for path in args.reports_root.rglob("test_metrics_*.txt"):
        try:
            reports.append(parse_report(path, args.reports_root))
        except ValueError as error:
            parse_errors.append(str(error))

    selected = select_reports(reports, args.filter, args.group, args.seed)
    aggregates = aggregate_subgroups(selected, args.metric)
    if not aggregates:
        raise SystemExit("No per-protein subgroup metrics matched the parameters.")

    random_baseline = args.random_baseline
    if random_baseline is None and args.metric == "balanced_accuracy":
        random_baseline = 0.5
    config_label = configuration_label(selected)
    positive_counts = read_positive_counts(args.dataset)
    subgroup_domains = read_subgroup_domains(args.dataset)
    output = args.output.with_suffix(f".{args.output_format}")
    plot_aggregates(
        aggregates,
        args.metric,
        output,
        args.title,
        random_baseline,
        config_label,
        positive_counts,
        subgroup_domains,
    )
    print(f"Configuration: {config_label}")
    for item in aggregates:
        print(
            f"{item['subgroup']}: {float(item['mean']):.6f} "
            f"+/- {float(item['std']):.6f}; n={item['count']}; "
            f"seeds={','.join(item['seeds'])}; groups={','.join(item['groups'])}"
        )
    if parse_errors:
        print(f"Skipped {len(parse_errors)} reports without usable subgroup tables.")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
