#!/usr/bin/env python3
"""Build the shared cache for the descriptor catalog's shared
per-candidate/per-protein base values (chain/unsaturation/hbond/heavy/tail_count/extent --
see needs_cache below).

Every training job otherwise runs RDKit over every candidate SMILES in the interaction
table and re-parses every protein's pocketness.pdb/coarse_graph_nodes.csv itself --
~12.2s of a ~13.6s dataset construction, measured on the current 35-protein table, and
none of it depends on --seed or --excluded_groups. Built once by this script, N
concurrent jobs share one cache file instead of paying that N times. See
dataloader/descriptor_cache_reader.py for the cache format and the fallback discipline a
missing/stale cache falls back to (compute directly, exactly as before this existed).

Meant to be run before a grid launches (scripts/run_local.sh calls it, alongside
data/build_lipid_embedding_store.py), which is also why it is a no-op when the cache is
already current: launching a grid must not rebuild it every time.

Usage:
    python3 data/build_descriptor_cache.py [--args_file=PATH] [--force] [--quiet]
                                                 [--check_only]

    --args_file=PATH  Pick whether a cache is needed, and which isomeric variant, from
                       that run's flags: none of --descriptor_heads, --protein_descriptors,
                       --lipid_descriptors or --deepclip_protein_gate means no cache is
                       read at all (see dataloader/Dataloader.py._compute_descriptors),
                       and --lipid_isomers selects the isomeric-SMILES variant. Without
                       this, a cache is assumed needed and the deterministic
                       (non-isomeric) variant is built.
    --force           Rebuild even when the cache is already current.
    --quiet           Print nothing when there was nothing to do.
    --check_only      Report whether a rebuild is needed (exit 0: nothing to do: not
                       needed, or already current; exit 1: a rebuild would run) without
                       doing the RDKit/pocket-parse work. For a caller (e.g. a cluster
                       launcher) that wants to know cheaply, on a shared login node,
                       whether it must hand the real build off to a job -- the check
                       itself is a handful of stat() calls, never the ~5 minutes of
                       single-threaded RDKit the actual build can take on the full
                       interaction table.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.cache_builders.descriptor_csv_builder import (  # noqa: E402
    build_lipid_descriptor_cache,
)
from dataloader.descriptor_cache_reader import store_is_current  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402


def flags_in(args_file):
    """Flag names only (text before '='), the same reading build_lipid_embedding_store
    uses for its own args-file inspection: independent of read_configuration's argv
    handling, and matching how scripts/run_local.sh already inspects an args file.
    """
    return [
        line.split("=", 1)[0].strip()
        for line in Path(args_file).read_text().splitlines()
        if line.startswith("--")
    ]


def needs_cache(args_file):
    """(needed, isomeric), from that run's flags, or (True, False) with no args file.

    Needed exactly when dataloader.descriptors.full_catalog_order(config) is non-empty,
    i.e. when any flag that feeds the descriptor catalog is present:
    Dataloader._compute_descriptors computes chain/unsaturation/hbond/heavy (and
    conditionally tail_count) the moment ANY of them is, and pays the ~12s-of-~13.6s
    RDKit/pocket-parse cost this cache exists to remove, independently in every job
    sharing a node, if the cache is missing. Checked here as raw flag presence rather
    than by calling full_catalog_order itself (which needs a parsed ModelConfig, not a
    flag list).

    No lipid_shape distinction: dataloader/descriptor_cache_reader.py's build always
    computes every measure (see that module's docstring), so the next run that reads
    radius_of_gyration/asphericity/molecular_volume never finds a cache silently
    missing them.
    """
    if args_file is None:
        return True, False
    flags = flags_in(args_file)
    needed = any(
        flag in flags
        for flag in (
            "--descriptor_heads", "--protein_descriptors", "--lipid_descriptors",
            "--deepclip_protein_gate",
        )
    )
    return needed, "--lipid_isomers" in flags


def main(argv):
    args_file = None
    force = False
    quiet = False
    check_only = False
    for argument in argv:
        if argument.startswith("--args_file="):
            args_file = argument.split("=", 1)[1]
        elif argument == "--force":
            force = True
        elif argument == "--quiet":
            quiet = True
        elif argument == "--check_only":
            check_only = True
        else:
            print(f"Unknown option: {argument}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            return 2

    needed, isomeric = needs_cache(args_file)
    if not needed:
        if not quiet:
            print(
                "pair descriptor cache: not needed "
                "(no descriptor flag is on)"
            )
        return 0

    data_dir = PROJECT_ROOT / "data"
    if store_is_current(data_dir, isomeric) and not force:
        if not quiet:
            variant = "isomeric" if isomeric else "deterministic"
            print(f"pair descriptor cache: {variant} already current")
        return 0

    if check_only:
        if not quiet:
            variant = "isomeric" if isomeric else "deterministic"
            print(f"pair descriptor cache: {variant} needs a rebuild")
        return 1

    import pandas

    csv_path = interaction_csv_path(str(data_dir) + "/")
    csv = pandas.read_csv(csv_path)
    protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())

    path, smiles_count, protein_count = build_lipid_descriptor_cache(
        data_dir, csv, protein_names, csv_path, isomeric=isomeric
    )
    print(
        f"pair descriptor cache: built {smiles_count} SMILES, {protein_count} "
        f"proteins -> {path.name} ({path.stat().st_size / 2**10:.0f} KiB)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
