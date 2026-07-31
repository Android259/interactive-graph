#!/usr/bin/env bash
# Print the number of trainable parameters of the model built from the config
# described by one arg_files/*.md file (the same flags test_run.sh feeds to
# training/new_train.py), without loading data or training.
#
# Usage: bash scripts/parameters.sh [ARGS_FILE]
#   ARGS_FILE   name or path of a file under scripts/arg_files (default: test)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

ARGS_FILE="${1:-test}"

if [[ -f "${ARGS_FILE}" ]]; then
    :
elif [[ -f "${SCRIPT_DIR}/arg_files/${ARGS_FILE}.md" ]]; then
    ARGS_FILE="${SCRIPT_DIR}/arg_files/${ARGS_FILE}.md"
elif [[ -f "${SCRIPT_DIR}/arg_files/${ARGS_FILE}" ]]; then
    ARGS_FILE="${SCRIPT_DIR}/arg_files/${ARGS_FILE}"
else
    printf 'Arguments file not found: %s\n' "${ARGS_FILE}" >&2
    exit 1
fi

label="$(basename "${ARGS_FILE}" .md)"

# Collect the --flag lines, stripping surrounding quotes from any =value so that
# e.g. --pool_type="gem" parses cleanly.
mapfile -t ARGS < <(grep '^--' "${ARGS_FILE}" | sed -E 's/^(--[^=]+=)"?([^"]*)"?$/\1\2/')

# Activate the conda training env when available; otherwise fall back to the
# python3 already on PATH so the script still works without conda.
if [[ "${CONDA_DEFAULT_ENV:-}" != "Kalinin_project_LP" ]]; then
    if ! source "${SCRIPT_DIR}/activate_training_env.sh"; then
        printf 'Using current python3: %s\n' "$(command -v python3 || echo 'not found')" >&2
    fi
fi

printf '=== %s ===\n' "${label}"
PYTHONUNBUFFERED=1 python3 - "${ARGS[@]}" <<'PY'
import os
import sys

TRAINING_DIR = os.path.join(os.getcwd(), "training")
sys.path.insert(0, TRAINING_DIR)
sys.path.insert(0, os.getcwd())

from read_configuration import read_configuration
from architecture.interaction_classification import InteractionClassification

# sys.argv[0] is the program name (skipped by the parser); the rest are the flags.
conf = read_configuration(sys.argv)
if conf.final_m is None:
    conf.final_m = conf.m

model = InteractionClassification(conf)
n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"number of parameters : {n_params}")
PY
