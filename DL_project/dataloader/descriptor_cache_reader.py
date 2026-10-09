"""Shared read path for descriptor VALUES, stored as three plain CSV tables:

    data/protein_descriptors.csv   one row per protein (dataloader/chemistry_prior.py's
                                    protein_descriptor_table -- this module does not
                                    touch it, see Dataloader.py's own read of it).
    data/lipid_descriptors.csv     one row per (canonical candidate SMILES, isomeric
                                    variant) -- every _MEASURES entry, always, read and
                                    written by THIS module.
    data/pair_descriptors.csv      one row per (candidate SMILES, protein, isomeric
                                    variant) actually present in the interaction table --
                                    every PAIR_DESCRIPTOR_NAMES value, read and written
                                    by this module (build_pair_value_cache/
                                    load_pair_value_cache below).

Builders (data/build_descriptor_cache.py calls them, before a grid launches) live in
dataloader/cache_builders/descriptor_csv_builder.py; this module is the read side plus the
code-fingerprinting that decides what either builder may still serve from an existing
table and what it must recompute.

Dataloader.py._compute_pair_descriptors runs RDKit over every candidate SMILES in the
interaction table (chain length, unsaturation, H-bond capacity, heavy-atom count, tail
count, and the three conformer-based lipid-shape measures) -- none of which depends on
--seed or --excluded_groups. A local grid launches one process per (group, seed) pair
(scripts/run_local.sh), so an untouched, unregenerated interaction table still gets this
work redone from scratch in every one of those processes if nothing shares it.

Built once by data/build_descriptor_cache.py (scripts/run_local.sh calls it alongside
data/build_lipid_embedding_store.py, before the grid launches) and read by every job
afterwards: every process just does a dict lookup against what is already in
data/lipid_descriptors.csv, never RDKit at load time.

Every measure this module knows how to compute is ALWAYS included -- no flag gates any of
them out of a build. Three of them (radius_of_gyration/asphericity/molecular_volume,
LIPID_SHAPE_DESCRIPTOR_NAMES) are genuinely expensive (a 10-conformer ETKDG+MMFF embed per
candidate, not microseconds like the rest), so the values are filled through a process
pool (dataloader/cache_builders/descriptor_csv_builder.py's _parallel_measures) -- ~1300
unique candidates on a 24-core box still takes real minutes the first time any build runs,
but it is paid exactly once per (isomeric, code version, table version), never per run and
never per job.

Two things the manifest (data/lipid_descriptors.manifest.json) carries, because two
different reads need canonicalisation skipped entirely to pay off:

    raw_to_canonical : {"deterministic": {...}, "isomeric": {...}} -- the exact candidate
                        string as it appears in the interaction table -> its canonical
                        SMILES, or None where RDKit cannot parse it, one dict per variant
                        (the same raw string can canonicalise differently depending on
                        isomeric). Without this, chain_lengths_by_row/
                        descriptor_values_by_row would still have to call
                        Chem.MolFromSmiles/MolToSmiles on every raw candidate just to know
                        which table row to look up.
    the CSV itself   : canonical SMILES, isomeric -> every _MEASURES entry (plus "chain"),
                        always -- read by `pandas.read_csv`, not re-parsed into a nested
                        dict on disk.

A raw string absent from raw_to_canonical (a candidate added to the table after the
cache was built) falls back to computing it directly, same as a store_is_current() miss
falls back to the source pickle in tensors_reading/lipid_embedding_tensors_reader.py -- the table is an
accelerator, never a second source of truth a stale run could disagree with the current
data from.

The manifest guards staleness the same way tensors_reading/protein_graph_tensors_reader.py does: the source
interaction table's size and nanosecond mtime must still match what the table was built
from, checked freshly on every load (cheap -- a couple of stat() calls, not a hash of file
contents).

The code that produced a value is NOT part of that question. These tables hold descriptor
numbers, and a column holding a number is a column this module serves: validity is the
data's, never the formula's. Editing a formula in preprocessing/compute_descriptors.py
therefore does not invalidate anything here -- recompute the affected column deliberately
(`python3 preprocessing/compute_descriptors.py NAME`) when a formula changes
and the stored numbers should follow it.
"""

import json
from pathlib import Path

import pandas as pd


# Bumped from the old per-(isomeric) JSON blob's version 2: the storage itself changed
# (one shared CSV table + a small sidecar manifest, no "proteins" sub-table any more --
# the protein side lives only in data/protein_descriptors.csv, built by
# dataloader/chemistry_prior.py's protein_descriptor_table), so an old-format manifest
# must read as stale rather than be misinterpreted.
CACHE_FORMAT_VERSION = 3



def lipid_descriptors_csv_path(root_dir):
    """data/lipid_descriptors.csv -- one row per (canonical candidate SMILES, isomeric
    variant), every _MEASURES entry (plus "chain"), always."""
    return Path(root_dir).resolve() / "lipid_descriptors.csv"


def lipid_descriptors_manifest_path(root_dir):
    """The small sidecar next to lipid_descriptors.csv: format version, per-measure code
    fingerprints, the source interaction table's size/mtime, and raw_to_canonical --
    bookkeeping only, never a descriptor value itself."""
    return Path(root_dir).resolve() / "lipid_descriptors.manifest.json"


def cache_path(root_dir, isomeric=None):
    """Backward-compatible alias for lipid_descriptors_csv_path.

    Deterministic and isomeric candidates used to live in two separate JSON files
    (one per `isomeric`); they now share one CSV table, distinguished by that table's
    own "isomeric" column, so this ignores `isomeric` and always returns the one path.
    Kept under its old name because existing callers (tests, the builder) still ask
    for "the cache path" without wanting to track that merge themselves.
    """
    return lipid_descriptors_csv_path(root_dir)


def load_lipid_descriptor_cache(root_dir, isomeric):
    """{"raw_to_canonical", "values"} -- everything still valid for this isomeric
    variant, or None.

    Deliberately not gated on every measure matching the current code (that question is
    `store_is_current`'s, "should the builder run"; this one is "what may I serve", and
    the two have different answers): a single changed formula drops only ITS OWN column
    from every entry, not the whole table.

    What is checked, and against what it is actually keyed:

      raw_to_canonical  one dict per variant inside the manifest, so it depends on
                         neither the CSV's rows nor any protein file. A regenerated
                         interaction table can only ADD candidates, and a candidate
                         absent from raw_to_canonical already falls back to direct
                         computation per miss (see dataloader/descriptors.py).
      values             read straight from lipid_descriptors.csv, filtered to this
                         variant's rows and, per measure, to names whose recorded
                         fingerprint still matches the code computing them -- so
                         `measure in entry`, what every caller already tests, stays the
                         exact question of validity.

    Returns None only when there is no readable, current-format table at all.
    """
    root_dir = Path(root_dir).resolve()
    csv_path = lipid_descriptors_csv_path(root_dir)
    manifest_path = lipid_descriptors_manifest_path(root_dir)
    if not csv_path.exists() or not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if manifest.get("format_version") != CACHE_FORMAT_VERSION:
        return None

    variant = "isomeric" if isomeric else "deterministic"
    raw_to_canonical = (manifest.get("raw_to_canonical") or {}).get(variant)
    if raw_to_canonical is None:
        return None

    try:
        # float_precision="round_trip": pandas' default C float parser is fast but
        # not always exact (a one-ULP drift the writer itself never introduces) --
        # round_trip serves back exactly the value _compute_one computed.
        table = pd.read_csv(csv_path, float_precision="round_trip")
    except (OSError, ValueError, pd.errors.ParserError, KeyError):
        return None
    if "isomeric" not in table.columns or "smiles" not in table.columns:
        return None
    table = table[table["isomeric"] == bool(isomeric)]

    # A column holding a number is a value this table may serve. Nothing here asks
    # whether the formula that produced it still has the same source text: the table
    # stores descriptor NUMBERS, and a number is either present or it is not.
    value_columns = [
        name for name in table.columns if name not in ("smiles", "isomeric")
    ]

    values = {}
    for _, row in table.iterrows():
        values[row["smiles"]] = {
            name: row[name] for name in value_columns if pd.notna(row[name])
        }

    return {"raw_to_canonical": raw_to_canonical, "values": values}


def store_is_current(root_dir, isomeric):
    """True when a table exists, its source still matches, and no value it holds moved.

    "Should the builder run", and it must answer that on the same terms the reader
    answers "what may I serve": a rebuild has something to do exactly when some value
    in this table would come out different now. That is per lipid measure
    (`measure_fingerprints`) plus the source interaction table's size/mtime --
    deliberately NOT a hash over the module as a whole, which is what this used to
    compare and which reported "rebuild" for a renamed local or an edited docstring in
    code no cached value depends on.
    """
    root_dir = Path(root_dir).resolve()
    csv_path = lipid_descriptors_csv_path(root_dir)
    manifest_path = lipid_descriptors_manifest_path(root_dir)
    if not csv_path.exists() or not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != CACHE_FORMAT_VERSION:
            return False
        variant = "isomeric" if isomeric else "deterministic"
        if variant not in (manifest.get("raw_to_canonical") or {}):
            return False
        for source in manifest.get("sources", []):
            stat = (root_dir / source["path"]).stat()
            if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
                return False
        return True
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return False


# --- pair-level (PAIR_DESCRIPTOR_NAMES) table ---------------------------------------
#
# occupancy/chain_extent_gap/aromatic_contact/hbond_match/volume_fit/buriedness_match/
# depth_bulk_match/hydropathy_chain_match/aromatic_contact_min/hbond_match_min/
# tail_elongation_fit/hydropathy_rim_match/elongation_shape_match/flatness_shape_match
# (dataloader.descriptors.pair_descriptor_value) are pure arithmetic over
# ALREADY-cached lipid values (data/lipid_descriptors.csv) and protein values
# (data/protein_descriptors.csv, dataloader/chemistry_prior.py's protein_descriptor_
# table) -- no RDKit, no pocket geometry, microseconds per (candidate, protein) pair.
# This is a separate table rather than more columns on the lipid rows above because a
# pair value needs BOTH a candidate AND a protein (a lipid's own values do not depend
# on which protein it is paired with), so the natural key is (smiles, protein,
# isomeric), not smiles alone.
#
# Not built for speed -- Dataloader.py's own inline pair_descriptor_value() calls over
# already-loaded numpy arrays cost about the same microseconds this table would save.
# Built so this is the one place the finished, genuinely joint lipid x protein numbers
# live on disk at all -- see dataloader/cache_builders/descriptor_csv_builder.py's
# build_pair_value_cache, the writer.


def pair_descriptors_csv_path(root_dir):
    """data/pair_descriptors.csv -- one row per (smiles, protein, isomeric) actually
    present in the interaction table, every PAIR_DESCRIPTOR_NAMES value."""
    return Path(root_dir).resolve() / "pair_descriptors.csv"


def pair_descriptors_manifest_path(root_dir):
    return Path(root_dir).resolve() / "pair_descriptors.manifest.json"


def pair_value_cache_is_current(root_dir, isomeric):
    """True when a pair-value table exists, matches the current code, and the lipid/
    protein tables it was built from are STILL current (rather than duplicating their
    own source lists here, defer to them directly -- this table's values are only ever
    as fresh as those two).
    """
    root_dir = Path(root_dir).resolve()
    path = pair_descriptors_csv_path(root_dir)
    manifest_path = pair_descriptors_manifest_path(root_dir)
    if not path.exists() or not manifest_path.exists():
        return False
    if not store_is_current(root_dir, isomeric):
        return False
    if not (root_dir / "protein_descriptors.csv").exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
        variant = "isomeric" if isomeric else "deterministic"
        return (
            manifest.get("format_version") == CACHE_FORMAT_VERSION
            and bool(manifest.get(f"built_{variant}"))
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return False


def load_pair_value_cache(root_dir, isomeric):
    """{(smiles, protein) key -> {PAIR_DESCRIPTOR_NAMES: value}} for this isomeric
    variant if current, else None."""
    if not pair_value_cache_is_current(root_dir, isomeric):
        return None
    root_dir = Path(root_dir).resolve()
    path = pair_descriptors_csv_path(root_dir)
    try:
        table = pd.read_csv(path, float_precision="round_trip")
    except (OSError, ValueError, pd.errors.ParserError):
        return None
    table = table[table["isomeric"] == bool(isomeric)]
    value_columns = [c for c in table.columns if c not in ("smiles", "protein", "isomeric")]
    return {
        (row["smiles"], row["protein"]): {name: row[name] for name in value_columns}
        for _, row in table.iterrows()
    }
