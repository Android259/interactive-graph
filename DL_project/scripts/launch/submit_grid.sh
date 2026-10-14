#!/usr/bin/env bash
# Submit one or several variants' whole group x seed grids to OAR, packed
# together as densely as PACK_SIZE allows.
#
#   bash scripts/launch/submit_grid.sh arg_files/<config>.md
#   bash scripts/launch/submit_grid.sh arg_files/a.md arg_files/b.md
#
# Each config picks its own series. Without --cold_split, one group is held out and
# serves as both validation and test. With it, a job trains on 7 groups, selects the
# checkpoint on one held-out group and tests on another:
#
#   --excluded_groups=<TEST>,<VAL> --test_group=<TEST>
#   -> csvtest = TEST | csvalidate = VAL | csvtrain = the other 7
#
# Either way TEST rotates over all 9 groups (9 x 5 seeds = 45 jobs); the VAL for each
# is the val_for_test map below.
#
# Labels named in one call share their packs: their (label, group, seed) records go
# into one stream, so a pack is filled to PACK_SIZE before the next one opens. One
# label per call would mean one pack per label, and on kraken-cpu a whole 192-core
# node per label.
#
# Called through scripts/run_bigfoot.sh / run_kraken.sh. They pass every
# cluster-dependent setting as an environment variable. Do not patch this file to
# retarget a cluster.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Walltime, the group lists and the default seeds.
# shellcheck source=scripts/settings.sh
source "${PROJECT_DIR}/scripts/settings.sh"
# shellcheck source=scripts/lib/pack_lib.sh
source "${PROJECT_DIR}/scripts/lib/pack_lib.sh"
# shellcheck source=scripts/lib/args_file_lib.sh
source "${PROJECT_DIR}/scripts/lib/args_file_lib.sh"
# shellcheck source=scripts/lib/grid_lib.sh
source "${PROJECT_DIR}/scripts/lib/grid_lib.sh"

# --- cluster-dependent settings ----------------------------------------------
# The real values come from scripts/lib/cluster_common.sh, keyed by CLUSTER_NAME.
# The defaults here are Bigfoot's, so calling this file directly still works.
# PROJECT and GPU_PROPERTY use `-`, not `:-`. An explicitly empty value then stays
# empty and its oarsub flag is dropped; some clusters need neither flag.
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
PROJECT="${PROJECT-pr-molgen}"
GPU_PROPERTY="${GPU_PROPERTY-(gpumodel='A100' OR gpumodel='V100')}"
# A shell `case` pattern the job matches against `nvidia-smi --query-gpu=name`,
# hence the character whitelist below. Empty on a CPU cluster.
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
OAR_RESOURCES="${OAR_RESOURCES:-/nodes=1/gpu=1}"
# 1 on kraken-cpu: the runners then skip nvidia-smi, the GPU lock and the memory
# wait, and derive concurrency from cores alone.
CPU_ONLY="${CPU_ONLY:-0}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
# Separates the clusters' OAR output filenames. Their job-ID spaces overlap, and
# the progress table finds a running job's log by `*_${job_id}.out`.
JOB_ID_TAG="${JOB_ID_TAG:-}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
# Space-separated subsets, for a smoke test instead of the full 45. They apply to
# every label in this call. There is no per-label override.
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"

# --- packing ------------------------------------------------------------------
# PACK_SIZE experiments share one OAR job. PACK_PARALLEL of them run at once on the
# card; the real number is chosen inside the job (run_experiment_pack.sh).
# PACK_SIZE=1 means one experiment per job, which run_one_experiment.sh handles.
PACK_SIZE="${PACK_SIZE:-1}"
PACK_PARALLEL="${PACK_PARALLEL:-1}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-5}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-0}"
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"
# The concurrency ASSUMED when sizing the walltime request. The request is fixed
# at submit time, so it must describe the weakest card GPU_PROPERTY admits.
PACK_WALLTIME_PARALLEL="${PACK_WALLTIME_PARALLEL:-1}"
# Documented scheduler cap; empty = unknown, do not check.
MAX_WALLTIME="${MAX_WALLTIME:-}"

for _pack_int in PACK_SIZE PACK_PARALLEL GPU_MIB_PER_RUN PACK_GPU_PERCENT \
    PACK_CPU_PER_RUN PACK_MIN_FREE_GPU_MIB PACK_HARDWARE_AUTO \
    PACK_WALLTIME_PARALLEL; do
    if [[ ! "${!_pack_int}" =~ ^[0-9]+$ ]]; then
        printf "%s must be an integer: %s\n" "${_pack_int}" "${!_pack_int}" >&2
        exit 2
    fi
done
if (( PACK_HARDWARE_AUTO != 0 && PACK_HARDWARE_AUTO != 1 )); then
    printf "PACK_HARDWARE_AUTO must be 0 or 1: %s\n" "${PACK_HARDWARE_AUTO}" >&2
    exit 2
fi
if [[ ! "${MIN_FREE_GPU_MIB}" =~ ^[0-9]+$ ]]; then
    printf "MIN_FREE_GPU_MIB must be an integer: %s\n" "${MIN_FREE_GPU_MIB}" >&2
    exit 2
fi
if [[ "${CPU_ONLY}" != "1" && ! "${GPU_MODEL_GLOB}" =~ ^[A-Za-z0-9_*?.|@%^:+-]+$ ]]; then
    printf "GPU_MODEL_GLOB contains unsafe characters: %s\n" "${GPU_MODEL_GLOB}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"

if [[ $# -lt 1 ]]; then
    printf "Usage: %s arguments_file.md [arguments_file.md ...]\n" "$0" >&2
    exit 1
fi
# capture_queue (scripts/cluster/cluster_queue_remote.sh) passes the whole
# submit_args as ONE shell word, because run_cluster.sh joins several labels with
# spaces so they land in the same pack. Hence the word-split. It is safe: a label is
# always a bare identifier or a plain path.
read -r -a REQUESTED_ARGS_FILES <<< "$*"

# --lipid_coldsplit: whole chemical families of lipids leave training and every
# protein stays. No protein group is held out, so the grid iterates these four sets.
# Keep the names in step with LIPID_COLDSPLIT_SETS
# (dataloader/splitting_on_blocks/lipid_coldsplit_blocks.py). An unknown name is
# rejected at parse time.
LIPID_COLDSPLIT_SETS_LIST=(sphingolipids phosphorus_free choline anionic)

# --lipid_subclass: the same lipid axis, cut by the source paper's subclasses
# (Titeca et al.) instead of the hand-built sets above. Bare gives one job per block
# below. --lipid_subclass=<spec> gives that one block alone. Keep in step with
# FIG3_SUBCLASS_BLOCKS (dataloader/splitting_on_blocks/lipid_subclass_blocks.py).
# A spec absent from data/lipid_article_classification.json is rejected at parse time.
LIPID_SUBCLASS_BLOCKS_LIST=(
    PC PG FA PE "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM" PI "LPC+LPE+LPG" PA
)

# --family_only, bare: one model per family, trained and validated on that family's
# own rows -- a warm row-level split inside the family
# (dataloader/Dataloader.py:147-150,1461), not a cold split. The grid still iterates
# PROTEIN_GROUPS, but nothing is excluded: the group is the whole training pool, so
# --family_only=<group> is appended instead of --excluded_groups. Every
# arg_files/deepclip/*.md config uses this axis.
#
# --random_split, bare: nothing is held out at all. It needs a marker because every
# other axis appends a flag and this one appends none; an args file cannot suppress
# the --excluded_groups this script would otherwise add, since the appended flag wins.
# With no split flag the loader takes its final branch (85% train, the rest halved
# label-by-label into valid and test) and new_train.py files the run under
# exclusion_set "random". One pseudo-group runs against the seeds. These runs are the
# warm anchor the cold-split numbers are read against, not a baseline for picking
# configurations: with every protein and lipid in training, both marginals are free.

# --- per-label setup ----------------------------------------------------------
# Parallel arrays, one entry per requested label, in command-line order.
# experiment_record/job_name/submit_one below take a label index into them.
LABEL_VARIANT=()
LABEL_ARGS_TEMPLATE=()
LABEL_COLD_SPLIT=()
LABEL_LIPID_COLDSPLIT=()
LABEL_FAMILY_ONLY=()
LABEL_FAMILY_ONLY_FIXED=()
LABEL_RANDOM_SPLIT=()
LABEL_LIPID_ISOLATION=()
LABEL_LIPID_SUBCLASS=()
LABEL_LIPID_SPECIES=()
LABEL_OUTPUT_ROOT=()
LABEL_WALLTIME=()
# 1 for a --deepclip label. On a CPU-only cluster its jobs ask for the cores their
# runs use instead of a whole node (cpu_only_resources below).
LABEL_CORE_SIZED=()
# One line per (label_index, group, seed), across all labels. The main loop below
# packs from this stream and crosses label boundaries on purpose.
combined_pairs=""

for args_file in "${REQUESTED_ARGS_FILES[@]}"; do
    if [[ ! -f "${args_file}" ]]; then
        printf "Arguments file not found: %s\n" "${args_file}" >&2
        exit 1
    fi

    this_cold_split=0
    if args_file_has_flag "${args_file}" --cold_split; then
        this_cold_split=1
    fi

    # Per label: a pack holding two labels that disagree takes the slower of them
    # (max-walltime tracking in the main loop), never the base WALLTIME.
    this_walltime="${WALLTIME}"
    if args_file_has_flag "${args_file}" --descriptors_head; then
        this_walltime="${DESCRIPTORS_HEAD_WALLTIME}"
        printf "Detected --descriptors_head in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --descriptor_mlp; then
        # The same no-encoder-towers cost class as --descriptors_head, and smaller
        # still, so that budget is not short here.
        this_walltime="${DESCRIPTORS_HEAD_WALLTIME}"
        printf "Detected --descriptor_mlp in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --deepclip; then
        # The most extreme case of the same shape: --deepclip builds
        # architecture/deepclip.py and nothing else (1960-8960 parameters). Checked
        # before --fast_attention, whose budget is sized for encoders this config
        # never builds. Why one number covers every arm: DEEPCLIP_WALLTIME.
        this_walltime="${DEEPCLIP_WALLTIME}"
        printf "Detected --deepclip in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --fast_attention; then
        this_walltime="${FAST_ATTENTION_WALLTIME}"
        printf "Detected --fast_attention in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    fi

    this_variant="$(basename "${args_file}" .md)"
    this_args_template="$(args_file_flags "${args_file}")"

    this_lipid_coldsplit=0
    if args_file_has_flag "${args_file}" --lipid_coldsplit; then
        this_lipid_coldsplit=1
        if (( this_cold_split )); then
            printf -- '--lipid_coldsplit and --cold_split hold out different axes; pick one (%s).\n' \
                "${args_file}" >&2
            exit 2
        fi
        this_args_template="$(printf '%s' "${this_args_template}" \
            | sed -E 's/(^|[[:space:]])--lipid_coldsplit([[:space:]]|$)/\1/g')"
    fi

    # Bare --lipid_subclass is stripped from the template, like the bare
    # --lipid_coldsplit marker above. The trainer's flag needs a value, and the
    # grid appends one per block.
    this_lipid_subclass=0
    this_lipid_subclass_fixed=""
    if args_file_has_flag "${args_file}" --lipid_subclass; then
        this_lipid_subclass=1
        if (( this_cold_split )) || (( this_lipid_coldsplit )); then
            printf -- '--lipid_subclass and --cold_split/--lipid_coldsplit hold out '\
'different things; pick one (%s).\n' "${args_file}" >&2
            exit 2
        fi
        this_lipid_subclass_fixed="$(args_file_flag_lines "${args_file}" \
            | sed -nE 's/^--lipid_subclass=(.+)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_subclass_fixed}" ]]; then
            this_args_template="$(printf '%s' "${this_args_template}" \
                | sed -E 's/(^|[[:space:]])--lipid_subclass([[:space:]]|$)/\1/g')"
        fi
    fi

    # Two forms. Bare: one job per PROTEIN_GROUPS entry, with --family_only=<group>
    # appended. --family_only=<value>: one fixed family, one job per seed, already
    # named in the template. A --lipid_isolation ladder scoped to one family
    # ("<family>__<key>" in lipid_isolation_blocks.py) needs the fixed form -- with a
    # bare marker the grid would iterate all nine groups and overwrite the family.
    this_family_only=0
    this_family_only_fixed=""
    if args_file_has_flag "${args_file}" --family_only; then
        this_family_only=1
        if (( this_cold_split )) || (( this_lipid_coldsplit )); then
            printf -- '--family_only is a warm per-family split, not a cold-split axis; '\
'it cannot combine with --cold_split/--lipid_coldsplit (%s).\n' "${args_file}" >&2
            exit 2
        fi
        this_family_only_fixed="$(args_file_flag_lines "${args_file}" \
            | sed -nE 's/^--family_only=(.+)$/\1/p' | tail -1)"
        if [[ -z "${this_family_only_fixed}" ]]; then
            this_args_template="$(printf '%s' "${this_args_template}" \
                | sed -E 's/(^|[[:space:]])--family_only([[:space:]]|$)/\1/g')"
        fi
    fi

    # --lipid_isolation=<key>: the lipid axis addressed by distance
    # (dataloader/splitting_on_blocks/lipid_isolation_blocks.py). It names its own
    # block, so nothing is expanded or appended: one pseudo-group against the seeds.
    this_lipid_isolation=""
    if args_file_has_flag "${args_file}" --lipid_isolation; then
        this_lipid_isolation="$(args_file_flag_lines "${args_file}" \
            | sed -nE 's/^--lipid_isolation=(.*)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_isolation}" ]]; then
            printf -- '--lipid_isolation needs a value (a key of LIPID_ISOLATION_BLOCKS) in %s.\n' \
                "${args_file}" >&2
            exit 2
        fi
        if (( this_cold_split )) || (( this_lipid_coldsplit )) || (( this_lipid_subclass )); then
            printf -- '--lipid_isolation and --cold_split/--lipid_coldsplit/'\
'--lipid_subclass hold out different things; pick one (%s).\n' "${args_file}" >&2
            exit 2
        fi
    fi

    # --lipid_species_coldsplit=<share>: the lipid axis cut at the concrete lipid
    # (dataloader/splitting_on_blocks/lipid_species_blocks.py). Names its own split,
    # like --lipid_isolation, but the block is drawn per seed, so the pseudo-group is
    # the share itself.
    this_lipid_species=""
    if args_file_has_flag "${args_file}" --lipid_species_coldsplit; then
        this_lipid_species="$(args_file_flag_lines "${args_file}" \
            | sed -nE 's/^--lipid_species_coldsplit=(.*)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_species}" ]]; then
            printf -- '--lipid_species_coldsplit needs a value (share of positives in '\
'the held-out block, e.g. 0.15) in %s.\n' "${args_file}" >&2
            exit 2
        fi
        if (( this_cold_split )) || (( this_lipid_coldsplit )) || (( this_lipid_subclass )) \
            || [[ -n "${this_lipid_isolation}" ]]; then
            printf -- '--lipid_species_coldsplit and --cold_split/--lipid_coldsplit/'\
'--lipid_subclass/--lipid_isolation hold out different things; pick one (%s).\n' \
                "${args_file}" >&2
            exit 2
        fi
    fi

    this_random_split=0
    if args_file_has_flag "${args_file}" --random_split; then
        this_random_split=1
        if (( this_cold_split )) || (( this_lipid_coldsplit )) || (( this_family_only )); then
            printf -- '--random_split holds nothing out; it cannot combine with '\
'--cold_split/--lipid_coldsplit/--family_only (%s).\n' "${args_file}" >&2
            exit 2
        fi
        # Stripped like the other markers: the trainer has no such flag.
        this_args_template="$(printf '%s' "${this_args_template}" \
            | sed -E 's/(^|[[:space:]])--random_split([[:space:]]|$)/\1/g')"
    fi

    # script_logs/<family>/..., the family directory run/ and test_metrics/ use
    # as well (arg_files/<family>/<label>.md -> training/results_layout.py).
    this_family="$(label_family "${this_variant}")"
    if (( this_cold_split )); then
        this_output_root="script_logs/${this_family}/${this_variant}_coldval_seeds01234"
        this_groups=("${COLD_TEST_GROUPS[@]}")
    else
        this_output_root="script_logs/${this_family}/${this_variant}_seeds01234"
        this_groups=("${PROTEIN_GROUPS[@]}")
    fi
    this_seeds=("${DEFAULT_SEEDS[@]}")
    if (( this_lipid_coldsplit )); then
        this_output_root="script_logs/${this_family}/${this_variant}_lipidsets"
        this_groups=("${LIPID_COLDSPLIT_SETS_LIST[@]}")
    fi
    if (( this_family_only )); then
        this_output_root="script_logs/${this_family}/${this_variant}_familyonly"
        if [[ -n "${this_family_only_fixed}" ]]; then
            # One job x seed, not nine: the family is already fixed in the template.
            this_groups=("${this_family_only_fixed}")
        else
            this_groups=("${PROTEIN_GROUPS[@]}")
        fi
    fi
    if (( this_random_split )); then
        # Named for the directory new_train.py files the run under, so the log,
        # run/ and test_metrics/ paths agree.
        this_output_root="script_logs/${this_family}/${this_variant}_random"
        this_groups=("random")
    fi
    if (( this_lipid_subclass )); then
        if [[ -n "${this_lipid_subclass_fixed}" ]]; then
            # One fixed block, already named in the template -- one job x seed.
            this_output_root="script_logs/${this_family}/${this_variant}_subclass"
            this_groups=("${this_lipid_subclass_fixed}")
        else
            this_output_root="script_logs/${this_family}/${this_variant}_lipidsubclasses"
            this_groups=("${LIPID_SUBCLASS_BLOCKS_LIST[@]}")
        fi
    fi
    if [[ -n "${this_lipid_isolation}" ]]; then
        this_output_root="script_logs/${this_family}/${this_variant}_iso${this_lipid_isolation}"
        this_groups=("iso${this_lipid_isolation}")
    fi
    if [[ -n "${this_lipid_species}" ]]; then
        # Two digits of the share, as new_train.py names the run directory.
        this_species_tag="species$(printf '%02d' \
            "$(awk -v s="${this_lipid_species}" 'BEGIN{printf "%d", s*100 + 0.5}')")"
        this_output_root="script_logs/${this_family}/${this_variant}_${this_species_tag}"
        this_groups=("${this_species_tag}")
    fi
    # GROUPS_OVERRIDE (run_cluster.sh's --groups/--no_groups) names protein families.
    # A label on another axis ignores it instead of failing, so one command can queue
    # protein-axis and lipid-axis labels together. Applying it would submit
    # --lipid_coldsplit=<family>, which the trainer rejects on every job; failing
    # would take the valid labels down too. Said on stderr, since the caller asked to
    # narrow something and here nothing was narrowed.
    if (( this_random_split )) && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        printf -- '--random_split holds no group out; ignoring --groups/--no_groups '\
'for %s -- the single random-split grid will run.\n' "${args_file}" >&2
    elif (( this_lipid_coldsplit )) && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        printf -- '--lipid_coldsplit runs over lipid sets, not protein groups; '\
'ignoring --groups/--no_groups for %s -- all %d lipid sets will run.\n' \
            "${args_file}" "${#this_groups[@]}" >&2
    elif (( this_lipid_subclass )) && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # To run a subset of the blocks, write --lipid_subclass=<spec> in the args
        # file. That form already runs exactly one block.
        printf -- '--lipid_subclass runs over lipid subclasses, not protein groups; '\
'ignoring --groups/--no_groups for %s -- all %d blocks will run.\n' \
            "${args_file}" "${#this_groups[@]}" >&2
    elif [[ -n "${this_lipid_isolation}" ]] && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        printf -- '--lipid_isolation names its own block; ignoring --groups/--no_groups '\
'for %s.\n' "${args_file}" >&2
    elif [[ -n "${this_lipid_species}" ]] && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        printf -- '--lipid_species_coldsplit names its own block; ignoring '\
'--groups/--no_groups for %s.\n' "${args_file}" >&2
    elif (( this_family_only )) && [[ -n "${this_family_only_fixed}" ]] \
        && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # The family is fixed in the template. An override would rename the output
        # directory without changing what trains.
        printf -- '--family_only=%s is already fixed in %s; ignoring --groups/--no_groups.\n' \
            "${this_family_only_fixed}" "${args_file}" >&2
    elif [[ -n "${GROUPS_OVERRIDE}" ]]; then
        read -r -a this_groups <<< "${GROUPS_OVERRIDE}"
    fi
    [[ -z "${SEEDS_OVERRIDE}" ]] || read -r -a this_seeds <<< "${SEEDS_OVERRIDE}"

    mkdir -p "${this_output_root}"
    grid_load_completed "${this_variant}" "" "${this_cold_split}"

    label_index="${#LABEL_VARIANT[@]}"
    LABEL_VARIANT+=("${this_variant}")
    LABEL_ARGS_TEMPLATE+=("${this_args_template}")
    LABEL_COLD_SPLIT+=("${this_cold_split}")
    LABEL_LIPID_COLDSPLIT+=("${this_lipid_coldsplit}")
    LABEL_FAMILY_ONLY+=("${this_family_only}")
    LABEL_FAMILY_ONLY_FIXED+=("${this_family_only_fixed}")
    LABEL_RANDOM_SPLIT+=("${this_random_split}")
    LABEL_LIPID_ISOLATION+=("${this_lipid_isolation}")
    LABEL_LIPID_SUBCLASS+=("${this_lipid_subclass}")
    LABEL_LIPID_SPECIES+=("${this_lipid_species}")
    LABEL_OUTPUT_ROOT+=("${this_output_root}")
    LABEL_WALLTIME+=("${this_walltime}")
    this_core_sized=0
    if args_file_has_flag "${args_file}" --deepclip; then
        this_core_sized=1
    fi
    LABEL_CORE_SIZED+=("${this_core_sized}")

    while IFS=$'\t' read -r group seed; do
        [[ -n "${group}" ]] || continue
        combined_pairs+="${label_index}"$'\t'"${group}"$'\t'"${seed}"$'\n'
    done < <(grid_pairs "${this_groups[*]}" "${this_seeds[*]}")
done

# TEST -> VAL mapping. Read only in cold-split mode. Shared across labels, because
# it belongs to the group rotation, not to a config.
declare -A val_for_test=(
    ["lipocalin"]="scp2"
    ["CRAL-TRIO"]="IP_trans"
    ["START"]="LBP_BPI_CETP"
    ["IP_trans"]="LBP_BPI_CETP"
    ["scp2"]="IP_trans"
    ["LBP_BPI_CETP"]="IP_trans"
    ["OSBP"]="scp2"
    ["GLTP"]="LBP_BPI_CETP"
    ["ML"]="scp2"
)

resolve_val_group() {
    local test_group="$1" val_group="${val_for_test[$1]:-}"
    if [[ -z "${val_group}" ]]; then
        printf "No validation group defined for test group: %s\n" "${test_group}" >&2
        exit 1
    fi
    printf '%s\n' "${val_group}"
}

# --- one experiment as a record ----------------------------------------------
# The record layout is scripts/lib/pack_lib.sh's, and both runners read it, so an
# experiment is described the same way alone or in a pack and writes the same tree.
# label_index says which requested label this (group, seed) belongs to.
experiment_record() {
    local label_index="$1" group="$2" seed="$3"
    local variant="${LABEL_VARIANT[label_index]}"
    local args_template="${LABEL_ARGS_TEMPLATE[label_index]}"
    local cold_split="${LABEL_COLD_SPLIT[label_index]}"
    local lipid_coldsplit="${LABEL_LIPID_COLDSPLIT[label_index]}"
    local family_only="${LABEL_FAMILY_ONLY[label_index]}"
    local family_only_fixed="${LABEL_FAMILY_ONLY_FIXED[label_index]}"
    local random_split="${LABEL_RANDOM_SPLIT[label_index]}"
    local lipid_isolation="${LABEL_LIPID_ISOLATION[label_index]}"
    local lipid_subclass="${LABEL_LIPID_SUBCLASS[label_index]}"
    local lipid_species="${LABEL_LIPID_SPECIES[label_index]}"
    local output_root="${LABEL_OUTPUT_ROOT[label_index]}"
    local val_group excluded output_dir stem header extra=""

    if (( cold_split )); then
        val_group="$(resolve_val_group "${group}")"
        excluded="${group},${val_group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_val-${val_group}_seed${seed}"
        extra=" --test_group=${group}"
        header="TEST: ${group} | VAL: ${val_group} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( lipid_coldsplit )); then
        # The "group" is the name of a lipid-class set and goes to its own flag.
        # excluded stays empty, so no protein leaves training.
        excluded=""
        extra=" --lipid_coldsplit=${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID SET: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( lipid_subclass )); then
        # The "group" is one article lipid-subclass block spec. Appended even when
        # the args file names it -- the same flag with the same value is a no-op, and
        # the branch stays identical for both forms.
        excluded=""
        extra=" --lipid_subclass=${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID SUBCLASS: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( family_only )) && [[ -n "${family_only_fixed}" ]]; then
        # The family is spelled out in the template, so nothing is appended, and a
        # --lipid_isolation there stays too: one fixed family with one fixed
        # cold-lipid block, which is what a ladder scoped to a family needs.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="FAMILY_ONLY (fixed): ${family_only_fixed}"
        if [[ -n "${lipid_isolation}" ]]; then
            header+=" | LIPID ISOLATION: ${lipid_isolation}"
        fi
        header+=" | VARIANT: ${variant} | SEED: ${seed}"
    elif (( family_only )); then
        # "group" is the family the whole table is restricted to, with a warm split
        # inside it. Nothing is excluded, so --family_only carries the group.
        excluded=""
        extra=" --family_only=${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="FAMILY_ONLY: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    elif [[ -n "${lipid_isolation}" ]]; then
        # The flag in the template already names the block, so nothing is appended.
        # "group" is the directory name new_train.py will use.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID ISOLATION: ${lipid_isolation} | VARIANT: ${variant} | SEED: ${seed}"
    elif [[ -n "${lipid_species}" ]]; then
        # Same shape as --lipid_isolation above. The loader draws the block per
        # seed, so two seeds hold out different lipids on purpose.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID SPECIES: ${lipid_species} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( random_split )); then
        # The axis defined by appending nothing: the loader's last branch splits
        # 85/7.5/7.5 and new_train.py names the run "random", which "group" is.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="RANDOM SPLIT | VARIANT: ${variant} | SEED: ${seed}"
    else
        excluded="${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="GROUP: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    fi

    mkdir -p "${output_dir}"
    pack_record \
        "${header}" \
        "${output_dir}/${stem}_ep150_batch16.log" \
        "${output_dir}/${stem}_" \
        "--label=${variant} ${args_template} --seed=${seed}$( [[ -n "${excluded}" ]] && printf ' --excluded_groups=%s' "${excluded}" )${extra}"
}

# --- oarsub -------------------------------------------------------------------
# An array, so an empty GPU_PROPERTY or PROJECT drops its flag entirely. `if`
# blocks rather than `[[ ]] &&`: a false test as the last command returns 1, and
# `set -e` would abort the whole submitter.
oarsub_submit() {
    local job_name="$1" walltime="$2" out_prefix="$3" job_command="$4"
    local resources="${5:-${OAR_RESOURCES}}"
    local -a oarsub_args=(
        --name "${job_name}"
        -l "${resources},walltime=${walltime}"
    )
    if [[ -n "${GPU_PROPERTY}" ]]; then
        oarsub_args+=(-p "${GPU_PROPERTY}")
    fi
    if [[ -n "${PROJECT}" ]]; then
        oarsub_args+=(--project "${PROJECT}")
    fi
    if [[ -n "${OARSUB_EXTRA}" ]]; then
        local -a extra_args
        read -r -a extra_args <<< "${OARSUB_EXTRA}"
        oarsub_args+=("${extra_args[@]}")
    fi
    oarsub_args+=(
        -O "${out_prefix}.out"
        -E "${out_prefix}.err"
        "${job_command}"
    )
    oarsub "${oarsub_args[@]}"
}

# What a CPU-only job asks OAR for. The kraken-cpu default is a whole node
# (/nodes=1: 192 cores), which suits a pack big enough to fill it. A --deepclip
# experiment runs on one core, and such a grid holds 5 to 45 of them, so a whole node
# would leave 150-190 cores idle for the full walltime. These jobs ask for exactly
# the cores their runs use. nproc inside the job then equals the run count, and nproc
# sets the runner's slot count, so every run still starts at once. Memory comes with
# the cores on OAR, so it is never requested separately. Any other label, and every
# GPU cluster, keeps OAR_RESOURCES.
cpu_only_resources() {
    local core_sized="$1" runs="$2"
    local cores=$(( runs * (PACK_CPU_PER_RUN > 0 ? PACK_CPU_PER_RUN : 1) ))
    if (( CPU_ONLY && core_sized && cores > 0 && cores <= 192 )); then
        printf '/nodes=1/core=%d\n' "${cores}"
    else
        printf '%s\n' "${OAR_RESOURCES}"
    fi
}

# The OAR job name. The progress table falls back to it when OAR does not report a
# job's output path, so a cold-split job must keep naming its validation group.
job_name() {
    local label_index="$1" group="$2" seed="$3"
    local variant="${LABEL_VARIANT[label_index]}"
    if (( LABEL_COLD_SPLIT[label_index] )); then
        printf '%s_%s_v%s_s%s\n' \
            "${variant}" "${group}" "$(resolve_val_group "${group}")" "${seed}"
    else
        printf '%s_%s_s%s\n' "${variant}" "${group}" "${seed}"
    fi
}

submit_one() {
    local label_index="$1" group="$2" seed="$3"
    local record log_file out_base job_command

    record="$(experiment_record "${label_index}" "${group}" "${seed}")"
    IFS=$'\t' read -r _ log_file out_base _ <<< "${record}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q CPU_ONLY=%q bash scripts/launch/run_one_experiment.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "${CPU_ONLY}" "$(pack_spec_encode "${record}")"

    oarsub_submit "$(job_name "${label_index}" "${group}" "${seed}")" \
        "${LABEL_WALLTIME[label_index]}" \
        "${out_base}${JOB_ID_TAG}%jobid%" "${job_command}" \
        "$(cpu_only_resources "${LABEL_CORE_SIZED[label_index]}" 1)"
}

submit_pack() {
    local pack_index="$1" spec="$2" pack_count="$3" pack_walltime_str="$4" pack_tag="$5" job_tag="$6"
    local pack_core_sized="${7:-0}"
    local job_walltime pack_dir job_command runner_env spec_file

    job_walltime="$(pack_job_walltime "${pack_count}" "${pack_walltime_str}" "${PACK_WALLTIME_PARALLEL}")"
    pack_check_walltime "${job_walltime}" "${MAX_WALLTIME}" || exit 2

    # The job's own stdout must not land on a "*_<tag><jobid>.out" path: that
    # pattern belongs to the runner's per-experiment files, and the progress table
    # turns every match into a row. One directory for all labels, since a pack can
    # span several.
    pack_dir="script_logs/_cross_label_packs"
    mkdir -p "${pack_dir}"

    printf -v runner_env \
        'GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q CPU_ONLY=%q JOB_ID_TAG=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q' \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "${CPU_ONLY}" "${JOB_ID_TAG}" \
        "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" "${PACK_GPU_PERCENT}" \
        "${PACK_CPU_PER_RUN}" "${PACK_MIN_FREE_GPU_MIB}" \
        "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}"

    # A file, not a base64 blob on the oarsub line: a full-size pack encodes past
    # Linux's ~128 KiB single-argument limit and fails oarsub's execve with "Argument
    # list too long" (pack_spec_write_file in pack_lib.sh). mktemp keeps two
    # concurrent submitters, whose pack_index both start at 0, apart.
    spec_file="$(mktemp "${pack_dir}/pack${pack_index}_spec.XXXXXX")"
    pack_spec_write_file "${spec}" "${spec_file}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && %s bash scripts/launch/run_experiment_pack.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${runner_env}" "${spec_file}"

    printf "Pack %d: %d experiment(s) [%s], walltime=%s.\n" \
        "${pack_index}" "${pack_count}" "${pack_tag}" "${job_walltime}"
    # Two OAR limits on a job name. Characters: only a-z A-Z 0-9 _.- , so the "+"
    # of the readable pack_tag becomes "-". Length: jobs.job_name is varying(100),
    # and five long descriptor labels in one pack built a 139-char name that killed
    # oarsub with a Postgres truncation error. Plain truncation would collide between
    # label combinations sharing a long prefix, so an over-length tag is cut and
    # given an 8-hex digest of the full tag: unique per combination and stable across
    # re-submissions, which the oarsub-command dedup in capture_queue needs.
    local suffix="_pack${pack_index}"
    local oar_job_name="${job_tag}${suffix}"
    if (( ${#oar_job_name} > 100 )); then
        local digest keep
        digest="$(printf '%s' "${job_tag}" | md5sum | cut -c1-8)"
        keep=$(( 100 - ${#suffix} - ${#digest} - 1 ))
        (( keep > 0 )) || keep=0
        oar_job_name="${job_tag:0:keep}-${digest}${suffix}"
    fi
    oarsub_submit "${oar_job_name}" \
        "${job_walltime}" \
        "${pack_dir}/pack${pack_index}_${JOB_ID_TAG}%jobid%.pack" \
        "${job_command}" \
        "$(cpu_only_resources "${pack_core_sized}" "${pack_count}")"
}

# --- the grid -----------------------------------------------------------------
# The seed loop stays innermost per label (grid_pairs), so a pack of 5 is one group's
# seeds and a pack of 9 spans groups at a fixed seed -- both natural units to
# resubmit or cancel whole. Labels follow in command-line order, so a pack crosses a
# label boundary only once the label ahead of it is exhausted.
submitted=0
experiments=0
pack_index=0
pack_count=0
pack_spec=""
# Empty means no record yet. Set from the first record's label walltime and only
# raised after that. It never starts at the base WALLTIME: a pack built entirely
# from --fast_attention labels must not inherit the slower default.
pack_walltime_str=""
# Stays 1 only while every experiment in the pack is core-sized. One other label in
# a cross-label pack keeps the whole-node request.
pack_core_sized=1
declare -A pack_labels_seen=()
pack_labels_list=()

flush_pack() {
    (( pack_count > 0 )) || return 0
    local tag job_tag
    tag="$(IFS=+; printf '%s' "${pack_labels_list[*]}")"
    job_tag="$(IFS=-; printf '%s' "${pack_labels_list[*]}")"
    submit_pack "${pack_index}" "${pack_spec}" "${pack_count}" "${pack_walltime_str}" "${tag}" "${job_tag}" "${pack_core_sized}"
    pack_index=$((pack_index + 1))
    submitted=$((submitted + 1))
    pack_count=0
    pack_spec=""
    pack_walltime_str=""
    pack_core_sized=1
    pack_labels_seen=()
    pack_labels_list=()
}

while IFS=$'\t' read -r label_index group seed; do
    [[ -n "${group}" ]] || continue
    experiments=$((experiments + 1))
    if (( PACK_SIZE <= 1 )); then
        submit_one "${label_index}" "${group}" "${seed}"
        submitted=$((submitted + 1))
        continue
    fi
    pack_spec+="$(experiment_record "${label_index}" "${group}" "${seed}")"$'\n'
    pack_count=$((pack_count + 1))
    (( LABEL_CORE_SIZED[label_index] )) || pack_core_sized=0

    this_walltime="${LABEL_WALLTIME[label_index]}"
    if [[ -z "${pack_walltime_str}" ]] \
        || (( $(pack_walltime_seconds "${this_walltime}") > $(pack_walltime_seconds "${pack_walltime_str}") )); then
        pack_walltime_str="${this_walltime}"
    fi
    this_label="${LABEL_VARIANT[label_index]}"
    if [[ -z "${pack_labels_seen[${this_label}]:-}" ]]; then
        pack_labels_seen["${this_label}"]=1
        pack_labels_list+=("${this_label}")
    fi

    if (( pack_count >= PACK_SIZE )); then
        flush_pack
    fi
done < <(printf '%s' "${combined_pairs}")
flush_pack

all_labels_csv="$(IFS=,; printf '%s' "${LABEL_VARIANT[*]}")"
if (( PACK_SIZE <= 1 )); then
    printf "Submitted %d jobs across %d label(s) (%s).\n" \
        "${submitted}" "${#LABEL_VARIANT[@]}" "${all_labels_csv}"
else
    printf "Submitted %d packed job(s), %d experiment(s) total across %d label(s) (%s), up to %d per job, up to %d concurrent per GPU.\n" \
        "${submitted}" "${experiments}" "${#LABEL_VARIANT[@]}" "${all_labels_csv}" \
        "${PACK_SIZE}" "${PACK_PARALLEL}"
fi
