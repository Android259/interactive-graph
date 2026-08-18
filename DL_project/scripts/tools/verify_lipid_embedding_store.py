#!/usr/bin/env python3
"""Check that the mapped lipid embedding store holds exactly the pickle's numbers.

The store exists to save memory, and it is only allowed to do that if it changes no
result. That is not something to take on trust from "it is the same tensors re-saved":
this compares them, key by key and element by element, and reports a difference as a
failure rather than as a tolerance.

Equality here means bitwise equality of float32 values -- ``torch.equal`` after a dtype
and shape check -- not ``allclose``. A store that rounded, cast or reordered anything
would shift metrics in the sixth decimal and make new runs incomparable with old ones,
which is exactly the failure this guards against.

Usage:
    python3 scripts/tools/verify_lipid_embedding_store.py [TABLE_PICKLE_NAME]

Exits non-zero on any mismatch, so it can gate a rebuild.
"""

import pickle
import sys
from pathlib import Path


# parents[2]: this file sits in scripts/tools/, so the project root is two levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402

from dataloader.lipid_embedding_store import (  # noqa: E402
    load_lipid_embedding_store,
    store_is_current,
)


DEFAULT_TABLE = "lipid_SMILES_embedding_deterministic.pkl"


def main(argv):
    table = argv[0] if argv else DEFAULT_TABLE
    data_dir = PROJECT_ROOT / "data"

    if not store_is_current(data_dir, table):
        print(f"no current store for {table}; build it first", file=sys.stderr)
        return 1
    store = load_lipid_embedding_store(data_dir, table)
    if store is None:
        print(f"store for {table} exists but could not be mapped", file=sys.stderr)
        return 1

    with open(data_dir / table, "rb") as handle:
        source = pickle.load(handle)

    problems = []
    if set(store) != set(source):
        only_store = len(set(store) - set(source))
        only_source = len(set(source) - set(store))
        problems.append(
            f"key sets differ: {only_store} only in store, {only_source} only in pickle"
        )

    checked = 0
    for key in source:
        if key not in store:
            continue
        mapped, original = store[key], source[key]
        if mapped.dtype != original.dtype:
            problems.append(f"{key[:40]}...: dtype {mapped.dtype} vs {original.dtype}")
        elif mapped.shape != original.shape:
            problems.append(f"{key[:40]}...: shape {tuple(mapped.shape)} vs {tuple(original.shape)}")
        elif not torch.equal(mapped, original):
            differing = int((mapped != original).sum())
            problems.append(f"{key[:40]}...: {differing} differing elements")
        checked += 1

    if problems:
        print(f"MISMATCH in {table}: {len(problems)} problem(s)", file=sys.stderr)
        for problem in problems[:20]:
            print(f"  {problem}", file=sys.stderr)
        return 1

    total = sum(value.numel() for value in source.values())
    print(
        f"OK: {checked} entries, {total} elements, bitwise identical "
        f"between {table} and its store"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
