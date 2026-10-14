# = mlp_s15_nomb_hid128_3mlp, одна правка: выброшены z-scored признаки.
#
# ЧТО УБРАНО И ПОЧЕМУ. Из --descriptor_heads выброшены признаки, которые считаются
# от СТАНДАРТИЗОВАННЫХ входов: aromatic_contact_min, hbond_match_min. Это единственные такие
# в каталоге (dataloader/descriptors.py, MIN_PAIR_DESCRIPTOR_NAMES): оба читают
# min(A, B), где A и B предварительно приведены к z-оценкам, причём всегда, независимо
# от каких-либо флагов -- см. preprocessing/compute_descriptors.py, описание
# aromatic_contact_min. Остальные парные признаки перемножают величины в их собственных
# единицах, поэтому к ним это не относится.
#
# Зачем это мерить. min() от z-оценок -- величина не физическая: она говорит "насколько
# слабая сторона пары отстаёт от СРЕДНЕГО по таблице", а не "сколько ангстрем" или
# "какая доля". Значит её значение зависит от состава таблицы, и на холодном разрезе
# среднее сдвигается вместе с вынесенным блоком. Этот прогон показывает, сколько
# конфигурация теряет (или не теряет) без таких признаков.
#
# Сравнивать с базой по парам (блок, сид): все прочие флаги скопированы дословно, и
# это ровно одна правка списка признаков.

--ep=120
--third_layers_in_mlps
--fast_attention
--hiddim=128
--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--descriptor_mlp
--descriptor_heads=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count,tail_length_asymmetry,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_double_bond_position,tail_logp,tail_molar_refractivity,tail_heavy_atoms,experimental_lipid_volume,extent,pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim,hydropathy_mean,ev14_q10,pocket_extent_lambda_sqrt,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,polar_share,basic_share_core,basic_share_rim,acidic_share_core,acidic_share_rim,polar_share_core,polar_share_rim,hbond_donor_share_core,hbond_donor_share_rim,hbond_acceptor_share_core,hbond_acceptor_share_rim,pocket_free_volume,pocket_packing_density,occupancy,chain_extent_gap,aromatic_contact,hbond_match,volume_fit,buriedness_match,depth_bulk_match,hydropathy_chain_match,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match
--save_model
--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
