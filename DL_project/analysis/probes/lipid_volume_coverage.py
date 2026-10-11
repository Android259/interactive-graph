#!/usr/bin/env python3
"""How many lipids of the interaction table have a measured experimental_lipid_volume.

Counts distinct FullIdentityOfLipid (and distinct SmileGlobal) in the table, then how many
of them have a volume for at least one candidate structure, and lists the ones that have
none. Also counts candidates with no value for every lipid descriptor.
Read-only; nothing is written.

    python3 analysis/probes/lipid_volume_coverage.py [--isomeric]
"""
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from dataloader.dataset_source import interaction_csv_path
from dataloader.descriptor_cache_reader import load_lipid_descriptor_cache
from dataloader.descriptors import LIPID_DESCRIPTOR_NAMES
from dataloader.pocket_lipid_compatibility import chain_lengths_by_row
from preprocessing.compute_descriptors import as_arrays, descriptor_values_by_row


def main():
    isomeric = "--isomeric" in sys.argv
    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    cache = load_lipid_descriptor_cache(data_dir, isomeric)

    print(f"rows {len(csv)}, proteins {csv['LTPProtein'].nunique()}, "
          f"distinct FullIdentityOfLipid {csv['FullIdentityOfLipid'].nunique()}, "
          f"distinct SmileGlobal {csv['SmileGlobal'].nunique()}")

    volume = as_arrays(descriptor_values_by_row(csv, "experimental_lipid_volume", isomeric, cache=cache))
    lipids = csv["FullIdentityOfLipid"].to_numpy()
    has_value = {}
    for lipid, row in zip(lipids, volume):
        has_value[lipid] = has_value.get(lipid, False) or bool((~np.isnan(row)).any())
    uncovered = sorted(name for name, found in has_value.items() if not found)
    print(f"experimental_lipid_volume: {len(has_value) - len(uncovered)} of {len(has_value)} "
          f"lipids have a value in at least one candidate; {len(uncovered)} have none")
    for name in uncovered:
        print(f"  no volume: {name}")

    print("candidates with no value, per lipid descriptor:")
    for name in LIPID_DESCRIPTOR_NAMES:
        if name == "chain":
            per_row = chain_lengths_by_row(csv, isomeric, cache=cache)
        else:
            per_row = descriptor_values_by_row(
                csv, "heavy_atoms" if name == "heavy" else name, isomeric, cache=cache
            )
        arrays = as_arrays(per_row)
        missing = sum(int(np.isnan(row).sum()) for row in arrays)
        print(f"  {name}: {missing} of {sum(len(row) for row in arrays)}")


if __name__ == "__main__":
    main()
