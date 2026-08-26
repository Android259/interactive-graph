#!/usr/bin/env bash
# Watch several clusters from ONE foreground loop: print statistics immediately,
# then every POLL_SECONDS (default 60) pull each cluster's logs / TensorBoard
# events / results and rebuild the metrics table once from the merged local tree.
#
#   bash scripts/wait_and_sync.sh                  # bigfoot, kraken, kraken-cpu, repeat
#   CLUSTERS=kraken bash scripts/wait_and_sync.sh  # one cluster only
#   bash scripts/wait_and_sync.sh --once           # a single round, then exit
#
# This is a VIEWER. Start it when you want to look, Ctrl-C when you are done;
# stopping it stops nothing, because nothing it does is load-bearing for the
# jobs.
#
# What keeps jobs flowing is a crontab entry on each frontend, which this
# installs on its first round: scripts/cluster/cluster_drain_cron.sh submits from
# the queue as waiting slots free up, so jobs keep going out no matter which
# computer queued them, which is watching, or whether either is switched on. If
# the crontab cannot be installed it says so loudly and drains from this loop
# instead, as a fallback rather than as the design.
#
# It is purely observational on the cluster side: it never deletes a remote queue
# or session marker, because the computer that happens to be watching must not be
# able to destroy state belonging to a batch queued from the other one.
#
# Building the metrics table locally (rather than on each cluster) is what makes
# multi-cluster watching correct: run/, test_metrics/ and script_logs/ from every
# cluster rsync into the same local tree, so one local rescan sees the union.
set -euo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_PROJECT="${LOCAL_PROJECT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

CLUSTERS="${CLUSTERS:-bigfoot kraken kraken-cpu}"
read -r -a CLUSTER_LIST <<< "${CLUSTERS}"
(( ${#CLUSTER_LIST[@]} > 0 )) || { printf 'CLUSTERS is empty.\n' >&2; exit 2; }

# cluster_common.sh derives every cluster-dependent global from CLUSTER_NAME;
# cluster_profile() re-derives them on each switch inside the poll loop.
# shellcheck source=scripts/lib/cluster_common.sh
CLUSTER_NAME="${CLUSTER_LIST[0]}"
source "${SCRIPT_DIR}/lib/cluster_common.sh"

# print_running_progress() and the log/TensorBoard readers behind it, shared
# with scripts/wait_and_sync_local.sh so the cluster and local views cannot drift.
# shellcheck source=scripts/lib/progress_table.sh
source "${SCRIPT_DIR}/lib/progress_table.sh"

# Routine chatter is hidden: a healthy round reports only what changed. Anything
# abnormal (failed reconnect, failed drain, missing drainer, rsync/OAR errors)
# prints unconditionally. WAIT_VERBOSE=1 restores the full narration.
WAIT_VERBOSE="${WAIT_VERBOSE:-0}"

# Cluster-side drainer.
REMOTE_DRAIN="${REMOTE_DRAIN:-1}"
DRAIN_CRON_SPEC="${DRAIN_CRON_SPEC:-*/5 * * * *}"
DRAIN_SCRIPT="${DRAIN_SCRIPT:-scripts/cluster/cluster_drain_cron.sh}"
# Renames a finished queue to done_<timestamp> so the next batch starts clean
# (a queue deduplicates against its own submitted.commands, so re-running an
# identical config into a used queue would be skipped). Off by default: it is
# the one thing here that changes remote state, and a stale queue is harmless.
ARCHIVE_IDLE_QUEUES="${ARCHIVE_IDLE_QUEUES:-0}"

RUN_ONCE=0
while (( $# > 0 )); do
    case "$1" in
        --once)             RUN_ONCE=1 ;;
        --verbose)          WAIT_VERBOSE=1 ;;
        --no-remote-drain)  REMOTE_DRAIN=0 ;;
        --uninstall-drain)  REMOTE_DRAIN=uninstall ;;
        --archive-idle-queues) ARCHIVE_IDLE_QUEUES=1 ;;
        --interval=*)       POLL_SECONDS="${1#*=}" ;;
        -h|--help)
            # The header comment, however long it happens to be: stop at the
            # first line that is not a comment rather than at a line number,
            # which silently starts printing code as soon as the header changes.
            awk 'NR == 1 { next } !/^#/ { exit } { sub(/^# ?/, ""); print }' \
                "${BASH_SOURCE[0]}"
            exit 0
            ;;
        *)
            printf 'Unknown option: %s (see --help)\n' "$1" >&2
            exit 2
            ;;
    esac
    shift
done

note() { [[ "${WAIT_VERBOSE}" == "1" ]] && printf '%s\n' "$*" || true; }

# Per-cluster state for the current round. Nothing survives a restart on
# purpose: every value here is re-read from the cluster each round, so this
# script has no state of its own to get out of sync.
declare -A CLUSTER_DRAINER_OK=()

# Every source this round visits, local jobs first: they cost one pgrep and a
# file read rather than an SSH round trip, so they are never gated behind
# CLUSTERS, and going first puts the jobs running ON this machine at the top of
# the output instead of behind two clusters' worth of network waiting.
SOURCES=("local" "${CLUSTER_LIST[@]}")

# SOURCE_IDLE is declared by lib/progress_table.sh and keyed by source name, so
# "local" is an entry like any cluster instead of a variable of its own.
for _source in "${SOURCES[@]}"; do
    SOURCE_IDLE["${_source}"]=0
done
for _cluster in "${CLUSTER_LIST[@]}"; do
    CLUSTER_DRAINER_OK["${_cluster}"]=0
done

cleanup() {
    rm -rf "$(wait_progress_event_cache_path)"
}
trap cleanup EXIT

# --- local tools ----------------------------------------------------------
# This project runs from two computers whose local layouts differ: different
# conda install prefix, different env names, and a base interpreter that may or
# may not carry tensorboard/pandas. cluster_common.sh pins one machine's answers
# (LOCAL_CONDA_SH=/opt/anaconda3/..., LOCAL_CONDA_ENV=rsync-env), which on the
# other machine means the conda fallback quietly does nothing and every step
# falls back to whatever `python3` happens to be. So look in the usual places
# and probe for an interpreter that can actually import what each step needs.
#
# Nothing below is cluster state -- it is purely about this computer, so the two
# machines never have to agree on any of it.
conda_prefixes() {
    local candidate conda_exe="${CONDA_EXE:-}"
    for candidate in \
        "${LOCAL_CONDA_SH%/etc/profile.d/conda.sh}" \
        "${CONDA_PREFIX:-}" \
        "${conda_exe%/bin/conda}" \
        "${HOME}/miniconda3" "${HOME}/anaconda3" "${HOME}/miniforge3" \
        /opt/anaconda3 /opt/miniconda3 /opt/miniforge3
    do
        [[ -n "${candidate}" && -d "${candidate}" ]] && printf '%s\n' "${candidate}"
    done
    return 0
}

ensure_rsync() {
    command -v rsync >/dev/null 2>&1 && return 0
    local prefix env_name
    while IFS= read -r prefix; do
        [[ -f "${prefix}/etc/profile.d/conda.sh" ]] || continue
        for env_name in "${LOCAL_CONDA_ENV}" "${CONDA_ENV}"; do
            # shellcheck disable=SC1090
            source "${prefix}/etc/profile.d/conda.sh" >/dev/null 2>&1 || continue
            conda activate "${env_name}" >/dev/null 2>&1 || continue
            command -v rsync >/dev/null 2>&1 && return 0
            conda deactivate >/dev/null 2>&1 || true
        done
    done < <(conda_prefixes)
    return 1
}

if ! ensure_rsync; then
    printf 'rsync is not available, and no conda env provided it.\n' >&2
    printf 'Looked for envs %s / %s under: %s\n' \
        "${LOCAL_CONDA_ENV}" "${CONDA_ENV}" "$(conda_prefixes | tr '\n' ' ')" >&2
    printf 'Set LOCAL_CONDA_SH and LOCAL_CONDA_ENV for this computer, or install rsync.\n' >&2
    exit 127
fi

# First interpreter that can import the named module, or failure. Cached, since
# each probe costs an interpreter start-up and the answer cannot change mid-run.
declare -A PYTHON_FOR=()
python_for() {
    local module="$1"
    if [[ -z "${PYTHON_FOR[${module}]-}" ]]; then
        local candidate prefix env_name found=""
        local -a candidates=()
        command -v python3 >/dev/null 2>&1 && candidates+=("$(command -v python3)")
        command -v python >/dev/null 2>&1 && candidates+=("$(command -v python)")
        while IFS= read -r prefix; do
            for env_name in "${CONDA_ENV}" "${LOCAL_CONDA_ENV}"; do
                candidates+=("${prefix}/envs/${env_name}/bin/python")
            done
            candidates+=("${prefix}/bin/python3")
        done < <(conda_prefixes)
        candidates+=("${HOME}/.conda/envs/${CONDA_ENV}/bin/python")
        for candidate in "${candidates[@]}"; do
            [[ -x "${candidate}" ]] || continue
            # From LOCAL_PROJECT: the metrics module is imported by package path.
            if ( cd "${LOCAL_PROJECT}" && "${candidate}" -c "import ${module}" ) \
                >/dev/null 2>&1
            then
                found="${candidate}"
                break
            fi
        done
        PYTHON_FOR["${module}"]="${found:-none}"
    fi
    [[ "${PYTHON_FOR[${module}]}" == "none" ]] && return 1
    printf '%s\n' "${PYTHON_FOR[${module}]}"
}

# --- ssh ------------------------------------------------------------------
# One shared connection per cluster, from scripts/lib/ssh_master_lib.sh. This script
# always has a terminal, so a password prompt has someone to answer it.
# shellcheck source=scripts/lib/ssh_master_lib.sh
source "${SCRIPT_DIR}/lib/ssh_master_lib.sh"

# Set by cluster_profile() for the cluster currently being visited.
ssh_args=()
rsync_ssh=""
set_transport() { ssh_set_transport; }

# --- cluster-side drainer -------------------------------------------------
drain_marker() { printf '# dl_project_drain:%s' "$1"; }

# Rewrites our own crontab line and leaves every other entry alone. Prints how
# many of our lines the crontab holds afterwards, which is how the caller tells
# success from a cluster that refuses crontabs.
install_remote_drainer() {
    local cluster="$1"
    local marker cron_line installed

    marker="$(drain_marker "${cluster}")"
    printf -v cron_line \
        '%s flock -n %q %s %q/%s >/dev/null 2>&1 %s' \
        "${DRAIN_CRON_SPEC}" \
        "${CLUSTER_QUEUE_ROOT}/.cron.lock" \
        "env CLUSTER_NAME=$(printf '%q' "${cluster}") REMOTE_USER=$(printf '%q' "${REMOTE_USER}") MAX_WAITING_JOBS=$(printf '%q' "${MAX_WAITING_JOBS}") bash" \
        "${REMOTE_PROJECT}" "${DRAIN_SCRIPT}" \
        "${marker}"

    installed="$(
        printf '%s\n' "${cron_line}" |
            ssh "${ssh_args[@]}" "${remote}" \
                "mkdir -p '${CLUSTER_QUEUE_ROOT}' && bash -c '
                    marker=\"\$1\"
                    { crontab -l 2>/dev/null | grep -vF \"\${marker}\" || true; cat; } |
                        crontab -
                    crontab -l 2>/dev/null | grep -cF \"\${marker}\" || true
                ' _ $(printf '%q' "${marker}")"
    )" || return 1

    [[ "${installed}" == "1" ]] || return 1
    printf '%s: cluster-side drainer installed (crontab %s).\n' \
        "${cluster}" "${DRAIN_CRON_SPEC}"
    return 0
}

uninstall_remote_drainer() {
    local cluster="$1"
    local marker
    marker="$(drain_marker "${cluster}")"
    ssh "${ssh_args[@]}" "${remote}" \
        "bash -c '
            marker=\"\$1\"
            if crontab -l 2>/dev/null | grep -qF \"\${marker}\"; then
                crontab -l 2>/dev/null | grep -vF \"\${marker}\" | crontab -
            fi
        ' _ $(printf '%q' "${marker}")" || return 1
    printf '%s: cluster-side drainer removed from the crontab.\n' "${cluster}"
}

# Once per start, before anything reads the cluster's queue state.
#
# Pushes the two files the cluster-side drainer consists of, because they must
# be current on the frontend whether or not the crontab needs installing -- a
# project sync would also put them there, but this script may be the first thing
# ever run against a cluster, and editing the drainer locally must not leave the
# cron running last week's copy.
#
# Seeds the waiting-job cap, which belongs to the cluster rather than to
# whichever computer happens to be watching: the drainer reads it there, so two
# machines cannot drain the same queue with two different limits. Written only
# when absent -- changing the cap is a deliberate edit of that file, not a side
# effect of starting a watcher whose MAX_WAITING_JOBS happens to differ.
prepare_cluster_side() {
    rsync -a --quiet -e "${rsync_ssh}" \
        "${LOCAL_PROJECT}/${DRAIN_SCRIPT}" \
        "${LOCAL_PROJECT}/scripts/cluster/cluster_queue_remote.sh" \
        "${remote}:${REMOTE_PROJECT}/scripts/cluster/" || return 1
    ssh "${ssh_args[@]}" "${remote}" \
        "mkdir -p '${CLUSTER_QUEUE_ROOT}' &&
         { [ -s '${CLUSTER_QUEUE_ROOT}/max_waiting' ] ||
           printf '%s\n' $(printf '%q' "${MAX_WAITING_JOBS}") > '${CLUSTER_QUEUE_ROOT}/max_waiting'; }" ||
        return 1
}

# Fallback path, and the immediate first pass so a fresh queue does not sit idle
# until the next cron tick. Drains every queue that has pending commands.
drain_from_here() {
    local cluster="$1"
    if ! ssh "${ssh_args[@]}" "${remote}" \
        "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=$(printf '%q' "${cluster}") \
         REMOTE_USER=$(printf '%q' "${REMOTE_USER}") \
         MAX_WAITING_JOBS=$(printf '%q' "${MAX_WAITING_JOBS}") \
         bash '${DRAIN_SCRIPT}'"
    then
        printf '%s: drain failed; will retry next round.\n' "${cluster}" >&2
    fi
}

# One round trip for everything queue-related: how much is pending, across how
# many queues, and whether the cluster-side drainer is still in the crontab.
# Checking the crontab here rather than only at startup means a drainer removed
# behind our back is noticed within one poll instead of silently never running.
cluster_queue_status() {
    local cluster="$1"
    local marker
    marker="$(drain_marker "${cluster}")"
    ssh "${ssh_args[@]}" "${remote}" "bash -c '
        pending=0
        queues=0
        for queue in \"\$1\"/*; do
            [ -f \"\${queue}/initialized\" ] || continue
            queues=\$((queues + 1))
            if [ -s \"\${queue}/pending.commands\" ]; then
                pending=\$((pending + \$(wc -l < \"\${queue}/pending.commands\")))
            fi
        done
        cron=\$(crontab -l 2>/dev/null | grep -cF \"\$2\" || true)
        printf \"%s %s %s\n\" \"\${pending}\" \"\${queues}\" \"\${cron:-0}\"
    ' _ $(printf '%q' "${CLUSTER_QUEUE_ROOT}") $(printf '%q' "${marker}")" ||
        printf '0 0 0\n'
}

# The OAR output paths of the commands still sitting in the queue -- queued here
# but never submitted, so oarstat cannot see them. Each path encodes the variant,
# the excluded group and the seed, which is what lets the progress table show one
# "(queued)" row per job instead of a bare count. Asked for only when something
# is actually pending, so an idle cluster costs no extra round trip.
cluster_pending_targets() {
    (( ${1:-0} > 0 )) || return 0
    { ssh "${ssh_args[@]}" "${remote}" \
        "cat '${CLUSTER_QUEUE_ROOT}'/*/pending.commands 2>/dev/null" || true; } |
        sed -n 's/.*[[:space:]]-O[[:space:]]\{1,\}\([^[:space:]]*\).*/\1/p'
}

# Rename, never delete: a finished queue is evidence, and the computer that
# happens to be watching must not be able to destroy a batch queued from the
# other one. Guarded by the same lock the drainer takes, and re-checked under it.
archive_idle_queues() {
    local cluster="$1"
    ssh "${ssh_args[@]}" "${remote}" "bash -c '
        root=\"\$1\"
        [ -d \"\${root}\" ] || exit 0
        for queue in \"\${root}\"/*; do
            [ -f \"\${queue}/initialized\" ] || continue
            case \"\${queue##*/}\" in done_*) continue ;; esac
            [ -s \"\${queue}/submitted.commands\" ] || continue
            [ -s \"\${queue}/pending.commands\" ] && continue
            flock -n \"\${queue}/drain.lock\" \
                mv \"\${queue}\" \"\${root}/done_\$(date +%Y%m%d_%H%M%S)_\${queue##*/}\" &&
                printf \"archived %s\n\" \"\${queue}\"
        done
    ' _ $(printf '%q' "${CLUSTER_QUEUE_ROOT}")" || true
}

# --- syncing --------------------------------------------------------------
sync_results() {
    # Ask once which directories exist rather than letting rsync fail per missing
    # one: a cluster that has not produced results yet has none of them (they are
    # outputs, excluded from the project sync), and rsync would print a
    # change_dir error for each, every round.
    #
    # models/ holds the --save_model checkpoints needed locally for rho
    # estimation. testmode_outputs/ is where a --testmode run redirects all its
    # artifacts; it is deliberately a sibling of test_metrics/, which is the only
    # tree update_metrics_table scans, so a smoke run can never reach
    # metrics_summary.csv.
    local existing directory
    existing="$(
        ssh "${ssh_args[@]}" "${remote}" \
            "cd '${REMOTE_PROJECT}' 2>/dev/null && for d in run test_metrics models testmode_outputs; do [ -d \"\$d\" ] && printf '%s\n' \"\$d\"; done" \
            2>/dev/null || true
    )"
    [[ -n "${existing}" ]] || return 0

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
    # An empty .err is itself a result: it is the evidence a job finished without
    # writing to stderr, which is what a --testmode smoke run is checked against.
    if [[ "${PRUNE_EMPTY_ERR:-0}" == "1" ]]; then
        find "${LOCAL_PROJECT}/script_logs" -type f -name '*.err' -empty -delete
    fi
}

update_metrics_table() {
    # Full, deduped rescan of the LOCAL tree, which already holds every cluster's
    # synced results. Gating on a session marker silently skipped jobs that
    # finished before the marker existed, so this always rescans everything;
    # add_new_metrics_to_table.py dedupes by source key, which makes repeated
    # runs cheap and self-healing.
    # The interpreter is probed, not pinned to CONDA_ENV: that name is the
    # CLUSTER's env, and this computer need not have one by that name. Running
    # the rebuild under whatever `python3` is on PATH is not safe either --
    # right after activating an env that only supplies rsync, it need not have
    # pandas at all.
    local python_bin
    if ! python_bin="$(python_for analysis.build_metrics_table)"; then
        printf 'No local python can import analysis.build_metrics_table; metrics table not updated.\n' >&2
        return 0
    fi
    # Roots are passed explicitly so it is visible here that testmode_outputs/ is
    # never scanned. "Added 0 ..." is the no-op case and would print every round.
    ( cd "${LOCAL_PROJECT}" && "${python_bin}" add_new_metrics_to_table.py \
        --metrics-root "${LOCAL_PROJECT}/test_metrics" \
        --run-root "${LOCAL_PROJECT}/run" \
        --table "${LOCAL_PROJECT}/metrics_summary.csv" ) \
        | grep -v '^Added 0 new metric rows' || true
}

print_next_waiting_start() {
    local estimate job_id start_epoch now_epoch remaining
    estimate="$(
        { ssh "${ssh_args[@]}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" || true; } |
            python3 "${SCRIPT_DIR}/lib/oarstat_json.py" next-waiting
    )"

    if [[ ! "${estimate}" =~ ^[^[:space:]]+[[:space:]][0-9]+$ ]]; then
        # Routine while the queue is deep: OAR simply has no estimate yet.
        note "Next waiting job start: OAR has not scheduled one yet."
        return
    fi

    read -r job_id start_epoch <<< "${estimate}"
    now_epoch="$(date +%s)"
    remaining=$((start_epoch - now_epoch))
    (( remaining < 0 )) && remaining=0
    printf 'Next waiting job: %s, scheduled start %s (in %dd %02dh %02dm %02ds).\n' \
        "${job_id}" \
        "$(date -d "@${start_epoch}" '+%Y-%m-%d %H:%M:%S %Z')" \
        "$((remaining / 86400))" "$(((remaining % 86400) / 3600))" \
        "$(((remaining % 3600) / 60))" "$((remaining % 60))"
}

# --- pending reports (cross-machine --graphics/--summarize handoff) ------
# launch/run_cluster.sh --graphics/--summarize drops one marker file per label
# under this cluster's own queue dir (CLUSTER_QUEUE_ROOT/active/pending_reports,
# on the cluster, not on whichever computer submitted) before it starts
# waiting. Called only once poll_cluster has this cluster's queue confirmed
# idle this round, so results are already synced and a checkpoint really is
# on disk to report on.
#
# This is what makes the handoff work from a different computer than the one
# that submitted: that machine's terminal or wait_and_sync.sh need not still
# be running -- the marker lives on the cluster, so whichever computer's
# wait_and_sync.sh next polls this cluster idle picks it up, generates the
# report locally on ITSELF, and clears the marker. Two watchers racing on the
# same idle cluster is handled by mv being atomic: it succeeds for exactly one
# of them, so only one machine ever generates a given label's report.
check_pending_reports() {
    local cluster="$1"
    local markers marker label claimed report_body seeds_csv do_graphics do_summarize

    markers="$(ssh "${ssh_args[@]}" "${remote}" \
        "ls '${CLUSTER_QUEUE_ROOT}/active/pending_reports/'*.report 2>/dev/null" || true)"
    [[ -n "${markers}" ]] || return 0

    while IFS= read -r marker; do
        [[ -n "${marker}" ]] || continue
        label="$(basename "${marker}" .report)"

        claimed="$(ssh "${ssh_args[@]}" "${remote}" \
            "mv '${marker}' '${marker}.claimed' 2>/dev/null && echo yes || echo no")"
        [[ "${claimed}" == "yes" ]] || continue

        report_body="$(ssh "${ssh_args[@]}" "${remote}" "cat '${marker}.claimed'" || true)"
        seeds_csv="$(printf '%s\n' "${report_body}" | sed -n 's/^seeds_csv=//p')"
        do_graphics="$(printf '%s\n' "${report_body}" | sed -n 's/^graphics=//p')"
        do_summarize="$(printf '%s\n' "${report_body}" | sed -n 's/^summarize=//p')"

        printf '%s: generating the report for %s (queued elsewhere, picked up here).\n' \
            "${cluster}" "${label}"
        bash "${LOCAL_PROJECT}/scripts/lib/generate_label_report.sh" \
            "${label}" "${seeds_csv:-0,1,2,3,4}" "${do_graphics:-1}" "${do_summarize:-1}" || true

        ssh "${ssh_args[@]}" "${remote}" "rm -f '${marker}.claimed'" || true
    done <<< "${markers}"
}

# --- one cluster, one round ----------------------------------------------
poll_cluster() {
    local cluster="$1"
    local job_table pending_jobs queue_count cron_installed
    local active_jobs running_jobs waiting_jobs other_jobs

    cluster_profile "${cluster}" || return 1
    set_transport
    SOURCE_IDLE["${cluster}"]=0
    ROUND_SYNCED=0

    printf '\n----- %s (%s) -----\n' "${cluster}" "${remote}"

    # The ControlMaster can die between rounds (idle overnight, network blip).
    if ! ensure_ssh_master; then
        printf 'Could not reconnect to %s; will retry next round.\n' "${remote}" >&2
        return 0
    fi

    if (( FIRST_ROUND )) && ! prepare_cluster_side; then
        printf 'Could not stage the cluster-side drainer on %s.\n' "${cluster}" >&2
    fi

    read -r pending_jobs queue_count cron_installed <<< "$(cluster_queue_status "${cluster}")"
    pending_jobs="${pending_jobs:-0}"
    queue_count="${queue_count:-0}"
    cron_installed="${cron_installed:-0}"

    if [[ "${REMOTE_DRAIN}" == "1" ]]; then
        if (( cron_installed == 0 )); then
            # Either never installed, or removed behind our back. Re-install, and
            # fall back to draining from here if the cluster refuses crontabs --
            # jobs must keep flowing either way.
            if install_remote_drainer "${cluster}"; then
                CLUSTER_DRAINER_OK["${cluster}"]=1
            else
                CLUSTER_DRAINER_OK["${cluster}"]=0
                printf '%s: could not install the cluster-side drainer; draining from this loop instead.\n' \
                    "${cluster}" >&2
                printf '%s: jobs will stop being submitted if this computer is switched off.\n' \
                    "${cluster}" >&2
            fi
        else
            CLUSTER_DRAINER_OK["${cluster}"]=1
        fi
    fi

    # Drain from here when there is no cluster-side drainer, and once at startup
    # even when there is, so a queue created moments ago does not sit idle until
    # the next cron tick.
    if (( pending_jobs > 0 )); then
        if (( CLUSTER_DRAINER_OK["${cluster}"] == 0 )) || (( FIRST_ROUND )); then
            drain_from_here "${cluster}"
        fi
    fi

    if ! job_table="$(ssh "${ssh_args[@]}" "${remote}" "oarstat -u ${REMOTE_USER}")"; then
        printf 'OAR status check failed for %s; will retry next round.\n' "${cluster}" >&2
        return 0
    fi

    read -r active_jobs running_jobs waiting_jobs other_jobs <<< "$(
        printf '%s\n' "${job_table}" |
            awk '
                $1 ~ /^[0-9]+$/ {
                    total++
                    if ($0 ~ /(^|[[:space:]])(R|Running)([[:space:]]|$)/) running++
                    else if ($0 ~ /(^|[[:space:]])(W|Waiting)([[:space:]]|$)/) waiting++
                    else other++
                }
                END { print total + 0, running + 0, waiting + 0, other + 0 }
            '
    )"

    wait_progress_add_cluster_stats "${cluster}" \
        "${running_jobs}" "${waiting_jobs}" "${other_jobs}" \
        "${active_jobs}" "${pending_jobs}" \
        "$( (( CLUSTER_DRAINER_OK["${cluster}"] )) && printf cluster-cron || printf local )"

    if (( active_jobs > 0 )); then
        note "Current OAR jobs for ${REMOTE_USER}:"
        [[ "${WAIT_VERBOSE}" == "1" ]] &&
            printf '%s\n' "${job_table}" | awk '$1 ~ /^[0-9]+$/ {print "  " $0}'
    else
        printf 'OAR jobs: total=0 for %s.\n' "${REMOTE_USER}"
    fi

    note "Synchronizing script logs."
    sync_script_logs || true

    # Results BEFORE the table, not after. run/ is what the TRAIN BA column is
    # read from, so pulling it first means the table shows this round's numbers
    # rather than last round's, and one transfer covers both.
    #
    # Synced whenever there is, or recently was, something to watch -- and always
    # on the first round, so starting the watcher pulls whatever came in while
    # nobody was looking. Deliberately not gated on a completed-jobs diff against
    # the previous round: such a diff only compares consecutive polls, so one
    # transient ssh failure would drop a batch of results permanently. rsync is
    # incremental, so repeating it is cheap and self-heals.
    if (( active_jobs > 0 || pending_jobs > 0 || queue_count > 0 || FIRST_ROUND )); then
        note "Synchronizing results."
        sync_results || true
        ROUND_SYNCED=1
    fi

    print_running_progress "${job_table}" \
        "$(cluster_pending_targets "${pending_jobs}" || true)" || true

    if (( active_jobs > 0 || pending_jobs > 0 )); then
        (( waiting_jobs > 0 )) && print_next_waiting_start
    else
        SOURCE_IDLE["${cluster}"]=1
        if (( queue_count > 0 )); then
            printf 'All %s jobs completed; nothing pending.\n' "${cluster}"
            (( ARCHIVE_IDLE_QUEUES )) && archive_idle_queues "${cluster}"
        fi
        check_pending_reports "${cluster}" || true
    fi
    return 0
}

# --- main -----------------------------------------------------------------
if [[ "${REMOTE_DRAIN}" == "uninstall" ]]; then
    for _cluster in "${CLUSTER_LIST[@]}"; do
        cluster_profile "${_cluster}" || continue
        set_transport
        ensure_ssh_master || continue
        uninstall_remote_drainer "${_cluster}" || true
    done
    exit 0
fi

note "Watching clusters: ${CLUSTERS} (refresh now, then every ${POLL_SECONDS}s)"

FIRST_ROUND=1
while true; do
    round_synced=0
    wait_progress_reset_cluster_stats

    # One loop over every source, in SOURCES order (local first). Both polls
    # keep the same contract -- they set ROUND_SYNCED and their own SOURCE_IDLE
    # entry -- so the frame around them is written once. poll_local
    # (lib/progress_table.sh) reads only script_logs/local_run.queue and the
    # pid-tagged *_l<pid>.out files, which nothing on a cluster ever writes, so
    # it can never race or double-count against poll_cluster.
    for _source in "${SOURCES[@]}"; do
        ROUND_SYNCED=0
        if [[ "${_source}" == "local" ]]; then
            poll_local || true
        else
            poll_cluster "${_source}" || true
        fi
        (( ROUND_SYNCED )) && round_synced=1
    done

    # One row per cluster plus the local row, always, after every source has
    # been visited, kept separate rather than summed.
    wait_progress_print_cluster_stats

    # One rebuild per round, from the merged local tree, so both clusters' (and
    # any local run's own) results land in the same table instead of
    # overwriting each other.
    if (( round_synced )); then
        note "Updating metrics table (merged, local)."
        update_metrics_table || true
    fi

    FIRST_ROUND=0
    (( RUN_ONCE )) && break

    all_idle=1
    for _source in "${SOURCES[@]}"; do
        (( SOURCE_IDLE["${_source}"] )) || all_idle=0
    done
    if (( all_idle )); then
        note "All clusters and the local grid idle; still watching (a new batch is picked up automatically)."
    fi

    note "Refreshing in ${POLL_SECONDS} seconds."
    sleep "${POLL_SECONDS}"
done
