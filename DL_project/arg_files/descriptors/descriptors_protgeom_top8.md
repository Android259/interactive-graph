--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pocket_descriptors
--pair_descriptors
--descriptors_head
--descriptor_names=pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
