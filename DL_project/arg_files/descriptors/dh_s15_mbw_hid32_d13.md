# dh_s15_mbw_hid32_d11 + basic_share_rim, occupancy (жадный отбор по силе эффекта).
# План: files/history/descriptor_models.md

--ep=120
--fast_attention
--marginal_balance_weight

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--negatives_per_positive=5
--lipid_species_coldsplit=0.15
