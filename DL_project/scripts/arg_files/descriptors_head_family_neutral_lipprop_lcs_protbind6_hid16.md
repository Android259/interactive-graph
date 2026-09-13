# --hiddim=16 instead of 8 against descriptors_head_family_neutral_lipprop_lcs_
# protbind6.md -- see that file's own header for the six-descriptor reasoning, left
# untouched here.
#
# descriptors_head has no separate --protein_hiddim/--lipid_hiddim split the way
# geometric_edge does (NamedDescriptorHead runs self-attention over ALL named tokens,
# lipid and protein alike, in one shared width -- architecture/named_descriptor_head.py)
# -- --hiddim here is the only capacity knob, and it widens both sides at once. Same
# motivation as the geometric_edge ..._protbind6_prothid16/32.md pair: protbind6 raises
# --descriptor_names from 11 to 17 tokens while leaving hiddim=8 untouched, so this
# checks whether the wider token set needs more room to attend over, this time with no
# way to isolate protein from lipid width. 16 divides HEADS=8 (the architecture's
# default self-attention head count), so no --HEADS change is needed alongside it.
#
# Not yet run.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=16

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
