#!/usr/bin/env bash
# Bigfoot entry point: sync, queue and run this project's OAR jobs.
#
# All behaviour lives in scripts/run_cluster.sh; scripts/cluster_common.sh
# supplies Bigfoot's settings (A100/V100, pr-molgen, .bigfoot_job_queues, the
# bigfoot_wait tmux session), which are unchanged from before the Kraken port.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CLUSTER_NAME="bigfoot"

exec bash "${SCRIPT_DIR}/run_cluster.sh" "$@"
