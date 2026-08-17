#!/usr/bin/env bash
# Kraken entry point: sync, queue and run this project's OAR jobs.
#
# Kraken's GPUs are H100/H200 while Bigfoot's are A100/V100. That difference is
# expressed as environment settings in scripts/cluster_common.sh, which the
# submitters read -- the previous version instead tried to rewrite the submitter
# text remotely with awk/sed and stripped the wrong line, leaving the in-job
# `case *A100*|*V100*` guard in place so every Kraken job exited immediately.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CLUSTER_NAME="kraken"

exec bash "${SCRIPT_DIR}/launch/run_cluster.sh" "$@"
