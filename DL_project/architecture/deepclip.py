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

from dataloader.pair_descriptors import full_catalog_order, parse_descriptor_list
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
        # --deepclip_lipid_descriptors widens the per-character input: the named
        # catalog quantities are broadcast onto every position beside the one-hot,
        # so a window sees "these characters, in a molecule with this head group"
        # rather than having to recover the head group from the characters alone.
        descriptor_width = 0
        lipid_descriptor_columns = None
        lipid_descriptor_tokens = parse_descriptor_list(
            getattr(config, "deepclip_lipid_descriptors", "")
        )
        if lipid_descriptor_tokens:
            catalog_index = {
                name: position
                for position, name in enumerate(full_catalog_order(config))
            }
            lipid_descriptor_columns = torch.tensor(
                [catalog_index[name] for name in lipid_descriptor_tokens],
                dtype=torch.long,
            )
            descriptor_width = len(lipid_descriptor_tokens)
        # register_buffer, not a plain attribute, so the column index follows the
        # module to whatever device the model moves to -- and registered even when
        # empty, because a buffer name cannot be assigned first and registered after.
        self.register_buffer(
            "lipid_descriptor_columns", lipid_descriptor_columns, persistent=False
        )
        conv_in = vocabulary + descriptor_width

        self.convs = torch.nn.ModuleList([
            torch.nn.Conv1d(conv_in, filters, width, padding="same", bias=False)
            for width in widths
        ])
        # --deepclip_conv_layers: further layers read the concatenated filter
        # channels of the one before, so the receptive field grows by (width - 1)
        # per layer -- the only way, short of a wider window, for the branch to see
        # across a ring closure (32-38 characters here) at all.
        self.extra_convs = torch.nn.ModuleList()
        stacked = int(getattr(config, "deepclip_conv_layers", 1))
        for _ in range(max(0, stacked - 1)):
            self.extra_convs.append(torch.nn.ModuleList([
                torch.nn.Conv1d(
                    filters * len(widths), filters, width, padding="same", bias=False
                )
                for width in widths
            ]))
        for conv in list(self.convs) + [c for layer in self.extra_convs for c in layer]:
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

        # The weights of Sum_last_ax. DeepCLIP's own are a fixed 1.0 each and are
        # what `None` here means; the two flags below are the two ways to make them
        # something else, and validate() refuses both at once because they write
        # the same vector.
        self.profile_weights = None
        if getattr(config, "deepclip_profile_weights", False):
            # Initialised at 1.0: the run starts as published DeepCLIP exactly, and
            # only departs from it if the gradient pays for the departure.
            self.profile_weights = torch.nn.Parameter(torch.ones(hidden))
        self.gate = None
        gate_columns = None
        gate_tokens = parse_descriptor_list(getattr(config, "deepclip_protein_gate", ""))
        if gate_tokens:
            catalog_index = {
                name: position
                for position, name in enumerate(full_catalog_order(config))
            }
            gate_columns = torch.tensor(
                [catalog_index[name] for name in gate_tokens], dtype=torch.long
            )
            gate_hidden = int(getattr(config, "deepclip_gate_hidden", 8))
            # hidden + 1 outputs, not hidden: the extra one is an additive bias on the
            # final score (forward() splits it back off), not another profile weight.
            # Why a bias is needed at all: the published readout (docstring above) has
            # none anywhere -- DeepCLIP trains one model per protein, so whatever
            # constant shift a protein needs is absorbed into the conv/LSTM weights
            # themselves. A shared multiplicative gate across several proteins does not
            # have that freedom: `weights = 1 + MLP(pocket)` scales the WHOLE profile
            # for one protein, and if that scaling lands the same sign on every
            # position (plausible on a data-starved family -- GLTP/GLTPD1 at ~25-30
            # positives each), the bias-free sum collapses to a constant answer for
            # every lipid that protein sees, regardless of sequence (measured: several
            # seeds of deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120 land at
            # specificity exactly 0.0 or 1.0 while AUC stays informative -- an ordering
            # signal the fixed threshold cannot express, files/deepclip_gate_and_
            # subclass_plan.md's running log). A per-protein bias gives the gate a
            # degree of freedom to correct that shift independently of the profile's
            # own scale, instead of every departure from 0 having to run through the
            # same channels that also carry the sequence signal.
            self.gate = torch.nn.Sequential(
                torch.nn.Linear(len(gate_tokens), gate_hidden),
                torch.nn.ReLU(),
                torch.nn.Linear(gate_hidden, hidden + 1),
            )
            # Last layer at zero, so the gate starts as the all-ones vector the
            # published readout uses (the +1.0 in forward) and every departure from
            # DeepCLIP is something the pocket had to earn.
            torch.nn.init.zeros_(self.gate[-1].weight)
            torch.nn.init.zeros_(self.gate[-1].bias)
        self.register_buffer("gate_columns", gate_columns, persistent=False)

    def forward(self, lip, lip_batch, descriptor_catalog_input=None):
        """`[nodes, vocabulary]` one-hot characters -> `[graphs, 2]` logits.

        The lipid arrives flat, every molecule of the batch stacked into one tensor
        with `lip_batch` saying which rows belong together. to_dense_batch restores
        the per-molecule sequence axis a convolution and an LSTM both need, and its
        mask is what keeps padded positions out of the profile sum below -- without
        that, a short molecule in a batch with a long one would have the padding
        counted into its score.
        """
        dense, mask = to_dense_batch(lip, lip_batch)
        if self.lipid_descriptor_columns is not None:
            if descriptor_catalog_input is None:
                raise ValueError(
                    "deepclip_lipid_descriptors requires descriptor_catalog_input"
                )
            selected = descriptor_catalog_input.index_select(
                1, self.lipid_descriptor_columns
            ).to(dense.dtype)
            # One row per graph, held constant along the character axis: these are
            # properties of the molecule, not of a position in its spelling.
            broadcast = selected.unsqueeze(1).expand(-1, dense.shape[1], -1)
            dense = torch.cat((dense, broadcast * mask.unsqueeze(-1)), dim=-1)
        scanned = torch.cat(
            [conv(dense.transpose(1, 2)) for conv in self.convs], dim=1
        )
        scanned = self.conv_act(scanned)
        for layer in self.extra_convs:
            scanned = self.conv_act(
                torch.cat([conv(scanned) for conv in layer], dim=1)
            )
        scanned = scanned.transpose(1, 2)

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
        gate_bias = None
        if self.gate is not None:
            if descriptor_catalog_input is None:
                raise ValueError(
                    "deepclip_protein_gate requires descriptor_catalog_input"
                )
            gate_input = descriptor_catalog_input.index_select(
                1, self.gate_columns
            ).to(states.dtype)
            gate_out = torch.tanh(self.gate(gate_input))
            # tanh bounds every gate output to (-1, 1) before it touches the profile or
            # the score, so neither the per-channel weights nor the bias can run away to
            # an extreme the way the raw linear output could -- measured on
            # deepclip_cral_trio_protein_gate_subclass_pa_ep120 (files/deepclip_gate_
            # and_subclass_plan.md's running log): adding an unbounded additive bias
            # alone barely moved specificity-collapse rate (7/10 seeds at
            # specificity 0 or 1 -> 6/10), consistent with the bias learning its own
            # runaway constant on the same data-starved family instead of a useful
            # correction. tanh(0) = 0 exactly, so a zero-initialised gate is still
            # published DeepCLIP's all-ones, no-bias sum -- this changes what the gate
            # CAN reach under gradient pressure, not where it starts.
            # +1.0 so a zero-initialised gate IS the published all-ones sum, and a
            # pocket that says nothing leaves the profile exactly as DeepCLIP's. The
            # last output column is the additive bias instead (also zero at init, so
            # it too starts as a no-op); split off BEFORE the +1.0, which only the
            # multiplicative weights get. Weights therefore live in (0, 2) -- bounded
            # away from 0 too, so a channel cannot be silenced outright, only damped.
            #
            # Mean-centred across channels: tanh alone bounded the PER-CHANNEL
            # magnitude but did nothing to stop every channel moving the SAME way at
            # once, which is the actual collapse mechanism (a protein whose gate
            # departs uniformly scales the whole profile toward one sign, regardless
            # of sequence -- measured: bias alone and bias+tanh gave statistically
            # identical specificity-collapse rates, files/deepclip_gate_and_subclass_
            # plan.md's running log). Subtracting the channel mean before the +1.0
            # forces weights.mean(channel) == 1.0 exactly, so this pathway can only
            # REDISTRIBUTE emphasis across profile channels, never scale all of them
            # up or down together -- any genuine protein-level shift has to go
            # through gate_bias instead, which is the one place that shift is
            # actually wanted and can be reasoned about on its own.
            channel_out = gate_out[:, :-1]
            channel_out = channel_out - channel_out.mean(dim=-1, keepdim=True)
            weights = (1.0 + channel_out).unsqueeze(1)
            gate_bias = gate_out[:, -1]
            profile = (states * weights).sum(dim=-1)
        elif self.profile_weights is not None:
            profile = (states * self.profile_weights).sum(dim=-1)
        else:
            profile = states.sum(dim=-1)
        profile = profile.masked_fill(~mask, 0.0)
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
        if gate_bias is not None:
            # Added AFTER the mean/sum readout, not folded into the profile: a
            # protein's calibration shift is one number per protein, not something
            # that should shrink with a longer molecule the way the summed profile
            # itself does under "sum" readout.
            score = score + gate_bias
        return torch.stack([torch.zeros_like(score), score], dim=1)
