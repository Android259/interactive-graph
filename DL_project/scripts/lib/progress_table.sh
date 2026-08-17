#!/usr/bin/env bash
# Running-job progress table, shared by scripts/wait_and_sync.sh (bigfoot and
# kraken) and scripts/wait_and_sync_local.sh (this machine). `source` it after
# cluster_common.sh.
#
# One implementation builds the table for all three sources: they differ only in
# how a job gets its id and where the not-yet-started ones are listed, and both
# are arguments to wait_progress_job_table.
#
# One line per running job:
#
#   LABEL                    EXCL GROUP  SEED  CUR  CKPT  BEST VBA  VBA  TRAIN BA
#
# LABEL / EXCL GROUP / SEED come from the OAR output file's path, which
# launch/submit_grid.sh builds as
# script_logs/<variant>_seeds01234/<group>/<variant>_seed<N>_<tag><jobid>.out
# (cold-split runs insert _val-<validation group> before the seed). CUR is the
# epoch in progress, CKPT the epoch of the best checkpoint, BEST VBA its rolling-5
# valid balanced accuracy, VBA the raw valid balanced accuracy of the last
# completed epoch (unsmoothed, so it moves every epoch instead of only when a new
# best is claimed), TRAIN BA the train balanced accuracy of that same epoch -- the one number training/new_train.py never prints, which is
# why the TensorBoard pass below exists at all.
#
# Callers must provide (cluster_common.sh does): LOCAL_PROJECT, JOB_ID_TAG,
# REMOTE_USER, remote, ssh_args.

_WAIT_PROGRESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Interpreter that can import $1. wait_and_sync.sh probes for one, since the two
# computers this project runs from have different conda layouts; anything else
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
#   last_valid_balanced_accuracy
# "best" is smoothed over the last five epochs, so a single lucky epoch does not
# claim the checkpoint. The last field is the RAW score of the last completed
# epoch -- the same number before smoothing, which is what shows whether the run
# is still moving right now rather than how good its best checkpoint once was.
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
                printf "%d %d %d %.6f %.6f\n", current, completed, best_epoch, best, score
            } else {
                printf "%d %d %d n/a n/a\n", current, completed, best_epoch
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

# Reads the recent-events directory built by wait_progress_refresh_event_cache
# and answers one TRAIN BA request per input line. Takes the directory as $1 so
# the caller decides when it was last rebuilt.
wait_progress_tb_counts() {
    local root="$1"
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

# Job id -> name and output-file path, from OAR. Needed for jobs that have no
# local log yet: one still waiting for a GPU, and one running whose log has not
# been rsynced across. The JSON is read by scripts/lib/oarstat_json.py, which is
# also what supplies the "next waiting job" estimate -- one parser, so the two
# cannot disagree about a payload.
#
#   out: job_id \t name \t stdout_file
wait_progress_oar_jobs() {
    { ssh "${ssh_args[@]}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" || true; } |
        python3 "${_WAIT_PROGRESS_DIR}/oarstat_json.py" jobs
}

# One OAR output path -> "label \t excluded group \t seed", the three name
# columns of the table.
#
# The submitters build that path as
#   script_logs/<variant>_seeds01234/<group>/<variant>_seed<N>_<tag><job id>.out
# and print_running_progress reads a running job's row back out of exactly the
# same shape, so a job that has not started yet lands in the same row it will
# occupy once it does -- which is the point: the row does not jump around when
# the job starts.
#
# %jobid% is accepted as well as a real id, because a command still sitting in
# the queue has not been through oarsub yet and still carries the placeholder.
wait_progress_parse_out_path() {
    local path="$1"
    local file stem label group seed

    file="$(basename "${path}")"
    group="$(basename "$(dirname "${path}")")"

    # A packed job (scripts/run_experiment_pack.sh) is ONE OAR job carrying
    # several experiments, written into a _packs directory. There is no single
    # group or seed to show for it until it starts and writes one log per
    # experiment, so name it and leave the rest blank.
    if [[ "${file}" == *.pack.out ]]; then
        stem="${file%.pack.out}"
        stem="$(printf '%s' "${stem}" | sed -E 's/_[A-Za-z]?(%jobid%|[0-9]+)$//')"
        printf '%s\t-\t-\n' "${stem}"
        return
    fi

    stem="${file%.out}"
    stem="$(printf '%s' "${stem}" | sed -E 's/_[A-Za-z]?(%jobid%|[0-9]+)$//')"
    label="${stem}"
    seed='-'
    if [[ "${stem}" =~ ^(.+)_seed([0-9]+)$ ]]; then
        label="${BASH_REMATCH[1]}"
        seed="${BASH_REMATCH[2]}"
    fi
    # A cold-split run holds out a validation group as well as the test group the
    # directory is named after; both belong in the group column.
    if [[ "${label}" =~ ^(.+)_val-([^_]+)$ ]]; then
        label="${BASH_REMATCH[1]}"
        group="${group}/val-${BASH_REMATCH[2]}"
    fi
    printf '%s\t%s\t%s\n' "${label}" "${group}" "${seed}"
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

# Whether each source has nothing left to do, keyed by source name -- "bigfoot",
# "kraken", "local". One map rather than an array for the clusters and a separate
# variable for local: the summary table already treats local as a third row like
# any other, and the two bookkeepings kept having to be checked separately.
declare -A SOURCE_IDLE=()

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
# watcher that has one.
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

# --- one table, three sources -----------------------------------------------
# Every ".out" file under script_logs, listed once. All three sources name their
# output "<...>_<tag><id>.out" -- tag "" on bigfoot, "k" on kraken, "l" for a
# local job, over three id spaces that cannot collide -- so one listing serves
# all of them. Taken once per table rather than once per job: script_logs holds
# every past run's logs, so walking it per job is the expensive way to ask a
# cheap question.
wait_progress_out_files() {
    find "${LOCAL_PROJECT}/script_logs" \( -type f -o -type l \) \
        -name '*.out' 2>/dev/null | sort
}

# The ".out" files belonging to one job.
#
# A PACKED job (scripts/run_experiment_pack.sh) writes one per experiment it
# runs, all carrying the same job id, so a pack matches several times and each
# match becomes its own row; an ordinary job matches once. The packed job's OWN
# output is named "*.pack.out" precisely so that it does not match here and turn
# into a phantom row.
wait_progress_logs_of() {
    local out_files="$1" tag="$2" id="$3"
    printf '%s\n' "${out_files}" | grep -E "_${tag}${id}\.out\$" || true
}

# THE progress table. One implementation for bigfoot, kraken and local runs.
# They differ in exactly two things -- how a job gets its id, and where the
# not-yet-started ones are listed -- and both are arguments here, so the columns,
# the parsing, the TensorBoard read and the sort order cannot drift apart.
#
#   $1  id tag: "" bigfoot, "k" kraken, "l" local
#   $2  directory of recent TensorBoard event files. TRAIN BA is read from there
#       and nowhere else -- training/new_train.py never prints it to the log.
#   $3  every ".out" file under script_logs, from wait_progress_out_files
#   $4  ids of the jobs that are RUNNING, one per line
#   $5  ready-made rows for jobs that are not running yet, one per line, already
#       eight tab-separated columns
wait_progress_job_table() {
    local tag="$1" event_root="$2" out_files="$3" running_ids="$4" extra_rows="$5"
    local id log_file label group seed row row_key row_index
    local current completed best_epoch best_score last_score
    local -a parsed=() rows=() log_files=()
    local tb_requests=""

    # Pass 1: read every running job's log.
    while IFS= read -r id; do
        [[ -n "${id}" ]] || continue
        log_files=()
        while IFS= read -r log_file; do
            [[ -n "${log_file}" ]] && log_files+=("${log_file}")
        done < <(wait_progress_logs_of "${out_files}" "${tag}" "${id}")

        row_index=0
        for log_file in "${log_files[@]+"${log_files[@]}"}"; do
            read -r current completed best_epoch best_score last_score \
                <<< "$(wait_progress_parse_log "${log_file}")"
            IFS=$'\t' read -r label group seed \
                <<< "$(wait_progress_parse_out_path "${log_file}")"

            # Keyed per EXPERIMENT, not per job: the several rows a packed job
            # contributes would otherwise overwrite each other's TRAIN BA. The
            # TensorBoard helper treats this field as an opaque key.
            row_key="${tag}${id}#${row_index}"
            row_index=$(( row_index + 1 ))

            parsed+=("${row_key}"$'\t'"${label}"$'\t'"${group}"$'\t'"${seed}"$'\t'"${current}"$'\t'"${best_epoch}"$'\t'"${best_score}"$'\t'"${last_score}")
            tb_requests+="${row_key}"$'\t'"${completed}"$'\t'"$(stat -c '%Y' "${log_file}")"$'\t'"groups_$(basename "$(dirname "${log_file}")")"$'\n'
        done
    done <<< "${running_ids}"

    if (( ${#parsed[@]} == 0 )) && [[ -z "${extra_rows}" ]]; then
        return 0
    fi

    # Pass 2: one TensorBoard read for the whole table.
    local -A train_ba=()
    if [[ -n "${tb_requests}" ]]; then
        local tb_key tb_value
        while IFS=$'\t' read -r tb_key tb_value; do
            train_ba["${tb_key}"]="${tb_value}"
        done < <(printf '%s' "${tb_requests}" |
            wait_progress_tb_counts "${event_root}")
    fi

    for row in "${parsed[@]+"${parsed[@]}"}"; do
        IFS=$'\t' read -r row_key label group seed current best_epoch best_score last_score <<< "${row}"
        rows+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
            "${label}" "${group}" "${seed}" "${current}" "${best_epoch}" \
            "$(wait_progress_round2 "${best_score}")" \
            "$(wait_progress_round2 "${last_score}")" \
            "$(wait_progress_round2 "${train_ba[${row_key}]-}")")")
    done

    if [[ -n "${extra_rows}" ]]; then
        while IFS= read -r row; do
            [[ -n "${row}" ]] && rows+=("${row}")
        done <<< "${extra_rows}"
    fi

    # Sorted by label, then group, then seed: the order the runs were conceived
    # in, not the order the scheduler happens to list them, so the same run sits
    # in the same place from one refresh to the next.
    {
        printf 'LABEL\tEXCL GROUP\tSEED\tCUR\tCKPT\tBEST VBA\tVBA\tTRAIN BA\n'
        printf '%s\n' "${rows[@]}" | sort -t$'\t' -k1,1 -k2,2 -k3,3n
    } | wait_progress_render_table 'LLRRRRRR'
}

# One table per cluster, from that cluster's `oarstat -u` output.
#
#   $1  the `oarstat -u` table
#   $2  OAR output paths of commands still queued on the cluster, one per line
print_running_progress() {
    local job_table="$1" queued_targets="${2:-}"
    local job_id label group seed out_files state entry target
    local running_ids="" extra_rows=""
    local -a pending=() waiting=() annotated=()

    out_files="$(wait_progress_out_files)"

    # Running jobs split in two: those whose log has reached this machine (a full
    # row with numbers) and those whose has not yet (a name only).
    while IFS= read -r job_id; do
        [[ -n "${job_id}" ]] || continue
        if [[ -n "$(wait_progress_logs_of "${out_files}" "${JOB_ID_TAG}" "${job_id}")" ]]; then
            running_ids+="${job_id}"$'\n'
        else
            pending+=("${job_id}")
        fi
    done < <(
        printf '%s\n' "${job_table}" |
            awk '$1 ~ /^[0-9]+$/ && $0 ~ /(^|[[:space:]])(R|Running)([[:space:]]|$)/ { print $1 }'
    )

    # Jobs OAR has accepted but not started yet. They have no log to read, but
    # they are real queued work, so they get a row of their own the way
    # run_local.sh's not-yet-started jobs do -- a count in the summary table says
    # nine are waiting without saying which nine.
    while IFS= read -r job_id; do
        [[ -n "${job_id}" ]] && waiting+=("${job_id}")
    done < <(
        printf '%s\n' "${job_table}" |
            awk '$1 ~ /^[0-9]+$/ && $0 ~ /(^|[[:space:]])(W|Waiting)([[:space:]]|$)/ { print $1 }'
    )

    # Both kinds are named from OAR's own record of where the job writes its
    # output -- the very path a running row is named from, so a job keeps the same
    # row when it starts instead of jumping elsewhere in the table. When OAR
    # reports no such path, fall back to the job name as one piece: it reads
    # "<variant>_<group>_s<seed>" and both halves contain underscores, so there is
    # no telling where the group name begins.
    if (( ${#pending[@]} + ${#waiting[@]} > 0 )); then
        local job_info job_name job_out
        job_info="$(wait_progress_oar_jobs)"
        for job_id in "${pending[@]+"${pending[@]}"}"; do
            annotated+=("${job_id}"$'\t'"log pending")
        done
        for job_id in "${waiting[@]+"${waiting[@]}"}"; do
            annotated+=("${job_id}"$'\t'"waiting")
        done
        for entry in "${annotated[@]}"; do
            IFS=$'\t' read -r job_id state <<< "${entry}"
            job_name="$(printf '%s\n' "${job_info}" |
                awk -F '\t' -v id="${job_id}" '$1 == id {print $2; exit}')"
            job_out="$(printf '%s\n' "${job_info}" |
                awk -F '\t' -v id="${job_id}" '$1 == id {print $3; exit}')"
            if [[ -n "${job_out}" ]]; then
                IFS=$'\t' read -r label group seed \
                    <<< "$(wait_progress_parse_out_path "${job_out}")"
            else
                label="${job_name:-job ${job_id}}"
                group='-'
                seed='-'
            fi
            extra_rows+="$(printf '%s (%s)\t%s\t%s\t-\t-\t-\t-\t-' \
                "${label}" "${state}" "${group}" "${seed}")"$'\n'
        done
    fi

    # Commands still sitting in the cluster's own queue: never submitted to OAR,
    # so oarstat knows nothing about them at all. The -O path each carries is the
    # one the job will write to once submitted, so it names the row exactly as the
    # running row will be named. This is the cluster's counterpart of
    # run_local.sh's script_logs/local_run.queue.
    if [[ -n "${queued_targets}" ]]; then
        while IFS= read -r target; do
            [[ -n "${target}" ]] || continue
            IFS=$'\t' read -r label group seed \
                <<< "$(wait_progress_parse_out_path "${target}")"
            extra_rows+="$(printf '%s (queued)\t%s\t%s\t-\t-\t-\t-\t-' \
                "${label}" "${group}" "${seed}")"$'\n'
        done <<< "${queued_targets}"
    fi

    wait_progress_job_table "${JOB_ID_TAG}" \
        "$(wait_progress_refresh_event_cache)" "${out_files}" \
        "${running_ids}" "${extra_rows}"
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

# --- the recent-events directory ---------------------------------------------
# The TRAIN BA reader is never pointed at run/ itself. It opens every run
# directory whose group name matches the one being asked about, and a group name
# like "groups_CRAL-TRIO" has been reused by hundreds of past experiments here,
# so reading run/ directly took over two minutes per round. Instead it is pointed
# at a directory holding ONLY the event files written in the last
# EVENT_LOOKBACK_MINUTES.
#
# One directory serves all three sources, because all three write into the same
# run/ tree on this machine: local jobs land there directly, and a cluster's land
# there when the round rsyncs its results in, which happens before the table is
# printed.
#
# Symlinks, not copies: the files are already on this disk. Rebuilt at the top of
# every call, since run/ changes under it. The name is keyed on the watcher's own
# pid so a long-lived watcher reuses one directory rather than leaving a fresh one
# in /tmp behind every round.
wait_progress_event_cache_path() {
    printf '/tmp/dl-events-%s-%s\n' "${USER:-$(id -un)}" "$$"
}

wait_progress_refresh_event_cache() {
    local cache lookback event_file rel_path link_dir
    cache="$(wait_progress_event_cache_path)"
    lookback="${EVENT_LOOKBACK_MINUTES:-480}"

    rm -rf "${cache}"
    mkdir -p "${cache}"
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
    local out_files="$1" pid
    while IFS= read -r pid; do
        [[ -n "${pid}" ]] || continue
        # A here-string, not a pipe into `grep -q`: grep stops at the first match
        # and closes its input, the writer takes SIGPIPE, and under `pipefail`
        # the whole test then reads as failed -- which silently reported every
        # running local job as not running.
        if grep -qE "_${LOCAL_JOB_TAG}${pid}\.out\$" <<< "${out_files}"; then
            printf '%s\n' "${pid}"
        fi
    done < <(pgrep -f 'training/new_train\.py' 2>/dev/null || true)
}

# The local half of the same table: scripts/run_local.sh grids on this machine.
#
# Same table, same function underneath. Only the two inputs differ: a job's id is
# the training process's own pid rather than an OAR job id, and the not-yet-
# started jobs come from run_local.sh's own queue file rather than from a
# scheduler.
print_local_progress() {
    local out_files="$1" running_ids="" extra_rows=""
    local pid q_variant q_group q_seed

    while IFS= read -r pid; do
        [[ -n "${pid}" ]] && running_ids+="${pid}"$'\n'
    done < <(wait_progress_local_pids "${out_files}")

    # Jobs of the grid that is running right now which run_local.sh has not
    # launched yet.
    if [[ -s "${LOCAL_QUEUE_FILE}" ]]; then
        while IFS=$'\t' read -r q_variant q_group q_seed; do
            [[ -n "${q_variant}" ]] || continue
            extra_rows+="$(printf '%s (queued)\t%s\t%s\t-\t-\t-\t-\t-' \
                "${q_variant}" "${q_group}" "${q_seed}")"$'\n'
        done < "${LOCAL_QUEUE_FILE}"
    fi

    wait_progress_job_table "${LOCAL_JOB_TAG}" \
        "$(wait_progress_refresh_event_cache)" "${out_files}" \
        "${running_ids}" "${extra_rows}"

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

# One round's worth of local-job observation: the table, the summary row, and
# whether this round found anything worth a metrics rescan. Same shape and same
# contract as poll_cluster() -- the round loop calls both the same way (reset
# ROUND_SYNCED, call, fold it into round_synced) and reads SOURCE_IDLE afterwards
# -- but needs neither SSH nor rsync, since local jobs write straight into
# LOCAL_PROJECT already. ROUND_SYNCED and SOURCE_IDLE are set rather than
# returned because the caller resets one right before the call and reads both
# right after, which needs no return-value plumbing.
poll_local() {
    local running=0 waiting=0 out_files

    # One listing of script_logs for the whole round: the pid check below and the
    # table both need it, and the tree holds every past run's logs.
    out_files="$(wait_progress_out_files)"
    running="$(wait_progress_local_pids "${out_files}" | wc -l)"
    [[ -s "${LOCAL_QUEUE_FILE}" ]] && waiting="$(wc -l < "${LOCAL_QUEUE_FILE}")"

    wait_progress_add_cluster_stats "local" "${running}" "${waiting}" 0 \
        "$(( running + waiting ))" 0

    SOURCE_IDLE["local"]=1
    if (( running > 0 || waiting > 0 )); then
        SOURCE_IDLE["local"]=0
        printf '\n----- local -----\n'
        print_local_progress "${out_files}" || true
        ROUND_SYNCED=1
    fi
}
