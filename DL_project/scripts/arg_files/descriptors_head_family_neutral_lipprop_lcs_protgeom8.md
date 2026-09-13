# descriptors_head_family_neutral_lipprop_lcs.md + item F (files/reference_baselines_
# metrics_proposal.md section 3): replace the family-neutral 7 protein descriptors
# with protgeom8's 8. Under --double_coldsplit family-neutrality matters because a
# whole protein family is held out; under --lipid_coldsplit no protein family is held
# out at all (every protein stays in train), so family eta^2 is not a leak channel
# here. depth_q10 and hydropathy_core -- the two descriptors dropped specifically for
# family eta^2 -- are the only two in the whole set with a measured, sign-stable link
# to a LIPID property: depth_q10 <-> acyl chain length (partial rho -0.407 pooled,
# same sign in two families), hydropathy_core <-> head-group class count (+0.403,
# agrees in CRAL-TRIO/lipocalin) -- exactly what a "new chemistry" question needs.
# On geometric_edge_mlp the full set gave test BA 0.601 vs family-neutral's 0.5525,
# but on double_coldsplit and confounded with lacking the bilinear stack -- not a
# clean single-variable read, and never measured under lcs or under descriptors_head
# at all (reference_baselines_metrics_proposal.md's own status for this item: "новая,
# непроверенная идея").

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
