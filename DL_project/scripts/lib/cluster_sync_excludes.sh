#!/usr/bin/env bash
# Shared rsync exclude list for project transfers, used by scripts/tools/sync_project.sh
# in both directions. One list means the two directions cannot drift apart on
# caches, results, logs and scheduler state. The direction-specific data rules
# stay in that script: going up it sends normal-sized data files, going down it
# skips data/ entirely.
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

    # Data directory: embeddings and datasets (3.8 GB locally). Already present on
    # clusters from initial setup; training reads it from there. Excluding it keeps the
    # per-run sync 10x faster over the slow gricad proxy.
    #
    # Three exceptions, and they are the files that change when the dataset does rather
    # than when the model does, so a code-only sync would leave the cluster reading an
    # older table than the code expects -- which is not a wrong number but a dead run,
    # since the loader opens the table by name. Together about 25 MB, against the 3.8 GB
    # the exclusion is there for:
    #   the interaction tables themselves;
    #   the compact Tanimoto artifacts, whose manifests name the table they were built
    #     from and which the loader refuses when that name or timestamp does not match;
    #   the GRAB pair-graph edges, indexed by the table's row positions.
    # Order matters: rsync takes the first matching rule, so the includes have to stand
    # before the exclusion they carve out of.
    --include='/data/'
    --include='/data/Processed_*.csv'
    --include='/data/Tanimoto_compact*'
    --include='/data/grab_pair_graph_edges.csv'
    --exclude='/data/**'
    --exclude='/data/'

    # Bulk that training never imports.
    --exclude='/external/'

    # Pretrained weights, not project data. Both are read only by the scripts that
    # BUILD the embedding stores (preprocessing/embed_isomeric_smiles_molformer.py,
    # frozen_embedding.py, the ESM3 embedding builders); training reads the built
    # artefacts -- data/embedding_ESM3*/ and lipid_SMILES_embedding_deterministic.* --
    # and never opens these.
    #
    # Excluded for a second and stronger reason than size: the authoritative MoLFormer
    # checkpoint is the one already on the cluster. A local copy fetched to rebuild an
    # embedding store is not necessarily the same weights, and an unexcluded mirror
    # would push it over the real one. Both entries are in SYNC_PROTECT below so
    # --delete-excluded cannot remove the cluster's copies either.
    --exclude='/data/Pretrained MoLFormer/'
    --exclude='/data/esm3_checkpoint/'

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
    # The directory AND everything in it. The bare rule protects only the directory
    # entry, which was enough while data/ was excluded outright -- rsync never
    # descends into an excluded directory, so nothing inside was a deletion
    # candidate. Now that the interaction table and the Tanimoto artifacts are
    # carved out of that exclusion, rsync does descend, and with --delete-excluded
    # every other file in data/ becomes one: without this line a sync wipes the
    # cluster's embeddings, the 3.8 GB the exclusion exists to avoid resending.
    --filter='P /data/'
    --filter='P /data/**'
    --filter='P /external/'
    --filter='P /data/Pretrained MoLFormer/'
    --filter='P /data/esm3_checkpoint/'
    --filter='P /.bigfoot_job_queue/'
    --filter='P /.bigfoot_job_queues/'
    --filter='P /.kraken_job_queues/'
    --filter='P /.bigfoot_session_*'
    --filter='P /.kraken_session_*'
    --filter='P /.git/'
)
