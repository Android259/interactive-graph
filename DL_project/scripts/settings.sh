#!/usr/bin/env bash
# Everything about this project you might want to change without reading code:
# which protein groups exist, which seeds are the default, how long a job may
# run, and how often the watcher refreshes.
#
# `source` this file. Every value keeps ${VAR:-default} form, so an environment
# variable still wins for a one-off; this is where the DEFAULT lives.
#
# Read by scripts/lib/cluster_common.sh (and through it by everything on the
# cluster path), by scripts/run_local.sh, and by launch/submit_grid.sh.

# ---------------------------------------------------------------------------
# Watching
# ---------------------------------------------------------------------------

# Seconds between refreshes of scripts/wait_and_sync.sh. Each round makes about
# six round trips through the gricad jump host per cluster, so this is the floor
# on how long a round takes, not a target.
POLL_SECONDS="${POLL_SECONDS:-60}"

# How far back the TRAIN BA reader looks for TensorBoard event files. Everything
# older is left out of the recent-events directory, which is what keeps a round
# from re-reading the hundreds of past runs sharing each group name.
EVENT_LOOKBACK_MINUTES="${EVENT_LOOKBACK_MINUTES:-480}"

# ---------------------------------------------------------------------------
# Job size
# ---------------------------------------------------------------------------

# Walltime budget of ONE experiment. A packed job multiplies it by its depth.
# Measured run time is 75-300 min (median ~140), so five hours is already tight
# at the tail.
WALLTIME="${WALLTIME:-5:00:00}"

# The same budget for a --fast_attention configuration, which removes the
# quadratic cross-sample attention work. One number for every way of launching,
# so a config cannot get a different walltime depending on how it was started.
FAST_ATTENTION_WALLTIME="${FAST_ATTENTION_WALLTIME:-0:25:00}"

# How many jobs may sit WAITING in OAR at once. The cluster's own copy of this
# (<queue>/max_waiting) wins when it exists, so two computers draining the same
# queue cannot use two different limits.
MAX_WAITING_JOBS="${MAX_WAITING_JOBS:-50}"

# ---------------------------------------------------------------------------
# What gets run
# ---------------------------------------------------------------------------

# Seeds every excluded group is run on unless --seeds says otherwise.
DEFAULT_SEEDS=(0 1 2 3 4)

PROTEIN_GROUPS=(
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

# The same nine, in the order the cold-split series rotates its TEST group. The
# order is not cosmetic: experiments are packed into OAR jobs in the order they
# are generated, so changing it changes which experiments share a job. It matches
# the TEST -> VAL table in the header of launch/submit_grid.sh, which
# is where the reasoning for the pairing lives.
COLD_TEST_GROUPS=(
    "lipocalin"
    "CRAL-TRIO"
    "START"
    "IP_trans"
    "scp2"
    "LBP_BPI_CETP"
    "OSBP"
    "GLTP"
    "ML"
)

# Names are compared in read_excluded_groups' normalized form: case-insensitive,
# with - and _ interchangeable, so cral_trio and CRAL-TRIO are the same group.
# The same spellings that work for --excluded_groups therefore work on the
# command line here.
normalize_group_name() {
    local name="${1,,}"
    printf '%s' "${name//-/_}"
}
