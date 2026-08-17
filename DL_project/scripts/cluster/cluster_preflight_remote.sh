#!/usr/bin/env bash
# Read-only checks run on a cluster frontend before any job is submitted.
#
# Emits KEY=value lines on stdout for run_cluster.sh to parse; human-readable
# diagnostics go to stderr. Exits non-zero on a hard failure, so a missing conda
# environment or a torch build without the right SM target is reported once,
# instead of as 45 identical job failures.
#
# Submits nothing and writes nothing.
set -uo pipefail

CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
# Compute-capability the GPUs need: sm_90 covers H100 and H200, sm_80 the A100,
# sm_70 the V100. A torch build that works on Bigfoot may lack sm_90 entirely.
REQUIRED_ARCH="${REQUIRED_ARCH:-}"

failed=0
note() { printf '%s\n' "$*" >&2; }
fail() { printf 'ERROR: %s\n' "$*" >&2; failed=1; }

# --- 1. project layout (catches a truncated rsync) ------------------------
for required in training/new_train.py add_new_metrics_to_table.py data; do
    if [[ ! -e "${required}" ]]; then
        fail "missing from $(pwd): ${required}"
    fi
done

# --- 2. conda installation ------------------------------------------------
conda_sh=""
for candidate in \
    "${CONDA_SH:-}" \
    "${HOME}/miniconda3/etc/profile.d/conda.sh" \
    "${HOME}/mambaforge/etc/profile.d/conda.sh" \
    "${HOME}/miniforge3/etc/profile.d/conda.sh" \
    /home/kalinina/miniconda3/etc/profile.d/conda.sh
do
    if [[ -n "${candidate}" && -f "${candidate}" ]]; then
        conda_sh="${candidate}"
        break
    fi
done
if [[ -z "${conda_sh}" ]] && command -v conda >/dev/null 2>&1; then
    conda_base="$(conda info --base 2>/dev/null || true)"
    if [[ -n "${conda_base}" && -f "${conda_base}/etc/profile.d/conda.sh" ]]; then
        conda_sh="${conda_base}/etc/profile.d/conda.sh"
    fi
fi

if [[ -z "${conda_sh}" ]]; then
    fail "no conda installation found on $(hostname). Install miniconda into \$HOME, then create the ${CONDA_ENV} environment."
else
    printf 'CONDA_SH=%s\n' "${conda_sh}"

    # --- 3. the training environment --------------------------------------
    # shellcheck disable=SC1090
    source "${conda_sh}"
    if conda env list 2>/dev/null | awk '{print $1}' | grep -qx "${CONDA_ENV}"; then
        printf 'CONDA_ENV=%s\n' "${CONDA_ENV}"

        # --- 4. torch built for this cluster's GPUs -----------------------
        # torch.cuda.get_arch_list() returns [] on a GPU-less frontend even for
        # a perfectly good CUDA build, so it cannot be used as the gate here.
        # torch._C._cuda_getArchFlags() reports the compiled SM targets without
        # needing a device; fall back to get_arch_list() only if it is absent.
        torch_info="$(
            conda run -n "${CONDA_ENV}" python -c '
import torch
print("TORCH_VERSION=" + torch.__version__)
print("TORCH_CUDA=" + str(torch.version.cuda))
archs = []
try:
    flags = torch._C._cuda_getArchFlags()
    if flags:
        archs = flags.split()
except Exception:
    pass
if not archs:
    archs = list(torch.cuda.get_arch_list())
print("TORCH_ARCHS=" + ",".join(archs))
' 2>/dev/null
        )"
        if [[ -z "${torch_info}" ]]; then
            fail "could not import torch in ${CONDA_ENV}"
        else
            printf '%s\n' "${torch_info}"
            if [[ -n "${REQUIRED_ARCH}" ]]; then
                archs="$(printf '%s\n' "${torch_info}" | sed -n 's/^TORCH_ARCHS=//p')"
                # sm_90a counts as sm_90.
                if ! printf '%s' "${archs}" | grep -qE "(^|,)${REQUIRED_ARCH}a?(,|$)"; then
                    fail "torch in ${CONDA_ENV} is not built for ${REQUIRED_ARCH} (has: ${archs}). Every job would fail with 'no kernel image is available'. Reinstall torch with a CUDA build covering ${REQUIRED_ARCH}."
                fi
            fi
        fi
    else
        fail "conda environment '${CONDA_ENV}' does not exist on $(hostname)."
        note "Available environments:"
        conda env list 2>/dev/null | sed 's/^/  /' >&2
        note "Create it with: conda create -n ${CONDA_ENV} -c conda-forge python=3.11 ..."
    fi
fi

# --- 5. scheduler tooling -------------------------------------------------
for tool in oarsub oarstat; do
    command -v "${tool}" >/dev/null 2>&1 || fail "${tool} not found on $(hostname)"
done

# --- 6. GPU models the scheduler actually advertises (warning only) -------
if command -v oarnodes >/dev/null 2>&1; then
    # `oarnodes -Y` emits the property as a two-line YAML pair, value on the
    # NEXT line, e.g.
    #     - - gpumodel
    #       - H100
    # so match the key line and print the following one.
    gpumodels="$(
        oarnodes -Y 2>/dev/null |
            awk '/- gpumodel[[:space:]]*$/ { getline; gsub(/^[[:space:]]*-[[:space:]]*/, ""); gsub(/["'"'"']/, ""); if ($0 != "") print }' |
            sort -u | paste -sd, -
    )"
    if [[ -n "${gpumodels}" ]]; then
        printf 'GPUMODELS=%s\n' "${gpumodels}"
    else
        note "WARNING: could not read gpumodel values from oarnodes; set GPU_PROPERTY manually if submission is rejected."
    fi
fi

# --- 7. OAR project candidates -------------------------------------------
projects="$(id -Gn 2>/dev/null | tr ' ' '\n' | grep -E '^pr-' | sort -u | paste -sd, -)"
printf 'PROJECTS=%s\n' "${projects}"
if [[ -z "${projects}" ]]; then
    note "WARNING: no pr-* group found; --project will be omitted. If OAR rejects the job, pass PROJECT=<name> explicitly."
fi

# --- 8. free space on the project filesystem (warning only) --------------
avail="$(df -Ph . 2>/dev/null | awk 'NR==2 {print $4}')"
[[ -n "${avail}" ]] && printf 'DISK_AVAIL=%s\n' "${avail}"

exit "${failed}"
