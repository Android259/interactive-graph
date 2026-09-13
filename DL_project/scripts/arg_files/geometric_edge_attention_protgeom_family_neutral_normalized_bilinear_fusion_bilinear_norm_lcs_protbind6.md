# LCS analogue of geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_rim_ev28.md (dcs test BA 0.5514, gap 0.4464 vs dcs base 0.5428/
# 0.5179; net vs chem null 0.529/0.545, increment 0.041/0.043 -- files/dcs_lcs_final_
# baseline_decision.md section 2 and this session's rim_ev28/rim_ev28_ckpt30 recheck).
# Minimal flip to --lipid_coldsplit, same convention as the existing geometric_edge_
# {mlp,attention}_..._bilinear_norm_lcs[_esm3].md pairs: swap --double_coldsplit ->
# --lipid_coldsplit, keep every other flag as-is (including --balanced_proteins, not
# --balanced_lipid_classes -- this is the "plain" lcs baseline lineage, not the
# advprot/balanced_lipid_classes line).
#
# --protein_descriptors= adds all six extra names this session's descriptor review
# flagged as worth trying (files/pocket_shape_descriptors.md sections 4/5/7, and this
# session's own eta^2-vs-binding-signal pass over it):
#   - ev28_q10, aromatic_share_rim: the already-tested rim_ev28 pair (dcs test BA
#     0.5514/0.5555 vs dcs base 0.5428 -- files/dcs_lcs_final_baseline_decision.md
#     section 2, this session's rim_ev28/rim_ev28_ckpt30 recheck).
#   - depth_q10, hydropathy_core: already in PROTEIN_DESCRIPTOR_NAMES (no code change
#     needed), excluded from family-neutral-7 for eta^2 (0.55/0.77), but the only two
#     entries whose correlation with a family-free proxy target (chain length /
#     head-group-class count) survives an if-checked-within-family look (section 4) --
#     the best candidates this project has for "real site signal", not fold leakage.
#   - ev14_q10, hydropathy_mean: new this session (dataloader/pair_descriptors.py,
#     dataloader/protein_graph_builder.py -- promoted from section 7's research-only
#     catalog). ev14_q10 eta^2=0.238 (at the family-neutral floor, ~0.235-0.25);
#     hydropathy_mean eta^2=0.611 (well above it, same risk profile as depth_q10/
#     hydropathy_core above). Both irrelevant here regardless of eta^2, since
#     --lipid_coldsplit does not hold out protein family at all (all 35 proteins stay
#     in train, files/lipid_coldsplit_architecture_direction.md section 4).
#
# No esm3 in this file (--no_protein_embeddings) -- see the _lcs_esm3 sibling for the
# other arm, and the _mlp_ sibling pair for the other edge aggregation. Not yet run.

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

--protein_edge_attention

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
