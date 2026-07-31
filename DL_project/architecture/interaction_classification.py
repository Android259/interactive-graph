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

    def set_rnabang_normalization(self, stats):
        self.protein1.set_rnabang_normalization(stats)

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
        prot_edge_node_degree=None):
        """Encode a batched protein-lipid input and return binary logits."""


        if config.lipid_fragments_mask:
            assert lipid_batch is not None
            multiple_lipid_mask = lipid_batch.unsqueeze(0) == lipid_batch.unsqueeze(1)

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
        else:
            prot_layout = None
            lip_layout = None
            prot_self_att_mask = prot_batch.unsqueeze(0) != prot_batch.unsqueeze(1)
            lip_self_att_mask = lip_batch.unsqueeze(0) != lip_batch.unsqueeze(1)
            lip_cross_att_mask = prot_batch.unsqueeze(0) != lip_batch.unsqueeze(1)
            prot_cross_att_mask = lip_batch.unsqueeze(0) != prot_batch.unsqueeze(1)

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
                cross_pocket_mask = pocket_mask if config.prot_attention_pos_bias else None
                if config.prot_attention_pos_bias:
                    assert cross_pocket_mask is not None
                lip1, prot1 = self.cross_attention1(
                    lip1, prot1, lip_cross_att_mask, prot_cross_att_mask, cross_pocket_mask,
                    lip_batch=lip_batch, prot_batch=prot_batch,
                    lip_layout=lip_layout, prot_layout=prot_layout)

            prot1, pooled_prot_batch = self._select_pocket_nodes(
                prot1, prot_batch, pocket_mask
            )
            out = self.final_layer(
                lip1, prot1, lip_batch, pooled_prot_batch, config.pool,
                self._pocket_pool_signal(prot_batch, pocket_mask, node_confidence)
            )

        if config.double_attention:
            cross_pocket_mask = pocket_mask if config.prot_attention_pos_bias else None
            if config.prot_attention_pos_bias:
                assert cross_pocket_mask is not None
            lip1, prot1 = self.cross_attention1(
                lip1, prot1, lip_cross_att_mask, prot_cross_att_mask, cross_pocket_mask,
                lip_batch=lip_batch, prot_batch=prot_batch,
                lip_layout=lip_layout, prot_layout=prot_layout)

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
            )

            prot2, pooled_prot_batch = self._select_pocket_nodes(
                prot2, prot_batch, pocket_mask
            )
            out = self.final_layer(
                lip2, prot2, lip_batch, pooled_prot_batch, config.pool,
                self._pocket_pool_signal(prot_batch, pocket_mask, node_confidence)
            )

        return out
