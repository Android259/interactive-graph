import numpy as np
import pytest

from dataloader.pocket_lipid_compatibility import coarsen_to_levels
from dataloader.pair_descriptors import (
    BOUNDED_SHARE_DESCRIPTOR_NAMES,
    CoarseSpec,
    DEFAULT_COARSE_SPECS,
    DESCRIPTOR_CATALOG,
    PAIR_DESCRIPTOR_NAMES,
    acyl_chain_count,
    canonical_descriptor_token,
    longest_acyl_chain,
    pair_descriptor_value,
    parse_descriptor_list,
    parse_descriptor_token,
    resolve_requested_tokens,
)

# Two same-length-tailed test molecules: DOPC (two C18 oleoyl tails) and its
# single-tailed lyso form -- the concrete case that motivated tail_count existing
# at all (longest_acyl_chain alone cannot tell them apart).
_DOPC = (
    "CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(COP(=O)([O-])OCC[N+](C)(C)C)"
    "OC(=O)CCCCCCC/C=C\\CCCCCCCC"
)
_LYSO_PC = "CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(O)COP(=O)([O-])OCC[N+](C)(C)C"
_TRISTEARIN = (
    "CCCCCCCCCCCCCCCCCC(=O)OCC(OC(=O)CCCCCCCCCCCCCCCCC)"
    "COC(=O)CCCCCCCCCCCCCCCCC"
)


def test_acyl_chain_count_distinguishes_one_and_two_tailed_lipids():
    assert longest_acyl_chain(_DOPC) == longest_acyl_chain(_LYSO_PC) == 18
    assert acyl_chain_count(_DOPC) == 2.0
    assert acyl_chain_count(_LYSO_PC) == 1.0
    assert acyl_chain_count(_TRISTEARIN) == 3.0


def test_acyl_chain_count_matches_longest_acyl_chain_on_missing_data():
    unparseable = "not a smiles"
    assert longest_acyl_chain(unparseable) is None
    assert acyl_chain_count(unparseable) is None


def test_tail_elongation_fit_is_in_the_catalog():
    assert "tail_elongation_fit" in PAIR_DESCRIPTOR_NAMES
    assert "tail_elongation_fit" in DESCRIPTOR_CATALOG


def test_tail_elongation_fit_favours_round_pockets_for_multi_tailed_lipids():
    # A round pocket (elongation near 1) should read multi-tailed lipids as a
    # better fit than a narrow channel (high elongation) does, for the SAME tail
    # count -- that is the whole point of pairing tail_count against elongation
    # rather than pocket size.
    two_tails = {"tail_count": 2.0}
    round_pocket = {"pocket_elongation": 1.1}
    narrow_pocket = {"pocket_elongation": 2.2}
    round_score = pair_descriptor_value("tail_elongation_fit", two_tails, round_pocket)
    narrow_score = pair_descriptor_value("tail_elongation_fit", two_tails, narrow_pocket)
    assert round_score > narrow_score


def test_tail_elongation_fit_guards_the_degenerate_zero_elongation_case():
    # pocket_shape (protein_graph_builder.py) returns elongation=0.0 for a cavity
    # with fewer than 4 pocket atoms -- dividing by that directly would inflate
    # the score instead of reading as "no usable shape information".
    lipid = {"tail_count": 3.0}
    degenerate_pocket = {"pocket_elongation": 0.0}
    assert pair_descriptor_value("tail_elongation_fit", lipid, degenerate_pocket) == 3.0


def test_parse_descriptor_token_bare_name():
    assert parse_descriptor_token("chain") == ("chain", None)


def test_parse_descriptor_token_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unknown descriptor"):
        parse_descriptor_token("not_a_real_descriptor")


@pytest.mark.parametrize(
    "token,expected",
    [
        ("aromatic_share_coarse=5", ("aromatic_share", CoarseSpec("fixed", 5))),
        ("hydropathy_core_coarse=quantiles", ("hydropathy_core", CoarseSpec("quantiles", 3))),
        ("pocket_extent_coarse=quantiles:7", ("pocket_extent", CoarseSpec("quantiles", 7))),
    ],
)
def test_parse_descriptor_token_coarse_forms(token, expected):
    assert parse_descriptor_token(token) == expected


@pytest.mark.parametrize(
    "bad_token",
    [
        "aromatic_share_coarse=1",  # below the N >= 2 floor
        "aromatic_share_coarse=abc",
        "aromatic_share_coarse=quantiles:1",  # quantiles floor is also 2
        "not_a_real_descriptor_coarse=5",  # unknown base name
    ],
)
def test_parse_descriptor_token_rejects_bad_coarse_specs(bad_token):
    with pytest.raises(ValueError):
        parse_descriptor_token(bad_token)


def test_canonical_descriptor_token_dedupes_bare_and_explicit_default_quantiles():
    bare = canonical_descriptor_token(*parse_descriptor_token("hydropathy_core_coarse=quantiles"))
    explicit = canonical_descriptor_token(
        *parse_descriptor_token("hydropathy_core_coarse=quantiles:3")
    )
    assert bare == explicit == "hydropathy_core_coarse=quantiles:3"


def test_parse_descriptor_list_is_comma_separated_and_canonical():
    tokens = parse_descriptor_list("chain, aromatic_share_coarse=5 ,heavy_coarse=quantiles")
    assert tokens == ("chain", "aromatic_share_coarse=5", "heavy_coarse=quantiles:3")


def test_resolve_requested_tokens_is_sorted_deduped_union():
    tokens = resolve_requested_tokens(
        "chain,pocket_extent", "pocket_extent_coarse=quantiles,heavy"
    )
    assert tokens == tuple(sorted(tokens))
    assert set(tokens) == {"chain", "pocket_extent", "pocket_extent_coarse=quantiles:3", "heavy"}


def test_coarsen_to_levels_two_bands_are_distinct():
    # Regression test: with exactly 2 bands (3 edges, one interior cut) the "nearest
    # finite cut" fallback for both open outer bands used to point at the SAME edge,
    # collapsing every input to one repeated output value regardless of which side of
    # the threshold it fell on -- verified directly before the fix. Any bin count >= 3
    # was never affected (a separate, unchanged code path).
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    edges = np.array([-np.inf, 5.5, np.inf])
    result = coarsen_to_levels(values, edges)
    assert len(set(result.tolist())) == 2
    assert (result[values < 5.5] == result[0]).all()
    assert (result[values > 5.5] == result[-1]).all()
    assert result[0] < result[-1]


def test_bounded_share_names_are_all_in_the_catalog():
    assert set(BOUNDED_SHARE_DESCRIPTOR_NAMES) <= set(DESCRIPTOR_CATALOG)


def test_aromatic_and_polar_share_coarse_default_to_good_quantile_specs():
    # aromatic_share_coarse/polar_share_coarse are not literal DESCRIPTOR_CATALOG
    # entries any more -- parse_descriptor_token resolves them through
    # DEFAULT_COARSE_SPECS instead -- but the bare names still work as descriptor
    # tokens, now backed by quantiles (population-balanced) rather than the old
    # fixed-thirds scheme: measured directly on this project's 35 proteins,
    # aromatic_share never left fixed-thirds' own first third (34/35 proteins
    # collapsed onto one value), while 3 quantile bins give an even ~12/11/12 split.
    assert DEFAULT_COARSE_SPECS["aromatic_share_coarse"] == CoarseSpec("quantiles", 3)
    assert DEFAULT_COARSE_SPECS["polar_share_coarse"] == CoarseSpec("quantiles", 3)
    assert parse_descriptor_token("aromatic_share_coarse") == (
        "aromatic_share", CoarseSpec("quantiles", 3),
    )
    assert parse_descriptor_token("polar_share_coarse") == (
        "polar_share", CoarseSpec("quantiles", 3),
    )
    # An explicit spec still overrides the default.
    assert parse_descriptor_token("aromatic_share_coarse=5") == (
        "aromatic_share", CoarseSpec("fixed", 5),
    )


def test_descriptor_catalog_no_longer_carries_the_broken_fixed_coarse_names():
    # aromatic_share_coarse/polar_share_coarse (fixed thirds) are gone from this
    # catalog's BARE-tuple entries specifically -- they are still valid descriptor
    # tokens (see test_aromatic_and_polar_share_coarse_default_to_good_quantile_
    # specs above), just resolved through DEFAULT_COARSE_SPECS instead of being
    # literal DESCRIPTOR_CATALOG members.
    assert "aromatic_share_coarse" not in DESCRIPTOR_CATALOG
    assert "polar_share_coarse" not in DESCRIPTOR_CATALOG
    assert "tail_count" in DESCRIPTOR_CATALOG
