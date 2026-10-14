# = ge_s15_prothid32_hid64_noreg + отбор отрицательных по БЕЛКОВОЙ похожести (protein_tmscore, hard).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид).
#
# База -- ge_s15_prothid32_hid64_noreg (test BA 0.902+-0.011). Липидная версия
# ..._dnm даёт 0.925+-0.010, +0.024 парно, лучше на 4 сидах из 5.
#
# Протеиновая ось отбора отрицательных: кандидат взвешивается не по похожести
# СВОЕГО ЛИПИДА на липиды этого белка (так делает танимото), а по похожести СВОЕГО БЕЛКА
# на белки, которые связывают этот же липид (dataloader/sampler.py,
# conditioned_reference). Эталон берётся по всей обучающей части, семьи из
# --excluded_groups из него выброшены, а сам белок кандидата исключается даром: строка
# является отрицательной ровно тогда, когда её белок не связывает её липид.
#
# Матрицы: data/protein_similarity/ (preprocessing/build_protein_tmscore.py,
# preprocessing/build_protein_sequence_similarity.py). Без них запуск падает на сборке
# датасета с указанием нужного построителя, а не молча отбирает равномерно.
#
# Замерено на таблице (сид 42, ratio 2, доля 1.0), среднее по отобранным отрицательным,
# равномерно -> hard / dissimilar: tmscore 0.336 -> 0.395 / 0.299, blosum62
# 0.130 -> 0.226 / 0.111. protein_descriptors (0.157 -> 0.160) намеренно не берём --
# карманные дескрипторы на этой панели почти равноудалены, выбирать нечего.

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
--save_model

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
--hard_negative_mining
--negative_similarity=protein_tmscore
--hard_negative_share=1.0
