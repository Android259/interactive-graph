#!/usr/bin/env bash
# Runs a PACK of experiments inside ONE OAR job.
#
# Invoked on the compute node as the job command:
#   bash scripts/run_experiment_pack.sh <base64-spec>
# where the spec is built by scripts/pack_lib.sh (see its header for the record
# layout). Keeping the logic in a real repository file rather than in a printf'd
# one-liner is what makes it reviewable and testable; the submitter only splices
# a single base64 blob into the oarsub command line.
#
# Deliberately NOT `set -e`: a pack exists to amortise one GPU allocation over
# several trainings, so one training that dies must not take the rest of the
# pack with it. Failures are counted and reported at the end.
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_DIR}"
# shellcheck source=scripts/lib/pack_lib.sh
source "${PROJECT_DIR}/scripts/lib/pack_lib.sh"

# Same knobs the one-experiment-per-job path uses, plus the packing ones.
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
# 1 on a CPU-only cluster (kraken-cpu): no nvidia-smi, no GPU admission/lock/
# memory-wait below -- concurrency comes from cores (nproc/PACK_CPU_PER_RUN)
# alone, same arithmetic the GPU path already uses for its own CPU cap.
CPU_ONLY="${CPU_ONLY:-0}"
JOB_ID_TAG="${JOB_ID_TAG:-}"
# Upper bound on concurrent trainings. The effective number is decided below
# from the card that was actually allocated.
PACK_PARALLEL="${PACK_PARALLEL:-1}"
# Measured GPU footprint of one training, in MiB. 0 = do not scale by card.
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
# Share of the card the pack is allowed to fill.
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
# CPU cores one training needs (main process + its DataLoader workers). Bigfoot
# hands out far fewer cores per GPU than Kraken's 48, so the same memory-derived
# concurrency would oversubscribe the cpuset there.
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-5}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-0}"
# Skip experiments a previous (walltime-killed) attempt already finished.
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"

if (( $# != 1 )); then
    printf 'Usage: %s <base64-pack-spec>\n' "${0##*/}" >&2
    exit 2
fi

spec="$(printf '%s' "$1" | base64 -d)" || {
    printf 'Could not decode the pack specification.\n' >&2
    exit 2
}

omp_threads_per_run=0
if (( CPU_ONLY )); then
    # --- CPU-only admission: no card to name, lock or wait memory on ---------
    # kraken-cpu (scripts/lib/cluster_common.sh) has no nvidia-smi at all, and no
    # GPU-bundled core count to profile the way pack_hardware_profile() does for
    # bigfoot/kraken -- the whole allocation IS the cores (OAR_RESOURCES=/nodes=1),
    # so concurrency is nproc/PACK_CPU_PER_RUN alone, same formula the GPU path
    # already uses as its OWN cpu cap (the "by_cpu" arithmetic below).
    gpu_name="cpu"
    gpu_uuid="job${OAR_JOB_ID:-local}"
    gpu_total_mib=0
    hardware_profile="cpu"
    run_min_free_gpu_mib=0

    (( PACK_CPU_PER_RUN > 0 )) || PACK_CPU_PER_RUN=1
    slots=$(( $(nproc) / PACK_CPU_PER_RUN ))
    (( slots >= 1 )) || slots=1
    (( PACK_PARALLEL <= 0 || slots <= PACK_PARALLEL )) || slots="${PACK_PARALLEL}"
    # Threads per run pinned to the cores it was budgeted, same discipline
    # run_local.sh uses OMP_THREADS_PER_JOB for: fixed once, not re-derived
    # mid-pack, so at::parallel_for splits every reduction the same way for
    # every run regardless of how many slots happened to be free when it started.
    omp_threads_per_run="${PACK_CPU_PER_RUN}"

    printf '=== PACK on %s cores (CPU-only, job %s): %d concurrent slot(s), %s thread(s)/run ===\n' \
        "$(nproc)" "${OAR_JOB_ID:-local}" "${slots}" "${omp_threads_per_run}"
else
    # --- GPU admission: identical guard to the single-experiment command -----
    gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"

    # The alternation in GPU_MODEL_GLOB ("*A100*|*V100*") must be split by hand.
    # In the one-experiment-per-job path the glob is spliced into the *text* of
    # the generated command, so bash parses the `|` as a case-pattern separator;
    # here it arrives in a variable, where `|` is just a character and the whole
    # string would be matched literally -- rejecting every real GPU.
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

    gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd 'A-Za-z0-9_-')"
    gpu_total_mib="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
    [[ "${gpu_total_mib}" =~ ^[0-9]+$ ]] || gpu_total_mib=0

    # --- How many trainings this particular card can hold ---------------------
    # This is the point of resolving concurrency inside the job: a 32GB V100 and
    # a 142GB H200 both match GPU_PROPERTY, but they do not hold the same number
    # of these trainings.
    IFS=$'\t' read -r hardware_profile profile_parallel profile_mib_per_run \
        profile_min_free profile_cpu_per_run < <(pack_hardware_profile "${gpu_name}")

    if [[ "${PACK_HARDWARE_AUTO}" == "1" ]]; then
        (( PACK_PARALLEL > 0 )) || PACK_PARALLEL="${profile_parallel}"
        (( GPU_MIB_PER_RUN > 0 )) || GPU_MIB_PER_RUN="${profile_mib_per_run}"
        (( PACK_CPU_PER_RUN > 0 )) || PACK_CPU_PER_RUN="${profile_cpu_per_run}"
        (( PACK_MIN_FREE_GPU_MIB > 0 )) || PACK_MIN_FREE_GPU_MIB="${profile_min_free}"
    fi

    slots="${PACK_PARALLEL}"
    (( slots >= 1 )) || slots=1
    run_min_free_gpu_mib="${PACK_MIN_FREE_GPU_MIB}"
    (( run_min_free_gpu_mib > 0 )) || run_min_free_gpu_mib="${MIN_FREE_GPU_MIB}"

    if (( GPU_MIB_PER_RUN > 0 && gpu_total_mib > 0 )); then
        by_memory=$(( gpu_total_mib * PACK_GPU_PERCENT / 100 / GPU_MIB_PER_RUN ))
        (( by_memory >= 1 )) || by_memory=1
        (( slots > by_memory )) && slots="${by_memory}"
    fi

    if (( PACK_CPU_PER_RUN > 0 )); then
        # nproc reports the OAR cpuset, i.e. the cores this job may actually use.
        by_cpu=$(( $(nproc) / PACK_CPU_PER_RUN ))
        (( by_cpu >= 1 )) || by_cpu=1
        (( slots > by_cpu )) && slots="${by_cpu}"
    fi

    printf '=== PACK on %s (%s MiB, %s cores): profile=%s, %d concurrent slot(s), cap=%s, per-run=%s MiB, min-free=%s MiB ===\n' \
        "${gpu_name}" "${gpu_total_mib}" "$(nproc)" "${hardware_profile}" \
        "${slots}" "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" "${run_min_free_gpu_mib}"
fi

# --- One experiment ----------------------------------------------------------
run_experiment() {
    local header="$1" log_file="$2" out_base="$3" python_args="$4"
    local out_file done_marker slot lock_file free_gpu_mib status

    out_file="${out_base}${JOB_ID_TAG}${OAR_JOB_ID:-0}.out"
    done_marker="$(dirname "${log_file}")/.pack_done/$(basename "${log_file}" .log)"

    mkdir -p "$(dirname "${log_file}")" "$(dirname "${done_marker}")"

    if [[ "${PACK_SKIP_DONE}" == "1" && -f "${done_marker}" ]]; then
        printf 'SKIP (already completed): %s\n' "${header}"
        return 0
    fi

    # Take one of the card's slots. Slot 0 keeps the historical lock path, so a
    # packed job and a one-experiment-per-job submission still exclude each
    # other on that slot instead of silently ignoring one another.
    while true; do
        for (( slot = 0; slot < slots; slot++ )); do
            if (( slot == 0 )); then
                lock_file="/tmp/dl-project-${gpu_uuid}.lock"
            else
                lock_file="/tmp/dl-project-${gpu_uuid}-slot${slot}.lock"
            fi
            (
                exec 9>"${lock_file}" || exit 70
                flock -n 9 || exit 75

                # Only once the slot is held does waiting for memory make sense:
                # otherwise every queued stream would race on the same reading.
                # Nothing to wait for on CPU_ONLY: there is no nvidia-smi, and
                # OAR's cpuset already partitions memory with the cores (kraken-c/
                # f nodes are 4-8 GiB/core, this project's heaviest measured
                # per-job footprint so far is under 2 GiB, see run_local.sh).
                if (( ! CPU_ONLY )); then
                    while true; do
                        free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
                        if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= run_min_free_gpu_mib )); then
                            break
                        fi
                        printf 'Waiting for GPU memory: free=%s MiB, required=%s MiB. Checking again in 60 seconds.\n' \
                            "${free_gpu_mib:-unknown}" "${run_min_free_gpu_mib}"
                        sleep 60
                    done
                fi

                printf '=== %s | GPU: %s | SLOT: %d ===\n' \
                    "${header}" "${gpu_name}" "${slot}" > "${out_file}"
                # `eval set --`, not bare ${python_args}: the one-experiment-per-job
                # path splices the arg_files flag block into a string that the
                # compute node runs through `bash -c`, so the shell removes the
                # quotes in flags like --pool_type="gem". Plain word splitting
                # would hand python the quote characters themselves and change
                # the run. This reproduces that single round of interpretation.
                eval "set -- ${python_args}"
                if (( CPU_ONLY )); then
                    # Pinned to the cores this run was budgeted (PACK_CPU_PER_RUN),
                    # not left at PyTorch's default (all visible cores): with
                    # `slots` runs sharing the node, an unset thread count would
                    # have every one of them try to use the whole node at once.
                    OMP_NUM_THREADS="${omp_threads_per_run}" MKL_NUM_THREADS="${omp_threads_per_run}" \
                    PYTHONUNBUFFERED=1 python ./training/new_train.py "$@" 2>&1 |
                        tee -a "${out_file}" |
                        tee "${log_file}"
                else
                    PYTHONUNBUFFERED=1 python ./training/new_train.py "$@" 2>&1 |
                        tee -a "${out_file}" |
                        tee "${log_file}"
                fi
                exit "${PIPESTATUS[0]}"
            )
            status=$?
            if (( status == 75 )); then
                continue            # slot busy, try the next one
            fi
            if (( status == 0 )); then
                : > "${done_marker}"
            else
                printf 'FAILED (exit %d): %s\n' "${status}" "${header}" >&2
            fi
            return "${status}"
        done
        # Every slot on this card is busy (another job holds them); wait and
        # rescan rather than giving up the experiment.
        sleep 60
    done
}

# --- Drive the pack ----------------------------------------------------------
# `wait -n` keeps the card full as soon as any stream ends; without it (bash <
# 4.3) fall back to fixed batches.
running=0
failures=0
declare -a pids=()

reap_one() {
    if (( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 3) )); then
        wait -n
        (( $? == 0 )) || failures=$(( failures + 1 ))
        running=$(( running - 1 ))
    else
        local pid
        for pid in "${pids[@]}"; do
            wait "${pid}" || failures=$(( failures + 1 ))
        done
        pids=()
        running=0
    fi
}

total=0
while IFS=$'\t' read -r header log_file out_base python_args; do
    [[ -n "${header}" ]] || continue
    total=$(( total + 1 ))

    while (( running >= slots )); do
        reap_one
    done

    run_experiment "${header}" "${log_file}" "${out_base}" "${python_args}" &
    pids+=("$!")
    running=$(( running + 1 ))
done <<< "${spec}"

while (( running > 0 )); do
    reap_one
done

printf '=== PACK finished: %d experiment(s), %d failure(s) ===\n' "${total}" "${failures}"
(( failures == 0 ))
