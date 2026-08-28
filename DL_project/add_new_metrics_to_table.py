#!/usr/bin/env python3
"""Root-level entry point -- delegates entirely to analysis/add_new_metrics_to_table.py.

This file used to carry its own copy of the aggregation logic, which diverged
from the analysis/ version over time (one got a bugfix the other didn't,
silently dropping real training results -- see the SOURCE_KEY_FIELDS history).
It now has none: every caller that invokes `add_new_metrics_to_table.py` from
the project root (wait_and_sync.sh's update_metrics_table/check_pending_reports,
cluster_preflight_remote.sh's file check, remote ssh invocations) still works
unchanged, but there is exactly one implementation to fix from now on.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ANALYSIS_DIR = Path(__file__).resolve().parent / "analysis"
if str(_ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS_DIR))

from add_new_metrics_to_table import main

if __name__ == "__main__":
    main()
