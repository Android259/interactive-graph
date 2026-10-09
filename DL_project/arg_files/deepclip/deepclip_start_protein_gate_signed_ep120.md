# deepclip_start_protein_gate_ep120.md + --deepclip_gate_signed, nothing else.
#
# The gate's channel weights live in (0, 2) there: a channel can be damped or
# amplified per protein but never inverted, and STARD2 vs STARD10 on PE/PG want the
# same lipid channel read with opposite sign. Here the range is (-1, 3); mean-centring
# (weights average to 1) is kept. Compare per protein and on mirror triples with
# analysis/probes/deepclip_mirror_pairs.py against deepclip_start_protein_gate_ep120.

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
--deepclip_gate_signed

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
