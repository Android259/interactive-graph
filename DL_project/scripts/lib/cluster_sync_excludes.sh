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
    # Exceptions, and they are the files that change when the dataset (or the data-prep
    # code) does rather than when the model does, so a code-only sync would leave the
    # cluster reading an older table -- or an older lipid_graphs/, or a missing build
    # script -- than the code expects. Not a wrong number but a dead run: the loader
    # opens the table by name, LipidIsomerGraphBuilder raises FileNotFoundError/KeyError
    # for a graph_id or column the cluster's copy does not have yet (this is exactly how
    # a stale data/lipid_graphs/ was found: --lipid_graph_isomers jobs crashed on
    # KeyError: 'chain_rank' because the cluster still had the pre-chain_rank CSVs), and
    # the per-run preflight cache builders (data/build_pair_descriptor_cache.py etc.)
    # simply are not there to run. Together about 160 MB, against the 3.8 GB the
    # exclusion is there for:
    #   the interaction tables themselves;
    #   the compact Tanimoto artifacts, whose manifests name the table they were built
    #     from and which the loader refuses when that name or timestamp does not match;
    #   the GRAB pair-graph edges, indexed by the table's row positions;
    #   data/*.py -- these are code (the build_*.py cache/graph generators), not data;
    #     excluding them only because they live under data/ was the bug behind the
    #     KeyError above, so they sync like any other .py file in the project;
    #   data/lipid_graphs/ -- the per-molecule isomer-graph CSVs build_lipid_isomer_
    #     graphs.py writes, read directly by LipidIsomerGraphBuilder every --lipid_graph_
    #     isomers run; regenerated on kraken-cpu (scripts/tools/lipid_graphs_on_kraken.sh)
    #     and needs to reach every OTHER cluster too, not just the one it was built on;
    #   data/graphs/ -- per-protein coarse_graph_nodes/links.csv, pocketness.pdb and
    #     geometric_transformer_nodes.csv (residue frames for --geometric_transformer/
    #     --protein_edge_attention/--protein_edge_mlp). Was excluded like the rest of
    #     data/, which does not just risk a stale copy: load_protein_graph_tensor_cache
    #     (dataloader/protein_graph_tensor_cache.py) rejects protein_graph_tensors.pt
    #     outright the moment ANY recorded source's mtime_ns does not match the file on
    #     disk, and an independently-timestamped copy of data/graphs/ never matches the
    #     mtimes protein_graph_tensors.manifest.json recorded when the cache was built --
    #     so every run silently fell back to the slow uncached per-protein CSV read
    #     instead of raising, the only visible symptom being --protein_edge_attention/
    #     --protein_edge_mlp jobs failing with "require protein residue frames";
    #   data/protein_graph_tensors* -- the cache itself (plus its --no_protein_geometry
    #     variant and both .manifest.json files), for the same reason as data/lipid_
    #     graphs/ above: rebuilt locally, it has to reach every cluster, not sit excluded
    #     next to the source files whose mtimes it is keyed on.
    # Order matters: rsync takes the first matching rule, so the includes have to stand
    # before the exclusion they carve out of.
    --include='/data/'
    --include='/data/Processed_*.csv'
    --include='/data/Tanimoto_compact*'
    --include='/data/grab_pair_graph_edges.csv'
    --include='/data/*.py'
    # Self-validating (dataloader/pair_descriptor_cache.py's store_is_current() embeds
    # every source file's size/mtime_ns in the JSON itself and checks it fresh on every
    # load), so shipping a copy built on this machine is never a wrong answer on the
    # far side -- at worst its recorded sources don't match the cluster's copies (a
    # table/protein-graph edit that has not round-tripped yet) and the loader falls
    # back to building it there, exactly as before this include existed. Worth carrying
    # unlike the rest of data/: a few hundred KB, against the single-threaded RDKit/
    # pocket-parse pass (minutes on the full interaction table -- GRICAD kills anything
    # over 600s of CPU on a login node, which is what motivated this) that a from-
    # scratch remote build otherwise costs on every table change.
    --include='/data/pair_descriptor_cache_*.json'
    --include='/data/lipid_graphs/'
    --include='/data/lipid_graphs/**'
    --include='/data/graphs/'
    --include='/data/graphs/**'
    --include='/data/protein_graph_tensors*'
    --exclude='/data/**'
    --exclude='/data/'

    # Bulk that training never imports -- with one carve-out, on the same
    # include-before-exclude pattern as data/ above.
    #
    # architecture/protein_edge_geometry.py builds its relative-orientation
    # quaternions with rigid_utils.Rotation, which lives in the RNA-BAnG
    # submodule. That import is lazy (only --edge_attention / --edge_mlp reach
    # it), so an unsynced external/ is no longer fatal for every run -- but a
    # structured-edge config still cannot run on a cluster that does not have
    # the file. It is ~50 KB of pure python against the hundreds of MB this
    # exclusion exists for.
    --include='/external/'
    --include='/external/RNA-BAnG/'
    --include='/external/RNA-BAnG/data/'
    --include='/external/RNA-BAnG/data/*.py'
    --exclude='/external/**'
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
    # As for /data/** above: now that rsync descends into external/ to carry
    # rigid_utils.py, every OTHER file under it is a --delete-excluded candidate.
    # Without this line a sync wipes the cluster's external/molformer.
    --filter='P /external/**'
    --filter='P /data/Pretrained MoLFormer/'
    --filter='P /data/esm3_checkpoint/'
    --filter='P /.bigfoot_job_queue/'
    --filter='P /.bigfoot_job_queues/'
    --filter='P /.kraken_job_queues/'
    --filter='P /.bigfoot_session_*'
    --filter='P /.kraken_session_*'
    --filter='P /.git/'
)
