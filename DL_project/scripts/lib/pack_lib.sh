#!/usr/bin/env bash
# Packing helpers shared by the two canonical submitters.
#
# A "pack" is one OAR job that runs several experiments instead of one. Two
# dimensions combine:
#
#   PACK_SIZE      how many experiments one OAR job owns (sequential depth
#                  when nothing runs concurrently).
#   PACK_PARALLEL  upper bound on how many of them run at the same time on the
#                  single allocated GPU. The effective number is decided inside
#                  the job from the card that was actually handed out (see
#                  scripts/run_experiment_pack.sh) -- a V100-32GB and an
#                  H200-142GB do not hold the same number of trainings.
#
# PACK_SIZE=1 keeps the historical one-experiment-per-job path untouched; the
# submitters only enter the pack path when PACK_SIZE > 1.
#
# `source` this file; it defines functions only.

# ---------------------------------------------------------------------------
# Runtime hardware profiles
# ---------------------------------------------------------------------------
#
# Output (TAB-separated):
#   profile_name  parallel_cap  gpu_mib_per_run  min_free_gpu_mib  cpu_per_run
#
# The cap describes what the model family is allowed to attempt on that GPU.
# The runner still takes min(cap, memory-derived slots, CPU-derived slots), so
# 16/32GB V100 and 40/80GB A100 variants separate automatically from the
# memory.total value reported by the allocated card.
pack_hardware_profile() {
    local gpu_name="$1"

    case "${gpu_name}" in
        *V100*)
            printf 'v100\t2\t12288\t11000\t5\n'
            ;;
        *A100*)
            printf 'a100\t4\t14336\t13000\t5\n'
            ;;
        *H100*)
            # Four, measured. Eight was tried on 2026-08-19 and is worse: a run that
            # takes 22 minutes for 120 epochs with four sharing the card takes about 57
            # with eight, so throughput falls from 10.9 to 8.4 runs per hour. The card is
            # already saturated at four, and the memory arithmetic that suggested eight
            # was answering the wrong question -- what binds is compute and CPU (eight
            # runs claim 40 of 48 cores before their loaders), not GPU memory. The
            # reservation stays at the measured-enough 8192 MiB; with a cap of four it
            # never binds, and it is closer to the truth than the old 16384 placeholder.
            printf 'h100\t4\t8192\t8000\t5\n'
            ;;
        *H200*)
            # Left at its original eight and 16384 MiB, which come out at seven slots on
            # a 143771 MiB card. Lowering the reservation to match the H100 would give
            # eight, but the H100 measurement above says eight is past the point where
            # more concurrency helps, and nothing has been measured on an H200.
            printf 'h200\t8\t16384\t15000\t5\n'
            ;;
        *)
            # A supported glob can be user-overridden to a future card. Keep
            # that safe and serial until it receives a measured profile.
            printf 'generic\t1\t16384\t15000\t5\n'
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Walltime arithmetic
# ---------------------------------------------------------------------------

# "H:MM:SS" (or "HH:MM:SS", or a bare number of hours) -> seconds.
pack_walltime_seconds() {
    local walltime="$1"
    local hours minutes seconds

    if [[ "${walltime}" =~ ^([0-9]+):([0-9]{1,2}):([0-9]{1,2})$ ]]; then
        hours="${BASH_REMATCH[1]}"
        minutes="${BASH_REMATCH[2]}"
        seconds="${BASH_REMATCH[3]}"
    elif [[ "${walltime}" =~ ^([0-9]+):([0-9]{1,2})$ ]]; then
        hours="${BASH_REMATCH[1]}"
        minutes="${BASH_REMATCH[2]}"
        seconds=0
    elif [[ "${walltime}" =~ ^([0-9]+)$ ]]; then
        hours="${BASH_REMATCH[1]}"
        minutes=0
        seconds=0
    else
        printf 'Unparsable walltime: %s\n' "${walltime}" >&2
        return 2
    fi

    printf '%d\n' "$(( 10#${hours} * 3600 + 10#${minutes} * 60 + 10#${seconds} ))"
}

# seconds -> "H:MM:SS" (OAR accepts an hour field above 24).
pack_format_walltime() {
    local total="$1"

    printf '%d:%02d:%02d\n' \
        "$(( total / 3600 ))" "$(( total % 3600 / 60 ))" "$(( total % 60 ))"
}

# Walltime one packed job must ask for: the per-experiment budget multiplied by
# the sequential depth of the pack.
#
# The depth is computed with PACK_WALLTIME_PARALLEL, NOT with PACK_PARALLEL:
# concurrency is resolved inside the job from the card that OAR actually gives
# out, so the request has to be sized for the *weakest* card the job may land
# on. PACK_WALLTIME_PARALLEL=1 (the default) is the safe assumption "the card
# holds one training at a time"; raise it only when every card matched by
# GPU_PROPERTY is known to hold that many.
pack_job_walltime() {
    local pack_size="$1"
    local per_run_walltime="$2"
    local assumed_parallel="${3:-1}"
    local per_run_seconds depth

    (( assumed_parallel >= 1 )) || assumed_parallel=1
    per_run_seconds="$(pack_walltime_seconds "${per_run_walltime}")" || return 2
    depth=$(( (pack_size + assumed_parallel - 1) / assumed_parallel ))
    (( depth >= 1 )) || depth=1

    pack_format_walltime "$(( depth * per_run_seconds ))"
}

# Refuse to build a job the scheduler will reject. MAX_WALLTIME empty = no known
# cap (do not guess one); otherwise the requested walltime must fit under it.
#
# Failing here is deliberate: an oarsub rejected at drain time stops the whole
# drain (cluster_queue_remote.sh keeps the remaining commands pending and
# returns non-zero), so a walltime that cannot be granted is much cheaper to
# catch while the queue is still being built.
pack_check_walltime() {
    local requested="$1"
    local max_walltime="${2:-}"
    local requested_seconds max_seconds

    [[ -n "${max_walltime}" ]] || return 0

    requested_seconds="$(pack_walltime_seconds "${requested}")" || return 2
    max_seconds="$(pack_walltime_seconds "${max_walltime}")" || return 2

    if (( requested_seconds > max_seconds )); then
        printf 'Requested walltime %s exceeds this cluster'\''s limit %s.\n' \
            "${requested}" "${max_walltime}" >&2
        printf 'Lower PACK_SIZE, raise PACK_WALLTIME_PARALLEL, or shorten WALLTIME.\n' >&2
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Pack specification
# ---------------------------------------------------------------------------
#
# One experiment is one TAB-separated record:
#
#   header <TAB> log_file <TAB> out_base <TAB> python_args
#
#     header       banner printed before the run, e.g. "GROUP: GLTP | ..."
#     log_file     the tee'd script_logs/<...>.log path (unchanged from the
#                  one-experiment-per-job layout)
#     out_base     path prefix the runner completes with
#                  "${JOB_ID_TAG}${OAR_JOB_ID}.out" so that every experiment in
#                  the pack still owns an OAR-job-id-bearing .out file where
#                  lib/progress_table.sh expects to find it
#     python_args  everything after `python ./training/new_train.py`
#
# None of these fields can contain a TAB (they are paths and CLI flags). The
# whole spec is base64-encoded before it goes onto the oarsub command line, so
# it survives the submitter -> oarsub -> queue file -> login shell -> `bash -c`
# chain without a second layer of quoting to get wrong.

pack_record() {
    printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"
}

pack_spec_encode() {
    printf '%s' "$1" | base64 -w 0
}
