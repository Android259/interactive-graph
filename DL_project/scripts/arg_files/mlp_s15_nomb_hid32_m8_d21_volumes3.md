# = mlp_s15_nomb_hid32_m8_d21 + три объёмных имени СРАЗУ: experimental_lipid_volume
# (измеренный объём липида, Å^3, data/Lipid_Volumes.csv), pocket_free_volume (свободный
# объём полости, Å^3) и pocket_packing_density (свободная ДОЛЯ того же объёма).
# Смысл именно батчем, а не по одному: первые два — единственная в проекте пара величин
# на ОДНОЙ физической шкале (комментарий dataloader/protein_graph_builder.py:341-345),
# то есть по отдельности каждое из них — половина объёмного утверждения; третье несёт
# "насколько карман рыхлый" независимо от "насколько он большой" (корреляция с числом
# остатков кармана -0.196 против 0.791 у самого объёма).
# Обоснование и литература: files/ge_node_volume_descriptor_proposals.md §1.
# Сиблинги по одному имени: ..._d21_experimental_lipid_volume / _pocket_free_volume /
# _pocket_packing_density -- тот же раунд 2 из files/mlp_descriptor_selection_plan.md.
# База для сравнения: mlp_s15_nomb_hid32_m8_d21 (5 сидов уже есть).

--ep=120
--fast_attention

--hiddim=32
--m=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy,aromatic_share_rim,aromatic_contact_min,hbond_match_min,hbond_donor_share_rim,tail_double_bond_position,pocket_elongation_lambda_sqrt,aromatic_contact,tail_molar_refractivity,experimental_lipid_volume,pocket_free_volume,pocket_packing_density

--save_model

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
