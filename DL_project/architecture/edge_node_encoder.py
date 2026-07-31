import torch


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
        self.self_attention = torch.nn.MultiheadAttention(
            EDGE_SET_WIDTH, heads, batch_first=True
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
            EDGE_SET_WIDTH, heads, batch_first=True
        )
        self.pool_norm = torch.nn.LayerNorm(EDGE_SET_WIDTH)

    def forward(self, pairs, degree):
        valid = _edge_mask(degree, pairs.shape[1])
        padding_mask = ~valid
        x = self.input(pairs)
        attended, _ = self.self_attention(
            x, x, x, key_padding_mask=padding_mask, need_weights=False
        )
        x = self.self_norm(x + attended)
        x = self.ffn_norm(x + self.feed_forward(x))
        seed = self.seed.expand(x.shape[0], -1, -1)
        pooled, _ = self.pool_attention(
            seed,
            x,
            x,
            key_padding_mask=padding_mask,
            need_weights=False,
        )
        return self.pool_norm(seed + pooled).squeeze(1)
