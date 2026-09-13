# Same as ..._lcs_esm3_balanced_lipid_classes_advprot_protgeom8's ESM3 sibling, but
# without ESM3 (--no_protein_embeddings) -- pairs with ..._lcs_balanced_lipid_classes_
# advprot (no esm3), same single variable isolated: --protein_descriptors = protgeom8's
# 8 names instead of family-neutral 7 (item F, files/reference_baselines_metrics_
# proposal.md section 3), nothing else touched.

--ep=120
--fast_attention
--hiddim=8
--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm
--no_protein_embeddings
--protein_descriptors=pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim
--protein_edge_mlp
--save_model_in_dynamics
--save_model
--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
