# deepclip_start_warm_ep120.md + --deepclip_protein_film with the gate's eleven
# descriptors (and the two flags that build them), nothing else -- no gate.
#
# FiLM on the convolution output, before the LSTM: per channel gamma in (-1, 3), beta
# in (-1, 1), from the pocket. Changes what the LSTM integrates, not how the finished
# profile is summed, and can invert a motif detector per protein. Starts as the
# control exactly (zero-initialised last layer). MLP 11 -> 8 -> 10.

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
--deepclip_protein_film=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
