# geometric_edge_mlp_..._protunion14_prothid32_pocketchem4.md plus ONE flag:
# --lipid_descriptors with the four lipid names the Kron-RLS search picked. Everything
# else, its own eighteen --protein_descriptors included, is copied from that file
# verbatim; that file in turn is the protunion14_prothid32 baseline plus four protein
# names. Read both headers for the rest.
#
# The added flag:
#   --lipid_descriptors=experimental_lipid_volume,tail_double_bonds,logp,
#                       tail_unsaturation_density
#
# WHY A SEPARATE FILE AND NOT A LINE IN THE OTHER ONE
#
# The two answer different questions and only the pair separates them. _pocketchem4.md
# gives the network the PROTEIN half of the matched pairs its header sets out and
# nothing else, so its result is what the new pocket chemistry buys with the lipid
# branch untouched. This file supplies the LIPID half as well. Three files in the
# series, and each adjacent pair changes exactly one thing:
#   _pocketchem4.md                              protein half only
#   THIS FILE                                    + lipid half, bilinear fusion
#   descriptors_head_..._pocketchem4_lipcron4.md   same eight names, token head
#
# WHY THE LIPID HALF IS NOT DECORATION HERE
#
# The strongest of the four new protein descriptors is a PARTNERED quantity:
# pocket_free_volume is an angstrom^3 cavity volume, and the only thing on that same
# physical scale is the lipid's own experimental_lipid_volume (mean 1006 A^3 against
# 632 A^3). Cavity volume against lipid volume is the one quantitative relation Titeca
# et al. actually measure. With only the protein half present there is nothing
# commensurate for the fusion to compare it with -- the lipid branch carries a learned
# graph embedding, from which a MEASURED volume (a data/Lipid_Volumes.xlsx lookup, not
# an RDKit formula) is not derivable.
#
# The mechanism that can use both halves is already on in the baseline:
# --bilinear_fusion builds torch.nn.Bilinear(pooled_lip_dim, pooled_prot_dim, middim),
# a true bilinear form in which every output unit sums over ALL (lipid channel x
# protein channel) products. --lipid_descriptors is the exact mirror of
# --protein_descriptors (architecture/lipid_encoder.py): an arbitrary named
# DESCRIPTOR_CATALOG subset selected by column out of the same shared
# descriptor_catalog_input tensor and broadcast onto every lipid node, pooled with the
# rest. So both halves reach the Bilinear as channels and the product is reachable --
# reachable, not guaranteed, which is what this run measures. Neither of the two flags
# that would silence the broadcast (--lipid_graph_isomers, --no_embeddings) is set in
# this file.
#
# WHY THESE FOUR LIPID NAMES
#
# cron_test_metrics/exhaustive_descriptor_search.csv, 16064 combinations with BOTH
# sides free, ranked by AUC_within_protein on the Figure-3 lipid-subclass split. The
# lipid side of the winner -- and of all three runners-up behind it -- is the identical
# five names; presence across the leading rows (chance ~50%):
#   experimental_lipid_volume 100% of the top 50, 100% of the top 200
#   logp                       98 / 98
#   tail_unsaturation_density  96 / 97
#   unsaturation               66 / 60
#   tail_double_bonds          60 / 51
#   tail_double_bond_position  12 / 17   <- dropped
# Four names here rather than five: `unsaturation` is dropped because this file's lipid
# branch is a learned encoder over the molecular graph, where an unsaturation COUNT is
# derivable -- unlike the measured volume. Its descriptors_head sibling carries all five
# (it has `unsaturation` from its own base file) because there the descriptor list is
# the whole input and nothing is derivable from anywhere else.
#
# Note the composition of the four: one measured size (experimental_lipid_volume) and
# three TAIL quantities. That is deliberate and it is what the split makes relevant. A
# --lipid_subclass block holds out one head group whole, so inside the block every
# species shares that head and the only thing that varies between them is the acyl
# chain -- PC(30:0) against PC(38:3). logp/tail_double_bonds/tail_unsaturation_density
# are exactly that axis.
#
# Note for a LOCAL smoke run: experimental_lipid_volume is a data/Lipid_Volumes.xlsx
# lookup and openpyxl is not installed on this machine, so it only resolves from an
# existing data/pair_descriptor_cache_deterministic_*.json -- same caveat as the
# descriptors_head sibling, and unlike _pocketchem4.md, which does not name it.
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

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume
--lipid_descriptors=experimental_lipid_volume,tail_double_bonds,logp,tail_unsaturation_density

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
