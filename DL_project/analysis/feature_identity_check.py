#!/usr/bin/env python3
"""How much a chemistry-only feature set already *is* identity, in a few cheap numbers.

Generalises preprocessing/pocket_descriptor_identity_check.py's method (eta^2 +
leave-one-out nearest-neighbour identity rate, each read against its own chance floor,
plus a permutation significance test) from "protein pocket descriptors vs protein
family" to any --features set analysis/baselines/null_model.py accepts, against every identity
axis that granularity can see: which lipid SPECIES, which lipid CLASS (head group),
which PROTEIN, and which protein FAMILY (ProteinDomain).

Why this question, before a network is trained. The project's recurring failure mode
(files/results/signal_state.md; project memory descriptors-path-fingerprint-leak,
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
analysis/baselines/null_model.py's own --double_coldsplit machinery, VALID and TEST pooled
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
to break eta^2 down by, so only the nearest-neighbour rate (and Mantel, below) is
reported for it -- a ceiling reading of how separable raw chemical structure alone
already makes lipid identity, the same role preprocessing/pocket_descriptor_identity_
check.py's mean-ESM3 embedding plays for protein identity.

--features molformer: the learned per-species MolFormer SMILES embedding
architecture/lipid_encoder.py's non-graph path actually feeds the model (one 768-dim
vector per lipid species, mean-pooled over tokens then over candidate isomers --
preprocessing/lipid_embedding_identity_check.py's own species_embeddings, reused
unchanged) -- the lipid-side analogue of --features ESM3/ESMIF1/PROTEINMPNN on the
protein side.

Mantel test, every axis, GLOBAL section only: Spearman correlation between the
descriptor set's own pairwise-distance structure (recovered from the already-built
`similarity` matrix, not recomputed) and one-hot(labels)'s, standardised the same way
any other descriptor matrix here is -- preprocessing/pocket_descriptor_identity_
check.py's own mantel, generalised to every axis build_axis_labels produces instead
of one hand-picked axis, and to any entity count: that script's broadcast distance is
fine at its own 35-protein scale but is O(entities^2 x columns) MEMORY, which blows
past what is available once entities is in the thousands (pair granularity) --
condensed_distance's dot-product form (the same identity _standardised_similarity
already relies on) keeps this at O(entities^2). A high-cardinality axis (e.g.
"lipid", ~283 distinct values) at pair granularity with a large --permutations can
still be slow -- each permutation re-ranks an O(entities^2) vector; lower
--permutations for that combination if needed.

    python3 analysis/feature_identity_check.py
    python3 analysis/feature_identity_check.py --features chain,unsaturation,hbond,heavy
    python3 analysis/feature_identity_check.py --features pocket_extent,ev14_q50,depth_q10
    python3 analysis/feature_identity_check.py --features occupancy,hbond_match,volume_fit
    python3 analysis/feature_identity_check.py --features occupancy,hbond_match --families GLTP,scp2 --seeds 0,1
    python3 analysis/feature_identity_check.py --features molformer

ALTERNATIVE MODES. Each replaces the --features report above with one specific
identity question, and each used to be its own script in analysis/probes/ (they all
already imported this module's eta_squared / eta_squared_joint / group_floor /
protein_family_map; two of them carried their own drifted copy of permutation_p, which
is now one implementation here):

  --descriptors            rank every pair/lipid/protein descriptor name individually
                           (one row per name, sorted by how lopsidedly each leaks
                           identity) -- was analysis/probes/rank_pair_descriptors.py.
  --lipid_classes          which LIPID descriptors are head-group-class fingerprints,
                           on three kinds of axis (fine classes, the four
                           LIPID_COLDSPLIT_SETS, each set against the rest), each eta^2
                           with its floor and a permutation p, ending in a
                           neutral/borderline/fingerprint verdict per descriptor -- was
                           analysis/probes/lipid_descriptor_class_identity.py.
  --family_separation FAM  which PROTEIN descriptor singles out one family against all
                           the others (Mann-Whitney outrank + eta^2 + permutation p),
                           over every descriptor in data/protein_descriptor_table.json
                           rather than only the model-facing ones -- was
                           analysis/probes/lbp_family_descriptor_separation.py.
  --pair_vs_family         eta^2 of each PAIR descriptor's actual COMPUTED value against
                           protein family, collapsed to one value per protein so the
                           number is comparable to the protein-side table -- was
                           analysis/probes/pair_descriptor_family_eta2.py.
  --edge_geometry          the same question for the 25-dim structured protein-EDGE
                           geometry vector, per-pocket mean/std per column -- was
                           analysis/probes/edge_geometry_family_check.py.

    python3 analysis/feature_identity_check.py --descriptors
    python3 analysis/feature_identity_check.py --descriptors=occupancy,hbond_match,volume_fit
    python3 analysis/feature_identity_check.py --lipid_classes
    python3 analysis/feature_identity_check.py --lipid_classes --descriptor_set both --out /tmp/lipid_eta2.csv
    python3 analysis/feature_identity_check.py --family_separation LBP_BPI_CETP --family_separation lipocalin
    python3 analysis/feature_identity_check.py --pair_vs_family
    python3 analysis/feature_identity_check.py --edge_geometry --out /tmp/edge_eta2.csv

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

# The same coldsplit machinery analysis/baselines/null_model.py itself uses for its (family,
# seed) held-out blocks, reused rather than reimplemented so a block reproduced here
# is provably the same rows a null-model/network run would see -- working_set/
# split_func/lipid_classes_for_holdout/DEFAULT_FAMILIES are plain re-exports on
# null_model's own module namespace (see its own imports), not analysis specific to
# the null model itself, so importing them here does not pull in anything about
# scoring the network.
from analysis.baselines.null_model import (  # noqa: E402
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
# standardise: mantel_test's own column-standardisation of the one-hot label matrix,
# reused rather than reimplemented so it matches preprocessing/pocket_descriptor_
# identity_check.py's own mantel/standardise exactly.
from pocket_descriptor_identity_check import standardise  # noqa: E402

# Same reserved value as analysis/baselines/null_model.py's own TANIMOTO -- kept as a separate
# literal rather than an import so the --features default here needs nothing beyond
# dataloader.chemistry_prior itself.
TANIMOTO = "tanimoto"
# --features molformer: preprocessing/lipid_embedding_identity_check.py's own learned
# per-species embedding, folded in here as a third --features option alongside
# tanimoto and the protein-embedding aliases below.
MOLFORMER = "molformer"

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


def permutation_p(values, labels, observed, permutations, rng):
    """Share of label reshuffles whose eta^2 reaches `observed`.

    The labels move and the values stay put, so the null being tested is "this
    descriptor is unrelated to which group an entity belongs to" while every other
    property of the descriptor's own distribution -- its spread, its skew, its ties --
    is preserved exactly. A boolean one-vs-rest mask is permuted the same way, which
    preserves the suspect group's size exactly, so this one implementation covers both
    the multi-class and the one-vs-rest axis (it replaces the two drifted copies that
    used to live in analysis/probes/lipid_descriptor_class_identity.py and
    analysis/probes/lbp_family_descriptor_separation.py).
    """
    if not np.isfinite(observed):
        return float("nan")
    shuffled = np.array(labels, copy=True)
    hits = 0
    for _ in range(permutations):
        rng.shuffle(shuffled)
        if eta_squared(values, shuffled) >= observed:
            hits += 1
    # +1 on both sides: the observed labelling is itself one of the arrangements under
    # the null, so a p-value of exactly 0 is not attainable and should not be reported.
    return (hits + 1) / (permutations + 1)


def outrank(values, is_suspect):
    """Mean fraction of the other entities a suspect entity exceeds; ties count half.

    The Mann-Whitney statistic, and the one to read for a one-vs-rest axis: 0.5 = no
    separation, 0.0/1.0 = the suspect group sits entirely below/above everyone else. It
    says whether a group is IDENTIFIABLE from the descriptor, which is what a leak
    needs -- eta^2 alone can sit near its floor while a small group is still perfectly
    separated.
    """
    suspect, other = values[is_suspect], values[~is_suspect]
    if len(suspect) == 0 or len(other) == 0:
        return float("nan")
    greater = (suspect[:, None] > other[None, :]).astype(float)
    tied = (suspect[:, None] == other[None, :]).astype(float)
    return float((greater + 0.5 * tied).mean())


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
    same way analysis/baselines/null_model.py's null model ranks by) shares its `labels` value;
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


def condensed_distance(matrix):
    """Condensed (upper-triangle) euclidean distances between every pair of rows of
    `matrix`, via the dot-product identity ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b --
    dataloader.chemistry_prior._standardised_similarity's own trick, reused here so
    this costs O(entities^2) memory, not the O(entities^2 x columns) a direct
    [:, None, :] - [None, :, :] broadcast (preprocessing/pocket_descriptor_identity_
    check.py's own pair_distances) would cost -- fine at that script's own 35-protein
    scale, but it blows well past available memory once entities is in the thousands
    (pair granularity) and columns is a one-hot label matrix with a high-cardinality
    axis (e.g. "lipid", ~283 distinct values) widening it further.
    """
    matrix = np.asarray(matrix, dtype=float)
    sq_norms = (matrix ** 2).sum(axis=1)
    sq_distance = sq_norms[:, None] + sq_norms[None, :] - 2 * matrix @ matrix.T
    np.clip(sq_distance, 0.0, None, out=sq_distance)
    distance = np.sqrt(sq_distance)
    rows, cols = np.triu_indices(len(matrix), k=1)
    return distance[rows, cols]


def mantel_test(similarity, labels, permutations=999, seed=0):
    """Spearman correlation between `similarity`'s own pairwise-distance structure
    and one-hot(labels)'s, with a label-permutation p -- preprocessing/pocket_
    descriptor_identity_check.py's own mantel, generalised to every axis build_axis_
    labels produces instead of one hand-picked axis, and to any entity count via
    condensed_distance (see its own docstring for why the original broadcast form
    does not scale to pair granularity).

    Takes the already-built `similarity` matrix (1/(1+distance), dataloader.
    chemistry_prior._standardised_similarity) rather than the raw feature matrix, so
    the feature side's own O(entities^2) distance is recovered by inverting values
    already computed upstream rather than paid for a second time.

    one-hot(labels), standardised per column exactly like any other descriptor
    matrix here, stands in for a continuous "pure identity" reference the way it does
    in preprocessing/lipid_embedding_identity_check.py's own Mantel test (there is no
    separate embedding to play mean-ESM3's role for an arbitrary label axis) --
    unchanged from that precedent.

    Each permutation reshuffles `labels`, rebuilds the one-hot distance (group
    proportions are preserved by a permutation, but which entity carries which label
    is not, so this cannot be hoisted out of the loop), and re-ranks it for Spearman
    -- O(entities^2) per permutation, same bound as the observed statistic, but this
    can still be slow for a high-cardinality axis at pair granularity with a large
    --permutations; lower --permutations for that combination if needed.
    """
    from scipy import stats

    similarity = np.asarray(similarity, dtype=float)
    rows, cols = np.triu_indices(len(similarity), k=1)
    feature_distance = 1.0 / similarity[rows, cols] - 1.0
    labels = np.asarray(labels)

    one_hot = pandas.get_dummies(labels).to_numpy(dtype=float)
    label_distance = condensed_distance(standardise(one_hot))
    observed = float(stats.spearmanr(feature_distance, label_distance).statistic)

    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(permutations):
        shuffled = rng.permutation(labels)
        shuffled_one_hot = pandas.get_dummies(shuffled).to_numpy(dtype=float)
        shuffled_distance = condensed_distance(standardise(shuffled_one_hot))
        if abs(stats.spearmanr(feature_distance, shuffled_distance).statistic) >= abs(observed):
            hits += 1
    p_value = (hits + 1) / (permutations + 1)
    return observed, p_value


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
    csv index -- see analysis/baselines/null_model.py's working_set). Otherwise several rows
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
        mantel_rho, mantel_p = mantel_test(similarity, labels, permutations=permutations)
        summary_rows.append({
            "axis": axis_name, "groups": groups, "entities": n, "eta2_floor": floor,
            "joint_eta2": joint, "nn_rate": rate, "nn_chance": chance, "nn_p": p_value,
            "mantel_rho": mantel_rho, "mantel_p": mantel_p,
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
    analysis/baselines/null_model.py's own --split keeps them apart because it is scoring one
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
    analysis/baselines/null_model.py's per_pair_auc uses on a SCORE, applied here to an input
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


# ================================================================= mode --lipid_classes
# Which of the lipid descriptors are head-group-class FINGERPRINTS rather than
# chemistry -- was analysis/probes/lipid_descriptor_class_identity.py. The protein-side
# question (section 2 of files/reference/descriptor_catalog.md) has an eta^2-by-family
# table and the "family-neutral 7" every geometric_edge_* baseline uses is that table's
# output; under --lipid_coldsplit the hidden axis is the other one, whole head-group
# classes leave training for every protein (dataloader/sampler.py's
# LIPID_COLDSPLIT_SETS), and a lipid descriptor that mostly encodes "which class is
# this" is the exact analogue of pocket_sasa_share (eta^2 = 0.85) on the protein side.

# The convention files/reference/descriptor_catalog.md section 2 already applies to the
# protein side: "at the floor" is the bar for neutrality, and a permutation p-value
# guards against reading noise above it as structure.
SIGNIFICANCE = 0.05


def candidate_matrix(csv, data_dir, names):
    """(species, matrix) for measure names that are not in LIPID_DESCRIPTOR_NAMES.

    raw_feature_matrix only resolves the catalog the MODEL can be given, and the
    candidates of descriptor_catalog section 7g are deliberately not in it yet --
    measuring a descriptor must not require first wiring it into what the network sees.
    Values come from the shared pair-descriptor cache (every _MEASURES entry is always
    built), averaged over a species' candidate structures the same way
    chemistry_prior's own lipid table does, so the two agree on what "this species'
    value" means.
    """
    from dataloader.pair_descriptor_cache_reader import load_pair_descriptor_cache
    from dataloader.pocket_lipid_compatibility import candidates_for_row
    from preprocessing.compute_descriptors import _MEASURES

    cache = load_pair_descriptor_cache(os.path.join(PROJECT_ROOT, "data"), isomeric=False)
    if cache is None:
        raise SystemExit(
            "no pair-descriptor cache -- run data/build_pair_descriptor_cache.py first; "
            "computing these from scratch here would re-embed conformers per lipid"
        )
    missing = [name for name in names if name not in _MEASURES]
    if missing:
        raise SystemExit(f"not cached measures: {missing}")

    species, rows = [], []
    seen = set()
    for _, row in csv.iterrows():
        name = row["FullIdentityOfLipid"]
        if name in seen:
            continue
        seen.add(name)
        collected = {measure: [] for measure in names}
        for raw in candidates_for_row(row):
            canonical = cache["raw_to_canonical"].get(raw)
            entry = cache["values"].get(canonical) if canonical else None
            if entry is None:
                continue
            for measure in names:
                value = entry.get(measure)
                if value is not None:
                    collected[measure].append(float(value))
        # np.nan, not 0.0: a species none of whose candidates has this measure has no
        # value, and eta_squared must not read a filler zero as a real one. Only
        # tail_double_bond_position is routinely absent (fully saturated lipids).
        species.append(name)
        rows.append([
            float(np.mean(collected[m])) if collected[m] else np.nan for m in names
        ])
    return species, np.array(rows, dtype=float)


def coldsplit_set_labels(classes):
    """Which LIPID_COLDSPLIT_SET each class belongs to, "kept" for the classes in none.

    Phosphatidyl- and lysophosphatidylethanolamine are deliberately in no set (see the
    LIPID_COLDSPLIT_SETS comment in dataloader/sampler.py), so "kept" is a real group
    with real members, not a leftover bucket to be dropped.
    """
    from dataloader.sampler import LIPID_COLDSPLIT_SETS

    membership = {}
    for set_name, class_names in LIPID_COLDSPLIT_SETS.items():
        for class_name in class_names:
            membership[class_name.lower()] = set_name
    return np.array([membership.get(str(c).lower(), "kept") for c in classes])


def axis_table(matrix, column_names, labels, axis_name, permutations, seed):
    """One eta^2 row per descriptor against one identity axis, floor and p-value included."""
    rng = np.random.default_rng(seed)
    rows = []
    for index, name in enumerate(column_names):
        values = matrix[:, index]
        # A descriptor undefined for some species (tail_double_bond_position on a fully
        # saturated lipid) is measured on the species where it IS defined, with the
        # count reported, rather than imputed -- an imputed value would be a constant
        # shared by exactly the saturated lipids, which is itself a class signal.
        defined = ~np.isnan(values)
        values, group_labels = values[defined], np.asarray(labels)[defined]
        observed = eta_squared(values, group_labels)
        floor = group_floor(group_labels)
        rows.append({
            "axis": axis_name,
            "descriptor": name,
            "eta2": observed,
            "floor": floor,
            "above_floor": observed - floor,
            # What the question needs alongside neutrality: a descriptor with eta^2 =
            # 0.99 has essentially no variation left INSIDE a class, so it can only ever
            # act as the class label. One at 0.5 still varies within a class and can
            # carry real interaction signal there -- being head-derived is not the same
            # as being a shortcut.
            "within_class_share": 1.0 - observed,
            "p_permutation": permutation_p(values, group_labels, observed, permutations, rng),
            "groups": len(pandas.unique(group_labels)),
            "n": len(group_labels),
        })
    return pandas.DataFrame(rows)


def verdict(row):
    """class-neutral / borderline / fingerprint, on the same bar as the protein side.

    "fingerprint" needs BOTH: measurably above the arithmetic floor AND not explainable
    as a reshuffle. A descriptor above the floor with p >= 0.05 is "borderline" rather
    than neutral because at these entity counts the permutation test is the weaker of
    the two checks, and calling such a column safe is the error this whole table exists
    to avoid.
    """
    if not np.isfinite(row["eta2"]):
        return "degenerate"
    if row["above_floor"] <= 0:
        return "class-neutral"
    if row["p_permutation"] < SIGNIFICANCE:
        return "fingerprint"
    return "borderline"


def print_joint(matrix, column_names, labels):
    """Joint eta^2 over the columns that have a value for every species.

    A degenerate column (aromatic_ring_count: no variance at all) or one undefined for
    some species (tail_double_bond_position on a saturated lipid) makes the whole
    standardised sum-of-squares nan, which reads as "could not be computed" when the
    answer is "these columns cannot take part". Dropped by name, and the drop is
    reported, so a joint number is never quietly over a different set than it says.
    """
    usable = [
        i for i in range(matrix.shape[1])
        if np.isfinite(matrix[:, i]).all() and matrix[:, i].std() > 1e-12
    ]
    dropped = [column_names[i] for i in range(matrix.shape[1]) if i not in usable]
    value = eta_squared_joint(matrix[:, usable], labels) if usable else float("nan")
    note = f"  [dropped: {','.join(dropped)}]" if dropped else ""
    print(f"joint eta2 over {len(usable)} of {len(column_names)} descriptors: "
          f"{value:.4f}  (floor {group_floor(labels):.4f}){note}")


def print_axis_table(frame, title):
    print(f"\n=== {title} ===")
    header = frame.iloc[0]
    print(f"groups: {header['groups']}   entities: {header['n']}   "
          f"arithmetic floor (k-1)/(n-1): {header['floor']:.4f}")
    print(f"{'descriptor':26s} {'eta2':>8s} {'-floor':>8s} {'within':>8s} {'p_perm':>8s} {'n':>5s}  verdict")
    for _, row in frame.sort_values("eta2", ascending=False).iterrows():
        print(f"{row['descriptor']:26s} {row['eta2']:8.4f} {row['above_floor']:8.4f} "
              f"{row['within_class_share']:8.4f} {row['p_permutation']:8.4f} "
              f"{int(row['n']):5d}  {row['verdict']}")


def run_lipid_classes(args):
    """Three axes, because they answer three different questions and can disagree:
    the fine head-group classes (directly comparable to the protein-side eta^2-by-family
    table), the four LIPID_COLDSPLIT_SETS plus "kept" (closer to what the split does),
    and one binary split per set (the most operational, because a run holds out exactly
    ONE set -- a descriptor can sit at the floor on the first two axes and still
    separate sphingolipids perfectly from the rest).
    """
    from dataloader.lipid_classes import lipid_class_series as class_series
    from dataloader.pair_descriptors import LIPID_DESCRIPTOR_NAMES as LIPID_NAMES
    from dataloader.sampler import LIPID_COLDSPLIT_SETS
    from preprocessing.compute_descriptors import CANDIDATE_LIPID_DESCRIPTOR_NAMES

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))

    # One row per distinct lipid species, not per interaction row: an interaction table
    # weighted by how often a species was screened would make eta^2 report which classes
    # were assayed most, not which classes the descriptor can tell apart.
    catalog = list(LIPID_NAMES)
    candidates = list(CANDIDATE_LIPID_DESCRIPTOR_NAMES)
    if args.descriptor_set == "candidates":
        catalog = []
    elif args.descriptor_set == "catalog":
        candidates = []

    species, matrix, column_names = None, None, []
    if catalog:
        species, matrix, entity_column, column_names = raw_feature_matrix(
            csv, data_dir, catalog, zscore=False
        )
        if entity_column != "FullIdentityOfLipid":
            raise SystemExit(
                f"expected lipid granularity, got {entity_column!r} -- "
                "LIPID_DESCRIPTOR_NAMES should resolve per species"
            )
        column_names = list(column_names)
    if candidates:
        candidate_species, candidate_values = candidate_matrix(csv, data_dir, candidates)
        if species is None:
            species, matrix = candidate_species, candidate_values
        else:
            # Same species, different order: raw_feature_matrix sorts, candidate_matrix
            # keeps first-seen csv order. Reindexed by NAME rather than positionally --
            # zipping two differently ordered lists would silently pair each species'
            # catalog values with another species' tail values, which is the one error
            # here that would look like a result instead of a crash. The SET must still
            # match exactly; a difference there is a real divergence, not an ordering.
            if set(candidate_species) != set(species):
                raise SystemExit(
                    f"catalog and candidate species sets disagree: "
                    f"{len(set(species) ^ set(candidate_species))} differ"
                )
            position = {name: i for i, name in enumerate(candidate_species)}
            reordered = candidate_values[[position[name] for name in species], :]
            matrix = np.hstack([matrix, reordered])
        column_names = column_names + candidates

    species_frame = pandas.DataFrame({"FullIdentityOfLipid": species})
    classes = class_series(species_frame).to_numpy()
    sets = coldsplit_set_labels(classes)

    print(f"lipid descriptors: {len(column_names)}   species: {len(species)}")
    print(f"head-group classes: {len(pandas.unique(classes))}   "
          f"coldsplit sets: {sorted(pandas.unique(sets))}")

    tables = []
    for axis_name, labels in (("head_group_class", classes), ("coldsplit_set", sets)):
        table = axis_table(matrix, column_names, labels, axis_name,
                           args.permutations, args.seed)
        table["verdict"] = table.apply(verdict, axis=1)
        tables.append(table)
        print_axis_table(table, f"axis: {axis_name}")
        print_joint(matrix, column_names, labels)

    # One binary split per set -- what a single --lipid_coldsplit run actually faces.
    for set_name in LIPID_COLDSPLIT_SETS:
        labels = np.where(sets == set_name, set_name, "rest")
        table = axis_table(matrix, column_names, labels, f"is_{set_name}",
                           args.permutations, args.seed)
        table["verdict"] = table.apply(verdict, axis=1)
        tables.append(table)
        print_axis_table(table, f"axis: {set_name} vs rest")
        print_joint(matrix, column_names, labels)

    everything = pandas.concat(tables, ignore_index=True)

    # The actual deliverable: a descriptor is only proposed as class-neutral if it is
    # neutral on EVERY axis. One run holds out one set, but the same descriptor list is
    # used for all four, so a column that fingerprints any single set disqualifies
    # itself for the whole sweep.
    per_descriptor = everything.groupby("descriptor")["verdict"]
    neutral = sorted(name for name, verdicts in per_descriptor
                     if set(verdicts) <= {"class-neutral"})
    flagged = sorted(name for name, verdicts in per_descriptor
                     if "fingerprint" in set(verdicts))
    borderline = sorted(set(column_names) - set(neutral) - set(flagged))

    print("\n=== proposed split (neutral on EVERY axis above) ===")
    print(f"class-neutral ({len(neutral)}): {','.join(neutral) if neutral else '(none)'}")
    print(f"borderline    ({len(borderline)}): {','.join(borderline) if borderline else '(none)'}")
    print(f"fingerprint   ({len(flagged)}): {','.join(flagged) if flagged else '(none)'}")
    if neutral:
        keep = [column_names.index(name) for name in neutral]
        print("\njoint eta2 of the class-neutral subset alone, per axis:")
        for axis_name, labels in (("head_group_class", classes), ("coldsplit_set", sets)):
            print(f"  {axis_name:20s} {eta_squared_joint(matrix[:, keep], labels):.4f}"
                  f"  (all {len(column_names)}: {eta_squared_joint(matrix, labels):.4f})")

    if args.out:
        everything.to_csv(args.out, index=False)
        print(f"\nwrote {len(everything)} rows to {args.out}")


# ============================================================= mode --family_separation
# Which protein descriptor, if any, singles out ONE family the way pocket_extent singles
# out lipocalin -- was analysis/probes/lbp_family_descriptor_separation.py. On
# --double_coldsplit, LBP_BPI_CETP is the family where the descriptor baseline clears its
# null model by a wide margin (test BA 0.677 on dh_family_neutral_lipprop, 0.796-0.826 on
# the earlier descriptors_path line) and files/results/signal_state.md section 8 calls
# that an unexplained leak rather than chemistry. lipocalin rides along as a positive
# control: a statistic that cannot reproduce its known pocket_extent separation is not
# measuring what it claims to.

# The protein-side half of dh_family_neutral_lipprop's --descriptor_names (the other four
# -- chain/unsaturation/hbond/heavy -- are lipid-only tokens and carry no per-protein
# value to separate anything with).
LABEL_PROTEIN_DESCRIPTORS = (
    "pocket_volume_per_sasa", "pocket_elongation", "pocket_flatness", "buriedness_q50",
    "apolar_sasa_share", "aromatic_share", "hydropathy_rim",
)


def family_separation_report(family, values_by_name, families, proteins, permutations, seed):
    is_suspect = families == family
    print(f"===== {family}: {int(is_suspect.sum())} of {len(proteins)} proteins "
          f"({', '.join(np.array(proteins)[is_suspect])}) =====")
    print(f"eta^2 floor for a 2-way split over {len(proteins)} proteins: "
          f"{1.0 / (len(proteins) - 1):.3f}\n")
    rng = np.random.default_rng(seed)
    rows = []
    for name, values in values_by_name.items():
        separation = outrank(values, is_suspect)
        observed = eta_squared(values, is_suspect)
        p_value = permutation_p(values, is_suspect, observed, permutations, rng)
        rows.append((abs(separation - 0.5), name, separation, observed, p_value))
    rows.sort(reverse=True)
    print(f"{'descriptor':34s} {'outrank':>8s} {'eta^2':>7s} {'p':>7s}  in label")
    for _, name, separation, observed, p_value in rows:
        flag = "yes" if name in LABEL_PROTEIN_DESCRIPTORS else ""
        print(f"{name:34s} {separation:8.2f} {observed:7.3f} {p_value:7.4f}  {flag}")
    print()


def run_family_separation(args):
    """Every protein-side descriptor the table holds, against one family vs the rest.

    Reads data/protein_descriptor_table.json (preprocessing.compute_descriptors'
    protein_descriptor_table) rather than raw_feature_matrix, so descriptors that were
    never wired into POCKET_DESCRIPTOR_NAMES are measured too -- the search does not
    proceed one suspect per session.
    """
    from preprocessing.compute_descriptors import protein_descriptor_table

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    families_by_protein = pandas.Series(protein_family_map(csv))
    table = protein_descriptor_table(data_dir)
    proteins = sorted(name for name in families_by_protein.index if name in table)
    families = np.array([families_by_protein[name] for name in proteins])

    names = sorted({name for protein in proteins for name in table[protein]})
    values_by_name = {}
    for name in names:
        values = np.array(
            [float(table[protein].get(name, np.nan)) for protein in proteins]
        )
        if not np.isfinite(values).all() or values.std() == 0.0:
            continue
        values_by_name[name] = values
    print(f"{len(values_by_name)} usable protein descriptors over {len(proteins)} proteins "
          f"({len(names) - len(values_by_name)} skipped as constant or incomplete)\n")

    suspects = args.family_separation or ["LBP_BPI_CETP", "lipocalin"]
    for family in suspects:
        if family not in set(families):
            raise SystemExit(f"unknown family {family}; known: {sorted(set(families))}")
        family_separation_report(
            family, values_by_name, families, proteins, args.permutations, args.seed
        )


# ================================================================ mode --pair_vs_family
# eta^2 of the ACTUAL COMPUTED pair-descriptor value against protein family -- was
# analysis/probes/pair_descriptor_family_eta2.py. `descriptors_pair_clean`
# (arg_files/descriptors/descriptors_pair_clean.md) was assembled from entries INFERRED
# safe because their protein-side component alone is family-neutral-safe (eta^2
# 0.28-0.48, preprocessing/pocket_descriptor_identity_check.py) and their lipid-side
# component is family-independent by construction. That inference was never checked
# against the descriptor's own computed VALUE, which multiplies (or takes min/ratio of)
# the two sides together -- a combination CAN reintroduce family structure the protein
# component alone does not have.

PAIR_VS_FAMILY_DEFAULT = (
    "aromatic_contact", "hbond_match", "volume_fit", "buriedness_match",
    "aromatic_contact_min", "hbond_match_min", "tail_elongation_fit",
    "hydropathy_rim_match", "elongation_shape_match", "flatness_shape_match",
)


def run_pair_vs_family(args):
    """One value per PROTEIN (not per row): the descriptor's real value from real
    (protein, lipid) pairs, averaged over every lipid screened against that protein, so
    the number is the same number, computed the same way, as every other entry in the
    protein-side eta^2 table (files/results/descriptors_baseline_leak_confirmed.md).

    Row-level eta^2 is printed alongside for context -- it is NOT the number the
    methodology asks for (its floor is governed by thousands of rows, not 35 proteins,
    so it is not comparable to the protein-side table), but a row-level number well
    above ITS OWN floor while the per-protein one sits at the family floor would say the
    descriptor's row-to-row variation still tracks family despite being lipid-driven.
    """
    names = [n for n in (args.names or ",".join(PAIR_VS_FAMILY_DEFAULT)).split(",") if n]
    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pandas.read_csv(interaction_csv_path(data_dir + os.sep))
    protein_family = protein_family_map(csv)
    protein_col = csv["LTPProtein"].to_numpy()
    family_col = np.array([protein_family[p] for p in protein_col])

    proteins = sorted(protein_family)
    families_by_protein = np.array([protein_family[p] for p in proteins])
    floor = group_floor(families_by_protein)
    print(f"{len(proteins)} proteins, {len(pandas.unique(families_by_protein))} families, "
          f"arithmetic floor (k-1)/(n-1) = {floor:.3f}\n")

    rows = []
    for name in names:
        entities, matrix, entity_column, _ = raw_feature_matrix(
            csv, data_dir, [name], zscore=args.zscore
        )
        if entity_column != "pair_id":
            raise SystemExit(
                f"{name}: expected pair_id granularity, got {entity_column}"
            )
        values = matrix[:, 0]
        frame = pandas.DataFrame({"protein": protein_col, "value": values})
        per_protein = frame.groupby("protein")["value"].mean()
        per_protein_values = np.array([per_protein[p] for p in proteins])
        rows.append({
            "descriptor": name,
            "eta2_per_protein": eta_squared(per_protein_values, families_by_protein),
            "above_floor": eta_squared(per_protein_values, families_by_protein) - floor,
            "eta2_row_level": eta_squared(values, family_col),
            "row_floor": group_floor(family_col),
        })

    table = pandas.DataFrame(rows).set_index("descriptor").sort_values(
        "eta2_per_protein", ascending=False
    )
    pandas.set_option("display.width", 200)
    print(table.round(4).to_string())


# ================================================================= mode --edge_geometry
# How much the structured protein-EDGE geometry vector already is family identity -- was
# analysis/probes/edge_geometry_family_check.py. Every one of the 15
# PROTEIN_DESCRIPTOR_NAMES has a measured eta^2 against family and the 7 lowest are the
# "family-neutral" set, but the 25-dim structured edge vector --protein_edge_mlp /
# --protein_edge_attention also feeds the network (architecture/protein_edge_geometry.py:
# 16-bin distance RBF, 3-dim local direction, 4-dim relative-orientation quaternion,
# log-area, log-boundary-ratio) had never had the same check. Pocket-only, on purpose, to
# match the protein-descriptor table's own subject (the binding cavity).

EDGE_GEOMETRY_BASELINE_LABEL = "ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm"
_RBF_CENTERS = np.linspace(2.0, 22.0, 16)
EDGE_COLUMN_NAMES = (
    [f"rbf_{center:.1f}A" for center in _RBF_CENTERS]
    + ["dir_x", "dir_y", "dir_z"]
    + ["quat_0", "quat_1", "quat_2", "quat_3"]
    + ["log_area", "log_boundary_ratio"]
)


def run_edge_geometry(args):
    """Per-pocket mean/std of each of the 25 edge-vector columns, across every directed
    contact edge inside that protein's pocket -- the only thing that makes an edge-level
    vector comparable across proteins with different residue counts -- then eta^2 of
    each of those 50 columns against family.
    """
    import torch

    from architecture.protein_edge_geometry import structured_edge_features
    from dataloader.protein_graph_builder import ProteinGraphBuilder
    from read_configuration import read_configuration

    from analysis.checkpoint_scores import arg_lines

    class _Builder(ProteinGraphBuilder):
        """Bare instance carrying only the .config protein_graph_tensors reads."""

        def __init__(self, config):
            self.config = config

    # The real family-neutral baseline config, plus --protein_pockets_only so the edge
    # geometry measured here is restricted to the pocket subgraph; everything else comes
    # straight from the baseline's own arg file, so this is provably the same edge
    # geometry that baseline's --protein_edge_mlp consumes. The --excluded_groups value
    # is inert (this never touches PLIDataset or the coldsplit) but the baseline's own
    # --double_coldsplit requires a nonempty one to pass validate().
    config = read_configuration(
        ["feature_identity_check"]
        + arg_lines(EDGE_GEOMETRY_BASELINE_LABEL)
        + ["--protein_pockets_only", "--excluded_groups=LBP_BPI_CETP"]
    )
    builder = _Builder(config)
    graph_root = os.path.join(PROJECT_ROOT, "data", "graphs")

    def pocket_edge_columns(protein):
        protein_dir = os.path.join(graph_root, protein)
        nodes = os.path.join(protein_dir, "coarse_graph_nodes.csv")
        edges = os.path.join(protein_dir, "coarse_graph_links.csv")
        pocketness = os.path.join(protein_dir, "pocketness.pdb")
        plm = torch.zeros(len(pandas.read_csv(nodes)), 1)
        parts = builder.protein_graph_tensors(nodes, edges, plm, pocketness)
        _, e_attr = structured_edge_features(
            parts["edge_index"], parts["frame_rotation"], parts["frame_translation"],
            parts["edge_attr"],
        )
        return e_attr.numpy()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    family_map = protein_family_map(csv)

    rows, skipped = [], []
    for protein, family in sorted(family_map.items()):
        try:
            values = pocket_edge_columns(protein)
        except (FileNotFoundError, ValueError) as error:
            skipped.append((protein, str(error)))
            continue
        if values.shape[0] == 0:
            skipped.append((protein, "no pocket-internal contact edges"))
            continue
        row = {"protein": protein, "family": family, "n_directed_edges": values.shape[0]}
        for i, name in enumerate(EDGE_COLUMN_NAMES):
            row[f"{name}_mean"] = float(values[:, i].mean())
            row[f"{name}_std"] = float(values[:, i].std())
        rows.append(row)

    if skipped:
        print(f"skipped {len(skipped)} protein(s):")
        for protein, reason in skipped:
            print(f"  {protein}: {reason}")

    frame = pandas.DataFrame(rows)
    n = len(frame)
    k = frame["family"].nunique()
    floor = (k - 1) / (n - 1) if n > 1 else float("nan")
    print(f"\n{n} proteins, {k} families, eta^2 chance floor (k-1)/(n-1) = {floor:.3f}\n")

    results = [
        {
            "column": f"{name}_{stat}",
            "eta2_family": eta_squared(
                frame[f"{name}_{stat}"].values, frame["family"].values
            ),
        }
        for name in EDGE_COLUMN_NAMES for stat in ("mean", "std")
    ]
    result_frame = pandas.DataFrame(results).sort_values("eta2_family", ascending=False)
    print(result_frame.round(3).to_string(index=False))

    if args.out:
        result_frame.to_csv(args.out, index=False)
        print(f"\nwrote {args.out}")


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
            f"({','.join(PAIR_DESCRIPTOR_NAMES)}) -- exactly analysis/baselines/null_model.py's "
            "own --features. Any token may instead be '<name>_coarse=<K>' -- quantile-"
            "bin that descriptor's raw values into K groups (pandas.qcut, data-driven "
            "edges) instead of using it raw, for ANY name here regardless of whether "
            "it already has its own fixed-band _coarse variant (aromatic_share_coarse, "
            "polar_share_coarse). E.g. depth_bulk_match_coarse=3. Any token may "
            "instead (or also, on a different token) be '<name>_neutral' -- subtract "
            "that descriptor's own per-protein mean and per-lipid_class mean "
            "(analysis/baselines/null_model.py's per_pair_auc residual, applied to an input "
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
            f"read straight from data/embedding_{{ESM3,ESMIF1,PROTEINMPNN}}/. Or '{MOLFORMER}' "
            "to run it on the learned per-species MolFormer SMILES embedding "
            "instead -- one entity per lipid species (FullIdentityOfLipid "
            "granularity), preprocessing/lipid_embedding_identity_check.py's own "
            "mean-pooled-over-tokens-then-candidates vector."
        ),
    )
    parser.add_argument(
        "--label", help="Short name for --features, printed as the run header only.",
    )
    parser.add_argument(
        "--descriptors", nargs="?", const="", default=None,
        help="Rank every one of these pair/lipid/protein descriptor names "
             "individually by how lopsidedly it leaks identity (rank_pair_"
             "descriptors -- folded in here from the former analysis/probes/"
             "rank_pair_descriptors.py) instead of running the --features report "
             "above. Comma-separated, no spaces. Bare --descriptors (no value) "
             "ranks the full dataloader.pair_descriptors.PAIR_DESCRIPTOR_NAMES set.",
    )
    parser.add_argument(
        "--zscore", action="store_true",
        help="See analysis/baselines/null_model.py --zscore; forwarded unchanged to feature_similarity.",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="How many highest-eta^2 descriptor rows to print per axis in the global "
             "section (default 20, i.e. all of them for every descriptor set this "
             "project currently has).",
    )
    parser.add_argument(
        "--permutations", type=int, default=999,
        help="Label-reshuffles for the nearest-neighbour, Mantel and per-descriptor "
             "permutation p-values (default 999).",
    )
    parser.add_argument(
        "--seed", type=int, default=0,
        help="Seed for the permutation reshuffles of the modes below.",
    )
    parser.add_argument(
        "--out", default=None,
        help="Where --lipid_classes / --edge_geometry write their full table as CSV.",
    )
    modes = parser.add_argument_group(
        "alternative modes",
        "Each replaces the --features report above with one specific identity question "
        "that used to be its own script in analysis/probes/.",
    )
    modes.add_argument(
        "--lipid_classes", action="store_true",
        help="Which LIPID descriptors are head-group-class fingerprints: eta^2 with its "
             "floor and a permutation p against the fine classes, the four "
             "LIPID_COLDSPLIT_SETS, and each set against the rest, ending in a "
             "neutral/borderline/fingerprint verdict per descriptor.",
    )
    modes.add_argument(
        "--descriptor_set", default="catalog", choices=("catalog", "candidates", "both"),
        help="--lipid_classes only. catalog: LIPID_DESCRIPTOR_NAMES, what the model can "
             "be given today. candidates: the head-group-neutral candidates, cached but "
             "not yet model-facing. both: one table over the union.",
    )
    modes.add_argument(
        "--family_separation", action="append", default=None, metavar="FAMILY",
        help="Which PROTEIN descriptor singles out FAMILY against all the others "
             "(Mann-Whitney outrank plus eta^2 with a permutation p), over every "
             "descriptor in data/protein_descriptor_table.json. Repeatable; bare "
             "--family_separation with no value is not valid, pass a family name "
             "(LBP_BPI_CETP and lipocalin are the usual pair).",
    )
    modes.add_argument(
        "--pair_vs_family", action="store_true",
        help="eta^2 of each PAIR descriptor's actual computed value against protein "
             "family, collapsed to one value per protein (and the row-level number "
             "alongside for context).",
    )
    modes.add_argument(
        "--names", default=None,
        help="--pair_vs_family only: which pair descriptors to measure (default: the "
             "ten descriptors_pair_clean was assembled from).",
    )
    modes.add_argument(
        "--edge_geometry", action="store_true",
        help="eta^2 against family of the per-pocket mean/std of each column of the "
             "25-dim structured protein-EDGE geometry vector.",
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

    for flag, run in (
        ("lipid_classes", run_lipid_classes),
        ("family_separation", run_family_separation),
        ("pair_vs_family", run_pair_vs_family),
        ("edge_geometry", run_edge_geometry),
    ):
        if getattr(args, flag):
            run(args)
            return

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    data_dir = os.path.join(PROJECT_ROOT, "data")

    if args.descriptors is not None:
        descriptor_names = (
            list(PAIR_DESCRIPTOR_NAMES) if args.descriptors == ""
            else [name for name in args.descriptors.split(",") if name]
        )
        pandas.set_option("display.width", 200)
        table = rank_pair_descriptors(csv, data_dir, descriptor_names, args.zscore)
        print(table.round(3).to_string())
        return

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
    elif args.features.lower() == MOLFORMER:
        # Deferred import: lipid_embedding_identity_check imports eta_squared_joint/
        # group_floor/nearest_neighbour_identity_rate/species_class_map FROM this
        # module, so importing it at module load time here would be circular --
        # by the time main() actually runs, this module is already fully defined,
        # so the cycle resolves fine deferred to call time.
        from dataloader.lipid_embedding_store_reader import load_lipid_embedding_store
        from lipid_embedding_identity_check import EMBEDDING_FILE, species_embeddings

        smiles_encoding = load_lipid_embedding_store(data_dir, EMBEDDING_FILE)
        if smiles_encoding is None:
            import pickle
            with open(os.path.join(data_dir, EMBEDDING_FILE), "rb") as handle:
                smiles_encoding = pickle.load(handle)
        vectors, missing_species, missing_keys = species_embeddings(csv, smiles_encoding)
        if missing_species or missing_keys:
            print(
                f"(no molformer embedding for {len(missing_species)} species, "
                f"{len(missing_keys)} distinct missing keys -- excluded)\n"
            )
        entities = sorted(vectors)
        matrix = np.stack([vectors[name] for name in entities])
        column_names = [f"dim{i}" for i in range(matrix.shape[1])]
        entity_column = "FullIdentityOfLipid"
        similarity = _standardised_similarity(matrix)
        index = {entity: position for position, entity in enumerate(entities)}
        label = args.label or MOLFORMER
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
