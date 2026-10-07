# = ge_s15_prothid32_hid64_noreg (лучший GE на groups_species15 по test BA/F1:
# 0.902/0.861, files/history/geometric_edge.md §4-5) + --dissimilar_negative_mining
# --dissimilar_negative_share=1.0. Та же проверка как в mlp_s15_nomb_hid128_3mlp_dnm.md:
# TRAIN-негативы каждого белка тянутся максимально ДАЛЁКИМИ по Танимото от его
# собственных позитивов (dataloader/AGENTS.md "Negative Sampling"), а не
# равномерно. share=1.0 -- вся масса на самых дальних кандидатах. balanced_proteins
# уже в базе, квота на группу не меняется.

--ep=120
--fast_attention

--hiddim=64

--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--save_model
--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--dissimilar_negative_mining
--dissimilar_negative_share=1.0
--lipid_species_coldsplit=0.15
