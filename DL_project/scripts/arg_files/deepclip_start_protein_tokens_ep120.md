# deepclip_start_warm_ep120.md + --deepclip_protein_tokens, nothing else.
#
# The protein graph tokenised into the lipid's own sequence: pocket residues in chain
# order (amino-acid one-hot + burial rank), one separator, then the SMILES characters,
# all on one axis the convolutions and the BLSTM scan. The score is still the mean
# profile over the LIPID positions only. The input widens by 21 residue channels + 1
# separator (~0.7k extra conv weights). Unlike every other variant this does not start
# as the control: the forward LSTM carries the pocket into the lipid from step one.

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

--deepclip_protein_tokens

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
