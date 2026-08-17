#!/usr/bin/env bash
# Stop running work, on either cluster or on this machine.
#
#   bash scripts/kill.sh --bigfoot          everything running on bigfoot
#   bash scripts/kill.sh --kraken           everything running on kraken
#   bash scripts/kill.sh --local            every local grid job on this machine
#   bash scripts/kill.sh <label>            that label everywhere: both clusters and here
#   bash scripts/kill.sh --kraken <label>   that label on kraken only
#
# Name a place and you stop everything there. Name a label and you stop that
# experiment wherever it happens to be running. Name both and you stop the
# narrower thing. Naming neither is refused -- "stop everything, everywhere"
# should have to be spelled out, and `--bigfoot --kraken --local` spells it.
#
# The label is the config's name, which is also the run's --label and the stem of
# its arg_files/*.md. Which label a job belongs to is read off the directory it
# writes into (script_logs/<label>_seeds01234/...), not off the job name: a name
# reads "<label>_<group>_s<seed>" and both halves contain underscores, so by name
# alone `dropout01` cannot be told apart from `dropout01_extra`.
#
# On a cluster: cancel through OAR, wait for the jobs to actually stop, then pull
# script_logs/ back, so the logs of what was killed are here to read.
# Locally: stop the training processes and the run_local.sh that launched them --
# without that second part it would simply start the next queued job.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=scripts/lib/cluster_common.sh
source "${SCRIPT_DIR}/lib/cluster_common.sh"
# shellcheck source=scripts/lib/ssh_master_lib.sh
source "${SCRIPT_DIR}/lib/ssh_master_lib.sh"

LOCAL_PROJECT="${LOCAL_PROJECT:-${PROJECT_ROOT}}"
POLL_SECONDS="${POLL_SECONDS:-5}"
LOCAL_JOB_TAG="l"
LOCAL_QUEUE_FILE="${LOCAL_PROJECT}/script_logs/local_run.queue"

usage() {
    awk 'NR == 1 { next } !/^#/ { exit } { sub(/^# ?/, ""); print }' "${BASH_SOURCE[0]}" >&2
}

TARGETS=()
LABEL=""
while (( $# > 0 )); do
    case "$1" in
        --bigfoot) TARGETS+=("bigfoot"); shift ;;
        --kraken)  TARGETS+=("kraken"); shift ;;
        --local)   TARGETS+=("local"); shift ;;
        -h|--help) usage; exit 0 ;;
        -*)        printf 'Unknown option: %s\n' "$1" >&2; usage; exit 2 ;;
        *)
            if [[ -n "${LABEL}" ]]; then
                printf 'Only one label may be given (got %s and %s).\n' "${LABEL}" "$1" >&2
                exit 2
            fi
            LABEL="$1"; shift
            ;;
    esac
done

if (( ${#TARGETS[@]} == 0 )); then
    if [[ -z "${LABEL}" ]]; then
        printf 'Name a place, a label, or both.\n\n' >&2
        usage
        exit 2
    fi
    # A label with no place: wherever that experiment is running.
    TARGETS=("bigfoot" "kraken" "local")
fi

# Does a variant belong to the requested label? Empty label matches everything,
# which is what "stop everything here" means.
matches_label() {
    [[ -z "${LABEL}" || "$1" == "${LABEL}" ]]
}

# The label a cluster job belongs to, from the directory it writes into:
#   script_logs/<label>_seeds01234/<group>/<label>_seed<N>_<tag><id>.out
#   script_logs/<label>_coldval_seeds01234/<group>/...
# Falls back to the job name when OAR reports no output path -- there the label
# cannot be separated from the group, so such a job is matched loosely and said
# to be matched loosely.
job_variant() {
    local name="$1" stdout_file="$2" top
    if [[ -n "${stdout_file}" ]]; then
        top="${stdout_file#*script_logs/}"
        top="${top%%/*}"
        top="${top%_seeds[0-9]*}"
        top="${top%_coldval}"
        if [[ -n "${top}" && "${top}" != "${stdout_file}" ]]; then
            printf '%s\n' "${top}"
            return
        fi
    fi
    printf '%s\n' "${name}"
}

# --- one cluster ---------------------------------------------------------------
kill_cluster() {
    local cluster="$1"
    local jobs targets job_id name still

    cluster_profile "${cluster}" || return 1
    printf '\n----- %s (%s) -----\n' "${cluster}" "${remote}"
    if ! ensure_ssh_master 1; then
        printf 'Could not connect to %s; skipped.\n' "${remote}" >&2
        return 1
    fi
    ssh_set_transport

    # id, name and output path for every job of this user, in one round trip.
    # scripts/lib/oarstat_json.py is the same reader the watcher uses, so the two
    # cannot disagree about what OAR said.
    jobs="$(
        { ssh "${ssh_args[@]}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" || true; } |
            python3 "${SCRIPT_DIR}/lib/oarstat_json.py" jobs
    )"

    targets=""
    local stdout_file variant
    while IFS=$'\t' read -r job_id name stdout_file; do
        [[ -n "${job_id}" ]] || continue
        variant="$(job_variant "${name}" "${stdout_file}")"
        if matches_label "${variant}"; then
            targets+="${job_id}"$'\n'
            printf '  %s  %s\n' "${job_id}" "${name:-<unnamed>}"
        fi
    done <<< "${jobs}"
    targets="${targets%$'\n'}"

    if [[ -z "${targets}" ]]; then
        printf 'Nothing to stop%s.\n' "${LABEL:+ for label ${LABEL}}"
        return 0
    fi

    # Unquoted on purpose: oardel takes the ids as separate arguments.
    # shellcheck disable=SC2086
    ssh "${ssh_args[@]}" "${remote}" oardel ${targets}

    while true; do
        still="$(
            ssh "${ssh_args[@]}" "${remote}" "oarstat -u '${REMOTE_USER}'" |
                awk '$1 ~ /^[0-9]+$/ {print $1}' |
                sort | comm -12 - <(printf '%s\n' "${targets}" | sort) | wc -l
        )"
        (( still > 0 )) || break
        printf 'Waiting for %d job(s) to stop.\n' "${still}"
        sleep "${POLL_SECONDS}"
    done

    printf 'Synchronizing script logs.\n'
    mkdir -p "${LOCAL_PROJECT}/script_logs"
    rsync -a --quiet -e "${rsync_ssh}" \
        "${remote}:${REMOTE_PROJECT}/script_logs/" \
        "${LOCAL_PROJECT}/script_logs/" || true
    printf 'Stopped; logs are in %s/script_logs\n' "${LOCAL_PROJECT}"
}

# --- this machine ---------------------------------------------------------------
kill_local() {
    local out_files pid out variant driver_pids stopped=0

    printf '\n----- local -----\n'

    # A grid job is a training process that owns a pid-tagged .out file, the same
    # thing the progress table counts. A hand-started training run has no such
    # file and is therefore left alone.
    out_files="$(
        find "${LOCAL_PROJECT}/script_logs" \( -type f -o -type l \) \
            -name "*_${LOCAL_JOB_TAG}*.out" 2>/dev/null || true
    )"

    for pid in $(pgrep -f 'training/new_train\.py' 2>/dev/null || true); do
        out="$(grep -E "_${LOCAL_JOB_TAG}${pid}\.out\$" <<< "${out_files}" | head -n 1 || true)"
        [[ -n "${out}" ]] || continue
        # ".../<variant>_seed<N>_l<pid>.out" -> variant
        variant="$(basename "${out}")"
        variant="${variant%_${LOCAL_JOB_TAG}${pid}.out}"
        variant="${variant%_seed*}"
        if matches_label "${variant}"; then
            printf '  %s  %s\n' "${pid}" "${variant}"
            kill "${pid}" 2>/dev/null || true
            stopped=$((stopped + 1))
        fi
    done

    # The grid driver, otherwise it just launches the next queued job. Its own
    # variant is the first field of the queue file it maintains; with no queue
    # file left there is nothing to launch and nothing to stop.
    driver_pids="$(pgrep -f 'scripts/run_local\.sh' 2>/dev/null || true)"
    if [[ -n "${driver_pids}" ]]; then
        variant=""
        [[ -s "${LOCAL_QUEUE_FILE}" ]] && variant="$(head -n 1 "${LOCAL_QUEUE_FILE}" | cut -f1)"
        # With a label but no queue file there is nothing to check the driver
        # against, and killing it on a guess would stop a grid the caller never
        # named. Only "stop everything local" may kill an unidentified driver.
        if [[ -z "${LABEL}" ]] || { [[ -n "${variant}" ]] && matches_label "${variant}"; }; then
            printf '  run_local.sh (%s)\n' "${variant:-no queue}"
            # shellcheck disable=SC2086
            kill ${driver_pids} 2>/dev/null || true
            rm -f "${LOCAL_QUEUE_FILE}"
            stopped=$((stopped + 1))
        fi
    fi

    if (( stopped == 0 )); then
        printf 'Nothing to stop%s.\n' "${LABEL:+ for label ${LABEL}}"
        return 0
    fi
    printf 'Stopped %d local process(es). Logs are already in %s/script_logs\n' \
        "${stopped}" "${LOCAL_PROJECT}"
    if [[ -s "${LOCAL_PROJECT}/script_logs/local_run_pending_batches" ]]; then
        printf 'Note: %d whole run(s) are still queued behind this one in %s.\n' \
            "$(wc -l < "${LOCAL_PROJECT}/script_logs/local_run_pending_batches")" \
            "script_logs/local_run_pending_batches"
    fi
}

for target in "${TARGETS[@]}"; do
    case "${target}" in
        local) kill_local || true ;;
        *)     kill_cluster "${target}" || true ;;
    esac
done
