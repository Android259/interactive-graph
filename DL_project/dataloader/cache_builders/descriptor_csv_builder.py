"""Build data/lipid_descriptors.csv (candidate-level lipid descriptor values) and
data/pair_descriptors.csv (candidate x protein PAIR_DESCRIPTOR_NAMES values).

See dataloader/descriptor_cache_reader.py for the read path, the table/manifest layout,
and the per-measure fingerprinting/staleness machinery this builder's output is
validated against.
"""

import json
import os
from pathlib import Path

import pandas as pd
from rdkit import Chem

from dataloader.cache_builders.protein_graph_tensors_builder import _source_record
from dataloader.descriptor_cache_reader import (
    CACHE_FORMAT_VERSION,
    lipid_descriptors_csv_path,
    lipid_descriptors_manifest_path,
    load_lipid_descriptor_cache,
    pair_descriptors_csv_path,
    pair_descriptors_manifest_path,
)
from preprocessing.compute_descriptors import _LIPID_MEASURES, PAIR_DESCRIPTOR_LIPID_INPUTS
from dataloader.pocket_lipid_compatibility import candidates_for_row


def _init_worker():
    """Limit BLAS/OpenMP to one thread per pool worker.

    Without limits, numpy/RDKit linear algebra and conformer optimization
    oversubscribe cores on top of the process pool (25 OS threads observed per
    worker). One candidate per worker thread avoids synchronization overhead.
    See scripts/tools/lipid_graphs_on_kraken.sh, OMP_NUM_THREADS=1.
    """
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"


def _compute_one(key, seed_entry=None, skip_measures=()):
    """Compute _LIPID_MEASURES for one canonical SMILES; picklable worker function.

    Reuse non-None seed_entry values from any previous build, regardless of its
    fingerprint. Adding a measure need not recompute existing conformer values.
    radius_of_gyration/asphericity/molecular_volume/npr1/npr2 share
    _cached_conformer_ensemble(key); a missing conformer measure still requires
    one 10-conformer ETKDG+MMFF embedding per key. seed_entry=None computes all.

    skip_measures preserves seeded values or leaves None for this call.
    This opt-in exception skips expensive work without changing the default.
    Skipped names get no manifest fingerprint, so a later ordinary build fills
    them instead of treating them as validated.
    """
    seed_entry = seed_entry or {}
    entry = {}
    for measure, fn in _LIPID_MEASURES.items():
        if measure in skip_measures:
            entry[measure] = seed_entry.get(measure)
            continue
        seeded = seed_entry.get(measure)
        entry[measure] = seeded if seeded is not None else fn(key)
    return key, entry


def _compute_one_star(args):
    """Unpack (key, seed_entry, skip_measures) for the single-argument Pool.map call."""
    return _compute_one(*args)


def _parallel_measures(keys, seed_values=None, skip_measures=(), progress=False):
    """Return {key: lipid-measure entry} through a process pool.

    seed_values maps keys to old entries (_compute_one); missing keys compute
    all measures. Forward skip_measures unchanged.
    progress defaults to False, retaining pool.map behavior. When enabled, use
    imap_unordered and print done N/total every 25 completions and at the end.
    Always use the pool: this is a one-off build, avoiding a separate small-task
    threshold and keeping one tested computation path despite fork overhead.
    """
    if not keys:
        return {}
    import multiprocessing

    seed_values = seed_values or {}
    tasks = [(key, seed_values.get(key), skip_measures) for key in keys]
    workers = min(len(keys), max(1, multiprocessing.cpu_count() - 1))
    with multiprocessing.Pool(workers, initializer=_init_worker) as pool:
        if not progress:
            return dict(pool.map(_compute_one_star, tasks))
        results = {}
        total = len(tasks)
        for position, (key, entry) in enumerate(
            pool.imap_unordered(_compute_one_star, tasks), start=1
        ):
            results[key] = entry
            if position % 25 == 0 or position == total:
                print(f"pair descriptor cache: done {position}/{total}", flush=True)
        return results


def _previous_cache_values(root_dir, isomeric):
    """Read {key: entry} for this variant from the existing lipid CSV.

    Ignore code fingerprints: old values seed partial rebuilds after code changes.
    Return {} if no table exists; an empty seed is equivalent to no seed.
    """
    path = lipid_descriptors_csv_path(root_dir)
    if not path.exists():
        return {}
    try:
        # Use round_trip to preserve seeded floats exactly; the default parser can
        # shift them by one ULP. See descriptor_cache_reader.load_lipid_descriptor_cache.
        table = pd.read_csv(path, float_precision="round_trip")
    except (OSError, ValueError, pd.errors.ParserError):
        return {}
    if "isomeric" not in table.columns or "smiles" not in table.columns:
        return {}
    table = table[table["isomeric"] == bool(isomeric)]
    seed = {}
    for _, row in table.iterrows():
        seed[row["smiles"]] = {
            name: row[name]
            for name in table.columns
            if name not in ("smiles", "isomeric") and pd.notna(row[name])
        }
    return seed


def build_lipid_descriptor_cache(
    root_dir, csv, protein_names, csv_path, isomeric=False, skip_measures=(),
    progress=False,
):
    """Build one variant and merge it into data/lipid_descriptors.csv.

    Keep other-variant rows. Return (table_path, smiles_count, protein_count).
    protein_names and protein_count remain for caller compatibility; protein
    values live separately in chemistry_prior.protein_descriptor_table's
     data/protein_descriptors.csv.

    Build unconditionally; data/build_descriptor_cache.py decides when needed,
    as for build_lipid_embedding_store. Include all _LIPID_MEASURES by default,
    including shape values unused by this run, so later runs find complete rows.
    Reuse existing entries through _previous_cache_values/_compute_one:
    adding a measure computes only missing values, not every RDKit embedding.

    skip_measures is opt-in. Skipped names receive no manifest fingerprint;
    a later default build fills them instead of treating them as validated.
    """
    root_dir = Path(root_dir).resolve()
    seed_values = _previous_cache_values(root_dir, isomeric)

    raw_to_canonical = {}
    pending_keys = []
    for _, row in csv.iterrows():
        for raw in candidates_for_row(row):
            if raw in raw_to_canonical:
                continue
            molecule = Chem.MolFromSmiles(raw)
            if molecule is None or molecule.GetNumAtoms() == 0:
                raw_to_canonical[raw] = None
                continue
            key = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=isomeric)
            raw_to_canonical[raw] = key
            if key not in pending_keys:
                pending_keys.append(key)

    values = _parallel_measures(
        pending_keys, seed_values=seed_values, skip_measures=skip_measures,
        progress=progress,
    )

    rows = [
        {"smiles": key, "isomeric": bool(isomeric), **entry}
        for key, entry in values.items()
    ]
    new_table = pd.DataFrame(rows, columns=["smiles", "isomeric", *_LIPID_MEASURES])

    table_path = lipid_descriptors_csv_path(root_dir)
    existing = pd.DataFrame()
    if table_path.exists():
        try:
            existing = pd.read_csv(table_path, float_precision="round_trip")
            existing = existing[existing["isomeric"] != bool(isomeric)]
        except (OSError, ValueError, pd.errors.ParserError, KeyError):
            existing = pd.DataFrame()
    combined = pd.concat([existing, new_table], ignore_index=True) if len(existing) else new_table
    table_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(table_path, index=False)

    manifest_path = lipid_descriptors_manifest_path(root_dir)
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, ValueError, json.JSONDecodeError):
            manifest = {}
    manifest_raw_to_canonical = dict(manifest.get("raw_to_canonical") or {})
    manifest_raw_to_canonical["isomeric" if isomeric else "deterministic"] = raw_to_canonical
    manifest = {
        "format_version": CACHE_FORMAT_VERSION,
        "sources": [_source_record(Path(csv_path), root_dir)],
        "raw_to_canonical": manifest_raw_to_canonical,
    }
    manifest_path.write_text(json.dumps(manifest))

    return table_path, len(values), len(protein_names)


def build_pair_value_cache(root_dir, csv, isomeric=False):
    """Write this variant's joint values to data/pair_descriptors.csv.

    Compute all PAIR_DESCRIPTOR_NAMES for (candidate, protein) pairs present
    in the interaction table. Read cached lipid/protein values; do not rerun
    RDKit. Return (table_path, pair_count).
    Require current data/lipid_descriptors.csv, otherwise raise RuntimeError.
    """
    from preprocessing.compute_descriptors import protein_descriptor_table
    from dataloader.descriptors import PAIR_DESCRIPTOR_NAMES
    from preprocessing.compute_descriptors import pair_descriptor_value

    root_dir = Path(root_dir).resolve()
    lipid_cache = load_lipid_descriptor_cache(root_dir, isomeric)
    if lipid_cache is None:
        raise RuntimeError(
            "build_pair_value_cache needs a current data/lipid_descriptors.csv first "
            "(build_lipid_descriptor_cache, or call this right after it)"
        )
    raw_to_canonical = lipid_cache["raw_to_canonical"]
    lipid_values = lipid_cache["values"]
    protein_table = protein_descriptor_table(str(root_dir))

    pairs_needed = set()
    for _, row in csv.iterrows():
        protein = row.get("LTPProtein")
        if not isinstance(protein, str) or protein not in protein_table:
            continue
        for raw in candidates_for_row(row):
            key = raw_to_canonical.get(raw)
            if key is not None and key in lipid_values:
                pairs_needed.add((key, protein))

    rows = []
    for smiles, protein in pairs_needed:
        lv = lipid_values[smiles]
        lipid_input = {key: lv[key] for key in PAIR_DESCRIPTOR_LIPID_INPUTS}
        pv = protein_table[protein]
        row = {"smiles": smiles, "protein": protein, "isomeric": bool(isomeric)}
        row.update({
            name: pair_descriptor_value(name, lipid_input, pv)
            for name in PAIR_DESCRIPTOR_NAMES
        })
        rows.append(row)

    new_table = pd.DataFrame(
        rows, columns=["smiles", "protein", "isomeric", *PAIR_DESCRIPTOR_NAMES]
    )

    table_path = pair_descriptors_csv_path(root_dir)
    existing = pd.DataFrame()
    if table_path.exists():
        try:
            existing = pd.read_csv(table_path, float_precision="round_trip")
            existing = existing[existing["isomeric"] != bool(isomeric)]
        except (OSError, ValueError, pd.errors.ParserError, KeyError):
            existing = pd.DataFrame()
    combined = pd.concat([existing, new_table], ignore_index=True) if len(existing) else new_table
    table_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(table_path, index=False)

    manifest_path = pair_descriptors_manifest_path(root_dir)
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, ValueError, json.JSONDecodeError):
            manifest = {}
    manifest["format_version"] = CACHE_FORMAT_VERSION
    manifest[f"built_{'isomeric' if isomeric else 'deterministic'}"] = True
    manifest_path.write_text(json.dumps(manifest))

    return table_path, len(rows)
