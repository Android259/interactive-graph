# deepclip_start_warm_ep120.md + --deepclip_protein_bilinear with the gate's eleven
# descriptors, nothing else -- no gate.
#
# score += h^T M p: h the molecule's mean LSTM state, p the pocket descriptors, M
# (10 x 11 = 110 parameters) zero-initialised. The sign of every channel's
# contribution becomes a function of the protein -- what the (0, 2) gate cannot do --
# at the smallest cost of all the variants.

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

--descriptors
--deepclip_protein_bilinear=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
