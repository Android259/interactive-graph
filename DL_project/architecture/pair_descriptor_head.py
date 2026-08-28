import torch

from .mlp_utils import make_self_attention

# Fixed token order: 6 of dataloader/Dataloader.py's _compute_pair_descriptors
# columns (chain, unsaturation, hbond, heavy, occupancy, extent -- 5 under
# --no_pair_descriptor_extent, which drops "extent" alone; occupancy still reads
# coarse_extent internally either way, see PairDescriptorHead/_compute_pair_
# descriptors), plus 2 read directly off the pocket descriptor tensor.
DATALOADER_TOKENS = ("chain", "unsaturation", "hbond", "heavy", "occupancy", "extent")
# --pair_descriptor_lipid_shape's 4 extra dataloader-computed columns (Dataloader.py.
# _compute_pair_descriptors, dataloader/pair_descriptors.py.LIPID_SHAPE_DESCRIPTOR_NAMES),
# inserted between "occupancy" and "extent" in pair_descriptor_input's column order --
# Dataloader.py's pair_descriptor_names list builds the identical order.
LIPID_SHAPE_TOKENS = (
    "radius_of_gyration", "asphericity", "molecular_volume", "rotatable_fraction",
)
# --pair_descriptor_pocket_shares_split's 2 extra dataloader-computed columns (New_
# dataloader.py._compute_pair_descriptors), appended after DATALOADER_TOKENS in the same
# fixed-order convention. No split of aromatic_share exists in POCKET_DESCRIPTOR_NAMES
# to read at forward time the way the plain pair (below) does, so this pair is computed
# per protein in dataloader/pocket_lipid_compatibility.py instead.
SPLIT_DATALOADER_TOKENS = ("aromatic_share_core", "aromatic_share_rim")
# Indices into POCKET_DESCRIPTOR_NAMES (dataloader/protein_graph_builder.py): both are
# already scale-free shares (bounded in [0, 1] by construction), unlike raw pocket_extent.
_APOLAR_SASA_SHARE_INDEX = 9
_AROMATIC_SHARE_INDEX = 10
# hydropathy_core/hydropathy_rim, --pair_descriptor_pocket_shares_split's replacement for
# aromatic_share/polar_share at forward time. Kyte-Doolittle mean, not a share -- not
# bounded in [0, 1] the way the two above are, but standardised the same as everything
# else the classifier that follows this head reads, so the unbounded range costs nothing.
_HYDROPATHY_CORE_INDEX = 11
_HYDROPATHY_RIM_INDEX = 12

# --pair_descriptor_pocket_shares_coarse's band edges for aromatic_share/polar_share.
# FIXED, not train-fit -- unlike coarse_extent (dataloader/Dataloader.py, quantile
# edges cut on TRAIN proteins), these do not depend on any data at all, train or test,
# so there is nothing here for a held-out split to leak into. Three equal-width bands
# are the same destroy-per-protein-resolution move coarse_extent already makes for
# "clash"/occupancy: 35 proteins over 3 bands is ~12 per band, which is what makes a
# share stop reading as close to a protein id.
_SHARE_BAND_EDGES = (1.0 / 3, 2.0 / 3)
_SHARE_BAND_CENTRES = (1.0 / 6, 0.5, 5.0 / 6)


def _coarse_band(values):
    """values (any shape, already in [0, 1]) -> the centre of its fixed-width band."""
    edges = torch.tensor(_SHARE_BAND_EDGES, device=values.device, dtype=values.dtype)
    band = torch.bucketize(values.contiguous(), edges)
    centres = torch.tensor(_SHARE_BAND_CENTRES, device=values.device, dtype=values.dtype)
    return centres[band]


class PairDescriptorHead(torch.nn.Module):
    """Self-attention over a small, fixed set of protein-only, lipid-only and pair
    descriptors (files/... see training/read_configuration.py's --pair_descriptors
    docstring), pooled to one vector concatenated into Final_Layer's fused
    representation.

    Token composition -- all three kinds, not lipid chemistry alone (a protein-blind
    token set here would repeat the exact leak analysis/null_model.py
    measures on the main branch, see [[working-triple-explains-protein-wins]] in
    project memory):

      lipid-only   : chain length, unsaturation count, H-bond capacity, heavy-atom
                     count (dataloader/pair_descriptors.py).
      protein-only : coarsened pocket extent (dataloader/Dataloader.py --
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
    leaving 6. --pair_descriptor_pocket_shares_split replaces them instead, with
    aromatic_share_core, aromatic_share_rim, hydropathy_core, hydropathy_rim -- 10
    tokens total; see SPLIT_DATALOADER_TOKENS and set_pocket_descriptor_normalization.
    --pair_descriptor_pocket_shares_coarse keeps the same two tokens but bands each
    into one of 3 FIXED (not train-fit) thirds before embedding -- see _coarse_band --
    the coarsening coarse_extent already gets, which this pair never did (both
    --split and dropping them outright made project memory
    [[descriptors-path-fingerprint-leak]]'s LBP_BPI_CETP gap wider, not narrower, so
    coarsening the ORIGINAL two rather than replacing them is the untried arm).
    Mutually exclusive with --pair_descriptor_pocket_shares_split (ModelConfig.
    validate) -- two different fixes for the same two tokens.
    --no_pair_descriptor_extent drops "extent" out of DATALOADER_TOKENS on top of
    either of those (occupancy keeps its own coarse_extent regardless -- only the
    standalone token disappears).

    The token stack is reduced to one vector by pool_type (training/read_
    configuration.py) -- the same flag every other pooling site in this project
    answers to, reused rather than hardcoding mean here (see __init__ and
    self.output_dim). --pair_descriptor_flatten skips the reduction and
    concatenates the tokens instead.
    """

    def __init__(self, config, act_fn=None):
        super().__init__()
        self.dim = config.hiddim
        # --no_pair_descriptor_extent (training/read_configuration.py): drops the
        # standalone extent token -- the last DATALOADER_TOKENS entry unexamined by
        # --pair_descriptor_pocket_shares_split, and the one with the highest raw
        # family-identity signal of the three protein-only entries (eta^2 0.78,
        # files/compat_input_audit.md), even after coarsening.
        base_tokens = ("chain", "unsaturation", "hbond", "heavy", "occupancy")
        if getattr(config, "pair_descriptor_lipid_shape", False):
            base_tokens = base_tokens + LIPID_SHAPE_TOKENS
        if getattr(config, "pair_descriptor_extent", True):
            base_tokens = base_tokens + ("extent",)
        # --no_pair_descriptor_occupancy: drops the one token that is neither
        # lipid-only nor protein-only. occupancy is always raw column 4 of
        # pair_descriptor_input regardless of pair_descriptor_extent (chain,
        # unsaturation, hbond, heavy, occupancy[, extent]) -- forward() below drops
        # it there by fixed position.
        self.use_occupancy = getattr(config, "pair_descriptor_occupancy", True)
        if not self.use_occupancy:
            base_tokens = tuple(name for name in base_tokens if name != "occupancy")
        # --no_pair_descriptor_pocket_shares (training/read_configuration.py): drops
        # the two pocket_descriptor-derived tokens to test whether they -- rather than
        # real pair signal -- are what LBP_BPI_CETP's above-null-model AUC came from
        # (project memory [[descriptors-path-fingerprint-leak]]).
        self.use_pocket_shares = getattr(config, "pair_descriptor_pocket_shares", True)
        # --pair_descriptor_pocket_shares_split: aromatic_share_core/rim (already
        # standardised in pair_descriptor_input, dataloader/Dataloader.py) plus
        # hydropathy_core/rim, read raw from pocket_descriptor like aromatic_share/
        # polar_share were -- but unlike those two this pair is not a bounded [0, 1]
        # share, so it needs its own standardisation (see set_pocket_descriptor_
        # normalization below), not skipped the way the two shares' was.
        self.split_pocket_shares = self.use_pocket_shares and getattr(
            config, "pair_descriptor_pocket_shares_split", False
        )
        # --pair_descriptor_pocket_shares_coarse (see class docstring): bands the
        # ORIGINAL aromatic_share/polar_share pair instead of replacing it.
        # ModelConfig.validate rejects combining this with _split -- both edit the
        # same two tokens.
        self.coarse_pocket_shares = self.use_pocket_shares and getattr(
            config, "pair_descriptor_pocket_shares_coarse", False
        )
        if self.split_pocket_shares:
            self.token_names = (
                base_tokens + SPLIT_DATALOADER_TOKENS
                + ("hydropathy_core", "hydropathy_rim")
            )
            self.register_buffer("hydropathy_mean", torch.zeros(2))
            self.register_buffer("hydropathy_std", torch.ones(2))
        elif self.coarse_pocket_shares:
            self.token_names = base_tokens + ("aromatic_share_coarse", "polar_share_coarse")
        else:
            self.token_names = base_tokens + (
                ("aromatic_share", "polar_share") if self.use_pocket_shares else ()
            )
        self.token_count = len(self.token_names)
        self.token_embed = torch.nn.Linear(1, self.dim)
        self.token_identity = torch.nn.Parameter(
            torch.randn(self.token_count, self.dim) * (self.dim ** -0.5)
        )
        self.attention = make_self_attention(
            self.dim, config.HEADS, config, act_fn, batch_first=True
        )
        self.ln1 = torch.nn.LayerNorm(self.dim)
        self.ln2 = torch.nn.LayerNorm(self.dim)
        hidden = max(config.m * self.dim, self.dim)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(self.dim, hidden),
            act_fn or torch.nn.LeakyReLU(),
            torch.nn.Linear(hidden, self.dim),
        )

        # --- token-axis reduction: pool_type, tied to the project's existing flag --
        # descriptors_head has no protein/lipid pooling anywhere else for pool_type to
        # affect, so without this it would be read and silently ignored here.
        # --pair_descriptor_flatten takes priority, same as attention_pooling/
        # swe_pooling already take priority over pool_type in Final_Layer's own
        # pooling -- concatenates the tokens instead of reducing them, so the
        # classifier reads every token's post-attention state at its own fixed
        # position rather than one pool_type-reduced summary of all of them.
        self.flatten = getattr(config, "pair_descriptor_flatten", False)
        self.pool_type = getattr(config, "pool_type", "mean")
        if self.flatten:
            self.output_dim = self.token_count * self.dim
        elif self.pool_type == "gem":
            # Deferred import: architecture.final_layer imports PairDescriptorHead,
            # so importing GeMPool from there at module load time would be circular.
            # By the time __init__ runs (Final_Layer builds this head from inside
            # its own __init__), final_layer.py has already finished importing.
            from architecture.final_layer import GeMPool

            self.gem_pool = GeMPool()
            self.output_dim = self.dim
        else:
            # global_add_pool / global_max_pool / global_mean_pool / the add_max
            # concat -- the same stateless functions Final_Layer's own pool_type
            # resolves to (training/read_configuration.py's ModelConfig.pool), just
            # applied over this head's fixed token axis instead of a graph's nodes
            # (see forward()'s synthetic batch index).
            self._pool_fn = config.pool
            self.output_dim = 2 * self.dim if self.pool_type == "add_max" else self.dim

    def set_pocket_descriptor_normalization(self, stats):
        """Install train-only mean/std for hydropathy_core/hydropathy_rim.

        Same stats dict ProteinEncoder.set_pocket_descriptor_normalization consumes
        (dataloader/protein_graph_builder.py's pocket_descriptor_stats -- train
        proteins only, one source of truth) via InteractionClassification.
        set_pair_descriptor_pocket_share_normalization; unlike ProteinEncoder's copy,
        which architecture/protein_encoder.py only fills under --rnabang_frozen_node_
        adapter, this one is meant to always be filled when --pair_descriptor_pocket_
        shares_split is on, so it no-ops rather than silently leaving hydropathy raw
        when the split is off or stats are unavailable.
        """
        if not self.split_pocket_shares or stats is None:
            return
        mean = stats["pocket_descriptor_mean"]
        std = stats["pocket_descriptor_std"]
        self.hydropathy_mean.copy_(
            torch.as_tensor(
                [mean[_HYDROPATHY_CORE_INDEX], mean[_HYDROPATHY_RIM_INDEX]],
                dtype=self.hydropathy_mean.dtype,
            )
        )
        self.hydropathy_std.copy_(
            torch.as_tensor(
                [std[_HYDROPATHY_CORE_INDEX], std[_HYDROPATHY_RIM_INDEX]],
                dtype=self.hydropathy_std.dtype,
            )
        )

    def forward(self, pair_descriptor_input, pocket_descriptor):
        """pair_descriptor_input: [batch, token_count] (DATALOADER_TOKENS order, plus
        SPLIT_DATALOADER_TOKENS when --pair_descriptor_pocket_shares_split is on).
        pocket_descriptor: [batch, len(POCKET_DESCRIPTOR_NAMES)], raw (unstandardised
        -- aromatic_share/apolar_sasa_share are already-bounded shares, see module
        docstring; hydropathy_core/hydropathy_rim are standardised here instead, see
        set_pocket_descriptor_normalization).
        Ignored entirely when --no_pair_descriptor_pocket_shares is set (still passed
        in by Final_Layer.forward, since --pair_descriptors still requires
        --pocket_descriptors either way).
        Returns [batch, self.output_dim] (hiddim, unless --pair_descriptor_flatten or
        pool_type=="add_max" widen it -- see __init__), one vector per sample.
        """
        if not self.use_occupancy:
            pair_descriptor_input = torch.cat(
                [pair_descriptor_input[:, :4], pair_descriptor_input[:, 5:]], dim=1
            )
        if self.split_pocket_shares:
            hydropathy = (
                pocket_descriptor[:, [_HYDROPATHY_CORE_INDEX, _HYDROPATHY_RIM_INDEX]]
                - self.hydropathy_mean
            ) / self.hydropathy_std
            scalars = torch.cat([pair_descriptor_input, hydropathy], dim=1)
        elif self.coarse_pocket_shares:
            aromatic_share = _coarse_band(pocket_descriptor[:, _AROMATIC_SHARE_INDEX])
            polar_share = _coarse_band(1.0 - pocket_descriptor[:, _APOLAR_SASA_SHARE_INDEX])
            scalars = torch.cat(
                [pair_descriptor_input, aromatic_share.unsqueeze(-1), polar_share.unsqueeze(-1)],
                dim=1,
            )
        elif self.use_pocket_shares:
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
        x = x + self.ffn(x)  # [batch, token_count, hiddim]

        if self.flatten:
            return x.flatten(1)

        # A synthetic PyG batch index turns this head's fixed token axis into the
        # scatter shape global_add_pool/global_max_pool/global_mean_pool/GeMPool
        # already expect (node axis + a graph-id per node) -- every sample owns
        # exactly token_count consecutive rows, so arange().repeat_interleave() names
        # them without needing an actual variable-size graph anywhere.
        batch_size = x.shape[0]
        flat = x.reshape(batch_size * self.token_count, self.dim)
        index = torch.arange(batch_size, device=x.device).repeat_interleave(self.token_count)
        if self.pool_type == "gem":
            return self.gem_pool(flat, index)
        return self._pool_fn(flat, index)
