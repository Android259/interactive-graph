#!/usr/bin/env bash
# Cluster profile shared by launch/run_cluster.sh and wait_and_sync.sh.
# `source` it after setting CLUSTER_NAME.
#
# Every value here is derived from CLUSTER_NAME so that a Bigfoot run and a
# Kraken run can proceed at the same time without sharing a queue directory, an
# ssh ControlMaster socket or an output-file namespace.
#
# Callers may override any of these from the environment; the assignments use
# `${VAR:-default}` except for PROJECT/GPU_PROPERTY, where `${VAR-default}`
# lets an explicitly empty value survive and omit the corresponding oarsub flag.

# shellcheck source=scripts/settings.sh
source "$(dirname "${BASH_SOURCE[0]}")/../settings.sh"

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
    _ENV_OAR_RESOURCES="${OAR_RESOURCES:-}"
    _ENV_CPU_ONLY="${CPU_ONLY:-}"
    _ENV_CLUSTER_QUEUE_ROOT="${CLUSTER_QUEUE_ROOT:-}"
    _ENV_CLUSTER_SESSION_PREFIX="${CLUSTER_SESSION_PREFIX:-}"
    _ENV_SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-}"
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
            # Bigfoot's unit of allocation is a GPU; cores and memory come bundled
            # pro-rata (GRICAD docs: "the resource unit to request is usually a
            # gpu"). Prefer A100 nodes when GPU_PROPERTY allows either -- 64 cores
            # / 2 GPUs = 32 cores per gpu=1, against a V100 node's 8-10.
            _default_oar_resources="/nodes=1/gpu=1"
            _default_cpu_only=0
            ;;
        kraken)
            # kraken-gpu is the GPU frontend; kraken-cpu is the separate CPU-only
            # frontend below.
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
            _default_oar_resources="/nodes=1/gpu=1"
            _default_cpu_only=0
            ;;
        kraken-cpu)
            # Genuinely CPU-only frontend, separate from kraken-gpu -- unlike
            # Bigfoot/kraken-gpu, cores are the unit to request directly (GRICAD
            # Kraken docs: "oarsub -l /core=54" / "-l /nodes=1" for a whole node),
            # no GPU ticket needed at all. One node is 192 cores (2x AMD EPYC
            # 9654/9655, 768-1536 GiB RAM) -- for a --descriptors_head-sized model
            # (~1000 params, 1 OMP thread/run measured optimal, see run_local.sh)
            # that is enough to run an entire 35-45 job grid concurrently on one
            # node instead of one GPU allocation's bundled 8-32 cores on Bigfoot.
            _default_host="kraken-cpu"
            _default_gpu_property=""
            _default_gpu_glob=""
            # "c" for CPU: distinct from Bigfoot's "" and kraken-gpu's "k", so the
            # three clusters' OAR ids never collide in script_logs/*.out names.
            _default_job_id_tag="c"
            # Not documented for kraken-cpu specifically (only kraken-gpu's cap is
            # published, and it has none either); leave unchecked rather than
            # guessing kraken-gpu's number applies here too.
            _default_max_walltime=""
            # One whole node, not a partial /core=N: the anti-fragmentation note
            # in GRICAD's docs favours full architectural units, and one node's
            # 192 cores are already far more than this project's grids need.
            _default_oar_resources="/nodes=1"
            _default_cpu_only=1
            ;;
        *)
            printf 'Unknown cluster: %s (expected bigfoot, kraken or kraken-cpu)\n' \
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
    OAR_RESOURCES="${_ENV_OAR_RESOURCES:-${_default_oar_resources}}"
    CPU_ONLY="${_ENV_CPU_ONLY:-${_default_cpu_only}}"

    CLUSTER_QUEUE_ROOT="${_ENV_CLUSTER_QUEUE_ROOT:-${REMOTE_PROJECT}/.${CLUSTER_NAME}_job_queues}"
    CLUSTER_SESSION_PREFIX="${_ENV_CLUSTER_SESSION_PREFIX:-${REMOTE_PROJECT}/.${CLUSTER_NAME}_session_}"
    SSH_CONTROL_PATH="${_ENV_SSH_CONTROL_PATH:-/tmp/${CLUSTER_NAME}-${_cluster_local_user}-${REMOTE_USER}-${REMOTE_HOST}.sock}"
    remote="${REMOTE_USER}@${REMOTE_HOST}"
}

REMOTE_USER="${REMOTE_USER:-kalinina}"
REMOTE_PROJECT="${REMOTE_PROJECT:-/home/kalinina/DL_project}"

PROJECT="${PROJECT-pr-molgen}"
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
#
# The default matches cluster_profile()'s below, so a caller that only wants the
# host and the queue paths can source this without naming a cluster first --
# under `set -u` a bare ${CLUSTER_NAME} here aborted such a caller outright.
case "${CLUSTER_NAME:-bigfoot}" in
    bigfoot)
        _default_pack_size=9
        # Two, not one: Bigfoot's GPU_PROPERTY matches A100 (four slots) and V100 (two),
        # so two is what the weakest card delivers. Measured on the V100 node the mcs
        # pack landed on -- 32768 MiB, 10 cores -> cap 2, memory 2, CPU 2. Leaving it at
        # 1 while the per-experiment budget rose would have inflated a nine-run pack's
        # request from 3:45 to 5:15 for no reason.
        _default_pack_walltime_parallel=2
        ;;
    kraken)
        _default_pack_size=12
        # Four: the weakest card GPU_PROPERTY matches runs four at a time. Eight was
        # tried on 2026-08-19 and reverted -- see the h100 profile in pack_lib.sh; past
        # four the card is saturated and total throughput drops rather than rises.
        _default_pack_walltime_parallel=4
        _default_pack_cpu_per_run=0
        ;;
    kraken-cpu)
        # 180, not 192: one node's core count minus headroom for OS/monitoring
        # overhead alongside 1-core-per-run jobs (PACK_CPU_PER_RUN below). Raised
        # from 45 (one 9-group x 5-seed grid) once cross-label packing meant
        # several labels' grids needed to share one pack to land in one OAR job
        # -- see PACK_WALLTIME_PARALLEL below for why the walltime this implies
        # is still safe.
        _default_pack_size=180
        # Equal to PACK_SIZE (full-parallel, depth=1 for any pack up to it), not
        # a fraction of it: with PACK_CPU_PER_RUN=1 and 192 cores on the node,
        # every experiment in a pack of up to 180 gets its own core at the same
        # time -- there is no sequential wave to size a depth multiplier for.
        # pack_job_walltime computes depth = ceil(pack_size / this), so any
        # value below PACK_SIZE invents a wave that does not exist and doubles
        # (or worse) the requested walltime for no reason -- measured on
        # kraken-cpu (script_logs/descriptors_no_extent_ckpt_seeds01234/_packs/
        # descriptors_no_extent_ckpt_pack0_c1468924.pack.out, "PACK finished: 35
        # experiment(s)"): a 35-experiment pack finished in ~3 minutes wall
        # clock against a 35-minute-per-run budget -- full concurrency, not the
        # sequential "one at a time" the old default of 1 assumed (which
        # requested 26h15m for that same 45-pack).
        _default_pack_walltime_parallel="${_default_pack_size}"
        # 1 core/run: this project's one measured tiny-model config
        # (--descriptors_head, ~1000 parameters) tops out at 1 OMP thread/run
        # before multithreading synchronisation overhead exceeds its own payoff
        # (scripts/run_local.sh's MAX_OMP_THREADS_PER_JOB auto-detection for the
        # same flag). A heavier config run here needs an explicit
        # PACK_CPU_PER_RUN override -- there is no GPU-model-keyed profile to
        # infer one from the way pack_hardware_profile() does for bigfoot/kraken.
        _default_pack_cpu_per_run=1
        ;;
esac
PACK_SIZE="${PACK_SIZE:-${_default_pack_size}}"
# 0 means use pack_hardware_profile() on the compute node (bigfoot/kraken); for
# kraken-cpu (CPU_ONLY=1, no GPU to profile) run_experiment_pack.sh instead
# falls back to PACK_CPU_PER_RUN itself when this is 0, so 0 keeps working as
# "no override" for both paths.
PACK_PARALLEL="${PACK_PARALLEL:-0}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-${_default_pack_cpu_per_run:-0}}"
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

LOCAL_CONDA_SH="${LOCAL_CONDA_SH:-/opt/anaconda3/etc/profile.d/conda.sh}"
LOCAL_CONDA_ENV="${LOCAL_CONDA_ENV:-rsync-env}"

# Serialised list of the settings the submitter reads, %q-escaped exactly once
# so it can be prefixed to a remote command and interpreted by the login shell.
# GPU_PROPERTY carries single quotes and parentheses, hence %q rather than
# manual quoting.
cluster_remote_env() {
    printf 'CONDA_SH=%q CONDA_ENV=%q PROJECT=%q GPU_PROPERTY=%q GPU_MODEL_GLOB=%q OAR_RESOURCES=%q CPU_ONLY=%q WALLTIME=%q FAST_ATTENTION_WALLTIME=%q DESCRIPTORS_HEAD_WALLTIME=%q MIN_FREE_GPU_MIB=%q JOB_ID_TAG=%q OARSUB_EXTRA=%q GROUPS_OVERRIDE=%q SEEDS_OVERRIDE=%q PACK_SIZE=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q COMPLETE_ONLY=%q COMPLETED_EXPERIMENTS=%q PACK_WALLTIME_PARALLEL=%q MAX_WALLTIME=%q' \
        "${CONDA_SH}" "${CONDA_ENV}" "${PROJECT}" "${GPU_PROPERTY}" \
        "${GPU_MODEL_GLOB}" "${OAR_RESOURCES}" "${CPU_ONLY}" "${WALLTIME}" \
        "${FAST_ATTENTION_WALLTIME}" "${DESCRIPTORS_HEAD_WALLTIME}" \
        "${MIN_FREE_GPU_MIB}" "${JOB_ID_TAG}" "${OARSUB_EXTRA}" \
        "${GROUPS_OVERRIDE}" "${SEEDS_OVERRIDE}" \
        "${PACK_SIZE}" "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" \
        "${PACK_GPU_PERCENT}" "${PACK_CPU_PER_RUN}" \
        "${PACK_MIN_FREE_GPU_MIB}" "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}" \
        "${COMPLETE_ONLY}" "${COMPLETED_EXPERIMENTS}" \
        "${PACK_WALLTIME_PARALLEL}" "${MAX_WALLTIME}"
}
