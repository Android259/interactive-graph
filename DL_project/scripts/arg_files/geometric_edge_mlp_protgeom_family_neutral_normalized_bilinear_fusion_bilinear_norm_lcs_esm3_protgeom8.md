# One variable against geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_lcs_esm3 (test BA 0.5530, 4 lipid sets x 5 seeds): the
# --protein_descriptors list, nothing else.
#
# Why. The family-neutral 7 were selected by eta^2-by-family <= 0.48 on 35 proteins
# (files/descriptor_catalog.md section 2) to stop the model recognising the HELD-OUT
# FAMILY. Under --lipid_coldsplit no family is held out -- dataloader/Dataloader.py's
# _split_interactions keeps every protein in train and holds out chemistry instead --
# so that selection protects an axis this run does not have, while dropping the two
# descriptors with the only MEASURED, sign-stable link to a lipid property:
#   depth_q10       <-> acyl chain length   (partial rho -0.407 pooled; -0.434/-0.683
#                                            inside two separate families, same sign)
#   hydropathy_core <-> number of head-group classes (+0.403, agrees in CRAL-TRIO and
#                                            lipocalin)
# Both are exactly what a lipid cold split needs and exactly what family-neutrality
# threw away.
#
# The list below is geometric_edge_mlp_protgeom8.md's eight names. That label reached
# test BA 0.6010 with sens/spec 0.561/0.641 (gap 0.313) against the family-neutral
# baseline's 0.5525 and gap 0.586 -- on the HARDER double cold split, where their
# family-ness genuinely is a leak.
#
# Deliberately still --protein_descriptors and not protgeom8.md's --pocket_descriptors
# /--pocket_descriptor_names: those are a different code path (expand_pocket_descriptor
# vs expand_named_protein_descriptors, files/descriptor_catalog.md section 0) even
# though the numbers are the same, and routing through it would change two things at
# once. All eight names are in PROTEIN_DESCRIPTOR_NAMES (dataloader/pair_descriptors.py).

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
--lipid_coldsplit
