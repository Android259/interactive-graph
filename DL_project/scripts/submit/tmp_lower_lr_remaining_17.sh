#!/usr/bin/env bash
set -euo pipefail

cd /home/kalinina/DL_project
mkdir -p script_logs/prot_pos_bias_lower_lr_complete_seeds0123

submit_variant() {
    local group="$1"
    local seed="$2"
    local variant="$3"
    local lr="$4"
    local output_dir="script_logs/prot_pos_bias_lower_lr_complete_seeds0123/${group}"
    local log_file="${output_dir}/${variant}_seed${seed}_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= 16384 )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=16384 MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== GROUP: %%s | VARIANT: %%s | SEED: %%s | LR: %%s | WEIGHT_DECAY: 0 | GPU: %%s ===\n" %q %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon  --no_tanimoto_weight --protein_pooling=attention_pos_bias --loss_type=cross_entropy --pool_type=max --HEADS=8 --hiddim=64 --m=4 --final_m=4 --final_dropout=0.0 --weight_decay=0.0 --batch=16 --ep=150 --num_workers=4 --seed=%q --protein_self_attention --lipid_self_attention --cross_attention --lr=%q --excluded_groups=%q 2>&1 | tee %q' \
        "${group}" "${variant}" "${seed}" "${lr}" \
        "${seed}" "${lr}" "${group}" "${log_file}"

    printf -v job_command \
        'cd /home/kalinina/DL_project && source /home/kalinina/miniconda3/etc/profile.d/conda.sh && conda activate Kalinin_project_LP && bash -o pipefail -c %q' \
        "${train_command}"

    oarsub \
        --name "pblrc_${group}_${variant}_s${seed}" \
        -l "/nodes=1/gpu=1,walltime=10:00:00" \
        -p "(gpumodel='A100' OR gpumodel='V100')" \
        --project "pr-molgen" \
        -O "${output_dir}/${variant}_seed${seed}_%jobid%.out" \
        -E "${output_dir}/${variant}_seed${seed}_%jobid%.err" \
        "${job_command}"
}

jobs=(
    "IP_trans|3|lr3e5|0.00003"
    "LBP_BPI_CETP|2|lr7e5|0.00007"
    "LBP_BPI_CETP|2|lr3e5|0.00003"
    "LBP_BPI_CETP|3|lr7e5|0.00007"
    "LBP_BPI_CETP|3|lr3e5|0.00003"
    "scp2|2|lr7e5|0.00007"
    "scp2|2|lr3e5|0.00003"
    "scp2|3|lr7e5|0.00007"
    "scp2|3|lr3e5|0.00003"
    "ML|2|lr7e5|0.00007"
    "ML|2|lr3e5|0.00003"
    "ML|3|lr7e5|0.00007"
    "ML|3|lr3e5|0.00003"
    "OSBP|2|lr7e5|0.00007"
    "OSBP|2|lr3e5|0.00003"
    "OSBP|3|lr7e5|0.00007"
    "OSBP|3|lr3e5|0.00003"
)

for specification in "${jobs[@]}"; do
    IFS="|" read -r group seed variant lr <<< "${specification}"
    submit_variant "${group}" "${seed}" "${variant}" "${lr}"
done

printf 'Submitted the 17 lower-LR jobs rejected by the previous queue-limit failure.\n'
