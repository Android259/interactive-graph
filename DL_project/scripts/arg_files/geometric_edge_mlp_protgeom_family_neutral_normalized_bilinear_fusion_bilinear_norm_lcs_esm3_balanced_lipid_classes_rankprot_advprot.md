# Both marginal-removal mechanisms at once, over ..._lcs_esm3_balanced_lipid_classes.
#
# Why. Measured separately (files/lipid_coldsplit_architecture_direction.md section 7n),
# they remove the SAME thing in different places -- rank_within_protein from what the
# LOSS compares, the protein-side gradient-reversal adversary from what the
# REPRESENTATION can encode -- and land on nearly the same number on choline, the set
# with enough protein blocks to read: AUC within protein 0.457 (baseline) -> 0.602
# (rank) and 0.622 (adversary), on 11 blocks, 3.6 and 5.8 combined SEM.
#
# The question this asks is whether they ADD. If the combination lands near either one
# alone, the ceiling is set by the data rather than by the mechanism, and further work
# on removing the marginal is finished. If it adds, the two were catching different
# parts of it. Either answer closes a branch, which is why it is worth one run.
#
# --batch=64 comes from the rank side and is required there, not a free choice: at 16 a
# batch rarely holds two rows of one protein with opposite labels, the pairwise loss
# returns a plain zero with no grad_fn, and the run dies at epoch 1. See ..._rankprot.
#
# Read by AUC_within_protein_pairs; pooled BA falls under both mechanisms BY DESIGN --
# it was the marginal.

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
--loss_type=pairwise_rank
--rank_within_protein
--batch=64
--adversarial_grl
--no_adv_lipid
