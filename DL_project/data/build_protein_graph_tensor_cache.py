#!/usr/bin/env python3
"""Convert protein graph CSV/PDB artifacts into one validated tensor cache.

Usage: python3 data/build_protein_graph_tensor_cache.py [--no_protein_geometry]

Plain, no flag: builds/refreshes the default cache (protein_graph_tensors.pt),
the one every config without --no_protein_geometry reads.

--no_protein_geometry: builds the separate cache
(protein_graph_tensors.no_geometry.pt) that --no_protein_geometry configs read
instead -- its protein node vector is 0 wide, same as what those configs build
live when there is no cache at all. The default cache is untouched either way;
the two never share a file.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.protein_graph_tensor_cache import build_protein_graph_tensor_cache


if __name__ == "__main__":
    node_columns = () if "--no_protein_geometry" in sys.argv[1:] else None
    kwargs = {} if node_columns is None else {"node_columns": node_columns}
    cache_path, manifest_path, count = build_protein_graph_tensor_cache(
        PROJECT_ROOT / "data", **kwargs
    )
    print(f"cached {count} protein graphs")
    print(cache_path)
    print(manifest_path)
