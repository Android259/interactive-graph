#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REMOTE_HOST="${REMOTE_HOST:-bigfoot}"
REMOTE_USER="${REMOTE_USER:-kalinina}"
REMOTE_PROJECT="${REMOTE_PROJECT:-/home/kalinina/DL_project}"
LOCAL_PROJECT="${LOCAL_PROJECT:-${PROJECT_ROOT}}"
POLL_SECONDS="${POLL_SECONDS:-5}"
SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-/tmp/bigfoot-cancel-job-${USER}-$$.sock}"

if (( $# != 1 )) || [[ ! "$1" =~ ^[0-9]+$ ]]; then
    printf 'Usage: bash %s JOB_ID\n' "${0##*/}" >&2
    printf 'Example: bash %s 10757\n' "${0##*/}" >&2
    exit 2
fi

job_id="$1"
remote="${REMOTE_USER}@${REMOTE_HOST}"

close_ssh_master() {
    ssh -S "${SSH_CONTROL_PATH}" -O exit "${remote}" >/dev/null 2>&1 || true
}
trap close_ssh_master EXIT

printf 'Opening shared SSH connection to %s.\n' "${remote}"
ssh -M -S "${SSH_CONTROL_PATH}" -o ControlPersist=10m -fN "${remote}"

if ! ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "oarstat -u '${REMOTE_USER}' | awk '\$1 == \"${job_id}\" {found=1} END {exit !found}'"
then
    printf 'Active OAR job %s owned by %s was not found.\n' \
        "${job_id}" "${REMOTE_USER}" >&2
    exit 1
fi

printf 'Cancelling OAR job %s.\n' "${job_id}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" "oardel '${job_id}'"

while ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "oarstat -u '${REMOTE_USER}' | awk '\$1 == \"${job_id}\" {found=1} END {exit !found}'"
do
    printf 'Waiting for job %s to stop.\n' "${job_id}"
    sleep "${POLL_SECONDS}"
done

printf 'Synchronizing script logs.\n'
mkdir -p "${LOCAL_PROJECT}/script_logs"
rsync -a --quiet -e "ssh -S ${SSH_CONTROL_PATH}" \
    "${remote}:${REMOTE_PROJECT}/script_logs/" \
    "${LOCAL_PROJECT}/script_logs/"
find "${LOCAL_PROJECT}/script_logs" -type f -name '*.err' -empty -delete

printf 'Job %s cancelled; logs synchronized to %s/script_logs\n' \
    "${job_id}" "${LOCAL_PROJECT}"
