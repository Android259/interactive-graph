#!/usr/bin/env bash
set -euo pipefail

cd /home/kalinina/DL_project
mkdir -p script_logs/complete_missing_groups

groups=(
    "START"
    "lipocalin"
    "LBP_BPI_CETP"
    "scp2"
    "ML"
    "OSBP"
)

variants=(
    "nt_cw_lr1e3|0.001|--no_tanimoto_weight"
    "t_cw_lr1e3|0.001|--tanimoto_weight"
    "nt_nocw_lr1e3|0.001|--no_tanimoto_weight --no_class_weights"
    "t_nocw_lr1e3|0.001|--tanimoto_weight --no_class_weights"
    "nt_cw_lr3e4|0.0003|--no_tanimoto_weight"
    "t_cw_lr3e4|0.0003|--tanimoto_weight"
    "nt_cw_lr3e4_pb|0.0003|--no_tanimoto_weight --protein_pooling=attention_pos_bias"
)

for group in "${groups[@]}"; do
    mkdir -p "script_logs/complete_missing_groups/${group}"

    for specification in "${variants[@]}"; do
        IFS="|" read -r variant lr flags <<< "${specification}"
        read -r -a extra_flags <<< "${flags}"

        printf -v train_command \
            'gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"; case "${gpu_name}" in *A100*|*V100*) ;; *) printf "Unsupported GPU model: %%s\n" "${gpu_name}" >&2; exit 1 ;; esac; gpu_uuid="$(nvidia-smi --query-gpu=uuid --format=csv,noheader | head -n 1 | tr -cd "A-Za-z0-9_-")"; exec 9>"/tmp/dl-project-${gpu_uuid}.lock"; printf "Waiting for exclusive access to GPU %%s.\n" "${gpu_uuid}"; flock 9; while true; do free_gpu_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d " ")"; if [[ "${free_gpu_mib}" =~ ^[0-9]+$ ]] && (( free_gpu_mib >= 16384 )); then break; fi; printf "Waiting for GPU memory: free=%%s MiB, required=16384 MiB. Checking again in 60 seconds.\n" "${free_gpu_mib:-unknown}"; sleep 60; done; printf "=== MISSING GROUP | group: %%s | variant: %%s | GPU: %%s ===\n" %q %q "${gpu_name}"; PYTHONUNBUFFERED=1 python ./training/new_train.py --lipid_fragments_treatment=concat --plmon --buryon --protein_pooling=ordinary --loss_type=cross_entropy --pool_type=max --HEADS=8 --hiddim=64 --m=4 --lr=%q --weight_decay=0.0 --batch=16 --ep=150 --num_workers=4 --seed=0 --protein_self_attention --lipid_self_attention --cross_attention --excluded_groups=%q %s 2>&1 | tee %q' \
            "${group}" "${variant}" "${lr}" "${group}" \
            "$(printf ' %q' "${extra_flags[@]}")" \
            "/home/kalinina/DL_project/script_logs/complete_missing_groups/${group}/${variant}_seed0_ep150_batch16.log"

        printf -v job_command \
            'cd /home/kalinina/DL_project && source /home/kalinina/miniconda3/etc/profile.d/conda.sh && conda activate Kalinin_project_LP && bash -o pipefail -c %q' \
            "${train_command}"

        oarsub \
            --name "fill_${group}_${variant}" \
            -l "/nodes=1/gpu=1,walltime=4:00:00" \
            -p "(gpumodel='A100' OR gpumodel='V100')" \
            --project "pr-molgen" \
            -O "script_logs/complete_missing_groups/${group}/${variant}_%jobid%.out" \
            -E "script_logs/complete_missing_groups/${group}/${variant}_%jobid%.err" \
            "${job_command}"
    done
done

printf 'Submitted 42 jobs for missing groups.\n'
