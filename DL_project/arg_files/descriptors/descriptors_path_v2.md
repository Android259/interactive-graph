# LEGACY: ran on a version that had --descriptor_pocket_shares_split, --descriptors; the flag was removed (descriptor heads now come from --descriptor_heads),
# so this file no longer parses. Kept as the record of what ran; its results stay in metrics_summary.csv.
--ep=120
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--descriptors
--descriptors_head
--descriptor_pocket_shares_split


--balanced_batches
--balanced_proteins
--double_coldsplit
