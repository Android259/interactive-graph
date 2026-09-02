#!/usr/bin/env bash
# Sync this project to a cluster, queue its OAR jobs, and hand off to the
# wait/sync loop. Cluster-generic: entered through scripts/run_bigfoot.sh or
# scripts/run_kraken.sh, which set CLUSTER_NAME.
#
# Takes an scripts/arg_files/*.md config (handed to launch/submit_grid.sh, which
# reads the series off the config) or, for the archived one-off runs, a submitter
# under scripts/submit/.
#
# Cluster differences (GPU model, walltime, OAR project, conda paths) are passed
# to the submitter as environment variables -- never by patching its text.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=scripts/lib/cluster_common.sh
source "${PROJECT_ROOT}/scripts/lib/cluster_common.sh"

# shellcheck source=scripts/lib/cluster_sync_excludes.sh
source "${PROJECT_ROOT}/scripts/lib/cluster_sync_excludes.sh"

# shellcheck source=scripts/settings.sh
source "${PROJECT_ROOT}/scripts/settings.sh"

# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_ROOT}/scripts/lib/args_file_lib.sh"

# shellcheck source=scripts/lib/grid_lib.sh
source "${PROJECT_ROOT}/scripts/lib/grid_lib.sh"

# shellcheck source=scripts/lib/ssh_master_lib.sh
source "${PROJECT_ROOT}/scripts/lib/ssh_master_lib.sh"

SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-0}"
DO_GRAPHICS="${DO_GRAPHICS:-0}"
DO_SUMMARIZE="${DO_SUMMARIZE:-0}"

usage() {
    printf 'Usage: bash %s [--complete] [--graphics] [--summarize] [--seeds=LIST] [--groups=LIST] [--no_groups=LIST] SUBMIT_SCRIPT_OR_ARGS_FILE [SUBMIT_SCRIPT_OR_ARGS_FILE ...]\n' "${0##*/}" >&2
    printf 'Example: bash %s common_attention_all_groups\n' "${0##*/}" >&2
    printf 'Example: bash %s scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --seeds=0,1,2 scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --no_groups=GLTP scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --graphics --summarize scripts/arg_files/nps3mlp_gat_residual.md\n' "${0##*/}" >&2
    printf 'Example: bash %s --graphics --summarize labelA labelB labelC\n' "${0##*/}" >&2
    printf '                 Queues every label'"'"'s whole grid together (one shared OAR\n' >&2
    printf '                 queue/drain), so they run concurrently across whatever this\n' >&2
    printf '                 cluster'"'"'s slots allow -- kraken-cpu, one 192-core node per\n' >&2
    printf '                 job, is the case this is for. --graphics/--summarize wait for\n' >&2
    printf '                 the whole batch to drain once, then write one report PER label\n' >&2
    printf '                 under graphics/<label>/ -- args-file labels only, not a\n' >&2
    printf '                 scripts/submit/*.sh script (which names no single label).\n' >&2
    printf '\n' >&2
    printf '  --seeds=LIST     Comma-separated seeds to run every excluded group on.\n' >&2
    printf '                   --seeds=0,1,2 runs all 9 groups on seeds 0, 1 and 2\n' >&2
    printf '                   (27 jobs); --seeds=0 runs 9 jobs. Default: 0,1,2,3,4.\n' >&2
    printf '  --groups=LIST    Comma-separated excluded groups. Default: the 9\n' >&2
    printf '                   canonical groups. On a cold-split config these are\n' >&2
    printf '                   the TEST groups the rotation covers.\n' >&2
    printf '  --no_groups=LIST Drop these groups from the list above, so leaving one\n' >&2
    printf '                   group out of a full run does not mean spelling out\n' >&2
    printf '                   the other 8.\n' >&2
    printf '  --complete       Submit only group/seed pairs without final test_metrics.\n' >&2
    printf '  --graphics       After every submitted OAR job on this cluster drains,\n' >&2
    printf '                   sync once more and run scripts/generate_config_graphics.sh\n' >&2
    printf '                   for this label, quietly (its own narration goes to\n' >&2
    printf '                   graphics/<label>/generate_graphics.log, not the terminal).\n' >&2
    printf '                   Exits instead of handing off to the indefinite watcher.\n' >&2
    printf '  --summarize      Same wait, then writes graphics/<label>/<label>.md from\n' >&2
    printf '                   analysis/summarize_label.py and analysis/full_label_report.py\n' >&2
    printf '                   (AUC vs the chemistry null model, in-sample increment --\n' >&2
    printf '                   empty for a label with no saved checkpoints). Combines\n' >&2
    printf '                   with --graphics; either alone still waits and exits.\n' >&2
}

# Pull option flags off the argument list; exactly one positional (the submitter
# or args file) must remain. --seeds sets SEEDS_OVERRIDE, which cluster_common.sh
# forwards to the submitter (a space-separated seed list).
POSITIONALS=()
while (( $# > 0 )); do
    case "$1" in
        --complete)
            COMPLETE_ONLY=1
            shift
            ;;
        --graphics)
            DO_GRAPHICS=1
            shift
            ;;
        --summarize)
            DO_SUMMARIZE=1
            shift
            ;;
        --seeds=*)
            SEEDS_ARG="${1#*=}"
            shift
            ;;
        --seeds)
            if (( $# < 2 )); then
                printf '%s requires an argument.\n' "$1" >&2
                usage
                exit 2
            fi
            SEEDS_ARG="$2"
            shift 2
            ;;
        --groups=*)
            GROUPS_ARG="${1#*=}"
            shift
            ;;
        --groups)
            if (( $# < 2 )); then
                printf '%s requires an argument.\n' "$1" >&2
                usage
                exit 2
            fi
            GROUPS_ARG="$2"
            shift 2
            ;;
        --no_groups=*)
            SKIP_GROUPS_ARG="${1#*=}"
            shift
            ;;
        --no_groups)
            if (( $# < 2 )); then
                printf '%s requires an argument.\n' "$1" >&2
                usage
                exit 2
            fi
            SKIP_GROUPS_ARG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            while (( $# > 0 )); do POSITIONALS+=("$1"); shift; done
            ;;
        -*)
            printf 'Unknown option: %s\n' "$1" >&2
            usage
            exit 2
            ;;
        *)
            POSITIONALS+=("$1")
            shift
            ;;
    esac
done

if [[ -n "${SEEDS_ARG:-}" ]]; then
    # Accept commas or whitespace between seeds; store space-separated.
    read -r -a _seed_list <<< "${SEEDS_ARG//,/ }"
    if (( ${#_seed_list[@]} == 0 )); then
        printf 'No seeds given to --seeds.\n' >&2
        exit 2
    fi
    for _seed in "${_seed_list[@]}"; do
        if [[ ! "${_seed}" =~ ^[0-9]+$ ]]; then
            printf 'Invalid seed (must be a non-negative integer): %s\n' "${_seed}" >&2
            exit 2
        fi
    done
    export SEEDS_OVERRIDE="${_seed_list[*]}"
fi

# --groups / --no_groups, with the same spellings and the same complement rule as
# scripts/run_local.sh, so the flag means the same thing on this machine and on a
# cluster. Both end up in GROUPS_OVERRIDE (space separated), which
# cluster_remote_env forwards to the submitter -- for a cold-split config that
# list is the TEST rotation.
if [[ -n "${GROUPS_ARG:-}" || -n "${SKIP_GROUPS_ARG:-}" ]]; then
    _groups=("${PROTEIN_GROUPS[@]}")
    if [[ -n "${GROUPS_ARG:-}" ]]; then
        read -r -a _groups <<< "${GROUPS_ARG//,/ }"
        if (( ${#_groups[@]} == 0 )); then
            printf 'No groups given to --groups.\n' >&2
            exit 2
        fi
    fi

    if [[ -n "${SKIP_GROUPS_ARG:-}" ]]; then
        read -r -a _skip_groups <<< "${SKIP_GROUPS_ARG//,/ }"
        declare -A _skip_matched=()
        _kept_groups=()
        for _group in "${_groups[@]}"; do
            _keep=1
            for _skipped in "${_skip_groups[@]}"; do
                if [[ "$(normalize_group_name "${_group}")" \
                      == "$(normalize_group_name "${_skipped}")" ]]; then
                    _keep=0
                    _skip_matched["$(normalize_group_name "${_skipped}")"]=1
                fi
            done
            if (( _keep == 1 )); then
                _kept_groups+=("${_group}")
            fi
        done
        # A name that matches nothing is an error, not a silent no-op: the whole
        # point of the flag is NOT running a group, so a typo would quietly
        # submit the very group the caller meant to leave out.
        for _skipped in "${_skip_groups[@]}"; do
            if [[ -z "${_skip_matched["$(normalize_group_name "${_skipped}")"]:-}" ]]; then
                printf -- '--no_groups names a group that is not being run: %s\n' "${_skipped}" >&2
                printf 'Groups in this run: %s\n' "${_groups[*]}" >&2
                exit 2
            fi
        done
        if (( ${#_kept_groups[@]} == 0 )); then
            printf -- '--no_groups excluded every group; nothing left to run.\n' >&2
            exit 2
        fi
        _groups=("${_kept_groups[@]}")
    fi

    export GROUPS_OVERRIDE="${_groups[*]}"
fi

if (( ${#POSITIONALS[@]} < 1 )); then
    usage
    exit 2
fi

# capture (below) queues every requested label's whole grid into the SAME
# shared pending-jobs file regardless of count, and drain_queue (scripts/
# cluster/cluster_queue_remote.sh) already submits only as many as
# MAX_WAITING_JOBS allows, leaving the rest queued for the next drain --
# including the frontend's own cron-drain (project memory
# [[cluster-cron-drain]]) -- so "more labels than fit right now" already means
# "the rest go out as a later request" with no change needed here.
#
# --graphics/--summarize wait for the WHOLE oar queue for this user on this
# cluster to drain (existing behaviour, not new -- see the wait loop below),
# which was already label-agnostic; what is new is looping the per-label
# report generation itself over every args-file label requested, collected
# into VARIANTS as the label-resolution loop below runs.
VARIANTS=()

if ! command -v rsync >/dev/null 2>&1; then
    if [[ -f "${LOCAL_CONDA_SH}" ]]; then
        # shellcheck disable=SC1090
        source "${LOCAL_CONDA_SH}"
        conda activate "${LOCAL_CONDA_ENV}"
    fi
fi

if ! command -v rsync >/dev/null 2>&1; then
    printf 'rsync is not available. Tried local conda env: %s\n' \
        "${LOCAL_CONDA_ENV}" >&2
    exit 127
fi

if ! ensure_ssh_master 1; then
    printf 'Could not connect to %s.\n' "${remote}" >&2
    exit 1
fi

printf 'Synchronizing local project to %s:%s.\n' "${remote}" "${REMOTE_PROJECT}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" "mkdir -p '${REMOTE_PROJECT}'"
# Exactly the same file set and rules as scripts/tools/sync_project.sh, from the
# shared scripts/lib/cluster_sync_excludes.sh: code only, and the cluster copy is
# mirrored (stale files removed). SYNC_PROTECT keeps data/, results, logs, the
# metrics tables and BOTH clusters' OAR queues from being deleted -- the queues
# live only on the remote side, so a sync from the other cluster's runner must
# not wipe a live pending queue.
rsync -a --delete --delete-excluded --quiet --timeout=300 \
    -e "ssh -S ${SSH_CONTROL_PATH} -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o TCPKeepAlive=yes" \
    "${SYNC_PROTECT[@]}" \
    "${SYNC_EXCLUDES[@]}" \
    "${PROJECT_ROOT}/" \
    "${remote}:${REMOTE_PROJECT}/"

# Preflight runs after the sync (it inspects the synced tree) and before any
# remote state is created, so a failure leaves nothing behind to clean up.
if [[ "${SKIP_PREFLIGHT}" != "1" ]]; then
    printf 'Running preflight checks on %s.\n' "${remote}"
    preflight_required_arch=""
    case "${CLUSTER_NAME}" in
        kraken) preflight_required_arch="sm_90" ;;   # H100 / H200
    esac

    preflight_output=""
    if ! preflight_output="$(
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
            "cd '${REMOTE_PROJECT}' && CONDA_ENV=$(printf '%q' "${CONDA_ENV}") CONDA_SH=$(printf '%q' "${CONDA_SH}") REQUIRED_ARCH=$(printf '%q' "${preflight_required_arch}") bash scripts/cluster/cluster_preflight_remote.sh"
    )"; then
        printf 'Preflight failed on %s; not submitting anything.\n' "${remote}" >&2
        printf '%s\n' "${preflight_output}" >&2
        exit 3
    fi
    printf '%s\n' "${preflight_output}" | sed 's/^/  /'

    # Adopt what preflight resolved, unless the caller pinned it explicitly.
    preflight_value() {
        printf '%s\n' "${preflight_output}" | sed -n "s/^$1=//p" | head -n 1
    }
    if [[ -z "${CONDA_SH_PINNED:-}" ]]; then
        discovered_conda_sh="$(preflight_value CONDA_SH)"
        [[ -n "${discovered_conda_sh}" ]] && CONDA_SH="${discovered_conda_sh}"
    fi
    if [[ -z "${PROJECT_PINNED:-}" && -z "${PROJECT}" ]]; then
        discovered_projects="$(preflight_value PROJECTS)"
        if [[ "${discovered_projects}" == *,* ]]; then
            printf 'Several OAR projects available (%s). Re-run with PROJECT=<name>.\n' \
                "${discovered_projects}" >&2
            exit 3
        elif [[ -n "${discovered_projects}" ]]; then
            PROJECT="${discovered_projects}"
            printf 'Using OAR project: %s\n' "${PROJECT}"
        fi
    fi
fi

SESSION_MARKER="${CLUSTER_SESSION_PREFIX}$(date +%Y%m%d_%H%M%S)_$$"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" "touch '${SESSION_MARKER}'"

REMOTE_QUEUE_DIR="${CLUSTER_QUEUE_ROOT}/active"

# The cluster settings are %q-escaped exactly once (see cluster_remote_env) and
# then interpreted once by the remote login shell. GPU_PROPERTY carries single
# quotes and parentheses, so this must not be quoted by hand. Label-independent,
# computed once rather than once per label in the loop below.
remote_env="$(cluster_remote_env)"

# GRICAD kills anything using >600s CPU on a frontend/login node (own
# monitoring, not OAR) -- see e.g. the kraken warning for a
# build_pair_descriptor_cache.py run that hit 351s there. The two prep builds
# below used to run as a plain `ssh ... python3 ...` on the login node, which
# is exactly what that policy forbids once a cache build is not a no-op (a
# stale/missing cache on a big args-file can run past the limit and get
# killed mid-build). This submits the same command as a small OAR job instead
# and blocks until it drains, so the caches are still ready before the real
# grid below queues -- see that loop's own comment for why "before" matters.
PREP_JOB_CORES="${PREP_JOB_CORES:-2}"
PREP_JOB_WALLTIME="${PREP_JOB_WALLTIME:-1:00:00}"

run_prep_job() {
    local job_label="$1" job_cmd="$2"
    local job_name="${job_label}_$$"
    local job_dir="${REMOTE_PROJECT}/.prep_jobs"
    local script_path="${job_dir}/${job_name}.sh"
    local out_path="${job_dir}/${job_name}.out"
    local err_path="${job_dir}/${job_name}.err"
    local exit_path="${job_dir}/${job_name}.exit"

    ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "mkdir -p '${job_dir}' && rm -f '${exit_path}' && cat > '${script_path}'" <<EOF
#!/usr/bin/env bash
set -uo pipefail
cd $(printf '%q' "${REMOTE_PROJECT}")
source $(printf '%q' "${CONDA_SH}")
conda activate $(printf '%q' "${CONDA_ENV}")
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
${job_cmd}
echo \$? > $(printf '%q' "${exit_path}")
EOF
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" "chmod +x '${script_path}'"

    if ! ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "cd '${REMOTE_PROJECT}' && oarsub --project $(printf '%q' "${PROJECT}") --name '${job_name}' -l /core=${PREP_JOB_CORES},walltime=${PREP_JOB_WALLTIME} -O '${out_path}' -E '${err_path}' '${script_path}'" \
        2>&1 | sed 's/^/  /'
    then
        return 1
    fi

    # Same primitive the whole-queue drain loop further below uses
    # (oarstat_json.py jobs), filtered to this one job's name. 10s, not that
    # loop's 60s: this blocks the real grid submission and is a single
    # lightweight job, not a whole queue to babysit.
    local still_running
    while :; do
        still_running="$(
            ssh -S "${SSH_CONTROL_PATH}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" |
                python3 "${PROJECT_ROOT}/scripts/lib/oarstat_json.py" jobs 2>/dev/null |
                awk -F'\t' -v n="${job_name}" '$2==n' | wc -l
        )"
        (( still_running == 0 )) && break
        sleep 10
    done

    ssh -S "${SSH_CONTROL_PATH}" "${remote}" "cat '${out_path}' 2>/dev/null" | sed 's/^/  /'
    local job_exit
    job_exit="$(ssh -S "${SSH_CONTROL_PATH}" "${remote}" "cat '${exit_path}' 2>/dev/null")"
    if [[ "${job_exit}" != "0" ]]; then
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" "cat '${err_path}' 2>/dev/null" | sed 's/^/  [stderr] /' >&2
        return 1
    fi
    return 0
}

# Per-label prep (resolve, --complete scan, sync that label's arg file, build
# its shared caches) still runs once per label below, but capture itself is
# called ONCE after the loop with every label's REMOTE_INPUT_PATH joined into
# one shell word -- submit_grid.sh word-splits that back into several args-file
# targets and packs their combined (label, group, seed) grid together (see its
# own header comment), which is what actually fills one OAR job with several
# labels instead of giving each its own. Calling capture once per label here
# (the earlier version of this loop) would have handed submit_grid.sh exactly
# one label each time, defeating that -- each label would still get its own
# pack/job even though submit_grid.sh itself now supports more.
ALL_REMOTE_INPUT_PATHS=()
for INPUT_ARG in "${POSITIONALS[@]}"; do
REMOTE_SCRIPT=""
REMOTE_INPUT_PATH=""

# A config first (resolve_args_file accepts a path, a bare stem, or a stem with
# .md -- the same three spellings run_local.sh and test_run.sh accept), and only
# if that finds nothing, a submitter under scripts/submit/. No name is claimed by
# both, so the order cannot hide one behind the other.
#
# The path handed to the cluster must be project-relative: it is rsynced to
# REMOTE_PROJECT and named again there. resolve_args_file returns a path it was
# given unchanged, and an absolute one for a stem, so strip the project root off
# whatever comes back.
if RESOLVED_ARGS_FILE="$(resolve_args_file "${INPUT_ARG}")"; then
    if [[ "${RESOLVED_ARGS_FILE}" != *.md ]]; then
        printf 'Unsupported file type: %s\n' "${INPUT_ARG}" >&2
        exit 2
    fi
    REMOTE_INPUT_PATH="${RESOLVED_ARGS_FILE#"${PROJECT_ROOT}"/}"
else
    SCRIPT_NAME="${INPUT_ARG%.sh}"
    if [[ ! "${SCRIPT_NAME}" =~ ^[A-Za-z0-9_-]+$ ]]; then
        printf 'Invalid SCRIPT_NAME: %s\n' "${SCRIPT_NAME}" >&2
        exit 2
    fi
    REMOTE_SCRIPT="scripts/submit/${SCRIPT_NAME}.sh"
fi

if [[ -n "${REMOTE_SCRIPT}" && ! -f "${PROJECT_ROOT}/${REMOTE_SCRIPT}" ]]; then
    printf 'Remote script not found: %s\n' "${REMOTE_SCRIPT}" >&2
    exit 2
fi

# A legacy scripts/submit/*.sh target names its own submitter, one per capture
# call; that has nothing in common with several args-file labels sharing one
# submit_grid.sh invocation, so the two cannot be mixed in one multi-label run.
if [[ -z "${REMOTE_INPUT_PATH}" && ${#POSITIONALS[@]} -gt 1 ]]; then
    printf -- 'Several labels at once only works for args-file targets, not a scripts/submit/*.sh script: %s\n' \
        "${INPUT_ARG}" >&2
    exit 2
fi

# variant is the label graphics/summarize below (and --complete's own
# already-done scan) key everything on -- only an args-file target has one; the
# legacy scripts/submit/*.sh path names no single label a report could be for.
# Persists after the loop as this iteration's value, which is exactly right when
# --graphics/--summarize run (they require exactly one label, checked above).
variant=""
if [[ -n "${REMOTE_INPUT_PATH}" ]]; then
    variant="$(basename "${REMOTE_INPUT_PATH}" .md)"
    VARIANTS+=("${variant}")
elif (( DO_GRAPHICS || DO_SUMMARIZE )); then
    printf -- '--graphics/--summarize need an args-file target (which has a label), not a scripts/submit/*.sh script: %s\n' "${INPUT_ARG}" >&2
    exit 2
fi

# Preserve locally completed pairs across the code-only rsync: the cluster's copy
# of the project has no test_metrics tree of its own to scan, so this scan has to
# happen here and travel as an environment variable. The remote submitter merges
# it with reports already present on that cluster (grid_load_completed).
if [[ "${COMPLETE_ONLY}" == "1" && -n "${REMOTE_INPUT_PATH}" ]]; then
    cold_series=0
    if args_file_has_flag "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}" --cold_split; then
        cold_series=1
    fi
    COMPLETED_EXPERIMENTS="$(
        grid_completed_list "${variant}" "${PROJECT_ROOT}/test_metrics" "${cold_series}"
    )"
    export COMPLETE_ONLY COMPLETED_EXPERIMENTS
fi

if [[ -n "${REMOTE_INPUT_PATH}" ]]; then
    printf 'Preparing to submit arguments file: %s\n' "${REMOTE_INPUT_PATH}"
    rsync -az --quiet -e "ssh -S ${SSH_CONTROL_PATH}" \
        "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}" \
        "${remote}:${REMOTE_PROJECT}/${REMOTE_INPUT_PATH}"

    # Build the memory-mapped lipid embedding store on the remote, once, before any
    # job exists. Without it every job unpickles the whole table into itself (267 MiB
    # resident, ~1 GiB of transient peak for the deterministic table); with it they map
    # one shared copy. Here rather than in cluster_preflight_remote.sh because that
    # script is read-only by contract, and before submission rather than inside a job
    # because 45 jobs starting at once would otherwise race to write the same archive.
    #
    # Runs as its own OAR job (run_prep_job, above) rather than directly on the
    # login node -- see that function's comment.
    #
    # Never fatal: a cluster where this cannot run still trains correctly, the jobs
    # just read the pickle as they always did. The build is a no-op when the store is
    # already current, so re-submitting the same grid costs nothing.
    # The environment has to be activated exactly as the jobs do it below: the
    # login shell's bare python3 has no torch, so without this the build always
    # failed and every job silently fell back to the pickle.
    printf 'Building shared embedding store on %s via OAR (skipped if current).\n' "${remote}"
    if ! run_prep_job "embed_store" \
        "python3 data/build_lipid_embedding_store.py --args_file=$(printf '%q' "${REMOTE_INPUT_PATH}")"; then
        printf 'WARNING: could not build the embedding store; jobs will read the pickle instead.\n' >&2
    fi

    # Same idea, for --pair_descriptors' per-candidate/per-protein RDKit values
    # (dataloader/pair_descriptor_cache.py). Never fatal, same as above: a job that
    # cannot read it just computes the values itself, slower but not wrong.
    #
    # Unlike the embedding store this cache is a few hundred KB, so
    # cluster_sync_excludes.sh now carries scripts/run_local.sh's own copy of it
    # along with the code sync above -- the common case is already current the
    # moment it lands (store_is_current() checks the payload's own recorded
    # source sizes/mtimes, not where it was built), and --check_only confirms
    # that with a handful of stat() calls, cheap enough to run directly on the
    # login node. Escalate to an OAR job (run_prep_job) only on an actual
    # mismatch (a table/protein-graph edit that has not round-tripped to this
    # machine yet) -- that RDKit/pocket-parse rebuild is what hit GRICAD's 600s
    # login-node CPU limit in the first place (see run_prep_job's comment).
    variant_pair_cache_cmd="python3 data/build_pair_descriptor_cache.py --args_file=$(printf '%q' "${REMOTE_INPUT_PATH}")"
    if ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "cd '${REMOTE_PROJECT}' && source $(printf '%q' "${CONDA_SH}") && conda activate $(printf '%q' "${CONDA_ENV}") && OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 ${variant_pair_cache_cmd} --check_only" \
        2>&1 | sed 's/^/  /'
    then
        : # already current -- the synced copy (or no cache needed at all) covers it
    else
        printf 'Building shared pair descriptor cache on %s via OAR (stale copy).\n' "${remote}"
        if ! run_prep_job "pair_descr_cache" "${variant_pair_cache_cmd}"; then
            printf 'WARNING: could not build the pair descriptor cache; jobs will compute it themselves.\n' >&2
        fi
    fi

    # One submitter for both series: it reads the config and picks the ordinary
    # or the cold-split rotation from the --cold_split flag in it.
    REMOTE_SCRIPT="scripts/launch/submit_grid.sh"
    if args_file_has_flag "${PROJECT_ROOT}/${REMOTE_INPUT_PATH}" --cold_split; then
        printf 'Detected --cold_split; the cold validation/test rotation will be used.\n'
    fi

    ALL_REMOTE_INPUT_PATHS+=("${REMOTE_INPUT_PATH}")
fi
done

# Single capture call: every args-file label's path, space-joined into ONE
# shell word (safe -- arg-file paths never contain whitespace, same assumption
# submit_grid.sh's own word-split makes), or the one legacy REMOTE_INPUT_PATH
# (empty) / REMOTE_SCRIPT (the submit/*.sh path) when POSITIONALS had exactly
# one non-args-file target.
if (( ${#ALL_REMOTE_INPUT_PATHS[@]} > 0 )); then
    printf -v REMOTE_INPUT_PATH '%s ' "${ALL_REMOTE_INPUT_PATHS[@]}"
    REMOTE_INPUT_PATH="${REMOTE_INPUT_PATH% }"
fi

printf 'Queuing OAR jobs on %s.\n' "${remote}"
ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} ${remote_env} bash scripts/cluster/cluster_queue_remote.sh capture '${REMOTE_QUEUE_DIR}' '${REMOTE_SCRIPT}' '${SESSION_MARKER}' '${REMOTE_INPUT_PATH}'"

# A wrong PROJECT or GPU_PROPERTY fails on the FIRST oarsub: drain keeps the
# remaining commands pending and returns non-zero, so nothing is lost -- fix the
# setting and re-run rather than re-queuing 45 jobs.
printf 'Submitting queued OAR jobs now.\n'
ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
    "cd '${REMOTE_PROJECT}' && CLUSTER_NAME=${CLUSTER_NAME} bash scripts/cluster/cluster_queue_remote.sh drain '${REMOTE_QUEUE_DIR}' '${REMOTE_USER}' '${MAX_WAITING_JOBS}'"

SESSION_MARKER="$(
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "cat '${REMOTE_QUEUE_DIR}/session_marker' 2>/dev/null || printf '%s\n' '${SESSION_MARKER}'"
)"

if (( DO_GRAPHICS || DO_SUMMARIZE )); then
    # Same seed set this invocation actually submitted -- SEEDS_OVERRIDE if
    # --seeds was given, DEFAULT_SEEDS (scripts/settings.sh) otherwise.
    if [[ -n "${SEEDS_OVERRIDE:-}" ]]; then
        read -r -a _report_seeds <<< "${SEEDS_OVERRIDE}"
    else
        _report_seeds=("${DEFAULT_SEEDS[@]}")
    fi
    seeds_csv="$(IFS=,; printf '%s' "${_report_seeds[*]}")"

    # One marker per label, dropped on the CLUSTER (not this computer) under
    # its queue dir. This is what lets a completely different machine finish
    # the job: wait_and_sync.sh's check_pending_reports() reads this same
    # directory whenever it sees this cluster's queue idle, on whichever
    # computer happens to be running it -- so if this terminal or this
    # computer disappears before the wait loop below returns, the report
    # still gets generated the next time anyone points wait_and_sync.sh at
    # this cluster, with no state needed here beyond this file.
    ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
        "mkdir -p '${REMOTE_QUEUE_DIR}/pending_reports'" || true
    for variant in "${VARIANTS[@]}"; do
        ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
            "printf 'seeds_csv=%s\ngraphics=%s\nsummarize=%s\n' \
                $(printf '%q' "${seeds_csv}") $(printf '%q' "${DO_GRAPHICS}") $(printf '%q' "${DO_SUMMARIZE}") \
                > '${REMOTE_QUEUE_DIR}/pending_reports/${variant}.report'" || true
    done

    # Bounded instead of the indefinite watcher below: poll only THIS cluster's
    # OAR queue for this user until it drains, sync once more, generate what was
    # asked for, exit -- "run this and hand back a report", not "watch forever".
    # oarstat_json.py jobs is the same one-job-per-line primitive
    # scripts/lib/progress_table.sh's own job table already uses; 60s rather
    # than the watcher's 300s default because a --graphics/--summarize caller is
    # explicitly waiting on this, not glancing at a table every so often.
    #
    # This loop, and everything after it, is a CONVENIENCE for staying in this
    # terminal -- if it never runs to completion (closed terminal, dropped
    # SSH, killed process), the markers written above are still there for
    # wait_and_sync.sh to pick up later, from here or from another computer.
    what="$( { (( DO_GRAPHICS )) && printf 'graphics'
                (( DO_GRAPHICS && DO_SUMMARIZE )) && printf ' and '
                (( DO_SUMMARIZE )) && printf 'the summary'; } )"
    printf 'Jobs queued. Waiting for %s@%s to drain before %s.\n' \
        "${REMOTE_USER}" "${CLUSTER_NAME}" "${what}"
    while :; do
        remaining="$(
            ssh -S "${SSH_CONTROL_PATH}" "${remote}" "oarstat -J -f -u '${REMOTE_USER}' 2>/dev/null" |
                python3 "${PROJECT_ROOT}/scripts/lib/oarstat_json.py" jobs 2>/dev/null | wc -l
        )"
        (( remaining == 0 )) && break
        sleep 60
    done

    CLUSTERS="${CLUSTER_NAME}" \
    REMOTE_USER="${REMOTE_USER}" \
    REMOTE_PROJECT="${REMOTE_PROJECT}" \
    LOCAL_PROJECT="${PROJECT_ROOT}" \
    CONDA_ENV="${CONDA_ENV}" \
    MAX_WAITING_JOBS="${MAX_WAITING_JOBS}" \
        bash "${PROJECT_ROOT}/scripts/wait_and_sync.sh" --once >/dev/null 2>&1 || true

    # One report per label, all queues having drained together above -- see
    # VARIANTS, collected in the capture loop above from every args-file label
    # requested (order of submission). Claim each marker (atomic rename) before
    # generating: the wait_and_sync.sh --once just above visits this same
    # cluster and, seeing it idle, may have already claimed and generated some
    # of these labels itself -- a failed claim here means it (or another
    # computer's watcher racing against this one) already has it in hand.
    for variant in "${VARIANTS[@]}"; do
        marker="${REMOTE_QUEUE_DIR}/pending_reports/${variant}.report"
        claimed="$(
            ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
                "mv '${marker}' '${marker}.claimed' 2>/dev/null && echo yes || echo no"
        )"
        [[ "${claimed}" == "yes" ]] || continue
        # Explicit if/else, not a bare call: this script runs under set -e, and an
        # unguarded failure here would abort the WHOLE loop -- silently skipping
        # every remaining label in VARIANTS, not just this one. On failure the
        # marker is restored (not deleted), so wait_and_sync.sh (or a later
        # --graphics/--summarize invocation) retries this label instead of its
        # report being lost with no trace.
        if bash "${PROJECT_ROOT}/scripts/lib/generate_label_report.sh" \
            "${variant}" "${seeds_csv}" "${DO_GRAPHICS}" "${DO_SUMMARIZE}"; then
            ssh -S "${SSH_CONTROL_PATH}" "${remote}" "rm -f '${marker}.claimed'" || true
        else
            printf 'generate_label_report.sh failed for %s -- leaving its marker queued for retry.\n' \
                "${variant}" >&2
            ssh -S "${SSH_CONTROL_PATH}" "${remote}" \
                "mv '${marker}.claimed' '${marker}' 2>/dev/null" || true
        fi
    done

    exit 0
fi

# Hand off to the watcher: it visits every cluster in turn, so jobs still running
# on the OTHER cluster keep being synced too, and the metrics table is rebuilt
# once per round from the merged local tree. WATCH_CLUSTERS=<name> narrows it
# back to a single cluster.
#
# Nothing about the batch just queued is passed on. The watcher is a viewer: it
# re-reads the queue and the session marker from the cluster every round and
# never deletes either, so it has no state to be handed. Ctrl-C stops watching
# and nothing else -- jobs keep being submitted by the crontab entry the watcher
# installs on the frontend, so neither this terminal nor this computer has to
# stay up for the queue to drain.
printf 'Jobs queued. Waiting for completion and synchronization.\n'
CLUSTERS="${WATCH_CLUSTERS:-bigfoot kraken kraken-cpu}" \
REMOTE_USER="${REMOTE_USER}" \
REMOTE_PROJECT="${REMOTE_PROJECT}" \
LOCAL_PROJECT="${PROJECT_ROOT}" \
CONDA_ENV="${CONDA_ENV}" \
MAX_WAITING_JOBS="${MAX_WAITING_JOBS}" \
    bash "${PROJECT_ROOT}/scripts/wait_and_sync.sh"
