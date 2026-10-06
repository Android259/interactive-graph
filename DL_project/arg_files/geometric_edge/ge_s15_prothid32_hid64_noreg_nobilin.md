# = ge_s15_prothid32_hid64_noreg БЕЗ --bilinear_fusion/--bilinear_pooled_norm.
# Существует только как КОНТРОЛЬ к _pairdesc: --pair_descriptors несовместим с
# bilinear_fusion (read_configuration.py:2812), поэтому _pairdesc нельзя сравнивать с
# базой напрямую -- снятие bilinear само по себе убирает 246k параметров. Эта строка
# измеряет цену снятия, чтобы вклад парной головы читался как _pairdesc минус _nobilin.
# Сравнивать с: базой (сколько стоит bilinear) и быть знаменателем для _pairdesc.
--ep=120
--fast_attention
--hiddim=64
--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent
--protein_edge_mlp
--protein_hiddim=32
--save_model_in_dynamics
--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
