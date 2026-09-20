#!/usr/bin/env python3
"""Label-driven runner for analysis/gbm_baseline.py -- writes test_metrics/ reports.

The HistGradientBoosting counterpart of scripts/run_cron.py (Kron-RLS): same label/
--set_label/--no_logs/--complete/--out_root conventions, same --protein_features/
--lipid_features convenience shorthand, same terminal summary layout. Takes a label
and writes one report file per (excluded block, seed) under

    test_metrics/gbm_<label>/groups_<block>/gbm_metrics_<timestamp>_seed<seed>.txt

-- `gbm_*` on both the label and the filename, exactly as `cron_*` keeps run_cron.py's
Kron-RLS runs out of analysis/build_metrics_table.py's own `rglob("test_metrics_*.txt")`
(it only matches network runs' exact filename shape); `gbm_*` keeps these out of BOTH
that glob and run_cron.py's own `cron_*` namespace.

Every gbm_baseline.py flag works here unchanged (this file reuses its own argument
parser, analysis.gbm_baseline.build_parser(), so the two can never silently drift
apart) -- split axis, class weighting, hyperparameters, threshold metric, etc.
--families omitted runs every default block for the chosen --split_mode, same as
run_cron.py.

    python3 scripts/run_gbm.py protunion14_gbm --split_mode lipid_coldsplit \\
        --seeds 0,1,2,3,4 --class_weight balanced \\
        --protein_features=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,\\
buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,depth_q10,\\
hydropathy_core,pocket_extent --lipid_features=chain,hbond,experimental_lipid_volume

Convenience feature-list shorthand. --protein_features/--lipid_features (new flags,
gbm_baseline.py itself has no "custom features file" concept to alias) accept a
comma-separated descriptor-name list, resolved the SAME way analysis/kronrls_
baseline.py's --lipid_kernel=explicit_subset resolves --lipid_descriptor_names
(training.pair_baseline_common.resolve_lipid_feature_subset: explicit_lipid_
features' own columns, dataloader.pair_descriptors.LIPID_DESCRIPTOR_NAMES for the
rest, "molformer" for the network's own raw embedding) -- so a name behaves
identically whether it reaches Kron-RLS or GBM. Unlike Kron-RLS, "tanimoto"/
"tanimoto_headgroup" as the SOLE --lipid_features value routes to
--lipid_similarity_feature instead of --lipid_descriptor_names (GBM's own way of
consuming a whole-species similarity, since a row classifier has no kernel to swap).

Pair features: WIRED, unlike Kron-RLS's --pair_features (provably impossible for its
closed form -- see run_cron.py's own module docstring). GBM is an ordinary row
classifier with no separable-kernel constraint, so a joint (protein, lipid) value is
just one more feature column: --pair_features is a comma-separated list of
dataloader.pair_descriptors.PAIR_DESCRIPTOR_NAMES entries (occupancy,
aromatic_contact, hbond_match, ...), each computed via pair_descriptor_value off
analysis/gbm_baseline.py's build_pair_feature_inputs (the fixed lipid/protein input
columns every pair descriptor formula reads).

    python3 scripts/run_gbm.py --pair_features=occupancy,aromatic_contact \\
        --split_mode=double --no_logs

--no_logs skips writing test_metrics/gbm_*/ files -- no label needed then, unless
--set_label is also given. --set_label names the run (same role as the positional
`label`) and wins over the positional if both are present.

Terminal output is the SAME layout scripts/run_cron.py prints (Summary/rows header,
test/valid F1+BA by group, Overall metric table, test BA/F1 by group, sens/spec gap,
seed variability, By group sections under --complete) -- computed directly from this
run's own report rows. Kron-RLS-only concepts (protein_lambda/lipid_lambda,
--lambda_grid/--lambda_selection) do not appear here; GBM-only concepts
(--class_weight, --train_negatives_per_positive, hyperparameters,
--lipid_similarity_feature) are written to the report file's config block instead.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# parents[1]: this file sits in scripts/, so the project root is one level up.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.gbm_baseline import (  # noqa: E402
    build_parser,
    build_report,
    load_table,
    resolve_families,
)
from training.pair_baseline_common import (  # noqa: E402
    balance_pool_negatives,
    cold_split_pools,
    csv_classes,
    generate_lipid_isolation_groups,
    resolve_excluded_lipids,
    resolve_family_excluded_lipids,
)

# Same shape as scripts/run_cron.py's own SUMMARY_METRICS -- (build_report() column,
# printed label, is_auc) -- restricted to what a GBM row actually has. is_auc rows
# only print with --complete, same convention.
SUMMARY_METRICS = (
    ("valid_ba", "checkpoint valid BA", False),
    ("valid_f1", "best valid F1", False),
    ("test_ba", "test BA", False),
    ("test_auc", "test AUC", True),
    ("per_protein_auc", "test AUC in-protein", True),
    ("n_proteins", "  (proteins averaged)", True),
    ("pair_auc", "test AUC in-protein (pairs)", True),
    ("n_pair_groups", "  (lipid classes)", True),
    ("test_f1", "test F1", False),
    ("test_sensitivity", "test sensitivity", False),
    ("test_specificity", "test specificity", False),
    ("precision", "test precision", False),
)
SUMMARY_RATE_METRICS = (
    ("FPR (FP/(FP+TN))", "FP", ("FP", "TN")),
    ("FNR (FN/(FN+TP))", "FN", ("FN", "TP")),
)

# Report-file keys a run_gbm.py row can fill -- same bare keys run_cron.py's own
# METRIC_FIELD_MAP uses (gbm_baseline.py's evaluate_block was extended to carry the
# same full confusion-matrix fields for exactly this reason).
METRIC_FIELD_MAP = {
    "total": "total",
    "real_positive": "real_positive",
    "real_negative": "real_negative",
    "predicted_positive": "predicted_positive",
    "predicted_negative": "predicted_negative",
    "TP": "TP",
    "FP": "FP",
    "TN": "TN",
    "FN": "FN",
    "accuracy": "accuracy",
    "sensitivity": "test_sensitivity",
    "precision": "precision",
    "specificity": "test_specificity",
    "IoU": "IoU",
    "FAR": "FAR",
    "F1": "test_f1",
    "balanced_accuracy": "test_ba",
    "AUC": "test_auc",
    "AUC_within_protein": "per_protein_auc",
    "AUC_within_protein_pairs": "pair_auc",
    "AUC_within_protein_proteins": "n_proteins",
}
# GBM's own config fields, in place of run_cron.py's protein_lambda/lipid_lambda/
# lambda_grid/lambda_selection (Kron-RLS-only concepts that do not exist here).
CONFIG_ARG_FIELDS = (
    "split_mode", "protein_descriptor_names", "lipid_descriptor_names",
    "class_weight", "train_negatives_per_positive", "eval_negatives_per_positive",
    "share", "lipid_similarity_feature", "similarity_neighbours", "learning_rate",
    "max_iter", "max_depth", "max_leaf_nodes", "l2_regularization",
    "min_samples_leaf", "threshold_metric",
)


def print_split_brief(table: pd.DataFrame, family: str, seed: int, args: argparse.Namespace) -> None:
    """One line per group: lipid classes in valid/test, valid+test row count.
    Uses seeds[0]'s pool as representative -- printed once per group, not once per
    (group, seed).
    """
    _, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share,
        excluded_lipids=resolve_family_excluded_lipids(args, family),
        merge_valid_test=True,
    )
    valid_pool = balance_pool_negatives(valid_pool, seed, args.eval_negatives_per_positive)
    test_pool = balance_pool_negatives(test_pool, seed, args.eval_negatives_per_positive)
    classes = sorted(set(csv_classes(valid_pool)) | set(csv_classes(test_pool)))
    # valid=test always here: nothing (threshold, early stopping) is fit on valid any
    # more, so halving the excluded block away would only shrink what test measures.
    print(f"{family}: classes={','.join(classes)} | valid=test rows={len(test_pool)} (merged)")


def _format(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if pd.isna(value):
            return "undefined"
        return f"{value:.6f}"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def build_report_text(row: pd.Series, args: argparse.Namespace, run_label: str) -> str:
    lines = [f"label: gbm_{run_label}"]
    for field in CONFIG_ARG_FIELDS:
        lines.append(f"{field}: {_format(getattr(args, field))}")
    lines.append(f"seed: {row['seed']}")
    lines.append(f"excluded_group: {row['family']}")
    lines.append(f"threshold: {_format(row['threshold'])}")
    lines.append(f"train_rows: {row['train_rows']}")
    lines.append(f"train_proteins: {row['train_proteins']}")
    lines.append(f"train_lipids: {row['train_lipids']}")
    lines.append(f"valid_rows: {row['valid_rows']}")
    lines.append(f"test_rows: {row['test_rows']}")
    lines.append(f"valid_balanced_accuracy: {_format(row['valid_ba'])}")
    lines.append(f"valid_F1: {_format(row['valid_f1'])}")
    lines.append(f"valid_AUC: {_format(row['valid_auc'])}")
    lines.append("")
    for report_key, column in METRIC_FIELD_MAP.items():
        lines.append(f"{report_key}: {_format(row[column])}")
    lines.append("loss: undefined")
    lines.append(f"AUC_within_protein_pairs_proteins: {_format(row['n_pair_groups'])}")
    return "\n".join(lines) + "\n"


def write_report(
    row: pd.Series, args: argparse.Namespace, run_label: str, out_dir: Path, run_id: str
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"gbm_metrics_{run_id}.txt"
    path.write_text(build_report_text(row, args, run_label))
    return path


# A --lipid_features value that is EXACTLY one of these (nothing else in the list)
# sets --lipid_similarity_feature directly instead of routing through
# resolve_lipid_feature_subset, which would reject it (a pairwise similarity matrix
# has no per-entity columns to select) -- GBM's own way of consuming a whole-species
# similarity is a dedicated feature COLUMN (training.pair_baseline_common.
# species_tanimoto_similarity/species_headgroup_tanimoto_similarity via null_scores),
# not a kernel swap the way Kron-RLS's --lipid_kernel is. "molformer" is deliberately
# NOT here: it IS a genuine per-entity raw feature table, so resolve_lipid_feature_
# subset already mixes it in alongside named descriptors.
_WHOLE_SIMILARITY_LIPID_NAMES = {"tanimoto", "tanimoto_headgroup"}


def _resolve_descriptor_shorthand(args: argparse.Namespace) -> None:
    """--protein_features/--lipid_features: a bare comma-separated name list sets
    --protein_descriptor_names/--lipid_descriptor_names (or, for a lone whole-species
    similarity name, --lipid_similarity_feature) -- see the module docstring's
    "Convenience feature-list shorthand" section.
    """
    if args.protein_features:
        args.protein_descriptor_names = [
            name for name in args.protein_features.split(",") if name
        ]
    if args.lipid_features:
        requested = [name for name in args.lipid_features.split(",") if name]
        if len(requested) == 1 and requested[0] in _WHOLE_SIMILARITY_LIPID_NAMES:
            args.lipid_similarity_feature = requested[0]
        else:
            args.lipid_descriptor_names = requested
    if args.pair_features:
        args.pair_descriptor_names = [name for name in args.pair_features.split(",") if name]


def _stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _metric_table(frame: pd.DataFrame, indent: str = "", complete: bool = False) -> str:
    lines = [f"{indent}{'metric':22s}  {'mean':>10s}  {'median':>10s}  {'std':>9s}  n"]
    for column, label, is_auc in SUMMARY_METRICS:
        if is_auc and not complete:
            continue
        values = frame[column].dropna().tolist()
        if not values:
            continue
        lines.append(
            f"{indent}{label:22s}  {statistics.mean(values):10.4f}  "
            f"{statistics.median(values):10.4f}  {_stddev(values):9.4f}  {len(values)}"
        )
    for label, numerator, denominators in SUMMARY_RATE_METRICS:
        denominator = sum(frame[column] for column in denominators)
        valid = denominator > 0
        values = (frame[numerator][valid] / denominator[valid]).dropna().tolist()
        if not values:
            continue
        lines.append(
            f"{indent}{label:22s}  {statistics.mean(values):10.4f}  "
            f"{statistics.median(values):10.4f}  {_stddev(values):9.4f}  {len(values)}"
        )
    return "\n".join(lines)


def _mean_std_cell(values: list[float]) -> str:
    if not values:
        return "n/a"
    if len(values) == 1:
        return f"{values[0]:.4f}"
    return f"{statistics.mean(values):.4f}±{_stddev(values):.4f}"


def _by_group_mean_std_table(
    report: pd.DataFrame, columns: tuple[tuple[str, str], ...], name_column: str = "group"
) -> str:
    col_width = 17
    groups = sorted(report["family"].unique()) + ["ALL"]
    name_width = max(len(name_column), *(len(name) for name in groups))
    header = (
        f"{name_column:{name_width}s}  {'n':>3s}  "
        + "  ".join(f"{label:>{col_width}s}" for _, label in columns)
    )
    lines = [header]
    for group in groups:
        frame = report if group == "ALL" else report[report["family"] == group]
        cells = [_mean_std_cell(frame[column].dropna().tolist()) for column, _ in columns]
        lines.append(
            f"{group:{name_width}s}  {len(frame):>3d}  "
            + "  ".join(f"{cell:>{col_width}s}" for cell in cells)
        )
    return "\n".join(lines)


def _f1_ba_by_group_table(report: pd.DataFrame) -> str:
    return _by_group_mean_std_table(
        report,
        (
            ("test_f1", "test_F1"), ("valid_f1", "valid_F1"),
            ("test_ba", "test_BA"), ("valid_ba", "valid_BA"),
        ),
    )


def _test_ba_f1_table(report: pd.DataFrame) -> str:
    return _by_group_mean_std_table(
        report, (("test_ba", "test BA"), ("test_f1", "test F1")), name_column="Group"
    )


def _sens_spec_by_group_table(report: pd.DataFrame) -> str:
    """train_sens/spec is always "n/a" -- HistGradientBoostingClassifier's early
    stopping tracks its own internal validation split, not a train-split confusion
    matrix this report keeps.
    """
    columns = ("test_sens", "test_spec", "train_sens", "train_spec", "valid_sens", "valid_spec")
    col_width = 10
    groups = sorted(report["family"].unique()) + ["ALL"]
    name_width = max(len("group"), *(len(name) for name in groups))
    header = (
        f"{'group':{name_width}s}  {'n':>3s}  "
        + "  ".join(f"{column:>{col_width}s}" for column in columns)
    )

    def cell(frame: pd.DataFrame, column: str | None) -> str:
        if column is None:
            return "n/a"
        values = frame[column].dropna().tolist()
        return f"{statistics.mean(values):.4f}" if values else "n/a"

    lines = [header]
    for group in groups:
        frame = report if group == "ALL" else report[report["family"] == group]
        cells = [
            cell(frame, "test_sensitivity"), cell(frame, "test_specificity"),
            cell(frame, None), cell(frame, None),
            cell(frame, "valid_sensitivity"), cell(frame, "valid_specificity"),
        ]
        lines.append(
            f"{group:{name_width}s}  {len(frame):>3d}  "
            + "  ".join(f"{value:>{col_width}s}" for value in cells)
        )
    return "\n".join(lines)


def _gap_line(report: pd.DataFrame) -> str:
    gaps = (report["test_sensitivity"] - report["test_specificity"]).abs().dropna().tolist()
    if not gaps:
        return "abs(sensitivity-specificity) gap: no rows with both metrics"
    return (
        f"abs(sensitivity-specificity) gap: mean={statistics.mean(gaps):.4f} "
        f"median={statistics.median(gaps):.4f} n={len(gaps)}"
    )


def _seed_variability_lines(report: pd.DataFrame) -> str:
    sens_stds, spec_stds = [], []
    for _, frame in report.groupby("family"):
        sensitivities = frame["test_sensitivity"].dropna().tolist()
        specificities = frame["test_specificity"].dropna().tolist()
        if len(sensitivities) > 1:
            sens_stds.append(_stddev(sensitivities))
        if len(specificities) > 1:
            spec_stds.append(_stddev(specificities))
    lines = []
    if sens_stds:
        lines.append(
            f"sensitivity std across seeds (by group): mean={statistics.mean(sens_stds):.4f} "
            f"median={statistics.median(sens_stds):.4f} n={len(sens_stds)}"
        )
    else:
        lines.append("sensitivity std across seeds (by group): no group with >1 seed")
    if spec_stds:
        lines.append(
            f"specificity std across seeds (by group): mean={statistics.mean(spec_stds):.4f} "
            f"median={statistics.median(spec_stds):.4f} n={len(spec_stds)}"
        )
    else:
        lines.append("specificity std across seeds (by group): no group with >1 seed")
    return "\n".join(lines)


def _by_group_sections(report: pd.DataFrame, complete: bool = False) -> str:
    sections = []
    for group, frame in report.groupby("family"):
        lines = [f"{group} (n={len(frame)}):", _metric_table(frame, indent="  ", complete=complete)]
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def print_standard_summary(report: pd.DataFrame, run_label: str, complete: bool = False) -> None:
    print(f"Summary: 'gbm_{run_label}'")
    print(f"rows: {len(report)}")
    print()
    if complete:
        print("=== Sensitivity / specificity by group (test / train / valid) ===")
        print(_sens_spec_by_group_table(report))
        print()
    print("=== test/valid F1, BA by group ===")
    print(_f1_ba_by_group_table(report))
    print()
    print("=== Overall ===")
    print(_metric_table(report, complete=complete))
    print()
    print("=== test BA / test F1 by group ===")
    print(_test_ba_f1_table(report))
    print()
    print("===", _gap_line(report), "===")
    print(_seed_variability_lines(report))
    if complete:
        print()
        print("=== By group ===")
        print(_by_group_sections(report, complete=complete))


def main() -> None:
    parser = build_parser()
    parser.add_argument(
        "label", nargs="?", default=None,
        help=(
            "run name -- output goes to test_metrics/gbm_<label>/, never "
            "test_metrics/<label>/ (that namespace is the network's own). Optional "
            "with --no_logs (nothing is written then); --set_label overrides it "
            "either way."
        ),
    )
    parser.add_argument(
        "--set_label", default=None,
        help="same role as the positional `label`, as a flag; wins if both are given",
    )
    parser.add_argument(
        "--no_logs", action="store_true",
        help=(
            "print each block's report to the terminal instead of writing "
            "test_metrics/gbm_<label>/ files"
        ),
    )
    parser.add_argument(
        "--pair_features", default=None,
        help=(
            "convenience shorthand: comma-separated dataloader.pair_descriptors."
            "PAIR_DESCRIPTOR_NAMES entries -> --pair_descriptor_names. See module "
            "docstring's Pair features section."
        ),
    )
    parser.add_argument(
        "--complete", action="store_true",
        help=(
            "print the full terminal summary: the sensitivity/specificity-by-group "
            "table and every AUC row, left out of the default (smaller) F1/BA-"
            "focused summary"
        ),
    )
    parser.add_argument(
        "--out_root", type=Path, default=PROJECT_ROOT / "test_metrics",
        help="parent of gbm_<label>/ (default: the project's test_metrics/)",
    )
    parser.add_argument(
        "--protein_features", default=None,
        help=(
            "convenience shorthand: comma-separated names -> "
            "--protein_descriptor_names. See module docstring."
        ),
    )
    parser.add_argument(
        "--lipid_features", default=None,
        help=(
            "convenience shorthand: comma-separated names -> "
            "--lipid_descriptor_names, or --lipid_similarity_feature for a lone "
            "whole-species similarity name. See module docstring."
        ),
    )
    parser.add_argument(
        "--families_number", type=int, default=None,
        help=(
            "generate this many --lipid_coldsplit species blocks via "
            "training.pair_baseline_common.generate_lipid_isolation_groups (analysis/"
            "lipid_block_search.py's search) instead of naming --families by hand -- "
            "not forced disjoint (lipids may repeat across groups), but each pair "
            "kept under 50% Jaccard overlap so groups stay genuinely different "
            "chemistries, persisted into dataloader/lipid_isolation_blocks.py and "
            "used as this run's --families. Only valid with --split_mode "
            "lipid_coldsplit. A single bare --families value combined with this "
            "names the target those groups cluster around, same as "
            "--isolation_target."
        ),
    )
    parser.add_argument(
        "--isolation_target", default=None,
        help=(
            "ONE Tanimoto-isolation target applied to EVERY --families entry under "
            "--split_mode double -- shorthand for suffixing each family with "
            "\"__<target>\" by hand (--families=CRAL-TRIO,START "
            "--isolation_target=0.8 is the same run as "
            "--families=CRAL-TRIO__0.8,START__0.8). A family already carrying its "
            "own \"__<target>\" is left alone. Combined with --families_number "
            "instead, names the target those generated groups cluster around."
        ),
    )
    parser.add_argument(
        "--excluded_lipids", default=None,
        help=(
            "comma-separated FullIdentityOfLipid species names and/or bare "
            "head-group class names (a class expands to every species in it) to "
            "hold out of training directly, bypassing LIPID_COLDSPLIT_SETS/LIPID_"
            "ISOLATION_BLOCKS entirely -- a hand-picked valid/test composition "
            "instead of a named class set or a searched Tanimoto target. Implies the "
            "lipid_coldsplit behaviour (every protein stays in training) on its "
            "own: --split_mode need not be given (and is ignored if it is). Runs "
            "as one group, labeled \"custom\"."
        ),
    )
    parser.add_argument(
        "--excluded_lipid_groups", default=None,
        help=(
            "comma-separated list of INDEPENDENT held-out groups -- scripts/"
            "run_cron.py's own flag of the same name, same syntax: each entry is one "
            "group (an exact FullIdentityOfLipid species, a project head-group "
            "class, or an article LTP-lipid subclass abbreviation -- \"PC\", \"PG\", "
            "..., see files/data_source.md), several names joined with \"+\" held "
            "out TOGETHER as one block. Unlike --excluded_lipids, which merges "
            "everything given into ONE \"custom\" block, comma-separated entries "
            "here stay apart, each its own row. Mutually exclusive with "
            "--excluded_lipids/--families/--families_number."
        ),
    )
    args = parser.parse_args()

    run_label = args.set_label or args.label
    if not args.no_logs and not run_label:
        parser.error("a label is required (positional, or --set_label) unless --no_logs is given")
    run_label = run_label or "adhoc"
    _resolve_descriptor_shorthand(args)

    args.excluded_lipids_species = None
    if args.excluded_lipids:
        if args.families or args.families_number or args.excluded_lipid_groups:
            parser.error(
                "--excluded_lipids gives its own species list directly -- combining "
                "it with --families/--families_number/--excluded_lipid_groups is "
                "ambiguous, drop one"
            )
        args.excluded_lipids_species = tuple(
            name.strip() for name in args.excluded_lipids.split(",") if name.strip()
        )

    excluded_lipid_group_specs = None
    if args.excluded_lipid_groups:
        if args.families or args.families_number:
            parser.error(
                "--excluded_lipid_groups gives its own list of independent groups "
                "-- combining it with --families/--families_number is ambiguous, "
                "drop one"
            )
        excluded_lipid_group_specs = []
        for segment in args.excluded_lipid_groups.split(","):
            segment = segment.strip()
            if not segment:
                continue
            tokens = [token.strip() for token in segment.split("+") if token.strip()]
            if tokens:
                excluded_lipid_group_specs.append((segment, tokens))

    families_number_target = 0.0
    if args.families_number:
        if args.split_mode != "lipid_coldsplit":
            parser.error("--families_number only applies to --split_mode lipid_coldsplit")
        if args.isolation_target and args.families:
            parser.error(
                "--isolation_target and --families both name a target for "
                "--families_number -- give only one"
            )
        if args.isolation_target:
            families_number_target = float(args.isolation_target)
        elif args.families:
            # --families=0.6 --families_number=3: the bare target those 3 groups
            # should cluster around, the same role --isolation_target plays.
            given = [name for name in args.families.split(",") if name]
            if len(given) != 1:
                parser.error(
                    "--families_number combined with --families needs exactly ONE "
                    "value -- the target isolation those groups should cluster "
                    "around (e.g. --families=0.6 --families_number=3), not a list "
                    "of groups to run (that is what --families_number itself "
                    "generates)"
                )
            try:
                families_number_target = float(given[0])
            except ValueError:
                parser.error(
                    f"--families_number combined with --families needs a numeric "
                    f"target, got {given[0]!r}"
                )
    if args.isolation_target and args.split_mode not in ("double", "lipid_coldsplit"):
        parser.error("--isolation_target only applies to --split_mode double/lipid_coldsplit")

    table = load_table(args)
    if excluded_lipid_group_specs:
        resolved_groups: dict[str, tuple[str, ...]] = {}
        for label, tokens in excluded_lipid_group_specs:
            try:
                resolved_groups[label] = resolve_excluded_lipids(table, tokens)
            except ValueError as error:
                parser.error(str(error))
        args.excluded_lipids_species = resolved_groups
        families = list(resolved_groups.keys())
    elif args.excluded_lipids_species:
        try:
            args.excluded_lipids_species = resolve_excluded_lipids(
                table, list(args.excluded_lipids_species)
            )
        except ValueError as error:
            parser.error(str(error))
        families = ["custom"]
    elif args.families_number:
        families = generate_lipid_isolation_groups(
            table, args.families_number, target=families_number_target
        )
    else:
        families = resolve_families(args)
    if args.isolation_target and args.split_mode == "double":
        families = [
            family if "__" in family else f"{family}__{args.isolation_target}"
            for family in families
        ]
    seeds = [int(value) for value in args.seeds.split(",")]

    for family in families:
        print_split_brief(table, family, seeds[0], args)
    print()

    report = build_report(table, families, seeds, args)
    print_standard_summary(report, run_label, complete=args.complete)

    if not args.no_logs:
        run_dir = args.out_root / f"gbm_{run_label}"
        written = []
        for _, row in report.iterrows():
            group_dir = run_dir / f"groups_{row['family']}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_id = f"{timestamp}_seed{row['seed']}"
            written.append(write_report(row, args, run_label, group_dir, run_id))
        print(f"\nwrote {len(written)} report(s) under {run_dir}")

    if args.out:
        report.to_json(args.out, orient="records", indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
