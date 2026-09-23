# Exact sibling of descriptors_head_family_neutral_lipprop.md (the DCS baseline for
# this architecture, one of this project's "four baselines"), ONE line added:
# --rotate_train_negatives. Every other flag copied verbatim -- see
# ..._rim_ev28_rotneg.md's header (same session, same flag, same "four baselines" set)
# for the full explanation of what --rotate_train_negatives changes and why it still
# respects this file's --balanced_batches/--balanced_proteins within each epoch.
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
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--save_model_in_dynamics
--save_model

--balanced_batches
--balanced_proteins
--double_coldsplit
--rotate_train_negatives
