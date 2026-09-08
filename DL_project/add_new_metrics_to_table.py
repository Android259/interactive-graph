#!/usr/bin/env python3
"""Root-level entry point -- delegates entirely to analysis/add_new_metrics_to_table.py.

This file used to carry its own copy of the aggregation logic, which diverged
from the analysis/ version over time (one got a bugfix the other didn't,
silently dropping real training results -- see the SOURCE_KEY_FIELDS history).
It now has none: every caller that invokes `add_new_metrics_to_table.py` from
the project root (wait_and_sync.sh's update_metrics_table/check_pending_reports,
cluster_preflight_remote.sh's file check, remote ssh invocations) still works
unchanged, but there is exactly one implementation to fix from now on.

The delegation is by explicit FILE PATH, not by putting analysis/ on sys.path and
importing the bare name. The bare-name version worked only while analysis/ happened to
sit ahead of the project root on sys.path: whenever the root came first -- which is what
pytest's collection produced once enough test modules were imported -- the bare import
resolved to THIS file, and its own `from add_new_metrics_to_table import main` then hit
a partially initialised module and raised ImportError instead. Two importable modules
sharing one name is the hazard; addressing the intended one by path removes it, and the
public names below stay re-exported so `from add_new_metrics_to_table import
add_new_metrics` keeps working from either directory.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ANALYSIS_DIR = Path(__file__).resolve().parent / "analysis"
_IMPLEMENTATION = _ANALYSIS_DIR / "add_new_metrics_to_table.py"

# analysis/ still has to be importable: the implementation imports its SIBLINGS by bare
# name (build_metrics_table and friends), the way every script in that directory does.
# What changed is only how the implementation ITSELF is addressed -- by path below, so
# the bare name never has two candidates.
if str(_ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS_DIR))

_spec = importlib.util.spec_from_file_location(
    "analysis.add_new_metrics_to_table", _IMPLEMENTATION
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

SOURCE_KEY_FIELDS = _module.SOURCE_KEY_FIELDS
metric_source_key = _module.metric_source_key
add_new_metrics = _module.add_new_metrics
main = _module.main

if __name__ == "__main__":
    main()
