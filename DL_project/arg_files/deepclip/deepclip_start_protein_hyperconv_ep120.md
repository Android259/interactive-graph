# deepclip_start_warm_ep120.md + --deepclip_protein_hyperconv with the gate's eleven
# descriptors, nothing else -- no gate.
#
# A hypernetwork adds a per-protein delta to every weight of the first convolution
# layer: each protein gets its own motif detectors. The delta is centred over the
# alphabet at every (filter, offset), so a protein can move a filter's preference
# between characters but not raise its response to all of them (a length detector).
# Starts as the control exactly.
#
# Cost: the MLP emits all 600 conv weights, 11 -> 8 -> 600, ~5.5k parameters -- more
# than the whole control network (~2k). The family has ~150 positives; read a bad
# number with that in mind.

--ep=120
--family_only=start
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
--deepclip_protein_hyperconv=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
