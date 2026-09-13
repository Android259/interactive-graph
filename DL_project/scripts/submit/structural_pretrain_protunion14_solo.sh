#!/usr/bin/env bash
set -euo pipefail

# One-off submitter for JUST stage 1 of a structural-pretrain checkpoint whose
# protein1 encoder includes --protein_descriptors= -- the GPU-wait/lock/oarsub
# machinery here is scripts/submit/structural_pretrain_solo.sh's own stage-1
# section, lifted out and pointed at a different STAGE1_ARGS_FILE, with the
# stage-2 chaining removed: stage 2 for a --protein_descriptors= arm goes through
# the ordinary --family_only grid axis (scripts/launch/submit_grid.sh, added this
# session) instead, once this stage-1 checkpoint exists.
#
# Why this needs its own stage-1 run at all: --structural_pretrain is a single,
# whole-table run (no --excluded_groups/--family_only), which the standard grid
# launcher does not know how to submit without incorrectly slicing it into 9
# per-family jobs and injecting --excluded_groups into each -- exactly what
# structural_pretrain_solo.sh's stage 1 already avoids by building one oarsub
# command directly instead of going through submit_grid.sh. This script does
# the same, for a second stage-1 config.
#
# Why a second stage-1 checkpoint, not the existing one: models/structural_
# pretrain/random/seed0.pt was trained with no --protein_descriptors= at all, so
# a stage-2 run that adds any (e.g. protunion14) cannot load it -- PyTorch refuses
# with a size mismatch on protein1's first-layer projections (confirmed by
# running it). --protein_descriptors= has to be present at STAGE 1 too, so the
# checkpoint's input shape already matches what stage 2 will build.
#
# Launch (from the project root):
#   bash scripts/submit/structural_pretrain_protunion14_solo.sh
# Then, once this drains, launch stage 2 normally:
#   SKIP_AUC=1 bash scripts/run_bigfoot.sh --summarize --no_groups=ML,OSBP \
#       structural_pretrain_family_unfrozen_protunion14

PROJECT="${PROJECT:-pr-molgen}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
GPU_PROPERTY="${GPU_PROPERTY:-(gpumodel='A100' OR gpumodel='V100')}"
WALLTIME="${WALLTIME:-8:00:00}"
BATCH="${BATCH:-16}"
NUM_WORKERS="${NUM_WORKERS:-4}"
SEED="${SEED:-0}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
GPU_WAIT_SECONDS="${GPU_WAIT_SECONDS:-60}"
LOG_ROOT="${LOG_ROOT:-${PROJECT_DIR}/script_logs/structural_pretrain_protunion14}"
STAGE1_ARGS_FILE="${STAGE1_ARGS_FILE:-${PROJECT_DIR}/scripts/arg_files/structural_pretrain_protunion14.md}"

# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_DIR}/scripts/lib/args_file_lib.sh"
stage1_args="$(args_file_flags "${STAGE1_ARGS_FILE}")"

mkdir -p "${LOG_ROOT}"
log1="${LOG_ROOT}/structural_pretrain_protunion14_seed${SEED}_batch${BATCH}.log"

train_command=""
printf -v train_command \
    'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= %q )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=%%s MiB. Checking again in %%s seconds.\n" "${free_gpu_mib:-unknown}" %q %q; sleep %q; done; printf "=== STAGE 1 (protunion14): STRUCTURAL PRETRAIN | seed: %%s | GPU: %%s | batch: %%s ===\n" %q "${gpu_name}" %q; PYTHONUNBUFFERED=1 python ./training/new_train.py %s --batch=%q --num_workers=%q --seed=%q 2>&1 | tee %q' \
    "${MIN_FREE_GPU_MIB}" "${MIN_FREE_GPU_MIB}" \
    "${GPU_WAIT_SECONDS}" "${GPU_WAIT_SECONDS}" \
    "${SEED}" "${BATCH}" \
    "${stage1_args}" "${BATCH}" "${NUM_WORKERS}" "${SEED}" "${log1}"

job_command=""
printf -v job_command \
    'cd %q && source %q && conda activate %q && bash -o pipefail -c %q' \
    "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" "${train_command}"

oarsub \
    --name "structural_pretrain_protunion14" \
    -l "/nodes=1/gpu=1,walltime=${WALLTIME}" \
    -p "${GPU_PROPERTY}" \
    --project "${PROJECT}" \
    -O "${LOG_ROOT}/structural_pretrain_protunion14_%jobid%.out" \
    -E "${LOG_ROOT}/structural_pretrain_protunion14_%jobid%.err" \
    "${job_command}"
