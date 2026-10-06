# = ge_s15_prothid32_hid64_noreg + хвостовые дескрипторы, ИСПРАВЛЕННЫЙ набор.
# Правка к _liptail (ΔBA -0.0227): тот подал tail_length_mean, tail_double_bonds,
# tail_unsaturation_density, tail_length_asymmetry и пропустил ровно те две величины,
# на которые указывают измерения -- tail_double_bond_position (наибольший внутриячеечный
# вклад: within-cell AUC 0.672 при pooled 0.503, то есть почти ортогонален маргинали
# "белок x подкласс") и experimental_lipid_volume (тот, чьё направление по белкам
# предсказывает depth_q10, rho -0.45). tail_length_mean оставлен как общий со старым
# набором столбец, чтобы разница читалась как замена колонок, а не как смена их числа.
# Числа: files/proposals/species15_information_above_protein_subclass.md §3-§4.
# Сравнивать с: _liptail (BA 0.879) и с базой (BA 0.902).
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
--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
--lipid_descriptors=tail_double_bond_position,experimental_lipid_volume,tail_length_mean
