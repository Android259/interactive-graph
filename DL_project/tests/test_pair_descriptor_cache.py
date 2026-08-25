import json
from pathlib import Path

import pandas as pd
import pytest

from dataloader.pair_descriptor_cache import (
    build_pair_descriptor_cache,
    cache_path,
    load_pair_descriptor_cache,
    store_is_current,
)
from dataloader.pair_descriptors import descriptor_values_by_row
from dataloader.pocket_lipid_compatibility import (
    chain_lengths_by_row,
    pocket_extent_by_protein,
    pocket_rim_core_aromatic_share_by_protein,
)

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
    """Give the test an empty cache_path(DATA_DIR, ...), then put back whatever real
    cache data/build_pair_descriptor_cache.py had already built there -- these paths
    are the live, shared production cache (dataloader/pair_descriptor_cache.py), not a
    fixture of this test file, so unlinking without restoring would force every grid
    job launched after the test suite runs to pay the ~12s rebuild this cache exists to
    avoid, for a file the test itself never touched the content of.
    """
    paths = [cache_path(DATA_DIR, isomeric) for isomeric in (False, True)]
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
    """A source CSV under data/ -- _source_record (protein_graph_tensor_cache.py,
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
    assert smiles_count == 2
    assert protein_count == len(PROTEINS)

    assert store_is_current(DATA_DIR, isomeric=False) is True
    cache = load_pair_descriptor_cache(DATA_DIR, isomeric=False)
    assert cache is not None
    assert set(cache) == {"raw_to_canonical", "values", "proteins"}
    assert len(cache["values"]) == 2
    assert set(cache["proteins"]) == set(PROTEINS)
    for protein in PROTEINS:
        entry = cache["proteins"][protein]
        assert set(entry) == {"extent", "aromatic_share_core", "aromatic_share_rim"}


def test_store_goes_stale_when_source_csv_changes(fixture_csv, csv_path, clean_cache_files):
    build_pair_descriptor_cache(DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False)
    assert store_is_current(DATA_DIR, isomeric=False) is True

    # A later mtime AND a different size on the exact source file the manifest
    # recorded, same discipline protein_graph_tensor_cache's own staleness check uses.
    with open(csv_path, "a") as handle:
        handle.write("\n")
    assert store_is_current(DATA_DIR, isomeric=False) is False
    assert load_pair_descriptor_cache(DATA_DIR, isomeric=False) is None


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

    extents_cached = pocket_extent_by_protein(DATA_DIR, PROTEINS, cache=cache["proteins"])
    extents_direct = pocket_extent_by_protein(DATA_DIR, PROTEINS)
    assert extents_cached == extents_direct

    shares_cached = pocket_rim_core_aromatic_share_by_protein(
        DATA_DIR, PROTEINS, cache=cache["proteins"]
    )
    shares_direct = pocket_rim_core_aromatic_share_by_protein(DATA_DIR, PROTEINS)
    assert shares_cached == shares_direct


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


def test_json_payload_has_no_non_serialisable_values(fixture_csv, csv_path, clean_cache_files):
    path, _, _ = build_pair_descriptor_cache(
        DATA_DIR, fixture_csv, PROTEINS, csv_path, isomeric=False
    )
    # Round-trips through json.loads without error -- a numpy scalar (e.g. int64/
    # float64, as opposed to plain int/float) would have made json.dumps raise inside
    # build_pair_descriptor_cache itself, before this point.
    json.loads(path.read_text())
