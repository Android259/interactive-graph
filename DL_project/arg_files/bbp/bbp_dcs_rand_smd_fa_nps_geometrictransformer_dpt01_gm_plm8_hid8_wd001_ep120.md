# Identical to bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 except for
# --geometric_transformer at the bottom: replaces the whole rest of the protein
# encoder past its input projection -- GATv2 layer, post-GAT MLP, self-attention,
# post-SA MLP -- with ProteinGeometricTransformerBlock, which reads residue frames
# (rotation/translation) and edge_node_pairs/edge_node_degree instead of the plain
# edge_dim=3 attributes GATv2 and TransformerConv read. 27749 parameters total (the
# base config is 27286; see bbp_dcs_rand_smd_fa_nps_transformerconv_dpt01_gm_plm8_hid8
# _wd001_ep120 for the smaller, single-layer-swap alternative at 28822).
#
# Why it exists. Both this and --transformer_conv replace GATv2's unscaled
# LeakyReLU(a^T[Wh_i||Wh_j||e_ij]) attention score with a scaled one
# (scaled_dot_product_attention / 1/sqrt(head_dim), see architecture/geometric_transformer.py),
# which is the property the transformer_conv ablation targets directly. This one is not
# the minimal test of that property -- it also changes what the attention reads (frames,
# not the three scalar edge attributes) and drops the post-GAT MLP and protein
# self-attention block entirely. Read together with the transformer_conv ablation, not
# as a substitute for it: agreement between the two would implicate the score scaling;
# disagreement would implicate the geometric input or the dropped modules instead.
#
# Read it against bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 and
# bbp_dcs_rand_smd_fa_nps_transformerconv_dpt01_gm_plm8_hid8_wd001_ep120 on the same
# seven families and seeds 0 and 1.

--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--balanced_batches
--balanced_proteins
--double_coldsplit

--geometric_transformer

--save_model_in_dynamics
