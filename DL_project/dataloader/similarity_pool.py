"""Share a similarity matrix, name-to-index map, and entity axis.

chemistry_prior.py builds the matrices; this module selects them and defines
the axis contract. sampler.py uses pools for --negative_similarity, comparing
candidates with positives. The pool itself is not specific to negatives.

Axes:
FullIdentityOfLipid: Tanimoto, MolFormer, lipid descriptors.
LTPProtein: three protein matrices or protein descriptors.
pair_id (row label): descriptors spanning both partners.

The axis also selects reference positives. See SimilarityPool.condition_column
and sampler.conditioned_reference for the required conditioning.
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
# Default descriptor sets for --negative_similarity_descriptors.
# An explicit list overrides them; naming both partners selects the pair axis.
DESCRIPTOR_SOURCES = {
    "lipid_descriptors": LIPID_DESCRIPTOR_NAMES,
    "protein_descriptors": PROTEIN_DESCRIPTOR_NAMES,
}
# Naive label-prior sources provide per-candidate scores.
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
        """Return the coordinate shared with reference positives, or None.

        Lipid/pair pools use the sampling group's positives (None): lipids similar
        to those this protein or family binds.
        Protein pools condition on lipid: proteins that bind the candidate's lipid.
        Using the group's proteins instead gives similarity 1.0 almost everywhere,
        because it includes the candidate's own protein.
        See sampler.conditioned_reference for measurements and leakage exclusions.
        """
        return LIPID_COLUMN if self.column == PROTEIN_COLUMN else None

    def row_keys(self, frame):
        """Return each frame row's key on this pool's entity axis.

        Pair pools use frame.index: feature_similarity uses csv.index, and sampler
        frames retain those labels through sampling/splitting (dataloader/AGENTS.md).
        """
        if self.column == PAIR_COLUMN:
            return frame.index
        return frame[self.column]

    def covers(self, frame):
        """The keys of `frame` that this pool has no row for."""
        return sorted({key for key in self.row_keys(frame) if key not in self.index})


class LearnedPriorPool:
    """Score candidate pairs with a small descriptor MLP fitted before training.

    Replace CellPriorPool's lookup with architecture.mlp_utils.build_mlp.
    Steer toward likely binders to select negatives the cheap scorer confuses
    with positives.

    Fit on training labels and freeze, as in chemistry_prior.fit_prior_calibration.
    Joint scorer/encoder optimization leaves their contributions undetermined;
    the network can take whichever route reduces loss first. This is not KBGAN's
    REINFORCE loop: updating from current model confusion would require draws
    inside the epoch loop.

    The MLP only selects rows and is discarded. It adds no parameters to the
    scored model; number_of_parameters stays comparable to the base configuration.
    """

    kind = "learned_prior"
    # Key per-row scores by row label, like pair-descriptor matrices.
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
    """Score candidates by the training positive rate of (protein, lipid subclass).

    A high score selects negatives sharing a cell with known binders, testing
    whether the network improves on the lookup. This differs from matrix pools,
    which compare similarity to positives.

    On --lipid_species_coldsplit=0.15, the recorded lookup test BA was
    0.871 +/- 0.009 versus network 0.902. Lipid-only lookups scored 0.570 by
    species and 0.539 by head-group class (lipid_marginal_baseline.py).
    See files/proposals/species15_information_above_protein_subclass.md section 1
    and analysis/baselines/protein_subclass_label_baseline.py.

    Store only species-to-subclass membership here. sampler.cell_prior_reference
    builds rates and applies conditioned_reference's leakage rule, since the
    sampler knows excluded_groups.
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
    """Build the pool selected by --negative_similarity.

    Raise on missing artifacts. A uniform fallback would misreport a steered run:
    vars(conf) records the requested configuration in the run report.
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
        # Naming both partners gives one feature row per interaction-table row,
        # in table order, matching per-candidate score keys.
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
        # Validate structures, then check protein coverage with covers.
        # Do not reject a 35 x 35 matrix for interaction-table mtime changes that
        # leave the protein set unchanged.
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
