import torch

from .mlp_utils import (
    make_activation, make_dropout, make_extra_hidden_layer, make_gate,
    insert_hidden_gate, insert_ffn_unit_gate, insert_input_gate, insert_output_gate,
    mlp_hidden_dims, link_concrete_dropouts,
)
from .fast_attention import (
    grouped_attention, can_use_grouped_attention, make_grouped_attention_layout,
)
from .thematic_descriptor_head import ForcedInteraction


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
        # cross_attention_bury_bias/cross_attention_chain_bias: extra, INDEPENDENT
        # additive key-bias terms (bury for lipid-query/protein-key, chain_rank for
        # protein-query/lipid-key -- the latter direction had no bias mechanism at all
        # before this). Kept separate from pocket_attention_bias above rather than
        # folded into it, so this cannot change that flag's existing behaviour for any
        # run that doesn't opt into the new ones. softplus keeps each scale >= 0, so
        # a larger bury/chain_rank value always contributes MORE in the same direction
        # -- never silently inverts sign the way an unconstrained scale could.
        per_head = getattr(self.config, "prot_pos_bias_per_head", False)
        bias_shape = (self.config.HEADS,) if per_head else ()
        self.bury_bias_on = bool(getattr(self.config, "cross_attention_bury_bias", False))
        if self.bury_bias_on:
            self.bury_bias_scale = torch.nn.Parameter(torch.ones(bias_shape))
        self.chain_bias_on = bool(getattr(self.config, "cross_attention_chain_bias", False))
        if self.chain_bias_on:
            self.chain_bias_scale = torch.nn.Parameter(torch.ones(bias_shape))
        if getattr(self.config, "attention_residual_gates", False):
            self.lip_attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.prot_attn_gate = torch.nn.Parameter(torch.zeros(1))
            self.lip_ffn_gate = torch.nn.Parameter(torch.zeros(1))
            self.prot_ffn_gate = torch.nn.Parameter(torch.zeros(1))

        # --node_bilinear_fusion (training/read_configuration.py): the node-level,
        # pre-pool sibling of --bilinear_fusion (architecture/final_layer.py). Neither
        # attention path below produces an elementwise/Hadamard product of a lipid
        # node's own content and a protein node's own content -- both compute a
        # weighted SUM of the OTHER side's raw value vectors (see the "Current compact
        # variant" comment in forward()); the interaction only ever decides which
        # values to copy in, never fuses both sides' content per output dimension.
        # ForcedInteraction (architecture/thematic_descriptor_head.py) is reused
        # unmodified for that missing product: lip_dim == prot_dim == config.hiddim
        # always (both CrossAttention instances are built with (hiddim, hiddim) in
        # architecture/interaction_classification.py), so its single `dim` matches
        # both sides.
        self.node_bilinear_fusion_on = bool(
            getattr(self.config, "node_bilinear_fusion", False)
        )
        self.node_bilinear_vec = None
        if self.node_bilinear_fusion_on:
            self.node_bilinear = ForcedInteraction(lip_dim, self.config, act_fn)

        # --cross_attention_forced_interaction: replaces the residual update itself
        # (finish() below), not an extra side-channel like node_bilinear_fusion above.
        # Plain cross-attention only ever computes a weighted SUM of the partner's
        # value vectors and adds it to the node's own content (`lip = lip + lip_outs`)
        # -- a skip path survives whenever attention degenerates toward uniform/near-
        # zero output, since the residual add alone still passes the node's own
        # content through unchanged. Routing (lip, lip_outs) through ForcedInteraction
        # (product-only, no skip -- same class node_bilinear_fusion/thematical_paths
        # reuse) before the residual add means the UPDATE ITSELF is forced to depend
        # on both the node's own content and what it pulled from the partner, not an
        # additional term next to an unforced one.
        self.cross_forced_interaction_on = bool(
            getattr(self.config, "cross_attention_forced_interaction", False)
        )
        if self.cross_forced_interaction_on:
            self.lip_forced_interaction = ForcedInteraction(lip_dim, self.config, act_fn)
            self.prot_forced_interaction = ForcedInteraction(prot_dim, self.config, act_fn)

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

    def make_lip_attention_bias(self, lip_mask, pocket_mask, lip, bury=None):
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
        per_head = getattr(self.config, "prot_pos_bias_per_head", False)
        if per_head:
            per_head_bias = self.pocket_attention_bias.view(-1, 1, 1)
            attention_bias = attention_bias + pocket_term.unsqueeze(0) * per_head_bias
        else:
            attention_bias = attention_bias + pocket_term * self.pocket_attention_bias
        if self.bury_bias_on and bury is not None:
            bury_term = pocket_term * bury.unsqueeze(0).expand_as(lip_mask)
            bury_weight = torch.nn.functional.softplus(self.bury_bias_scale)
            if per_head:
                attention_bias = attention_bias + bury_term.unsqueeze(0) * bury_weight.view(-1, 1, 1)
            else:
                attention_bias = attention_bias + bury_term * bury_weight
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

    def _scaled(self, scale, term):
        """term (per-key vector, matching make_lip_key_bias's own convention),
        weighted by softplus(scale) -- see __init__ for why softplus."""
        weight = torch.nn.functional.softplus(scale)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            return term.unsqueeze(0) * weight.view(-1, 1)
        return term * weight

    def make_bury_key_bias(self, pocket_mask, bury):
        """Extra per-key vector for lipid-query/protein-key attention: bury, restricted
        to pocket residues same as make_lip_key_bias's own pocket_term (so this adds a
        continuous within-pocket preference on top of that binary one, not a second,
        independent channel that could also fire on non-pocket keys). Added to, not
        blended into, make_lip_key_bias's output -- see __init__.
        """
        if not self.bury_bias_on or bury is None or pocket_mask is None:
            return None
        return self._scaled(self.bury_bias_scale, bury * pocket_mask.to(bury.dtype))

    def make_chain_key_bias(self, chain_rank):
        """Per-key vector for protein-query/lipid-key attention -- the direction that,
        before cross_attention_chain_bias, had no bias mechanism at all (only a mask).
        Unrestricted by any pocket-style gate: every lipid atom is a legitimate key
        here, gated only by lip_mask/same-sample membership like the rest of that
        attention already is.
        """
        if not self.chain_bias_on or chain_rank is None:
            return None
        return self._scaled(self.chain_bias_scale, chain_rank)

    def _combine_key_bias(self, *terms):
        terms = [term for term in terms if term is not None]
        if not terms:
            return None
        combined = terms[0]
        for term in terms[1:]:
            combined = combined + term
        return combined

    def make_prot_attention_bias(self, prot_mask, chain_rank, prot):
        """Dense-matrix counterpart of make_chain_key_bias, for the non-fast_attention
        path -- mirrors make_lip_attention_bias's own structure. prot_mask is
        [N_protein(query), N_lipid(key)] (see architecture/AGENTS.md's Attention And
        Pooling Contracts), so chain_rank broadcasts along the LAST axis.
        """
        if not self.chain_bias_on or chain_rank is None:
            return prot_mask
        same_batch = ~prot_mask
        attention_bias = torch.zeros(
            prot_mask.shape, dtype=prot.dtype, device=prot.device
        )
        attention_bias = attention_bias.masked_fill(prot_mask, float("-inf"))
        chain_term = same_batch.to(prot.dtype) * chain_rank.unsqueeze(0).expand_as(prot_mask)
        weight = torch.nn.functional.softplus(self.chain_bias_scale)
        if getattr(self.config, "prot_pos_bias_per_head", False):
            attention_bias = attention_bias + chain_term.unsqueeze(0) * weight.view(-1, 1, 1)
        else:
            attention_bias = attention_bias + chain_term * weight
        return attention_bias

    def _node_bilinear_pooled(self, lip_in, prot_in, lip_batch, prot_batch,
                               lip_layout, prot_layout, pocket_layout, pocket_index,
                               pocket_mask):
        """One --node_bilinear_fusion vector per graph pair (see __init__ docstring).

        Restricted to the SAME (lipid, protein) pairs the lipid-query cross-attention
        already scores in forward() -- pocket-only keys when self.attention_by_pockets
        narrows that site, every same-sample pair otherwise -- so this adds a
        comparable channel, not a wider one. That restriction has two different
        existing spellings depending on --fast_attention, and both are reused as-is:
        on the fast/grouped path pocket_index/pocket_layout are already the compacted
        pocket-only key layout (mirroring the ``pocket_prot = prot[pocket_index]``
        restriction forward()'s grouped-attention branch applies); off that path
        pocket_index is always None (interaction_classification._pocket_attention_
        operands only builds it under --fast_attention) and the same restriction is
        instead spelled as a boolean mask there (make_lip_attention_bias's
        ``pocket_key_mask``), so this falls back to ``prot_in[pocket_mask]`` -- the
        exact boolean-indexing pattern interaction_classification._select_pocket_nodes
        already uses for the pooling step, not a new indexing scheme.

        Reuses GroupedAttentionLayout.pack/valid (architecture/fast_attention.py)
        purely to get a dense (graphs, nodes, dim) view of each side and know which
        entries are padding; lip_layout/prot_layout/pocket_layout are the SAME layouts
        forward()'s grouped-attention branch builds (and are None, requiring a local
        build, exactly on the non-fast_attention path -- no new segment/scatter logic
        either way). The full outer product over a graph's lipid x protein/pocket
        nodes is masked and summed directly rather than routed through
        torch_geometric.nn.global_add_pool: building a flat pair index for a
        variable-size dense product would be new indexing logic of the kind this
        feature is meant to avoid, and masking padding to zero before summing over
        both node axes is the same reduction global_add_pool performs, applied on the
        layout already in hand.
        """
        num_graphs = int(max(int(lip_batch.max()), int(prot_batch.max()))) + 1
        lip_layout = lip_layout or make_grouped_attention_layout(lip_batch, num_graphs)
        if self.attention_by_pockets:
            if pocket_index is not None:
                kv = prot_in[pocket_index]
                kv_batch = prot_batch[pocket_index]
                kv_layout = pocket_layout or make_grouped_attention_layout(kv_batch, num_graphs)
            elif pocket_mask is not None:
                pocket_bool = pocket_mask.bool()
                kv = prot_in[pocket_bool]
                kv_batch = prot_batch[pocket_bool]
                kv_layout = make_grouped_attention_layout(kv_batch, num_graphs)
            else:
                raise ValueError(
                    "node_bilinear_fusion with attention_by_pockets restricting the "
                    "cross site needs pocket_index or pocket_mask -- got neither"
                )
        else:
            kv = prot_in
            kv_batch = prot_batch
            kv_layout = prot_layout or make_grouped_attention_layout(kv_batch, num_graphs)

        lip_dense = lip_layout.pack(lip_in)  # [graphs, max_lip, dim]
        kv_dense = kv_layout.pack(kv)  # [graphs, max_kv, dim]
        # Broadcasts to [graphs, max_lip, max_kv, dim]: ForcedInteraction's proj_a/
        # proj_b/ffn are plain per-last-dim Linears, so they apply unchanged to the
        # extra leading axes -- no modification to that class was needed.
        interaction = self.node_bilinear(lip_dense.unsqueeze(2), kv_dense.unsqueeze(1))
        pair_valid = lip_layout.valid.unsqueeze(2) & kv_layout.valid.unsqueeze(1)
        interaction = interaction * pair_valid.unsqueeze(-1).to(interaction.dtype)
        return interaction.sum(dim=(1, 2))  # [graphs, dim]

    def forward(self, lip, prot, lip_mask, prot_mask, pocket_mask=None,
                lip_batch=None, prot_batch=None, lip_layout=None, prot_layout=None,
                pocket_layout=None, pocket_index=None, bury=None, chain_rank=None):
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

        if self.node_bilinear_fusion_on:
            if lip_batch is None or prot_batch is None:
                raise ValueError(
                    "node_bilinear_fusion requires lip_batch and prot_batch"
                )
            self.node_bilinear_vec = self._node_bilinear_pooled(
                lip_in, prot_in, lip_batch, prot_batch, lip_layout, prot_layout,
                pocket_layout, pocket_index, pocket_mask,
            )
        else:
            self.node_bilinear_vec = None

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
                    key_bias=self._combine_key_bias(
                        self.make_lip_key_bias(pocket_mask, lip),
                        self.make_bury_key_bias(pocket_mask, bury),
                    ),
                    q_layout=lip_layout, kv_layout=prot_layout,
                    q_dense=lip_dense, kv_dense=prot_dense,
                )
            prot_outs = grouped_attention(
                self.prot_cross_attention, prot, prot_batch, lip, lip_batch, num_graphs,
                key_bias=self.make_chain_key_bias(chain_rank),
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

        lip_attn_mask = self.make_lip_attention_bias(lip_mask, pocket_mask, lip, bury)
        prot_attn_mask = self.make_prot_attention_bias(prot_mask, chain_rank, prot)

        # need_weights=False: neither returned weight tensor is used below (both
        # discarded as `_`), and skipping them lets MultiheadAttention take the fused
        # scaled_dot_product_attention path instead of the slower baddbmm fallback.
        # outl is bit-identical either way.
        lip_outs, _ = self.lip_cross_attention(
            lipid_query, lipid_key, lipid_value, attn_mask=lip_attn_mask, need_weights=False
        )
        prot_outs, _ = self.prot_cross_attention(
            prot_query, prot_key, prot_value, attn_mask=prot_attn_mask, need_weights=False
        )

        return self.finish(
            lip_in, prot_in, lip, prot, lip_outs.squeeze(1), prot_outs.squeeze(1)
        )

    def finish(self, lip_in, prot_in, lip, prot, lip_outs, prot_outs):
        """Residual add, norms, FFNs and block gate -- shared by both attention paths."""
        # add
        if self.cross_forced_interaction_on:
            lip_outs = self.lip_forced_interaction(lip, lip_outs)
            prot_outs = self.prot_forced_interaction(prot, prot_outs)
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
