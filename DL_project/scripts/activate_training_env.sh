#!/usr/bin/env bash

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
    return 1 2>/dev/null || exit 1
fi

conda activate Kalinin_project_LP
