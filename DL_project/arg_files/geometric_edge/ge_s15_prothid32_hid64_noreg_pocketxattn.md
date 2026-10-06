# = ge_s15_prothid32_hid64_noreg + --attention_by_pockets --pocket_attention_sites=cross
# (CLI-флаги; pocket_attention_cross сам -- производное поле, не настраивается
# напрямую). Заменяет мягкий bias к карману в cross-attention (prot_attention_pos_bias,
# уже включён по умолчанию) на жёсткий запрет -inf на всех не-карманных ключах --
# лиганд физически не может attend куда-то за пределы кармана. sites=cross (не
# "both") -- ограничивается только cross-attention, self-attention не трогается.
# Обоснование: files/history/geometric_edge.md

--ep=120
--fast_attention

--hiddim=64
--attention_by_pockets
--pocket_attention_sites=cross

--dropout=0.0
--weight_decay=0.00001
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--save_model
--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
