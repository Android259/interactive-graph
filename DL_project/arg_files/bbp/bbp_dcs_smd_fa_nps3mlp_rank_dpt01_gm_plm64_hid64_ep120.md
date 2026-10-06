--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--fast_attention

--hiddim=64
--plm_compression_dim=64

--dropout=0.1
--weight_decay=0.001
--pool_type="gem"

--loss_type=pairwise_rank

--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics