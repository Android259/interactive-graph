"""Build data/lipid_descriptors.csv (candidate-level lipid descriptor values) and
data/pair_descriptors.csv (candidate x protein PAIR_DESCRIPTOR_NAMES values).

See dataloader/pair_descriptor_cache.py for the read path, the table/manifest layout,
and the per-measure fingerprinting/staleness machinery this builder's output is
validated against.
"""

import json
import os
from pathlib import Path

import pandas as pd
from rdkit import Chem

from dataloader.cache_builders.protein_graph_tensor_cache import _source_record
from dataloader.pair_descriptor_cache import (
    CACHE_FORMAT_VERSION,
    lipid_descriptors_csv_path,
    lipid_descriptors_manifest_path,
    load_pair_descriptor_cache,
    pair_descriptors_csv_path,
    pair_descriptors_manifest_path,
)
from preprocessing.compute_descriptors import _MEASURES, longest_acyl_chain
from dataloader.pocket_lipid_compatibility import candidates_for_row


def _init_worker():
    """Pool initializer: one BLAS/OpenMP thread per worker process.

    Without this, numpy/RDKit's threaded BLAS calls (pocket_shape's eigh/cov, and
    whatever the conformer-optimisation step below pulls in) each try to grab every
    core on the host THEMSELVES, on top of the process pool already using all of
    them -- measured as 25 OS threads for what should be one, thrashing on
    creation/synchronisation instead of finishing sooner (same issue scripts/tools/
    lipid_graphs_on_kraken.sh's own OMP_NUM_THREADS=1 comment documents). Every
    worker doing its own one candidate on its own one thread is what makes the pool
    add up to real parallelism instead of oversubscribing the box N times over.
    """
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"


def _compute_one(key, seed_entry=None, skip_measures=()):
    """{"chain": ..., **_MEASURES} for one canonical SMILES -- the pool's unit of work.

    `seed_entry`, when given, is that same key's entry from a PREVIOUS build (any
    older code fingerprint) -- a measure already present there (and not None) is
    reused as-is instead of calling its fn again. This is what makes adding one new
    _MEASURES entry (a new descriptor, unrelated formulas for the rest) NOT force a
    fresh 10-conformer ETKDG+MMFF embed for the four measures that already had it:
    radius_of_gyration/asphericity/molecular_volume/npr1/npr2 all read the SAME
    _cached_conformer_ensemble(key), so a genuinely new conformer-based measure
    (missing from every seed) still costs one embed per key, same as always -- this
    only removes cost that ISN'T actually needed, never changes what a from-scratch
    build (seed_entry=None, e.g. this project's very first build) computes.

    `skip_measures`: names to leave uncomputed THIS call -- the seeded value (if any)
    is kept, otherwise the entry is None, same as RDKit failing to resolve it. An
    explicit, opt-in escape from "every measure, always" (see build_pair_descriptor_
    cache's own docstring for why that is the default and stays the default), for a
    one-off build that must skip the expensive conformer-based measures this call --
    the manifest records no fingerprint for a skipped name, so a later ordinary build
    (no skip_measures) sees it as missing and fills it in, never serving it as if it
    had been validated.

    Module-level (not a closure) so it can be pickled to worker processes.
    """
    seed_entry = seed_entry or {}
    entry = {"chain": longest_acyl_chain(key)}
    for measure, fn in _MEASURES.items():
        if measure in skip_measures:
            entry[measure] = seed_entry.get(measure)
            continue
        seeded = seed_entry.get(measure)
        entry[measure] = seeded if seeded is not None else fn(key)
    return key, entry


def _compute_one_star(args):
    """Pool.starmap-free (key, seed_entry, skip_measures) unpacking -- Pool.map takes
    one arg per call, and a seed dict cannot be a second positional without this."""
    return _compute_one(*args)


def _parallel_measures(keys, seed_values=None, skip_measures=(), progress=False):
    """{key: {"chain": ..., **_MEASURES}} for every key in `keys`, via a process pool.

    `seed_values`: {key: previous-build entry}, see _compute_one -- keys absent from
    it (a genuinely new candidate, or no previous table at all) compute every measure
    fresh, exactly as before this parameter existed.

    `skip_measures`: see _compute_one -- forwarded as-is to every task.

    `progress`: opt-in, default off (preserves the exact original pool.map behaviour
    for every existing caller) -- prints "done N/total" to stdout every 25 completions
    plus the final one. Uses imap_unordered instead of map so a result is available
    to print as soon as ANY worker finishes it, not only once the whole batch returns.

    Serial below a small pool would not be worth starting (fork overhead exceeds the
    saving), but there is no such thing as "too few" here in practice -- a build is a
    one-off, not a per-job cost, so always parallelising is simpler than guessing a
    threshold and both keep the exact same code path tested.
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
    """{key: entry} read straight off the existing data/lipid_descriptors.csv for this
    isomeric variant, regardless of whether its measures still validate against the
    current code -- deliberately NOT gated on that (a code change is exactly the case
    this exists to make cheap: a fingerprint match would mean nothing to seed from in
    the first place). {} when the table does not exist yet (this project's very first
    build for this variant) -- an empty seed is the same as not seeding at all, never
    an error.
    """
    path = lipid_descriptors_csv_path(root_dir)
    if not path.exists():
        return {}
    try:
        # float_precision="round_trip": see dataloader/pair_descriptor_cache.py's
        # load_pair_descriptor_cache for why this flag is not optional here -- without
        # it, a seeded value already in the table can read back one ULP off from what
        # was actually written.
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


def build_pair_descriptor_cache(
    root_dir, csv, protein_names, csv_path, isomeric=False, skip_measures=(),
    progress=False,
):
    """Compute this isomeric variant's rows and merge them into data/
    lipid_descriptors.csv (the other variant's rows, if any, are left untouched).
    Returns (table_path, smiles_count, protein_count).

    `protein_names` is accepted and `protein_count` still returned only so every
    existing caller's (path, smiles_count, protein_count) unpacking keeps working --
    the protein side no longer lives in this table at all (dataloader.chemistry_prior.
    protein_descriptor_table owns it, in data/protein_descriptors.csv, built and read
    independently of this function).

    Rebuilds unconditionally -- the caller (data/build_pair_descriptor_cache.py)
    decides whether that is needed, same division of responsibility as
    cache_builders.lipid_embedding_store.build_lipid_embedding_store. Every
    _MEASURES entry is computed by DEFAULT (see dataloader/pair_descriptor_cache.py's
    module docstring) -- there is no lipid_shape flag here anymore; an ordinary run
    (skip_measures=()) that never reads radius_of_gyration/asphericity/molecular_volume
    still gets a table that carries them, because the NEXT run that does must never
    hit a table silently missing what it asked for. "Computed" does not mean
    "recomputed from RDKit every time a rebuild runs", though -- see
    _previous_cache_values/_compute_one: a measure already correct in the table before
    this call is carried over rather than re-embedded, so adding ONE new descriptor
    costs ONLY that descriptor's own compute, not every existing one's too.

    `skip_measures`: an explicit, opt-in exception to "every measure, always" -- names
    left uncomputed THIS call (see _compute_one). Their fingerprint is also left out of
    the written manifest, so a later ordinary build (skip_measures=()) sees them as
    missing -- never already-validated -- and fills them in rather than silently
    continuing to serve a table that never actually computed them.
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
    new_table = pd.DataFrame(rows, columns=["smiles", "isomeric", "chain", *_MEASURES])

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
    """Compute and write data/pair_descriptors.csv's rows for this isomeric variant:
    every PAIR_DESCRIPTOR_NAMES value for every (candidate, protein) combination the
    interaction table actually contains, read from data/lipid_descriptors.csv and
    data/protein_descriptors.csv rather than recomputed. Returns (table_path,
    pair_count).

    Requires a current data/lipid_descriptors.csv (raises RuntimeError otherwise) --
    this reads lipid values from it rather than recomputing them, so building this
    table is only ever the cheap arithmetic step, never RDKit.
    """
    from preprocessing.compute_descriptors import protein_descriptor_table
    from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES
    from preprocessing.compute_descriptors import pair_descriptor_value

    root_dir = Path(root_dir).resolve()
    lipid_cache = load_pair_descriptor_cache(root_dir, isomeric)
    if lipid_cache is None:
        raise RuntimeError(
            "build_pair_value_cache needs a current data/lipid_descriptors.csv first "
            "(build_pair_descriptor_cache, or call this right after it)"
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
        # pair_descriptor_value's own key names (Dataloader.py's identical dict at
        # its inline call site): "heavy", not this table's "heavy_atoms". Every key
        # pair_descriptor_value actually reads across all of PAIR_DESCRIPTOR_NAMES --
        # npr1/npr2 included, for elongation_shape_match/flatness_shape_match.
        lipid_input = {
            "chain": lv["chain"],
            "unsaturation": lv["unsaturation"],
            "hbond": lv["hbond"],
            "heavy": lv["heavy_atoms"],
            "tail_count": lv["tail_count"],
            "npr1": lv["npr1"],
            "npr2": lv["npr2"],
        }
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
