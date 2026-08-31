import torch
import torch_geometric

from dataloader.protein_graph_builder import (
    POCKET_DESCRIPTOR_FAMILY_NEUTRAL_INDICES, POCKET_DESCRIPTOR_NAMES,
)
from dataloader.pair_descriptors import full_catalog_order, parse_descriptor_list

from .edge_node_encoder import DeepSetsEdgeEncoder, SetTransformerEdgeEncoder
from .geometric_transformer import ProteinGeometricTransformerBlock
from .edge_geometric_conv import EdgeAttentionConv, EdgeMLPConv
from .protein_edge_geometry import STRUCTURED_EDGE_DIM, structured_edge_features
from .self_attention import ProteinSelfAttention
from .pair_descriptor_head import _APOLAR_SASA_SHARE_INDEX, _AROMATIC_SHARE_INDEX
from .mlp_utils import (
    make_activation, make_dropout, make_extra_hidden_layer,
    make_optional_projection, make_norm_layer, apply_norm,
    build_sequential_compression, HeadGate, insert_hidden_gate,
    insert_input_gate, insert_output_gate, mlp_hidden_dims,
    link_concrete_dropouts
)


class Protein_encoder(torch.nn.Module):
    def __init__(
        self,
        config,
        start=True,
        act_fn=None,
    ) -> None:
        """Initialize a protein GATv2 encoder block."""
        super(Protein_encoder, self).__init__()
        self.config = config
        hiddim = self.config.hiddim
        self.rnabang_full_encoder = bool(
            start and getattr(self.config, "rnabang_full_protein_encoder", False)
        )
        self.rnabang_residual_with_esm3 = bool(
            start and getattr(self.config, "rnabang_residual_with_esm3", False)
        )
        self.rnabang_no_gat = bool(
            getattr(self.config, "rnabang_residual_with_esm3", False)
        )
        self.use_gine_conv = bool(self.config.gine_conv)
        self.use_geometric_transformer = bool(
            getattr(self.config, "geometric_transformer", False)
        )
        self.use_edge_attention = bool(
            getattr(self.config, "protein_edge_attention", False)
        )
        self.use_edge_mlp = bool(getattr(self.config, "protein_edge_mlp", False))
        self.use_structured_edges = self.use_edge_attention or self.use_edge_mlp
        self.use_rnabang_frozen_node_adapter = bool(
            start and getattr(self.config, "rnabang_frozen_node_adapter", False)
        )

        if self.use_rnabang_frozen_node_adapter:
            self.use_residue_type_embedding = bool(
                getattr(self.config, "rnabang_residue_type_embedding", False)
            )
            self.rnabang_norm = torch.nn.LayerNorm(
                self.config.rnabang_embedding_dim
            )
            if self.use_residue_type_embedding:
                self.residue_type_embedding = torch.nn.Embedding(20, 8)
            self.edge_node_encoder = None
            if getattr(self.config, "rnabang_edge_deepsets", False):
                self.edge_node_encoder = DeepSetsEdgeEncoder()
                edge_feature_dim = self.edge_node_encoder.output_dim
            elif getattr(self.config, "rnabang_edge_set_transformer", False):
                self.edge_node_encoder = SetTransformerEdgeEncoder()
                edge_feature_dim = self.edge_node_encoder.output_dim
            elif getattr(self.config, "rnabang_edge_topk_by_area", False):
                edge_feature_dim = 43
            elif getattr(self.config, "rnabang_edge_pna", False):
                edge_feature_dim = 13
            elif getattr(self.config, "rnabang_edge_quantiles", False):
                edge_feature_dim = 18
            else:
                edge_feature_dim = 2
            adapter_input_dim = (
                self.config.rnabang_embedding_dim
                + (8 if self.use_residue_type_embedding else 1)
                + 3
                + edge_feature_dim
            )
            self.register_buffer("structural_mean", torch.zeros(3))
            self.register_buffer("structural_std", torch.ones(3))
            self.register_buffer("edge_feature_mean", torch.zeros(edge_feature_dim))
            self.register_buffer("edge_feature_std", torch.ones(edge_feature_dim))
            self.register_buffer("edge_pair_mean", torch.zeros(2))
            self.register_buffer("edge_pair_std", torch.ones(2))
            self.rnabang_node_adapter = torch.nn.Sequential(
                torch.nn.Linear(adapter_input_dim, 2 * hiddim),
                torch.nn.GELU(),
                torch.nn.Linear(2 * hiddim, hiddim),
                torch.nn.LayerNorm(hiddim),
            )
            return

        if self.rnabang_full_encoder:
            self.rnabang_projection = torch.nn.Linear(
                self.config.rnabang_embedding_dim, hiddim
            )
            if self.config.protein_self_attention:
                self.attention = ProteinSelfAttention(hiddim, self.config)
            post_sa_layers = []
            if not getattr(self.config, "protein_disable_post_sa_mlp", False):
                post_enlarged, post_last = mlp_hidden_dims(
                    self.config, "protein_post_sa", hiddim * self.config.m
                )
                post_extra = make_extra_hidden_layer(
                    post_enlarged, post_last, self.config, act_fn
                )
                post_sa_layers = [
                    torch.nn.Linear(hiddim, post_enlarged),
                    make_activation(self.config, act_fn),
                    *make_dropout(self.config, post_enlarged),
                    *post_extra,
                    torch.nn.Linear(post_last, hiddim),
                    *make_dropout(self.config, hiddim),
                ]
                insert_hidden_gate(post_sa_layers, post_enlarged, self.config)
                insert_input_gate(post_sa_layers, hiddim, self.config)
                insert_output_gate(post_sa_layers, hiddim, self.config)
                link_concrete_dropouts(post_sa_layers)
            self.post_sa = torch.nn.Sequential(*post_sa_layers)
            self.ln = make_norm_layer(
                self.config, hiddim, "protein_output_graph_norm"
            )
            return

        if self.rnabang_residual_with_esm3:
            self.rnabang_residual_projection = torch.nn.Sequential(
                torch.nn.LayerNorm(self.config.rnabang_embedding_dim),
                torch.nn.Linear(self.config.rnabang_embedding_dim, hiddim),
            )
            self.rnabang_residual_alpha = torch.nn.Parameter(torch.zeros(1))

        if start:
            # residue_type, SASA, volume, plus the optional Voronota extras appended
            # after them by the loader (see protein_graph_builder.EXTRA_NODE_COLUMNS).
            indim = getattr(self.config, "protein_node_feature_count", 3)
            # The cavity descriptor conditions the protein encoding from the start:
            # broadcast to every residue and concatenated next to plm and buriedness,
            # so the GAT, the self-attention and -- the point -- the cross-attention
            # the lipid reads all see it. Injecting it at pooling instead would leave
            # the interaction itself blind to the shape of the cavity.
            #
            # Standardisation lives here rather than in the loader because the
            # statistics must come from train proteins only; the buffers are filled by
            # set_pocket_descriptor_normalization before the first epoch.
            # --pocket_descriptors_family_neutral restricts this broadcast to the 7
            # POCKET_DESCRIPTOR_NAMES entries at/near the no-structure eta^2 floor
            # (dataloader/protein_graph_builder.py); --pocket_descriptor_names restricts
            # it to an arbitrary named subset instead (mutually exclusive with
            # family_neutral, enforced in training/read_configuration.py's validate()).
            # Either way the incoming pocket_descriptor tensor stays the full 13-wide
            # vector (pocket_descriptor() and PairDescriptorHead's fixed indices are
            # untouched), sliced here at both normalisation and forward time.
            pocket_descriptor_names = getattr(self.config, "pocket_descriptor_names", "")
            if pocket_descriptor_names:
                self.pocket_descriptor_indices = tuple(
                    POCKET_DESCRIPTOR_NAMES.index(name)
                    for name in (
                        n.strip() for n in pocket_descriptor_names.split(",")
                    )
                    if name
                )
            elif getattr(self.config, "pocket_descriptors_family_neutral", False):
                self.pocket_descriptor_indices = POCKET_DESCRIPTOR_FAMILY_NEUTRAL_INDICES
            else:
                self.pocket_descriptor_indices = None
            self.pocket_descriptor_count = int(
                len(self.pocket_descriptor_indices)
                if self.pocket_descriptor_indices is not None
                else getattr(self.config, "pocket_descriptor_count", 0)
            )
            if self.pocket_descriptor_count:
                self.register_buffer(
                    "pocket_descriptor_mean", torch.zeros(self.pocket_descriptor_count)
                )
                self.register_buffer(
                    "pocket_descriptor_std", torch.ones(self.pocket_descriptor_count)
                )
                indim += self.pocket_descriptor_count
            # --descriptors_in_protein_lipid: aromatic_share/polar_share (already
            # bounded [0,1] shares, read raw like pair_descriptor_head.py does) plus
            # coarsened extent (already standardised in pair_descriptor_input by the
            # loader) when --pair_descriptor_extent is on -- see
            # expand_pair_descriptors below. No normalisation buffers needed here,
            # unlike pocket_descriptor_count above: nothing in this set is raw/
            # unstandardised.
            self.pair_descriptor_broadcast_count = int(
                getattr(self.config, "protein_pair_descriptor_broadcast_count", 0)
            )
            indim += self.pair_descriptor_broadcast_count
            # --protein_descriptors: broadcast an ARBITRARY named subset of the full
            # DESCRIPTOR_CATALOG (lipid, protein/pocket, or pair-level names -- unlike
            # pocket_descriptor_count above, not restricted to POCKET_DESCRIPTOR_NAMES)
            # onto every node, read out of the shared descriptor_catalog_input tensor by
            # column index -- same {name: position} lookup NamedDescriptorHead.__init__
            # uses (architecture/named_descriptor_head.py). Independent, coexisting
            # mechanism from pocket_descriptor_count/pair_descriptor_broadcast_count
            # above: neither is touched or restricted by this. No derived width field on
            # ModelConfig -- the count is only ever this many tokens, computed here from
            # the string itself.
            protein_descriptor_tokens = parse_descriptor_list(
                getattr(self.config, "protein_descriptors", "")
            )
            if protein_descriptor_tokens:
                catalog_order = full_catalog_order(self.config)
                catalog_index = {
                    name: position for position, name in enumerate(catalog_order)
                }
                self.register_buffer(
                    "protein_descriptor_columns",
                    torch.tensor(
                        [catalog_index[name] for name in protein_descriptor_tokens],
                        dtype=torch.long,
                    ),
                    persistent=False,
                )
                indim += len(protein_descriptor_tokens)
            else:
                self.protein_descriptor_columns = None
            plm_output_dim = self.config.plm_compression_dim
            plm_input_dim = 1536
            frozen_replacement = (
                self.config.frozen_protein_embedding()
                if hasattr(self.config, "frozen_protein_embedding") else None
            )
            if frozen_replacement is not None:
                # Replaces ESM3's contribution, including inside the RNA-BAnG
                # concatenation modes, which validate() allows to compose with it.
                plm_input_dim = frozen_replacement[1]
                if getattr(self.config, "rnabang_with_esm3", False):
                    plm_input_dim += self.config.rnabang_embedding_dim
            elif getattr(self.config, "rnabang_replace_esm3", False):
                plm_input_dim = self.config.rnabang_embedding_dim
            elif getattr(self.config, "rnabang_with_esm3", False):
                plm_input_dim += self.config.rnabang_embedding_dim
            plm_dims = (
                list(getattr(self.config, "plm_compression_dims", None) or [512, 171, 57])
                if self.config.plm_sequential_compression
                else None
            )
            self.enc_plm = build_sequential_compression(
                plm_input_dim, plm_output_dim, self.config, act_fn, plm_dims
            )
            indim += plm_output_dim if self.config.plmon else 0
            indim += 1 if self.config.buryon else 0
        else:
            indim = hiddim

        if self.use_geometric_transformer:
            # area sum and solvent-boundary/contact-area ratio are appended below.
            self.geometric_input = torch.nn.Linear(indim + 2, hiddim)
            self.geometric_block = ProteinGeometricTransformerBlock(
                hiddim, self.config.HEADS, config=self.config, act_fn=act_fn
            )
            return

        gat_out = hiddim * self.config.HEADS
        conv_out_dim = (
            hiddim if (self.use_gine_conv or self.rnabang_no_gat or self.use_edge_mlp)
            else gat_out
        )

        # Old protein graph encoder:
        # self.encodin = torch_geometric.nn.conv.GATv2Conv(
        #     indim, hiddim, heads=4, edge_dim=3, add_self_loops=True)
        if self.rnabang_no_gat:
            # RNA-BAnG embeddings already passed ten pretrained geometric-transformer
            # blocks offline. Preserve the complementary project residue features
            # (residue_type, SASA, volume), buriedness and coarse edge attributes
            # without applying another graph-attention layer.
            self.rnabang_node_projection = torch.nn.Linear(indim, hiddim)
            self.rnabang_edge_projection = torch.nn.Linear(3, hiddim)
            self.encodin1 = None
            self.encodin2 = None
        else:
            conv = self._make_protein_conv
            self.encodin1 = conv(indim, hiddim)
            # Only built when it will actually run: single_gat_layer skips the second
            # conv entirely, and an allocated-but-unreachable module would still count
            # toward the parameter total that names run directories.
            self.encodin2 = (
                None if self.config.single_gat_layer
                else conv(conv_out_dim, hiddim)
            )
        # Per-head gates for GATv2/Transformer conv (concat output hiddim*HEADS);
        # GINE has no head concat, so head gating does not apply there.
        self.head_gate1 = None
        self.head_gate2 = None
        if (
            getattr(self.config, "structured_sparsity", False)
            and getattr(self.config, "sparsity_gate_heads", False)
            and not self.use_gine_conv
            and not self.rnabang_no_gat
            and not self.use_edge_mlp
        ):
            self.head_gate1 = HeadGate(self.config.HEADS, hiddim, self.config)
            if not self.config.single_gat_layer:
                self.head_gate2 = HeadGate(self.config.HEADS, hiddim, self.config)
        if self.config.protein_gine_residual:
            self.gine_residual1 = make_optional_projection(indim, hiddim)
            self.gine_residual2 = torch.nn.Identity()
            self.gine_residual_gate1 = torch.nn.Parameter(torch.zeros(1))
            self.gine_residual_gate2 = torch.nn.Parameter(torch.zeros(1))
        if self.config.protein_gat_residual:
            self.gat_residual1 = make_optional_projection(indim, conv_out_dim)
            self.gat_residual_gate = torch.nn.Parameter(torch.zeros(1))
        self.gat_ln = make_norm_layer(self.config, conv_out_dim, "protein_gat_graph_norm")

        if self.config.protein_self_attention:
            self.attention = ProteinSelfAttention(hiddim, self.config)

        enlarged, last = mlp_hidden_dims(self.config, "protein_mlp", hiddim * self.config.m)
        extra = make_extra_hidden_layer(enlarged, last, self.config, act_fn)
        post_enlarged, post_last = mlp_hidden_dims(
            self.config, "protein_post_sa", hiddim * self.config.m
        )
        post_extra = make_extra_hidden_layer(
            post_enlarged, post_last, self.config, act_fn
        )

        mlp_layers = [
            torch.nn.Linear(conv_out_dim, enlarged),
            make_activation(self.config, act_fn),
            *make_dropout(self.config, enlarged),
        ]
        insert_hidden_gate(mlp_layers, enlarged, self.config)
        mlp_layers += [
            *extra,
            torch.nn.Linear(last, hiddim),
            make_activation(self.config, act_fn),
            *make_dropout(self.config, hiddim),
        ]
        insert_input_gate(mlp_layers, conv_out_dim, self.config)
        insert_output_gate(mlp_layers, hiddim, self.config)
        link_concrete_dropouts(mlp_layers)
        self.mlp = torch.nn.Sequential(*mlp_layers)

        post_sa_layers = []
        if not getattr(self.config, "protein_disable_post_sa_mlp", False):
            post_sa_layers = [
                torch.nn.Linear(hiddim, post_enlarged),
                make_activation(self.config, act_fn),
                *make_dropout(self.config, post_enlarged),
            ]
            insert_hidden_gate(post_sa_layers, post_enlarged, self.config)
            post_sa_layers += [
                *post_extra,
                torch.nn.Linear(post_last, hiddim),
                *make_dropout(self.config, hiddim),
            ]
            insert_input_gate(post_sa_layers, hiddim, self.config)
            insert_output_gate(post_sa_layers, hiddim, self.config)
            link_concrete_dropouts(post_sa_layers)
        self.post_sa = torch.nn.Sequential(*post_sa_layers)
        self.ln = make_norm_layer(self.config, hiddim, "protein_output_graph_norm")

    def _make_protein_conv(self, indim, hiddim):
        if self.use_edge_attention:
            return EdgeAttentionConv(
                indim, hiddim, self.config.HEADS, STRUCTURED_EDGE_DIM
            )
        if self.use_edge_mlp:
            return EdgeMLPConv(
                indim, hiddim, STRUCTURED_EDGE_DIM,
                lam=getattr(self.config, "protein_edge_mlp_lambda", 30.0),
            )
        if self.use_gine_conv:
            nn = torch.nn.Sequential(
                torch.nn.Linear(indim, hiddim),
                self.config.make_activation(),
                torch.nn.Linear(hiddim, hiddim),
            )
            return torch_geometric.nn.conv.GINEConv(nn, edge_dim=3)

        if self.config.transformer_conv:
            return torch_geometric.nn.conv.TransformerConv(
                indim,
                hiddim,
                heads=self.config.HEADS,
                edge_dim=3,
            )

        return torch_geometric.nn.conv.GATv2Conv(
            indim,
            hiddim,
            heads=self.config.HEADS,
            edge_dim=3,
            add_self_loops=True,
        )

    def make_bidirectional_edges(self, edgidx, e_attr):
        """Append reverse protein contact edges for symmetric message passing."""
        bidirectional_edgidx = torch.cat((edgidx, edgidx.flip(0)), dim=1)
        bidirectional_e_attr = torch.cat((e_attr, e_attr), dim=0)
        return bidirectional_edgidx, bidirectional_e_attr

    def apply_gine_conv(self, conv, residual, gate, node, edgidx, e_attr):
        """Apply optional gated pre-convolution residual around one GINE layer."""
        conv_out = conv(node, edgidx, e_attr)
        if not self.config.protein_gine_residual:
            return conv_out
        return conv_out + gate * residual(node)

    def apply_rnabang_edge_residual(self, node, edgidx, e_attr):
        """Encode project node and edge features without another graph attention."""
        out = self.rnabang_node_projection(node)
        edge_messages = self.rnabang_edge_projection(e_attr)
        aggregate = torch.zeros_like(out)
        degree = torch.zeros(
            out.shape[0], dtype=out.dtype, device=out.device
        )
        source, target = edgidx
        aggregate.index_add_(0, source, edge_messages)
        aggregate.index_add_(0, target, edge_messages)
        ones = torch.ones(
            edge_messages.shape[0], dtype=out.dtype, device=out.device
        )
        degree.index_add_(0, source, ones)
        degree.index_add_(0, target, ones)
        return out + aggregate / degree.clamp_min(1).unsqueeze(-1)

    def set_pocket_descriptor_normalization(self, stats):
        """Install fixed descriptor statistics computed from train proteins only."""
        if not getattr(self, "pocket_descriptor_count", 0) or stats is None:
            return
        indices = getattr(self, "pocket_descriptor_indices", None)
        for name in ("pocket_descriptor_mean", "pocket_descriptor_std"):
            target = getattr(self, name)
            value = stats[name].to(device=target.device, dtype=target.dtype)
            if indices is not None:
                value = value[list(indices)]
            if value.shape != target.shape:
                raise ValueError(
                    f"{name} shape {tuple(value.shape)} != {tuple(target.shape)}"
                )
            target.copy_(value)

    def expand_pocket_descriptor(self, node, batch, pocket_descriptor):
        """Standardise the per-protein descriptor and broadcast it over that protein's nodes."""
        if not getattr(self, "pocket_descriptor_count", 0):
            return node
        if pocket_descriptor is None:
            raise ValueError("pocket_descriptors requires pocket_descriptor")
        indices = getattr(self, "pocket_descriptor_indices", None)
        if indices is not None:
            pocket_descriptor = pocket_descriptor[:, list(indices)]
        scaled = (
            pocket_descriptor.to(node.dtype) - self.pocket_descriptor_mean
        ) / self.pocket_descriptor_std
        return torch.cat((node, scaled[batch]), dim=-1)

    def expand_pair_descriptors(self, node, batch, pocket_descriptor, pair_descriptor_input):
        """--descriptors_in_protein_lipid: broadcast pair_descriptors' protein-only
        tokens (aromatic_share, polar_share, coarsened extent) over every node.

        Deliberately not a reuse of expand_pocket_descriptor: that broadcasts the full
        13-wide POCKET_DESCRIPTOR_NAMES vector, this only the 2-3 tokens
        architecture/pair_descriptor_head.py's self-attention head itself reads --
        the two are independent, coexisting mechanisms (see ModelConfig's
        descriptors_in_protein_lipid docstring). aromatic_share/polar_share are read
        raw (already-bounded [0,1] shares, no standardisation needed, same as
        pair_descriptor_head.py); extent is pair_descriptor_input's last column,
        already standardised by the loader -- no local buffers needed either.
        """
        if not getattr(self, "pair_descriptor_broadcast_count", 0):
            return node
        if pocket_descriptor is None or pair_descriptor_input is None:
            raise ValueError(
                "descriptors_in_protein_lipid requires pocket_descriptor and "
                "pair_descriptor_input"
            )
        aromatic_share = pocket_descriptor[:, _AROMATIC_SHARE_INDEX]
        polar_share = 1.0 - pocket_descriptor[:, _APOLAR_SASA_SHARE_INDEX]
        parts = [aromatic_share.unsqueeze(-1), polar_share.unsqueeze(-1)]
        if self.pair_descriptor_broadcast_count > 2:
            parts.append(pair_descriptor_input[:, -1:].to(node.dtype))
        per_protein = torch.cat(parts, dim=-1).to(node.dtype)
        return torch.cat((node, per_protein[batch]), dim=-1)

    def expand_named_protein_descriptors(self, node, batch, descriptor_catalog_input):
        """--protein_descriptors: broadcast an arbitrary named DESCRIPTOR_CATALOG subset
        (dataloader/pair_descriptors.py) over every node, selected out of the shared
        descriptor_catalog_input tensor by column index -- same shape as
        expand_pair_descriptors above, but reading named columns instead of a fixed pair
        of pocket_descriptor indices. Values are already standardised (train-only) by
        the loader when it materialises descriptor_catalog_input, same as
        pair_descriptor_input's tokens -- no local buffers needed here either.
        """
        columns = getattr(self, "protein_descriptor_columns", None)
        if columns is None:
            return node
        if descriptor_catalog_input is None:
            raise ValueError("protein_descriptors requires descriptor_catalog_input")
        selected = descriptor_catalog_input.index_select(1, columns).to(node.dtype)
        return torch.cat((node, selected[batch]), dim=-1)

    def set_rnabang_normalization(self, stats):
        """Install fixed feature statistics computed from train proteins only."""
        if not self.use_rnabang_frozen_node_adapter:
            return
        for name in (
            "structural_mean", "structural_std",
            "edge_feature_mean", "edge_feature_std",
            "edge_pair_mean", "edge_pair_std",
        ):
            target = getattr(self, name)
            value = stats[name].to(device=target.device, dtype=target.dtype)
            if value.shape != target.shape:
                raise ValueError(
                    f"{name} shape {tuple(value.shape)} != {tuple(target.shape)}"
                )
            target.copy_(value)

    def forward(
        self, config, node, edgidx, plm, e_attr, batch, bury, attn_mask,
        pocket_mask, start=True, fast_layout=None, frame_rotation=None,
        frame_translation=None, geometric_node_attr=None, edge_node_pairs=None,
        edge_node_degree=None, pocket_layout=None, pocket_index=None,
        pocket_descriptor=None, pair_descriptor_input=None, descriptor_catalog_input=None
    ):
        """Encode protein nodes while preserving graph-node alignment."""
        if self.use_rnabang_frozen_node_adapter:
            if geometric_node_attr is None:
                raise ValueError(
                    "rnabang_frozen_node_adapter requires precomputed node features"
                )
            expected_dim = self.config.rnabang_embedding_dim
            if plm.shape[-1] != expected_dim:
                raise ValueError(
                    "rnabang_frozen_node_adapter expected RNA-BAnG width "
                    f"{expected_dim}, got {plm.shape[-1]}"
                )
            sasa = torch.log1p(node[:, 1].clamp_min(0))
            volume = node[:, 2]
            bury_missing = bury == 2
            bury_value = torch.where(
                bury_missing,
                self.structural_mean[2].to(bury.dtype),
                bury,
            )
            structural = torch.stack((sasa, volume, bury_value), dim=-1)
            structural = (
                structural - self.structural_mean.to(structural.dtype)
            ) / self.structural_std.to(structural.dtype)
            if self.use_residue_type_embedding:
                residue_type = node[:, 0].long()
                if torch.any((residue_type < 0) | (residue_type >= 20)):
                    raise ValueError("residue_type must be in [0, 19]")
                residue_features = self.residue_type_embedding(residue_type)
            else:
                residue_features = node[:, :1]
            edge_features = geometric_node_attr.to(node.dtype)
            if self.edge_node_encoder is not None:
                if edge_node_pairs is None or edge_node_degree is None:
                    raise ValueError(
                        "learned edge-to-node mode requires padded incident edges"
                    )
                pairs = (
                    edge_node_pairs.to(node.dtype)
                    - self.edge_pair_mean.to(node.dtype)
                ) / self.edge_pair_std.to(node.dtype)
                pair_mask = (
                    torch.arange(pairs.shape[1], device=pairs.device).unsqueeze(0)
                    < edge_node_degree.unsqueeze(1)
                )
                pairs = pairs * pair_mask.unsqueeze(-1)
                edge_features = self.edge_node_encoder(pairs, edge_node_degree)
            else:
                edge_features = (
                    edge_features - self.edge_feature_mean.to(node.dtype)
                ) / self.edge_feature_std.to(node.dtype)
                if getattr(self.config, "rnabang_edge_topk_by_area", False):
                    if edge_node_degree is None:
                        raise ValueError("top-k edge mode requires edge degree")
                    ranks = torch.arange(
                        21, device=edge_features.device
                    ).unsqueeze(0)
                    valid = ranks < edge_node_degree.unsqueeze(1)
                    edge_features[:, :42] *= (
                        valid.unsqueeze(-1).expand(-1, -1, 2).reshape(-1, 42)
                    )
            return self.rnabang_node_adapter(
                torch.cat(
                    (
                        self.rnabang_norm(plm),
                        residue_features,
                        structural,
                        edge_features,
                    ),
                    dim=-1,
                )
            )

        if self.rnabang_full_encoder:
            out = self.rnabang_projection(plm)
            if self.config.protein_self_attention:
                out = self.attention(
                    out, attn_mask, pocket_mask, batch=batch,
                    fast_layout=fast_layout,
                    pocket_layout=pocket_layout, pocket_index=pocket_index,
                )
            out = self.post_sa(out)
            return apply_norm(
                self.ln, out, batch, self.config.protein_output_graph_norm
            )

        if start:
            rnabang_residual = None
            if self.config.plmon:
                if self.rnabang_residual_with_esm3:
                    # The leading block is ESM3 unless a frozen replacement took its
                    # slot in the concatenation, in which case it is that instead.
                    replacement = (
                        self.config.frozen_protein_embedding()
                        if hasattr(self.config, "frozen_protein_embedding") else None
                    )
                    leading_dim = 1536 if replacement is None else replacement[1]
                    expected_dim = leading_dim + self.config.rnabang_embedding_dim
                    if plm.shape[-1] != expected_dim:
                        raise ValueError(
                            "rnabang_residual_with_esm3 expected PLM width "
                            f"{expected_dim}, got {plm.shape[-1]}"
                        )
                    plm, rnabang_residual = torch.split(
                        plm,
                        [leading_dim, self.config.rnabang_embedding_dim],
                        dim=-1,
                    )
                # Old PLM projection:
                # plm = self.enc_plm(plm, edgidx)
                plm = self.enc_plm(plm)
                node = torch.cat((node, plm), -1)
            if self.config.buryon:
                node = torch.cat((node, bury.unsqueeze(1)), -1)
            node = self.expand_pocket_descriptor(node, batch, pocket_descriptor)
            node = self.expand_pair_descriptors(
                node, batch, pocket_descriptor, pair_descriptor_input
            )
            node = self.expand_named_protein_descriptors(
                node, batch, descriptor_catalog_input
            )

        if self.use_geometric_transformer:
            if frame_rotation is None or frame_translation is None:
                raise ValueError(
                    "geometric_transformer requires protein residue frames"
                )
            if geometric_node_attr is None:
                raise ValueError(
                    "geometric_transformer requires precomputed node edge features"
                )
            node = torch.cat((node, geometric_node_attr.to(node.dtype)), dim=-1)
            return self.geometric_block(
                self.geometric_input(node),
                frame_rotation,
                frame_translation,
                batch,
                fast_layout,
                getattr(self.config, "geometric_ipa_chunk_size", 64),
            )

        if self.use_structured_edges:
            if frame_rotation is None or frame_translation is None:
                raise ValueError(
                    "protein_edge_attention/protein_edge_mlp require protein "
                    "residue frames"
                )
            edgidx, e_attr = structured_edge_features(
                edgidx, frame_rotation, frame_translation, e_attr
            )
        elif self.config.bidirectional_edges:
            edgidx, e_attr = self.make_bidirectional_edges(edgidx, e_attr)

        # Old protein graph encoder:
        # inn = self.encodin(node, edgidx, e_attr)
        if self.rnabang_no_gat:
            inn = self.apply_rnabang_edge_residual(node, edgidx, e_attr)
        elif self.use_gine_conv and self.config.protein_gine_residual:
            inn = self.apply_gine_conv(
                self.encodin1,
                self.gine_residual1,
                self.gine_residual_gate1,
                node,
                edgidx,
                e_attr,
            )
        else:
            inn = self.encodin1(node, edgidx, e_attr)
            if self.head_gate1 is not None:
                inn = self.head_gate1(inn)
            if self.config.protein_gat_residual:
                inn = inn + self.gat_residual_gate * self.gat_residual1(node)
        if self.rnabang_no_gat:
            inn = apply_norm(
                self.gat_ln, inn, batch, self.config.protein_gat_graph_norm
            )
        elif self.config.single_gat_layer:
            inn = apply_norm(self.gat_ln, inn, batch, self.config.protein_gat_graph_norm)
        else:
            if self.use_gine_conv and self.config.protein_gine_residual:
                inn = self.apply_gine_conv(
                    self.encodin2,
                    self.gine_residual2,
                    self.gine_residual_gate2,
                    inn,
                    edgidx,
                    e_attr,
                )
            else:
                enc2 = self.encodin2(inn, edgidx, e_attr)
                if self.head_gate2 is not None:
                    enc2 = self.head_gate2(enc2)
                inn = inn + enc2
            inn = apply_norm(self.gat_ln, inn, batch, self.config.protein_gat_graph_norm)

        if self.config.protein_self_attention:
            attention_input = (
                inn
                if self.config.protein_disable_pre_sa_mlp
                else self.mlp(inn)
            )
            out = self.post_sa(
                self.attention(
                    attention_input, attn_mask, pocket_mask, batch=batch,
                    fast_layout=fast_layout,
                    pocket_layout=pocket_layout, pocket_index=pocket_index,
                )
            )
        else:
            out = self.post_sa(self.mlp(inn))

        if self.rnabang_residual_with_esm3:
            out = out + self.rnabang_residual_alpha * self.rnabang_residual_projection(
                rnabang_residual
            )
        out = apply_norm(self.ln, out, batch, self.config.protein_output_graph_norm)
        return out
