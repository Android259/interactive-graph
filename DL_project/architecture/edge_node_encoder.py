import torch

from .fast_attention import grouped_attention, make_grouped_attention_layout


EDGE_SET_WIDTH = 32
MAX_INCIDENT_EDGES = 21


def _edge_mask(degree, width):
    return (
        torch.arange(width, device=degree.device).unsqueeze(0)
        < degree.unsqueeze(1)
    )


class DeepSetsEdgeEncoder(torch.nn.Module):
    """Permutation-invariant learned encoder of each node's incident edge set."""

    output_dim = EDGE_SET_WIDTH

    def __init__(self):
        super().__init__()
        self.phi = torch.nn.Sequential(
            torch.nn.Linear(2, EDGE_SET_WIDTH),
            torch.nn.GELU(),
            torch.nn.Linear(EDGE_SET_WIDTH, EDGE_SET_WIDTH),
        )
        self.rho = torch.nn.Sequential(
            torch.nn.Linear(EDGE_SET_WIDTH + 1, EDGE_SET_WIDTH),
            torch.nn.GELU(),
            torch.nn.LayerNorm(EDGE_SET_WIDTH),
        )

    def forward(self, pairs, degree):
        mask = _edge_mask(degree, pairs.shape[1])
        encoded = self.phi(pairs) * mask.unsqueeze(-1)
        pooled = encoded.sum(dim=1)
        degree_feature = (
            degree.to(pairs.dtype) / float(MAX_INCIDENT_EDGES)
        ).unsqueeze(-1)
        return self.rho(torch.cat((pooled, degree_feature), dim=-1))


class SetTransformerEdgeEncoder(torch.nn.Module):
    """One self-attention block plus PMA-style learned-seed pooling."""

    output_dim = EDGE_SET_WIDTH

    def __init__(self, heads=4):
        super().__init__()
        self.input = torch.nn.Linear(2, EDGE_SET_WIDTH)
        # batch_first=False because grouped_attention builds its own
        # (sets, members, width) layout and reads the packed projections directly. The
        # flag decides how nn.MultiheadAttention would interpret inputs, which this path
        # bypasses, so no parameter and no saved state_dict changes with it.
        self.self_attention = torch.nn.MultiheadAttention(
            EDGE_SET_WIDTH, heads, batch_first=False
        )
        self.self_norm = torch.nn.LayerNorm(EDGE_SET_WIDTH)
        self.feed_forward = torch.nn.Sequential(
            torch.nn.Linear(EDGE_SET_WIDTH, 2 * EDGE_SET_WIDTH),
            torch.nn.GELU(),
            torch.nn.Linear(2 * EDGE_SET_WIDTH, EDGE_SET_WIDTH),
        )
        self.ffn_norm = torch.nn.LayerNorm(EDGE_SET_WIDTH)
        self.seed = torch.nn.Parameter(torch.zeros(1, 1, EDGE_SET_WIDTH))
        self.pool_attention = torch.nn.MultiheadAttention(
            EDGE_SET_WIDTH, heads, batch_first=False
        )
        self.pool_norm = torch.nn.LayerNorm(EDGE_SET_WIDTH)

    def forward(self, pairs, degree):
        # Through grouped_attention rather than nn.MultiheadAttention's key_padding_mask.
        # That mask is expanded to (nodes*heads, L, S) before the kernel sees it -- 5.6M
        # entries at the real sizes (3200 nodes, 21 edges, 4 heads), rebuilt every call --
        # while grouped_attention broadcasts it over heads and queries instead. Measured
        # bit-identical to the previous path and about twice as fast.
        #
        # It wants a flat list plus "which set each row belongs to", so the padded slots
        # are dropped here and the sets are rebuilt inside. Padding never reached the
        # output anyway: the pooling below masked it out, and normalisation and the FFN
        # act per position, so no padded slot could influence a real one.
        valid = _edge_mask(degree, pairs.shape[1])
        node_of_edge = torch.arange(
            pairs.shape[0], device=pairs.device
        ).repeat_interleave(degree)
        # width pinned to the padded input's own width: letting it shrink to the largest
        # degree in the batch would change the shapes and the last bits with them, and it
        # would shrink almost always -- one node in 7804 reaches the cap.
        edge_layout = make_grouped_attention_layout(
            node_of_edge, pairs.shape[0], width=pairs.shape[1]
        )

        x = self.input(pairs[valid])
        attended = grouped_attention(
            self.self_attention, x, node_of_edge, x, node_of_edge, pairs.shape[0],
            q_layout=edge_layout, kv_layout=edge_layout,
        )
        x = self.self_norm(x + attended)
        x = self.ffn_norm(x + self.feed_forward(x))

        # One query per node, so its "sets" hold a single row each.
        seed = self.seed.expand(pairs.shape[0], -1, -1).reshape(pairs.shape[0], -1)
        node_ids = torch.arange(pairs.shape[0], device=pairs.device)
        pooled = grouped_attention(
            self.pool_attention, seed, node_ids, x, node_of_edge, pairs.shape[0],
            q_layout=make_grouped_attention_layout(node_ids, pairs.shape[0]),
            kv_layout=edge_layout,
        )
        return self.pool_norm(seed + pooled)
