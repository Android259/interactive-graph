#!/usr/bin/env bash
# Run training/new_train.py locally with the flags from one arg_files/*.md file.
#
# Usage: bash scripts/test_run.sh [ARGS_FILE] [GROUP] [SEED]
#   ARGS_FILE   name or path of a file under scripts/arg_files (default: test)
#   GROUP       defaults to START
#   SEED        defaults to 0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

ARGS_FILE="${1:-test}"
GROUP="${2:-START}"
SEED="${3:-0}"

# shellcheck source=scripts/lib/args_file_lib.sh
source "${SCRIPT_DIR}/../lib/args_file_lib.sh"

if ! ARGS_FILE="$(resolve_args_file "${ARGS_FILE}")"; then
    printf 'Arguments file not found: %s\n' "${ARGS_FILE}" >&2
    exit 1
fi

label="$(basename "${ARGS_FILE}" .md)"
args_template="$(args_file_flags "${ARGS_FILE}")"

log_dir="script_logs/${label}"
mkdir -p "${log_dir}"
log_file="${log_dir}/${label}_seed${SEED}_${GROUP}.log"

printf '=== %s | group=%s | seed=%s ===\n' "${label}" "${GROUP}" "${SEED}"
# shellcheck disable=SC2086
PYTHONUNBUFFERED=1 python3 ./training/new_train.py \
    ${args_template} \
    --seed="${SEED}" \
    --excluded_groups="${GROUP}" \
    --label="${label}" \
    2>&1 | tee "${log_file}"

printf '\nDone. Log at %s\n' "${log_file}"
