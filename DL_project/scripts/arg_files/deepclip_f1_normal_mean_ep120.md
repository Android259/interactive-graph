# DeepCLIP, init arm: identical to deepclip_f1_const_mean except the convolution
# weights start random (normal, std 0.01) instead of all at the constant 0.01.
#
# Two things this answers. First, whether DeepCLIP's constant init matters at all at
# its own one-filter-per-width setting, where it has no symmetry to break and is
# just an unusually small, unusually uniform start. Second -- and the reason this arm
# is in the set rather than a curiosity -- it is the base the capacity sweep runs
# off: at filters>1 the constant init leaves the copies identical forever, so
# deepclip_f4/f8_normal_mean have to differ from SOMETHING in filter count alone,
# and this is that something.
#
# Same 1960 parameters as the reference arm; only the starting values differ.

--ep=120

# One model per protein family (bare: launch/submit_grid.sh appends the group).
--family_only

--deepclip
--lipid_smiles_tokens

--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1

# The only line that differs from deepclip_f1_const_mean.
--deepclip_conv_init=normal

--deepclip_readout=mean
