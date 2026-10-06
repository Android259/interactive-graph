# = mlp_s15_nomb_hid64_pu01 + --pu_rho_by_subclass. Первый реальный прогон этой опции
# (architecture/loss.py::_grouped_pu_loss, добавлена этой сессией, до сих пор только
# юнит-тестами покрыта). Вместо одного train-wide rho -- отдельный rho на каждый
# подкласс липида (data/lipid_article_classification.json), посчитанный той же формулой
# effective_pu_rho, но на train-счётчиках именно этого подкласса; подклассы с <20
# train-строк падают на общий rho (training/new_train.py::build_pu_subclass_priors).

--ep=120
--fast_attention

--hiddim=64
--pu_loss
--pu_unlabeled_positive_fraction=0.1
--pu_rho_by_subclass

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count,tail_length_asymmetry,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_double_bond_position,tail_logp,tail_molar_refractivity,tail_heavy_atoms,experimental_lipid_volume,extent,pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim,hydropathy_mean,ev14_q10,pocket_extent_lambda_sqrt,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,polar_share,basic_share_core,basic_share_rim,acidic_share_core,acidic_share_rim,polar_share_core,polar_share_rim,hbond_donor_share_core,hbond_donor_share_rim,hbond_acceptor_share_core,hbond_acceptor_share_rim,pocket_free_volume,pocket_packing_density,occupancy,chain_extent_gap,aromatic_contact,hbond_match,volume_fit,buriedness_match,depth_bulk_match,hydropathy_chain_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
