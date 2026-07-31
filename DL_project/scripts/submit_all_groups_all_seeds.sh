#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Cluster-dependent settings. Every default reproduces the Bigfoot values this
# script used to hardcode, so an unset environment behaves exactly as before;
# scripts/run_cluster.sh overrides them per cluster (Kraken needs H100/H200).
# Never patch this file's text to retarget a cluster -- set these instead.
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
# `-` rather than `:-`: an explicitly empty PROJECT/GPU_PROPERTY must stay empty
# so the corresponding oarsub flag is omitted (a cluster may not require a
# project, or may need no gpumodel filter at all). Only an *unset* variable
# takes the Bigfoot default.
PROJECT="${PROJECT-pr-molgen}"
GPU_PROPERTY="${GPU_PROPERTY-(gpumodel='A100' OR gpumodel='V100')}"
# Shell `case` pattern matched against `nvidia-smi --query-gpu=name` inside the
# job. It is spliced into a string the compute node runs via `bash -c`, hence
# the character whitelist below.
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
GPU_RESOURCES="${GPU_RESOURCES:-/nodes=1/gpu=1}"
WALLTIME="${WALLTIME:-5:00:00}"
FAST_ATTENTION_WALLTIME="${FAST_ATTENTION_WALLTIME:-0:20:00}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
# Distinguishes OAR output filenames between clusters, whose job-ID spaces
# overlap (wait_and_sync locates a running job's log by `*_${job_id}.out`).
JOB_ID_TAG="${JOB_ID_TAG:-}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
# Space-separated subsets, for a one-job smoke test instead of the full 45.
# Not named GROUPS/SEEDS: those are the local arrays below.
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"

# --- Packing -----------------------------------------------------------------
# PACK_SIZE experiments share one OAR job; PACK_PARALLEL of them may run at once
# on the single allocated GPU (the effective number is decided inside the job
# from the card actually handed out -- see scripts/run_experiment_pack.sh).
# PACK_SIZE=1 leaves the historical one-experiment-per-job path untouched.
PACK_SIZE="${PACK_SIZE:-1}"
PACK_PARALLEL="${PACK_PARALLEL:-1}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-5}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-0}"
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"
# Concurrency ASSUMED when sizing the walltime request. Must describe the
# weakest card GPU_PROPERTY admits, because the request is fixed at submit time
# while the real concurrency is not.
PACK_WALLTIME_PARALLEL="${PACK_WALLTIME_PARALLEL:-1}"
# Documented scheduler cap; empty = unknown, do not check.
MAX_WALLTIME="${MAX_WALLTIME:-}"

for _pack_int in PACK_SIZE PACK_PARALLEL GPU_MIB_PER_RUN PACK_GPU_PERCENT \
    PACK_CPU_PER_RUN PACK_MIN_FREE_GPU_MIB PACK_HARDWARE_AUTO \
    PACK_WALLTIME_PARALLEL; do
    if [[ ! "${!_pack_int}" =~ ^[0-9]+$ ]]; then
        printf "%s must be an integer: %s\n" "${_pack_int}" "${!_pack_int}" >&2
        exit 2
    fi
done
if (( PACK_HARDWARE_AUTO != 0 && PACK_HARDWARE_AUTO != 1 )); then
    printf "PACK_HARDWARE_AUTO must be 0 or 1: %s\n" \
        "${PACK_HARDWARE_AUTO}" >&2
    exit 2
fi

# shellcheck source=scripts/pack_lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/pack_lib.sh"

if [[ ! "${MIN_FREE_GPU_MIB}" =~ ^[0-9]+$ ]]; then
    printf "MIN_FREE_GPU_MIB must be an integer: %s\n" "${MIN_FREE_GPU_MIB}" >&2
    exit 2
fi
if [[ ! "${GPU_MODEL_GLOB}" =~ ^[A-Za-z0-9_*?.|@%^:+-]+$ ]]; then
    printf "GPU_MODEL_GLOB contains unsafe characters: %s\n" "${GPU_MODEL_GLOB}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"

if [[ $# -ne 1 ]]; then
    printf "Usage: %s arguments_file.md\n" "$0" >&2
    exit 1
fi

args_file="$1"

if [[ ! -f "${args_file}" ]]; then
    printf "Arguments file not found: %s\n" "${args_file}" >&2
    exit 1
fi

# Use the shorter request only for configurations that explicitly enable the
# fast path. This value feeds both unpacked jobs and pack walltime arithmetic.
if grep -qE '^--fast_attention([[:space:]=]|$)' "${args_file}"; then
    WALLTIME="${FAST_ATTENTION_WALLTIME}"
    printf "Detected --fast_attention; per-experiment walltime=%s.\n" "${WALLTIME}"
fi

# A `--cold_split` flag in the arguments file selects the cold-split series
# (separate held-out validation and test groups per fold). Delegate to the
# dedicated submitter so the flag is the single switch, whether this script is
# invoked directly or through run_bigfoot.sh's queue capture (the exported
# oarsub override survives exec via the process environment).
if grep -qE '^--cold_split([[:space:]=]|$)' "${args_file}"; then
    printf "Detected --cold_split; delegating to submit_cold_val_test_all_seeds.sh.\n"
    exec bash "${PROJECT_DIR}/scripts/submit_cold_val_test_all_seeds.sh" "${args_file}"
fi

variant="$(basename "${args_file}" .md)"

mkdir -p "script_logs/${variant}_seeds01234"

args_template="$(grep '^--' "${args_file}" | tr '\n' ' ')"

declare -A completed_pairs=()
if [[ "${COMPLETE_ONLY}" == "1" ]]; then
    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && completed_pairs["${pair}"]=1
    done <<< "${COMPLETED_EXPERIMENTS}"
    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && completed_pairs["${pair}"]=1
    done < <(python3 scripts/list_completed_experiments.py "${variant}")
fi

is_completed() {
    [[ "${COMPLETE_ONLY}" == "1" && -n "${completed_pairs["$1:$2"]:-}" ]]
}

submit_variant() {
    local group="$1"
    local seed="$2"
    local output_dir="script_logs/${variant}_seeds01234/${group}"
    local log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    # GPU_MODEL_GLOB is spliced with %s, never %q: printf '%q' '*A100*|*V100*'
    # yields an escaped literal that `case` would only match verbatim, so the
    # guard would reject every real GPU. MIN_FREE_GPU_MIB is spliced twice with
    # %q (arithmetic test and message text); it is validated as digits-only
    # above, so %q emits it unchanged and the generated command stays
    # byte-identical to the previously hardcoded one.
    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in %s) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= %q )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=%q MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== GROUP: %%s | VARIANT: %s | SEED: %%s | GPU: %%s ===\n" %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --label=%q %s --seed=%q --excluded_groups=%q 2>&1 | tee %q' \
        "${GPU_MODEL_GLOB}" \
        "${MIN_FREE_GPU_MIB}" \
        "${MIN_FREE_GPU_MIB}" \
        "${variant}" \
        "${group}" "${seed}" \
        "${variant}" "${args_template}" "${seed}" "${group}" "${log_file}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && bash -o pipefail -c %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" "${train_command}"

    # Built as an array so an empty GPU_PROPERTY/PROJECT omits the flag entirely
    # (a cluster may not require --project). Plain `[[ -n x ]] && arr+=(...)` is
    # avoided: a false test as the last command would return 1 and `set -e`
    # would abort the whole submitter.
    local -a oarsub_args=(
        --name "${variant}_${group}_s${seed}"
        -l "${GPU_RESOURCES},walltime=${WALLTIME}"
    )
    if [[ -n "${GPU_PROPERTY}" ]]; then
        oarsub_args+=(-p "${GPU_PROPERTY}")
    fi
    if [[ -n "${PROJECT}" ]]; then
        oarsub_args+=(--project "${PROJECT}")
    fi
    if [[ -n "${OARSUB_EXTRA}" ]]; then
        local -a extra_args
        read -r -a extra_args <<< "${OARSUB_EXTRA}"
        oarsub_args+=("${extra_args[@]}")
    fi
    oarsub_args+=(
        -O "${output_dir}/${variant}_seed${seed}_${JOB_ID_TAG}%jobid%.out"
        -E "${output_dir}/${variant}_seed${seed}_${JOB_ID_TAG}%jobid%.err"
        "${job_command}"
    )

    oarsub "${oarsub_args[@]}"
}

# --- Pack path ---------------------------------------------------------------
# One record per experiment, in the layout scripts/pack_lib.sh documents. The
# log path and the python arguments are exactly the ones submit_variant would
# have produced, so a packed run and an unpacked run write the same tree.
experiment_record() {
    local group="$1" seed="$2"
    local output_dir="script_logs/${variant}_seeds01234/${group}"

    mkdir -p "${output_dir}"

    pack_record \
        "GROUP: ${group} | VARIANT: ${variant} | SEED: ${seed}" \
        "${output_dir}/${variant}_seed${seed}_ep150_batch16.log" \
        "${output_dir}/${variant}_seed${seed}_" \
        "--label=${variant} ${args_template} --seed=${seed} --excluded_groups=${group}"
}

submit_pack() {
    local pack_index="$1"
    local spec="$2"
    local pack_count="$3"
    local job_walltime pack_dir job_command runner_env

    job_walltime="$(pack_job_walltime "${pack_count}" "${WALLTIME}" "${PACK_WALLTIME_PARALLEL}")"
    pack_check_walltime "${job_walltime}" "${MAX_WALLTIME}" || exit 2

    # The job's own stdout/stderr must NOT land on a "*_<tag><jobid>.out" path:
    # that pattern belongs to the per-experiment files the runner writes, and
    # wait_progress_table.sh turns every match into a row.
    pack_dir="script_logs/${variant}_seeds01234/_packs"
    mkdir -p "${pack_dir}"

    printf -v runner_env \
        'GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q JOB_ID_TAG=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q' \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "${JOB_ID_TAG}" \
        "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" "${PACK_GPU_PERCENT}" \
        "${PACK_CPU_PER_RUN}" "${PACK_MIN_FREE_GPU_MIB}" \
        "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && %s bash scripts/run_experiment_pack.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${runner_env}" "$(pack_spec_encode "${spec}")"

    local -a oarsub_args=(
        --name "${variant}_pack${pack_index}"
        -l "${GPU_RESOURCES},walltime=${job_walltime}"
    )
    if [[ -n "${GPU_PROPERTY}" ]]; then
        oarsub_args+=(-p "${GPU_PROPERTY}")
    fi
    if [[ -n "${PROJECT}" ]]; then
        oarsub_args+=(--project "${PROJECT}")
    fi
    if [[ -n "${OARSUB_EXTRA}" ]]; then
        local -a extra_args
        read -r -a extra_args <<< "${OARSUB_EXTRA}"
        oarsub_args+=("${extra_args[@]}")
    fi
    oarsub_args+=(
        -O "${pack_dir}/${variant}_pack${pack_index}_${JOB_ID_TAG}%jobid%.pack.out"
        -E "${pack_dir}/${variant}_pack${pack_index}_${JOB_ID_TAG}%jobid%.pack.err"
        "${job_command}"
    )

    printf "Pack %d: %d experiment(s), walltime=%s.\n" \
        "${pack_index}" "${pack_count}" "${job_walltime}"
    oarsub "${oarsub_args[@]}"
}

groups=(
    "CRAL-TRIO"
    "START"
    "lipocalin"
    "GLTP"
    "IP_trans"
    "LBP_BPI_CETP"
    "scp2"
    "ML"
    "OSBP"
)

seeds=(0 1 2 3 4)

if [[ -n "${GROUPS_OVERRIDE}" ]]; then
    read -r -a groups <<< "${GROUPS_OVERRIDE}"
fi
if [[ -n "${SEEDS_OVERRIDE}" ]]; then
    read -r -a seeds <<< "${SEEDS_OVERRIDE}"
fi

submitted=0

if (( PACK_SIZE <= 1 )); then
    for group in "${groups[@]}"; do
        for seed in "${seeds[@]}"; do
            if is_completed "${group}" "${seed}"; then
                printf "Skipping completed experiment: group=%s seed=%s.\n" "${group}" "${seed}"
                continue
            fi
            submit_variant "${group}" "${seed}"
            submitted=$((submitted + 1))
        done
    done

    printf "Submitted %d jobs %s across %d groups and %d seeds.\n" \
        "${submitted}" "${variant}" "${#groups[@]}" "${#seeds[@]}"
    exit 0
fi

# Packed: the seed loop stays innermost, so a pack of 5 is exactly one group's
# seeds and a pack of 9 spans groups at a fixed seed -- both natural units to
# resubmit or cancel as a whole.
experiments=0
pack_index=0
pack_count=0
pack_spec=""

flush_pack() {
    (( pack_count > 0 )) || return 0
    submit_pack "${pack_index}" "${pack_spec}" "${pack_count}"
    pack_index=$((pack_index + 1))
    submitted=$((submitted + 1))
    pack_count=0
    pack_spec=""
}

for group in "${groups[@]}"; do
    for seed in "${seeds[@]}"; do
        if is_completed "${group}" "${seed}"; then
            printf "Skipping completed experiment: group=%s seed=%s.\n" "${group}" "${seed}"
            continue
        fi
        pack_spec+="$(experiment_record "${group}" "${seed}")"$'\n'
        pack_count=$((pack_count + 1))
        experiments=$((experiments + 1))
        if (( pack_count >= PACK_SIZE )); then
            flush_pack
        fi
    done
done
flush_pack

printf "Submitted %d packed job(s) %s: %d experiments (%d groups x %d seeds), up to %d per job, up to %d concurrent per GPU.\n" \
    "${submitted}" "${variant}" "${experiments}" "${#groups[@]}" "${#seeds[@]}" \
    "${PACK_SIZE}" "${PACK_PARALLEL}"
