# Control arm: the lipid half of the compatibility feature alone.
#
#   -chain_length(l)   standardised, and nothing else -- pocket_extent never reaches
#                      the model, so eta^2 against protein identity is 0.0001.
#
# What it settles (files/compat_input_audit.md 1.3, 7.2): the shipped difference and the
# raw chain length rank a held-out block identically inside protein, 0.579 both, so on
# the RAW numbers the pocket half contributes nothing. But the network reads its input
# through a nonlinearity, and relu(chain - extent) cannot be built without extent -- a
# model given only the chain length cannot tell a 15 A cavity from a 30 A one and must
# treat every protein alike. The raw numbers agree; the set of functions buildable from
# them does not. Only this arm says which matters.
#
# 27 318 parameters, the same as ..._compatinput_..., so the comparison is one input
# against one input.
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
--compat_input_parts="chain"
--compat_extent_bins=4

--save_model_in_dynamics
