# = mlp_sub_pb6_keep5_all6 (лучший MLP на --lipid_subclass по test BA: 0.664+-0.144,
# 8 блоков из 9) + --dissimilar_negative_mining --dissimilar_negative_share=1.0.
# Ось балансировки НЕ меняется: --balanced_lipid_classes остаётся, и dissimilar-
# отбор теперь работает внутри неё -- негативы в каждой клетке (семья × класс
# липида) тянутся максимально ДАЛЁКИМИ по Танимото от позитивов этой же клетки
# (dataloader/sampler.py::sample_lipid_class_balanced_negatives). Раньше этот флаг
# требовал balanced_proteins/balance_negatives_by_family, то есть смены оси; его
# подключение к lipid-class сэмплеру -- правка этой же сессии.
#
# Чем это слабее того же флага на species15-конфигах: внутри клетки у всех
# кандидатов УЖЕ одна головная группа, поэтому Танимото разделяет их только по
# ацильному составу, а не по химии головы. Квота на клетку (draw_n) не меняется,
# поэтому per-class баланс, ради которого клетка и существует, сохраняется --
# меняется только КАКОЙ конгенер её заполняет.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=buriedness_q50,aromatic_share,aromatic_share_rim,depth_q10,ev14_q10,tail_elongation_fit,hydropathy_rim_match,aromatic_contact_min,basic_share_rim,pocket_packing_density,pocket_elongation

--save_model
--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--dissimilar_negative_mining
--dissimilar_negative_share=1.0
--lipid_subclass
