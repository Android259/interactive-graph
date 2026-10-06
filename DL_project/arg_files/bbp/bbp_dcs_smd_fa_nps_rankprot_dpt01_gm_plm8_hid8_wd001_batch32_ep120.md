--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--loss_type=pairwise_rank
--rank_within_protein

--balanced_batches
--balanced_proteins
--double_coldsplit

# batch=16 leaves only 3.95 same-protein pairs per batch and 10% of batches with
# none at all; 32 gives 16.9 pairs and no empty batch (measured on scp2/seed0).
--batch=32

--save_model_in_dynamics
