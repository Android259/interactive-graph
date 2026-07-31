#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf 'Use: source scripts/enter_project_env.sh\n' >&2
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_CONDA_ENV="${PROJECT_CONDA_ENV:-Kalinin_project_LP}"

if [[ -f /home/kalinina/miniconda3/etc/profile.d/conda.sh ]]; then
    source /home/kalinina/miniconda3/etc/profile.d/conda.sh
elif [[ -f "${HOME}/miniconda3/etc/profile.d/conda.sh" ]]; then
    source "${HOME}/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "${HOME}/mambaforge/etc/profile.d/conda.sh" ]]; then
    source "${HOME}/mambaforge/etc/profile.d/conda.sh"
elif command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook)"
else
    printf 'conda is not available in this environment.\n' >&2
    return 1
fi

if ! conda env list | awk '{print $1}' | grep -qx "${PROJECT_CONDA_ENV}"; then
    conda create -y -n "${PROJECT_CONDA_ENV}" -c conda-forge python=3.11 pandas rdkit rsync || return 1
fi

conda activate "${PROJECT_CONDA_ENV}" || return 1

export PROJECT_ROOT
export PYTHONPATH="${PROJECT_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${PROJECT_ROOT}" || return 1

python3 - <<'PY'
import sys

print(f"python: {sys.executable}")

try:
    import rdkit
except ModuleNotFoundError:
    print("rdkit: not installed")
else:
    print(f"rdkit: {rdkit.__version__}")
PY
