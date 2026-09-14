# Same as descriptors_head_family_neutral_lipprop.md with ONE change: the two cavity-axis
# ratios in --descriptor_names are the sqrt(eigenvalue)-on-robust-covariance versions
# instead of the percentile-span ones.
#   pocket_elongation -> pocket_elongation_lambda_sqrt
#   pocket_flatness   -> pocket_flatness_lambda_sqrt
# The base file's list has no pocket_extent, so nothing else changes; every other flag is
# identical line for line.
#
# Why: files/pocket_shape_metric_comparison.md compared the two formulas over seven
# variants against both lipid targets. Against head-group-class diversity -- the target
# protein family does NOT determine (eta^2 0.22 against a 0.25 floor) --
# pocket_elongation_lambda_sqrt is the only one of the seven whose sign holds in all
# three slices: CRAL-TRIO +0.115, lipocalin +0.312, pooled +0.401 [0.061, 0.658]. The
# span-based entry it replaces gives pooled +0.288 but reverses inside both families
# (-0.071 / -0.156), which files/pocket_shape_descriptors.md section 4a treats as the
# signature of a between-family artifact rather than site signal.
#
# CAVEAT: this config is --double_coldsplit, so family eta^2 is a real leak risk here,
# and the swapped-in entries are NOT family-neutral by the standard this label's name
# refers to -- pocket_elongation_lambda_sqrt scores 0.479 against the span version's
# 0.189, pocket_flatness_lambda_sqrt 0.256 against 0.481. The two move in opposite
# directions, and neither is in POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES. Read a win here
# against that: the elongation entry carries more family information than what it
# replaced, so a gain has to be checked per excluded group before it is called signal.
#
# Compare against: descriptors_head_family_neutral_lipprop (same groups, same seeds).
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
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
