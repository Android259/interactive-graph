--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,pocket_extent,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev56_q10,buriedness_q10,aromatic_share_core,buriedness_q90,depth_q90,ev14_q10

--protein_edge_attention

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit