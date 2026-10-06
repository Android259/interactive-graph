# = ge_s15_prothid32_hid64_noreg + --drop_uncovered_protein_subclass, флаг в флаг.
# Тест: сравнимо ли превышение сети над планкой "белок x подкласс", если из valid/test
# убрать строки, где ячейка планке неизвестна (на них она даёт 0.500 по построению).
# Ожидание: планка 0.871 -> 0.879, строк -10%, позитивов -3%.
# Читать: files/proposals/species15_information_above_protein_subclass.md §1-2.
# Сравнивать с: ge_s15_prothid32_hid64_noreg (БА/F1 0.902/0.861) и с
#   analysis/baselines/protein_subclass_label_baseline.py --label ge_s15_prothid32_hid64_noreg_covered

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
--drop_uncovered_protein_subclass
