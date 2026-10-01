# = ge_s15_prothid32_hid64_noreg + те же две величины, но ТОЛЬКО через произведение
# с пулированным белком (--lipid_head_descriptors -> ForcedInteraction, skip-пути нет,
# read_configuration.py:1566-1584). Сильная форма "подтолкнуть к взаимодействию": эти
# столбцы физически не могут дойти до классификатора без белка, в отличие от обычного
# broadcast-а в _liptail2.
# Пара к _liptail2: один и тот же вход, разный способ его пропустить. Если выигрыш даёт
# только эта версия -- дело во взаимодействии, если обе -- в самих столбцах.
# Сравнивать с: _liptail2 и с базой.
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
--lipid_head_descriptors=tail_double_bond_position,experimental_lipid_volume
