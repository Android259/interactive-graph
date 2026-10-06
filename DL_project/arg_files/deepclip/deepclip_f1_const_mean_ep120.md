# DeepCLIP, reference arm: the published network, unchanged except for the readout.
#
# One of five (deepclip_f1_const_mean, deepclip_f1_normal_mean, deepclip_f4_normal_
# mean, deepclip_f8_normal_mean, deepclip_f1_const_sum). Each differs from a
# neighbour in exactly ONE flag, so a difference in results is attributable:
#
#   f1_const_mean  -> f1_normal_mean   : conv init only (constant 0.01 -> normal)
#   f1_normal_mean -> f4/f8_normal_mean: filter count only (the capacity sweep)
#   f1_const_mean  -> f1_const_sum     : readout only (mean -> the published sum)
#
# The filter sweep runs off the `normal` arm, not off this one, because DeepCLIP's
# constant 0.01 init makes every filter of a width identical with identical
# gradients -- at filters>1 they would stay one filter in N copies, which validate()
# refuses. That is why the init arm exists at all: it is the bridge that lets the
# capacity sweep vary one thing.
#
# --family_only below is the grid's third axis, bare and without a value:
# launch/submit_grid.sh strips it from the template and appends
# --family_only=<group> per job, one model per family x seed, with --label taken
# from this file's own stem. No bespoke submitter needed.
#
# 1960 parameters: 600 of motif scanner, 1360 of BLSTM. No protein encoder, no
# cross-attention, no Final_Layer -- --deepclip builds architecture/deepclip.py alone.

--ep=120

# One model per protein family, trained and validated on that family's own rows --
# the regime DeepCLIP is built for, and the one this project already names after it
# (dataloader/Dataloader.py, training/read_configuration.py).
--family_only

--deepclip
--lipid_smiles_tokens

# DeepCLIP's own constants.py / oned_convlayer_rectify.py values.
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=constant

# The one deliberate departure from the paper, measured rather than assumed: the
# published readout sums the profile over positions, which is length-neutral for
# DeepCLIP only because it pads every sequence to one fixed length and never masks
# (slice_n_pad.py). Lipid SMILES here are 26-165 characters, and at initialisation
# the summed score is 0.4 * character count (26 -> 10.4, 165 -> 66.0), every one
# saturating the sigmoid at P=1.0000. Dividing by the molecule's own length gives
# 0.3998 / 0.4002 / 0.4003 over that range and P=0.599. deepclip_f1_const_sum is the
# arm that measures what this costs or buys on real data.
--deepclip_readout=mean
