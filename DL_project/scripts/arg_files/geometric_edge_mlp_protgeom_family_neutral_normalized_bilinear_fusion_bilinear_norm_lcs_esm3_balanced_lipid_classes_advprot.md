# One intervention against ..._lcs_esm3_balanced_lipid_classes: a gradient-reversal
# adversary on the PROTEIN branch only.
#
# Aimed at the shortcut this split was measured to have, not at a generic one. Under
# --lipid_coldsplit every protein stays in training, so "which protein is this, and how
# promiscuous is it" is free and fully learnable, and the pooled metric is largely that:
# on this baseline, same rows, all AUC -- pooled 0.568 against 0.480 within protein, and
# 0.460/0.457 on the two sets with enough protein blocks to read
# (files/lipid_coldsplit_architecture_direction.md section 7j).
#
# --adversarial_grl adds a head that tries to predict the LABEL from one partner's
# pooled pre-cross-attention representation alone, with a gradient-reversal layer
# pushing that branch to be individually uninformative -- so the decision has to come
# from the interaction. --no_adv_lipid leaves only the protein-side adversary, which is
# the branch carrying the free marginal here. The lipid side is deliberately NOT
# policed: ModelConfig's own note says it is the side that carries the transferable
# signal and suppressing it may cost more than the shortcut it removes -- and under a
# LIPID cold split that side is the one being asked to generalise.
#
# Sibling of ..._rankprot, and the contrast is the point: rankprot removes the marginal
# from what the LOSS compares (pairs only within a protein), this removes it from what
# the REPRESENTATION can encode. Same target, two different mechanisms; running both
# says which one the problem actually responds to.
#
# Read by AUC_within_protein_pairs, not by test BA -- see the RULE box in
# files/lipid_coldsplit_architecture_direction.md.

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
