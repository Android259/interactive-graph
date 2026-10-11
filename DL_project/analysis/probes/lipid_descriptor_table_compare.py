#!/usr/bin/env python3
"""Does dataloader.chemistry_prior._lipid_descriptor_table give the same per-lipid table as before an edit?

    python3 analysis/probes/lipid_descriptor_table_compare.py --save before.json
    # ... edit the code ...
    python3 analysis/probes/lipid_descriptor_table_compare.py --compare before.json

Reads the interaction table and the descriptor cache; writes only the file given to --save.
"""
import json
import os
import sys

import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from dataloader.chemistry_prior import _lipid_descriptor_table
from dataloader.dataset_source import interaction_csv_path


def main():
    mode, path = sys.argv[1], sys.argv[2]
    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data")))
    table = _lipid_descriptor_table(csv)
    if mode == "--save":
        with open(path, "w") as handle:
            json.dump(table, handle)
        print(f"saved {len(table)} lipids x {len(next(iter(table.values())))} descriptors")
        return
    with open(path) as handle:
        before = json.load(handle)
    print("same lipids, same order:", list(before) == list(table))
    print("same descriptor order  :", list(next(iter(before.values()))) == list(next(iter(table.values()))))
    worst = {}
    for lipid, values in before.items():
        for name, value in values.items():
            worst[name] = max(worst.get(name, 0.0), abs(value - table[lipid][name]))
    for name, gap in worst.items():
        print(f"  {name}: max abs difference {gap:.3g}")
    print("identical:", all(gap == 0.0 for gap in worst.values()))


if __name__ == "__main__":
    main()
