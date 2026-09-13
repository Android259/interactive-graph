# Same as geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_lcs_protbind6.md, ESM3 turned on (drop --no_protein_
# embeddings) -- the with/without-esm3 pair the way the existing plain lcs baseline
# has ..._lcs.md / ..._lcs_esm3.md. See that file's own header for the full
# six-descriptor reasoning (ev28_q10/aromatic_share_rim already tested under dcs as
# rim_ev28, so far only on attention; depth_q10/hydropathy_core already in
# PROTEIN_DESCRIPTOR_NAMES, excluded from family-neutral-7 by eta^2 but the two best
# "real site signal" candidates in files/pocket_shape_descriptors.md section 4;
# ev14_q10/hydropathy_mean new this session -- family eta^2 is moot either way since
# --lipid_coldsplit does not hold out protein family).
#
# Earlier this session, turning esm3 on alone (family-neutral-7 only, same mlp
# architecture, plain --lcs) moved test BA 0.5286 -> 0.5530, +0.024 pooled -- a real,
# non-trivial protein-identity contribution once the protein axis is not the held-out
# one. Whether that still holds with the wider protein_descriptors list here is what
# this file is for.
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

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
