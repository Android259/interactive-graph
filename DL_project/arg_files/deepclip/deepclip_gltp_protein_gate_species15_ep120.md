# deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120.md, одна строка изменена:
# --lipid_subclass=CerP+Hex2Cer+SHexCer -> --lipid_species_coldsplit=0.15.
#
# Блок: 15 строк / 5 позитивов на сид, перерисовывается каждым сидом.
# Планка без обучения на нём: lipid_only 0.914, within_protein 0.979 (AUC, 10 сидов).
# Читать как превышение над 0.979, не как собственный AUC.

--ep=120
--family_only=gltp
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

--balanced_proteins
--balanced_batches
--negatives_per_positive=2
--lipid_species_coldsplit=0.15

--save_model_in_dynamics
--save_model
