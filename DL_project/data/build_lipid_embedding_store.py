#!/usr/bin/env python3
"""Build the memory-mapped store for the lipid SMILES embedding table a run needs.

Every training job otherwise unpickles the whole table into itself -- 267 MiB resident
and roughly 1 GiB of transient peak for the deterministic table -- so N concurrent jobs
pay for it N times over. Built once by this script, the table is mapped instead of read,
and the jobs share one copy through the page cache. See
``dataloader/lipid_embedding_store.py`` for why that leaves every computed number
unchanged.

Meant to be run before a grid launches (``scripts/run_local.sh`` calls it, and the
cluster preflight does too), which is also why it is a no-op when the store is already
current: launching a grid must not rebuild a 267 MiB archive every time.

Usage:
    python3 data/build_lipid_embedding_store.py [--args_file=PATH] [--force] [--quiet]

    --args_file=PATH  Pick the table the way PLIDataset does, from that run's flags:
                       --lipid_graph_isomers needs no table at all, --lipid_isomers
                       needs the isomeric one, everything else the deterministic one.
                       Without this, the deterministic table is assumed.
    --force           Rebuild even when the store is already current.
    --quiet           Print nothing when there was nothing to do.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.lipid_embedding_store import (  # noqa: E402
    build_lipid_embedding_store,
    store_is_current,
)


DETERMINISTIC_TABLE = "lipid_SMILES_embedding_deterministic.pkl"
ISOMERIC_TABLE = "lipid_SMILES_isomeric_embedding.pkl"


def table_for_args_file(args_file):
    """The embedding table a run with these flags will open, or None for no table.

    Mirrors the selection in PLIDataset.__init__. Reading the flags as text keeps this
    script independent of read_configuration's argv handling, and matches how
    scripts/run_local.sh already inspects an args file (for --cold_split, --num_workers).
    """
    flags = [
        line.split("=", 1)[0].strip()
        for line in Path(args_file).read_text().splitlines()
        if line.startswith("--")
    ]
    if "--lipid_graph_isomers" in flags:
        return None
    return ISOMERIC_TABLE if "--lipid_isomers" in flags else DETERMINISTIC_TABLE


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

    data_dir = PROJECT_ROOT / "data"
    table = DETERMINISTIC_TABLE if args_file is None else table_for_args_file(args_file)
    if table is None:
        if not quiet:
            print("lipid embedding store: not needed (--lipid_graph_isomers)")
        return 0

    # A missing table is not this script's problem to report: the run itself raises a
    # clear FileNotFoundError naming the file, and a preflight that hard-failed here
    # would block grids whose config never opens it.
    if not (data_dir / table).exists():
        if not quiet:
            print(f"lipid embedding store: {table} not present, skipping")
        return 0

    if store_is_current(data_dir, table) and not force:
        if not quiet:
            print(f"lipid embedding store: {table} already current")
        return 0

    store_path, manifest_path, count = build_lipid_embedding_store(data_dir, table)
    print(
        f"lipid embedding store: built {count} entries from {table} -> "
        f"{store_path.name} ({store_path.stat().st_size / 2**20:.0f} MiB)"
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
