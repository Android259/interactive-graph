# Same arm as deepclip_cral_trio_protein_gate_subclass_pa_ep120.md (see that file's
# header for family/block/rule rationale), one flag added: --deepclip_gate_weight_decay
# on top of the current architecture.py gate (bias output, tanh-bounded, zero-sum
# channel weights -- files/deepclip_gate_and_subclass_plan.md's running log has the
# three prior steps and why each one was tried). Variant B of the "prevent gate
# collapse" series: bias and bias+tanh+zero-sum both left specificity-collapse rate
# roughly unchanged (7/10 -> 6/10 seeds at specificity exactly 0 or 1). This tests a
# different lever entirely -- not bounding what the gate's OUTPUT can reach, but
# penalising the optimizer for growing gate weights in the first place.
#
# 0.01: the same value this project already uses for a similarly overfit-prone,
# quadratic-ish module (bbp_..._wd001_*.md's --weight_decay=0.01), applied here only to
# architecture/deepclip.py's DeepCLIP.gate parameters via its own optimizer group
# (training/new_train.py's deepclip_gate_params split) rather than the whole network,
# for the same reason --bilinear_weight_decay exists: gate_hidden=8 out of ~9 CRAL-TRIO
# proteins / 778 train rows is thin enough that a global decay would flatten the
# conv/LSTM trunk that carries the actual sequence signal along with it.
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
--deepclip_gate_weight_decay=0.01

--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_subclass=PA

--save_model_in_dynamics
--save_model
