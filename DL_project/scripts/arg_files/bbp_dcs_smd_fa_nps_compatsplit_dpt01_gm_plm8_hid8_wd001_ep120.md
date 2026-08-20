# Both halves of the compatibility feature, as two separate inputs.
#
#   -chain_length(l)                     the lipid-only marginal, named explicitly
#   relu(chain_length - pocket_extent)   the pair term, on a coarsened extent
#
# Replaces the single difference of --compatibility_input, which mixes them: that
# difference is additive, so its own pair content is exactly 0.0000, and it carries
# eta^2 0.78 against protein identity through pocket_extent at full resolution
# (files/compat_input_audit.md 1.3, 6.3). Split apart, the marginal can be reported
# against and adversarially removed, and the pair half sits at eta^2 0.16 against
# family -- below the 0.28-0.85 band that rejected the pocket descriptors.
#
# 27 350 parameters, = 27 286 + 2 x 32. Compare against:
#   ..._nps_dpt01_...           base, neither half
#   ..._nps_compatinput_...     the same information as one difference
#   ..._nps_chainonly_...       the marginal half alone
#   ..._nps_clashonly_...       the pair half alone
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
--compat_input_parts="chain,clash"
--compat_extent_bins=4

--save_model_in_dynamics
