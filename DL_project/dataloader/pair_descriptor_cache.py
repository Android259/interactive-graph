"""Precomputed, disk-shared cache for --pair_descriptors' per-candidate/per-protein values.

Dataloader.py._compute_pair_descriptors runs RDKit over every candidate SMILES in
the interaction table (chain length, unsaturation, H-bond capacity, heavy-atom count)
and parses every protein's pocketness.pdb/coarse_graph_nodes.csv (pocket extent,
aromatic_share_core/rim) -- none of which depends on --seed or --excluded_groups. A
local grid launches one process per (group, seed) pair (scripts/run_local.sh), so an
untouched, unregenerated interaction table and an untouched data/graphs/ still get this
work redone from scratch in every one of those processes: measured at ~12.2s of a
~13.6s dataset construction, on a 35-protein/~9905-row table (files/... see the
descriptors_path perf investigation this module answers).

Built once by data/build_pair_descriptor_cache.py (scripts/run_local.sh calls it
alongside data/build_lipid_embedding_store.py, before the grid launches) and read by
every job afterwards. Unlike the lipid embedding table this is not memory-mapped: the
payload is a few thousand SMILES times 4 floats plus 35 proteins times 3, kilobytes not
hundreds of megabytes, so there is no per-process RAM to share -- what repeats across
jobs is CPU time, not resident memory, and a plain JSON `read_text` + `json.loads` per
job removes that without needing torch's mmap machinery at all.

Two things are cached, because two different reads need canonicalisation skipped
entirely to pay off:

    raw_to_canonical : the exact candidate string as it appears in the interaction
                        table -> its canonical SMILES, or None where RDKit cannot parse
                        it. Without this, chain_lengths_by_row/descriptor_values_by_row
                        would still have to call Chem.MolFromSmiles/MolToSmiles on every
                        raw candidate just to know which cache entry to look up --
                        that parse is roughly a fifth of the per-molecule RDKit cost, so
                        skipping only the value computation below it would leave most of
                        the win on the table.
    values            : canonical SMILES -> {chain, unsaturation, hbond, heavy_atoms}.

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
# _MEASURES' formulas (unsaturation/hbond/heavy_atoms), pocket_extent_by_protein,
# pocket_rim_core_aromatic_share_by_protein. None of these are files
# store_is_current()'s size/mtime check watches -- that check guards the DATA
# a cache was built from (the interaction table, protein structures), not the
# CODE that turns it into cached numbers, so a formula change here would
# otherwise leave a still-"current" cache silently serving values computed
# under the old formula. Folded into the cache filename below instead: a code
# change is then a different filename outright, never a stale hit.
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


def build_pair_descriptor_cache(root_dir, csv, protein_names, csv_path, isomeric=False):
    """Compute and write the cache. Returns (cache_path, smiles_count, protein_count).

    Rebuilds unconditionally -- the caller (data/build_pair_descriptor_cache.py)
    decides whether that is needed, same division of responsibility as
    lipid_embedding_store.build_lipid_embedding_store.
    """
    root_dir = Path(root_dir).resolve()

    raw_to_canonical = {}
    values = {}
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
            if key not in values:
                entry = {"chain": longest_acyl_chain(key)}
                entry.update((measure, fn(key)) for measure, fn in _MEASURES.items())
                values[key] = entry

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
