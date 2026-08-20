# Control arm: the pair half of the compatibility feature alone.
#
#   relu(chain_length(l) - pocket_extent(p))   on a coarsened extent, standardised,
#                                              and nothing else.
#
# The mirror of ..._chainonly_...: there the protein is absent, here the lipid-only
# marginal is. This is the arm that answers the question the whole audit turns on --
# whether anything survives once the chain-length shortcut is taken away
# (files/compat_input_audit.md 6.2).
#
# What is known before the run. The term is genuinely non-additive: interaction share
# 0.229 against the shipped difference's 0.0000, so unlike the difference it carries
# pair content of its own. It is also the only candidate form whose eta^2 against family
# falls below the 0.28-0.85 band that rejected every pocket descriptor -- 0.207 at full
# extent resolution, 0.161 at four levels. And it is weaker alone than the marginal is:
# 0.535 inside protein against 0.579. So a result here would be smaller and worth more.
#
# 27 318 parameters, matching ..._chainonly_... and ..._compatinput_... exactly.
--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--balanced_batches
--balanced_proteins
--double_coldsplit

--compatibility_split_input
--compat_input_parts="clash"
--compat_extent_bins=4

--save_model_in_dynamics
