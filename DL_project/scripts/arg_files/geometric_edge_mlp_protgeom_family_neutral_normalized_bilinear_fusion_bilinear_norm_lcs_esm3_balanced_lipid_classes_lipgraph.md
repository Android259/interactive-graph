# One intervention against ..._lcs_esm3_balanced_lipid_classes: the lipid side stops being
# a MolFormer projection and becomes a real chemical graph.
#
# Two flags, one change. --lipid_graph_isomers switches architecture/lipid_encoder.py from
# Linear(768, hiddim) over an embedding to a GNN over data/lipid_graphs/ (1319 molecules,
# already built). --lipid_edge_mlp_lambda=2 is what makes that conv correct rather than
# merely enabled: EdgeMLPConv divides its summed messages by a CONSTANT, and the inherited
# 30 is Dauparas et al.'s value for a protein contact graph with ~30 neighbours per
# residue. Measured on this project's own lipid graphs
# (analysis/lipid_graph_degree.py): mean degree 1.968 over 72450 atoms, so 30 is 15.2x too
# large and every lipid node update arrived that much weaker than the layer was tuned for.
# Every --lipid_graph_isomers run before 2026-09-07 paid exactly that, because the divisor
# was shared with the protein graph and there was no way to set it apart (section 7d/7e).
#
# The honest counterweight, so this is run knowing it: the one existing direct ablation of
# lipid graphs is FLAT, in both conv variants -- geometric_edge_mlp_nwd 0.5409 with graphs
# vs 0.5463 without, geometric_edge_attention_nwd 0.5502 vs 0.5442. The attention arm has
# neither the lambda nor the width problem and still bought nothing. That was the double
# cold split with unequal n (14/18/19) and pooled numbers, so it does not settle the lipid
# split -- but it is not support either.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--lipid_graph_isomers
--lipid_edge_mlp_lambda=2
