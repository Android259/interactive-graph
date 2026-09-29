# = mlp_s15_best_d12 + occupancy. Раунд 1 подбора дескрипторов под лучшую архитектуру.
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
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_rim,occupancy

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
