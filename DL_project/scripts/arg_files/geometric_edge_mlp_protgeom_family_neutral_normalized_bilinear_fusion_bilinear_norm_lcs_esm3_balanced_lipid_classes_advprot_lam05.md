# Adversary strength, point 2 of 3: gradient reversal at HALF the default.
#
# Identical to ..._advprot in every other flag; see ..._advprot_lam025 for why the sweep
# exists and what --adv_lambda scales. This is the midpoint: with 0.25 and 1.0 on either
# side, three points say whether the response is flat, monotone, or peaked, which one
# point cannot.
#
# Read by AUC_within_protein_pairs on anionic and choline only.
#
# Written before the run: the interesting outcome is choline at or above advprot's 0.604
# with a visibly higher train BA than 0.582 -- same signal, less destruction. Three
# points within one combined SEM of each other means the response is flat over 4x in
# lambda, and the knob is not where the remaining headroom is.

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

--adv_lambda=0.5
