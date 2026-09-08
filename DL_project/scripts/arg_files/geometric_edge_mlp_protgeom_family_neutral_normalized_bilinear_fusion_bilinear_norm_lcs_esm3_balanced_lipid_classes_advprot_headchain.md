# The two-branch lipid split (files/lipid_coldsplit_architecture_direction.md section
# 7q), over ..._advprot.
#
# Why two branches. Head group and acyl chain behave OPPOSITELY across this split, and
# the correspondence is 4 sets out of 4 (section 7p): where a held-out block's variation
# is chain-dominated (choline, phosphorus_free) within-protein signal exists; where it is
# head-dominated (anionic, sphingolipids) it does not. Chain transfers because chains
# exist in every class left in training; head does not, because a set's heads all leave
# training together. Right now both axes are entangled in one Linear(768, hiddim) over a
# MolFormer embedding, so the model is forced to treat them the same.
#
# Why the two halves are NOT treated the same. Splitting and rejoining symmetrically is
# a capacity change, and capacity changes measured flat here (--lipid_hiddim 32 and 64,
# section 7k). The asymmetry is the proposal:
#   --lipid_descriptors      chain columns, ordinary broadcast into the lipid tower.
#                            eta^2 by head-group class 0.31-0.43: transferable, let it
#                            act on its own.
#   --lipid_head_descriptors head columns, reaching the classifier ONLY through
#                            ForcedInteraction with the pooled protein, no skip path.
#                            eta^2 0.98-0.99: alone this IS the class label, and the
#                            class is absent from training by construction. In a product
#                            with a protein it can still carry real pair signal -- the
#                            question section 7h left open.
#
# Built on descriptors, not on the molecule graph, deliberately: the one previous attempt
# to rebuild the lipid representation on this split (--lipid_graph_isomers) cost
# sphingolipids 4.6 combined SEM.
#
# Base is ..._advprot rather than the plain baseline because that is the first
# configuration whose within-protein number is off the floor (choline 0.62 on 11 protein
# blocks), i.e. the first where an improvement in the pair term is observable at all.
#
# WHAT TO EXPECT, written before the run so it cannot be fitted afterwards: a gain is
# possible on anionic and sphingolipids, where head variation exists and nothing can use
# it today. On choline and phosphorus_free -- chain-dominated, and chain already works --
# expect nothing. A gain on choline WITHOUT one on anionic would contradict section 7p,
# and that would matter more than the change itself.
#
# Read by AUC_within_protein_pairs.

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
--adversarial_grl
--no_adv_lipid
--lipid_descriptors=tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_length_asymmetry
--lipid_head_descriptors=tpsa,hbond,ring_count
