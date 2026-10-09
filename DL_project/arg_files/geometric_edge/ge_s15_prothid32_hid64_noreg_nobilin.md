# = ge_s15_prothid32_hid64_noreg БЕЗ --bilinear_fusion/--bilinear_pooled_norm.
# ВНИМАНИЕ: _pairdesc, для которого этот файл был знаменателем, удалён вместе с
# --pocket_descriptors (он нёс сырой ненормированный broadcast на узлы белка).
# Остаётся как замер цены снятия bilinear самого по себе: --pair_descriptors
# несовместим с bilinear_fusion (read_configuration.py, validate(): "pair_descriptors
# cannot be combined with bilinear_fusion"), поэтому любая будущая парная голова на
# этой базе снова потребует этот знаменатель.
# Сравнивать с: базой (сколько стоит bilinear).
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
