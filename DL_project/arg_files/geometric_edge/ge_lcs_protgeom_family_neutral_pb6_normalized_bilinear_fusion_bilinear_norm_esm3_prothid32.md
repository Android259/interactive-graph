# esm3 arm of geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_lcs_protbind6_prothid32.md -- see that file's own header for the
# --protein_hiddim=32 reasoning and the known protein-side-width memorisation risk
# under --lipid_coldsplit (..._liphid32.md).
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

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
