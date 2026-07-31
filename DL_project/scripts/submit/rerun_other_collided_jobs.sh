#!/usr/bin/env bash
set -euo pipefail

cd /home/kalinina/DL_project
mkdir -p script_logs/rerun_other_collided_jobs

submit_variant() {
    local group="$1"
    local variant="$2"
    local lr="$3"
    shift 3
    local extra_flags=("$@")
    local output_dir="script_logs/rerun_other_collided_jobs/${group}"
    local log_file="${output_dir}/${variant}_seed0_ep150_batch16.log"
    local train_command
    local job_command

    mkdir -p "${output_dir}"

    printf -v train_command \
        'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= 16384 )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=16384 MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== RERUN | GROUP: %%s | VARIANT: %%s | LR: %%s | GPU: %%s ===\n" %q %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon --protein_pooling=ordinary --loss_type=cross_entropy --pool_type=max --HEADS=8 --hiddim=64 --m=4 --weight_decay=0.0 --batch=16 --ep=150 --num_workers=4 --seed=0 --protein_self_attention --lipid_self_attention --cross_attention --lr=%q --excluded_groups=%q %s 2>&1 | tee %q' \
        "${group}" "${variant}" "${lr}" "${lr}" "${group}" \
        "$(printf ' %q' "${extra_flags[@]}")" "${log_file}"

    printf -v job_command \
        'cd /home/kalinina/DL_project && source /home/kalinina/miniconda3/etc/profile.d/conda.sh && conda activate Kalinin_project_LP && bash -o pipefail -c %q' \
        "${train_command}"

    oarsub \
        --name "othercol_${group}_${variant}" \
        -l "/nodes=1/gpu=1,walltime=10:00:00" \
        -p "(gpumodel='A100' OR gpumodel='V100')" \
        --project "pr-molgen" \
        -O "${output_dir}/${variant}_%jobid%.out" \
        -E "${output_dir}/${variant}_%jobid%.err" \
        "${job_command}"
}

jobs=(
    "CRAL-TRIO|nt_cw_lr3e4|0.0003|--no_tanimoto_weight"
    "CRAL-TRIO|t_cw_lr3e4|0.0003|--tanimoto_weight"
    "GLTP|nt_nocw_lr1e3|0.001|--no_tanimoto_weight --no_class_weights"
    "GLTP|nt_cw_lr1e3|0.001|--no_tanimoto_weight"
    "GLTP|t_cw_lr1e3|0.001|--tanimoto_weight"
)

for specification in "${jobs[@]}"; do
    IFS="|" read -r group variant lr flags <<< "${specification}"
    read -r -a extra_flags <<< "${flags}"
    submit_variant "${group}" "${variant}" "${lr}" "${extra_flags[@]}"
done

printf 'Submitted 5 reruns for non-weight-decay collided jobs.\n'
