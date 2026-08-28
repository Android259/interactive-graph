--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pocket_descriptors
--pair_descriptors
--descriptors_head
--descriptor_names=occupancy,volume_fit,chain_extent_gap,aromatic_contact,hbond_match,hbond_match_min,depth_bulk_match

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit