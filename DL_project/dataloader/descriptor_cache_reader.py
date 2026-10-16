"""Read descriptor values from plain CSV tables.

Layouts:
- data/protein_descriptors.csv: one row per protein, used by
  chemistry_prior.protein_descriptor_table and Dataloader.py, not this reader.
- data/lipid_descriptors.csv: one row per (canonical SMILES, isomeric variant),
  holding every _LIPID_MEASURES value.
- data/pair_descriptors.csv: one row per (candidate SMILES, protein, isomeric
  variant) present in the interaction table, holding PAIR_DESCRIPTOR_NAMES.

Builders live in cache_builders/descriptor_csv_builder.py and are called by
data/build_descriptor_cache.py. This module holds readers, format checks,
and fingerprint metadata shared with builders.

scripts/run_local.sh builds the tables and embedding store before its grid.
Without shared values, each (group, seed) process repeats RDKit calculations
for unchanged candidates: chains, unsaturation, H-bonds, heavy atoms, tails,
and conformer shapes. These values do not depend on seed or excluded_groups.
After building, jobs use dict lookups instead of repeating that work.

Every measure is included by default, without a lipid_shape flag.
radius_of_gyration/asphericity/molecular_volume (LIPID_SHAPE_DESCRIPTOR_NAMES)
use 10-conformer ETKDG+MMFF embeddings. _parallel_measures uses a process pool;
~1300 candidates on 24 cores still take minutes for the first build.
The recorded build cost is per (isomeric, code version, table version), not job.

The manifest data/lipid_descriptors.manifest.json stores raw_to_canonical:
{"deterministic": {...}, "isomeric": {...}}. Each maps raw candidate text to
canonical SMILES or None for failed parsing. Separate maps handle variants
and let chain_lengths_by_row/descriptor_values_by_row skip MolFromSmiles and
MolToSmiles lookups. Descriptor numbers themselves stay in the CSV, read by pandas.
New raw strings fall back to direct computation, as missing embedding stores
fall back to source pickles: the cache is an accelerator, not another truth source.

Source checks use interaction-table size and nanosecond mtime on each load,
as in tensors_reading/protein_graph_tensors_reader.py, without content hashing.
Formula edits do not invalidate stored numbers here. To update an affected
column deliberately, run python3 preprocessing/compute_descriptors.py NAME.
"""

import json
from pathlib import Path

import pandas as pd


# Reject old version-2 manifests: separate variant JSON blobs became one
# CSV and a sidecar. Protein values moved to data/protein_descriptors.csv,
# owned by chemistry_prior.protein_descriptor_table.
CACHE_FORMAT_VERSION = 4



def lipid_descriptors_csv_path(root_dir):
    """Return data/lipid_descriptors.csv, keyed by canonical SMILES and isomeric variant.

    Each row holds all _LIPID_MEASURES values.
    """
    return Path(root_dir).resolve() / "lipid_descriptors.csv"


def lipid_descriptors_manifest_path(root_dir):
    """Return the lipid CSV sidecar path.

    It stores format version, measure fingerprints, source size/mtime, and
    raw_to_canonical metadata; descriptor values remain in the CSV.
    """
    return Path(root_dir).resolve() / "lipid_descriptors.manifest.json"


def cache_path(root_dir, isomeric=None):
    """Alias lipid_descriptors_csv_path for existing tests and builders.

    Ignore isomeric: the two former JSON caches now share one CSV, distinguished
    by its isomeric column.
    """
    return lipid_descriptors_csv_path(root_dir)


def load_lipid_descriptor_cache(root_dir, isomeric):
    """Return {"raw_to_canonical", "values"} for this variant, or None.

    This read contract differs from store_is_current's build decision: a measure
    change should affect its own column, not discard the whole table.
    raw_to_canonical is per variant in the manifest, independent of protein files
    and CSV rows. New candidates absent from it fall back to direct computation.
    values selects this variant's CSV rows and available valid measure names;
    callers test measure presence in each entry.

    Return None only when no readable current-format table exists.
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
        # round_trip preserves computed floats exactly; pandas' default C parser
        # can introduce a one-ULP difference absent from the written values.
        table = pd.read_csv(csv_path, float_precision="round_trip")
    except (OSError, ValueError, pd.errors.ParserError, KeyError):
        return None
    if "isomeric" not in table.columns or "smiles" not in table.columns:
        return None
    table = table[table["isomeric"] == bool(isomeric)]

    # Serve present numeric columns without comparing formula source text.
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
    """Return whether the table exists and its source and stored values are current.

    This is the builder decision, distinct from the reader's available-value check.
    Track measure_fingerprints and interaction-table size/mtime, not a whole-module
    hash that would invalidate values for unrelated renames or docstring edits.
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


# Pair-level PAIR_DESCRIPTOR_NAMES table: every pair formula (occupancy,
# aromatic_contact, volume_fit, ...) applied to the lipid and protein tables above.
# Dataloader.py's pair_values_by_row prefers this over computing a formula inline;
# a (candidate, protein) absent from it -- a new candidate, or no current table at
# all -- falls back to the two source tables directly, the same discipline every
# other table here uses. Key by (smiles, protein, isomeric): values depend on both
# partners. Writer: cache_builders/descriptor_csv_builder.build_pair_value_cache.


def pair_descriptors_csv_path(root_dir):
    """data/pair_descriptors.csv -- one row per (smiles, protein, isomeric) actually
    present in the interaction table, every PAIR_DESCRIPTOR_NAMES value."""
    return Path(root_dir).resolve() / "pair_descriptors.csv"


def pair_descriptors_manifest_path(root_dir):
    return Path(root_dir).resolve() / "pair_descriptors.manifest.json"


def pair_value_cache_is_current(root_dir, isomeric):
    """Return whether pair values and their lipid/protein source tables are current.

    Delegate source validation to those tables instead of duplicating their lists.
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
