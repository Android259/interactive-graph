#!/usr/bin/env python3
"""How large and how ISOLATED every Titeca-et-al. lipid subclass block is, when that
subclass is the thing held out of training.

The question this answers is the one that has to be settled BEFORE a subclass cold
split is worth running: the collaborator's task definition ("classify binders and
non-binders by lipid subclass", the third column of the shared CSV -- the y axis of
the source paper's LTP x lipid-subclass matrix, Figure 3a of files/Reuter.pdf) names
23 subclasses, and they differ by two orders of magnitude in size. A block of 2
species with 3 positives is not a cold split, it is a coin flip; and a block whose
close chemical relative stays in training is not a COLD split either, however many
rows it has.

Three numbers per block, all read off artefacts that already exist -- nothing is
trained here, nothing is fitted:

  species / positives / proteins-with-a-positive
      the size of what leaves training, and how many protein blocks the project's
      primary lipid-coldsplit metric (AUC_within_protein, averaged OVER proteins --
      see files/lipid_coldsplit_architecture_direction.md section 7j) would actually
      be averaged over. A block with 2 such proteins cannot produce a readable number
      whatever the model does, which is exactly what happened to PI and PS+PGP in
      cron_test_metrics/cron_fig3_lipidgroups.txt.

  tanimoto_whole / tanimoto_headgroup
      training.pair_baseline_common.block_tanimoto_similarity and its head-group
      counterpart: mean best Tanimoto similarity of the held-out species to whatever
      chemistry stays in training. LOW = genuinely novel chemistry (a cold split),
      HIGH = a close relative stayed behind (a warm split wearing a cold split's
      name). The two are reported side by side because a subclass block is cut on the
      HEAD GROUP: its acyl tails are shared with everything else in the table by
      construction, so the whole-molecule number is optimistic for this axis and the
      head-group number is the one that says whether the head group itself is new.

`--by_family` adds the same size columns restricted to one protein family's own rows,
which is what a --family_only (deepclip) run would actually train and test on.

Reads only. Writes nothing unless --csv is given.

    python3 analysis/lipid_subclass_block_report.py
    python3 analysis/lipid_subclass_block_report.py --blocks fig3
    python3 analysis/lipid_subclass_block_report.py --by_family CRAL-TRIO
    python3 analysis/lipid_subclass_block_report.py --blocks fig3 --by_family all \
        --project_test_rows 2,5,all
    python3 analysis/lipid_subclass_block_report.py --csv files/subclass_blocks.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import training.pair_baseline_common as pbc  # noqa: E402

# The nine blocks cron_test_metrics/cron_fig3_lipidgroups.txt was actually run over --
# the singletons big enough to stand alone, plus three merges of subclasses too small
# to be their own block. Kept here as the one spelling, so the Kron-RLS run, the
# network's own --lipid_subclass grid (dataloader/lipid_subclass_blocks.py) and this
# report all name the same nine things the same way.
FIG3_BLOCKS = (
    "PC",
    "PG",
    "FA",
    "PE",
    "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM",
    "PI",
    "LPC+LPE+LPG",
    "PA",
    "PS+PGP+DAG+TAG",
)


def block_specs(table: pd.DataFrame, which: str) -> list[str]:
    """The list of `+`-joined subclass specs to report, in a stable order."""
    if which == "fig3":
        return list(FIG3_BLOCKS)
    lookup = pbc._article_subclass_lookup()
    counts = {
        name: int(table.loc[table["FullIdentityOfLipid"].isin(species), "Interaction"].sum())
        for name, species in lookup.items()
    }
    # Uppercase spelling is what the article and files/data_source.md use; the lookup
    # keys are lowercased for case-insensitive matching.
    canonical = {name.lower(): name for name in _article_names()}
    return [canonical[name] for name in sorted(counts, key=lambda n: (-counts[n], n))]


def _article_names() -> list[str]:
    import json

    path = PROJECT_ROOT / "data" / "lipid_article_classification.json"
    return sorted(set(json.loads(path.read_text()).values()))


def describe(table: pd.DataFrame, spec: str, cache: dict, family: str | None) -> dict:
    species = pbc.resolve_excluded_lipids(table, spec.split("+"))
    rows = table["FullIdentityOfLipid"].isin(species)
    scope = table
    if family:
        scope = table[table["ProteinDomain"].str.lower() == family.lower()]
        rows = rows & table.index.isin(scope.index)
    block = table[rows]
    positives = block[block["Interaction"] == 1]
    return {
        "block": spec,
        "species": len(species),
        "rows": len(block),
        "positives": len(positives),
        "negatives": len(block) - len(positives),
        "proteins_with_positive": positives["LTPProtein"].nunique(),
        # Isolation is a property of the CHEMISTRY, not of one family's rows: the
        # species set is the same whichever family is being looked at, so these two
        # columns do not change under --by_family and are computed on the full table.
        "tanimoto_whole": pbc.block_tanimoto_similarity(table, species, cache),
        "tanimoto_headgroup": pbc.block_tanimoto_headgroup_similarity(table, species, cache),
    }


def _sampled_block(rows: pd.DataFrame, per_positive: int, seed: int) -> pd.DataFrame:
    """The block as the loader's per-protein negative sampler would leave it.

    --balanced_proteins draws `per_positive` negatives per positive INSIDE each protein
    (dataloader/sampler.py), so which of the colliding species actually reach the
    evaluated pool depends on that ratio -- which is exactly why the ceiling below moves
    with it.
    """
    kept = []
    for _, group in rows.groupby("LTPProtein"):
        positive = group[group["Interaction"] == 1]
        if positive.empty:
            continue
        negative = group[group["Interaction"] == 0]
        take = min(per_positive * len(positive), len(negative))
        kept.append(positive)
        if take:
            kept.append(negative.sample(n=take, random_state=seed))
    return pd.concat(kept) if kept else rows.iloc[:0]


def lipid_only_ceiling(
    table: pd.DataFrame,
    species,
    family: str | None,
    per_positive: int | None = None,
    seeds: tuple[int, ...] = (0, 1, 2, 3, 4),
) -> tuple[float, int]:
    """(best AUC a LIPID-ONLY scorer can reach inside the block, species both-labelled).

    DeepCLIP reads the lipid and nothing else (--family_only, one branch, one lipid on
    the input), so inside a held-out block its score is a function of the lipid species
    alone. Whenever one species is a positive with one protein of the family and a
    negative with another, no such function can be right on both rows -- and a subclass
    block is exactly where that collides most, because every species in it shares a
    head group and the model has no protein to tell them apart by.

    The ceiling is computed by giving the model the best function it could possibly
    have: each species scored by its own positive RATE inside this block. The resulting
    AUC (ties counted as 0.5, the usual convention) is what a perfect lipid-only
    predictor would score -- not what a model will score, an upper bound on it. The
    second return value is how many species carry both labels, the reason the bound is
    below 1.0 at all.

    `per_positive=None` measures the whole block. An integer measures the pool the
    loader's K:1 per-protein draw would actually leave, averaged over `seeds` -- a
    smaller K hides collisions (the colliding species is simply not drawn as a
    negative), so the ceiling RISES as the negative ratio falls. That is the trade the
    "take more negatives" recommendation has to be read against: more rows, harder
    ceiling.
    """
    rows = table[table["FullIdentityOfLipid"].isin(species)]
    if family:
        rows = rows[rows["ProteinDomain"].str.lower() == family.lower()]
    if per_positive is not None:
        scored = [
            _ceiling_of(block)
            for block in (_sampled_block(rows, per_positive, seed) for seed in seeds)
            if not block.empty
        ]
        finite = [value for value, _ in scored if value == value]
        return (
            (sum(finite) / len(finite) if finite else float("nan")),
            scored[0][1] if scored else 0,
        )
    return _ceiling_of(rows)


def _ceiling_of(rows: pd.DataFrame) -> tuple[float, int]:
    """lipid_only_ceiling's arithmetic on an already-selected set of rows."""
    positive = rows["Interaction"].to_numpy() == 1
    if not positive.any() or positive.all():
        return float("nan"), 0
    rate = rows.groupby("FullIdentityOfLipid")["Interaction"].transform("mean").to_numpy()
    both = int(
        rows.groupby("FullIdentityOfLipid")["Interaction"].nunique().gt(1).sum()
    )
    pos_scores, neg_scores = rate[positive], rate[~positive]
    wins = (pos_scores[:, None] > neg_scores[None, :]).sum()
    ties = (pos_scores[:, None] == neg_scores[None, :]).sum()
    auc = (wins + 0.5 * ties) / (len(pos_scores) * len(neg_scores))
    return float(auc), both


def projected_test_rows(positives: int, negatives: int, per_positive: int | None) -> int:
    """How many rows the held-out block's TEST half would carry.

    The loader halves the block label by label (dataloader/Dataloader.py::
    _split_interactions -- positives and negatives are each sampled frac=0.5, so both
    halves carry the same positive rate by construction), and the negative sampler
    draws `per_positive` negatives per positive inside each balancing group, capped by
    how many the block actually has. `per_positive=None` means every negative in the
    block is kept -- the ceiling this axis can reach.

    Reported because it is the number that decides whether a (family, subclass) cell is
    worth running at all: files/deepclip_results_and_hard_negatives.md section 2
    measured 2-22 test rows on the --family_only arms with the DEFAULT sampler, and
    per-cell BA scatter of 0.10-0.22 at that size.
    """
    kept = negatives if per_positive is None else min(per_positive * positives, negatives)
    return (positives + kept) // 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--blocks", choices=("fig3", "subclasses"), default="subclasses",
        help="fig3 = the nine blocks the Kron-RLS run used; subclasses = all 23 "
             "article subclasses on their own (default)",
    )
    parser.add_argument(
        "--by_family", default=None,
        help="restrict the size columns to one ProteinDomain's own rows (what a "
             "--family_only run trains and tests on); 'all' reports every family in "
             "turn, reusing one Tanimoto build",
    )
    parser.add_argument(
        "--project_test_rows", default="", metavar="K[,K...]",
        help="add a projected test-block size per negatives-per-positive setting; "
             "'all' keeps every negative in the block (e.g. --project_test_rows 2,5,all)",
    )
    parser.add_argument(
        "--lipid_only_ceiling", default="", metavar="K[,K...]",
        help="add the best AUC a lipid-only model (deepclip) could reach inside each "
             "block, and how many species carry both labels there. 'all' measures the "
             "whole block, an integer K the per-protein K:1 draw the loader would make "
             "(mean over seeds 0-4), e.g. --lipid_only_ceiling 2,5,all",
    )
    parser.add_argument("--csv", type=Path, default=None, help="also write the table here")
    args = parser.parse_args()

    table = pbc.read_interactions()
    cache: dict = {}
    specs = block_specs(table, args.blocks)
    if args.by_family == "all":
        families = sorted(table["ProteinDomain"].unique())
    else:
        families = [args.by_family]
    frames = []
    for family in families:
        frame = pd.DataFrame([describe(table, spec, cache, family) for spec in specs])
        if family:
            frame.insert(0, "family", family)
        frames.append(frame)
    frame = pd.concat(frames, ignore_index=True)
    for token in (t.strip() for t in args.lipid_only_ceiling.split(",") if t.strip()):
        per_positive = None if token.lower() == "all" else int(token)
        ceiling, both = [], []
        for row in frame.itertuples():
            species = pbc.resolve_excluded_lipids(table, row.block.split("+"))
            value, collisions = lipid_only_ceiling(
                table, species, getattr(row, "family", None), per_positive
            )
            ceiling.append(value)
            both.append(collisions)
        frame[f"lipid_only_auc_max_npp{token}"] = ceiling
        frame[f"species_both_labels_npp{token}"] = both
    for token in (t.strip() for t in args.project_test_rows.split(",") if t.strip()):
        per_positive = None if token.lower() == "all" else int(token)
        frame[f"test_rows_npp{token}"] = [
            projected_test_rows(int(row.positives), int(row.negatives), per_positive)
            for row in frame.itertuples()
        ]
    scope = f" within {args.by_family}" if args.by_family else ""
    print(f"lipid subclass blocks ({args.blocks}){scope} -- {len(table)} rows, "
          f"{int(table['Interaction'].sum())} positives in the whole table")
    print(frame.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    if args.csv:
        frame.to_csv(args.csv, index=False)
        print(f"\nwritten to {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
