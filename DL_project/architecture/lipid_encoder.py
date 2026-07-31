import torch
import torch_geometric

try:
    from .self_attention import SelfAttention
    from .mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer,
        make_norm_layer, apply_norm, HeadGate, insert_hidden_gate,
        insert_input_gate, insert_output_gate, mlp_hidden_dims,
        link_concrete_dropouts
    )
except ImportError:
    from self_attention import SelfAttention
    from mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer,
        make_norm_layer, apply_norm, HeadGate, insert_hidden_gate,
        insert_input_gate, insert_output_gate, mlp_hidden_dims,
        link_concrete_dropouts
    )


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
            gat_out = hiddim * config.HEADS
            self.encodin1 = torch_geometric.nn.conv.GATv2Conv(
                indim, hiddim, heads=config.HEADS, edge_dim=6, add_self_loops=True)
            self.encodin2 = torch_geometric.nn.conv.GATv2Conv(
                gat_out, hiddim, heads=config.HEADS, edge_dim=6, add_self_loops=True)
            if gate_heads:
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
            if start:
                self.encodin = torch.nn.Linear(768, hiddim)
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
        edge_attr=None, start=True, fast_layout=None
    ):
        """Encode lipid nodes using the configured embedding or graph path."""
        if self.config.lipid_fragments_mask:
            assert mult_mask is not None


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
