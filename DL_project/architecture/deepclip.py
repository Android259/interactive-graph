"""DeepCLIP, as published, reading canonical SMILES instead of RNA.

Gronning et al., "DeepCLIP: predicting the effect of mutations on protein-RNA
binding with deep learning", Nucleic Acids Research 48(13), 2020. Structure and
every default here are taken from its own source (github.com/deepclip/deepclip,
network.py and constants.py), not from a description of it:

    one-hot sequence
      -> one Conv1d per filter width, FILTER_SIZES = [4, 5, 6, 7, 8],
         NUM_FILTERS = 1 of each
      -> a single bidirectional LSTM, LSTM_NODES = 10 per direction
      -> the two directions are SUMMED (network.py's l_sumz2x), then summed over
         the hidden axis (Sum_last_ax) -> one number per position: the binding
         profile, and the thing DeepCLIP is actually known for
      -> the profile is summed over positions (DenseLayer num_units=1,
         W=Constant(1.0), b=None -- a fixed unit weight and no bias) -> one score
      -> sigmoid

This is the whole network. At its published defaults it is ~1.9k parameters on a
20-character SMILES alphabet (~1.4k on RNA's four bases), and that is the design,
not a scaled-down version of one: DeepCLIP trains ONE model per protein on that
protein's own few thousand sequences, which is the regime --family_only puts this
project in (dataloader/Dataloader.py's own comment names DeepCLIP for exactly
this).

Nothing else from this project's architecture is involved. There is no protein
encoder, no cross-attention, no self-attention tower, no pooling flag and no
Final_Layer: InteractionClassification builds this module ALONE under --deepclip,
the same way it builds only a descriptor head under --descriptors_head. The lipid
is the whole input, which is what DeepCLIP is -- a per-protein sequence model --
rather than an ablation of a two-partner model.

Two deliberate departures from the source, both forced and both local:

1. padding="same" where DeepCLIP pads "valid". With several widths at once, valid
   padding leaves each width a different output length, and they have to be
   concatenated channel-wise before the LSTM. "same" keeps every width at the
   molecule's own length. A window hanging off the end then reads zeros, which in
   one-hot space is "no character" -- the same thing running off the end means.
2. Two logits out, not one sigmoid. This project's loss and every metric read
   `[batch, 2]` (AGENTS.md's invariant). Emitting `[0, score]` is not a re-fit:
   softmax([0, s])[1] IS sigmoid(s), so the decision and the probability are
   DeepCLIP's own, and the zero column carries no parameters.
"""

import torch
from torch_geometric.utils import to_dense_batch

from dataloader.smiles_tokens import SMILES_VOCABULARY
from training.read_configuration import parse_deepclip_widths


class DeepCLIP(torch.nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        widths = parse_deepclip_widths(config.deepclip_widths)
        filters = int(config.deepclip_filters)
        vocabulary = len(SMILES_VOCABULARY)

        # One convolution per width, `filters` of each -- DeepCLIP's NUM_FILTERS is
        # per width, not in total, and its own value is 1. Each learned window is a
        # (width x vocabulary) table of weights, which is why it can be drawn directly
        # as a sequence logo: the table IS the motif.
        #
        # bias=False and the constant 0.01 initialisation are both DeepCLIP's, from
        # oned_convlayer_rectify.py (W=lasagne.init.Constant(0.01), b=None). The
        # initialisation is not a detail: PyTorch's default here has std ~0.053, five
        # times larger, and that alone drives the summed profile far enough to
        # saturate the output sigmoid at initialisation.
        #
        # Constant init leaves every filter of one width IDENTICAL, with identical
        # gradients, forever. That is harmless at DeepCLIP's own NUM_FILTERS=1 (one
        # filter per width, nothing to be identical to) and fatal above it, so
        # validate() refuses filters > 1 unless the initialisation is changed.
        self.convs = torch.nn.ModuleList([
            torch.nn.Conv1d(vocabulary, filters, width, padding="same", bias=False)
            for width in widths
        ])
        for conv in self.convs:
            if config.deepclip_conv_init == "constant":
                torch.nn.init.constant_(conv.weight, 0.01)
            else:
                torch.nn.init.normal_(conv.weight, std=0.01)
        # ReLU: DeepCLIP's convolutional layers are rectified (network.py builds them
        # through oned_convlayer_rectify).
        self.conv_act = torch.nn.ReLU()
        hidden = int(config.deepclip_lstm)
        self.lstm = torch.nn.LSTM(
            filters * len(widths),
            hidden,
            batch_first=True,
            bidirectional=True,
        )
        self.hidden = hidden
        # DeepCLIP applies dropout to the BLSTM output and, separately, to the
        # profile (LSTM_DROPOUT = 0.1, DROPOUT_OUT = 0.0 at its defaults).
        self.lstm_dropout = torch.nn.Dropout(float(config.deepclip_lstm_dropout))
        self.profile_dropout = torch.nn.Dropout(float(config.deepclip_out_dropout))

    def forward(self, lip, lip_batch):
        """`[nodes, vocabulary]` one-hot characters -> `[graphs, 2]` logits.

        The lipid arrives flat, every molecule of the batch stacked into one tensor
        with `lip_batch` saying which rows belong together. to_dense_batch restores
        the per-molecule sequence axis a convolution and an LSTM both need, and its
        mask is what keeps padded positions out of the profile sum below -- without
        that, a short molecule in a batch with a long one would have the padding
        counted into its score.
        """
        dense, mask = to_dense_batch(lip, lip_batch)
        scanned = torch.cat(
            [conv(dense.transpose(1, 2)) for conv in self.convs], dim=1
        )
        scanned = self.conv_act(scanned).transpose(1, 2)

        # Packed, not run over the padded tensor. Masking the LSTM's output would not
        # be enough: the backward direction starts at the LAST position, so on a short
        # molecule padded up to a longer one in the same batch it would consume the
        # padding first and arrive at the real characters with contaminated state --
        # the molecule would then score differently depending on what it was batched
        # with. Packing makes each direction start and stop at that molecule's own
        # ends. (The convolution above needs no such care: a window reaching into the
        # zero padding reads the same nothing it reads running off the end of the
        # string, which is what padding="same" gives it when the molecule is alone.)
        lengths = mask.sum(dim=1).cpu()
        packed = torch.nn.utils.rnn.pack_padded_sequence(
            scanned, lengths, batch_first=True, enforce_sorted=False
        )
        states, _ = self.lstm(packed)
        states, _ = torch.nn.utils.rnn.pad_packed_sequence(
            states, batch_first=True, total_length=scanned.shape[1]
        )
        states = self.lstm_dropout(states)
        # l_sumz2x: the two directions are SUMMED, not concatenated.
        states = states[:, :, : self.hidden] + states[:, :, self.hidden :]
        # Sum_last_ax: one number per position. This vector is the binding profile
        # -- the per-character readout DeepCLIP's motif logos and mutation maps are
        # built from -- so it is kept on the module for anything that wants to read
        # it, rather than only existing inside this expression.
        profile = states.sum(dim=-1).masked_fill(~mask, 0.0)
        self.profile = profile
        profile = self.profile_dropout(profile)

        # The output unit: a fixed weight of one over the profile and no bias -- the
        # plain sum of the profile. DeepCLIP can sum because it pads every sequence to
        # one fixed length and never masks, so the count of summed positions is the
        # same for every input; here molecules are 26-165 characters and that sum
        # reads length instead (see ModelConfig.deepclip_readout for the measurement).
        # "mean" divides by this molecule's own character count to remove exactly that.
        score = profile.sum(dim=-1)
        if self.config.deepclip_readout == "mean":
            score = score / lengths.to(score.device).clamp(min=1)
        return torch.stack([torch.zeros_like(score), score], dim=1)
