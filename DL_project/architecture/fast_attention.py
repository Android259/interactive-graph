"""Block-diagonal multi-head attention over a batch of graphs.

The default path in self_attention.py / cross_attention.py lays a whole batch out as
one long sequence -- ``x.unsqueeze(1)`` gives ``(N_total_nodes, 1, dim)`` -- and blocks
cross-graph pairs with an ``N x N`` ``-inf`` mask. That computes the full N^2 attention
matrix and then throws most of it away: measured on a real batch of 16, the three
attention sites together build 18.84M logits of which 2.09M are inside a graph (9x
waste), and the cost grows quadratically with batch size while the useful part grows
linearly.

This module computes the same thing on the dense ``(graphs, max_nodes, dim)`` layout,
where the blocked pairs simply do not exist. Two details make it a win rather than a
wash:

* ``nn.MultiheadAttention`` only accepts an ``(N*heads, L, S)`` attention mask, so
  feeding it the padded layout would materialize ``graphs*heads*L*S`` entries -- larger
  than the N^2 mask it replaces, and measurably slower than the default path. So the
  attention is run through ``F.scaled_dot_product_attention`` directly, which accepts a
  broadcastable mask.
* The additive bias here depends only on the *key* (the pocket term is a property of the
  key node), so the mask is built as ``(graphs, heads, 1, max_keys)`` and broadcast over
  the query axis instead of being expanded -- 2.3K entries instead of 2.65M.

The projections come from the caller's ``nn.MultiheadAttention`` module, so the
parameters (and therefore every saved state_dict) are unchanged; only the order of
arithmetic differs. That reordering is not free numerically: summing over a graph's
nodes instead of over the whole padded batch changes float rounding, so results match
the default path to ~6e-08 absolute (~3e-07 relative on gradients) rather than bitwise.
That is why this sits behind ``--fast_attention`` instead of replacing the default.
"""

import torch
import torch.nn.functional as F


class GroupedAttentionLayout:
    """Reusable mapping between flat graph nodes and one padded dense batch."""

    def __init__(self, batch, num_graphs):
        self.batch = batch
        self.num_graphs = num_graphs
        counts = torch.bincount(batch, minlength=num_graphs)
        self.max_nodes = int(counts.max()) if counts.numel() else 0
        starts = torch.cumsum(counts, dim=0) - counts
        # PyG batches are graph-major, so subtracting each graph's flat start gives
        # the reusable within-graph position without another scatter/cumsum per site.
        offsets = torch.arange(batch.numel(), device=batch.device) - starts[batch]
        self.offsets = offsets
        self.valid = torch.zeros(
            num_graphs, self.max_nodes, dtype=torch.bool, device=batch.device
        )
        self.valid[batch, offsets] = True

    def pack(self, values):
        dense = values.new_zeros(
            (self.num_graphs, self.max_nodes) + tuple(values.shape[1:])
        )
        dense[self.batch, self.offsets] = values
        return dense

    def unpack(self, dense):
        return dense[self.batch, self.offsets]


def make_grouped_attention_layout(batch, num_graphs=None):
    """Build the static flat↔dense mapping once for all attention sites."""
    if num_graphs is None:
        num_graphs = int(batch.max()) + 1
    return GroupedAttentionLayout(batch, num_graphs)


def _check_supported(mha):
    """Reject the nn.MultiheadAttention options this path does not reimplement.

    Everything here is off under the project's ``MultiheadAttention(dim, HEADS)``
    construction, so this never fires today. It exists because each of these would
    otherwise change the result *silently*: the module would keep the option, this path
    would ignore it, and the only symptom would be a quietly different model. Fail
    loudly instead, so enabling one is a crash rather than a bad run.
    """
    if mha.dropout:
        raise NotImplementedError(
            f"fast_attention does not apply attention dropout (module has "
            f"dropout={mha.dropout}); it would be silently skipped"
        )
    if mha.bias_k is not None or mha.bias_v is not None:
        raise NotImplementedError("fast_attention does not support add_bias_kv")
    if mha.add_zero_attn:
        raise NotImplementedError("fast_attention does not support add_zero_attn")
    if not mha._qkv_same_embed_dim:
        raise NotImplementedError(
            "fast_attention reads the packed in_proj_weight, so it needs "
            "kdim == vdim == embed_dim"
        )
    if mha.batch_first:
        raise NotImplementedError(
            "fast_attention builds its own (graphs, nodes, dim) layout and assumes the "
            "module was created with batch_first=False"
        )


def grouped_attention(
    mha,
    q_x,
    q_batch,
    kv_x,
    kv_batch,
    num_graphs,
    key_bias=None,
    q_layout=None,
    kv_layout=None,
):
    """Attend within each graph only, returning ``(q_x.shape[0], dim)``.

    ``mha`` supplies the packed in/out projections. ``key_bias`` is an additive
    per-key term, shaped ``(N_kv,)`` or ``(heads, N_kv)``; it lands on the attention
    logits exactly like the pocket bias the default path folds into its mask.

    Unlike ``nn.MultiheadAttention`` this returns only the attended values, never the
    attention weight matrix -- computing it is what the default path pays for and
    discards (see the ``need_weights=False`` calls there).
    """
    _check_supported(mha)
    dim = mha.embed_dim
    heads = mha.num_heads
    head_dim = dim // heads

    q_layout = q_layout or make_grouped_attention_layout(q_batch, num_graphs)
    kv_layout = kv_layout or make_grouped_attention_layout(kv_batch, num_graphs)
    q_dense = q_layout.pack(q_x)
    kv_dense = kv_layout.pack(kv_x)
    q_valid = q_layout.valid
    kv_valid = kv_layout.valid
    graphs, q_len, _ = q_dense.shape
    kv_len = kv_dense.shape[1]

    # Packed QKV weights, sliced so cross-attention (q and kv from different partners)
    # uses the same projections nn.MultiheadAttention would have used.
    weight, bias = mha.in_proj_weight, mha.in_proj_bias
    q_bias, k_bias, v_bias = (None, None, None) if bias is None else bias.chunk(3)
    query = F.linear(q_dense, weight[:dim], q_bias)
    key = F.linear(kv_dense, weight[dim:2 * dim], k_bias)
    value = F.linear(kv_dense, weight[2 * dim:], v_bias)

    def split_heads(tensor, length):
        return tensor.view(graphs, length, heads, head_dim).transpose(1, 2)

    query = split_heads(query, q_len)
    key = split_heads(key, kv_len)
    value = split_heads(value, kv_len)

    # (graphs, heads, 1, kv_len): broadcast over queries rather than expanded, which is
    # the whole reason this path is cheaper than the padded nn.MultiheadAttention one.
    attn_bias = torch.zeros(
        graphs, 1, 1, kv_len, dtype=q_dense.dtype, device=q_dense.device
    ).masked_fill(~kv_valid.view(graphs, 1, 1, kv_len), float("-inf"))
    if key_bias is not None:
        dense_key_bias = kv_layout.pack(
            key_bias.t() if key_bias.dim() == 2 else key_bias.unsqueeze(-1)
        )
        # (graphs, kv_len, 1) for a shared bias, (graphs, kv_len, heads) per head.
        attn_bias = attn_bias + dense_key_bias.permute(0, 2, 1).unsqueeze(2)

    out = F.scaled_dot_product_attention(query, key, value, attn_mask=attn_bias)
    out = out.transpose(1, 2).reshape(graphs, q_len, dim)
    out = F.linear(out, mha.out_proj.weight, mha.out_proj.bias)
    return q_layout.unpack(out)


def can_use_grouped_attention(config, batch):
    """Whether the fast path applies: enabled, and the grouping vector is available.

    ``lipid_fragments_mask`` narrows attention to a fragment rather than a whole graph,
    so its blocks are not the ``batch`` partition this path pads by; those call sites
    keep the default path.
    """
    return getattr(config, "fast_attention", False) and batch is not None
