#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# COLD SPLIT with SEPARATE validation and test protein groups.
#
# Each job trains on 7 groups, validates (checkpoint selection) on 1 held-out
# group, and tests on a DIFFERENT held-out group. Test rotates over all 9
# groups (complete cold coverage); validation is picked -- not by brute-force
# permutation -- from a "safe" pool so that (a) removing it barely shrinks the
# training set and (b) its class balance is a usable proxy for the val metric.
#
#   run:  python ./training/new_train.py \
#             --excluded_groups=<TEST>,<VAL> --test_group=<TEST> ...
#   -> csvtest    = TEST group   (reported, seen once at the end)
#   -> csvalidate = VAL  group   (drives early-stopping / checkpoint choice)
#   -> csvtrain   = the other 7 groups
#
# 9 test groups x 5 seeds = 45 jobs.
#
# -----------------------------------------------------------------------------
# GROUP STATISTICS  (data/Processed_Negative_Interaction_Corrected_Domains.csv)
#   overall positive fraction = 6.9%   |   total interactions = 11018
#
#   group          total    pos    neg    pos%   %of-all   role-as-VAL?
#   -----------------------------------------------------------------------
#   lipocalin       3123     90   3033    2.9%    28.3%    NO  (too large)
#   CRAL-TRIO       2845    204   2641    7.2%    25.8%    NO  (too large)
#   START            982    200    782   20.4%     8.9%    NO  (balance too skewed)
#   IP_trans         943     65    878    6.9%     8.6%    YES (balance == global)
#   scp2             936     43    893    4.6%     8.5%    YES (small, ~balanced)
#   LBP_BPI_CETP     626     55    571    8.8%     5.7%    YES (small, ~balanced)
#   OSBP             626      8    618    1.3%     5.7%    NO  (only 8 positives)
#   GLTP             625     81    544   13.0%     5.7%    YES (small, enough pos)
#   ML               312     10    302    3.2%     2.8%    NO  (tiny, 10 positives)
#
#   VAL pool = { IP_trans, scp2, LBP_BPI_CETP, GLTP } : each <=8.6% of the data
#   (training barely suffers) and each has >=40 positives with a balance not far
#   from the global 6.9% (val metric stays meaningful).
#
# -----------------------------------------------------------------------------
# TEST -> VAL ASSIGNMENT
#   VAL = the safe-pool group whose positive-fraction is closest to the TEST
#   group's (a "not too different" proxy), excluding TEST itself.
#
#   TEST            pos%     ->  VAL             pos%   train-loss (test+val %of-all)
#   ---------------------------------------------------------------------------
#   lipocalin       2.9%     ->  scp2            4.6%    36.8%  (28.3 + 8.5)
#   CRAL-TRIO       7.2%     ->  IP_trans        6.9%    34.4%  (25.8 + 8.6)
#   START          20.4%     ->  LBP_BPI_CETP    8.8%    14.6%  ( 8.9 + 5.7)  [see note]
#   IP_trans        6.9%     ->  LBP_BPI_CETP    8.8%    14.3%  ( 8.6 + 5.7)
#   scp2            4.6%     ->  IP_trans        6.9%    17.1%  ( 8.5 + 8.6)
#   LBP_BPI_CETP    8.8%     ->  IP_trans        6.9%    14.3%  ( 5.7 + 8.6)
#   OSBP            1.3%     ->  scp2            4.6%    14.2%  ( 5.7 + 8.5)
#   GLTP           13.0%     ->  LBP_BPI_CETP    8.8%    11.4%  ( 5.7 + 5.7)
#   ML              3.2%     ->  scp2            4.6%    11.3%  ( 2.8 + 8.5)
#
#   VAL usage: scp2 x3, IP_trans x3, LBP_BPI_CETP x3, GLTP x0  (val != test always).
#
#   NOTE: balanced accuracy (the checkpoint-selection metric) is prevalence-
#   invariant, so matching VAL's positive-fraction to TEST is not required; the
#   VAL group must instead give a learnable, above-chance signal. GLTP collapses
#   (BA~0.41) and cannot select a meaningful epoch, so START's VAL is the
#   learnable LBP_BPI_CETP (BA~0.76) despite the balance mismatch, and GLTP is no
#   longer used for validation anywhere.
# =============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Cluster-dependent settings; see scripts/submit_all_groups_all_seeds.sh for the
# rationale. Defaults reproduce the Bigfoot values that used to be hardcoded.
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
# `-` not `:-`: an explicitly empty value must survive so the flag is omitted.
PROJECT="${PROJECT-pr-molgen}"
GPU_PROPERTY="${GPU_PROPERTY-(gpumodel='A100' OR gpumodel='V100')}"
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
GPU_RESOURCES="${GPU_RESOURCES:-/nodes=1/gpu=1}"
WALLTIME="${WALLTIME:-5:00:00}"
FAST_ATTENTION_WALLTIME="${FAST_ATTENTION_WALLTIME:-0:20:00}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
JOB_ID_TAG="${JOB_ID_TAG:-}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
# Subsets of the TEST rotation / seeds, for a one-job smoke test.
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"

# Packing; see scripts/submit_all_groups_all_seeds.sh and scripts/pack_lib.sh.
# PACK_SIZE=1 leaves the historical one-experiment-per-job path untouched.
PACK_SIZE="${PACK_SIZE:-1}"
PACK_PARALLEL="${PACK_PARALLEL:-1}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-5}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-0}"
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"
PACK_WALLTIME_PARALLEL="${PACK_WALLTIME_PARALLEL:-1}"
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

# Keep ordinary configurations on WALLTIME; only an explicit fast-attention
# flag gets the shorter per-experiment request (including packed jobs).
if grep -qE '^--fast_attention([[:space:]=]|$)' "${args_file}"; then
    WALLTIME="${FAST_ATTENTION_WALLTIME}"
    printf "Detected --fast_attention; per-experiment walltime=%s.\n" "${WALLTIME}"
fi

variant="$(basename "${args_file}" .md)"

mkdir -p "script_logs/${variant}_coldval_seeds01234"

args_template="$(grep '^--' "${args_file}" | tr '\n' ' ')"

declare -A completed_pairs=()
if [[ "${COMPLETE_ONLY}" == "1" ]]; then
    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && completed_pairs["${pair}"]=1
    done <<< "${COMPLETED_EXPERIMENTS}"
    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && completed_pairs["${pair}"]=1
    done < <(python3 scripts/list_completed_experiments.py "${variant}" --cold-split)
fi

is_completed() {
    [[ "${COMPLETE_ONLY}" == "1" && -n "${completed_pairs["$1:$2"]:-}" ]]
}

# TEST -> VAL mapping (see table above). Test rotates over all 9 groups.
declare -A val_for_test=(
    ["lipocalin"]="scp2"
    ["CRAL-TRIO"]="IP_trans"
    ["START"]="LBP_BPI_CETP"
    ["IP_trans"]="LBP_BPI_CETP"
    ["scp2"]="IP_trans"
    ["LBP_BPI_CETP"]="IP_trans"
    ["OSBP"]="scp2"
    ["GLTP"]="LBP_BPI_CETP"
    ["ML"]="scp2"
)

# Deterministic test-group order (matches the table).
test_groups=(
    "lipocalin"
    "CRAL-TRIO"
    "START"
    "IP_trans"
    "scp2"
    "LBP_BPI_CETP"
    "OSBP"
    "GLTP"
    "ML"
)

seeds=(0 1 2 3 4)

submit_variant() {
    local test_group="$1"
    local val_group="$2"
    local seed="$3"
    local excluded="${test_group},${val_group}"
    local output_dir="script_logs/${variant}_coldval_seeds01234/${test_group}"
    local log_file="${output_dir}/${variant}_val-${val_group}_seed${seed}_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    # See submit_all_groups_all_seeds.sh: GPU_MODEL_GLOB must use %s (a %q-escaped
    # glob would never match), MIN_FREE_GPU_MIB uses %q twice and is digits-only.
    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in %s) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= %q )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=%q MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== TEST: %%s | VAL: %%s | VARIANT: %s | SEED: %%s | GPU: %%s ===\n" %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --label=%q %s --seed=%q --excluded_groups=%q --test_group=%q 2>&1 | tee %q' \
        "${GPU_MODEL_GLOB}" \
        "${MIN_FREE_GPU_MIB}" \
        "${MIN_FREE_GPU_MIB}" \
        "${variant}" \
        "${test_group}" "${val_group}" "${seed}" \
        "${variant}" "${args_template}" "${seed}" "${excluded}" "${test_group}" "${log_file}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && bash -o pipefail -c %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" "${train_command}"

    # Array form so an empty GPU_PROPERTY/PROJECT omits the flag; `if` blocks
    # rather than `[[ ]] &&` so a false test cannot trip `set -e`.
    local -a oarsub_args=(
        --name "${variant}_${test_group}_v${val_group}_s${seed}"
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
        -O "${output_dir}/${variant}_val-${val_group}_seed${seed}_${JOB_ID_TAG}%jobid%.out"
        -E "${output_dir}/${variant}_val-${val_group}_seed${seed}_${JOB_ID_TAG}%jobid%.err"
        "${job_command}"
    )

    oarsub "${oarsub_args[@]}"
}

# --- Pack path ---------------------------------------------------------------
# Same log paths and python arguments submit_variant would have produced, so a
# packed cold-split run writes the same tree as an unpacked one.
experiment_record() {
    local test_group="$1" val_group="$2" seed="$3"
    local excluded="${test_group},${val_group}"
    local output_dir="script_logs/${variant}_coldval_seeds01234/${test_group}"

    mkdir -p "${output_dir}"

    pack_record \
        "TEST: ${test_group} | VAL: ${val_group} | VARIANT: ${variant} | SEED: ${seed}" \
        "${output_dir}/${variant}_val-${val_group}_seed${seed}_ep150_batch16.log" \
        "${output_dir}/${variant}_val-${val_group}_seed${seed}_" \
        "--label=${variant} ${args_template} --seed=${seed} --excluded_groups=${excluded} --test_group=${test_group}"
}

submit_pack() {
    local pack_index="$1"
    local spec="$2"
    local pack_count="$3"
    local job_walltime pack_dir job_command runner_env

    job_walltime="$(pack_job_walltime "${pack_count}" "${WALLTIME}" "${PACK_WALLTIME_PARALLEL}")"
    pack_check_walltime "${job_walltime}" "${MAX_WALLTIME}" || exit 2

    # Kept off the "*_<tag><jobid>.out" pattern, which belongs to the
    # per-experiment files the runner writes for wait_progress_table.sh.
    pack_dir="script_logs/${variant}_coldval_seeds01234/_packs"
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
        --name "${variant}_coldval_pack${pack_index}"
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

if [[ -n "${GROUPS_OVERRIDE}" ]]; then
    read -r -a test_groups <<< "${GROUPS_OVERRIDE}"
fi
if [[ -n "${SEEDS_OVERRIDE}" ]]; then
    read -r -a seeds <<< "${SEEDS_OVERRIDE}"
fi

resolve_val_group() {
    local test_group="$1" val_group

    val_group="${val_for_test[${test_group}]:-}"
    if [[ -z "${val_group}" ]]; then
        printf "No validation group defined for test group: %s\n" "${test_group}" >&2
        exit 1
    fi
    printf '%s\n' "${val_group}"
}

submitted=0

if (( PACK_SIZE <= 1 )); then
    for test_group in "${test_groups[@]}"; do
        val_group="$(resolve_val_group "${test_group}")"
        for seed in "${seeds[@]}"; do
            if is_completed "${test_group}" "${seed}"; then
                printf "Skipping completed experiment: test_group=%s seed=%s.\n" \
                    "${test_group}" "${seed}"
                continue
            fi
            submit_variant "${test_group}" "${val_group}" "${seed}"
            submitted=$((submitted + 1))
        done
    done

    printf "Submitted %d cold-split jobs %s: %d test groups x %d seeds, separate cold validation group per fold.\n" \
        "${submitted}" "${variant}" "${#test_groups[@]}" "${#seeds[@]}"
    exit 0
fi

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

for test_group in "${test_groups[@]}"; do
    val_group="$(resolve_val_group "${test_group}")"
    for seed in "${seeds[@]}"; do
        if is_completed "${test_group}" "${seed}"; then
            printf "Skipping completed experiment: test_group=%s seed=%s.\n" \
                "${test_group}" "${seed}"
            continue
        fi
        pack_spec+="$(experiment_record "${test_group}" "${val_group}" "${seed}")"$'\n'
        pack_count=$((pack_count + 1))
        experiments=$((experiments + 1))
        if (( pack_count >= PACK_SIZE )); then
            flush_pack
        fi
    done
done
flush_pack

printf "Submitted %d packed cold-split job(s) %s: %d experiments (%d test groups x %d seeds), up to %d per job, up to %d concurrent per GPU.\n" \
    "${submitted}" "${variant}" "${experiments}" "${#test_groups[@]}" "${#seeds[@]}" \
    "${PACK_SIZE}" "${PACK_PARALLEL}"
