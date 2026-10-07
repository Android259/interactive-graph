# = ..._prothid32_subclass (единственный прогнанный GE на --lipid_subclass,
# полное покрытие 9 блоков: test BA 0.568+-0.090, F1 0.473+-0.235) +
# --dissimilar_negative_mining --dissimilar_negative_share=1.0. Та же проверка
# как в ge_s15_prothid32_hid64_noreg_dnm.md / mlp_s15_nomb_hid128_3mlp_dnm.md:
# TRAIN-негативы каждого белка тянутся максимально ДАЛЁКИМИ по Танимото от его
# собственных позитивов, не равномерно (dataloader/AGENTS.md "Negative
# Sampling"). balanced_proteins уже в базе, квота на группу не меняется.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics
--save_model

--balanced_batches
--balanced_proteins
--dissimilar_negative_mining
--dissimilar_negative_share=1.0
--lipid_subclass
