#!/usr/bin/env bash
# Watch bigfoot only. The combined watcher is scripts/wait_and_sync.sh, which
# visits every cluster in turn from a single loop; this wrapper narrows it to
# one cluster and gets its own tmux session, so the two never collide.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CLUSTERS="bigfoot"
export WAIT_ENTRY_SCRIPT="${SCRIPT_DIR}/$(basename "${BASH_SOURCE[0]}")"

exec bash "${SCRIPT_DIR}/../wait_and_sync.sh" "$@"
