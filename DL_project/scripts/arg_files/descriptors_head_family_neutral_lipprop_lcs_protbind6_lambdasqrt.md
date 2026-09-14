# Same as descriptors_head_family_neutral_lipprop_lcs_protbind6.md with ONE change: the
# two cavity-axis ratios in --descriptor_names are the sqrt(eigenvalue)-on-robust-
# covariance versions instead of the percentile-span ones.
#   pocket_elongation -> pocket_elongation_lambda_sqrt
#   pocket_flatness   -> pocket_flatness_lambda_sqrt
# The base file's list has no pocket_extent, so the six protbind6 additions and every
# other flag stay identical line for line.
#
# Why: files/pocket_shape_metric_comparison.md, seven variants against both lipid
# targets. Against head-group-class diversity (the target family does not determine),
# pocket_elongation_lambda_sqrt is the only variant of the seven whose sign holds in all
# three slices -- CRAL-TRIO +0.115, lipocalin +0.312, pooled +0.401 [0.061, 0.658] --
# where the span-based entry it replaces reverses inside both families against a positive
# pooled value, the between-family artifact pattern files/pocket_shape_descriptors.md
# section 4a used to reject pocket_volume_per_sasa.
#
# Family eta^2 is not a leak risk on this one: --lipid_coldsplit does not hold out the
# protein axis (all 35 proteins stay in train), which is the same argument the base file
# already makes for its own depth_q10/hydropathy_core/hydropathy_mean. Recorded anyway:
# pocket_elongation_lambda_sqrt 0.479 (span twin 0.189), pocket_flatness_lambda_sqrt
# 0.256 (0.481) -- the two formulas move in opposite directions per entry.
#
# Rank this by AUC_within_protein, not pooled AUC -- --lipid_coldsplit label
# (files/AGENTS.md, files/lipid_coldsplit_architecture_direction.md section 7j).
#
# Compare against: descriptors_head_family_neutral_lipprop_lcs_protbind6 (itself not yet
# run).
#
# Not yet run.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
