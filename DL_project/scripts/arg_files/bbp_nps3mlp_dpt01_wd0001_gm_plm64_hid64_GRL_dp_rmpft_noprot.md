Mirror of _GRLnolip: keep the LIPID adversary, drop the protein one.

Only interpretable next to _GRLnolip. Together the pair splits the effect of the
original two-sided adversary into its halves, at the cost of one extra run.

Expected weak: protein_only sits at chance (train BA 0.510/0.504) under
balanced_proteins, so there is little protein-side signal for its adversary to be
protecting. Launch only if _GRLnolip changes the picture and the split needs attributing.

--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--hiddim=64
--plm_compression_dim=64

--dropout=0.1
--weight_decay=0.001
--pool_type="gem"

--balanced_batches
--balanced_proteins

--adversarial_grl
--adv_weight=1.0
--adv_lambda=1.0
--adv_deep
--adv_lambda_ramp_by_fit
--no_adv_protein
