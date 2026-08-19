#!/usr/bin/env bash
# Local entry point: run this project's group x seed grid as parallel processes
# on this machine, instead of queuing OAR jobs on bigfoot/kraken.
#
# Analogous to run_bigfoot.sh / run_kraken.sh + launch/submit_grid.sh,
# but there is only one local target, so sync/preflight/oarsub/wait_and_sync do
# not apply: this script resolves the args file, builds the group x seed grid,
# and runs it directly through a bounded local job queue.
#
# Usage: bash scripts/run_local.sh [--complete] [--seeds=LIST] [--groups=LIST]
#                                  [--no_groups=LIST] ARGS_FILE
# Example: bash scripts/run_local.sh scripts/arg_files/standard.md
# Example: bash scripts/run_local.sh --seeds=0,1,2 nps3mlp_gat_residual
# Example: bash scripts/run_local.sh --no_groups=GLTP nps3mlp_gat_residual
#
#   --seeds=LIST     Comma/space-separated seeds. Default: 0,1,2,3,4 (same as
#                     run_cluster.sh).
#   --groups=LIST    Comma/space-separated excluded groups. Default: the 9
#                     canonical groups.
#   --no_groups=LIST Drop these groups from the list above, so leaving one group
#                     out of a full run does not mean spelling out the other 8.
#   --complete       Run only requested group/seed pairs without final test_metrics.
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
#                           RESERVED_CORES but for memory. Default: 2 -- margin
#                           on top of the free memory the kernel reports, NOT an
#                           assumption about how much the desktop is using (that
#                           is measured, see below).
#   MEM_PER_JOB_GIB         RAM budgeted per job. Setting it FIXES the budget at
#                           that value and turns the measurement below off; left
#                           unset, it is only the bootstrap for the first jobs
#                           (default 2) and the real figure is measured from the
#                           jobs themselves as soon as one is training. What is
#                           budgeted is the MARGINAL cost of one more concurrent
#                           job, not one job's own RSS in isolation (summing
#                           isolated RSS overestimates: shared libtorch/MKL
#                           pages are not duplicated per process). THIS IS THE
#                           BINDING CONSTRAINT ON THIS MACHINE, not cores: a
#                           LOCAL_JOBS=22 run (basing the job count on cores
#                           alone, before this cap existed) exhausted the 31 GiB
#                           of RAM here and the OOM killer took out GNOME Shell
#                           itself along with several terminals. CPU and memory
#                           are independent budgets; nothing about reserving
#                           cores protects against this.
#   MEM_MARGIN_PERCENT      Margin added to the measured figure. Default: 30 --
#                           covers what a snapshot cannot see (a best-epoch
#                           state_dict copy, the end-of-run test pass) and the
#                           drift of a long run.
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
    printf 'Usage: bash %s [--complete] [--seeds=LIST] [--groups=LIST] [--no_groups=LIST] ARGS_FILE\n' "${0##*/}" >&2
    printf 'Example: bash %s scripts/arg_files/standard.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --seeds=0,1,2 nps3mlp_gat_residual\n' "${0##*/}" >&2
    printf 'Example: bash %s --no_groups=GLTP nps3mlp_gat_residual\n' "${0##*/}" >&2
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
# machine) does not kill a grid that is still running. Unlike a cluster job,
# which OAR keeps running whatever happens here, a local grid IS this machine's
# process. tmux is not installed on every machine this runs on (checked here at run time, nothing is installed to fix
# that) and the caller may not be able to install it either, so this falls
# back to setsid+nohup, which need nothing beyond coreutils/util-linux that
# every one of this project's machines already has. Both paths give the same
# guarantee: the training processes keep running detached from the shell that
# launched them; only the log-tailing in this terminal stops on Ctrl-C or on
# the client machine going away.
#
# RUN_LOCAL_TMUX=0 opts out of both, and the relaunch sets it so the detached
# copy does not try to detach again.
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
    if ! source "${SCRIPT_DIR}/lib/activate_training_env.sh"; then
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
        --no_groups=*)
            SKIP_GROUPS_ARG="${1#*=}"
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

# A path as given, a bare stem under scripts/arg_files, or that stem with .md
# appended -- the same three spellings every other launcher accepts, from the one
# implementation in scripts/lib/args_file_lib.sh.
# shellcheck source=scripts/lib/args_file_lib.sh
source "${SCRIPT_DIR}/lib/args_file_lib.sh"

if ! ARGS_FILE="$(resolve_args_file "${ARGS_FILE}")"; then
    printf 'Arguments file not found: %s\n' "${ARGS_FILE}" >&2
    exit 1
fi

if args_file_has_flag "${ARGS_FILE}" --cold_split; then
    printf '%s uses --cold_split, which this script does not implement (it needs\n' "${ARGS_FILE}" >&2
    printf 'the per-group val/test pairing that launch/submit_grid.sh applies).\n' >&2
    printf 'Run it on a cluster instead: bash scripts/run_bigfoot.sh %s\n' "${ARGS_FILE}" >&2
    exit 2
fi

variant="$(basename "${ARGS_FILE}" .md)"
args_template="$(args_file_flags "${ARGS_FILE}")"

# shellcheck source=scripts/settings.sh
source "${SCRIPT_DIR}/settings.sh"
excl_groups=("${PROTEIN_GROUPS[@]}")
seeds=("${DEFAULT_SEEDS[@]}")

if [[ -n "${GROUPS_ARG:-}" ]]; then
    read -r -a excl_groups <<< "${GROUPS_ARG//,/ }"
fi

# --no_groups is the complement of --groups: drop these from whatever list is
# active (the 9 canonical groups, or an explicit --groups), which is what a full
# run minus one group wants -- the whitelist alone forces spelling out the other
# eight. Names are matched by normalize_group_name (scripts/settings.sh),
# so the same spellings that work for --excluded_groups work here
# (case-insensitive, - and _ interchangeable: cral_trio == CRAL-TRIO).
if [[ -n "${SKIP_GROUPS_ARG:-}" ]]; then
    read -r -a skip_groups <<< "${SKIP_GROUPS_ARG//,/ }"
    declare -A skip_matched=()
    kept_groups=()
    for group in "${excl_groups[@]}"; do
        keep=1
        for skipped in "${skip_groups[@]}"; do
            if [[ "$(normalize_group_name "${group}")" \
                  == "$(normalize_group_name "${skipped}")" ]]; then
                keep=0
                skip_matched["$(normalize_group_name "${skipped}")"]=1
            fi
        done
        (( keep == 1 )) && kept_groups+=("${group}")
    done
    # A name that matches nothing is an error, not a silent no-op: the whole
    # point of this flag is NOT running a group, so a typo would quietly spend
    # hours training the very group the caller meant to leave out.
    for skipped in "${skip_groups[@]}"; do
        if [[ -z "${skip_matched["$(normalize_group_name "${skipped}")"]:-}" ]]; then
            printf -- '--no_groups names a group that is not being run: %s\n' "${skipped}" >&2
            printf 'Groups in this run: %s\n' "${excl_groups[*]}" >&2
            exit 2
        fi
    done
    if (( ${#kept_groups[@]} == 0 )); then
        printf -- '--no_groups excluded every group; nothing left to run.\n' >&2
        exit 2
    fi
    excl_groups=("${kept_groups[@]}")
fi

# --lipid_coldsplit in the args file is the OTHER axis: whole chemical families of
# lipids leave training while every protein stays. There is no held-out protein group
# then, so the grid iterates the lipid sets instead -- one run per set, four in all.
# The bare flag is stripped from the template because the trainer only accepts the
# named form, which is appended per run below.
lipid_coldsplit_sets=()
if args_file_has_flag "${ARGS_FILE}" --lipid_coldsplit; then
    if [[ -n "${GROUPS_ARG:-}${SKIP_GROUPS_ARG:-}" ]]; then
        printf -- '--lipid_coldsplit runs over lipid sets, not protein groups; '\
'--groups/--no_groups do not apply.\n' >&2
        exit 2
    fi
    # Keep in step with LIPID_COLDSPLIT_SETS (dataloader/sampler.py) and
    # LIPID_COLDSPLIT_NAMES (training/read_configuration.py); a name absent from either
    # is rejected at parse time, so a drift here fails loudly on the first run.
    lipid_coldsplit_sets=(sphingolipids phosphorus_free choline anionic)
    excl_groups=("${lipid_coldsplit_sets[@]}")
    args_template="$(printf '%s' "${args_template}" \
        | sed -E 's/(^|[[:space:]])--lipid_coldsplit([[:space:]]|$)/\1/g')"
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
# split inside two loops. The grid itself, and the skipping of pairs that
# already have a final test report, come from scripts/lib/grid_lib.sh -- the same
# ones the cluster submitters use, so --complete means the same thing here.
# shellcheck source=scripts/lib/grid_lib.sh
source "${SCRIPT_DIR}/lib/grid_lib.sh"

grid_load_completed "${variant}" "${PROJECT_ROOT}/test_metrics" 0

job_groups=()
job_seeds=()
while IFS=$'\t' read -r group seed; do
    [[ -n "${group}" ]] || continue
    job_groups+=("${group}")
    job_seeds+=("${seed}")
done < <(grid_pairs "${excl_groups[*]}" "${seeds[*]}")
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
# catch). A later, finer measurement on the 12-CPU/13 GiB laptop put it lower:
# per-process PSS (which, unlike RSS, splits those shared pages across the
# processes mapping them instead of counting them once per process) came to
# 1.25 GiB for the main process and 0.72 GiB for its one DataLoader worker --
# 2.0 GiB per job, on the same heavy adversarial_grl+adv_deep config. Hence 2
# Hence 2. A config heavier than any measured here wants an explicit
# MEM_PER_JOB_GIB, which is what the override is for.
#
# All of those numbers are measurements of ONE config on ONE machine, carried as a
# constant into every other config -- which is exactly what went wrong in both
# directions: 2 GiB/job is roughly double what this project's lighter configs
# actually take (measured 1.13 GiB PSS per job for a 1.0M-parameter run with
# --num_workers=0, where the 0.72 GiB DataLoader worker of the measurement above
# does not exist), and it would be too little for a config heavier than any tried
# so far. So the constant is now only the bootstrap for the first jobs, and the
# budget is re-derived from the jobs actually running -- see update_job_budget
# below. An explicitly set MEM_PER_JOB_GIB still wins and switches the
# measurement off, because a caller who names a number has usually measured
# something this script cannot see.
if [[ -n "${MEM_PER_JOB_GIB+set}" ]]; then
    MEM_PER_JOB_FIXED=1
else
    MEM_PER_JOB_FIXED=0
fi
MEM_PER_JOB_GIB="${MEM_PER_JOB_GIB:-2}"
# The budget in MiB, which is what everything below works in: a measured figure has
# no reason to land on a whole gibibyte, and rounding it up to one would give back
# most of what measuring gained.
MEM_PER_JOB_MIB=$(( MEM_PER_JOB_GIB * 1024 ))
MEM_MARGIN_PERCENT="${MEM_MARGIN_PERCENT:-30}"
# Memory equivalent of RESERVED_CORES: kept separate (not derived from it)
# because the two resources are unrelated, and the failure mode here is worse
# than a slow desktop -- the OOM killer picks whatever it wants, which is how
# GNOME Shell itself died rather than one of the training jobs.
#
# What the jobs' budget is taken FROM is MemAvailable -- the kernel's own
# estimate of what can be allocated right now without swapping -- not MemTotal
# minus a guessed idle baseline. The old form (MemTotal - 9, where 9 was one
# particular desktop's measured footprint) travelled badly: the same constant on
# a 13 GiB laptop left (13-9)/4 = 1, i.e. no parallelism at all, while that
# machine actually had ~10 GiB free. Whatever the desktop, browser and editors
# are using is already subtracted from MemAvailable, on the machine in hand, at
# the moment of the run -- nothing has to be assumed about it. RESERVED_MEM_GIB
# is therefore margin on top of an already conservative number, hence 2 not 9.
RESERVED_MEM_GIB="${RESERVED_MEM_GIB:-2}"
total_mem_gib=$(( $(awk '/^MemTotal:/ {print $2}' /proc/meminfo) / 1024 / 1024 ))

# MiB of memory a new job may be given right now: what the kernel says can be
# allocated without swapping, less the reserve. Read fresh every time, never cached
# -- the whole point of re-deriving the budget during the run is that both sides of
# the division change while it runs.
mem_headroom_mib() {
    local available
    available=$(( $(awk '/^MemAvailable:/ {print $2}' /proc/meminfo) / 1024 \
        - RESERVED_MEM_GIB * 1024 ))
    (( available < 0 )) && available=0
    printf '%d\n' "${available}"
}

mem_free_gib=$(( $(awk '/^MemAvailable:/ {print $2}' /proc/meminfo) / 1024 / 1024 ))
mem_available_mib="$(mem_headroom_mib)"
mem_max_jobs=$(( mem_available_mib / MEM_PER_JOB_MIB ))
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
if [[ -n "${LOCAL_JOBS+set}" ]]; then
    LOCAL_JOBS_FIXED=1
else
    LOCAL_JOBS_FIXED=0
fi
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

# Pin each job to one last-level-cache domain. Unpinned, the kernel is free to
# move a job's threads between domains, and on a machine whose L3 is split (the
# 6-core Ryzen here has two 4 MiB domains, cpu 0-5 and cpu 6-11) every such
# migration throws away that job's cached working set -- the model's parameters
# alone are ~3 MB, nearly a whole domain -- and it has to be fetched from RAM
# again. Pinning removes the migrations and nothing else: the thread COUNT is
# untouched, so at::parallel_for splits every reduction exactly as before and the
# run's numbers stay bit-identical. That is the whole point -- this file must not
# acquire a speedup that costs a metric.
#
# Domains are read off the machine rather than hardcoded, because they differ per
# CPU (one domain on a desktop Zen with a single CCX, two here, more on a server).
# A kernel that does not expose index3, or a machine without taskset, simply runs
# unpinned exactly as before.
#
# Jobs are handed domains round-robin by launch index. Since jobs launch in order
# and LOCAL_JOBS of them run at a time, consecutive indices are what is
# concurrently live, so round-robin spreads them evenly over the domains without
# this script having to track which slot freed up.
JOB_CPU_DOMAINS=()
if command -v taskset >/dev/null 2>&1; then
    while IFS= read -r cpu_domain; do
        [[ -n "${cpu_domain}" ]] && JOB_CPU_DOMAINS+=("${cpu_domain}")
    done < <(cat /sys/devices/system/cpu/cpu*/cache/index3/shared_cpu_list \
        2>/dev/null | sort -u)
fi

output_dir_root="script_logs/${variant}_seeds$(IFS=; echo "${seeds[*]}")"

# Tag matching lib/progress_table.sh's LOCAL_JOB_TAG there: bigfoot's OAR
# .out files carry no tag, kraken's carry "k", this carries "l" -- three
# disjoint id namespaces (two clusters' OAR job ids, this script's pids) over
# the same tag+id naming, which is what lets script_logs/ hold all three
# sources of logs at once without a filename ever colliding.
LOCAL_JOB_TAG="l"

# Jobs this invocation has not started yet, as "variant<TAB>group<TAB>seed"
# lines -- the watchers read this to show a "(queued)"
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
printf '  memory: %d MiB usable of %d GiB free now (%d total, %d reserved), %d MiB/job (%s) -> caps at %d concurrent job(s)\n' \
    "${mem_available_mib}" "${mem_free_gib}" "${total_mem_gib}" "${RESERVED_MEM_GIB}" \
    "${MEM_PER_JOB_MIB}" \
    "$( (( MEM_PER_JOB_FIXED )) && printf 'fixed by MEM_PER_JOB_GIB' \
        || printf 'bootstrap, re-measured once a job is training')" \
    "${mem_max_jobs}"
if (( ${#JOB_CPU_DOMAINS[@]} > 0 )); then
    printf '  pinning: %d cache domain(s), one per job round-robin: %s\n' \
        "${#JOB_CPU_DOMAINS[@]}" "${JOB_CPU_DOMAINS[*]}"
else
    printf '  pinning: none (no taskset or no cache topology exposed)\n'
fi

# Build the memory-mapped lipid embedding store before the first job starts. Each job
# would otherwise unpickle the whole table into itself -- 267 MiB resident and about a
# gigabyte of transient peak for the deterministic table -- so on this machine four
# concurrent jobs paid for it four times, and that peak, not the cores, is what the
# MEM_PER_JOB_GIB cap above is mostly budgeting for. Built once here, the table is
# mapped instead of read and the jobs share one copy through the page cache.
#
# Here rather than inside a job because LOCAL_JOBS of them start a second apart and
# would race to write the same archive. Never fatal: without the store the jobs read
# the pickle exactly as before, which is slower and heavier but not wrong. Already
# current means no work, so relaunching a grid costs nothing.
if ! python3 "${PROJECT_ROOT}/data/build_lipid_embedding_store.py" \
    --args_file="${ARGS_FILE}"; then
    printf 'WARNING: could not build the embedding store; jobs will read the pickle.\n' >&2
fi

# --- the memory budget, measured rather than assumed -----------------------------
#
# What one more concurrent job costs is a property of the config, not of this
# machine: the same script runs a 481k-parameter model with no DataLoader worker and
# a 1.28M-parameter adversarial one with two, and their real footprints differ by
# more than a factor of two. A constant therefore has to be wrong in one direction or
# the other, and both directions hurt -- too high wastes half the machine, too low
# hands the OOM killer a choice it makes badly. So the constant is used only until
# there is something to measure, and from the first training job onwards the budget
# is what the running jobs actually occupy.
#
# PSS, not RSS: it divides each shared page among the processes mapping it, so the
# libtorch and MKL text pages, and the mmapped embedding stores, are counted once in
# total instead of once per job. Summed over the jobs it is very nearly their true
# joint footprint, which makes the mean the cost of one more of them -- the same
# quantity the fixed constant was always trying to name.

# The whole process tree of one job, in KiB. DataLoader workers are children and
# their memory is as real as their parent's, so a job is the tree, not the process.
job_tree_pss_kib() {
    local root="$1" pid value total=0
    for pid in "${root}" $(pgrep -P "${root}" 2>/dev/null || true); do
        value="$(awk '/^Pss:/ {print $2; exit}' "/proc/${pid}/smaps_rollup" 2>/dev/null || true)"
        # smaps_rollup needs a 4.14 kernel and a readable process; VmRSS is always
        # there, and overestimating is the safe way to be wrong about a budget.
        [[ -n "${value}" ]] || value="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/${pid}/status" 2>/dev/null || true)"
        [[ -n "${value}" ]] && total=$(( total + value ))
    done
    printf '%d\n' "${total}"
}

# Mean MiB per running job, or nothing if none can be read.
measure_job_memory_mib() {
    local pid tree total=0 count=0
    for pid in "${pids[@]}"; do
        kill -0 "${pid}" 2>/dev/null || continue
        tree="$(job_tree_pss_kib "${pid}")"
        (( tree > 0 )) || continue
        total=$(( total + tree ))
        count=$(( count + 1 ))
    done
    (( count > 0 )) || return 1
    printf '%d\n' $(( total / count / 1024 ))
}

# Re-derive how many jobs may run at once, from the measured cost and the memory free
# at this moment. Called before every launch and after every job that finishes, so a
# grid that starts under a loaded desktop widens as the desktop lets go, and one that
# meets a heavier config than expected narrows instead of meeting the OOM killer.
update_job_budget() {
    (( LOCAL_JOBS_FIXED )) && return 0
    local measured headroom affordable cap
    if (( ! MEM_PER_JOB_FIXED )) && [[ -n "${first_log_file}" ]] \
        && grep -q '^EPOCH ' "${first_log_file}" 2>/dev/null; then
        # Measured only once a job is past dataset construction and into its first
        # epoch: before that the model, the optimizer state and the sample caches are
        # not allocated yet, and a snapshot taken then would budget for a job that
        # does not exist. Re-measured every time rather than once, because a run's
        # footprint drifts and because the mean falls as later jobs share more pages.
        if measured="$(measure_job_memory_mib)"; then
            measured=$(( measured * (100 + MEM_MARGIN_PERCENT) / 100 ))
            # Never zero: it is a divisor below, and a job that measures as free is a
            # broken measurement rather than a job that costs nothing.
            (( measured < 1 )) && measured=1
            # Said out loud only when it moves by more than 5%. Re-measured before
            # every launch, the figure drifts by a megabyte at a time, and a line per
            # launch would bury the launches themselves.
            if (( measured * 20 < MEM_PER_JOB_MIB * 19 || measured * 20 > MEM_PER_JOB_MIB * 21 )); then
                printf '  memory: measured %d MiB/job over %d running job(s), margin included\n' \
                    "${measured}" "${#pids[@]}"
            fi
            MEM_PER_JOB_MIB=${measured}
        fi
    fi
    (( MEM_PER_JOB_MIB > 0 )) || MEM_PER_JOB_MIB=1
    headroom="$(mem_headroom_mib)"
    affordable=$(( headroom / MEM_PER_JOB_MIB ))
    cap=$(( ${#pids[@]} + affordable ))
    # OMP_THREADS_PER_JOB was fixed before the first job started and must stay fixed:
    # the thread count decides how at::parallel_for splits every reduction, so
    # changing it mid-grid would make the second half of a run's numbers incomparable
    # with the first. Widening therefore stops where the cores run out at the thread
    # count already handed out, not where memory does.
    local core_cap=$(( usable_cores / OMP_THREADS_PER_JOB ))
    (( core_cap < 1 )) && core_cap=1
    (( cap > core_cap )) && cap=${core_cap}
    (( cap > total_jobs )) && cap=${total_jobs}
    (( cap < 1 )) && cap=1
    LOCAL_JOBS=${cap}
}

# Wait for at least one running job to exit, then reap every job that has, exactly
# once each.
#
# Poll rather than `wait -n`: wait -n reaps ONE job anonymously and discards its exit
# status, and a later `wait "${pid}"` on that same pid cannot recover it (bash has
# already forgotten it, so a second wait on it is either an error or a meaningless
# status). That used to lose the exit status of every job it silently reaped this way
# -- for slow jobs a rare event, but jobs that all die in under a second (e.g. a whole
# grid launched without the conda env active) can finish several at a time between one
# stagger tick and the next, and this is exactly how a run once reported "1 job(s)
# exited non-zero" when in fact all 18 had. Reaping only pids confirmed dead by
# kill -0, and each exactly once via `wait "${pid}"` right here, cannot lose one.
reap_finished_jobs() {
    local pid
    local still_running=() finished=()
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
}

pids=()
failed=0
# The log of the first job launched, which is what tells the budget when there is
# something worth measuring.
first_log_file=""
for (( job_index=0; job_index<total_jobs; job_index++ )); do
    group="${job_groups[job_index]}"
    seed="${job_seeds[job_index]}"
    output_dir="${output_dir_root}/${group}"
    mkdir -p "${output_dir}"
    log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"

    # BEFORE the launch, not after it: the cap has to be met by not starting a job,
    # which is the one moment where refusing still costs nothing. Re-derived inside
    # the wait too, so a job finishing or the desktop freeing memory is noticed while
    # this is blocked here rather than one launch later.
    update_job_budget
    while (( ${#pids[@]} >= LOCAL_JOBS )); do
        reap_finished_jobs
        update_job_budget
    done

    # Which axis this run holds out. With --lipid_coldsplit the "group" is the name of
    # a lipid-class set, not a protein family, and it goes to a different flag.
    if (( ${#lipid_coldsplit_sets[@]} > 0 )); then
        split_flag=(--lipid_coldsplit="${group}")
    else
        split_flag=(--excluded_groups="${group}")
    fi

    printf '=== [%d/%d] %s: %s | VARIANT: %s | SEED: %s ===\n' \
        "$(( job_index + 1 ))" "${total_jobs}" \
        "$( (( ${#lipid_coldsplit_sets[@]} > 0 )) && printf 'LIPID SET' || printf 'GROUP')" \
        "${group}" "${variant}" "${seed}"

    # read_configuration.py applies flags in argv order and the last one wins,
    # so appending --num_workers here would silently override an args file
    # that sets its own (e.g. arg_files/test.md uses --num_workers=0 for
    # deterministic single-process debugging). Only fill it in when the args
    # file is silent about it.
    num_workers_flag=()
    if ! args_file_has_flag "${ARGS_FILE}" --num_workers; then
        num_workers_flag=(--num_workers="${NUM_WORKERS_PER_JOB}")
    fi

    pin_command=()
    if (( ${#JOB_CPU_DOMAINS[@]} > 0 )); then
        pin_command=(taskset -c \
            "${JOB_CPU_DOMAINS[job_index % ${#JOB_CPU_DOMAINS[@]}]}")
    fi

    # OMP_WAIT_POLICY=PASSIVE: libgomp's default is to spin on a running CPU while
    # waiting for the rest of the team, which pays off only when the waiting
    # thread has a core to itself. It does not here -- the default job count puts
    # LOCAL_JOBS x OMP_THREADS_PER_JOB threads on fewer physical cores than that
    # (4 x 2 on 6 cores, measured on this machine), and at batch 8 the model
    # enters and leaves thousands of tiny parallel regions per second, so the
    # spinning is mostly burning cycles a neighbouring job could have used.
    # PASSIVE makes a waiting thread sleep instead. Scheduling only: the thread
    # count and therefore the arithmetic are untouched.
    #
    # MALLOC_ARENA_MAX=2: glibc otherwise opens up to 8 x ncores malloc arenas per
    # process and each one keeps its own free lists, so freed memory stays spread
    # across arenas and out of the kernel's reach. Capping them holds RSS down
    # with no effect on what is allocated.
    # shellcheck disable=SC2086
    OMP_NUM_THREADS="${OMP_THREADS_PER_JOB}" MKL_NUM_THREADS="${OMP_THREADS_PER_JOB}" \
    OMP_WAIT_POLICY=PASSIVE MALLOC_ARENA_MAX=2 \
    PYTHONUNBUFFERED=1 "${pin_command[@]}" python3 ./training/new_train.py \
        ${args_template} \
        --label="${variant}" \
        --seed="${seed}" \
        "${split_flag[@]}" \
        "${num_workers_flag[@]}" \
        > "${log_file}" 2>&1 &
    pids+=($!)

    # Job-id-tagged .out, symlinked to the friendlier stable-named .log so
    # scripts/lib/progress_table.sh's local-jobs lookup (print_local_progress,
    # keyed on "*_l<pid>.out", the same convention as the cluster's
    # "*_<tag><oar job id>.out") can find this run while it is live. The pid is
    # only known after backgrounding, so this comes after `pids+=($!)`, not
    # before -- the .log redirect target above had to be pid-free from the
    # start, which is also why it is the real file and .out is the symlink
    # rather than the other way around.
    out_file="${output_dir}/${variant}_seed${seed}_${LOCAL_JOB_TAG}${pids[-1]}.out"
    ln -sf "$(basename "${log_file}")" "${out_file}"

    [[ -n "${first_log_file}" ]] || first_log_file="${log_file}"

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
