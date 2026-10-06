--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--no_protein_self_attention
--no_lipid_self_attention
--fast_attention

--hiddim=8
--HEADS=4

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pocket_descriptors
--pair_descriptors

--no_embeddings
--descriptors_in_protein_lipid

--no_protein_geometry
--no_pair_descriptor_extent
--pair_descriptor_pocket_shares_coarse


--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics