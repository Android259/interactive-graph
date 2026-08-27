#!/usr/bin/env python3
"""The chemistry-only null model for the doubly-cold block, and the network beside it.

The question this answers. `--double_coldsplit` leaves the held-out block with no lipid
that training ever saw, so the per-lipid label prior that used to carry the one-axis
split scores 0.500 by construction. That closes the *lookup* leak but not the weaker
one underneath it: a lipid the model has never seen can still resemble one it has, and
"resembles a training positive" is a prediction that needs no protein at all. Everything
the project is built to measure -- pocket, attention, pair -- lives above that line, so
the line has to be drawn before any number above it means anything.

The null model. For a row (protein p, lipid l) it ignores p entirely and scores l by the
similarity-weighted train positive rate of its k nearest training lipids, nearest by
Morgan-fingerprint Tanimoto (`data/Tanimoto_compact_isomeric_*`, the same artifacts the
loader's `--tanimoto_weight` uses). Held-out classes have no training rows whatsoever, so
every neighbour is necessarily from a different class -- this is extrapolation across
chemistry, not the class lookup the split already closed.

Reported as AUC, not balanced accuracy. At a fixed 0.5 threshold the null model scores
BA 0.512 while ranking the block at AUC 0.589: nearly all of its measured weakness is
threshold placement, and a comparison against a network at the same fixed threshold
would credit the network for a decision boundary rather than for information. AUC
compares what each one knows.

    python3 analysis/null_model.py
    python3 analysis/null_model.py --scores /tmp/scores_small27k.csv --epoch 120

With `--scores` (the CSV `analysis/checkpoint_scores.py` writes) the network's AUC is
computed on exactly the rows it was evaluated on, matched by `pair_id`, and the null
model is restricted to those same rows -- so the two numbers are the same measurement of
the same block and the difference between them is the network's own contribution.

Reads only. Trains nothing, appends to no shared table.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas

from dataloader.chemistry_prior import (  # noqa: E402
    LIPID_DESCRIPTOR_NAMES, PAIR_DESCRIPTOR_NAMES, feature_similarity, null_scores,
    species_similarity,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from lipid_marginal_baseline import split as split_func  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    lipid_class_series,
    lipid_classes_for_holdout,
    split_and_sample_protein_balanced_interactions,
)

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
# The three families whose validation sits above 0.5 in every dcs run, from
# files/signal_state.md section 4.1. Named here so the summary can report them apart:
# averaging across all seven hides both halves of the split.
WORKING = ("LBP_BPI_CETP", "scp2", "IP_trans")

# Reserved --features value: the original whole-molecule Morgan-fingerprint null
# model (species_similarity) rather than a named scalar descriptor set --
# feature_similarity has no entry for "the whole structure", only named columns.
TANIMOTO = "tanimoto"

# Persisted null-model-only results (never the network's own AUC, which depends on
# that label's own checkpoints and must always be scored fresh): one process building
# graphics/<labelA>/<labelA>.md and graphics/<labelB>/<labelB>.md back to back (the
# common case -- scripts/lib/generate_label_report.sh runs full_label_report.py once
# per label) recomputes the IDENTICAL null model for every label that shares a
# --features set and a --coldsplit_share/--negatives_per_positive, which is most of
# them. Keyed by (label, family, seed, neighbour_counts, share, ratio, split, a cheap
# csv fingerprint) so a rebuilt interaction table (project memory
# [[table-rebuilt-2026-08-24]]) naturally misses instead of silently returning stale
# numbers -- see _cache_key.
CACHE_PATH = os.path.join(PROJECT_ROOT, "analysis", ".null_model_cache.json")


def _csv_fingerprint(csv):
    return f"{len(csv)}:{int(csv['Interaction'].sum())}"


def load_null_model_cache(path=CACHE_PATH):
    if os.path.isfile(path):
        with open(path) as handle:
            return json.load(handle)
    return {}


def save_null_model_cache(cache, path=CACHE_PATH):
    """Atomic write (tmp + rename): a cache that only ever grows one entry at a time
    should not lose everything already computed to a crash or an interrupted run --
    exactly the failure mode this project has hit repeatedly with long cluster jobs.
    """
    # No sort_keys: json.load/json.dump both preserve dict insertion order, and a
    # cache-hit record's column order (which print_null_model_report's caller sees)
    # should match a cache-miss one's -- sorting here would silently permute it.
    tmp = f"{path}.tmp"
    with open(tmp, "w") as handle:
        json.dump(cache, handle, indent=2)
    os.replace(tmp, path)


def _cache_key(label, family, seed, neighbour_counts, share, ratio, split, csv_fingerprint):
    return "|".join(str(part) for part in (
        label, family, seed, ",".join(str(k) for k in sorted(neighbour_counts)),
        share, ratio, split, csv_fingerprint,
    ))


def resolve_similarity(csv, data_dir, features, label=None, zscore=False):
    """--features (comma-separated descriptor names, or the literal "tanimoto") ->
    (similarity, index, entity_column, label, feature_list).

    `features` a single string, either TANIMOTO or a comma list drawing on
    dataloader.chemistry_prior.LIPID_DESCRIPTOR_NAMES /
    dataloader.protein_graph_builder.POCKET_DESCRIPTOR_NAMES / PAIR_DESCRIPTOR_NAMES
    in any combination -- feature_similarity resolves the mix and decides the null
    model's granularity (per lipid species, per protein, or per protein-lipid row).

    `label`: short name for this descriptor set, used both as the cache namespace and
    as the printed identifier -- defaults to `features` itself (already short for one
    or two names; --label is for when the list is long and a run label reads better
    than a wall of comma-separated names).

    `zscore`: see dataloader.chemistry_prior.feature_similarity. A "zscore" marker is
    appended to the returned `feature_list` (and, when `label` was not given, to the
    auto-generated one) purely so null_model_table's cache treats a zscored and a
    non-zscored run of the same --features as different entries -- without it, two
    runs sharing an auto-generated label but differing only in --zscore would
    silently collide in the cache and one would read the other's numbers.
    """
    if features == TANIMOTO:
        similarity, index = species_similarity(csv, data_dir)
        entity_column = "FullIdentityOfLipid"
        feature_list = [TANIMOTO]
    else:
        feature_list = sorted(name for name in features.split(",") if name)
        similarity, index, entity_column = feature_similarity(
            csv, data_dir, feature_list, zscore=zscore
        )
    resolved_label = label or (features + (" +zscore" if zscore else ""))
    if zscore:
        feature_list = feature_list + ["zscore"]
    return similarity, index, entity_column, resolved_label, feature_list


def working_set(csv, seed, ratio, lipid_classes):
    """The loader's `csvt`, carrying the loader's `pair_id`.

    `lipid_marginal_baseline.working_set` builds the same rows in the same order but
    renumbers them 0..N-1 and keeps no trace of where they came from, and `pair_id` --
    the original row of the interaction table -- is assigned by
    `New_dataloader.__init__` *before* that renumbering. Matching rows against the
    scores `analysis/checkpoint_scores.py` writes needs that id, so the two lines are
    reproduced here rather than in the baseline, whose own numbers do not use it.
    """
    held = {name.lower() for name in lipid_classes}
    strata = lipid_class_series(csv).str.lower().isin(held) if held else None
    positives, negatives = split_and_sample_protein_balanced_interactions(
        csv, seed, ratio, strata
    )
    positives = positives.copy()
    negatives = negatives.copy()
    positives["pair_id"] = positives.index
    negatives["pair_id"] = negatives.index
    both = pandas.concat([positives, negatives])
    return both.set_index(pandas.Index(list(range(len(both)))))


def auc(truth, score):
    """Rank-based AUC; nan when the block is single-class."""
    truth = np.asarray(truth)
    score = np.asarray(score, dtype=float)
    positives = truth.sum()
    negatives = len(truth) - positives
    if positives == 0 or negatives == 0:
        return float("nan")
    ranks = pandas.Series(score).rank().to_numpy()
    return float((ranks[truth == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def per_protein_auc(held, score, minimum_rows=6):
    """AUC computed inside each protein separately, then averaged over proteins.

    The pooled AUC of a held-out block can be inflated by a confound that has nothing
    to do with any row's own label: some proteins in the block simply have an easier
    candidate pool than others (a higher base positive rate, or candidates that
    happen to score more separably), so ranking correctly ordered PROTEINS -- not
    rows -- already buys AUC before the model has told any one protein's own
    positives from its own negatives.

    Ranking a protein's own candidate lipids against each other, rather than the
    whole pooled block, removes exactly that: comparisons never cross a protein
    boundary, so "which protein is this" cannot contribute. It does NOT remove a
    lipid's own marginal (a lipid that is broadly positive across many proteins in
    train still carries that into its score here) -- only the cross-protein
    heterogeneity that pooled AUC could otherwise exploit for free. See
    per_lipid_auc for the symmetric case (protein-only/combined feature sets, where
    THIS function is the degenerate one -- see print_null_model_report).

    Proteins with fewer than `minimum_rows` rows, or with only one class present,
    carry no usable ranking and are skipped -- reported, so a mean over three
    proteins is not mistaken for a mean over thirty.
    """
    values = []
    frame = held.assign(_score=np.asarray(score, dtype=float))
    for _, group in frame.groupby("LTPProtein"):
        if len(group) < minimum_rows or group["Interaction"].nunique() < 2:
            continue
        value = auc(group["Interaction"].to_numpy(), group["_score"].to_numpy())
        if value == value:
            values.append(value)
    return (float(np.mean(values)) if values else float("nan")), len(values)


def per_lipid_auc(held, score, minimum_rows=6, group_column="lipid_class"):
    """AUC computed inside each lipid group separately, then averaged over groups --
    the mirror image of per_protein_auc, for a score built from protein-only (or
    combined) descriptors instead of lipid-only ones.

    Symmetric confound, symmetric fix: pooled AUC over a protein-only score can be
    inflated by cross-LIPID heterogeneity (some lipids in the block were screened
    against a candidate-protein pool that just happens to be easier to separate),
    independent of whether the score actually distinguishes this lipid's true binder
    from its other candidates. Ranking within one lipid's own candidate proteins
    removes that -- comparisons never cross a lipid-group boundary. It does NOT
    remove a PROTEIN's own marginal (a generically permissive pocket that scores well
    against many lipids in train still carries that score into every group's own
    ranking) -- only the cross-lipid heterogeneity pooled AUC could otherwise exploit.

    `group_column="lipid_class"` (dataloader.lipid_classes.lipid_class_series's
    head-group class, e.g. "Phosphatidylglycerol" -- null_model_table attaches this
    column before calling), not `FullIdentityOfLipid` (exact species): a held-out
    block's candidate-PROTEIN axis is small by construction (2-5 proteins per
    excluded family), so a single species is essentially never tested against
    `minimum_rows` of them -- measured directly on scp2/seed0, 37 of 44 species
    appeared exactly once and none reached even 3, so per-species grouping is
    structurally unusable, not merely uninformative, on this dataset's split shape.
    Per-class groups pool species sharing a head group (the level a binding
    preference actually lives at, per lipid_class_series's own docstring) instead,
    which reaches minimum_rows in practice -- at a real cost: it also re-admits some
    of the cross-SPECIES heterogeneity per_lipid_auc exists to remove, just bounded to
    within one class rather than across all of them. Pass group_column=
    "FullIdentityOfLipid" for the pure (but usually all-NaN) per-species version.

    Degenerate (always exactly 0.5) when `score` depends on the lipid alone, for the
    same reason per_protein_auc is degenerate when `score` depends on the protein
    alone: every row of one lipid then shares the identical score, so the ranking is
    an unbroken tie. See print_null_model_report's entity_column check.
    """
    values = []
    frame = held.assign(_score=np.asarray(score, dtype=float))
    for _, group in frame.groupby(group_column):
        if len(group) < minimum_rows or group["Interaction"].nunique() < 2:
            continue
        value = auc(group["Interaction"].to_numpy(), group["_score"].to_numpy())
        if value == value:
            values.append(value)
    return (float(np.mean(values)) if values else float("nan")), len(values)


def per_pair_auc(held, score, group_column="lipid_class"):
    """Pooled AUC after removing BOTH the protein axis' and the lipid axis' own mean
    score in one shot -- a two-way fixed-effects residual (row effect + column
    effect subtracted, only the interaction left), not two separate single-axis
    checks.

    per_protein_auc and per_lipid_auc each remove only their OWN axis' confound: a
    combined/pair score (feature_similarity's "pair" granularity, entity_column ==
    "pair_id") can be inflated by EITHER source independently, and neither function
    guards against the other -- per_protein_auc's within-protein groups can still
    carry a lipid-level score-shift, and per_lipid_auc's within-class groups can
    still carry a protein-level one. This removes both from every row at once:

        residual(p, l) = score(p, l) - mean(score | protein=p) - mean(score | lipid
                          group=l) + mean(score | whole block)

    then a single POOLED auc() on the residuals -- no per-group averaging afterwards,
    unlike per_protein_auc/per_lipid_auc, because the two-way subtraction already
    happened per row; there is no further "which group" left to rank within.

    `group_column="lipid_class"`, not `FullIdentityOfLipid`, for the same reason
    per_lipid_auc uses it: a species' own mean over 1-2 rows in a held block would
    just cancel that row's own score outright (residual = -protein mean + overall
    mean, no lipid information left at all), the worst case of the sparsity
    per_lipid_auc's docstring measures directly. A lipid class's larger row count
    gives a genuine (if class-level, not species-level) mean to subtract instead.

    Only meaningful for a score that varies on BOTH axes (pair/combined features):
    for a lipid-only or protein-only score, subtracting the OTHER axis' mean removes
    real signal, not just confound, since that score has no genuine variation on the
    axis being subtracted in the first place. print_null_model_report accordingly
    only surfaces this for entity_column == "pair_id".
    """
    frame = held.assign(_score=np.asarray(score, dtype=float))
    if group_column not in frame.columns:
        frame = frame.assign(**{group_column: lipid_class_series(frame)})
    protein_mean = frame.groupby("LTPProtein")["_score"].transform("mean")
    lipid_mean = frame.groupby(group_column)["_score"].transform("mean")
    residual = frame["_score"] - protein_mean - lipid_mean + frame["_score"].mean()
    return auc(frame["Interaction"].to_numpy(), residual.to_numpy())


def proximity_to_train_positives(train, held, similarity, index,
                                  entity_column="FullIdentityOfLipid"):
    """How close the block's positives sit to the nearest positive left in training.

    Mean over the block's positive rows of the highest similarity to any entity that
    is positive somewhere in train (entity = whatever `entity_column` names -- lipid
    species by default, but a protein or a protein-lipid row under a null model built
    from protein or combined/pair descriptors, see feature_similarity). This is the
    input the null model runs on, and for the default lipid-species case it is also
    what predicts a run's sensitivity: below ~0.77 the model calls nothing positive on
    that family, above ~0.82 it calls roughly half. See section 7 of
    files/marginals_and_cold_split.md.
    """
    positives = train[train["Interaction"] == 1][entity_column].unique()
    if len(positives) == 0:
        return float("nan")
    positive_positions = np.array([index[name] for name in positives])
    held_positives = held[held["Interaction"] == 1][entity_column]
    if held_positives.empty:
        return float("nan")
    per_entity = {
        name: float(similarity[index[name], positive_positions].max())
        for name in held_positives.unique()
    }
    return float(held_positives.map(per_entity).mean())


def null_model_table(csv, similarity, index, families, seeds, neighbour_counts,
                      share=0.7, ratio=2, split="valid", network=None, epoch=None,
                      entity_column="FullIdentityOfLipid", label=None, features=None,
                      cache_path=CACHE_PATH):
    """One row per (family, seed): null-model AUC(s) and, if `network` is given, its AUC.

    `network` is the RAW (unfiltered) scores DataFrame from
    analysis/checkpoint_scores.py; filtered here by `epoch`/`split` rather than by the
    caller, so a caller holding scores for several epochs can call this once per epoch
    without re-reading anything. Pass network=None for the null model alone.

    `entity_column`: which column of `held`/`train` identifies one null-model entity
    (FullIdentityOfLipid / LTPProtein / pair_id) -- must match what `similarity`/
    `index` are keyed by (see feature_similarity/resolve_similarity).

    `label`/`features`: when `label` is given, the null-model-only columns (not
    net_AUC/net_AUC_prot, which depend on `network` and are always recomputed) are
    read from and written to a persistent on-disk cache at `cache_path`, keyed by
    (label, family, seed, neighbour_counts, share, ratio, split, a csv fingerprint) --
    see CACHE_PATH. `features` (the resolved descriptor-name list `label` stands for)
    is stored alongside each cache entry and checked against the current call's, so a
    label re-used for a different descriptor set misses rather than returning the old
    set's numbers under the new name. `label=None` (the default) disables caching.

    Returns the `table` main() used to print -- factored out so
    analysis/full_label_report.py can build it without a CSV round-trip through
    --scores.
    """
    if network is not None:
        network = network[(network["epoch"] == epoch) & (network["split"] == split)]

    cache = load_null_model_cache(cache_path) if label is not None else None
    csv_fingerprint = _csv_fingerprint(csv)
    feature_list = sorted(features) if features is not None else None

    rows = []
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, ratio, held_classes)
            train, valid, test = split_func(csvt, family, seed, held_classes, double=True)
            held = valid if split == "valid" else test
            # per_lipid_auc's default grouping -- attached once here so both the
            # null-model call below and the network call further down see it.
            held = held.assign(lipid_class=lipid_class_series(held))

            cache_key = None
            cached_entry = None
            if cache is not None:
                cache_key = _cache_key(
                    label, family, seed, neighbour_counts, share, ratio, split,
                    csv_fingerprint,
                )
                cached_entry = cache.get(cache_key)
                if cached_entry is not None and cached_entry.get("features") != feature_list:
                    cached_entry = None  # same label, different descriptor set: miss

            if cached_entry is not None:
                record = dict(cached_entry["record"])
            else:
                record = {
                    "fam": family,
                    "seed": seed,
                    "rows": len(held),
                    "pos": int(held["Interaction"].sum()),
                    "sim_to_train_pos": proximity_to_train_positives(
                        train, held, similarity, index, entity_column
                    ),
                }
                for neighbours in neighbour_counts:
                    scores = null_scores(
                        train, held[entity_column], similarity, index, neighbours,
                        entity_column,
                    )
                    record[f"null_AUC_k{neighbours}"] = auc(
                        held["Interaction"].to_numpy(), scores
                    )
                    # Both computed unconditionally, regardless of entity_column --
                    # cheap either way, and which one is degenerate (always exactly
                    # 0.5, see per_protein_auc/per_lipid_auc) depends on
                    # entity_column, so print_null_model_report decides which to
                    # show rather than this function guessing on its behalf.
                    null_auc_prot, null_proteins = per_protein_auc(held, scores)
                    record[f"null_AUC_prot_k{neighbours}"] = null_auc_prot
                    null_auc_lipid, null_lipids = per_lipid_auc(held, scores)
                    record[f"null_AUC_lipid_k{neighbours}"] = null_auc_lipid
                    record[f"null_AUC_pair_k{neighbours}"] = per_pair_auc(held, scores)
                    # The protein-/lipid-block count depends only on `held`'s
                    # grouping (>= minimum_rows, both classes present), not on which
                    # scores ranked it, so it is identical whichever call produces
                    # it -- set once, from whichever ran first.
                    record.setdefault("proteins", null_proteins)
                    record.setdefault("lipids", null_lipids)
                if cache is not None:
                    cache[cache_key] = {"label": label, "features": feature_list, "record": record}
                    save_null_model_cache(cache, cache_path)

            if network is not None:
                mine = network[(network["fam"] == family) & (network["seed"] == seed)]
                # The loader renumbers csvt 0..N-1 before splitting, and both sides of
                # this comparison carry that number, so equal pair_id sets mean the two
                # reproductions of the split agree row for row.
                if set(mine["pair_id"]) != set(held["pair_id"]):
                    raise SystemExit(
                        f"{family}/seed{seed}: split reproduced here does not match the scored rows"
                    )
                held = held.merge(
                    mine[["pair_id", "prob"]], on="pair_id", how="left", validate="one_to_one"
                )
                record = dict(record)
                record["net_AUC"] = auc(held["Interaction"].to_numpy(), held["prob"].to_numpy())
                # Unlike null_AUC_prot/null_AUC_lipid, neither of these is ever
                # mechanically degenerate: the network sees both protein and lipid
                # information regardless of what the null model's own --features
                # granularity is, so both stay meaningful and print_null_model_report
                # shows both unconditionally.
                record["net_AUC_prot"], _ = per_protein_auc(held, held["prob"].to_numpy())
                record["net_AUC_lipid"], _ = per_lipid_auc(held, held["prob"].to_numpy())
                record["net_AUC_pair"] = per_pair_auc(held, held["prob"].to_numpy())

            rows.append(record)

    return pandas.DataFrame(rows)


def _group_stats(groups, columns):
    """One column per (group label, stat) -- every group's mean first, then every
    group's median, then two std's, each stat's block to the right of the previous
    one rather than interleaved per group: the mean is what every existing reader of
    these tables already reads first; median next to it is the check for "is this
    mean actually representative or is one split dragging it around" (a lone
    high/low seed moves a mean a lot more than it moves a median).

    The two std's are a variance DECOMPOSITION, not one pooled number, because
    `table`'s rows mix two very different sources of spread that a single std over
    all of them conflates: seed-to-seed noise WITHIN one excluded family, and
    family-to-family differences in the underlying chemistry (the whole reason
    files/signal_state.md 6.4 says never average over all seven at once). Pooling
    both into one std answers neither "how noisy is one family's own estimate"
    nor "how much do families genuinely differ" -- it answers a mixture of both,
    same as the "mean over all seven" mistake this file's own aggregation already
    avoids for the mean.

        (std seeds)    : mean, over the group's families, of that family's OWN std
                          across its seeds -- average within-family noise.
        (std families)  : std, across the group's families, of that family's OWN
                          mean-over-seeds -- between-family spread, seed noise
                          already averaged out of each family before this std runs.
    """
    frame = pandas.DataFrame({label: group[columns].mean() for label, group in groups.items()})
    for label, group in groups.items():
        frame[f"{label} (median)"] = group[columns].median()
    for label, group in groups.items():
        by_family = group.groupby("fam")[columns]
        frame[f"{label} (std seeds)"] = by_family.std().mean()
        frame[f"{label} (std families)"] = by_family.mean().std()
    return frame


def print_null_model_report(table, split, epoch, entity_column="FullIdentityOfLipid"):
    """The printout main() used to produce, given a table from null_model_table --
    mean over seeds, the never-pooled-over-all-seven AUC means, and the within-entity
    rankings. The raw per-(family, seed) rows `table` itself holds are NOT printed
    here (still fully present in `table` for a caller, and in the on-disk cache when
    null_model_table was given a `label` -- see CACHE_PATH): with 5+ families x
    several seeds x several k, the raw rows are mostly noise next to the summaries
    below, which is what every reader has actually wanted so far.

    Two within-entity rankings exist -- null_AUC_prot_k*/net_AUC_prot (per_protein_auc,
    ranks a protein's own candidate lipids against each other) and
    null_AUC_lipid_k*/net_AUC_lipid (per_lipid_auc, the mirror image, ranks a lipid's
    own candidate proteins) -- and one of the null-model pair can be MECHANICALLY
    degenerate (always exactly 0.5, not "no signal") depending on `entity_column`
    (feature_similarity's granularity, see dataloader.chemistry_prior):
      entity_column == "LTPProtein"        (protein-only features): null_AUC_prot_k*
                                            degenerate -- every row of one protein
                                            then shares an identical (protein-only)
                                            score, an unbroken tie.
      entity_column == "FullIdentityOfLipid" (lipid-only features, the original null
                                            model): null_AUC_lipid_k* degenerate, by
                                            the mirror argument.
      entity_column == "pair_id"           (combined/pair features): neither is
                                            degenerate -- both print.
    The network's own net_AUC_prot/net_AUC_lipid (when `network` was given to
    null_model_table) are NEVER degenerate this way -- the network sees both protein
    and lipid information regardless of the null model's own --features -- so they
    print unconditionally whenever present, even for a family/entity_column whose
    null_AUC_*_k* sibling is hidden as degenerate.
    """
    pandas.set_option("display.width", 200)
    # For combined/pair features (entity_column == "pair_id"), per_pair_auc (one
    # joint, two-way-demeaned diagnostic that controls BOTH axes in the same
    # measurement) replaces printing per_protein_auc/per_lipid_auc separately here:
    # each of those two only guards against its OWN axis' confound, so printing them
    # side by side invites reading "both look fine" as "no confound", which is not
    # what either one (or the pair of them) actually establishes -- per_pair_auc is
    # the number that does. The single-axis columns are NOT dropped from `table` --
    # still fully there, and in the on-disk cache when null_model_table was given a
    # `label` -- only hidden from this printout for this one granularity.
    is_pair = entity_column == "pair_id"
    prot_meaningful = entity_column != "LTPProtein"
    lipid_meaningful = entity_column != "FullIdentityOfLipid"
    has_net_prot = "net_AUC_prot" in table.columns
    has_net_lipid = "net_AUC_lipid" in table.columns
    show_prot_group = (prot_meaningful or has_net_prot) and not is_pair
    show_lipid_group = (lipid_meaningful or has_net_lipid) and not is_pair
    show_pair_group = is_pair

    def group_cols(*prefixes):
        return [c for c in table.columns if c.startswith(prefixes)]

    prot_group_all = group_cols("null_AUC_prot", "net_AUC_prot")
    lipid_group_all = group_cols("null_AUC_lipid", "net_AUC_lipid")
    pair_group_all = group_cols("null_AUC_pair", "net_AUC_pair")

    # rows/pos (block size, not a measurement) dropped from the printed mean -- still
    # fully present in `table` itself and in the on-disk cache, just not useful next
    # to the AUC columns this table exists to show.
    drop_cols = ["seed", "rows", "pos"]
    if not show_prot_group:
        drop_cols += ["proteins"] + prot_group_all
    if not show_lipid_group:
        drop_cols += ["lipids"] + lipid_group_all
    if not show_pair_group:
        drop_cols += pair_group_all
    by_family = table.groupby("fam").mean(numeric_only=True).drop(
        columns=[c for c in drop_cols if c in table.columns]
    )
    # Pooled columns (rank the whole block) first, then whichever within-entity
    # group(s) this granularity shows -- grouped rather than interleaved by k, since
    # these answer different questions (see the "never averaged together" note
    # below) and reading them side by side per-k invites comparing across that line
    # by accident.
    prot_group = [c for c in prot_group_all if c in by_family.columns]
    lipid_group = [c for c in lipid_group_all if c in by_family.columns]
    pair_group = [c for c in pair_group_all if c in by_family.columns]
    pooled_cols = [c for c in by_family.columns
                   if c not in prot_group and c not in lipid_group and c not in pair_group
                   and c not in ("proteins", "lipids")]
    ordered = pooled_cols[:]
    if show_prot_group:
        ordered += ["proteins"] + prot_group
    if show_lipid_group:
        ordered += ["lipids"] + lipid_group
    if show_pair_group:
        ordered += pair_group
    by_family = by_family[ordered]
    print("=== mean over seeds ===")
    print(by_family.round(3).to_string())
    print()
    # Pooled columns rank the whole block; _prot/_lipid/_pair columns rank inside one
    # entity (or, for _pair, inside neither -- see per_pair_auc). They are different
    # questions and must not be averaged together or read off one line.
    columns = [c for c in table.columns
               if (c.endswith("AUC") or "AUC_k" in c)
               and c not in prot_group_all and c not in lipid_group_all
               and c not in pair_group_all]
    # WORKING/other-four split (files/signal_state.md 6.4: never average over all
    # seven at once) is NOT printed here any more -- `table` (and the on-disk cache
    # when null_model_table was given a `label`) still carries `fam` on every row, so
    # that split is one groupby away for whoever needs it from there. The printout
    # is one general table instead -- mean, median, and the two std's (see
    # _group_stats) over all seven at once, which is simpler on the terminal and, for
    # the two std's specifically, still correctly separates seed noise from
    # family-to-family spread regardless of which families are pooled into it.
    print("=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===")
    groups = {"all seven": table}
    print(_group_stats(groups, columns).round(3).to_string())

    def print_within_entity_section(header, count_col, group_columns):
        if not group_columns:
            return
        print(f"\n=== the same rows ranked INSIDE each {header} ===")
        if count_col is not None:
            print(f"{int(table[count_col].sum())} {header} blocks across {len(table)} "
                  f"family-seed splits carry a usable ranking "
                  f"(median {table[count_col].median():.0f} {header} groups per split)")
        groups = {"all seven": table}
        print(_group_stats(groups, group_columns).round(3).to_string())

    if show_prot_group:
        print_within_entity_section("protein", "proteins", prot_group)
    if show_lipid_group:
        # "lipid class" (dataloader.lipid_classes.lipid_class_series), not species --
        # see per_lipid_auc's own docstring for why species-level is structurally
        # unusable on this dataset's split shape (2-5 candidate proteins per block).
        print_within_entity_section("lipid class", "lipids", lipid_group)
    if show_pair_group:
        print_within_entity_section(
            "protein AND inside each lipid class jointly (per_pair_auc)", None, pair_group
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--neighbours", default="5,15,40", help="k, comma separated")
    parser.add_argument("--share", type=float, default=0.7, help="--coldsplit_share of the run")
    parser.add_argument("--ratio", type=int, default=2, help="--negatives_per_positive of the run")
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument(
        "--scores",
        help="CSV from analysis/checkpoint_scores.py; adds the network's AUC on the same rows",
    )
    parser.add_argument("--epoch", type=int, default=120, help="which checkpoint epoch to read")
    parser.add_argument(
        "--features", default=TANIMOTO,
        help=(
            f'"{TANIMOTO}" (default): full-structure Morgan-fingerprint similarity, '
            "one null-model entity per lipid species -- the original null model. "
            "Otherwise a comma-separated list of descriptor names, any mix of "
            f"lipid-only ({','.join(LIPID_DESCRIPTOR_NAMES)}), protein-only "
            "(dataloader.protein_graph_builder.POCKET_DESCRIPTOR_NAMES, e.g. "
            "pocket_extent,aromatic_share), and pair "
            f"({','.join(PAIR_DESCRIPTOR_NAMES)}). Lipid-only names alone give one "
            "entity per lipid species (as before); protein-only names alone give one "
            "entity per protein; anything spanning both, or any pair name, gives one "
            "entity per protein-lipid row -- see dataloader.chemistry_prior."
            "feature_similarity."
        ),
    )
    parser.add_argument(
        "--label",
        help=(
            "Short name for --features, used both to print the descriptor set and as "
            "the cache key (see --no-cache) -- defaults to --features itself, which "
            "is fine for one or two names but unwieldy for a long list."
        ),
    )
    parser.add_argument(
        "--no-cache", dest="cache", action="store_false",
        help="Recompute the null model even if a matching --label result is cached.",
    )
    parser.add_argument(
        "--zscore", action="store_true",
        help=(
            "Standardise both sides of the six MULTIPLICATIVE pair descriptors "
            "(aromatic_contact, hbond_match, volume_fit, buriedness_match, "
            "depth_bulk_match, hydropathy_chain_match) before multiplying, so "
            "neither side's raw scale accidentally dominates the product's variance "
            "-- see dataloader.chemistry_prior.feature_similarity. Has no effect on "
            "occupancy/chain_extent_gap (already a physical angstrom-vs-angstrom "
            "comparison) or on non-pair descriptors."
        ),
    )
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    data_dir = os.path.join(PROJECT_ROOT, "data")
    similarity, index, entity_column, label, feature_list = resolve_similarity(
        csv, data_dir, args.features, args.label, zscore=args.zscore
    )
    network = pandas.read_csv(args.scores) if args.scores else None

    table = null_model_table(
        csv, similarity, index,
        families=[f for f in args.families.split(",") if f],
        seeds=[int(s) for s in args.seeds.split(",")],
        neighbour_counts=[int(k) for k in args.neighbours.split(",")],
        share=args.share, ratio=args.ratio, split=args.split,
        network=network, epoch=args.epoch, entity_column=entity_column,
        label=(label if args.cache else None), features=feature_list,
    )
    print(f"=== features = {label} ({','.join(feature_list)}) ===\n")
    print_null_model_report(table, args.split, args.epoch, entity_column=entity_column)


if __name__ == "__main__":
    main()
