--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pocket_descriptors
--pair_descriptors
--descriptors_head
--no_pair_descriptor_extent
--pair_descriptor_pocket_shares_coarse

--loss_type=pairwise_rank
--rank_within_protein

# batch=16 leaves ~4 same-protein pairs per batch and 10% of batches with none at
# all (interaction_signal_plan.md 4.2); 32 gives ~17 pairs and no empty batch.
--batch=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
