# = geometric_edge_..._esm3_protunion14_hid32_species15 при npp=2 (дефолт) вместо 5.
# Проверка: бьёт ли большая модель планку 0.879/0.837 при npp=2.


--ep=120
--fast_attention

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
