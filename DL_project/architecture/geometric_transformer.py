import math

import torch
import torch.nn.functional as F

from .mlp_utils import NodeMLPSubstitute


class RMSNorm(torch.nn.Module):
    def __init__(self, dim, eps=1e-8):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        scale = torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return x * scale * self.weight


def _apply_rope(x, positions):
    """Apply residue-index rotary encoding to [nodes, heads, head_dim]."""
    rotary_dim = x.shape[-1] - (x.shape[-1] % 2)
    if rotary_dim == 0:
        return x
    half = rotary_dim // 2
    frequencies = torch.exp(
        torch.arange(half, device=x.device, dtype=x.dtype)
        * (-math.log(10000.0) / max(half, 1))
    )
    angles = positions.to(x.dtype)[:, None] * frequencies[None, :]
    cos = angles.cos()[:, None, :]
    sin = angles.sin()[:, None, :]
    even = x[..., :rotary_dim:2]
    odd = x[..., 1:rotary_dim:2]
    rotated = torch.stack(
        (even * cos - odd * sin, even * sin + odd * cos), dim=-1
    ).flatten(-2)
    if rotary_dim == x.shape[-1]:
        return rotated
    return torch.cat((rotated, x[..., rotary_dim:]), dim=-1)


def _positions_within_graph(batch):
    counts = torch.bincount(batch)
    return torch.cat(
        [torch.arange(int(count), device=batch.device) for count in counts], dim=0
    )


class RoPESelfAttention(torch.nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.q = torch.nn.Linear(dim, dim, bias=False)
        self.kv = torch.nn.Linear(dim, 2 * dim, bias=False)
        self.out = torch.nn.Linear(dim, dim)

    def forward(self, x, batch, layout=None):
        shape = (x.shape[0], self.heads, self.head_dim)
        positions = _positions_within_graph(batch)
        q = _apply_rope(self.q(x).view(shape), positions)
        k, v = self.kv(x).view(x.shape[0], self.heads, 2 * self.head_dim).chunk(2, -1)
        k = _apply_rope(k, positions)
        if layout is not None:
            q = layout.pack(q).transpose(1, 2)
            k = layout.pack(k).transpose(1, 2)
            v = layout.pack(v).transpose(1, 2)
            key_mask = torch.zeros(
                layout.num_graphs,
                1,
                1,
                layout.max_nodes,
                dtype=x.dtype,
                device=x.device,
            ).masked_fill(
                ~layout.valid[:, None, None, :], -torch.inf
            )
            values = F.scaled_dot_product_attention(
                q, k, v, attn_mask=key_mask
            )
            values = values.transpose(1, 2).reshape(
                layout.num_graphs, layout.max_nodes, -1
            )
            return self.out(layout.unpack(values))
        scores = torch.einsum("ihd,jhd->hij", q, k) / math.sqrt(self.head_dim)
        scores = scores.masked_fill(
            (batch[:, None] != batch[None, :]).unsqueeze(0), -torch.inf
        )
        attention = torch.softmax(scores, dim=-1)
        values = torch.einsum("hij,jhd->ihd", attention, v)
        return self.out(values.reshape(x.shape[0], -1))


class InvariantPointAttention(torch.nn.Module):
    """Point-only geometric attention used by RNA-BAnG's protein encoder."""

    def __init__(self, dim, heads, query_points=4, value_points=8, eps=1e-8):
        super().__init__()
        self.heads = heads
        self.query_points = query_points
        self.value_points = value_points
        self.eps = eps
        self.q_points = torch.nn.Linear(
            dim, heads * query_points * 3, bias=False
        )
        self.kv_points = torch.nn.Linear(
            dim, heads * (query_points + value_points) * 3, bias=False
        )
        self.head_weights = torch.nn.Parameter(torch.full((heads,), 0.5413248546))
        self.out = torch.nn.Linear(heads * value_points * 4, dim)

    def forward(
        self, x, rotations, translations, batch, layout=None, query_chunk_size=0
    ):
        if layout is not None:
            return self._forward_padded(
                x,
                rotations,
                translations,
                layout,
                query_chunk_size,
            )
        n = x.shape[0]
        q_local = self.q_points(x).view(
            n, self.heads, self.query_points, 3
        )
        kv_local = self.kv_points(x).view(
            n, self.heads, self.query_points + self.value_points, 3
        )
        k_local, v_local = torch.split(
            kv_local, [self.query_points, self.value_points], dim=2
        )

        q = torch.einsum("nij,nhpj->nhpi", rotations, q_local)
        k = torch.einsum("nij,nhpj->nhpi", rotations, k_local)
        v = torch.einsum("nij,nhpj->nhpi", rotations, v_local)
        q = q + translations[:, None, None, :]
        k = k + translations[:, None, None, :]
        v = v + translations[:, None, None, :]

        squared_distance = (
            q[:, None] - k[None, :]
        ).pow(2).sum(dim=(-1, -2)).permute(2, 0, 1)
        weights = torch.nn.functional.softplus(self.head_weights)
        weights = weights * math.sqrt(
            1.0 / (3.0 * (self.query_points * 9.0 / 2.0))
        )
        scores = -0.5 * squared_distance * weights[:, None, None]
        scores = scores.masked_fill(
            (batch[:, None] != batch[None, :]).unsqueeze(0), -torch.inf
        )
        attention = torch.softmax(scores, dim=-1)

        global_output = torch.einsum("hij,jhvc->ihvc", attention, v)
        centered = global_output - translations[:, None, None, :]
        local_output = torch.einsum(
            "nji,nhvj->nhvi", rotations, centered
        )
        norms = torch.sqrt(local_output.pow(2).sum(-1) + self.eps)
        features = torch.cat(
            (local_output.reshape(n, -1), norms.reshape(n, -1)), dim=-1
        )
        return self.out(features.to(x.dtype))

    def _forward_padded(
        self, x, rotations, translations, layout, query_chunk_size
    ):
        """Exact full IPA without constructing cross-protein residue pairs."""
        x_dense = layout.pack(x)
        rotations = layout.pack(rotations)
        translations = layout.pack(translations)
        graphs, length, _ = x_dense.shape
        q_local = self.q_points(x_dense).view(
            graphs, length, self.heads, self.query_points, 3
        )
        kv_local = self.kv_points(x_dense).view(
            graphs,
            length,
            self.heads,
            self.query_points + self.value_points,
            3,
        )
        k_local, v_local = torch.split(
            kv_local, [self.query_points, self.value_points], dim=3
        )
        q = torch.einsum("blij,blhpj->blhpi", rotations, q_local)
        k = torch.einsum("blij,blhpj->blhpi", rotations, k_local)
        v = torch.einsum("blij,blhpj->blhpi", rotations, v_local)
        q = q + translations[:, :, None, None, :]
        k = k + translations[:, :, None, None, :]
        v = v + translations[:, :, None, None, :]

        weights = F.softplus(self.head_weights)
        weights = weights * math.sqrt(
            1.0 / (3.0 * (self.query_points * 9.0 / 2.0))
        )
        chunk_size = query_chunk_size if query_chunk_size > 0 else length
        chunks = []
        key_mask = ~layout.valid[:, None, None, :]
        for start in range(0, length, chunk_size):
            stop = min(start + chunk_size, length)
            q_chunk = q[:, start:stop].permute(0, 2, 1, 3, 4)
            k_by_head = k.permute(0, 2, 1, 3, 4)
            squared_distance = (
                q_chunk[:, :, :, None] - k_by_head[:, :, None, :]
            ).pow(2).sum(dim=(-1, -2))
            scores = -0.5 * squared_distance * weights[None, :, None, None]
            scores = scores.masked_fill(key_mask, -torch.inf)
            attention = torch.softmax(scores, dim=-1)
            output = torch.einsum(
                "bhqk,bkhvc->bqhvc", attention, v
            )
            centered = output - translations[:, start:stop, None, None, :]
            local = torch.einsum(
                "bqji,bqhvj->bqhvi",
                rotations[:, start:stop],
                centered,
            )
            norms = torch.sqrt(local.pow(2).sum(-1) + self.eps)
            chunks.append(
                torch.cat(
                    (
                        local.reshape(graphs, stop - start, -1),
                        norms.reshape(graphs, stop - start, -1),
                    ),
                    dim=-1,
                )
            )
        features = torch.cat(chunks, dim=1)
        return layout.unpack(self.out(features.to(x.dtype)))


class ProteinGeometricTransformerBlock(torch.nn.Module):
    def __init__(self, dim, heads, expansion=2, config=None, act_fn=None):
        super().__init__()
        # --mlp_in_place_of_sa: config is optional (defaults to the real
        # RoPESelfAttention) so existing callers that never pass it are unaffected.
        self.self_attention = (
            NodeMLPSubstitute(dim, config, act_fn)
            if config is not None and getattr(config, "mlp_in_place_of_sa", False)
            else RoPESelfAttention(dim, heads)
        )
        self.geometric_attention = InvariantPointAttention(dim, heads)
        self.feed_forward = torch.nn.Sequential(
            torch.nn.Linear(dim, expansion * dim),
            torch.nn.GELU(),
            torch.nn.Linear(expansion * dim, dim),
        )
        self.norm1 = RMSNorm(dim)
        self.norm2 = RMSNorm(dim)
        self.norm3 = RMSNorm(dim)

    def forward(
        self,
        x,
        rotations,
        translations,
        batch,
        layout=None,
        query_chunk_size=0,
    ):
        x = self.norm1(x + self.self_attention(x, batch, layout))
        x = self.norm2(
            x
            + self.geometric_attention(
                x,
                rotations,
                translations,
                batch,
                layout,
                query_chunk_size,
            )
        )
        return self.norm3(x + self.feed_forward(x))
