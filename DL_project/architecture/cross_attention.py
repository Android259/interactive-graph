import torch

try:
    from .mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer, make_gate,
        insert_hidden_gate, insert_ffn_unit_gate, insert_input_gate, insert_output_gate,
        mlp_hidden_dims, link_concrete_dropouts,
    )
    from .fast_attention import grouped_attention, can_use_grouped_attention
except ImportError:
    from mlp_utils import (
        make_activation, make_dropout, make_extra_hidden_layer, make_gate,
        insert_hidden_gate, insert_ffn_unit_gate, insert_input_gate, insert_output_gate,
        mlp_hidden_dims, link_concrete_dropouts,
    )
    from fast_attention import grouped_attention, can_use_grouped_attention


class CrossAttention(torch.nn.Module):
    def __init__(self, lip_dim, prot_dim, config, act_fn=None) -> None:

        super(CrossAttention, self).__init__()
        self.lip_dim = lip_dim
        self.prot_dim = prot_dim
        self.config = config
        self.lip_cross_attention = torch.nn.MultiheadAttention(lip_dim, self.config.HEADS)
        self.prot_cross_attention = torch.nn.MultiheadAttention(prot_dim, self.config.HEADS)

        self.attention_by_pockets = bool(
            getattr(self.config, "pocket_attention_cross", False)
        )
        # See ProteinSelfAttention.__init__: with non-pocket keys removed the bias would
        # be a constant over the survivors, hence a parameter without gradient.
        if self.config.prot_attention_pos_bias and not self.attention_by_pockets:
            # Under pocket_attention_sites=self the cross site is unrestricted, so its
            # soft bias survives and still trains; validate() only rejects the
            # combination when both sites are restricted and nothing would be left.
            bias_shape = (
                (self.config.HEADS,)
                if getattr(self.config, "prot_pos_bias_per_head", False)
                else ()
            )
            self.pocket_attention_bias = torch.nn.Parameter(torch.ones(bias_shape))
        if getattr(self.config, "attention_residual_gates", False):
            self.lip_attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.prot_attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.lip_ffn_gate = torch.nn.Parameter(torch.zeros(1))
            self.prot_ffn_gate = torch.nn.Parameter(torch.zeros(1))

        lip_enlarged, lip_last = mlp_hidden_dims(
            self.config, "cross_lip_ffn", self.config.m * lip_dim
        )
        prot_enlarged, prot_last = mlp_hidden_dims(
            self.config, "cross_prot_ffn", self.config.m * prot_dim
        )
        lip_extra = make_extra_hidden_layer(
            lip_enlarged, lip_last, self.config, act_fn
        )
        prot_extra = make_extra_hidden_layer(
            prot_enlarged, prot_last, self.config, act_fn
        )
        self.lipFFN = None
        self.protFFN = None
        self.no_ffns = getattr(self.config, "no_ffns", False)

        if not self.no_ffns:
            lip_ffn_layers = [
                torch.nn.Linear(lip_dim, lip_enlarged),
                make_activation(self.config, act_fn),
                *make_dropout(self.config, lip_enlarged),
            ]
            insert_ffn_unit_gate(lip_ffn_layers, lip_enlarged, self.config)
            insert_hidden_gate(lip_ffn_layers, lip_enlarged, self.config)
            lip_ffn_layers += [
                *lip_extra,
                torch.nn.Linear(lip_last, lip_dim),
                *make_dropout(self.config, lip_dim),
            ]
            insert_input_gate(lip_ffn_layers, lip_dim, self.config)
            insert_output_gate(lip_ffn_layers, lip_dim, self.config)
            link_concrete_dropouts(lip_ffn_layers)
            self.lipFFN = torch.nn.Sequential(*lip_ffn_layers)

            prot_ffn_layers = [
                torch.nn.Linear(prot_dim, prot_enlarged),
                make_activation(self.config, act_fn),
                *make_dropout(self.config, prot_enlarged),
            ]
            insert_ffn_unit_gate(prot_ffn_layers, prot_enlarged, self.config)
            insert_hidden_gate(prot_ffn_layers, prot_enlarged, self.config)
            prot_ffn_layers += [
                *prot_extra,
                torch.nn.Linear(prot_last, prot_dim),
                *make_dropout(self.config, prot_dim),
            ]
            insert_input_gate(prot_ffn_layers, prot_dim, self.config)
            insert_output_gate(prot_ffn_layers, prot_dim, self.config)
            link_concrete_dropouts(prot_ffn_layers)
            self.protFFN = torch.nn.Sequential(*prot_ffn_layers)
        self.lip_ln1 = torch.nn.LayerNorm(lip_dim)
        self.prot_ln1 = torch.nn.LayerNorm(prot_dim)
        self.lip_ln2 = torch.nn.LayerNorm(lip_dim)
        self.prot_ln2 = torch.nn.LayerNorm(prot_dim)

        # Whole-block gate: out = in + gate * (block(in) - in). Gate -> 0 prunes
        # the entire cross-attention block back to an identity pass-through.
        self.cross_block_gate = None
        if getattr(self.config, "structured_sparsity", False) and getattr(
            self.config, "sparsity_gate_cross_attention", False
        ):
            self.cross_block_gate = make_gate(1, self.config)

    def make_lip_attention_bias(self, lip_mask, pocket_mask, lip):
        if pocket_mask is None:
            return lip_mask

        same_batch = ~lip_mask
        attention_bias = torch.zeros(
            lip_mask.shape,
            dtype=lip.dtype,
            device=lip.device,
        )
        attention_bias = attention_bias.masked_fill(lip_mask, float("-inf"))

        pocket_key_mask = pocket_mask.unsqueeze(0).expand_as(lip_mask)
        if self.attention_by_pockets:
            # The lipid may only look at binding-site residues.
            return attention_bias.masked_fill(~pocket_key_mask, float("-inf"))
        pocket_term = (same_batch & pocket_key_mask).to(lip.dtype)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            per_head_bias = self.pocket_attention_bias.view(-1, 1, 1)
            attention_bias = attention_bias + pocket_term.unsqueeze(0) * per_head_bias
        else:
            attention_bias = attention_bias + pocket_term * self.pocket_attention_bias
        return attention_bias

    def make_lip_key_bias(self, pocket_mask, lip):
        """The pocket term of make_lip_attention_bias as a per-key vector.

        Protein nodes are the keys of the lipid-side cross-attention, and the bias
        depends only on the key, so the fast path broadcasts this over queries instead
        of filling an (lipid_nodes x protein_nodes) matrix with it. attention_by_pockets
        never reaches here: on the fast path it compacts the key layout instead.
        """
        if pocket_mask is None:
            return None
        pocket_term = pocket_mask.to(lip.dtype)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            return pocket_term.unsqueeze(0) * self.pocket_attention_bias.view(-1, 1)
        return pocket_term * self.pocket_attention_bias

    def forward(self, lip, prot, lip_mask, prot_mask, pocket_mask=None,
                lip_batch=None, prot_batch=None, lip_layout=None, prot_layout=None,
                pocket_layout=None, pocket_index=None):
        # Current compact variant:
        # lipid_query = lip.unsqueeze(1)
        # lipid_key = prot.unsqueeze(1)
        # lipid_value = lipid_key
        #
        # prot_query = lipid_key
        # prot_key = lipid_query
        # prot_value = lipid_query
        #
        # lip_outs, _ = self.lip_cross_attention(
        #     lipid_query, lipid_key, lipid_value, attn_mask=lip_mask
        # )
        # prot_outs, _ = self.prot_cross_attention(
        #     prot_query, prot_key, prot_value, attn_mask=prot_mask
        # )
        #
        # lip = lip + lip_outs.squeeze(1)
        # prot = prot + prot_outs.squeeze(1)
        #
        # lip = self.lip_ln1(lip)
        # prot = self.prot_ln1(prot)
        #
        # lip = lip + self.lipFFN(lip)
        # prot = prot + self.protFFN(prot)
        #
        # lip = self.lip_ln2(lip)
        # prot = self.prot_ln2(prot)
        # return lip, prot

        # lip/prot_batch - lists of appartenance of all the nodes to particular graphs
        # lip - all the nodes of all the lipids in dimension self.lip_dimension
        # prot - all the nodes of all the lipids in dimension self.lip_dimension
        # outputs of cross-attentions to all the pairs of lipid-protein of sample from csv

        # Save inputs so the whole block can be gated to an identity when pruned.
        lip_in, prot_in = lip, prot

        if can_use_grouped_attention(self.config, lip_batch) and prot_batch is not None:
            num_graphs = int(max(int(lip_batch.max()), int(prot_batch.max()))) + 1
            # The two calls use the same two tensors with the roles swapped, so left to
            # itself each would pack both partners and the pair would be packed twice
            # over. Packing here instead costs the same two scatters once and hands the
            # identical tensors to both directions. Reuse only -- nothing is recomputed,
            # so the attention sees exactly what it saw before.
            lip_dense = lip_layout.pack(lip)
            prot_dense = prot_layout.pack(prot)
            if pocket_index is not None:
                # Only the lipid-query direction reads protein keys, so only its key
                # axis compacts. The protein-query direction below keeps every residue
                # as a query and attends over lipid nodes, which pockets do not touch.
                pocket_prot = prot[pocket_index]
                lip_outs = grouped_attention(
                    self.lip_cross_attention, lip, lip_batch, pocket_prot,
                    prot_batch[pocket_index], num_graphs,
                    q_layout=lip_layout, kv_layout=pocket_layout,
                    q_dense=lip_dense, kv_dense=pocket_layout.pack(pocket_prot),
                )
            else:
                lip_outs = grouped_attention(
                    self.lip_cross_attention, lip, lip_batch, prot, prot_batch,
                    num_graphs,
                    key_bias=self.make_lip_key_bias(pocket_mask, lip),
                    q_layout=lip_layout, kv_layout=prot_layout,
                    q_dense=lip_dense, kv_dense=prot_dense,
                )
            prot_outs = grouped_attention(
                self.prot_cross_attention, prot, prot_batch, lip, lip_batch, num_graphs,
                q_layout=prot_layout, kv_layout=lip_layout,
                q_dense=prot_dense, kv_dense=lip_dense,
            )
            return self.finish(lip_in, prot_in, lip, prot, lip_outs, prot_outs)

        # from protein to lipid
        lipid_query = lip.unsqueeze(1)
        lipid_key = prot.unsqueeze(1)
        lipid_value = lipid_key

        # from lipid to protein
        prot_query = lipid_key
        prot_key = lipid_query
        prot_value = lipid_query

        lip_attn_mask = self.make_lip_attention_bias(lip_mask, pocket_mask, lip)

        # need_weights=False: neither returned weight tensor is used below (both
        # discarded as `_`), and skipping them lets MultiheadAttention take the fused
        # scaled_dot_product_attention path instead of the slower baddbmm fallback.
        # outl is bit-identical either way.
        lip_outs, _ = self.lip_cross_attention(
            lipid_query, lipid_key, lipid_value, attn_mask=lip_attn_mask, need_weights=False
        )
        prot_outs, _ = self.prot_cross_attention(
            prot_query, prot_key, prot_value, attn_mask=prot_mask, need_weights=False
        )

        return self.finish(
            lip_in, prot_in, lip, prot, lip_outs.squeeze(1), prot_outs.squeeze(1)
        )

    def finish(self, lip_in, prot_in, lip, prot, lip_outs, prot_outs):
        """Residual add, norms, FFNs and block gate -- shared by both attention paths."""
        # add
        gated = getattr(self.config, "attention_residual_gates", False)
        lip = lip + (self.lip_attn_gate * lip_outs if gated else lip_outs)
        prot = prot + (self.prot_attn_gate * prot_outs if gated else prot_outs)

        # normalization
        lip = self.lip_ln1(lip)
        prot = self.prot_ln1(prot)

        # feed-forwards and add
        if not self.no_ffns:
            lip_ffn_out = self.lipFFN(lip)
            prot_ffn_out = self.protFFN(prot)
            lip = lip + (self.lip_ffn_gate * lip_ffn_out if gated else lip_ffn_out)
            prot = prot + (self.prot_ffn_gate * prot_ffn_out if gated else prot_ffn_out)

        # scnd normalisation
        lip = self.lip_ln2(lip)
        prot = self.prot_ln2(prot)

        if self.cross_block_gate is not None:
            lip = lip_in + self.cross_block_gate(lip - lip_in)
            prot = prot_in + self.cross_block_gate(prot - prot_in)
        return lip, prot
