# mlp_s15_mbw_hid32, greedy descriptor selection, 16 names. Mirrors dh_s15_mbw_hid32_d16.
# План: files/descriptors_head_species15_run_plan.md §5

--ep=120
--fast_attention
--marginal_balance_weight

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy,aromatic_share_rim,aromatic_contact_min,hbond_match_min

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
