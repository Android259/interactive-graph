#!/usr/bin/env bash
# Copy the project code between this machine and the clusters, in either
# direction. One file for both, because it is one operation with one exclude
# list (scripts/lib/cluster_sync_excludes.sh) -- what counts as "code" must not
# depend on which way it is travelling.
#
#   bash scripts/tools/sync_project.sh                  # here -> bigfoot and kraken
#   bash scripts/tools/sync_project.sh kraken           # here -> one cluster
#   bash scripts/tools/sync_project.sh --from           # clusters -> here
#   bash scripts/tools/sync_project.sh --from kraken    # one cluster -> here
#   DRY_RUN=1 bash scripts/tools/sync_project.sh        # show what would change
#   NO_DELETE=1 bash scripts/tools/sync_project.sh      # add/update only, delete nothing
#
# UP (the default) MIRRORS: anything on the cluster that is not here and not
# excluded is deleted, so stray code cannot linger there. Deliberately not sent:
# files in data/ over MAX_DATA_FILE_BYTES (default 1 GiB), run/, test_metrics*/,
# models/, testmode_outputs/, graphics/, script_logs/, the metrics tables, and
# both clusters' OAR queues and session markers.
#
# DOWN never deletes: removing a local file because a cluster lacks it would
# throw away work that exists only here. It also skips data/ -- it is for picking
# up edits made on a cluster, not for downloading datasets. Results and logs are
# not fetched here either; scripts/wait_and_sync.sh brings those back and knows
# how to merge several clusters into one local tree.
#
# With more than one cluster going DOWN, the LAST one wins for a file both
# changed, since they are copied in sequence into the same tree. Name one cluster
# when that matters.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DIRECTION="up"
POSITIONALS=()
while (( $# > 0 )); do
    case "$1" in
        --from|--down) DIRECTION="down"; shift ;;
        --to|--up)     DIRECTION="up"; shift ;;
        -h|--help)     awk 'NR == 1 { next } !/^#/ { exit } { sub(/^# ?/, ""); print }' \
                           "${BASH_SOURCE[0]}"; exit 0 ;;
        -*)            printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
        *)             POSITIONALS+=("$1"); shift ;;
    esac
done

CLUSTERS="${CLUSTERS:-bigfoot kraken}"
if (( ${#POSITIONALS[@]} > 0 )); then
    CLUSTERS="${POSITIONALS[*]}"
fi
DRY_RUN="${DRY_RUN:-0}"
NO_DELETE="${NO_DELETE:-0}"
MAX_DATA_FILE_BYTES="${MAX_DATA_FILE_BYTES:-1073741824}"

if [[ ! "${MAX_DATA_FILE_BYTES}" =~ ^[0-9]+$ ]] || (( MAX_DATA_FILE_BYTES < 1 )); then
    printf 'MAX_DATA_FILE_BYTES must be a positive integer.\n' >&2
    exit 2
fi

# shellcheck source=scripts/lib/cluster_common.sh
CLUSTER_NAME="${CLUSTERS%% *}"
source "${SCRIPT_DIR}/../lib/cluster_common.sh"
# shellcheck source=scripts/lib/cluster_sync_excludes.sh
source "${SCRIPT_DIR}/../lib/cluster_sync_excludes.sh"
# shellcheck source=scripts/lib/ssh_master_lib.sh
source "${SCRIPT_DIR}/../lib/ssh_master_lib.sh"

rsync_flags=(-az --human-readable)
(( DRY_RUN )) && rsync_flags+=(--dry-run --itemize-changes)

if [[ "${DIRECTION}" == "up" ]]; then
    # Exact filters for oversized local files, rather than excluding data/
    # wholesale or maintaining a fragile allowlist. Protected as well as
    # excluded, because --delete-excluded is used for the mirror cleanup.
    while IFS= read -r -d '' data_file; do
        relative_path="${data_file#"${PROJECT_ROOT}"/}"
        SYNC_EXCLUDES+=(--exclude="/${relative_path}")
        SYNC_PROTECT+=(--filter="P /${relative_path}")
    done < <(find "${PROJECT_ROOT}/data" -type f -size "+${MAX_DATA_FILE_BYTES}c" -print0)

    # Mirror by default. --delete-excluded plus SYNC_PROTECT: caches inside a
    # stale copy are removed (they are excluded, so plain --delete would protect
    # them and keep the whole stale tree alive), while the project directories in
    # SYNC_PROTECT survive.
    (( NO_DELETE )) || rsync_flags+=(--delete --delete-excluded)
    rsync_filters=("${SYNC_PROTECT[@]}" "${SYNC_EXCLUDES[@]}")
else
    SYNC_EXCLUDES+=(--exclude='/data/')
    rsync_filters=("${SYNC_EXCLUDES[@]}")
fi

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

failed=()
for cluster in ${CLUSTERS}; do
    cluster_profile "${cluster}" || { failed+=("${cluster}"); continue; }

    # Reuse the shared connection when one is up; otherwise a direct connection
    # (which may prompt for a password at the jump host). Deliberately does NOT
    # open a shared one: this is a one-off copy, and leaving a connection behind
    # for half an hour after it is not its business.
    ssh_opt="ssh -o ConnectTimeout=${SSH_CONNECT_TIMEOUT}"
    if ssh_master_alive; then
        ssh_opt="ssh -S ${SSH_CONTROL_PATH}"
    fi

    printf '=== %s (%s) ===\n' "${cluster}" "${remote}"
    if [[ "${DIRECTION}" == "up" ]]; then
        probe="mkdir -p '${REMOTE_PROJECT}'"
    else
        probe="test -d '${REMOTE_PROJECT}'"
    fi
    if ! ssh ${ssh_opt#ssh } -o ConnectTimeout="${SSH_CONNECT_TIMEOUT}" "${remote}" \
        "${probe}" 2>/dev/null
    then
        printf '  cannot reach %s (or %s is missing); skipped.\n' \
            "${remote}" "${REMOTE_PROJECT}" >&2
        failed+=("${cluster}")
        continue
    fi

    if [[ "${DIRECTION}" == "up" ]]; then
        source_path="${PROJECT_ROOT}/"
        target_path="${remote}:${REMOTE_PROJECT}/"
    else
        source_path="${remote}:${REMOTE_PROJECT}/"
        target_path="${PROJECT_ROOT}/"
    fi

    # The exit status is checked explicitly: a silent rsync failure must not be
    # reported as a successful update.
    if rsync "${rsync_flags[@]}" -e "${ssh_opt}" "${rsync_filters[@]}" \
        "${source_path}" "${target_path}"
    then
        if (( DRY_RUN )); then
            printf '  dry run only, nothing was written.\n'
        else
            printf '  done.\n'
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
elif [[ "${DIRECTION}" == "up" ]]; then
    printf '\nAll clusters updated: %s\n' "${CLUSTERS}"
else
    printf '\nCopied from: %s\n' "${CLUSTERS}"
fi
