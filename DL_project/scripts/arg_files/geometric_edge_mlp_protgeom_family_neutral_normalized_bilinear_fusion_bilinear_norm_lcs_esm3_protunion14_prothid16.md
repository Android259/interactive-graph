# --protein_hiddim=16 against geometric_edge_mlp_protgeom_family_neutral_normalized_
# bilinear_fusion_bilinear_norm_lcs_esm3_protunion14.md -- see that file's own header
# for the 14-name union reasoning. Same motivation as this session's
# ..._protbind6_prothid16/32.md pair: a wider descriptor vector (14 names now, up
# from protbind6's 13 and family-neutral-7's 7) may need more room than hiddim=8
# gives it. Same known risk: protein-side width bought only memorisation last time it
# was isolated under --lipid_coldsplit (..._liphid32.md's finding via plain --hiddim).
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

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=16

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
