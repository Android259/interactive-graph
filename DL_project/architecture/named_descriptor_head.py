import torch

from .mlp_utils import make_self_attention

from dataloader.pair_descriptors import parse_descriptor_list, resolve_requested_tokens


class NamedDescriptorHead(torch.nn.Module):
    """Self-attention over an ARBITRARY, caller-named subset of dataloader.pair_
    descriptors.DESCRIPTOR_CATALOG (bare or <name>_coarse=<spec> tokens, see
    parse_descriptor_token) -- --two_pair_descriptors_paths' --good_descriptors/
    --bad_descriptors, each building one of these (architecture/final_layer.py).
    Same token-embed -> self-attention -> FFN -> pool_type-reduce-to-one-vector
    shape as architecture.pair_descriptor_head.PairDescriptorHead, generalised to
    take its token names directly as an argument instead of deriving a fixed set
    from --pair_descriptor_* flags -- the two classes are kept separate rather than
    merged so PairDescriptorHead's existing, tested token-composition logic
    (aromatic_share_split/coarse etc.) is untouched.

    --mlp_in_place_of_sa swaps the self-attention block for a parameter-budget-matched
    per-token MLP here exactly as it does for PairDescriptorHead -- see
    mlp_utils.make_self_attention.
    """

    def __init__(self, config, token_names, catalog_order, act_fn=None):
        """`token_names`: this head's OWN tokens (already-canonical, e.g. from
        dataloader.pair_descriptors.parse_descriptor_list(config.good_descriptors)).
        `catalog_order`: the FULL, shared column order dataloader/Dataloader.py's
        descriptor_catalog_input tensor is stacked in for THIS config -- resolve_
        requested_tokens(config.good_descriptors, config.bad_descriptors), computed
        once by architecture.final_layer.Final_Layer.__init__ and passed to both the
        good and the bad head, so the two agree on where each token lives in the one
        tensor both read from without either recomputing the union independently.
        """
        super().__init__()
        if not token_names:
            raise ValueError("NamedDescriptorHead needs at least one descriptor name")
        catalog_index = {name: position for position, name in enumerate(catalog_order)}
        unknown = [name for name in token_names if name not in catalog_index]
        if unknown:
            # Only reachable if a caller passes a catalog_order that does not cover
            # token_names -- resolve_requested_tokens always includes both heads'
            # own tokens in its union, so Final_Layer's own call site cannot hit this.
            raise ValueError(
                f"Descriptor name(s) {unknown} are not in catalog_order {catalog_order}"
            )
        self.dim = config.hiddim
        self.token_names = tuple(token_names)
        self.token_count = len(self.token_names)
        # Column indices into descriptor_catalog_input (dataloader/Dataloader.py),
        # so forward() can select exactly this head's own tokens out of the one shared
        # tensor both the good and the bad head read from.
        self.register_buffer(
            "catalog_columns",
            torch.tensor(
                [catalog_index[name] for name in self.token_names], dtype=torch.long
            ),
            persistent=False,
        )
        self.token_embed = torch.nn.Linear(1, self.dim)
        self.token_identity = torch.nn.Parameter(
            torch.randn(self.token_count, self.dim) * (self.dim ** -0.5)
        )
        self.attention = make_self_attention(
            self.dim, config.HEADS, config, act_fn, batch_first=True
        )
        self.ln1 = torch.nn.LayerNorm(self.dim)
        self.ln2 = torch.nn.LayerNorm(self.dim)
        hidden = max(config.m * self.dim, self.dim)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(self.dim, hidden),
            act_fn or torch.nn.LeakyReLU(),
            torch.nn.Linear(hidden, self.dim),
        )

        # Token-axis reduction: pool_type, the same flag PairDescriptorHead's own
        # reduction (and every other pooling site in this project) answers to -- see
        # that class's __init__ for the full rationale. No --pair_descriptor_flatten
        # equivalent here (not requested; every head is pool_type-reduced to one
        # vector before the two heads are combined the same way, see final_layer.py).
        self.pool_type = getattr(config, "pool_type", "mean")
        if self.pool_type == "gem":
            # Deferred import: architecture.final_layer imports this module, so
            # importing GeMPool from there at module load time would be circular --
            # see PairDescriptorHead's own identical comment.
            from architecture.final_layer import GeMPool

            self.gem_pool = GeMPool()
            self.output_dim = self.dim
        else:
            self._pool_fn = config.pool
            self.output_dim = 2 * self.dim if self.pool_type == "add_max" else self.dim

    def forward(self, descriptor_catalog_input):
        """descriptor_catalog_input: [batch, len(catalog_order)] (the shared,
        per-config column order __init__ was built with). Returns
        [batch, self.output_dim].
        """
        scalars = descriptor_catalog_input.index_select(1, self.catalog_columns)
        tokens = self.token_embed(scalars.unsqueeze(-1)) + self.token_identity
        x = self.ln1(tokens)
        attended, _ = self.attention(x, x, x, need_weights=False)
        x = tokens + attended
        x = self.ln2(x)
        x = x + self.ffn(x)  # [batch, token_count, hiddim]

        # Same synthetic-PyG-batch-index trick PairDescriptorHead's own reduction
        # uses: every sample owns exactly token_count consecutive rows.
        batch_size = x.shape[0]
        flat = x.reshape(batch_size * self.token_count, self.dim)
        index = torch.arange(batch_size, device=x.device).repeat_interleave(self.token_count)
        if self.pool_type == "gem":
            return self.gem_pool(flat, index)
        return self._pool_fn(flat, index)


def pool_descriptor_head_outputs(vectors, pool_type, pool_fn, gem_pool=None):
    """[batch, dim] x N (one per NamedDescriptorHead, e.g. good/bad) -> one [batch,
    dim] vector, reduced with pool_type over the N heads treated as a token axis --
    the SAME mechanism (and the SAME flag) each head already uses internally to
    reduce its own tokens to one vector. `gem_pool` must be a persistent submodule
    (its exponent is learned) when pool_type == "gem" -- see Final_Layer.__init__,
    which builds one under --two_pair_descriptors_paths the same way it builds
    lip_gem_pool/prot_gem_pool.
    """
    stacked = torch.stack(vectors, dim=1)  # [batch, N, dim]
    batch_size, count, dim = stacked.shape
    flat = stacked.reshape(batch_size * count, dim)
    index = torch.arange(batch_size, device=stacked.device).repeat_interleave(count)
    if pool_type == "gem":
        return gem_pool(flat, index)
    return pool_fn(flat, index)
