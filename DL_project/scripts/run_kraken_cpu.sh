#!/usr/bin/env bash
# Kraken-CPU entry point: sync, queue and run this project's OAR jobs on the
# CPU-only frontend (separate from Kraken's GPU frontend, scripts/run_kraken.sh).
#
# No GPU is requested (CPU_ONLY=1, scripts/lib/cluster_common.sh's kraken-cpu
# profile): OAR_RESOURCES=/nodes=1 gets one whole 192-core node directly, no GPU
# ticket needed the way Bigfoot/kraken-gpu require one. Meant for configs that do
# not benefit from GPU compute -- measured so far only for --descriptors_head
# (~1000 parameters, 1 OMP thread/run optimal, see scripts/run_local.sh).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CLUSTER_NAME="kraken-cpu"

exec bash "${SCRIPT_DIR}/launch/run_cluster.sh" "$@"
