# Identical to bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 except for
# --transformer_conv at the bottom: the protein encoder's GATv2 layer is replaced by
# torch_geometric's TransformerConv, same edge_dim=3 input (distance, contact area,
# solvent-facing area), same head count and output width, so only the "protein: GATv2
# layer and norm" parameter bucket changes (2112 -> 3648 parameters; see
# files/architecture_section.tex, Table~tab:params).
#
# Why it exists. GATv2's attention score is an unscaled LeakyReLU(a^T[Wh_i||Wh_j||e_ij]),
# with no normalisation against the growing norm of Wh as training proceeds;
# TransformerConv scores queries against keys with the standard 1/sqrt(d) scaling.
# Measured on this project's own runs (rand base config, both seeds, two-axis split),
# GLTP's valid predictions collapse to a single class for 75 and 117 of 120 epochs
# (collapse_epoch_count), and CRAL-TRIO seed 1 does the same less totally while
# gLip/gProt (TensorBoard epoch/grad norm lipid|protein) climb without bound across the
# whole run. This variant asks whether the scaled score changes that.
#
# Read it against bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 on the same
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

--transformer_conv

--save_model_in_dynamics
