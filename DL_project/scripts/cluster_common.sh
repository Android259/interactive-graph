#!/usr/bin/env bash
# Cluster profile shared by run_cluster.sh, wait_and_sync_cluster.sh and
# cluster_wait_watchdog.sh. `source` it after setting CLUSTER_NAME.
#
# Every value here is derived from CLUSTER_NAME so that a Bigfoot run and a
# Kraken run can proceed at the same time without sharing a queue directory,
# an ssh ControlMaster socket, a tmux session, or a pid/log file. The bigfoot
# column reproduces the names this project used before the port, so nothing
# about an in-flight Bigfoot session changes.
#
# Callers may override any of these from the environment; the assignments use
# `${VAR:-default}` except for PROJECT/GPU_PROPERTY, where `${VAR-default}`
# lets an explicitly empty value survive and omit the corresponding oarsub flag.

# Snapshot of the caller's genuine overrides, taken once before anything is
# derived. cluster_profile() re-derives every value from this snapshot, so it
# can be called repeatedly to switch clusters inside a loop (wait_and_sync.sh
# polls several clusters in turn) without the previous cluster's values leaking
# into the next. `+set` markers distinguish "unset" from "explicitly empty",
# which matters for PROJECT/GPU_PROPERTY: empty means "omit the oarsub flag".
if [[ -z "${_CLUSTER_ENV_CAPTURED:-}" ]]; then
    _CLUSTER_ENV_CAPTURED=1
    _ENV_REMOTE_HOST="${REMOTE_HOST:-}"
    _ENV_GPU_PROPERTY_SET="${GPU_PROPERTY+set}"
    _ENV_GPU_PROPERTY="${GPU_PROPERTY-}"
    _ENV_GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-}"
    _ENV_JOB_ID_TAG_SET="${JOB_ID_TAG+set}"
    _ENV_JOB_ID_TAG="${JOB_ID_TAG-}"
    _ENV_MAX_WALLTIME_SET="${MAX_WALLTIME+set}"
    _ENV_MAX_WALLTIME="${MAX_WALLTIME-}"
    _ENV_CLUSTER_QUEUE_ROOT="${CLUSTER_QUEUE_ROOT:-}"
    _ENV_CLUSTER_SESSION_PREFIX="${CLUSTER_SESSION_PREFIX:-}"
    _ENV_SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-}"
    _ENV_EVENT_CACHE="${EVENT_CACHE:-}"
fi

# Set every cluster-dependent global for the named cluster. Idempotent and
# repeatable.
cluster_profile() {
    CLUSTER_NAME="$1"

    case "${CLUSTER_NAME}" in
        bigfoot)
            _default_host="bigfoot"
            # A100 (sm_80) and V100 (sm_70).
            _default_gpu_property="(gpumodel='A100' OR gpumodel='V100')"
            _default_gpu_glob="*A100*|*V100*"
            # Empty: Bigfoot's OAR output filenames must not change.
            _default_job_id_tag=""
            # "The maximum walltime is 48 hours" -- GRICAD Bigfoot GPU-job docs.
            # Caps how deep a pack may be: a job asking for more is rejected at
            # oarsub time, which would stall the whole drain.
            _default_max_walltime="48:00:00"
            ;;
        kraken)
            # kraken-gpu is the GPU frontend; kraken-cpu exists but this project
            # trains single-GPU only and needs no CPU-only allocation.
            _default_host="kraken-gpu"
            # H100 (94GB) and H200 (142GB); both are sm_90.
            _default_gpu_property="(gpumodel='H100' OR gpumodel='H200')"
            _default_gpu_glob="*H100*|*H200*"
            # Distinguishes Kraken's OAR .out/.err from Bigfoot's: the two
            # clusters hand out overlapping job IDs and the wait loop locates a
            # running job's log by `*_${job_id}.out`.
            _default_job_id_tag="k"
            # GRICAD documents no maximum walltime for Kraken production jobs
            # (only devel: 30 min, and a 2 h default when none is given). Empty
            # means "no known cap, do not check" -- guessing one here would
            # silently shrink packs. Set MAX_WALLTIME if the site announces one.
            _default_max_walltime=""
            ;;
        *)
            printf 'Unknown cluster: %s (expected bigfoot or kraken)\n' \
                "${CLUSTER_NAME}" >&2
            return 1
            ;;
    esac

    REMOTE_HOST="${_ENV_REMOTE_HOST:-${_default_host}}"
    GPU_MODEL_GLOB="${_ENV_GPU_MODEL_GLOB:-${_default_gpu_glob}}"
    if [[ -n "${_ENV_GPU_PROPERTY_SET}" ]]; then
        GPU_PROPERTY="${_ENV_GPU_PROPERTY}"
    else
        GPU_PROPERTY="${_default_gpu_property}"
    fi
    if [[ -n "${_ENV_JOB_ID_TAG_SET}" ]]; then
        JOB_ID_TAG="${_ENV_JOB_ID_TAG}"
    else
        JOB_ID_TAG="${_default_job_id_tag}"
    fi
    if [[ -n "${_ENV_MAX_WALLTIME_SET}" ]]; then
        MAX_WALLTIME="${_ENV_MAX_WALLTIME}"
    else
        MAX_WALLTIME="${_default_max_walltime}"
    fi

    CLUSTER_QUEUE_ROOT="${_ENV_CLUSTER_QUEUE_ROOT:-${REMOTE_PROJECT}/.${CLUSTER_NAME}_job_queues}"
    CLUSTER_SESSION_PREFIX="${_ENV_CLUSTER_SESSION_PREFIX:-${REMOTE_PROJECT}/.${CLUSTER_NAME}_session_}"
    SSH_CONTROL_PATH="${_ENV_SSH_CONTROL_PATH:-/tmp/${CLUSTER_NAME}-${_cluster_local_user}-${REMOTE_USER}-${REMOTE_HOST}.sock}"
    EVENT_CACHE="${_ENV_EVENT_CACHE:-/tmp/${CLUSTER_NAME}-events-${_cluster_local_user}-$$}"
    remote="${REMOTE_USER}@${REMOTE_HOST}"
}

REMOTE_USER="${REMOTE_USER:-kalinina}"
REMOTE_PROJECT="${REMOTE_PROJECT:-/home/kalinina/DL_project}"

PROJECT="${PROJECT-pr-molgen}"
GPU_RESOURCES="${GPU_RESOURCES:-/nodes=1/gpu=1}"
WALLTIME="${WALLTIME:-5:00:00}"
# Fast attention removes the quadratic cross-sample attention work. Completed
# 150-epoch runs are comfortably below this separate per-experiment budget.
FAST_ATTENTION_WALLTIME="${FAST_ATTENTION_WALLTIME:-0:25:00}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"

# Packing (scripts/pack_lib.sh, scripts/run_experiment_pack.sh). Defaults are
# cluster-specific: Bigfoot is sized for its weakest V100, while Kraken is
# sized for its weakest H100. Runtime concurrency is then selected from the
# actual V100/A100/H100/H200 assigned by OAR.
# WALLTIME above stays the budget of ONE experiment; a packed job multiplies it
# by its sequential depth and is checked against MAX_WALLTIME.
case "${CLUSTER_NAME}" in
    bigfoot)
        _default_pack_size=9
        _default_pack_walltime_parallel=1
        ;;
    kraken)
        _default_pack_size=12
        _default_pack_walltime_parallel=4
        ;;
esac
PACK_SIZE="${PACK_SIZE:-${_default_pack_size}}"
# 0 means use pack_hardware_profile() on the compute node.
PACK_PARALLEL="${PACK_PARALLEL:-0}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-0}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-1}"
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"
PACK_WALLTIME_PARALLEL="${PACK_WALLTIME_PARALLEL:-${_default_pack_walltime_parallel}}"

# Resolved on the frontend by cluster_preflight_remote.sh; these are only the
# fallbacks used when preflight is skipped.
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"

_cluster_local_user="${USER:-$(id -un)}"

# Apply the requested profile now, so plain `source cluster_common.sh` keeps
# working for the single-cluster callers.
cluster_profile "${CLUSTER_NAME:-bigfoot}" || return 1 2>/dev/null || exit 1

# Back-compat: the pre-port scripts used BIGFOOT_*-prefixed names, and a wait
# daemon started from the old code keeps passing them in its environment.
WAIT_QUEUE_DIR="${WAIT_QUEUE_DIR:-${BIGFOOT_QUEUE_DIR:-}}"
MAX_WAITING_JOBS="${MAX_WAITING_JOBS:-${BIGFOOT_MAX_WAITING_JOBS:-50}}"
QUEUE_HELPER="${QUEUE_HELPER:-${BIGFOOT_QUEUE_HELPER:-scripts/cluster_queue_remote.sh}}"
WAIT_TMUX="${WAIT_TMUX:-${BIGFOOT_WAIT_TMUX:-1}}"
WAIT_TMUX_LOG="${WAIT_TMUX_LOG:-${BIGFOOT_WAIT_TMUX_LOG:-}}"
# tmux session name for a wait loop, derived from the SET of clusters it
# watches: the combined watcher and a single-cluster one must never adopt each
# other's session, log or pid file. Fixed (non-timestamped) so a second
# invocation reattaches instead of spawning a duplicate.
# Both wait_and_sync.sh and cluster_wait_watchdog.sh must use this one formula.
cluster_wait_session() {
    printf 'wait_%s' "$(printf '%s' "$1" | tr -c 'A-Za-z0-9' '_')"
}
WAIT_TMUX_SESSION="${WAIT_TMUX_SESSION:-${BIGFOOT_WAIT_TMUX_SESSION:-$(cluster_wait_session "${CLUSTERS:-${CLUSTER_NAME}}")}}"
WAIT_HEADLESS="${WAIT_HEADLESS:-${BIGFOOT_WAIT_HEADLESS:-0}}"
WAIT_WATCHDOG_STALE_SECONDS="${WAIT_WATCHDOG_STALE_SECONDS:-${BIGFOOT_WATCHDOG_STALE_SECONDS:-900}}"

LOCAL_CONDA_SH="${LOCAL_CONDA_SH:-/opt/anaconda3/etc/profile.d/conda.sh}"
LOCAL_CONDA_ENV="${LOCAL_CONDA_ENV:-rsync-env}"
POLL_SECONDS="${POLL_SECONDS:-60}"

# Serialised list of the settings the submitters read, %q-escaped exactly once
# so it can be prefixed to a remote command and interpreted by the login shell.
# GPU_PROPERTY carries single quotes and parentheses, hence %q rather than
# manual quoting.
cluster_remote_env() {
    printf 'CONDA_SH=%q CONDA_ENV=%q PROJECT=%q GPU_PROPERTY=%q GPU_MODEL_GLOB=%q GPU_RESOURCES=%q WALLTIME=%q FAST_ATTENTION_WALLTIME=%q MIN_FREE_GPU_MIB=%q JOB_ID_TAG=%q OARSUB_EXTRA=%q GROUPS_OVERRIDE=%q SEEDS_OVERRIDE=%q PACK_SIZE=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q COMPLETE_ONLY=%q COMPLETED_EXPERIMENTS=%q PACK_WALLTIME_PARALLEL=%q MAX_WALLTIME=%q' \
        "${CONDA_SH}" "${CONDA_ENV}" "${PROJECT}" "${GPU_PROPERTY}" \
        "${GPU_MODEL_GLOB}" "${GPU_RESOURCES}" "${WALLTIME}" \
        "${FAST_ATTENTION_WALLTIME}" \
        "${MIN_FREE_GPU_MIB}" "${JOB_ID_TAG}" "${OARSUB_EXTRA}" \
        "${GROUPS_OVERRIDE}" "${SEEDS_OVERRIDE}" \
        "${PACK_SIZE}" "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" \
        "${PACK_GPU_PERCENT}" "${PACK_CPU_PER_RUN}" \
        "${PACK_MIN_FREE_GPU_MIB}" "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}" \
        "${COMPLETE_ONLY}" "${COMPLETED_EXPERIMENTS}" \
        "${PACK_WALLTIME_PARALLEL}" "${MAX_WALLTIME}"
}
