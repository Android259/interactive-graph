#!/usr/bin/env bash
# Sync this project to a cluster, queue its OAR jobs, and hand off to the
# wait/sync loop. Cluster-generic: entered through scripts/run_bigfoot.sh or
# scripts/run_kraken.sh, which set CLUSTER_NAME.
#
# Takes either a submitter under scripts/submit/ or an scripts/arg_files/*.md
# config (which routes to the canonical all-groups or cold-split submitter).
#
# Cluster differences (GPU model, walltime, OAR project, conda paths) are passed
# to the submitters as environment variables -- never by patching their text.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=scripts/cluster_common.sh
source "${SCRIPT_DIR}/cluster_common.sh"

# shellcheck source=scripts/cluster_sync_excludes.sh
source "${SCRIPT_DIR}/cluster_sync_excludes.sh"

SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-0}"

usage() {
    printf 'Usage: bash %s [--complete] [--seeds=LIST] SUBMIT_SCRIPT_OR_ARGS_FILE\n' "${0##*/}" >&2
    printf 'Example: bash %s common_attention_all_groups\n' "${0##*/}" >&2
    printf 'Example: bash %s scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --seeds=0,1,2 scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf '\n' >&2
    printf '  --seeds=LIST  Comma-separated seeds to run every excluded group on.\n' >&2
    printf '                --seeds=0,1,2 runs all 9 groups on seeds 0, 1 and 2\n' >&2
    printf '                (27 jobs); --seeds=0 runs 9 jobs. Default: 0,1,2,3,4.\n' >&2
    printf '  --complete    Submit only group/seed pairs without final test_metrics.\n' >&2
}

# Pull option flags off the argument list; exactly one positional (the submitter
# or args file) must remain. --seeds sets SEEDS_OVERRIDE, which cluster_common.sh
# forwards to the submitters (a space-separated seed list).
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
        --seeds)
            if (( $# < 2 )); then
                printf '%s requires an argument.\n' "$1" >&2
                usage
                exit 2
            fi
            SEEDS_ARG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            while (( $# > 0 )); do POSITIONALS+=("$1"); shift; done
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

if [[ -n "${SEEDS_ARG:-}" ]]; then
    # Accept commas or whitespace between seeds; store space-separated.
    read -r -a _seed_list <<< "${SEEDS_ARG//,/ }"
    if (( ${#_seed_list[@]} == 0 )); then
        printf 'No seeds given to --seeds.\n' >&2
        exit 2
    fi
    for _seed in "${_seed_list[@]}"; do
        if [[ ! "${_seed}" =~ ^[0-9]+$ ]]; then
            printf 'Invalid seed (must be a non-negative integer): %s\n' "${_seed}" >&2
            exit 2
        fi
    done
    export SEEDS_OVERRIDE="${_seed_list[*]}"
fi

if (( ${#POSITIONALS[@]} != 1 )); then
    usage
    exit 2
fi

INPUT_ARG="${POSITIONALS[0]}"
REMOTE_SCRIPT=""
REMOTE_INPUT_PATH=""

if [[ -f "${INPUT_ARG}" ]]; then
    if [[ "${INPUT_ARG}" != *.md ]]; then
        printf 'Unsupported file type: %s\n' "${INPUT_ARG}" >&2
        exit 2
    fi
    REMOTE_INPUT_PATH="${INPUT_ARG}"
elif [[ -f "${PROJECT_ROOT}/scripts/arg_files/${INPUT_ARG}" ]]; then
    REMOTE_INPUT_PATH="scripts/arg_files/${INPUT_ARG}"
elif [[ -f "${PROJECT_ROOT}/${INPUT_ARG}" ]]; then
    REMOTE_INPUT_PATH="${INPUT_ARG}"
else
    SCRIPT_NAME="${INPUT_ARG%.sh}"
    if [[ ! "${SCRIPT_NAME}" =~ ^[A-Za-z0-9_-]+$ ]]; then
        printf 'Invalid SCRIPT_NAME: %s\n' "${SCRIPT_NAME}" >&2
        exit 2
    fi
    REMOTE_SCRIPT="scripts/submit/${SCRIPT_NAME}.sh"
fi

if [[ -n "${REMOTE_SCRIPT}" && ! -f "${PROJECT_ROOT}/${REMOTE_SCRIPT}" ]]; then
    printf 'Remote script not found: %s\n' "${REMOTE_SCRIPT}" >&2
    exit 2
fi

# Preserve locally completed pairs across the code-only rsync. The remote
# submitter merges this list with reports already present on that cluster.
if [[ "${COMPLETE_ONLY}" == "1" && -n "${REMOTE_INPUT_PATH}" ]]; then
    variant="$(basename "${REMOTE_INPUT_PATH}" .md)"
    complete_args=()
    if grep -qE '^--cold_split([[:space:]=]|$)' "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}"; then
        complete_args+=(--cold-split)
    fi
    COMPLETED_EXPERIMENTS="$(
        python3 "${SCRIPT_DIR}/list_completed_experiments.py" \
            "${variant}" --reports-root "${PROJECT_ROOT}/test_metrics" \
            "${complete_args[@]}"
    )"
    export COMPLETE_ONLY COMPLETED_EXPERIMENTS
fi

remote="${REMOTE_USER}@${REMOTE_HOST}"

if ! command -v rsync >/dev/null 2>&1; then
    if [[ -f "${LOCAL_CONDA_SH}" ]]; then
        # shellcheck disable=SC1090
        source "${LOCAL_CONDA_SH}"
        conda activate "${LOCAL_CONDA_ENV}"
    fi
fi

if ! command -v rsync >/dev/null 2>&1; then
    printf 'rsync is not available. Tried local conda env: %s\n' \
        "${LOCAL_CONDA_ENV}" >&2
    exit 127
fi

{
    flock 9
    if ssh -S "${SSH_CONTROL_PATH}" -O check "${remote}" >/dev/null 2>&1; then
        printf 'Reusing shared SSH connection to %s.\n' "${remote}"
    else
        printf 'Opening shared SSH connection to %s.\n' "${remote}"
        ssh -M -S "${SSH_CONTROL_PATH}" -o ControlPersist=30m -fN "${remote}"
    fi
} 9>"${SSH_CONTROL_PATH}.lock"

printf 'Synchronizing local project to %s:%s.\n' "${remote}" "${REMOTE_PROJECT}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" "mkdir -p '${REMOTE_PROJECT}'"
# Exactly the same file set and rules as scripts/update_clusters.sh, from the
# shared scripts/cluster_sync_excludes.sh: code only, and the cluster copy is
# mirrored (stale files removed). SYNC_PROTECT keeps data/, results, logs, the
# metrics tables and BOTH clusters' OAR queues from being deleted -- the queues
# live only on the remote side, so a sync from the other cluster's runner must
# not wipe a live pending queue.
rsync -az --delete --delete-excluded --quiet -e "ssh -S ${SSH_CONTROL_PATH}" \
    "${SYNC_PROTECT[@]}" \
    "${SYNC_EXCLUDES[@]}" \
    "${PROJECT_ROOT}/" \
    "${remote}:${REMOTE_PROJECT}/"

# Preflight runs after the sync (it inspects the synced tree) and before any
# remote state is created, so a failure leaves nothing behind to clean up.
if [[ "${SKIP_PREFLIGHT}" != "1" ]]; then
    printf 'Running preflight checks on %s.\n' "${remote}"
    preflight_required_arch=""
    case "${CLUSTER_NAME}" in
        kraken) preflight_required_arch="sm_90" ;;   # H100 / H200
    esac

    preflight_output=""
    if ! preflight_output="$(
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
            "cd '${REMOTE_PROJECT}' && CONDA_ENV=$(printf '%q' "${CONDA_ENV}") CONDA_SH=$(printf '%q' "${CONDA_SH}") REQUIRED_ARCH=$(printf '%q' "${preflight_required_arch}") bash scripts/cluster_preflight_remote.sh"
    )"; then
        printf 'Preflight failed on %s; not submitting anything.\n' "${remote}" >&2
        printf '%s\n' "${preflight_output}" >&2
        exit 3
    fi
    printf '%s\n' "${preflight_output}" | sed 's/^/  /'

    # Adopt what preflight resolved, unless the caller pinned it explicitly.
    preflight_value() {
        printf '%s\n' "${preflight_output}" | sed -n "s/^$1=//p" | head -n 1
    }
    if [[ -z "${CONDA_SH_PINNED:-}" ]]; then
        discovered_conda_sh="$(preflight_value CONDA_SH)"
        [[ -n "${discovered_conda_sh}" ]] && CONDA_SH="${discovered_conda_sh}"
    fi
    if [[ -z "${PROJECT_PINNED:-}" && -z "${PROJECT}" ]]; then
        discovered_projects="$(preflight_value PROJECTS)"
        if [[ "${discovered_projects}" == *,* ]]; then
            printf 'Several OAR projects available (%s). Re-run with PROJECT=<name>.\n' \
                "${discovered_projects}" >&2
            exit 3
        elif [[ -n "${discovered_projects}" ]]; then
            PROJECT="${discovered_projects}"
            printf 'Using OAR project: %s\n' "${PROJECT}"
        fi
    fi
fi

SESSION_MARKER="${CLUSTER_SESSION_PREFIX}$(date +%Y%m%d_%H%M%S)_$$"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" "touch '${SESSION_MARKER}'"

REMOTE_QUEUE_DIR="${CLUSTER_QUEUE_ROOT}/active"

if [[ -n "${REMOTE_INPUT_PATH}" ]]; then
    printf 'Preparing to submit arguments file: %s\n' "${REMOTE_INPUT_PATH}"
    rsync -az --quiet -e "ssh -S ${SSH_CONTROL_PATH}" \
        "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}" \
        "${remote}:${REMOTE_PROJECT}/${REMOTE_INPUT_PATH}"
    # Select the submitter from the arguments file: a --cold_split flag needs the
    # cold-split series (separate held-out validation and test groups per fold),
    # so route straight to the dedicated launcher instead of relying on
    # downstream exec-delegation surviving the queue capture.
    if grep -qE '^--cold_split([[:space:]=]|$)' "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}"; then
        REMOTE_SCRIPT="scripts/submit_cold_val_test_all_seeds.sh"
        printf 'Detected --cold_split; using %s.\n' "${REMOTE_SCRIPT}"
    else
        REMOTE_SCRIPT="scripts/submit_all_groups_all_seeds.sh"
    fi
fi

# The cluster settings are %q-escaped exactly once (see cluster_remote_env) and
# then interpreted once by the remote login shell. GPU_PROPERTY carries single
# quotes and parentheses, so this must not be quoted by hand.
remote_env="$(cluster_remote_env)"

printf 'Queuing OAR jobs on %s.\n' "${remote}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} ${remote_env} bash scripts/cluster_queue_remote.sh capture '${REMOTE_QUEUE_DIR}' '${REMOTE_SCRIPT}' '${SESSION_MARKER}' '${REMOTE_INPUT_PATH}'"

# A wrong PROJECT or GPU_PROPERTY fails on the FIRST oarsub: drain keeps the
# remaining commands pending and returns non-zero, so nothing is lost -- fix the
# setting and re-run rather than re-queuing 45 jobs.
printf 'Submitting queued OAR jobs now.\n'
ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} bash scripts/cluster_queue_remote.sh drain '${REMOTE_QUEUE_DIR}' '${REMOTE_USER}' '${MAX_WAITING_JOBS}'"

SESSION_MARKER="$(
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "cat '${REMOTE_QUEUE_DIR}/session_marker' 2>/dev/null || printf '%s\n' '${SESSION_MARKER}'"
)"

# Hand off to the combined watcher: it visits every cluster in turn, so jobs
# still running on the OTHER cluster keep being synced too, and the metrics
# table is rebuilt once per round from the merged local tree. HANDOFF_CLUSTER
# tells it which cluster the marker and queue below belong to.
# WATCH_CLUSTERS=<name> narrows it back to a single cluster.
printf 'Jobs queued. Waiting for completion and synchronization.\n'
CLUSTERS="${WATCH_CLUSTERS:-bigfoot kraken}" \
HANDOFF_CLUSTER="${CLUSTER_NAME}" \
REMOTE_USER="${REMOTE_USER}" \
REMOTE_PROJECT="${REMOTE_PROJECT}" \
LOCAL_PROJECT="${PROJECT_ROOT}" \
CONDA_SH="${CONDA_SH}" \
CONDA_ENV="${CONDA_ENV}" \
SESSION_MARKER="${SESSION_MARKER}" \
WAIT_QUEUE_DIR="${REMOTE_QUEUE_DIR}" \
MAX_WAITING_JOBS="${MAX_WAITING_JOBS}" \
    bash "${SCRIPT_DIR}/wait_and_sync.sh"
