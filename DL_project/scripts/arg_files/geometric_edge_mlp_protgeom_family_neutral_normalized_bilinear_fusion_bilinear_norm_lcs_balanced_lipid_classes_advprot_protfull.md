# Same as ..._lcs_balanced_lipid_classes_advprot_protfull's ESM3 sibling
# (..._lcs_esm3_balanced_lipid_classes_advprot_protfull), but without ESM3
# (--no_protein_embeddings) -- pairs with ..._lcs_balanced_lipid_classes_advprot
# (no esm3), same single variable isolated: --protein_descriptors full 15 instead of
# family-neutral 7, nothing else touched.

--ep=120
--fast_attention
--hiddim=8
--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm
--no_protein_embeddings
--protein_descriptors=pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim
--protein_edge_mlp
--save_model_in_dynamics
--save_model
--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
