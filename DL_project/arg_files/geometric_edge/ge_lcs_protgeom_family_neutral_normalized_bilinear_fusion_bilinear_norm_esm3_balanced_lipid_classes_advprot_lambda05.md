# Half the gradient-reversal strength, over ..._advprot.
#
# Why. The adversary buys its within-protein number by stopping the model from fitting
# anything: final train BA 0.884 -> 0.582 against the plain baseline, and the train loss
# barely moves at all over 120 epochs (reduction 0.028 against 0.411). Validation BA sits
# at 0.49-0.51 for the whole run. That is what over-suppression looks like -- the protein
# branch is pushed to be individually uninformative and the pair term left behind is too
# small to fit on its own.
#
# adv_lambda is the reversal strength (adv_weight scales the adversary's own CE instead;
# ModelConfig.adversarial_grl). It has never been varied on this split -- every lcs run
# uses the default 1.0 -- so it is unknown whether the current setting sits on a slope or
# past the optimum. Two points (0.5 here, 2.0 in the sibling) answer that, and it is the
# only capacity-like knob left in the part of the system that actually works: seven
# representation knobs measured flat or negative, both marginal-removal mechanisms
# positive.
#
# WHAT TO EXPECT, written before the run: if 1.0 is past the optimum, 0.5 recovers some
# train fit (train BA above 0.58) AND keeps the within-protein number; if 1.0 is on the
# slope, 0.5 gives back part of the protein marginal -- pooled BA rises, within-protein
# falls toward the baseline's 0.448 on choline. The two are distinguishable, which is the
# point of running it.
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
--adv_lambda=0.5
--save_checkpoint
