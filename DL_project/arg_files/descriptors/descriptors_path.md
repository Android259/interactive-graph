# LEGACY: ran on a version that had --descriptors; the flag was removed (descriptor heads now come from --descriptor_heads),
# so this file no longer parses. Kept as the record of what ran; its results stay in metrics_summary.csv.
--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--descriptors
--descriptors_head

--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics