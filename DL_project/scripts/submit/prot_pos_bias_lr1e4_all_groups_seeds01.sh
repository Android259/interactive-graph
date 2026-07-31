#!/usr/bin/env bash
set -euo pipefail

cd /home/kalinina/DL_project
mkdir -p script_logs/prot_pos_bias_lr1e4_all_groups_seeds01

submit_variant() {
    local group="$1"
    local seed="$2"
    local variant="$3"
    local lr="$4"
    shift 4
    local extra_flags=("$@")
    local output_dir="script_logs/prot_pos_bias_lr1e4_all_groups_seeds01/${group}"
    local log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= 16384 )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=16384 MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== GROUP: %%s | VARIANT: %%s | SEED: %%s | GPU: %%s ===\n" %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon --protein_pooling=ordinary --loss_type=cross_entropy --pool_type=max --HEADS=8 --hiddim=64 --m=4 --weight_decay=0.0 --batch=16 --ep=150 --num_workers=4 --seed=%q --protein_self_attention --lipid_self_attention --cross_attention --lr=%q --excluded_groups=%q %s 2>&1 | tee %q' \
        "${group}" "${variant}" "${seed}" "${seed}" "${lr}" "${group}" \
        "$(printf ' %q' "${extra_flags[@]}")" "${log_file}"

    printf -v job_command \
        'cd /home/kalinina/DL_project && source /home/kalinina/miniconda3/etc/profile.d/conda.sh && conda activate Kalinin_project_LP && bash -o pipefail -c %q' \
        "${train_command}"

    oarsub \
        --name "pb1e4_${group}_s${seed}" \
        -l "/nodes=1/gpu=1,walltime=10:00:00" \
        -p "(gpumodel='A100' OR gpumodel='V100')" \
        --project "pr-molgen" \
        -O "${output_dir}/${variant}_seed${seed}_%jobid%.out" \
        -E "${output_dir}/${variant}_seed${seed}_%jobid%.err" \
        "${job_command}"
}

groups=(
    "CRAL-TRIO"
    "START"
    "lipocalin"
    "GLTP"
    "IP_trans"
    "LBP_BPI_CETP"
    "scp2"
    "ML"
    "OSBP"
)

seeds=(0 1)

variants=(
    "nt_cw_lr1e4_pb_typeopt0|0.0001|--no_tanimoto_weight --protein_pooling=attention_pos_bias"
)

for group in "${groups[@]}"; do
    for seed in "${seeds[@]}"; do
        for specification in "${variants[@]}"; do
            IFS="|" read -r variant lr flags <<< "${specification}"
            read -r -a extra_flags <<< "${flags}"
            submit_variant \
                "${group}" "${seed}" "${variant}" "${lr}" \
                "${extra_flags[@]}"
        done
    done
done

printf 'Submitted 18 jobs for protPosBias type_opt=0, lr=1e-4, seeds 0/1 across all groups.\n'
