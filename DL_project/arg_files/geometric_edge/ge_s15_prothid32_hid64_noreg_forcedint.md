# = ge_s15_prothid32_hid64_noreg (лучший на species15, test BA 0.902+-0.011) +
# --cross_attention_forced_interaction. Заменяет residual-апдейт cross-attention
# (lip = lip + lip_outs, всегда переживает вырождение внимания в identity) на
# ForcedInteraction -- произведение без skip-альтернативы, апдейт узла обязан
# зависеть от партнёра. Обоснование: files/history/geometric_edge.md

--ep=120
--fast_attention

--hiddim=64
--cross_attention_forced_interaction

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
--lipid_species_coldsplit=0.15
