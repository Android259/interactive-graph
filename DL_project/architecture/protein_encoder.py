import torch
import torch_geometric

from dataloader.descriptors import full_catalog_order, parse_descriptor_list

from .geometric_transformer import ProteinGeometricTransformerBlock
from .edge_geometric_conv import EdgeAttentionConv, EdgeMLPConv
from .protein_edge_geometry import structured_edge_dim, structured_edge_features
from .self_attention import ProteinSelfAttention
from .mlp_utils import (
    make_activation, make_dropout, make_extra_hidden_layer,
    make_optional_projection, make_norm_layer, apply_norm,
    build_sequential_compression, HeadGate, insert_hidden_gate,
    insert_input_gate, insert_output_gate, mlp_hidden_dims,
    link_concrete_dropouts, branch_width
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
        # --protein_hiddim, defaulting to --hiddim. Bound once here; every use below is
        # this local, so the whole tower -- convs, self-attention, MLPs, norms -- moves
        # with it. The hand-off to cross-attention does NOT: see branch_width's
        # docstring and the adapter in architecture/interaction_classification.py.
        hiddim = branch_width(self.config, "protein")
        self.rnabang_full_encoder = bool(
            start and getattr(self.config, "rnabang_full_protein_encoder", False)
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
        # --protein_edge_raw3: use the plain [distance, area, boundary] edge_attr
        # (edge_dim=3) as input to EdgeAttentionConv/EdgeMLPConv instead of the
        # SE(3)-invariant structured vector -- isolates the Ingraham/Dauparas
        # message-passing mechanism from the RBF/direction/orientation expansion.
        self.use_edge_raw3 = bool(getattr(self.config, "protein_edge_raw3", False))
        self.structured_edge_dim = structured_edge_dim(
            rbf_count=getattr(self.config, "protein_edge_rbf_count", None) or 16,
            use_orientation_scalar=bool(
                getattr(self.config, "protein_edge_orientation_scalar", False)
            ),
        )
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

        if start:
            # residue_type, SASA, volume, plus the optional Voronota extras appended
            # after them by the loader (see protein_graph_builder.EXTRA_NODE_COLUMNS).
            indim = getattr(self.config, "protein_node_feature_count", 3)
            # --protein_descriptors: broadcast an ARBITRARY named subset of the full
            # DESCRIPTOR_CATALOG (lipid, protein/pocket, or pair-level names) onto
            # every node, read out of the shared descriptor_catalog_input tensor by
            # column index -- same {name: position} lookup NamedDescriptorHead.__init__
            # uses (architecture/named_descriptor_head.py). No derived width field on
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
                plm_input_dim = frozen_replacement[1]
            elif getattr(self.config, "rnabang_replace_esm3", False):
                plm_input_dim = self.config.rnabang_embedding_dim
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
            hiddim if (self.use_gine_conv or self.use_edge_mlp)
            else gat_out
        )

        # Old protein graph encoder:
        # self.encodin = torch_geometric.nn.conv.GATv2Conv(
        #     indim, hiddim, heads=4, edge_dim=3, add_self_loops=True)
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
        edge_dim = 3 if self.use_edge_raw3 else self.structured_edge_dim
        if self.use_edge_attention:
            return EdgeAttentionConv(
                indim, hiddim, self.config.HEADS, edge_dim
            )
        if self.use_edge_mlp:
            return EdgeMLPConv(
                indim, hiddim, edge_dim,
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


    def expand_named_protein_descriptors(self, node, batch, descriptor_catalog_input):
        """--protein_descriptors: broadcast an arbitrary named DESCRIPTOR_CATALOG subset
        (dataloader/descriptors.py) over every node, selected out of the shared
        descriptor_catalog_input tensor by column index. Values are already
        standardised (train-only) by the loader when it materialises
        descriptor_catalog_input -- no local buffers needed here.
        """
        columns = getattr(self, "protein_descriptor_columns", None)
        if columns is None:
            return node
        if descriptor_catalog_input is None:
            raise ValueError("protein_descriptors requires descriptor_catalog_input")
        selected = descriptor_catalog_input.index_select(1, columns).to(node.dtype)
        return torch.cat((node, selected[batch]), dim=-1)


    def forward(
        self, config, node, edgidx, plm, e_attr, batch, bury, attn_mask,
        pocket_mask, start=True, fast_layout=None, frame_rotation=None,
        frame_translation=None, geometric_node_attr=None,
        pocket_layout=None, pocket_index=None,
        descriptor_catalog_input=None
    ):
        """Encode protein nodes while preserving graph-node alignment."""
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
            if self.config.plmon:
                # Old PLM projection:
                # plm = self.enc_plm(plm, edgidx)
                plm = self.enc_plm(plm)
                node = torch.cat((node, plm), -1)
            if self.config.buryon:
                node = torch.cat((node, bury.unsqueeze(1)), -1)
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

        if self.use_structured_edges and self.use_edge_raw3:
            edgidx, e_attr = self.make_bidirectional_edges(edgidx, e_attr)
        elif self.use_structured_edges:
            if frame_rotation is None or frame_translation is None:
                raise ValueError(
                    "protein_edge_attention/protein_edge_mlp require protein "
                    "residue frames"
                )
            edgidx, e_attr = structured_edge_features(
                edgidx,
                frame_rotation,
                frame_translation,
                e_attr,
                rbf_count=getattr(self.config, "protein_edge_rbf_count", None) or 16,
                use_orientation_scalar=bool(
                    getattr(self.config, "protein_edge_orientation_scalar", False)
                ),
            )
        elif self.config.bidirectional_edges:
            edgidx, e_attr = self.make_bidirectional_edges(edgidx, e_attr)

        # Old protein graph encoder:
        # inn = self.encodin(node, edgidx, e_attr)
        if self.use_gine_conv and self.config.protein_gine_residual:
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
        if self.config.single_gat_layer:
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

        out = apply_norm(self.ln, out, batch, self.config.protein_output_graph_norm)
        return out
