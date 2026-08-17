#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

EP="${EP:-10}"
BATCH="${BATCH:-16}"
NUM_WORKERS="${NUM_WORKERS:-0}"
SUBGROUPS="${SUBGROUPS:-RLBP1,GLTPD1}"
SEEDS="${SEEDS:-0}"

SAFE_SUBGROUPS="${SUBGROUPS//,/-}"
excluded_set_name="subgroups_${SAFE_SUBGROUPS}"

run_variant() {
    local name="$1"
    shift

    for seed in $SEEDS; do
        local log_dir="${LOG_ROOT:-script_logs}/${name}/${excluded_set_name}"
        mkdir -p "$log_dir"
        local log_file="${log_dir}/seed${seed}_ep${EP}_batch${BATCH}.log"
        echo "=== excluded subgroups ${SUBGROUPS} | ${name} | seed ${seed} ==="
        ./training/new_train.py \
            --ep="${EP}" \
            --batch="${BATCH}" \
            --seed="${seed}" \
            --num_workers="${NUM_WORKERS}" \
            --excluded_subgroups="${SUBGROUPS}" \
            "$@" 2>&1 | tee "$log_file"
    done
}

run_variant "protSA_lipSA_CA_pockets_tanimoto_protein_group_weight" \
    --protein_group_weight \
    --protein_self_attention \
    --lipid_self_attention \
    --cross_attention \
    --prot_attention_pos_bias
run_variant "protSA_lipSA_CA_tanimoto_protein_group_weight" \
    --protein_group_weight \
    --protein_self_attention \
    --lipid_self_attention \
    --cross_attention
run_variant "protSA_lipSA_CA_pockets_no_weights" \
    --no_tanimoto_weight \
    --protein_self_attention \
    --lipid_self_attention \
    --cross_attention \
    --prot_attention_pos_bias
run_variant "protSA_lipSA_CA_no_weights" \
    --no_tanimoto_weight \
    --protein_self_attention \
    --lipid_self_attention \
    --cross_attention
