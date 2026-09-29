# deepclip_start_warm_ep120.md + --deepclip_pocket_cross_attention, nothing else.
#
# Every lipid position attends to the protein's real pocket residues (amino-acid
# one-hot + burial rank within the pocket, chain order; dataloader/
# protein_graph_builder.py's pocket_residue_tokens) instead of a pooled descriptor
# vector. The context is added to the LSTM state through a zero-initialised output
# projection, so the run starts as the control. ~0.6k extra parameters. No
# descriptor flags: the residues are the protein input.

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

--deepclip_pocket_cross_attention

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
