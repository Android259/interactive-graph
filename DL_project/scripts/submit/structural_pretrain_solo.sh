#!/usr/bin/env bash
set -euo pipefail

# One-off submitter for stages 1+2 of files/ plan "Структурное предобучение
# перед per-family дообучением", chained in ONE OAR job so stage 2 cannot start
# before stage 1 actually finishes: OAR job-id dependencies (-a <id>) don't work
# here because submission goes through scripts/cluster/cluster_queue_remote.sh's
# capture/drain split -- there is no real job id yet at capture time, only a
# queued command line a later cron drain turns into an actual oarsub call. The
# only ordering guarantee available is shell sequencing inside one job script.
#
# Stage 2 is --family_only (new_train.py/Dataloader.py): one model per family,
# trained AND validated only on its own rows -- the DeepCLIP/BERT-RBP "one
# model per protein/family" regime, not cross-family generalization. Runs for
# ALL 9 families, sequentially, all gated on stage 1 succeeding (the `&&` before
# the `{ ...; }` group) but independent of each other after that (`;` between
# families, so one family's failure doesn't skip the rest).
#
# Flags for both stages come from their own scripts/arg_files/*.md (via
# args_file_flags) so there is one place to tune them, matching the comment in
# structural_pretrain.md about encoder flags needing to match. --double_
# coldsplit is stripped from bbp_dcs's flags below since it tests the opposite
# thing (generalization to a held-out family) -- the .md file itself is
# untouched, still valid for a real cross-family grid run separately.
#
# Launch (bare stem -- see run_cluster.sh's resolve_args_file):
#   bash scripts/run_bigfoot.sh structural_pretrain_solo

PROJECT="${PROJECT:-pr-molgen}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
GPU_PROPERTY="${GPU_PROPERTY:-(gpumodel='A100' OR gpumodel='V100')}"
WALLTIME="${WALLTIME:-3:00:00}"
BATCH="${BATCH:-16}"
NUM_WORKERS="${NUM_WORKERS:-4}"
SEED="${SEED:-0}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
GPU_WAIT_SECONDS="${GPU_WAIT_SECONDS:-60}"
LOG_ROOT="${LOG_ROOT:-${PROJECT_DIR}/script_logs/structural_pretrain}"
STAGE1_ARGS_FILE="${PROJECT_DIR}/scripts/arg_files/structural_pretrain.md"
STAGE2_ARGS_FILE="${PROJECT_DIR}/scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md"
# scripts/settings.sh's PROTEIN_GROUPS, all 9 families.
PROTEIN_GROUPS=(
    "CRAL-TRIO" "START" "lipocalin" "GLTP" "IP_trans"
    "LBP_BPI_CETP" "scp2" "ML" "OSBP"
)

# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_DIR}/scripts/lib/args_file_lib.sh"
stage1_args="$(args_file_flags "${STAGE1_ARGS_FILE}")"
stage2_args="$(args_file_flags "${STAGE2_ARGS_FILE}" | sed -E 's/--double_coldsplit//')"

mkdir -p "${LOG_ROOT}"

log1="${LOG_ROOT}/structural_pretrain_seed${SEED}_batch${BATCH}.log"

# Built here (not inside the single printf below) because it's one segment per
# family, all needing the same %q-safe quoting as everything else in
# train_command.
family_commands=""
for family in "${PROTEIN_GROUPS[@]}"; do
    log_fam="${LOG_ROOT}/structural_pretrain_familyonly_${family}_seed${SEED}_batch${BATCH}.log"
    one_command=""
    printf -v one_command \
        'printf "=== STAGE 2: FAMILY_ONLY %%s | seed: %%s ===\n" %q %q; PYTHONUNBUFFERED=1 python ./training/new_train.py %s --family_only=%q --batch=%q --num_workers=%q --seed=%q 2>&1 | tee %q; ' \
        "${family}" "${SEED}" \
        "${stage2_args}" "${family}" "${BATCH}" "${NUM_WORKERS}" "${SEED}" "${log_fam}"
    family_commands+="${one_command}"
done

job_name="structural_pretrain_chain"
train_command=""
job_command=""

printf -v train_command \
    'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= %q )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=%%s MiB. Checking again in %%s seconds.\n" "${free_gpu_mib:-unknown}" %q %q; sleep %q; done; printf "=== STAGE 1: STRUCTURAL PRETRAIN | seed: %%s | GPU: %%s | batch: %%s ===\n" %q "${gpu_name}" %q; PYTHONUNBUFFERED=1 python ./training/new_train.py %s --batch=%q --num_workers=%q --seed=%q 2>&1 | tee %q && { %s }' \
    "${MIN_FREE_GPU_MIB}" "${MIN_FREE_GPU_MIB}" \
    "${GPU_WAIT_SECONDS}" "${GPU_WAIT_SECONDS}" \
    "${SEED}" "${BATCH}" \
    "${stage1_args}" "${BATCH}" "${NUM_WORKERS}" "${SEED}" "${log1}" \
    "${family_commands}"

printf -v job_command \
    'cd %q && source %q && conda activate %q && bash -o pipefail -c %q' \
    "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" "${train_command}"

oarsub \
    --name "${job_name}" \
    -l "/nodes=1/gpu=1,walltime=${WALLTIME}" \
    -p "${GPU_PROPERTY}" \
    --project "${PROJECT}" \
    -O "${LOG_ROOT}/structural_pretrain_chain_%jobid%.out" \
    -E "${LOG_ROOT}/structural_pretrain_chain_%jobid%.err" \
    "${job_command}"
