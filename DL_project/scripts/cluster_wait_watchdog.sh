#!/usr/bin/env bash
# Ensures the persistent wait/sync tmux daemon is alive and making progress.
# Meant to run unattended from cron every few minutes; it is a no-op when the
# daemon is healthy, so it is safe to invoke often.
#
# Watches the same SET of clusters as the daemon it guards -- the session, log
# and restart-log names all derive from CLUSTERS via cluster_wait_session(), so
# a watchdog for the combined watcher never fights one for a single cluster.
#
#   bash scripts/cluster_wait_watchdog.sh                  # combined watcher
#   CLUSTERS=kraken bash scripts/cluster_wait_watchdog.sh  # kraken-only watcher
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CLUSTERS="${CLUSTERS:-bigfoot kraken}"
read -r -a CLUSTER_LIST <<< "${CLUSTERS}"
CLUSTER_NAME="${CLUSTER_LIST[0]}"

# shellcheck source=scripts/cluster_common.sh
source "${SCRIPT_DIR}/cluster_common.sh"

SESSION="${WAIT_TMUX_SESSION}"
LOG_FILE="${PROJECT_ROOT}/script_logs/${SESSION}.log"
# Must exceed POLL_SECONDS (default 300s) by a comfortable margin so a
# normal-length poll (rsync of a busy run/ tree, a slow ssh round trip, now
# multiplied by the number of clusters visited) never looks like a hang.
STALE_SECONDS="${WAIT_WATCHDOG_STALE_SECONDS}"

# One cluster -> its wrapper; several -> the combined watcher.
if (( ${#CLUSTER_LIST[@]} == 1 )) \
    && [[ -f "${PROJECT_ROOT}/scripts/wait_and_sync_${CLUSTER_LIST[0]}.sh" ]]
then
    WAIT_SCRIPT="scripts/wait_and_sync_${CLUSTER_LIST[0]}.sh"
else
    WAIT_SCRIPT="scripts/wait_and_sync.sh"
fi

log() {
    printf '[%s] %s\n' "$(date -Iseconds)" "$1"
}

session_alive=0
if tmux has-session -t "${SESSION}" 2>/dev/null; then
    session_alive=1
fi

stale=0
if [[ -f "${LOG_FILE}" ]]; then
    now="$(date +%s)"
    log_mtime="$(stat -c %Y "${LOG_FILE}")"
    if (( now - log_mtime > STALE_SECONDS )); then
        stale=1
    fi
fi

if (( session_alive == 1 && stale == 0 )); then
    exit 0
fi

if (( session_alive == 1 && stale == 1 )); then
    log "${SESSION} log stale for >${STALE_SECONDS}s; killing hung session."
    tmux kill-session -t "${SESSION}" 2>/dev/null || true
fi

if (( session_alive == 0 )); then
    log "${SESSION} tmux session not found."
fi

log "Restarting ${WAIT_SCRIPT} for: ${CLUSTERS}."
cd "${PROJECT_ROOT}"
CLUSTERS="${CLUSTERS}" nohup bash "${WAIT_SCRIPT}" \
    >"/tmp/${SESSION}_last_restart.log" 2>&1 &
disown
