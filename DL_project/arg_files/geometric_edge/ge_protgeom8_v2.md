--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--no_protein_embeddings
--protein_descriptors=chain,unsaturation,hbond,heavy,occupancy,aromatic_share_coarse,polar_share_coarse

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit