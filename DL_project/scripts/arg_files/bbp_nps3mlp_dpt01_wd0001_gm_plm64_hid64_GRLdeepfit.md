Best-guess configuration: capacity matched AND scheduled by fit.

The shallow 2-layer adversary carries 4290 parameters per side against the 49984 of the
cross-attention block it has to keep honest, so leakage the block can decode but the
probe cannot is never penalised. adv_deep replaces it with the same block minus the
multihead (MLP of width 2*dim standing in for the Q/K/V/O budget, then the FFN, both
LayerNorms, both residuals) at 50050 parameters.

Combined with the fit ramp because a larger adversary at constant lambda=1 pushes harder
from epoch 1 and risks starving the encoder outright. Run after _GRLfit: if that already
recovers sensitivity, this says whether capacity was also binding.

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
--adv_deep
--adv_weight=1.0
--adv_lambda=1.0
--adv_lambda_ramp_by_fit
