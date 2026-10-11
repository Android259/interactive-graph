# LEGACY: ran on a version that had --descriptor_pocket_shares_coarse, --descriptors, --no_descriptor_extent; the flag was removed (descriptor heads now come from --descriptor_heads),
# so this file no longer parses. Kept as the record of what ran; its results stay in metrics_summary.csv.
--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=4
--HEADS=1

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptors
--descriptors_head
--no_descriptor_extent
--descriptor_pocket_shares_coarse

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
