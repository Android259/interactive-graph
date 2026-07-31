The original shallow adversary, rescheduled by fit instead of by epoch.

Measured on bbp_nps3mlp_dpt01_wd0001_gm_plm64_hid64_GRL: valid loss sits flat near ln 2 for ~45 epochs, then the model
switches to memorising and valid sensitivity drops to a 0.10-0.28 floor. A constant
lambda=1 spends its whole pressure on the plateau, where nothing has been learned yet.
adv_lambda_ramp_by_fit drives lambda from train balanced accuracy instead: ~0.24 while
the model is still near chance, ~0.86 once it starts to fit -- pressure arrives when
there is finally a shortcut worth suppressing.

Same adversary as the analysed run in every other respect, so any difference is the
schedule alone.

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
