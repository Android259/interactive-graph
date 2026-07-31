#!/usr/bin/env bash
# Upload the project to every cluster.
#
#   bash scripts/update_clusters.sh              # bigfoot and kraken
#   bash scripts/update_clusters.sh kraken       # one cluster
#   DRY_RUN=1 bash scripts/update_clusters.sh    # show what would change
#   NO_DELETE=1 bash scripts/update_clusters.sh  # add/update only, delete nothing
#
# The cluster copy is made to MIRROR the local tree: anything there that is not
# in the local tree and not in the exclude list is deleted. rsync protects
# excluded paths from deletion automatically, so oversized data files, run/, test_metrics*/,
# models/, script_logs/, testmode_outputs/ and the OAR queues on the cluster are
# never touched -- only stray code is removed.
#
# Deliberately NOT sent:
#   files in data/ over MAX_DATA_FILE_BYTES (default: 1 GiB)
#   run/ test_metrics*/ models/ testmode_outputs/ graphics/
#   script_logs/                -- job logs are produced ON the cluster and
#                                  travel the other way, via wait_and_sync.sh
#   metrics_summary*.csv metrics_analysis.txt feature_contributions.csv
#   the OAR job queues and session markers of BOTH clusters
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CLUSTERS="${CLUSTERS:-bigfoot kraken}"
if (( $# > 0 )); then
    CLUSTERS="$*"
fi
DRY_RUN="${DRY_RUN:-0}"
NO_DELETE="${NO_DELETE:-0}"
MAX_DATA_FILE_BYTES="${MAX_DATA_FILE_BYTES:-1073741824}"

if [[ ! "${MAX_DATA_FILE_BYTES}" =~ ^[0-9]+$ ]] || (( MAX_DATA_FILE_BYTES < 1 )); then
    printf 'MAX_DATA_FILE_BYTES must be a positive integer.\n' >&2
    exit 2
fi

# shellcheck source=scripts/cluster_common.sh
CLUSTER_NAME="${CLUSTERS%% *}"
source "${SCRIPT_DIR}/cluster_common.sh"

# shellcheck source=scripts/cluster_sync_excludes.sh
source "${SCRIPT_DIR}/cluster_sync_excludes.sh"

# Sync all ordinary data inputs. Generate exact filters for large local files
# instead of excluding data/ wholesale or maintaining a fragile allowlist.
# Protect the same paths because --delete-excluded is used for mirror cleanup.
while IFS= read -r -d '' data_file; do
    relative_path="${data_file#${PROJECT_ROOT}/}"
    SYNC_EXCLUDES+=(--exclude="/${relative_path}")
    SYNC_PROTECT+=(--filter="P /${relative_path}")
done < <(find "${PROJECT_ROOT}/data" -type f -size "+${MAX_DATA_FILE_BYTES}c" -print0)

if ! command -v rsync >/dev/null 2>&1; then
    if [[ -f "${LOCAL_CONDA_SH}" ]]; then
        # shellcheck disable=SC1090
        source "${LOCAL_CONDA_SH}"
        conda activate "${LOCAL_CONDA_ENV}"
    fi
fi
if ! command -v rsync >/dev/null 2>&1; then
    printf 'rsync is not available (tried conda env %s).\n' "${LOCAL_CONDA_ENV}" >&2
    exit 127
fi

rsync_flags=(-az --human-readable)
(( DRY_RUN )) && rsync_flags+=(--dry-run --itemize-changes)
# Mirror by default: remove remote files that no longer exist locally. Excluded
# paths are protected by rsync and are never deleted.
# --delete-excluded plus SYNC_PROTECT: caches inside a stale copy are removed
# (they are excluded, so plain --delete would protect them and keep the whole
# stale tree alive), while the project directories in SYNC_PROTECT survive.
(( NO_DELETE )) || rsync_flags+=(--delete --delete-excluded)

failed=()
for cluster in ${CLUSTERS}; do
    cluster_profile "${cluster}" || { failed+=("${cluster}"); continue; }

    # Reuse an existing ControlMaster when one is up; otherwise a direct
    # connection (which may prompt for a password at the jump host).
    ssh_opt="ssh -o ConnectTimeout=25"
    if ssh -S "${SSH_CONTROL_PATH}" -O check "${remote}" >/dev/null 2>&1; then
        ssh_opt="ssh -S ${SSH_CONTROL_PATH}"
    fi

    printf '=== %s (%s) ===\n' "${cluster}" "${remote}"
    if ! ssh ${ssh_opt#ssh } -o ConnectTimeout=25 "${remote}" \
        "mkdir -p '${REMOTE_PROJECT}'" 2>/dev/null
    then
        printf '  cannot reach %s; skipped.\n' "${remote}" >&2
        failed+=("${cluster}")
        continue
    fi

    # The exit status is checked explicitly: a silent rsync failure must not be
    # reported as a successful update.
    if rsync "${rsync_flags[@]}" -e "${ssh_opt}" "${SYNC_PROTECT[@]}" "${SYNC_EXCLUDES[@]}" \
        "${PROJECT_ROOT}/" "${remote}:${REMOTE_PROJECT}/"
    then
        if (( DRY_RUN )); then
            printf '  dry run only, nothing was written.\n'
        else
            printf '  updated.\n'
        fi
    else
        printf '  rsync failed for %s.\n' "${cluster}" >&2
        failed+=("${cluster}")
    fi
done

if (( ${#failed[@]} )); then
    printf '\nFailed: %s\n' "${failed[*]}" >&2
    exit 1
fi
if (( DRY_RUN )); then
    printf '\nDry run complete for: %s (nothing was written)\n' "${CLUSTERS}"
else
    printf '\nAll clusters updated: %s\n' "${CLUSTERS}"
fi
