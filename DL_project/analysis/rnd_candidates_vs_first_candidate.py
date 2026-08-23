#!/usr/bin/env python3
"""Compare the random-candidate (rnd) double-coldsplit runs against their predecessors.

The rnd runs encode a lipid row as one candidate structure drawn afresh at every
presentation (``lipid_fragments_treatment=random_choice``); the runs they replace named
``concat`` but carried ``lipid_first_fragment_only``, so they encoded one fixed member of
the candidate set. That is the contrast of interest.

It is NOT a clean one: the same rebuild moved ``coldsplit_share`` from 0.70 to 0.80, so
the held-out blocks are not the same rows. Every number below is therefore reported as a
matched (variant, family, seed) pair, and the confound is printed with it.

Beyond the summary table this reads the per-epoch TensorBoard scalars, which carry the
three things the summary cannot answer:

* ``epoch/valid sensitivity`` -- whether the positive class is recovered at all, and when;
* ``epoch/protein contribution`` -- full validation BA minus BA with the pooled protein
  zeroed. Near zero means the decision is the lipid marginal, which a protein-blind
  lookup already answers;
* ``epoch/pooled protein between-protein variance`` -- the share of the pooled protein
  vector's variance that lies between proteins rather than within one. High means the
  encoder has learned protein identity.

Usage: python3 analysis/rnd_candidates_vs_first_candidate.py
"""

import glob
import os
import re
import sys

import numpy
import pandas

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

VARIANTS = {
    "plain": (
        "bbp_dcs_rnd_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120",
        "bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120",
    ),
    "compat_input": (
        "bbp_dcs_rnd_smd_fa_nps_compatinput_dpt01_gm_plm8_hid8_wd001_ep120",
        "bbp_dcs_smd_fa_nps_compatinput_dpt01_gm_plm8_hid8_wd001_ep120",
    ),
    "compat_split": (
        "bbp_dcs_rnd_smd_fa_nps_compatsplit_dpt01_gm_plm8_hid8_wd001_ep120",
        "bbp_dcs_smd_fa_nps_compatsplit_dpt01_gm_plm8_hid8_wd001_ep120",
    ),
}

SUMMARY_COLUMNS = [
    "checkpoint_epoch",
    "checkpoint_valid_balanced_accuracy",
    "checkpoint_rolling_valid_balanced_accuracy",
    "max_valid_epoch_centered_window_balanced_accuracy_mean",
    "max_valid_epoch_min_class_recall",
    "max_valid_epoch_class_recall_gap",
    "max_valid_epoch_sensitivity",
    "max_valid_epoch_specificity",
    "collapse_fraction",
    "max_train_valid_gap",
    "balanced_accuracy",
    "sensitivity",
    "specificity",
    "F1",
    "prediction_positive_fraction",
]

RUN_DIR_PATTERN = re.compile(
    r"train\d{8}_\d{6}_\d+parameters_\d+_\d+_(?P<seed>\d+)_[\d.]+_\d+_\d+$"
)


def load_summary(path="metrics_summary.csv"):
    """The metrics table, read with pandas so the duplicate `label` column is safe."""
    table = pandas.read_csv(path, low_memory=False)
    wanted = {name for pair in VARIANTS.values() for name in pair}
    selected = table[table["label"].isin(wanted)].copy()
    selected["family"] = selected["exclusion_set"].str.replace("groups_", "", regex=False)
    return selected


def tensorboard_series(run_root, label, family, seed):
    """Per-epoch scalars of one run, or None when its event file is absent."""
    directory = os.path.join(run_root, label, f"groups_{family}")
    if not os.path.isdir(directory):
        return None
    for candidate in sorted(os.listdir(directory)):
        match = RUN_DIR_PATTERN.match(candidate)
        if not match or int(match.group("seed")) != seed:
            continue
        events = sorted(glob.glob(os.path.join(directory, candidate, "events*")))
        if not events:
            continue
        accumulator = EventAccumulator(events[0], size_guidance={"scalars": 0})
        accumulator.Reload()
        available = set(accumulator.Tags()["scalars"])
        series = {}
        for tag in (
            "epoch/valid sensitivity",
            "epoch/valid specificity",
            "epoch/valid balanced_accuracy",
            "epoch/protein contribution",
            "epoch/lipid contribution",
            "epoch/pooled protein between-protein variance",
        ):
            if tag in available:
                series[tag] = numpy.array(
                    [event.value for event in accumulator.Scalars(tag)], dtype=float
                )
        return series
    return None


def first_epoch_reaching(values, level):
    """1-based epoch at which the series first reaches `level`, or None."""
    hits = numpy.nonzero(values >= level)[0]
    return int(hits[0]) + 1 if hits.size else None


def curve_features(series, checkpoint_epoch):
    """The handful of curve statistics the comparison is argued from."""
    if not series:
        return {}
    out = {}
    sensitivity = series.get("epoch/valid sensitivity")
    specificity = series.get("epoch/valid specificity")
    if sensitivity is not None and sensitivity.size:
        out["sens_first10"] = float(sensitivity[:10].mean())
        out["sens_last10"] = float(sensitivity[-10:].mean())
        out["sens_growth"] = out["sens_last10"] - out["sens_first10"]
        out["sens_epoch_half"] = first_epoch_reaching(sensitivity, 0.5)
        epochs = numpy.arange(1, sensitivity.size + 1, dtype=float)
        out["sens_slope_per_100ep"] = float(
            numpy.polyfit(epochs, sensitivity, 1)[0] * 100.0
        )
        if checkpoint_epoch and 1 <= int(checkpoint_epoch) <= sensitivity.size:
            out["sens_at_checkpoint"] = float(sensitivity[int(checkpoint_epoch) - 1])
    if specificity is not None and specificity.size:
        out["spec_last10"] = float(specificity[-10:].mean())
        if sensitivity is not None and sensitivity.size == specificity.size:
            out["gap_last10"] = float(
                numpy.abs(sensitivity[-10:] - specificity[-10:]).mean()
            )
    protein = series.get("epoch/protein contribution")
    if protein is not None and protein.size:
        out["protein_contrib_last10"] = float(protein[-10:].mean())
        out["protein_contrib_max"] = float(protein.max())
        if checkpoint_epoch and 1 <= int(checkpoint_epoch) <= protein.size:
            out["protein_contrib_at_checkpoint"] = float(protein[int(checkpoint_epoch) - 1])
    lipid = series.get("epoch/lipid contribution")
    if lipid is not None and lipid.size:
        out["lipid_contrib_last10"] = float(lipid[-10:].mean())
    variance = series.get("epoch/pooled protein between-protein variance")
    if variance is not None and variance.size:
        out["between_protein_var_first10"] = float(variance[:10].mean())
        out["between_protein_var_last10"] = float(variance[-10:].mean())
    return out


def build_rows(summary, run_root="run"):
    """One row per run, summary columns plus the curve features."""
    rows = []
    for variant, (rnd_label, old_label) in VARIANTS.items():
        for arm, label in (("rnd", rnd_label), ("first", old_label)):
            block = summary[summary["label"] == label]
            for _, run in block.iterrows():
                record = {
                    "variant": variant,
                    "arm": arm,
                    "family": run["family"],
                    "seed": int(run["seed"]),
                    "coldsplit_share": run.get("coldsplit_share"),
                    "treatment": run.get("lipid_fragments_treatment"),
                    "first_only": run.get("lipid_first_fragment_only"),
                }
                for column in SUMMARY_COLUMNS:
                    record[column] = run.get(column)
                record.update(
                    curve_features(
                        tensorboard_series(
                            run_root, label, run["family"], int(run["seed"])
                        )
                        or {},
                        run.get("checkpoint_epoch"),
                    )
                )
                rows.append(record)
    return pandas.DataFrame(rows)


def matched_deltas(rows, metrics):
    """rnd minus first-candidate on every (variant, family, seed) present in both."""
    keys = ["variant", "family", "seed"]
    rnd = rows[rows["arm"] == "rnd"].set_index(keys)
    first = rows[rows["arm"] == "first"].set_index(keys)
    shared = rnd.index.intersection(first.index)
    report = []
    for metric in metrics:
        if metric not in rows.columns:
            continue
        a = pandas.to_numeric(rnd.loc[shared, metric], errors="coerce")
        b = pandas.to_numeric(first.loc[shared, metric], errors="coerce")
        delta = (a - b).dropna()
        if delta.empty:
            continue
        report.append(
            {
                "metric": metric,
                "pairs": int(delta.size),
                "rnd_mean": float(a.mean()),
                "first_mean": float(b.mean()),
                "mean_delta": float(delta.mean()),
                "median_delta": float(delta.median()),
                "improved": int((delta > 0).sum()),
                "worsened": int((delta < 0).sum()),
            }
        )
    return pandas.DataFrame(report), shared


def show(frame, columns=None, floats=3):
    if frame.empty:
        return "(nothing)"
    view = frame if columns is None else frame[columns]
    return view.to_string(index=False, float_format=lambda v: f"{v:.{floats}f}")


def main():
    summary = load_summary()
    if summary.empty:
        sys.exit("no rows for the compared labels in metrics_summary.csv")
    rows = build_rows(summary)

    print("=" * 78)
    print("COVERAGE AND CONFOUND")
    print("=" * 78)
    coverage = (
        rows.groupby(["variant", "arm"])
        .agg(
            runs=("family", "size"),
            families=("family", "nunique"),
            seeds=("seed", "nunique"),
            share=("coldsplit_share", lambda s: sorted(set(s.dropna()))),
            treatment=("treatment", lambda s: sorted(set(s.dropna()))),
            first_only=("first_only", lambda s: sorted(set(s.dropna()))),
        )
        .reset_index()
    )
    print(show(coverage))

    valid_metrics = [
        "checkpoint_rolling_valid_balanced_accuracy",
        "checkpoint_valid_balanced_accuracy",
        "max_valid_epoch_centered_window_balanced_accuracy_mean",
        "max_valid_epoch_min_class_recall",
        "max_valid_epoch_class_recall_gap",
        "collapse_fraction",
        "max_train_valid_gap",
        "checkpoint_epoch",
    ]
    test_metrics = [
        "balanced_accuracy",
        "sensitivity",
        "specificity",
        "F1",
        "prediction_positive_fraction",
    ]
    curve_metrics = [
        "sens_first10",
        "sens_last10",
        "sens_growth",
        "sens_slope_per_100ep",
        "sens_at_checkpoint",
        "spec_last10",
        "gap_last10",
        "protein_contrib_at_checkpoint",
        "protein_contrib_last10",
        "protein_contrib_max",
        "lipid_contrib_last10",
        "between_protein_var_first10",
        "between_protein_var_last10",
    ]

    for title, metrics in (
        ("MATCHED DELTAS, VALIDATION (rnd - first candidate)", valid_metrics),
        ("MATCHED DELTAS, TEST (descriptive)", test_metrics),
        ("MATCHED DELTAS, PER-EPOCH CURVES", curve_metrics),
    ):
        table, shared = matched_deltas(rows, metrics)
        print()
        print("=" * 78)
        print(f"{title} -- {len(shared)} matched pairs")
        print("=" * 78)
        print(show(table))

    print()
    print("=" * 78)
    print("PER FAMILY, PLAIN VARIANT (both seeds averaged)")
    print("=" * 78)
    per_family = (
        rows[rows["variant"] == "plain"]
        .groupby(["family", "arm"])[
            [
                "checkpoint_rolling_valid_balanced_accuracy",
                "balanced_accuracy",
                "sensitivity",
                "specificity",
                "sens_last10",
                "protein_contrib_last10",
                "between_protein_var_last10",
            ]
        ]
        .mean()
        .reset_index()
    )
    print(show(per_family))

    print()
    print("=" * 78)
    print("TEST BALANCED ACCURACY PER FAMILY, ALL VARIANTS (both seeds averaged)")
    print("=" * 78)
    per_family_test = (
        rows.pivot_table(
            index="family", columns=["variant", "arm"], values="balanced_accuracy",
            aggfunc="mean",
        )
    )
    print(per_family_test.to_string(float_format=lambda v: f"{v:.3f}"))

    print()
    print("=" * 78)
    print("SENSITIVITY COLLAPSE COUNT (test sensitivity == 0)")
    print("=" * 78)
    zero = (
        rows.assign(dead=lambda f: pandas.to_numeric(f["sensitivity"], errors="coerce") == 0)
        .groupby(["variant", "arm"])["dead"]
        .agg(["sum", "size"])
        .reset_index()
    )
    print(show(zero))

    print()
    print("=" * 78)
    print("NOTE")
    print("=" * 78)
    print(
        "Three things changed at once between the two arms, not one:\n"
        "  1. the candidate treatment -- one fixed member of the set, then one drawn\n"
        "     afresh at every presentation;\n"
        "  2. coldsplit_share, 0.70 -> 0.80, so different lipid classes leave training\n"
        "     and the held-out blocks are different rows;\n"
        "  3. the interaction table itself -- the runs before 2026-08-23 read the\n"
        "     pre-deduplication file (11018 rows, 756 rows labelled positive over 10920\n"
        "     distinct cells), the rnd runs read the deduplicated one (10920 rows, 658\n"
        "     positive cells).\n"
        "No matched pair isolates the candidate treatment, and (3) alone changes the\n"
        "positive count by 15 percent. Every delta above is the sum of the three."
    )


if __name__ == "__main__":
    main()
