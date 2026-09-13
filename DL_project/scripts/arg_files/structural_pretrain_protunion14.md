
# Stage 1 counterpart of scripts/arg_files/structural_pretrain.md, adding
# --protein_descriptors= (the 14-name protunion14 union) so a stage-2 run that also
# sets it can actually load this checkpoint. The plain structural_pretrain.md
# checkpoint (models/structural_pretrain/random/seed0.pt) was trained with NO
# --protein_descriptors= at all, so its protein1 encoder's first-layer projections
# (q_proj/k_proj/v_proj) are shaped for a narrower per-node input; loading it into a
# stage-2 run that adds protunion14 fails with a PyTorch size mismatch of exactly 14
# (confirmed by running it: 68->82, 93->107) -- not fixable from the stage-2 arg file
# alone, since the mismatch is in weights already baked into the checkpoint. This
# file exists so that mismatch has a matching stage-1 checkpoint to load instead.
#
# --label=structural_pretrain_protunion14 (not plain "structural_pretrain"): saves to
# models/structural_pretrain_protunion14/random/seed0.pt, a separate file from the
# original -- this session's protunion14-specific pretrain, not a replacement for the
# baseline three arms' shared checkpoint.
#
# Every OTHER encoder-matching flag is identical to structural_pretrain.md, same
# requirement as that file's own header states: protein1's saved weights are only
# meaningful for the exact module structure they were saved with, and new_train.py's
# load_state_dict check refuses a mismatch loudly otherwise (which is exactly the
# error this file exists to avoid, for the input width specifically).
#
# --protein_descriptors= here does not interact with --structural_pretrain's masking
# objective: the mask targets protein_node_feature_count's 3-dim geometric columns
# (dataloader/Dataloader.py's _mask_residue_features), a separate set of columns from
# whatever --protein_descriptors= broadcasts -- confirmed no validate() rule in
# training/read_configuration.py rejects the combination.
#
# Launch this FIRST, once, before the matching stage-2
# structural_pretrain_family_unfrozen_protunion14.md can run (that file's own header
# names the exact checkpoint path this one produces).
#
# Not yet run.

--structural_pretrain
--save_model
--label=structural_pretrain_protunion14

--ep=120
--hiddim=64
--dropout=0.1

--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--fast_attention
--plm_compression_dim=64
--protein_edge_attention

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent
