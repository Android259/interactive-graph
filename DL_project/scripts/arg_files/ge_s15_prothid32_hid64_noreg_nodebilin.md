# = ge_s15_prothid32_hid64_noreg + --node_bilinear_fusion. Узловой Hadamard-аналог
# уже работающего пулированного --bilinear_fusion -- добавляет произведение
# белок/липид ДО пулинга как доп. канал (не заменяет residual, в отличие от
# _forcedint, а добавляется рядом). Проверяет, не теряется ли по нодам сигнал,
# который пулинг усредняет раньше, чем нужно.
# Обоснование: files/ge_architecture_proposals_species15.md §5.

--ep=120
--fast_attention

--hiddim=64
--node_bilinear_fusion

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
