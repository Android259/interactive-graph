"""One pairwise-similarity matrix, the index into it, and the axis it is keyed on.

Not named for negatives, and deliberately so: a candidate is weighted by how similar it
is to the POSITIVES it should be confusable with, so this holds the comparison against
positives, not a property of negatives. What is negative-specific is the one consumer --
`dataloader/sampler.py`'s steered draw, configured by `--negative_similarity` -- and
nothing in here knows about it. The builders come from
`dataloader/chemistry_prior.py`, which already owned every one of them; this module adds
only the choice between them and the axis contract that makes the choice usable.

A `SimilarityPool` carries the matrix, the name -> row index, and the COLUMN of the
interaction table that names one entity of it. Three axes follow from the sources, and
the sampler treats all three alike:

    FullIdentityOfLipid   tanimoto, molformer, lipid descriptors
    LTPProtein            the three protein-similarity matrices, protein descriptors
    pair_id (row label)   a descriptor set naming both sides, which neither the lipid
                          nor the protein alone determines

The axis also decides WHICH positives a candidate is compared against, because the two
are not symmetric: see `SimilarityPool.condition_column` here and
`dataloader.sampler.conditioned_reference` for the measurement that forced it.
"""

import os

from dataloader.chemistry_prior import (
    feature_similarity,
    raw_feature_matrix,
    molformer_species_similarity,
    species_similarity,
)
from dataloader.descriptors import (
    LIPID_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
)
from preprocessing.similarity.protein_similarity_common import (
    METRIC_PREFIX,
    load_similarity,
    similarity_paths,
)


LIPID_COLUMN = "FullIdentityOfLipid"
PROTEIN_COLUMN = "LTPProtein"
PAIR_COLUMN = "pair_id"

# source name -> the metric file set under data/cache/protein_similarity/, built by
# preprocessing/similarity/build_protein_sequence_similarity.py and build_protein_tmscore.py.
PROTEIN_METRIC_SOURCES = {
    "protein_identity": "identity",
    "protein_blosum62": "blosum62",
    "protein_tmscore": "tmscore",
}
# source name -> the descriptor set it defaults to when --negative_similarity_descriptors
# names none. Any explicit name list overrides it, including one spanning both sides,
# which moves the axis to the pair.
DESCRIPTOR_SOURCES = {
    "lipid_descriptors": LIPID_DESCRIPTOR_NAMES,
    "protein_descriptors": PROTEIN_DESCRIPTOR_NAMES,
}
# Naive label-prior sources: a per-candidate score rather than a pairwise matrix.
PRIOR_SOURCES = ("protein_subclass_prior", "learned_prior")
# Sources that take a descriptor name list through --negative_similarity_descriptors.
NAMED_FEATURE_SOURCES = ("lipid_descriptors", "protein_descriptors", "learned_prior")
NEGATIVE_SIMILARITY_SOURCES = (
    ("tanimoto", "molformer")
    + tuple(DESCRIPTOR_SOURCES)
    + tuple(PROTEIN_METRIC_SOURCES)
    + PRIOR_SOURCES
)


class SimilarityPool:
    """A similarity matrix, its name -> row index, and the column its names come from."""

    kind = "similarity"

    def __init__(self, similarity, index, column=LIPID_COLUMN, source="tanimoto"):
        self.similarity = similarity
        self.index = index
        self.column = column
        self.source = source

    @property
    def condition_column(self):
        """The coordinate a candidate must SHARE with the positives it is compared to.

        None means the comparison is against the sampling group's own positives, which
        is what a lipid-axis (and a pair-axis) pool wants: the group is a protein or a
        family of them, so "close to anything this group binds" already reads as "a
        lipid like the ones this protein binds".

        A protein-axis pool cannot use that reference -- it scores 1.0 almost everywhere,
        since a candidate's own protein is one of the group's positive proteins. It
        conditions on the LIPID instead, making the question the mirror of the lipid
        axis': how like the proteins that bind THIS lipid is the candidate's protein.
        `dataloader.sampler.conditioned_reference` carries the measurement that forced
        this and the leakage rule that bounds it.
        """
        return LIPID_COLUMN if self.column == PROTEIN_COLUMN else None

    def row_keys(self, frame):
        """One index key per row of `frame`, on this pool's own axis.

        The pair axis reads the frame's INDEX rather than a column: `feature_similarity`
        keys a pair-granularity matrix by `csv.index`, and every frame the sampler hands
        back is a slice of that same table, so the labels still line up after sampling
        and splitting (the invariant `dataloader/AGENTS.md` states for pair IDs).
        """
        if self.column == PAIR_COLUMN:
            return frame.index
        return frame[self.column]

    def covers(self, frame):
        """The keys of `frame` that this pool has no row for."""
        return sorted({key for key in self.row_keys(frame) if key not in self.index})


class LearnedPriorPool:
    """The naive prior's learned counterpart: a small MLP that predicts a pair's label.

    Same job as `CellPriorPool` -- score every candidate by how much it looks like a
    real binder to a cheap predictor, so the steered quota fills with the pairs that
    predictor cannot separate -- with the lookup table replaced by
    `architecture.mlp_utils.build_mlp`, the standard block every other MLP in this
    project is built from, over the descriptor catalog.

    Why it is FIT BEFORE the run and then frozen, rather than trained against the
    network KBGAN-style: `dataloader.chemistry_prior.fit_prior_calibration` already
    states this project's reason, and it applies unchanged here. A cheap scorer and a
    many-parameter encoder competing by gradient descent to explain the SAME variance is
    underdetermined -- nothing pins the split between them -- and this network is already
    known to take whichever route reaches the loss first. Fitting on train labels alone,
    before the network sees a gradient, removes the ambiguity. What this therefore does
    NOT do is update the generator from the network's own current confusion, which is the
    one thing KBGAN's REINFORCE loop buys; that needs the draw moved inside the epoch
    loop and is not what this class is.

    Adds nothing to the scored model: the MLP lives here, picks rows, and is discarded.
    `number_of_parameters` is the base configuration's, so a steered run stays directly
    comparable with it -- the same property the naive prior has.
    """

    kind = "learned_prior"
    # One score per interaction-table row, so the row label is the key, exactly as a
    # pair-granularity descriptor matrix is keyed.
    column = PAIR_COLUMN
    condition_column = None

    def __init__(self, features, feature_names, config, source):
        self.features = features
        self.feature_names = tuple(feature_names)
        self.config = config
        self.source = source
        self.index = {}

    def row_keys(self, frame):
        return frame.index

    def covers(self, frame):
        return []


class CellPriorPool:
    """A naive (protein, lipid subclass) label prior, as a per-candidate score.

    The other pool kind answers "how like the positives is this candidate". This one
    answers the question the project's own strongest naive competitor answers: "would a
    lookup table of train labels call this cell positive at all". Steering toward a high
    score therefore fills the quota with the pairs that competitor cannot tell from real
    binders -- same protein, same subclass as something it binds -- which is exactly the
    contrast a network has to win to be worth more than the lookup.

    Why this prior and not another naive one: on `--lipid_species_coldsplit=0.15` it is
    the strongest naive predictor on record, test BA 0.871 +- 0.009 against the network's
    own 0.902 (files/proposals/species15_information_above_protein_subclass.md section 1,
    measured by analysis/baselines/protein_subclass_label_baseline.py). The label-only
    lipid lookups are far weaker on their own axis -- per-species 0.570, per-head-group
    class 0.539 test BA (preprocessing/lipid_marginal_baseline.py) -- so they have much
    less to confuse a model with.

    Carries only the species -> subclass map. The rates themselves are built in
    `dataloader.sampler.cell_prior_reference`, with the same leakage rule
    `conditioned_reference` uses, because only the sampler knows `excluded_groups`.
    """

    kind = "cell_prior"
    column = PROTEIN_COLUMN
    condition_column = None

    def __init__(self, subclass_of, source):
        self.subclass_of = subclass_of
        self.source = source
        self.index = subclass_of

    def cell_keys(self, frame):
        """The (protein, subclass) key of every row, the baseline script's own join."""
        subclass = (
            frame[LIPID_COLUMN].map(self.subclass_of).fillna("?unclassified")
        )
        return frame[PROTEIN_COLUMN].astype(str) + "|" + subclass.astype(str)

    def covers(self, frame):
        return []


def resolve_similarity_pool(source, csv, data_dir, descriptor_names=(), config=None):
    """Build the `SimilarityPool` named by `--negative_similarity`.

    Raises rather than falling back when a source's artifacts are missing: a steered run
    that silently drew uniformly would be recorded as steered, and
    `number_of_parameters`-style identity of past runs is not the only thing that has to
    stay honest -- `vars(conf)` goes into the run report.
    """
    if source not in NEGATIVE_SIMILARITY_SOURCES:
        raise ValueError(
            f"unknown negative-similarity source {source!r}; expected one of "
            f"{', '.join(NEGATIVE_SIMILARITY_SOURCES)}"
        )

    if source == "learned_prior":
        if config is None:
            raise ValueError(
                "negative_similarity=learned_prior fits an MLP built with the run's own "
                "--hiddim/--m/--dropout conventions, so it needs the config"
            )
        names = tuple(descriptor_names) or (
            tuple(LIPID_DESCRIPTOR_NAMES) + tuple(PROTEIN_DESCRIPTOR_NAMES)
        )
        # Naming both sides puts raw_feature_matrix at PAIR granularity: one feature row
        # per interaction-table row, in the table's own order, which is what a
        # per-candidate score has to be keyed by.
        entities, features, entity_column, columns = raw_feature_matrix(
            csv, data_dir, names
        )
        if entity_column != PAIR_COLUMN:
            raise ValueError(
                "negative_similarity=learned_prior needs descriptor names spanning both "
                f"the lipid and the protein side; {list(names)[:4]}... resolved to "
                f"{entity_column} granularity, which gives one score per "
                f"{entity_column} rather than per pair"
            )
        return LearnedPriorPool(features, columns, config, source)

    if source in PRIOR_SOURCES:
        from dataloader.splitting_on_blocks.lipid_subclass_blocks import (
            article_subclass_species,
        )

        subclass_of = {}
        for subclass, species in article_subclass_species(data_dir).items():
            for name in species:
                subclass_of[name] = subclass
        return CellPriorPool(subclass_of, source)

    if source == "tanimoto":
        similarity, index = species_similarity(csv, data_dir)
        pool = SimilarityPool(similarity, index, LIPID_COLUMN, source)
    elif source == "molformer":
        matrix_path = os.path.join(data_dir, "molformer_species_similarity_matrix.npy")
        if not os.path.isfile(matrix_path):
            raise FileNotFoundError(
                f"{matrix_path} is missing; build it with "
                "python3 preprocessing/build_molformer_similarity_matrix.py"
            )
        similarity, index = molformer_species_similarity(data_dir)
        pool = SimilarityPool(similarity, index, LIPID_COLUMN, source)
    elif source in DESCRIPTOR_SOURCES:
        names = tuple(descriptor_names) or tuple(DESCRIPTOR_SOURCES[source])
        similarity, index, entity_column = feature_similarity(csv, data_dir, names)
        pool = SimilarityPool(similarity, index, entity_column, source)
    else:
        metric = PROTEIN_METRIC_SOURCES[source]
        # Structures checked, the interaction table deliberately not: what this matrix
        # has to cover is the PROTEIN SET, and `covers` below reads that off the table
        # directly. Refusing on the table's mtime instead would reject a perfectly good
        # 35 x 35 matrix over an edit that never touched which proteins exist.
        loaded = load_similarity(data_dir, metric, data_dir=data_dir)
        if loaded is None:
            matrix_path, _, _ = similarity_paths(data_dir, metric)
            builder = (
                "preprocessing/similarity/build_protein_tmscore.py"
                if metric == "tmscore"
                else "preprocessing/similarity/build_protein_sequence_similarity.py"
            )
            raise FileNotFoundError(
                f"{METRIC_PREFIX[metric]}_* is missing or stale under "
                f"{matrix_path.parent}; build it with python3 {builder}"
            )
        pool = SimilarityPool(
            loaded.as_float(), loaded.index, PROTEIN_COLUMN, source
        )

    missing = pool.covers(csv)
    if missing:
        raise ValueError(
            f"negative_similarity={source} has no similarity row for "
            f"{len(missing)} of the table's {pool.column} values "
            f"(first: {missing[0]!r}); it cannot steer a draw over rows it cannot see"
        )
    return pool


def pool_report(pool):
    """One line naming what a run is steering by, for the dataset's own log."""
    return (
        f"negative similarity : {pool.source} over {len(pool.index)} "
        f"{pool.column} entities"
    )
