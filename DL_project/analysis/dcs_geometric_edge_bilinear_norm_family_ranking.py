"""Per-excluded-family (honest, not pooled) ranking of the
--double_coldsplit geometric_edge_mlp_protgeom_family_neutral_normalized_
bilinear_fusion_bilinear_norm* line (baseline + ~16 surviving variants;
hid4/lipid_descriptors have no checkpoints and are absent from
metrics_summary.csv, see files/reference_baselines_metrics_proposal.md's
2026-09-11 "Chemistry-null comparison" section).

Reads only metrics_summary.csv (test-report-derived columns: balanced_accuracy,
sensitivity, specificity, max_valid_epoch_train_valid_gap, collapse_fraction).
Does not load checkpoints, does not run any forward pass, does not train.

For each label: groups by exclusion_set (the excluded protein family), averages
each metric over the 5 seeds within that family first, THEN averages over
families -- this is the "mean of |gap|"/per-group-first convention documented
in files/four_families_audit.md section 1.1 (gap-of-means understates a
sens/spec split-by-family collapse by 2.5x-200x on this project's own worked
examples), applied here to every metric, not just the sens/spec gap.

Also prints a paired per-family seed-level significance check (combined SEM,
diff/combinedSEM) between the pooled-BA-best variant and the baseline, to show
whether a pooled-level "improvement" survives a per-family look (it does not,
in the 2026-09-12 snapshot -- see files/dcs_lcs_final_baseline_decision.md
section 2).

Example invocation:
    python3 analysis/dcs_geometric_edge_bilinear_norm_family_ranking.py
"""
from __future__ import annotations

import pandas as pd

METRICS_CSV = "metrics_summary.csv"
BASE_LABEL = (
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_"
    "bilinear_norm"
)


def main() -> None:
    df = pd.read_csv(METRICS_CSV, low_memory=False)
    is_line = df["label"].astype(str).str.startswith(BASE_LABEL) & ~df[
        "label"
    ].astype(str).str.contains("_lcs")
    sub = df[is_line].copy()
    sub["gap"] = (sub["sensitivity"] - sub["specificity"]).abs()

    labels = sorted(sub["label"].unique())
    rows = []
    for lab in labels:
        s = sub[sub["label"] == lab]
        per_fam = s.groupby("exclusion_set").agg(
            BA=("balanced_accuracy", "mean"),
            gap=("gap", "mean"),
            traingap=("max_valid_epoch_train_valid_gap", "mean"),
            collapse=("collapse_fraction", "mean"),
        )
        suffix = lab.replace(BASE_LABEL, "") or "(base)"
        rows.append(
            (
                suffix,
                per_fam["BA"].mean(),
                per_fam["gap"].mean(),
                per_fam["traingap"].mean(),
                per_fam["collapse"].mean(),
                len(per_fam),
            )
        )
    rows.sort(key=lambda r: -r[1])
    header = f"{'suffix':45s} {'BA':>7} {'|gap|':>7} {'traingap':>9} {'collapse':>9} nfam"
    print(header)
    for r in rows:
        print(f"{r[0]:45s} {r[1]:7.3f} {r[2]:7.3f} {r[3]:9.3f} {r[4]:9.3f} {r[5]}")

    # Paired per-family significance check: pooled-BA-best variant vs base.
    best_suffix = rows[0][0]
    if best_suffix != "(base)":
        best_label = BASE_LABEL + best_suffix
        print(f"\nPer-family paired check: {best_suffix} vs (base)")
        for fam in sorted(sub[sub.label == BASE_LABEL]["exclusion_set"].unique()):
            b = sub[(sub.label == BASE_LABEL) & (sub.exclusion_set == fam)][
                "balanced_accuracy"
            ]
            r = sub[(sub.label == best_label) & (sub.exclusion_set == fam)][
                "balanced_accuracy"
            ]
            if len(b) == 0 or len(r) == 0:
                continue
            diff = r.mean() - b.mean()
            combined_sem = (
                (b.std(ddof=1) ** 2 / len(b) + r.std(ddof=1) ** 2 / len(r)) ** 0.5
            )
            sigma = diff / combined_sem if combined_sem > 0 else float("nan")
            print(
                f"  {fam:25s} base={b.mean():.3f} {best_suffix}={r.mean():.3f} "
                f"diff={diff:+.3f} combinedSEM={combined_sem:.3f} sigma={sigma:+.2f}"
            )


if __name__ == "__main__":
    main()
