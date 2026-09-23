#!/usr/bin/env python3
"""Per-group test metrics against the held-out block's Tanimoto similarity.

The lipid-subclass figure-3 series (scripts/run_cron.py, Kron-RLS) holds out one
article subclass block at a time, so every group is one point on an x axis of "how
close is the held-out chemistry to what stayed in training". The run's own report
already carries both readings of that x -- whole-molecule and head-group-only
Tanimoto -- and both the metrics and the four confusion cells per group, but it
prints them as text in two different sections and draws nothing. This script reads
that report and draws the curve.

Six panels, the same set analysis/split_similarity_vs_metric.py draws for the neural
labels: balanced accuracy, F1, and the four confusion cells as SHARES of the block's
evaluated rows (TP + FP + TN + FN = 1 by construction, so the four panels are the
split of one block between the four outcomes and can be read against each other).
TP + FN is the block's own positive rate, drawn as a reference line on those two
panels -- a point sitting on it means every positive was recovered (TP panel) or
none was (FN panel).

Error bars are the std across seeds the report itself prints; x has none (the block
is fixed, the seeds only redraw negatives), so a visible x spread would be a bug.

    python3 analysis/plot_cron_group_metric_vs_tanimoto.py \
        --report cron_test_metrics/cron_fig3_lipidgroups.txt
    python3 analysis/plot_cron_group_metric_vs_tanimoto.py --x headgroup

Reads only; writes the PDF and the per-point CSV under graphics/<label>/tanimoto/.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROUP_ROW = re.compile(
    r"^(?P<group>\S+)\s+(?P<n>\d+)\s+"
    r"(?P<ba>[\d.]+)±(?P<ba_std>[\d.]+)\s+"
    r"(?P<f1>[\d.]+)±(?P<f1_std>[\d.]+)\s+"
    r"(?P<whole>[\d.]+)±[\d.]+\s+"
    r"(?P<head>[\d.]+)±[\d.]+\s*$"
)
DETAIL_HEAD = re.compile(r"^--- group=(?P<group>.+?) ---\s*$")
DETAIL_ROW = re.compile(r"^(?P<key>[A-Za-z_0-9]+):\s*(?P<mean>[-\d.]+)±(?P<std>[-\d.]+)\s*$")

CELLS = ("TP", "FP", "TN", "FN")
PANELS = ("balanced_accuracy", "F1") + tuple(f"{cell}_share" for cell in CELLS)


def parse_report(path: Path):
    """Return {group: {...}} merging the summary table and the per-group detail block."""
    points: dict[str, dict[str, float]] = {}
    label = path.stem
    current = None
    in_groups = False
    for line in path.read_text().splitlines():
        if line.startswith("label:"):
            label = line.split(":", 1)[1].strip()
        if line.startswith("=== by group"):
            in_groups = True
            continue
        if in_groups:
            if line.startswith("==="):
                in_groups = False
            else:
                match = GROUP_ROW.match(line)
                if match and match.group("group") != "ALL":
                    points[match.group("group")] = {
                        "seeds": int(match.group("n")),
                        "balanced_accuracy": float(match.group("ba")),
                        "balanced_accuracy_std": float(match.group("ba_std")),
                        "F1": float(match.group("f1")),
                        "F1_std": float(match.group("f1_std")),
                        "tanimoto_whole": float(match.group("whole")),
                        "tanimoto_headgroup": float(match.group("head")),
                    }
                continue
        head = DETAIL_HEAD.match(line)
        if head:
            current = head.group("group")
            continue
        row = DETAIL_ROW.match(line) if current else None
        if row and current in points:
            points[current][f"detail_{row.group('key')}"] = float(row.group("mean"))
            points[current][f"detail_{row.group('key')}_std"] = float(row.group("std"))

    for group, point in points.items():
        total = point.get("detail_total")
        if not total:
            continue
        for cell in CELLS:
            mean = point.get(f"detail_{cell}")
            std = point.get(f"detail_{cell}_std")
            if mean is not None:
                point[f"{cell}_share"] = mean / total
                point[f"{cell}_share_std"] = (std or 0.0) / total
        # TP + FN is the block's positive rate: the line the two positive-cell panels
        # are read against, and it comes from the block, not from the model.
        if "TP_share" in point and "FN_share" in point:
            point["positive_rate"] = point["TP_share"] + point["FN_share"]
    return label, points


def plot(label, points, x_key, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = sorted(points, key=lambda name: points[name][x_key])
    figure, axes = plt.subplots(3, 2, figsize=(11, 12), sharex=True)
    x = [points[name][x_key] for name in groups]

    for axis, panel in zip(axes.ravel(), PANELS):
        y = [points[name].get(panel) for name in groups]
        yerr = [points[name].get(f"{panel}_std", 0.0) for name in groups]
        if any(value is None for value in y):
            axis.set_title(f"{panel}: not in report")
            continue
        axis.errorbar(x, y, yerr=yerr, fmt="o", capsize=3, color="#1f77b4")
        for name, xi, yi in zip(groups, x, y):
            axis.annotate(
                name if len(name) <= 12 else name[:10] + "…",
                (xi, yi), textcoords="offset points", xytext=(4, 4), fontsize=7,
            )
        if panel in ("TP_share", "FN_share"):
            rates = [points[name].get("positive_rate") for name in groups]
            if all(rate is not None for rate in rates):
                axis.plot(x, rates, "--", color="#999999", linewidth=1,
                          label="block positive rate (TP+FN)")
                axis.legend(fontsize=7)
        if panel.endswith("_share"):
            axis.set_ylim(0.0, 1.0)
            axis.set_ylabel(f"test {panel.removesuffix('_share')} / block rows")
        else:
            axis.axhline(0.5, color="#cccccc", linewidth=1)
            axis.set_ylabel(f"test {panel}")
        axis.grid(alpha=0.3)

    for axis in axes[-1]:
        axis.set_xlabel(
            "block Tanimoto similarity to training chemistry"
            + (" (head group only)" if x_key == "tanimoto_headgroup" else " (whole molecule)")
        )
    figure.suptitle(f"{label}: per-group test metrics vs block Tanimoto ({len(groups)} points)")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200, bbox_inches="tight")
    return groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=PROJECT_ROOT / "cron_test_metrics" / "cron_fig3_lipidgroups.txt",
    )
    parser.add_argument("--x", choices=("whole", "headgroup"), default="whole")
    parser.add_argument("--output_dir", type=Path, default=None)
    args = parser.parse_args()

    label, points = parse_report(args.report)
    if not points:
        raise SystemExit(f"no per-group rows parsed from {args.report}")
    x_key = "tanimoto_whole" if args.x == "whole" else "tanimoto_headgroup"
    output_dir = args.output_dir or PROJECT_ROOT / "graphics" / label / "tanimoto"
    output = output_dir / f"{label}_metrics_vs_tanimoto_{args.x}.pdf"
    groups = plot(label, points, x_key, output)

    csv_path = output_dir / f"{label}_metrics_vs_tanimoto_points.csv"
    columns = ["group", "seeds", "tanimoto_whole", "tanimoto_headgroup", "positive_rate"]
    columns += [panel for panel in PANELS] + [f"{panel}_std" for panel in PANELS]
    with csv_path.open("w", encoding="utf-8") as handle:
        handle.write(",".join(columns) + "\n")
        for name in groups:
            point = points[name]
            values = [name] + [
                f"{point.get(column, float('nan')):.6f}" if column != "seeds"
                else str(int(point.get("seeds", 0)))
                for column in columns[1:]
            ]
            handle.write(",".join(values) + "\n")
    print(f"wrote {output}")
    print(f"wrote {csv_path}  ({len(groups)} points)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
