#!/usr/bin/env bash
# Submit one variant's whole group x seed grid to OAR.
#
#   bash scripts/launch/submit_grid.sh scripts/arg_files/<config>.md
#
# One file for both series. Which one runs is decided by the config itself: a
# --cold_split flag in it selects separate held-out validation and test groups
# (the table below), anything else excludes one group and uses it for both.
#
# Called through scripts/run_bigfoot.sh / run_kraken.sh, which supply every
# cluster-dependent setting as an environment variable -- never by patching this
# file's text.
#
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

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Walltime, the group lists and the default seeds.
# shellcheck source=scripts/settings.sh
source "${PROJECT_DIR}/scripts/settings.sh"
# shellcheck source=scripts/lib/pack_lib.sh
source "${PROJECT_DIR}/scripts/lib/pack_lib.sh"
# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_DIR}/scripts/lib/args_file_lib.sh"
# shellcheck source=scripts/lib/grid_lib.sh
source "${PROJECT_DIR}/scripts/lib/grid_lib.sh"

# --- cluster-dependent settings ----------------------------------------------
# Every default is a Bigfoot value, so an unset environment targets Bigfoot.
# `-` rather than `:-` for PROJECT and
# GPU_PROPERTY: an explicitly empty value must stay empty so the corresponding
# oarsub flag is omitted (a cluster may need no project, or no gpumodel filter).
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
PROJECT="${PROJECT-pr-molgen}"
GPU_PROPERTY="${GPU_PROPERTY-(gpumodel='A100' OR gpumodel='V100')}"
# Shell `case` pattern matched against `nvidia-smi --query-gpu=name` inside the
# job, hence the character whitelist below.
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
GPU_RESOURCES="${GPU_RESOURCES:-/nodes=1/gpu=1}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
# Distinguishes OAR output filenames between clusters, whose job-ID spaces
# overlap (the progress table locates a running job's log by `*_${job_id}.out`).
JOB_ID_TAG="${JOB_ID_TAG:-}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
# Space-separated subsets, for a smoke test instead of the full 45.
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"

# --- packing ------------------------------------------------------------------
# PACK_SIZE experiments share one OAR job; PACK_PARALLEL of them may run at once
# on the single allocated GPU (the effective number is decided inside the job
# from the card actually handed out -- see run_experiment_pack.sh). PACK_SIZE=1
# is one experiment per job, which run_one_experiment.sh handles directly.
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
    printf "PACK_HARDWARE_AUTO must be 0 or 1: %s\n" "${PACK_HARDWARE_AUTO}" >&2
    exit 2
fi
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

# --- what this config asks for ------------------------------------------------
COLD_SPLIT=0
if args_file_has_flag "${args_file}" --cold_split; then
    COLD_SPLIT=1
fi

# The shorter request only for configurations that explicitly enable the fast
# path. Feeds both unpacked jobs and pack walltime arithmetic.
if args_file_has_flag "${args_file}" --fast_attention; then
    WALLTIME="${FAST_ATTENTION_WALLTIME}"
    printf "Detected --fast_attention; per-experiment walltime=%s.\n" "${WALLTIME}"
fi

variant="$(basename "${args_file}" .md)"
args_template="$(args_file_flags "${args_file}")"

if (( COLD_SPLIT )); then
    output_root="script_logs/${variant}_coldval_seeds01234"
    groups=("${COLD_TEST_GROUPS[@]}")
else
    output_root="script_logs/${variant}_seeds01234"
    groups=("${PROTEIN_GROUPS[@]}")
fi
seeds=("${DEFAULT_SEEDS[@]}")
[[ -z "${GROUPS_OVERRIDE}" ]] || read -r -a groups <<< "${GROUPS_OVERRIDE}"
[[ -z "${SEEDS_OVERRIDE}" ]] || read -r -a seeds <<< "${SEEDS_OVERRIDE}"

mkdir -p "${output_root}"
grid_load_completed "${variant}" "" "${COLD_SPLIT}"

# TEST -> VAL mapping (see the table at the top). Only read in cold-split mode.
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

resolve_val_group() {
    local test_group="$1" val_group="${val_for_test[$1]:-}"
    if [[ -z "${val_group}" ]]; then
        printf "No validation group defined for test group: %s\n" "${test_group}" >&2
        exit 1
    fi
    printf '%s\n' "${val_group}"
}

# --- one experiment as a record ----------------------------------------------
# The record layout is scripts/lib/pack_lib.sh's; both runners read it, so an
# experiment is described the same way whether it is run alone or in a pack, and
# both write the same tree.
experiment_record() {
    local group="$1" seed="$2"
    local val_group excluded output_dir stem header extra=""

    if (( COLD_SPLIT )); then
        val_group="$(resolve_val_group "${group}")"
        excluded="${group},${val_group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_val-${val_group}_seed${seed}"
        extra=" --test_group=${group}"
        header="TEST: ${group} | VAL: ${val_group} | VARIANT: ${variant} | SEED: ${seed}"
    else
        excluded="${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="GROUP: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    fi

    mkdir -p "${output_dir}"
    pack_record \
        "${header}" \
        "${output_dir}/${stem}_ep150_batch16.log" \
        "${output_dir}/${stem}_" \
        "--label=${variant} ${args_template} --seed=${seed} --excluded_groups=${excluded}${extra}"
}

# --- oarsub -------------------------------------------------------------------
# Built as an array so an empty GPU_PROPERTY/PROJECT omits the flag entirely.
# `if` blocks rather than `[[ ]] &&`: a false test as the last command would
# return 1 and `set -e` would abort the whole submitter.
oarsub_submit() {
    local job_name="$1" walltime="$2" out_prefix="$3" job_command="$4"
    local -a oarsub_args=(
        --name "${job_name}"
        -l "${GPU_RESOURCES},walltime=${walltime}"
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
        -O "${out_prefix}.out"
        -E "${out_prefix}.err"
        "${job_command}"
    )
    oarsub "${oarsub_args[@]}"
}

# The OAR job name. It is what the progress table falls back to for a job whose
# output path OAR does not report, so a cold-split job has to keep naming its
# validation group here.
job_name() {
    local group="$1" seed="$2"
    if (( COLD_SPLIT )); then
        printf '%s_%s_v%s_s%s\n' \
            "${variant}" "${group}" "$(resolve_val_group "${group}")" "${seed}"
    else
        printf '%s_%s_s%s\n' "${variant}" "${group}" "${seed}"
    fi
}

submit_one() {
    local group="$1" seed="$2"
    local record log_file out_base job_command

    record="$(experiment_record "${group}" "${seed}")"
    IFS=$'\t' read -r _ log_file out_base _ <<< "${record}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q bash scripts/launch/run_one_experiment.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "$(pack_spec_encode "${record}")"

    oarsub_submit "$(job_name "${group}" "${seed}")" "${WALLTIME}" \
        "${out_base}${JOB_ID_TAG}%jobid%" "${job_command}"
}

submit_pack() {
    local pack_index="$1" spec="$2" pack_count="$3"
    local job_walltime pack_dir job_command runner_env

    job_walltime="$(pack_job_walltime "${pack_count}" "${WALLTIME}" "${PACK_WALLTIME_PARALLEL}")"
    pack_check_walltime "${job_walltime}" "${MAX_WALLTIME}" || exit 2

    # The job's own stdout must NOT land on a "*_<tag><jobid>.out" path: that
    # pattern belongs to the per-experiment files the runner writes, and the
    # progress table turns every match into a row.
    pack_dir="${output_root}/_packs"
    mkdir -p "${pack_dir}"

    printf -v runner_env \
        'GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q JOB_ID_TAG=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q' \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "${JOB_ID_TAG}" \
        "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" "${PACK_GPU_PERCENT}" \
        "${PACK_CPU_PER_RUN}" "${PACK_MIN_FREE_GPU_MIB}" \
        "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && %s bash scripts/launch/run_experiment_pack.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${runner_env}" "$(pack_spec_encode "${spec}")"

    printf "Pack %d: %d experiment(s), walltime=%s.\n" \
        "${pack_index}" "${pack_count}" "${job_walltime}"
    oarsub_submit "${variant}$( (( COLD_SPLIT )) && printf _coldval )_pack${pack_index}" \
        "${job_walltime}" \
        "${pack_dir}/${variant}_pack${pack_index}_${JOB_ID_TAG}%jobid%.pack" \
        "${job_command}"
}

# --- the grid -----------------------------------------------------------------
# The seed loop stays innermost (grid_pairs), so a pack of 5 is exactly one
# group's seeds and a pack of 9 spans groups at a fixed seed -- both natural
# units to resubmit or cancel as a whole.
submitted=0
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

while IFS=$'\t' read -r group seed; do
    [[ -n "${group}" ]] || continue
    experiments=$((experiments + 1))
    if (( PACK_SIZE <= 1 )); then
        submit_one "${group}" "${seed}"
        submitted=$((submitted + 1))
        continue
    fi
    pack_spec+="$(experiment_record "${group}" "${seed}")"$'\n'
    pack_count=$((pack_count + 1))
    if (( pack_count >= PACK_SIZE )); then
        flush_pack
    fi
done < <(grid_pairs "${groups[*]}" "${seeds[*]}")
flush_pack

if (( PACK_SIZE <= 1 )); then
    printf "Submitted %d jobs %s across %d groups and %d seeds%s.\n" \
        "${submitted}" "${variant}" "${#groups[@]}" "${#seeds[@]}" \
        "$( (( COLD_SPLIT )) && printf ', separate cold validation group per fold' )"
else
    printf "Submitted %d packed job(s) %s: %d experiments (%d groups x %d seeds), up to %d per job, up to %d concurrent per GPU%s.\n" \
        "${submitted}" "${variant}" "${experiments}" "${#groups[@]}" "${#seeds[@]}" \
        "${PACK_SIZE}" "${PACK_PARALLEL}" \
        "$( (( COLD_SPLIT )) && printf ', cold split' )"
fi

