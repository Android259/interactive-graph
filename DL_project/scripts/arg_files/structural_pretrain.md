
# Stage 1 of files/ plan "Структурное предобучение перед per-family дообучением".
# Encoder flags below must match scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_
# wd0001_gm_plm64_hid64.md exactly (protein1's saved weights are only meaningful
# for the exact module structure they were saved with -- new_train.py's own
# load_state_dict check refuses a mismatch loudly otherwise).

--structural_pretrain
--save_model
--label=structural_pretrain

--ep=120
--hiddim=64
--dropout=0.1

--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--fast_attention
--plm_compression_dim=64
--protein_edge_attention
