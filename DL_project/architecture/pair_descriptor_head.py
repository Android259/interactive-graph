import torch

# Fixed token order: 5 of dataloader/New_dataloader.py's _compute_pair_descriptors
# columns (chain, unsaturation, hbond, heavy, occupancy -- "extent" is folded into the
# aromatic/polar tokens' pairing below, not its own token, see PairDescriptorHead), plus
# 2 read directly off the pocket descriptor tensor.
DATALOADER_TOKENS = ("chain", "unsaturation", "hbond", "heavy", "occupancy", "extent")
# Indices into POCKET_DESCRIPTOR_NAMES (dataloader/protein_graph_builder.py): both are
# already scale-free shares (bounded in [0, 1] by construction), unlike raw pocket_extent.
_APOLAR_SASA_SHARE_INDEX = 9
_AROMATIC_SHARE_INDEX = 10


class PairDescriptorHead(torch.nn.Module):
    """Self-attention over a small, fixed set of protein-only, lipid-only and pair
    descriptors (files/... see training/read_configuration.py's --pair_descriptors
    docstring), pooled to one vector concatenated into Final_Layer's fused
    representation.

    Token composition -- all three kinds, not lipid chemistry alone (a protein-blind
    token set here would repeat the exact leak analysis/chemistry_null_model.py
    measures on the main branch, see [[working-triple-explains-protein-wins]] in
    project memory):

      lipid-only   : chain length, unsaturation count, H-bond capacity, heavy-atom
                     count (dataloader/pair_descriptors.py).
      protein-only : coarsened pocket extent (dataloader/New_dataloader.py --
                     coarsened the same way --compatibility_split_input's "clash"
                     term is, so raw cavity size cannot re-identify the held-out
                     protein), aromatic_share and polar_share (1 - apolar_sasa_share),
                     read directly off the pocket descriptor tensor.
      pair         : occupancy = relu(cbrt(heavy_atom_count) - coarse_extent), a
                     cheap, docking-free stand-in for the paper's bound-ligand/cavity
                     volume ratio.

    Unlike --compatibility_input/--pocket_compat_prior, which hand the classifier (or
    the logit) one pre-combined scalar, this hands the tokens to one self-attention
    layer UNCOMBINED and lets it learn which combinations matter -- the whole reason to
    use attention here rather than concatenating raw numbers.

    --no_pair_descriptor_pocket_shares drops the last two (protein-only) tokens,
    leaving 6.
    """

    def __init__(self, config, act_fn=None):
        super().__init__()
        self.dim = config.hiddim
        # --no_pair_descriptor_pocket_shares (training/read_configuration.py): drops
        # the two pocket_descriptor-derived tokens to test whether they -- rather than
        # real pair signal -- are what LBP_BPI_CETP's above-null-model AUC came from
        # (project memory [[descriptors-path-fingerprint-leak]]).
        self.use_pocket_shares = getattr(config, "pair_descriptor_pocket_shares", True)
        self.token_names = DATALOADER_TOKENS + (
            ("aromatic_share", "polar_share") if self.use_pocket_shares else ()
        )
        self.token_count = len(self.token_names)
        self.token_embed = torch.nn.Linear(1, self.dim)
        self.token_identity = torch.nn.Parameter(
            torch.randn(self.token_count, self.dim) * (self.dim ** -0.5)
        )
        self.attention = torch.nn.MultiheadAttention(
            self.dim, config.HEADS, batch_first=True
        )
        self.ln1 = torch.nn.LayerNorm(self.dim)
        self.ln2 = torch.nn.LayerNorm(self.dim)
        hidden = max(config.m * self.dim, self.dim)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(self.dim, hidden),
            act_fn or torch.nn.LeakyReLU(),
            torch.nn.Linear(hidden, self.dim),
        )

    def forward(self, pair_descriptor_input, pocket_descriptor):
        """pair_descriptor_input: [batch, 6] (DATALOADER_TOKENS order).
        pocket_descriptor: [batch, len(POCKET_DESCRIPTOR_NAMES)], raw (unstandardised
        -- both entries read here are already-bounded shares, see module docstring).
        Ignored entirely when --no_pair_descriptor_pocket_shares is set (still passed
        in by Final_Layer.forward, since --pair_descriptors still requires
        --pocket_descriptors either way).
        Returns [batch, hiddim], one vector per sample.
        """
        if self.use_pocket_shares:
            aromatic_share = pocket_descriptor[:, _AROMATIC_SHARE_INDEX]
            polar_share = 1.0 - pocket_descriptor[:, _APOLAR_SASA_SHARE_INDEX]
            scalars = torch.cat(
                [pair_descriptor_input, aromatic_share.unsqueeze(-1), polar_share.unsqueeze(-1)],
                dim=1,
            )  # [batch, token_count]
        else:
            scalars = pair_descriptor_input  # [batch, token_count]

        tokens = self.token_embed(scalars.unsqueeze(-1)) + self.token_identity
        x = self.ln1(tokens)
        attended, _ = self.attention(x, x, x, need_weights=False)
        x = tokens + attended
        x = self.ln2(x)
        x = x + self.ffn(x)
        return x.mean(dim=1)
