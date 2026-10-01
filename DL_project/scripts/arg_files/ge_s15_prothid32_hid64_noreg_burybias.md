# = ge_s15_prothid32_hid64_noreg + --cross_attention_bury_bias. Аддитивный
# softplus-ограниченный bias-терм на attention-скорах: buriedness остатка (глубже
# похороненный -- вероятнее реальный контакт кармана) модулирует внимание, а не
# транслируется как слепая константа на ноды (как остальные --protein_descriptors
# этого конфига). --cross_attention_chain_bias исключён: требует chain_rank, который
# существует только под --lipid_graph_isomers (графовое представление липида), а этот
# конфиг на MoLFormer-эмбеддинге -- смена липидного представления вне рамок
# архитектурной правки (files/ge_architecture_proposals_species15.md, "что не
# предлагается"). Обоснование bury_bias: files/ge_architecture_proposals_species15.md §6.

--ep=120
--fast_attention

--hiddim=64
--cross_attention_bury_bias

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
