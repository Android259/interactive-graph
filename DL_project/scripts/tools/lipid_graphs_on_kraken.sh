#!/usr/bin/env bash
# One-shot: rebuild every lipid isomer graph on kraken-cpu's 192-core node.
#
# Why not the usual launcher: scripts/launch/run_cluster.sh takes an arg-file and
# queues a TRAINING grid; this is data prep, which that machinery has no path for.
#
# Why the graphs are not shipped there: data/ is excluded from project sync
# (scripts/lib/cluster_sync_excludes.sh) apart from a whitelist, and rebuilding
# all 1319 on 190 cores is faster than transferring the ones already built.
set -euo pipefail

REMOTE=kraken-cpu
REMOTE_PROJECT=/home/kalinina/DL_project
SOCKET="${HOME}/.ssh/controlmasters/kraken-cpu"
JOBS="${JOBS:-190}"
WALLTIME="${WALLTIME:-1:00:00}"
INTERACTION_CSV="Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv"

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$(dirname "${SOCKET}")"

# One shared connection for every ssh/rsync below, so the password is asked once.
if ! ssh -S "${SOCKET}" -O check "${REMOTE}" 2>/dev/null; then
    echo "== opening ssh master to ${REMOTE} (password prompt expected once)"
    ssh -M -S "${SOCKET}" -o ControlPersist=8h -fN "${REMOTE}"
fi
SSH=(ssh -S "${SOCKET}")

echo "== syncing code and the interaction table"
rsync -az -e "ssh -S ${SOCKET}" \
    data/build_lipid_isomer_graphs.py "${REMOTE}:${REMOTE_PROJECT}/data/"
rsync -az -e "ssh -S ${SOCKET}" --exclude='__pycache__/' \
    dataloader/ "${REMOTE}:${REMOTE_PROJECT}/dataloader/"
rsync -az -e "ssh -S ${SOCKET}" \
    "data/${INTERACTION_CSV}" "${REMOTE}:${REMOTE_PROJECT}/data/"

echo "== installing the job script"
# OMP_NUM_THREADS=1 is load-bearing: without it each of the 190 workers lets
# RDKit/BLAS grab the whole node and they thrash instead of scaling.
"${SSH[@]}" "${REMOTE}" "cat > ${REMOTE_PROJECT}/run_lipid_graphs.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
source /home/kalinina/miniconda3/etc/profile.d/conda.sh
conda activate Kalinin_project_LP
cd ${REMOTE_PROJECT}
export OMP_NUM_THREADS=1
python data/build_lipid_isomer_graphs.py --jobs ${JOBS}
EOF
"${SSH[@]}" "${REMOTE}" "chmod +x ${REMOTE_PROJECT}/run_lipid_graphs.sh"

echo "== submitting"
"${SSH[@]}" "${REMOTE}" "cd ${REMOTE_PROJECT} && oarsub --project pr-molgen \
    -l /nodes=1,walltime=${WALLTIME} \
    -O lipid_graphs.%jobid%.out -E lipid_graphs.%jobid%.err \
    ${REMOTE_PROJECT}/run_lipid_graphs.sh"

echo
echo "== queued. follow with:"
echo "   ssh -S ${SOCKET} ${REMOTE} 'oarstat -u kalinina'"
echo "   ssh -S ${SOCKET} ${REMOTE} 'tail -20 ${REMOTE_PROJECT}/lipid_graphs.*.out'"
echo
echo "== when it finishes -- STOP the local build first, it writes the same dir:"
echo "   pkill -f build_lipid_isomer_graphs.py"
echo "   rsync -az -e 'ssh -S ${SOCKET}' --delete \\"
echo "       ${REMOTE}:${REMOTE_PROJECT}/data/lipid_graphs/ data/lipid_graphs/"
echo "   python data/build_lipid_graph_tensor_cache.py"
echo "   python data/build_pair_descriptor_cache.py"
