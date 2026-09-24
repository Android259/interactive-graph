# Variant C of the "prevent gate collapse" series (see deepclip_cral_trio_protein_gate_
# subclass_pa_ep120.md for the family/block/rule rationale and files/deepclip_gate_and_
# subclass_plan.md's running log for variants A/B). Exact sibling of ..._gatewd_ep120.md
# (variant B, --deepclip_gate_weight_decay=0.01), one more change: --deepclip_gate_hidden
# down from the default 8 to 3.
#
# Less capacity to memorise an idiosyncratic per-protein shortcut on ~9 proteins / 778
# train rows -- the gate MLP is Linear(11, gate_hidden) -> ReLU -> Linear(gate_hidden,
# hidden+1); at gate_hidden=3 its first layer alone drops from 96 to 36 weights. Not a
# replacement for weight_decay (which is still on, same 0.01) -- a smaller network is a
# harder constraint that no amount of optimizer pressure can undo, so this asks a
# different question: is the collapse a WIDE gate finding many equally-good ways to
# overfit the 9 proteins, or would even a narrow one still find one.
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

--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_subclass=PA

--save_model_in_dynamics
--save_model
