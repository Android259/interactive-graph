# Adversary strength, point 3 of 3: gradient reversal at TWICE the default.
#
# Identical to ..._advprot in every other flag; see ..._advprot_lam025 for why the sweep
# exists and what --adv_lambda scales. This point exists to test saturation from the
# other side: at 1.0 the model already fits almost nothing (train BA 0.582 against a
# chance 0.500), so doubling the push may have nothing left to take away.
#
# Read by AUC_within_protein_pairs on anionic and choline only.
#
# Written before the run: 2.0 indistinguishable from 1.0 means the plateau starts at or
# below the default, and the weak points are where the answer is. 2.0 clearly WORSE means
# 1.0 is already past the peak. 2.0 better would be the one genuinely surprising outcome
# and would say the marginal is still not fully removed at the default.

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

--adv_lambda=2.0
