#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-bigfoot}"
REMOTE_USER="${REMOTE_USER:-kalinina}"
SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-/tmp/bigfoot-cancel-prefix-${USER}-$$.sock}"

if (( $# == 0 )); then
    printf 'Usage: bash %s JOB_NAME_PREFIX [JOB_NAME_PREFIX ...]\n' "${0##*/}" >&2
    printf 'Example: bash %s ca_nt gdiag_\n' "${0##*/}" >&2
    exit 2
fi

prefixes=("$@")
for prefix in "${prefixes[@]}"; do
    if [[ ! "${prefix}" =~ ^[A-Za-z0-9_-]+$ ]]; then
        printf 'Invalid job name prefix: %s\n' "${prefix}" >&2
        exit 2
    fi
done

remote="${REMOTE_USER}@${REMOTE_HOST}"

close_ssh_master() {
    ssh -S "${SSH_CONTROL_PATH}" -O exit "${remote}" >/dev/null 2>&1 || true
}
trap close_ssh_master EXIT

printf 'Opening shared SSH connection to %s.\n' "${remote}"
ssh -M -S "${SSH_CONTROL_PATH}" -o ControlPersist=10m -fN "${remote}"

job_ids="$(
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" "oarstat -u '${REMOTE_USER}'" |
        awk '$1 ~ /^[0-9]+$/ {print $1}'
)"

matching_jobs=
discovered_jobs=
while IFS= read -r job_id; do
    [[ -n "${job_id}" ]] || continue
    job_details="$(
        ssh -n -S "${SSH_CONTROL_PATH}" "${remote}" \
            "oarstat -f -j '${job_id}'"
    )"
    job_name="$(
        printf '%s\n' "${job_details}" |
            awk -F ' = ' 'tolower($1) ~ /(^|[[:space:]])(job_)?name$/ {print $2; exit}'
    )"
    discovered_jobs+="${job_id} ${job_name:-<name unavailable>}"$'\n'
    for prefix in "${prefixes[@]}"; do
        if grep -Fq "${prefix}" <<< "${job_details}"; then
            matching_jobs+="${job_id}"$'\n'
            break
        fi
    done
done <<< "${job_ids}"
matching_jobs="${matching_jobs%$'\n'}"
discovered_jobs="${discovered_jobs%$'\n'}"

if [[ -z "${matching_jobs}" ]]; then
    printf 'No active OAR jobs found with name prefixes: %s\n' "${prefixes[*]}"
    if [[ -n "${discovered_jobs}" ]]; then
        printf 'Current OAR jobs:\n%s\n' "${discovered_jobs}"
    else
        printf 'There are no active OAR jobs owned by %s.\n' "${REMOTE_USER}"
    fi
    exit 0
fi

printf 'Cancelling OAR job IDs:\n%s\n' "${matching_jobs}"

ssh -S "${SSH_CONTROL_PATH}" "${remote}" oardel ${matching_jobs}
printf 'Cancellation requested for %d job(s).\n' \
    "$(printf '%s\n' "${matching_jobs}" | awk 'NF {count++} END {print count + 0}')"
