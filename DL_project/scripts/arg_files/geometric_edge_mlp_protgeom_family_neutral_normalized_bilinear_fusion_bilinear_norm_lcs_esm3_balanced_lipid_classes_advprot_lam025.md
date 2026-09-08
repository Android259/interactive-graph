# Adversary strength, point 1 of 3: gradient reversal at a QUARTER of the default.
#
# Identical to ..._advprot in every other flag. --adv_lambda scales only the reversed
# gradient flowing back into the protein encoder -- how hard that branch is pushed to be
# individually uninformative -- leaving the adversary head's own learning rate alone
# (that is --adv_weight). It is therefore the clean "suppression strength" knob, and it
# is the one Ganin ramps.
#
# Why this sweep exists. Both adversary knobs have sat at their 1.0 defaults since the
# mechanism was first switched on here, and 1.0 turns out to be violent: under it the
# model stops fitting even TRAIN (train BA 0.884 -> 0.582, train-loss reduction 0.411 ->
# 0.028). The within-protein signal it buys was bought by leaving almost nothing to fit.
# That is the profile of a knob past its optimum, not on the slope to it -- and nobody
# has looked. This is the only capacity knob on this split that has never been measured,
# and it sits in the one part of the system that works
# (files/geometric_edge_and_solo_next_architecture.md 3.2).
#
# Read by AUC_within_protein_pairs on anionic and choline only -- the other two sets
# stand on 2 and 8 protein blocks (RULE box in
# files/lipid_coldsplit_architecture_direction.md).
#
# Written before the run: if 0.25 holds choline near advprot's 0.604 while train BA
# recovers well above 0.582, the suppression at 1.0 is wasteful and the whole line
# should move down. If choline collapses back toward the baseline's 0.448, then the
# marginal really does have to be destroyed this thoroughly, and 1.0 is not the problem.

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
# Both weight files (tested pick + last epoch); see
# files/geometric_edge_and_solo_next_architecture.md 6.3 for why the tested pick had to
# start being kept.
--save_model

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid

--adv_lambda=0.25
