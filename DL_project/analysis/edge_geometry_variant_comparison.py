#!/usr/bin/env python3
"""Test-set comparison of the three edge-geometry-pruning variants against the
geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm
baseline (--protein_edge_rbf_count=6, --protein_edge_orientation_scalar,
--protein_edge_raw3 -- see architecture/protein_edge_geometry.py and
files/descriptor_catalog.md section 6 for what each flag removes).

Answers, per excluded protein family (metrics_summary.csv `excluded_groups`):
  - test balanced_accuracy / sensitivity / specificity / abs(sens-spec) gap /
    loss, mean +/- SEM across the 5 seeds, for baseline and all three variants;
  - whether a variant's BA delta vs baseline exceeds the combined (baseline +
    variant) SEM -- the project's convention for "not just noise";
  - per-(group, seed) rows flagged as class-collapse (sensitivity or
    specificity outside [0.05, 0.95]), since balanced_accuracy alone hides
    this;
  - the canonical build_metrics_table.py diagnostics already in the table
    (valid_balanced_accuracy_oscillation, collapse_epoch_count, converged,
    checkpoint_epoch vs max_valid_balanced_accuracy_epoch) so training-dynamics
    claims are grounded in existing columns, not re-derived from raw logs.

Reads only metrics_summary.csv. Writes nothing.

Usage:
    python3 analysis/edge_geometry_variant_comparison.py
"""
import csv
import math
import statistics as st
from collections import defaultdict

BASELINE = "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm"
VARIANTS = {
    "rbf6": BASELINE + "_edge_rbf6",
    "orient": BASELINE + "_edge_orientation_scalar",
    "raw3": BASELINE + "_edge_raw3",
}
LABELS = [BASELINE] + list(VARIANTS.values())
SHORT = {BASELINE: "baseline", **{v: k for k, v in VARIANTS.items()}}

CSV_PATH = "metrics_summary.csv"


def load_rows():
    rows = defaultdict(list)
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["label"] in LABELS:
                rows[(row["label"], row["excluded_groups"])].append(row)
    return rows


def f(row, key):
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return None


def sem(values):
    if len(values) < 2:
        return 0.0
    return st.stdev(values) / math.sqrt(len(values))


def per_group_table(rows):
    groups = sorted({g for (_, g) in rows})
    for g in groups:
        print(f"\n=== {g} ===")
        base_rows = rows[(BASELINE, g)]
        base_ba = [f(r, "balanced_accuracy") for r in base_rows]
        base_mean, base_sem = st.mean(base_ba), sem(base_ba)
        for label in LABELS:
            rs = rows[(label, g)]
            if not rs:
                print(f"  {SHORT[label]:8s} NO DATA")
                continue
            ba = [f(r, "balanced_accuracy") for r in rs]
            sens = [f(r, "sensitivity") for r in rs]
            spec = [f(r, "specificity") for r in rs]
            loss = [f(r, "loss") for r in rs]
            gap = [abs(a - b) for a, b in zip(sens, spec)]
            n_collapse = sum(1 for a, b in zip(sens, spec) if a < 0.05 or a > 0.95 or b < 0.05 or b > 0.95)
            m_ba, s_ba = st.mean(ba), sem(ba)
            delta = m_ba - base_mean
            combined = math.sqrt(base_sem ** 2 + s_ba ** 2)
            if label == BASELINE:
                flag = "(baseline)"
            elif combined == 0:
                flag = "n/a"
            elif abs(delta) < combined:
                flag = "within ~1 SEM"
            elif abs(delta) < 2 * combined:
                flag = ">1 SEM"
            else:
                flag = ">2 SEM"
            print(
                f"  {SHORT[label]:8s} n={len(rs)} BA={m_ba:.3f}+/-{s_ba:.3f} "
                f"(delta={delta:+.3f}, {flag})  sens={st.mean(sens):.3f} spec={st.mean(spec):.3f} "
                f"gap={st.mean(gap):.3f} loss={st.mean(loss):.3f}+/-{sem(loss):.3f} "
                f"collapsed_seeds={n_collapse}/{len(rs)}"
            )


def per_seed_collapse(rows):
    print("\n=== per-(group, seed) collapse flags (sens or spec outside [0.05, 0.95]) ===")
    groups = sorted({g for (_, g) in rows})
    for g in groups:
        for label in LABELS:
            for r in sorted(rows[(label, g)], key=lambda r: int(r["seed"])):
                sens, spec = f(r, "sensitivity"), f(r, "specificity")
                if sens < 0.05 or sens > 0.95 or spec < 0.05 or spec > 0.95:
                    print(
                        f"  {g:18s} {SHORT[label]:8s} seed{r['seed']} "
                        f"sens={sens:.3f} spec={spec:.3f} BA={f(r,'balanced_accuracy'):.3f} "
                        f"ckpt_epoch={r['checkpoint_epoch']} max_valid_BA_epoch={r['max_valid_balanced_accuracy_epoch']} "
                        f"max_valid_BA={r['max_valid_balanced_accuracy']}"
                    )


def dynamics_diagnostics(rows):
    print("\n=== canonical per-config training-dynamics columns (pooled over all groups/seeds) ===")
    for label in LABELS:
        rs = [r for (l, g), lst in rows.items() if l == label for r in lst]
        osc = [f(r, "valid_balanced_accuracy_oscillation") for r in rs]
        collapse_ep = [f(r, "collapse_epoch_count") for r in rs]
        converged = sum(1 for r in rs if r["converged"] == "True")
        print(
            f"  {SHORT[label]:8s} n={len(rs)} "
            f"osc={st.mean(osc):.4f}+/-{st.pstdev(osc):.4f} "
            f"collapse_epoch_count_mean={st.mean(collapse_ep):.2f} "
            f"converged={converged}/{len(rs)}"
        )


if __name__ == "__main__":
    rows = load_rows()
    per_group_table(rows)
    per_seed_collapse(rows)
    dynamics_diagnostics(rows)
