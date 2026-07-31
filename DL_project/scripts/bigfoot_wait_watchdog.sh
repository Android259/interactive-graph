#!/usr/bin/env bash
# Watchdog for the bigfoot-only wait daemon. The combined watcher is guarded by
# scripts/cluster_wait_watchdog.sh with no CLUSTERS override.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CLUSTERS="bigfoot"

exec bash "${SCRIPT_DIR}/cluster_wait_watchdog.sh" "$@"
