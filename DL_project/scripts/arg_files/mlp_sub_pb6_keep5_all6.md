# = mlp_sub_pb6_keep5 + 3 парных и 3 карманных (кандидаты по абляции mlp_sub_pb6_all70,
# files/mlp_all70_subclass_ablation.md §3). Сравнивать с mlp_sub_pb6_keep5 на тех же 40 парах.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=buriedness_q50,aromatic_share,aromatic_share_rim,depth_q10,ev14_q10,tail_elongation_fit,hydropathy_rim_match,aromatic_contact_min,basic_share_rim,pocket_packing_density,pocket_elongation

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_subclass
