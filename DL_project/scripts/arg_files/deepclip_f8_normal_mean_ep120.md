# DeepCLIP, capacity sweep: 8 learned windows per width.
#
# Differs from deepclip_f4_normal_mean in --deepclip_filters alone, and from
# deepclip_f1_normal_mean in the same single flag, so the three of them read as one
# curve: 1 -> 4 -> 8 windows per width.
#
# This is the far end of the sweep on purpose. 40 windows over a family with 43-165
# positives is roughly one learned parameter per two training rows once the BLSTM is
# counted, so if capacity is what the reference arm lacks this should show it, and if
# overfitting is the real constraint this is where it becomes visible. Whichever it
# is, it is only interpretable next to the other two points -- read it as the end of
# the curve, not on its own.
#
# 4800 of scanner + 4160 of BLSTM (its input is 40 channels here) = 8960 parameters,
# against 4960 at four filters and 1960 at one.

--ep=120

# One model per protein family (bare: launch/submit_grid.sh appends the group).
--family_only

--deepclip
--lipid_smiles_tokens

# The only line that differs from deepclip_f4_normal_mean.
--deepclip_filters=8

--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean
