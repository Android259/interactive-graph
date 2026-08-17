#!/usr/bin/env bash
# Which (group, seed) pairs a launcher should actually run.
#
# `source` this file; it defines functions only.
#
# All three launchers -- run_local.sh and the two OAR submitters -- build the
# same grid and skip the same already-finished pairs. That step lives here once,
# so "--complete" means the same thing on this machine and on either cluster.

_GRID_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The (group, seed) pairs that already have a final test report, as "group:seed"
# lines.
#
#   $1  variant (the run label)
#   $2  reports root, or empty for list_completed_experiments.py's own default
#   $3  1 for a cold-split series, 0 otherwise
grid_completed_list() {
    local variant="$1" reports_root="${2:-}" cold="${3:-0}"
    local -a args=("${variant}")

    if [[ -n "${reports_root}" ]]; then
        args+=(--reports-root "${reports_root}")
    fi
    if [[ "${cold}" == "1" ]]; then
        args+=(--cold-split)
    fi
    python3 "${_GRID_LIB_DIR}/list_completed_experiments.py" "${args[@]}"
}

# Fills the COMPLETED_PAIRS map, from two sources that are both optional:
#
#   COMPLETED_EXPERIMENTS in the environment -- pairs worked out on ANOTHER
#     machine and carried across. run_cluster.sh fills it by scanning the local
#     test_metrics tree, because the cluster's copy does not have it: the project
#     sync sends code only.
#   a fresh scan of the reports tree on the machine this runs on.
#
# Does nothing at all unless COMPLETE_ONLY is 1, so a launcher can call it
# unconditionally.
grid_load_completed() {
    local variant="$1" reports_root="${2:-}" cold="${3:-0}"
    local pair

    declare -gA COMPLETED_PAIRS=()
    [[ "${COMPLETE_ONLY:-0}" == "1" ]] || return 0

    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && COMPLETED_PAIRS["${pair}"]=1
    done <<< "${COMPLETED_EXPERIMENTS:-}"

    while IFS= read -r pair; do
        [[ -n "${pair}" ]] && COMPLETED_PAIRS["${pair}"]=1
    done < <(grid_completed_list "${variant}" "${reports_root}" "${cold}")

    return 0
}

grid_is_completed() {
    [[ "${COMPLETE_ONLY:-0}" == "1" && -n "${COMPLETED_PAIRS["$1:$2"]:-}" ]]
}

# "group<TAB>seed" for every pair that still needs running, seed innermost.
#
# The seed loop stays innermost because that is what packing assumes: a pack of 5
# is exactly one group's seeds and a pack of 9 spans groups at a fixed seed, both
# natural units to resubmit or cancel as a whole.
#
# Skipped pairs are announced on stderr, so a caller can read the pairs off
# stdout without filtering.
grid_pairs() {
    local groups="$1" seeds="$2" group seed
    for group in ${groups}; do
        for seed in ${seeds}; do
            if grid_is_completed "${group}" "${seed}"; then
                printf 'Skipping completed experiment: group=%s seed=%s.\n' \
                    "${group}" "${seed}" >&2
                continue
            fi
            printf '%s\t%s\n' "${group}" "${seed}"
        done
    done
}
