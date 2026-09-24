# Variant D of the "prevent gate collapse" series (see deepclip_cral_trio_protein_gate_
# subclass_pa_ep120.md for the family/block/rule rationale and files/deepclip_gate_and_
# subclass_plan.md's running log for variants A/B/C). Exact sibling of ..._gatewd_
# smallgate_ep120.md (variant C), one more change: --checkpoint_selection_metric=auc.
#
# Does NOT touch the 0.5 decision threshold anywhere -- sensitivity/specificity/
# balanced_accuracy are still read at exactly 0.5 the same way every other run's are.
# The only thing this changes is WHICH EPOCH's weights get kept: the rolling-window
# comparison (training/new_train.py) now tracks valid AUC instead of valid balanced_
# accuracy. balanced_accuracy is fixed-threshold AND coarse on this family's ~16-17-row
# valid split (one row flips it by ~0.06), so the epoch it picks as "best" can be a
# noisy draw among several epochs that look identical at that resolution. AUC is
# threshold-independent and continuous, so it distinguishes those epochs where BA
# cannot -- this is a different, less discretised STOPPING criterion, not a threshold
# fit to the result (the report's own metrics, and the 0.5 cutoff they are read at,
# are unchanged).
#
# Not yet run.

--ep=120
--family_only=cral-trio
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

--pair_descriptors
--pocket_descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume
--deepclip_gate_hidden=3
--deepclip_gate_weight_decay=0.01
--checkpoint_selection_metric=auc

--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_subclass=PA

--save_model_in_dynamics
--save_model
