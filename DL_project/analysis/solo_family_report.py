#!/usr/bin/env python3
"""The whole solo (--family_only) line in one pass: metrics, the competitor it has to
beat, the figures, and the write-up.

Why this is one script rather than a handful. The solo sweep is the only line in the
project whose runs cannot be read by the normal tooling, and every previous look at it
re-derived the same three workarounds:

  1. There is no `scripts/arg_files/<label>.md` for it -- scripts/submit/
     structural_pretrain_solo.sh builds the arguments with sed -- so
     analysis/checkpoint_scores.py cannot rebuild the configuration. It CAN be rebuilt
     from the argv the run saved next to each checkpoint
     (models/<label>/groups_<family>/seed<N>.args.json), which is what this does.
  2. The sweep saves only the final `seed<N>.pt`, no `dynamics/` directory, so anything
     epoch-indexed is unavailable -- but that final file IS the tested model here
     (--save_model), unlike every lipid-cold-split label, where the tested weights are
     not saved at all.
  3. The split is WARM (a random split inside one family: 19-77% of the test block's
     lipids are also in training), so 0.500 is a meaningless bar and the per-lipid /
     per-class priors printed in the log are a weak one. The competitor that matters is
     the same no-training chemistry lookup the lipid-cold-split line is read against
     (dataloader.chemistry_prior), computed on the same rows.

Read by AUC_within_protein_pairs MINUS the same quantity for the within-protein
competitor. The first term removes the protein marginal (comparisons never cross a
protein boundary); the second removes the lipid marginal, which a warm split leaves free
and which is what the raw 0.9 AUC of this line mostly is. The difference is the only
quantity on which this line and the cold-split line are comparable at all -- see
files/lcs_marginal_removal_and_solo_on_one_metric.md section 8.

Reads only: no training, no writes to metrics_summary.csv or any other shared table.
Writes exactly what --out-csv / --report / --figures name.

    scripts/env.sh python3 analysis/solo_family_report.py
    scripts/env.sh python3 analysis/solo_family_report.py \
        --labels structural_pretrain_family_scratch --seeds 0,1,2 --no-figures
"""
import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

# Same reason as new_train.py: set before any thread exists, so intra-op workers inherit
# it -- a checkpoint whose dead blocks decayed into denormals evaluates orders of
# magnitude slower otherwise, for bit-identical output.
torch.set_flush_denormal(True)

import torch_geometric  # noqa: E402,F401

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.chemistry_prior import null_scores, null_scores_within_protein  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from checkpoint_scores import score_split  # noqa: E402
from null_model import TANIMOTO, resolve_similarity  # noqa: E402
# The three metric bodies live in cross_sampler_eval so the two scripts cannot drift;
# within_protein_pair_auc there mirrors training/new_train.py:730-769 line for line.
from cross_sampler_eval import (  # noqa: E402
    balanced_accuracy, binary_auc, within_protein_pair_auc,
)

DEFAULT_LABELS = (
    "structural_pretrain_family_scratch",
    "structural_pretrain_family",
    # The arm files/lipid_coldsplit_architecture_direction.md section 9 asked for:
    # the pretrained encoders WITHOUT --freeze_pretrained_encoders, so that the
    # frozen arm is not being compared to a control that trains everything.
    "structural_pretrain_family_unfrozen",
)
# Below this many test rows a family carries no readable number at all (ML and OSBP come
# out at two rows); kept in the table, excluded from every pooled figure and from the
# plots, and said so rather than silently dropped.
READABLE_MINIMUM_ROWS = 9
LOG_DIRECTORY = os.path.join(PROJECT_ROOT, "script_logs", "structural_pretrain")
PRIOR_LINE = re.compile(
    r"lipid prior baseline test : balanced accuracy ([\d.]+) by lipid, ([\d.]+) by class"
    r" \| (\d+)% of rows"
)
EPOCH_LINE = re.compile(r"valid epoch balanced_accuracy: ([\d.]+)")


def confusion_metrics(labels, scores, threshold=0.5):
    """Every threshold-0.5 metric the run's own TEST block prints, from the same scores.

    Recomputed here rather than parsed out of test_metrics/*.txt so that they sit on the
    identical rows and identical weights as the ranking metrics above -- the reports are
    a second source that can only agree or disagree, not add anything.
    """
    labels = np.asarray(labels)
    predicted = (np.asarray(scores, dtype=float) >= threshold).astype(int)
    tp = int(((predicted == 1) & (labels == 1)).sum())
    fn = int(((predicted == 0) & (labels == 1)).sum())
    tn = int(((predicted == 0) & (labels != 1)).sum())
    fp = int(((predicted == 1) & (labels != 1)).sum())
    nan = float("nan")
    sensitivity = tp / (tp + fn) if (tp + fn) else nan
    specificity = tn / (tn + fp) if (tn + fp) else nan
    precision = tp / (tp + fp) if (tp + fp) else nan
    f1 = (2 * precision * sensitivity / (precision + sensitivity)
          if precision == precision and sensitivity == sensitivity
          and (precision + sensitivity) else nan)
    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": (tp + tn) / len(labels) if len(labels) else nan,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "F1": f1,
        "IoU": tp / (tp + fp + fn) if (tp + fp + fn) else nan,
        "FAR": fp / (fp + tn) if (fp + tn) else nan,
        # The recurring asymmetry of this project: specificity tracks training while
        # sensitivity collapses. Signed, so the direction is visible, not just the size.
        "sens_spec_gap": (specificity - sensitivity
                          if specificity == specificity and sensitivity == sensitivity
                          else nan),
    }


def log_curve(label, family, seed):
    """Per-epoch validation balanced accuracy, as the run printed it. [] when no log."""
    path = os.path.join(LOG_DIRECTORY, f"{label}_{family}_seed{seed}_batch16.log")
    if not os.path.exists(path):
        return []
    return [float(x) for x in EPOCH_LINE.findall(open(path).read())]


def log_priors(label, family, seed):
    """(per-lipid prior, per-class prior, share of test rows whose lipid is in train).

    The run prints these; they are the bar the earlier reading of this line used. Kept
    for continuity even though the chemistry competitor below is the stronger one, and
    because the "seen in train" share is the direct measure of how warm the split is.
    Missing log -> (nan, nan, nan) rather than a hard failure: the checkpoints are the
    primary source here, the logs only annotate them.
    """
    path = os.path.join(LOG_DIRECTORY, f"{label}_{family}_seed{seed}_batch16.log")
    if not os.path.exists(path):
        return float("nan"), float("nan"), float("nan")
    match = PRIOR_LINE.search(open(path).read())
    if not match:
        return float("nan"), float("nan"), float("nan")
    return float(match.group(1)), float(match.group(2)), float(match.group(3)) / 100.0


def families_of(label):
    root = os.path.join(PROJECT_ROOT, "models", label)
    if not os.path.isdir(root):
        raise SystemExit(f"no such label directory: {root}")
    return sorted(
        name[len("groups_"):] for name in os.listdir(root) if name.startswith("groups_")
    )


def score_one(label, family, seed, data_dir, similarity, index, entity_column):
    """One (label, family, seed): the model's metrics and the competitors', same rows.

    The configuration comes from the argv the run itself saved, so the split rebuilt here
    is the split it trained on -- the loader is deterministic in the seed. --num_workers
    is overridden to 0 because this is a single-process read.
    """
    base = os.path.join(PROJECT_ROOT, "models", label, f"groups_{family}", f"seed{seed}")
    if not (os.path.exists(base + ".pt") and os.path.exists(base + ".args.json")):
        return None
    argv = [a for a in json.load(open(base + ".args.json")) if not a.startswith("--num_workers")]
    conf = read_configuration(["solo_family_report"] + argv + ["--num_workers=0"])
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    csv = pd.read_csv(interaction_csv_path(data_dir))
    train_dataset, _, test_dataset = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups, config=conf,
        excluded_groups=conf.excluded_groups,
    )
    del csv
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(base + ".pt", map_location="cpu", weights_only=True))
    parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    scores, labels = score_split(model, conf, test_dataset, torch.device("cpu"))

    train_frame, test_frame = train_dataset.csv, test_dataset.csv
    proteins = test_frame["LTPProtein"].to_numpy()
    model_pairs, blocks = within_protein_pair_auc(proteins, labels, scores)

    # The two no-training competitors, on these very rows. lipid_only ignores the protein
    # ("is this chemistry usually bound by anybody"); within_protein restricts the lookup
    # to this protein's own training rows, and is the one the pair metric has to beat.
    lipid_only = null_scores(
        train_frame, test_frame[entity_column], similarity, index, conf.chem_neighbours,
        entity_column,
    )
    within = null_scores_within_protein(
        train_frame, test_frame, similarity, index, conf.chem_neighbours, entity_column,
    )
    truth = test_frame["Interaction"].to_numpy()

    def competitor(values):
        finite = ~np.isnan(np.asarray(values, dtype=float))
        pooled = binary_auc(truth[finite], np.asarray(values, dtype=float)[finite])
        pairs, _ = within_protein_pair_auc(
            proteins[finite], truth[finite], np.asarray(values, dtype=float)[finite]
        )
        return pooled, pairs, float(finite.mean())

    lipid_pooled, lipid_pairs, _ = competitor(lipid_only)
    within_pooled, within_pairs, within_covered = competitor(within)
    prior_lipid, prior_class, seen = log_priors(label, family, seed)
    curve = log_curve(label, family, seed)
    del train_dataset, test_dataset, model
    return {
        **confusion_metrics(labels, scores),
        "valid_curve": curve,
        "valid_last": curve[-1] if curve else float("nan"),
        "valid_max": max(curve) if curve else float("nan"),
        "valid_max_epoch": (int(np.argmax(curve)) + 1) if curve else float("nan"),
        "label": label, "family": family, "seed": seed, "parameters": parameters,
        "train_rows": len(train_frame), "test_rows": len(test_frame),
        "positives": int(truth.sum()), "proteins": int(test_frame["LTPProtein"].nunique()),
        "seen_in_train": seen, "prior_by_lipid": prior_lipid, "prior_by_class": prior_class,
        "BA": balanced_accuracy(labels, scores),
        "AUC": binary_auc(labels, scores),
        "AUC_within_protein_pairs": model_pairs,
        "AUC_within_protein_pairs_proteins": blocks,
        "null_lipid_only_AUC": lipid_pooled,
        "null_lipid_only_pairs": lipid_pairs,
        "null_within_protein_AUC": within_pooled,
        "null_within_protein_pairs": within_pairs,
        "null_within_protein_covered": within_covered,
        "skill_pairs": model_pairs - within_pairs,
        "skill_pairs_vs_best": model_pairs - max(within_pairs, lipid_pairs),
    }


def aggregate(table):
    """Per (label, family) means with the SEM of the PAIRED skill, not of two means.

    The competitor and the model see identical rows, so their shared per-seed variance
    (which split this seed drew) cancels in the difference -- taking the SEM of the
    difference is both tighter and the honest one.
    """
    grouped = table.groupby(["label", "family"])
    summary = grouped.agg(
        seeds=("seed", "count"),
        test_rows=("test_rows", "mean"),
        positives=("positives", "mean"),
        proteins=("proteins", "mean"),
        seen_in_train=("seen_in_train", "mean"),
        prior_best=("prior_by_class", "mean"),
        BA=("BA", "mean"), BA_sem=("BA", "sem"),
        AUC=("AUC", "mean"), AUC_sem=("AUC", "sem"),
        sensitivity=("sensitivity", "mean"), sensitivity_sem=("sensitivity", "sem"),
        specificity=("specificity", "mean"), specificity_sem=("specificity", "sem"),
        precision=("precision", "mean"), F1=("F1", "mean"),
        sens_spec_gap=("sens_spec_gap", "mean"), sens_spec_gap_sem=("sens_spec_gap", "sem"),
        valid_max=("valid_max", "mean"), valid_max_epoch=("valid_max_epoch", "mean"),
        valid_last=("valid_last", "mean"),
        pairs=("AUC_within_protein_pairs", "mean"),
        pairs_sem=("AUC_within_protein_pairs", "sem"),
        blocks=("AUC_within_protein_pairs_proteins", "mean"),
        null_pairs=("null_within_protein_pairs", "mean"),
        null_lipid_pairs=("null_lipid_only_pairs", "mean"),
        null_AUC=("null_within_protein_AUC", "mean"),
        null_lipid_AUC=("null_lipid_only_AUC", "mean"),
        skill=("skill_pairs", "mean"), skill_sem=("skill_pairs", "sem"),
        skill_best=("skill_pairs_vs_best", "mean"),
    ).reset_index()
    summary["prior_best"] = table.groupby(["label", "family"])[
        ["prior_by_lipid", "prior_by_class"]
    ].mean().max(axis=1).values
    return summary


def make_figures(labels):
    """graphics/<label>/{subgroups,learning_curves}/*.pdf via the project's OWN
    generator, unmodified -- scripts/generate_config_graphics.sh, the exact command
    every other label's --graphics uses. It reads metrics_summary.csv and
    run/<label>/groups_<family>/... TensorBoard runs directly and does not touch
    arg_lines()/--excluded_groups, so it needs no adaptation for --family_only: verified
    to complete (exit 0) on all three solo labels, producing the standard
    learning_curves/<family>/<metric>.pdf and subgroups/<label>_<metric>_by_subgroup.pdf
    layout, the same one graphics/<other-label>/ already has.
    """
    written = []
    for label in labels:
        result = subprocess.run(
            [os.path.join(PROJECT_ROOT, "scripts", "generate_config_graphics.sh"), label],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
        )
        directory = os.path.join(PROJECT_ROOT, "graphics", label)
        produced = []
        for root, _, files in os.walk(directory):
            produced += [os.path.join(root, f) for f in files if f.endswith(".pdf")]
        if result.returncode and not produced:
            print(f"generate_config_graphics.sh failed for {label}: "
                  f"{result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ''}",
                  flush=True)
        for path in sorted(produced):
            written.append(path)
        print(f"{label}: wrote {len(produced)} figure(s) under graphics/{label}/", flush=True)
    return written


def write_label_md(label, table, similarity, index, entity_column):
    """graphics/<label>/<label>.md -- same file, same location, same first section as
    every other label's --summarize output; only the second section is label-specific.

    Section 1 (## Summary) is literally analysis/summarize_label.py's own output --
    split-axis-agnostic (it reads test_metrics/*.txt), so it needs no adaptation and is
    run exactly as scripts/lib/generate_label_report.sh runs it for every other label.

    Section 2 (## AUC vs chemistry null model) is where the standard tool
    (analysis/full_label_report.py) breaks for this label: it rebuilds the split via
    analysis/null_model.py's working_set/null_model_table, which reconstructs an
    EXCLUDED-family split (--excluded_groups/--lipid_coldsplit) -- the opposite of
    --family_only, which RESTRICTS the table to one family and splits randomly inside
    it. Patching that split reconstruction into the shared tool would mean
    special-casing --family_only inside code that three other pipelines
    (checkpoint_scores, null_model, interaction_increment) all assume behaves like an
    exclusion axis; the correct split for this axis is already implemented once, in
    score_one() above via PLIDataset itself. So this section is filled from THAT table
    instead of by calling full_label_report.py, in the same row/column shape its
    "null model (chemistry_null_model.py)" block uses, so the two read the same either
    way.
    """
    summary_result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "analysis", "summarize_label.py"),
         label, "--by-groups"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    lines = [f"# {label}", "", "## Summary (analysis/summarize_label.py)", "", "```"]
    lines.append(summary_result.stdout.rstrip() or "(no output)")
    if summary_result.returncode:
        lines.append("(summarize_label.py exited non-zero; output above, if any, is what "
                     "it printed before failing)")
    lines += ["```", "", "## AUC vs chemistry null model, same rows (analysis/solo_family_report.py)",
              "", "Not analysis/full_label_report.py: its null model reconstructs an "
              "EXCLUDED-family split, the opposite of --family_only (restricts to one "
              "family, splits randomly inside it) -- see this function's own docstring.", "",
              "```"]
    rows = table[table["label"] == label].sort_values(["family", "seed"])
    header = (f"{'fam':13}{'seed':>5}{'rows':>6}{'pos':>5}{'seen_in_train':>14}"
              f"{'net_AUC':>9}{'net_AUC_pairs':>14}{'proteins':>9}"
              f"{'null_AUC':>10}{'null_AUC_pairs':>15}")
    lines.append(header)
    for _, r in rows.iterrows():
        lines.append(
            f"{r['family']:13}{r['seed']:>5}{r['test_rows']:>6.0f}{r['positives']:>5.0f}"
            f"{r['seen_in_train']:>14.3f}{r['AUC']:>9.3f}"
            f"{r['AUC_within_protein_pairs']:>14.3f}{r['AUC_within_protein_pairs_proteins']:>9.1f}"
            f"{r['null_within_protein_AUC']:>10.3f}{r['null_within_protein_pairs']:>15.3f}"
        )
    lines += ["```", ""]
    output = os.path.join(PROJECT_ROOT, "graphics", label, f"{label}.md")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as handle:
        handle.write("\n".join(lines))
    return output


def write_report(table, summary, path, figures, labels):
    readable = summary[summary["test_rows"] >= READABLE_MINIMUM_ROWS]
    unreadable = sorted(set(summary[summary["test_rows"] < READABLE_MINIMUM_ROWS]["family"]))
    rows = table[table["test_rows"] >= READABLE_MINIMUM_ROWS]
    lines = [
        "# Solo (`--family_only`) line: what it scores and what that is worth",
        "",
        "Generated by `analysis/solo_family_report.py` (reads only). One model per protein",
        "family, WARM split -- a random split inside the family -- so the bar is not 0.500 and",
        "not the per-class prior the log prints, but the no-training chemistry lookup computed",
        "on the same rows. Read by `AUC_within_protein_pairs` minus that lookup: the first term",
        "removes the protein marginal, the second the lipid marginal a warm split leaves free.",
        "",
        f"Families with fewer than {READABLE_MINIMUM_ROWS} test rows carry no readable number and are",
        f"excluded from every pooled figure and from the plots: {', '.join(unreadable) or 'none'}.",
        "",
        "## Per family",
        "",
    ]
    for label in labels:
        block = readable[readable["label"] == label].sort_values("test_rows", ascending=False)
        if block.empty:
            continue
        lines += [
            f"### `{label}`", "",
            "| family | test rows | + | белков в парной метрике | доля липидов теста в train |"
            " модель (парная) | соперник | **skill** |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for _, r in block.iterrows():
            lines.append(
                f"| {r['family']} | {r['test_rows']:.0f} | {r['positives']:.0f} |"
                f" {r['blocks']:.1f} | {r['seen_in_train']:.0%} |"
                f" {r['pairs']:.3f} ± {r['pairs_sem']:.3f} | {r['null_pairs']:.3f} |"
                f" **{r['skill']:+.3f} ± {r['skill_sem']:.3f}** |"
            )
        pooled = rows[rows["label"] == label]
        skill, sem = pooled["skill_pairs"].mean(), pooled["skill_pairs"].sem()
        lines += [
            "",
            f"Пул по {block.shape[0]} читаемым семьям: модель "
            f"**{pooled['AUC_within_protein_pairs'].mean():.3f} ± "
            f"{pooled['AUC_within_protein_pairs'].sem():.3f}**, соперник "
            f"**{pooled['null_within_protein_pairs'].mean():.3f}**, "
            f"skill **{skill:+.3f} ± {sem:.3f}** "
            f"({abs(skill / sem) if sem else float('nan'):.1f}σ).",
            "",
            "| family | BA | AUC | соперник (AUC) | sensitivity | specificity |"
            " spec − sens | пик valid BA (эпоха) |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for _, r in block.iterrows():
            lines.append(
                f"| {r['family']} | {r['BA']:.3f} ± {r['BA_sem']:.3f} |"
                f" {r['AUC']:.3f} ± {r['AUC_sem']:.3f} | {r['null_AUC']:.3f} |"
                f" {r['sensitivity']:.3f} ± {r['sensitivity_sem']:.3f} |"
                f" {r['specificity']:.3f} ± {r['specificity_sem']:.3f} |"
                f" {r['sens_spec_gap']:+.3f} ± {r['sens_spec_gap_sem']:.3f} |"
                f" {r['valid_max']:.3f} ({r['valid_max_epoch']:.0f}) |"
            )
        lines.append("")
    lines += ["## Графики", ""]
    lines += [f"- [{os.path.basename(f)}]({os.path.relpath(f, os.path.dirname(path))})"
              for f in figures]
    lines += [
        "",
        "## Чем посчитано",
        "",
        "- Конфигурация каждого прогона восстановлена из `models/<label>/groups_<family>/"
        "seed<N>.args.json`; веса — из соседнего `seed<N>.pt`, и это именно та модель, "
        "которую тестировал прогон (`--save_model`).",
        "- Скоринг — `analysis/checkpoint_scores.score_split`; метрики — "
        "`analysis/cross_sampler_eval.py`, где `within_protein_pair_auc` построчно "
        "повторяет `training/new_train.py:730-769`.",
        "- Соперники без обучения — `dataloader.chemistry_prior.null_scores` и "
        "`null_scores_within_protein` на train-кадре того же сплита, сходство — "
        "`analysis/null_model.resolve_similarity` (Morgan-фингерпринты).",
        "- SEM у `skill` — по ПАРНОЙ разности внутри (семья, сид): соперник и модель "
        "видят одни и те же строки, и общая дисперсия сплита в разности сокращается.",
        "- Ничего не обучалось, `metrics_summary.csv` не менялся.",
        "",
    ]
    with open(path, "w") as handle:
        handle.write("\n".join(lines))
    return path


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--labels", default=",".join(DEFAULT_LABELS))
    parser.add_argument("--families", help="default: every groups_* directory the label has")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--features", default=TANIMOTO,
                        help="feature space the no-training competitor measures similarity in")
    parser.add_argument("--out-csv", default=os.path.join(PROJECT_ROOT, "graphics",
                                                          "solo_family_runs.csv"))
    parser.add_argument("--report", default=os.path.join(PROJECT_ROOT, "files",
                                                         "solo_family_report.md"))
    parser.add_argument("--no-figures", action="store_true",
                        help="skip scripts/generate_config_graphics.sh and the per-label .md")
    args = parser.parse_args()

    labels = [x for x in args.labels.split(",") if x]
    seeds = [int(s) for s in args.seeds.split(",") if s]
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    similarity, index, entity_column, _, _ = resolve_similarity(
        csv, data_dir, args.features, None, False
    )
    del csv

    records = []
    for label in labels:
        families = ([x for x in args.families.split(",") if x] if args.families
                    else families_of(label))
        for family in families:
            for seed in seeds:
                record = score_one(label, family, seed, data_dir, similarity, index,
                                   entity_column)
                if record is None:
                    print(f"missing : {label}/groups_{family}/seed{seed}", flush=True)
                    continue
                records.append(record)
                print(f"{label[-28:]} | {family} seed{seed} : pairs "
                      f"{record['AUC_within_protein_pairs']:.3f} vs null "
                      f"{record['null_within_protein_pairs']:.3f}", flush=True)
    if not records:
        raise SystemExit("nothing scored")

    table = pd.DataFrame(records)
    summary = aggregate(table)
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    table.drop(columns=["valid_curve"]).to_csv(args.out_csv, index=False)
    print(f"wrote : {args.out_csv}")

    figures = []
    if not args.no_figures:
        figures = make_figures(labels)
        for label in labels:
            path = write_label_md(label, table, similarity, index, entity_column)
            print(f"wrote : {path}", flush=True)

    if args.report:
        os.makedirs(os.path.dirname(args.report), exist_ok=True)
        write_report(table, summary, args.report, figures, labels)
        print(f"wrote : {args.report}")

    pd.set_option("display.width", 220)
    shown = ["label", "family", "test_rows", "seen_in_train", "pairs", "null_pairs",
             "skill", "skill_sem"]
    print("\n" + summary[shown].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
