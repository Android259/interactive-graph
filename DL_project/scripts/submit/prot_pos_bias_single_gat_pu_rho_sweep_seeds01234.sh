#!/usr/bin/env bash
set -euo pipefail

cd /home/kalinina/DL_project
mkdir -p script_logs/prot_pos_bias_single_gat_pu_rho_sweep_seeds01234

submit_variant() {
    local group="$1"
    local seed="$2"
    local rho="$3"
    local variant="$4"
    local output_dir="script_logs/prot_pos_bias_single_gat_pu_rho_sweep_seeds01234/${group}"
    local log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= 16384 )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=16384 MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== GROUP: %%s | VARIANT: %%s | SEED: %%s | PU_RHO: %%s | GPU: %%s ===\n" %q %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon  --no_tanimoto_weight --no_class_weights --protein_class_weight --protein_pooling=attention_pos_bias --single_gat_layer --pu_loss --pu_rho=%q --pu_beta=0.0 --pu_gamma=1.0 --loss_type=cross_entropy --pool_type=max --HEADS=8 --hiddim=64 --m=4 --final_m=4 --final_dropout=0.0 --lr=0.0001 --weight_decay=0.00001 --batch=16 --ep=150 --num_workers=4 --seed=%q --protein_self_attention --lipid_self_attention --cross_attention --excluded_groups=%q 2>&1 | tee %q' \
        "${group}" "${variant}" "${seed}" "${rho}" \
        "${rho}" "${seed}" "${group}" "${log_file}"

    printf -v job_command \
        'cd /home/kalinina/DL_project && source /home/kalinina/miniconda3/etc/profile.d/conda.sh && conda activate Kalinin_project_LP && bash -o pipefail -c %q' \
        "${train_command}"

    oarsub \
        --name "pu_rho_${group}_${variant}_s${seed}" \
        -l "/nodes=1/gpu=1,walltime=4:00:00" \
        -p "(gpumodel='A100' OR gpumodel='V100')" \
        --project "pr-molgen" \
        -O "${output_dir}/${variant}_seed${seed}_%jobid%.out" \
        -E "${output_dir}/${variant}_seed${seed}_%jobid%.err" \
        "${job_command}"
}

groups=(
    "CRAL-TRIO"
    "GLTP"
    "IP_trans"
    "LBP_BPI_CETP"
    "ML"
    "OSBP"
    "START"
    "lipocalin"
    "scp2"
)

seeds=(0 1 2 3 4)

variants=(
    "pu_rho010|0.10"
    "pu_rho020|0.20"
    "pu_rho030|0.30"
)

for group in "${groups[@]}"; do
    for seed in "${seeds[@]}"; do
        for specification in "${variants[@]}"; do
            IFS="|" read -r variant rho <<< "${specification}"
            submit_variant "${group}" "${seed}" "${rho}" "${variant}"
        done
    done
done

printf 'Submitted 135 single-GAT PU rho sweep jobs: 9 groups x 5 seeds x 3 rho levels.\n'
