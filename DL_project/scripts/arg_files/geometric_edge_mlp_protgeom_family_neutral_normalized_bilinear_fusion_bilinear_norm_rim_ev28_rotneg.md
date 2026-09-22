# Exact sibling of geometric_edge_mlp_..._rim_ev28.md (the DCS baseline for this
# architecture, one of this project's "four baselines" -- files/split_similarity_four_
# baselines_and_deepclip.md), ONE line added: --rotate_train_negatives. Every other
# flag is copied verbatim. This file's header carries the full explanation for the
# whole _rotneg sibling family added this session (rim_ev28, lcs_esm3_protunion14_
# prothid32, lipprop, lcs_protbind6) -- the other three just point back here.
#
# WHAT THE FLAG CHANGES
#
# Without it, a run's negatives are one fixed random draw -- negatives_per_positive
# per positive -- made once at dataset-build time and replayed identically every
# epoch for the whole run. With --rotate_train_negatives (training/read_configuration.py,
# dataloader/sampler.py's RotatingNegativeBatchSampler, dataloader/Dataloader.py's
# _add_rotating_negatives):
#   - TRAIN is first widened to every eligible negative NOT already drawn by the
#     initial sampler (still excluding whatever this file already excludes -- the
#     held-out DCS family/chemistry -- and never touching valid/test), so more
#     negatives exist to rotate through than the base file ever sees.
#   - that enlarged pool is permuted once (seeded, reproducible), and each epoch takes
#     the next consecutive chunk of the permutation (training/new_train.py calls
#     rotating_sampler.set_epoch(epoch) before iterating the loader each epoch, the
#     same pattern as DistributedSampler.set_epoch), wrapping back to the start once a
#     pass completes.
#   - chunk size is not overridden here (--rotate_negatives_per_epoch left unset), so
#     it defaults to negatives_per_positive * train_positives -- same per-epoch
#     class ratio and batch cost as the base file; only WHICH negatives fill each
#     epoch changes.
#   - epochs_per_pass = ceil(n_negatives / chunk): with --ep=120, the run should cycle
#     through the whole widened pool several times, instead of training all 120
#     epochs on the base file's single fixed draw.
#
# Composes cleanly with this file's --balanced_batches/--balanced_proteins: the
# rotating sampler delegates batch composition to the same class-balanced sampler over
# each epoch's active rows, so balancing still applies within each epoch's rotated
# slice.
#
# First arg files in the project to use --rotate_train_negatives -- no prior run on
# this flag to compare against; compare each _rotneg file only against its own base
# file.
#
# Not yet run.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
--rotate_train_negatives
