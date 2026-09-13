# One variable against ..._lcs_esm3_balanced_lipid_classes_advprot (current best lcs
# baseline): --protein_descriptors = protgeom8's 8 names instead of family-neutral 7.
# This is item F of files/reference_baselines_metrics_proposal.md section 3. That
# file's own text calls protgeom8 the "full" pre-reduction set for this question --
# NOT all 15 PROTEIN_DESCRIPTOR_NAMES (see the sibling _protfull.md files for that
# separate, less-justified idea).
#
# §7.1 (lipid_coldsplit_architecture_direction.md:365,887,1125) already tried
# protgeom8 vs family-neutral 7 under lcs and found it refuted (0.5525 vs 0.5530) --
# but on the OLD baseline, without --balanced_lipid_classes/--adversarial_grl. Item F
# flags this explicitly as unresolved on the current bilinear-stack baseline: the
# double_coldsplit contrast (protgeom8 0.601 vs family-neutral 0.5525) is confounded
# with lacking bilinear_fusion there, and lcs was never tried with the current best
# baseline's other pieces in place.
#
# depth_q10/hydropathy_core -- the two descriptors dropped from family-neutral 7 for
# family eta^2 -- are the only two with a measured, sign-stable link to a LIPID
# property: depth_q10 <-> acyl chain length (partial rho -0.407 pooled, same sign in
# two families), hydropathy_core <-> head-group class count (+0.403, agrees in
# CRAL-TRIO/lipocalin) -- files/descriptor_catalog.md section 2.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
