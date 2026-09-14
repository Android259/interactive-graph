# Same as geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_rim_ev28.md with ONE change: the two cavity-axis ratios are the
# sqrt(eigenvalue)-on-robust-covariance versions instead of the percentile-span ones.
#   pocket_elongation -> pocket_elongation_lambda_sqrt
#   pocket_flatness   -> pocket_flatness_lambda_sqrt
# Every other flag, and the rest of the descriptor list, is identical line for line, so
# a difference in the result maps to the formula and nothing else.
#
# Why: files/pocket_shape_metric_comparison.md compared the two formulas over seven
# variants against both lipid targets. Against the head-group-class target -- the one
# protein family does NOT determine (eta^2 0.22 against a 0.25 floor) --
# pocket_elongation_lambda_sqrt is the only one of the seven whose sign holds in all
# three slices: CRAL-TRIO +0.115, lipocalin +0.312, pooled +0.401 [0.061, 0.658]. The
# span-based pocket_elongation this file replaces gives pooled +0.288 but REVERSES
# inside both families (-0.071 / -0.156) -- the between-family artifact pattern
# files/pocket_shape_descriptors.md section 4a used to reject pocket_volume_per_sasa.
#
# CAVEAT, and it is the reason this is a separate label rather than an edit to the base
# file: this config is --double_coldsplit, where family eta^2 IS the leak risk, and the
# swapped-in entries are NOT family-neutral by the standard the "family_neutral" in this
# label refers to. eta^2 against the 9-family split: pocket_elongation_lambda_sqrt 0.479
# against the span version's 0.189, pocket_flatness_lambda_sqrt 0.256 against 0.481. So
# the two move in OPPOSITE directions -- elongation gets more family-correlated, flatness
# less -- and neither was added to POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES. If this run
# beats the base one, the next question is whether the gain survives the per-excluded-
# group test metrics or is just the extra family information; if it loses, the elongation
# eta^2 is the first thing to suspect.
#
# Compare against: geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_rim_ev28 (same groups, same seeds).
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

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
