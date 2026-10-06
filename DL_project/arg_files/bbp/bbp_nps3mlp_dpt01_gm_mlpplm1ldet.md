--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--hiddim=96
--plm_compression_dim=90

--dropout=0.1
--pool_type="gem"

--mlp_widths=protein_mlp=289,protein_mlp_third=255,protein_ffn=78,protein_ffn_third=66,lipid_ffn=241,lipid_ffn_third=186,cross_lip_ffn=199,cross_lip_ffn_third=147,cross_prot_ffn=114,cross_prot_ffn_third=90,final=299,final_third=218

--balanced_batches
--balanced_proteins
