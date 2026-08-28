#!/usr/bin/env python3
"""How much a chemistry-only feature set already *is* identity, in a few cheap numbers.

Generalises preprocessing/pocket_descriptor_identity_check.py's method (eta^2 +
leave-one-out nearest-neighbour identity rate, each read against its own chance floor,
plus a permutation significance test) from "protein pocket descriptors vs protein
family" to any --features set analysis/null_model.py accepts, against every identity
axis that granularity can see: which lipid SPECIES, which lipid CLASS (head group),
which PROTEIN, and which protein FAMILY (ProteinDomain).

Why this question, before a network is trained. The project's recurring failure mode
(files/signal_state.md; project memory descriptors-path-fingerprint-leak,
working-triple-explains-protein-wins) is not "the network scores badly" but "the
network scores well by keying on identity instead of chemistry", which then fails to
transfer to an unseen protein-lipid pair. Training a network and reading its
cold-split collapse is the expensive way to discover that a given --features set
enables that shortcut. This script answers the cheaper, prior question straight from
the feature vectors themselves: does this descriptor set, entirely on its own, already
determine identity? A set that does is a candidate fingerprint regardless of what any
particular network ends up doing with it.

Two report sections.

GLOBAL -- whole dataset, every entity against every other entity of the same kind:

  1. eta^2, joint and per-entry. `joint eta^2` is the headline number: share of the
     WHOLE standardised vector's variance (every descriptor entry at once, not one at
     a time) that sits between identity groups rather than within them -- the direct
     answer to "does this descriptor SET, combined, determine identity", since a
     handful of individually-weak entries can jointly pin identity down (or a single
     strong entry can dominate the per-entry view while contributing little once the
     others are accounted for). The per-entry breakdown underneath names which single
     entries the joint number is built from, same as before: near 1, that one entry
     alone says which [species / class / protein / family] and nothing else. A split
     of k groups over n entities has an arithmetic floor of (k-1)/(n-1) even for a
     column (or the whole vector) with no identity structure at all (printed
     alongside) -- a score at the floor carries no identity information whatever the
     bar length suggests.

  2. Nearest-other-entity-shares-identity rate -- leave-one-out: for each entity, does
     its single nearest OTHER entity (by the same standardised-euclidean similarity
     dataloader.chemistry_prior's null model itself ranks by) share its identity? Read
     against the rate a same-sized random draw would give by chance, and against a
     label-permutation p-value (entity labels reshuffled `--permutations` times,
     nearest-neighbour structure held fixed -- it depends only on the vectors, not the
     labels -- so each reshuffle costs one O(entities) pass, not a matrix rebuild).

TRAIN vs VALID+TEST (--families/--seeds/--share/--ratio, exactly
analysis/null_model.py's own --double_coldsplit machinery, VALID and TEST pooled
together) -- NOT an identity-match test. preprocessing/lipid_marginal_baseline.split
removes a held-out family's protein rows, and that family's held-out classes' lipid
rows, from TRAIN UNCONDITIONALLY (every protein, not just the held family's own) --
so no TRAIN row can ever carry the exact identity label a VALID+TEST row carries, by
the split's own construction. An identity-match rate there would read 0.0 for every
--features set on every family, always -- the split working as designed, not a
measurement. What the split does NOT rule out, and what this section reports
instead, is a VALID+TEST row's vector sitting unusually CLOSE to one particular
TRAIN row despite carrying no shared label: `best_match` is a VALID+TEST row's own
highest similarity to any single TRAIN row, `avg_similarity` its average similarity
to TRAIN generally, and `standout_gap` the difference -- a row with a standout
near-match in TRAIN has the same shape of shortcut an identity-match would have
caught, had the split allowed
one to exist at all.

--features tanimoto (the whole-molecule Morgan-fingerprint case) has no named columns
to break eta^2 down by, so only the nearest-neighbour rate is reported for it -- a
ceiling reading of how separable raw chemical structure alone already makes lipid
identity, the same role preprocessing/pocket_descriptor_identity_check.py's mean-ESM3
embedding plays for protein identity.

    python3 analysis/feature_identity_check.py
    python3 analysis/feature_identity_check.py --features chain,unsaturation,hbond,heavy
    python3 analysis/feature_identity_check.py --features pocket_extent,ev14_q50,depth_q10
    python3 analysis/feature_identity_check.py --features occupancy,hbond_match,volume_fit
    python3 analysis/feature_identity_check.py --features occupancy,hbond_match --families GLTP,scp2 --seeds 0,1

Reads only. Trains nothing, appends to no shared table.
"""
import argparse
import os
import re
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from dataloader.chemistry_prior import (  # noqa: E402
    LIPID_DESCRIPTOR_NAMES, PAIR_DESCRIPTOR_NAMES, _standardised_similarity,
    raw_feature_matrix, species_similarity,
)
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pair_descriptors import MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES  # noqa: E402
from dataloader.sampler import lipid_class_series  # noqa: E402

# The same coldsplit machinery analysis/null_model.py itself uses for its (family,
# seed) held-out blocks, reused rather than reimplemented so a block reproduced here
# is provably the same rows a null-model/network run would see -- working_set/
# split_func/lipid_classes_for_holdout/DEFAULT_FAMILIES are plain re-exports on
# null_model's own module namespace (see its own imports), not analysis specific to
# the null model itself, so importing them here does not pull in anything about
# scoring the network.
from analysis.null_model import (  # noqa: E402
    DEFAULT_FAMILIES, lipid_classes_for_holdout, split_func, working_set,
)
# REPRESENTATIONS (directory/suffix/trim per learned protein representation) and
# mean_pooled (the loader that reads and residue-averages them) are protein_
# representation_identity_check.py's own -- reused rather than reimplemented so
# "one vector per protein" here is exactly the vector that script already measured
# ESM3 collapsing to one point on, not a second, possibly-diverging recipe.
from protein_representation_identity_check import (  # noqa: E402
    REPRESENTATIONS, mean_pooled,
)

# Same reserved value as analysis/null_model.py's own TANIMOTO -- kept as a separate
# literal rather than an import so the --features default here needs nothing beyond
# dataloader.chemistry_prior itself.
TANIMOTO = "tanimoto"

# --features ESM3 / ESMIF1 / PROTEINMPNN: the user's own spelling (no hyphen, no
# case-sensitivity to remember) mapped onto REPRESENTATIONS' actual keys ("ESM-IF1",
# "ProteinMPNN" carry punctuation/casing that would be an awkward CLI token).
PROTEIN_EMBEDDING_ALIASES = {
    name.upper().replace("-", ""): name for name in REPRESENTATIONS
}


def eta_squared(values, labels):
    """Share of `values`' variance across all entities that lies between groups of
    `labels`, rather than within them -- preprocessing/pocket_descriptor_identity_
    check.py's own eta_squared, unchanged.
    """
    values = np.asarray(values, dtype=float)
    grand_mean = values.mean()
    total = ((values - grand_mean) ** 2).sum()
    if total <= 0:
        return float("nan")
    between = 0.0
    for label in pandas.unique(labels):
        group = values[labels == label]
        between += len(group) * (group.mean() - grand_mean) ** 2
    return float(between / total)


def eta_squared_joint(matrix, labels):
    """Whole-vector generalisation of eta_squared: share of the STANDARDISED
    descriptor matrix's total sum-of-squares -- summed across every column at once,
    not one column at a time -- that lies between identity groups rather than within
    them.

    Per-column eta_squared can only say "this one entry, on its own, tracks
    identity"; several entries can each look weak alone while their COMBINATION still
    pins identity down almost exactly (or the reverse: one entry can dominate the
    per-column bars while contributing little once the others are accounted for).
    This is the same variance-decomposition idea eta_squared already uses, just
    applied to the joint standardised vector instead of one raw column, so the same
    group_floor baseline still applies unchanged.

    Standardised first (mean 0, std 1 per column) so a column with a larger native
    scale cannot dominate the combined sum-of-squares purely by unit choice -- the
    same reason dataloader.chemistry_prior._standardised_similarity standardises
    before it ever compares columns to each other.
    """
    matrix = np.asarray(matrix, dtype=float)
    std = matrix.std(axis=0)
    std = np.where(std > 1e-9, std, 1.0)
    standardised = (matrix - matrix.mean(axis=0)) / std
    grand_mean = standardised.mean(axis=0)
    total = ((standardised - grand_mean) ** 2).sum()
    if total <= 0:
        return float("nan")
    between = 0.0
    for label in pandas.unique(labels):
        group = standardised[labels == label]
        diff = group.mean(axis=0) - grand_mean
        between += len(group) * (diff ** 2).sum()
    return float(between / total)


def group_floor(labels):
    """Arithmetic eta^2 floor for a label split carrying no real identity structure:
    splitting n points into k groups puts (k-1)/(n-1) of the variance between the
    groups by arithmetic alone, whatever the values are.
    """
    n = len(labels)
    k = len(pandas.unique(labels))
    return (k - 1) / (n - 1) if n > 1 else float("nan")


def nearest_neighbour_identity_rate(similarity, labels, permutations=999, seed=0):
    """How often an entity's nearest OTHER entity (by `similarity`, already built the
    same way analysis/null_model.py's null model ranks by) shares its `labels` value;
    the rate a same-sized random draw would give by chance; and a label-permutation
    p-value.

    Takes a similarity matrix rather than raw feature vectors so the "pair" (row)
    granularity -- entities in the thousands -- never touches an O(entities^2 x
    descriptors) distance broadcast; `similarity` is already the O(entities^2 +
    entities x descriptors) computation dataloader.chemistry_prior._standardised_
    similarity produces once, upstream of this function.

    The permutation test reshuffles `labels` across entities `permutations` times and
    recomputes the same match rate under each reshuffle -- cheap because `nearest`
    (an index into the OTHER entities, fixed by the vectors alone) is computed once
    and reused for every reshuffle rather than rebuilt.
    """
    labels = np.asarray(labels)
    n = len(labels)
    score = np.array(similarity, dtype=float, copy=True)
    np.fill_diagonal(score, -np.inf)
    nearest = score.argmax(axis=1)
    observed = float((labels[nearest] == labels).mean())
    counts = pandas.Series(labels).value_counts()
    chance = float(np.mean([(counts[label] - 1) / (n - 1) for label in labels]))
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(permutations):
        shuffled = rng.permutation(labels)
        if (shuffled[nearest] == shuffled).mean() >= observed:
            hits += 1
    p_value = (hits + 1) / (permutations + 1)
    return observed, chance, p_value


def species_class_map(csv):
    """{lipid species: head-group class}, dataloader.lipid_classes.lipid_class_series
    applied once per distinct species rather than once per row.
    """
    species = csv[["FullIdentityOfLipid"]].drop_duplicates()
    species = species.assign(lipid_class=lipid_class_series(species))
    return dict(zip(species["FullIdentityOfLipid"], species["lipid_class"]))


def protein_family_map(csv):
    """{protein: family}, majority ProteinDomain of its interaction rows -- same
    recipe preprocessing/pocket_descriptor_identity_check.py's protein_families uses
    (in practice a protein's ProteinDomain is constant across its own rows; the
    majority vote is just insurance against the rare exception silently biasing this
    script's own labels rather than raising).
    """
    return csv.groupby("LTPProtein")["ProteinDomain"].agg(
        lambda values: values.value_counts().index[0]
    ).to_dict()


def block_entities(entity_column, frame):
    """The distinct null-model entities a row-level `frame` (a train/held split) touches.

    entity_column == "pair_id": every row IS its own entity (`pair_id`, the original
    csv index -- see analysis/null_model.py's working_set). Otherwise several rows
    share one entity (a species or a protein), so only the distinct values matter.
    """
    if entity_column == "pair_id":
        return frame["pair_id"].tolist()
    return frame[entity_column].unique().tolist()


def build_axis_labels(entity_column, entities, csv, species_class, protein_family):
    """{axis name: label array aligned to `entities`}, restricted to the axes this
    `entity_column` (feature_similarity's own granularity) can actually vary on --
    see this module's docstring for why the matching fine-grained axis (species at
    lipid granularity, protein at protein granularity) is mechanically degenerate and
    left out rather than printed as a meaningless 1.0.
    """
    if entity_column == "FullIdentityOfLipid":
        return {"lipid_class": np.array([species_class[e] for e in entities])}
    if entity_column == "LTPProtein":
        return {"protein_family": np.array([protein_family[e] for e in entities])}
    rows = csv.loc[entities]  # entity_column == "pair_id": entities are csv.index values
    lipid_class = lipid_class_series(rows).to_numpy()
    protein_family_col = rows["ProteinDomain"].to_numpy()
    return {
        "lipid": rows["FullIdentityOfLipid"].to_numpy(),
        "lipid_class": lipid_class,
        "protein": rows["LTPProtein"].to_numpy(),
        "protein_family": protein_family_col,
        # The pairing itself, not either side alone: a row can share its lipid_class
        # with one held-out row and its protein_family with another without any row
        # sharing BOTH -- this axis is the one a --pair_descriptor_* head actually
        # conditions its whole output on, so it is the one whose identity-leakage
        # this script should not leave unmeasured just because it decomposes into two
        # axes already reported separately.
        "lipid_class_x_protein_family": np.array([
            f"{lc}||{pf}" for lc, pf in zip(lipid_class, protein_family_col)
        ]),
    }


def print_global_report(entity_column, entities, similarity, matrix, column_names,
                         csv, species_class, protein_family, top, permutations):
    axes = build_axis_labels(entity_column, entities, csv, species_class, protein_family)
    print(f"entity granularity: {entity_column}  ({len(entities)} entities)\n")
    print("## GLOBAL -- whole dataset ##\n")
    summary_rows = []
    eta2_by_axis = {}
    for axis_name, labels in axes.items():
        n = len(labels)
        groups = len(pandas.unique(labels))
        floor = group_floor(labels)
        rate, chance, p_value = nearest_neighbour_identity_rate(
            similarity, labels, permutations=permutations
        )
        joint = eta_squared_joint(matrix, labels) if matrix is not None else float("nan")
        summary_rows.append({
            "axis": axis_name, "groups": groups, "entities": n, "eta2_floor": floor,
            "joint_eta2": joint, "nn_rate": rate, "nn_chance": chance, "nn_p": p_value,
        })
        if matrix is not None:
            eta2_by_axis[axis_name] = [eta_squared(matrix[:, i], labels) for i in range(matrix.shape[1])]

    if matrix is None:
        print("(no named per-descriptor breakdown for tanimoto -- whole-molecule fingerprint)\n")
    else:
        print("=== eta^2 per descriptor, one column per axis ===")
        eta2_table = pandas.DataFrame(eta2_by_axis, index=column_names)
        eta2_table["mean"] = eta2_table.mean(axis=1)
        eta2_table = eta2_table.sort_values("mean", ascending=False).head(top)
        print(eta2_table.round(3).to_string())
        print()

    print("=== summary, all axes ===")
    pandas.set_option("display.width", 200)
    summary = pandas.DataFrame(summary_rows).set_index("axis")
    print(summary.round(3).to_string())
    print()


def rank_pair_descriptors(csv, data_dir, descriptor_names, zscore):
    """One row per PAIR descriptor: how lopsidedly it leaks identity, and how much of
    the combined-identity axis it explains beyond either single axis alone.

    Each descriptor is fetched and scored ON ITS OWN (raw_feature_matrix([name])), so
    every row of the table answers "if this were the only pair descriptor in
    --features, what would GLOBAL's own eta^2 table say" -- the same numbers
    print_global_report would show one descriptor at a time, just collected so they
    can be sorted and compared directly instead of read off separate runs.

    `imbalance` = |eta2(lipid) - eta2(protein)|: near 0 means the descriptor leans on
    lipid and protein identity about equally (or on neither); large means it is
    mostly one or the other -- a descriptor built to encode COMPATIBILITY should not
    be dominated by either side's identity alone.

    `excess_pair` = eta2(lipid_class x protein_family) - max(eta2(lipid_class),
    eta2(protein_family)): the combined axis's eta^2 minus whichever single COARSE
    axis already explains more on its own. Near 0 means the pair axis adds nothing a
    single axis did not already say; positive means the descriptor genuinely responds
    to the PAIRING itself, not just to one side -- the part worth keeping. This is
    read against the coarse axes (lipid_class/protein_family), not the fine ones
    (lipid/protein), on purpose: a descriptor tracking identity down to the exact
    protein or exact lipid species will never generalise to an unseen one regardless
    of how this number reads, so `imbalance` is still the first thing to check.
    """
    species_class = species_class_map(csv)
    protein_family = protein_family_map(csv)
    rows = []
    for name in descriptor_names:
        entities, matrix, entity_column, _ = raw_feature_matrix(csv, data_dir, [name], zscore=zscore)
        axes = build_axis_labels(entity_column, entities, csv, species_class, protein_family)
        values = matrix[:, 0]
        rows.append({
            "descriptor": name,
            **{axis_name: eta_squared(values, labels) for axis_name, labels in axes.items()},
        })
    table = pandas.DataFrame(rows).set_index("descriptor")
    table["imbalance"] = (table["lipid"] - table["protein"]).abs()
    table["excess_pair"] = table["lipid_class_x_protein_family"] - table[
        ["lipid_class", "protein_family"]
    ].max(axis=1)
    return table.sort_values("imbalance", ascending=False)


def coldsplit_report(csv, entity_column, index, similarity, families, seeds,
                      share, ratio):
    """VALID and TEST pooled into one set before comparing against TRAIN --
    analysis/null_model.py's own --split keeps them apart because it is scoring one
    particular network's checkpoint against one particular half, but the two halves
    are the same random 50/50 draw from the same excluded rows (see
    preprocessing/lipid_marginal_baseline.split), not two different populations, and
    this script has no checkpoint to match either half to -- so there is nothing to
    lose and a bigger, steadier sample to gain by using both together.
    Not an identity-match test -- see this module's own docstring (TRAIN vs
    VALID+TEST section) for why one is structurally impossible under this project's
    split, and for what best_match/avg_similarity/standout_gap mean instead.
    """
    print("## TRAIN vs VALID+TEST ##\n")
    # best_match: one value per VALID+TEST row (that row's own max similarity to any
    # TRAIN row), pooled across every seed of a family. similarity_values: every
    # individual pairwise similarity in the VALID+TEST x TRAIN matrix, pooled the same
    # way -- avg_similarity's mean/median/std are read off THIS raw pool, not off the
    # per-row averages, so std reflects how spread out actual similarity values are,
    # not how spread out a small number of per-row (or per-seed) means are.
    by_family = {family: {"best_match": [], "similarity_values": []} for family in families}
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, ratio, held_classes)
            train, valid, test = split_func(csvt, family, seed, held_classes, double=True)
            evaluated = pandas.concat([valid, test])

            evaluated_entities = block_entities(entity_column, evaluated)
            train_entities = block_entities(entity_column, train)
            if not evaluated_entities or not train_entities:
                continue
            evaluated_pos = [index[e] for e in evaluated_entities]
            train_pos = [index[e] for e in train_entities]
            sub = np.asarray(similarity[np.ix_(evaluated_pos, train_pos)], dtype=float)
            by_family[family]["best_match"].append(sub.max(axis=1))
            by_family[family]["similarity_values"].append(sub.ravel())

    family_rows = {}
    pooled_best_match, pooled_similarity = [], []
    for family, columns in by_family.items():
        if not columns["best_match"]:
            continue
        best_match = np.concatenate(columns["best_match"])
        similarity_values = np.concatenate(columns["similarity_values"])
        family_rows[family] = {
            "best_match": float(best_match.mean()),
            "avg_similarity": float(similarity_values.mean()),
            "median": float(np.median(similarity_values)),
            "std": float(similarity_values.std()),
        }
        pooled_best_match.append(best_match)
        pooled_similarity.append(similarity_values)

    if not family_rows:
        print("(no family/seed reached at least 1 evaluated row and 1 train row -- nothing to report)")
        return
    pandas.set_option("display.width", 200)
    print("=== per family (all seeds pooled) ===")
    print(pandas.DataFrame(family_rows).T.round(3).to_string())
    print()

    print("=== all families pooled ===")
    best_match_all = np.concatenate(pooled_best_match)
    similarity_all = np.concatenate(pooled_similarity)
    print(f"best_match             mean={best_match_all.mean():.3f}")
    print(
        f"avg_similarity         mean={similarity_all.mean():.3f}  "
        f"median={np.median(similarity_all):.3f}  std={similarity_all.std():.3f}"
    )
    print()


COARSE_TOKEN = re.compile(r"^(?P<base>.+)_coarse=(?P<k>\d+)$")
NEUTRAL_TOKEN = re.compile(r"^(?P<base>.+)_neutral$")
ZSCORE_TOKEN = re.compile(r"^(?P<base>.+)_zscore$")


def parse_feature_tokens(features_arg):
    """--features string -> (base_names, specs).

    A token "<name>_coarse=<K>" means: fetch the named descriptor's RAW values (any
    lipid/protein/pair name raw_feature_matrix knows -- whether or not it already has
    its own project "coarse" variant; dataloader.pair_descriptors' aromatic_share_
    coarse/polar_share_coarse are hand-picked FIXED bands over a share already known
    to live in [0, 1], which does not generalise to a descriptor with a different
    native scale, e.g. depth_bulk_match) and quantile-bin it into K groups instead of
    using the raw value -- see apply_coarsening.

    A token "<name>_neutral" means: subtract that descriptor's own per-protein mean
    and per-lipid_class mean (two-way de-meaning, the same residual analysis/
    null_model.py's per_pair_auc already computes post-hoc for a score) so what is
    left is only what depends on BOTH the protein and the lipid, not "this protein"
    or "this lipid class" alone -- see resolve_pair_broadcast_features/
    neutralize_row_values.

    A token "<name>_zscore" means: standardise the protein-side and lipid-side raw
    values EACH ON THEIR OWN SCALE, over the full protein/lipid descriptor tables
    (every protein this project has pocket geometry for, every lipid it has
    chemistry for -- never row- or split-restricted, so this is well-defined for a
    protein or lipid that has never appeared in train), before combining them into
    `name` -- exactly dataloader.chemistry_prior.feature_similarity's own --zscore,
    now selectable per token instead of one flag applied to the whole --features set
    at once. Valid only for `name` in MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES: outside
    that set the underlying mechanism either has no effect (occupancy/
    chain_extent_gap/tail_elongation_fit are deliberately excluded -- an angstrom-vs-
    angstrom or shape-ratio comparison, not a product two different native scales
    could unbalance) or is already unconditionally on (aromatic_contact_min/
    hbond_match_min) -- raised here rather than silently accepted as a no-op, so a
    "_zscore" token that would not change anything is never mistaken for one that did.

    Any other token is used as-is, exactly like today.

    `base_names`: the underlying descriptor names to actually ask raw_feature_matrix
    for, de-duplicated, first-seen order. `specs`: one entry per --features token, in
    the ORIGINAL order, each ("raw", token, token, None), ("coarse", token, base, k),
    ("neutral", token, base, None), or ("zscore", token, base, None).
    """
    base_names = []
    specs = []
    for token in features_arg.split(","):
        token = token.strip()
        if not token:
            continue
        coarse_match = COARSE_TOKEN.match(token)
        neutral_match = NEUTRAL_TOKEN.match(token)
        zscore_match = ZSCORE_TOKEN.match(token)
        if coarse_match:
            base = coarse_match.group("base")
            specs.append(("coarse", token, base, int(coarse_match.group("k"))))
        elif neutral_match:
            base = neutral_match.group("base")
            specs.append(("neutral", token, base, None))
        elif zscore_match:
            base = zscore_match.group("base")
            if base not in MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES:
                raise ValueError(
                    f"'{token}': _zscore has no defined effect on '{base}' -- only "
                    f"{', '.join(MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES)} respond to it "
                    "(everything else in PAIR_DESCRIPTOR_NAMES is either never "
                    "standardised, by design, or always standardised regardless of "
                    "this flag -- see parse_feature_tokens' own docstring)."
                )
            specs.append(("zscore", token, base, None))
        else:
            base = token
            specs.append(("raw", token, base, None))
        if base not in base_names:
            base_names.append(base)
    return base_names, specs


def apply_coarsening(matrix, column_names, specs):
    """(matrix, column_names) rebuilt to match `specs` exactly, in order.

    A "coarse" entry becomes a quantile bin index (0..k-1) of its base column via
    pandas.qcut -- data-driven edges from THIS run's own entities, not a fixed
    threshold, so it applies to any descriptor regardless of native scale.
    `duplicates="drop"` because several of these descriptors are dense with exact
    ties a strict K-way split cannot always honour, which would otherwise raise
    rather than fall back to fewer, wider bins. A "raw" entry passes its column
    through unchanged. Only called when no "neutral" spec is present -- see main --
    so `kind` here is always "raw" or "coarse".
    """
    lookup = {name: matrix[:, i] for i, name in enumerate(column_names)}
    out_columns = []
    out_names = []
    for kind, output_name, base, k in specs:
        if kind == "raw":
            out_columns.append(lookup[base])
        else:
            binned = pandas.qcut(lookup[base], k, labels=False, duplicates="drop")
            out_columns.append(np.asarray(binned, dtype=float))
        out_names.append(output_name)
    return np.column_stack(out_columns), out_names


def resolve_row_values(csv, data_dir, base, zscore):
    """`base`'s value broadcast to one entry per interaction-table row, whatever its
    own natural granularity (lipid species, protein, or already-per-row pair) is --
    fetched via raw_feature_matrix at whichever granularity `base` alone resolves to,
    then mapped onto every row that names that species/protein (a species- or
    protein-only descriptor is constant across every row sharing it, same value
    repeated; a pair descriptor is already one value per row).
    """
    entities_b, matrix_b, entity_column_b, _ = raw_feature_matrix(csv, data_dir, [base], zscore=zscore)
    if entity_column_b == "pair_id":
        return pandas.Series(matrix_b[:, 0], index=entities_b).reindex(csv.index).to_numpy()
    key_column = "FullIdentityOfLipid" if entity_column_b == "FullIdentityOfLipid" else "LTPProtein"
    lookup = dict(zip(entities_b, matrix_b[:, 0]))
    return csv[key_column].map(lookup).to_numpy(dtype=float)


def neutralize_row_values(protein_col, lipid_class_col, values):
    """Two-way de-meaned residual: values - mean(values | protein) -
    mean(values | lipid_class) + mean(values | everything) -- the same formula
    analysis/null_model.py's per_pair_auc uses on a SCORE, applied here to an input
    FEATURE instead, so what a network is given no longer carries "this protein" or
    "this lipid class" alone, only what depends on both together.
    """
    frame = pandas.DataFrame({"value": values, "protein": protein_col, "lipid_class": lipid_class_col})
    protein_mean = frame.groupby("protein")["value"].transform("mean")
    lipid_mean = frame.groupby("lipid_class")["value"].transform("mean")
    return (frame["value"] - protein_mean - lipid_mean + frame["value"].mean()).to_numpy()


def resolve_pair_broadcast_features(csv, data_dir, specs):
    """(entities, matrix, entity_column, column_names) at pair (one row per
    interaction) granularity, built directly from `specs` -- the path main() takes
    whenever --features includes any "_neutral" or "_zscore" token, since both need
    every requested descriptor's value at row level regardless of its own natural
    granularity (see resolve_row_values), not the species-/protein-level matrix
    raw_feature_matrix would otherwise return for a lipid-only or protein-only name.

    Every "raw"/"coarse"/"neutral" spec resolves its base with zscore=False (plain);
    a "zscore" spec resolves its own base with zscore=True instead -- the two are
    cached separately (keyed by (base, zscore)), so a --features set naming the same
    base BOTH plain and "_zscore"-suffixed (e.g. "depth_bulk_match,depth_bulk_match_
    zscore") fetches and reports both, side by side, rather than one silently
    shadowing the other.
    """
    cache = {}
    protein_col = csv["LTPProtein"].to_numpy()
    lipid_class_col = lipid_class_series(csv).to_numpy()
    out_columns = []
    out_names = []
    for kind, output_name, base, k in specs:
        use_zscore = kind == "zscore"
        cache_key = (base, use_zscore)
        if cache_key not in cache:
            cache[cache_key] = resolve_row_values(csv, data_dir, base, use_zscore)
        values = cache[cache_key]
        if kind == "neutral":
            values = neutralize_row_values(protein_col, lipid_class_col, values)
        elif kind == "coarse":
            values = np.asarray(
                pandas.qcut(values, k, labels=False, duplicates="drop"), dtype=float
            )
        out_columns.append(values)
        out_names.append(output_name)
    return list(csv.index), np.column_stack(out_columns), "pair_id", out_names


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--features", default=TANIMOTO,
        help=(
            f'"{TANIMOTO}" (default): whole-structure Morgan-fingerprint similarity, '
            "one entity per lipid species. Otherwise a comma-separated list of "
            f"descriptor names, any mix of lipid-only ({','.join(LIPID_DESCRIPTOR_NAMES)}), "
            "protein-only (dataloader.protein_graph_builder.POCKET_DESCRIPTOR_NAMES, "
            "e.g. pocket_extent,aromatic_share), and pair "
            f"({','.join(PAIR_DESCRIPTOR_NAMES)}) -- exactly analysis/null_model.py's "
            "own --features. Any token may instead be '<name>_coarse=<K>' -- quantile-"
            "bin that descriptor's raw values into K groups (pandas.qcut, data-driven "
            "edges) instead of using it raw, for ANY name here regardless of whether "
            "it already has its own fixed-band _coarse variant (aromatic_share_coarse, "
            "polar_share_coarse). E.g. depth_bulk_match_coarse=3. Any token may "
            "instead (or also, on a different token) be '<name>_neutral' -- subtract "
            "that descriptor's own per-protein mean and per-lipid_class mean "
            "(analysis/null_model.py's per_pair_auc residual, applied to an input "
            "feature instead of a score) so what is left depends on neither the "
            "protein nor the lipid class alone, any --features name, forcing pair "
            "(row) granularity for the whole set. Or '<name>_zscore' -- standardise "
            f"the protein and lipid side separately (over the FULL protein/lipid "
            "descriptor tables, never row- or split-restricted) before combining "
            f"into `name`; valid only for {','.join(MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES)} "
            "(a ValueError names why elsewhere in PAIR_DESCRIPTOR_NAMES this has no "
            "effect). Or --features may be "
            "exactly one of ESM3 / ESMIF1 / PROTEINMPNN (case/hyphen-insensitive) to "
            "run the same eta^2/nn_rate analysis on that LEARNED protein "
            "representation instead of a hand-built descriptor -- one entity per "
            "protein (LTPProtein granularity), the mean-pooled vector "
            "preprocessing/protein_representation_identity_check.py already uses, "
            "read straight from data/embedding_{ESM3,ESMIF1,PROTEINMPNN}/."
        ),
    )
    parser.add_argument(
        "--label", help="Short name for --features, printed as the run header only.",
    )
    parser.add_argument(
        "--zscore", action="store_true",
        help="See analysis/null_model.py --zscore; forwarded unchanged to feature_similarity.",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="How many highest-eta^2 descriptor rows to print per axis in the global "
             "section (default 20, i.e. all of them for every descriptor set this "
             "project currently has).",
    )
    parser.add_argument(
        "--permutations", type=int, default=999,
        help="Label-reshuffles for the nearest-neighbour permutation p-value (default 999).",
    )
    parser.add_argument(
        "--no-blocks", dest="blocks", action="store_false",
        help="Skip the TRAIN vs VALID+TEST section (--families/--seeds/--share/"
             "--ratio below) and print only the whole-dataset GLOBAL section.",
    )
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--share", type=float, default=0.7, help="--coldsplit_share of the run")
    parser.add_argument("--ratio", type=int, default=2, help="--negatives_per_positive of the run")
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    data_dir = os.path.join(PROJECT_ROOT, "data")

    species_class = species_class_map(csv)
    protein_family = protein_family_map(csv)

    if args.features == TANIMOTO:
        similarity, index = species_similarity(csv, data_dir)
        entities = sorted(index, key=index.get)
        entity_column = "FullIdentityOfLipid"
        matrix, column_names = None, []
        label = args.label or TANIMOTO
    elif args.features.upper().replace("-", "") in PROTEIN_EMBEDDING_ALIASES:
        rep_key = PROTEIN_EMBEDDING_ALIASES[args.features.upper().replace("-", "")]
        directory, suffix, trim = REPRESENTATIONS[rep_key]
        all_proteins = sorted(csv["LTPProtein"].unique())
        vectors = mean_pooled(directory, suffix, trim, all_proteins)
        missing = [p for p in all_proteins if p not in vectors]
        if missing:
            print(f"(no {rep_key} embedding on disk for: {', '.join(missing)} -- skipped)\n")
        entities = sorted(vectors)
        matrix = np.stack([vectors[name] for name in entities])
        column_names = [f"dim{i}" for i in range(matrix.shape[1])]
        entity_column = "LTPProtein"
        similarity = _standardised_similarity(matrix)
        index = {entity: position for position, entity in enumerate(entities)}
        label = args.label or rep_key
    else:
        base_names, specs = parse_feature_tokens(args.features)
        if any(kind in ("neutral", "zscore") for kind, _, _, _ in specs):
            # Any "_neutral" or "_zscore" token forces pair (row) granularity for
            # the WHOLE --features set, even a lipid-only or protein-only base name
            # mixed in alongside it -- both need every requested column's value at
            # row level (neutralising to subtract per-protein/per-lipid_class means
            # from, zscore to standardise a specific token's own base independently
            # of every other token's), so there is no species-/protein-level matrix
            # left to hand back.
            entities, matrix, entity_column, column_names = resolve_pair_broadcast_features(
                csv, data_dir, specs
            )
        else:
            entities, matrix, entity_column, column_names = raw_feature_matrix(
                csv, data_dir, base_names, zscore=args.zscore
            )
            matrix, column_names = apply_coarsening(matrix, column_names, specs)
        similarity = _standardised_similarity(matrix)
        index = {entity: position for position, entity in enumerate(entities)}
        label = args.label or (args.features + (" +zscore" if args.zscore else ""))

    print(f"=== features = {label} ===")
    print_global_report(
        entity_column, entities, similarity, matrix, column_names,
        csv, species_class, protein_family, args.top, args.permutations,
    )

    if args.blocks:
        families = [f for f in args.families.split(",") if f]
        seeds = [int(s) for s in args.seeds.split(",")]
        coldsplit_report(
            csv, entity_column, index, similarity,
            families, seeds, args.share, args.ratio,
        )


if __name__ == "__main__":
    main()
