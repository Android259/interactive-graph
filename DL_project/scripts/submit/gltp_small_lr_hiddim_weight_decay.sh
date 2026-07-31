#!/usr/bin/env bash
set -euo pipefail

PROJECT="${PROJECT:-pr-molgen}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
GPU_PROPERTY="${GPU_PROPERTY:-(gpumodel='A100' OR gpumodel='V100')}"
WALLTIME="${WALLTIME:-4:00:00}"
EP="${EP:-150}"
BATCH="${BATCH:-16}"
NUM_WORKERS="${NUM_WORKERS:-4}"
SEED="${SEED:-0}"
HEADS="${HEADS:-8}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
GPU_WAIT_SECONDS="${GPU_WAIT_SECONDS:-60}"
LOG_ROOT="${LOG_ROOT:-${PROJECT_DIR}/script_logs/gltp_small_lr_hiddim_weight_decay}"

LRS=(0.0001 0.00003)
HIDDIMS=(32 16)
WEIGHT_DECAYS=(0.0 0.00001 0.0001)

mkdir -p "${LOG_ROOT}"

submit_variant() {
    local lr="$1"
    local hiddim="$2"
    local weight_decay="$3"
    local lr_label="${lr//./p}"
    local wd_label="${weight_decay//./p}"
    local variant="lr${lr_label}_h${hiddim}_wd${wd_label}"
    local log_file="${LOG_ROOT}/${variant}_seed${SEED}_ep${EP}_batch${BATCH}.log"
    local job_name="gsmall_${variant}"
    local train_command
    local job_command

    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= %q )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=%%s MiB. Checking again in %%s seconds.\n" "${free_gpu_mib:-unknown}" %q %q; sleep %q; done; printf "=== GLTP SMALL-PARAMETER SWEEP | lr: %%s | hiddim: %%s | weight_decay: %%s | seed: %%s | GPU: %%s ===\n" %q %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon  --no_tanimoto_weight --protein_pooling=attention_pos_bias --loss_type=cross_entropy --pool_type=max --HEADS=%q --hiddim=%q --m=4 --lr=%q --weight_decay=%q --batch=%q --ep=%q --num_workers=%q --seed=%q --protein_self_attention --lipid_self_attention --cross_attention --excluded_groups=GLTP 2>&1 | tee %q' \
        "${MIN_FREE_GPU_MIB}" "${MIN_FREE_GPU_MIB}" \
        "${GPU_WAIT_SECONDS}" "${GPU_WAIT_SECONDS}" \
        "${lr}" "${hiddim}" "${weight_decay}" "${SEED}" \
        "${HEADS}" "${hiddim}" "${lr}" "${weight_decay}" "${BATCH}" \
        "${EP}" "${NUM_WORKERS}" "${SEED}" "${log_file}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && bash -o pipefail -c %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" "${train_command}"

    oarsub \
        --name "${job_name}" \
        -l "/nodes=1/gpu=1,walltime=${WALLTIME}" \
        -p "${GPU_PROPERTY}" \
        --project "${PROJECT}" \
        -O "${LOG_ROOT}/${variant}_%jobid%.out" \
        -E "${LOG_ROOT}/${variant}_%jobid%.err" \
        "${job_command}"
}

for lr in "${LRS[@]}"; do
    for hiddim in "${HIDDIMS[@]}"; do
        for weight_decay in "${WEIGHT_DECAYS[@]}"; do
            submit_variant "${lr}" "${hiddim}" "${weight_decay}"
        done
    done
done
