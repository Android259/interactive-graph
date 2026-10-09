# = ge_s15_prothid32_hid64_noreg + ГОТОВЫЕ ПАРНЫЕ произведения на узлы липидной ветки.
# Закрывает пустую клетку: --pair_descriptors выключен во всех 30 labels ge_s15*, то есть
# 14 предрассчитанных парных величин в эту ветку не доходили ни разу. Путь через
# --lipid_descriptors (он принимает парные имена каталога) выбран вместо
# --pair_descriptors: тот конфликтует с --bilinear_fusion (read_configuration.py, validate()) и
# потребовал бы снять базовый флаг, то есть сравнение перестало бы быть парным.
# Набор: depth_bulk_match -- ровно измеренное взаимодействие (depth_q10 x размер липида,
# rho -0.45..-0.38, files/proposals/species15_where_to_go_next.md §2.3); volume_fit -- объём кармана
# x объём липида; chain_extent_gap -- знаковая физическая разница "достаёт ли полость до
# конца цепи".
# Читать по within-cell метрике, НЕ по пулированной BA (§2.1 там же).
# Сравнивать с: ge_s15_prothid32_hid64_noreg (BA 0.902 / F1 0.861).
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
--save_model_in_dynamics
--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
--lipid_descriptors=volume_fit,depth_bulk_match,chain_extent_gap
