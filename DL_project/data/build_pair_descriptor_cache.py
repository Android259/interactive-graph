#!/usr/bin/env python3
"""Build the shared cache for --pair_descriptors'/--two_pair_descriptors_paths' shared
per-candidate/per-protein base values (chain/unsaturation/hbond/heavy/tail_count/extent --
see needs_cache below).

Every training job otherwise runs RDKit over every candidate SMILES in the interaction
table and re-parses every protein's pocketness.pdb/coarse_graph_nodes.csv itself --
~12.2s of a ~13.6s dataset construction, measured on the current 35-protein table, and
none of it depends on --seed or --excluded_groups. Built once by this script, N
concurrent jobs share one cache file instead of paying that N times. See
dataloader/pair_descriptor_cache.py for the cache format and the fallback discipline a
missing/stale cache falls back to (compute directly, exactly as before this existed).

Meant to be run before a grid launches (scripts/run_local.sh calls it, alongside
data/build_lipid_embedding_store.py), which is also why it is a no-op when the cache is
already current: launching a grid must not rebuild it every time.

Usage:
    python3 data/build_pair_descriptor_cache.py [--args_file=PATH] [--force] [--quiet]

    --args_file=PATH  Pick whether a cache is needed, and which isomeric variant, from
                       that run's flags: neither --pair_descriptors nor
                       --two_pair_descriptors_paths means no cache is read at all (see
                       dataloader/New_dataloader.py._compute_pair_descriptors, which
                       reads the cache under either flag), and --lipid_isomers selects
                       the isomeric-SMILES variant. Without this, --pair_descriptors is
                       assumed and the deterministic (non-isomeric) variant is built.
    --force           Rebuild even when the cache is already current.
    --quiet           Print nothing when there was nothing to do.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.pair_descriptor_cache import (  # noqa: E402
    build_pair_descriptor_cache,
    store_is_current,
)
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

    Needed under --pair_descriptors OR --two_pair_descriptors_paths: New_dataloader.
    _compute_pair_descriptors reads this cache (chain/unsaturation/hbond/heavy/
    tail_count) whenever either is on, not just the first -- --two_pair_descriptors_
    paths' --good_descriptors/--bad_descriptors are built from those same base values
    (dataloader.pair_descriptors.resolve_requested_tokens), so a run of one without the
    other still pays the ~12s-of-~13.6s RDKit/pocket-parse cost this cache exists to
    remove, independently in every job sharing a node, if this only checked the flag
    named in the cache's own docstring.
    """
    if args_file is None:
        return True, False
    flags = flags_in(args_file)
    needed = "--pair_descriptors" in flags or "--two_pair_descriptors_paths" in flags
    return needed, "--lipid_isomers" in flags


def main(argv):
    args_file = None
    force = False
    quiet = False
    for argument in argv:
        if argument.startswith("--args_file="):
            args_file = argument.split("=", 1)[1]
        elif argument == "--force":
            force = True
        elif argument == "--quiet":
            quiet = True
        else:
            print(f"Unknown option: {argument}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            return 2

    needed, isomeric = needs_cache(args_file)
    if not needed:
        if not quiet:
            print(
                "pair descriptor cache: not needed "
                "(neither --pair_descriptors nor --two_pair_descriptors_paths is on)"
            )
        return 0

    data_dir = PROJECT_ROOT / "data"
    if store_is_current(data_dir, isomeric) and not force:
        if not quiet:
            variant = "isomeric" if isomeric else "deterministic"
            print(f"pair descriptor cache: {variant} already current")
        return 0

    import pandas

    csv_path = interaction_csv_path(str(data_dir) + "/")
    csv = pandas.read_csv(csv_path)
    protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())

    path, smiles_count, protein_count = build_pair_descriptor_cache(
        data_dir, csv, protein_names, csv_path, isomeric=isomeric
    )
    print(
        f"pair descriptor cache: built {smiles_count} SMILES, {protein_count} "
        f"proteins -> {path.name} ({path.stat().st_size / 2**10:.0f} KiB)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
