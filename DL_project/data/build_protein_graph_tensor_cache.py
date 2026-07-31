#!/usr/bin/env python3
"""Convert protein graph CSV/PDB artifacts into one validated tensor cache."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataloader.protein_graph_tensor_cache import build_protein_graph_tensor_cache


if __name__ == "__main__":
    cache_path, manifest_path, count = build_protein_graph_tensor_cache(
        PROJECT_ROOT / "data"
    )
    print(f"cached {count} protein graphs")
    print(cache_path)
    print(manifest_path)
