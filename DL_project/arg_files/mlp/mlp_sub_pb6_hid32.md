# = dh_lcs_family_neutral_pb6_lipprop_subclass с --descriptor_mlp вместо --descriptors_head.
# Поиск архитектуры mlp на оси --lipid_subclass (9 блоков). Отличие: hid32.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_subclass
