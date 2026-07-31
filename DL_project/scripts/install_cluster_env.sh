#!/usr/bin/env bash
# Reproduce Bigfoot's Kalinin_project_LP environment on a cluster that has no
# conda. The spec is scripts/cluster_env.yml (see scripts/AGENTS.md for the
# three corrections it carries over a raw `conda env export`). Installed into the same path Bigfoot uses, so the default CONDA_SH in
# scripts/cluster_common.sh resolves without an override.
#
# Idempotent: skips the installer if conda is already there, and skips env
# creation if the environment already exists.
set -euo pipefail

CONDA_ROOT="${CONDA_ROOT:-${HOME}/miniconda3}"
ENV_NAME="${ENV_NAME:-Kalinin_project_LP}"
ENV_YML="${ENV_YML:-${HOME}/DL_project/scripts/cluster_env.yml}"
INSTALLER_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"

printf '=== target: %s (env %s) ===\n' "${CONDA_ROOT}" "${ENV_NAME}"

if [[ ! -f "${CONDA_ROOT}/etc/profile.d/conda.sh" ]]; then
    printf 'Downloading Miniforge installer...\n'
    installer="$(mktemp /tmp/miniforge.XXXXXX.sh)"
    curl -fsSL "${INSTALLER_URL}" -o "${installer}"
    printf 'Installing to %s ...\n' "${CONDA_ROOT}"
    bash "${installer}" -b -p "${CONDA_ROOT}"
    rm -f "${installer}"
else
    printf 'conda already present, skipping installer.\n'
fi

# shellcheck disable=SC1091
source "${CONDA_ROOT}/etc/profile.d/conda.sh"
conda --version

if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
    printf 'Environment %s already exists; updating from spec.\n' "${ENV_NAME}"
    conda env update -n "${ENV_NAME}" -f "${ENV_YML}" --prune
else
    printf 'Creating %s from %s ...\n' "${ENV_NAME}" "${ENV_YML}"
    conda env create -n "${ENV_NAME}" -f "${ENV_YML}"
fi

printf '=== verifying ===\n'
conda run -n "${ENV_NAME}" python - <<'PY'
import torch
print("torch  :", torch.__version__)
print("cuda   :", torch.version.cuda)
try:
    print("archs  :", torch._C._cuda_getArchFlags())
except Exception as exc:
    print("archs  : unavailable ->", type(exc).__name__)
import torch_geometric, torch_scatter, torch_sparse, rdkit, pandas, numpy
print("pyg    :", torch_geometric.__version__)
print("rdkit  :", rdkit.__version__)
print("pandas :", pandas.__version__)
print("numpy  :", numpy.__version__)
PY

printf '=== done ===\n'
