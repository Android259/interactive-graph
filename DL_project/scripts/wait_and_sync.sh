#!/usr/bin/env bash
# Watch several clusters from ONE loop: each poll visits every cluster in turn,
# pulls its logs / TensorBoard events / results, then rebuilds the metrics table
# once from the merged local tree.
#
#   bash scripts/wait_and_sync.sh                 # bigfoot, then kraken, repeat
#   CLUSTERS=kraken bash scripts/wait_and_sync.sh # one cluster only
#
# Building the table locally (rather than on each cluster, as the per-cluster
# loop used to) is what makes multi-cluster watching correct: run/, test_metrics/
# and script_logs/ from every cluster rsync into the same local tree, so one
# local rescan sees the union. The old remote-then-download approach had each
# cluster regenerate the table from only its own results and copy it over the
# local file, so two clusters would overwrite each other's rows in turn.
set -euo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/$(basename "${BASH_SOURCE[0]}")"
ENTRY_SCRIPT="${WAIT_ENTRY_SCRIPT:-${SCRIPT_PATH}}"
LOCAL_PROJECT="${LOCAL_PROJECT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

# Clusters to visit, in order. cluster_profile() (cluster_common.sh) re-derives
# every cluster-dependent global on each switch.
_ENV_WAIT_TMUX_SESSION="${WAIT_TMUX_SESSION:-}"
unset WAIT_TMUX_SESSION
CLUSTERS="${CLUSTERS:-bigfoot kraken}"
read -r -a CLUSTER_LIST <<< "${CLUSTERS}"
(( ${#CLUSTER_LIST[@]} > 0 )) || { printf 'CLUSTERS is empty.\n' >&2; exit 2; }

# shellcheck source=scripts/cluster_common.sh
CLUSTER_NAME="${CLUSTER_LIST[0]}"
source "${SCRIPT_DIR}/cluster_common.sh"

# print_running_progress() and the log/TensorBoard readers behind it, shared
# verbatim with scripts/wait_and_sync2.sh so the two watchers cannot drift.
# shellcheck source=scripts/wait_progress_table.sh
source "${SCRIPT_DIR}/wait_progress_table.sh"

# One tmux session per SET of clusters, so a combined watcher and a
# single-cluster watcher never adopt each other's session or pid file.
WAIT_TMUX_SESSION="${_ENV_WAIT_TMUX_SESSION:-$(cluster_wait_session "${CLUSTERS}")}"

EVENT_LOOKBACK_MINUTES="${EVENT_LOOKBACK_MINUTES:-480}"

# Routine progress chatter is hidden: a healthy poll should report only what
# changed. Anything abnormal (failed reconnect, failed drain, a resumed stale
# queue, rsync/OAR errors) is printed unconditionally. WAIT_VERBOSE=1 restores
# the full narration.
WAIT_VERBOSE="${WAIT_VERBOSE:-0}"
note() { [[ "${WAIT_VERBOSE}" == "1" ]] && printf '%s\n' "$*" || true; }

# Per-cluster state, indexed by cluster name.
declare -A CLUSTER_PREVIOUS_JOB_IDS=()
declare -A CLUSTER_SESSION_MARKER=()
declare -A CLUSTER_QUEUE_DIR=()
declare -A CLUSTER_IDLE=()

# Establishes (or reuses) the shared SSH ControlMaster connection to $remote.
# allow_password=1 permits an interactive password prompt (only safe when a
# real terminal is attached, i.e. before we detach into tmux); allow_password=0
# forces key-only BatchMode auth so a headless caller can never hang on a
# prompt nobody can answer.
ensure_ssh_master() {
    local allow_password="${1:-0}"
    local batch_opt=(-o BatchMode=yes)
    [[ "${allow_password}" == "1" ]] && batch_opt=()

    # `-O check` must never block: without BatchMode/ConnectTimeout, a stale or
    # half-dead master socket makes it fall through to a fresh jump-host (gricad)
    # connect that hangs forever with no tty, freezing the whole poll loop. Wrap
    # in `timeout` so a dead master can never stall the cycle -- a non-zero here
    # just means "no usable master", and the block below (re)opens one.
    if timeout 15 ssh -S "${SSH_CONTROL_PATH}" -o BatchMode=yes \
        -o ConnectTimeout=10 -O check "${remote}" >/dev/null 2>&1; then
        note "Reusing shared SSH connection to ${remote}."
        return 0
    fi

    note "Opening shared SSH connection to ${remote}."
    # The jump-host hop (gricad) occasionally resets the very first attempt
    # ("Connection closed by UNKNOWN port 65535") even though the network is
    # otherwise fine; a short retry avoids losing a full POLL_SECONDS cycle
    # to one flaky attempt.
    local attempt
    for attempt in 1 2 3; do
        if ssh -M -S "${SSH_CONTROL_PATH}" \
            "${batch_opt[@]}" \
            -o ConnectTimeout=20 \
            -o ControlPersist=30m \
            -o ServerAliveInterval=30 \
            -o ServerAliveCountMax=10 \
            -fN "${remote}"
        then
            return 0
        fi
        printf 'Connection attempt %d/3 to %s failed; retrying.\n' "${attempt}" "${remote}" >&2
        sleep 3
    done
    return 1
}

if [[ "${WAIT_TMUX}" != "0" && -z "${TMUX:-}" ]] && command -v tmux >/dev/null 2>&1; then
    tmux_session="${WAIT_TMUX_SESSION}"
    if [[ -z "${WAIT_TMUX_LOG}" ]]; then
        mkdir -p "${LOCAL_PROJECT}/script_logs"
        WAIT_TMUX_LOG="${LOCAL_PROJECT}/script_logs/${tmux_session}.log"
    fi

    if tmux has-session -t "${tmux_session}" 2>/dev/null; then
        daemon_pid_file="${LOCAL_PROJECT}/script_logs/${tmux_session}.pid"
        # A tmux daemon runs the copy of the script it read at launch, so edits
        # never reach an already-running daemon and re-running just reattaches
        # to the stale one. If any file the daemon's behaviour depends on was
        # updated after it started, kill it and fall through to relaunch with
        # the current code. All four matter: this generic implementation, the
        # per-cluster wrapper that selects CLUSTER_NAME, the cluster profile, and
        # the shared progress table.
        daemon_stale=0
        if [[ -f "${daemon_pid_file}" ]]; then
            for source_file in \
                "${SCRIPT_PATH}" "${ENTRY_SCRIPT}" \
                "${SCRIPT_DIR}/cluster_common.sh" \
                "${SCRIPT_DIR}/wait_progress_table.sh"
            do
                if [[ -f "${source_file}" && "${source_file}" -nt "${daemon_pid_file}" ]]; then
                    daemon_stale=1
                fi
            done
        fi
        if (( daemon_stale )); then
            printf 'wait_and_sync was updated since the running daemon started; restarting it with the latest code.\n'
            tmux kill-session -t "${tmux_session}" 2>/dev/null || true
        else
            printf 'Wait/sync is already running in tmux session: %s (not starting another).\n' "${tmux_session}"
            if [[ -f "${daemon_pid_file}" ]] && kill -USR1 "$(cat "${daemon_pid_file}")" 2>/dev/null; then
                printf 'Requested an immediate refresh (no need to wait out the poll interval).\n'
            fi
            printf 'Streaming stats in this terminal from: %s\n' "${WAIT_TMUX_LOG}"
            printf 'Stop watching with Ctrl-c; tmux wait keeps running. Attach with: tmux attach -t %s\n' "${tmux_session}"
            pane_pid="$(tmux display-message -p -t "${tmux_session}" '#{pane_pid}')"
            tail --pid="${pane_pid}" -n +1 -f "${WAIT_TMUX_LOG}"
            exit 0
        fi
    fi

    # Open every cluster's ControlMaster while a terminal is still attached, so
    # a password prompt (if the key is rejected) has someone to answer it. The
    # detached daemon can then run key-only.
    for _cluster in "${CLUSTER_LIST[@]}"; do
        cluster_profile "${_cluster}"
        printf 'Establishing SSH connection to %s (will prompt for a password here if the key is rejected)...\n' "${remote}"
        {
            flock 9
            if ! ensure_ssh_master 1; then
                printf 'Could not establish an SSH connection to %s. Not starting a background session.\n' "${remote}" >&2
                exit 1
            fi
        } 9>"${SSH_CONTROL_PATH}.lock"
    done

    : > "${WAIT_TMUX_LOG}"
    # The daemon is launched through the per-cluster WRAPPER, not through this
    # generic file, so it re-derives CLUSTER_NAME (and with it the queue root,
    # socket and artifact names) instead of silently falling back to defaults.
    # Relaunch through the entry script with the same CLUSTER SET. SSH_CONTROL_PATH
    # and SESSION_MARKER/WAIT_QUEUE_DIR are deliberately NOT forwarded: they are
    # per-cluster and re-derived by cluster_profile() on every visit.
    printf -v wait_command \
        'cd %q && CLUSTERS=%q WAIT_ENTRY_SCRIPT=%q WAIT_TMUX=0 WAIT_HEADLESS=1 WAIT_TMUX_SESSION=%q SSH_AUTH_SOCK=%q REMOTE_USER=%q REMOTE_PROJECT=%q LOCAL_PROJECT=%q CONDA_SH=%q CONDA_ENV=%q LOCAL_CONDA_SH=%q LOCAL_CONDA_ENV=%q MAX_WAITING_JOBS=%q QUEUE_HELPER=%q POLL_SECONDS=%q stdbuf -oL -eL bash %q 2>&1 | tee -a %q' \
        "${LOCAL_PROJECT}" \
        "${CLUSTERS}" \
        "${ENTRY_SCRIPT}" \
        "${tmux_session}" \
        "${SSH_AUTH_SOCK:-}" \
        "${REMOTE_USER}" \
        "${REMOTE_PROJECT}" \
        "${LOCAL_PROJECT}" \
        "${CONDA_SH}" \
        "${CONDA_ENV}" \
        "${LOCAL_CONDA_SH}" \
        "${LOCAL_CONDA_ENV}" \
        "${MAX_WAITING_JOBS}" \
        "${QUEUE_HELPER}" \
        "${POLL_SECONDS}" \
        "${ENTRY_SCRIPT}" \
        "${WAIT_TMUX_LOG}"

    tmux new-session -d -s "${tmux_session}" "${wait_command}"
    printf 'Wait/sync started in tmux session: %s\n' "${tmux_session}"
    printf 'Streaming stats in this terminal from: %s\n' "${WAIT_TMUX_LOG}"
    printf 'Stop watching with Ctrl-c; tmux wait keeps running. Attach with: tmux attach -t %s\n' "${tmux_session}"
    pane_pid="$(tmux display-message -p -t "${tmux_session}" '#{pane_pid}')"
    tail --pid="${pane_pid}" -n +1 -f "${WAIT_TMUX_LOG}"
    exit 0
fi

# Record our PID so a later invocation that finds us already running (the
# reattach branch above) can send SIGUSR1 to force an immediate poll instead
# of the caller having to wait out the rest of POLL_SECONDS.
mkdir -p "${LOCAL_PROJECT}/script_logs"
printf '%s\n' "$$" > "${LOCAL_PROJECT}/script_logs/${WAIT_TMUX_SESSION}.pid"

# no-op handler: its only purpose is to make a blocking `wait` below return
# early when kicked, so the poll loop moves on without waiting out the rest
# of an in-progress sleep.
kick_requested=0
trap 'kick_requested=1' USR1

interruptible_sleep() {
    local seconds="$1"
    if (( kick_requested )); then
        kick_requested=0
        return
    fi
    sleep "${seconds}" &
    local sleep_pid=$!
    wait "${sleep_pid}" 2>/dev/null
    kick_requested=0
    kill "${sleep_pid}" 2>/dev/null || true
}

if ! command -v rsync >/dev/null 2>&1; then
    if [[ -f "${LOCAL_CONDA_SH}" ]]; then
        # shellcheck disable=SC1090
        source "${LOCAL_CONDA_SH}"
        conda activate "${LOCAL_CONDA_ENV}"
    fi
fi

if ! command -v rsync >/dev/null 2>&1; then
    printf 'rsync is not available. Tried local conda env: %s\n' \
        "${LOCAL_CONDA_ENV}" >&2
    exit 127
fi

allow_password=0
if [[ "${WAIT_HEADLESS}" != "1" && -t 1 ]]; then
    allow_password=1
fi
{
    flock 9
    if ! ensure_ssh_master "${allow_password}"; then
        printf 'Could not establish an SSH connection to %s.\n' "${remote}" >&2
        exit 1
    fi
} 9>"${SSH_CONTROL_PATH}.lock"

close_ssh_master() {
    rm -rf "${EVENT_CACHE}"
}
trap close_ssh_master EXIT

ssh_args=(-S "${SSH_CONTROL_PATH}" -o BatchMode=yes -o ConnectTimeout=20)
rsync_ssh="ssh -S ${SSH_CONTROL_PATH} -o BatchMode=yes -o ConnectTimeout=20"

discover_cluster_queue() {
    local active_queue pending_queues queues

    [[ -z "${WAIT_QUEUE_DIR}" ]] || return 0
    active_queue="${CLUSTER_QUEUE_ROOT}/active"
    if ssh "${ssh_args[@]}" "${remote}" \
        "[[ -f '${active_queue}/initialized' ]]"
    then
        WAIT_QUEUE_DIR="${active_queue}"
        note "Using active ${CLUSTER_NAME} queue: ${WAIT_QUEUE_DIR}"
        return
    fi
    pending_queues="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "for queue in '${CLUSTER_QUEUE_ROOT}'/*; do [[ -f \"\${queue}/initialized\" && -s \"\${queue}/pending.commands\" ]] && printf '%s %s\n' \"\$(stat -c %Y \"\${queue}/initialized\")\" \"\${queue}\"; done 2>/dev/null | sort -n | cut -d' ' -f2-" ||
            true
    )"
    if [[ -n "${pending_queues}" ]]; then
        WAIT_QUEUE_DIR="$(printf '%s\n' "${pending_queues}" | sed '/^$/d' | head -n 1)"
        printf 'Resuming oldest %s queue with pending jobs: %s\n' "${CLUSTER_NAME}" "${WAIT_QUEUE_DIR}"
        return
    fi

    queues="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "find '${CLUSTER_QUEUE_ROOT}' -mindepth 2 -maxdepth 2 -name initialized -printf '%T@ %h\n' 2>/dev/null | sort -n | cut -d' ' -f2-" ||
            true
    )"
    if [[ -n "${queues}" ]]; then
        WAIT_QUEUE_DIR="$(printf '%s\n' "${queues}" | sed '/^$/d' | head -n 1)"
        printf 'Resuming oldest %s queue: %s\n' "${CLUSTER_NAME}" "${WAIT_QUEUE_DIR}"
    fi
}

# Symmetric to discover_cluster_queue, for the session marker. Without it a
# daemon that has already finalised one batch (marker deleted, variable cleared)
# never tracks the NEXT batch: a later run_cluster.sh creates a fresh marker and
# this loop would keep polling with an empty one, so it would never clean up
# after that batch. Re-attempted every poll while no marker is tracked, and a
# no-op once one is.
discover_cluster_session() {
    local marker

    [[ -z "${SESSION_MARKER}" ]] || return 0
    marker="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "ls -1dt '${CLUSTER_SESSION_PREFIX}'* 2>/dev/null | head -n 1" ||
            true
    )"
    marker="$(printf '%s\n' "${marker}" | sed '/^$/d' | head -n 1)"
    if [[ -n "${marker}" ]]; then
        SESSION_MARKER="${marker}"
        note "Tracking ${CLUSTER_NAME} session: ${SESSION_MARKER}"
    fi
}

cluster_queue_pending_count() {
    if [[ -z "${WAIT_QUEUE_DIR}" ]]; then
        printf '0\n'
        return
    fi

    ssh "${ssh_args[@]}" "${remote}" \
        "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} bash '${QUEUE_HELPER}' count '${WAIT_QUEUE_DIR}'"
}

drain_cluster_queue() {
    [[ -n "${WAIT_QUEUE_DIR}" ]] || return 0

    if ! ssh "${ssh_args[@]}" "${remote}" \
        "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} bash '${QUEUE_HELPER}' drain '${WAIT_QUEUE_DIR}' '${REMOTE_USER}' '${MAX_WAITING_JOBS}'"
    then
        printf '%s queue: drain failed; will retry on the next poll.\n' "${CLUSTER_NAME}" >&2
    fi
}

sync_results() {
    # Each directory is tolerated independently: on a cluster that has not
    # produced results yet none of them exist remotely (they are outputs, so the
    # project sync excludes them). Without the per-directory `|| true` the first
    # missing one would abort the loop and silently skip the rest.
    #
    # models/ holds the --save_model checkpoints (models/<label>/<set>/seedN.pt)
    # needed locally for rho estimation.
    #
    # testmode_outputs/ is where a --testmode run redirects ALL of its artifacts
    # (see training/new_train.py: artifact_root). It is synced so smoke-test
    # results come back, and it is deliberately a sibling of test_metrics/ --
    # update_metrics_table scans only the project-root test_metrics/, so nothing
    # produced by a testmode run can ever reach metrics_summary.csv.
    # Ask once which of them exist rather than letting rsync fail per missing
    # directory: a cluster that has not produced results yet has none of them,
    # and rsync would print a change_dir/broken-pipe error for each, every poll.
    local existing
    existing="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "cd '${REMOTE_PROJECT}' 2>/dev/null && for d in run test_metrics models testmode_outputs; do [ -d \"\$d\" ] && printf '%s\n' \"\$d\"; done" \
            2>/dev/null || true
    )"
    [[ -n "${existing}" ]] || return 0

    local directory
    while IFS= read -r directory; do
        [[ -n "${directory}" ]] || continue
        mkdir -p "${LOCAL_PROJECT}/${directory}"
        rsync -a --quiet -e "${rsync_ssh}" \
            "${remote}:${REMOTE_PROJECT}/${directory}/" \
            "${LOCAL_PROJECT}/${directory}/" || true
    done <<< "${existing}"
}

sync_script_logs() {
    mkdir -p "${LOCAL_PROJECT}/script_logs"
    rsync -a --quiet -e "${rsync_ssh}" \
        "${remote}:${REMOTE_PROJECT}/script_logs/" \
        "${LOCAL_PROJECT}/script_logs/"
    # An empty .err is itself a result -- it is the evidence a job finished
    # without writing anything to stderr, which is exactly what a --testmode
    # smoke run is checked against. Pruning them used to hide that, so keep
    # them by default; set PRUNE_EMPTY_ERR=1 to restore the old cleanup.
    if [[ "${PRUNE_EMPTY_ERR:-0}" == "1" ]]; then
        find "${LOCAL_PROJECT}/script_logs" -type f -name '*.err' -empty -delete
    fi
}

sync_recent_tensorboard_events() {
    local event_files

    mkdir -p "${EVENT_CACHE}"
    # `run/` does not exist on a cluster that has not produced results yet (it
    # is an output directory, excluded from the project sync), so guard the
    # find instead of letting it print "No such file or directory" every poll.
    event_files="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "cd '${REMOTE_PROJECT}' && [ -d run ] && find run -type f -name 'events.out.tfevents.*' -mmin -${EVENT_LOOKBACK_MINUTES} -printf '%P\n' || true"
    )"
    [[ -n "${event_files}" ]] || return
    printf '%s\n' "${event_files}" |
        rsync -a --quiet --files-from=- -e "${rsync_ssh}" \
            "${remote}:${REMOTE_PROJECT}/run/" \
            "${EVENT_CACHE}/"
}

update_metrics_table() {
    # Full, deduped rescan of the LOCAL tree, which already holds every
    # cluster's synced results. Gating on files newer than a session marker
    # silently skips jobs that finished before the marker existed, so this
    # always rescans everything; add_new_metrics_to_table.py dedupes by source
    # key, making repeated runs cheap and self-healing.
    local python_bin="python3"
    if [[ -f "${LOCAL_CONDA_SH}" ]]; then
        # shellcheck disable=SC1090
        source "${LOCAL_CONDA_SH}" >/dev/null 2>&1 || true
        conda activate "${CONDA_ENV}" >/dev/null 2>&1 || true
        command -v python >/dev/null 2>&1 && python_bin="python"
    fi

    # Roots are passed explicitly rather than relying on the defaults, so it is
    # visible here that testmode_outputs/ is never scanned: a --testmode run
    # must not leave rows in metrics_summary.csv.
    # Report only when rows were actually added; "Added 0 ..." is the no-op
    # case and would print on every poll. Errors still come through on stderr.
    ( cd "${LOCAL_PROJECT}" && "${python_bin}" add_new_metrics_to_table.py \
        --metrics-root "${LOCAL_PROJECT}/test_metrics" \
        --run-root "${LOCAL_PROJECT}/run" \
        --table "${LOCAL_PROJECT}/metrics_summary.csv" ) \
        | grep -v '^Added 0 new metric rows' || true
}

print_next_waiting_start() {
    local estimate

    estimate="$(
        {
            ssh "${ssh_args[@]}" "${remote}" \
                "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" ||
                true
        } |
            python3 -c '
import datetime
import json
import sys
import time


def parse_time(value):
    try:
        timestamp = float(value)
    except (TypeError, ValueError):
        timestamp = None
    if timestamp is not None:
        return timestamp if timestamp > 0 else None
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).timestamp()
    except ValueError:
        return None


def job_records(value, inherited_id=None):
    if isinstance(value, dict):
        job_id = inherited_id
        for key in ("job_id", "jobId", "id", "Job_Id"):
            if key in value:
                job_id = value[key]
                break
        state = next(
            (
                value[key]
                for key in ("state", "job_state", "jobState")
                if key in value
            ),
            None,
        )
        if state is not None:
            yield job_id, value
        for key, item in value.items():
            child_id = key if str(key).isdigit() else job_id
            yield from job_records(item, child_id)
    elif isinstance(value, list):
        for item in value:
            yield from job_records(item, inherited_id)


try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    raise SystemExit

now = time.time()
candidates = []
for job_id, job in job_records(payload):
    state = str(
        next(
            (
                job[key]
                for key in ("state", "job_state", "jobState")
                if key in job
            ),
            "",
        )
    ).lower()
    if state not in {"w", "waiting", "tolaunch", "to_launch"}:
        continue
    start = next(
        (
            parse_time(job[key])
            for key in (
                "scheduledStart",
                "scheduled_start",
                "scheduled_start_time",
            )
            if key in job and parse_time(job[key]) is not None
        ),
        None,
    )
    if start is not None and start >= now - 60:
        candidates.append((start, str(job_id or "?")))

if candidates:
    start, job_id = min(candidates)
    print(job_id, round(start))
'
    )"

    if [[ ! "${estimate}" =~ ^[^[:space:]]+[[:space:]][0-9]+$ ]]; then
        # Routine while the queue is deep: OAR simply has no estimate yet.
        note "Next waiting job start: OAR has not scheduled one yet."
        return
    fi

    local job_id start_epoch now_epoch remaining
    read -r job_id start_epoch <<< "${estimate}"
    now_epoch="$(date +%s)"
    remaining=$((start_epoch - now_epoch))
    (( remaining < 0 )) && remaining=0

    printf 'Next waiting job: %s, scheduled start %s (in %dd %02dh %02dm %02ds).\n' \
        "${job_id}" \
        "$(date -d "@${start_epoch}" '+%Y-%m-%d %H:%M:%S %Z')" \
        "$((remaining / 86400))" \
        "$(((remaining % 86400) / 3600))" \
        "$(((remaining % 3600) / 60))" \
        "$((remaining % 60))"
}


# --- one cluster, one poll -------------------------------------------------
# Sets CLUSTER_IDLE[cluster]=1 when the cluster has neither active OAR jobs nor
# pending queued commands. Result syncing happens here; the metrics table is
# rebuilt once per round by the caller, from the merged local tree.
poll_cluster() {
    local cluster="$1"
    local job_table current_job_ids completed_job_ids previous_job_ids
    local active_jobs running_jobs waiting_jobs other_jobs pending_jobs

    cluster_profile "${cluster}" || return 1
    ssh_args=(-S "${SSH_CONTROL_PATH}" -o BatchMode=yes -o ConnectTimeout=20)
    rsync_ssh="ssh -S ${SSH_CONTROL_PATH} -o BatchMode=yes -o ConnectTimeout=20"

    # Restore this cluster's own state (the globals the helpers read).
    SESSION_MARKER="${CLUSTER_SESSION_MARKER[${cluster}]-}"
    WAIT_QUEUE_DIR="${CLUSTER_QUEUE_DIR[${cluster}]-}"
    previous_job_ids="${CLUSTER_PREVIOUS_JOB_IDS[${cluster}]-}"
    CLUSTER_IDLE["${cluster}"]=0
    ROUND_SYNCED=0

    printf '\n----- %s (%s) -----\n' "${cluster}" "${remote}"

    # The ControlMaster can silently die between polls (idle overnight, network
    # blip, cluster-side reset); reconnect key-only before touching it.
    if ! ensure_ssh_master 0; then
        printf 'Could not reconnect to %s; will retry next poll.\n' "${remote}" >&2
        return 0
    fi

    # Re-attempt discovery every poll while no queue is tracked: this daemon can
    # outlive the run_cluster.sh invocation that started it, so a queue created
    # later must still be picked up. It is a no-op once WAIT_QUEUE_DIR is set.
    discover_cluster_queue
    discover_cluster_session
    drain_cluster_queue

    if ! job_table="$(ssh "${ssh_args[@]}" "${remote}" "oarstat -u ${REMOTE_USER}")"; then
        printf 'OAR status check failed for %s; will retry next poll.\n' "${cluster}" >&2
        return 0
    fi

    current_job_ids="$(printf '%s\n' "${job_table}" | awk '$1 ~ /^[0-9]+$/ {print $1}' | sort -n)"
    read -r active_jobs running_jobs waiting_jobs other_jobs <<< "$(
        printf '%s\n' "${job_table}" |
            awk '
                $1 ~ /^[0-9]+$/ {
                    total++
                    if ($0 ~ /(^|[[:space:]])(R|Running)([[:space:]]|$)/) {
                        running++
                    } else if ($0 ~ /(^|[[:space:]])(W|Waiting)([[:space:]]|$)/) {
                        waiting++
                    } else {
                        other++
                    }
                }
                END { print total + 0, running + 0, waiting + 0, other + 0 }
            '
    )"
    pending_jobs="$(cluster_queue_pending_count)"

    # Stash this cluster's own counts, so the caller can print one row per
    # cluster at the end of the round (kept separate, not summed together).
    wait_progress_add_cluster_stats "${cluster}" \
        "${running_jobs}" "${waiting_jobs}" "${other_jobs}" \
        "${active_jobs}" "${pending_jobs}"

    if (( active_jobs > 0 )); then
        note "Current OAR jobs for ${REMOTE_USER}:"
        if [[ "${WAIT_VERBOSE}" == "1" ]]; then
            printf '%s\n' "${job_table}" | awk '$1 ~ /^[0-9]+$/ {print "  " $0}'
        fi
    else
        printf 'OAR jobs: total=0 for %s.\n' "${REMOTE_USER}"
    fi

    note "Synchronizing script logs."
    sync_script_logs || true
    sync_recent_tensorboard_events || true
    print_running_progress "${job_table}" || true

    completed_job_ids=
    if [[ -n "${previous_job_ids}" ]]; then
        completed_job_ids="$(
            comm -23 <(printf '%s\n' "${previous_job_ids}") \
                     <(printf '%s\n' "${current_job_ids}")
        )"
    fi
    [[ -n "${completed_job_ids}" ]] && printf 'Completed OAR job IDs:\n%s\n' "${completed_job_ids}"

    # Sync unconditionally whenever there was something to watch, rather than
    # gating on the completed-jobs diff: that diff only compares against the
    # previous poll, so one transient ssh failure would drop a batch of results
    # permanently. rsync is incremental, so redoing it is cheap and self-heals.
    if (( active_jobs > 0 )) || [[ -n "${completed_job_ids}" ]]; then
        note "Synchronizing results."
        sync_results || true
        ROUND_SYNCED=1
    fi

    if (( active_jobs == 0 && pending_jobs == 0 )); then
        CLUSTER_IDLE["${cluster}"]=1
        if [[ -n "${SESSION_MARKER}" || -n "${WAIT_QUEUE_DIR}" ]]; then
            printf 'All %s jobs completed. Synchronizing final results.\n' "${cluster}"
            sync_results || true
            ROUND_SYNCED=1
            # Only tear down the session this poll actually finished. A
            # run_cluster.sh submitting a NEW batch right now has already written
            # its own marker into the queue directory, and OAR may not list its
            # jobs yet -- deleting blindly would wipe a live session and leave
            # that batch untracked. The queue's own session_marker file is the
            # arbiter; a mismatch means the queue has moved on, so leave it and
            # adopt it on the next poll.
            local queue_marker=""
            if [[ -n "${WAIT_QUEUE_DIR}" ]]; then
                queue_marker="$(
                    ssh "${ssh_args[@]}" "${remote}" \
                        "cat '${WAIT_QUEUE_DIR}/session_marker' 2>/dev/null" || true
                )"
            fi
            if [[ -n "${queue_marker}" && -n "${SESSION_MARKER}" \
                  && "${queue_marker}" != "${SESSION_MARKER}" ]]; then
                printf '%s queue now belongs to session %s; keeping it.\n' \
                    "${CLUSTER_NAME}" "${queue_marker}"
                SESSION_MARKER=""
                WAIT_QUEUE_DIR=""
            else
                if [[ -n "${SESSION_MARKER}" ]]; then
                    ssh "${ssh_args[@]}" "${remote}" "rm -f '${SESSION_MARKER}'" || true
                    SESSION_MARKER=""
                fi
                if [[ -n "${WAIT_QUEUE_DIR}" ]]; then
                    ssh "${ssh_args[@]}" "${remote}" "rm -rf '${WAIT_QUEUE_DIR}'" || true
                    WAIT_QUEUE_DIR=""
                fi
            fi
        fi
        current_job_ids=
    else
        (( waiting_jobs > 0 )) && print_next_waiting_start
    fi

    CLUSTER_PREVIOUS_JOB_IDS["${cluster}"]="${current_job_ids}"
    CLUSTER_SESSION_MARKER["${cluster}"]="${SESSION_MARKER}"
    CLUSTER_QUEUE_DIR["${cluster}"]="${WAIT_QUEUE_DIR}"
    return 0
}

# Seed per-cluster state from the environment: run_cluster.sh hands off right
# after queuing, naming the cluster it just submitted to.
for _cluster in "${CLUSTER_LIST[@]}"; do
    CLUSTER_PREVIOUS_JOB_IDS["${_cluster}"]=""
    CLUSTER_SESSION_MARKER["${_cluster}"]=""
    CLUSTER_QUEUE_DIR["${_cluster}"]=""
    CLUSTER_IDLE["${_cluster}"]=0
done
if [[ -n "${HANDOFF_CLUSTER:-}" ]]; then
    CLUSTER_SESSION_MARKER["${HANDOFF_CLUSTER}"]="${SESSION_MARKER:-}"
    CLUSTER_QUEUE_DIR["${HANDOFF_CLUSTER}"]="${WAIT_QUEUE_DIR:-}"
fi

note "Watching clusters: ${CLUSTERS} (poll every ${POLL_SECONDS}s)"

while true; do
    round_synced=0
    wait_progress_reset_cluster_stats

    # Local jobs first: scripts/run_local.sh grids on this machine, alongside
    # bigfoot and kraken as a third source. Polled every round regardless of
    # what CLUSTERS names -- unlike the two below it costs one pgrep and a
    # file read, no SSH round trip, so there is no reason to gate it behind an
    # opt-in. Going first (both here and in the summary table below, since
    # wait_progress_add_cluster_stats just appends in call order) means the
    # jobs actually running ON this machine lead the output instead of being
    # buried after two SSH round trips' worth of cluster status. poll_local
    # (wait_progress_table.sh) reads script_logs/local_run.queue and
    # pid-tagged *_l<pid>.out files, both written by run_local.sh, never by
    # anything on a cluster, so this can never race or double-count against
    # poll_cluster's own results below -- three disjoint id namespaces over
    # one shared tree.
    ROUND_SYNCED=0
    poll_local || true
    (( ROUND_SYNCED )) && round_synced=1

    for _cluster in "${CLUSTER_LIST[@]}"; do
        ROUND_SYNCED=0
        poll_cluster "${_cluster}" || true
        (( ROUND_SYNCED )) && round_synced=1
    done

    # OAR job statistics, one row per cluster plus the local row, printed at
    # the end of the round -- always (even when everything is idle), after
    # every source has been visited, and kept separate per source.
    wait_progress_print_cluster_stats

    # One rebuild per round, from the merged local tree, so both clusters' (and
    # any local run's own) results land in the same table instead of
    # overwriting each other. The "Added N new metric rows" line it prints
    # comes right after the summary above, closing the round's output.
    if (( round_synced )); then
        note "Updating metrics table and feature contributions (merged, local)."
        update_metrics_table || true
    fi

    all_idle=1
    for _cluster in "${CLUSTER_LIST[@]}"; do
        (( CLUSTER_IDLE["${_cluster}"] )) || all_idle=0
    done
    (( LOCAL_IDLE )) || all_idle=0

    if (( all_idle )); then
        if [[ "${WAIT_HEADLESS}" == "1" ]]; then
            # The persistent daemon stays alive so a queue created by a later
            # run_cluster.sh call is picked up without restarting anything.
            note "All clusters and the local grid idle; daemon staying alive. Checking again in ${POLL_SECONDS}s."
            interruptible_sleep "${POLL_SECONDS}"
            continue
        fi
        printf '\nAll clusters and the local grid idle. Results synchronized to %s\n' "${LOCAL_PROJECT}"
        break
    fi

    note "Checking again in ${POLL_SECONDS} seconds."
    interruptible_sleep "${POLL_SECONDS}"
done
