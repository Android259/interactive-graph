--ep=120
--fast_attention

--hiddim=16

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion

--no_protein_embeddings

--pocket_descriptors
--pocket_descriptor_names=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit