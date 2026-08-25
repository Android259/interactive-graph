#!/usr/bin/env bash
# Runs ONE experiment inside one OAR job -- the historical one-experiment-per-job
# path, as a real file.
#
# Invoked on the compute node as the job command:
#   bash scripts/launch/run_one_experiment.sh <base64-record>
# where the record is built by scripts/lib/pack_lib.sh (pack_record) and carries
#   header <TAB> log_file <TAB> out_base <TAB> python_args
# out_base is unused here: an unpacked job's own OAR output already IS the
# "..._<tag><job id>.out" file the progress table looks for, so nothing has to
# write a second one. It is in the record so that one record format describes an
# experiment whether it is run alone or inside a pack.
#
# A file rather than a string spliced into the oarsub command line: the project
# is rsynced to the cluster anyway, so there is nothing to splice it for, and a
# file can be read and tested.
#
# Same admission rules as scripts/launch/run_experiment_pack.sh, which is the
# same steps for several experiments at once: refuse a GPU model this
# configuration was not built for, take the card's lock, and wait for the memory
# a training needs before starting one.
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_DIR}"

GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
GPU_WAIT_SECONDS="${GPU_WAIT_SECONDS:-60}"
# 1 on a CPU-only cluster (kraken-cpu, scripts/lib/cluster_common.sh): no
# nvidia-smi, so no GPU model check, lock or memory wait below -- the whole
# node allocation belongs to this one un-packed run, nothing to admit it past.
CPU_ONLY="${CPU_ONLY:-0}"

if (( $# != 1 )); then
    printf 'Usage: %s <base64-experiment-record>\n' "${0##*/}" >&2
    exit 2
fi

record="$(printf '%s' "$1" | base64 -d)" || {
    printf 'Could not decode the experiment record.\n' >&2
    exit 2
}
IFS=$'\t' read -r header log_file _out_base python_args <<< "${record}"

if (( ! CPU_ONLY )); then
    # --- GPU admission ---------------------------------------------------------
    gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"

    # The alternation in GPU_MODEL_GLOB ("*A100*|*V100*") has to be split by hand:
    # it arrives in a variable, where `|` is an ordinary character, so matching
    # the whole string as one pattern would reject every real GPU.
    gpu_supported=0
    IFS='|' read -r -a gpu_globs <<< "${GPU_MODEL_GLOB}"
    for gpu_glob in "${gpu_globs[@]}"; do
        # Unquoted on purpose: one alternative, still a pattern.
        # shellcheck disable=SC2254
        case "${gpu_name}" in
            ${gpu_glob}) gpu_supported=1; break ;;
        esac
    done
    if (( gpu_supported == 0 )); then
        printf 'Unsupported GPU model: %s\n' "${gpu_name}" >&2
        exit 1
    fi

    # --- one training at a time on this card -----------------------------------
    # Slot 0's lock path is the one a packed job also takes for its first slot,
    # so a packed job and an unpacked one exclude each other instead of quietly
    # sharing the card.
    gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd 'A-Za-z0-9_-')"
    exec 9>"/tmp/dl-project-${gpu_uuid}.lock"
    printf 'Waiting for exclusive access to GPU %s.\n' "${gpu_uuid}"
    flock 9

    while true; do
        free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
        if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= MIN_FREE_GPU_MIB )); then
            break
        fi
        printf 'Waiting for GPU memory: free=%s MiB, required=%s MiB. Checking again in %s seconds.\n' \
            "${free_gpu_mib:-unknown}" "${MIN_FREE_GPU_MIB}" "${GPU_WAIT_SECONDS}"
        sleep "${GPU_WAIT_SECONDS}"
    done
fi

# --- run ---------------------------------------------------------------------
if (( CPU_ONLY )); then
    printf '=== %s | CPU-only (%s cores) ===\n' "${header}" "$(nproc)"
else
    printf '=== %s | GPU: %s ===\n' "${header}" "${gpu_name}"
fi

mkdir -p "$(dirname "${log_file}")"
# `eval set --`, not bare ${python_args}: a flag like --pool_type="gem" needs one
# round of shell interpretation, exactly as the spliced-string version got from
# the `bash -c` it was run through.
eval "set -- ${python_args}"
PYTHONUNBUFFERED=1 python ./training/new_train.py "$@" 2>&1 | tee "${log_file}"
exit "${PIPESTATUS[0]}"
