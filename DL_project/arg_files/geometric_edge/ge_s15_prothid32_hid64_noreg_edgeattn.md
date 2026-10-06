# = ge_s15_prothid32_hid64_noreg с --protein_edge_attention ВМЕСТО --protein_edge_mlp
# (взаимоисключающие флаги, training/read_configuration.py:2428). Та же 25-мерная
# геометрия ребра, но softmax-агрегация вместо MLP-суммирования с фиксированной
# нормировкой -- явная конкуренция соседей за вес вместо равного усреднения.
# Обоснование: files/reference/protein_edge_mlp_vs_attention.md,
# files/history/geometric_edge.md

--ep=120
--fast_attention

--hiddim=64

--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_attention
--protein_hiddim=32

--save_model
--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
