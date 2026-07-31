#!/usr/bin/env bash
# Generate the full standard graphics set for one configuration, selected by
# its `label` value in metrics_summary.csv.
#
# Usage: bash scripts/generate_config_graphics.sh LABEL
#
# The expected seed set is the union of seeds that have a completed run for the
# label. Learning curves are produced one excluded group at a time, but only
# for groups that have a completed run for every expected seed; groups missing
# one or more seeds are skipped with a note instead of aborting the whole run.
#
# Produces, under graphics/<label>/:
#   learning_curves/<group>/<metric>.pdf   for every complete group and metric
#   subgroups/<label>_<metric>_by_subgroup.pdf   for every subgroup metric
#
# Learning-curve metrics: balanced_accuracy, F1, sensitivity, specificity, precision, loss
# Subgroup metrics:       balanced_accuracy, F1, sensitivity, specificity, precision

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TABLE="${TABLE:-${PROJECT_ROOT}/metrics_summary.csv}"
export PYTHONPATH="${PROJECT_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

if (( $# != 1 )); then
    printf 'Usage: %s LABEL\n' "${0##*/}" >&2
    exit 2
fi

LABEL="$1"
OUTPUT_DIR="${PROJECT_ROOT}/graphics/${LABEL}"
CURVE_METRICS=(balanced_accuracy F1 sensitivity specificity precision loss)
SUBGROUP_METRICS=(balanced_accuracy F1 sensitivity specificity precision)

cd "${PROJECT_ROOT}"

list_dim() {
    python3 "${SCRIPT_DIR}/_list_label_dimension.py" "${TABLE}" "${LABEL}" "$@"
}

expected_list="$(list_dim seed run_status=complete)"
mapfile -t EXPECTED_SEEDS < <(printf '%s' "${expected_list}")
mapfile -t COMPLETE_GROUPS < <(list_dim exclusion_set run_status=complete)

if (( ${#EXPECTED_SEEDS[@]} == 0 )) || (( ${#COMPLETE_GROUPS[@]} == 0 )); then
    printf 'No completed runs found with label=%s in %s\n' "${LABEL}" "${TABLE}" >&2
    exit 1
fi

printf 'Configuration: %s\n' "${LABEL}"
printf 'Expected seeds (%d): %s\n' "${#EXPECTED_SEEDS[@]}" "${EXPECTED_SEEDS[*]}"
printf 'Groups with completed runs (%d): %s\n' \
    "${#COMPLETE_GROUPS[@]}" "${COMPLETE_GROUPS[*]}"

mkdir -p "${OUTPUT_DIR}/learning_curves" "${OUTPUT_DIR}/subgroups"

seed_args=()
for seed in "${EXPECTED_SEEDS[@]}"; do
    seed_args+=(--seed "${seed}")
done

metric_args=()
for metric in "${CURVE_METRICS[@]}"; do
    metric_args+=(--metric "${metric}")
done

# --- Learning curves: only for groups complete across every expected seed. ---
PLOTTED_GROUPS=()
SKIPPED_GROUPS=()
for group in "${COMPLETE_GROUPS[@]}"; do
    group_list="$(list_dim seed "exclusion_set=${group}" run_status=complete)"
    if [[ "${group_list}" != "${expected_list}" ]]; then
        missing="$(
            LC_ALL=C comm -23 \
                <(printf '%s\n' "${expected_list}" | LC_ALL=C sort) \
                <(printf '%s\n' "${group_list}" | LC_ALL=C sort) | paste -sd, -
        )"
        printf 'Skipping learning curves for %s: missing seed(s) %s\n' \
            "${group}" "${missing}" >&2
        SKIPPED_GROUPS+=("${group}")
        continue
    fi
    printf '\n== learning curves: %s ==\n' "${group}"
    python3 "${PROJECT_ROOT}/analysis/plot_group_learning_curve.py" \
        --table "${TABLE}" \
        --group "${group}" \
        "${metric_args[@]}" \
        --filter "label=${LABEL}" \
        "${seed_args[@]}" \
        --output-dir "${OUTPUT_DIR}/learning_curves"
    PLOTTED_GROUPS+=("${group}")
done

# --- Subgroup bar charts: aggregate over whatever completed reports exist. ---
for metric in "${SUBGROUP_METRICS[@]}"; do
    printf '\n== subgroup metric: %s ==\n' "${metric}"
    python3 "${PROJECT_ROOT}/analysis/plot_metric_by_subgroup.py" \
        --reports-root test_metrics \
        --metric "${metric}" \
        --filter "label=${LABEL}" \
        --title "${LABEL} ${metric} by subgroup" \
        --output "${OUTPUT_DIR}/subgroups/${LABEL}_${metric}_by_subgroup.pdf"
done

printf '\nDone. Graphics written under %s\n' "${OUTPUT_DIR}"
printf 'Learning curves plotted for %d group(s): %s\n' \
    "${#PLOTTED_GROUPS[@]}" "${PLOTTED_GROUPS[*]:-none}"
if (( ${#SKIPPED_GROUPS[@]} > 0 )); then
    printf 'Learning curves skipped for %d group(s) missing seeds: %s\n' \
        "${#SKIPPED_GROUPS[@]}" "${SKIPPED_GROUPS[*]}"
fi
