#!/usr/bin/env python3
"""Shared, data-closed utilities for the two-axis non-neural baselines.

The functions in this module deliberately consume only the interaction table, the
compact isomeric Tanimoto artefacts, and the already generated pocket graphs.  They do
not download annotations, structures, or assays, and they never modify the data tree.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

from dataloader.dataset_source import interaction_csv_path
from dataloader.pair_descriptors import npr1 as _compute_npr1
from dataloader.pair_descriptors import npr2 as _compute_npr2
from dataloader.pair_descriptors import hbond_capacity as _hbond_capacity
from dataloader.pair_descriptors import heavy_atom_count as _heavy_atom_count
from dataloader.pair_descriptors import longest_acyl_chain as _longest_acyl_chain
from dataloader.pair_descriptors import unsaturation_count as _unsaturation_count
from dataloader.pair_descriptors import LIPID_DESCRIPTOR_NAMES
from dataloader.pair_descriptors import PROTEIN_DERIVED_DESCRIPTOR_NAMES
from dataloader.pair_descriptors import PROTEIN_DESCRIPTOR_NAMES
from dataloader.pair_descriptor_cache import load_pair_descriptor_cache
from dataloader.sampler import (
    LIPID_COLDSPLIT_SETS,
    class_level_positive_labels,
    lipid_class_series,
    lipid_classes_for_holdout,
    sample_protein_balanced_negatives,
)
from preprocessing.audit_lipid_identity_by_smiles import features as smiles_features
from preprocessing.lipid_marginal_baseline import lipid_isolation_split, lipid_split

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
except ModuleNotFoundError:  # pragma: no cover - project environments include RDKit
    Chem = None
    Descriptors = None
    rdMolDescriptors = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
# The canonical, deduplicated interaction table (dataloader.dataset_source is the single
# source of truth for which file that is) -- every artefact indexed by row position
# (pair_id, the compact Tanimoto arrays) is built against this exact file.
DEFAULT_CSV = Path(interaction_csv_path(str(PROJECT_ROOT / "data")))
DEFAULT_GRAPHS = PROJECT_ROOT / "data" / "graphs"

POCKET13_NAMES = (
    "pocket_residue_share",
    "pocket_sasa_share",
    "pocket_volume_per_sasa",
    "pocket_extent",
    "pocket_elongation",
    "pocket_flatness",
    "ev14_q50",
    "buriedness_q50",
    "depth_q10",
    "apolar_sasa_share",
    "aromatic_share",
    "hydropathy_core",
    "hydropathy_rim",
)

# The added values are deliberately simple shares over the same pocket residues the
# model already sees.  They capture the charged/polar part of head-group recognition
# absent from the existing shape/hydropathy descriptor without adding a new source.
POCKET_CHEMISTRY_NAMES = (
    "basic_share_core",
    "basic_share_rim",
    "acidic_share_core",
    "acidic_share_rim",
    "polar_share_core",
    "polar_share_rim",
    "hbond_donor_share_core",
    "hbond_donor_share_rim",
    "hbond_acceptor_share_core",
    "hbond_acceptor_share_rim",
)
POCKET23_NAMES = POCKET13_NAMES + POCKET_CHEMISTRY_NAMES

# The four names dataloader/pair_descriptors.py's PROTEIN_DESCRIPTOR_NAMES has beyond
# POCKET23_NAMES -- e.g. protunion14 (protbind6's 13 plus protgeom8's pocket_extent)
# is NOT a subset of pocket23 without these. Exact same formulas as dataloader/
# protein_graph_builder.py's pocket_descriptor(), computed here from the same
# site/hydropathy/aromatic/rim locals protein_pocket_features already builds for the
# 13+10 above -- not a separate reimplementation, so this cannot drift from the
# network's own values the way an independently-derived formula could.
POCKET_EXTRA_NAMES = ("ev28_q10", "aromatic_share_rim", "hydropathy_mean", "ev14_q10")
# The two cavity measures added on top -- see _cavity_values for what they are and why
# the pre-existing "volume" entries were not cavity measures at all.
POCKET_CAVITY_NAMES = ("pocket_free_volume", "pocket_packing_density")
POCKET_ALL_NAMES = POCKET23_NAMES + POCKET_EXTRA_NAMES + POCKET_CAVITY_NAMES

RESIDUE_ORDER = "A R N D C Q E G H I L K M F P S T W Y V".split()
KYTE_DOOLITTLE = np.array(
    [
        1.8,
        -4.5,
        -3.5,
        -3.5,
        2.5,
        -3.5,
        -3.5,
        -0.4,
        -3.2,
        4.5,
        3.8,
        -3.9,
        1.9,
        2.8,
        -1.6,
        -0.8,
        -0.7,
        -0.9,
        -1.3,
        4.2,
    ]
)
AROMATIC = {"F", "W", "Y"}
BASIC = {"R", "K", "H"}
ACIDIC = {"D", "E"}
POLAR = {"N", "Q", "S", "T", "Y", "C"}
HBOND_DONOR = {"R", "K", "H", "N", "Q", "S", "T", "Y", "W", "C"}
HBOND_ACCEPTOR = {"D", "E", "H", "N", "Q", "S", "T", "Y", "C"}


def read_interactions(csv_path: Path | str = DEFAULT_CSV) -> pd.DataFrame:
    """Read the immutable source table and attach its stable original row id."""
    table = pd.read_csv(csv_path)
    table = table.copy()
    table["pair_id"] = table.index.astype(int)
    return table


def csv_classes(table: pd.DataFrame) -> pd.Series:
    """Canonical full-name head-group class, matching the active dataloader."""
    return lipid_class_series(table)


def _article_subclass_lookup() -> dict[str, set[str]]:
    """{article subclass (lowercase, e.g. "pc") -> species set}, from
    data/lipid_article_classification.json (preprocessing/classify_lipids_by_
    article.py's own output: Titeca et al. 2023 Figure 3a's LTP-lipid subclass
    scheme -- see files/data_source.md). Empty (not an error) when that file has
    never been generated -- resolve_excluded_lipids then simply finds no match for
    an article-subclass name, same as any other genuinely unknown one.
    """
    path = PROJECT_ROOT / "data" / "lipid_article_classification.json"
    if not path.exists():
        return {}
    import json

    mapping = json.loads(path.read_text())
    by_subclass: dict[str, set[str]] = {}
    for species, subclass in mapping.items():
        by_subclass.setdefault(subclass.lower(), set()).add(species)
    return by_subclass


def resolve_excluded_lipids(table: pd.DataFrame, names: list[str]) -> tuple[str, ...]:
    """--excluded_lipids' own name resolution: each entry in `names` is one of
    three things, tried in this order --

    1. an EXACT FullIdentityOfLipid species name (e.g. "Phosphatidylcholine (34:1)")
    2. a bare head-group CLASS name (csv_classes' own value, e.g.
       "Phosphatidylcholine", case-insensitive) -- expands to every species
       csv_classes assigns to it
    3. an article LTP-lipid subclass abbreviation (Titeca et al. 2023 Figure 3a,
       e.g. "PC", "Cer", "HexCer" -- files/data_source.md's own table, resolved via
       data/lipid_article_classification.json) -- expands to every species that
       classification assigns to it, coarser than (2) for classes the article
       lumps together (PC and PC-O, for instance, both become PC's "Phosphatidyl-
       choline" project class already, so this mostly matters for FA/FAL, which
       collapse many distinct project classes into one article subclass)

    Mixing all three kinds in one list is fine; they never collide (a species name
    always carries chain composition in parentheses, or a semicolon-joined
    ambiguity list, which neither class form has, and this project's class names
    and article abbreviations do not share a spelling).

    Raises ValueError naming whichever entries matched none of the three, rather
    than silently excluding nothing for them (a bare class name used to slip
    through as an unmatched species, producing an empty held-out block and an
    all-NaN report instead of an error).
    """
    known_species = set(table["FullIdentityOfLipid"])
    classes = csv_classes(table)
    class_lookup = {name.lower(): name for name in classes.unique()}
    article_lookup: dict[str, set[str]] | None = None
    species: set[str] = set()
    unknown: list[str] = []
    for name in names:
        if name in known_species:
            species.add(name)
        elif name.lower() in class_lookup:
            species.update(table.loc[classes == class_lookup[name.lower()], "FullIdentityOfLipid"])
        else:
            if article_lookup is None:
                article_lookup = _article_subclass_lookup()
            if name.lower() in article_lookup:
                species.update(article_lookup[name.lower()])
            else:
                unknown.append(name)
    if unknown:
        raise ValueError(
            f"--excluded_lipids: {unknown} match neither a FullIdentityOfLipid "
            "species (e.g. \"Phosphatidylcholine (34:1)\"), a head-group class "
            f"(e.g. \"Phosphatidylcholine\" -- known: {sorted(class_lookup.values())}), "
            "nor an article LTP-lipid subclass (e.g. \"PC\", \"Cer\" -- see "
            "files/data_source.md; run preprocessing/classify_lipids_by_article.py "
            "first if data/lipid_article_classification.json does not exist yet)"
        )
    return tuple(sorted(species))


def resolve_family_excluded_lipids(args, family: str) -> tuple[str, ...] | None:
    """args.excluded_lipids_species, resolved for one --families loop iteration.

    A flat tuple (--excluded_lipids' own single merged "custom" block, scripts/
    run_cron.py) applies the same way regardless of `family` -- there is only ever
    one such block, named "custom". A dict (--excluded_lipid_groups' several
    INDEPENDENT blocks) instead maps each family label to its own species tuple, so
    cold_split_pools only ever sees the block matching the CURRENT loop iteration,
    not every group's species merged together.
    """
    excluded = getattr(args, "excluded_lipids_species", None)
    if isinstance(excluded, dict):
        return excluded.get(family)
    return excluded


def _headgroup_isolation_units(table: pd.DataFrame, context: str):
    """analysis.lipid_block_search.Units at species granularity, built on the HEAD-
    GROUP-restricted Tanimoto artifacts (preprocessing/build_tanimoto_headgroup.py's
    Tanimoto_headgroup_compact_* -- acyl tails cut off, see species_headgroup_
    tanimoto_similarity's own docstring above) instead of _lipid_isolation_units'
    whole-molecule ones. For a --excluded_lipid_groups block defined BY head-group
    class (PC, PG, ...), whole-molecule similarity conflates head group and acyl
    chain; this isolates the axis the block is actually cut on. No manifest/staleness
    check here (species_headgroup_tanimoto_similarity's own loader does not do one
    either -- there is no isomeric variant of this artifact to disambiguate against).
    """
    from analysis.lipid_block_search import Units
    from dataloader.tanimoto_compact import CompactTanimoto

    data_dir = PROJECT_ROOT / "data"
    matrix_path = data_dir / "Tanimoto_headgroup_compact_matrix_uint8.npy"
    index_path = data_dir / "Tanimoto_headgroup_compact_structure_index.npy"
    row_path = data_dir / "Tanimoto_headgroup_compact_row_ids.npy"
    if not (matrix_path.exists() and index_path.exists() and row_path.exists()):
        raise ValueError(
            f"{context}: the headgroup-restricted Tanimoto artifacts are missing -- "
            "rebuild with preprocessing/build_tanimoto_headgroup.py"
        )
    compact = CompactTanimoto(
        np.load(matrix_path, mmap_mode="r"), np.load(index_path), np.load(row_path)
    )
    if len(np.unique(compact.row_ids)) != len(table):
        raise ValueError(
            f"{context}: the headgroup-restricted Tanimoto artifacts are stale for "
            "this table -- rebuild with preprocessing/build_tanimoto_headgroup.py"
        )
    return Units(table, compact, "species", family=None)


def block_tanimoto_headgroup_similarity(
    table: pd.DataFrame, species, units_cache: dict | None = None
) -> float:
    """Mean best-HEAD-GROUP-Tanimoto-similarity of an excluded species block to
    whatever chemistry stays in training -- analysis.lipid_block_search.Units.
    isolation's own number, over _headgroup_isolation_units instead of the whole-
    molecule one, computed for an ARBITRARY hand-picked species set (--excluded_
    lipids/--excluded_lipid_groups). Same scale --isolation_target already uses: LOW
    means no similar head group was left behind (a cold split, the fully-novel
    extreme is 0.0); HIGH means a close relative's head group stayed in training.

    NaN when `species` is empty/None -- there is no block to measure (a --split_mode
    single/double/lipid_coldsplit family this was never asked about, not a real "0
    similarity" claim).

    `units_cache`, when given (the same dict evaluate_block/build_report already pass
    around for their own protein/lipid kernel cache), memoizes the expensive Units
    build under one fixed key so every (family, seed) block in one run shares it
    instead of rebuilding it per call -- the table and its compact artifacts never
    change within a run.
    """
    if not species:
        return float("nan")
    units = units_cache.get("_headgroup_isolation_units") if units_cache is not None else None
    if units is None:
        units = _headgroup_isolation_units(table, "block Tanimoto headgroup similarity")
        if units_cache is not None:
            units_cache["_headgroup_isolation_units"] = units
    held = set(species)
    block = np.array([name in held for name in units.names], dtype=bool)
    return units.isolation(block)


def block_tanimoto_similarity(
    table: pd.DataFrame, species, units_cache: dict | None = None
) -> float:
    """Whole-molecule counterpart of block_tanimoto_headgroup_similarity, over
    _lipid_isolation_units instead of _headgroup_isolation_units -- the two are
    reported side by side (not one replacing the other): a block can be isolated on
    the head group alone while its acyl tails still resemble something in train, or
    vice versa, and the gap between the two numbers is itself informative. See
    block_tanimoto_headgroup_similarity's own docstring for the shared scale/NaN
    convention and the units_cache memoization this mirrors (own cache key, so the
    two never evict each other).
    """
    if not species:
        return float("nan")
    units = units_cache.get("_lipid_isolation_units") if units_cache is not None else None
    if units is None:
        units = _lipid_isolation_units(table, "block Tanimoto similarity")
        if units_cache is not None:
            units_cache["_lipid_isolation_units"] = units
    held = set(species)
    block = np.array([name in held for name in units.names], dtype=bool)
    return units.isolation(block)


def raw_double_cold_pool(
    table: pd.DataFrame, family: str, share: float
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[str, ...]]:
    """Return all P-vs-U rows of one two-axis held-out block, without sampling.

    The class choice is the existing project rule.  Train removes the held protein
    family and held lipid classes globally.  The reported pool contains exactly the
    intersection: the unseen family *and* unseen head-group classes.
    """
    held_classes = tuple(lipid_classes_for_holdout(table, family, share)[0])
    classes = csv_classes(table).str.lower()
    held = {name.lower() for name in held_classes}
    train = table[
        (table["ProteinDomain"].str.lower() != family.lower()) & ~classes.isin(held)
    ].copy()
    evaluation = table[
        (table["ProteinDomain"].str.lower() == family.lower()) & classes.isin(held)
    ].copy()
    if train.empty or evaluation.empty:
        raise ValueError(f"{family}: empty train or held-out block")
    return train, evaluation, held_classes


def raw_double_isolation_pool(
    table: pd.DataFrame, family: str, target: str
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[str, ...]]:
    """raw_double_cold_pool's counterpart keyed by a numeric Tanimoto-isolation
    target (species, via resolve_lipid_isolation_species) instead of lipid_classes_
    for_holdout's derived named class set.

    Exactly the combination dataloader/Dataloader.py's `_split_interactions`
    produces when --excluded_groups + --lipid_isolation + --double_coldsplit run
    together (see its own comment on `double_coldsplit and _has_cold_chemistry`):
    the family leaves train (protein axis), the target's species block leaves
    train for EVERY protein (lipid axis, computed once against the WHOLE table --
    the same global block a bare --lipid_coldsplit=<target> run would use, not
    re-searched against this family's own reduced training set), and the reported
    pool is exactly their intersection: the family's own rows on that species block.
    """
    species = resolve_lipid_isolation_species(target, table)
    held = set(species)
    domain = table["ProteinDomain"].str.lower()
    in_species = table["FullIdentityOfLipid"].isin(held)
    train = table[(domain != family.lower()) & ~in_species].copy()
    evaluation = table[(domain == family.lower()) & in_species].copy()
    if train.empty or evaluation.empty:
        raise ValueError(f"{family}__{target}: empty train or held-out block")
    return train, evaluation, tuple(sorted(held))


def raw_single_cold_pool(
    table: pd.DataFrame, family: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return all P-vs-U rows of a protein-only cold split (parity with --excluded_groups
    without --double_coldsplit): only the protein family is held out, every lipid class
    stays available in training.
    """
    domain = table["ProteinDomain"].str.lower()
    train = table[domain != family.lower()].copy()
    evaluation = table[domain == family.lower()].copy()
    if train.empty or evaluation.empty:
        raise ValueError(f"{family}: empty train or held-out block")
    return train, evaluation


def split_held_pairs(
    held: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a held pool by pair, keeping duplicate assay rows together.

    There are 98 repeated protein--lipid pairs under different `Screen` values.  A
    row-wise split would put the same pair in validation and test; the pair-level split
    avoids that leakage while retaining all Screen rows in the relevant half.
    """
    pairs = held[["LTPProtein", "FullIdentityOfLipid"]].drop_duplicates()
    valid_pairs = pairs.sample(frac=0.5, random_state=seed)
    valid_index = pd.MultiIndex.from_frame(valid_pairs)
    held_index = pd.MultiIndex.from_frame(held[["LTPProtein", "FullIdentityOfLipid"]])
    in_valid = held_index.isin(valid_index)
    return held.loc[in_valid].copy(), held.loc[~in_valid].copy()


def _isolation_key(target) -> str:
    """dataloader.lipid_isolation_blocks.LIPID_ISOLATION_BLOCKS' own key format --
    "%.2f" of the requested isolation, e.g. "0.8"/"0.80"/0.8 all normalize to "0.80".
    """
    return f"{float(target):.2f}"


def _looks_like_isolation_target(family: str) -> bool:
    """A --lipid_coldsplit family name is a LIPID_COLDSPLIT_SETS key (a chemistry
    name: "sphingolipids", "choline", ...) or a --lipid_isolation-style numeric
    target ("0.8", "0.90"). Numbers never collide with the named set's keys, so a
    bare float-parse is enough to tell the two apart.
    """
    try:
        float(family)
    except (TypeError, ValueError):
        return False
    return True


def _lipid_isolation_units(table: pd.DataFrame, context: str):
    """analysis.lipid_block_search.Units at species granularity over the whole
    table -- the shared setup step resolve_lipid_isolation_species and
    generate_lipid_isolation_groups both need before they can search for a block.
    `context` names what asked for it, only used in the error message on a
    missing/stale compact matrix.
    """
    from analysis.lipid_block_search import Units
    from dataloader.tanimoto_compact import load_compact

    compact = load_compact(str(PROJECT_ROOT / "data"))
    if compact is None or len(np.unique(compact.row_ids)) != len(table):
        raise ValueError(
            f"{context}: the compact Tanimoto artifacts needed to generate an "
            "isolation block are missing or stale -- rebuild with "
            "preprocessing/build_tanimoto_compact.py"
        )
    return Units(table, compact, "species", family=None)


def generate_lipid_isolation_groups(
    table: pd.DataFrame,
    count: int,
    target: float = 0.0,
    minimum_positives: int = 40,
    maximum_positives: int = 140,
) -> list[str]:
    """`count` --lipid_coldsplit=<key> blocks, each independently AS CLOSE TO
    `target` AS POSSIBLE within the size window -- --families_number's own
    mechanism. `target=0.0` (the default) asks for "as cold as achievable", since
    isolation is 0 at the fully-novel extreme; --isolation_target lets a run instead
    ask for `count` DIVERSE blocks clustered AROUND one chosen isolation level (e.g.
    "3 blocks near 0.6") rather than only ever the coldest extreme.

    NOT forced disjoint: an earlier version took blocks one at a time via analysis.
    lipid_block_search.search_groups, each restricted to species no earlier group
    already claimed. That constraint only matters when several folds must be held
    out AT ONCE in one combined run -- --families_number instead runs each group as
    its OWN separate (family, seed) evaluate_block, one train/valid/test built and
    scored independently, so a later group being unable to reuse an earlier group's
    species bought nothing but a shrinking pool to search -- smaller, less-isolated
    blocks the more groups were asked for, with nothing to show for the loss. Lipids
    repeating across groups is fine; a single analysis.lipid_block_search.search
    pass already tries every unit as a starting point and returns them ranked by
    closeness to `target`, so the top `count` DISTINCT candidates from that ONE pass
    is this function's whole job.

    Each block's key is its own ACHIEVED isolation ("%.2f", extra decimal digits
    added only on a genuine collision with a DIFFERENT existing/sibling block).
    Persisted into dataloader/lipid_isolation_blocks.py via analysis.
    lipid_block_search.emit_module, same reviewable-in-a-diff reasoning as
    resolve_lipid_isolation_species. Returns the keys closest-to-target-first, ready
    to use as --families.
    """
    import importlib

    from analysis.lipid_block_search import describe, emit_module, search
    import dataloader.lipid_isolation_blocks as isolation_blocks

    units = _lipid_isolation_units(table, f"--families_number={count}")
    best, _ = search(
        units, target=target, minimum_positives=minimum_positives,
        maximum_positives=maximum_positives, seeds=range(units.count),
    )
    # A tight target + a narrow size window can leave only ONE real chemistry in
    # range (e.g. target=0.6 on this table: sphingolipids/ceramides is close to the
    # only cluster there), so ranking by mere set-inequality accepted near-duplicates
    # that differed by one or two borderline species while sharing the same
    # backbone -- not the diversity --families_number groups are for. Reject a
    # candidate that shares more than half its species (Jaccard) with any block
    # already chosen, so a genuinely different chemistry is required, not just a
    # different SET.
    max_overlap = 0.5
    chosen_sets: list[set[str]] = []
    distinct: list[tuple[float, np.ndarray]] = []
    for _, value, block, _ in best:
        members = {units.names[position] for position in np.flatnonzero(block)}
        if any(
            len(members & chosen) / len(members | chosen) > max_overlap
            for chosen in chosen_sets
        ):
            continue
        chosen_sets.append(members)
        distinct.append((value, block))
        if len(distinct) >= count:
            break
    if len(distinct) < count:
        raise ValueError(
            f"--families_number={count}: only {len(distinct)} sufficiently distinct "
            f"species block(s) (<= {max_overlap:.0%} Jaccard overlap with each "
            f"other) fit the {minimum_positives}-{maximum_positives} positives "
            f"window around target={target} -- lower --families_number, move "
            "--isolation_target, or widen the window"
        )

    existing = isolation_blocks.LIPID_ISOLATION_BLOCKS
    chosen: dict[str, dict] = {}
    keys: list[str] = []
    for value, block in distinct:
        report = describe(units, block)
        members = tuple(report["units"])
        precision = 2
        key = f"{value:.{precision}f}"
        while (key in chosen and tuple(chosen[key]["units"]) != members) or (
            key in existing and tuple(existing[key]) != members
        ):
            precision += 1
            key = f"{value:.{precision}f}"
        chosen[key] = {"isolation": value, **report}
        keys.append(key)

    search_args = argparse.Namespace(
        granularity="species", targets=",".join(keys), family="",
        min_positives=minimum_positives, max_positives=maximum_positives,
    )
    emit_module(
        str(PROJECT_ROOT / "dataloader" / "lipid_isolation_blocks.py"),
        chosen, search_args, table,
    )
    importlib.reload(isolation_blocks)
    print(
        f"--families_number={count}: generated {len(keys)} species block(s), not "
        f"forced disjoint ({', '.join(keys)}) -- written to "
        "dataloader/lipid_isolation_blocks.py"
    )
    return keys


def resolve_lipid_isolation_species(target: str, table: pd.DataFrame) -> tuple[str, ...]:
    """Species set for one --lipid_coldsplit=<target> block, keyed by a REQUESTED
    Tanimoto isolation level (e.g. "0.8") rather than a named LIPID_COLDSPLIT_SETS
    chemistry -- the --lipid_isolation axis the network itself already supports
    (dataloader/Dataloader.py, dataloader/lipid_isolation_blocks.py).

    Looks up dataloader.lipid_isolation_blocks.LIPID_ISOLATION_BLOCKS first, trying
    `target` VERBATIM (as a string) before falling back to _isolation_key(target)'s
    2-decimal rounding: generate_lipid_isolation_groups disambiguates a same-2-
    decimal collision between two DIFFERENT sibling blocks with extra digits
    ("0.600" vs "0.596" both rounding to "0.60"), and rounding on lookup here would
    silently collapse those distinct keys back onto whichever one happened to be
    stored under the rounded form -- exactly the bug that let two supposedly-
    different --families_number groups resolve to the same species set. A target
    that does not have EITHER form yet is generated AND PERSISTED by calling
    analysis.lipid_block_search's own species-granularity search in-process (the
    same algorithm a hand-run `--emit_module` uses) and writing the result into
    dataloader/lipid_isolation_blocks.py under its _isolation_key(...) form (e.g.
    "0.80"), so it stays reviewable in a git diff and fixed for every later run that
    asks for the same target -- exactly the guarantee that module's own docstring
    says a silently-regenerated-on-a-whim file would break. Re-imports the module
    after writing so this process sees its own freshly written block without a
    restart.
    """
    import dataloader.lipid_isolation_blocks as isolation_blocks

    species = isolation_blocks.LIPID_ISOLATION_BLOCKS.get(str(target))
    key = _isolation_key(target)
    if species is None:
        species = isolation_blocks.LIPID_ISOLATION_BLOCKS.get(key)
    if species is not None:
        return species

    import importlib

    from analysis.lipid_block_search import describe, emit_module, search

    units = _lipid_isolation_units(table, f"--lipid_coldsplit={target}")
    best, _ = search(
        units, float(key), minimum_positives=40, maximum_positives=140,
        seeds=range(units.count),
    )
    if not best:
        raise ValueError(
            f"--lipid_coldsplit={target}: no species block hits {key!r} within the "
            "default 40-140 positives window -- generate one by hand with a wider "
            "--min_positives/--max_positives via analysis/lipid_block_search.py "
            f"--targets {key} --granularity species --emit_module "
            "dataloader/lipid_isolation_blocks.py"
        )
    _, value, block, _ = best[0]
    report = describe(units, block)
    print(
        f"--lipid_coldsplit={target}: no existing LIPID_ISOLATION_BLOCKS entry, "
        f"generated one now (isolation {value:.3f} vs requested {key}, "
        f"{report['positives']} positives, {len(report['units'])} species) -- "
        "writing it to dataloader/lipid_isolation_blocks.py for reuse"
    )
    search_args = argparse.Namespace(
        granularity="species", targets=key, family="", min_positives=40, max_positives=140,
    )
    emit_module(
        str(PROJECT_ROOT / "dataloader" / "lipid_isolation_blocks.py"),
        {key: {"isolation": value, **report}},
        search_args,
        table,
    )
    importlib.reload(isolation_blocks)
    return isolation_blocks.LIPID_ISOLATION_BLOCKS[key]


def cold_split_pools(
    table: pd.DataFrame,
    family: str,
    seed: int,
    split_mode: str,
    share: float = 0.8,
    excluded_lipids: tuple[str, ...] | None = None,
    merge_valid_test: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """(train, valid, test) for one cold-split block, shared by every non-neural baseline.

    `merge_valid_test`, when True, skips the usual 50/50 valid/test halving and hands
    back the WHOLE held-out block as both -- see preprocessing.lipid_marginal_baseline.
    halve_excluded_block's own docstring for when this is (and is not) sound: only when
    nothing downstream selects a lambda or a threshold on valid and then reads a
    DIFFERENT number off test, i.e. no real --lambda_grid and only threshold-free
    metrics (AUC_within_protein) are read.

    `excluded_lipids`, when given (a non-empty tuple of FullIdentityOfLipid names),
    takes priority over everything below: every protein stays in training and
    exactly this species set leaves it (preprocessing.lipid_marginal_baseline.
    lipid_isolation_split) -- --excluded_lipids' own mechanism, a hand-picked
    species list instead of a LIPID_COLDSPLIT_SETS name or a searched Tanimoto-
    isolation target, needing no --split_mode at all (ignored when this is given).

    Otherwise, `split_mode`: "single"/"double" hold out a protein family (`family`
    names it, --excluded_groups/--double_coldsplit parity); "lipid_coldsplit" holds
    out lipid chemistry with every protein still in training (--lipid_coldsplit/
    --lipid_isolation parity) -- `family` is either a LIPID_COLDSPLIT_SETS key (a
    named class set, e.g. "sphingolipids", via preprocessing.lipid_marginal_
    baseline.lipid_split) or a numeric Tanimoto-isolation target (e.g. "0.8",
    resolved through resolve_lipid_isolation_species + preprocessing.
    lipid_marginal_baseline.lipid_isolation_split), told apart by whether `family`
    parses as a float.

    "double" additionally accepts a combined "<family>__<target>" name (e.g.
    "CRAL-TRIO__0.8", the family names never containing "__" themselves): the
    family leaves train same as ever, and the lipid side is a numeric isolation
    target (raw_double_isolation_pool) instead of lipid_classes_for_holdout's
    derived class set (raw_double_cold_pool) -- exactly the combination
    dataloader/Dataloader.py's own --excluded_groups + --lipid_isolation +
    --double_coldsplit produces.
    """
    if excluded_lipids:
        return lipid_isolation_split(table, excluded_lipids, seed, merge_valid_test=merge_valid_test)
    if split_mode == "lipid_coldsplit":
        if _looks_like_isolation_target(family):
            species = resolve_lipid_isolation_species(family, table)
            return lipid_isolation_split(table, species, seed, merge_valid_test=merge_valid_test)
        return lipid_split(
            table, LIPID_COLDSPLIT_SETS[family], seed, merge_valid_test=merge_valid_test
        )
    if split_mode == "double":
        if "__" in family:
            protein_family, target = family.split("__", 1)
            train_pool, held_pool, _ = raw_double_isolation_pool(table, protein_family, target)
        else:
            train_pool, held_pool, _ = raw_double_cold_pool(table, family, share)
    else:
        train_pool, held_pool = raw_single_cold_pool(table, family)
    if merge_valid_test:
        return train_pool, held_pool, held_pool
    valid_pool, test_pool = split_held_pairs(held_pool, seed)
    return train_pool, valid_pool, test_pool


def balance_pool_negatives(pool: pd.DataFrame, seed: int, ratio: int) -> pd.DataFrame:
    """Keep every positive row, subsample negatives to `ratio` per positive per protein.

    dataloader.sampler.sample_protein_balanced_negatives -- the same
    negatives_per_positive convention every current arg file trains AND is scored
    under (training/read_configuration.py's own default is 2; dataloader/Dataloader.
    py's `_sample_interactions` applies this balancing to the working set BEFORE the
    train/valid/test split, so the network's own valid/test rows are already this
    1:2 pool, never the held-out block's raw positive rate).

    A row-based classifier (unlike Kron-RLS's matrix-completion fit) may call this on
    TRAIN too -- it has no completeness requirement to protect. `ratio` falsy (0/None)
    returns `pool` unchanged.
    """
    if not ratio:
        return pool
    positives = pool[pool["Interaction"] == 1]
    negatives = sample_protein_balanced_negatives(pool, seed, ratio)
    return pd.concat([positives, negatives])


def aggregate_pair_labels(
    table: pd.DataFrame, lipid_class_targets: bool = False
) -> pd.DataFrame:
    """Collapse duplicate assay rows into a complete protein-by-lipid P-vs-U matrix.

    `Interaction=0` is unlabelled rather than a confirmed negative.  A duplicate pair
    is therefore positive whenever either existing screen observed a positive.  Screen
    remains available in the separate row-level diagnostic.

    lipid_class_targets widens what counts as positive before that collapse: a cell is
    positive whenever its protein has ANY positive elsewhere in `table` sharing its
    lipid's head-group class (dataloader.lipid_classes.class_level_positive_labels),
    not only when its own species was screened positive. `table` here is always the
    caller's train pool alone (see evaluate_block in analysis/kronrls_baseline.py), so
    a held-out block's positives never leak into a training cell's label through this
    widening; the held-out pool is still scored against its own exact Interaction
    values, unchanged.
    """
    source = (
        table.assign(Interaction=class_level_positive_labels(table))
        if lipid_class_targets
        else table
    )
    labels = source.groupby(["LTPProtein", "FullIdentityOfLipid"], sort=True)["Interaction"].max()
    matrix = labels.unstack("FullIdentityOfLipid")
    if matrix.isna().any().any():
        missing = int(matrix.isna().sum().sum())
        raise ValueError(
            f"training rectangle is incomplete ({missing} missing protein-lipid cells); "
            "KronRLS must not silently treat missing assays as unlabelled"
        )
    return matrix.astype(float)


def auc_p_vs_u(truth: np.ndarray | pd.Series, scores: np.ndarray | pd.Series) -> float:
    """Tie-aware rank AUC for observed positives versus unlabelled rows."""
    truth = np.asarray(truth, dtype=int)
    scores = np.asarray(scores, dtype=float)
    positive_count = int(truth.sum())
    negative_count = len(truth) - positive_count
    if positive_count == 0 or negative_count == 0:
        return float("nan")
    ranks = pd.Series(scores).rank(method="average").to_numpy()
    return float(
        (ranks[truth == 1].sum() - positive_count * (positive_count + 1) / 2)
        / (positive_count * negative_count)
    )


def best_threshold_for_metric(
    truth: np.ndarray | pd.Series,
    scores: np.ndarray | pd.Series,
    metric: str = "balanced_accuracy",
) -> tuple[float, float]:
    """The score cut maximizing `metric` ("balanced_accuracy" or "F1") on the pool passed in.

    Kron-RLS scores are ridge-regression outputs, not calibrated probabilities --
    on a lipid_coldsplit test pool they were observed at roughly -0.11..0.22, nowhere
    near a fixed 0.5. Thresholding at 0.5 (the network's convention, since its output
    IS a calibrated sigmoid) would call every row negative here, exactly the
    "threshold placement" pitfall analysis/null_model.py's docstring warns about for
    fixed-cut BA on an uncalibrated score. So the cut is fit like protein_lambda/
    lipid_lambda are: on the validation pool only, then applied unchanged to test --
    never fit on the pool it will be reported on.

    balanced_accuracy and F1 are NOT maximized by the same cut under class imbalance:
    BA weighs sensitivity and specificity equally regardless of the tiny positive
    rate, F1 weighs precision, which collapses fast as false positives pile up against
    a small positive count. Picking `metric` up front makes that tradeoff explicit
    instead of silently reporting a BA-optimal cut's F1 (which reads as "broken").

    Vectorised over all candidate cuts at once rather than one Python iteration per
    cut: each cut's confusion matrix comes from a searchsorted over the score-sorted
    rows, so the whole sweep is O(n log n) instead of O(n_cuts * n). Same cuts and
    same values as the loop it replaces (same midpoint candidates, same ">= cut"
    rule) -- it only matters for speed, and it matters a lot now that the threshold
    is fit on TRAIN (thousands of rows, thousands of distinct scores) instead of a
    small held-out pool.
    """
    if metric not in ("balanced_accuracy", "F1"):
        raise ValueError(f"unknown metric {metric!r}; expected balanced_accuracy or F1")
    truth = np.asarray(truth, dtype=int)
    scores = np.asarray(scores, dtype=float)
    order = np.unique(scores)
    if order.size == 0:
        return 0.5, float("nan")
    midpoints = (order[:-1] + order[1:]) / 2 if order.size > 1 else order
    cuts = np.concatenate([[order[0] - 1e-9], midpoints, [order[-1] + 1e-9]])

    positives = int(truth.sum())
    negatives = len(truth) - positives
    # For each cut, how many rows fall BELOW it (searchsorted on the sorted scores),
    # split by label -- the predicted-negative side; the predicted-positive side is
    # then the complement, so all four cells come from two searchsorted calls.
    positive_scores = np.sort(scores[truth == 1])
    negative_scores = np.sort(scores[truth == 0])
    false_negative = np.searchsorted(positive_scores, cuts, side="left")
    true_negative = np.searchsorted(negative_scores, cuts, side="left")
    true_positive = positives - false_negative
    false_positive = negatives - true_negative

    with np.errstate(divide="ignore", invalid="ignore"):
        if metric == "balanced_accuracy":
            values = 0.5 * (
                np.divide(true_positive, positives, where=positives > 0,
                          out=np.full(cuts.shape, np.nan))
                + np.divide(true_negative, negatives, where=negatives > 0,
                            out=np.full(cuts.shape, np.nan))
            )
        else:
            denominator = 2 * true_positive + false_positive + false_negative
            values = np.divide(
                2 * true_positive, denominator, where=denominator > 0,
                out=np.full(cuts.shape, np.nan),
            )
    if not np.isfinite(values).any():
        return 0.5, float("nan")
    best = int(np.nanargmax(values))
    return float(cuts[best]), float(values[best])


def binary_confusion_metrics(
    truth: np.ndarray | pd.Series, scores: np.ndarray | pd.Series, threshold: float
) -> dict:
    """Confusion-matrix metrics at a fixed threshold, training/new_train.py-compatible.

    Same formulas and key names as training/new_train.py's metric_values (F1 =
    2TP/(2TP+FP+FN), balanced_accuracy = (sensitivity+specificity)/2, IoU =
    TP/(TP+FP+FN), FAR = FP/(FP+TN)) -- so a Kron-RLS row's dict is a drop-in match
    for a network test_metrics_*.txt report's own bare metric keys (see analysis/
    run_cron.py, which writes exactly these keys out under that convention).
    """
    truth = np.asarray(truth, dtype=int)
    predicted = np.asarray(scores, dtype=float) >= threshold
    true_positive = int((predicted & (truth == 1)).sum())
    false_negative = int((~predicted & (truth == 1)).sum())
    true_negative = int((~predicted & (truth == 0)).sum())
    false_positive = int((predicted & (truth == 0)).sum())
    total = true_positive + false_negative + true_negative + false_positive
    sensitivity = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative) else float("nan")
    )
    specificity = (
        true_negative / (true_negative + false_positive)
        if (true_negative + false_positive) else float("nan")
    )
    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive) else float("nan")
    )
    iou_denominator = true_positive + false_positive + false_negative
    far_denominator = false_positive + true_negative
    return {
        "TP": true_positive,
        "FP": false_positive,
        "TN": true_negative,
        "FN": false_negative,
        "total": total,
        "real_positive": true_positive + false_negative,
        "real_negative": true_negative + false_positive,
        "predicted_positive": true_positive + false_positive,
        "predicted_negative": true_negative + false_negative,
        "accuracy": (true_positive + true_negative) / total if total else float("nan"),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "IoU": (true_positive / iou_denominator) if iou_denominator else float("nan"),
        "FAR": (false_positive / far_denominator) if far_denominator else float("nan"),
        "balanced_accuracy": (
            float("nan") if np.isnan(sensitivity) or np.isnan(specificity)
            else 0.5 * (sensitivity + specificity)
        ),
        "F1": (
            2 * true_positive / (2 * true_positive + false_positive + false_negative)
            if (2 * true_positive + false_positive + false_negative) else float("nan")
        ),
    }


def _pocket_mask(nodes: pd.DataFrame, pocket_path: Path) -> np.ndarray:
    """Pocket mask with the same B-factor and side-chain convention as the loader."""
    from analysis.pocket_shape_descriptors import read_pocket_atoms

    _, pocket_residues, _ = read_pocket_atoms(pocket_path)
    keys = [
        str(int(value)) if float(value).is_integer() else str(value)
        for value in nodes["ID_resSeq"]
    ]
    mask = np.asarray([residue in pocket_residues for residue in keys], dtype=bool)
    if not mask.any():
        raise ValueError(f"{pocket_path}: no pocket residues match coarse_graph_nodes.csv")
    return mask


def _shape_values(pocket_path: Path) -> tuple[float, float, float]:
    from analysis.pocket_shape_descriptors import read_pocket_atoms, shape_from_coordinates

    coordinates, _, _ = read_pocket_atoms(pocket_path)
    shape = shape_from_coordinates(coordinates)
    if shape is None:
        return 0.0, 0.0, 0.0
    return shape["pocket_extent"], shape["pocket_elongation"], shape["pocket_flatness"]


# Van der Waals radii, angstrom (Bondi). Only the elements a protein PDB actually
# carries; anything unlisted falls back to carbon, the commonest by far.
_VDW_RADII = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "H": 1.20}


def _cavity_values(pocket_path: Path) -> tuple[float, float]:
    """(free cavity volume in A^3, packing density) of the binding pocket.

    The existing "volume" in this catalog is NOT the cavity: `residue_volume` is the
    Voronoi cell of each LINING RESIDUE -- protein material, not empty space -- and
    since a residue's cell varies only ~21% around 198 A^3, summing it over the pocket
    tracks the residue count at rho=0.993 (see PROTEIN_DESCRIPTOR_NAMES' own comment in
    dataloader/pair_descriptors.py, which is why pocket_volume_per_sasa replaced it).
    A convex hull of the pocket atoms is no better on its own -- measured here across
    all 35 proteins, hull volume still correlates 0.972 with residue count.

    What IS new information is the hull MINUS the van der Waals volume of every atom
    whose centre falls inside it: the space actually left for a ligand. Measured over
    the 35 proteins: mean 1006 A^3 (range 162-3064), correlation with pocket residue
    count 0.791 -- and the free FRACTION (this function's second return value) sits at
    -0.196, i.e. essentially independent of how big the pocket is. That fraction is a
    genuinely new axis rather than another size proxy.

    The absolute free volume matters for a second reason: it lands on the same physical
    scale as the lipid side's `experimental_lipid_volume` (283 species, mean 632 A^3,
    range 22-1248), so the lipid-volume-against-pocket-volume relationship the source
    paper (Titeca et al., files/Reuter.pdf) actually measures becomes expressible.
    """
    from scipy.spatial import ConvexHull, Delaunay

    from analysis.pocket_shape_descriptors import read_pocket_atoms

    pocket, _, _ = read_pocket_atoms(pocket_path)
    if len(pocket) < 4:
        return 0.0, 0.0
    hull = ConvexHull(pocket)
    triangulation = Delaunay(pocket)
    coordinates, elements = [], []
    with open(pocket_path) as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")) or len(line) < 63:
                continue
            coordinates.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
            elements.append((line[76:78].strip() or line[13:14]).upper())
    inside = triangulation.find_simplex(np.asarray(coordinates)) >= 0
    occupied = sum(
        4.0 / 3.0 * np.pi * _VDW_RADII.get(element, 1.70) ** 3
        for element, is_inside in zip(elements, inside) if is_inside
    )
    free = max(hull.volume - occupied, 0.0)
    return float(free), float(free / max(hull.volume, 1e-9))


def _share(residue_letters: np.ndarray, allowed: set[str]) -> float:
    return float(np.isin(residue_letters, list(allowed)).mean())


def protein_pocket_features(
    proteins: list[str] | tuple[str, ...], graphs: Path | str = DEFAULT_GRAPHS
) -> pd.DataFrame:
    """Build pocket13 and its residue-chemistry extension from existing graph files."""
    rows = []
    for protein in proteins:
        protein_dir = Path(graphs) / str(protein)
        nodes_path = protein_dir / "coarse_graph_nodes.csv"
        pocket_path = protein_dir / "pocketness.pdb"
        if not nodes_path.is_file() or not pocket_path.is_file():
            raise FileNotFoundError(f"missing existing graph artefacts for {protein}: {protein_dir}")
        nodes = pd.read_csv(nodes_path)
        mask = _pocket_mask(nodes, pocket_path)
        site = nodes.loc[mask]
        residue_types = site["residue_type"].to_numpy(dtype=int)
        residue_letters = np.asarray([RESIDUE_ORDER[index] for index in residue_types])
        hydropathy = KYTE_DOOLITTLE[residue_types]
        aromatic = np.isin(residue_letters, list(AROMATIC))
        sasa = site["residue_sas_area"].to_numpy(dtype=float)
        pocket_sasa = float(sasa.sum())
        burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
        core = burial >= np.median(burial)
        rim = ~core
        if not rim.any():
            rim = np.ones(len(site), dtype=bool)
        extent, elongation, flatness = _shape_values(pocket_path)
        free_volume, packing = _cavity_values(pocket_path)
        row = {
            "LTPProtein": protein,
            "pocket_residue_share": len(site) / max(len(nodes), 1),
            "pocket_sasa_share": pocket_sasa
            / max(float(nodes["residue_sas_area"].sum()), 1e-9),
            "pocket_volume_per_sasa": float(site["residue_volume"].sum())
            / max(pocket_sasa, 1e-9),
            "pocket_extent": extent,
            "pocket_elongation": elongation,
            "pocket_flatness": flatness,
            "ev14_q50": float(np.median(site["residue_mean_ev14"].to_numpy(dtype=float))),
            "buriedness_q50": float(np.median(burial)),
            "depth_q10": float(
                np.percentile(site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 10)
            ),
            "apolar_sasa_share": float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9)),
            "aromatic_share": float(aromatic.mean()),
            "hydropathy_core": float(hydropathy[core].mean()),
            "hydropathy_rim": float(hydropathy[rim].mean()),
            # POCKET_EXTRA_NAMES -- same formulas as dataloader/protein_graph_
            # builder.py's pocket_descriptor(), same `rim` (already patched to the
            # whole site when the burial median split leaves it empty, so no
            # separate rim.any() fallback is needed here either).
            "ev28_q10": float(
                np.percentile(site["residue_mean_ev28"].to_numpy(dtype=float), 10)
            ),
            "aromatic_share_rim": float(aromatic[rim].mean()),
            "hydropathy_mean": float(hydropathy.mean()),
            "ev14_q10": float(
                np.percentile(site["residue_mean_ev14"].to_numpy(dtype=float), 10)
            ),
            # See _cavity_values: the first real cavity measure in this catalog (the
            # older "volume" entries were residue count in disguise), and the only
            # protein-side quantity on the same physical scale as the lipid side's
            # experimental_lipid_volume.
            "pocket_free_volume": free_volume,
            "pocket_packing_density": packing,
        }
        for name, allowed in (
            ("basic", BASIC),
            ("acidic", ACIDIC),
            ("polar", POLAR),
            ("hbond_donor", HBOND_DONOR),
            ("hbond_acceptor", HBOND_ACCEPTOR),
        ):
            row[f"{name}_share_core"] = _share(residue_letters[core], allowed)
            row[f"{name}_share_rim"] = _share(residue_letters[rim], allowed)
        rows.append(row)
    return pd.DataFrame(rows).set_index("LTPProtein").loc[list(proteins)]


def protein_features_for_kernel(
    table: pd.DataFrame, kernel: str, graphs: Path | str = DEFAULT_GRAPHS
) -> pd.DataFrame:
    """Select the canonical 13 or 13+10 data-closed pocket descriptor set."""
    proteins = sorted(table["LTPProtein"].unique())
    features = protein_pocket_features(proteins, graphs)
    if kernel == "pocket13":
        return features.loc[:, POCKET13_NAMES]
    if kernel == "pocket23":
        return features.loc[:, POCKET23_NAMES]
    raise ValueError(f"unknown protein kernel {kernel!r}; expected pocket13 or pocket23")


def _candidate_smiles(value: object) -> list[str]:
    return [part.strip() for part in str(value).split(";") if part.strip()]


def _chain_composition(chain_fragments: object, lipid_name: object) -> tuple[float, float, float, float, float]:
    """Count tails/length/unsaturation from existing ChainFragments, then Lipid text."""
    fragments = str(chain_fragments) if pd.notna(chain_fragments) else ""
    pairs = re.findall(r"(\d+)\s*:\s*(\d+)", fragments)
    if not pairs:
        pairs = re.findall(r"(?:[A-Za-z*\-]+)?(\d+)\s*:\s*(\d+)", str(lipid_name))
    values = [(float(carbons), float(double_bonds)) for carbons, double_bonds in pairs]
    if not values:
        return (np.nan, np.nan, np.nan, np.nan, np.nan)
    carbons = np.asarray([value[0] for value in values])
    unsaturation = np.asarray([value[1] for value in values])
    return (
        float(len(values)),
        float(carbons.sum()),
        float(carbons.mean()),
        float(carbons.max()),
        float(unsaturation.sum()),
    )


def _fallback_nan(value: float | None) -> float:
    """None -> NaN, anything else (0.0 included) passed through unchanged.

    `value or np.nan` would be wrong here: 0.0 is a real, common answer for chain/
    unsaturation/hbond/heavy (a sterol with no acyl tail, a fully saturated chain)
    and is falsy, so `or` would silently turn a real zero into a missing value.
    """
    return np.nan if value is None else value


def _candidate_explicit_features(smiles: str, npr_cache: dict | None = None) -> dict[str, float]:
    """`npr_cache`, when given, is a dataloader.pair_descriptor_cache load result
    ({"raw_to_canonical", "values", ...}) -- npr1/npr2 are looked up there first (a
    disk-cached value skips the 10-conformer ETKDG+MMFF embed entirely), falling
    back to dataloader.pair_descriptors.npr1/npr2 (which still hits that module's own
    in-process lru_cache on repeat calls within the same run) exactly as without a
    cache. Same fallback discipline as dataloader.pair_descriptors.descriptor_values_
    by_row's own `cache` parameter.
    """
    parsed = smiles_features(smiles)
    mol = Chem.MolFromSmiles(smiles) if Chem is not None else None
    formal_charge = 0.0
    positive_atoms = 0.0
    negative_atoms = 0.0
    carbon_double_bonds = np.nan
    # Whole-molecule RDKit descriptors (proposal 9): the lipid-side analogues of the
    # protein pocket's own family_neutral axes (pocket_volume_per_sasa/apolar_sasa_share/
    # hydropathy_rim/pocket_extent/aromatic_share) -- logp/tpsa are the two orthogonal
    # hydrophobicity/polarity axes (a molecule can be apolar overall with polarity
    # concentrated in one headgroup, which logp alone would not show), molar_refractivity
    # is the volume/polarizability analogue of pocket_volume_per_sasa, rotatable_bond_count
    # is how much the lipid can conform to a cavity's shape, and aromatic_ring_count/
    # ring_count are the direct counterparts of the pocket's own aromatic_share. Left NaN
    # (not defaulted to 0.0, unlike formal_charge/positive_atoms/negative_atoms above) when
    # RDKit cannot parse a candidate -- 0.0 is a real logp/tpsa value, not a "no structure"
    # placeholder, so it must not be fabricated; every species in this project's own table
    # has at least one parseable candidate (verified), so explicit_lipid_features' per-
    # species median never actually sees an all-NaN column.
    logp = np.nan
    tpsa = np.nan
    molar_refractivity = np.nan
    rotatable_bond_count = np.nan
    aromatic_ring_count = np.nan
    ring_count = np.nan
    # npr1/npr2 (Sauer & Schwarz 2003): normalized principal moment ratios off an
    # actual 3D conformer ensemble, not a 2D-topology proxy -- the direct lipid-side
    # counterparts of the pocket's own pocket_elongation/pocket_flatness, and the
    # most direct candidate bilinear partner for pocket shape (unlike chain/tail_count,
    # which only stand in for shape via carbon-count topology). See npr1/npr2 above
    # for the median-over-conformers rationale.
    npr1_value = np.nan
    npr2_value = np.nan
    chain_value = np.nan
    unsaturation_value = np.nan
    hbond_value = np.nan
    heavy_value = np.nan
    if mol is not None:
        charges = [atom.GetFormalCharge() for atom in mol.GetAtoms()]
        formal_charge = float(sum(charges))
        positive_atoms = float(sum(charge > 0 for charge in charges))
        negative_atoms = float(sum(charge < 0 for charge in charges))
        carbon_double_bonds = float(
            sum(
                bond.GetBondType() == Chem.BondType.DOUBLE
                and bond.GetBeginAtom().GetAtomicNum() == 6
                and bond.GetEndAtom().GetAtomicNum() == 6
                for bond in mol.GetBonds()
            )
        )
        logp = float(Descriptors.MolLogP(mol))
        tpsa = float(Descriptors.TPSA(mol))
        molar_refractivity = float(Descriptors.MolMR(mol))
        rotatable_bond_count = float(rdMolDescriptors.CalcNumRotatableBonds(mol))
        aromatic_ring_count = float(rdMolDescriptors.CalcNumAromaticRings(mol))
        ring_count = float(rdMolDescriptors.CalcNumRings(mol))
        cached_entry = None
        if npr_cache is not None:
            canonical = npr_cache["raw_to_canonical"].get(smiles)
            if canonical is not None:
                cached_entry = npr_cache["values"].get(canonical)
        if cached_entry is not None and "npr1" in cached_entry and "npr2" in cached_entry:
            npr1_value = cached_entry["npr1"]
            npr2_value = cached_entry["npr2"]
            npr1_value = np.nan if npr1_value is None else npr1_value
            npr2_value = np.nan if npr2_value is None else npr2_value
        else:
            npr1_value = _compute_npr1(smiles)
            npr2_value = _compute_npr2(smiles)
            npr1_value = np.nan if npr1_value is None else npr1_value
            npr2_value = np.nan if npr2_value is None else npr2_value
        # data/build_pair_descriptor_cache.py's own cache already stores these four
        # (built specifically "for --pair_descriptors'/--two_pair_descriptors_paths'
        # shared per-candidate ... base values (chain/unsaturation/hbond/heavy ...)"
        # -- see that script's module docstring) under "chain"/"unsaturation"/
        # "hbond"/"heavy_atoms" (dataloader/pair_descriptor_cache.py's own
        # build_pair_value_cache renames "heavy_atoms" -> "heavy" at its own call
        # site; same rename applied here). A cache hit is a dict lookup instead of
        # re-parsing the SMILES with RDKit -- the same discipline npr1/npr2 already
        # get above, now extended to these four instead of always computing them
        # live regardless of whether a current cache exists.
        if cached_entry is not None and "chain" in cached_entry:
            chain_value = _fallback_nan(cached_entry["chain"])
        else:
            chain_value = _fallback_nan(_longest_acyl_chain(smiles))
        if cached_entry is not None and "unsaturation" in cached_entry:
            unsaturation_value = _fallback_nan(cached_entry["unsaturation"])
        else:
            unsaturation_value = _fallback_nan(_unsaturation_count(smiles))
        if cached_entry is not None and "hbond" in cached_entry:
            hbond_value = _fallback_nan(cached_entry["hbond"])
        else:
            hbond_value = _fallback_nan(_hbond_capacity(smiles))
        if cached_entry is not None and "heavy_atoms" in cached_entry:
            heavy_value = _fallback_nan(cached_entry["heavy_atoms"])
        else:
            heavy_value = _fallback_nan(_heavy_atom_count(smiles))
    ether_tail_count = max(
        0.0,
        float(parsed["tail_count"])
        - float(parsed["ester_count"])
        - float(bool(parsed["amide_present"])),
    )
    return {
        "formal_charge": formal_charge,
        "positive_atom_count": positive_atoms,
        "negative_atom_count": negative_atoms,
        "phosphate_count": float(parsed["phosphate_count"]),
        "glycerol_backbone": float(bool(parsed["glycerol_backbone_present"])),
        "sphingoid_backbone": float(bool(parsed["sphingoid_base_present"])),
        "tail_count": float(parsed["tail_count"]),
        "ester_tail_count": float(parsed["ester_count"]),
        "ether_tail_count": ether_tail_count,
        "amide_tail": float(bool(parsed["amide_present"])),
        "sugar_ring_count": float(parsed["sugar_ring_count"]),
        "sulfate_present": float(bool(parsed["sulfate_present"])),
        "carbon_count": float(parsed["carbon_count"]),
        "carbon_double_bond_count": carbon_double_bonds,
        "logp": logp,
        "tpsa": tpsa,
        "molar_refractivity": molar_refractivity,
        "rotatable_bond_count": rotatable_bond_count,
        "aromatic_ring_count": aromatic_ring_count,
        "ring_count": ring_count,
        "npr1": npr1_value,
        "npr2": npr2_value,
        # dataloader.pair_descriptors.LIPID_DESCRIPTOR_NAMES' own short aliases
        # (--descriptor_names=chain,unsaturation,hbond,heavy in a real arg file) --
        # the SAME functions dataloader.chemistry_prior._lipid_descriptor_table
        # calls for the network's own null-model/PairDescriptorHead path (cache hit
        # or not, see above), so a value under this name can never drift from what
        # --descriptor_names=chain,... actually feeds the network. That function
        # mean-pools over candidates; explicit_lipid_features' own per-species
        # reduction is a median (see its docstring) -- these values are aggregated
        # the same way every other column here is, not literally reproduced
        # number-for-number against the null-model table.
        "chain": chain_value,
        "unsaturation": unsaturation_value,
        "hbond": hbond_value,
        "heavy": heavy_value,
    }


_EXPLICIT_LIPID_FEATURES_CACHE: dict[tuple[int, int], pd.DataFrame] = {}


def explicit_lipid_features(table: pd.DataFrame, npr_cache: dict | None = None) -> pd.DataFrame:
    """Interpretable lipid features, derived only from fields already in the CSV.

    Head-group is one-hot encoded from the table's canonical full-name class.  Chemical
    counts are medians across the documented candidate isomers, while acyl composition
    uses ChainFragments when present.  Thus a candidate enumeration cannot turn into an
    arbitrary first-isomer choice.

    `npr_cache`: a dataloader.pair_descriptor_cache.load_pair_descriptor_cache result,
    or None to auto-load the project's own on-disk cache (data/pair_descriptor_cache_
    deterministic_<fingerprint>.json) -- the SAME cache dataloader/pair_descriptors.py's
    network path reads, so npr1/npr2/chain/unsaturation/hbond/heavy (the only fields
    this module does not always compute itself from scratch) are a dict lookup here
    too instead of a fresh ETKDG+MMFF embed or RDKit reparse, once
    `data/build_pair_descriptor_cache.py` has been run since those were added. None
    (not an error) when no current cache exists -- _candidate_explicit_features falls
    back to computing them directly, exactly as before this cache was wired in.

    Memoized by (id(table), id(npr_cache)) in-process: build_lipid_kernel's
    "explicit"/"explicit_subset" branches call this once per (family, seed) block
    with the SAME table object and the SAME npr_cache argument (None, every time,
    letting it resolve below) -- without this, every one of those calls reprocessed
    every one of this project's ~1300 lipid candidates through RDKit from scratch
    (id(npr_cache) covers the None case too: id(None) is one fixed value for the
    whole process, so repeat calls hit this cache before even touching the on-disk
    cache file, not just before the RDKit work).
    """
    cache_key = (id(table), id(npr_cache))
    cached = _EXPLICIT_LIPID_FEATURES_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if npr_cache is None:
        npr_cache = load_pair_descriptor_cache(PROJECT_ROOT / "data", isomeric=False)
    records = []
    classes = csv_classes(table)
    species_rows = table.assign(_lipid_class=classes).drop_duplicates("FullIdentityOfLipid")
    all_classes = sorted(classes.unique())
    for _, row in species_rows.iterrows():
        # SmileGlobal is "0" (a stand-in, not a structure) for about a third of the
        # catalog's species; SmileFragment carries a real, detailed candidate SMILES
        # set for those same rows. Fall back to it rather than let RDKit fail on the
        # placeholder and every downstream feature degrade to its mol-is-None default.
        smiles_source = (
            row["SmileGlobal"]
            if str(row["SmileGlobal"]).strip() not in ("", "0")
            else row["SmileFragment"]
        )
        candidates = [
            _candidate_explicit_features(smiles, npr_cache=npr_cache)
            for smiles in _candidate_smiles(smiles_source)
        ]
        if not candidates:
            raise ValueError(f"{row['FullIdentityOfLipid']}: empty SmileGlobal candidate set")
        candidate_table = pd.DataFrame(candidates)
        values = candidate_table.median(numeric_only=True).to_dict()
        chain_count, total_carbon, mean_carbon, max_carbon, total_unsaturation = _chain_composition(
            row.get("ChainFragments", ""), row.get("Lipid", "")
        )
        if not np.isfinite(chain_count):
            chain_count = values["tail_count"]
        if not np.isfinite(total_carbon):
            total_carbon = values["carbon_count"]
        if not np.isfinite(mean_carbon):
            mean_carbon = total_carbon / max(chain_count, 1.0)
        if not np.isfinite(max_carbon):
            max_carbon = mean_carbon
        if not np.isfinite(total_unsaturation):
            total_unsaturation = values["carbon_double_bond_count"]
        # The reverse gap: when every candidate's SMILES fails to parse (RDKit
        # returns no molecule), _candidate_explicit_features leaves its own
        # "carbon_double_bond_count" NaN and nothing here ever patched THAT field
        # back -- only total_unsaturation got a fallback. Chain-composition text
        # (species name / ChainFragments) is available for nearly every species even
        # when its structure isn't, so borrow the same count in the other direction.
        if not np.isfinite(values["carbon_double_bond_count"]):
            values["carbon_double_bond_count"] = total_unsaturation
        values.update(
            {
                "chain_count": chain_count,
                "total_chain_carbons": total_carbon,
                "mean_chain_carbons": mean_carbon,
                "max_chain_carbons": max_carbon,
                "total_unsaturation": total_unsaturation,
            }
        )
        values["FullIdentityOfLipid"] = row["FullIdentityOfLipid"]
        lipid_class = row["_lipid_class"]
        for name in all_classes:
            values[f"headgroup::{name}"] = float(lipid_class == name)
        records.append(values)
    result = pd.DataFrame(records).set_index("FullIdentityOfLipid").sort_index()
    _EXPLICIT_LIPID_FEATURES_CACHE[cache_key] = result
    return result


def standardize_from_train(
    features: pd.DataFrame, train_names: list[str] | tuple[str, ...]
) -> pd.DataFrame:
    """Standardize only by training objects; constants remain zero."""
    train = features.loc[list(train_names)]
    mean = train.mean(axis=0)
    scale = train.std(axis=0, ddof=0).replace(0.0, 1.0)
    return (features - mean) / scale


def rbf_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Unit-diagonal RBF kernel with train-only z-scoring and fixed gamma=1/d."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    squared_distance = ((left[:, None, :] - right[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-squared_distance / max(left.shape[1], 1))


def linear_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Train-only z-scored dot product. A cheaper alternative to `rbf_kernel` for
    feature vectors where scale, not just direction, carries information."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    return left @ right.T


def cosine_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Train-only z-scored cosine similarity. Suited to embedding-style vectors (e.g. a
    user-supplied protein language model pooling) where only direction should count."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    left = left / np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-12)
    right = right / np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-12)
    return left @ right.T


KERNEL_FUNCTIONS = {"rbf": rbf_kernel, "linear": linear_kernel, "cosine": cosine_kernel}


def _require_finite(features: pd.DataFrame, entities: list[str]) -> None:
    """A NaN/inf feature value does not stay local: standardize_from_train's z-score
    turns it into a NaN row of the kernel, and a single NaN anywhere in a kernel makes
    np.linalg.solve return an all-NaN result for the WHOLE block, not just that one
    entity's pair -- see kronrls_baseline.py's --lipid_kernel=explicit failure, one
    species with an unparseable SmileGlobal ("0") silently NaN-ed every AUC in every
    family/seed/lambda combination. Fail loud here instead, naming the entity.
    """
    subset = features.loc[list(entities)]
    finite = np.isfinite(subset.to_numpy(dtype=float))
    bad_rows = subset.index[~finite.all(axis=1)]
    if len(bad_rows):
        bad_columns = subset.columns[~finite.all(axis=0)].tolist()
        raise ValueError(
            f"non-finite feature values for {list(bad_rows)} (columns: {bad_columns}); "
            "fix or drop these entities before building the kernel -- see _require_finite"
        )


def _feature_kernel(
    kernel_type: str,
    features: pd.DataFrame,
    entities: list[str],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    _require_finite(features, entities)
    try:
        function = KERNEL_FUNCTIONS[kernel_type]
    except KeyError:
        raise ValueError(
            f"unknown kernel_type {kernel_type!r}; expected one of {sorted(KERNEL_FUNCTIONS)}"
        )
    return function(features, entities, entities, train_names)


def load_feature_table(path: Path | str, index_name: str) -> pd.DataFrame:
    """Arbitrary externally supplied entity vectors: first CSV column is the entity id
    (must match `LTPProtein` / `FullIdentityOfLipid` values exactly), the rest are
    numeric features of any kind -- there is no fixed schema here by design."""
    table = pd.read_csv(path)
    id_column = table.columns[0]
    table = table.set_index(id_column)
    table.index = table.index.astype(str)
    table.index.name = index_name
    numeric = table.apply(pd.to_numeric, errors="coerce")
    bad = numeric.index[numeric.isna().any(axis=1)]
    if len(bad):
        raise ValueError(f"{path}: non-numeric or missing feature values for {list(bad)}")
    return numeric


def load_precomputed_kernel(
    path: Path | str, names_path: Path | str
) -> tuple[np.ndarray, dict[str, int]]:
    """A user-supplied square similarity/kernel matrix (e.g. an ESM3-embedding cosine
    matrix, or any other precomputed measure) used as-is, without recomputing it from
    feature vectors. `names_path` lists one entity name per line, in the matrix's row
    and column order."""
    matrix = np.load(path).astype(np.float64)
    names = [line.strip() for line in Path(names_path).read_text().splitlines() if line.strip()]
    if matrix.shape != (len(names), len(names)):
        raise ValueError(
            f"{path}: matrix shape {matrix.shape} does not match {len(names)} names in {names_path}"
        )
    return matrix, {name: position for position, name in enumerate(names)}


def _kernel_from_index(
    matrix: np.ndarray, index: dict[str, int], entities: list[str], source: str
) -> np.ndarray:
    missing = sorted(set(entities) - set(index))
    if missing:
        raise ValueError(f"{source} is missing entities: {missing}")
    positions = [index[name] for name in entities]
    kernel = matrix[np.ix_(positions, positions)]
    if not np.isfinite(kernel).all():
        bad = sorted(
            entities[row] for row in range(len(entities))
            if not np.isfinite(kernel[row]).all()
        )
        raise ValueError(
            f"{source}: non-finite kernel values involving {bad}; a NaN/inf here "
            "would silently poison the whole solve for every entity, not just "
            "these -- fix the source matrix before using it"
        )
    return kernel


def build_protein_kernel(
    kind: str,
    entities: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
    graphs: Path | str = DEFAULT_GRAPHS,
    kernel_type: str = "rbf",
    descriptor_names: list[str] | tuple[str, ...] | None = None,
    features_path: Path | str | None = None,
    kernel_path: Path | str | None = None,
    names_path: Path | str | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build a protein x protein kernel over `entities`, standardized by `train_names`
    only. `kind` selects the feature source:

    - "pocket13" / "pocket23": the full 13- or 23-name pocket-shape descriptor set.
    - "pocket_subset": the same pocket descriptors, restricted to `descriptor_names`
      (any subset of POCKET_ALL_NAMES -- pocket23 plus dataloader/pair_descriptors.
      py's PROTEIN_DESCRIPTOR_NAMES' four further promotions: ev28_q10,
      aromatic_share_rim, hydropathy_mean, ev14_q10) -- use this to match a network
      run's own `--pocket_descriptor_names`/`--protein_descriptors` exactly, e.g.
      the project's "protgeom8" or full "protunion14" set.
    - "custom_features": any vectors of your own (`features_path`, see
      `load_feature_table`), turned into a kernel via `kernel_type`.
    - "custom_kernel": a precomputed similarity/kernel matrix of your own
      (`kernel_path` + `names_path`, see `load_precomputed_kernel`), used directly.
    """
    entities = list(entities)
    if kind in ("pocket13", "pocket23"):
        features = protein_pocket_features(entities, graphs)
        names = POCKET13_NAMES if kind == "pocket13" else POCKET23_NAMES
        kernel = _feature_kernel(kernel_type, features.loc[:, names], entities, train_names)
    elif kind == "pocket_subset":
        if not descriptor_names:
            raise ValueError("descriptor_names is required for protein_kernel=pocket_subset")
        features = resolve_protein_feature_subset(entities, list(descriptor_names), graphs)
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_features":
        if features_path is None:
            raise ValueError("--protein_features is required for protein_kernel=custom_features")
        features = load_feature_table(features_path, index_name="LTPProtein")
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"{features_path} is missing proteins: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_kernel":
        if kernel_path is None or names_path is None:
            raise ValueError(
                "--protein_kernel_matrix and --protein_kernel_names are required "
                "for protein_kernel=custom_kernel"
            )
        matrix, index = load_precomputed_kernel(kernel_path, names_path)
        kernel = _kernel_from_index(matrix, index, entities, str(kernel_path))
    else:
        raise ValueError(
            f"unknown protein kernel {kind!r}; expected pocket13, pocket23, "
            "pocket_subset, custom_features, or custom_kernel"
        )
    return kernel, {name: position for position, name in enumerate(entities)}


def build_lipid_kernel(
    kind: str,
    table: pd.DataFrame,
    entities: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
    kernel_type: str = "rbf",
    descriptor_names: list[str] | tuple[str, ...] | None = None,
    features_path: Path | str | None = None,
    kernel_path: Path | str | None = None,
    names_path: Path | str | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build a lipid x lipid kernel over `entities`, standardized by `train_names` only.
    `kind` selects the feature source:

    - "tanimoto": the existing Morgan-fingerprint species similarity. `table` MUST be
      the full, unfiltered, original-row-order interaction table (see
      `species_tanimoto_similarity` -- it is positionally aligned to the compact
      Tanimoto artefacts, not to any subset).
    - "tanimoto_headgroup": the same, but on the head group only, acyl tails cut off
      first (species_headgroup_tanimoto_similarity, preprocessing/build_tanimoto_
      headgroup.py's artefacts) -- same positional-alignment requirement on `table`.
    - "molformer": the network's own lipid input -- raw 768-dim MolFormer embedding
      per species (molformer_lipid_features), turned into a kernel via kernel_type,
      same as "explicit" -- not a precomputed similarity artefact.
    - "explicit": the existing interpretable lipid descriptors, turned into a kernel
      via `kernel_type`.
    - "explicit_subset": the same explicit_lipid_features table, restricted to
      `descriptor_names` -- the lipid-side mirror of build_protein_kernel's
      "pocket_subset", for picking a specific descriptor combination (e.g. just the
      new logp/tpsa/molar_refractivity/rotatable_bond_count/aromatic_ring_count/
      ring_count whole-molecule set) instead of every explicit column at once, the
      same way mixing all 17 explicit+family_neutral columns into one RBF kernel
      diluted the signal (files/cron.md) rather than helping it. Names are checked
      against the columns explicit_lipid_features(table) actually produced for THIS
      table (not a fixed list) since headgroup::<class> one-hot columns depend on
      the lipid classes present.
    - "custom_features" / "custom_kernel": your own vectors or precomputed kernel, same
      contract as `build_protein_kernel`.
    """
    entities = list(entities)
    if kind == "tanimoto":
        similarity, index = species_tanimoto_similarity(table)
        kernel = _kernel_from_index(similarity.astype(float), index, entities, "tanimoto similarity")
    elif kind == "tanimoto_headgroup":
        similarity, index = species_headgroup_tanimoto_similarity(table)
        kernel = _kernel_from_index(
            similarity.astype(float), index, entities, "head-group tanimoto similarity"
        )
    elif kind == "molformer":
        # The network's own lipid input -- raw 768-dim MolFormer embedding per
        # species (molformer_lipid_features), turned into a kernel via kernel_type,
        # same pattern as "explicit". NOT species_tanimoto_similarity-style: no
        # precomputed similarity artefact, no `table`-row positional alignment.
        features = molformer_lipid_features(table)
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"molformer embedding is missing for lipids: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "explicit":
        features = explicit_lipid_features(table)
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"explicit lipid features are missing: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "explicit_subset":
        if not descriptor_names:
            raise ValueError("descriptor_names is required for lipid_kernel=explicit_subset")
        subset = resolve_lipid_feature_subset(table, descriptor_names)
        missing = sorted(set(entities) - set(subset.index))
        if missing:
            raise ValueError(f"explicit lipid features are missing: {missing}")
        kernel = _feature_kernel(kernel_type, subset, entities, train_names)
    elif kind == "custom_features":
        if features_path is None:
            raise ValueError("--lipid_features is required for lipid_kernel=custom_features")
        features = load_feature_table(features_path, index_name="FullIdentityOfLipid")
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"{features_path} is missing lipids: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_kernel":
        if kernel_path is None or names_path is None:
            raise ValueError(
                "--lipid_kernel_matrix and --lipid_kernel_names are required "
                "for lipid_kernel=custom_kernel"
            )
        matrix, index = load_precomputed_kernel(kernel_path, names_path)
        kernel = _kernel_from_index(matrix, index, entities, str(kernel_path))
    else:
        raise ValueError(
            f"unknown lipid kernel {kind!r}; expected tanimoto, tanimoto_headgroup, molformer, "
            "explicit, explicit_subset, custom_features, or custom_kernel"
        )
    return kernel, {name: position for position, name in enumerate(entities)}


def species_tanimoto_similarity(table: pd.DataFrame) -> tuple[np.ndarray, dict[str, int]]:
    """Species Tanimoto, max-reduced over the same candidate structures as the loader."""
    data_dir = PROJECT_ROOT / "data"
    matrix = np.load(data_dir / "Tanimoto_compact_isomeric_matrix_uint8.npy").astype(np.float32) / 255.0
    structure_index = np.load(data_dir / "Tanimoto_compact_isomeric_structure_index.npy")
    row_ids = np.load(data_dir / "Tanimoto_compact_isomeric_row_ids.npy")
    structures_of_row: dict[int, set[int]] = {}
    for row_id, structure in zip(row_ids, structure_index):
        structures_of_row.setdefault(int(row_id), set()).add(int(structure))
    structures_of_species: dict[str, set[int]] = {}
    for row_position, species in enumerate(table["FullIdentityOfLipid"]):
        structures_of_species.setdefault(species, set()).update(
            structures_of_row.get(row_position, set())
        )
    names = sorted(structures_of_species)
    index = {name: position for position, name in enumerate(names)}
    similarity = np.empty((len(names), len(names)), dtype=np.float32)
    for position, name in enumerate(names):
        source = matrix[sorted(structures_of_species[name]), :].max(axis=0)
        similarity[position] = [
            source[sorted(structures_of_species[other])].max() for other in names
        ]
    return similarity, index


def molformer_lipid_features(table: pd.DataFrame) -> pd.DataFrame:
    """768-dim MolFormer embedding per lipid species -- the network's own lipid input.

    The SAME per-species vector architecture/lipid_encoder.py's
    `torch.nn.Linear(768, hiddim)` consumes directly (see any `..._liphid32.md` arg
    file's own header: "ONE torch.nn.Linear(768, hiddim) over a MolFormer
    embedding"). Mean-pooled over MolFormer's token dimension, then over a species'
    candidate isomer structures (preprocessing.lipid_embedding_identity_check.
    species_embeddings, reading data/lipid_SMILES_embedding_deterministic.pkl or its
    mmap store) -- the RAW embedding, not preprocessing/build_molformer_similarity_
    matrix.py's derived species x species similarity (that one is for analysis/
    null_model.py's --features=molformer null model, a different, already-reduced
    artefact). --lipid_kernel=molformer turns THIS into a kernel via
    --lipid_kernel_type, matching how "explicit" turns hand-built descriptors into
    one -- a network's own embedding is what the fit sees, not a lookup similarity.
    """
    from dataloader.lipid_embedding_store import load_lipid_embedding_store
    from preprocessing.lipid_embedding_identity_check import EMBEDDING_FILE, species_embeddings

    data_dir = PROJECT_ROOT / "data"
    smiles_encoding = load_lipid_embedding_store(data_dir, EMBEDDING_FILE)
    if smiles_encoding is None:
        import pickle

        with open(data_dir / EMBEDDING_FILE, "rb") as handle:
            smiles_encoding = pickle.load(handle)
    vectors, missing_species, _ = species_embeddings(table, smiles_encoding)
    if missing_species:
        print(
            f"molformer_lipid_features: {len(missing_species)} species with no "
            "resolvable embedding, excluded (same as build_molformer_similarity_"
            f"matrix.py's own warning): {sorted(missing_species)[:10]}"
        )
    names = sorted(vectors)
    matrix = np.stack([vectors[name] for name in names])
    return pd.DataFrame(matrix, index=pd.Index(names, name="FullIdentityOfLipid"))


_PROTEIN_DESCRIPTOR_TABLE_CACHE: dict | None = None


def _protein_catalog_features(proteins: list[str], names: list[str]) -> pd.DataFrame:
    """Per-protein feature columns for `names` (a subset of dataloader.pair_
    descriptors.PROTEIN_DESCRIPTOR_NAMES/PROTEIN_DERIVED_DESCRIPTOR_NAMES), read
    straight from dataloader.chemistry_prior.protein_descriptor_table -- the
    network's own cached, self-persisting per-protein table for the FULL descriptor
    catalog (data/protein_descriptor_table.json) -- rather than reimplementing each
    one by hand the way protein_pocket_features does for its own (partial) column
    set (POCKET_ALL_NAMES: pocket23 plus the four family_neutral promotions, not the
    three lambda_sqrt shape variants or anything newer). Mirrors
    _lipid_catalog_features' role on the lipid side. Used by build_protein_kernel's
    pocket_subset branch, the only caller: for any requested name protein_pocket_
    features does not already carry as a column.
    """
    global _PROTEIN_DESCRIPTOR_TABLE_CACHE
    if _PROTEIN_DESCRIPTOR_TABLE_CACHE is None:
        from dataloader.chemistry_prior import protein_descriptor_table

        _PROTEIN_DESCRIPTOR_TABLE_CACHE = protein_descriptor_table(str(PROJECT_ROOT / "data"))
    return pd.DataFrame.from_dict(_PROTEIN_DESCRIPTOR_TABLE_CACHE, orient="index").loc[
        list(proteins), names
    ]


def resolve_protein_feature_subset(
    proteins: list[str], names: list[str], graphs: Path | str = DEFAULT_GRAPHS
) -> pd.DataFrame:
    """Per-protein feature columns for `names` -- shared resolution behind
    build_protein_kernel's pocket_subset branch, mirroring resolve_lipid_feature_
    subset on the lipid side.

    Resolution order: protein_pocket_features' own (partial) columns (POCKET_ALL_
    NAMES) first; anything not there but in dataloader.pair_descriptors.
    PROTEIN_DESCRIPTOR_NAMES/PROTEIN_DERIVED_DESCRIPTOR_NAMES (e.g. the three
    *_lambda_sqrt shape variants) from _protein_catalog_features instead of being
    rejected. Raises ValueError on any other unknown name.
    """
    features = protein_pocket_features(proteins, graphs)
    unknown = sorted(set(names) - set(features.columns))
    catalog_names = set(PROTEIN_DESCRIPTOR_NAMES) | set(PROTEIN_DERIVED_DESCRIPTOR_NAMES)
    catalog_only = sorted(set(unknown) & catalog_names)
    unknown = sorted(set(unknown) - set(catalog_only))
    if unknown:
        raise ValueError(
            f"unknown pocket descriptor names: {unknown}. Known: "
            f"{sorted(set(features.columns) | catalog_names)}"
        )
    if catalog_only:
        features = features.join(_protein_catalog_features(proteins, catalog_only), how="left")
    return features.loc[:, list(names)]


_LIPID_DESCRIPTOR_TABLE_CACHE: dict[int, dict] = {}


def _lipid_catalog_features(table: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """`names` (a subset of dataloader.pair_descriptors.LIPID_DESCRIPTOR_NAMES) as a
    per-species DataFrame, read straight from dataloader.chemistry_prior.
    _lipid_descriptor_table -- the network's own cached, mean-over-candidates
    per-species table for the FULL descriptor catalog -- rather than reimplementing
    each one by hand the way explicit_lipid_features does for its own (partial,
    median-aggregated) column set. See build_lipid_kernel's explicit_subset branch,
    the only caller: it uses this for any requested name explicit_lipid_features
    does not already carry as a column.

    Memoized by id(table) (like explicit_lipid_features' own cache) -- _lipid_
    descriptor_table already self-persists to data/lipid_descriptor_table.json, but
    still re-reads/re-validates that file and rebuilds a fresh per-species dict from
    it on every call; this avoids paying that repeatedly across a run's (family,
    seed) blocks the same way explicit_lipid_features' own cache does.
    """
    table_by_species = _LIPID_DESCRIPTOR_TABLE_CACHE.get(id(table))
    if table_by_species is None:
        from dataloader.chemistry_prior import _lipid_descriptor_table

        table_by_species = _lipid_descriptor_table(table, PROJECT_ROOT / "data")
        _LIPID_DESCRIPTOR_TABLE_CACHE[id(table)] = table_by_species
    return pd.DataFrame.from_dict(table_by_species, orient="index").loc[:, names]


def resolve_lipid_feature_subset(table: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """Per-species feature columns for `names` -- shared by build_lipid_kernel's
    explicit_subset branch and analysis/gbm_baseline.py's row-feature builder, so
    the two baselines' --lipid_features shorthand can never silently drift on what a
    name resolves to.

    Resolution order: explicit_lipid_features' own (partial, median-aggregated)
    columns first; anything not there but IN dataloader.pair_descriptors.
    LIPID_DESCRIPTOR_NAMES (the network's own descriptor catalog -- e.g.
    experimental_lipid_volume, the tail_* measures) from _lipid_catalog_features
    instead of being rejected; the special name "molformer" (the network's own raw
    768-dim embedding, molformer_lipid_features -- a genuine per-species feature
    table, unlike a pairwise similarity artefact, so it CAN sit alongside named
    descriptors) joined in last. Raises ValueError on any other unknown name, with a
    hint when it actually names a whole different --lipid_kernel/
    --lipid_similarity_feature (e.g. "tanimoto" -- a pairwise similarity, not a
    per-entity column, so it cannot be mixed in here).
    """
    requested = list(names)
    include_molformer = "molformer" in requested
    named = [name for name in requested if name != "molformer"]
    features = explicit_lipid_features(table)
    unknown = sorted(set(named) - set(features.columns))
    catalog_only = sorted(set(unknown) & set(LIPID_DESCRIPTOR_NAMES))
    unknown = sorted(set(unknown) - set(catalog_only))
    if unknown:
        kernel_keywords = sorted(set(unknown) & {"tanimoto", "tanimoto_headgroup", "explicit"})
        hint = (
            f" {kernel_keywords} name a whole different --lipid_kernel/--lipid_"
            "similarity_feature (a fingerprint SIMILARITY, not a descriptor column) "
            "-- cannot mix one in alongside named descriptors; pick a single one."
            if kernel_keywords else ""
        )
        raise ValueError(
            f"unknown explicit lipid descriptor names: {unknown}.{hint} "
            f"Known: {sorted(set(features.columns) | set(LIPID_DESCRIPTOR_NAMES))} "
            "(plus the special name 'molformer')"
        )
    if catalog_only:
        features = features.join(_lipid_catalog_features(table, catalog_only), how="left")
    subset = features.loc[:, named] if named else pd.DataFrame(index=features.index)
    if include_molformer:
        subset = subset.join(molformer_lipid_features(table).add_prefix("molformer_"), how="inner")
    return subset


def species_headgroup_tanimoto_similarity(table: pd.DataFrame) -> tuple[np.ndarray, dict[str, int]]:
    """Species Tanimoto restricted to the head group -- acyl tails cut off first.

    Same max-reduction-over-candidate-structures scheme as species_tanimoto_
    similarity, over preprocessing/build_tanimoto_headgroup.py's artefacts instead
    of build_tanimoto_compact.py's: every candidate SMILES has its qualifying acyl
    tails removed (dataloader.pair_descriptors._qualifying_tails' rule) before the
    Tanimoto matrix is built, so two species differing only in chain length/
    unsaturation collapse onto the same head-group fingerprint. Answers "does
    headgroup chemistry alone carry the signal", the direct chemical counterpart
    of --lipid_coldsplit's own class-name-based holdout (LIPID_COLDSPLIT_SETS
    groups by the same head-group boundary, just categorically instead of by
    structure) -- a species-level Tanimoto lookup that does not need the class
    name at all, so it can rank NOVEL head groups too, not just the four named
    ones. Non-isomeric only (no *_isomeric* artefact has been built for this yet);
    unlike species_tanimoto_similarity this does not require --lipid_isomers
    parity, since head-group fingerprints normally do not depend on tail
    stereochemistry.
    """
    data_dir = PROJECT_ROOT / "data"
    matrix = (
        np.load(data_dir / "Tanimoto_headgroup_compact_matrix_uint8.npy").astype(np.float32)
        / 255.0
    )
    structure_index = np.load(data_dir / "Tanimoto_headgroup_compact_structure_index.npy")
    row_ids = np.load(data_dir / "Tanimoto_headgroup_compact_row_ids.npy")
    structures_of_row: dict[int, set[int]] = {}
    for row_id, structure in zip(row_ids, structure_index):
        structures_of_row.setdefault(int(row_id), set()).add(int(structure))
    structures_of_species: dict[str, set[int]] = {}
    for row_position, species in enumerate(table["FullIdentityOfLipid"]):
        structures_of_species.setdefault(species, set()).update(
            structures_of_row.get(row_position, set())
        )
    names = sorted(structures_of_species)
    index = {name: position for position, name in enumerate(names)}
    similarity = np.empty((len(names), len(names)), dtype=np.float32)
    for position, name in enumerate(names):
        source = matrix[sorted(structures_of_species[name]), :].max(axis=0)
        similarity[position] = [
            source[sorted(structures_of_species[other])].max() for other in names
        ]
    return similarity, index


def two_step_kronrls(
    protein_kernel: np.ndarray,
    lipid_kernel: np.ndarray,
    labels: np.ndarray,
    protein_lambda: float,
    lipid_lambda: float,
) -> np.ndarray:
    """Solve the regularized two-step KronRLS coefficient matrix.

    For a train label matrix Y, predictions are Kp_test,train @ A @
    Kl_train,test, with A = (Kp + λp I)^−1 Y (Kl + λl I)^−1.
    """
    if labels.shape != (protein_kernel.shape[0], lipid_kernel.shape[0]):
        raise ValueError("labels must align with the train protein and lipid kernels")
    left = np.linalg.solve(
        protein_kernel + protein_lambda * np.eye(len(protein_kernel)), labels
    )
    return np.linalg.solve(
        lipid_kernel + lipid_lambda * np.eye(len(lipid_kernel)), left.T
    ).T


def predict_kronrls(
    coefficients: np.ndarray,
    protein_kernel_query_train: np.ndarray,
    lipid_kernel_train_query: np.ndarray,
) -> np.ndarray:
    """Score (protein, lipid) pairs whose protein and/or lipid need not have been in
    training. `coefficients` is `two_step_kronrls`'s return value, `A = (Kp+lambda_p I)^-1
    Y (Kl+lambda_l I)^-1`. `protein_kernel_query_train` is `[n_query_proteins,
    n_train_proteins]`, `lipid_kernel_train_query` is `[n_train_lipids,
    n_query_lipids]`; querying exactly the training entities (i.e. passing the training
    kernels themselves) recovers the fitted training-block scores, `Kp @ A @ Kl`.
    """
    return protein_kernel_query_train @ coefficients @ lipid_kernel_train_query


def pair_prediction_frame(
    held: pd.DataFrame,
    protein_scores: np.ndarray,
    proteins: list[str],
    lipid_scores: np.ndarray,
    lipids: list[str],
) -> pd.DataFrame:
    """Map a score rectangle back to every original held-out assay row."""
    p_index = {name: position for position, name in enumerate(proteins)}
    l_index = {name: position for position, name in enumerate(lipids)}
    result = held.copy()
    result["score"] = [
        float(protein_scores[p_index[p], l_index[l]])
        for p, l in zip(result["LTPProtein"], result["FullIdentityOfLipid"])
    ]
    return result


def train_threshold(
    table: pd.DataFrame,
    all_proteins: list[str],
    all_lipids: list[str],
    protein_kernel: np.ndarray,
    protein_index: dict[str, int],
    lipid_kernel: np.ndarray,
    lipid_index: dict[str, int],
    coefficients: np.ndarray,
    metric: str = "balanced_accuracy",
) -> float:
    """The decision threshold for an already-fit production model (one fit, on ALL
    data, nothing held out) -- read directly off that SAME fit's own scores on its own
    training rows. One fit, one threshold search, no second model, no held-out split:
    `predict_kronrls` queried with the training kernels themselves reproduces the
    training-block scores exactly (see its own docstring), so this is literally
    best_threshold_for_metric on train -- no folds, no re-fitting.
    """
    scores = predict_kronrls(coefficients, protein_kernel[
        np.ix_([protein_index[name] for name in all_proteins],
               [protein_index[name] for name in all_proteins])
    ], lipid_kernel[
        np.ix_([lipid_index[name] for name in all_lipids],
               [lipid_index[name] for name in all_lipids])
    ])
    protein_position = {name: position for position, name in enumerate(all_proteins)}
    lipid_position = {name: position for position, name in enumerate(all_lipids)}
    row_scores = np.array([
        scores[protein_position[protein], lipid_position[lipid]]
        for protein, lipid in zip(table["LTPProtein"], table["FullIdentityOfLipid"])
    ])
    threshold, _ = best_threshold_for_metric(
        table["Interaction"].to_numpy(), row_scores, metric=metric
    )
    return float(threshold)
