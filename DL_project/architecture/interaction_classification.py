import torch

try:
    from .cross_attention import CrossAttention
    from .final_layer import Final_Layer
    from .lipid_encoder import Lipid_encoder
    from .protein_encoder import Protein_encoder
    from .mlp_utils import ConcreteDropout
    from .fast_attention import make_grouped_attention_layout
    from training.read_configuration import ModelConfig
except ImportError:
    from cross_attention import CrossAttention
    from final_layer import Final_Layer
    from lipid_encoder import Lipid_encoder
    from protein_encoder import Protein_encoder
    from mlp_utils import ConcreteDropout
    from fast_attention import make_grouped_attention_layout
    from read_configuration import ModelConfig


class InteractionClassification(torch.nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        """Initialize the configured protein-lipid interaction architecture."""

        super(InteractionClassification, self).__init__()
        config.validate()
        self.config = config

        self.lipid1 = Lipid_encoder(self.config)
        self.protein1 = Protein_encoder(self.config)
        if self.config.cross_attention:
            self.cross_attention1 = CrossAttention(
                self.config.hiddim, self.config.hiddim, self.config
            )
        if self.config.double_attention:
            self.lipid2 = Lipid_encoder(self.config, start=False)
            self.protein2 = Protein_encoder(self.config, start=False)
            self.cross_attention2 = CrossAttention(
                self.config.hiddim, self.config.hiddim, self.config
            )
        self.final_layer = Final_Layer(self.config)

    def lipid_branch_parameters(self):
        """The lipid stream's own parameters, from the encoder through its pooling.

        What lipid_path_handicap slows. The boundary is deliberate: everything that
        transforms the lipid stream is in, but ``lip_cross_attention`` is NOT. That
        block's weights are how the lipid reads the protein -- the interaction channel
        the handicap exists to make room for -- so slowing it would work against the
        point. ``lip_adversary`` is also out: it is a probe attached to the lipid
        stream, not part of it, and handicapping a probe only weakens the measurement.

        A parameter list rather than a gradient hook because the optimiser is Adam,
        whose step m/sqrt(v) is invariant to a constant rescaling of the gradient --
        scaling the lipid gradient would be very nearly a no-op. Selecting parameters
        also keeps the handicap off the protein, which a hook on the post-attention
        lipid activations could not do: cross-attention makes that tensor a function of
        both partners, so its gradient runs back into the protein encoder as well.
        """
        modules = [self.lipid1]
        if self.config.double_attention:
            modules.append(self.lipid2)
        for name in ("cross_attention1", "cross_attention2"):
            block = getattr(self, name, None)
            if block is None:
                continue
            modules.extend(
                part
                for part in (
                    block.lipFFN, block.lip_ln1, block.lip_ln2,
                    getattr(block, "lip_attn_gate", None),
                    getattr(block, "lip_ffn_gate", None),
                )
                if part is not None
            )
        modules.extend(
            pool
            for pool in (
                getattr(self.final_layer, "lip_attn_pool", None),
                getattr(self.final_layer, "lip_gem_pool", None),
            )
            if pool is not None
        )
        seen, params = set(), []
        for module in modules:
            owned = (
                [module] if isinstance(module, torch.nn.Parameter)
                else module.parameters()
            )
            for parameter in owned:
                if id(parameter) not in seen:
                    seen.add(id(parameter))
                    params.append(parameter)
        return params

    def set_rnabang_normalization(self, stats):
        self.protein1.set_rnabang_normalization(stats)

    def set_pocket_descriptor_normalization(self, stats):
        self.protein1.set_pocket_descriptor_normalization(stats)

    def discovered_dropout(self):
        """Learned dropout p per Concrete Dropout site, keyed by module path.

        Empty dict when bilevel_dropout is off. The module path says which layer each
        rate belongs to, so a later plain run can bake each p into its own nn.Dropout.
        """
        return {
            name: float(module.p().detach())
            for name, module in self.named_modules()
            if isinstance(module, ConcreteDropout)
        }

    def _select_pocket_nodes(self, prot, prot_batch, pocket_mask):
        """Select pocket nodes for final pooling when pocket pooling is enabled."""
        if not self.config.prot_pooling_by_pockets:
            return prot, prot_batch
        if pocket_mask is None:
            raise ValueError("pocket_mask is required for protein pocket pooling")

        pocket_mask = pocket_mask.bool()
        graph_count = int(prot_batch.max().item()) + 1
        pocket_counts = torch.bincount(
            prot_batch[pocket_mask],
            minlength=graph_count,
        )
        missing_graphs = torch.nonzero(pocket_counts == 0, as_tuple=False).flatten()
        if missing_graphs.numel() > 0:
            missing = missing_graphs.detach().cpu().tolist()
            raise ValueError(
                f"Protein samples without pocket nodes cannot be pooled: {missing}"
            )

        return prot[pocket_mask], prot_batch[pocket_mask]

    def _pocket_attention_operands(self, prot_batch, pocket_mask, num_graphs):
        """Layout and node index for the compacted pocket-restricted attention.

        Returns ``(None, None)`` unless a site is restricted; this is only reached on
        the fast_attention path, which is the one that has a padded key axis to shrink.
        The default path spells the same restriction as -inf key biases. Building the
        layout once here matters for the same reason the full layouts are built once:
        the protein self-attention and the lipid-query cross-attention would otherwise
        each rebuild the same bincount/cumsum/scatter mapping -- and they share it even
        when only one of them is restricted, so the shared build is never wasted.
        """
        if not self._restricts_any_site():
            return None, None
        if pocket_mask is None:
            raise ValueError("attention_by_pockets requires pocket_mask")
        pocket_index = torch.nonzero(pocket_mask.bool(), as_tuple=False).flatten()
        return (
            make_grouped_attention_layout(prot_batch[pocket_index], num_graphs),
            pocket_index,
        )

    def _restricts_any_site(self):
        """Whether pocket restriction is active at the self- or the cross-attention."""
        return bool(
            getattr(self.config, "pocket_attention_self", False)
            or getattr(self.config, "pocket_attention_cross", False)
        )

    def _check_pocket_coverage(self, prot_batch, pocket_mask):
        """Every sample needs a pocket residue once non-pocket keys are forbidden.

        A protein with no pocket node leaves its queries with every key masked to -inf,
        and softmax over an all -inf row is NaN -- which would surface as a silent NaN
        loss many layers later rather than here.
        """
        if pocket_mask is None:
            raise ValueError("attention_by_pockets requires pocket_mask")
        counts = torch.bincount(
            prot_batch[pocket_mask.bool()],
            minlength=int(prot_batch.max().item()) + 1,
        )
        missing = torch.nonzero(counts == 0, as_tuple=False).flatten()
        if missing.numel() > 0:
            raise ValueError(
                "attention_by_pockets leaves these samples with no attendable "
                f"protein residue: {missing.detach().cpu().tolist()}"
            )

    def _pool_pocket_mask(self, prot_batch, pocket_mask):
        """Pocket bool aligned to the protein nodes that reach pooling.

        Only consumed by attention-pooling pocket bias. When pooling by pockets the
        nodes are already restricted to the pocket (all True); otherwise it is the full
        mask. Returns None when there is no pocket information.
        """
        if pocket_mask is None:
            return None
        pocket_mask = pocket_mask.bool()
        if self.config.prot_pooling_by_pockets:
            return torch.ones(
                int(pocket_mask.sum()), dtype=torch.bool, device=pocket_mask.device
            )
        return pocket_mask

    def _pocket_pool_signal(self, prot_batch, pocket_mask, node_confidence):
        """Per-node signal fed to AttentionPool's pocket-bias term.

        Binary pocket flag by default (_pool_pocket_mask), matching pocketness.pdb's
        own pocket-membership flag. When use_esm3_v2_embeddings is on and a real
        per-node confidence is supplied (data/esm3_input/<stem>_node_confidence.csv --
        real pLDDT for AlphaFold stems, direction-normalized B-factor for
        experimental ones; NOT pocketness.pdb's binary flag, see
        preprocessing/build_consistent_esm3_pdb.py), use that continuous value
        instead, so pooling weights residues by how reliable their structure is
        rather than by a coarse in/out-of-pocket flag.
        """
        if (
            getattr(self.config, "use_esm3_v2_embeddings", False)
            and node_confidence is not None
        ):
            if pocket_mask is not None and self.config.prot_pooling_by_pockets:
                return node_confidence[pocket_mask.bool()]
            return node_confidence
        return self._pool_pocket_mask(prot_batch, pocket_mask)

    def forward(
        self,
        config,
        plm,
        bury,
        prot,
        prot_edgidx,
        prot_e_attr,
        prot_batch,
        lip,
        lip_batch,
        lip_edgidx=None,
        lip_e_attr=None,
        lipid_batch=None,
        pocket_mask=None,
        node_confidence=None,
        prot_frame_rotation=None,
        prot_frame_translation=None,
        prot_geometric_node_attr=None,
        prot_edge_node_pairs=None,
        prot_edge_node_degree=None,
        pocket_descriptor=None,
        frozen_prior=None,
        compat_input=None):
        """Encode a batched protein-lipid input and return binary logits."""


        if config.lipid_fragments_mask:
            assert lipid_batch is not None
            multiple_lipid_mask = lipid_batch.unsqueeze(0) == lipid_batch.unsqueeze(1)

        if self._restricts_any_site():
            self._check_pocket_coverage(prot_batch, pocket_mask)

        if config.fast_attention:
            num_graphs = int(max(int(prot_batch.max()), int(lip_batch.max()))) + 1
            prot_layout = make_grouped_attention_layout(prot_batch, num_graphs)
            lip_layout = make_grouped_attention_layout(lip_batch, num_graphs)
            # Every fast attention site uses the layouts above. Lipid fragment
            # attention is the sole exception and still needs its finer mask.
            prot_self_att_mask = None
            lip_self_att_mask = (
                lip_batch.unsqueeze(0) != lip_batch.unsqueeze(1)
                if config.lipid_fragments_mask
                else None
            )
            lip_cross_att_mask = None
            prot_cross_att_mask = None
            pocket_layout, pocket_index = self._pocket_attention_operands(
                prot_batch, pocket_mask, num_graphs
            )
        else:
            prot_layout = None
            lip_layout = None
            pocket_layout, pocket_index = None, None
            prot_self_att_mask = prot_batch.unsqueeze(0) != prot_batch.unsqueeze(1)
            lip_self_att_mask = lip_batch.unsqueeze(0) != lip_batch.unsqueeze(1)
            lip_cross_att_mask = prot_batch.unsqueeze(0) != lip_batch.unsqueeze(1)
            prot_cross_att_mask = lip_batch.unsqueeze(0) != prot_batch.unsqueeze(1)

        # Each site compacts only if that site is the restricted one. Off the fast
        # path both are None and each module falls back to its -inf mask.
        self_pocket_layout, self_pocket_index = (
            (pocket_layout, pocket_index)
            if getattr(config, "pocket_attention_self", False)
            else (None, None)
        )
        cross_pocket_layout, cross_pocket_index = (
            (pocket_layout, pocket_index)
            if getattr(config, "pocket_attention_cross", False)
            else (None, None)
        )

        prot1 = self.protein1(
            config,
            prot,
            prot_edgidx,
            plm,
            prot_e_attr,
            prot_batch,
            bury,
            prot_self_att_mask,
            pocket_mask,
            fast_layout=prot_layout,
            pocket_layout=self_pocket_layout,
            pocket_index=self_pocket_index,
            pocket_descriptor=pocket_descriptor,
            frame_rotation=prot_frame_rotation,
            frame_translation=prot_frame_translation,
            geometric_node_attr=prot_geometric_node_attr,
            edge_node_pairs=prot_edge_node_pairs,
            edge_node_degree=prot_edge_node_degree)


        if getattr(config, "lipid_graph_isomers", False):
            lip1 = self.lipid1(
                lip,
                lip_batch,
                lip_self_att_mask,
                multiple_lipid_mask if config.lipid_fragments_mask else None,
                edge_index=lip_edgidx, edge_attr=lip_e_attr,
                fast_layout=lip_layout)
        elif config.lipid_fragments_mask:
            lip1 = self.lipid1(
                lip, lip_batch, lip_self_att_mask, multiple_lipid_mask,
                fast_layout=lip_layout,
            )
        else:
            lip1 = self.lipid1(
                lip, lip_batch, lip_self_att_mask, fast_layout=lip_layout
            )

        # Adversarial anti-shortcut: run the per-partner adversaries on the
        # PRE-cross-attention representations, the only point where each partner is
        # still genuinely single-partner. Cross-attention below injects the
        # counterpart into each stream (its values are the other partner, added
        # residually), so the adversary must read lip1/prot1 before it. Pocket
        # selection mirrors the classifier's protein pooling substrate.
        if config.adversarial_grl and self.training:
            prot_adv, prot_adv_batch = self._select_pocket_nodes(
                prot1, prot_batch, pocket_mask
            )
            prot_adv_pocket = self._pocket_pool_signal(prot_batch, pocket_mask, node_confidence)
        else:
            prot_adv, prot_adv_batch, prot_adv_pocket = prot1, prot_batch, None
        self.final_layer.compute_adversary(
            lip1, prot_adv, lip_batch, prot_adv_batch, config.pool, prot_adv_pocket
        )

        if not config.double_attention:
            if config.cross_attention:
                cross_pocket_mask = (
                    pocket_mask
                    if config.prot_attention_pos_bias
                    or getattr(config, "pocket_attention_cross", False)
                    else None
                )
                lip1, prot1 = self.cross_attention1(
                    lip1, prot1, lip_cross_att_mask, prot_cross_att_mask, cross_pocket_mask,
                    lip_batch=lip_batch, prot_batch=prot_batch,
                    lip_layout=lip_layout, prot_layout=prot_layout,
                    pocket_layout=cross_pocket_layout, pocket_index=cross_pocket_index)

            prot1, pooled_prot_batch = self._select_pocket_nodes(
                prot1, prot_batch, pocket_mask
            )
            out = self.final_layer(
                lip1, prot1, lip_batch, pooled_prot_batch, config.pool,
                self._pocket_pool_signal(prot_batch, pocket_mask, node_confidence),
                frozen_prior=frozen_prior,
                compat_input=compat_input,
            )

        if config.double_attention:
            cross_pocket_mask = (
                pocket_mask
                if config.prot_attention_pos_bias
                or getattr(config, "pocket_attention_cross", False)
                else None
            )
            lip1, prot1 = self.cross_attention1(
                lip1, prot1, lip_cross_att_mask, prot_cross_att_mask, cross_pocket_mask,
                lip_batch=lip_batch, prot_batch=prot_batch,
                lip_layout=lip_layout, prot_layout=prot_layout,
                pocket_layout=cross_pocket_layout, pocket_index=cross_pocket_index)

            prot2 = self.protein2(
                config,
                prot1,
                prot_edgidx,
                plm,
                prot_e_attr,
                prot_batch,
                bury,
                prot_self_att_mask,
                pocket_mask,
                start=False,
                fast_layout=prot_layout,
                pocket_layout=self_pocket_layout,
                pocket_index=self_pocket_index,
                frame_rotation=prot_frame_rotation,
                frame_translation=prot_frame_translation,
                geometric_node_attr=prot_geometric_node_attr,
                edge_node_pairs=prot_edge_node_pairs,
                edge_node_degree=prot_edge_node_degree)

            if getattr(config, "lipid_graph_isomers", False):
                lip2 = self.lipid2(
                    lip1,
                    lip_batch,
                    lip_self_att_mask,
                    multiple_lipid_mask if config.lipid_fragments_mask else None,
                    edge_index=lip_edgidx, edge_attr=lip_e_attr,
                    fast_layout=lip_layout)
            elif config.lipid_fragments_mask:
                lip2 = self.lipid2(
                    lip1, lip_batch, lip_self_att_mask, multiple_lipid_mask,
                    fast_layout=lip_layout,
                )
            else:
                lip2 = self.lipid2(
                    lip1, lip_batch, lip_self_att_mask, fast_layout=lip_layout
                )

            lip2, prot2 = self.cross_attention2(
                lip2, prot2, lip_cross_att_mask, prot_cross_att_mask, cross_pocket_mask,
                lip_batch=lip_batch, prot_batch=prot_batch,
                lip_layout=lip_layout, prot_layout=prot_layout,
                pocket_layout=cross_pocket_layout, pocket_index=cross_pocket_index,
            )

            prot2, pooled_prot_batch = self._select_pocket_nodes(
                prot2, prot_batch, pocket_mask
            )
            out = self.final_layer(
                lip2, prot2, lip_batch, pooled_prot_batch, config.pool,
                self._pocket_pool_signal(prot_batch, pocket_mask, node_confidence),
                frozen_prior=frozen_prior,
                compat_input=compat_input,
            )

        return out
