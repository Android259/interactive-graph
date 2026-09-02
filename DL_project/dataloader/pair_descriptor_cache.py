"""Precomputed, disk-shared cache for --pair_descriptors' per-candidate/per-protein values.

Dataloader.py._compute_pair_descriptors runs RDKit over every candidate SMILES in
the interaction table (chain length, unsaturation, H-bond capacity, heavy-atom count,
tail count, and the three conformer-based lipid-shape measures) and parses every
protein's pocketness.pdb/coarse_graph_nodes.csv (pocket extent, aromatic_share_core/
rim) -- none of which depends on --seed or --excluded_groups. A local grid launches one
process per (group, seed) pair (scripts/run_local.sh), so an untouched, unregenerated
interaction table and an untouched data/graphs/ still get this work redone from scratch
in every one of those processes if nothing shares it.

Built once by data/build_pair_descriptor_cache.py (scripts/run_local.sh calls it
alongside data/build_lipid_embedding_store.py, before the grid launches) and read by
every job afterwards: every process just does a dict lookup against what is already
here, never RDKit/pocket-parsing at load time.

Every measure this module knows how to compute is ALWAYS included -- no flag gates any
of them out of a build. Three of them (radius_of_gyration/asphericity/molecular_volume,
LIPID_SHAPE_DESCRIPTOR_NAMES) are genuinely expensive (a 10-conformer ETKDG+MMFF embed
per candidate, not microseconds like the rest), so the values dict is filled through a
process pool (_parallel_measures below) -- ~1300 unique candidates on a 24-core box
still takes real minutes the first time any build runs, but it is paid exactly once per
(isomeric, code version, table version), never per run and never per job.

Two things are cached, because two different reads need canonicalisation skipped
entirely to pay off:

    raw_to_canonical : the exact candidate string as it appears in the interaction
                        table -> its canonical SMILES, or None where RDKit cannot parse
                        it. Without this, chain_lengths_by_row/descriptor_values_by_row
                        would still have to call Chem.MolFromSmiles/MolToSmiles on every
                        raw candidate just to know which cache entry to look up.
    values            : canonical SMILES -> {chain, unsaturation, hbond, heavy_atoms,
                        tail_count, radius_of_gyration, asphericity, molecular_volume,
                        rotatable_fraction} -- every _MEASURES entry, always.

A raw string absent from raw_to_canonical (a candidate added to the table after the
cache was built) falls back to computing it directly, same as a store_is_current() miss
falls back to the source pickle in lipid_embedding_store.py -- the cache is an
accelerator, never a second source of truth a stale run could disagree with the current
data from.

The manifest guards staleness the same way protein_graph_tensor_cache.py does: every
source file's size and nanosecond mtime must still match what the cache was built from,
checked freshly on every load (cheap -- a few dozen stat() calls, not a hash of file
contents).
"""

import hashlib
import json
import os
from pathlib import Path

from rdkit import Chem

import dataloader.pair_descriptors as pair_descriptors
import dataloader.pocket_lipid_compatibility as pocket_lipid_compatibility
from dataloader.pair_descriptors import _MEASURES, longest_acyl_chain
from dataloader.pocket_lipid_compatibility import (
    candidates_for_row,
    pocket_extent_by_protein,
    pocket_rim_core_aromatic_share_by_protein,
)
from dataloader.protein_graph_tensor_cache import _source_record

CACHE_FORMAT_VERSION = 1

# Modules whose source defines what a cache entry MEANS: longest_acyl_chain,
# _MEASURES' formulas (unsaturation/hbond/heavy_atoms/tail_count/the three
# conformer-based ones), pocket_extent_by_protein, pocket_rim_core_aromatic_share_
# by_protein. None of these are files store_is_current()'s size/mtime check watches --
# that check guards the DATA a cache was built from (the interaction table, protein
# structures), not the CODE that turns it into cached numbers, so a formula change
# here would otherwise leave a still-"current" cache silently serving values computed
# under the old formula. Folded into the cache filename below instead: a code change
# is then a different filename outright, never a stale hit.
_CODE_MODULES = (pair_descriptors, pocket_lipid_compatibility)


def _code_fingerprint():
    """Short hash of every module in _CODE_MODULES' source, in a fixed order."""
    hasher = hashlib.sha256()
    for module in _CODE_MODULES:
        hasher.update(Path(module.__file__).read_bytes())
    return hasher.hexdigest()[:16]


def cache_path(root_dir, isomeric):
    root_dir = Path(root_dir).resolve()
    stem = "isomeric" if isomeric else "deterministic"
    return root_dir / f"pair_descriptor_cache_{stem}_{_code_fingerprint()}.json"


def _protein_source_paths(root_dir, protein_names):
    root_dir = Path(root_dir)
    paths = []
    for protein in protein_names:
        protein_dir = root_dir / "graphs" / protein
        paths.append(protein_dir / "pocketness.pdb")
        paths.append(protein_dir / "coarse_graph_nodes.csv")
    return paths


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


def _compute_one(key):
    """{"chain": ..., **_MEASURES} for one canonical SMILES -- the pool's unit of work.

    Module-level (not a closure) so it can be pickled to worker processes.
    """
    entry = {"chain": longest_acyl_chain(key)}
    entry.update((measure, fn(key)) for measure, fn in _MEASURES.items())
    return key, entry


def _parallel_measures(keys):
    """{key: {"chain": ..., **_MEASURES}} for every key in `keys`, via a process pool.

    Serial below a small pool would not be worth starting (fork overhead exceeds the
    saving), but there is no such thing as "too few" here in practice -- a build is a
    one-off, not a per-job cost, so always parallelising is simpler than guessing a
    threshold and both keep the exact same code path tested.
    """
    if not keys:
        return {}
    import multiprocessing

    workers = min(len(keys), max(1, multiprocessing.cpu_count() - 1))
    with multiprocessing.Pool(workers, initializer=_init_worker) as pool:
        return dict(pool.map(_compute_one, keys))


def build_pair_descriptor_cache(root_dir, csv, protein_names, csv_path, isomeric=False):
    """Compute and write the cache. Returns (cache_path, smiles_count, protein_count).

    Rebuilds unconditionally -- the caller (data/build_pair_descriptor_cache.py)
    decides whether that is needed, same division of responsibility as
    lipid_embedding_store.build_lipid_embedding_store. Every _MEASURES entry is
    always computed (see module docstring) -- there is no lipid_shape flag here
    anymore; a run that never reads radius_of_gyration/asphericity/molecular_volume
    still gets a cache that carries them, because the NEXT run that does must never
    hit a cache silently missing what it asked for.
    """
    root_dir = Path(root_dir).resolve()

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

    values = _parallel_measures(pending_keys)

    extents = pocket_extent_by_protein(root_dir, protein_names)
    rim_core = pocket_rim_core_aromatic_share_by_protein(root_dir, protein_names)
    proteins = {}
    for protein in protein_names:
        core, rim = rim_core[protein]
        proteins[protein] = {
            "extent": extents[protein],
            "aromatic_share_core": core,
            "aromatic_share_rim": rim,
        }

    source_paths = [Path(csv_path)] + [
        path for path in _protein_source_paths(root_dir, protein_names) if path.exists()
    ]
    payload = {
        "format_version": CACHE_FORMAT_VERSION,
        # Belt and suspenders alongside the filename (cache_path already embeds
        # this): a copy or manual rename could carry the fingerprint-tagged
        # name to code it no longer matches, and this catches that too.
        "code_fingerprint": _code_fingerprint(),
        "isomeric": bool(isomeric),
        "sources": [_source_record(path, root_dir) for path in source_paths],
        "raw_to_canonical": raw_to_canonical,
        "values": values,
        "proteins": proteins,
    }
    path = cache_path(root_dir, isomeric)
    path.write_text(json.dumps(payload))
    return path, len(values), len(proteins)


def store_is_current(root_dir, isomeric):
    """True when a cache exists and every recorded source still matches on disk."""
    root_dir = Path(root_dir).resolve()
    path = cache_path(root_dir, isomeric)
    if not path.exists():
        return False
    try:
        manifest = json.loads(path.read_text())
        if manifest.get("format_version") != CACHE_FORMAT_VERSION:
            return False
        if manifest.get("code_fingerprint") != _code_fingerprint():
            return False
        if bool(manifest.get("isomeric")) != bool(isomeric):
            return False
        for source in manifest["sources"]:
            stat = (root_dir / source["path"]).stat()
            if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
                return False
        return True
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return False


def load_pair_descriptor_cache(root_dir, isomeric):
    """{"raw_to_canonical", "values", "proteins"} if current, else None (fall back).

    None is a normal answer, not an error -- a checkout that never ran the builder, a
    regenerated interaction table, an added protein or a stale run all end up here, and
    the caller (Dataloader._compute_pair_descriptors) computes exactly as it did
    before this module existed.
    """
    if not store_is_current(root_dir, isomeric):
        return None
    path = cache_path(Path(root_dir).resolve(), isomeric)
    try:
        manifest = json.loads(path.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return {
        "raw_to_canonical": manifest["raw_to_canonical"],
        "values": manifest["values"],
        "proteins": manifest["proteins"],
    }


# --- pair-level (PAIR_DESCRIPTOR_NAMES) cache -------------------------------------
#
# occupancy/chain_extent_gap/aromatic_contact/hbond_match/volume_fit/buriedness_match/
# depth_bulk_match/hydropathy_chain_match/aromatic_contact_min/hbond_match_min/
# tail_elongation_fit (dataloader.pair_descriptors.pair_descriptor_value) are pure
# arithmetic over ALREADY-cached lipid values (above) and protein values
# (dataloader/chemistry_prior.py's protein_descriptor_table) -- no RDKit, no pocket
# geometry, microseconds per (candidate, protein) pair. This is a separate cache
# rather than more keys on the lipid entries above because a pair value needs BOTH a
# candidate AND a protein (a lipid's own values do not depend on which protein it is
# paired with), so the natural key is (canonical smiles, protein), not smiles alone.
#
# Not built for speed -- Dataloader.py's own inline pair_descriptor_value() calls
# over already-loaded numpy arrays cost the same microseconds this cache would save.
# Built so vector assembly is a lookup at every layer, matching the lipid/protein
# base-value caches: nothing in the descriptor pipeline computes a value that was
# already computed once for the same (candidate, protein, code version, table
# version) combination.


def _pair_value_cache_path(root_dir, isomeric):
    root_dir = Path(root_dir).resolve()
    stem = "isomeric" if isomeric else "deterministic"
    return root_dir / f"pair_value_cache_{stem}_{_code_fingerprint()}.json"


def build_pair_value_cache(root_dir, csv, isomeric=False):
    """Compute and write every PAIR_DESCRIPTOR_NAMES value for every (candidate,
    protein) combination the interaction table actually contains. Returns
    (cache_path, pair_count).

    Requires a current pair_descriptor_cache (raises RuntimeError otherwise) -- this
    reads lipid values from it rather than recomputing them, so building this cache
    is only ever the cheap arithmetic step, never RDKit.
    """
    from dataloader.chemistry_prior import protein_descriptor_table
    from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES, pair_descriptor_value

    root_dir = Path(root_dir).resolve()
    lipid_cache = load_pair_descriptor_cache(root_dir, isomeric)
    if lipid_cache is None:
        raise RuntimeError(
            "build_pair_value_cache needs a current pair_descriptor_cache first "
            "(build that one, or call this right after build_pair_descriptor_cache)"
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

    values = {}
    for smiles, protein in pairs_needed:
        lv = lipid_values[smiles]
        # pair_descriptor_value's own key names (Dataloader.py's identical dict at
        # its inline call site): "heavy", not this cache's "heavy_atoms".
        lipid_input = {
            "chain": lv["chain"],
            "unsaturation": lv["unsaturation"],
            "hbond": lv["hbond"],
            "heavy": lv["heavy_atoms"],
            "tail_count": lv["tail_count"],
        }
        pv = protein_table[protein]
        values[f"{smiles}\x1f{protein}"] = {
            name: pair_descriptor_value(name, lipid_input, pv)
            for name in PAIR_DESCRIPTOR_NAMES
        }

    payload = {
        "format_version": CACHE_FORMAT_VERSION,
        "code_fingerprint": _code_fingerprint(),
        "isomeric": bool(isomeric),
        # No "sources" list of its own: staleness is checked by deferring to the
        # lipid cache's store_is_current() and the protein table's own presence
        # (pair_value_cache_is_current below) -- this cache's values are only ever
        # as fresh as those two, so tracking a second, redundant copy of the same
        # source records here could only drift from them, never add information.
        "values": values,
    }
    path = _pair_value_cache_path(root_dir, isomeric)
    path.write_text(json.dumps(payload))
    return path, len(values)


def pair_value_cache_is_current(root_dir, isomeric):
    """True when a pair-value cache exists, matches the current code, and the
    lipid/protein caches it was built from are STILL current (rather than
    duplicating their own source lists here, defer to them directly -- this cache's
    values are only ever as fresh as those two).
    """
    from dataloader.chemistry_prior import _protein_descriptor_table_path

    root_dir = Path(root_dir).resolve()
    path = _pair_value_cache_path(root_dir, isomeric)
    if not path.exists():
        return False
    if not store_is_current(root_dir, isomeric):
        return False
    if not _protein_descriptor_table_path(root_dir).exists():
        return False
    try:
        manifest = json.loads(path.read_text())
        return (
            manifest.get("format_version") == CACHE_FORMAT_VERSION
            and manifest.get("code_fingerprint") == _code_fingerprint()
            and bool(manifest.get("isomeric")) == bool(isomeric)
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return False


def load_pair_value_cache(root_dir, isomeric):
    """{(smiles, protein) key -> {PAIR_DESCRIPTOR_NAMES: value}} if current, else None."""
    if not pair_value_cache_is_current(root_dir, isomeric):
        return None
    path = _pair_value_cache_path(Path(root_dir).resolve(), isomeric)
    try:
        manifest = json.loads(path.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return manifest["values"]
