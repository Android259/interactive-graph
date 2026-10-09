import torch

from .mlp_utils import build_mlp


class DescriptorMLPHead(torch.nn.Module):
    """Plain MLP over an ARBITRARY, caller-named subset of dataloader.descriptors.
    DESCRIPTOR_CATALOG -- same token selection as NamedDescriptorHead (architecture/
    named_descriptor_head.py), but no per-token embedding or self-attention: every
    requested descriptor's own (already-standardized) scalar value is read directly as
    one input feature of an ordinary feedforward network, built with mlp_utils.build_mlp
    at config.hiddim width (the same dropout/gating/third-layer conventions every other
    MLP block in this project already answers to).

    files/results/descriptors_head_bottleneck.md: NamedDescriptorHead's `token_embed =
    Linear(1, dim)` is the SAME weight for every token (only the additive
    `token_identity` constant differs between them), so its reaction to a descriptor's
    own value cannot depend on which descriptor it is. Section 1 there measures an
    ordinary 2-hidden-layer MLP of the same 11 standardized descriptors at test BA
    0.853 against that head's 0.535 on identical input/split/weights. --descriptor_mlp
    (training/read_configuration.py) builds this class instead of NamedDescriptorHead
    in Final_Layer's --descriptor_names sufficiency-test branch, so that comparison is
    a --descriptor_names sweep like --descriptors_head's own, not a one-off script.
    """

    def __init__(self, config, token_names, catalog_order, act_fn=None):
        """`token_names`: this head's own tokens (already-canonical, e.g. from
        dataloader.descriptors.parse_descriptor_list(config.descriptor_names)).
        `catalog_order`: the full, shared column order dataloader/Dataloader.py's
        descriptor_catalog_input tensor is stacked in for this config
        (dataloader.descriptors.full_catalog_order).
        """
        super().__init__()
        if not token_names:
            raise ValueError("DescriptorMLPHead needs at least one descriptor name")
        catalog_index = {name: position for position, name in enumerate(catalog_order)}
        unknown = [name for name in token_names if name not in catalog_index]
        if unknown:
            raise ValueError(
                f"Descriptor name(s) {unknown} are not in catalog_order {catalog_order}"
            )
        self.token_names = tuple(token_names)
        self.token_count = len(self.token_names)
        # Column indices into descriptor_catalog_input, so forward() can select exactly
        # this head's own tokens out of the one shared tensor -- same mechanism as
        # NamedDescriptorHead.catalog_columns.
        self.register_buffer(
            "catalog_columns",
            torch.tensor(
                [catalog_index[name] for name in self.token_names], dtype=torch.long
            ),
            persistent=False,
        )
        self.output_dim = config.hiddim
        # hidden_dim = m * output_dim, output_dim = config.hiddim: the same "enlarged
        # inner width, config.hiddim-wide output" shape every other gated MLP block in
        # this project uses (e.g. Final_Layer's own classifier, NamedDescriptorHead's
        # ffn) -- --m/--hiddim are the configurable width flags, --third_layers_in_mlps
        # the configurable depth flag, all reused rather than a bespoke pair for this
        # head alone.
        hidden = max(config.m * self.output_dim, self.output_dim)
        self.mlp = build_mlp(self.token_count, hidden, self.output_dim, config, act_fn)

    def forward(self, descriptor_catalog_input):
        """descriptor_catalog_input: [batch, len(catalog_order)]. Returns
        [batch, self.output_dim].
        """
        scalars = descriptor_catalog_input.index_select(1, self.catalog_columns)
        return self.mlp(scalars)
