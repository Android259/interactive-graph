#!/usr/bin/env bash
# Local entry point: run this project's group x seed grid as parallel processes
# on this machine, instead of queuing OAR jobs on bigfoot/kraken.
#
# Analogous to run_bigfoot.sh / run_kraken.sh + submit_all_groups_all_seeds.sh,
# but there is only one local target, so sync/preflight/oarsub/wait_and_sync do
# not apply: this script resolves the args file, builds the group x seed grid,
# and runs it directly through a bounded local job queue.
#
# Usage: bash scripts/run_local.sh [--complete] [--seeds=LIST] [--groups=LIST] ARGS_FILE
# Example: bash scripts/run_local.sh scripts/arg_files/standard.md
# Example: bash scripts/run_local.sh --seeds=0,1,2 nps3mlp_gat_residual
#
#   --seeds=LIST   Comma/space-separated seeds. Default: 0,1,2,3,4 (same as
#                   run_cluster.sh).
#   --groups=LIST  Comma/space-separated excluded groups. Default: the 9
#                   canonical groups.
#   --complete     Run only requested group/seed pairs without final test_metrics.
#
# Parallelism, threads-per-job and workers-per-job are not flags -- like every
# other cluster-dependent setting in this project (PROJECT, GPU_RESOURCES,
# WALLTIME, ...) they are environment overrides with a computed default, so an
# unset environment does the right thing on this machine's resources:
#
#   LOCAL_JOBS             number of training processes run at once.
#                           Default: min(usable cores, jobs RAM fits) -- see
#                           RESERVED_CORES and RESERVED_MEM_GIB/MEM_PER_JOB_GIB
#                           below. The actual maximum both budgets allow, not
#                           a throughput-tuned guess; see the note further
#                           down. An explicit LOCAL_JOBS skips both caps, on
#                           the assumption the caller has already accounted
#                           for memory themselves.
#   OMP_THREADS_PER_JOB     OMP_NUM_THREADS / MKL_NUM_THREADS given to each job.
#                           Default: (nproc - RESERVED_CORES) / LOCAL_JOBS.
#   NUM_WORKERS_PER_JOB     --num_workers given to each job. Default: 1.
#   RESERVED_CORES          Cores held back from the CPU split. Default: 25% of
#                           the CPUs detected on this machine, at least 2.
#                           Override with 0 on a headless worker.
#   MAX_OMP_THREADS_PER_JOB Upper bound for one training process. Default: 4,
#                           the measured optimum on the local 12-CPU machine.
#   RESERVED_MEM_GIB        RAM held back from the job-count cap, same idea as
#                           RESERVED_CORES but for memory. Default: 9 (this
#                           machine's measured idle baseline).
#   MEM_PER_JOB_GIB         RAM budgeted per job for that cap. Default: 4 --
#                           the MARGINAL cost of one more concurrent job, not
#                           one job's own RSS in isolation (summing isolated
#                           RSS overestimates: shared libtorch/MKL pages are
#                           not duplicated per process). See the measurements
#                           below. THIS IS THE BINDING CONSTRAINT ON THIS
#                           MACHINE, not cores: a LOCAL_JOBS=22 run (basing
#                           the job count on cores alone, before this cap
#                           existed) exhausted the 31 GiB of RAM here and the
#                           OOM killer took out GNOME Shell itself along with
#                           several terminals. CPU and memory are independent
#                           budgets; nothing about reserving cores protects
#                           against this.
#
# A partial throughput sweep exists from earlier work on this machine (24
# cores, a lighter 481k-parameter config, testmode, 3 epochs): throughput kept
# climbing from N=1 through N=6 (0.0238 -> 0.0339 epochs/s), N=8/N=12 were
# attempted but never got a clean, uncontaminated measurement, and it was
# never run at all for a heavier config or for the current (nproc-2)/N split.
# That is not enough to defend any N as "optimal" in general, so LOCAL_JOBS no
# longer defaults to a throughput-tuned guess -- it defaults to the actual
# maximum, one job per usable core. If a config's true throughput peak turns
# out to sit below that (small tensors do not scale linearly across threads
# within one process -- see the cProfile breakdown in dataloader/AGENTS.md:
# ~44% of an epoch is torch.autograd run_backward, ~29% is attention
# baddbmm/softmax/bmm -- so a single job rarely saturates its own thread
# budget with useful work, and per earlier data giving a job the FULL machine
# was measured worse than splitting it: N=4 at 6 threads/job scored below N=4
# at 4 threads/job), the fix is to override LOCAL_JOBS down after actually
# measuring that config, not to bake an unverified number in as everyone's
# default.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

usage() {
    printf 'Usage: bash %s [--complete] [--seeds=LIST] [--groups=LIST] ARGS_FILE\n' "${0##*/}" >&2
    printf 'Example: bash %s scripts/arg_files/standard.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --seeds=0,1,2 nps3mlp_gat_residual\n' "${0##*/}" >&2
}

# -h/--help must short-circuit before self-detach: it does not launch
# anything, so it has no business spawning a tmux session or a setsid+nohup
# process just to print usage and exit (this is not a hypothetical -- it did
# exactly that before this check existed).
for _arg in "$@"; do
    if [[ "${_arg}" == "-h" || "${_arg}" == "--help" ]]; then
        usage
        exit 0
    fi
done

# Self-detach so closing the terminal (or losing the SSH session to this
# machine) does not kill a grid that is still running -- same intent as
# scripts/wait_and_sync.sh's tmux daemon, but tmux is not installed on every
# machine this runs on (checked here at run time, nothing is installed to fix
# that) and the caller may not be able to install it either, so this falls
# back to setsid+nohup, which need nothing beyond coreutils/util-linux that
# every one of this project's machines already has. Both paths give the same
# guarantee: the training processes keep running detached from the shell that
# launched them; only the log-tailing in this terminal stops on Ctrl-C or on
# the client machine going away.
#
# RUN_LOCAL_TMUX=0 opts out of both (matches wait_and_sync.sh's WAIT_TMUX=0),
# and the relaunch sets it so the detached copy does not try to detach again.
LOCAL_RUN_SESSION="local_run"
# FIFO of invocations queued behind an already-active run, one %q-encoded
# argv per line -- see the "already active" branches below, where a second
# invocation appends itself here instead of being silently dropped, and the
# chaining check at the end of a real run, which pops and execs the next one.
PENDING_BATCHES_FILE="${PROJECT_ROOT}/script_logs/local_run_pending_batches"
if [[ "${RUN_LOCAL_TMUX:-1}" != "0" && -z "${TMUX:-}" && -z "${RUN_LOCAL_DETACHED:-}" ]]; then
    mkdir -p "${PROJECT_ROOT}/script_logs"
    log_file="${PROJECT_ROOT}/script_logs/${LOCAL_RUN_SESSION}.log"

    if command -v tmux >/dev/null 2>&1; then
        if tmux has-session -t "${LOCAL_RUN_SESSION}" 2>/dev/null; then
            printf '%s\n' "$(printf '%q ' "$@")" >> "${PENDING_BATCHES_FILE}"
            printf 'A local run is already active in tmux session: %s. Queued this one behind it (%d queued); it will start automatically once the current run finishes.\n' \
                "${LOCAL_RUN_SESSION}" "$(wc -l < "${PENDING_BATCHES_FILE}")"
        else
            : > "${log_file}"
            printf -v relaunch_command 'cd %q && RUN_LOCAL_TMUX=0 stdbuf -oL -eL bash %q %s 2>&1 | tee -a %q' \
                "${PROJECT_ROOT}" "${BASH_SOURCE[0]}" "$(printf '%q ' "$@")" "${log_file}"
            tmux new-session -d -s "${LOCAL_RUN_SESSION}" "${relaunch_command}"
            printf 'Local run started in tmux session: %s\n' "${LOCAL_RUN_SESSION}"
        fi
        printf 'Streaming its log in this terminal from: %s\n' "${log_file}"
        printf 'Stop watching with Ctrl-c; the tmux session keeps going. Attach with: tmux attach -t %s\n' \
            "${LOCAL_RUN_SESSION}"
        follow_pid="$(tmux display-message -p -t "${LOCAL_RUN_SESSION}" '#{pane_pid}')"
    else
        pid_file="${PROJECT_ROOT}/script_logs/${LOCAL_RUN_SESSION}.pid"
        existing_pid="$(cat "${pid_file}" 2>/dev/null || true)"
        if [[ -n "${existing_pid}" ]] && kill -0 "${existing_pid}" 2>/dev/null; then
            printf '%s\n' "$(printf '%q ' "$@")" >> "${PENDING_BATCHES_FILE}"
            printf 'A local run is already active (pid %s, no tmux here). Queued this one behind it (%d queued); it will start automatically once the current run finishes.\n' \
                "${existing_pid}" "$(wc -l < "${PENDING_BATCHES_FILE}")"
            follow_pid="${existing_pid}"
        else
            : > "${log_file}"
            # setsid starts a new session with no controlling terminal, so the
            # child is immune to the SIGHUP a closing SSH session sends; nohup
            # additionally ignores it directly; disown drops it from this
            # shell's job table so this shell exiting sends it nothing either.
            RUN_LOCAL_DETACHED=1 setsid nohup bash "${BASH_SOURCE[0]}" "$@" \
                < /dev/null >> "${log_file}" 2>&1 &
            follow_pid=$!
            disown "${follow_pid}"
            printf '%s\n' "${follow_pid}" > "${pid_file}"
            printf 'tmux is not installed here; local run started detached (pid %s) via setsid+nohup.\n' \
                "${follow_pid}"
        fi
        printf 'Streaming its log in this terminal from: %s\n' "${log_file}"
        printf 'Stop watching with Ctrl-c; the detached run keeps going. Check on it with: tail -f %s\n' \
            "${log_file}"
    fi
    tail --pid="${follow_pid}" -n +1 -f "${log_file}"
    exit 0
fi

# Same activation scripts/parameters.sh uses. Without it, a shell that never
# ran `conda activate Kalinin_project_LP` launches every job with whatever
# python3 happens to be on PATH -- no torch, so every job dies on the import
# line in under a second, before it can even warn about the missing module in
# a way that stands out from a normal training crash. Falls back to whatever
# python3 is already on PATH (with a warning) rather than hard-failing, same
# as parameters.sh: some environments genuinely have no conda and still work.
if [[ "${CONDA_DEFAULT_ENV:-}" != "Kalinin_project_LP" ]]; then
    if ! source "${SCRIPT_DIR}/activate_training_env.sh"; then
        printf 'Could not activate the Kalinin_project_LP conda env; using current python3: %s\n' \
            "$(command -v python3 || echo 'not found')" >&2
    fi
fi

POSITIONALS=()
while (( $# > 0 )); do
    case "$1" in
        --complete)
            COMPLETE_ONLY=1
            shift
            ;;
        --seeds=*)
            SEEDS_ARG="${1#*=}"
            shift
            ;;
        --groups=*)
            GROUPS_ARG="${1#*=}"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            printf 'Unknown option: %s\n' "$1" >&2
            usage
            exit 2
            ;;
        *)
            POSITIONALS+=("$1")
            shift
            ;;
    esac
done

if (( ${#POSITIONALS[@]} != 1 )); then
    usage
    exit 2
fi

ARGS_FILE="${POSITIONALS[0]}"

# Same resolution as scripts/test_run.sh / scripts/parameters.sh: a path as
# given, a bare stem under scripts/arg_files, or that stem with .md appended.
if [[ -f "${ARGS_FILE}" ]]; then
    :
elif [[ -f "${SCRIPT_DIR}/arg_files/${ARGS_FILE}.md" ]]; then
    ARGS_FILE="${SCRIPT_DIR}/arg_files/${ARGS_FILE}.md"
elif [[ -f "${SCRIPT_DIR}/arg_files/${ARGS_FILE}" ]]; then
    ARGS_FILE="${SCRIPT_DIR}/arg_files/${ARGS_FILE}"
else
    printf 'Arguments file not found: %s\n' "${ARGS_FILE}" >&2
    exit 1
fi

if grep -qE '^--cold_split([[:space:]=]|$)' "${ARGS_FILE}"; then
    printf '%s uses --cold_split, which this script does not implement (it needs\n' "${ARGS_FILE}" >&2
    printf 'the per-group val/test pairing from submit_cold_val_test_all_seeds.sh).\n' >&2
    printf 'Run it on a cluster instead: bash scripts/run_bigfoot.sh %s\n' "${ARGS_FILE}" >&2
    exit 2
fi

variant="$(basename "${ARGS_FILE}" .md)"
# Strip quotes around a flag's value (scripts/parameters.sh does the same, for
# the same reason): --pool_type="gem" survives unquoted word-splitting fine
# when this is interpolated below, but bash does not re-interpret quote
# characters inside an already-expanded variable, so the literal quotes would
# reach read_configuration.py as part of the value and fail its POOL_TYPES
# check. Without this, any arg file with a quoted string value (arg_files/
# *GRL_dp_rmpft*.md's --pool_type="gem" among them) fails at config parsing,
# before a single job's process even starts.
args_template="$(grep '^--' "${ARGS_FILE}" | sed -E 's/^(--[^=]+=)"?([^"]*)"?$/\1\2/' | tr '\n' ' ')"

excl_groups=(
    "CRAL-TRIO"
    "START"
    "lipocalin"
    "GLTP"
    "IP_trans"
    "LBP_BPI_CETP"
    "scp2"
    "ML"
    "OSBP"
)
seeds=(0 1 2 3 4)

if [[ -n "${GROUPS_ARG:-}" ]]; then
    read -r -a excl_groups <<< "${GROUPS_ARG//,/ }"
fi
if [[ -n "${SEEDS_ARG:-}" ]]; then
    read -r -a seeds <<< "${SEEDS_ARG//,/ }"
    for _seed in "${seeds[@]}"; do
        if [[ ! "${_seed}" =~ ^[0-9]+$ ]]; then
            printf 'Invalid seed (must be a non-negative integer): %s\n' "${_seed}" >&2
            exit 2
        fi
    done
fi

# Flatten the group x seed grid into two parallel arrays up front, so the
# launch loop below just indexes a job count instead of nesting the nproc/N
# split inside two loops.
job_groups=()
job_seeds=()
declare -A completed_pairs=()
if [[ "${COMPLETE_ONLY:-0}" == "1" ]]; then
    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && completed_pairs["${pair}"]=1
    done < <(python3 "${SCRIPT_DIR}/list_completed_experiments.py" \
        "${variant}" --reports-root "${PROJECT_ROOT}/test_metrics")
fi
for group in "${excl_groups[@]}"; do
    for seed in "${seeds[@]}"; do
        if [[ -n "${completed_pairs["${group}:${seed}"]:-}" ]]; then
            printf 'Skipping completed experiment: group=%s seed=%s.\n' \
                "${group}" "${seed}"
            continue
        fi
        job_groups+=("${group}")
        job_seeds+=("${seed}")
    done
done
total_jobs=${#job_groups[@]}
if (( total_jobs == 0 )); then
    printf 'All requested group/seed pairs already have final test_metrics.\n'
    exit 0
fi

nproc_count="$(nproc)"
# Derive the desktop reserve from the machine instead of carrying the old
# 24-CPU workstation's fixed value onto smaller computers. A quarter leaves
# useful headroom on both known hosts; the minimum of two keeps a small desktop
# responsive. Explicit RESERVED_CORES still wins.
default_reserved_cores=$(( nproc_count / 4 ))
if (( default_reserved_cores < 2 )); then default_reserved_cores=2; fi
RESERVED_CORES="${RESERVED_CORES:-${default_reserved_cores}}"
usable_cores=$(( nproc_count - RESERVED_CORES ))
if (( usable_cores < 1 )); then usable_cores=1; fi

# Memory cap. This is not optional headroom the way RESERVED_CORES is -- a
# LOCAL_JOBS=22 run on this machine (24 cores, 31 GiB RAM) OOM-killed GNOME
# Shell itself along with several terminals: CPU and memory are independent
# budgets, and cores were never the resource actually being exhausted.
#
# MEM_PER_JOB_GIB is the MARGINAL cost of one more concurrent job, not one
# job's own RSS in isolation -- summing per-process RSS overestimates badly,
# because a large share of it is libtorch/MKL shared-library pages the kernel
# maps once and shares across every process running the same binary, not
# once per process. Measured directly on this machine, the heaviest config
# used so far (1.28M params, adversarial_grl+adv_deep+balanced_batches):
# system-wide `used` memory rose from an ~8.5 GiB idle baseline to a 25.75 GiB
# peak running 6 of them at once -- (25.75-8.5)/6 =~ 2.9 GiB per job, not the
# ~5.4 GiB a single isolated process's own RSS suggested. Rounded up to 4 for
# margin (this was one config over one ~3-minute, 3-epoch window, not a full
# multi-hour run where e.g. a new best-epoch checkpoint's
# copy.deepcopy(model.state_dict()) could add a transient spike this did not
# catch).
MEM_PER_JOB_GIB="${MEM_PER_JOB_GIB:-4}"
# Memory equivalent of RESERVED_CORES: kept separate (not derived from it)
# because the two resources are unrelated, and the failure mode here is worse
# than a slow desktop -- the OOM killer picks whatever it wants, which is how
# GNOME Shell itself died rather than one of the training jobs. Set from the
# same measurement: idle baseline on this machine was ~8.5 GiB, so reserving
# only 6 (an earlier, unmeasured guess) left jobs assuming they could use RAM
# the desktop was already sitting on.
RESERVED_MEM_GIB="${RESERVED_MEM_GIB:-9}"
total_mem_gib=$(( $(awk '/^MemTotal:/ {print $2}' /proc/meminfo) / 1024 / 1024 ))
mem_available_gib=$(( total_mem_gib - RESERVED_MEM_GIB ))
if (( mem_available_gib < MEM_PER_JOB_GIB )); then mem_available_gib=${MEM_PER_JOB_GIB}; fi
mem_max_jobs=$(( mem_available_gib / MEM_PER_JOB_GIB ))
if (( mem_max_jobs < 1 )); then mem_max_jobs=1; fi

# Default LOCAL_JOBS to the actual maximum under BOTH budgets -- one job per
# usable core, capped by how many jobs fit in usable RAM, whichever is lower
# -- rather than a throughput-tuned guess: that number was never cleanly
# measured for every config this runs (only for a lighter one, at N up to 6),
# so instead of defending an unproven "optimal" default this hands out every
# usable core as its own job slot, up to what memory allows. Override
# LOCAL_JOBS directly for anything else (fewer, wider jobs; a throughput
# sweet spot once one is actually measured for the config in hand) -- doing
# that skips both caps, on the assumption an explicit override means the
# caller has already accounted for memory themselves.
LOCAL_JOBS="${LOCAL_JOBS:-$(( usable_cores < mem_max_jobs ? usable_cores : mem_max_jobs ))}"
if (( LOCAL_JOBS < 1 )); then LOCAL_JOBS=1; fi
if (( LOCAL_JOBS > total_jobs )); then LOCAL_JOBS=${total_jobs}; fi
OMP_THREADS_PER_JOB="${OMP_THREADS_PER_JOB:-$(( usable_cores / LOCAL_JOBS ))}"
if (( OMP_THREADS_PER_JOB < 1 )); then OMP_THREADS_PER_JOB=1; fi
MAX_OMP_THREADS_PER_JOB="${MAX_OMP_THREADS_PER_JOB:-4}"
if (( OMP_THREADS_PER_JOB > MAX_OMP_THREADS_PER_JOB )); then
    OMP_THREADS_PER_JOB="${MAX_OMP_THREADS_PER_JOB}"
fi
NUM_WORKERS_PER_JOB="${NUM_WORKERS_PER_JOB:-1}"

output_dir_root="script_logs/${variant}_seeds$(IFS=; echo "${seeds[*]}")"

# Tag matching wait_progress_table.sh's LOCAL_JOB_TAG there: bigfoot's OAR
# .out files carry no tag, kraken's carry "k", this carries "l" -- three
# disjoint id namespaces (two clusters' OAR job ids, this script's pids) over
# the same tag+id naming, which is what lets script_logs/ hold all three
# sources of logs at once without a filename ever colliding.
LOCAL_JOB_TAG="l"

# Jobs this invocation has not started yet, as "variant<TAB>group<TAB>seed"
# lines -- wait_and_sync.sh/wait_and_sync2.sh read this to show a "(queued)"
# row for each and to count WAITING in the summary table, the same way
# .bigfoot_job_queues/active/pending.commands does for OAR. Popped from the
# top as each job launches; removed entirely on exit (the trap below), success
# or failure, so a dead invocation never leaves phantom queued rows behind.
local_queue_file="${PROJECT_ROOT}/script_logs/local_run.queue"
mkdir -p "${PROJECT_ROOT}/script_logs"
: > "${local_queue_file}"
for (( i=0; i<total_jobs; i++ )); do
    printf '%s\t%s\t%s\n' "${variant}" "${job_groups[i]}" "${job_seeds[i]}" >> "${local_queue_file}"
done
trap 'rm -f "${local_queue_file}"' EXIT

printf 'Running %d jobs (%d groups x %d seeds) from %s.\n' \
    "${total_jobs}" "${#excl_groups[@]}" "${#seeds[@]}" "${variant}"
printf 'LOCAL_JOBS=%d OMP_THREADS_PER_JOB=%d NUM_WORKERS_PER_JOB=%d\n' \
    "${LOCAL_JOBS}" "${OMP_THREADS_PER_JOB}" "${NUM_WORKERS_PER_JOB}"
printf '  cores: %d usable of %d (%d reserved for the desktop)\n' \
    "${usable_cores}" "${nproc_count}" "${RESERVED_CORES}"
printf '  memory: %d GiB usable of %d (%d reserved), %d GiB/job -> caps at %d concurrent job(s)\n' \
    "${mem_available_gib}" "${total_mem_gib}" "${RESERVED_MEM_GIB}" "${MEM_PER_JOB_GIB}" "${mem_max_jobs}"

pids=()
failed=0
for (( job_index=0; job_index<total_jobs; job_index++ )); do
    group="${job_groups[job_index]}"
    seed="${job_seeds[job_index]}"
    output_dir="${output_dir_root}/${group}"
    mkdir -p "${output_dir}"
    log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"

    printf '=== [%d/%d] GROUP: %s | VARIANT: %s | SEED: %s ===\n' \
        "$(( job_index + 1 ))" "${total_jobs}" "${group}" "${variant}" "${seed}"

    # read_configuration.py applies flags in argv order and the last one wins,
    # so appending --num_workers here would silently override an args file
    # that sets its own (e.g. arg_files/test.md uses --num_workers=0 for
    # deterministic single-process debugging). Only fill it in when the args
    # file is silent about it.
    num_workers_flag=()
    if ! grep -qE '^--num_workers(=|$)' "${ARGS_FILE}"; then
        num_workers_flag=(--num_workers="${NUM_WORKERS_PER_JOB}")
    fi

    # shellcheck disable=SC2086
    OMP_NUM_THREADS="${OMP_THREADS_PER_JOB}" MKL_NUM_THREADS="${OMP_THREADS_PER_JOB}" \
    PYTHONUNBUFFERED=1 python3 ./training/new_train.py \
        ${args_template} \
        --label="${variant}" \
        --seed="${seed}" \
        --excluded_groups="${group}" \
        "${num_workers_flag[@]}" \
        > "${log_file}" 2>&1 &
    pids+=($!)

    # Job-id-tagged .out, symlinked to the friendlier stable-named .log so
    # scripts/wait_progress_table.sh's local-jobs lookup (print_local_progress,
    # keyed on "*_l<pid>.out", the same convention as the cluster's
    # "*_<tag><oar job id>.out") can find this run while it is live. The pid is
    # only known after backgrounding, so this comes after `pids+=($!)`, not
    # before -- the .log redirect target above had to be pid-free from the
    # start, which is also why it is the real file and .out is the symlink
    # rather than the other way around.
    out_file="${output_dir}/${variant}_seed${seed}_${LOCAL_JOB_TAG}${pids[-1]}.out"
    ln -sf "$(basename "${log_file}")" "${out_file}"

    # This job is no longer queued -- pop its line (jobs launch in the same
    # order local_queue_file was written in, so it is always the first line).
    tail -n +2 "${local_queue_file}" > "${local_queue_file}.tmp"
    mv "${local_queue_file}.tmp" "${local_queue_file}"

    # One-second stagger between launches: new_train.py names its TensorBoard
    # run directory train<timestamp>_..._<seed>_..., retrying with a 1s sleep
    # (training/new_train.py, the os.makedirs/FileExistsError loop) only if
    # that exact name already exists. seed differs per job here so it can't
    # collide, but staggering keeps launches readable in the terminal and
    # matches how oarsub submissions on bigfoot/kraken are naturally spaced by
    # SSH round-trip time -- jobs there are never launched in the same second.
    if (( job_index + 1 < total_jobs )); then
        sleep 1
    fi

    if (( ${#pids[@]} >= LOCAL_JOBS )); then
        # Poll rather than `wait -n`: wait -n reaps ONE job anonymously and
        # discards its exit status, and a later `wait "${pid}"` on that same
        # pid cannot recover it (bash has already forgotten it, so a second
        # wait on it is either an error or a meaningless status). That used to
        # lose the exit status of every job it silently reaped this way -- for
        # slow jobs a rare event, but jobs that all die in under a second
        # (e.g. a whole grid launched without the conda env active) can finish
        # several at a time between one stagger tick and the next, and this is
        # exactly how a run once reported "1 job(s) exited non-zero" when in
        # fact all 18 had. Reaping only pids confirmed dead by kill -0, and
        # each exactly once via `wait "${pid}"` right here, cannot lose one.
        while :; do
            still_running=()
            finished=()
            for pid in "${pids[@]}"; do
                if kill -0 "${pid}" 2>/dev/null; then
                    still_running+=("${pid}")
                else
                    finished+=("${pid}")
                fi
            done
            (( ${#finished[@]} > 0 )) && break
            sleep 0.2
        done
        for pid in "${finished[@]}"; do
            wait "${pid}" || failed=$((failed + 1))
        done
        pids=("${still_running[@]}")
    fi
done

for pid in "${pids[@]}"; do
    wait "${pid}" || failed=$((failed + 1))
done

printf 'Ran %d jobs %s across %d groups and %d seeds.\n' \
    "${total_jobs}" "${variant}" "${#excl_groups[@]}" "${#seeds[@]}"
if (( failed > 0 )); then
    printf '%d job(s) exited non-zero; check the logs under %s.\n' "${failed}" "${output_dir_root}" >&2
fi

# Chain to the next queued batch, if any -- see the "already active" branches
# above, where a second invocation appends itself to PENDING_BATCHES_FILE
# instead of being silently dropped. This runs regardless of whether THIS
# batch had failures: a bad config in one queued batch must not strand every
# batch queued behind it. exec (not a fresh launch) replaces this process in
# place, so the next batch continues under the same detached session, pid and
# log file; RUN_LOCAL_DETACHED is already set in this process's own
# environment, so the next invocation will not try to self-detach again.
if [[ -s "${PENDING_BATCHES_FILE}" ]]; then
    next_batch="$(head -n 1 "${PENDING_BATCHES_FILE}")"
    tail -n +2 "${PENDING_BATCHES_FILE}" > "${PENDING_BATCHES_FILE}.tmp"
    mv "${PENDING_BATCHES_FILE}.tmp" "${PENDING_BATCHES_FILE}"
    printf 'Starting next queued batch: %s\n' "${next_batch}"
    # exec does not run EXIT traps -- it replaces this process outright rather
    # than exiting it -- so this batch's own queue file (normally cleaned up
    # by the `trap ... EXIT` above) needs an explicit remove here. Already
    # empty in the ordinary case (every job popped its own line on launch);
    # this is just making sure rather than assuming.
    rm -f "${local_queue_file}"
    eval "set -- ${next_batch}"
    exec bash "${BASH_SOURCE[0]}" "$@"
fi

if (( failed > 0 )); then
    exit 1
fi
