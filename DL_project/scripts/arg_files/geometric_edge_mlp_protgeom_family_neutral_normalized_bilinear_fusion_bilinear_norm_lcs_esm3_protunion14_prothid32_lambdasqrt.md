# Same as geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_lcs_esm3_protunion14_prothid32.md with ONE change: all THREE cavity-axis
# entries are the sqrt(eigenvalue)-on-robust-covariance versions instead of the
# percentile-span ones.
#   pocket_elongation -> pocket_elongation_lambda_sqrt
#   pocket_flatness   -> pocket_flatness_lambda_sqrt
#   pocket_extent     -> pocket_extent_lambda_sqrt
# This is the only one of the four _lambdasqrt files that swaps extent as well, because
# it is the only one of the four base files whose descriptor list contains it. Every
# other flag identical line for line.
#
# Why: files/pocket_shape_metric_comparison.md, seven variants against both lipid
# targets. Against head-group-class diversity (the target family does not determine),
# pocket_elongation_lambda_sqrt is the only variant of the seven keeping its sign in all
# three slices -- CRAL-TRIO +0.115, lipocalin +0.312, pooled +0.401 [0.061, 0.658] --
# where the span version reverses inside both families. For extent the two formulas rank
# the 35 proteins at Spearman 0.987 of each other, so that swap is near-cosmetic; what it
# buys is the slightly stronger chain-length partial correlation (+0.426 [0.102, 0.668]
# against span's +0.368 [0.034, 0.628], sign agreeing in both families either way).
#
# Family eta^2 does not apply as a leak risk here: --lipid_coldsplit does not hold out
# the protein axis at all (all 35 proteins stay in train -- files/lipid_coldsplit_
# architecture_direction.md section 4), which is the same argument the base file already
# makes for keeping depth_q10/hydropathy_core/hydropathy_mean in its list. Recorded for
# completeness anyway: pocket_extent_lambda_sqrt 0.737 (span twin 0.618),
# pocket_elongation_lambda_sqrt 0.479 (0.189), pocket_flatness_lambda_sqrt 0.256 (0.481).
#
# Rank this by AUC_within_protein, not pooled AUC -- it is a --lipid_coldsplit label
# (files/AGENTS.md, files/lipid_coldsplit_architecture_direction.md section 7j).
#
# Compare against: geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_lcs_esm3_protunion14_prothid32 (itself not yet run).
#
# Not yet run.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent_lambda_sqrt

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
