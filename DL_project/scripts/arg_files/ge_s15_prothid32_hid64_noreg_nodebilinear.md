# = ge_s15_prothid32_hid64_noreg + --node_bilinear_fusion (второй, узловой билинейный
# канал ДО пуллинга, в дополнение к pool-level --bilinear_fusion).
# План: files/species15_minimal_model_plan.md

--ep=120
--fast_attention

--hiddim=64

--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm
--node_bilinear_fusion

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
