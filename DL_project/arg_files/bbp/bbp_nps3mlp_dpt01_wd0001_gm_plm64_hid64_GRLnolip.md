Drop the LIPID adversary, keep the protein one.

The sharpest test of whether the lipid-side adversary earns its place. Measured on
groups_CRAL-TRIO, lipid_only reaches valid BA 0.619/0.586 while the full model reaches
0.451/0.433 -- the lipid pathway is the one that transfers across families. The lipid
adversary exists to make lip1 individually uninformative about the label, which is
precisely that pathway. If it is costing more than the shortcut it removes, this run
beats both bbp_nps3mlp_dpt01_wd0001_gm_plm64_hid64_GRL and bbp_nps3mlp_dpt01_wd0001_gm_plm64_hid64_GRLfit.

Pairs with _GRLnoprot as the mirror ablation; run this one first, it is the one the
lipid_only result predicts.

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
--adv_lambda_ramp_by_fit
--no_adv_lipid
