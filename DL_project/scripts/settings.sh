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
# Measured on Kraken 2026-08-19: 120 epochs of the fast-attention model take about
# 22 minutes per run with four runs sharing one H100. 25 minutes left a 12% margin,
# which was enough only while the card ran four at a time; at eight the runs contend
# for it and each one slows down -- that is why this was raised to 35 rather than
# staying at 25.
# Trimmed back to 20 (2026-09-04): the family_neutral bilinear_fusion grid actually
# run overnight (2026-09-03/04) measured training_duration_sec of 300-850s (5-14 min)
# at the CURRENT pack depth (2 on Bigfoot, 4 on Kraken, per cluster_common.sh) --
# 20 minutes still leaves >=30% margin over the observed max. This does not
# override the 2026-08-19 finding above: if pack depth is ever pushed past what
# cluster_common.sh currently sets (the 8-way attempt that motivated 35 was
# reverted as saturating), re-measure before trusting 20 again, since contention
# at higher packing was exactly what ate the margin last time.
FAST_ATTENTION_WALLTIME="${FAST_ATTENTION_WALLTIME:-0:20:00}"

# --descriptors_head budget: this is a ~1000-parameter model (only
# architecture/pair_descriptor_head.py's self-attention head + a small
# classifier, no protein/lipid encoders at all), not the fast-attention full
# model FAST_ATTENTION_WALLTIME above is sized for -- using that number here
# means asking for 35 minutes for a run that needs a fraction of it. Measured
# from metrics_summary.csv (385 completed descriptors_* runs,
# training_sec_per_epoch): 2.75-5.96s/epoch, mean 3.86s; at 120 epochs the
# slowest observed run is ~12 minutes of training alone. 20 minutes covers that
# plus data-loading/embedding-cache warm-up overhead with real margin, checked
# per label ahead of the more general --fast_attention branch below (a config
# can set both; descriptors_head is the more specific and correct budget when
# it does).
DESCRIPTORS_HEAD_WALLTIME="${DESCRIPTORS_HEAD_WALLTIME:-0:20:00}"

# --thematical_paths budget: same cost class as --descriptors_head (Final_Layer
# builds only architecture/thematic_descriptor_head.py's ~4-5K-parameter head, no
# protein/lipid encoders at all -- see files/thematic_interaction_architecture.md).
# No thematical_paths-specific training_sec_per_epoch rows exist yet in
# metrics_summary.csv, so this borrows DESCRIPTORS_HEAD_WALLTIME's measured budget
# rather than guessing a different number; kept as its OWN variable (not a literal
# reuse of DESCRIPTORS_HEAD_WALLTIME) so it can be re-measured and retuned
# independently once real thematical_paths runs exist, the same way
# FAST_ATTENTION_WALLTIME and DESCRIPTORS_HEAD_WALLTIME above were each measured
# and tuned on their own label's actual runs rather than sharing one number.
THEMATICAL_PATHS_WALLTIME="${THEMATICAL_PATHS_WALLTIME:-0:20:00}"

# --deepclip budget: the fourth member of the same no-encoder-towers cost class.
# InteractionClassification builds architecture/deepclip.py and NOTHING else under
# this flag -- no protein encoder, no lipid encoder, no cross-attention, no
# Final_Layer -- so the model is 1960 parameters at DeepCLIP's published settings
# (600 of convolution + 1360 of BLSTM) and 8960 at the widest arm of the current
# sweep (deepclip_f8_normal_mean_ep120). That whole 1960-8960 range sits between
# --descriptors_head's ~1000 and --thematical_paths' ~4-5K, which is why one number
# covers all five arm files rather than each getting its own: the parameter count
# varies 4.6x across them, but what varies with it is a 5-to-40-channel LSTM input,
# i.e. a few hundred extra multiply-accumulates per timestep on a model whose per
# epoch cost is dominated by the dataloader, not by its matmuls.
#
# 20 minutes is BORROWED from DESCRIPTORS_HEAD_WALLTIME's measured budget (385
# completed runs, 2.75-5.96 s/epoch, ~12 min of training at 120 epochs), not measured
# on deepclip runs -- none exist yet. Kept as its own variable for exactly the reason
# THEMATICAL_PATHS_WALLTIME above is: so it can be retuned on its own label's real
# runs. The specific reason it might NOT hold, and the thing to check first if these
# jobs hit the wall: DeepCLIP is the only member of this cost class with a recurrent
# layer, and its BLSTM is sequential over the molecule's characters (26-165 of them,
# up to 165 kernel launches per direction per batch that cannot be parallelised away).
# A --family_only job trains on one family's 240-2400 rows, so at batch 16 that is
# 15-150 batches per epoch; the arithmetic says this stays well inside 20 minutes, but
# arithmetic is not a measurement.
DEEPCLIP_WALLTIME="${DEEPCLIP_WALLTIME:-0:20:00}"

# How many jobs may sit WAITING in OAR at once. The cluster's own copy of this
# (<queue>/max_waiting) wins when it exists, so two computers draining the same
# queue cannot use two different limits.
MAX_WAITING_JOBS="${MAX_WAITING_JOBS:-50}"

# How many times launch/run_cluster.sh's --graphics/--summarize claim loop and
# wait_and_sync.sh's check_pending_reports() each retry a label whose
# generate_label_report.sh call failed, before giving up on it. Both restore
# the marker (not delete it) on failure so a transient blip gets retried --
# but generate_label_report.sh only READS existing test_metrics/dynamics
# files, it never resubmits the training job, so a label whose job never
# produced usable data fails the SAME way forever: without a cap, every
# unrelated future --graphics/--summarize invocation (or wait_and_sync.sh
# round) retries it again, forever, printing the same failure with no signal
# that it will never succeed. Past MAX_REPORT_FAILURES the marker is parked as
# "<label>.report.gaveup" instead of being restored -- still on disk, not
# auto-retried, rename it back to "<label>.report" by hand once the actual
# problem (usually: resubmit that label's training) is fixed.
MAX_REPORT_FAILURES="${MAX_REPORT_FAILURES:-3}"

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
