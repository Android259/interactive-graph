#!/usr/bin/env bash
# Copy the project code FROM the clusters back to this machine -- the mirror of
# scripts/update_clusters.sh, for picking up edits made directly on a cluster.
#
#   bash scripts/update_local.sh              # bigfoot, then kraken
#   bash scripts/update_local.sh kraken       # one cluster
#   DRY_RUN=1 bash scripts/update_local.sh    # show what would change
#
# Code only; the exclude list is shared with update_clusters.sh
# (scripts/cluster_sync_excludes.sh), so both directions agree on what "code"
# means. Not copied: data/, script_logs/, run/, test_metrics*/, models/,
# testmode_outputs/, graphics/, the metrics tables, and the OAR queues.
#
# Results and logs are deliberately NOT fetched here: scripts/wait_and_sync.sh
# already brings them back, and it knows how to merge several clusters into one
# local tree without one overwriting the other.
#
# With more than one cluster the LAST one wins for any file both have changed,
# because they are copied in sequence into the same tree. Pass a single cluster
# when that matters.
#
# There is no PRUNE here on purpose: deleting local files because a cluster
# lacks them would throw away work that only exists on this machine.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CLUSTERS="${CLUSTERS:-bigfoot kraken}"
if (( $# > 0 )); then
    CLUSTERS="$*"
fi
DRY_RUN="${DRY_RUN:-0}"

# shellcheck source=scripts/cluster_common.sh
CLUSTER_NAME="${CLUSTERS%% *}"
source "${SCRIPT_DIR}/cluster_common.sh"

# shellcheck source=scripts/cluster_sync_excludes.sh
source "${SCRIPT_DIR}/cluster_sync_excludes.sh"

# update_local is for code recovery, not for downloading cluster datasets.
SYNC_EXCLUDES+=(--exclude='/data/')

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
        "test -d '${REMOTE_PROJECT}'" 2>/dev/null
    then
        printf '  cannot reach %s (or %s is missing); skipped.\n' \
            "${remote}" "${REMOTE_PROJECT}" >&2
        failed+=("${cluster}")
        continue
    fi

    # The exit status is checked explicitly: a silent rsync failure must not be
    # reported as a successful copy.
    if rsync "${rsync_flags[@]}" -e "${ssh_opt}" "${SYNC_EXCLUDES[@]}" \
        "${remote}:${REMOTE_PROJECT}/" "${PROJECT_ROOT}/"
    then
        if (( DRY_RUN )); then
            printf '  dry run only, nothing was written.\n'
        else
            printf '  copied.\n'
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
    printf '\nCopied from: %s\n' "${CLUSTERS}"
fi
