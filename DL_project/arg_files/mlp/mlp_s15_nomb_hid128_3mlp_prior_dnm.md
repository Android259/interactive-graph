# = mlp_s15_nomb_hid128_3mlp + НАИВНЫЙ отбор отрицательных (protein_subclass_prior, dissimilar).
# Все остальные флаги скопированы из базы дословно; сравнивать с ней по парам
# (блок, сид), и отдельно -- с её же вариантами ..._tmscore_* / ..._blosum_*,
# где отбор идёт по белковой похожести.
#
# База -- mlp_s15_nomb_hid128_3mlp (test BA 0.884+-0.020 на 5 сидах). Её же
# липидная версия ..._dnm даёт 0.923+-0.005, +0.039 парно, лучше на 4 сидах из 5 --
# то есть на этом разрезе отбор отрицательных уже доказал себя, и вопрос тут
# только в том, добавляет ли белковая ось что-то поверх липидной.
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
--negative_similarity=protein_subclass_prior
--dissimilar_negative_share=1.0
