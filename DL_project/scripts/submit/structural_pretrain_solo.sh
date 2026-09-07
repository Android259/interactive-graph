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
#
# ---------------------------------------------------------------------------
# What the first run of this (2026-09-07, script_logs/structural_pretrain/) got
# wrong, and what changed here:
#
# 1. ONE LABEL FOR NINE FAMILIES. Stage 2 passed no --label, so new_train.py fell
#    back to OAR_JOB_NAME and every family reported `label: structural_pretrain_
#    chain`, `exclusion_set: random`, `seed: 0`. Three consequences, all silent:
#    metrics_summary.csv got nine rows that analysis/compare_labels.py's
#    latest_rows_for_label -- keyed on (exclusion_set, seed) -- collapses to
#    whichever finished last (OSBP: 2 test rows, BA 0.500), so eight families
#    were invisible to every summary; models/structural_pretrain_chain/random/
#    seed0.pt was overwritten nine times, leaving only the last family's weights;
#    and TensorBoard runs shared one directory. Fixed on both sides: an explicit
#    per-arm --label below, and new_train.py now puts --family_only into
#    excluded_set_name (so the path is groups_<family>, like every other axis).
#    One label per ARM, nine exclusion sets inside it -- which is what makes
#    `analysis/summarize_label.py --label structural_pretrain_family` print the
#    per-family breakdown by itself.
#
# 2. ONE SEED. Stage-2 test blocks are 2-36 rows. At that size a single seed
#    cannot tell START's +0.180 over its own null model from luck. STAGE2_SEEDS
#    now defaults to five.
#
# 3. NO CONTROL. Every stage-2 run loaded the stage-1 checkpoint, so nothing in
#    the batch answers whether the pretraining contributed anything at all, or
#    whether +0.180 on START is just what 382 training rows buy. Each family now
#    runs TWICE: once with the pretrained frozen encoders, once from scratch
#    with those two flags stripped, under two labels that differ in nothing else.
#
# Stage 1 stays at a single seed on purpose: it is the shared structural prior,
# and holding it fixed is what makes the two arms differ in exactly one thing.
# The consequence to keep in mind when reading the result is that the pretrained
# arm's seed-to-seed spread measures stage-2 variance only, while the scratch
# arm's measures the whole pipeline's.
#
# Runtime: stage 2 is 9 families x |STAGE2_SEEDS| x 2 arms. The 2026-09-07 run
# took 1-3 min per family-run (21 min for all nine at one seed), so the default
# 90 runs is ~3.5 h, plus ~4 min for stage 1 and the GPU wait below. WALLTIME is
# set accordingly; cut STAGE2_SEEDS if the queue makes 6 h expensive.

PROJECT="${PROJECT:-pr-molgen}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
GPU_PROPERTY="${GPU_PROPERTY:-(gpumodel='A100' OR gpumodel='V100')}"
WALLTIME="${WALLTIME:-6:00:00}"
BATCH="${BATCH:-16}"
NUM_WORKERS="${NUM_WORKERS:-4}"
SEED="${SEED:-0}"
STAGE2_SEEDS="${STAGE2_SEEDS:-0 1 2 3 4}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
GPU_WAIT_SECONDS="${GPU_WAIT_SECONDS:-60}"
LOG_ROOT="${LOG_ROOT:-${PROJECT_DIR}/script_logs/structural_pretrain}"
STAGE1_ARGS_FILE="${PROJECT_DIR}/scripts/arg_files/structural_pretrain.md"
STAGE2_ARGS_FILE="${PROJECT_DIR}/scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md"
# The two stage-2 arms. Names are the --label each arm reports, and therefore the
# metrics_summary.csv label, the models/ directory and the summarize_label target.
STAGE2_PRETRAINED_LABEL="${STAGE2_PRETRAINED_LABEL:-structural_pretrain_family}"
STAGE2_SCRATCH_LABEL="${STAGE2_SCRATCH_LABEL:-structural_pretrain_family_scratch}"
# scripts/settings.sh's PROTEIN_GROUPS, all 9 families.
PROTEIN_GROUPS=(
    "CRAL-TRIO" "START" "lipocalin" "GLTP" "IP_trans"
    "LBP_BPI_CETP" "scp2" "ML" "OSBP"
)

# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_DIR}/scripts/lib/args_file_lib.sh"
stage1_args="$(args_file_flags "${STAGE1_ARGS_FILE}")"
stage2_args="$(args_file_flags "${STAGE2_ARGS_FILE}" | sed -E 's/--double_coldsplit//')"
# The control arm. --pretrained_checkpoint carries a path (so the pattern has to eat
# its value), --freeze_pretrained_encoders is bare; with both gone the run builds the
# same architecture and trains all of it from a fresh initialisation. Nothing else
# differs between the two arms.
stage2_scratch_args="$(printf '%s' "${stage2_args}" \
    | sed -E 's/--pretrained_checkpoint=[^[:space:]]+//; s/--freeze_pretrained_encoders//')"
if [[ "${stage2_scratch_args}" == "${stage2_args}" ]]; then
    printf 'Refusing to submit: the scratch arm is identical to the pretrained arm.\n' >&2
    printf 'Neither --pretrained_checkpoint nor --freeze_pretrained_encoders was found in %s\n' \
        "${STAGE2_ARGS_FILE}" >&2
    exit 2
fi

mkdir -p "${LOG_ROOT}"

log1="${LOG_ROOT}/structural_pretrain_seed${SEED}_batch${BATCH}.log"

# Built here (not inside the single printf below) because it's one segment per
# (arm, family, seed), all needing the same %q-safe quoting as everything else in
# train_command.
family_commands=""
for arm in pretrained scratch; do
    if [[ "${arm}" == "pretrained" ]]; then
        arm_args="${stage2_args}"
        arm_label="${STAGE2_PRETRAINED_LABEL}"
    else
        arm_args="${stage2_scratch_args}"
        arm_label="${STAGE2_SCRATCH_LABEL}"
    fi
    for family in "${PROTEIN_GROUPS[@]}"; do
        for stage2_seed in ${STAGE2_SEEDS}; do
            log_fam="${LOG_ROOT}/${arm_label}_${family}_seed${stage2_seed}_batch${BATCH}.log"
            one_command=""
            printf -v one_command \
                'printf "=== STAGE 2: %%s | FAMILY_ONLY %%s | seed: %%s ===\n" %q %q %q; PYTHONUNBUFFERED=1 python ./training/new_train.py %s --label=%q --family_only=%q --batch=%q --num_workers=%q --seed=%q 2>&1 | tee %q; ' \
                "${arm_label}" "${family}" "${stage2_seed}" \
                "${arm_args}" "${arm_label}" "${family}" "${BATCH}" "${NUM_WORKERS}" "${stage2_seed}" "${log_fam}"
            family_commands+="${one_command}"
        done
    done
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
