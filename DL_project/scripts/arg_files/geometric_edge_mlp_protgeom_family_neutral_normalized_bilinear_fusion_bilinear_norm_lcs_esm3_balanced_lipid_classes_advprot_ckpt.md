# ..._advprot again, with the weights the test actually runs on written to disk.
#
# Why re-run something already measured. run_test evaluates best_model_state --
# the checkpoint selected by pooled validation balanced accuracy
# (training/new_train.py:2219,2281) -- and no label on this split saves it:
# --save_model_in_dynamics keeps epochs 1/10/49/51/120 only, and --save_checkpoint is
# set nowhere. So every post-hoc question about the tested model ("is this channel
# alive at test", "what does the null model score on the same weights") is currently
# unanswerable, and the numbers that were recomputed from dynamics/epoch120 describe a
# model nobody tested. Selection epochs across the existing 20 advprot-family runs run
# from 2 to 117, so epoch 120 is not even a good proxy.
#
# This is the base of the three siblings below (lambda05, lambda2, batch64): with it
# they are all comparable to a base whose tested weights can be inspected, instead of
# to one that can only be re-derived from the wrong epoch.
#
# Read by AUC_within_protein_pairs. Everything else is byte-identical to
# ..._advprot.md.

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
--save_checkpoint
