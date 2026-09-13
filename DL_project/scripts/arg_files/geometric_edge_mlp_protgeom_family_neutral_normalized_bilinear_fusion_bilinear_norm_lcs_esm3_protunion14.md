# Union of protbind6's 13 names and protgeom8's 8 names -- protbind6 already covers
# 7 of protgeom8's 8 (pocket_elongation, pocket_flatness, buriedness_q50,
# aromatic_share, hydropathy_rim, depth_q10, hydropathy_core); the only addition is
# protgeom8's pocket_extent, protbind6's only gap relative to it. 14 names total:
# pocket_volume_per_sasa, pocket_elongation, pocket_flatness, buriedness_q50,
# apolar_sasa_share, aromatic_share, hydropathy_rim, ev28_q10, aromatic_share_rim,
# depth_q10, hydropathy_core, ev14_q10, hydropathy_mean, pocket_extent.
#
# esm3 arm specifically: this session's comparison table showed mlp_..._lcs_esm3_
# protgeom8 with the highest increment_prot (0.036) and fit_chem_net_prot (0.744) of
# all 11 configs compared, at pooled BA (0.5525) essentially tied with the plain
# esm3 baseline (0.5530) -- pocket_extent was the one candidate explanation for that
# edge, being protgeom8's only content protbind6 lacks. This file checks whether
# adding it ON TOP of protbind6 (rather than instead of protbind6's other 6) keeps or
# loses that edge.
#
# Same "plain" lcs lineage as ..._lcs_esm3_protbind6.md (--balanced_proteins, not
# --balanced_lipid_classes; no adversarial_grl). Not yet run.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
