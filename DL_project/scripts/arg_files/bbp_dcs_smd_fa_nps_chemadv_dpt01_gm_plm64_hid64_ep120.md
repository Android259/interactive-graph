--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=64
--plm_compression_dim=64

--dropout=0.1
--weight_decay=0.001
--pool_type="gem"

--balanced_batches
--balanced_proteins
--double_coldsplit

--chem_prior
--chem_adversary
--chem_lambda_ramp_by_fit

--save_model_in_dynamics