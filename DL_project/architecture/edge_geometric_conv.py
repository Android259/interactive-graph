"""Literal Ingraham/Dauparas edge-conditioned graph layers.

Both classes take the same `(x, edge_index, edge_attr) -> x` shape as any PyG conv
layer, and both are graph-generic -- nothing here is protein- or lipid-specific, so
`architecture/protein_encoder.py` and `architecture/lipid_encoder.py` share the same
two classes.

`edge_index[0]` is the reference node whose local frame `edge_attr` was computed
relative to (the node being updated); `edge_index[1]` is the neighbor contributing
keys/values. This is the opposite of PyG's usual source->target message-passing
convention, so it is spelled out with `reference`/`neighbor` names throughout rather
than `src`/`dst`, to avoid silently assuming the wrong direction.

Neither layer applies its own residual connection or normalization -- both are
applied uniformly by the caller for every conv choice already (GATv2Conv,
TransformerConv, GINEConv included), so adding a second one here would double up.
The one paper-specific piece of aggregation math each layer owns (softmax attention
for EdgeAttentionConv, sum-over-lambda for EdgeMLPConv) stays inside; everything
generic stays outside, matching how the existing conv choices are wrapped.

Neither adds self-loops. Ingraham's own kNN graph includes a residue as one of its
own neighbors (thesis Sec 3.3.3: "one of the nearest neighbors of a residue is
always the residue itself"); this project's graph is a Voronota contact
tessellation instead, which has no self-contacts, and the node's own state already
re-enters via the caller's residual step -- so this is a deliberate, minor
deviation from strict paper fidelity, not an oversight.
"""

import torch
import torch_geometric


class EdgeAttentionConv(torch.nn.Module):
    """Ingraham et al. 2019, Sec 3.3.2, literally:

        q_i = W_Q h_i
        k_ij = W_K [e_ij, h_j]      v_ij = W_V [e_ij, h_j]
        w_ij = softmax_j(q_i^T k_ij / sqrt(d))      h~_i = sum_j w_ij v_ij

    Multi-head (heads splits the per-head width out_dim, concatenated on output --
    same convention as GATv2Conv/TransformerConv: output width is heads * out_dim).
    Attention is only over j in N(i) -- the graph's real edges -- via a scatter
    softmax grouped by the reference node, not a dense all-pairs matrix.
    """

    def __init__(self, in_dim, out_dim, heads, edge_dim):
        super().__init__()
        self.heads = heads
        self.out_dim = out_dim
        self.q_proj = torch.nn.Linear(in_dim, heads * out_dim, bias=False)
        kv_in_dim = in_dim + edge_dim
        self.k_proj = torch.nn.Linear(kv_in_dim, heads * out_dim, bias=False)
        self.v_proj = torch.nn.Linear(kv_in_dim, heads * out_dim, bias=False)

    def forward(self, x, edge_index, edge_attr):
        reference, neighbor = edge_index[0], edge_index[1]
        num_nodes = x.shape[0]

        q = self.q_proj(x).view(num_nodes, self.heads, self.out_dim)
        kv_input = torch.cat((x[neighbor], edge_attr), dim=-1)
        k = self.k_proj(kv_input).view(-1, self.heads, self.out_dim)
        v = self.v_proj(kv_input).view(-1, self.heads, self.out_dim)

        scores = (q[reference] * k).sum(dim=-1) / (self.out_dim ** 0.5)
        weights = torch_geometric.utils.softmax(scores, index=reference, num_nodes=num_nodes)

        out = torch.zeros(
            num_nodes, self.heads, self.out_dim, dtype=v.dtype, device=v.device
        )
        out.index_add_(0, reference, weights.unsqueeze(-1) * v)
        return out.reshape(num_nodes, self.heads * self.out_dim)


class EdgeMLPConv(torch.nn.Module):
    """Dauparas/ProteinMPNN, Sec 3.4.2, literally:

        m_ij = MLP([h_i, e_ij, h_j])     (3 linear layers, GELU)
        aggregated_i = sum_j m_ij / lambda,   lambda = 30 by default (the paper's
        experimentally-found value)

    No attention at all -- plain sum aggregation over j in N(i).
    """

    def __init__(self, in_dim, out_dim, edge_dim, lam=30.0):
        super().__init__()
        self.lam = lam
        message_in_dim = 2 * in_dim + edge_dim
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(message_in_dim, out_dim),
            torch.nn.GELU(),
            torch.nn.Linear(out_dim, out_dim),
            torch.nn.GELU(),
            torch.nn.Linear(out_dim, out_dim),
        )

    def forward(self, x, edge_index, edge_attr):
        reference, neighbor = edge_index[0], edge_index[1]
        num_nodes = x.shape[0]

        messages = self.mlp(
            torch.cat((x[reference], edge_attr, x[neighbor]), dim=-1)
        )
        aggregated = torch.zeros(
            num_nodes, messages.shape[-1], dtype=messages.dtype, device=messages.device
        )
        aggregated.index_add_(0, reference, messages)
        return aggregated / self.lam
