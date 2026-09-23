# Exact sibling of geometric_edge_mlp_..._lcs_esm3_protunion14_prothid32.md (the LCS
# baseline for this architecture, one of this project's "four baselines"), ONE line
# added: --rotate_train_negatives. Every other flag copied verbatim -- see that file's
# own header for the architecture (protunion14, --protein_edge_mlp,
# --protein_hiddim=32, --bilinear_fusion) and ..._rim_ev28_rotneg.md's header for the
# full explanation of what --rotate_train_negatives changes and why it still respects
# --balanced_batches/--balanced_proteins within each epoch.
#
# LCS pairing of that DCS file: same architecture, --lipid_coldsplit instead of
# --double_coldsplit, so _add_rotating_negatives widens the negative pool by whatever
# chemistry this file's own --lipid_coldsplit excludes rather than by protein family --
# valid/test stay exactly as the base file samples them either way.
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

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics
--save_model

--balanced_batches
--balanced_proteins
--lipid_coldsplit
--rotate_train_negatives
