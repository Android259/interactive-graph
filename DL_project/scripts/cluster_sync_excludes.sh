#!/usr/bin/env bash
# Shared rsync exclude list for project transfers, used by BOTH
# scripts/update_clusters.sh (local -> clusters) and scripts/update_local.sh
# (clusters -> local). Keeping one list means the two directions cannot drift
# apart on caches, results, logs, and scheduler state. Direction-specific data
# rules stay in the callers: update_clusters uploads normal-sized data files;
# update_local does not download data.
#
# Sets the SYNC_EXCLUDES array.
#
# The project's own directories are anchored with a leading slash, so each
# pattern means "this directory AT THE PROJECT ROOT" and nothing else. An
# unanchored 'data/' would match every directory named data at any depth --
# including the ones inside stale copies left on a cluster -- and rsync never
# deletes an excluded path, so those copies would be protected forever and
# could never be cleaned up by the mirror sync.
#
# Only genuinely path-independent junk (build caches, editor droppings) stays
# unanchored, because it really can appear at any depth.
#
# Two separate questions, and rsync conflates them by default:
#   1. what to TRANSFER   -> SYNC_EXCLUDES
#   2. what to never DELETE on the far side -> SYNC_PROTECT
# By default --delete protects every excluded path, which means a stale tree on
# a cluster survives forever as soon as it contains a single __pycache__ or
# .DS_Store. Callers therefore pass --delete-excluded (so caches inside stale
# trees really go) together with SYNC_PROTECT, which re-protects exactly the
# project directories that must never be touched.
#
# SYNC_PROTECT is the safety net for --delete-excluded. Adding a pattern to
# SYNC_EXCLUDES without adding it here means it can be DELETED on the far side.

SYNC_EXCLUDES=(
    # any depth: caches and droppings
    --exclude='.git/'
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='.DS_Store'
    --exclude='.~lock*'
    --exclude='.pytest_cache/'

    # Scheduler state: it lives on the cluster and is managed by the queue
    # helper, so neither direction may overwrite or remove it.
    --exclude='/.bigfoot_job_queue/'
    --exclude='/.bigfoot_job_queues/'
    --exclude='/.kraken_job_queues/'
    --exclude='/.bigfoot_session_*'
    --exclude='/.kraken_session_*'

    # Results: produced on the cluster, and they travel back only through
    # wait_and_sync.sh, which merges several clusters into one local tree.
    --exclude='/run/'
    --exclude='/run_old_arch_layout/'
    --exclude='/test_metrics/'
    --exclude='/test_metrics_*/'
    --exclude='/models/'
    --exclude='/testmode_outputs/'
    --exclude='/graphics/'

    # Logs.
    --exclude='/script_logs/'

    # Aggregated tables, including the timestamped .bak_*/.backup copies -- a
    # metrics_summary*.csv pattern would miss those, they do not end in .csv.
    --exclude='/metrics_summary*'
    --exclude='/metrics_analysis*'
    --exclude='/feature_contributions*'

    # Bulk that training never imports.
    --exclude='/external/'
)

# Paths that must survive on the receiving side even though they are not
# transferred. Used together with --delete-excluded; without it these would be
# protected implicitly, but so would every cache inside a stale copy.
SYNC_PROTECT=(
    --filter='P /run/'
    --filter='P /run_old_arch_layout/'
    --filter='P /test_metrics/'
    --filter='P /test_metrics_*/'
    --filter='P /models/'
    --filter='P /testmode_outputs/'
    --filter='P /graphics/'
    --filter='P /script_logs/'
    --filter='P /metrics_summary*'
    --filter='P /metrics_analysis*'
    --filter='P /feature_contributions*'
    --filter='P /external/'
    --filter='P /.bigfoot_job_queue/'
    --filter='P /.bigfoot_job_queues/'
    --filter='P /.kraken_job_queues/'
    --filter='P /.bigfoot_session_*'
    --filter='P /.kraken_session_*'
    --filter='P /.git/'
)
