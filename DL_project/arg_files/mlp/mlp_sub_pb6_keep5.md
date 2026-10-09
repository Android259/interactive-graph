# = mlp_sub_pb6 с 5 из 17 дескрипторов: набор, оставшийся после обнуления 12 по checkpoint-абляции
# (analysis/input_ablation.py subsets, отбор по valid: test dBA -0.004). Все 4 липидных убраны.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptors
--descriptor_mlp
--descriptor_names=buriedness_q50,aromatic_share,aromatic_share_rim,depth_q10,ev14_q10

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_subclass
