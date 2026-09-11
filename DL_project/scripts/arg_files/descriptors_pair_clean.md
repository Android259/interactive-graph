--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=aromatic_contact,hbond_match,volume_fit,buriedness_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match
--zscore

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
