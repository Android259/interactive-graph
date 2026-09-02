--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type=add

--no_protein_embeddings

--pocket_descriptors
--pocket_descriptor_names=pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim,pocket_volume_per_sasa

--protein_edge_mlp

--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics