--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--loss_type=pairwise_rank
--rank_within_protein

# batch=16 leaves ~4 same-protein pairs per batch and 10% of batches with none at
# all (interaction_signal_plan.md 4.2); 32 gives ~17 pairs and no empty batch --
# same reasoning as descriptors_no_extent_coarse_add_lipprop_rankprot.md /
# descriptors_pair_only_rankprot.md.
--batch=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
