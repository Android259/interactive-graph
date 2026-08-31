#!/usr/bin/env bash
# Stop running work, on either cluster or on this machine.
#
#   bash scripts/kill.sh --bigfoot          everything running on bigfoot
#   bash scripts/kill.sh --kraken           everything running on kraken
#   bash scripts/kill.sh --kraken_cpu       everything running on kraken-cpu
#   bash scripts/kill.sh --local            every local grid job on this machine
#   bash scripts/kill.sh <label>            that label everywhere: both clusters and here
#   bash scripts/kill.sh --kraken <label>   that label on kraken only
#   bash scripts/kill.sh --local --clean_logs   stop them and delete their logs
#
# Name a place and you stop everything there. Name a label and you stop that
# experiment wherever it happens to be running. Name both and you stop the
# narrower thing. Naming neither is refused -- "stop everything, everywhere"
# should have to be spelled out, and `--bigfoot --kraken --kraken_cpu --local`
# spells it.
#
# --clean_logs deletes the log files of the jobs this invocation stopped -- the
# job-tagged .out, the .log it points at, any .err beside it -- and then the
# directories those leave empty. Only jobs that were actually stopped here are
# touched; a killed job's logs are a stump of an epoch or two, and a rerun of the
# same label writes new files rather than reusing them. Off by default: a killed
# job's log is often exactly what one wants to read afterwards.
#
# The label is the config's name, which is also the run's --label and the stem of
# its arg_files/*.md. Which label a job belongs to is read off the directory it
# writes into (script_logs/<label>_seeds01234/...), not off the job name: a name
# reads "<label>_<group>_s<seed>" and both halves contain underscores, so by name
# alone `dropout01` cannot be told apart from `dropout01_extra`.
#
# On a cluster: cancel through OAR, wait for the jobs to actually stop, then pull
# script_logs/ back, so the logs of what was killed are here to read. Also clears
# that label's pending --graphics/--summarize report marker, if any -- otherwise
# wait_and_sync.sh keeps retrying (and failing) a report for jobs that no longer
# exist on every future idle round.
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
CLEAN_LOGS=0
while (( $# > 0 )); do
    case "$1" in
        --bigfoot) TARGETS+=("bigfoot"); shift ;;
        --kraken)  TARGETS+=("kraken"); shift ;;
        --kraken_cpu) TARGETS+=("kraken-cpu"); shift ;;
        --local)   TARGETS+=("local"); shift ;;
        --clean_logs) CLEAN_LOGS=1; shift ;;
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
    TARGETS=("bigfoot" "kraken" "kraken-cpu" "local")
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
        # --lipid_coldsplit names its output root <variant>_lipidsets instead of
        # <variant>_seeds01234, so without this a label given on the command line never
        # matched one of those runs and kill.sh reported "nothing to stop".
        top="${top%_lipidsets}"
        if [[ -n "${top}" && "${top}" != "${stdout_file}" ]]; then
            printf '%s\n' "${top}"
            return
        fi
    fi
    printf '%s\n' "${name}"
}

# Delete one stopped job's logs here: the job-tagged .out, whatever stable .log it
# symlinks to (the .out is the link and the .log the real file -- see the launchers),
# and an .err of the same stem if the cluster wrote one. The group and label
# directories go too once they are empty, so cleaning a whole label does not leave a
# tree of empty folders where a run used to be.
remove_job_logs() {
    local out_file="$1" target directory
    [[ -n "${out_file}" ]] || return 0
    if [[ -L "${out_file}" ]]; then
        target="$(dirname "${out_file}")/$(readlink "${out_file}")"
        [[ -e "${target}" ]] && rm -f -- "${target}" && printf '  removed %s\n' "${target#"${LOCAL_PROJECT}"/}"
    fi
    [[ -e "${out_file}" || -L "${out_file}" ]] || return 0
    rm -f -- "${out_file}" "${out_file%.out}.err"
    printf '  removed %s\n' "${out_file#"${LOCAL_PROJECT}"/}"
    directory="$(dirname "${out_file}")"
    # rmdir, never rm -r: a directory that still holds another job's logs must survive,
    # and a non-empty rmdir failing is the check that guarantees it.
    rmdir -- "${directory}" 2>/dev/null || return 0
    rmdir -- "$(dirname "${directory}")" 2>/dev/null || true
}

# Drop pending.commands lines (queued, never yet a real OAR job) that belong to
# the current TARGETS/LABEL scope. Runs against the raw command text: --name is
# always a plain word (OAR job names are restricted to a-zA-Z0-9_.-, so %q never
# quotes it) and the -O path is a plain word too, so both are grep -o'able even
# though the rest of the line is %q-escaped.
purge_pending_queue() {
    local cluster="$1"
    local pending_path="${CLUSTER_QUEUE_ROOT}/active/pending.commands"
    local pending_content line name stdout_file variant
    local kept="" removed=0

    pending_content="$(ssh "${ssh_args[@]}" "${remote}" "cat '${pending_path}' 2>/dev/null" || true)"
    [[ -n "${pending_content}" ]] || return 0

    while IFS= read -r line; do
        [[ -n "${line}" ]] || continue
        name="$(grep -oE -- '--name [^ ]+' <<< "${line}" | cut -d' ' -f2 || true)"
        stdout_file="$(grep -oE -- ' -O [^ ]+' <<< "${line}" | awk '{print $2}' || true)"
        variant="$(job_variant "${name}" "${stdout_file}")"
        if matches_label "${variant}"; then
            removed=$((removed + 1))
        else
            kept+="${line}"$'\n'
        fi
    done <<< "${pending_content}"

    (( removed > 0 )) || return 0
    printf 'Removing %d not-yet-submitted queued command(s) for %s from the queue on %s.\n' \
        "${removed}" "${LABEL:-everything}" "${cluster}"
    printf '%s' "${kept}" | ssh "${ssh_args[@]}" "${remote}" "cat > '${pending_path}'"
}

# Drop pending_reports/<label>.report[.claimed] markers for labels this
# invocation targets. launch/run_cluster.sh --graphics/--summarize drops one of
# these on the cluster before it starts waiting; wait_and_sync.sh's
# check_pending_reports() picks it up the next time it sees the cluster idle,
# runs generate_label_report.sh, and -- on ANY failure, deliberately, so a
# transient one does not lose the report -- restores the marker for the next
# round to retry. oardel above knows nothing of that marker, so a label killed
# on purpose left it behind forever: every later idle round keeps retrying a
# report for jobs that no longer exist, failing every time, which is exactly
# what was burning time in wait_and_sync's loop. Runs even when targets is
# empty -- a marker can outlive its jobs if they were already stopped before
# this invocation (by hand, or a previous kill.sh run before this fix).
purge_pending_reports() {
    local cluster="$1"
    local reports_dir="${CLUSTER_QUEUE_ROOT}/active/pending_reports"
    local listing marker base variant
    local to_remove=()

    listing="$(ssh "${ssh_args[@]}" "${remote}" \
        "ls '${reports_dir}/'*.report* 2>/dev/null" || true)"
    [[ -n "${listing}" ]] || return 0

    while IFS= read -r marker; do
        [[ -n "${marker}" ]] || continue
        base="$(basename "${marker}")"
        variant="${base%.report.claimed}"
        variant="${variant%.report}"
        matches_label "${variant}" && to_remove+=("${marker}")
    done <<< "${listing}"
    (( ${#to_remove[@]} > 0 )) || return 0

    printf 'Removing %d pending report marker(s) for %s on %s (their jobs were stopped).\n' \
        "${#to_remove[@]}" "${LABEL:-everything}" "${cluster}"
    local rm_script="" f
    for f in "${to_remove[@]}"; do
        rm_script+="rm -f -- $(printf '%q' "${f}"); "
    done
    ssh "${ssh_args[@]}" "${remote}" "${rm_script}" || \
        printf 'WARNING: could not clear pending report markers on %s.\n' "${cluster}" >&2
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
    local killed_out_files=()
    local killed_names=()
    while IFS=$'\t' read -r job_id name stdout_file; do
        [[ -n "${job_id}" ]] || continue
        variant="$(job_variant "${name}" "${stdout_file}")"
        if matches_label "${variant}"; then
            targets+="${job_id}"$'\n'
            printf '  %s  %s\n' "${job_id}" "${name:-<unnamed>}"
            [[ -n "${stdout_file}" ]] && killed_out_files+=("${stdout_file}")
            [[ -n "${name}" ]] && killed_names+=("${name}")
        fi
    done <<< "${jobs}"
    targets="${targets%$'\n'}"

    # oardel below only touches jobs oarstat already knows about. A command that
    # never even reached a real OAR job (e.g. oarsub itself failed, as with an
    # oversized argument list) sits only in pending.commands, invisible to the
    # loop above, and survives a kill forever unless purged here too -- the same
    # job_variant()/matches_label() rule applied to each pending line's own -O
    # path instead of oarstat's JSON, since a not-yet-submitted line already
    # carries that path (only %jobid% is still unresolved, and label detection
    # never looks at the id).
    purge_pending_queue "${cluster}"
    purge_pending_reports "${cluster}"

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

    # oardel stops the job but knows nothing of scripts/cluster/cluster_queue_remote.sh's
    # own bookkeeping: capture_queue's oarsub() shadow dedupes a future submission
    # against the EXACT command text already sitting in pending.commands/
    # submitted.commands, and a killed job's command is still there, still reading as
    # "already queued" -- so without this, resubmitting the same grid after a kill is
    # silently skipped, one line per killed job, with no error. Purge by --name, the
    # one token every stored command line carries that this job's oarstat row also
    # gives directly.
    if (( ${#killed_names[@]} > 0 )); then
        printf 'Clearing these jobs'"'"' commands from the queue on %s (so a resubmit is not skipped as already-queued).\n' "${cluster}"
        local purge_script="" kname
        for kname in "${killed_names[@]}"; do
            purge_script+="name=$(printf '%q' "${kname}"); "
            purge_script+='for f in '"$(printf '%q' "${CLUSTER_QUEUE_ROOT}/active/pending.commands")"' '"$(printf '%q' "${CLUSTER_QUEUE_ROOT}/active/submitted.commands")"'; do '
            purge_script+='[ -f "$f" ] || continue; '
            purge_script+='grep -v -F -- "--name $name " "$f" > "$f.kill_tmp"; mv "$f.kill_tmp" "$f"; '
            purge_script+='done; '
        done
        ssh "${ssh_args[@]}" "${remote}" "${purge_script}" || \
            printf 'WARNING: could not clear the queue on %s; a resubmit may still be skipped as already-queued.\n' "${cluster}" >&2
    fi

    # Remote first, then the sync, then the copies here: deleting only this side would
    # be undone by the very next rsync, which mirrors the cluster's script_logs into it.
    if (( CLEAN_LOGS )) && (( ${#killed_out_files[@]} > 0 )); then
        printf 'Removing the stopped jobs'"'"' logs on %s.\n' "${cluster}"
        local remote_script="" remote_out
        for remote_out in "${killed_out_files[@]}"; do
            remote_script+="out=$(printf '%q' "${remote_out}"); "
            remote_script+='if [ -L "$out" ]; then rm -f -- "$(dirname "$out")/$(readlink "$out")"; fi; '
            remote_script+='rm -f -- "$out" "${out%.out}.err"; '
            remote_script+='rmdir -- "$(dirname "$out")" 2>/dev/null || true; '
        done
        ssh "${ssh_args[@]}" "${remote}" "${remote_script}" || true
    fi

    printf 'Synchronizing script logs.\n'
    mkdir -p "${LOCAL_PROJECT}/script_logs"
    rsync -a --quiet -e "${rsync_ssh}" \
        "${remote}:${REMOTE_PROJECT}/script_logs/" \
        "${LOCAL_PROJECT}/script_logs/" || true
    if (( CLEAN_LOGS )) && (( ${#killed_out_files[@]} > 0 )); then
        # The same paths under this project root: rsync above copies without --delete,
        # so a file pulled here by an earlier sync outlives its removal on the cluster.
        local local_out
        for remote_out in "${killed_out_files[@]}"; do
            local_out="${LOCAL_PROJECT}/${remote_out#"${REMOTE_PROJECT}"/}"
            [[ "${local_out}" != "${LOCAL_PROJECT}/${remote_out}" ]] || continue
            remove_job_logs "${local_out}"
        done
        printf 'Stopped; their logs were deleted here and on %s.\n' "${cluster}"
        return 0
    fi
    printf 'Stopped; logs are in %s/script_logs\n' "${LOCAL_PROJECT}"
}

# --- this machine ---------------------------------------------------------------
kill_local() {
    local out_files pid out variant driver_pids stopped=0
    local killed_out_files=()

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
            killed_out_files+=("${out}")
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
    if (( CLEAN_LOGS )) && (( ${#killed_out_files[@]} > 0 )); then
        # After the kills, not between them: a training process holds its log open, and
        # unlinking it while the rest are still being signalled would only make the last
        # writes disappear into a file with no name.
        for out in "${killed_out_files[@]}"; do
            remove_job_logs "${out}"
        done
    fi
    if (( CLEAN_LOGS )); then
        printf 'Stopped %d local process(es); their logs were deleted.\n' "${stopped}"
    else
        printf 'Stopped %d local process(es). Logs are already in %s/script_logs\n' \
            "${stopped}" "${LOCAL_PROJECT}"
    fi
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
