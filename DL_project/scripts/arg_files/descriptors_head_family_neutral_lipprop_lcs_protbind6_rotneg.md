# Exact sibling of descriptors_head_family_neutral_lipprop_lcs_protbind6.md (the LCS
# baseline for this architecture, one of this project's "four baselines"), ONE line
# added: --rotate_train_negatives. Every other flag copied verbatim -- see that file's
# own header for the thirteen protein descriptor names and --lipid_propensity_weight,
# and ..._rim_ev28_rotneg.md's header for the full explanation of what
# --rotate_train_negatives changes.
#
# LCS pairing of lipprop_rotneg.md's DCS file, same architecture.
#
# Not yet run.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
--rotate_train_negatives
