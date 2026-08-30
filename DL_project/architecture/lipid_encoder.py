import torch
import torch_geometric

from .self_attention import SelfAttention
from .edge_geometric_conv import EdgeAttentionConv, EdgeMLPConv
from .mlp_utils import (
    make_activation, make_dropout, make_extra_hidden_layer,
    make_norm_layer, apply_norm, HeadGate, insert_hidden_gate,
    insert_input_gate, insert_output_gate, mlp_hidden_dims,
    link_concrete_dropouts
)

LIPID_ISOMER_EDGE_DIM = 22


class Lipid_encoder(torch.nn.Module):
    def __init__(self, config, act_fn=None, start=True):
        """Initialize an embedding or chemical-graph lipid encoder block."""
        super(Lipid_encoder, self).__init__()
        self.config = config
        hiddim = self.config.hiddim
        enlarged, last = mlp_hidden_dims(self.config, "lipid_mlp", hiddim * config.m)
        extra = make_extra_hidden_layer(enlarged, last, self.config, act_fn)
        post_enlarged, post_last = mlp_hidden_dims(
            self.config, "lipid_post_sa", hiddim * config.m
        )
        post_extra = make_extra_hidden_layer(
            post_enlarged, post_last, self.config, act_fn
        )

        # Per-head gates for the lipid GATv2 layers (only on the graph path).
        self.head_gate1 = None
        self.head_gate2 = None
        gate_heads = (
            getattr(config, "structured_sparsity", False)
            and getattr(config, "sparsity_gate_heads", False)
        )

        if getattr(config, "lipid_graph_isomers", False):
            indim = 11 if start else hiddim
            # Same conv choice as architecture/protein_encoder.py's _make_protein_conv
            # -- protein_edge_attention/protein_edge_mlp swap GATv2Conv here too, one
            # switch for both graphs rather than a separate lipid-only flag.
            self.use_edge_mlp = bool(getattr(config, "protein_edge_mlp", False))
            use_edge_attention = bool(getattr(config, "protein_edge_attention", False))
            conv_out_dim = hiddim if self.use_edge_mlp else hiddim * config.HEADS
            gat_out = conv_out_dim
            if use_edge_attention:
                self.encodin1 = EdgeAttentionConv(
                    indim, hiddim, config.HEADS, LIPID_ISOMER_EDGE_DIM
                )
                self.encodin2 = EdgeAttentionConv(
                    gat_out, hiddim, config.HEADS, LIPID_ISOMER_EDGE_DIM
                )
            elif self.use_edge_mlp:
                self.encodin1 = EdgeMLPConv(
                    indim, hiddim, LIPID_ISOMER_EDGE_DIM,
                    lam=getattr(config, "protein_edge_mlp_lambda", 30.0),
                )
                self.encodin2 = EdgeMLPConv(
                    gat_out, hiddim, LIPID_ISOMER_EDGE_DIM,
                    lam=getattr(config, "protein_edge_mlp_lambda", 30.0),
                )
            else:
                self.encodin1 = torch_geometric.nn.conv.GATv2Conv(
                    indim, hiddim, heads=config.HEADS,
                    edge_dim=LIPID_ISOMER_EDGE_DIM, add_self_loops=True,
                )
                self.encodin2 = torch_geometric.nn.conv.GATv2Conv(
                    gat_out, hiddim, heads=config.HEADS,
                    edge_dim=LIPID_ISOMER_EDGE_DIM, add_self_loops=True,
                )
            if gate_heads and not self.use_edge_mlp:
                self.head_gate1 = HeadGate(config.HEADS, hiddim, config)
                self.head_gate2 = HeadGate(config.HEADS, hiddim, config)
            self.gat_ln = make_norm_layer(self.config, gat_out, "lipid_gat_graph_norm")

            mlp_layers = [
                torch.nn.Linear(gat_out, enlarged),
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
            insert_input_gate(mlp_layers, gat_out, self.config)
            insert_output_gate(mlp_layers, hiddim, self.config)
            link_concrete_dropouts(mlp_layers)
            self.mlp = torch.nn.Sequential(*mlp_layers)
        else:
            # --descriptors_in_lipid's tokens (also settable together with the
            # protein-side broadcast via --descriptors_in_protein_lipid: chain,
            # unsaturation, hbond, heavy -- pair_descriptor_input's first 4 columns,
            # already standardised by the loader; see architecture/protein_encoder.py's
            # expand_pair_descriptors for the protein-side equivalent and why no
            # normalisation buffers are needed here either).
            #
            # --no_embeddings: MolFormer contributes nothing at all -- there is no
            # per-token structure to build multiple nodes from without it (validate()
            # requires descriptors_in_lipid for exactly this reason), so
            # dataloader.Dataloader collapses the lipid graph to ONE node whose
            # feature vector already IS these 4 scalars; encodin reads them directly,
            # no broadcast-cat needed in forward (there is nothing else to cat onto).
            #
            # Otherwise (no_embeddings off): MolFormer's per-token embedding stays the
            # base, and forward() broadcasts the same 4 scalars onto every token node
            # in addition to it -- concatenated, not replacing, same as
            # descriptors_in_lipid coexists with --pair_descriptors elsewhere.
            # Only for the start=True instance (lipid1): the start=False second pass
            # (lipid2, under --double_attention) receives lip1 -- already hiddim-wide,
            # nothing raw left to broadcast onto, same reason
            # architecture/protein_encoder.py's equivalent sits inside `if start:`.
            # Left at 0 here, forward() below reads it off self and skips the cat.
            self.lipid_pair_descriptor_broadcast_count = 0
            no_embeddings = getattr(config, "no_embeddings", False)
            if start:
                self.lipid_pair_descriptor_broadcast_count = int(
                    getattr(config, "lipid_pair_descriptor_broadcast_count", 0)
                )
                base_dim = 0 if no_embeddings else 768
                self.encodin = torch.nn.Linear(
                    base_dim + self.lipid_pair_descriptor_broadcast_count, hiddim
                )
            else:
                self.encodin = torch.nn.Linear(hiddim, hiddim)
        post_sa_layers = []
        if not getattr(self.config, "lipid_disable_post_sa_mlp", False):
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
        self.act_fn = act_fn
        if self.config.lipid_self_attention:
            self.attention = SelfAttention(hiddim, self.config)
        self.ln = make_norm_layer(self.config, hiddim, "lipid_output_graph_norm")

    def forward(
        self, lipLM, lipbatch, attn_mask, mult_mask=None, edge_index=None,
        edge_attr=None, start=True, fast_layout=None, pair_descriptor_input=None
    ):
        """Encode lipid nodes using the configured embedding or graph path."""
        if self.config.lipid_fragments_mask:
            assert mult_mask is not None

        if (
            not getattr(self.config, "lipid_graph_isomers", False)
            and getattr(self, "lipid_pair_descriptor_broadcast_count", 0)
            and not getattr(self.config, "no_embeddings", False)
        ):
            # MolFormer's per-token embedding is still the base here (no_embeddings
            # off) -- broadcast the 4 lipid-only tokens onto every one of its nodes.
            # Under no_embeddings, lipLM already IS these 4 scalars (one node, built
            # by the loader), nothing to broadcast onto.
            if pair_descriptor_input is None:
                raise ValueError("descriptors_in_lipid requires pair_descriptor_input")
            per_lipid = pair_descriptor_input[:, :4].to(lipLM.dtype)
            lipLM = torch.cat((lipLM, per_lipid[lipbatch]), dim=-1)

        if getattr(self.config, "lipid_graph_isomers", False):
            assert edge_index is not None
            assert edge_attr is not None
            inn = self.encodin1(lipLM, edge_index, edge_attr)
            if self.head_gate1 is not None:
                inn = self.head_gate1(inn)
            enc2 = self.encodin2(inn, edge_index, edge_attr)
            if self.head_gate2 is not None:
                enc2 = self.head_gate2(enc2)
            inn = inn + enc2
            inn = apply_norm(self.gat_ln, inn, lipbatch, self.config.lipid_gat_graph_norm)
            if self.config.lipid_self_attention:
                out = self.post_sa(
                    self.attention(
                        self.mlp(inn), attn_mask, mult_mask, batch=lipbatch,
                        fast_layout=fast_layout,
                    )
                )
            else:
                out = self.post_sa(self.mlp(inn))
            out = apply_norm(self.ln, out, lipbatch, self.config.lipid_output_graph_norm)
            return out

        if self.config.lipid_self_attention:
            if self.config.lipid_fragments_mask:
                assert mult_mask is not None
                out = self.post_sa(
                    self.attention(
                        self.encodin(lipLM), attn_mask, mult_mask, batch=lipbatch,
                        fast_layout=fast_layout,
                    )
                )
            else:
                out = self.post_sa(
                    self.attention(
                        self.encodin(lipLM), attn_mask, batch=lipbatch,
                        fast_layout=fast_layout,
                    )
                )
        else:
            out = self.post_sa(self.encodin(lipLM))

        out = apply_norm(self.ln, out, lipbatch, self.config.lipid_output_graph_norm)
        return out
