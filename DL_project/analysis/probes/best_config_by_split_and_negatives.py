"""Rank mlp / geometric_edge configurations separately for every (lipid split,
negative-sampling) regime, by held-out *test* balanced accuracy and test F1.

Why this exists
---------------
The lipid axis was run under two cuts -- `--lipid_species_coldsplit=0.15` ("s15")
and `--lipid_subclass` ("sub") -- and, inside each cut, under several ways of
drawing the negatives (plain random draw, `--dissimilar_negative_mining`,
`--hard_negative_mining`, each with a `--negative_similarity` flavour, plus the
historical `negatives_per_positive=5` default).  A different negative draw
changes the test rows themselves, so runs that differ in it are *not*
interchangeable: they are separate regimes, ranked separately.  This script
therefore

1. classifies every completed mlp / geometric_edge run into
   `(split, negative sampling)`;
2. ranks the labels inside each regime by mean test balanced accuracy and mean
   test F1, aggregated per excluded group first and then across groups, so a
   label that happens to have run more seeds on an easy group cannot win;
3. for label pairs whose recorded configuration is identical *except* the
   negative-sampling flags, reports the matched (group, seed) delta -- the only
   fair way to say whether a sampling variant helped.

Metric choice follows the project rule for the lipid axis: test balanced
accuracy against the 0.500 null, with sensitivity / specificity and their gap
beside it; test F1 as the second criterion.  Validation columns are not used.

Reads only.  No training, no writes to `results/tables/`.

Examples
--------
    python3 analysis/probes/best_config_by_split_and_negatives.py
    python3 analysis/probes/best_config_by_split_and_negatives.py --top 10
    python3 analysis/probes/best_config_by_split_and_negatives.py --regime sub
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_TABLE = Path("results/tables/metrics_summary.csv")

# Columns that define how negatives were drawn.  They are excluded from the
# configuration signature precisely because they are the dimension compared.
SAMPLING_COLS = [
    "hard_negative_mining",
    "hard_negative_share",
    "dissimilar_negative_mining",
    "dissimilar_negative_share",
    "negative_similarity",
    "negative_similarity_descriptors",
    "rotate_train_negatives",
    "rotate_negatives_per_epoch",
    "negatives_per_positive",
    "balance_negatives_by_family",
    "balance_excluded_group_negatives",
]

# Flags that only decide what is written to disk; they never change training,
# so two labels differing only in these are still the same configuration.
IO_COLS = [
    "save_checkpoint",
    "save_model",
    "save_dynamics",
    "save_model_in_dynamics",
    "num_workers",
]

# Everything after this column in the header is an outcome, not a setting.
FIRST_OUTCOME_COL = "training_duration_sec"

TEST_COLS = ["balanced_accuracy", "F1", "sensitivity", "specificity"]


def load(table: Path) -> pd.DataFrame:
    # pandas (never csv.DictReader) because the header carries two columns
    # named `label`; the second one is ModelConfig.label and is almost always
    # empty, and DictReader would silently keep that empty one.
    frame = pd.read_csv(table, low_memory=False)
    return frame.drop(columns=[c for c in frame.columns if c == "label.1"])


def family_of(label: str) -> str | None:
    if label.startswith("mlp_"):
        return "mlp"
    if label.startswith(("ge_", "geatt", "geometric_edge")):
        return "geometric_edge"
    return None


def split_of(row) -> str | None:
    if row["lipid_species_coldsplit"] == 0.15:
        return "s15"
    if isinstance(row["lipid_subclass"], str) and row["lipid_subclass"].strip():
        return "sub"
    return None


def sampling_of(row) -> str:
    """Name the negative draw.

    `negative_similarity` is only meaningful when a mining flag is on: the
    column records the code default (`tanimoto`) for every run made after the
    flag was introduced, including runs that mine nothing.
    """
    hard = row["hard_negative_mining"] == 1
    dissimilar = row["dissimilar_negative_mining"] == 1
    parts = []
    if hard:
        parts.append("hnm")
    if dissimilar:
        parts.append("dnm")
    if hard or dissimilar:
        flavour = row["negative_similarity"]
        parts.append(flavour if isinstance(flavour, str) and flavour.strip() else "tanimoto")
        share = row["hard_negative_share"] if hard else row["dissimilar_negative_share"]
        parts.append(f"share{share:g}")
    if row["rotate_train_negatives"] == 1:
        parts.append("rotneg")
    npp = row["negatives_per_positive"]
    if pd.notna(npp) and npp != 2:
        parts.append(f"npp{npp:g}")
    return "_".join(parts) if parts else "random"


ARG_FILES = Path("arg_files")

SAMPLING_FLAGS = {
    "--dissimilar_negative_mining",
    "--dissimilar_negative_share",
    "--hard_negative_mining",
    "--hard_negative_share",
    "--negative_similarity",
    "--negative_similarity_descriptors",
    "--rotate_train_negatives",
    "--negatives_per_positive",
}

IO_FLAGS = {
    "--save_model",
    "--save_model_in_dynamics",
    "--save_checkpoint",
    "--save_dynamics",
    "--num_workers",
}


def arg_flags(label: str) -> set[str] | None:
    """The flag set of a label's configuration file, or None if it is gone.

    Configuration identity is read from `arg_files/` instead of from the
    table's own setting columns: a flag introduced after a run was made is
    empty in that run's row and holds its default in later rows, and an unset
    flag (`protein_hiddim` falling back to `hiddim`) is empty as well, so table
    columns cannot tell "same configuration" from "different code version".
    """
    matches = list(ARG_FILES.glob(f"*/{label}.md")) + list(ARG_FILES.glob(f"{label}.md"))
    if not matches:
        return None
    flags = set()
    for line in matches[0].read_text().splitlines():
        line = line.strip()
        if not line.startswith("--"):
            continue
        for token in line.split():
            if token.startswith("--"):
                flags.add(token)
    return flags


def cells(frame: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per (label, excluded group, seed).

    A few labels were run twice for the same seed; averaging the repeats keeps
    them from counting twice in the group mean.
    """
    return (
        frame.groupby(["label", "exclusion_set", "seed"], as_index=False)[TEST_COLS]
        .mean()
    )


def reference_groups(cell_frame: pd.DataFrame) -> list[str]:
    """Excluded groups that most labels of the regime actually ran.

    Ranking on a label's own groups would reward whoever skipped the hard ones.
    """
    per_group = cell_frame.groupby("exclusion_set")["label"].nunique()
    labels = cell_frame["label"].nunique()
    return sorted(per_group[per_group >= 0.5 * labels].index)


def summarize(cell_frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    kept = cell_frame[cell_frame["exclusion_set"].isin(groups)]
    by_group = kept.groupby(["label", "exclusion_set"])[TEST_COLS].mean().reset_index()
    rows = []
    for label, part in by_group.groupby("label"):
        seeds = kept[kept["label"] == label]
        rows.append(
            {
                "label": label,
                "groups": part["exclusion_set"].nunique(),
                "runs": len(seeds),
                "test_BA": part["balanced_accuracy"].mean(),
                "BA_group_std": part["balanced_accuracy"].std(ddof=0),
                "BA_worst_group": part["balanced_accuracy"].min(),
                "BA_run_std": seeds["balanced_accuracy"].std(ddof=0),
                "BA_worst_run": seeds["balanced_accuracy"].min(),
                "test_F1": part["F1"].mean(),
                "F1_worst_group": part["F1"].min(),
                "sens": part["sensitivity"].mean(),
                "spec": part["specificity"].mean(),
                "recall_gap": (part["sensitivity"] - part["specificity"]).abs().mean(),
            }
        )
    return pd.DataFrame(rows)


def matched_pairs(cell_frame: pd.DataFrame, labels: list[str], sampling: dict[str, str], npp: dict[str, float]) -> tuple[list[dict], list[str]]:
    """Deltas between labels whose configuration files differ only in the draw."""
    flags = {label: arg_flags(label) for label in labels}
    missing = sorted(label for label, value in flags.items() if value is None)
    out = []
    known = [label for label in sorted(labels) if flags[label] is not None]
    for i, left_label in enumerate(known):
        for right_label in known[i + 1:]:
            difference = flags[left_label] ^ flags[right_label]
            names = {token.split("=", 1)[0] for token in difference} - IO_FLAGS
            if names - SAMPLING_FLAGS:
                continue
            difference = {t for t in difference if t.split("=", 1)[0] not in IO_FLAGS}
            same_draw = sampling[left_label] == sampling[right_label]
            if not difference and (same_draw or npp[left_label] == npp[right_label]):
                continue
            baseline, variant = left_label, right_label
            if sampling[variant] == "random" and sampling[baseline] != "random":
                baseline, variant = variant, baseline
            left = cell_frame[cell_frame["label"] == baseline].set_index(["exclusion_set", "seed"])
            right = cell_frame[cell_frame["label"] == variant].set_index(["exclusion_set", "seed"])
            common = left.index.intersection(right.index)
            if common.empty:
                continue
            delta_ba = right.loc[common, "balanced_accuracy"] - left.loc[common, "balanced_accuracy"]
            delta_f1 = right.loc[common, "F1"] - left.loc[common, "F1"]
            out.append(
                {
                    "baseline": baseline,
                    "base_draw": sampling[baseline],
                    "variant": variant,
                    "var_draw": sampling[variant],
                    "pairs": len(common),
                    "groups": len({g for g, _ in common}),
                    "base_BA": left.loc[common, "balanced_accuracy"].mean(),
                    "var_BA": right.loc[common, "balanced_accuracy"].mean(),
                    "dBA": delta_ba.mean(),
                    "dBA_median": delta_ba.median(),
                    "BA_up": int((delta_ba > 0).sum()),
                    "base_F1": left.loc[common, "F1"].mean(),
                    "var_F1": right.loc[common, "F1"].mean(),
                    "dF1": delta_f1.mean(),
                    "F1_up": int((delta_f1 > 0).sum()),
                    "same_code_default": npp[baseline] == npp[variant],
                }
            )
    return out, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--top", type=int, default=6, help="rows shown per ranking")
    parser.add_argument("--regime", default=None, help="only this split (s15 / sub)")
    parser.add_argument("--min-groups", type=int, default=None, help="drop labels covering fewer reference groups")
    args = parser.parse_args()

    frame = load(args.table)
    frame = frame[frame["run_status"] == "complete"].copy()
    frame["family"] = frame["label"].fillna("").astype(str).map(family_of)
    frame = frame[frame["family"].notna()]
    frame["split"] = frame.apply(split_of, axis=1)
    frame = frame[frame["split"].notna()]
    if args.regime:
        frame = frame[frame["split"] == args.regime]
    frame["sampling"] = frame.apply(sampling_of, axis=1)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 95)

    print(f"table: {args.table}")
    print(f"complete mlp / geometric_edge rows on a lipid split: {len(frame)}")
    print("configuration identity read from arg_files/<family>/<label>.md")
    print()

    counts = frame.groupby(["split", "sampling", "family"])["label"].agg(["nunique", "size"])
    print("=== regimes (labels / rows) ===")
    print(counts.rename(columns={"nunique": "labels", "size": "rows"}).to_string())
    print()

    for (split, sampling, family), part in frame.groupby(["split", "sampling", "family"]):
        cell_frame = cells(part)
        groups = reference_groups(cell_frame)
        table = summarize(cell_frame, groups)
        if args.min_groups is not None:
            table = table[table["groups"] >= args.min_groups]
        if table.empty:
            continue
        full = table["groups"].max()
        print(f"=== split={split}  negatives={sampling}  family={family} ===")
        print(f"reference groups ({len(groups)}): {', '.join(groups)}")
        print(f"-- by test BA (labels with {full} reference group(s) first) --")
        ranked = table.sort_values(["groups", "test_BA"], ascending=[False, False])
        print(ranked.head(args.top).round(4).to_string(index=False))
        print("-- by test F1 --")
        print(table.sort_values(["groups", "test_F1"], ascending=[False, False]).head(args.top).round(4).to_string(index=False))
        print()

    # A handful of labels were run both before and after the code default for
    # negatives_per_positive changed from 5 to 2, so the same configuration
    # exists under two negative ratios -- the cleanest read of that flag.
    repeated = []
    for (split, label), part in frame.groupby(["split", "label"]):
        ratios = sorted(part["negatives_per_positive"].dropna().unique())
        if len(ratios) < 2:
            continue
        cell_frame = cells(part.assign(label=part["negatives_per_positive"].astype(str)))
        low = cell_frame[cell_frame["label"] == f"{ratios[0]:g}.0"].set_index(["exclusion_set", "seed"])
        high = cell_frame[cell_frame["label"] == f"{ratios[-1]:g}.0"].set_index(["exclusion_set", "seed"])
        common = low.index.intersection(high.index)
        if common.empty:
            continue
        repeated.append(
            {
                "split": split,
                "label": label,
                "pairs": len(common),
                f"BA_npp{ratios[0]:g}": low.loc[common, "balanced_accuracy"].mean(),
                f"BA_npp{ratios[-1]:g}": high.loc[common, "balanced_accuracy"].mean(),
                "dBA": (low.loc[common, "balanced_accuracy"] - high.loc[common, "balanced_accuracy"]).mean(),
                f"F1_npp{ratios[0]:g}": low.loc[common, "F1"].mean(),
                f"F1_npp{ratios[-1]:g}": high.loc[common, "F1"].mean(),
            }
        )
    print("=== same label under both negatives_per_positive defaults (dBA = npp2 minus npp5) ===")
    print(pd.DataFrame(repeated).round(4).to_string(index=False) if repeated else "none")
    print()

    for split, part in frame.groupby("split"):
        cell_frame = cells(part)
        sampling = part.groupby("label")["sampling"].agg(lambda s: s.mode().iloc[0]).to_dict()
        npp = part.groupby("label")["negatives_per_positive"].max().to_dict()
        pairs, missing = matched_pairs(cell_frame, sorted(sampling), sampling, npp)
        print(f"=== split={split}: matched negative-sampling comparisons (same configuration otherwise) ===")
        if not pairs:
            print("no label pair differs only in the negative draw")
        else:
            print(pd.DataFrame(pairs).round(4).to_string(index=False))
        if missing:
            print(f"no arg file (configuration unverifiable): {', '.join(missing)}")
        print()


if __name__ == "__main__":
    main()
