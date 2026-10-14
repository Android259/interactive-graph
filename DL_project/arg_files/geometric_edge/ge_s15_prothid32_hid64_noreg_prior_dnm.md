# = ge_s15_prothid32_hid64_noreg + НАИВНЫЙ отбор отрицательных (protein_subclass_prior, dissimilar).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид), и отдельно -- с её же вариантами ..._tmscore_* / ..._blosum_*,
# где отбор идёт по белковой похожести.
#
# База -- ge_s15_prothid32_hid64_noreg (test BA 0.902+-0.011). Липидная версия
# ..._dnm даёт 0.925+-0.010, +0.024 парно, лучше на 4 сидах из 5.
#
#
# Наивный отбор отрицательных: кандидат взвешивается долей положительных в его
# ячейке (LTPProtein, подкласс статьи), оценённой по обучающим строкам -- тем самым
# предсказателем, который на этом разрезе и является главным конкурентом сети.
# Неизмеренная ячейка получает общий приор, а не ноль: ячейка, которую никто не мерил,
# не есть свидетельство несвязывания. Семьи из --excluded_groups в оценку не входят.
#
# ПОЧЕМУ ИМЕННО ЭТОТ НАИВНЫЙ ПРЕДСКАЗАТЕЛЬ. На --lipid_species_coldsplit=0.15 он самый
# точный из записанных: test BA 0.871+-0.009 при 0.902 у самой сети
# (files/proposals/species15_information_above_protein_subclass.md §1, канонический
# скрипт analysis/baselines/protein_subclass_label_baseline.py, правило "доля > 0.5").
# Потолок всего, что видит только пару (белок, подкласс), -- оракул ячейки 0.935.
# Липидные lookup-таблицы много слабее: по конкретному липиду 0.570, по классу головной
# группы 0.539 (preprocessing/lipid_marginal_baseline.py).
#
# ЧТО ЭТО ДАЁТ. При hard квота заполняется парами, которые lookup-таблица не отличает
# от настоящих связываний -- тот же белок, тот же подкласс, что у чего-то связываемого.
# Ровно тот контраст, который сеть обязана выиграть, чтобы стоить больше таблицы частот.
# Замерено на таблице (сид 42, ratio 2, доля 1.0): средний приор у отобранных
# отрицательных 0.040 равномерно -> 0.180 (hard) / 0.035 (dissimilar) при сэмплере по
# семьям, 0.040 -> 0.165 / 0.053 при сэмплере по белкам. Это самое сильное сцепление из
# всех источников: приор резко двуполюсный, выше 0.5 всего 1% кандидатов.
#
# Параметров модели не добавляет: это таблица частот по обучающим меткам, а не модель с
# весами, поэтому number_of_parameters совпадает с базой и прогоны сравнимы напрямую.

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
--dissimilar_negative_mining
--negative_similarity=protein_subclass_prior
--dissimilar_negative_share=1.0
