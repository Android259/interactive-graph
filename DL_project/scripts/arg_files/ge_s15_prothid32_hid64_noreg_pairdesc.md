# = ge_s15_prothid32_hid64_noreg_nobilin + --pair_descriptors с тем же узким набором
# произведений, что в _lipprod. Второй, независимый путь к той же пустой клетке: здесь
# произведения идут через отдельную пулированную голову (NamedDescriptorHead, её
# включает --descriptor_names рядом с --pair_descriptors), а не broadcast-ом на узлы.
# --descriptor_names обязателен ещё и потому, что иначе --pair_descriptors требует
# --pocket_descriptors (read_configuration.py:2833), а тот в этой ветке подаёт
# НЕНОРМИРОВАННЫЕ значения: set_pocket_descriptor_normalization вызывается только под
# rnabang_frozen_node_adapter (new_train.py:102), который здесь не ставится.
# ВАЖНО: сравнивать с _nobilin, НЕ с базой -- bilinear здесь снят по необходимости.
--ep=120
--fast_attention
--hiddim=64
--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent
--protein_edge_mlp
--protein_hiddim=32
--save_model_in_dynamics
--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
--pair_descriptors
--descriptor_names=volume_fit,depth_bulk_match,chain_extent_gap
