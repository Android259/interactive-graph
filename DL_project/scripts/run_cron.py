#!/usr/bin/env python3
"""Label-driven runner for analysis/kronrls_baseline.py -- writes test_metrics/ reports.

Takes a label (arbitrary name, like a network arg-file's own label) and runs the
Kron-RLS calculation over it, then writes one report file per (excluded block, seed)
under

    test_metrics/cron_<label>/groups_<block>/cron_metrics_<timestamp>_seed<seed>.txt

-- same directory shape as a real network run's test_metrics/<label>/groups_<set>/
(so a human/agent already used to reading those can read these the same way), but
filenames start with `cron_metrics_`, not `test_metrics_`. Deliberate: analysis/
build_metrics_table.py's own `rglob("test_metrics_*.txt")` would otherwise pick
these up and either crash (parse_metric_filename expects a network run's exact
filename shape: timestamp + parameter string) or, worse, silently merge Kron-RLS
rows into metrics_summary.csv, the network's own canonical table. `cron_*` on the
label and `cron_metrics_` on the filename both exist to keep this baseline in its
own, clearly separate namespace.

Every kronrls_baseline.py flag works here unchanged (this file reuses its own
argument parser, analysis.kronrls_baseline.build_parser(), so the two can never
silently drift apart) -- split axis, kernels, lambda grid, threshold metric, etc.
--families omitted runs every default block for the chosen --split_mode ("without
groups" -- --split_mode lipid_coldsplit with no --families runs all four
LIPID_COLDSPLIT_SETS; single/double runs all seven project families).

    python3 scripts/run_cron.py protunion14_headgroup \\
        --split_mode lipid_coldsplit --seeds 0,1,2,3,4 \\
        --protein_kernel pocket_subset --protein_descriptor_names=\\
pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,\\
apolar_sasa_share,aromatic_share,hydropathy_rim,depth_q10,hydropathy_core,\\
pocket_extent --lipid_kernel tanimoto_headgroup --lambda_grid 0.01,0.1,1,10,100

    python3 scripts/run_cron.py quick_check --split_mode single --seeds 0

Writes to test_metrics/cron_<label>/ (and, if --out is also given, the usual JSON
report kronrls_baseline.py's own --out writes). Nothing outside test_metrics/cron_*
and --out's own path is touched; metrics_summary.csv is never read or written.

Convenience feature-list shorthand. --protein_features and --lipid_features are
kronrls_baseline.py's own flags (a CSV path, for --protein_kernel/--lipid_kernel=
custom_features) -- here they ALSO accept a bare comma-separated descriptor-name
list, sniffed by whether the value is an existing file: if it isn't, it is treated
as names for --protein_kernel=pocket_subset / --lipid_kernel=explicit_subset
respectively (--protein_descriptor_names / --lipid_descriptor_names, set
automatically), the two-flag combination kronrls_baseline.py itself still requires
directly. An existing CSV path keeps the original custom_features meaning.

    python3 scripts/run_cron.py protunion14 --split_mode lipid_coldsplit \\
        --protein_features=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,\\
buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,depth_q10,\\
hydropathy_core,pocket_extent --lipid_features=logp,tpsa,ring_count

Pair features: not supported, and not simply unimplemented -- two_step_kronrls's
closed form needs exactly two SEPARABLE kernels (protein x protein, lipid x lipid)
for the Kronecker identity that makes the two sequential solves equal one joint
solve. A pair descriptor (npr1/npr2, pocket_shares, ...) is a joint (protein, lipid)
value by construction and does not factor into either kernel alone, so there is no
well-defined place for it in this method -- passing --pair_features fails fast with
that explanation rather than silently doing something else with it.

--no_logs skips writing test_metrics/cron_*/ files -- no label needed then, unless
--set_label is also given. --set_label names the run (same role as the positional
`label`, provided as a flag for scripting convenience) and, when given, wins over
the positional if both are present.

Terminal output is the SAME layout analysis/summarize_label.py prints for a network
label after training (Summary/rows header, sensitivity-specificity-by-group table,
Overall metric table, sens/spec gap, seed variability, By group sections) --
computed directly from this run's own report rows, not from metrics_summary.csv
(this label was never written there). Metrics that summarize_label.py has and this
one structurally cannot (checkpoint-epoch train sensitivity/specificity -- Kron-RLS
has no training dynamics to checkpoint; test loss -- no loss concept for a
closed-form fit; "max valid BA" -- no per-epoch history to take a max over) print as
"n/a" or are skipped, the same way that script already skips a column a pre-
instrumentation network run never wrote, never fabricated to fill the shape.
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

from analysis.kronrls_baseline import (  # noqa: E402
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
)

# analysis/summarize_label.py's own METRICS table, restricted to what a Kron-RLS row
# actually has: (build_report() column, printed label, is_auc), same order/wording
# as that script where the concept genuinely matches ("test BA", "test AUC", ...);
# dropped where it does not (max_valid_balanced_accuracy has no per-epoch history to
# take a max over; test loss has no loss concept here) rather than fabricated.
# "(proteins contributing)" becomes "(lipid classes)" for AUC_within_protein_pairs'
# own count, since per_pair_auc counts lipid-class groups, not proteins -- see
# analysis/null_model.py's per_pair_auc docstring; relabeled rather than mislabeled.
# is_auc rows only print with --complete (AUC is left out of the default summary
# for now -- see this file's own header for why, once it has one).
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
# (label, numerator column, denominator columns) -- same FPR/FNR compare_labels.py
# reports, computed directly from our own TP/FP/TN/FN instead of re-reading them
# from a written report.
SUMMARY_RATE_METRICS = (
    ("FPR (FP/(FP+TN))", "FP", ("FP", "TN")),
    ("FNR (FN/(FN+TP))", "FN", ("FN", "TP")),
)

# Report-file keys a run_cron.py row can actually fill, in the order a network's own
# test_metrics_*.txt lists its metric block (see that file's tail) -- values missing
# here (loss, everything ModelConfig-only) are written as "undefined", never
# fabricated. Left side: report-file key. Right side: the build_report() column it
# comes from.
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
# Config/provenance keys, written above the metric block -- kronrls_baseline.py's
# own args plus what the split resolved to, not a ModelConfig field dump (this is
# not a network run and faking hiddim/lr/etc. for it would be actively misleading,
# not just incomplete).
CONFIG_ARG_FIELDS = (
    "split_mode", "protein_kernel", "protein_kernel_type", "protein_descriptor_names",
    "lipid_kernel", "lipid_kernel_type", "lipid_descriptor_names", "protein_lambda",
    "lipid_lambda", "positive_weight", "eval_negatives_per_positive", "share",
    "lipid_class_targets", "select_metric", "threshold_metric",
)


def print_split_brief(table: pd.DataFrame, family: str, seed: int, args: argparse.Namespace) -> None:
    """One line per group: lipid classes in valid/test, valid+test row count.
    Uses seeds[0]'s pool as representative (train/class composition is fixed per
    group; valid/test size barely moves across seeds) -- printed once per group,
    not once per (group, seed), to avoid repeating the same line seeds times.
    """
    _, valid_pool, test_pool = cold_split_pools(
        table, family, seed, args.split_mode, args.share,
        excluded_lipids=getattr(args, "excluded_lipids_species", None),
    )
    valid_pool = balance_pool_negatives(valid_pool, seed, args.eval_negatives_per_positive)
    test_pool = balance_pool_negatives(test_pool, seed, args.eval_negatives_per_positive)
    classes = sorted(set(csv_classes(valid_pool)) | set(csv_classes(test_pool)))
    print(f"{family}: classes={','.join(classes)} | valid+test rows={len(valid_pool) + len(test_pool)}")


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
    lines = [f"label: cron_{run_label}"]
    for field in CONFIG_ARG_FIELDS:
        lines.append(f"{field}: {_format(getattr(args, field))}")
    lines.append(f"seed: {row['seed']}")
    lines.append(f"excluded_group: {row['family']}")
    lines.append(f"lambda_grid_protein_lambda: {_format(row['protein_lambda'])}")
    lines.append(f"lambda_grid_lipid_lambda: {_format(row['lipid_lambda'])}")
    lines.append(f"threshold: {_format(row['threshold'])}")
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
    path = out_dir / f"cron_metrics_{run_id}.txt"
    path.write_text(build_report_text(row, args, run_label))
    return path


# Whole-kernel lipid similarity types -- a --lipid_features value that is EXACTLY
# one of these (nothing else in the list) sets --lipid_kernel directly instead of
# routing through explicit_subset, which would reject it (a pairwise similarity
# matrix has no per-entity columns to select). Mirrors what
# training.pair_baseline_common.build_lipid_kernel's own explicit_subset branch
# already tells the user in its error hint -- "name a whole different
# --lipid_kernel" -- so --lipid_features=tanimoto_headgroup just does that instead
# of failing and asking the user to pass --lipid_kernel by hand. "molformer" is
# deliberately NOT here: unlike tanimoto/tanimoto_headgroup it IS a genuine
# per-entity raw feature table (molformer_lipid_features), so explicit_subset can
# and does mix it in alongside named descriptors (--lipid_features=chain,molformer).
_WHOLE_KERNEL_LIPID_NAMES = {"tanimoto", "tanimoto_headgroup"}


def _resolve_descriptor_shorthand(args: argparse.Namespace) -> None:
    """--protein_features/--lipid_features: a bare name list (not an existing file)
    switches the matching kernel to pocket_subset/explicit_subset automatically --
    see the module docstring's "Convenience feature-list shorthand" section.
    """
    if args.protein_features and not Path(args.protein_features).is_file():
        args.protein_descriptor_names = [
            name for name in args.protein_features.split(",") if name
        ]
        args.protein_kernel = "pocket_subset"
        args.protein_features = None
    if args.lipid_features and not Path(args.lipid_features).is_file():
        requested = [name for name in args.lipid_features.split(",") if name]
        if len(requested) == 1 and requested[0] in _WHOLE_KERNEL_LIPID_NAMES:
            args.lipid_kernel = requested[0]
        else:
            args.lipid_descriptor_names = requested
            args.lipid_kernel = "explicit_subset"
        args.lipid_features = None


def _stddev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _metric_table(frame: pd.DataFrame, indent: str = "", complete: bool = False) -> str:
    """analysis/summarize_label.py's format_metrics_table, over our own DataFrame
    instead of metrics_summary.csv rows. AUC rows only print with complete=True
    (--complete) -- left out of the default summary for now.
    """
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
    """One row per group (plus ALL), one "mean+-std across that group's seeds" cell
    per (build_report() column, header label) in `columns` -- the shared renderer
    behind both _f1_ba_by_group_table and _test_ba_f1_table below.
    """
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
    """Per-group test/valid F1 and BA -- the default first table (replaces the old
    sensitivity/specificity-by-group one, still available under --complete via
    _sens_spec_by_group_table below).
    """
    return _by_group_mean_std_table(
        report,
        (
            ("test_f1", "test_F1"), ("valid_f1", "valid_F1"),
            ("test_ba", "test_BA"), ("valid_ba", "valid_BA"),
        ),
    )


def _test_ba_f1_table(report: pd.DataFrame) -> str:
    """Group / test BA / test F1 -- always printed, complete or not (unlike every
    other table here, which --complete gates in one direction or another).
    """
    return _by_group_mean_std_table(
        report, (("test_ba", "test BA"), ("test_f1", "test F1")), name_column="Group"
    )


def _sens_spec_by_group_table(report: pd.DataFrame) -> str:
    """analysis/summarize_label.py's format_sens_spec_by_group. train_sens/spec is
    always "n/a" -- Kron-RLS has no training-dynamics checkpoint to read a train-
    split confusion matrix from, the same "n/a" a pre-instrumentation network run
    shows for checkpoint_train_sensitivity there.
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
    """analysis/summarize_label.py's terminal layout, computed straight from this
    run's own report rows instead of metrics_summary.csv (cron_* labels are
    deliberately never written there -- see the module docstring). AUC rows and the
    old sensitivity/specificity-by-group table only print with complete=True
    (--complete); the default is the smaller F1/BA-by-group table instead.
    """
    print(f"Summary: 'cron_{run_label}'")
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
            "run name -- output goes to test_metrics/cron_<label>/, never "
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
            "test_metrics/cron_<label>/ files"
        ),
    )
    parser.add_argument(
        "--pair_features", default=None,
        help="NOT SUPPORTED -- see module docstring's Pair features section for why",
    )
    parser.add_argument(
        "--complete", action="store_true",
        help=(
            "print the full terminal summary: the old sensitivity/specificity-by-"
            "group table and every AUC row, left out of the default (smaller) "
            "F1/BA-focused summary"
        ),
    )
    parser.add_argument(
        "--out_root", type=Path, default=PROJECT_ROOT / "test_metrics",
        help="parent of cron_<label>/ (default: the project's test_metrics/)",
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
    args = parser.parse_args()

    if args.pair_features:
        parser.error(
            "--pair_features is not supported: two_step_kronrls needs two SEPARABLE "
            "kernels (protein x protein, lipid x lipid) for its closed form; a pair "
            "descriptor is a joint (protein, lipid) value and does not factor into "
            "either one alone. See this file's own module docstring."
        )
    run_label = args.set_label or args.label
    if not args.no_logs and not run_label:
        parser.error("a label is required (positional, or --set_label) unless --no_logs is given")
    run_label = run_label or "adhoc"
    _resolve_descriptor_shorthand(args)

    args.excluded_lipids_species = None
    if args.excluded_lipids:
        if args.families or args.families_number:
            parser.error(
                "--excluded_lipids gives its own species list directly -- combining "
                "it with --families/--families_number is ambiguous, drop one"
            )
        args.excluded_lipids_species = tuple(
            name.strip() for name in args.excluded_lipids.split(",") if name.strip()
        )

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
            # should cluster around, the same role --isolation_target plays --
            # exactly what a user reaching for --families to name ONE group
            # naturally tries when asking for several around it instead.
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
    if args.excluded_lipids_species:
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
        run_dir = args.out_root / f"cron_{run_label}"
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
