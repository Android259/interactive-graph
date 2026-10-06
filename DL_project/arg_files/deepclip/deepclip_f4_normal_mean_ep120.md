# DeepCLIP, capacity sweep: 4 learned windows per width instead of 1.
#
# Differs from deepclip_f1_normal_mean in --deepclip_filters alone.
#
# The question. DeepCLIP looks for five motifs in total over a four-letter RNA
# alphabet. SMILES here use 20 characters and encode a chemistry with more than five
# recognisable fragments, so one window per width may simply be too few. Against it:
# a family holds 43-165 positives (10 for ML, 6 for OSBP), and four windows per width
# is 2400 parameters of scanner where one was 600.
#
# Scanner cost: 4 * sum over widths of (vocabulary * width) = 4 * 600 = 2400, and the
# BLSTM's input grows from 5 channels to 20, taking it from 1360 to 2560. 4960
# parameters in total against the reference arm's 1960.

--ep=120

# One model per protein family (bare: launch/submit_grid.sh appends the group).
--family_only

--deepclip
--lipid_smiles_tokens

# The only line that differs from deepclip_f1_normal_mean.
--deepclip_filters=4

--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean
