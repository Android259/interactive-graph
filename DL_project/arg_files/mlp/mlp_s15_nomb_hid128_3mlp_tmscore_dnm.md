# = mlp_s15_nomb_hid128_3mlp + отбор отрицательных по БЕЛКОВОЙ похожести (protein_tmscore, dissimilar).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид).
#
# База -- mlp_s15_nomb_hid128_3mlp (test BA 0.884+-0.020 на 5 сидах). Её же
# липидная версия ..._dnm даёт 0.923+-0.005, +0.039 парно, лучше на 4 сидах из 5 --
# то есть на этом разрезе отбор отрицательных уже доказал себя, и вопрос тут
# только в том, добавляет ли белковая ось что-то поверх липидной.
#
# Протеиновая ось отбора отрицательных: кандидат взвешивается не по похожести
# СВОЕГО ЛИПИДА на липиды этого белка (так делает танимото), а по похожести СВОЕГО БЕЛКА
# на белки, которые связывают этот же липид (dataloader/sampler.py,
# conditioned_reference). Эталон берётся по всей обучающей части, семьи из
# --excluded_groups из него выброшены, а сам белок кандидата исключается даром: строка
# является отрицательной ровно тогда, когда её белок не связывает её липид.
#
# Матрицы: data/cache/protein_similarity/ (preprocessing/similarity/build_protein_tmscore.py,
# preprocessing/similarity/build_protein_sequence_similarity.py). Без них запуск падает на сборке
# датасета с указанием нужного построителя, а не молча отбирает равномерно.
#
# Замерено на таблице (сид 42, ratio 2, доля 1.0), среднее по отобранным отрицательным,
# равномерно -> hard / dissimilar: tmscore 0.336 -> 0.395 / 0.299, blosum62
# 0.130 -> 0.226 / 0.111. protein_descriptors (0.157 -> 0.160) намеренно не берём --
# карманные дескрипторы на этой панели почти равноудалены, выбирать нечего.

--ep=120
--third_layers_in_mlps
--fast_attention

--hiddim=128

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptor_mlp
--descriptor_heads=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count,tail_length_asymmetry,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_double_bond_position,tail_logp,tail_molar_refractivity,tail_heavy_atoms,experimental_lipid_volume,extent,pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim,hydropathy_mean,ev14_q10,pocket_extent_lambda_sqrt,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,polar_share,basic_share_core,basic_share_rim,acidic_share_core,acidic_share_rim,polar_share_core,polar_share_rim,hbond_donor_share_core,hbond_donor_share_rim,hbond_acceptor_share_core,hbond_acceptor_share_rim,pocket_free_volume,pocket_packing_density,occupancy,chain_extent_gap,aromatic_contact,hbond_match,volume_fit,buriedness_match,depth_bulk_match,hydropathy_chain_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
--dissimilar_negative_mining
--negative_similarity=protein_tmscore
--dissimilar_negative_share=1.0
