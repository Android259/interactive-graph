# = mlp_sub_pb6_keep5_pair3, одна правка: выброшены z-scored признаки.
#
# ЧТО УБРАНО И ПОЧЕМУ. Из --descriptor_heads выброшены признаки, которые считаются
# от СТАНДАРТИЗОВАННЫХ входов: aromatic_contact_min. Это единственные такие
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
--fast_attention
--lipid_propensity_weight
--hiddim=8
--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--descriptor_mlp
--descriptor_heads=buriedness_q50,aromatic_share,aromatic_share_rim,depth_q10,ev14_q10,tail_elongation_fit,hydropathy_rim_match
--save_model_in_dynamics
--save_model
--balanced_batches
--balanced_lipid_classes
--lipid_subclass
