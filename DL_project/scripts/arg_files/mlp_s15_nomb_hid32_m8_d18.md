# = mlp_s15_best_d16 + hbond_donor_share_rim, tail_double_bond_position. Раунд 1
# подбора дескрипторов под лучшую архитектуру.
# План: files/mlp_descriptor_selection_plan.md

--ep=120
--fast_attention

--hiddim=32
--m=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy,aromatic_share_rim,aromatic_contact_min,hbond_match_min,hbond_donor_share_rim,tail_double_bond_position

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
