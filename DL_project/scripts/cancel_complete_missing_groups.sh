#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-bigfoot}"
REMOTE_USER="${REMOTE_USER:-kalinina}"
SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-/tmp/bigfoot-cancel-complete-${USER}-$$.sock}"

remote="${REMOTE_USER}@${REMOTE_HOST}"

close_ssh_master() {
    ssh -S "${SSH_CONTROL_PATH}" -O exit "${remote}" >/dev/null 2>&1 || true
}
trap close_ssh_master EXIT

printf 'Opening shared SSH connection to %s.\n' "${remote}"
ssh -M -S "${SSH_CONTROL_PATH}" -o ControlPersist=10m -fN "${remote}"

job_ids="$(
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "oarstat -u '${REMOTE_USER}' --sql \"job_name LIKE 'fill%'\"" |
        awk '$1 ~ /^[0-9]+$/ {print $1}'
)"

if [[ -z "${job_ids}" ]]; then
    printf 'No active complete_missing_groups jobs found.\n'
    exit 0
fi

printf 'Cancelling complete_missing_groups OAR job IDs:\n%s\n' "${job_ids}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" oardel ${job_ids}

printf 'Cancellation requested for %d job(s).\n' \
    "$(printf '%s\n' "${job_ids}" | awk 'NF {count++} END {print count + 0}')"
