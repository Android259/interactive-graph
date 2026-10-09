import json
from pathlib import Path

import pandas as pd
import pytest

import dataloader.pair_descriptor_cache_reader as pair_descriptor_cache
from dataloader.pair_descriptor_cache_reader import (
    lipid_descriptors_csv_path,
    lipid_descriptors_manifest_path,
    load_pair_descriptor_cache,
    load_pair_value_cache,
    pair_descriptors_csv_path,
    pair_descriptors_manifest_path,
    pair_value_cache_is_current,
    store_is_current,
)
from dataloader.cache_builders.pair_descriptor_cache_writer import (
    _compute_one,
    _previous_cache_values,
    build_pair_descriptor_cache,
    build_pair_value_cache,
)
import preprocessing.compute_descriptors as compute_descriptors
from preprocessing.compute_descriptors import descriptor_values_by_row
from dataloader.pocket_lipid_compatibility import chain_lengths_by_row

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
# Two real proteins already used elsewhere in tests/dataloader as fixtures (they ship
# with the repo's data/graphs/, so no synthetic PDB has to be fabricated here).
PROTEINS = [
    name for name in ("BPI", "CRABP2")
    if (DATA_DIR / "graphs" / name / "pocketness.pdb").is_file()
]

pytestmark = pytest.mark.skipif(
    len(PROTEINS) < 2, reason="fixture proteins not present in data/graphs"
)


@pytest.fixture
def fixture_csv():
    return pd.DataFrame({
        "LTPProtein": ["BPI", "CRABP2"],
        # Real, simply-parseable SMILES: an unsaturated fatty acid and an octane chain,
        # covering both a non-None and a chemically distinct case for every measure.
        "SmileGlobal": ["CCCCCCCC/C=C\\CCCCCCCC(=O)O", "CCCCCCCC"],
    })


@pytest.fixture
def clean_cache_files():
    """Give the test an empty lipid_descriptors.csv/.manifest.json, then put back
    whatever real table data/build_pair_descriptor_cache.py had already built there --
    these paths are the live, shared production table (dataloader/pair_descriptor_
    cache.py), not a fixture of this test file, so unlinking without restoring would
    force every grid job launched after the test suite runs to pay the ~12s rebuild
    this table exists to avoid, for files the test itself never touched the content of.
    """
    paths = [lipid_descriptors_csv_path(DATA_DIR), lipid_descriptors_manifest_path(DATA_DIR)]
    saved = {path: path.read_bytes() if path.exists() else None for path in paths}
    for path in paths:
        path.unlink(missing_ok=True)
    yield
    for path in paths:
        path.unlink(missing_ok=True)
        if saved[path] is not None:
            path.write_bytes(saved[path])


@pytest.fixture
def clean_pair_value_cache_files():
    """Same discipline as clean_cache_files, for data/pair_descriptors.csv/.manifest.json."""
    paths = [pair_descriptors_csv_path(DATA_DIR), pair_descriptors_manifest_path(DATA_DIR)]
    saved = {path: path.read_bytes() if path.exists() else None for path in paths}
    for path in paths:
        path.unlink(missing_ok=True)
    yield
    for path in paths:
        path.unlink(missing_ok=True)
        if saved[path] is not None:
            path.write_bytes(saved[path])


@pytest.fixture
def csv_path(fixture_csv):
    """A source CSV under data/ -- _source_record (protein_graph_tensor_cache_writer.py,
    reused by build_pair_descriptor_cache) stores every source path relative to
    root_dir, which only works for a source actually inside it, same as the real
    interaction table (dataloader/dataset_source.interaction_csv_path) always is."""
    path = DATA_DIR / "_test_pair_descriptor_cache_interactions.csv"
    fixture_csv.to_csv(path, index=False)
    yield path
    path.unlink(missing_ok=True)


def test_load_returns_none_without_a_build(clean_cache_files):
    assert store_is_current(DATA_DIR, isomeric=False) is False
    assert load_pair_descriptor_cache(DATA_DIR, isomeric=False) is None


def test_build_then_load_roundtrip(fixture_csv, csv_path, clean_cache_files):
    path, smiles_count, protein_count = build_pair_descriptor_cache(
        DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False
    )
    assert path.exists()
    assert path == lipid_descriptors_csv_path(DATA_DIR)
    assert smiles_count == 2
    assert protein_count == len(PROTEINS)

    assert store_is_current(DATA_DIR, isomeric=False) is True
    cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    assert cache is not None
    # No "proteins" sub-table any more -- that data lives only in
    # data/protein_descriptors.csv (dataloader/chemistry_prior.py).
    assert set(cache) == {"raw_to_canonical", "values"}
    assert len(cache["values"]) == 2


def test_build_pair_value_cache_roundtrip(
    fixture_csv, csv_path, clean_cache_files, clean_pair_value_cache_files
):
    """data/pair_descriptors.csv -- the genuinely joint (lipid x protein) table --
    reads lipid values from data/lipid_descriptors.csv and protein values from
    data/protein_descriptors.csv (built independently by dataloader/chemistry_prior.py)
    and must agree with preprocessing.compute_descriptors.pair_descriptor_value computed
    directly over the same inputs, for every (candidate, protein) pair the fixture
    table actually contains.
    """
    from preprocessing.compute_descriptors import protein_descriptor_table
    from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES
    from preprocessing.compute_descriptors import pair_descriptor_value

    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    assert pair_value_cache_is_current(DATA_DIR, isomeric=False) is False  # not built yet

    path, pair_count = build_pair_value_cache(DATA_DIR, fixture_csv, isomeric=False)
    assert path.exists()
    assert path == pair_descriptors_csv_path(DATA_DIR)
    # One row per (candidate, protein): 2 fixture rows, each naming exactly one
    # protein and one candidate SMILES, and both candidates resolve.
    assert pair_count == 2

    assert pair_value_cache_is_current(DATA_DIR, isomeric=False) is True
    loaded = load_pair_value_cache(DATA_DIR, isomeric=False)
    assert loaded is not None
    assert len(loaded) == 2

    lipid_cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    protein_table = protein_descriptor_table(str(DATA_DIR))
    for (smiles, protein), values in loaded.items():
        lv = lipid_cache["values"][smiles]
        lipid_input = {
            "chain": lv["chain"], "unsaturation": lv["unsaturation"],
            "hbond": lv["hbond"], "heavy": lv["heavy_atoms"],
            "tail_count": lv["tail_count"],
            "npr1": lv["npr1"], "npr2": lv["npr2"],
        }
        expected = {
            name: pair_descriptor_value(name, lipid_input, protein_table[protein])
            for name in PAIR_DESCRIPTOR_NAMES
        }
        for name in PAIR_DESCRIPTOR_NAMES:
            assert values[name] == pytest.approx(expected[name]), (smiles, protein, name)


def test_store_goes_stale_when_source_csv_changes(fixture_csv, csv_path, clean_cache_files):
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    assert store_is_current(DATA_DIR, isomeric=False) is True

    # A later mtime AND a different size on the exact source file the manifest
    # recorded, same discipline protein_graph_tensor_cache_reader's own staleness check uses.
    with open(csv_path, "a") as handle:
        handle.write("\n")
    # A rebuild is still due: a regenerated table may name candidates the cache has
    # never seen, and only a build can add them.
    assert store_is_current(DATA_DIR, isomeric=False) is False
    # But the per-SMILES values survive it. They are keyed by canonical SMILES and
    # depend on no table at all, so throwing them away here bought nothing and cost a
    # full RDKit recompute in every reader until somebody reran the builder -- the
    # failure this split (strict for "rebuild?", per-measure for "serve?") removes.
    cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    assert cache is not None
    assert len(cache["values"]) == 2
    # And a candidate the cache has never seen still falls back per miss, which is what
    # makes serving the old values safe rather than merely cheap.
    assert "totally-new-smiles" not in cache["raw_to_canonical"]



def test_cached_values_match_uncached_computation(fixture_csv, csv_path, clean_cache_files):
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    assert cache is not None

    chain_cached = chain_lengths_by_row(fixture_csv, isomeric=False, cache=cache)
    chain_direct = chain_lengths_by_row(fixture_csv, isomeric=False)
    assert chain_cached == chain_direct

    for measure in ("unsaturation", "hbond", "heavy_atoms"):
        cached = descriptor_values_by_row(fixture_csv, measure, isomeric=False, cache=cache)
        direct = descriptor_values_by_row(fixture_csv, measure, isomeric=False)
        assert cached == direct


def test_unseen_candidate_falls_back_to_direct_computation(fixture_csv, csv_path, clean_cache_files):
    """A candidate absent from the cache (added to the table after it was built) is
    still computed correctly, not silently dropped or left None."""
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)

    extended = pd.concat([
        fixture_csv,
        pd.DataFrame({"LTPProtein": ["BPI"], "SmileGlobal": ["CCCCCCCCCC"]}),
    ], ignore_index=True)

    cached = chain_lengths_by_row(extended, isomeric=False, cache=cache)
    direct = chain_lengths_by_row(extended, isomeric=False)
    assert cached == direct
    assert cached[-1] != [None]


def test_compute_one_reuses_seeded_measures_and_only_computes_missing_ones():
    # A new _MEASURES entry (any future descriptor) must not force re-embedding a
    # measure that is already correct in whatever cache existed before -- otherwise
    # adding ONE cheap descriptor pays for every existing expensive one all over
    # again, every single time.
    key = "CCO"  # ethanol: trivially fast even if genuinely (re)computed
    seed_entry = {
        "unsaturation": 999.0, "hbond": 999.0, "heavy_atoms": 999.0, "tail_count": 999.0,
        "radius_of_gyration": 999.0, "asphericity": 999.0, "molecular_volume": 999.0,
        "rotatable_fraction": 999.0,
        # npr1/npr2 deliberately absent -- simulates a cache built before they existed.
    }
    _, entry = _compute_one(key, seed_entry)
    for measure in seed_entry:
        assert entry[measure] == 999.0, f"{measure} should have been reused from the seed"
    assert entry["npr1"] is not None and entry["npr1"] != 999.0
    assert entry["npr2"] is not None and entry["npr2"] != 999.0


def test_compute_one_computes_everything_fresh_without_a_seed():
    # Ethanol: two carbons, so it has no acyl tail at all. Every measure must still be
    # a KEY -- that is the invariant the cache rests on, since a reader tests
    # `measure in entry` and a silently absent one would read as "not cached" forever.
    _, entry = _compute_one("CCO", seed_entry=None)
    assert set(entry) == {"chain", *compute_descriptors._MEASURES}
    tail_only = set(compute_descriptors.CANDIDATE_LIPID_DESCRIPTOR_NAMES)
    # experimental_lipid_volume is a data/Lipid_Volumes.xlsx lookup, not an RDKit
    # formula -- unlike every other name here, it is legitimately None for anything
    # RDKit parses fine but the sheet never measured (ethanol included), so it does
    # not share this test's "always resolves" invariant even though it is promoted
    # into LIPID_DESCRIPTOR_NAMES.
    always_resolves = {"experimental_lipid_volume"} | tail_only
    assert all(
        value is not None
        for name, value in entry.items()
        if name not in always_resolves
    )

    # A real lipid: now the tail measures have values too. tail_double_bond_position is
    # the one that stays None even here when the tails are fully saturated -- the
    # position of a double bond that does not exist, absent rather than zero.
    _, lipid = _compute_one(
        "CCCCCCCCCCCCCCCC(=O)OCC(O)COP(=O)(O)OCC[N+](C)(C)C", seed_entry=None
    )
    assert set(lipid) == {"chain", *compute_descriptors._MEASURES}
    assert lipid["tail_double_bond_position"] is None
    assert all(
        lipid[name] is not None
        for name in tail_only
        if name != "tail_double_bond_position"
    )


def test_previous_cache_values_reads_the_existing_table(tmp_path):
    # Simulates a table already built by an earlier run -- seeding must read it back
    # whatever is in it, since that is the only thing there is to seed from.
    table = pd.DataFrame([
        {"smiles": "CCO", "isomeric": False, "chain": 2.0, "unsaturation": 0.0},
        {"smiles": "CCCCCCCC", "isomeric": True, "chain": 8.0, "unsaturation": 0.0},
    ])
    table.to_csv(tmp_path / "lipid_descriptors.csv", index=False)

    seed = _previous_cache_values(tmp_path, isomeric=False)
    assert seed == {"CCO": {"chain": 2.0, "unsaturation": 0.0}}
    # The isomeric variant's row is excluded from a deterministic-variant seed.
    assert "CCCCCCCC" not in seed

    seed_isomeric = _previous_cache_values(tmp_path, isomeric=True)
    assert seed_isomeric == {"CCCCCCCC": {"chain": 8.0, "unsaturation": 0.0}}


def test_previous_cache_values_empty_with_no_existing_file(tmp_path):
    assert _previous_cache_values(tmp_path, isomeric=False) == {}


def test_build_pair_descriptor_cache_seeds_expensive_measures_across_a_code_change(
    fixture_csv, csv_path, clean_cache_files, monkeypatch
):
    # First build under "old" code: pretend npr1/npr2 do not exist yet. Patched on
    # dataloader.pair_descriptors itself, the module _compute_one's own _MEASURES
    # name is bound from at import time in dataloader/cache_builders/pair_descriptor_
    # cache.py -- patching there is what that module actually reads.
    import dataloader.cache_builders.pair_descriptor_cache_writer as cache_builder

    original_measures = dict(cache_builder._MEASURES)
    monkeypatch.setattr(
        cache_builder, "_MEASURES",
        {k: v for k, v in original_measures.items() if k not in ("npr1", "npr2")},
    )
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    old_cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    old_values = old_cache["values"]

    # Now "add" npr1/npr2 back (a code change) and rebuild -- every OTHER measure's
    # value must survive unchanged (reused, not re-embedded), and npr1/npr2 must be
    # freshly present.
    monkeypatch.setattr(cache_builder, "_MEASURES", original_measures)
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    new_cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    new_values = new_cache["values"]

    assert set(new_values) == set(old_values)
    for key, old_entry in old_values.items():
        new_entry = new_values[key]
        for measure in old_entry:
            assert new_entry[measure] == old_entry[measure], (
                f"{measure} for {key} changed across a rebuild that only ADDED measures"
            )
        assert new_entry["npr1"] is not None
        assert new_entry["npr2"] is not None


def test_manifest_has_no_non_serialisable_values(fixture_csv, csv_path, clean_cache_files):
    path, _, _ = build_pair_descriptor_cache(
        DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False
    )
    assert path.exists()
    # Round-trips through json.loads without error -- a numpy scalar (e.g. int64/
    # float64, as opposed to plain int/float) in raw_to_canonical would have made
    # json.dumps raise inside build_pair_descriptor_cache itself, before this point.
    manifest_path = lipid_descriptors_manifest_path(DATA_DIR)
    json.loads(manifest_path.read_text())
    # And the CSV itself must be a valid, readable table.
    pd.read_csv(path)
