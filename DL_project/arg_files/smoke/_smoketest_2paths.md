--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pocket_descriptors
--two_pair_descriptors_paths

--good_descriptors=chain_extent_gap,volume_fit,
                aromatic_contact,hbond_match,tail_elongation_fit,occupancy

--bad_descriptors=buriedness_q50,depth_q10,ev14_q50,hydropathy_rim,
                polar_share,aromatic_share,
                pocket_elongation,pocket_extent,pocket_flatness,
                unsaturation,hbond,heavy,tail_count,chain


--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
