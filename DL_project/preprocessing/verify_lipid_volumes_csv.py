#!/usr/bin/env python3
"""Cross-check data/Lipid_Volumes.csv (preprocessing/convert_lipid_volumes_xlsx.py's
output) against the one independent source of the same numbers this machine has:
data/pair_descriptor_cache_deterministic_v2.json's already-cached
`experimental_lipid_volume` entries, computed earlier by whichever machine last had
`openpyxl` and ran a cache build straight off the original .xlsx.

Builds the same {canonical SMILES: volume} table dataloader/pair_descriptors.py's
`_experimental_lipid_volume_table` builds (same RDKit canonicalisation, same
flat-then-isomeric-on-top merge for the couple of structures that collapse under
non-isomeric canonicalisation), then compares every entry against the cache's own
value for the same canonical key -- an entry the cache never saw is skipped rather
than counted as a mismatch (the cache only covers whichever candidates a build so far
has actually asked for, not this sheet's whole 391 structures).

This is real agreement only for whatever the cache already covers -- see
convert_lipid_volumes_xlsx.py's own docstring for what closes the rest of the gap.

Reads only.

    python3 preprocessing/verify_lipid_volumes_csv.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", type=Path, default=PROJECT_ROOT / "data" / "Lipid_Volumes.csv")
    parser.add_argument(
        "--cache", type=Path,
        default=PROJECT_ROOT / "data" / "pair_descriptor_cache_deterministic_v2.json",
    )
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args()

    import dataloader.pair_descriptors as pair_descriptors

    pair_descriptors._LIPID_VOLUME_CSV = args.csv
    pair_descriptors._experimental_lipid_volume_table.cache_clear()
    table = pair_descriptors._experimental_lipid_volume_table()
    print(f"{args.csv}: {len(table)} distinct canonical structures")

    cache = json.loads(args.cache.read_text())
    cached_values = cache.get("values", cache)

    checked = 0
    worst = 0.0
    mismatches = []
    for canonical, entry in cached_values.items():
        if not isinstance(entry, dict) or "experimental_lipid_volume" not in entry:
            continue
        cached_value = entry["experimental_lipid_volume"]
        if cached_value is None:
            continue
        ours = table.get(canonical)
        if ours is None:
            continue
        checked += 1
        diff = abs(float(cached_value) - float(ours))
        worst = max(worst, diff)
        if diff > args.tolerance:
            mismatches.append((canonical, cached_value, ours, diff))

    print(f"checked {checked} structures the cache already had a value for")
    print(f"largest difference: {worst:.2e}")
    if mismatches:
        print(f"{len(mismatches)} MISMATCHES beyond tolerance {args.tolerance}:")
        for canonical, cached_value, ours, diff in mismatches[:10]:
            print(f"  {canonical[:60]:60s} cache={cached_value} csv={ours} diff={diff:.4f}")
        return 1
    print("no mismatches -- CSV agrees with every cached value it overlaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
