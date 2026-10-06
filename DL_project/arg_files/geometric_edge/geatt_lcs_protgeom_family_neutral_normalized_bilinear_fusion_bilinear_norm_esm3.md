# One variable against geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_lcs_esm3 (test BA 0.5530, 4 lipid sets x 5 seeds):
# --protein_edge_attention in place of --protein_edge_mlp. Same stem-swap convention as
# the dcs pair geometric_edge_{mlp,attention}_protgeom_family_neutral_normalized_
# bilinear_fusion_bilinear_norm.md.
#
# Both flags feed the conv the SAME 25-dimensional SE(3)-invariant edge vector
# (architecture/protein_edge_geometry.py); the difference is the aggregation, and one
# consequence of it is capacity, which is why this is worth a run under a lipid split
# specifically. architecture/protein_encoder.py:275-278:
#
#     gat_out      = hiddim * config.HEADS          # HEADS = 8
#     conv_out_dim = hiddim if use_edge_mlp else gat_out
#
# EdgeMLPConv returns out_dim, EdgeAttentionConv returns heads * out_dim -- at hiddim=8
# that is 8 wide against 64 wide in the graph path, an 8x widening for +25% parameters
# (27294 -> 33982 on the dcs baseline). It is the one capacity knob measured so far that
# does NOT simply widen everything: --hiddim 8 -> 64 under this same lipid split moved
# test BA 0.5530 -> 0.5511 (nothing) while train sensitivity went 0.837 -> 0.897 and the
# sens/spec gap 0.448 -> 0.505, i.e. pure memorisation.
#
# What it cannot do here, stated so the result is not over-read: with
# lipid_graph_isomers off (the default, and off in every lcs run so far) this flag
# touches only the PROTEIN graph, and under --lipid_coldsplit the protein side is
# in-distribution. So a large effect either way would be about capacity, not about
# reading the held-out chemistry. Pooled on the double cold split the two are within
# noise of each other (mlp 0.5525 vs attention 0.5428, n=35).

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_attention

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
