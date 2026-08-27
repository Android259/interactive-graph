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

    def __init__(self, batch, num_graphs, width=None):
        self.batch = batch
        self.num_graphs = num_graphs
        counts = torch.bincount(batch, minlength=num_graphs)
        # width pins the padded rectangle instead of fitting it to the largest group.
        # The graph attention leaves it None and gets the tightest rectangle, which is
        # the point of the dense layout. A caller whose input was already padded to a
        # fixed width passes that width, because shrinking it changes the shapes the
        # arithmetic runs on and with them the last bits of the result -- measured at
        # ~4e-07 on the edge-set encoder, whose degrees reach the cap in exactly one node
        # out of 7804, so the rectangle would otherwise shrink in almost every batch.
        self.max_nodes = (
            width if width is not None
            else (int(counts.max()) if counts.numel() else 0)
        )
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


def make_grouped_attention_layout(batch, num_graphs=None, width=None):
    """Build the static flat↔dense mapping once for all attention sites."""
    if num_graphs is None:
        num_graphs = int(batch.max()) + 1
    return GroupedAttentionLayout(batch, num_graphs, width=width)


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
    q_dense=None,
    kv_dense=None,
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
    # Packing allocates a (graphs, max_nodes, dim) zero tensor and scatters the flat
    # values into it. Doing it twice for the same input is pure waste -- the second
    # result is byte-identical to the first, and it costs the allocation, the scatter,
    # and a matching gather in the backward pass. Two ways in:
    #
    # * Self-attention hands the SAME tensor and layout as query and key, exactly as
    #   nn.MultiheadAttention's own `if q is k` fast path expects, so the identity check
    #   below collapses the two packs into one.
    # * Cross-attention calls this twice per layer with the roles swapped (lip as query
    #   then as key, prot the other way round), so the duplicate spans two calls and no
    #   check inside one of them can see it. There the caller packs each partner once and
    #   passes the result in.
    #
    # Neither path computes anything: this only decides whether an identical tensor is
    # built again or reused, so results are unchanged bit for bit.
    if q_dense is None:
        q_dense = q_layout.pack(q_x)
    if kv_dense is None:
        kv_dense = (
            q_dense
            if (kv_x is q_x and kv_layout is q_layout)
            else kv_layout.pack(kv_x)
        )
    q_valid = q_layout.valid
    kv_valid = kv_layout.valid
    graphs, q_len, _ = q_dense.shape
    kv_len = kv_dense.shape[1]

    # Packed QKV weights, projected exactly the way nn.MultiheadAttention's own
    # _in_projection_packed does it: one matmul when query and key are the same tensor,
    # otherwise one for the query and one shared by key and value, which always come from
    # the same input. Three separate projections was this file's own invention and it
    # loses twice -- three dispatches instead of one, and BLAS repacking the same input
    # matrix into its internal blocked layout once per call instead of once in total.
    #
    # Merging changes the problem's shape (3*dim outputs instead of dim), and BLAS picks
    # its blocking over the reduction axis from the shape, so this is only safe because it
    # was measured: bit-identical to the three separate projections at (graphs, len, dim)
    # of (8,400,64), (8,72,64), (8,600,64), (16,400,64) and (8,400,128). The reduction
    # axis is `dim` either way and MKL kept the same blocking over it. Re-check before
    # trusting it at a hiddim far from these.
    weight, bias = mha.in_proj_weight, mha.in_proj_bias
    if kv_dense is q_dense:
        query, key, value = F.linear(q_dense, weight, bias).chunk(3, dim=-1)
    else:
        q_weight, kv_weight = weight.split([dim, 2 * dim])
        q_bias, kv_bias = (
            (None, None) if bias is None else bias.split([dim, 2 * dim])
        )
        query = F.linear(q_dense, q_weight, q_bias)
        key, value = F.linear(kv_dense, kv_weight, kv_bias).chunk(2, dim=-1)

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

    --mlp_in_place_of_sa also keeps the default path: this fast path reaches directly
    into the caller's nn.MultiheadAttention (in_proj_weight/out_proj -- see this
    module's own docstring), which mlp_utils.AttentionMLPSubstitute does not have,
    so it must go through the ordinary (query, key, value)-call fallback instead.
    """
    return (
        getattr(config, "fast_attention", False)
        and batch is not None
        and not getattr(config, "mlp_in_place_of_sa", False)
    )
