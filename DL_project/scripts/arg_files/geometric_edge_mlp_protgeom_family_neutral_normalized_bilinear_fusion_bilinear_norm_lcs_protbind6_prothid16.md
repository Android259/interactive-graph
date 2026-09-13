# One variable against geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_lcs_protbind6.md: --protein_hiddim=16 (protein branch only,
# --hiddim stays 8 for everything else, including the lipid branch). Paired with
# _prothid32.md the same way the existing ..._liphid32.md/_liphid64.md pair is, so a
# flat result reads as a flat slope rather than one point that missed the useful width.
#
# Motivation specific to protbind6, not a blind capacity sweep: that file widens
# --protein_descriptors from 7 to 13 names while leaving hiddim=8 untouched, so the
# six extra numbers are squeezed through the same width as before -- --protein_hiddim
# tests whether the wider descriptor vector needs more room to be used at all, isolated
# from the lipid branch.
#
# Known risk, stated so a flat/negative result is not a surprise: ..._liphid32.md's own
# header records that raising width on the PROTEIN side under --lipid_coldsplit bought
# only memorisation last time it was tried -- raising --hiddim 8->64 (both branches)
# moved test BA 0.5530->0.5511 while train sensitivity went 0.837->0.897, because the
# protein axis is fully in-distribution here (every protein is in training) so extra
# capacity on that side has nothing held-out to generalise across. --protein_hiddim
# isolates the width to the protein branch alone, unlike that --hiddim sweep, but the
# same in-distribution argument applies to it too.
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
--protein_hiddim=16

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
