--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type=gem

--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics

--protein_edge_attention
--lipid_graph_isomers
--pair_descriptor_lipid_shape

--excluded_groups=GLTP
