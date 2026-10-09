# = mlp_s15_nomb_hid32_m8_d21 + hydropathy_mean (раунд 2 жадного шага, files/history/descriptor_models.md).
# План: files/history/descriptor_models.md

--ep=120
--fast_attention

--hiddim=32
--m=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy,aromatic_share_rim,aromatic_contact_min,hbond_match_min,hbond_donor_share_rim,tail_double_bond_position,pocket_elongation_lambda_sqrt,aromatic_contact,tail_molar_refractivity,hydropathy_mean

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
