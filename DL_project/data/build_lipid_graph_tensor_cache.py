#!/usr/bin/env python3
"""Convert lipid isomer graph CSV artifacts into one validated tensor cache.

Usage: python3 data/build_lipid_graph_tensor_cache.py

Mirrors data/build_protein_graph_tensor_cache.py: manual, run once after
data/build_lipid_isomer_graphs.py has (re)written data/lipid_graphs/*, not
wired into every grid launch, since these tensors depend only on that data,
never on an args file. Rerun it whenever data/lipid_graphs/ changes; a stale
or missing cache is never fatal, LipidIsomerGraphBuilder falls back to
reading the CSVs directly.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.lipid_graph_tensor_cache import build_lipid_graph_tensor_cache


if __name__ == "__main__":
    cache_path, manifest_path, count = build_lipid_graph_tensor_cache(PROJECT_ROOT / "data")
    print(f"cached {count} lipid graphs")
    print(cache_path)
    print(manifest_path)
