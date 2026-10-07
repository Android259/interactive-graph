# = mlp_s15_nomb_hid128_3mlp (лучший MLP на groups_species15 по test BA/F1:
# 0.884/0.832) + --dissimilar_negative_mining --dissimilar_negative_share=1.0.
# Проверяет новую ось сэмплинга: негативы для TRAIN-строк каждого белка тянутся
# максимально ДАЛЁКИМИ по Танимото от его собственных позитивов, а не равномерно
# (dataloader/AGENTS.md "Negative Sampling"; dataloader/sampler.py's
# _dissimilar_negative_weights). share=1.0 -- вся сэмплинг-масса на самых дальних
# кандидатах, та же точка, на которой эффект смещения измерен в
# dataloader/AGENTS.md (mean best Tanimoto 0.657 -> 0.534). Класс-баланс и квота
# на группу не меняются -- balanced_proteins уже стоит в базе, достаточно
# дополнить его флагом направления.

--ep=120
--third_layers_in_mlps
--fast_attention

--hiddim=128

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count,tail_length_asymmetry,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_double_bond_position,tail_logp,tail_molar_refractivity,tail_heavy_atoms,experimental_lipid_volume,extent,pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim,hydropathy_mean,ev14_q10,pocket_extent_lambda_sqrt,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,polar_share,basic_share_core,basic_share_rim,acidic_share_core,acidic_share_rim,polar_share_core,polar_share_rim,hbond_donor_share_core,hbond_donor_share_rim,hbond_acceptor_share_core,hbond_acceptor_share_rim,pocket_free_volume,pocket_packing_density,occupancy,chain_extent_gap,aromatic_contact,hbond_match,volume_fit,buriedness_match,depth_bulk_match,hydropathy_chain_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model

--balanced_batches
--balanced_proteins
--dissimilar_negative_mining
--dissimilar_negative_share=1.0
--lipid_species_coldsplit=0.15
