import torch

try:
    from .mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer, insert_hidden_gate,
        insert_ffn_unit_gate, insert_input_gate, insert_output_gate, mlp_hidden_dims,
        link_concrete_dropouts,
    )
    from .fast_attention import grouped_attention, can_use_grouped_attention
except ImportError:
    from mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer, insert_hidden_gate,
        insert_ffn_unit_gate, insert_input_gate, insert_output_gate, mlp_hidden_dims,
        link_concrete_dropouts,
    )
    from fast_attention import grouped_attention, can_use_grouped_attention


class SelfAttention(torch.nn.Module):
    def __init__(self, dim, config, act_fn=None) -> None:

        super(SelfAttention, self).__init__()
        self.dim = dim
        self.config = config
        self.self_attention = torch.nn.MultiheadAttention(dim, self.config.HEADS)
        if getattr(self.config, "attention_residual_gates", False):
            self.attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.ffn_gate = torch.nn.Parameter(torch.zeros(1))

        enlarged, last = mlp_hidden_dims(self.config, "lipid_ffn", self.config.m * dim)
        extra = make_extra_hidden_layer(enlarged, last, self.config, act_fn)

        self.FFN = None
        if not getattr(self.config, "no_ffns", False):
            ffn_layers = [
                torch.nn.Linear(dim, enlarged),
                make_activation(self.config, act_fn),
                *make_dropout(self.config, enlarged),
            ]
            insert_ffn_unit_gate(ffn_layers, enlarged, self.config)
            insert_hidden_gate(ffn_layers, enlarged, self.config)
            ffn_layers += [
                *extra,
                torch.nn.Linear(last, dim),
                *make_dropout(self.config, dim),
            ]
            insert_input_gate(ffn_layers, dim, self.config)
            insert_output_gate(ffn_layers, dim, self.config)
            link_concrete_dropouts(ffn_layers)
            self.FFN = torch.nn.Sequential(*ffn_layers)

        self.ln1 = torch.nn.LayerNorm(dim)
        self.ln2 = torch.nn.LayerNorm(dim)
        self.ln3 = torch.nn.LayerNorm(dim)

    def forward(self, x, attn_mask, mult_mask=None, batch=None, fast_layout=None):

        # Pre-norm variant:
        # unnormalized = x
        # x = self.ln1(x)
        # x = x.unsqueeze(1)
        # outl, _ = self.self_attention(x, x, x, attn_mask=attn_mask)
        # unnormalized = unnormalized + outl.squeeze(1)
        # x = self.ln2(unnormalized)
        # x = unnormalized + self.FFN(x)
        # return x

        x = self.ln1(x)
        if self.config.lipid_fragments_mask:
            assert mult_mask is not None
            attn_mask = attn_mask | ~mult_mask
        # fragments_mask blocks by fragment, which is finer than the `batch` partition
        # grouped_attention pads by, so that combination stays on the default path.
        if can_use_grouped_attention(self.config, batch) and not self.config.lipid_fragments_mask:
            outl = grouped_attention(
                self.self_attention, x, batch, x, batch, int(batch.max()) + 1,
                q_layout=fast_layout, kv_layout=fast_layout,
            )
            gated = getattr(self.config, "attention_residual_gates", False)
            x = x + (self.attn_gate * outl if gated else outl)
            x = self.ln2(x)
            if self.FFN is not None:
                ffn_out = self.FFN(x)
                x = x + (self.ffn_gate * ffn_out if gated else ffn_out)
            return self.ln3(x)
        x = x.unsqueeze(1)
        # need_weights=False: outl is bit-identical either way (the discarded second
        # return value is never used), but it lets MultiheadAttention take PyTorch's
        # fused scaled_dot_product_attention path instead of the slower explicit
        # baddbmm + weight-averaging fallback that need_weights=True forces.
        outl, _ = self.self_attention(x, x, x, attn_mask=attn_mask, need_weights=False)
        outl = outl.squeeze(1)
        x = x.squeeze(1)
        gated = getattr(self.config, "attention_residual_gates", False)
        x = x + (self.attn_gate * outl if gated else outl)
        x = self.ln2(x)

        if self.FFN is not None:
            ffn_out = self.FFN(x)
            x = x + (self.ffn_gate * ffn_out if gated else ffn_out)
        x = self.ln3(x)
        return x


class ProteinSelfAttention(torch.nn.Module):
    def __init__(self, dim, config, act_fn=None) -> None:
        super(ProteinSelfAttention, self).__init__()
        self.dim = dim
        self.config = config
        self.self_attention = torch.nn.MultiheadAttention(dim, self.config.HEADS)
        self.attention_by_pockets = bool(
            getattr(self.config, "pocket_attention_self", False)
        )
        # Under attention_by_pockets the surviving keys are all pocket keys, so a bias
        # on them is a constant shift that softmax cancels. Building it anyway would add
        # a parameter that never receives gradient, which inflates number_of_parameters
        # and breaks test_active_configuration_has_no_parameters_without_gradients.
        if not self.attention_by_pockets and (
            self.config.prot_attention_pos_bias or self.config.prot_pooling_by_pockets
        ):
            bias_shape = (
                (self.config.HEADS,)
                if getattr(self.config, "prot_pos_bias_per_head", False)
                else ()
            )
            self.pocket_attention_bias = torch.nn.Parameter(torch.ones(bias_shape))
        if getattr(self.config, "attention_residual_gates", False):
            self.attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.ffn_gate = torch.nn.Parameter(torch.zeros(1))

        enlarged, last = mlp_hidden_dims(self.config, "protein_ffn", self.config.m * dim)
        extra = make_extra_hidden_layer(enlarged, last, self.config, act_fn)

        self.FFN = None
        if not getattr(self.config, "no_ffns", False):
            ffn_layers = [
                torch.nn.Linear(dim, enlarged),
                make_activation(self.config, act_fn),
                *make_dropout(self.config, enlarged),
            ]
            insert_ffn_unit_gate(ffn_layers, enlarged, self.config)
            insert_hidden_gate(ffn_layers, enlarged, self.config)
            ffn_layers += [
                *extra,
                torch.nn.Linear(last, dim),
                *make_dropout(self.config, dim),
            ]
            insert_input_gate(ffn_layers, dim, self.config)
            insert_output_gate(ffn_layers, dim, self.config)
            link_concrete_dropouts(ffn_layers)
            self.FFN = torch.nn.Sequential(*ffn_layers)

        self.ln1 = torch.nn.LayerNorm(dim)
        self.ln2 = torch.nn.LayerNorm(dim)
        self.ln3 = torch.nn.LayerNorm(dim)

    def make_attention_bias(self, attn_mask, pocket_mask, x):

        same_batch = ~attn_mask

        attention_bias = torch.zeros(
            attn_mask.shape,
            dtype=x.dtype,
            device=x.device)

        attention_bias = attention_bias.masked_fill(attn_mask, float("-inf"))
        if pocket_mask is None:
            return attention_bias

        pocket_key_mask = pocket_mask.unsqueeze(0).expand_as(attn_mask)
        if self.attention_by_pockets:
            # Forbid every non-pocket key outright instead of preferring pocket ones.
            return attention_bias.masked_fill(~pocket_key_mask, float("-inf"))
        pocket_term = (same_batch & pocket_key_mask).to(x.dtype)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            per_head_bias = self.pocket_attention_bias.view(-1, 1, 1)
            attention_bias = attention_bias + pocket_term.unsqueeze(0) * per_head_bias
        else:
            attention_bias = attention_bias + pocket_term * self.pocket_attention_bias
        return attention_bias

    def make_key_bias(self, pocket_mask, x):
        """The pocket term of make_attention_bias as a per-key vector.

        make_attention_bias writes `pocket_term * pocket_attention_bias` into every
        (query, key) cell, but the value depends only on the key, so the fast path
        carries just that vector and broadcasts it over queries. attention_by_pockets
        never reaches here: on the fast path it is spelled by compacting the key layout
        instead, so there is no bias to carry.
        """
        if pocket_mask is None:
            return None
        pocket_term = pocket_mask.to(x.dtype)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            return pocket_term.unsqueeze(0) * self.pocket_attention_bias.view(-1, 1)
        return pocket_term * self.pocket_attention_bias

    def forward(
        self, x, attn_mask, pocket_mask, mult_mask=None, batch=None, fast_layout=None,
        pocket_layout=None, pocket_index=None
    ):

        # Pre-norm variant:
        # unnormalized = x
        # x = self.ln1(x)
        # attn_bias = self.make_attention_bias(attn_mask, pocket_mask, x)
        # x = x.unsqueeze(1)
        # outl, _ = self.self_attention(x, x, x, attn_mask=attn_bias)
        # unnormalized = unnormalized + outl.squeeze(1)
        # x = self.ln2(unnormalized)
        # x = unnormalized + self.FFN(x)
        # return x

        x = self.ln1(x)
        if can_use_grouped_attention(self.config, batch):
            if pocket_index is not None:
                # Compacted restriction: the key axis is padded to the largest pocket
                # instead of the largest protein. Queries stay every residue, so each
                # one is still updated -- only what it may look at changes, exactly as
                # in the -inf variant, whose key_bias is then unnecessary.
                outl = grouped_attention(
                    self.self_attention, x, batch, x[pocket_index],
                    batch[pocket_index], int(batch.max()) + 1,
                    q_layout=fast_layout, kv_layout=pocket_layout,
                )
            else:
                outl = grouped_attention(
                    self.self_attention, x, batch, x, batch, int(batch.max()) + 1,
                    key_bias=self.make_key_bias(pocket_mask, x),
                    q_layout=fast_layout, kv_layout=fast_layout,
                )
            gated = getattr(self.config, "attention_residual_gates", False)
            x = x + (self.attn_gate * outl if gated else outl)
            x = self.ln2(x)
            if self.FFN is not None:
                ffn_out = self.FFN(x)
                x = x + (self.ffn_gate * ffn_out if gated else ffn_out)
            return self.ln3(x)
        attn_bias = self.make_attention_bias(attn_mask, pocket_mask, x)
        x = x.unsqueeze(1)
        # See SelfAttention.forward above: need_weights=False is a no-op on outl.
        outl, _ = self.self_attention(x, x, x, attn_mask=attn_bias, need_weights=False)
        outl = outl.squeeze(1)
        x = x.squeeze(1)
        gated = getattr(self.config, "attention_residual_gates", False)
        x = x + (self.attn_gate * outl if gated else outl)
        x = self.ln2(x)

        if self.FFN is not None:
            ffn_out = self.FFN(x)
            x = x + (self.ffn_gate * ffn_out if gated else ffn_out)
        x = self.ln3(x)
        return x
