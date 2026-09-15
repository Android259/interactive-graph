# DeepCLIP, published-readout arm: the paper's network with nothing changed at all.
#
# Differs from the reference arm deepclip_f1_const_mean in --deepclip_readout alone.
# This is the only arm of the five that reproduces DeepCLIP exactly, and it exists to
# put a number on the one place the other four depart from it.
#
# What is expected to go wrong, and why it is still worth running. The published
# readout sums the per-position profile, and DeepCLIP can do that because it pads
# every sequence to one fixed length and never masks (slice_n_pad.py), so its sum
# always runs over the same count. Lipid SMILES are 26-165 characters, and measured
# at initialisation the summed score is 0.4 * character count -- 10.4 at 26
# characters, 66.0 at 165 -- which puts sigmoid at 1.0000 for every molecule in the
# dataset. So at epoch 0 this arm answers "binds" with probability 1 for everything
# and its score is a character counter.
#
# Training may or may not pull it out of that: the LSTM can learn a negative profile
# offset and undo the constant, and molecule size is not pure noise here (it tracks
# lipid class). Both are guesses. The point of the arm is that "the published readout
# does not transfer to variable-length input" is currently an initialisation-time
# measurement and an argument, not a trained result, and the other four arms all rest
# on it.
#
# Read it against deepclip_f1_const_mean specifically, on the same seeds.

--ep=120

# One model per protein family (bare: launch/submit_grid.sh appends the group).
--family_only

--deepclip
--lipid_smiles_tokens

--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=constant

# The only line that differs from deepclip_f1_const_mean.
--deepclip_readout=sum
