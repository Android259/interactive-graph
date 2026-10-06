Probe run: measure the single-partner leakage without suppressing it.

adv_lambda=0 makes gradient reversal a no-op, so the encoder is trained by the task
loss alone and the run is numerically the plain bbp_nps3mlp_dpt01_wd0001_gm_plm64_hid64 baseline. The two adversary heads
still train normally on top of the frozen-from-their-side representations, so their
loss reads as a pure measurement: how well can the label be predicted from ONE partner?

Read "epoch/train adversary loss": ln 2 = 0.693 means a partner alone says nothing and
there is no shortcut for GRL to remove; well below 0.693 means there is. This is the
precondition for every other GRL run -- if the curve sits at 0.693 the whole approach
has nothing to act on, and the remaining files should not be launched.

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
--adv_lambda=0.0
