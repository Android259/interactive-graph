# = mlp_sub_pb6_keep5_all6 + отбор отрицательных по БЕЛКОВОЙ похожести (protein_tmscore, dissimilar).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид).
#
# База -- mlp_sub_pb6_keep5_all6 (test BA 0.664+-0.023, 8 блоков x 5 сидов; худшие
# блоки PC 0.520 и PI 0.519, то есть на уровне случая). Это единственная из четырёх
# линий, где липидный отбор НЕ дал ничего: ..._all6_dnm даёт -0.009, улучшилось 19
# прогонов против 21 ухудшившегося, медиана ровно 0.000. Причина не в разрезе, а в
# сэмплере: --balanced_lipid_classes набирает отрицательные внутри ячейки
# (семья, класс головной группы), где все кандидаты уже делят головную группу и
# танимото между ними в среднем 0.978 ещё до всякого отбора -- двигать нечего.
# Белковая ось этим не ограничена: ячейка держит все белки семьи. Поэтому здесь
# проверяются ОБА направления -- ни одно не проверено на этой линии.
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
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptor_mlp
--descriptor_heads=buriedness_q50,aromatic_share,aromatic_share_rim,depth_q10,ev14_q10,tail_elongation_fit,hydropathy_rim_match,aromatic_contact_min,basic_share_rim,pocket_packing_density,pocket_elongation

--save_model_in_dynamics
--save_model

--balanced_batches
--balanced_lipid_classes
--lipid_subclass
--dissimilar_negative_mining
--negative_similarity=protein_tmscore
--dissimilar_negative_share=1.0
