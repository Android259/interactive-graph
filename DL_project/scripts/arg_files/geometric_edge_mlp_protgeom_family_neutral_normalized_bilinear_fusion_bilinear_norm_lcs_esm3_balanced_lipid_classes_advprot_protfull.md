# One variable against ..._lcs_esm3_balanced_lipid_classes_advprot (current best lcs
# baseline): the --protein_descriptors list, nothing else. ESM3, bilinear_pooled_norm,
# balanced_lipid_classes, adversarial_grl/no_adv_lipid all kept exactly as there.
#
# Why. §7.1 (files/lipid_coldsplit_architecture_direction.md:365,887,1125) already
# tested widening family-neutral 7 to protgeom8's 8 names and found it refuted (0.5525
# vs 0.5530) -- but that comparison ran on the OLD baseline, before balanced_lipid_
# classes/advprot existed. Neither protgeom8 nor the full 15 (all of PROTEIN_
# DESCRIPTOR_NAMES) has been tried against the CURRENT best baseline in isolation.
# geometric_edge_mlp_protgeom_full_lcs.md also uses the full 15, but confounds it with
# dropping ESM3 and swapping --balanced_lipid_classes for --balanced_proteins (see that
# file and lipid_coldsplit_architecture_direction.md:1607) -- not a clean read on the
# descriptor list alone. This file isolates that one variable.
#
# Family-neutral 7 was selected to hide protein FAMILY identity (--double_coldsplit
# axis). Under --lipid_coldsplit no family is held out, so that protection guards an
# axis this run doesn't have, at the cost of dropping the two descriptors with a
# measured, sign-stable link to a lipid property (depth_q10 <-> chain length;
# hydropathy_core <-> head-group class count -- files/descriptor_catalog.md section 2).
# Full 15 = PROTEIN_DESCRIPTOR_NAMES (dataloader/pair_descriptors.py) in full, not just
# protgeom8's curated 8.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
