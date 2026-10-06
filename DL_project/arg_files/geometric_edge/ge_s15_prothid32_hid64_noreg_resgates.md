# = ge_s15_prothid32_hid64_noreg + --attention_residual_gates. ReZero-стиль: каждый
# под-блок (self-attention/FFN x2 стороны, cross-attention/FFN x2 стороны) получает
# обучаемый скаляр-вентиль, инициализированный в ноль -- блок стартует как identity
# и учится включать себя постепенно, вместо полной residual-силы с первой эпохи.
# Обоснование и риск (сжатие разброса по сидам, не сдвиг среднего, по аналогии с
# третьим слоем MLP): files/history/geometric_edge.md,
# files/results/mlp_s15_architecture_sweep.md §7.

--ep=120
--fast_attention

--hiddim=64
--attention_residual_gates

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
