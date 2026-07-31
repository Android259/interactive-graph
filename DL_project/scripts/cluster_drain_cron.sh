#!/usr/bin/env bash
# Cluster-side job drainer: submits queued OAR jobs as waiting slots free up.
#
# This runs ON the cluster frontend, from the frontend's own crontab, which is
# the whole point: with it installed, getting jobs onto the cluster no longer
# depends on a laptop being switched on, connected, or running a tmux daemon.
# The queue itself already lives on the cluster (.<cluster>_job_queues/), so the
# only thing that used to be remote was the timer.
#
#   CLUSTER_NAME=bigfoot bash scripts/cluster_drain_cron.sh
#
# scripts/wait_and_sync2.sh installs the crontab entry that calls this; running
# it by hand does one drain pass. It is a no-op when nothing is pending, so it
# is safe to schedule every few minutes.
#
# Concurrency: cluster_queue_remote.sh's drain takes a blocking flock on
# <queue>/drain.lock, so a cron pass and a hand-run pass serialise correctly.
# The crontab entry adds its own `flock -n` so overlapping ticks skip rather
# than pile up.
set -euo pipefail
export LC_ALL=C
# cron hands over a minimal environment; oarsub/oarstat live in /usr/bin.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH:+:${PATH}}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

CLUSTER_NAME="${CLUSTER_NAME:-bigfoot}"
QUEUE_ROOT="${CLUSTER_QUEUE_ROOT:-${PROJECT_DIR}/.${CLUSTER_NAME}_job_queues}"
QUEUE_USER="${REMOTE_USER:-$(id -un)}"
QUEUE_HELPER="${QUEUE_HELPER:-${PROJECT_DIR}/scripts/cluster_queue_remote.sh}"
# The cap on simultaneously waiting OAR jobs. The file below is authoritative
# and lives on the cluster, so two computers submitting to the same cluster
# cannot drain it with two different limits; the environment is the fallback for
# a cluster where the file has not been written yet.
MAX_WAITING_JOBS="${MAX_WAITING_JOBS:-50}"
if [[ -s "${QUEUE_ROOT}/max_waiting" ]]; then
    read -r configured < "${QUEUE_ROOT}/max_waiting" || configured=""
    [[ "${configured}" =~ ^[0-9]+$ ]] && MAX_WAITING_JOBS="${configured}"
fi
DRAIN_LOG="${DRAIN_LOG:-${PROJECT_DIR}/script_logs/drain_${CLUSTER_NAME}.log}"
LOG_MAX_BYTES="${LOG_MAX_BYTES:-1048576}"

mkdir -p "$(dirname "${DRAIN_LOG}")"
# Nothing rotates an unattended cron job's log, so keep its tail ourselves.
if [[ -f "${DRAIN_LOG}" ]] &&
    (( $(stat -c %s "${DRAIN_LOG}" 2>/dev/null || printf 0) > LOG_MAX_BYTES ))
then
    if tail -c "$((LOG_MAX_BYTES / 2))" "${DRAIN_LOG}" > "${DRAIN_LOG}.trim"; then
        mv "${DRAIN_LOG}.trim" "${DRAIN_LOG}"
    else
        rm -f "${DRAIN_LOG}.trim"
    fi
fi
# script_logs/ is rsynced back by the watcher, so this log is readable from
# either computer -- that is how you see what the drainer did while you were
# offline.
exec >>"${DRAIN_LOG}" 2>&1

log() { printf '[%s] %s\n' "$(date -Iseconds)" "$*"; }

[[ -d "${QUEUE_ROOT}" ]] || exit 0

status=0
for queue_dir in "${QUEUE_ROOT}"/*; do
    [[ -d "${queue_dir}" ]] || continue
    [[ -f "${queue_dir}/initialized" ]] || continue
    # Silent when there is nothing to submit: an idle cron pass must not write a
    # line every few minutes forever.
    [[ -s "${queue_dir}/pending.commands" ]] || continue

    max_waiting="${MAX_WAITING_JOBS}"
    if [[ -s "${queue_dir}/max_waiting" ]]; then
        read -r configured < "${queue_dir}/max_waiting" || configured=""
        [[ "${configured}" =~ ^[0-9]+$ ]] && max_waiting="${configured}"
    fi

    # drain prints its own submitted/waiting/pending summary on success.
    if ! CLUSTER_NAME="${CLUSTER_NAME}" CLUSTER_LABEL="${CLUSTER_NAME}" \
        bash "${QUEUE_HELPER}" drain \
            "${queue_dir}" "${QUEUE_USER}" "${max_waiting}"
    then
        # drain keeps every unsubmitted command pending when an oarsub fails, so
        # nothing is lost and the next tick retries. A persistent failure here
        # means a bad PROJECT/GPU_PROPERTY, not a lost batch.
        log "drain failed for ${queue_dir}; commands kept pending."
        status=1
    fi
done

exit "${status}"
