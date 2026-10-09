# deepclip_start_protein_gate_ep120.md + --deepclip_gate_positional, nothing else.
#
# The gate reads the LSTM state of each position beside the pocket descriptors, so its
# weight depends on the protein AND on what the molecule holds there. Centred across
# each molecule's positions: the position-constant part (the protein alone scaling the
# whole profile, the documented collapse mechanism) is removed by construction; a
# protein-level shift only enters through the bias. Gate MLP input 11 -> 21.

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
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume
--deepclip_gate_positional

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
