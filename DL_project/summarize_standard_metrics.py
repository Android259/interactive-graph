#!/usr/bin/env python3
"""Summarize standard single-GAT metrics from metrics_summary.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_METRICS = (
    "balanced_accuracy",
    "sensitivity",
    "specificity",
    "precision",
)
STANDARD_FILTERS = {
    "single_gat_layer": 1.0,
    "class_weights": 1.0,
    "lipid_fragments_treatment": "0",
    "protein_pooling": "1",
    "lr": 0.0001,
    "weight_decay": 0.00001,
    "hiddim": 64.0,
    "ep": 150.0,
    "batch": 16.0,
    "grab_loss": 0.0,
}
STANDARD_EMPTY_FIELDS = ("transformer_conv", "gine_conv")
GROUP_FIELD = "exclusion_set"
SEED_FIELD = "seed"


def numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame[column], errors="coerce")


def normalize_text_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame[column].fillna("").astype(str)


def apply_standard_filter(frame: pd.DataFrame) -> pd.DataFrame:
    mask = pd.Series(True, index=frame.index)

    for column, expected in STANDARD_FILTERS.items():
        if column not in frame.columns:
            raise SystemExit(f"Missing required column: {column}")
        if isinstance(expected, float):
            mask &= numeric_series(frame, column) == expected
        else:
            mask &= normalize_text_series(frame, column) == expected

    for column in STANDARD_EMPTY_FIELDS:
        if column in frame.columns:
            mask &= frame[column].isna() | (normalize_text_series(frame, column) == "")

    return frame[mask].copy()


def latest_by_group_seed(frame: pd.DataFrame) -> pd.DataFrame:
    if "datetime" in frame.columns:
        frame = frame.copy()
        frame["_datetime_sort"] = pd.to_datetime(frame["datetime"], errors="coerce")
        frame = frame.sort_values(["_datetime_sort", "datetime"], na_position="first")
    return frame.drop_duplicates([GROUP_FIELD, SEED_FIELD], keep="last").copy()


def format_mean_std(mean: float, std: float) -> str:
    if pd.isna(std):
        return f"{mean:.3f}+/-NA"
    return f"{mean:.3f}+/-{std:.3f}"


def metric_summary(frame: pd.DataFrame, metrics: tuple[str, ...]) -> pd.DataFrame:
    rows = []
    for metric in metrics:
        values = numeric_series(frame, metric).dropna()
        rows.append({
            "metric": metric,
            "mean": values.mean(),
            "median": values.median(),
            "std": values.std(ddof=1),
            "min": values.min(),
            "max": values.max(),
            "n": len(values),
        })
    return pd.DataFrame(rows)


def group_summary(frame: pd.DataFrame, metrics: tuple[str, ...]) -> pd.DataFrame:
    rows = []
    for group, group_frame in frame.groupby(GROUP_FIELD, dropna=False):
        row = {
            "group": group,
            "n": len(group_frame),
            "seeds": ",".join(
                str(seed)
                for seed in sorted(numeric_series(group_frame, SEED_FIELD).dropna().astype(int))
            ),
        }
        for metric in metrics:
            values = numeric_series(group_frame, metric).dropna()
            row[metric] = format_mean_std(values.mean(), values.std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("group")


def print_markdown(title: str, frame: pd.DataFrame) -> None:
    print(f"\n## {title}")
    print(frame.to_markdown(index=False))


def print_csv(title: str, frame: pd.DataFrame) -> None:
    print(f"\n# {title}")
    print(frame.to_csv(index=False).rstrip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=Path("metrics_summary.csv"))
    parser.add_argument("--format", choices=("markdown", "csv"), default="markdown")
    parser.add_argument("--metrics", nargs="+", default=list(DEFAULT_METRICS))
    args = parser.parse_args()

    frame = pd.read_csv(args.table)
    metrics = tuple(args.metrics)
    for metric in metrics:
        if metric not in frame.columns:
            raise SystemExit(f"Missing metric column: {metric}")

    filtered = apply_standard_filter(frame)
    deduplicated = latest_by_group_seed(filtered)

    group_count = deduplicated[GROUP_FIELD].nunique(dropna=True)
    seed_count = deduplicated[SEED_FIELD].nunique(dropna=True)
    expected = group_count * seed_count
    print(f"Input rows: {len(frame)}")
    print(f"Standard rows before dedup: {len(filtered)}")
    print(f"Standard rows after dedup: {len(deduplicated)}")
    print(f"Coverage: {len(deduplicated)}/{expected} group-seed runs")
    print(f"Groups: {group_count}")
    print(f"Seeds: {','.join(str(seed) for seed in sorted(numeric_series(deduplicated, SEED_FIELD).dropna().astype(int).unique()))}")

    overall = metric_summary(deduplicated, metrics)
    by_group = group_summary(deduplicated, metrics)
    printer = print_markdown if args.format == "markdown" else print_csv
    printer("Overall", overall)
    printer("By group, mean+/-std", by_group)


if __name__ == "__main__":
    main()
