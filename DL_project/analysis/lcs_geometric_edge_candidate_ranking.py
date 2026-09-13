"""Rank geometric_edge lipid_coldsplit (lcs) candidates that share the same
protein descriptor set and normalization path, on the project's primary lcs
metric (AUC_within_protein_pairs, test) plus the train-valid GAP, per excluded
lipid set (anionic/choline/phosphorus_free/sphingolipids) -- never pooled only.

Reads only: metrics_summary.csv. Does not train, does not load checkpoints.

What "comparable" means here (see files/lcs_geometric_edge_best_candidate_recheck.md
for the full argument): bilinear_fusion=1 AND bilinear_pooled_norm=1 (bilinear_fusion
is numerically unstable without pooled-norm, per
files/geometric_edge_descriptors_baseline_selection_results.md SS3.3) AND
protein_descriptors equal to the family-neutral-7 string. Candidates that change the
protein descriptor set (protgeom8, protfull) or drop bilinear_pooled_norm
(geometric_edge_mlp_protgeom_full_lcs) are reported in a second, clearly separated
table -- they answer a different question (does the descriptor SET matter) and must
not be blended into the "same features" ranking.

Example invocation:
    python3 analysis/lcs_geometric_edge_candidate_ranking.py
"""
import math
import sys

import pandas as pd

CSV_PATH = "metrics_summary.csv"

FAMILY_NEUTRAL_7 = (
    "pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,"
    "apolar_sasa_share,aromatic_share,hydropathy_rim"
)

LIPID_SETS = ["anionic", "choline", "phosphorus_free", "sphingolipids"]

# Labels considered for the "same feature set, same normalization, bilinear-norm
# present" comparison group. Order = rough chronology, not a ranking.
SAME_FEATURES_LABELS = [
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_hid64",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_advprot",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid32",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_liphid32",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads2",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads4",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam025",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam05",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam2",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_cross_forced",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_node_bilinear",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_headchain",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot_advprot",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipdesc",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipgraph",
    "geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3",
]

# Labels that change the protein descriptor SET (protgeom8 / protfull) and/or drop
# bilinear_pooled_norm -- reported separately, never merged into the ranking above.
DIFFERENT_FEATURES_LABELS = [
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protgeom8",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protgeom8",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protfull",
    "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protfull",
    "geometric_edge_mlp_protgeom_full_lcs",  # also bilinear_pooled_norm=0
]

METRIC_COLS = [
    "sensitivity", "specificity", "balanced_accuracy", "AUC",
    "AUC_within_protein", "AUC_within_protein_proteins",
    "AUC_within_protein_pairs", "AUC_within_protein_pairs_proteins",
    "mean_train_valid_gap", "max_train_valid_gap", "max_valid_epoch_train_valid_gap",
]


def sem(series):
    s = series.dropna()
    n = len(s)
    if n < 2:
        return float("nan")
    return s.std(ddof=1) / math.sqrt(n)


def short_set(exclusion_set):
    return str(exclusion_set).replace("groups_", "")


def build_table(df, labels):
    rows = []
    for label in labels:
        sub = df[df["label"] == label]
        if sub.empty:
            print(f"# WARNING: no rows for {label}", file=sys.stderr)
            continue
        for excl, g in sub.groupby("exclusion_set"):
            lipid_set = short_set(excl)
            if lipid_set not in LIPID_SETS:
                continue
            row = {"label": label, "lipid_set": lipid_set, "n_seeds": len(g)}
            for col in METRIC_COLS:
                row[f"{col}_mean"] = g[col].mean()
                row[f"{col}_sem"] = sem(g[col])
            # AUC_within_protein_pairs only exists for runs after 2026-09-08 (added
            # in files/lipid_coldsplit_architecture_direction.md SS7k); older runs
            # (liphid32/64, lipdesc, lipgraph, plain esm3/base/hid64, attention) only
            # have the coarser AUC_within_protein (mean-over-proteins, needs >=6 rows
            # and both classes per protein). Coalesce so every label gets a
            # within-protein number, tagging which metric it came from.
            if not math.isnan(row.get("AUC_within_protein_pairs_mean", float("nan"))):
                row["inprotein_mean"] = row["AUC_within_protein_pairs_mean"]
                row["inprotein_sem"] = row["AUC_within_protein_pairs_sem"]
                row["inprotein_proteins"] = row["AUC_within_protein_pairs_proteins_mean"]
                row["inprotein_source"] = "pairs"
            else:
                row["inprotein_mean"] = row["AUC_within_protein_mean"]
                row["inprotein_sem"] = row["AUC_within_protein_sem"]
                row["inprotein_proteins"] = row["AUC_within_protein_proteins_mean"]
                row["inprotein_source"] = "mean-of-proteins"
            rows.append(row)
    return pd.DataFrame(rows)


def verify_feature_consistency(df, labels):
    """Confirms every label in `labels` really shares bilinear_fusion=1,
    bilinear_pooled_norm=1 and the family-neutral-7 protein descriptor string --
    the precondition for putting them in one ranking table."""
    bad = []
    for label in labels:
        sub = df[df["label"] == label]
        if sub.empty:
            continue
        row = sub.iloc[0]
        if row.get("bilinear_fusion") != 1.0 or row.get("bilinear_pooled_norm") != 1.0:
            bad.append((label, "bilinear_fusion/bilinear_pooled_norm mismatch"))
        if str(row.get("protein_descriptors")) != FAMILY_NEUTRAL_7:
            bad.append((label, f"protein_descriptors mismatch: {row.get('protein_descriptors')}"))
    return bad


PREFIX = "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs"


def shorten(label):
    if label.startswith(PREFIX):
        rest = label[len(PREFIX):]
        return rest if rest else "(base)"
    return label.replace("geometric_edge_", "ge_")


def wide(table, value_col, round_to=3):
    t = table.copy()
    t["label"] = t["label"].map(shorten)
    p = t.pivot(index="label", columns="lipid_set", values=value_col)
    p = p.reindex(columns=[c for c in LIPID_SETS if c in p.columns])
    if pd.api.types.is_numeric_dtype(p.to_numpy().dtype if p.size else float):
        try:
            return p.round(round_to)
        except TypeError:
            return p
    return p


def main():
    df = pd.read_csv(CSV_PATH, low_memory=False)

    bad = verify_feature_consistency(df, SAME_FEATURES_LABELS)
    if bad:
        print("# FEATURE-CONSISTENCY VIOLATIONS in SAME_FEATURES_LABELS:")
        for label, why in bad:
            print(f"  {label}: {why}")
        print()

    same = build_table(df, SAME_FEATURES_LABELS)
    diff = build_table(df, DIFFERENT_FEATURES_LABELS)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 10)

    for group_name, table in [("SAME features (family-neutral-7 + bilinear+norm)", same),
                               ("DIFFERENT protein-descriptor-set / no bilinear-norm", diff)]:
        print(f"##### {group_name} #####\n")
        for col, label_txt in [
            ("inprotein_mean", "test within-protein AUC (pairs if avail., else mean-of-proteins)"),
            ("inprotein_sem", "  .. SEM across seeds"),
            ("inprotein_proteins", "  .. mean #proteins contributing"),
            ("inprotein_source", "  .. metric actually used (pairs / mean-of-proteins)"),
            ("sensitivity_mean", "test sensitivity (pooled)"),
            ("specificity_mean", "test specificity (pooled)"),
            ("balanced_accuracy_mean", "test balanced_accuracy (pooled, NOT for ranking)"),
            ("mean_train_valid_gap_mean", "GAP train-valid BA (mean over training)"),
            ("mean_train_valid_gap_sem", "  .. SEM across seeds"),
        ]:
            print(f"--- {label_txt} ---")
            print(wide(table, col))
            print()
        print()

    return same, diff


if __name__ == "__main__":
    main()
