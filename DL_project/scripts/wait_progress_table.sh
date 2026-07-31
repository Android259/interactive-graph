#!/usr/bin/env bash
# Running-job progress table, shared by scripts/wait_and_sync.sh and
# scripts/wait_and_sync2.sh. `source` it after cluster_common.sh.
#
# The two watchers differ in how they keep jobs flowing (tmux daemon + local
# drain vs. foreground viewer + cluster cron) but they observe the same thing,
# so the observation lives here once: both used to carry their own copy of the
# log parser, the TensorBoard reader and the progress printer, and a change to
# the display had to be made twice and stayed in sync only by luck.
#
# One line per running job:
#
#   LABEL                    EXCL GROUP  SEED  CUR  CKPT  BEST VBA  TRAIN BA
#
# LABEL / EXCL GROUP / SEED come from the OAR output file's path, which the
# submitters build as script_logs/<variant>_seeds01234/<group>/<variant>_seed<N>_<tag><jobid>.out
# (cold-split runs insert _val-<validation group> before the seed). CUR is the
# epoch in progress, CKPT the epoch of the best checkpoint, BEST VBA its rolling-5
# valid balanced accuracy, TRAIN BA the train balanced accuracy of the last
# completed epoch -- the one number training/new_train.py never prints, which is
# why the TensorBoard pass below exists at all.
#
# Callers must provide (cluster_common.sh does): LOCAL_PROJECT, JOB_ID_TAG,
# EVENT_CACHE, REMOTE_USER, remote, ssh_args.

# Interpreter that can import $1. wait_and_sync2.sh probes for one (the two
# computers this project runs from have different conda layouts); anything else
# gets plain python3.
wait_progress_python() {
    local module="$1"
    if declare -F python_for >/dev/null 2>&1; then
        python_for "${module}"
        return
    fi
    command -v python3 >/dev/null 2>&1 || return 1
    python3 -c "import ${module}" >/dev/null 2>&1 || return 1
    printf 'python3\n'
}

# Per-epoch progress from one OAR .out file:
#   current_epoch completed_epoch best_epoch best_rolling5_valid_balanced_accuracy
# "best" is smoothed over the last five epochs, so a single lucky epoch does not
# claim the checkpoint.
wait_progress_parse_log() {
    awk '
        /^EPOCH [0-9]+:/ {
            current = $2
            sub(/:$/, "", current)
        }
        /^valid epoch balanced_accuracy:/ {
            completed = current
            score = $4 + 0
            score_count += 1
            score_index = (score_count - 1) % 5
            rolling_scores[score_index] = score
            rolling_count = score_count < 5 ? score_count : 5
            rolling_sum = 0
            for (rolling_index = 0; rolling_index < rolling_count; rolling_index++) {
                rolling_sum += rolling_scores[rolling_index]
            }
            rolling_score = rolling_sum / rolling_count
            if (!have_best || rolling_score > best) {
                best = rolling_score
                best_epoch = current
                have_best = 1
            }
        }
        END {
            if (current == "") current = 0
            if (completed == "") completed = 0
            if (best_epoch == "") best_epoch = 0
            if (have_best) {
                printf "%d %d %d %.6f\n", current, completed, best_epoch, best
            } else {
                printf "%d %d %d n/a\n", current, completed, best_epoch
            }
        }
    ' "$1"
}

# Train balanced accuracy, which lives only in TensorBoard. Reads one request
# per line on stdin and writes one answer per line, so a whole round costs a
# single Python start-up and loads each run directory at most once.
#
#   in : job_id \t completed_epoch \t log_mtime \t exclusion_set
#   out: job_id \t train_balanced_accuracy
#
# Held in a variable rather than a heredoc because stdin carries the records.
_WAIT_PROGRESS_TB_PROGRAM='
import sys
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

REQUIRED = {"epoch/train balanced_accuracy", "epoch/valid balanced_accuracy"}

cache = Path(sys.argv[1])

# One walk of the cache, indexed by exclusion set. Deduped by DIRECTORY:
# EventAccumulator loads every event file in a directory, so two files there are
# one run seen twice, not two candidate runs -- indexing by file made those
# directories tie against themselves and report n/a.
dirs_by_set = {}
for event_file in cache.rglob("events.out.tfevents.*"):
    for part in event_file.parts:
        if part.startswith("groups_"):
            dirs_by_set.setdefault(part, set()).add(event_file.parent)

loaded = {}


def accumulator_for(directory):
    if directory not in loaded:
        result = None
        try:
            candidate = EventAccumulator(str(directory), size_guidance={"scalars": 0})
            candidate.Reload()
            if REQUIRED.issubset(set(candidate.Tags().get("scalars", []))):
                result = candidate
        except Exception:
            result = None
        loaded[directory] = result
    return loaded[directory]


def scalar_map(accumulator, tag):
    return {event.step: event for event in accumulator.Scalars(tag)}


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) != 4:
        continue
    key, completed_raw, mtime_raw, group = fields
    try:
        completed_epoch = int(completed_raw)
        log_mtime = float(mtime_raw)
    except ValueError:
        continue
    if completed_epoch == 0:
        print(f"{key}\tn/a")
        continue

    # The run directory whose completed epoch was written closest in time to the
    # log s last write is the one this job belongs to; two equally close ones
    # mean we cannot tell them apart, so report nothing rather than guess.
    candidates = []
    for directory in dirs_by_set.get(group, ()):
        accumulator = accumulator_for(directory)
        if accumulator is None:
            continue
        event = scalar_map(accumulator, "epoch/valid balanced_accuracy").get(
            completed_epoch
        )
        if event is None:
            continue
        candidates.append((abs(event.wall_time - log_mtime), str(directory), accumulator))

    if not candidates:
        print(f"{key}\tn/a")
        continue
    candidates.sort(key=lambda item: (item[0], item[1]))
    if len(candidates) > 1 and abs(candidates[1][0] - candidates[0][0]) < 2:
        print(f"{key}\tn/a")
        continue

    value = scalar_map(candidates[0][2], "epoch/train balanced_accuracy").get(
        completed_epoch
    )
    print(f"{key}\t" + ("n/a" if value is None else repr(value.value)))
'

#
# Takes the root to scan as $1, defaulting to EVENT_CACHE for the cluster
# caller (print_running_progress): that is a per-cluster temp dir populated
# by sync_recent_tensorboard_events(), which rsyncs event files FROM the
# remote cluster and never contains anything for local jobs. Local jobs never
# leave LOCAL_PROJECT at all -- their events already sit directly under
# LOCAL_PROJECT/run with no sync step -- so print_local_progress passes that
# instead of relying on whatever cluster EVENT_CACHE happened to be set to
# last (poll_cluster re-derives it per cluster inside cluster_profile(), so by
# the time poll_local runs after that loop it would be stale garbage anyway).
wait_progress_tb_counts() {
    local root="${1:-${EVENT_CACHE}}"
    local python_bin
    [[ -d "${root}" ]] || return 0
    if ! python_bin="$(wait_progress_python tensorboard)"; then
        # Warn once, then keep going: everything except train balanced accuracy
        # still comes from the job log.
        if [[ -z "${_WAIT_PROGRESS_TB_WARNED:-}" ]]; then
            _WAIT_PROGRESS_TB_WARNED=1
            printf 'No local python can import tensorboard; TRAIN BA will show n/a.\n' >&2
        fi
        return 0
    fi
    "${python_bin}" -c "${_WAIT_PROGRESS_TB_PROGRAM}" "${root}"
}

# Job id -> name, from OAR. Only needed for jobs whose log has not appeared yet;
# every other row is named from its log path. `oarstat -J` nests differently
# across versions, so accept either {"<id>": {...}} or a list of job objects.
wait_progress_oar_job_names() {
    { ssh "${ssh_args[@]}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" || true; } |
        python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    raise SystemExit

for key, job in (
    payload.items() if isinstance(payload, dict) else enumerate(payload)
):
    if not isinstance(job, dict):
        continue
    job_id = job.get("job_id", job.get("Job_Id", key))
    name = job.get("name") or job.get("job_name") or job.get("Job_Name")
    if name:
        print(f"{job_id}\t{name}")
'
}

# Tab-separated rows on stdin, header first, aligned table on stdout. $1 is one
# character per column: L left-aligns (names), R right-aligns (numbers, so digits
# line up under each other). Both tables below share it, so they indent and rule
# the same way and a change to the house style lands in one place.
wait_progress_render_table() {
    awk -F '\t' -v align="$1" '
        {
            line[NR] = $0
            if (NF > columns) columns = NF
            for (i = 1; i <= NF; i++) {
                if (length($i) > width[i]) width[i] = length($i)
            }
        }
        function cell(column, text) {
            return substr(align, column, 1) == "L" \
                ? sprintf("%-*s", width[column], text) \
                : sprintf("%*s", width[column], text)
        }
        function render(   i, out) {
            out = ""
            for (i = 1; i <= columns; i++) {
                out = out (i == 1 ? "" : "  ") cell(i, field[i])
            }
            sub(/ +$/, "", out)
            print "  " out
        }
        END {
            for (row = 1; row <= NR; row++) {
                split(line[row], field, "\t")
                render()
                if (row == 1) {
                    for (i = 1; i <= columns; i++) {
                        field[i] = sprintf("%*s", width[i], "")
                        gsub(/ /, "-", field[i])
                    }
                    render()
                }
            }
        }
    '
}

# --- per-cluster OAR summary ----------------------------------------------
# Filled in as the round visits each cluster, printed once at the end so the
# clusters sit next to each other rather than being separated by their own
# progress output.
WAIT_PROGRESS_CLUSTER_ROWS=()

wait_progress_reset_cluster_stats() { WAIT_PROGRESS_CLUSTER_ROWS=(); }

# cluster running waiting other total pending [drainer]
wait_progress_add_cluster_stats() {
    WAIT_PROGRESS_CLUSTER_ROWS+=(
        "$1"$'\t'"$2"$'\t'"$3"$'\t'"$4"$'\t'"$5"$'\t'"$6"$'\t'"${7:-}"
    )
}

# OTHER and PENDING are dropped when every cluster reports zero: they are the
# columns that are normally zero, and a column of zeros is noise that pushes the
# numbers that do change further apart. DRAINER likewise only appears for the
# watcher that has one (wait_and_sync2.sh).
wait_progress_print_cluster_stats() {
    (( ${#WAIT_PROGRESS_CLUSTER_ROWS[@]} > 0 )) || return 0

    local row cluster running waiting other total pending drainer
    local show_other=0 show_pending=0 show_drainer=0
    for row in "${WAIT_PROGRESS_CLUSTER_ROWS[@]}"; do
        IFS=$'\t' read -r cluster running waiting other total pending drainer <<< "${row}"
        [[ "${other}" == 0 ]] || show_other=1
        [[ "${pending}" == 0 ]] || show_pending=1
        [[ -z "${drainer}" ]] || show_drainer=1
    done

    local header=$'CLUSTER\tRUN\tWAIT'
    local align='LRR'
    if (( show_other )); then
        header+=$'\tOTHER'
        align+='R'
    fi
    header+=$'\tTOTAL'
    align+='R'
    if (( show_pending )); then
        header+=$'\tPENDING'
        align+='R'
    fi
    if (( show_drainer )); then
        header+=$'\tDRAINER'
        align+='L'
    fi

    # Blank line first: this table closes the round, and the last thing printed
    # before it is the final cluster's progress table.
    printf '\n'
    {
        printf '%s\n' "${header}"
        for row in "${WAIT_PROGRESS_CLUSTER_ROWS[@]}"; do
            IFS=$'\t' read -r cluster running waiting other total pending drainer <<< "${row}"
            printf '%s\t%s\t%s' "${cluster}" "${running}" "${waiting}"
            (( show_other )) && printf '\t%s' "${other}"
            printf '\t%s' "${total}"
            (( show_pending )) && printf '\t%s' "${pending}"
            (( show_drainer )) && printf '\t%s' "${drainer}"
            printf '\n'
        done
    } | wait_progress_render_table "${align}"
}

# Two decimals, or a dash for anything that is not a number (n/a, empty, a job
# whose first epoch has not finished).
wait_progress_round2() {
    local value="${1:-}"
    if [[ "${value}" =~ ^-?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$ ]]; then
        printf '%.2f' "${value}"
    else
        printf -- '-'
    fi
}

# One table per cluster, from that cluster's `oarstat -u` output.
print_running_progress() {
    local job_table="$1"
    local job_id log_file found stem label group seed
    local current completed best_epoch best_score
    local row_index row_key
    local -a parsed=() pending=() rows=() log_files=()
    local tb_requests=""

    # Pass 1: locate each running job's logs and parse them.
    while IFS= read -r job_id; do
        [[ -n "${job_id}" ]] || continue
        # The OAR output file is "..._${JOB_ID_TAG}${job_id}.out": the tag (empty
        # on Bigfoot, "k" on Kraken) is what keeps the two clusters' overlapping
        # job-ID spaces apart, so it must be part of the lookup.
        #
        # A PACKED job (scripts/run_experiment_pack.sh) writes one such file per
        # experiment it runs, all carrying the same job id, so each match is its
        # own row -- an unpacked job simply matches once. The packed job's own
        # OAR output is named "*.pack.out" precisely so that it does not match
        # here and turn into a phantom row.
        log_files=()
        while IFS= read -r found; do
            [[ -n "${found}" ]] && log_files+=("${found}")
        done < <(
            find "${LOCAL_PROJECT}/script_logs" -type f \
                -name "*_${JOB_ID_TAG}${job_id}.out" | sort
        )
        if (( ${#log_files[@]} == 0 )); then
            pending+=("${job_id}")
            continue
        fi

        row_index=0
        for log_file in "${log_files[@]}"; do
            read -r current completed best_epoch best_score \
                <<< "$(wait_progress_parse_log "${log_file}")"

            stem="$(basename "${log_file}" "_${JOB_ID_TAG}${job_id}.out")"
            group="$(basename "$(dirname "${log_file}")")"
            label="${stem}"
            seed='-'
            if [[ "${stem}" =~ ^(.+)_seed([0-9]+)$ ]]; then
                label="${BASH_REMATCH[1]}"
                seed="${BASH_REMATCH[2]}"
            fi
            # A cold-split run holds out a validation group as well as the test
            # group the directory is named after; both belong in the group column.
            if [[ "${label}" =~ ^(.+)_val-([^_]+)$ ]]; then
                label="${BASH_REMATCH[1]}"
                group="${group}/val-${BASH_REMATCH[2]}"
            fi

            # Keyed per EXPERIMENT, not per job: the several rows a packed job
            # contributes would otherwise overwrite each other's TRAIN BA. The
            # TensorBoard helper treats this field as an opaque key.
            row_key="${job_id}#${row_index}"
            row_index=$(( row_index + 1 ))

            parsed+=("${row_key}"$'\t'"${label}"$'\t'"${group}"$'\t'"${seed}"$'\t'"${current}"$'\t'"${best_epoch}"$'\t'"${best_score}")
            tb_requests+="${row_key}"$'\t'"${completed}"$'\t'"$(stat -c '%Y' "${log_file}")"$'\t'"groups_$(basename "$(dirname "${log_file}")")"$'\n'
        done
    done < <(
        printf '%s\n' "${job_table}" |
            awk '$1 ~ /^[0-9]+$/ && $0 ~ /(^|[[:space:]])(R|Running)([[:space:]]|$)/ { print $1 }'
    )

    (( ${#parsed[@]} + ${#pending[@]} > 0 )) || return 0

    # Pass 2: one TensorBoard read for the whole cluster.
    local -A train_ba=()
    if [[ -n "${tb_requests}" ]]; then
        local tb_key tb_value
        while IFS=$'\t' read -r tb_key tb_value; do
            train_ba["${tb_key}"]="${tb_value}"
        done < <(printf '%s' "${tb_requests}" | wait_progress_tb_counts)
    fi

    local row
    for row in "${parsed[@]+"${parsed[@]}"}"; do
        IFS=$'\t' read -r row_key label group seed current best_epoch best_score <<< "${row}"
        rows+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
            "${label}" "${group}" "${seed}" "${current}" "${best_epoch}" \
            "$(wait_progress_round2 "${best_score}")" \
            "$(wait_progress_round2 "${train_ba[${row_key}]-}")")")
    done

    # Jobs whose log has not reached us yet: OAR's job name already carries the
    # variant, group and seed, so show it whole rather than guessing where the
    # group name (some contain underscores) starts and ends.
    if (( ${#pending[@]} > 0 )); then
        local job_names
        job_names="$(wait_progress_oar_job_names)"
        for job_id in "${pending[@]}"; do
            label="$(
                printf '%s\n' "${job_names}" |
                    awk -F '\t' -v job_id="${job_id}" '$1 == job_id {print $2; exit}'
            )"
            [[ -n "${label}" ]] || label="job ${job_id}"
            rows+=("$(printf '%s (log pending)\t-\t-\t-\t-\t-\t-' "${label}")")
        done
    fi

    # Sorted by label, then group, then seed: the order the runs were conceived
    # in, not the order OAR happens to list them, so the same run sits in the
    # same place from one refresh to the next.
    {
        printf 'LABEL\tEXCL GROUP\tSEED\tCUR\tCKPT\tBEST VBA\tTRAIN BA\n'
        printf '%s\n' "${rows[@]}" | sort -t$'\t' -k1,1 -k2,2 -k3,3n
    } | wait_progress_render_table 'LLRRRRR'
}

# --- local jobs (scripts/run_local.sh) -------------------------------------
# The cluster path identifies a job by its OAR job id; a plain local background
# process has no scheduler-assigned id of its own, so run_local.sh manufactures
# one -- LOCAL_JOB_TAG plus the process's own pid -- mirroring bigfoot's empty
# tag / kraken's "k" tag on the exact same "*_${tag}${id}.out" naming
# print_running_progress already looks for. Three different tags over three
# disjoint id namespaces (each cluster's OAR job ids; local pids) is what keeps
# all three sources of logs living in the same script_logs/ tree without ever
# colliding on a filename, and metrics_summary.csv rows are keyed by
# datetime+config (upsert_row, analysis/build_metrics_table.py, guarded by an
# flock against exactly the concurrent-local-jobs case this script watches
# for) rather than by job id, so nothing here needs to know about that layer
# at all.
LOCAL_JOB_TAG="l"
# Jobs not yet launched WITHIN the currently-running grid.
LOCAL_QUEUE_FILE="${LOCAL_PROJECT}/script_logs/local_run.queue"
# Whole OTHER run_local.sh invocations queued behind the current one --
# e.g. "bash scripts/run_local.sh other.md" while a grid is already running
# gets appended here (run_local.sh) instead of refused outright. Distinct
# from LOCAL_QUEUE_FILE: that lists (group, seed) pairs inside one grid;
# this lists whole %q-encoded argv lines, one per queued invocation, each
# expanding into its OWN grid (and its own LOCAL_QUEUE_FILE) once it starts.
LOCAL_PENDING_BATCHES_FILE="${LOCAL_PROJECT}/script_logs/local_run_pending_batches"

# Recency-bounded view of LOCAL_PROJECT/run for the TensorBoard reader, built
# fresh each call: local jobs never leave LOCAL_PROJECT, so their events
# already sit directly under run/ with no sync step needed, but scanning that
# whole tree directly is not an option -- on this project's real history it
# took wait_progress_tb_counts over two minutes per poll, because the reader
# calls EventAccumulator.Reload() (parses the whole file) once per directory
# that shares a group name with the request, and a group name like
# "groups_CRAL-TRIO" has been reused by hundreds of past experiments. The
# cluster path never hits this: EVENT_CACHE there is populated by
# sync_recent_tensorboard_events(), which rsyncs in only files modified within
# EVENT_LOOKBACK_MINUTES. This reproduces that same bound locally with
# symlinks instead of rsync (nothing to transfer, it is already local) --
# same env var, same default, so one setting governs both sources.
#
# The cache dir name is keyed on this shell's own pid, not per-call, so a
# long-lived watcher reuses one path across every poll instead of leaking a
# fresh /tmp directory per round; wiped and rebuilt at the top of every call.
wait_progress_local_event_cache() {
    local cache="/tmp/local-events-${USER:-$(id -un)}-$$"
    rm -rf "${cache}"
    mkdir -p "${cache}"
    local lookback="${EVENT_LOOKBACK_MINUTES:-480}"
    local event_file rel_path link_dir
    while IFS= read -r event_file; do
        [[ -n "${event_file}" ]] || continue
        rel_path="${event_file#"${LOCAL_PROJECT}"/run/}"
        link_dir="${cache}/$(dirname "${rel_path}")"
        mkdir -p "${link_dir}"
        ln -sf "${event_file}" "${link_dir}/$(basename "${event_file}")"
    done < <(
        find "${LOCAL_PROJECT}/run" -type f -name 'events.out.tfevents.*' \
            -mmin "-${lookback}" 2>/dev/null
    )
    printf '%s\n' "${cache}"
}

# PIDs of currently-running local training jobs -- new_train.py processes that
# run_local.sh itself launched, identified by having a matching PID-tagged
# .out file under script_logs. This is what keeps a manually started training
# run (scripts/test_run.sh, an ad hoc smoke test) out of the local progress
# table and stats row: those never get tagged, so they never match here.
wait_progress_local_pids() {
    local pid
    while IFS= read -r pid; do
        [[ -n "${pid}" ]] || continue
        if find "${LOCAL_PROJECT}/script_logs" \( -type f -o -type l \) \
                -name "*_${LOCAL_JOB_TAG}${pid}.out" -print -quit 2>/dev/null | grep -q .
        then
            printf '%s\n' "${pid}"
        fi
    done < <(pgrep -f 'training/new_train\.py' 2>/dev/null || true)
}

# Same three-pass shape as print_running_progress (find each job's log, parse
# it, one shared TensorBoard read) but keyed by pid instead of an OAR job
# table, and with no "pending" branch: a local job that has no pid yet is not
# running at all, it is a line in LOCAL_QUEUE_FILE (run_local.sh has not
# backgrounded it), shown from there instead of guessed at from a job table.
print_local_progress() {
    local pid log_file found stem label group seed
    local current completed best_epoch best_score
    local row_index row_key
    local -a parsed_rows=() log_files=()
    local tb_requests=""

    while IFS= read -r pid; do
        [[ -n "${pid}" ]] || continue
        log_files=()
        while IFS= read -r found; do
            [[ -n "${found}" ]] && log_files+=("${found}")
        done < <(
            find "${LOCAL_PROJECT}/script_logs" \( -type f -o -type l \) \
                -name "*_${LOCAL_JOB_TAG}${pid}.out" 2>/dev/null | sort
        )
        (( ${#log_files[@]} > 0 )) || continue

        row_index=0
        for log_file in "${log_files[@]}"; do
            read -r current completed best_epoch best_score \
                <<< "$(wait_progress_parse_log "${log_file}")"

            stem="$(basename "${log_file}" "_${LOCAL_JOB_TAG}${pid}.out")"
            group="$(basename "$(dirname "${log_file}")")"
            label="${stem}"
            seed='-'
            if [[ "${stem}" =~ ^(.+)_seed([0-9]+)$ ]]; then
                label="${BASH_REMATCH[1]}"
                seed="${BASH_REMATCH[2]}"
            fi

            row_key="local${pid}#${row_index}"
            row_index=$(( row_index + 1 ))
            parsed_rows+=("${row_key}"$'\t'"${label}"$'\t'"${group}"$'\t'"${seed}"$'\t'"${current}"$'\t'"${best_epoch}"$'\t'"${best_score}")
            tb_requests+="${row_key}"$'\t'"${completed}"$'\t'"$(stat -c '%Y' "${log_file}")"$'\t'"groups_$(basename "$(dirname "${log_file}")")"$'\n'
        done
    done < <(wait_progress_local_pids)

    local -a queued_rows=()
    if [[ -s "${LOCAL_QUEUE_FILE}" ]]; then
        local q_variant q_group q_seed
        while IFS=$'\t' read -r q_variant q_group q_seed; do
            [[ -n "${q_variant}" ]] || continue
            queued_rows+=("$(printf '%s (queued)\t%s\t%s\t-\t-\t-\t-' "${q_variant}" "${q_group}" "${q_seed}")")
        done < "${LOCAL_QUEUE_FILE}"
    fi

    (( ${#parsed_rows[@]} + ${#queued_rows[@]} > 0 )) || return 0

    local -A train_ba=()
    if [[ -n "${tb_requests}" ]]; then
        local tb_key tb_value
        while IFS=$'\t' read -r tb_key tb_value; do
            train_ba["${tb_key}"]="${tb_value}"
        done < <(printf '%s' "${tb_requests}" | wait_progress_tb_counts "$(wait_progress_local_event_cache)")
    fi

    local -a out_rows=()
    local row
    for row in "${parsed_rows[@]+"${parsed_rows[@]}"}"; do
        IFS=$'\t' read -r row_key label group seed current best_epoch best_score <<< "${row}"
        out_rows+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
            "${label}" "${group}" "${seed}" "${current}" "${best_epoch}" \
            "$(wait_progress_round2 "${best_score}")" \
            "$(wait_progress_round2 "${train_ba[${row_key}]-}")")")
    done
    out_rows+=("${queued_rows[@]+"${queued_rows[@]}"}")

    {
        printf 'LABEL\tEXCL GROUP\tSEED\tCUR\tCKPT\tBEST VBA\tTRAIN BA\n'
        printf '%s\n' "${out_rows[@]}" | sort -t$'\t' -k1,1 -k2,2 -k3,3n
    } | wait_progress_render_table 'LLRRRRR'

    wait_progress_print_pending_batches
}

# Whole OTHER run_local.sh invocations queued behind the current run (see
# LOCAL_PENDING_BATCHES_FILE above) -- separate from the per-job table above,
# which only covers jobs inside the grid that is actually running right now.
# Each line is a %q-encoded argv; decoded back to plain text for display.
wait_progress_print_pending_batches() {
    [[ -s "${LOCAL_PENDING_BATCHES_FILE}" ]] || return 0
    local line decoded n=0
    printf '\nBatches queued behind the current run:\n'
    while IFS= read -r line; do
        [[ -n "${line}" ]] || continue
        n=$(( n + 1 ))
        eval "set -- ${line}"
        printf -v decoded '%s ' "$@"
        printf '  %d. %s\n' "${n}" "${decoded% }"
    done < "${LOCAL_PENDING_BATCHES_FILE}"
}

# One round's worth of local-job observation: table, cluster-stats row, and
# whether this round found anything worth a metrics rescan for. Mirrors
# poll_cluster()'s shape closely enough that both watchers call it the same
# way they call poll_cluster per named cluster -- reset ROUND_SYNCED, call,
# fold it into round_synced -- but needs neither SSH nor rsync, since local
# jobs write straight into LOCAL_PROJECT already. Sets the plain (non-local)
# globals ROUND_SYNCED and LOCAL_IDLE for the same reason poll_cluster sets
# ROUND_SYNCED: the caller resets it right before the call and reads it right
# after, so this needs no return-value plumbing.
poll_local() {
    local running=0 waiting=0

    running="$(wait_progress_local_pids | wc -l)"
    [[ -s "${LOCAL_QUEUE_FILE}" ]] && waiting="$(wc -l < "${LOCAL_QUEUE_FILE}")"

    wait_progress_add_cluster_stats "local" "${running}" "${waiting}" 0 \
        "$(( running + waiting ))" 0

    LOCAL_IDLE=1
    if (( running > 0 || waiting > 0 )); then
        LOCAL_IDLE=0
        printf '\n----- local -----\n'
        print_local_progress || true
        ROUND_SYNCED=1
    fi
}
