#!/usr/bin/env bash
set -euo pipefail

# One command, run from your OWN machine (NOT the cluster -- this calls
# scripts/run_bigfoot.sh, which does the syncing/SSH/oarsub dance itself; it does
# not need oarsub installed locally). Submits stage 1, waits for bigfoot's queue
# to drain, confirms the checkpoint landed, then submits stage 2 with
# --summarize (which does its own wait-for-drain before writing the summary).
#
# Why not one remote script chaining everything with oarsub directly (like
# scripts/submit/structural_pretrain_solo.sh does for the original three arms):
# stage 2 here goes through the ordinary --family_only GRID (scripts/launch/
# submit_grid.sh, packed jobs across bigfoot's GPUs), not a single hand-rolled
# job -- there is no clean way to embed "wait for a packed multi-job grid" inside
# one oarsub command the way the original script embeds "run stage 2's for-loop
# after stage 1" inside one job's shell. Waiting for bigfoot's OAR queue to
# drain between the two run_bigfoot.sh calls (the same primitive run_cluster.sh's
# own --summarize/--graphics already use) gets the same ordering guarantee
# without a second submission mechanism.
#
#   bash scripts/submit/structural_pretrain_protunion14_full.sh
#
# Put it in the background yourself (nohup .../& , screen, tmux) if you want your
# shell back immediately; left in the foreground it blocks until both stages and
# the final summary are done -- stage 1 plus the 35-run stage-2 grid is
# realistically an hour-plus.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_DIR}"

export CLUSTER_NAME="${CLUSTER_NAME:-bigfoot}"
# shellcheck source=scripts/lib/cluster_common.sh
source scripts/lib/cluster_common.sh
# shellcheck source=scripts/lib/ssh_master_lib.sh
source scripts/lib/ssh_master_lib.sh
ensure_ssh_master

POLL_SECONDS="${POLL_SECONDS:-60}"

printf '=== Stage 1: submitting structural_pretrain_protunion14 ===\n'
# --summarize/--graphics are the only two things that make run_cluster.sh return
# once its own submission is done (scripts/launch/run_cluster.sh:612-726); a bare
# call like this one falls through to an UNCONDITIONAL, INDEFINITE hand-off to
# scripts/wait_and_sync.sh (line 728-746 there -- "Ctrl-C stops watching and
# nothing else"), which never exits on its own. Confirmed by running it: the
# submission itself (the two SSH round trips cluster_queue_remote.sh's capture/
# drain make) finishes in seconds, so a generous timeout here only ever fires
# AFTER submission has already happened, cutting off the watcher hand-off before
# it can block this script forever. Exit code 124 (timeout's own "killed on
# time") is the EXPECTED, successful outcome here, not a failure.
set +e
timeout 180 bash scripts/run_bigfoot.sh structural_pretrain_protunion14_solo
stage1_submit_status=$?
set -e
if [[ ${stage1_submit_status} -ne 0 && ${stage1_submit_status} -ne 124 ]]; then
    printf 'Stage 1 submission itself failed (exit %s, not the expected 124-from-timeout) -- see the output above.\n' \
        "${stage1_submit_status}" >&2
    exit "${stage1_submit_status}"
fi

printf 'Waiting for %s@%s'"'"'s OAR queue to drain before stage 2 (polling every %ss)...\n' \
    "${REMOTE_USER}" "${CLUSTER_NAME}" "${POLL_SECONDS}"
while :; do
    remaining="$(
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" |
            python3 scripts/lib/oarstat_json.py jobs 2>/dev/null | wc -l
    )"
    (( remaining == 0 )) && break
    sleep "${POLL_SECONDS}"
done
printf 'Queue drained.\n'

checkpoint_check="$(ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "test -f '${REMOTE_PROJECT}/models/structural_pretrain_protunion14/random/seed0.pt' && echo yes || echo no")"
if [[ "${checkpoint_check}" != "yes" ]]; then
    printf 'Stage 1 finished but models/structural_pretrain_protunion14/random/seed0.pt does not exist on %s -- it likely failed. Check script_logs/structural_pretrain_protunion14/ there before running stage 2 by hand. Not launching stage 2.\n' \
        "${CLUSTER_NAME}" >&2
    exit 1
fi
printf 'Checkpoint confirmed on %s. Proceeding to stage 2.\n' "${CLUSTER_NAME}"

printf '=== Stage 2: structural_pretrain_family_unfrozen_protunion14 (grid + summary) ===\n'
SKIP_AUC=1 bash scripts/run_bigfoot.sh --summarize --no_groups=ML,OSBP \
    structural_pretrain_family_unfrozen_protunion14
