# = ge_lcs_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_prothid32_subclass + отбор отрицательных по БЕЛКОВОЙ похожести (protein_blosum62, dissimilar).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид).
#
# База -- ge_lcs_..._prothid32_subclass (test BA 0.568, 9 блоков x 5 сидов), то есть
# не-dnm вариант. Липидная версия ge_sub_prothid32_dnm даёт +0.020 парно на 40 парах,
# лучше на 25 из 40 -- здесь сэмплер --balanced_proteins, и липидный отбор работает,
# в отличие от линии mlp_sub на --balanced_lipid_classes. Оба направления и оба
# источника прогоняются одинаково, как на трёх остальных базах: какое направление
# выигрывает на БЕЛКОВОЙ оси, из липидного результата не следует.
# NB: на блоке PA база схлопывается в один класс (sens 1.000 / spec 0.000, BA ровно
# 0.500) -- если белковая ось это не починит, читать её результат на PA бессмысленно.
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
--lipid_subclass
--dissimilar_negative_mining
--negative_similarity=protein_blosum62
--dissimilar_negative_share=1.0
