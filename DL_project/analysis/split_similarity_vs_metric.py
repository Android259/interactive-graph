#!/usr/bin/env python3
"""How far the evaluated block sits from training, against the test metric it scored.

One point per (label, exclusion set): the x axis is the chemical distance between the
block a run was tested on and the chemistry that run trained on, the y axis is that
run's test metric. The question it answers is the one the four lipid sets already hint
at without being able to settle -- files/lipid_coldsplit_architecture_direction.md
notes that the model breaks on `sphingolipids`, "самый химически изолированный набор
(Tanimoto 0.458)" -- namely whether the test metric is a function of that distance, and
how steep it is.

Distance is measured exactly as the report already measures it for the existing blocks
(`analysis/coldsplit_geometry.isolation`, the same number quoted in
dataloader/sampler.py's LIPID_COLDSPLIT_SETS comment):

    isolation = mean over the block's distinct lipid structures of the highest
                Tanimoto similarity to any structure that stayed in training

so 0 would mean the block's chemistry has no relative left in training and 1 that every
structure in it has a twin there. The older statistic from tanimoto_group_analysis/
(the plain mean over all cross pairs, not the mean of the maxima) is reported in the
same table as `cross_mean`, so a curve can be read either way without a second run.

The split is not read off the block name -- it is rebuilt, row for row, from the
configuration columns metrics_summary.csv already stores for every run, with the run's
own seed: the same sampler (`dataloader/sampler.py`), the same held-out classes, the
same 50/50 label-stratified halving of the excluded block that
`Dataloader._split_interactions` does. That is what makes the x value belong to the run
whose y value sits next to it, rather than to an idealised version of its split. The
reconstruction is pure pandas and reads no embedding, no graph and no checkpoint.

Every split axis the project runs is handled:

    --lipid_coldsplit     a named chemical set leaves training, every protein stays
    --lipid_isolation     a block chosen by distance, same axis addressed differently
    --lipid_subclass      one Titeca-et-al. subclass, same axis named a third way
    --excluded_groups     a protein family leaves training (+ --double_coldsplit)
    --family_only         one family is the whole table, split 85/7.5/7.5 inside it
    neither of the above  the plain 85/7.5/7.5 random split ("random" in the reports)

TWO axes can go on x, and they are the same statistic read on the two partners:

    --x test_isolation           LIPID: mean over the block's structures of the best
                                 Tanimoto similarity to a training structure
    --x test_protein_isolation   PROTEIN: mean over the block's proteins of the best
                                 RBF pocket-descriptor similarity to a training protein

The protein reading is built the way the Kron-RLS protein kernel is built (standardized
pocket descriptors, RBF), over the descriptor set the RUN itself named in
--protein_descriptors/--pocket_descriptor_names where it named one. It is 1.0 by
construction on every lipid-side split -- no protein is held out there -- so it is the
axis for --excluded_groups/--cold_split labels, where the LIPID axis in turn crushes six
of the seven blocks into 0.78-0.86 and cannot separate them.

Several labels are handled in ONE call -- every label in the table by default, or the
ones named by --labels -- and each gets its own curve in its own place, the way the rest
of the project's figures are filed (scripts/generate_config_graphics.sh):

    graphics/<label>/split_similarity/<label>_split_similarity_vs_metric.pdf
    graphics/<label>/split_similarity/<label>_split_similarity_points.csv

One pass rather than one call per label is not only convenience: the expensive step is
rebuilding the splits, and that work is cached per SPLIT, not per label, so two
configurations that ran the same blocks on the same seeds pay for it once.

Reads metrics_summary.csv and the compact Tanimoto artifacts. Trains nothing, touches no
shared table, and writes only inside the labels' own graphics directories.

    python3 analysis/split_similarity_vs_metric.py
    python3 analysis/split_similarity_vs_metric.py --labels label_a,label_b,label_c
    python3 analysis/split_similarity_vs_metric.py --metrics balanced_accuracy,F1,AUC_within_protein
    python3 analysis/split_similarity_vs_metric.py --labels <protein-coldsplit label> \
        --x test_protein_isolation
"""

from __future__ import annotations

import argparse
import csv as csv_module
import json
import math
import os
import re
import statistics
import sys
import types
from collections import defaultdict
from dataclasses import dataclass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Same stand-in as preprocessing/lipid_marginal_baseline.py: dataloader.sampler imports
# torch for its batch sampler, the pool samplers used here are pure pandas, and the
# machine that reads a metrics table need not have the training runtime installed.
try:  # pragma: no cover - depends on the machine, not on the code path
    import torch  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _torch = types.ModuleType("torch")
    _torch.utils = types.ModuleType("torch.utils")
    _torch.utils.data = types.ModuleType("torch.utils.data")
    _torch.utils.data.Sampler = object
    sys.modules.update(
        {
            "torch": _torch,
            "torch.utils": _torch.utils,
            "torch.utils.data": _torch.utils.data,
        }
    )

import numpy as np  # noqa: E402
import pandas  # noqa: E402

from analysis.coldsplit_geometry import structures_of_rows  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.lipid_isolation_blocks import LIPID_ISOLATION_BLOCKS  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    LIPID_COLDSPLIT_SETS,
    lipid_classes_for_holdout,
    rebalance_excluded_group_negatives,
    split_and_sample_family_balanced_interactions,
    split_and_sample_interactions,
    split_and_sample_lipid_class_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
)
from dataloader.lipid_subclass_blocks import subclass_block_species  # noqa: E402
from dataloader.tanimoto_compact import load_compact  # noqa: E402

# Pocket descriptors the protein-side similarity may be computed over. The Kron-RLS
# protein kernel's own catalog (POCKET_ALL_NAMES) plus the three lambda_sqrt shape
# variants, which live only in the network's PROTEIN_DESCRIPTOR_NAMES -- both reach
# resolve_protein_feature_subset, which is what actually builds the vectors.
# Imported lazily-ish (module level is fine: these two modules are pure pandas/numpy)
# so a machine without the training runtime still runs the lipid axis.
try:  # pragma: no cover - a metrics-only machine may lack rdkit/scipy
    from training.pair_baseline_common import (
        POCKET_ALL_NAMES,
        resolve_protein_feature_subset,
    )
    from dataloader.pair_descriptors import PROTEIN_DESCRIPTOR_NAMES

    PROTEIN_KERNEL_NAMES = frozenset(POCKET_ALL_NAMES) | frozenset(PROTEIN_DESCRIPTOR_NAMES)
except Exception:  # pragma: no cover
    resolve_protein_feature_subset = None
    PROTEIN_KERNEL_NAMES = frozenset()

# What a run that names no descriptor set is measured with: the project's "protunion14",
# the set both current baselines' protein side is built from. Named explicitly rather
# than "whatever is in the catalog" because the similarity is only comparable across
# labels when the description of a pocket is the same for all of them.
DEFAULT_PROTEIN_DESCRIPTORS = (
    "pocket_volume_per_sasa", "pocket_elongation", "pocket_flatness", "buriedness_q50",
    "apolar_sasa_share", "aromatic_share", "hydropathy_rim", "ev28_q10",
    "aromatic_share_rim", "depth_q10", "hydropathy_core", "ev14_q10", "hydropathy_mean",
    "pocket_extent",
)

# The four confusion cells as SHARES of the evaluated block, derived per run from the
# TP/FP/TN/FN counts metrics_summary.csv already stores (derived_metric below). Shares
# and not the raw counts, because the blocks on one curve differ in size by an order of
# magnitude -- the Figure-3 PC block is 2660 rows against PI's 245 -- so a curve of raw
# counts is a curve of block size with the model's behaviour buried in it. The counts
# themselves still go into the point CSV beside the figure.
#
# Why they belong next to BA and F1 rather than instead of them: a summary metric hides
# WHICH WAY a block fails. balanced_accuracy 0.5 is returned equally by a model that
# calls everything positive and one that calls everything negative, and the project has
# already hit both -- the PI block of cron_test_metrics/cron_fig3_lipidgroups.txt is
# test_spec 0.0000 with TN=0 on all ten seeds (everything positive), while deepclip's
# iso70 rung is sensitivity 0.091 against specificity 0.914 (everything negative). On
# these panels those two are opposite corners, not the same point.
CONFUSION_SHARE_METRICS = ("TP_share", "FP_share", "TN_share", "FN_share")
CONFUSION_COUNTS = ("TP", "FP", "TN", "FN")
DEFAULT_METRICS = ("balanced_accuracy", "F1") + CONFUSION_SHARE_METRICS


def derived_metric(row, name):
    """Metric columns that are computed from a metrics row rather than read from it.

    Returns None for a name this function does not derive, so the caller falls back to
    reading the column, and for a row whose counts are missing or do not add up to a
    block (a pre-2026-09 row, or one where the run failed before the test block).
    """
    if name not in CONFUSION_SHARE_METRICS:
        return None
    counts = {}
    for cell in CONFUSION_COUNTS:
        raw = str(row.get(cell, "")).strip()
        try:
            counts[cell] = float(raw)
        except (TypeError, ValueError):
            return None
    total = sum(counts.values())
    if total <= 0:
        return None
    return counts[name.removesuffix("_share")] / total


def read_flag(row, name):
    """A metrics-table boolean: serialize_config writes bools as "0"/"1"."""
    return str(row.get(name, "")).strip() in {"1", "True", "true"}


def read_list(row, name):
    """A metrics-table list column, written by serialize_config as compact JSON."""
    raw = str(row.get(name, "")).strip()
    if not raw or raw in {"[]", "nan"}:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        # Pre-JSON rows spelled a single group out bare; treat it as that one name.
        return [raw]
    return [str(item) for item in value] if isinstance(value, list) else [str(value)]


def read_number(row, name, default):
    raw = str(row.get(name, "")).strip()
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class SplitSpec:
    """Everything about a run that decides which rows it trains on and evaluates."""

    seed: int
    excluded_groups: tuple = ()
    excluded_subgroups: tuple = ()
    lipid_coldsplit: str = ""
    lipid_isolation: str = ""
    lipid_subclass: str = ""
    double_coldsplit: bool = False
    mixed_coldsplit: bool = False
    coldsplit_share: float = 0.8
    family_only: str = ""
    test_group: str = ""
    sampler: str = "plain"
    negatives_per_positive: int = 2
    balance_excluded_group_negatives: bool = False
    hard_negative_mining: bool = False
    # Not part of the split at all -- it is the descriptor set the PROTEIN similarity
    # reading is computed over (protein_isolation below). Carried on the spec because
    # measure_split is cached by spec, and two runs that held out the same proteins but
    # describe their pockets differently do not have the same protein similarity.
    protein_descriptors: tuple = ()

    @property
    def axis(self):
        if self.lipid_isolation:
            return "lipid_isolation"
        if self.lipid_subclass:
            return "lipid_subclass"
        if self.lipid_coldsplit:
            return "lipid_coldsplit"
        if self.family_only:
            return "family_only"
        if self.excluded_groups:
            return "double_coldsplit" if self.double_coldsplit else "protein_coldsplit"
        if self.excluded_subgroups:
            return "protein_subgroups"
        return "random"


def spec_from_row(row):
    """The split a metrics row describes, read off its configuration columns only."""
    sampler = "plain"
    if read_flag(row, "balanced_lipid_classes"):
        sampler = "balanced_lipid_classes"
    elif read_flag(row, "balanced_proteins"):
        sampler = "balanced_proteins"
    elif read_flag(row, "balance_negatives_by_family"):
        sampler = "balance_negatives_by_family"
    return SplitSpec(
        seed=int(read_number(row, "seed", 0)),
        excluded_groups=tuple(read_list(row, "excluded_groups")),
        excluded_subgroups=tuple(read_list(row, "excluded_subgroups")),
        lipid_coldsplit=str(row.get("lipid_coldsplit", "") or "").strip(),
        lipid_isolation=str(row.get("lipid_isolation", "") or "").strip(),
        lipid_subclass=str(row.get("lipid_subclass", "") or "").strip(),
        double_coldsplit=read_flag(row, "double_coldsplit"),
        mixed_coldsplit=read_flag(row, "mixed_coldsplit"),
        coldsplit_share=read_number(row, "coldsplit_share", 0.8),
        family_only=str(row.get("family_only", "") or "").strip(),
        test_group=str(row.get("test_group", "") or "").strip(),
        sampler=sampler,
        negatives_per_positive=int(read_number(row, "negatives_per_positive", 2)),
        balance_excluded_group_negatives=read_flag(
            row, "balance_excluded_group_negatives"
        ),
        hard_negative_mining=read_flag(row, "hard_negative_mining"),
        protein_descriptors=protein_descriptor_names(row),
    )


def protein_descriptor_names(row):
    """The pocket descriptors the PROTEIN similarity reading is computed over.

    The run's own set when it names one -- --protein_descriptors (the node broadcast) or
    --pocket_descriptor_names (the fixed cavity vector's restriction) -- so the
    similarity is computed in the same description of a pocket the model was given.
    Runs that name neither (every --descriptors_head label, and every run older than
    those flags) fall back to DEFAULT_PROTEIN_DESCRIPTORS, and the figure says which was
    used.

    Only the PROTEIN-side names are kept: --protein_descriptors is validated against the
    whole DESCRIPTOR_CATALOG, so a label is free to broadcast lipid names through it too,
    and those have no place in a protein kernel.
    """
    raw = str(row.get("protein_descriptors", "") or "").strip()
    if not raw:
        raw = str(row.get("pocket_descriptor_names", "") or "").strip()
    names = tuple(
        name.strip() for name in raw.split(",")
        if name.strip() in PROTEIN_KERNEL_NAMES
    )
    return names or DEFAULT_PROTEIN_DESCRIPTORS


def held_lipid_species(spec):
    """The lipid species --lipid_isolation holds out, or an empty set.

    The other axis names chemistry by head-group class; this one names it by species,
    because a block chosen for its distance from training is not a class (see
    dataloader/lipid_isolation_blocks.py). `cold_chemistry` is where the two meet, the
    same way `Dataloader._cold_chemistry` joins them for the run itself.
    """
    if spec.lipid_subclass:
        # The third naming of the same axis (dataloader/lipid_subclass_blocks.py): one
        # or more Titeca-et-al. subclasses, "+"-joined. Without this branch a
        # --lipid_subclass run reconstructs as a RANDOM split -- silently, with an x
        # value belonging to a split the run never used.
        return set(subclass_block_species(spec.lipid_subclass))
    if not spec.lipid_isolation:
        return set()
    species = LIPID_ISOLATION_BLOCKS.get(spec.lipid_isolation)
    if species is None:
        raise ValueError(f"unknown lipid_isolation block: {spec.lipid_isolation}")
    return set(species)


def cold_chemistry(frame, held_classes, held_species):
    """Rows of `frame` carrying chemistry the run holds out, by either naming."""
    held = pandas.Series(False, index=frame.index)
    if held_classes:
        held |= lipid_class_series(frame).str.lower().isin(held_classes)
    if held_species:
        held |= frame["FullIdentityOfLipid"].isin(held_species)
    return held


def held_lipid_classes(csv, spec):
    """The head-group classes that leave training, lower-cased.

    Mirrors `Dataloader._derive_lipid_class_holdout`: a named --lipid_coldsplit set is
    taken as written, while --double_coldsplit/--mixed_coldsplit derive one set per
    held-out family from the FULL table (not the sampled pool) and take the union.
    """
    if spec.lipid_coldsplit:
        classes = LIPID_COLDSPLIT_SETS.get(spec.lipid_coldsplit)
        if classes is None:
            raise ValueError(f"unknown lipid_coldsplit set: {spec.lipid_coldsplit}")
        return {name.lower() for name in classes}
    if not (spec.double_coldsplit or spec.mixed_coldsplit):
        return set()
    chosen = set()
    for group in sorted(spec.excluded_groups):
        classes, _, _ = lipid_classes_for_holdout(csv, group, spec.coldsplit_share)
        chosen.update(name.lower() for name in classes)
    return chosen


def working_set(csv, spec, held_classes, held_species=frozenset()):
    """`PLIDataset.csvt`: every positive plus the sampled negatives, `pair_id` kept.

    `pair_id` is the row's position in `csv` -- the loader's own definition (it reads
    `.index` off a frame that came straight from `pandas.read_csv`), and the key the
    compact Tanimoto row ids are expressed in.
    """
    if spec.hard_negative_mining:
        # --hard_negative_mining reweights the negative draw from the MolFormer species
        # similarity matrix. Reproducing it would mean loading that matrix and matching
        # its RNG draw; nothing analysed here uses it, so refuse rather than return a
        # split that is close but not the run's own.
        raise ValueError("hard_negative_mining splits are not reconstructed here")

    strata = None
    if held_classes or held_species:
        strata = cold_chemistry(csv, held_classes, held_species)

    ratio = spec.negatives_per_positive
    if spec.sampler == "balanced_lipid_classes":
        csvtrue, csvfalse = split_and_sample_lipid_class_balanced_interactions(
            csv, spec.seed, ratio=ratio
        )
    elif spec.sampler == "balanced_proteins":
        csvtrue, csvfalse = split_and_sample_protein_balanced_interactions(
            csv, spec.seed, ratio, strata, None, list(spec.excluded_groups), 0.5
        )
    elif spec.sampler == "balance_negatives_by_family":
        csvtrue, csvfalse = split_and_sample_family_balanced_interactions(
            csv, spec.seed, ratio, strata, None, list(spec.excluded_groups), 0.5
        )
    else:
        csvtrue, csvfalse = split_and_sample_interactions(csv, spec.seed)

    if (
        spec.excluded_groups
        and spec.balance_excluded_group_negatives
        and not (held_classes or held_species)
    ):
        csvfalse = rebalance_excluded_group_negatives(
            csv, csvfalse, list(spec.excluded_groups), spec.seed
        )

    csvtrue = csvtrue.copy()
    csvfalse = csvfalse.copy()
    csvtrue["pair_id"] = csvtrue.index
    csvfalse["pair_id"] = csvfalse.index
    both = pandas.concat([csvtrue, csvfalse])
    return both.set_index(pandas.Index(list(range(len(both)))))


def halve_excluded_block(excluded, seed):
    """(valid, test) from one excluded block, exactly as `_split_interactions` halves it.

    Each label is halved separately, so both halves carry the same positive rate by
    construction -- which is what lets a threshold chosen on validation be read on test.
    """
    positive_validate = excluded[excluded["Interaction"] == 1].sample(
        frac=0.5, random_state=seed
    )
    negative_validate = excluded[excluded["Interaction"] == 0].sample(
        frac=0.5, random_state=seed
    )
    valid = pandas.concat([positive_validate, negative_validate]).sample(
        frac=1, random_state=seed
    )
    test = excluded.drop(valid.index)
    return valid, test


def split_working_set(csvt, spec, held_classes, held_species=frozenset()):
    """train / valid / test frames, mirroring `Dataloader._split_interactions`."""
    if spec.excluded_groups:
        excluded_lower = {group.lower() for group in spec.excluded_groups}
        train = csvt[~csvt["ProteinDomain"].str.lower().isin(excluded_lower)]
    elif spec.excluded_subgroups or spec.lipid_coldsplit or spec.lipid_isolation:
        train = csvt
    else:
        train = csvt.sample(frac=0.85, random_state=spec.seed)

    if spec.excluded_subgroups:
        train = train[~train["LTPProtein"].isin(set(spec.excluded_subgroups))]
    if held_classes or held_species:
        train = train[~cold_chemistry(train, held_classes, held_species)]

    excluded = csvt.drop(train.index)

    if spec.double_coldsplit and (held_classes or held_species):
        in_cold_chemistry = cold_chemistry(excluded, held_classes, held_species)
        if spec.excluded_groups:
            excluded_lower = {group.lower() for group in spec.excluded_groups}
            held_out_protein = excluded["ProteinDomain"].str.lower().isin(excluded_lower)
        elif spec.excluded_subgroups:
            held_out_protein = excluded["LTPProtein"].isin(set(spec.excluded_subgroups))
        else:
            held_out_protein = pandas.Series(True, index=excluded.index)
        excluded = excluded[in_cold_chemistry & held_out_protein]

    if spec.test_group:
        domain_lower = excluded["ProteinDomain"].str.lower()
        test = excluded[domain_lower == spec.test_group.lower()]
        valid = excluded[domain_lower != spec.test_group.lower()]
        return train, valid, test

    valid, test = halve_excluded_block(excluded, spec.seed)
    return train, valid, test


def build_split(csv, spec):
    """(train, valid, test) as arrays of ORIGINAL interaction-table row ids.

    --family_only is the one axis that renumbers: the loader filters the table down to
    one family and calls `reset_index(drop=True)` (Dataloader.py's own comment explains
    why it must), so from there on `pair_id` counts positions inside the family, not
    rows of the full table. The original ids are kept here and mapped back at the end,
    because the compact Tanimoto artifacts are indexed by the full table's rows.
    """
    frame = csv
    original_rows = None
    if spec.family_only:
        frame = csv[csv["ProteinDomain"].str.lower() == spec.family_only.lower()]
        original_rows = frame.index.to_numpy()
        frame = frame.reset_index(drop=True)

    held_classes = held_lipid_classes(frame, spec)
    held_species = held_lipid_species(spec)
    csvt = working_set(frame, spec, held_classes, held_species)
    train, valid, test = split_working_set(csvt, spec, held_classes, held_species)

    def rows(part):
        ids = part["pair_id"].to_numpy(dtype=np.int64)
        return ids if original_rows is None else original_rows[ids]

    return (rows(train), rows(valid), rows(test)), (train, valid, test)


def block_geometry(compact, train_rows, held_rows):
    """Both similarity readings of one held-out block against training.

    `isolation` is the report's own number (mean of the maxima,
    analysis/coldsplit_geometry.isolation); `cross_mean` is the plain mean over all
    cross pairs, which is what tanimoto_group_analysis/ reported for protein groups.
    They answer different questions -- "is there a relative left in training" versus
    "how similar is the chemistry on average" -- and disagree most exactly where a
    block has a few close relatives and many distant ones, so both are carried.
    """
    held = structures_of_rows(compact, held_rows)
    kept = structures_of_rows(compact, train_rows)
    if not len(held) or not len(kept):
        return {
            "isolation": float("nan"),
            "cross_mean": float("nan"),
            "block_structures": int(len(held)),
            "train_structures": int(len(kept)),
        }
    block = np.asarray(compact.matrix[np.ix_(held, kept)], dtype=np.float32) / 255.0
    return {
        "isolation": float(block.max(axis=1).mean()),
        "cross_mean": float(block.mean()),
        "block_structures": int(len(held)),
        "train_structures": int(len(kept)),
    }


_PROTEIN_FEATURE_CACHE = {}


def protein_similarity(proteins, names):
    """Protein x protein RBF similarity over the pocket descriptors `names`.

    The same construction the Kron-RLS protein kernel uses
    (training.pair_baseline_common.build_protein_kernel's "pocket_subset" branch with
    kernel_type="rbf"): standardize the descriptor columns, then
    exp(-||a-b||^2 / (2 * d)) with d the number of descriptors, so the width does not
    move when the set does and two labels with different-sized sets are still on one
    scale. 1.0 on the diagonal, falling toward 0 as pockets differ.

    Standardized over ALL 35 proteins rather than over a split's training proteins --
    deliberately, and differently from build_protein_kernel, which standardizes on train
    only. Here the number is an x AXIS shared by every point of a curve: if each block's
    similarity were computed in its own standardization, two blocks' x values would be
    measured with two different rulers and the curve between them would not mean
    anything. Nothing is fitted on it, so there is no leak to avoid.
    """
    if resolve_protein_feature_subset is None:
        raise ValueError(
            "the protein axis needs training.pair_baseline_common, which did not import "
            "on this machine (rdkit/scipy missing?) -- the lipid axis still works"
        )
    key = (tuple(proteins), tuple(names))
    cached = _PROTEIN_FEATURE_CACHE.get(key)
    if cached is not None:
        return cached
    features = resolve_protein_feature_subset(list(proteins), list(names))
    matrix = features.to_numpy(dtype=float)
    matrix = (matrix - matrix.mean(axis=0)) / np.clip(matrix.std(axis=0), 1e-12, None)
    squared = (
        (matrix ** 2).sum(axis=1)[:, None]
        + (matrix ** 2).sum(axis=1)[None, :]
        - 2.0 * matrix @ matrix.T
    )
    similarity = np.exp(-np.clip(squared, 0.0, None) / (2.0 * max(matrix.shape[1], 1)))
    index = {name: position for position, name in enumerate(features.index)}
    _PROTEIN_FEATURE_CACHE[key] = (similarity, index)
    return similarity, index


def protein_block_geometry(similarity, index, train_proteins, held_proteins):
    """The lipid curve's own statistic, on the protein axis.

    isolation = mean over the block's PROTEINS of the highest similarity to any protein
    that stayed in training -- the same "is there a relative left in training" reading
    block_geometry applies to lipid structures, so the two axes are read the same way
    and a figure can put them side by side.

    Under every lipid-side axis (--lipid_coldsplit / --lipid_isolation /
    --lipid_subclass) this is 1.0 by construction: every protein stays in training, and
    each one is its own nearest relative. That is not a defect of the measurement, it is
    the statement that those runs hold nothing out on this axis -- and it is why a
    protein-axis curve is read on --excluded_groups / --cold_split labels.
    """
    held = [index[name] for name in held_proteins if name in index]
    kept = [index[name] for name in train_proteins if name in index]
    if not held or not kept:
        return {
            "protein_isolation": float("nan"),
            "protein_cross_mean": float("nan"),
            "block_proteins": len(held),
            "train_proteins": len(kept),
        }
    block = similarity[np.ix_(held, kept)]
    return {
        "protein_isolation": float(block.max(axis=1).mean()),
        "protein_cross_mean": float(block.mean()),
        "block_proteins": len(held),
        "train_proteins": len(kept),
    }


def measure_split(csv, compact, spec):
    """Every geometric property of one run's split; cached by the caller."""
    (train_rows, valid_rows, test_rows), (train, valid, test) = build_split(csv, spec)
    measurement = {
        "axis": spec.axis,
        "train_rows": len(train),
        "valid_rows": len(valid),
        "test_rows": len(test),
        "test_positives": int(test["Interaction"].sum()) if len(test) else 0,
        "test_positive_rate": (
            float(test["Interaction"].mean()) if len(test) else float("nan")
        ),
        "test_proteins": int(test["LTPProtein"].nunique()) if len(test) else 0,
        "train_positives": int(train["Interaction"].sum()) if len(train) else 0,
    }
    # The share of evaluated rows whose exact lipid species is also in training -- the
    # loader prints the same number as its "lipid prior baseline" line. It is 0 on a
    # lipid cold split and ~1 on a random one, and it is what separates "a new molecule"
    # from "a known molecule against a protein that has not seen it".
    seen = set(train["FullIdentityOfLipid"].unique())
    for name, part, rows in (("test", test, test_rows), ("valid", valid, valid_rows)):
        geometry = block_geometry(compact, train_rows, rows)
        for key, value in geometry.items():
            measurement[f"{name}_{key}"] = value
        measurement[f"{name}_seen_lipid_share"] = (
            float(part["FullIdentityOfLipid"].isin(seen).mean())
            if len(part)
            else float("nan")
        )
    # The protein axis. Computed over every protein in the table, so a block whose
    # proteins all stayed in training reads 1.0 rather than going missing.
    #
    # Filled with NaN rather than raised when the protein kernel is unavailable: this
    # module is meant to run on a machine that has a metrics table and nothing else
    # (see the torch stand-in at the top), and the LIPID axis needs none of what the
    # protein axis needs. Asking for --x test_protein_isolation there still fails, with
    # protein_similarity's own message.
    train_proteins = set(train["LTPProtein"].dropna().unique())
    try:
        similarity, index = protein_similarity(
            sorted(csv["LTPProtein"].dropna().unique()), spec.protein_descriptors
        )
    except (ValueError, OSError, FileNotFoundError, ImportError):
        similarity = index = None
    for name, part in (("test", test), ("valid", valid)):
        geometry = (
            protein_block_geometry(
                similarity, index, train_proteins,
                set(part["LTPProtein"].dropna().unique()),
            )
            if similarity is not None
            else {
                "protein_isolation": float("nan"),
                "protein_cross_mean": float("nan"),
                "block_proteins": int(part["LTPProtein"].nunique()) if len(part) else 0,
                "train_proteins": len(train_proteins),
            }
        )
        for key, value in geometry.items():
            measurement[f"{name}_{key}"] = value
    measurement["protein_descriptors"] = ",".join(spec.protein_descriptors)
    return measurement


def load_compact_checked(data_dir, csv, source_csv):
    """The compact Tanimoto artifacts, accepted only if they match THIS table.

    `load_compact`'s own guard compares the source table's size and nanosecond mtime
    against the manifest, which is the cheap proxy for "were these similarities computed
    for this candidate list". The proxy has a false positive that costs a whole analysis:
    a table copied or re-synced without being edited keeps its bytes and loses its mtime,
    and the artifacts are then refused although they describe it exactly.

    So when the proxy fails, the real question is asked instead of skipped:

      * every row of the table appears among the candidate row ids, and no id points
        past the table -- a table that gained, lost or reordered rows fails here;
      * the structure index is as long as the row ids and indexes the matrix exactly;
      * and, when rdkit is importable, the candidate list is re-derived from the table
        with the builder's OWN function (preprocessing/build_tanimoto_matrix.collect,
        the same one that wrote the files) and required to be identical, row id for row
        id and structure for structure. That is a stronger statement than the mtime
        ever made.

    Loud either way: the run's own output says which check passed, because "the numbers
    were computed against artifacts whose manifest did not match" is exactly the kind of
    thing a later reader has to be able to see.
    """
    compact = load_compact(data_dir, source_csv=source_csv)
    if compact is not None:
        return compact

    compact = load_compact(data_dir)
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts are missing or unreadable; rebuild them with "
            "preprocessing/build_tanimoto_compact.py"
        )

    covered = np.unique(compact.row_ids)
    structure_index = compact.structure_index
    if (
        len(covered) != len(csv)
        or covered[0] != 0
        or covered[-1] != len(csv) - 1
        or len(structure_index) != len(compact.row_ids)
        or int(structure_index.max()) + 1 != compact.matrix.shape[0]
    ):
        raise SystemExit(
            "the compact Tanimoto artifacts were built for a different table "
            f"({len(covered)} rows covered against {len(csv)} in the table); rebuild "
            "them with preprocessing/build_tanimoto_compact.py"
        )

    print(
        "compact Tanimoto manifest does not match the table's mtime; verifying by "
        "content instead"
    )
    try:
        from preprocessing.build_tanimoto_matrix import collect
    except Exception as error:  # rdkit is absent on analysis machines
        print(
            f"  rdkit unavailable ({error.__class__.__name__}), so the check is "
            f"structural only: {len(covered)} rows covered exactly, "
            f"{len(compact.row_ids)} candidates over {compact.matrix.shape[0]} "
            "structures"
        )
        return compact

    smiles, row_ids = collect(csv, isomeric=False)
    order = {}
    rebuilt_index = []
    for item in smiles:
        if item not in order:
            order[item] = len(order)
        rebuilt_index.append(order[item])
    same = (
        len(row_ids) == len(compact.row_ids)
        and bool((row_ids == compact.row_ids).all())
        and bool((np.asarray(rebuilt_index) == structure_index).all())
    )
    if not same:
        raise SystemExit(
            "the compact Tanimoto artifacts describe a different candidate list than "
            "this table produces; rebuild them with "
            "preprocessing/build_tanimoto_compact.py"
        )
    print(
        f"  candidate list re-derived with the builder's own rule and identical: "
        f"{len(row_ids)} candidates, {len(order)} distinct structures"
    )
    return compact


def latest_rows(table_path, labels, metrics):
    """Latest metrics row per (label, exclusion_set, seed), for the requested labels.

    Matching is the project's own convention (analysis/AGENTS.md): (label,
    exclusion_set, seed). A rerun of the same triple replaces the earlier row rather
    than being averaged with it.
    """
    keep = {}
    with open(table_path, newline="") as handle:
        for row in csv_module.DictReader(handle):
            label = row.get("label", "")
            if labels and label not in labels:
                continue
            # A derived metric has no column of its own, so "is this row populated"
            # has to be asked of what it is derived FROM -- otherwise a request for
            # the confusion panels alone would discard every row in the table.
            if not any(
                derived_metric(row, metric) is not None
                if metric in CONFUSION_SHARE_METRICS
                else str(row.get(metric, "")).strip()
                for metric in metrics
            ):
                continue
            key = (label, row.get("exclusion_set", ""), row.get("seed", ""))
            previous = keep.get(key)
            if previous is None or row.get("datetime", "") >= previous.get("datetime", ""):
                keep[key] = row
    return keep


def aggregate(points, metrics):
    """Mean and deviation over the seeds of one (curve, exclusion set).

    Keyed on the CURVE rather than on the label, because one curve can be measured by
    two labels: a configuration's cold-split arg file and its `--random_split` sibling
    differ by exactly one line, so the random block is the same configuration at the far
    end of the same axis, not a different model. The blocks they contribute are disjoint
    ("random" against the cold blocks), so pooling them cannot merge two measurements of
    one block.
    """
    grouped = defaultdict(list)
    for point in points:
        grouped[(point["curve"], point["exclusion_set"])].append(point)
    aggregated = []
    for (curve, exclusion_set), rows in sorted(grouped.items()):
        entry = {
            "curve": curve,
            "label": rows[0]["label"],
            "exclusion_set": exclusion_set,
            "axis": rows[0]["axis"],
            "seeds": len(rows),
            "test_rows": statistics.fmean(row["test_rows"] for row in rows),
            "test_positive_rate": statistics.fmean(
                row["test_positive_rate"] for row in rows
            ),
            "test_proteins": statistics.fmean(row["test_proteins"] for row in rows),
        }
        if len({row["label"] for row in rows}) > 1:
            raise ValueError(
                f"block {exclusion_set} of curve {curve} was measured by more than one "
                "label; the curve would average two configurations into one point"
            )
        for column in (
            "test_isolation",
            "test_cross_mean",
            "test_seen_lipid_share",
            "test_protein_isolation",
            "test_protein_cross_mean",
        ):
            values = [row[column] for row in rows if not math.isnan(row[column])]
            entry[column] = statistics.fmean(values) if values else float("nan")
            entry[f"{column}_std"] = deviation(values)
            entry[f"{column}_sem"] = standard_error(values)
        for metric in metrics:
            values = [row[metric] for row in rows if row.get(metric) is not None]
            entry[metric] = statistics.fmean(values) if values else float("nan")
            # Both, and the figure draws the deviation: the band on every other curve
            # in this project (analysis/plot_group_learning_curve.py) is the spread
            # ACROSS SEEDS, not the precision of their mean, and two figures whose
            # shaded bands mean different things cannot be read side by side.
            entry[f"{metric}_std"] = deviation(values)
            entry[f"{metric}_sem"] = standard_error(values)
        aggregated.append(entry)
    return aggregated


def deviation(values):
    if len(values) < 2:
        return float("nan")
    return statistics.stdev(values)


def standard_error(values):
    if len(values) < 2:
        return float("nan")
    return statistics.stdev(values) / math.sqrt(len(values))


def write_points(path, points, metrics):
    columns = [
        "label",
        "exclusion_set",
        "seed",
        "axis",
        "test_isolation",
        "test_cross_mean",
        "test_seen_lipid_share",
        "test_protein_isolation",
        "test_protein_cross_mean",
        "test_block_proteins",
        "test_train_proteins",
        "protein_descriptors",
        "valid_isolation",
        "valid_cross_mean",
        "valid_seen_lipid_share",
        "valid_protein_isolation",
        "train_rows",
        "valid_rows",
        "test_rows",
        "test_positives",
        "test_positive_rate",
        "test_proteins",
        "train_positives",
        "test_block_structures",
        "test_train_structures",
        *CONFUSION_COUNTS,
        *[metric for metric in metrics if metric not in CONFUSION_COUNTS],
    ]
    with open(path, "w", newline="") as handle:
        writer = csv_module.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore"
        )
        writer.writeheader()
        for point in sorted(
            points, key=lambda item: (item["label"], item["test_isolation"], item["seed"])
        ):
            writer.writerow(point)


X_AXIS_LABELS = {
    "test_isolation": (
        "Tanimoto similarity of the test block to train\n"
        "(mean over block structures of the best similarity to a training structure)"
    ),
    "test_cross_mean": (
        "Tanimoto similarity of the test block to train\n"
        "(plain mean over all block x train structure pairs)"
    ),
    "test_seen_lipid_share": (
        "share of evaluated rows whose exact lipid species is also in training"
    ),
    "test_protein_isolation": (
        "pocket similarity of the test block's proteins to train\n"
        "(mean over block proteins of the best RBF pocket-descriptor similarity\n"
        "to a protein that stayed in training)"
    ),
    "test_protein_cross_mean": (
        "pocket similarity of the test block's proteins to train\n"
        "(plain mean over all block x train protein pairs)"
    ),
}


def plot(aggregated, metrics, path, x_column="test_isolation", title=""):
    """One panel per metric: the curve over the blocks, shaded by its spread over seeds.

    Points only -- which block each one is is in the CSV written beside the figure, and
    on the protein axis six of the seven blocks sit within 0.78-0.86, where their names
    printed on the plot cover the curve they are meant to explain.

    Drawn the way every other curve in this project is drawn
    (analysis/plot_group_learning_curve.py): a solid line in the project's red with a
    band at mean +/- one standard deviation over the seeds behind it, so a reader who
    already knows those figures reads this one without being told. The band is the
    deviation, not the standard error of the mean -- same quantity as there.

    Called once per label (the figure lands in that label's own graphics directory), so
    the usual case is one curve; a second label handed to the same call gets the
    project's blue, and further ones fall back to a categorical palette.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = sorted({entry["curve"] for entry in aggregated})
    # The project's own two curve colours first (plot_group_learning_curve.py's
    # validation red and train blue), then a palette for any further series.
    palette = ["#C00000", "#4472C4"]
    extra = plt.get_cmap("tab10")

    def colour_for(index):
        return palette[index] if index < len(palette) else extra((index - len(palette)) % 10)

    # Up to three panels per row. One row was fine while the default was two metrics;
    # with the four confusion shares beside BA and F1 it is six, and a single row would
    # be a 45-inch figure nobody opens.
    columns = min(3, max(1, len(metrics)))
    rows = -(-len(metrics) // columns)
    figure, axes = plt.subplots(
        rows, columns, figsize=(7.5 * columns, 5.5 * rows), squeeze=False
    )
    for index, metric in enumerate(metrics):
        axis = axes[index // columns][index % columns]
        for colour_index, label in enumerate(labels):
            series = [
                entry
                for entry in aggregated
                if entry["curve"] == label
                and not math.isnan(entry[x_column])
                and not math.isnan(entry[metric])
            ]
            series.sort(key=lambda entry: entry[x_column])
            if not series:
                continue
            colour = colour_for(colour_index)
            x_values = [entry[x_column] for entry in series]
            means = [entry[metric] for entry in series]
            # A block run on one seed has no deviation; its band closes to the line
            # rather than opening to nothing, which would break fill_between's polygon.
            deviations = [
                0.0 if math.isnan(entry[f"{metric}_std"]) else entry[f"{metric}_std"]
                for entry in series
            ]
            axis.plot(
                x_values,
                means,
                color=colour,
                linewidth=2,
                marker="o",
                markersize=5,
                label=shorten(label),
            )
            axis.fill_between(
                x_values,
                [mean - value for mean, value in zip(means, deviations)],
                [mean + value for mean, value in zip(means, deviations)],
                color=colour,
                alpha=0.18,
            )
        if metric == "balanced_accuracy":
            axis.axhline(
                0.5,
                color="black",
                linestyle="--",
                linewidth=1.0,
                alpha=0.7,
                label="random = 0.500",
            )
        axis.set_xlabel(X_AXIS_LABELS.get(x_column, x_column))
        if metric in CONFUSION_SHARE_METRICS:
            # Fixed [0, 1] on all four, so the panels can be read against each other --
            # the whole point is the SPLIT of the block between the four cells, and
            # autoscaled axes would make a cell holding 2% of the block look like one
            # holding 60%. The block's own positive rate is the line a share panel is
            # read against (TP+FN is it by construction), so it is drawn where it
            # applies: on the two positive-row panels.
            axis.set_ylim(-0.02, 1.02)
            if metric in ("TP_share", "FN_share"):
                rates = [
                    entry["test_positive_rate"]
                    for entry in aggregated
                    if not math.isnan(entry["test_positive_rate"])
                ]
                if rates:
                    axis.axhline(
                        statistics.fmean(rates),
                        color="black", linestyle=":", linewidth=1.0, alpha=0.7,
                        label="mean positive rate of the blocks",
                    )
            axis.set_ylabel(f"test {metric.removesuffix('_share')} / block rows")
        else:
            axis.set_ylabel(f"test {metric}")
        axis.grid(alpha=0.25)
        # With one curve per figure the series entry just repeats the title, so only
        # the baseline stays in the legend; a comparison figure keeps both.
        handles, texts = axis.get_legend_handles_labels()
        if len(labels) == 1:
            reference = [
                (handle, text)
                for handle, text in zip(handles, texts)
                if text.startswith("random =") or text.startswith("mean positive rate")
            ]
            handles, texts = zip(*reference) if reference else ((), ())
        if handles:
            axis.legend(handles, texts, fontsize=8, loc="best")
    if title:
        figure.suptitle(title, fontsize=9)
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def curve_correlations(aggregated, metrics, x_column):
    """Spearman rho between the x reading and each metric, over one curve's BLOCKS.

    Rank correlation and not Pearson: the question the figure asks is monotone ("does
    the metric fall as the block gets more distant"), the blocks are 4-9 points, and one
    block at an extreme x would set a Pearson slope on its own.

    Computed over the per-block MEANS, so n is the number of blocks, not the number of
    runs -- which is the honest n here: the five seeds of one block are five readings of
    the same point, not five points. With 4 blocks even rho = 1.0 is p = 0.083, so these
    are effect sizes to look at next to the figure, never significance claims; the
    number of blocks is printed beside them for exactly that reason.
    """
    texts = []
    for metric in metrics:
        pairs = [
            (entry[x_column], entry[metric])
            for entry in aggregated
            if not math.isnan(entry[x_column]) and not math.isnan(entry[metric])
        ]
        if len(pairs) < 3:
            texts.append("n/a")
            continue
        xs = [value for value, _ in pairs]
        ys = [value for _, value in pairs]
        texts.append(f"{spearman(xs, ys):+.3f} (n={len(pairs)})")
    return texts


def spearman(xs, ys):
    """Rank correlation, average ranks for ties, without pulling scipy in."""
    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        position = 0
        while position < len(order):
            stop = position
            while stop + 1 < len(order) and values[order[stop + 1]] == values[order[position]]:
                stop += 1
            average = (position + stop) / 2.0 + 1.0
            for index in range(position, stop + 1):
                out[order[index]] = average
            position = stop + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    mean_x, mean_y = statistics.fmean(rx), statistics.fmean(ry)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry))
    denominator = math.sqrt(
        sum((a - mean_x) ** 2 for a in rx) * sum((b - mean_y) ** 2 for b in ry)
    )
    return numerator / denominator if denominator else float("nan")


def shorten(label, width=48):
    return label if len(label) <= width else label[: width - 3] + "..."


def safe_path_part(value):
    """The label as a directory name, by build_metrics_table's own rule.

    Labels reaching metrics_summary.csv are already sanitised by new_train.py, so this
    only guards a hand-edited row -- and it has to use the SAME rule, or the figure
    would land next to `graphics/<label>/` instead of inside it.
    """
    value = re.sub(r"[^A-Za-z0-9._=-]+", "_", str(value).strip()).strip("._")
    return value or "unknown_label"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", default=os.path.join(PROJECT_ROOT, "metrics_summary.csv"))
    parser.add_argument("--data_dir", default=os.path.join(PROJECT_ROOT, "data"))
    parser.add_argument(
        "--labels",
        default="",
        help=(
            "comma-separated labels; every label in the table by default. Several "
            "labels are computed in one call and each gets its own CSV and figure "
            "under graphics/<label>/split_similarity/"
        ),
    )
    parser.add_argument(
        "--curve",
        action="append",
        default=[],
        metavar="LABEL,LABEL",
        help=(
            "comma-separated labels that form ONE curve -- use it to put a "
            "configuration's cold-split arg file and its --random_split sibling on the "
            "same axis, since they differ by one line and the random block is that same "
            "configuration at the warm end. Repeatable. The figure and the point table "
            "are named after the first label and written into EVERY named label's own "
            "graphics directory"
        ),
    )
    parser.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help="test metric columns of metrics_summary.csv, one panel each",
    )
    parser.add_argument(
        "--x",
        default="test_isolation",
        choices=(
            "test_isolation",
            "test_cross_mean",
            "test_seen_lipid_share",
            "test_protein_isolation",
            "test_protein_cross_mean",
        ),
        help=(
            "which similarity reading goes on the x axis. The first three are the LIPID "
            "axis (Tanimoto of the evaluated block's chemistry to training chemistry); "
            "test_protein_isolation is the same statistic on the PROTEIN axis -- mean "
            "over the block's proteins of the highest RBF pocket-descriptor similarity "
            "to a protein that stayed in training. The protein axis is 1.0 by "
            "construction on every lipid-side split, so it is read on "
            "--excluded_groups/--cold_split labels"
        ),
    )
    parser.add_argument(
        "--graphics_root",
        default=os.path.join(PROJECT_ROOT, "graphics"),
        help="figures and point tables go to <graphics_root>/<label>/split_similarity/",
    )
    parser.add_argument(
        "--output_format",
        default="pdf",
        help="figure format, as for analysis/plot_metric_by_subgroup.py",
    )
    arguments = parser.parse_args()

    metrics = [item.strip() for item in arguments.metrics.split(",") if item.strip()]
    labels = {item.strip() for item in arguments.labels.split(",") if item.strip()}

    # Which labels share a curve. A label named in no --curve keeps a curve of its own,
    # which is what every label did before this flag existed.
    curve_members = [
        [item.strip() for item in group.split(",") if item.strip()]
        for group in arguments.curve
    ]
    curve_of_label = {}
    for members in curve_members:
        for member in members:
            if member in curve_of_label:
                raise SystemExit(f"label {member} is named in two curves")
            curve_of_label[member] = members[0]
        labels.update(members)

    data_dir = arguments.data_dir.rstrip(os.sep) + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    compact = load_compact_checked(
        arguments.data_dir, csv, interaction_csv_path(data_dir)
    )

    rows = latest_rows(arguments.table, labels, metrics)
    if not rows:
        raise SystemExit("no rows in the metrics table match those labels and metrics")

    cache = {}
    points = []
    skipped = defaultdict(int)
    for (label, exclusion_set, seed), row in sorted(rows.items()):
        spec = spec_from_row(row)
        try:
            if spec not in cache:
                cache[spec] = measure_split(csv, compact, spec)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        point = {
            "label": label,
            "curve": curve_of_label.get(label, label),
            "exclusion_set": exclusion_set,
            "seed": int(seed),
        }
        point.update(cache[spec])
        # The raw cells travel with the point whether or not a share panel was asked
        # for: the CSV beside the figure is where block size is recoverable, and a
        # share without its denominator cannot be checked.
        for cell in CONFUSION_COUNTS:
            raw = str(row.get(cell, "")).strip()
            try:
                point[cell] = float(raw)
            except (TypeError, ValueError):
                point[cell] = None
        for metric in metrics:
            value = derived_metric(row, metric)
            if value is not None:
                point[metric] = value
                continue
            raw = str(row.get(metric, "")).strip()
            try:
                point[metric] = float(raw)
            except (TypeError, ValueError):
                point[metric] = None
        if all(point[metric] is None for metric in metrics):
            continue
        points.append(point)

    if not points:
        raise SystemExit("no run could be matched to a reconstructed split")

    # One curve, one directory per label that measured it -- the project's graphics
    # layout (graphics/<label>/<kind>/<label>_<what>,
    # scripts/generate_config_graphics.sh). A curve carried by two labels is written
    # into both, so opening either configuration's directory shows the whole curve
    # rather than the half that label happened to run.
    #
    # Several curves are still computed in ONE pass: the expensive part is rebuilding
    # the splits, and `cache` is keyed on the split rather than on the label, so two
    # configurations that ran the same blocks on the same seeds pay for them once.
    by_curve = defaultdict(list)
    for point in points:
        by_curve[point["curve"]].append(point)

    written = []
    for curve, curve_points in sorted(by_curve.items()):
        aggregated = aggregate(curve_points, metrics)
        axis_names = ", ".join(sorted({entry["axis"] for entry in aggregated}))
        members = sorted({point["label"] for point in curve_points})
        stem = safe_path_part(curve)
        paths = []
        for member in members:
            directory = os.path.join(
                arguments.graphics_root, safe_path_part(member), "split_similarity"
            )
            os.makedirs(directory, exist_ok=True)
            points_path = os.path.join(
                directory, f"{stem}_split_similarity_points.csv"
            )
            write_points(points_path, curve_points, metrics)
            figure_path = os.path.join(
                directory,
                f"{stem}_split_similarity_vs_metric.{arguments.output_format}",
            )
            # Per metric, not per point: a run from before AUC_within_protein existed
            # has that column empty and the other two filled, and dropping the whole
            # point would quietly shrink the curve of every metric to the intersection
            # of all of them.
            plot(
                aggregated,
                metrics,
                figure_path,
                arguments.x,
                f"{curve}  [{axis_names}]",
            )
            paths.extend((points_path, figure_path))
        written.append((curve, aggregated, paths))

    header = f"{'block':22s} {'axis':18s} {'seeds':>5s} {'x':>7s}"
    for curve, aggregated, paths in written:
        print(f"\n=== {curve} ===")
        print(header + "".join(f" {metric:>22s}" for metric in metrics))
        for entry in sorted(aggregated, key=lambda item: item[arguments.x]):
            line = (
                f"{entry['exclusion_set'][:22]:22s} {entry['axis']:18s} "
                f"{entry['seeds']:5d} {entry[arguments.x]:7.3f}"
            )
            for metric in metrics:
                line += f" {entry[metric]:10.3f} +/- {entry[f'{metric}_sem']:7.3f}"
            print(line)
        correlations = curve_correlations(aggregated, metrics, arguments.x)
        if correlations:
            print(
                f"{'Spearman rho vs x':22s} {'':18s} {len(aggregated):5d}    n/a"
                + "".join(f" {text:>22s}" for text in correlations)
            )
        for written_path in paths:
            print(f"wrote {written_path}")
    for reason, count in skipped.items():
        print(f"skipped {count} runs: {reason}")


if __name__ == "__main__":
    main()
