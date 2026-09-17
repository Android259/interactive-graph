#!/usr/bin/env bash
# Submit one or several variants' whole group x seed grids to OAR, packed
# together as densely as PACK_SIZE allows.
#
#   bash scripts/launch/submit_grid.sh scripts/arg_files/<config>.md
#   bash scripts/launch/submit_grid.sh scripts/arg_files/a.md scripts/arg_files/b.md
#
# One file for both series. Which one runs is decided by each config itself: a
# --cold_split flag in it selects separate held-out validation and test groups
# (the table below), anything else excludes one group and uses it for both.
#
# Several labels in one call is what makes packing cross labels possible: with
# one label per call (the old contract here), each label's grid fills its own
# pack(s) and each pack is its own OAR job -- on kraken-cpu, where PACK_SIZE is
# sized to fit an entire descriptors_head grid already, that means one whole
# 192-core node per label even when three tiny labels together would fit on
# one. Passed several labels, this script builds ONE combined (label, group,
# seed) stream and packs records into a job without caring which label they
# came from, so packs -- and therefore nodes -- are filled to PACK_SIZE before
# a new one opens, regardless of label boundaries.
#
# Called through scripts/run_bigfoot.sh / run_kraken.sh, which supply every
# cluster-dependent setting as an environment variable -- never by patching this
# file's text.
#
# =============================================================================
# COLD SPLIT with SEPARATE validation and test protein groups.
#
# Each job trains on 7 groups, validates (checkpoint selection) on 1 held-out
# group, and tests on a DIFFERENT held-out group. Test rotates over all 9
# groups (complete cold coverage); validation is picked -- not by brute-force
# permutation -- from a "safe" pool so that (a) removing it barely shrinks the
# training set and (b) its class balance is a usable proxy for the val metric.
#
#   run:  python ./training/new_train.py \
#             --excluded_groups=<TEST>,<VAL> --test_group=<TEST> ...
#   -> csvtest    = TEST group   (reported, seen once at the end)
#   -> csvalidate = VAL  group   (drives early-stopping / checkpoint choice)
#   -> csvtrain   = the other 7 groups
#
# 9 test groups x 5 seeds = 45 jobs.
#
# -----------------------------------------------------------------------------
# GROUP STATISTICS  (data/Processed_Negative_Interaction_Corrected_Domains.csv)
#   overall positive fraction = 6.9%   |   total interactions = 11018
#
#   group          total    pos    neg    pos%   %of-all   role-as-VAL?
#   -----------------------------------------------------------------------
#   lipocalin       3123     90   3033    2.9%    28.3%    NO  (too large)
#   CRAL-TRIO       2845    204   2641    7.2%    25.8%    NO  (too large)
#   START            982    200    782   20.4%     8.9%    NO  (balance too skewed)
#   IP_trans         943     65    878    6.9%     8.6%    YES (balance == global)
#   scp2             936     43    893    4.6%     8.5%    YES (small, ~balanced)
#   LBP_BPI_CETP     626     55    571    8.8%     5.7%    YES (small, ~balanced)
#   OSBP             626      8    618    1.3%     5.7%    NO  (only 8 positives)
#   GLTP             625     81    544   13.0%     5.7%    YES (small, enough pos)
#   ML               312     10    302    3.2%     2.8%    NO  (tiny, 10 positives)
#
#   VAL pool = { IP_trans, scp2, LBP_BPI_CETP, GLTP } : each <=8.6% of the data
#   (training barely suffers) and each has >=40 positives with a balance not far
#   from the global 6.9% (val metric stays meaningful).
#
# -----------------------------------------------------------------------------
# TEST -> VAL ASSIGNMENT
#   VAL = the safe-pool group whose positive-fraction is closest to the TEST
#   group's (a "not too different" proxy), excluding TEST itself.
#
#   TEST            pos%     ->  VAL             pos%   train-loss (test+val %of-all)
#   ---------------------------------------------------------------------------
#   lipocalin       2.9%     ->  scp2            4.6%    36.8%  (28.3 + 8.5)
#   CRAL-TRIO       7.2%     ->  IP_trans        6.9%    34.4%  (25.8 + 8.6)
#   START          20.4%     ->  LBP_BPI_CETP    8.8%    14.6%  ( 8.9 + 5.7)  [see note]
#   IP_trans        6.9%     ->  LBP_BPI_CETP    8.8%    14.3%  ( 8.6 + 5.7)
#   scp2            4.6%     ->  IP_trans        6.9%    17.1%  ( 8.5 + 8.6)
#   LBP_BPI_CETP    8.8%     ->  IP_trans        6.9%    14.3%  ( 5.7 + 8.6)
#   OSBP            1.3%     ->  scp2            4.6%    14.2%  ( 5.7 + 8.5)
#   GLTP           13.0%     ->  LBP_BPI_CETP    8.8%    11.4%  ( 5.7 + 5.7)
#   ML              3.2%     ->  scp2            4.6%    11.3%  ( 2.8 + 8.5)
#
#   VAL usage: scp2 x3, IP_trans x3, LBP_BPI_CETP x3, GLTP x0  (val != test always).
#
#   NOTE: balanced accuracy (the checkpoint-selection metric) is prevalence-
#   invariant, so matching VAL's positive-fraction to TEST is not required; the
#   VAL group must instead give a learnable, above-chance signal. GLTP collapses
#   (BA~0.41) and cannot select a meaningful epoch, so START's VAL is the
#   learnable LBP_BPI_CETP (BA~0.76) despite the balance mismatch, and GLTP is no
#   longer used for validation anywhere.
# =============================================================================

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
# Every default is a Bigfoot value, so an unset environment targets Bigfoot.
# `-` rather than `:-` for PROJECT and
# GPU_PROPERTY: an explicitly empty value must stay empty so the corresponding
# oarsub flag is omitted (a cluster may need no project, or no gpumodel filter).
CONDA_SH="${CONDA_SH:-/home/kalinina/miniconda3/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-Kalinin_project_LP}"
PROJECT="${PROJECT-pr-molgen}"
GPU_PROPERTY="${GPU_PROPERTY-(gpumodel='A100' OR gpumodel='V100')}"
# Shell `case` pattern matched against `nvidia-smi --query-gpu=name` inside the
# job, hence the character whitelist below. Empty on a CPU-only cluster
# (CPU_ONLY=1, scripts/lib/cluster_common.sh's kraken-cpu profile), where there
# is no GPU to name.
GPU_MODEL_GLOB="${GPU_MODEL_GLOB:-*A100*|*V100*}"
OAR_RESOURCES="${OAR_RESOURCES:-/nodes=1/gpu=1}"
# 1 on kraken-cpu: no nvidia-smi, no GPU admission/lock/memory-wait in
# run_one_experiment.sh / run_experiment_pack.sh, concurrency from cores alone.
CPU_ONLY="${CPU_ONLY:-0}"
MIN_FREE_GPU_MIB="${MIN_FREE_GPU_MIB:-16384}"
# Distinguishes OAR output filenames between clusters, whose job-ID spaces
# overlap (the progress table locates a running job's log by `*_${job_id}.out`).
JOB_ID_TAG="${JOB_ID_TAG:-}"
OARSUB_EXTRA="${OARSUB_EXTRA:-}"
# Space-separated subsets, for a smoke test instead of the full 45. Applied to
# EVERY label in this call, same as before -- there was never a per-label
# override and this does not add one.
GROUPS_OVERRIDE="${GROUPS_OVERRIDE:-}"
SEEDS_OVERRIDE="${SEEDS_OVERRIDE:-}"
COMPLETE_ONLY="${COMPLETE_ONLY:-0}"
COMPLETED_EXPERIMENTS="${COMPLETED_EXPERIMENTS:-}"

# --- packing ------------------------------------------------------------------
# PACK_SIZE experiments share one OAR job; PACK_PARALLEL of them may run at once
# on the single allocated GPU (the effective number is decided inside the job
# from the card actually handed out -- see run_experiment_pack.sh). PACK_SIZE=1
# is one experiment per job, which run_one_experiment.sh handles directly.
PACK_SIZE="${PACK_SIZE:-1}"
PACK_PARALLEL="${PACK_PARALLEL:-1}"
GPU_MIB_PER_RUN="${GPU_MIB_PER_RUN:-0}"
PACK_GPU_PERCENT="${PACK_GPU_PERCENT:-80}"
PACK_CPU_PER_RUN="${PACK_CPU_PER_RUN:-5}"
PACK_MIN_FREE_GPU_MIB="${PACK_MIN_FREE_GPU_MIB:-0}"
PACK_HARDWARE_AUTO="${PACK_HARDWARE_AUTO:-0}"
PACK_SKIP_DONE="${PACK_SKIP_DONE:-1}"
# Concurrency ASSUMED when sizing the walltime request. Must describe the
# weakest card GPU_PROPERTY admits, because the request is fixed at submit time
# while the real concurrency is not.
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
# scripts/cluster/cluster_queue_remote.sh's capture_queue hands this script its
# whole submit_args as ONE shell word (run_cluster.sh joins several requested
# labels space-separated before making its single capture call, precisely so
# they land in the SAME pack -- see the header comment above), so several
# labels arrive here as one "$1", not as "$1 $2 $3". Word-splitting it is safe:
# every label in this project is a bare identifier or a plain path, never one
# containing whitespace.
read -r -a REQUESTED_ARGS_FILES <<< "$*"

# --lipid_coldsplit in the args file switches the grid to the other axis: whole chemical
# families of lipids leave training while every protein stays, so there is no held-out
# protein group and the grid iterates the four lipid sets instead. Keep the names in
# step with LIPID_COLDSPLIT_SETS (dataloader/sampler.py); one absent from there is
# rejected at parse time.
LIPID_COLDSPLIT_SETS_LIST=(sphingolipids phosphorus_free choline anionic)

# --family_only, bare (no value), in the args file switches the grid to a third axis:
# one model per family, trained AND validated on that family's own rows only (a warm,
# row-level random split inside the family -- dataloader/Dataloader.py:147-150,1461 --
# NOT a held-out-family cold split; see files/structural_pretrain_family_diagnosis.md's
# "central correction" for why this is a different regime from --double_coldsplit/
# --cold_split, not a variant of either). The grid still iterates PROTEIN_GROUPS (one
# job per family x seed, --groups/--no_groups apply normally, same group spelling as
# every other protein-side axis), but no protein is EXCLUDED from training -- the
# family named by the group IS the entire training pool -- so --excluded_groups is
# never appended; --family_only=<group> is appended instead. Originally only reachable
# through scripts/submit/structural_pretrain_solo.sh's bespoke per-family bash loop
# (needed there to chain a fresh stage-1 pretrain run before stage 2); once stage 1's
# checkpoint already exists on disk, each stage-2 (family, seed) job is an ordinary
# independent run and needs no chaining, which is what this grid path assumes.
#
# --random_split, bare (no value), in the args file switches the grid to a fourth axis:
# nothing is held out at all. Every other axis above answers its question by APPENDING a
# flag (--excluded_groups, --lipid_coldsplit, --family_only); this one is defined by
# appending none, which is why it needs a marker of its own -- an args file cannot
# suppress the --excluded_groups this script would otherwise add, since flags are
# applied in argv order and the appended one comes last. With no split flag,
# Dataloader._split_interactions takes its final branch: csvt.sample(frac=0.85) is
# train, the remaining 15% is halved label-by-label into validation and test, and
# new_train.py files the run under exclusion_set "random". There is no group axis to
# rotate, so the grid runs one pseudo-group ("random") x the seeds, and --groups/
# --no_groups are ignored for such a label exactly as they are for --lipid_coldsplit.
# What the runs are FOR: the warm end of the similarity-to-train axis, the anchor the
# cold-split numbers are read against (analysis/split_similarity_vs_metric.py). They are
# not a baseline to pick configurations on -- with every protein and every lipid in
# training both label marginals are free.

# --- per-label setup ----------------------------------------------------------
# Parallel arrays, one entry per requested label (index order == command-line
# order). experiment_record/job_name/submit_one below take a label index and
# read these instead of the single-label globals this script used to have.
LABEL_VARIANT=()
LABEL_ARGS_TEMPLATE=()
LABEL_COLD_SPLIT=()
LABEL_LIPID_COLDSPLIT=()
LABEL_FAMILY_ONLY=()
LABEL_FAMILY_ONLY_FIXED=()
LABEL_RANDOM_SPLIT=()
LABEL_LIPID_ISOLATION=()
LABEL_OUTPUT_ROOT=()
LABEL_WALLTIME=()
# One line per (label_index, group, seed), across ALL labels -- the combined
# stream the main loop below packs from, label boundaries included on purpose.
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

    # The shorter request only for configs that explicitly enable the fast path.
    # Per label: two labels in one call can disagree, and the pack that ends up
    # holding both takes the SLOWER of the two (see the max-walltime tracking in
    # the main loop below), never the base WALLTIME blindly.
    this_walltime="${WALLTIME}"
    if args_file_has_flag "${args_file}" --descriptors_head; then
        this_walltime="${DESCRIPTORS_HEAD_WALLTIME}"
        printf "Detected --descriptors_head in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --two_pair_descriptors_paths; then
        # Same no-encoder-towers cost class as --descriptors_head (Final_Layer
        # builds only the two NamedDescriptorHead instances + a small classifier) --
        # this branch was simply missing before, not a deliberate exclusion; closing
        # it here rather than leaving it to fall through to the full WALLTIME/
        # --fast_attention budgets below, which are sized for a real protein/lipid
        # encoder this config never builds.
        this_walltime="${DESCRIPTORS_HEAD_WALLTIME}"
        printf "Detected --two_pair_descriptors_paths in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --thematical_paths; then
        # Third sibling of the same sufficiency-test/no-towers shape (architecture/
        # thematic_descriptor_head.py) -- see THEMATICAL_PATHS_WALLTIME's own comment
        # in settings.sh for why it is a separate, independently re-measurable
        # variable rather than a literal reuse of DESCRIPTORS_HEAD_WALLTIME.
        this_walltime="${THEMATICAL_PATHS_WALLTIME}"
        printf "Detected --thematical_paths in %s; per-experiment walltime=%s.\n" \
            "${args_file}" "${this_walltime}"
    elif args_file_has_flag "${args_file}" --deepclip; then
        # Fourth sibling of the same no-towers shape, and the most extreme of them:
        # under --deepclip, InteractionClassification builds architecture/deepclip.py
        # and nothing else at all (1960 parameters at DeepCLIP's published settings,
        # 8960 at the widest sweep arm). Checked ahead of --fast_attention below for
        # the same reason --descriptors_head is: that branch's budget is sized for a
        # real protein/lipid encoder this config never constructs. See
        # DEEPCLIP_WALLTIME's own comment in settings.sh for why one number covers
        # every arm of the sweep despite their 4.6x spread in parameter count.
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

    # --family_only comes in two forms. BARE (no value) is the marker documented
    # below: the grid expands it into one job per PROTEIN_GROUPS entry, appending
    # --family_only=<group> itself. --family_only=<value>, spelled out in the file, is
    # a FIXED family instead -- nothing to expand, the template already names it, and
    # this is what a --lipid_isolation ladder scoped to one family (a "<family>__<key>"
    # block in dataloader/lipid_isolation_blocks.py) has to use: a bare marker would
    # let the grid iterate all nine groups and overwrite the fixed family with whichever
    # one it is currently on, once appended after the template's own line (last flag
    # wins). This grid still runs FIXED as one job x seed, not nine, and the flag stays
    # in the template untouched either way.
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

    # --lipid_isolation=<key> in the args file is the lipid axis addressed by distance
    # (dataloader/lipid_isolation_blocks.py). Unlike the bare --lipid_coldsplit marker
    # it already names its block, so there is nothing for the grid to expand: it runs
    # one pseudo-group, named the way new_train.py files the run, against the seeds. The
    # flag stays in the template -- the trainer takes it as written.
    this_lipid_isolation=""
    if args_file_has_flag "${args_file}" --lipid_isolation; then
        this_lipid_isolation="$(args_file_flag_lines "${args_file}" \
            | sed -nE 's/^--lipid_isolation=(.*)$/\1/p' | tail -1)"
        if [[ -z "${this_lipid_isolation}" ]]; then
            printf -- '--lipid_isolation needs a value (a key of LIPID_ISOLATION_BLOCKS) in %s.\n' \
                "${args_file}" >&2
            exit 2
        fi
        if (( this_cold_split )) || (( this_lipid_coldsplit )); then
            printf -- '--lipid_isolation and --cold_split/--lipid_coldsplit hold out '\
'different things; pick one (%s).\n' "${args_file}" >&2
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
        # Stripped like the other two markers: the trainer has no such flag, and must
        # not be handed one.
        this_args_template="$(printf '%s' "${this_args_template}" \
            | sed -E 's/(^|[[:space:]])--random_split([[:space:]]|$)/\1/g')"
    fi

    if (( this_cold_split )); then
        this_output_root="script_logs/${this_variant}_coldval_seeds01234"
        this_groups=("${COLD_TEST_GROUPS[@]}")
    else
        this_output_root="script_logs/${this_variant}_seeds01234"
        this_groups=("${PROTEIN_GROUPS[@]}")
    fi
    this_seeds=("${DEFAULT_SEEDS[@]}")
    if (( this_lipid_coldsplit )); then
        this_output_root="script_logs/${this_variant}_lipidsets"
        this_groups=("${LIPID_COLDSPLIT_SETS_LIST[@]}")
    fi
    if (( this_family_only )); then
        this_output_root="script_logs/${this_variant}_familyonly"
        if [[ -n "${this_family_only_fixed}" ]]; then
            # One job x seed, not nine: the family is already fixed in the template.
            this_groups=("${this_family_only_fixed}")
        else
            this_groups=("${PROTEIN_GROUPS[@]}")
        fi
    fi
    if (( this_random_split )); then
        # One pseudo-group, named for the directory new_train.py will file the run
        # under, so log path, run/ path and test_metrics/ path agree the way they do on
        # every other axis.
        this_output_root="script_logs/${this_variant}_random"
        this_groups=("random")
    fi
    if [[ -n "${this_lipid_isolation}" ]]; then
        this_output_root="script_logs/${this_variant}_iso${this_lipid_isolation}"
        this_groups=("iso${this_lipid_isolation}")
    fi
    if (( this_random_split )) && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # Same rule, same reason as the --lipid_coldsplit case just below: the override
        # names protein families, which is not this label's axis. Ignored, not fatal, so
        # one command can queue protein-axis and random-split labels together.
        printf -- '--random_split holds no group out; ignoring --groups/--no_groups '\
'for %s -- the single random-split grid will run.\n' "${args_file}" >&2
    elif (( this_lipid_coldsplit )) && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # Same rule as scripts/run_local.sh's --groups/--no_groups check: GROUPS_OVERRIDE
        # (run_cluster.sh's --groups/--no_groups) names protein families, which is the
        # OTHER axis for a --lipid_coldsplit label. It is IGNORED here rather than
        # applied -- applying it would replace LIPID_COLDSPLIT_SETS_LIST with family
        # names and submit --lipid_coldsplit=<family>, which read_lipid_coldsplit rejects
        # at run time for every single job.
        #
        # Ignored rather than fatal so that one command can queue protein-axis and
        # lipid-axis labels together: the flag narrows the protein-group labels and
        # passes over the lipid-set ones, instead of the whole submission (the valid
        # labels included) dying on the first --lipid_coldsplit label in the list. Said
        # out loud on stderr, not silently, because the caller asked to narrow something
        # and for this label nothing was narrowed.
        printf -- '--lipid_coldsplit runs over lipid sets, not protein groups; '\
'ignoring --groups/--no_groups for %s -- all %d lipid sets will run.\n' \
            "${args_file}" "${#this_groups[@]}" >&2
    elif [[ -n "${this_lipid_isolation}" ]] && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # A --lipid_isolation label runs one fixed group already named by its key (and,
        # when combined with a fixed --family_only=<value>, one fixed family too); a
        # protein-family override has nothing to narrow here.
        printf -- '--lipid_isolation names its own block; ignoring --groups/--no_groups '\
'for %s.\n' "${args_file}" >&2
    elif (( this_family_only )) && [[ -n "${this_family_only_fixed}" ]] \
        && [[ -n "${GROUPS_OVERRIDE}" ]]; then
        # Same reason: the family is already fixed in the template, so overriding
        # "groups" here would rename the output directory without changing what
        # actually trains -- confusing, not narrowing.
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
    LABEL_OUTPUT_ROOT+=("${this_output_root}")
    LABEL_WALLTIME+=("${this_walltime}")

    while IFS=$'\t' read -r group seed; do
        [[ -n "${group}" ]] || continue
        combined_pairs+="${label_index}"$'\t'"${group}"$'\t'"${seed}"$'\n'
    done < <(grid_pairs "${this_groups[*]}" "${this_seeds[*]}")
done

# TEST -> VAL mapping (see the table at the top). Only read in cold-split mode;
# shared across labels, since it is a property of the group rotation, not of
# any one config.
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
# The record layout is scripts/lib/pack_lib.sh's; both runners read it, so an
# experiment is described the same way whether it is run alone or in a pack, and
# both write the same tree. label_index selects which requested label this
# (group, seed) belongs to -- see LABEL_* above.
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
        # The "group" is the name of a lipid-class set, and it goes to its own flag;
        # excluded stays empty so no protein leaves training.
        excluded=""
        extra=" --lipid_coldsplit=${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID SET: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( family_only )) && [[ -n "${family_only_fixed}" ]]; then
        # The family is already spelled out in the template (--family_only=<value>);
        # nothing is appended, and if --lipid_isolation is ALSO set it stays in the
        # template too -- this is the "one fixed family, one fixed cold-lipid block"
        # combination a --lipid_isolation ladder scoped to that family needs.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="FAMILY_ONLY (fixed): ${family_only_fixed}"
        if [[ -n "${lipid_isolation}" ]]; then
            header+=" | LIPID ISOLATION: ${lipid_isolation}"
        fi
        header+=" | VARIANT: ${variant} | SEED: ${seed}"
    elif (( family_only )); then
        # "group" is the one family the whole table is restricted to (warm split
        # inside it, dataloader/Dataloader.py:147-150) -- nothing is EXCLUDED from
        # training, so excluded stays empty and --family_only carries the group
        # instead of --excluded_groups.
        excluded=""
        extra=" --family_only=${group}"
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="FAMILY_ONLY: ${group} | VARIANT: ${variant} | SEED: ${seed}"
    elif [[ -n "${lipid_isolation}" ]]; then
        # The block is named by the flag already in the template, so nothing is
        # appended; "group" is the directory name new_train.py will use.
        excluded=""
        output_dir="${output_root}/${group}"
        stem="${variant}_seed${seed}"
        header="LIPID ISOLATION: ${lipid_isolation} | VARIANT: ${variant} | SEED: ${seed}"
    elif (( random_split )); then
        # The axis defined by appending nothing: no --excluded_groups, no split flag of
        # any kind, so the loader's own last branch does the 85/7.5/7.5 random split and
        # new_train.py names the run "random" -- which is what "group" already is here.
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
# Built as an array so an empty GPU_PROPERTY/PROJECT omits the flag entirely.
# `if` blocks rather than `[[ ]] &&`: a false test as the last command would
# return 1 and `set -e` would abort the whole submitter.
oarsub_submit() {
    local job_name="$1" walltime="$2" out_prefix="$3" job_command="$4"
    local -a oarsub_args=(
        --name "${job_name}"
        -l "${OAR_RESOURCES},walltime=${walltime}"
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

# The OAR job name. It is what the progress table falls back to for a job whose
# output path OAR does not report, so a cold-split job has to keep naming its
# validation group here.
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
        "${out_base}${JOB_ID_TAG}%jobid%" "${job_command}"
}

submit_pack() {
    local pack_index="$1" spec="$2" pack_count="$3" pack_walltime_str="$4" pack_tag="$5" job_tag="$6"
    local job_walltime pack_dir job_command runner_env spec_file

    job_walltime="$(pack_job_walltime "${pack_count}" "${pack_walltime_str}" "${PACK_WALLTIME_PARALLEL}")"
    pack_check_walltime "${job_walltime}" "${MAX_WALLTIME}" || exit 2

    # The job's own stdout must NOT land on a "*_<tag><jobid>.out" path: that
    # pattern belongs to the per-experiment files the runner writes, and the
    # progress table turns every match into a row. Shared across labels rather
    # than one label's own output_root/_packs, since a pack can span several.
    pack_dir="script_logs/_cross_label_packs"
    mkdir -p "${pack_dir}"

    printf -v runner_env \
        'GPU_MODEL_GLOB=%q MIN_FREE_GPU_MIB=%q CPU_ONLY=%q JOB_ID_TAG=%q PACK_PARALLEL=%q GPU_MIB_PER_RUN=%q PACK_GPU_PERCENT=%q PACK_CPU_PER_RUN=%q PACK_MIN_FREE_GPU_MIB=%q PACK_HARDWARE_AUTO=%q PACK_SKIP_DONE=%q' \
        "${GPU_MODEL_GLOB}" "${MIN_FREE_GPU_MIB}" "${CPU_ONLY}" "${JOB_ID_TAG}" \
        "${PACK_PARALLEL}" "${GPU_MIB_PER_RUN}" "${PACK_GPU_PERCENT}" \
        "${PACK_CPU_PER_RUN}" "${PACK_MIN_FREE_GPU_MIB}" \
        "${PACK_HARDWARE_AUTO}" "${PACK_SKIP_DONE}"

    # Written to a file rather than base64-spliced onto the oarsub command
    # line: a full-size pack (PACK_SIZE=180 on kraken-cpu, several labels
    # sharing one pack) encodes past Linux's ~128 KiB single-argument limit,
    # which fails oarsub's execve with "Argument list too long" -- see
    # pack_spec_write_file's comment in pack_lib.sh. mktemp keeps concurrent
    # submitters (pack_index resets to 0 in each) from colliding on the name.
    spec_file="$(mktemp "${pack_dir}/pack${pack_index}_spec.XXXXXX")"
    pack_spec_write_file "${spec}" "${spec_file}"

    printf -v job_command \
        'cd %q && source %q && conda activate %q && %s bash scripts/launch/run_experiment_pack.sh %q' \
        "${PROJECT_DIR}" "${CONDA_SH}" "${CONDA_ENV}" \
        "${runner_env}" "${spec_file}"

    printf "Pack %d: %d experiment(s) [%s], walltime=%s.\n" \
        "${pack_index}" "${pack_count}" "${pack_tag}" "${job_walltime}"
    # OAR rejects any job name (-n) with characters outside a-z A-Z 0-9 _.- --
    # "+" (used above only for the human-readable pack_tag, to list every label
    # in a cross-label pack) is not in that set, so the job name uses "-" as
    # the label separator instead.
    #
    # OAR's jobs.job_name column is `character varying(100)` (hit in production:
    # 5 long descriptor labels packed together built a 139-char name and oarsub
    # died with a Postgres StringDataRightTruncation error, past the point of no
    # return -- the job was never created). A truncated name would collide
    # across different label combinations that happen to share a long common
    # prefix, so an over-length tag is cut and given an 8-hex-char digest of the
    # FULL tag instead -- short, unique per label combination, and stable
    # across re-submissions of the same combination (so the oarsub-command dedup
    # in cluster_queue_remote.sh's capture_queue still recognises it).
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
        "${job_command}"
}

# --- the grid -----------------------------------------------------------------
# The seed loop stays innermost per label (grid_pairs), so a pack of 5 is
# exactly one group's seeds and a pack of 9 spans groups at a fixed seed within
# one label -- both natural units to resubmit or cancel as a whole. Labels are
# concatenated after that, in command-line order, in combined_pairs above, so a
# pack only spans a label boundary once the label ahead of it in the stream has
# been exhausted -- filling PACK_SIZE takes priority over keeping one pack to
# one label.
submitted=0
experiments=0
pack_index=0
pack_count=0
pack_spec=""
# Empty means "no record added yet"; set to the first record's own label
# walltime and only ever raised after that -- see the comparison below. Never
# initialised to the base WALLTIME: a pack built entirely from --fast_attention
# labels must not inherit the slower default just because it once existed.
pack_walltime_str=""
declare -A pack_labels_seen=()
pack_labels_list=()

flush_pack() {
    (( pack_count > 0 )) || return 0
    local tag job_tag
    tag="$(IFS=+; printf '%s' "${pack_labels_list[*]}")"
    job_tag="$(IFS=-; printf '%s' "${pack_labels_list[*]}")"
    submit_pack "${pack_index}" "${pack_spec}" "${pack_count}" "${pack_walltime_str}" "${tag}" "${job_tag}"
    pack_index=$((pack_index + 1))
    submitted=$((submitted + 1))
    pack_count=0
    pack_spec=""
    pack_walltime_str=""
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
