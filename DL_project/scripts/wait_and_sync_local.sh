#!/usr/bin/env bash
# Watch the run_local.sh grid on THIS machine and nothing else: the same
# "----- local -----" table wait_and_sync.sh prints, with no cluster, no SSH and
# no rsync anywhere in the path.
#
#   bash scripts/wait_and_sync_local.sh          # poll every POLL_SECONDS
#   bash scripts/wait_and_sync_local.sh --once   # one round, then exit
#
#   POLL_SECONDS  seconds between rounds. Default: 30 (local state is a pgrep
#                  and a file read, so polling costs far less than the cluster
#                  path's 60 s default).
#
# Why this exists next to wait_and_sync.sh: that script watches clusters, and
# local jobs ride along as a third source. Everything it does around them --
# opening the shared SSH connection, draining the queue, rsyncing results back --
# is cluster machinery a local grid has no use for. When a cluster is simply
# unreachable (VPN down, laptop off the network) that machinery is pure cost:
# three connection attempts and a ~20 s timeout per cluster, every round, to
# learn nothing about the jobs running on this very machine.
#
# It reads the same two things run_local.sh writes and nothing else --
# script_logs/local_run.queue and the pid-tagged *_l<pid>.out files -- through
# the same poll_local() as wait_and_sync.sh, so the two never disagree about
# what is running here.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_PROJECT="${LOCAL_PROJECT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
POLL_SECONDS="${POLL_SECONDS:-300}"

usage() {
    printf 'Usage: bash %s [--once]\n' "${0##*/}" >&2
}

once=0
while (( $# > 0 )); do
    case "$1" in
        --once) once=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; usage; exit 2 ;;
    esac
done

# lib/progress_table.sh is shared with the cluster watchers and documents the
# globals its callers must provide. The cluster half of that contract is unused
# here, but the file is read under `set -u`, so the names still have to exist.
JOB_ID_TAG=""
REMOTE_USER=""
REMOTE_PROJECT=""
remote=""
rsync_ssh=""
ssh_args=()
# shellcheck source=scripts/lib/progress_table.sh
source "${SCRIPT_DIR}/lib/progress_table.sh"

# print_local_progress builds a symlink view of run/ under /tmp keyed on this
# shell's pid (wait_progress_refresh_event_cache), reused across rounds; drop it
# on the way out rather than leaving one per watcher behind.
trap 'rm -rf "$(wait_progress_event_cache_path)"' EXIT

while true; do
    printf '\n===== %s =====\n' "$(date '+%F %T')"
    wait_progress_reset_cluster_stats
    SOURCE_IDLE["local"]=1
    poll_local || true
    if (( SOURCE_IDLE["local"] )); then
        printf 'No local jobs: nothing running and %s is empty.\n' \
            "${LOCAL_QUEUE_FILE#"${LOCAL_PROJECT}"/}"
    fi
    wait_progress_print_cluster_stats

    (( once )) && break
    sleep "${POLL_SECONDS}"
done
