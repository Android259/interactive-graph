# deepclip_cral_trio_protein_gate_subclass_pa_ep120.md, одна строка изменена:
# --lipid_subclass=PA -> --lipid_species_coldsplit=0.15.
#
# Блок: ~61 строка / 13 позитивов / ~6 белков на сид.
# Сиблинг на подклассовой оси: test AUC 0.674 против планки within_protein 0.658,
# при balanced_accuracy 0.518 (скоры сжаты, порог 0.5 мимо).

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
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_species_coldsplit=0.15

--save_model_in_dynamics
--save_model
