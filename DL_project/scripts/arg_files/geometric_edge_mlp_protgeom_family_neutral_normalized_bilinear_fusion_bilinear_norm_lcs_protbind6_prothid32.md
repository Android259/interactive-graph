# Same as geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_lcs_protbind6_prothid16.md, --protein_hiddim=32 instead of 16 -- see
# that file's own header for the full reasoning and the known memorisation risk this
# pair is checking for (..._liphid32.md's finding that protein-side width bought only
# memorisation under --lipid_coldsplit last time it was tried, via plain --hiddim).
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

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
