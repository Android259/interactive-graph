#!/usr/bin/env bash
set -euo pipefail

# Runs on the cluster frontend, standalone (invoked over ssh), so it takes
# its label from the environment rather than sourcing cluster_common.sh.
CLUSTER_LABEL="${CLUSTER_LABEL:-${CLUSTER_NAME:-Cluster}}"

usage() {
    printf 'Usage: %s capture|drain|count QUEUE_DIR [...]\n' "${0##*/}" >&2
    exit 2
}

quote_oarsub_command() {
    local command="oarsub"
    local quoted

    for argument in "$@"; do
        printf -v quoted ' %q' "${argument}"
        command+="${quoted}"
    done

    printf '%s\n' "${command}"
}

capture_queue() {
    local queue_dir="$1"
    local submit_script="$2"
    local session_marker="$3"
    local submit_args="${4:-}"
    local pending_file="${queue_dir}/pending.commands"
    local submitted_file="${queue_dir}/submitted.commands"
    local before_count

    mkdir -p "${queue_dir}"
    before_count=0
    if [[ -f "${pending_file}" ]]; then
        before_count="$(wc -l < "${pending_file}")"
    fi
    touch "${pending_file}" "${submitted_file}"
    printf '%s\n' "${submit_script}" > "${queue_dir}/submit_script"
    printf '%s\n' "${session_marker}" > "${queue_dir}/session_marker"

    oarsub() {
        local quoted
        quoted="$(quote_oarsub_command "$@")"
        if grep -qxF "${quoted}" "${QUEUE_PENDING}" "${QUEUE_SUBMITTED}" 2>/dev/null; then
            printf 'Skipping already-queued job: %s\n' "${quoted}" >&2
            return 0
        fi
        printf '%s\n' "${quoted}" >> "${QUEUE_PENDING}"
    }

    export QUEUE_PENDING="${pending_file}"
    export QUEUE_SUBMITTED="${submitted_file}"
    export -f quote_oarsub_command
    export -f oarsub

    if [[ -n "${submit_args}" ]]; then
        bash "${submit_script}" "${submit_args}"
    else
        bash "${submit_script}"
    fi
    touch "${queue_dir}/initialized"

    printf 'Queued %d new OAR jobs in %s; pending total=%d.\n' \
        "$(( $(wc -l < "${pending_file}") - before_count ))" \
        "${pending_file}" \
        "$(wc -l < "${pending_file}")"
}

count_active_jobs() {
    local remote_user="$1"

    oarstat -u "${remote_user}" |
        awk '$1 ~ /^[0-9]+$/ {count++} END {print count + 0}'
}

count_waiting_jobs() {
    local remote_user="$1"

    oarstat -u "${remote_user}" |
        awk '$1 ~ /^[0-9]+$/ && $4 == "Waiting" {count++} END {print count + 0}'
}

drain_queue() {
    local queue_dir="$1"
    local remote_user="$2"
    local max_waiting_jobs="$3"
    local pending_file="${queue_dir}/pending.commands"
    local submitted_file="${queue_dir}/submitted.commands"
    local lock_file="${queue_dir}/drain.lock"
    local waiting_jobs slots submitted line
    local tmp_file

    [[ -f "${pending_file}" ]] || return
    mkdir -p "${queue_dir}"

    exec 8>"${lock_file}"
    flock 8

    waiting_jobs="$(count_waiting_jobs "${remote_user}")"
    if (( waiting_jobs < 0 )); then
        waiting_jobs=0
    fi
    slots=$((max_waiting_jobs - waiting_jobs))
    if (( slots <= 0 )); then
        printf '%s queue: waiting=%d max_waiting=%d pending=%d, no free waiting slots.\n' \
            "${CLUSTER_LABEL}" "${waiting_jobs}" "${max_waiting_jobs}" \
            "$(wc -l < "${pending_file}")"
        return
    fi

    tmp_file="$(mktemp "${queue_dir}/pending.XXXXXX")"
    submitted=0
    while IFS= read -r line; do
        if (( submitted < slots )); then
            if eval "${line}"; then
                printf '%s\n' "${line}" >> "${submitted_file}"
                submitted=$((submitted + 1))
            else
                printf '%s\n' "${line}" >> "${tmp_file}"
                cat >> "${tmp_file}"
                mv "${tmp_file}" "${pending_file}"
                printf '%s queue: oarsub failed; kept remaining commands in %s.\n' \
                    "${CLUSTER_LABEL}" "${pending_file}" >&2
                return 1
            fi
        else
            printf '%s\n' "${line}" >> "${tmp_file}"
        fi
    done < "${pending_file}"

    mv "${tmp_file}" "${pending_file}"
    printf '%s queue: submitted=%d waiting_before=%d max_waiting=%d pending=%d.\n' \
        "${CLUSTER_LABEL}" "${submitted}" "${waiting_jobs}" "${max_waiting_jobs}" \
        "$(wc -l < "${pending_file}")"
}

count_pending() {
    local queue_dir="$1"
    local pending_file="${queue_dir}/pending.commands"

    if [[ -f "${pending_file}" ]]; then
        wc -l < "${pending_file}"
    else
        printf '0\n'
    fi
}

command="${1:-}"
case "${command}" in
    capture)
        (( $# == 4 || $# == 5 )) || usage
        capture_queue "$2" "$3" "$4" "${5:-}"
        ;;
    drain)
        (( $# == 4 )) || usage
        drain_queue "$2" "$3" "$4"
        ;;
    count)
        (( $# == 2 )) || usage
        count_pending "$2"
        ;;
    *)
        usage
        ;;
esac
