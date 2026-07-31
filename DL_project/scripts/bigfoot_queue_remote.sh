#!/usr/bin/env bash
# Compatibility shim: the queue helper is now cluster-generic.
#
# Kept because a wait/sync daemon started before the port holds this path in
# BIGFOOT_QUEUE_HELPER and keeps invoking it remotely on every poll. Safe to
# delete once no such daemon is running.
set -euo pipefail

exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cluster_queue_remote.sh" "$@"
