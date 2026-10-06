--num_workers=0
--batch=8
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--fast_attention

--hiddim=64
--plm_compression_dim=64

--dropout=0.1
--weight_decay=0.001
--pool_type="gem"

--balanced_batches
--balanced_proteins

--esmif1_replace_esm3