#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REMOTE_HOST="${REMOTE_HOST:-bigfoot}"
REMOTE_USER="${REMOTE_USER:-kalinina}"
REMOTE_PROJECT="${REMOTE_PROJECT:-/home/kalinina/DL_project}"
LOCAL_PROJECT="${LOCAL_PROJECT:-${PROJECT_ROOT}}"
POLL_SECONDS="${POLL_SECONDS:-5}"
SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-/tmp/bigfoot-cancel-${USER}-$$.sock}"

remote="${REMOTE_USER}@${REMOTE_HOST}"

close_ssh_master() {
    ssh -S "${SSH_CONTROL_PATH}" -O exit "${remote}" >/dev/null 2>&1 || true
}
trap close_ssh_master EXIT

printf 'Opening shared SSH connection to %s.\n' "${remote}"
ssh -M -S "${SSH_CONTROL_PATH}" -o ControlPersist=10m -fN "${remote}"

printf 'Deleting all OAR jobs owned by %s.\n' "${REMOTE_USER}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "job_ids=\$(oarstat -u '${REMOTE_USER}' | awk '\$1 ~ /^[0-9]+\$/ {print \$1}'); if [[ -n \"\${job_ids}\" ]]; then oardel \${job_ids}; else printf 'No OAR jobs found.\n'; fi"

while true; do
    active_jobs="$(
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
            "oarstat -u '${REMOTE_USER}' | awk '\$1 ~ /^[0-9]+\$/ {count++} END {print count + 0}'"
    )"
    if (( active_jobs == 0 )); then
        break
    fi
    printf 'Waiting for %d jobs to stop.\n' "${active_jobs}"
    sleep "${POLL_SECONDS}"
done

printf 'Synchronizing script logs.\n'
mkdir -p "${LOCAL_PROJECT}/script_logs"
rsync -a --quiet -e "ssh -S ${SSH_CONTROL_PATH}" \
    "${remote}:${REMOTE_PROJECT}/script_logs/" \
    "${LOCAL_PROJECT}/script_logs/"

printf 'All jobs deleted; logs synchronized to %s/script_logs\n' "${LOCAL_PROJECT}"
