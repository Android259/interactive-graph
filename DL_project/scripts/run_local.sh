#!/usr/bin/env bash
# Run group-by-seed grids locally through a bounded process queue.
# No SSH, synchronization, preflight, OAR submission, or cluster watcher is used.
#
# Usage: bash scripts/run_local.sh [--complete] [--graphics] [--summarize]
#                                  [--seeds=LIST] [--groups=LIST]
#                                  [--no_groups=LIST] ARGS_FILE [ARGS_FILE ...]
# Examples:
#   bash scripts/run_local.sh arg_files/archive/standard.md
#   bash scripts/run_local.sh --seeds=0,1,2 nps3mlp_gat_residual
#   bash scripts/run_local.sh --no_groups=GLTP nps3mlp_gat_residual
#   bash scripts/run_local.sh --graphics --summarize label_a label_b
#
# Labels in one call share an interleaved LOCAL_JOBS pool and common options.
# Separate invocations queue sequentially. Reports go under graphics/<label>/.
# --seeds: comma/space-separated seeds, default 0,1,2,3,4.
# --groups: excluded groups, default nine canonical groups.
# --no_groups: remove named groups from that list.
# --complete: skip group/seed pairs with final test_metrics.
#
# Resource controls are environment variables:
# LOCAL_JOBS: min(usable cores, jobs fitting RAM). Explicit values bypass both caps.
# OMP_THREADS_PER_JOB: OMP/MKL threads, default usable cores / LOCAL_JOBS.
# NUM_WORKERS_PER_JOB: DataLoader workers, default 0.
# RESERVED_CORES: default 25% of detected CPUs, at least 2; use 0 on headless workers.
# MAX_OMP_THREADS_PER_JOB: default 4, or 1 when any label uses a descriptor-only model.
# RESERVED_MEM_GIB: default 2 GiB beyond current MemAvailable usage.
# MEM_PER_JOB_GIB: explicit fixed budget disables measurement. Otherwise bootstrap
#   at 4 GiB and measure marginal running-job cost, accounting for shared pages.
# MEM_MARGIN_PERCENT: default 30%; covers checkpoint copies, testing, and later growth.
# CPU and RAM limits are independent. Override LOCAL_JOBS after measuring throughput
# for the intended configuration; automatic slots are resource limits, not an optimum.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

usage() {
    printf 'Usage: bash %s [--complete] [--graphics] [--summarize] [--seeds=LIST] [--groups=LIST] [--no_groups=LIST] ARGS_FILE [ARGS_FILE ...]\n' "${0##*/}" >&2
    printf 'Example: bash %s arg_files/archive/standard.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --seeds=0,1,2 nps3mlp_gat_residual\n' "${0##*/}" >&2
    printf 'Example: bash %s --no_groups=GLTP nps3mlp_gat_residual\n' "${0##*/}" >&2
    printf 'Example: bash %s label_a label_b label_c   # one shared pool, interleaved\n' "${0##*/}" >&2
    printf 'Example: bash %s --graphics --summarize label_a label_b\n' "${0##*/}" >&2
    printf '                 Once every job of every label finishes (this machine runs\n' >&2
    printf '                 them directly, no queue to wait on), writes one report per\n' >&2
    printf '                 label under graphics/<label>/.\n' >&2
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
# Separate invocations queue in PENDING_BATCHES_FILE.
# On completion, pop and exec the next batch, including after failures.
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
            # setsid detaches from the controlling terminal; nohup ignores SIGHUP;
            # disown removes the child from this shell's job table.
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

# Activate the same environment as scripts/parameters.sh.
# If conda is unavailable, warn and continue with python3 on PATH;
# non-conda environments may already contain the dependencies.
if [[ "${CONDA_DEFAULT_ENV:-}" != "Kalinin_project_LP" ]]; then
    if ! source "${SCRIPT_DIR}/lib/activate_training_env.sh"; then
        printf 'Could not activate the Kalinin_project_LP conda env; using current python3: %s\n' \
            "$(command -v python3 || echo 'not found')" >&2
    fi
fi

# LOCAL_PYTHON selects the job interpreter. Default: CPU-only torch layered
# over the conda environment (venv --system-site-packages, torch==2.12.1+cpu),
# avoiding CUDA libraries on this CPU host. If unavailable or broken, warn
# and fall back to the conda environment's python3.
LOCAL_PYTHON="${LOCAL_PYTHON:-${HOME}/.venvs/ltp_cpu/bin/python}"
if [[ ! -x "${LOCAL_PYTHON}" ]] \
    || ! "${LOCAL_PYTHON}" -c 'import torch, torch_geometric' 2>/dev/null; then
    if [[ -n "${LOCAL_PYTHON}" ]]; then
        printf 'LOCAL_PYTHON (%s) cannot import torch/torch_geometric; using python3 from the active env.\n' \
            "${LOCAL_PYTHON}" >&2
    fi
    LOCAL_PYTHON="$(command -v python3)"
fi

POSITIONALS=()
DO_GRAPHICS=0
DO_SUMMARIZE=0
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
        --graphics)
            DO_GRAPHICS=1
            shift
            ;;
        --summarize)
            DO_SUMMARIZE=1
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

if (( ${#POSITIONALS[@]} < 1 )); then
    usage
    exit 2
fi

# Resolve paths, bare arg-file stems, and optional .md suffixes through args_file_lib.sh.
# shellcheck source=scripts/lib/args_file_lib.sh
source "${SCRIPT_DIR}/lib/args_file_lib.sh"
# shellcheck source=scripts/settings.sh
source "${SCRIPT_DIR}/settings.sh"
# shellcheck source=scripts/lib/grid_lib.sh
source "${SCRIPT_DIR}/lib/grid_lib.sh"

# LABEL_* arrays hold each label; job_label_index maps combined-grid jobs to labels.
# All labels in this call interleave under one LOCAL_JOBS cap.
# Separate overlapping invocations remain sequential, preserving the active pool.
LABEL_VARIANT=()
LABEL_ARGS_FILE=()
LABEL_ARGS_TEMPLATE=()
LABEL_OUTPUT_ROOT=()
LABEL_IS_LIPID_COLDSPLIT=()
LABEL_IS_LIPID_SUBCLASS=()
LABEL_IS_RANDOM_SPLIT=()
LABEL_IS_FAMILY_ONLY=()
LABEL_FAMILY_ONLY_FIXED=()
LABEL_LIPID_ISOLATION=()
LABEL_LIPID_SPECIES=()
LABEL_SEEDS_CSV=()
job_label_index=()
job_groups=()
job_seeds=()

for requested in "${POSITIONALS[@]}"; do
    this_args_file="${requested}"
    if ! this_args_file="$(resolve_args_file "${this_args_file}")"; then
        printf 'Arguments file not found: %s\n' "${requested}" >&2
        exit 1
    fi

    if args_file_has_flag "${this_args_file}" --cold_split; then
        printf '%s uses --cold_split, which this script does not implement (it needs\n' "${this_args_file}" >&2
        printf 'the per-group val/test pairing that launch/submit_grid.sh applies).\n' >&2
        printf 'Run it on a cluster instead: bash scripts/run_bigfoot.sh %s\n' "${this_args_file}" >&2
        exit 2
    fi

    this_variant="$(basename "${this_args_file}" .md)"
    this_args_template="$(args_file_flags "${this_args_file}")"

    this_excl_groups=("${PROTEIN_GROUPS[@]}")
    if [[ -n "${GROUPS_ARG:-}" ]]; then
        read -r -a this_excl_groups <<< "${GROUPS_ARG//,/ }"
    fi

    # Apply --no_groups after --groups/default selection, identically for all labels.
    # normalize_group_name accepts case-insensitive names and interchangeable -/_
    # (e.g. cral_trio == CRAL-TRIO), as for --excluded_groups.
    if [[ -n "${SKIP_GROUPS_ARG:-}" ]]; then
        read -r -a skip_groups <<< "${SKIP_GROUPS_ARG//,/ }"
        declare -A skip_matched=()
        kept_groups=()
        for group in "${this_excl_groups[@]}"; do
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
        # Reject unknown group names so typos cannot silently launch excluded work.
        for skipped in "${skip_groups[@]}"; do
            if [[ -z "${skip_matched["$(normalize_group_name "${skipped}")"]:-}" ]]; then
                printf -- '--no_groups names a group that is not being run: %s\n' "${skipped}" >&2
                printf 'Groups in this run: %s\n' "${this_excl_groups[*]}" >&2
                exit 2
            fi
        done
        if (( ${#kept_groups[@]} == 0 )); then
            printf -- '--no_groups excluded every group; nothing left to run.\n' >&2
            exit 2
        fi
        this_excl_groups=("${kept_groups[@]}")
    fi

    # --lipid_coldsplit retains all proteins and iterates four lipid-class sets.
    # Strip the bare marker; append the trainer's required named form per job.
    this_is_lipid_coldsplit=0
    if args_file_has_flag "${this_args_file}" --lipid_coldsplit; then
        if [[ -n "${GROUPS_ARG:-}${SKIP_GROUPS_ARG:-}" ]]; then
            # Ignore protein --groups/--no_groups for lipid-axis labels, as submit_grid.sh does.
            # This allows mixed axes in one call. The lipid sets overwrite this_excl_groups.
            printf -- '--lipid_coldsplit runs over lipid sets, not protein groups; '\
'ignoring --groups/--no_groups for %s -- all four lipid sets will run.\n' \
                "${this_args_file}" >&2
        fi
        # Keep names aligned with LIPID_COLDSPLIT_SETS and LIPID_COLDSPLIT_NAMES
        # (splitting_on_blocks/lipid_coldsplit_blocks.py, training/read_configuration.py).
        # Unknown names fail parsing.
        this_is_lipid_coldsplit=1
        this_excl_groups=(sphingolipids phosphorus_free choline anionic)
        this_args_template="$(printf '%s' "${this_args_template}" \
            | sed -E 's/(^|[[:space:]])--lipid_coldsplit([[:space:]]|$)/\1/g')"
    fi

    # --family_only filters the whole table before a within-family random split.
    # Append --family_only=<group>, never --excluded_groups.
    # Bare form iterates PROTEIN_GROUPS, honoring --groups/--no_groups;
    # family_only=<value> runs one fixed family.
    # Match scripts/launch/submit_grid.sh. Detect this before subclass/isolation
    # so a combined family/subclass label lets the lipid block overwrite the axis.
    this_is_family_only=0
    this_family_only_fixed=""
    if args_file_has_flag "${this_args_file}" --family_only; then
        if (( this_is_lipid_coldsplit )); then
            printf -- '--family_only is a warm per-family split, not a cold-split axis; '\
'it cannot combine with --lipid_coldsplit (%s).\n' "${this_args_file}" >&2
            exit 2
        fi
        this_is_family_only=1
        this_family_only_fixed="$(args_file_flag_lines "${this_args_file}" \
            | sed -nE 's/^--family_only=(.+)$/\1/p' | tail -1)"
        if [[ -n "${this_family_only_fixed}" ]]; then
            # One job x seed, not nine: the family is already fixed in the template.
            this_excl_groups=("${this_family_only_fixed}")
        fi
        # Bare form uses the already filtered PROTEIN_GROUPS list.
    fi

    # --random_split holds out neither proteins nor chemistry. Add no exclusion flag:
    # the loader uses 85% train and halves the remaining 15% by label for valid/test.
    # Use one pseudo-group, random, for result paths and seed iteration.
    # Ignore --groups/--no_groups; appended flags otherwise win by argv order.
    # --lipid_isolation=<key> already names a distance block; retain the template flag
    # and run one pseudo-group with the same result name as new_train.py.
    # --lipid_subclass uses Titeca et al.'s LTP-by-subclass blocks.
    # Bare form expands the block list; <spec> retains one template block.
    # Keep aligned with FIG3_SUBCLASS_BLOCKS in splitting_on_blocks/lipid_subclass_blocks.py
    # and scripts/launch/submit_grid.sh.
    this_is_lipid_subclass=0
    this_lipid_subclass_fixed=""
    if args_file_has_flag "${this_args_file}" --lipid_subclass; then
        if (( this_is_lipid_coldsplit )); then
            printf -- '--lipid_subclass and --lipid_coldsplit hold out different '\
'things; pick one (%s).\n' "${this_args_file}" >&2
            exit 2
        fi
        this_is_lipid_subclass=1
        this_lipid_subclass_fixed="$(args_file_flag_lines "${this_args_file}" \
            | sed -nE 's/^--lipid_subclass=(.+)$/\1/p' | tail -1)"
        if [[ -n "${this_lipid_subclass_fixed}" ]]; then
            this_excl_groups=("${this_lipid_subclass_fixed}")
        else
            if [[ -n "${GROUPS_ARG:-}${SKIP_GROUPS_ARG:-}" ]]; then
                printf -- '--lipid_subclass runs over lipid subclasses, not protein '\
'groups; ignoring --groups/--no_groups for %s -- all eight blocks will run.\n' \
                    "${this_args_file}" >&2
            fi
            this_excl_groups=(
                PC PG FA PE "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM" PI "LPC+LPE+LPG" PA
            )
            this_args_template="$(printf '%s' "${this_args_template}" \
                | sed -E 's/(^|[[:space:]])--lipid_subclass([[:space:]]|$)/\1/g')"
        fi
    fi

    this_lipid_isolation=""
    if args_file_has_flag "${this_args_file}" --lipid_isolation; then
        this_lipid_isolation="$(args_file_flag_lines "${this_args_file}" \
            | sed -nE 's/^--lipid_isolation=(.*)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_isolation}" ]]; then
            printf -- '--lipid_isolation needs a value (a key of LIPID_ISOLATION_BLOCKS) in %s.\n' \
                "${this_args_file}" >&2
            exit 2
        fi
        if (( this_is_lipid_coldsplit )) || (( this_is_lipid_subclass )); then
            printf -- '--lipid_isolation and --lipid_coldsplit/--lipid_subclass hold '\
'out different things; pick one (%s).\n' "${this_args_file}" >&2
            exit 2
        fi
        this_excl_groups=("iso${this_lipid_isolation}")
    fi

    # --lipid_species_coldsplit=<share> uses one pseudo-group across seeds.
    # The loader draws different structure-disjoint lipid blocks per seed
    # (splitting_on_blocks/lipid_species_blocks.py).
    this_lipid_species=""
    if args_file_has_flag "${this_args_file}" --lipid_species_coldsplit; then
        this_lipid_species="$(args_file_flag_lines "${this_args_file}" \
            | sed -nE 's/^--lipid_species_coldsplit=(.*)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_species}" ]]; then
            printf -- '--lipid_species_coldsplit needs a value (share of positives in '\
'the held-out block, e.g. 0.15) in %s.\n' "${this_args_file}" >&2
            exit 2
        fi
        if (( this_is_lipid_coldsplit )) || (( this_is_lipid_subclass )) \
            || [[ -n "${this_lipid_isolation}" ]]; then
            printf -- '--lipid_species_coldsplit and --lipid_coldsplit/--lipid_subclass'\
'/--lipid_isolation hold out different things; pick one (%s).\n' \
                "${this_args_file}" >&2
            exit 2
        fi
        this_excl_groups=("species$(printf '%02d' \
            "$(awk -v s="${this_lipid_species}" 'BEGIN{printf "%d", s*100 + 0.5}')")")
    fi

    this_is_random_split=0
    if args_file_has_flag "${this_args_file}" --random_split; then
        if (( this_is_lipid_coldsplit )); then
            printf -- '--random_split holds nothing out and --lipid_coldsplit holds a '\
'chemical set out; pick one (%s).\n' "${this_args_file}" >&2
            exit 2
        fi
        if (( this_is_family_only )); then
            printf -- '--random_split holds nothing out and --family_only restricts '\
'training to one family; pick one (%s).\n' "${this_args_file}" >&2
            exit 2
        fi
        if [[ -n "${GROUPS_ARG:-}${SKIP_GROUPS_ARG:-}" ]]; then
            printf -- '--random_split holds no group out; ignoring --groups/--no_groups '\
'for %s -- the single random-split grid will run.\n' "${this_args_file}" >&2
        fi
        this_is_random_split=1
        this_excl_groups=(random)
        # Stripped like the marker above: the trainer has no such flag.
        this_args_template="$(printf '%s' "${this_args_template}" \
            | sed -E 's/(^|[[:space:]])--random_split([[:space:]]|$)/\1/g')"
    fi

    this_seeds=("${DEFAULT_SEEDS[@]}")
    if [[ -n "${SEEDS_ARG:-}" ]]; then
        read -r -a this_seeds <<< "${SEEDS_ARG//,/ }"
        for _seed in "${this_seeds[@]}"; do
            if [[ ! "${_seed}" =~ ^[0-9]+$ ]]; then
                printf 'Invalid seed (must be a non-negative integer): %s\n' "${_seed}" >&2
                exit 2
            fi
        done
    fi

    # --complete skips final reports through grid_lib.sh, as cluster submitters do.
    grid_load_completed "${this_variant}" "${PROJECT_ROOT}/test_metrics" 0

    label_index=${#LABEL_VARIANT[@]}
    LABEL_VARIANT+=("${this_variant}")
    LABEL_ARGS_FILE+=("${this_args_file}")
    LABEL_ARGS_TEMPLATE+=("${this_args_template}")
    # script_logs/<family>/..., like run/ and test_metrics/ (training/results_layout.py).
    LABEL_OUTPUT_ROOT+=("script_logs/$(label_family "${this_variant}")/${this_variant}_seeds$(IFS=; echo "${this_seeds[*]}")")
    LABEL_IS_LIPID_COLDSPLIT+=("${this_is_lipid_coldsplit}")
    LABEL_IS_LIPID_SUBCLASS+=("${this_is_lipid_subclass}")
    LABEL_IS_RANDOM_SPLIT+=("${this_is_random_split}")
    LABEL_IS_FAMILY_ONLY+=("${this_is_family_only}")
    LABEL_FAMILY_ONLY_FIXED+=("${this_family_only_fixed}")
    LABEL_LIPID_ISOLATION+=("${this_lipid_isolation}")
    LABEL_LIPID_SPECIES+=("${this_lipid_species}")
    LABEL_SEEDS_CSV+=("$(IFS=,; printf '%s' "${this_seeds[*]}")")

    while IFS=$'\t' read -r group seed; do
        [[ -n "${group}" ]] || continue
        job_label_index+=("${label_index}")
        job_groups+=("${group}")
        job_seeds+=("${seed}")
    done < <(grid_pairs "${this_excl_groups[*]}" "${this_seeds[*]}")
done

total_jobs=${#job_groups[@]}
if (( total_jobs == 0 )); then
    printf 'All requested group/seed pairs already have final test_metrics.\n'
    exit 0
fi

# Track jobs per label. report_label_if_done prints completion and generates
# --graphics/--summarize once that label finishes, even while other labels run.
LABEL_TOTAL_JOBS=()
for label_index in "${!LABEL_VARIANT[@]}"; do
    count=0
    for li in "${job_label_index[@]}"; do
        (( li == label_index )) && count=$((count + 1))
    done
    LABEL_TOTAL_JOBS+=("${count}")
done
LABEL_FINISHED_JOBS=()
LABEL_FAILED_JOBS=()
for label_index in "${!LABEL_VARIANT[@]}"; do
    LABEL_FINISHED_JOBS+=(0)
    LABEL_FAILED_JOBS+=(0)
done

nproc_count="$(nproc)"
# Reserve a quarter of detected CPUs, at least two, for desktop responsiveness.
# Explicit RESERVED_CORES overrides this machine-scaled default.
default_reserved_cores=$(( nproc_count / 4 ))
if (( default_reserved_cores < 2 )); then default_reserved_cores=2; fi
RESERVED_CORES="${RESERVED_CORES:-${default_reserved_cores}}"
usable_cores=$(( nproc_count - RESERVED_CORES ))
if (( usable_cores < 1 )); then usable_cores=1; fi

# Budget CPU and RAM independently. Use marginal per-job memory:
# shared libtorch/MKL pages make summed RSS overestimate concurrent cost.
# MEM_PER_JOB_GIB overrides measurement. Otherwise start with 4 GiB/job and
# update_job_budget measures complete job trees after the first validation.
# The conservative bootstrap covers allocation before the first valid measurement.
if [[ -n "${MEM_PER_JOB_GIB+set}" ]]; then
    MEM_PER_JOB_FIXED=1
else
    MEM_PER_JOB_FIXED=0
fi
MEM_PER_JOB_GIB="${MEM_PER_JOB_GIB:-4}"
# Keep budgets in MiB to preserve measured resolution.
MEM_PER_JOB_MIB=$(( MEM_PER_JOB_GIB * 1024 ))
# Set once update_job_budget has replaced the bootstrap figure with a measured one.
MEM_MEASURED=0
MEM_MARGIN_PERCENT="${MEM_MARGIN_PERCENT:-30}"
# RESERVED_MEM_GIB adds independent RAM headroom.
# Use the kernel's current MemAvailable estimate (allocatable without swapping),
# which already accounts for desktop/browser/editor usage. Add a 2 GiB reserve;
# do not subtract a fixed desktop footprint from MemTotal.
RESERVED_MEM_GIB="${RESERVED_MEM_GIB:-2}"
total_mem_gib=$(( $(awk '/^MemTotal:/ {print $2}' /proc/meminfo) / 1024 / 1024 ))

# Read fresh MemAvailable minus reserve before each budget decision.
# Both available memory and measured per-job cost can change during the grid.
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

# Default LOCAL_JOBS to min(usable cores, jobs fitting available RAM).
# An explicit value bypasses both caps; callers must account for memory and
# measure any configuration-specific throughput optimum themselves.
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
# Descriptor-only models have little arithmetic per batch; default to one
# OMP thread to reduce synchronization overhead. Any descriptor-only label
# sets this default for the combined pool. Thread count stays fixed for all jobs;
# explicit MAX_OMP_THREADS_PER_JOB overrides it.
default_max_omp_threads_per_job=4
for _label_args_file in "${LABEL_ARGS_FILE[@]}"; do
    if args_file_has_flag "${_label_args_file}" --descriptors_head \
        || args_file_has_flag "${_label_args_file}" --descriptor_mlp; then
        # descriptor_mlp also has no encoder towers and uses the same one-thread default;
        # its descriptor head has no token self-attention.
        default_max_omp_threads_per_job=1
        break
    fi
done
MAX_OMP_THREADS_PER_JOB="${MAX_OMP_THREADS_PER_JOB:-${default_max_omp_threads_per_job}}"
if (( OMP_THREADS_PER_JOB > MAX_OMP_THREADS_PER_JOB )); then
    OMP_THREADS_PER_JOB="${MAX_OMP_THREADS_PER_JOB}"
fi
# Default to zero DataLoader workers: persistent split workers retain forked
# datasets and increase per-job memory, reducing concurrent slots.
NUM_WORKERS_PER_JOB="${NUM_WORKERS_PER_JOB:-0}"

# Pin jobs round-robin to detected last-level-cache domains by launch index.
# This reduces thread migration and working-set reloads without changing thread
# count or reduction partitioning. Consecutive live jobs spread across domains.
# Read domains from the host; if index3 or taskset is unavailable, run unpinned.
JOB_CPU_DOMAINS=()
if command -v taskset >/dev/null 2>&1; then
    while IFS= read -r cpu_domain; do
        [[ -n "${cpu_domain}" ]] && JOB_CPU_DOMAINS+=("${cpu_domain}")
    done < <(cat /sys/devices/system/cpu/cpu*/cache/index3/shared_cpu_list \
        2>/dev/null | sort -u)
fi

# Use LOCAL_JOB_TAG=l, matching progress_table.sh. Bigfoot uses no tag and Kraken
# uses k; distinct PID/OAR namespaces share collision-free tag+ID log names.
LOCAL_JOB_TAG="l"

# Pending jobs are variant<TAB>group<TAB>seed lines for watcher WAITING counts
# and queued rows, like OAR pending.commands. Pop on launch; the exit trap
# removes the queue file on success/failure to avoid phantom jobs.
local_queue_file="${PROJECT_ROOT}/script_logs/local_run.queue"
mkdir -p "${PROJECT_ROOT}/script_logs"
: > "${local_queue_file}"
for (( i=0; i<total_jobs; i++ )); do
    printf '%s\t%s\t%s\n' "${LABEL_VARIANT[job_label_index[i]]}" "${job_groups[i]}" "${job_seeds[i]}" >> "${local_queue_file}"
done
trap 'rm -f "${local_queue_file}"' EXIT

all_labels_csv="$(IFS=,; printf '%s' "${LABEL_VARIANT[*]}")"
printf 'Running %d jobs across %d label(s) (%s), interleaved in one pool.\n' \
    "${total_jobs}" "${#LABEL_VARIANT[@]}" "${all_labels_csv}"
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

# Build current memory-mapped embedding stores once per label before launching.
# Labels may select different isomeric variants. Serial preparation avoids jobs
# racing to write one archive and lets jobs share its page cache.
# Missing stores are nonfatal: jobs load the source pickle with higher RAM cost.
# Set OMP_NUM_THREADS/MKL_NUM_THREADS/OPENBLAS_NUM_THREADS=1 during preparation
# to avoid BLAS/RDKit thread oversubscription on serial work
# (see scripts/tools/lipid_graphs_on_kraken.sh).
for _label_args_file in "${LABEL_ARGS_FILE[@]}"; do
    if ! OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        python3 "${PROJECT_ROOT}/data/build_lipid_embedding_store.py" \
        --args_file="${_label_args_file}"; then
        printf 'WARNING: could not build the embedding store for %s; its jobs will read the pickle.\n' \
            "${_label_args_file}" >&2
    fi

    # Build shared descriptor values once before the grid (descriptor_cache_reader.py).
    # If unavailable, jobs compute values directly; correctness is unchanged.
    if ! OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        python3 "${PROJECT_ROOT}/data/build_descriptor_cache.py" \
        --args_file="${_label_args_file}"; then
        printf 'WARNING: could not build the pair descriptor cache for %s; its jobs will compute it themselves.\n' \
            "${_label_args_file}" >&2
    fi
done

# Measure marginal per-job memory after the bootstrap period.
# Use PSS to divide shared libtorch/MKL and mapped pages across their users.
# The mean over complete job trees estimates the cost of another concurrent job.

# Return job-tree memory in KiB, including DataLoader children.
job_tree_pss_kib() {
    local root="$1" pid value total=0
    for pid in "${root}" $(pgrep -P "${root}" 2>/dev/null || true); do
        value="$(awk '/^Pss:/ {print $2; exit}' "/proc/${pid}/smaps_rollup" 2>/dev/null || true)"
        # Use smaps_rollup on readable processes (kernel >=4.14), with conservative VmRSS fallback.
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

# Update the concurrency cap from current free memory and measured job cost.
# Run before launches and after completions to follow desktop/configuration changes.
update_job_budget() {
    (( LOCAL_JOBS_FIXED )) && return 0
    local measured headroom affordable cap
    if (( ! MEM_PER_JOB_FIXED )) && [[ -n "${first_log_file}" ]] \
        && grep -q '^EPOCH 2:' "${first_log_file}" 2>/dev/null; then
        # Wait for the first epoch and validation before measuring: optimizer state,
        # sample caches, and persistent validation workers must already exist.
        if measured="$(measure_job_memory_mib)"; then
            measured=$(( measured * (100 + MEM_MARGIN_PERCENT) / 100 ))
            # Reject zero measurements: the budget is a divisor, and jobs cannot cost zero.
            (( measured < 1 )) && measured=1
            # The first measurement replaces bootstrap in either direction.
            # Then retain peak mean cost, covering late workers, checkpoints, and testing;
            # a later decrease must not launch extra jobs.
            if (( MEM_MEASURED && measured < MEM_PER_JOB_MIB )); then
                measured=${MEM_PER_JOB_MIB}
            fi
            MEM_MEASURED=1
            # Log budget changes only above 5% to keep launch output readable.
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
    # Keep OMP_THREADS_PER_JOB fixed across the grid: reduction partitioning depends
    # on thread count, so changing it mid-grid could change seeded results.
    local core_cap=$(( usable_cores / OMP_THREADS_PER_JOB ))
    (( core_cap < 1 )) && core_cap=1
    (( cap > core_cap )) && cap=${core_cap}
    (( cap > total_jobs )) && cap=${total_jobs}
    (( cap < 1 )) && cap=1
    LOCAL_JOBS=${cap}
}

# Report each label as soon as all its interleaved jobs finish,
# without waiting for unrelated labels' jobs.
report_label_if_done() {
    local label_index="$1" variant
    (( LABEL_FINISHED_JOBS[label_index] >= LABEL_TOTAL_JOBS[label_index] )) || return 0
    variant="${LABEL_VARIANT[label_index]}"
    printf 'Ran %d job(s) for %s.\n' "${LABEL_TOTAL_JOBS[label_index]}" "${variant}"
    if (( LABEL_FAILED_JOBS[label_index] > 0 )); then
        printf '%d job(s) exited non-zero for %s; check the logs under %s/.\n' \
            "${LABEL_FAILED_JOBS[label_index]}" "${variant}" "${LABEL_OUTPUT_ROOT[label_index]}" >&2
    fi
    (( DO_GRAPHICS || DO_SUMMARIZE )) || return 0

    # Report-section failures are nonfatal; generate_label_report.sh records them.
    # Guard its status under set -e so one failed label report does not abort the grid.
    if ! bash "${PROJECT_ROOT}/scripts/lib/generate_label_report.sh" \
        "${variant}" "${LABEL_SEEDS_CSV[label_index]}" "${DO_GRAPHICS}" "${DO_SUMMARIZE}"
    then
        printf 'generate_label_report.sh failed for %s -- rerun it directly to retry.\n' \
            "${variant}" >&2
    fi
}

# Poll for exited jobs, then wait for each known PID exactly once.
# Avoid wait -n here: anonymous reaping can lose the status needed by later
# per-PID waits, especially when several jobs fail between polling ticks.
reap_finished_jobs() {
    local pid label_index
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
        label_index="${PID_LABEL_INDEX[${pid}]}"
        if ! wait "${pid}"; then
            failed=$((failed + 1))
            LABEL_FAILED_JOBS[label_index]=$(( LABEL_FAILED_JOBS[label_index] + 1 ))
        fi
        LABEL_FINISHED_JOBS[label_index]=$(( LABEL_FINISHED_JOBS[label_index] + 1 ))
        unset "PID_LABEL_INDEX[${pid}]"
        report_label_if_done "${label_index}"
    done
    pids=("${still_running[@]}")
}

pids=()
failed=0
# Map PID to label for completion/failure counts and per-label reports.
# Register immediately after launch and remove when reaped.
declare -A PID_LABEL_INDEX=()
# Keep the first job's log to detect when memory measurements are valid.
first_log_file=""
for (( job_index=0; job_index<total_jobs; job_index++ )); do
    label_index="${job_label_index[job_index]}"
    variant="${LABEL_VARIANT[label_index]}"
    args_template="${LABEL_ARGS_TEMPLATE[label_index]}"
    this_args_file="${LABEL_ARGS_FILE[label_index]}"
    group="${job_groups[job_index]}"
    seed="${job_seeds[job_index]}"
    output_dir="${LABEL_OUTPUT_ROOT[label_index]}/${group}"
    mkdir -p "${output_dir}"
    log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"

    # Enforce the cap before launching. Refresh it while waiting so completions
    # and newly available memory are noticed immediately.
    update_job_budget
    while (( ${#pids[@]} >= LOCAL_JOBS )); do
        reap_finished_jobs
        update_job_budget
    done

    # Read the axis per label: mixed-axis pools dispatch each job correctly.
    # For --lipid_coldsplit, group is a lipid-set name, not a protein family.
    if (( LABEL_IS_LIPID_COLDSPLIT[label_index] )); then
        split_flag=(--lipid_coldsplit="${group}")
    elif (( LABEL_IS_LIPID_SUBCLASS[label_index] )); then
        # Append the article subclass spec, even if already in the template;
        # the identical last value wins.
        split_flag=(--lipid_subclass="${group}")
    elif [[ -n "${LABEL_LIPID_ISOLATION[label_index]}" ]]; then
        # The block is named by the flag already in the template; nothing is appended.
        split_flag=()
    elif [[ -n "${LABEL_LIPID_SPECIES[label_index]}" ]]; then
        # The template already holds the share. group names the species<NN> result path.
        split_flag=()
    elif (( LABEL_IS_RANDOM_SPLIT[label_index] )); then
        # Add no holdout flag for random: the loader defines and names the split.
        split_flag=()
    elif (( LABEL_IS_FAMILY_ONLY[label_index] )); then
        # family_only uses the whole named family, without --excluded_groups.
        # Fixed form is already in the template; bare form gets this job's group.
        if [[ -n "${LABEL_FAMILY_ONLY_FIXED[label_index]}" ]]; then
            split_flag=()
        else
            split_flag=(--family_only="${group}")
        fi
    else
        split_flag=(--excluded_groups="${group}")
    fi

    printf '=== [%d/%d] %s: %s | VARIANT: %s | SEED: %s ===\n' \
        "$(( job_index + 1 ))" "${total_jobs}" \
        "$( (( LABEL_IS_LIPID_COLDSPLIT[label_index] )) && printf 'LIPID SET' \
            || { (( LABEL_IS_LIPID_SUBCLASS[label_index] )) && printf 'SUBCLASS' \
            || { [[ -n "${LABEL_LIPID_ISOLATION[label_index]}" ]] && printf 'ISOLATION' \
            || { (( LABEL_IS_RANDOM_SPLIT[label_index] )) && printf 'SPLIT' \
            || { (( LABEL_IS_FAMILY_ONLY[label_index] )) && printf 'FAMILY_ONLY' \
            || printf 'GROUP'; }; }; }; } )" \
        "${group}" "${variant}" "${seed}"

    # Fill --num_workers only when absent: appended argv values override earlier ones.
    # Preserve explicit settings, including deterministic smoke/debug configurations.
    num_workers_flag=()
    if ! args_file_has_flag "${this_args_file}" --num_workers; then
        num_workers_flag=(--num_workers="${NUM_WORKERS_PER_JOB}")
    fi

    pin_command=()
    if (( ${#JOB_CPU_DOMAINS[@]} > 0 )); then
        pin_command=(taskset -c \
            "${JOB_CPU_DOMAINS[job_index % ${#JOB_CPU_DOMAINS[@]}]}")
    fi

    # OMP_WAIT_POLICY=PASSIVE sleeps waiting OpenMP threads, freeing CPU for other jobs.
    # Thread counts and reduction arithmetic stay unchanged.
    # MALLOC_ARENA_MAX=2 limits glibc arenas (otherwise up to 8*ncores per process),
    # reducing retained RSS without changing allocations.
    # shellcheck disable=SC2086
    OMP_NUM_THREADS="${OMP_THREADS_PER_JOB}" MKL_NUM_THREADS="${OMP_THREADS_PER_JOB}" \
    OMP_WAIT_POLICY=PASSIVE MALLOC_ARENA_MAX=2 \
    PYTHONUNBUFFERED=1 "${pin_command[@]}" "${LOCAL_PYTHON}" ./training/new_train.py \
        ${args_template} \
        --label="${variant}" \
        --seed="${seed}" \
        "${split_flag[@]}" \
        "${num_workers_flag[@]}" \
        > "${log_file}" 2>&1 &
    pids+=($!)
    PID_LABEL_INDEX[${pids[-1]}]="${label_index}"

    # After PID creation, symlink *_l<pid>.out to the stable .log redirect target.
    # progress_table.sh uses the tagged path to discover live local jobs,
    # matching the clusters' *_<tag><jobid>.out convention.
    out_file="${output_dir}/${variant}_seed${seed}_${LOCAL_JOB_TAG}${pids[-1]}.out"
    ln -sf "$(basename "${log_file}")" "${out_file}"

    [[ -n "${first_log_file}" ]] || first_log_file="${log_file}"

    # Pop the first queue line: launch order matches queue-file order.
    tail -n +2 "${local_queue_file}" > "${local_queue_file}.tmp"
    mv "${local_queue_file}.tmp" "${local_queue_file}"

    # Stagger launches by one second for readable output. TensorBoard paths include
    # seed and timestamp; new_train.py retries name collisions after one second.
    if (( job_index + 1 < total_jobs )); then
        sleep 1
    fi

done

# Drain with reap_finished_jobs so the final jobs also update per-label
# completion counts and trigger --graphics/--summarize reports.
while (( ${#pids[@]} > 0 )); do
    reap_finished_jobs
done

printf 'All %d jobs across %d label(s) (%s) finished.\n' \
    "${total_jobs}" "${#LABEL_VARIANT[@]}" "${all_labels_csv}"
if (( failed > 0 )); then
    printf '%d job(s) total exited non-zero.\n' "${failed}" >&2
fi

# Pop and exec the next queued batch even if this batch failed.
# Retain the detached session, PID, log, and RUN_LOCAL_DETACHED environment;
# one bad configuration must not strand later batches.
if [[ -s "${PENDING_BATCHES_FILE}" ]]; then
    next_batch="$(head -n 1 "${PENDING_BATCHES_FILE}")"
    tail -n +2 "${PENDING_BATCHES_FILE}" > "${PENDING_BATCHES_FILE}.tmp"
    mv "${PENDING_BATCHES_FILE}.tmp" "${PENDING_BATCHES_FILE}"
    printf 'Starting next queued batch: %s\n' "${next_batch}"
    # exec skips EXIT traps. Remove this batch's queue file explicitly before
    # replacing the process; it is normally already empty after launches.
    rm -f "${local_queue_file}"
    eval "set -- ${next_batch}"
    exec bash "${BASH_SOURCE[0]}" "$@"
fi

if (( failed > 0 )); then
    exit 1
fi
