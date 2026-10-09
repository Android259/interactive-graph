#!/usr/bin/env python3
"""The no-training competitors every cold split has to be read against, one script for
every split axis and every feature set.

The question. A cold-split number means nothing on its own: it has to be read against
what a predictor that never trained scores on the IDENTICAL rows. Which trivial
predictor that is depends on the axis, and the trap is the same on all of them -- the
number usually quoted (0.500, "the per-lipid label prior") is 0.500 BY CONSTRUCTION
there (no evaluated lipid's class is in train, so the lookup always falls back), so it
is not a bar at all. Chemistry extrapolation is: a lipid the model has never seen can
still resemble one it has, and "resembles a training positive" needs no protein, no
pocket and no attention. Everything this project is built to measure lives above that
line, so the line has to be drawn before any number above it means anything.

Three competitors, all trained on nothing, all scored on the rows the network is scored
on. Read them as a set, not one instead of another:

  null            For a held row (P, L), the similarity-weighted train positive rate of
                  L's k nearest training entities -- bound by ANYBODY. Ignores P
                  entirely at lipid granularity, so two held rows sharing a lipid get
                  the same score. Answers: is the signal in the chemistry alone?
  within_protein  The same, restricted to P's own training rows: did THIS protein bind
                  the lipids most like L. Stronger, and the one a network has to beat
                  before "it learned the pair" means anything, since the network also
                  sees both sides. nan where a protein kept no training rows at all --
                  reported as coverage rather than hidden, see auc_on_scored.
  contrastive     Closer to something this protein BINDS than to something it does not
                  (top-k mean similarity to its training positives minus the same over
                  its negatives). The subtraction cancels the sampled class ratio, which
                  is what makes `within_protein` read as chance at small k -- see
                  dataloader.chemistry_prior.null_scores_contrastive. The hardest bar.

Every split axis, one code path. Which rows are held out is the ONLY thing that differs
between axes, so it is the only thing branched on (see Block/split_held_block):

  --families          the protein-family axis (`--double_coldsplit`): the family leaves
                      train and the lipid classes it owns leave with it
                      (lipid_classes_for_holdout, --share).
  --sets              the lipid-class axis (`--lipid_coldsplit`): whole head-group
                      classes leave train, every protein stays in it
                      (dataloader.splitting_on_blocks.lipid_coldsplit_blocks.LIPID_COLDSPLIT_SETS).
  --lipid_subclass    a species-keyed block (`--lipid_subclass`), e.g. "PA" or
                      "CerP+Hex2Cer+SHexCer".
  --lipid_species_coldsplit  a species-keyed block of this share, redrawn per seed
                      exactly as the loader draws it.
  --family_only       restrict the whole table to one ProteinDomain first, the way the
                      loader does -- the regime the DeepCLIP runs train in. Both
                      protein-aware competitors are then built from that family's own
                      rows only, which is what they have to be compared against.

Every feature set, one flag. `--features` is any feature vector, not only chemical
fingerprints: the literal "tanimoto" (Morgan fingerprints over the whole structure),
"molformer" (the learned embedding, same per-species grain), or any comma-separated mix
of lipid-only / protein-only / pair descriptor names --
dataloader.chemistry_prior.feature_similarity resolves the mix and decides the
granularity (per lipid species, per protein, or per protein-lipid row). So "would these
four descriptors alone have done it" is one flag away, and is the direct way to ask
whether a descriptor set carries a split or merely tracks it.

Reported as AUC, not balanced accuracy. At a fixed 0.5 threshold the chemistry null
model scores BA 0.512 while ranking the doubly-cold block at AUC 0.589: nearly all of
its measured weakness is threshold placement, and a comparison against a network at the
same fixed threshold would credit the network for a decision boundary rather than for
information. AUC compares what each one knows.

    python3 analysis/baselines/null_model.py
    python3 analysis/baselines/null_model.py --scores /tmp/scores_small27k.csv --epoch 120
    python3 analysis/baselines/null_model.py --sets sphingolipids --split test
    python3 analysis/baselines/null_model.py --family_only gltp \\
        --lipid_subclass CerP+Hex2Cer+SHexCer --features chain,unsaturation,hbond,heavy
    python3 analysis/baselines/null_model.py --lipid_species_coldsplit 0.3 --out /tmp/lcs.csv

With `--scores` (the CSV `analysis/checkpoint_scores.py` writes) the network's AUC is
computed on exactly the rows it was evaluated on, matched by `pair_id`, and the
competitors are restricted to those same rows -- so the numbers are the same measurement
of the same block and the difference between them is the network's own contribution.

Reads only. Trains nothing, appends to no shared table (writes only the null-model cache
below, and `--out` when given).
"""
import argparse
import json
import os
import sys
from collections import namedtuple

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dataloader.chemistry_prior import (  # noqa: E402
    LIPID_DESCRIPTOR_NAMES, PAIR_DESCRIPTOR_NAMES, feature_similarity,
    molformer_species_similarity, null_scores, null_scores_contrastive,
    null_scores_within_protein, species_similarity,
)
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.splitting_on_blocks.lipid_species_blocks import species_coldsplit_block  # noqa: E402
from dataloader.splitting_on_blocks.lipid_subclass_blocks import subclass_block_species  # noqa: E402
from dataloader.splitting_on_blocks.lipid_coldsplit_blocks import (  # noqa: E402
    LIPID_COLDSPLIT_SETS,
    lipid_classes_for_holdout,
)
from dataloader.sampler import (  # noqa: E402
    lipid_class_series,
    split_and_sample_lipid_class_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
)
from preprocessing.lipid_marginal_baseline import lipid_isolation_split  # noqa: E402
from preprocessing.lipid_marginal_baseline import lipid_split as lipid_split_func  # noqa: E402
from preprocessing.lipid_marginal_baseline import split as split_func  # noqa: E402

DEFAULT_FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")
# The three families whose validation sits above 0.5 in every dcs run, from
# files/results/signal_state.md section 4.1. Named here so the summary can report them apart:
# averaging across all seven hides both halves of the split.
WORKING = ("LBP_BPI_CETP", "scp2", "IP_trans")

# Reserved --features value: the original whole-molecule Morgan-fingerprint null
# model (species_similarity) rather than a named scalar descriptor set --
# feature_similarity has no entry for "the whole structure", only named columns.
TANIMOTO = "tanimoto"

# Reserved --features value: the whole-molecule MolFormer-embedding null model
# (molformer_species_similarity), reading the matrix
# preprocessing/build_molformer_similarity_matrix.py precomputes -- same idea as
# TANIMOTO (one entity per lipid species, whole-structure similarity rather than a
# named scalar subset) but from the learned embedding instead of a Morgan fingerprint.
MOLFORMER = "molformer"

# ModelConfig defaults for the flags a lipid-axis arg file leaves alone; a split has to
# be rebuilt with the same ones the compared run trained under or the rows will not
# match (the pair_id check in null_model_table says so rather than guessing).
DEFAULT_RATIO = 2
DEFAULT_NEIGHBOURS = (5, 15, 40)

# The three competitors, by the column prefix each one's numbers are reported under.
# `null` takes the held rows' entity values; the two protein-aware ones take the whole
# held frame, because they need its protein column too -- _competitor_scores is the one
# place that difference lives.
COMPETITORS = {
    "null": null_scores,
    "within_protein": null_scores_within_protein,
    "contrastive": null_scores_contrastive,
}
DEFAULT_COMPETITORS = tuple(COMPETITORS)

# Persisted competitor-only results (never the network's own AUC, which depends on
# that label's own checkpoints and must always be scored fresh): one process building
# graphics/<labelA>/<labelA>.md and graphics/<labelB>/<labelB>.md back to back (the
# common case -- scripts/lib/generate_label_report.sh runs full_label_report.py once
# per label) recomputes the IDENTICAL null model for every label that shares a
# --features set and a --coldsplit_share/--negatives_per_positive, which is most of
# them. Keyed by (label, block, seed, neighbour_counts, competitors, share, ratio,
# split, a cheap csv fingerprint) so a rebuilt interaction table (project memory
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


def _cache_key(label, block, seed, neighbour_counts, competitors, share, ratio, split,
               csv_fingerprint):
    """The identity of one cached record.

    `block` is the block's own name AND kind (see Block): a --lipid_subclass block
    called "PA" and a LIPID_COLDSPLIT_SETS entry of the same name would hold out
    different rows, so the kind has to be in the key and not only the name.
    `competitors` is in it because a record carries one column block per competitor --
    without it, a table computed for `null` alone would be served to a caller asking
    for all three, which would then read missing columns as absent rather than
    uncomputed.
    """
    return "|".join(str(part) for part in (
        label, f"{block.kind}:{block.name}", seed,
        ",".join(str(k) for k in sorted(neighbour_counts)),
        ",".join(sorted(competitors)), share, ratio, split, csv_fingerprint,
    ))


def resolve_similarity(csv, data_dir, features, label=None, zscore=False):
    """--features (comma-separated descriptor names, or the literal "tanimoto") ->
    (similarity, index, entity_column, label, feature_list).

    `features` a single string, either TANIMOTO, MOLFORMER or a comma list drawing on
    dataloader.chemistry_prior.LIPID_DESCRIPTOR_NAMES /
    dataloader.graphs_builders.protein_graph_builder.POCKET_DESCRIPTOR_NAMES / PAIR_DESCRIPTOR_NAMES
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
    elif features == MOLFORMER:
        similarity, index = molformer_species_similarity(data_dir)
        entity_column = "FullIdentityOfLipid"
        feature_list = [MOLFORMER]
    else:
        feature_list = sorted(name for name in features.split(",") if name)
        similarity, index, entity_column = feature_similarity(
            csv, data_dir, feature_list, zscore=zscore
        )
    resolved_label = label or (features + (" +zscore" if zscore else ""))
    if zscore:
        feature_list = feature_list + ["zscore"]
    return similarity, index, entity_column, resolved_label, feature_list


def working_set(csv, seed, ratio, lipid_classes, balanced_lipid_classes=False,
                species=None):
    """The loader's `csvt`, carrying the loader's `pair_id`.

    `lipid_marginal_baseline.working_set` builds the same rows in the same order but
    renumbers them 0..N-1 and keeps no trace of where they came from, and `pair_id` --
    the original row of the interaction table -- is assigned by
    `Dataloader.__init__` *before* that renumbering. Matching rows against the
    scores `analysis/checkpoint_scores.py` writes needs that id, so the two lines are
    reproduced here rather than in the baseline, whose own numbers do not use it.

    `balanced_lipid_classes` picks the SAMPLER, and it has to match the run being
    compared against or the rebuilt pool is a different set of rows. Dataloader.py tests
    that flag FIRST in its own if/elif chain, so a run setting it never reaches the
    protein-balanced sampler at all -- reproducing it here with the default would
    silently compare a network's scores to a null model built on other rows.
    """
    if species is not None:
        # A block named by SPECIES (--lipid_subclass / --lipid_isolation /
        # --lipid_species_coldsplit) rather than by head-group class. The sampler's
        # strata are "which side of the coming cut is this row on", so they have to be
        # computed on the same key the cut uses -- head-group class would put a held-out
        # species and a retained one of the same class on the same side.
        strata = csv["FullIdentityOfLipid"].isin(set(species))
    else:
        held = {name.lower() for name in lipid_classes}
        strata = lipid_class_series(csv).str.lower().isin(held) if held else None
    if balanced_lipid_classes:
        positives, negatives = split_and_sample_lipid_class_balanced_interactions(
            csv, seed, ratio=ratio
        )
    else:
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


def auc_on_scored(truth, score):
    """(AUC over the rows this competitor could score, share of rows it could score).

    `null_scores_within_protein`/`null_scores_contrastive` return nan for a held row
    whose protein has NO training rows left (or none of one label) -- real under a lipid
    axis: a protein that only ever binds the held-out chemistry keeps nothing once those
    classes leave training. A single nan poisons the pooled AUC (pandas' rank()
    propagates it), which silently turned three of the four lipid sets into "nan" rather
    than into a number plus a caveat.

    Scoring the covered rows and reporting the coverage is the honest reading: the
    competitor is not wrong on the rows it cannot see, it is absent, and how often it is
    absent is itself worth knowing -- it says how much of the block is out of reach of
    "ask this protein about similar lipids" altogether. `null` never returns nan, so its
    coverage is 1.0 and the two readings coincide.
    """
    truth = np.asarray(truth)
    score = np.asarray(score, dtype=float)
    covered = ~np.isnan(score)
    if not covered.any():
        return float("nan"), 0.0
    return auc(truth[covered], score[covered]), float(covered.mean())


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

    Rows this competitor could not score at all (nan -- see auc_on_scored) are dropped
    before the two means are taken, not merely at the end: one nan would otherwise
    poison both its protein's and its class's mean and, through pandas' rank(), the
    whole pooled number, so a competitor with 86% coverage would report nan rather than
    its AUC over the 86%. A nan-free score (every `null` one) loses nothing here.
    """
    frame = held.assign(_score=np.asarray(score, dtype=float))
    frame = frame[frame["_score"].notna()]
    if frame.empty:
        return float("nan")
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


# One held-out block, independent of which axis produced it. `kind` selects the
# reconstruction (see split_held_block), `name` is what the block is called in the
# table's `fam` column and in the cache key, and `species_of_seed` is a callable
# seed -> the FullIdentityOfLipid set this block holds out, for the species-keyed axes
# only (a callable rather than a set because --lipid_species_coldsplit draws its block
# per seed, exactly as the loader does).
Block = namedtuple("Block", "name kind species_of_seed")


def family_block(name):
    """The protein-family axis (`--double_coldsplit`): one entry of DEFAULT_FAMILIES."""
    return Block(name=name, kind="family", species_of_seed=None)


def lipid_set_block(name):
    """The lipid-class axis (`--lipid_coldsplit`): one key of LIPID_COLDSPLIT_SETS."""
    return Block(name=name, kind="lipid_set", species_of_seed=None)


def subclass_blocks(specs, data_dir):
    """`--lipid_subclass` specs ("PA", "CerP+Hex2Cer+SHexCer") -> species-keyed Blocks.

    The species-keyed axes are not expressible as a LIPID_COLDSPLIT_SETS entry, which is
    why the class-set route alone left the regime the DeepCLIP gate runs in
    (--family_only plus a subclass block) with no baseline at all.
    """
    blocks = []
    for spec in specs:
        held = tuple(subclass_block_species(spec, data_dir))
        blocks.append(Block(
            name=spec, kind="species", species_of_seed=lambda seed, held=held: held
        ))
    return blocks


def species_coldsplit_blocks(csv, share):
    """`--lipid_species_coldsplit`: one Block whose species set is redrawn per seed."""
    return [Block(
        name="species%02d" % int(share * 100 + 0.5),
        kind="species",
        species_of_seed=lambda seed, share=share: species_coldsplit_block(csv, share, seed)[0],
    )]


def blocks_from_families(families):
    """`--families` entries -> Blocks, each axis by its own name.

    A name that is a LIPID_COLDSPLIT_SETS key is the lipid-class axis; anything else is
    a protein family. Kept as one list rather than two flags because `families` is the
    parameter every existing caller (analysis/full_label_report.py,
    analysis/probes/greedy_descriptor_search.py) already passes both kinds of name through.
    """
    return [
        lipid_set_block(name) if name in LIPID_COLDSPLIT_SETS else family_block(name)
        for name in families
    ]


def held_classes_for(csv, block, share):
    """The head-group classes this block holds out of training, or () for a species one.

    `--lipid_coldsplit` holds out a set fixed in advance (LIPID_COLDSPLIT_SETS) -- there
    is no family to derive anything from, every protein stays in train. `--double_
    coldsplit` derives them per family (`lipid_classes_for_holdout`). Calling the
    derivation on a lipid-set name looks up a `ProteinDomain` that does not exist and
    silently returns `[]`, which is why the two are branched on rather than merged.

    Accepts a Block or a bare name (a bare name is resolved through
    blocks_from_families' own rule, so a caller holding a family or set name keeps
    working).
    """
    if not isinstance(block, Block):
        block = blocks_from_families([block])[0]
    if block.kind == "species":
        return []
    if block.kind == "lipid_set":
        return list(LIPID_COLDSPLIT_SETS[block.name])
    return lipid_classes_for_holdout(csv, block.name, share)[0]


def split_held_block(csv, block, seed, share, ratio, balanced_lipid_classes=False):
    """(train, valid, test) for one block and seed -- the only axis-dependent step.

    The pool is rebuilt first (`working_set`, the loader's own sampler and `pair_id`),
    then cut the way the loader cuts it for this axis:
      family     `split(..., double=True)`: the family's rows leave train along with
                 the classes it owns, and only rows held out on BOTH axes are evaluated
                 (preprocessing.lipid_marginal_baseline.split).
      lipid_set  `lipid_split`: whole head-group classes leave train, no family does.
      species    `lipid_isolation_split`: the same, keyed by FullIdentityOfLipid.

    `block` may be a bare name instead of a Block, resolved by blocks_from_families'
    own rule -- the two string-named axes are what a caller with a family list has.
    """
    if not isinstance(block, Block):
        block = blocks_from_families([block])[0]
    species = block.species_of_seed(seed) if block.species_of_seed is not None else None
    held_classes = held_classes_for(csv, block, share)
    csvt = working_set(
        csv, seed, ratio, held_classes,
        balanced_lipid_classes=balanced_lipid_classes, species=species,
    )
    if block.kind == "species":
        return lipid_isolation_split(csvt, species, seed)
    if block.kind == "lipid_set":
        return lipid_split_func(csvt, held_classes, seed)
    return split_func(csvt, block.name, seed, held_classes, double=True)


def usable_group_counts(held, minimum_rows=6, group_column="lipid_class"):
    """(proteins, lipid groups) of `held` that carry a usable within-entity ranking.

    The same admission rule per_protein_auc/per_lipid_auc apply (at least
    `minimum_rows` rows and both labels present), counted from `held`'s grouping
    alone -- which is all it depends on, so it is the same number whichever score
    vector is being ranked, and reporting "a mean over three proteins" rather than
    over thirty does not have to wait for one of the competitors to run.
    """
    counts = []
    for column in ("LTPProtein", group_column):
        usable = 0
        for _, group in held.groupby(column):
            if len(group) >= minimum_rows and group["Interaction"].nunique() >= 2:
                usable += 1
        counts.append(usable)
    return tuple(counts)


def structurally_impossible(block, competitor):
    """Whether this competitor can say anything at all about this block's rows.

    On the protein-family axis it cannot: `--double_coldsplit` evaluates only rows whose
    protein IS the held-out family, and that family left training entirely, so "did THIS
    protein bind the lipids most like L" has no training rows to ask -- coverage is
    exactly 0.0 for every row of every seed, by construction and not by accident. The
    columns are still reported (nan AUC, 0.0 coverage, so the table's shape does not
    change with the axis) but the k-nearest-neighbour pass behind them is skipped, which
    is the whole per-label cost of carrying both competitors on an axis that cannot use
    them.
    """
    return block.kind == "family" and competitor != "null"


def _competitor_scores(name, train, held, similarity, index, neighbours, entity_column):
    """One competitor's score vector for `held`. See COMPETITORS.

    `null` is a function of the held row's ENTITY alone, so it takes that column; the
    protein-aware two need the frame itself to find each row's own protein. This is the
    whole of the difference between them at the call site.
    """
    scorer = COMPETITORS[name]
    if name == "null":
        return scorer(train, held[entity_column], similarity, index, neighbours,
                      entity_column)
    return scorer(train, held, similarity, index, neighbours, entity_column)


def _network_rows(network, block, seed, split_name):
    """The scored rows of `network` belonging to this (block, seed, split), or None.

    A label that names its own block files the run under the whole directory name
    (analysis/checkpoint_scores.self_named_group), so a --family_only + --lipid_subclass
    run writes fam "PA_groups_cral-trio" where the block here is called "PA". Matching
    on equality alone found nothing and silently dropped the net_AUC column instead of
    saying so.
    """
    if network is None:
        return None
    fam = network["fam"].astype(str)
    mine = network[
        ((fam == block.name) | fam.str.startswith(f"{block.name}_groups_"))
        & (network["seed"] == seed)
        & (network["split"] == split_name)
    ]
    return None if mine.empty else mine


def null_model_table(csv, similarity, index, families=None, seeds=(0, 1, 2, 3, 4),
                      neighbour_counts=DEFAULT_NEIGHBOURS, share=0.7, ratio=2,
                      split="valid", network=None, epoch=None,
                      entity_column="FullIdentityOfLipid", label=None, features=None,
                      cache_path=CACHE_PATH, balanced_lipid_classes=False,
                      blocks=None, competitors=DEFAULT_COMPETITORS):
    """One row per (block, seed, split): every competitor's AUC(s) and, if `network` is
    given, the network's own on the same rows.

    `blocks`/`families`: pass `blocks` (a list of Block, from subclass_blocks /
    species_coldsplit_blocks / blocks_from_families) for an arbitrary axis, or
    `families` (names, resolved by blocks_from_families) for the two axes that are
    named by a plain string. Exactly one of the two.

    `competitors`: which of COMPETITORS to score. Each one contributes its own
    `<name>_AUC*` column block, so a caller reading only one of them (a descriptor
    search looping over thousands of feature sets, say) should ask for only that one
    rather than paying for three.

    `balanced_lipid_classes` must match whether `--label`'s own run set
    `--balanced_lipid_classes`: it picks working_set's negative sampler, and a
    mismatch there reproduces a different set of rows than the checkpoint was
    actually scored on (working_set's own docstring), which fails the pair_id
    check below just as surely as a wrong held_classes does.

    `network` is the RAW (unfiltered) scores DataFrame from
    analysis/checkpoint_scores.py; filtered here by `epoch` and, per row, by the split
    being scored, so a caller holding scores for several epochs can call this once per
    epoch without re-reading anything. Pass network=None for the competitors alone.

    `entity_column`: which column of `held`/`train` identifies one null-model entity
    (FullIdentityOfLipid / LTPProtein / pair_id) -- must match what `similarity`/
    `index` are keyed by (see feature_similarity/resolve_similarity).

    `split`: "valid", "test", or "both" (one row per split then).

    `label`/`features`: when `label` is given, the competitor-only columns (not
    net_AUC*, which depend on `network` and are always recomputed) are read from and
    written to a persistent on-disk cache at `cache_path`, keyed by (label, block,
    seed, neighbour_counts, competitors, share, ratio, split, a csv fingerprint) --
    see CACHE_PATH. `features` (the resolved descriptor-name list `label` stands for)
    is stored alongside each cache entry and checked against the current call's, so a
    label re-used for a different descriptor set misses rather than returning the old
    set's numbers under the new name. `label=None` (the default) disables caching.

    Returns the `table` main() used to print -- factored out so
    analysis/full_label_report.py can build it without a CSV round-trip through
    --scores.
    """
    if (blocks is None) == (families is None):
        raise ValueError("null_model_table takes either `blocks` or `families`")
    if blocks is None:
        blocks = blocks_from_families(families)
    unknown = [name for name in competitors if name not in COMPETITORS]
    if unknown:
        raise ValueError(f"unknown competitor(s): {unknown}. Known: {list(COMPETITORS)}")
    if network is not None and epoch is not None:
        network = network[network["epoch"] == epoch]
    split_names = ("valid", "test") if split == "both" else (split,)

    cache = load_null_model_cache(cache_path) if label is not None else None
    csv_fingerprint = _csv_fingerprint(csv)
    feature_list = sorted(features) if features is not None else None

    rows = []
    for block in blocks:
        for seed in seeds:
            train, valid, test = split_held_block(
                csv, block, seed, share, ratio,
                balanced_lipid_classes=balanced_lipid_classes,
            )
            for split_name in split_names:
                held = valid if split_name == "valid" else test
                if held.empty:
                    continue
                # per_lipid_auc's default grouping -- attached once here so every
                # competitor's call below and the network call further down see it.
                held = held.assign(lipid_class=lipid_class_series(held))

                cache_key = None
                cached_entry = None
                if cache is not None:
                    cache_key = _cache_key(
                        label, block, seed, neighbour_counts, competitors, share, ratio,
                        split_name, csv_fingerprint,
                    )
                    cached_entry = cache.get(cache_key)
                    if cached_entry is not None and cached_entry.get("features") != feature_list:
                        cached_entry = None  # same label, different descriptor set: miss

                if cached_entry is not None:
                    record = dict(cached_entry["record"])
                else:
                    count_proteins, count_lipids = usable_group_counts(held)
                    record = {
                        "fam": block.name,
                        "seed": seed,
                        "split": split_name,
                        "rows": len(held),
                        "pos": int(held["Interaction"].sum()),
                        "sim_to_train_pos": proximity_to_train_positives(
                            train, held, similarity, index, entity_column
                        ),
                        "proteins": count_proteins,
                        "lipids": count_lipids,
                    }
                    truth = held["Interaction"].to_numpy()
                    for name in competitors:
                        impossible = structurally_impossible(block, name)
                        for neighbours in neighbour_counts:
                            if impossible:
                                for suffix in ("", "_prot", "_lipid", "_pair"):
                                    record[f"{name}_AUC{suffix}_k{neighbours}"] = float("nan")
                                record[f"{name}_covered_k{neighbours}"] = 0.0
                                continue
                            scores = _competitor_scores(
                                name, train, held, similarity, index, neighbours,
                                entity_column,
                            )
                            # auc_on_scored, not auc: the two protein-aware competitors
                            # return nan where a protein kept no training rows, and one
                            # nan poisons a pooled rank. `null` has none, so this is the
                            # plain AUC there and the coverage is 1.0.
                            pooled, covered = auc_on_scored(truth, scores)
                            record[f"{name}_AUC_k{neighbours}"] = pooled
                            record[f"{name}_covered_k{neighbours}"] = covered
                            # All three within-entity readings computed unconditionally,
                            # regardless of entity_column -- cheap either way, and which
                            # one is degenerate (always exactly 0.5, see per_protein_auc/
                            # per_lipid_auc) depends on entity_column, so
                            # print_null_model_report decides which to show rather than
                            # this function guessing on its behalf.
                            record[f"{name}_AUC_prot_k{neighbours}"] = per_protein_auc(
                                held, scores
                            )[0]
                            record[f"{name}_AUC_lipid_k{neighbours}"] = per_lipid_auc(
                                held, scores
                            )[0]
                            record[f"{name}_AUC_pair_k{neighbours}"] = per_pair_auc(
                                held, scores
                            )
                    if cache is not None:
                        cache[cache_key] = {
                            "label": label, "features": feature_list, "record": record
                        }
                        save_null_model_cache(cache, cache_path)

                mine = _network_rows(network, block, seed, split_name)
                if mine is not None:
                    # The loader renumbers csvt 0..N-1 before splitting, and both sides
                    # of this comparison carry that number, so equal pair_id sets mean
                    # the two reproductions of the split agree row for row.
                    if set(mine["pair_id"]) != set(held["pair_id"]):
                        raise SystemExit(
                            f"{block.name}/seed{seed}/{split_name}: the split rebuilt "
                            "here does not match the scored rows -- check --ratio "
                            "against the label's own --negatives_per_positive"
                        )
                    merged = held.merge(
                        mine[["pair_id", "prob"]], on="pair_id", how="left",
                        validate="one_to_one",
                    )
                    probs = merged["prob"].to_numpy()
                    record = dict(record)
                    record["net_AUC"] = auc(merged["Interaction"].to_numpy(), probs)
                    # Unlike the competitors' own _prot/_lipid columns, none of these is
                    # ever mechanically degenerate: the network sees both protein and
                    # lipid information regardless of what the competitors' --features
                    # granularity is, so all three stay meaningful and
                    # print_null_model_report shows them unconditionally.
                    record["net_AUC_prot"], _ = per_protein_auc(merged, probs)
                    record["net_AUC_lipid"], _ = per_lipid_auc(merged, probs)
                    record["net_AUC_pair"] = per_pair_auc(merged, probs)

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
    files/results/signal_state.md 6.4 says never average over all seven at once). Pooling
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


def _reading_of(column):
    """Which reading a column reports: "prot", "lipid", "pair", "pooled", or None.

    One classifier for every competitor's columns and for the network's, so adding a
    competitor needs no second list of prefixes. The `_k{k}` suffix is what separates a
    competitor's column from the network's (`net_AUC_prot` has no k -- the network is
    not a k-nearest-neighbour anything), and both land in the same reading group.
    """
    if "_AUC_prot" in column:
        return "prot"
    if "_AUC_lipid" in column:
        return "lipid"
    if "_AUC_pair" in column:
        return "pair"
    if column.endswith("_AUC") or "_AUC_k" in column:
        return "pooled"
    return None


def print_null_model_report(table, split, epoch, entity_column="FullIdentityOfLipid"):
    """The printout main() produces, given a table from null_model_table -- mean over
    seeds, the never-pooled-over-all-seven AUC means, and the within-entity rankings.
    The raw per-(block, seed) rows `table` itself holds are NOT printed here (still
    fully present in `table` for a caller, and in the on-disk cache when
    null_model_table was given a `label` -- see CACHE_PATH): with 5+ blocks x several
    seeds x several k x several competitors, the raw rows are mostly noise next to the
    summaries below, which is what every reader has actually wanted so far.

    Two within-entity rankings exist -- `*_AUC_prot*` (per_protein_auc, ranks a
    protein's own candidate lipids against each other) and `*_AUC_lipid*`
    (per_lipid_auc, the mirror image, ranks a lipid's own candidate proteins) -- and one
    of each competitor's pair can be MECHANICALLY degenerate (always exactly 0.5, not
    "no signal") depending on `entity_column` (feature_similarity's granularity, see
    dataloader.chemistry_prior):
      entity_column == "LTPProtein"        (protein-only features): the _prot columns
                                            are degenerate -- every row of one protein
                                            then shares an identical (protein-only)
                                            score, an unbroken tie.
      entity_column == "FullIdentityOfLipid" (lipid-only features, the original null
                                            model): the _lipid columns are, by the
                                            mirror argument.
      entity_column == "pair_id"           (combined/pair features): neither is
                                            degenerate -- both print.
    The network's own net_AUC_prot/net_AUC_lipid (when `network` was given to
    null_model_table) are NEVER degenerate this way -- the network sees both protein
    and lipid information regardless of the competitors' own --features -- so they
    print unconditionally whenever present, even for a block/entity_column whose
    competitor sibling is hidden as degenerate.
    """
    pandas.set_option("display.width", 200)
    if "split" in table.columns:
        table = table[table["split"] == split]
        if table.empty:
            print(f"\nno {split} rows")
            return
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
    readings = {name: [] for name in ("prot", "lipid", "pair", "pooled")}
    for column in table.columns:
        reading = _reading_of(column)
        if reading is not None:
            readings[reading].append(column)
    # A competitor's own _prot/_lipid column is degenerate at the matching granularity;
    # the network's (no `_k`) never is, so a group stays shown when it holds a net_*
    # column even where the competitors' own are hidden.
    has_net = {
        reading: any("_k" not in column for column in columns)
        for reading, columns in readings.items()
    }
    prot_meaningful = entity_column != "LTPProtein"
    lipid_meaningful = entity_column != "FullIdentityOfLipid"
    show = {
        "prot": (prot_meaningful or has_net["prot"]) and not is_pair,
        "lipid": (lipid_meaningful or has_net["lipid"]) and not is_pair,
        # *_AUC_pair_k* is computed unconditionally in null_model_table regardless of
        # entity_column (see its own comment there), so there is always data to show
        # here -- shown alongside prot/lipid now, not only when is_pair collapses to
        # pair-only (that collapse, and its "replaces" rationale above, is unchanged
        # for entity_column == "pair_id"; this only turns the pair group ON for every
        # other entity_column too, where it used to be silently computed and dropped).
        "pair": is_pair or bool(readings["pair"]),
    }

    # rows/pos (block size, not a measurement) and the coverage columns (reported in
    # their own section below) dropped from the printed mean -- still fully present in
    # `table` itself and in the on-disk cache, just not useful next to the AUC columns
    # this table exists to show.
    covered_cols = [c for c in table.columns if "_covered_k" in c]
    drop_cols = ["seed", "rows", "pos"] + covered_cols
    if not show["prot"]:
        drop_cols += ["proteins"] + readings["prot"]
    if not show["lipid"]:
        drop_cols += ["lipids"] + readings["lipid"]
    if not show["pair"]:
        drop_cols += readings["pair"]
    by_family = table.groupby("fam").mean(numeric_only=True).drop(
        columns=[c for c in drop_cols if c in table.columns]
    )
    present = {
        reading: [c for c in columns if c in by_family.columns]
        for reading, columns in readings.items()
    }
    # Pooled columns (rank the whole block) first, then whichever within-entity
    # group(s) this granularity shows -- grouped rather than interleaved by k, since
    # these answer different questions (see the "never averaged together" note
    # below) and reading them side by side per-k invites comparing across that line
    # by accident.
    within_entity = present["prot"] + present["lipid"] + present["pair"]
    ordered = [c for c in by_family.columns
               if c not in within_entity and c not in ("proteins", "lipids")]
    if show["prot"]:
        ordered += ["proteins"] + present["prot"]
    if show["lipid"]:
        ordered += ["lipids"] + present["lipid"]
    if show["pair"]:
        ordered += present["pair"]
    by_family = by_family[ordered]
    print("=== mean over seeds ===")
    print(by_family.round(3).to_string())
    print()
    if covered_cols:
        # How often each protein-aware competitor could score a row at all. A high AUC
        # over half a block is a different claim from the same AUC over all of it, and
        # the share is itself a measurement: it says how much of the block is out of
        # reach of "ask this protein about similar lipids" -- see auc_on_scored.
        print("=== share of rows each competitor could score (1.000 = all of them) ===")
        print(table.groupby("fam")[covered_cols].mean().round(3).to_string())
        print()
    # Pooled columns rank the whole block; _prot/_lipid/_pair columns rank inside one
    # entity (or, for _pair, inside neither -- see per_pair_auc). They are different
    # questions and must not be averaged together or read off one line.
    print("=== mean AUC (files/results/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===")
    print(_group_stats({"all seven": table}, present["pooled"]).round(3).to_string())

    def print_within_entity_section(header, count_col, group_columns):
        if not group_columns:
            return
        print(f"\n=== the same rows ranked INSIDE each {header} ===")
        if count_col is not None and count_col in table.columns:
            print(f"{int(table[count_col].sum())} {header} blocks across {len(table)} "
                  f"block-seed splits carry a usable ranking "
                  f"(median {table[count_col].median():.0f} {header} groups per split)")
        print(_group_stats({"all seven": table}, group_columns).round(3).to_string())

    if show["prot"]:
        print_within_entity_section("protein", "proteins", present["prot"])
    if show["lipid"]:
        # "lipid class" (dataloader.lipid_classes.lipid_class_series), not species --
        # see per_lipid_auc's own docstring for why species-level is structurally
        # unusable on this dataset's split shape (2-5 candidate proteins per block).
        print_within_entity_section("lipid class", "lipids", present["lipid"])
    if show["pair"]:
        print_within_entity_section(
            "protein AND inside each lipid class jointly (per_pair_auc)", None,
            present["pair"],
        )


def resolve_blocks(args, csv, data_dir):
    """--families / --sets / --lipid_subclass / --lipid_species_coldsplit -> [Block].

    One axis per run: the flags name different held-out blocks, and a table mixing them
    would be averaged over by every reader downstream (`fam` is the only key they carry).
    """
    chosen = [
        name for name, value in (
            ("--lipid_subclass", args.lipid_subclass),
            ("--lipid_species_coldsplit", args.lipid_species_coldsplit),
            ("--sets", args.sets),
        ) if value is not None
    ]
    if len(chosen) > 1:
        raise SystemExit(f"{' and '.join(chosen)} name different blocks; pass one")
    if args.lipid_subclass is not None:
        return subclass_blocks([s for s in args.lipid_subclass.split(",") if s], data_dir)
    if args.lipid_species_coldsplit is not None:
        return species_coldsplit_blocks(csv, args.lipid_species_coldsplit)
    if args.sets is not None:
        names = [s for s in args.sets.split(",") if s]
        unknown = [name for name in names if name not in LIPID_COLDSPLIT_SETS]
        if unknown:
            raise SystemExit(
                f"unknown lipid set(s): {unknown}. Known: {list(LIPID_COLDSPLIT_SETS)}"
            )
        return [lipid_set_block(name) for name in names]
    return blocks_from_families([f for f in args.families.split(",") if f])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--families", default=",".join(DEFAULT_FAMILIES),
        help="protein families for the --double_coldsplit axis (a LIPID_COLDSPLIT_SETS "
             "name here is read as the lipid-class axis instead, same as --sets)",
    )
    parser.add_argument(
        "--sets",
        help=f"score the --lipid_coldsplit axis instead: any of "
             f"{list(LIPID_COLDSPLIT_SETS)}, comma-separated",
    )
    parser.add_argument(
        "--lipid_subclass",
        help="score a --lipid_subclass block instead: one or more specs (\"PA\", "
             "\"CerP+Hex2Cer+SHexCer\"), comma-separated for several blocks",
    )
    parser.add_argument(
        "--lipid_species_coldsplit", type=float,
        help="score a --lipid_species_coldsplit block of this share instead; the block "
             "is redrawn per seed exactly as the loader draws it",
    )
    parser.add_argument(
        "--family_only",
        help="restrict the whole table to one ProteinDomain before anything else, the "
             "way --family_only does in the loader -- the regime every DeepCLIP run "
             "trains in. The protein-aware competitors are then built from that "
             "family's own rows only, which is what they have to be compared against",
    )
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument(
        "--neighbours", default=",".join(str(k) for k in DEFAULT_NEIGHBOURS),
        help="k nearest training entities per held row, comma separated",
    )
    parser.add_argument("--share", type=float, default=0.8, help="--coldsplit_share of the run")
    parser.add_argument("--ratio", type=int, default=DEFAULT_RATIO,
                        help="--negatives_per_positive the compared run trained with")
    parser.add_argument("--split", default="test", choices=("valid", "test", "both"))
    parser.add_argument(
        "--competitors", default=",".join(DEFAULT_COMPETITORS),
        help=f"which no-training competitors to score, comma separated: "
             f"{list(COMPETITORS)} -- see the module docstring for what each one asks",
    )
    parser.add_argument(
        "--scores",
        help="CSV from analysis/checkpoint_scores.py; adds the network's AUC on the same rows",
    )
    parser.add_argument("--epoch", type=int, help="which checkpoint epoch to read")
    parser.add_argument(
        "--features", default=TANIMOTO,
        help=(
            f'"{TANIMOTO}" (default): full-structure Morgan-fingerprint similarity, '
            "one null-model entity per lipid species -- the original null model. "
            f'"{MOLFORMER}": full-structure MolFormer-embedding similarity (same '
            "per-species granularity, see "
            "preprocessing/build_molformer_similarity_matrix.py). "
            "Otherwise a comma-separated list of descriptor names, any mix of "
            f"lipid-only ({','.join(LIPID_DESCRIPTOR_NAMES)}), protein-only "
            "(dataloader.graphs_builders.protein_graph_builder.POCKET_DESCRIPTOR_NAMES, e.g. "
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
        help="Recompute the competitors even if a matching --label result is cached.",
    )
    parser.add_argument(
        "--balanced_lipid_classes", action="store_true",
        help="rebuild the pool with the (family, lipid class)-matched sampler -- must "
             "match the compared run's own flag, or the rows will not line up",
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
    parser.add_argument("--out", help="write every per-(block, seed, split) row here")
    args = parser.parse_args()

    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pandas.read_csv(interaction_csv_path(data_dir + os.sep))
    # The similarity index is built on the FULL table on purpose, before any
    # restriction. dataloader.chemistry_prior.species_similarity maps a species to its
    # candidate structures by ROW POSITION (enumerate over the frame) against row ids
    # that are positions in the whole interaction table, so handing it a subset -- a
    # --family_only slice, reindexed or not -- silently pairs species with another
    # row's structures. Similarity is a property of the chemistry, not of which family
    # is being scored, and the competitors look it up by species name, so the full
    # index serves the restricted rows correctly.
    similarity_csv = csv
    if args.family_only:
        csv = csv[csv["ProteinDomain"].str.lower() == args.family_only.lower()]
        if csv.empty:
            raise SystemExit(f"--family_only={args.family_only} matches no rows")
        # reset_index, because the loader does it too (dataloader/Dataloader.py's own
        # --family_only filter) and pair_id is read straight off the index in
        # working_set. Without it every pair_id here is an id in the whole table while
        # the scored rows carry positions within the family, and the --scores
        # comparison refuses the pair rather than matching wrong rows.
        csv = csv.reset_index(drop=True)
    similarity, index, entity_column, label, feature_list = resolve_similarity(
        similarity_csv, data_dir, args.features, args.label, zscore=args.zscore
    )

    network = None
    if args.scores:
        network = pandas.read_csv(args.scores)
        if args.epoch is None and network["epoch"].nunique() > 1:
            raise SystemExit(
                f"--scores holds epochs {sorted(network['epoch'].unique())}; "
                "pass --epoch to choose one"
            )

    blocks = resolve_blocks(args, csv, data_dir)
    competitors = tuple(name for name in args.competitors.split(",") if name)
    table = null_model_table(
        csv, similarity, index,
        blocks=blocks,
        seeds=[int(s) for s in args.seeds.split(",") if s],
        neighbour_counts=[int(k) for k in args.neighbours.split(",") if k],
        share=args.share, ratio=args.ratio, split=args.split,
        network=network, epoch=args.epoch, entity_column=entity_column,
        label=(label if args.cache else None), features=feature_list,
        balanced_lipid_classes=args.balanced_lipid_classes,
        competitors=competitors,
    )
    print(f"=== features = {label} ({','.join(feature_list)}) ===")
    print(f"entity granularity: {entity_column}, competitors: {','.join(competitors)}\n")
    for split in (("valid", "test") if args.split == "both" else (args.split,)):
        print_null_model_report(table, split, args.epoch, entity_column=entity_column)

    if args.out:
        table.to_csv(args.out, index=False)
        print(f"\nwrote {len(table)} rows to {args.out}")


if __name__ == "__main__":
    main()
