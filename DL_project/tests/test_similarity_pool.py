import numpy as np
import pandas as pd
import pytest
import torch

from dataloader.similarity_pool import (
    LIPID_COLUMN,
    PAIR_COLUMN,
    PROTEIN_COLUMN,
    SimilarityPool,
    resolve_similarity_pool,
)
from dataloader.sampler import (
    candidate_similarities,
    conditioned_reference,
    sample_family_balanced_negatives,
)
from training.read_configuration import ModelConfig


def one_family_table():
    """One family, one lipid, three proteins -- only P1 binds it.

    The shape a protein-axis pool is asked about: both candidates share lipid L1 with
    P1's positive, so "how like the proteins that bind THIS lipid" has an answer, and it
    differs between them. Note what is NOT needed -- neither candidate's own protein can
    appear in its own reference set, because a row is a candidate exactly when its
    protein does not bind its lipid.
    """
    return pd.DataFrame(
        {
            "Interaction": [1, 0, 0],
            "LTPProtein": ["P1", "P2", "P3"],
            "ProteinDomain": ["A", "A", "A"],
            "FullIdentityOfLipid": ["L1", "L1", "L1"],
        },
        index=[10, 11, 12],
    )


def lipid_axis_table():
    """One protein, three lipids -- the shape the lipid axis has always been asked."""
    return pd.DataFrame(
        {
            "Interaction": [1, 0, 0],
            "LTPProtein": ["P1", "P1", "P1"],
            "ProteinDomain": ["A", "A", "A"],
            "FullIdentityOfLipid": ["L0", "L1", "L2"],
        },
        index=[10, 11, 12],
    )


def protein_pool(similarity_to_p1):
    """A protein-axis pool: P1 against itself, P2 and P3 as given."""
    names = ["P1", "P2", "P3"]
    similarity = np.eye(3, dtype=np.float32)
    similarity[0, 1] = similarity[1, 0] = similarity_to_p1["P2"]
    similarity[0, 2] = similarity[2, 0] = similarity_to_p1["P3"]
    return SimilarityPool(
        similarity,
        {name: position for position, name in enumerate(names)},
        PROTEIN_COLUMN,
        "protein_tmscore",
    )


def test_row_keys_read_the_lipid_column_on_a_lipid_axis():
    table = lipid_axis_table()
    pool = SimilarityPool(np.eye(3, dtype=np.float32), {}, LIPID_COLUMN)

    assert list(pool.row_keys(table)) == ["L0", "L1", "L2"]


def test_row_keys_read_the_protein_column_on_a_protein_axis():
    table = one_family_table()
    pool = SimilarityPool(np.eye(3, dtype=np.float32), {}, PROTEIN_COLUMN)

    assert list(pool.row_keys(table)) == ["P1", "P2", "P3"]


def test_row_keys_read_the_frame_index_on_a_pair_axis():
    table = lipid_axis_table()
    pool = SimilarityPool(np.eye(3, dtype=np.float32), {}, PAIR_COLUMN)

    # The row LABELS, not positions: pair ids survive sampling and splitting, so a
    # slice of the table still indexes the same rows of a pair-granularity matrix.
    assert list(pool.row_keys(table)) == [10, 11, 12]
    assert list(pool.row_keys(table.iloc[1:])) == [11, 12]


def test_hard_mining_on_a_protein_axis_draws_the_closest_protein():
    # P3 scores exactly 0 against the group's only positive protein, so at share=1.0 its
    # weight is 0 and the single-slot quota goes to P2 without a coin flip.
    negatives = sample_family_balanced_negatives(
        one_family_table(),
        seed=3,
        ratio=1,
        hard_negative_pool=protein_pool({"P2": 0.9, "P3": 0.0}),
        hard_negative_share=1.0,
        negative_mode="hard",
    )

    assert list(negatives["LTPProtein"]) == ["P2"]


def test_dissimilar_mining_on_a_protein_axis_draws_the_most_distant_protein():
    # The mirror image: P2 is identical to the only protein binding L1, so its
    # DISTANCE is 0 and the single-slot quota goes to P3.
    negatives = sample_family_balanced_negatives(
        one_family_table(),
        seed=3,
        ratio=1,
        hard_negative_pool=protein_pool({"P2": 1.0, "P3": 0.4}),
        hard_negative_share=1.0,
        negative_mode="dissimilar",
    )

    assert list(negatives["LTPProtein"]) == ["P3"]


def test_a_candidate_is_never_compared_against_its_own_protein():
    """What makes the conditioned reference work at all.

    Against the group's positives, a protein-axis pool scores ~1.0 everywhere: the
    candidate's own protein binds something in the group, and a protein is identical to
    itself. Conditioning on the lipid removes that for free.
    """
    table = one_family_table()
    pool = protein_pool({"P2": 0.9, "P3": 0.0})
    candidates = table[table["Interaction"] == 0]

    reference = conditioned_reference(pool, table)
    sims = candidate_similarities(pool, candidates, table, reference)

    # Only P1 binds L1, so both candidates are measured against P1 alone -- not against
    # themselves, and not against each other.
    assert reference == {"L1": [pool.index["P1"]]}
    assert sims.tolist() == pytest.approx([0.9, 0.0])


def test_the_conditioned_reference_drops_held_out_families():
    """A held-out family's positives must not decide which TRAIN negatives are drawn."""
    table = pd.DataFrame(
        {
            "Interaction": [1, 1, 0],
            "LTPProtein": ["P1", "P2", "P3"],
            "ProteinDomain": ["A", "B", "A"],
            "FullIdentityOfLipid": ["L1", "L1", "L1"],
        },
        index=[10, 11, 12],
    )
    pool = protein_pool({"P2": 0.9, "P3": 0.1})

    with_all = conditioned_reference(pool, table)
    without_b = conditioned_reference(pool, table, excluded_groups=["B"])

    assert with_all == {"L1": sorted([pool.index["P1"], pool.index["P2"]])}
    assert without_b == {"L1": [pool.index["P1"]]}


def test_pool_rejects_an_unknown_source():
    with pytest.raises(ValueError, match="unknown negative-similarity source"):
        resolve_similarity_pool("tanomito", one_family_table(), "data")


def test_pool_reports_a_missing_protein_matrix_with_its_builder(tmp_path):
    with pytest.raises(FileNotFoundError, match="build_protein_tmscore.py"):
        resolve_similarity_pool("protein_tmscore", one_family_table(), tmp_path)


def test_pool_refuses_a_matrix_that_does_not_cover_the_table(monkeypatch):
    import dataloader.similarity_pool as module

    partial = SimilarityPool(
        np.eye(2, dtype=np.float32), {"P1": 0, "P2": 1}, PROTEIN_COLUMN
    )

    class Loaded:
        index = partial.index

        @staticmethod
        def as_float():
            return partial.similarity

    monkeypatch.setattr(module, "load_similarity", lambda *a, **k: Loaded())

    # P3 has no row, so no weight could be computed for its rows.
    with pytest.raises(ValueError, match="no similarity row"):
        resolve_similarity_pool("protein_tmscore", one_family_table(), "data")


def test_default_source_is_tanimoto_so_earlier_runs_are_unchanged():
    assert ModelConfig().negative_similarity == "tanimoto"
    assert ModelConfig().negative_similarity_descriptors == ""


def test_configuration_rejects_an_unknown_source():
    with pytest.raises(ValueError, match="unknown negative_similarity"):
        ModelConfig(
            negative_similarity="tmscore",
            hard_negative_mining=True,
            balance_negatives_by_family=True,
        ).validate()


def test_configuration_rejects_a_source_nothing_steers_by():
    with pytest.raises(ValueError, match="nothing steers it"):
        ModelConfig(negative_similarity="protein_tmscore").validate()


def test_configuration_accepts_a_protein_metric_under_any_balanced_sampler():
    """No grouping restriction: the reference set is cross-family, not per group."""
    for sampler in ("balanced_proteins", "balance_negatives_by_family",
                    "balanced_lipid_classes"):
        ModelConfig(
            negative_similarity="protein_tmscore",
            hard_negative_mining=True,
            **{sampler: True},
        ).validate()


def test_configuration_accepts_a_protein_metric_under_family_balancing():
    config = ModelConfig(
        negative_similarity="protein_blosum62",
        dissimilar_negative_mining=True,
        balance_negatives_by_family=True,
    )
    config.validate()

    assert config.negative_similarity == "protein_blosum62"


def test_configuration_rejects_descriptor_names_without_a_descriptor_source():
    with pytest.raises(ValueError, match="which has its own fixed"):
        ModelConfig(
            negative_similarity="protein_tmscore",
            negative_similarity_descriptors="pocket_extent",
            hard_negative_mining=True,
            balance_negatives_by_family=True,
        ).validate()


def test_configuration_accepts_descriptor_names_for_a_descriptor_source():
    config = ModelConfig(
        negative_similarity="lipid_descriptors",
        negative_similarity_descriptors="chain,unsaturation",
        hard_negative_mining=True,
        balanced_lipid_classes=True,
    )
    config.validate()

    assert config.negative_similarity_descriptors == "chain,unsaturation"


def dataset_stub(**overrides):
    """A PLIDataset carrying only what `_sample_interactions` reads.

    `object.__new__` rather than a real construction: the method under test is the
    sampling decision, and building the real dataset would load graphs, embeddings and
    caches that have nothing to do with it (the convention
    tests/test_new_dataloader_lipid_graphs.py already follows).
    """
    from dataloader.Dataloader import PLIDataset

    dataset = object.__new__(PLIDataset)
    dataset.ROOT_DIR = "data"
    # _sample_interactions hands the config to the pool resolver (only the learned
    # source reads it).
    dataset.config = ModelConfig()
    # `_has_cold_chemistry` is a read-only property over these two.
    dataset.excluded_lipid_classes = set()
    dataset.excluded_lipid_species = set()
    dataset.hard_negative_mining = False
    dataset.dissimilar_negative_mining = False
    dataset.hard_negative_share = 1.0
    dataset.dissimilar_negative_share = 1.0
    dataset.negative_similarity = "tanimoto"
    dataset.negative_similarity_descriptors = ""
    dataset.balanced_lipid_classes = False
    dataset.balanced_proteins = False
    dataset.balance_negatives_by_family = False
    dataset.negatives_per_positive = 1
    dataset.excluded_groups = []
    dataset.balance_excluded_group_negatives = False
    for name, value in overrides.items():
        setattr(dataset, name, value)
    return dataset


def test_the_dataset_steers_its_draw_with_the_requested_pool(monkeypatch):
    """The Dataloader wiring: the flag reaches the sampler and changes the draw."""
    import dataloader.Dataloader as module

    pool = protein_pool({"P2": 0.9, "P3": 0.0})
    asked = {}

    def fake_pool(source, csv, data_dir, names=(), config=None):
        asked["source"] = source
        asked["names"] = names
        return pool

    monkeypatch.setattr(module, "resolve_similarity_pool", fake_pool)
    dataset = dataset_stub(
        hard_negative_mining=True,
        negative_similarity="protein_tmscore",
        balance_negatives_by_family=True,
    )

    positives, negatives = dataset._sample_interactions(one_family_table(), seed=3)

    assert asked == {"source": "protein_tmscore", "names": ()}
    assert list(positives["LTPProtein"]) == ["P1"]
    # P3 scores 0 against the only protein binding L1, so the quota goes to P2.
    assert list(negatives["LTPProtein"]) == ["P2"]


def test_the_dataset_passes_descriptor_names_through_parsed(monkeypatch):
    import dataloader.Dataloader as module

    asked = {}

    def fake_pool(source, csv, data_dir, names=(), config=None):
        asked["names"] = names
        return SimilarityPool(
            np.eye(3, dtype=np.float32),
            {name: position for position, name in enumerate(["L0", "L1", "L2"])},
            LIPID_COLUMN,
            source,
        )

    monkeypatch.setattr(module, "resolve_similarity_pool", fake_pool)
    dataset = dataset_stub(
        dissimilar_negative_mining=True,
        negative_similarity="lipid_descriptors",
        negative_similarity_descriptors="chain, unsaturation",
        balanced_proteins=True,
    )

    dataset._sample_interactions(lipid_axis_table(), seed=3)

    assert asked["names"] == ("chain", "unsaturation")


def test_the_dataset_builds_no_pool_without_a_mining_flag(monkeypatch):
    import dataloader.Dataloader as module

    def refuse(*args, **kwargs):
        raise AssertionError("no pool should be built when nothing steers the draw")

    monkeypatch.setattr(module, "resolve_similarity_pool", refuse)

    positives, negatives = dataset_stub(
        balance_negatives_by_family=True
    )._sample_interactions(one_family_table(), seed=3)

    assert len(positives) == 1
    assert len(negatives) == 1


def cell_prior_pool(subclass_of=None):
    from dataloader.similarity_pool import CellPriorPool

    return CellPriorPool(
        subclass_of or {"L1": "PC", "L2": "PC", "L3": "PE"},
        "protein_subclass_prior",
    )


def prior_table():
    """P1 binds one PC lipid, P2 does not; P3's subclass is unseen in training."""
    return pd.DataFrame(
        {
            "Interaction": [1, 0, 0, 0],
            "LTPProtein": ["P1", "P1", "P2", "P3"],
            "ProteinDomain": ["A", "A", "A", "B"],
            "FullIdentityOfLipid": ["L1", "L2", "L1", "L3"],
        },
        index=[10, 11, 12, 13],
    )


def test_cell_prior_reference_is_the_train_rate_per_protein_subclass_cell():
    from dataloader.sampler import cell_prior_reference

    pool = cell_prior_pool()
    reference = cell_prior_reference(pool, prior_table())

    # P1 has one positive and one negative, both in PC -> 0.5; P2's PC cell is all
    # negative -> 0.0. The fallback is the table's own positive rate, 1 of 4.
    assert reference["rates"]["P1|PC"] == pytest.approx(0.5)
    assert reference["rates"]["P2|PC"] == pytest.approx(0.0)
    assert reference["overall"] == pytest.approx(0.25)


def test_cell_prior_reference_drops_held_out_families():
    from dataloader.sampler import cell_prior_reference

    pool = cell_prior_pool()
    reference = cell_prior_reference(pool, prior_table(), excluded_groups=["B"])

    assert "P3|PE" not in reference["rates"]
    # Family B gone, so the fallback is computed over family A's three rows alone.
    assert reference["overall"] == pytest.approx(1 / 3)


def test_an_uncovered_cell_scores_the_global_rate_not_zero():
    from dataloader.sampler import candidate_similarities, cell_prior_reference

    pool = cell_prior_pool()
    table = prior_table()
    reference = cell_prior_reference(pool, table, excluded_groups=["B"])
    # P3's row was excluded from the rates, so its own cell is unmeasured.
    scores = candidate_similarities(pool, table.loc[[13]], None, reference)

    assert scores.tolist() == pytest.approx([1 / 3])


def test_hard_mining_on_the_naive_prior_draws_the_confusable_cell():
    from dataloader.sampler import sample_protein_balanced_negatives

    # Within P1's group: the L2 candidate sits in P1|PC, the cell the lookup calls
    # positive at 0.5; the L3 candidate sits in P1|PE, which holds no positive at all.
    table = pd.DataFrame(
        {
            "Interaction": [1, 0, 0],
            "LTPProtein": ["P1", "P1", "P1"],
            "ProteinDomain": ["A", "A", "A"],
            "FullIdentityOfLipid": ["L1", "L2", "L3"],
        },
        index=[10, 11, 12],
    )

    drawn = sample_protein_balanced_negatives(
        table, seed=3, ratio=1, hard_negative_pool=cell_prior_pool(),
        hard_negative_share=1.0, negative_mode="hard",
    )

    assert list(drawn["FullIdentityOfLipid"]) == ["L2"]


def test_the_naive_prior_source_is_configurable():
    config = ModelConfig(
        negative_similarity="protein_subclass_prior",
        hard_negative_mining=True,
        balanced_proteins=True,
    )
    config.validate()

    assert config.negative_similarity == "protein_subclass_prior"


def learned_pool(rows=24, features=4, hiddim=8):
    """A LearnedPriorPool over a synthetic feature matrix.

    Built directly rather than through `resolve_similarity_pool`: that path computes the
    real descriptor tables, and a unit test must not depend on the generated dataset.
    """
    from dataloader.similarity_pool import LearnedPriorPool

    rng = np.random.default_rng(0)
    matrix = rng.normal(size=(rows, features))
    return LearnedPriorPool(
        matrix, [f"f{i}" for i in range(features)], ModelConfig(hiddim=hiddim),
        "learned_prior",
    )


def learned_table(rows=24):
    """Half positive, two families -- enough for a fit and for an exclusion to bite."""
    return pd.DataFrame(
        {
            "Interaction": [i % 2 for i in range(rows)],
            "LTPProtein": [f"P{i % 3}" for i in range(rows)],
            "ProteinDomain": ["A" if i < rows // 2 else "B" for i in range(rows)],
            "FullIdentityOfLipid": [f"L{i % 4}" for i in range(rows)],
        },
        index=range(100, 100 + rows),
    )


def test_the_learned_prior_scores_every_row_in_the_unit_interval():
    from dataloader.sampler import learned_prior_reference

    table = learned_table()
    scores = learned_prior_reference(learned_pool(), table, seed=1)

    assert list(scores.index) == list(table.index)
    assert ((scores >= 0.0) & (scores <= 1.0)).all()


def test_fitting_the_learned_prior_leaves_the_global_torch_rng_alone():
    """Otherwise a steered run would also shift model init and the loader's shuffle."""
    from dataloader.sampler import learned_prior_reference

    torch.manual_seed(123)
    before = torch.get_rng_state().clone()
    learned_prior_reference(learned_pool(), learned_table(), seed=1)

    assert torch.equal(torch.get_rng_state(), before)


def test_the_learned_prior_is_reproducible_for_a_seed():
    from dataloader.sampler import learned_prior_reference

    table = learned_table()
    pool = learned_pool()
    first = learned_prior_reference(pool, table, seed=5)
    again = learned_prior_reference(pool, table, seed=5)
    other = learned_prior_reference(pool, table, seed=6)

    assert np.allclose(first.to_numpy(), again.to_numpy())
    assert not np.allclose(first.to_numpy(), other.to_numpy())


def test_the_learned_prior_is_fitted_without_the_held_out_families():
    from dataloader.sampler import learned_prior_reference

    table = learned_table()
    pool = learned_pool()
    everything = learned_prior_reference(pool, table, seed=5)
    without_b = learned_prior_reference(pool, table, excluded_groups=["B"], seed=5)

    # Still one score per row -- family B is dropped from the FIT, not from the scoring.
    assert list(without_b.index) == list(table.index)
    assert not np.allclose(everything.to_numpy(), without_b.to_numpy())


def test_the_learned_prior_steers_the_draw():
    from dataloader.sampler import sample_family_balanced_negatives

    # A pool whose only feature is the label itself: the scorer then separates the two
    # classes perfectly, so "hard" must take the candidate that looks most like a binder.
    from dataloader.similarity_pool import LearnedPriorPool

    table = pd.DataFrame(
        {
            "Interaction": [1, 0, 0],
            "LTPProtein": ["P1", "P2", "P3"],
            "ProteinDomain": ["A", "A", "A"],
            "FullIdentityOfLipid": ["L1", "L2", "L3"],
        },
        index=[10, 11, 12],
    )
    pool = LearnedPriorPool(
        np.array([[1.0], [0.9], [-1.0]]), ["f"], ModelConfig(hiddim=8), "learned_prior"
    )

    drawn = sample_family_balanced_negatives(
        table, seed=3, ratio=1, hard_negative_pool=pool,
        hard_negative_share=1.0, negative_mode="hard",
    )

    assert list(drawn["LTPProtein"]) == ["P2"]


def test_the_learned_prior_source_is_configurable_with_its_own_descriptors():
    config = ModelConfig(
        negative_similarity="learned_prior",
        negative_similarity_descriptors="chain,pocket_extent",
        dissimilar_negative_mining=True,
        balance_negatives_by_family=True,
    )
    config.validate()

    assert config.negative_similarity_descriptors == "chain,pocket_extent"


def suspect_share_dataset(train_frame, root_dir="data"):
    """A PLIDataset carrying only what `_suspect_negative_share` reads."""
    from dataloader.Dataloader import PLIDataset

    dataset = object.__new__(PLIDataset)
    dataset.ROOT_DIR = root_dir
    dataset.csvtrain = train_frame
    return dataset


def test_suspect_negative_share_counts_negatives_in_a_positive_cell(monkeypatch):
    import dataloader.splitting_on_blocks.lipid_subclass_blocks as blocks

    monkeypatch.setattr(
        blocks, "article_subclass_species",
        lambda data_dir=None: {"PC": frozenset({"L1", "L2"}), "PE": frozenset({"L3"})},
    )
    # P1 binds L1 (PC), so its L2 negative shares the P1|PC cell -> suspect.
    # P1's L3 negative is P1|PE, which holds no positive. P2's L2 negative is P2|PC,
    # also no positive. So 1 of 3 negatives is suspect.
    train = pd.DataFrame(
        {
            "Interaction": [1, 0, 0, 0],
            "LTPProtein": ["P1", "P1", "P1", "P2"],
            "FullIdentityOfLipid": ["L1", "L2", "L3", "L2"],
        }
    )

    assert suspect_share_dataset(train)._suspect_negative_share() == pytest.approx(1 / 3)


def test_suspect_negative_share_is_none_without_the_classification(monkeypatch):
    """A missing classification must not stop a run -- this is a diagnostic."""
    import dataloader.splitting_on_blocks.lipid_subclass_blocks as blocks

    def missing(data_dir=None):
        raise FileNotFoundError("lipid_article_classification.json is missing")

    monkeypatch.setattr(blocks, "article_subclass_species", missing)
    train = pd.DataFrame(
        {
            "Interaction": [1, 0],
            "LTPProtein": ["P1", "P1"],
            "FullIdentityOfLipid": ["L1", "L2"],
        }
    )

    assert suspect_share_dataset(train)._suspect_negative_share() is None


def test_suspect_negative_share_is_none_without_negatives(monkeypatch):
    import dataloader.splitting_on_blocks.lipid_subclass_blocks as blocks

    monkeypatch.setattr(
        blocks, "article_subclass_species",
        lambda data_dir=None: {"PC": frozenset({"L1"})},
    )
    train = pd.DataFrame(
        {"Interaction": [1], "LTPProtein": ["P1"], "FullIdentityOfLipid": ["L1"]}
    )

    assert suspect_share_dataset(train)._suspect_negative_share() is None


def test_suspect_negative_share_is_a_reported_table_column():
    import sys

    sys.path.insert(0, "analysis")
    from build_metrics_table import CSV_FIELDS
    from compare_labels import METRICS

    assert "suspect_negative_share" in CSV_FIELDS
    # Listed for display, and as a LOWER-is-better metric.
    assert ("suspect_negative_share", "suspect negatives", False) in METRICS
