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
contents). The CODE side of staleness is checked at the granularity a value is actually
produced at -- per lipid measure, and once for the protein half -- so an edit to either
module invalidates what it changed and nothing else. Neither question is answered by a
hash over the modules as wholes any more; `_code_fingerprint` says why.
"""

import hashlib
import inspect
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
from dataloader.protein_graph_builder import (
    AROMATIC_RESIDUE_TYPES,
    pocket_atom_coordinates,
    pocket_shape,
)
from dataloader.protein_graph_tensor_cache import _pocket_tensor, _source_record

CACHE_FORMAT_VERSION = 2

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
    """Short hash of every module in _CODE_MODULES' source, in a fixed order.

    Provenance only, plus the pair-VALUE cache's filename (`_pair_value_cache_path`,
    whose contents are cheap arithmetic over this cache and never RDKit). It no longer
    decides anything about THIS cache, in either direction:

      what a reader may serve   `_measure_fingerprints`, per measure
      whether to rebuild        `store_is_current`, per measure + `_protein_fingerprint`

    It stopped deciding "rebuild?" because at that granularity it is wrong in the
    expensive direction: a docstring edit anywhere in either module -- and both are
    edited constantly for reasons that touch no formula -- made a cache whose every
    value was still correct report itself stale. A cluster launch acts on that report
    by queueing an OAR job that asks for a GPU and BLOCKS the launch until it drains,
    once per label, so the cost of a false alarm here is not a recompute, it is a grid
    that does not reach the queue.
    """
    hasher = hashlib.sha256()
    for module in _CODE_MODULES:
        hasher.update(Path(module.__file__).read_bytes())
    return hasher.hexdigest()[:16]


# Functions the conformer-based measures all route through: a change in any of them
# changes those measures' values without touching the measures' own source.
# CONFORMER_COUNT/CONFORMER_SEED are folded in for the same reason -- the ensemble is a
# pure function of (smiles, count, seed), so moving either moves every value built on it.
_SHARED_CONFORMER_FUNCTIONS = (
    "generate_conformer_ensemble",
    "_cached_conformer_ensemble",
    "_mean_over_conformers",
)

# Helpers a measure's value depends on without naming them in its own body's hash: a
# measure that delegates its real work is only as fixed as what it delegates to. Keyed
# by the helper, valued by the measures that route through it, because that is the way
# round which stays readable as measures are added.
#
# Missing one of these is a silent staleness bug of exactly the kind per-measure
# fingerprints exist to prevent -- the measure's own source would be unchanged, its
# fingerprint would match, and the cache would keep serving values the current code no
# longer produces. `_acyl_chain_component_lengths`/`_acyl_chain_components` are the
# case that made this concrete: `chain`, `tail_count` and every tail_* descriptor do
# nothing but read them.
_SHARED_HELPERS = {
    "_acyl_chain_component_lengths": ("chain", "tail_count"),
    "_acyl_chain_components": (
        "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
        "tail_unsaturation_density", "tail_double_bond_position",
        "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
    ),
    "_qualifying_tails": (
        "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
        "tail_unsaturation_density", "tail_double_bond_position",
        "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
    ),
    "_tail_fragment": ("tail_logp", "tail_molar_refractivity", "tail_heavy_atoms"),
}


def _measure_functions():
    """{measure name: the function that computes it}, chain included.

    `chain` comes from longest_acyl_chain rather than _MEASURES (which does not carry
    it), and _compute_one writes it into every entry, so it needs a fingerprint like
    the rest or it would be the one measure nothing could invalidate.
    """
    return {"chain": longest_acyl_chain, **_MEASURES}


def _measure_fingerprints():
    """{measure name: short hash of the code that produces THAT measure}.

    The fix for the failure this module used to have. Validity was one hash over the
    whole of pair_descriptors.py + pocket_lipid_compatibility.py, embedded in the cache
    FILENAME, so any edit anywhere in either file -- a new descriptor, a docstring, a
    renamed local -- made every previously cached value unreachable at once. Nothing
    was wrong with the values; the reader simply could not find a file under the new
    name, and every consumer silently recomputed from scratch until somebody happened
    to rerun the builder. Measured consequence: an edit to pair_descriptors.py on
    2026-09-06 orphaned five cache files holding 1226 lipids' conformer measures, and
    every reader after it paid a fresh 10-conformer ETKDG+MMFF embed per lipid.

    Per measure, the question is answerable honestly: `npr1`'s cached value is valid
    exactly while the code computing `npr1` is unchanged, whatever else moved in the
    module. So an unrelated edit now invalidates nothing, and a real change to one
    formula invalidates that formula only.

    inspect.getsource, not the whole module: that IS the granularity being bought.
    """
    conformer_shared = b""
    for name in _SHARED_CONFORMER_FUNCTIONS:
        conformer_shared += inspect.getsource(getattr(pair_descriptors, name)).encode()
    conformer_shared += (
        f"{pair_descriptors.CONFORMER_COUNT}:{pair_descriptors.CONFORMER_SEED}".encode()
    )

    # Inverted once, so the per-measure loop below stays a lookup: measure -> the
    # helpers whose source its value also depends on.
    helpers_by_measure = {}
    for helper, measures in _SHARED_HELPERS.items():
        for measure in measures:
            helpers_by_measure.setdefault(measure, []).append(helper)

    fingerprints = {}
    for name, function in _measure_functions().items():
        blob = inspect.getsource(function).encode()
        if name in pair_descriptors.CONFORMER_MEASURE_NAMES:
            blob += conformer_shared
        for helper in sorted(helpers_by_measure.get(name, ())):
            blob += inspect.getsource(getattr(pair_descriptors, helper)).encode()
        fingerprints[name] = hashlib.sha256(blob).hexdigest()[:16]
    return fingerprints


# The protein half of the cache. `values` above is covered measure by measure; these
# are the two functions that fill `proteins`, plus everything their values route through
# without naming it in their own body -- the same reason _SHARED_HELPERS exists for the
# lipid measures, and the same silent-staleness bug if one is left out (an edit to
# pocket_shape would move every cached extent while both entry points' own source, and
# therefore their hash, stayed put).
_PROTEIN_VALUE_FUNCTIONS = (
    pocket_extent_by_protein,
    pocket_rim_core_aromatic_share_by_protein,
    pocket_atom_coordinates,
    pocket_shape,
    _pocket_tensor,
)


def _protein_fingerprint():
    """Short hash of the code producing the cache's per-protein values.

    Not per protein-measure the way `_measure_fingerprints` is per lipid measure: the
    three protein values are computed together, from the same two parses, and the read
    path already drops them together when a protein's own files move
    (`load_pair_descriptor_cache`). One hash for the three is the granularity that
    matches how they are produced and invalidated.
    """
    blob = b""
    for function in _PROTEIN_VALUE_FUNCTIONS:
        blob += inspect.getsource(function).encode()
    # A constant, not a function: the aromatic mask is data the rim/core shares are
    # computed against, so moving it moves every share without changing a line of the
    # source hashed above.
    blob += repr(tuple(sorted(AROMATIC_RESIDUE_TYPES))).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def cache_path(root_dir, isomeric):
    """One stable path per (isomeric) variant.

    The code fingerprint used to be in this name, which is what made a code change
    orphan the file rather than invalidate the part of it that actually changed. Only
    the FORMAT version is in the name now; what is still valid inside is decided per
    measure, on read. The `_v2` suffix keeps `_previous_cache_values`' glob (which
    matches `..._*.json`) able to find v1 files to seed a rebuild from.
    """
    root_dir = Path(root_dir).resolve()
    stem = "isomeric" if isomeric else "deterministic"
    return root_dir / f"pair_descriptor_cache_{stem}_v{CACHE_FORMAT_VERSION}.json"


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


def _compute_one(key, seed_entry=None):
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

    Module-level (not a closure) so it can be pickled to worker processes.
    """
    seed_entry = seed_entry or {}
    entry = {"chain": longest_acyl_chain(key)}
    for measure, fn in _MEASURES.items():
        seeded = seed_entry.get(measure)
        entry[measure] = seeded if seeded is not None else fn(key)
    return key, entry


def _compute_one_star(args):
    """Pool.starmap-free (key, seed_entry) unpacking -- Pool.map takes one arg per
    call, and a seed dict cannot be a second positional without this."""
    return _compute_one(*args)


def _parallel_measures(keys, seed_values=None):
    """{key: {"chain": ..., **_MEASURES}} for every key in `keys`, via a process pool.

    `seed_values`: {key: previous-build entry}, see _compute_one -- keys absent from
    it (a genuinely new candidate, or no previous cache at all) compute every measure
    fresh, exactly as before this parameter existed.

    Serial below a small pool would not be worth starting (fork overhead exceeds the
    saving), but there is no such thing as "too few" here in practice -- a build is a
    one-off, not a per-job cost, so always parallelising is simpler than guessing a
    threshold and both keep the exact same code path tested.
    """
    if not keys:
        return {}
    import multiprocessing

    seed_values = seed_values or {}
    tasks = [(key, seed_values.get(key)) for key in keys]
    workers = min(len(keys), max(1, multiprocessing.cpu_count() - 1))
    with multiprocessing.Pool(workers, initializer=_init_worker) as pool:
        return dict(pool.map(_compute_one_star, tasks))


def _previous_cache_values(root_dir, isomeric):
    """{key: entry} from the MOST RECENTLY MODIFIED existing pair_descriptor_cache_
    <stem>_*.json for this isomeric variant, regardless of its code fingerprint --
    deliberately NOT gated by store_is_current/code_fingerprint (a code change is
    exactly the case this exists to make cheap: a fingerprint match would mean
    nothing to seed from in the first place). {} when none exists yet (this
    project's very first build for this variant) -- an empty seed is the same as
    not seeding at all, never an error.
    """
    stem = "isomeric" if isomeric else "deterministic"
    candidates = sorted(
        Path(root_dir).glob(f"pair_descriptor_cache_{stem}_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        try:
            manifest = json.loads(path.read_text())
            return manifest["values"]
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            continue
    return {}


def build_pair_descriptor_cache(root_dir, csv, protein_names, csv_path, isomeric=False):
    """Compute and write the cache. Returns (cache_path, smiles_count, protein_count).

    Rebuilds unconditionally -- the caller (data/build_pair_descriptor_cache.py)
    decides whether that is needed, same division of responsibility as
    lipid_embedding_store.build_lipid_embedding_store. Every _MEASURES entry is
    always computed (see module docstring) -- there is no lipid_shape flag here
    anymore; a run that never reads radius_of_gyration/asphericity/molecular_volume
    still gets a cache that carries them, because the NEXT run that does must never
    hit a cache silently missing what it asked for. "Computed" does not mean
    "recomputed from RDKit every time a rebuild runs", though -- see
    _previous_cache_values/_compute_one: a measure already correct in whatever
    cache existed before this call (any older code fingerprint) is carried over
    rather than re-embedded, so adding ONE new descriptor costs ONLY that
    descriptor's own compute, not every existing one's too.
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

    values = _parallel_measures(pending_keys, seed_values=seed_values)

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
        # Provenance: which whole-module state this file happened to be built under.
        # Nothing reads it back for a decision -- see `_code_fingerprint`.
        "code_fingerprint": _code_fingerprint(),
        # What decides validity, at the granularity each half is actually produced and
        # invalidated at: one entry per lipid measure (the READ path filters on these,
        # and so does `store_is_current`), one hash for the protein half.
        "measure_fingerprints": _measure_fingerprints(),
        "protein_fingerprint": _protein_fingerprint(),
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
    """True when a cache exists, its sources still match, and no VALUE it holds moved.

    "Should the builder run", and it must answer that on the same terms the reader
    answers "what may I serve": a rebuild has something to do exactly when some value
    in this file would come out different now. That is per lipid measure
    (`measure_fingerprints`) plus the protein half (`_protein_fingerprint`) plus the
    source files' size/mtime -- and deliberately NOT a hash over the two modules as
    wholes, which is what this used to compare and which reported "rebuild" for a
    renamed local or an edited docstring in code no cached value depends on.

    Manifests written before the protein fingerprint existed have no way to say which
    protein-side code they were built under, so they read as stale once: one rebuild,
    and every later launch answers honestly.
    """
    root_dir = Path(root_dir).resolve()
    path = cache_path(root_dir, isomeric)
    if not path.exists():
        return False
    try:
        manifest = json.loads(path.read_text())
        if manifest.get("format_version") != CACHE_FORMAT_VERSION:
            return False
        if manifest.get("measure_fingerprints") != _measure_fingerprints():
            return False
        if manifest.get("protein_fingerprint") != _protein_fingerprint():
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
    """{"raw_to_canonical", "values", "proteins"} -- everything still valid, or None.

    Deliberately NOT `store_is_current`. That question is "should the builder run"; this
    one is "what may I serve", and the two have different answers. Serving used to be
    gated on the strict one, so a single changed byte in pair_descriptors.py, or a
    regenerated interaction table, threw away every cached value at once and sent every
    reader back to RDKit -- which is exactly what happened after 2026-09-06 and is what
    `_measure_fingerprints` exists to end.

    What is checked, and against what it is actually keyed:

      values / raw_to_canonical  keyed by canonical SMILES, so they depend on NEITHER
                                  the interaction table nor any protein file. A
                                  regenerated table can only ADD candidates, and a
                                  candidate absent from raw_to_canonical already falls
                                  back to direct computation per miss. Filtered per
                                  measure: an entry keeps the measures whose recorded
                                  fingerprint still matches the code, and drops the
                                  rest, so `measure in entry` -- what every caller
                                  already tests -- stays the exact question of validity.
      proteins                   keyed by protein, computed FROM pocketness.pdb /
                                  coarse_graph_nodes.csv, so it is dropped when any of
                                  those moved. Callers see an empty dict and recompute,
                                  as they did for a full miss.

    Returns None only when there is no readable cache of this format at all.
    """
    root_dir = Path(root_dir).resolve()
    path = cache_path(root_dir, isomeric)
    try:
        manifest = json.loads(path.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if manifest.get("format_version") != CACHE_FORMAT_VERSION:
        return None
    if bool(manifest.get("isomeric")) != bool(isomeric):
        return None

    current = _measure_fingerprints()
    recorded = manifest.get("measure_fingerprints") or {}
    # A measure the manifest has no fingerprint for cannot be shown to be current, so it
    # is dropped rather than trusted -- the conservative direction, and only reachable
    # for a hand-edited manifest since every v2 build writes all of them.
    valid = {name for name, fp in current.items() if recorded.get(name) == fp}
    values = {
        key: {name: value for name, value in entry.items() if name in valid}
        for key, entry in manifest["values"].items()
    }

    proteins = manifest["proteins"]
    if not _protein_sources_unchanged(root_dir, manifest):
        proteins = {}

    return {
        "raw_to_canonical": manifest["raw_to_canonical"],
        "values": values,
        "proteins": proteins,
    }


def _protein_sources_unchanged(root_dir, manifest):
    """True when every recorded protein source still matches on disk.

    Only the protein files: `sources` also records the interaction table, which the
    per-SMILES values do not depend on (see load_pair_descriptor_cache).
    """
    for source in manifest.get("sources", []):
        relative = source["path"]
        if not relative.startswith("graphs" + os.sep) and not relative.startswith("graphs/"):
            continue
        try:
            stat = (root_dir / relative).stat()
        except OSError:
            return False
        if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
            return False
    return True


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
