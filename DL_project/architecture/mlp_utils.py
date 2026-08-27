"""Reusable MLP building blocks and activation utilities."""
import math

import torch


class HardConcreteGate(torch.nn.Module):
    """L0 hard-concrete gate over `num_gates` groups (Louizos et al. 2018). https://openreview.net/pdf?id=H1Y8hhg0b 

    A multiplicative gate in [0, 1] per group; `penalty()` is the expected number
    of *active* gates (a differentiable L0 surrogate). Driving a gate to 0 lets the
    corresponding group (FFN unit, head, block) be pruned. Deterministic at eval.
    """

    def __init__(self, num_gates, dim=-1, init_mean=0.95,
                 temperature=2.0 / 3.0, gamma=-0.1, zeta=1.1):
        super().__init__()
        self.num_gates = int(num_gates)
        self.dim = dim
        self.temperature = float(temperature)
        self.gamma = float(gamma)
        self.zeta = float(zeta)
        init_mean = min(max(init_mean, 1e-3), 1 - 1e-3)
        init_log_alpha = math.log(init_mean) - math.log(1.0 - init_mean)
        self.log_alpha = torch.nn.Parameter(
            torch.full((self.num_gates,), init_log_alpha)
        )

    def _z(self):
        if self.training:
            u = torch.rand_like(self.log_alpha).clamp(1e-6, 1 - 1e-6)
            s = torch.sigmoid(
                (torch.log(u) - torch.log(1 - u) + self.log_alpha) / self.temperature
            )
        else:
            s = torch.sigmoid(self.log_alpha)
        return (s * (self.zeta - self.gamma) + self.gamma).clamp(0.0, 1.0)

    def _broadcast(self, z, x):
        shape = [1] * x.dim()
        shape[self.dim] = self.num_gates
        return z.view(shape)

    def forward(self, x):
        return x * self._broadcast(self._z(), x)

    def penalty(self):
        prob_active = torch.sigmoid(
            self.log_alpha - self.temperature * math.log(-self.gamma / self.zeta)
        )
        return prob_active.sum()

    @torch.no_grad()
    def gate_values(self):
        s = torch.sigmoid(self.log_alpha)
        return (s * (self.zeta - self.gamma) + self.gamma).clamp(0.0, 1.0)

    @torch.no_grad()
    def active_mask(self, threshold=1e-2):
        return self.gate_values() > threshold

    @torch.no_grad()
    def num_active(self, threshold=1e-2):
        return int(self.active_mask(threshold).sum())


class L1Gate(torch.nn.Module):
    """Network-Slimming-style gate: non-negative scale per group + L1 penalty."""

    def __init__(self, num_gates, dim=-1, init_value=1.0):
        super().__init__()
        self.num_gates = int(num_gates)
        self.dim = dim
        self.gamma = torch.nn.Parameter(torch.full((self.num_gates,), float(init_value)))

    def _broadcast(self, z, x):
        shape = [1] * x.dim()
        shape[self.dim] = self.num_gates
        return z.view(shape)

    def forward(self, x):
        return x * self._broadcast(self.gamma.clamp(min=0.0), x)

    def penalty(self):
        return self.gamma.clamp(min=0.0).sum()

    @torch.no_grad()
    def gate_values(self):
        return self.gamma.clamp(min=0.0)

    @torch.no_grad()
    def active_mask(self, threshold=1e-2):
        return self.gate_values() > threshold

    @torch.no_grad()
    def num_active(self, threshold=1e-2):
        return int(self.active_mask(threshold).sum())


class ConcreteDropout(torch.nn.Module):
    """Per-layer Concrete Dropout, producer-attributed. https://arxiv.org/pdf/1705.07832

    One instance per dropout site, each with its own learnable rate ``p = sigmoid(logit)``.
    ``reg()`` is the KL surrogate::

        weight_reg * ||W||^2 / (1 - p)  +  dropout_reg * K * (p log p + (1-p) log(1-p))

    i.e. ``weight_reg*||W||^2/(1-p) - dropout_reg*K*H(p)``. The entropy term pulls p up
    (toward 0.5); the weight term and the task loss pull it down, so p settles at a
    data-driven value instead of collapsing to 0. Canonically ``weight_reg = l^2/(tau*N)``
    and ``dropout_reg = 2/(tau*N)``.

    NOTE -- this is the *mirror* of Gal et al.'s derivation, not their literal formulation.
    They attribute the mask to the *consumer* (dropout on a layer's input, so the mask zeros
    *columns* of the downstream W, q(W) = M diag(z)). Here the mask is attributed to the
    *producer*: masking output unit i of ``y = W h + b`` zeros *row* i of the producing W,
    q(W) = diag(z) M -- an identical KL structure with ``K = out_features``. Producer
    attribution is used because it is well-defined at *every* site: the attribution runs
    upstream of the mask, so a downstream residual add / LayerNorm (which mixes features and
    would break the consumer-side equivalence) is irrelevant. It also avoids double-counting
    -- each Linear produces exactly one dropout site, whereas consumer attribution would put
    the middle Linear in two KL terms at once. Elementwise activations between the Linear and
    the mask are transparent here because ``act(0) = 0`` for LeakyReLU/GELU/PReLU.

    The producing Linear is wired by :func:`link_concrete_dropouts`; a site with no Linear
    upstream keeps the entropy term only, with ``K`` falling back to ``num_units``.

    Learned on the TRAIN objective: a first-order bilevel/val objective would collapse p to
    0, since on fixed weights dropout only injects noise. Inverted-dropout scaling at train
    time; identity at eval like ``nn.Dropout``, so a discovered ``p`` can later be baked
    into a plain ``nn.Dropout(p)``.
    """

    def __init__(self, num_units, init_p=0.1, weight_reg=0.0, dropout_reg=0.0,
                 temperature=0.1, eps=1e-7):
        super().__init__()
        self.num_units = int(num_units)
        init_p = min(max(float(init_p), 1e-2), 0.5)
        self.logit = torch.nn.Parameter(
            torch.tensor(math.log(init_p) - math.log(1.0 - init_p))
        )
        self.weight_reg = float(weight_reg)
        self.dropout_reg = float(dropout_reg)
        self.temperature = float(temperature)
        self.eps = eps
        # Held in a list so the producing Linear (already registered by its Sequential) is
        # not registered a second time as a submodule of this dropout.
        self._producer = []

    def set_producer(self, linear):
        """Attach the upstream Linear whose output units this dropout masks."""
        self._producer = [linear]

    @property
    def producer_linear(self):
        return self._producer[0] if self._producer else None

    def p(self):
        return torch.sigmoid(self.logit)

    def forward(self, x):
        if not self.training:
            return x
        p = torch.sigmoid(self.logit)
        u = torch.rand_like(x).clamp(self.eps, 1 - self.eps)
        drop = torch.sigmoid(
            (
                torch.log(p + self.eps) - torch.log1p(-p + self.eps)
                + torch.log(u) - torch.log1p(-u)
            )
            / self.temperature
        )
        keep = 1.0 - drop
        return x * keep / (1.0 - p).clamp_min(self.eps)

    def reg(self):
        """KL surrogate over the producing layer's rows (see class docstring)."""
        p = torch.sigmoid(self.logit)
        entropy_term = p * torch.log(p + self.eps) + (1.0 - p) * torch.log1p(-p + self.eps)
        linear = self.producer_linear
        num_units = linear.out_features if linear is not None else self.num_units
        total = self.dropout_reg * num_units * entropy_term
        if linear is not None and self.weight_reg > 0.0:
            total = total + self.weight_reg * (linear.weight ** 2).sum() / (
                1.0 - p
            ).clamp_min(self.eps)
        return total


def link_concrete_dropouts(layers):
    """Attach every ConcreteDropout in `layers` to the preceding Linear that produced it.

    Masking output unit i of that Linear zeros row i of its weight, which is what the
    site's regularizer is over, so its ``W``/``out_features`` define the term. The search
    runs backwards and skips elementwise layers (activations, gates), which are transparent
    to the attribution. Sites with no upstream Linear keep an entropy-only term.
    """
    for index, layer in enumerate(layers):
        if not isinstance(layer, ConcreteDropout):
            continue
        for candidate in reversed(layers[:index]):
            if isinstance(candidate, torch.nn.Linear):
                layer.set_producer(candidate)
                break
    return layers


class GatedResidual(torch.nn.Module):
    """Residual wrapper with a scalar gate: ``x -> x + gate * sub(x)``.

    Used to make a whole sub-block (a third MLP layer, a GAT/FFN block) prunable:
    driving its scalar gate to 0 removes the block while the identity path stays,
    so the block count itself becomes learnable. Requires sub(x) to match x's shape.
    """

    def __init__(self, sub, gate):
        super().__init__()
        self.sub = sub
        self.gate = gate

    def forward(self, x):
        return x + self.gate(self.sub(x))


class HeadGate(torch.nn.Module):
    """Per-head gate on a concatenated multi-head tensor ``(..., heads*per_head_dim)``.

    Each of the ``heads`` blocks of width ``per_head_dim`` gets one scalar gate;
    driving a head's gate to 0 prunes that attention head, so #heads is learnable.
    """

    def __init__(self, heads, per_head_dim, config):
        super().__init__()
        self.heads = int(heads)
        self.per_head_dim = int(per_head_dim)
        self.gate = make_gate(self.heads, config, dim=-2)

    def forward(self, x):
        if self.gate is None:
            return x
        shape = x.shape
        x = x.view(*shape[:-1], self.heads, self.per_head_dim)
        x = self.gate(x)
        return x.reshape(shape)


def make_gate(num_gates, config, dim=-1):
    """Build the configured gate type, or None when no gating mode is enabled.

    Gates are produced when structured_sparsity (explicit gate placements),
    gate_all_mlp_hidden (blanket per-unit width gates on internal MLP layers) or
    gate_all_mlp_layers (the same plus the block input/output boundaries) is on; all
    reuse the same sparsity_mode (l0 hard-concrete / l1 scale) machinery.
    """
    if not (
        getattr(config, "structured_sparsity", False)
        or getattr(config, "gate_all_mlp_hidden", False)
        or getattr(config, "gate_all_mlp_layers", False)
    ):
        return None
    if str(getattr(config, "sparsity_mode", "l0")).lower() == "l1":
        return L1Gate(num_gates, dim=dim)
    return HardConcreteGate(num_gates, dim=dim)


def insert_hidden_gate(layers, num_units, config):
    """Append a per-unit width gate over an internal MLP hidden layer (learns its width).

    Enabled by gate_all_mlp_hidden (and by gate_all_mlp_layers, which additionally gates
    the block boundaries). Unlike insert_ffn_unit_gate (which is tied to the explicit
    sparsity_gate_ffn placement), this is the blanket gate applied at every internal MLP
    hidden layer across the architecture.
    """
    if getattr(config, "gate_all_mlp_hidden", False) or getattr(
        config, "gate_all_mlp_layers", False
    ):
        gate = make_gate(num_units, config, dim=-1)
        if gate is not None:
            layers.append(gate)
    return layers


def mlp_hidden_dims(config, site, default_hidden):
    """Return the (first hidden, pre-output) widths of one gated MLP block.

    Both default to ``m * dim``; ``--mlp_widths`` overrides them per block, which is how
    widths discovered by a gate/bilevel run are baked into a clean production run. The
    second value is the third layer's width (it feeds the block's output Linear) and
    defaults to the first, so a block stays rectangular unless asked otherwise.
    """
    widths = getattr(config, "mlp_widths", None) or {}
    hidden = int(widths.get(site, default_hidden)) if site else int(default_hidden)
    if not getattr(config, "third_layers_in_mlps", False):
        return hidden, hidden
    if site and f"{site}_third" in widths:
        return hidden, int(widths[f"{site}_third"])
    return hidden, hidden


def insert_input_gate(layers, num_units, config):
    """Prepend a per-unit gate over an MLP block's input tensor.

    Enabled by gate_all_mlp_layers only: together with insert_hidden_gate and
    insert_output_gate it puts one gate on every representation boundary of the block
    (input, each hidden, output), which is the layout the discovery runs on the cluster
    used (gate indices 0/4/8/12 inside the block's Sequential).

    Note this gate can prune a residual branch's input, which removes the whole branch
    at once and leaves its interior without gradient; keep that in mind when reading the
    discovered widths.
    """
    if getattr(config, "gate_all_mlp_layers", False):
        gate = make_gate(num_units, config, dim=-1)
        if gate is not None:
            layers.insert(0, gate)
    return layers


def insert_output_gate(layers, num_units, config):
    """Append a per-unit gate over an MLP block's output tensor (gate_all_mlp_layers)."""
    if getattr(config, "gate_all_mlp_layers", False):
        gate = make_gate(num_units, config, dim=-1)
        if gate is not None:
            layers.append(gate)
    return layers


def collect_sparsity_penalty(model):
    """Sum penalty() over every gate in `model`. Returns a scalar tensor."""
    total = None
    for module in model.modules():
        if isinstance(module, (HardConcreteGate, L1Gate)):
            term = module.penalty()
            total = term if total is None else total + term
    return total if total is not None else torch.zeros(())


def collect_gate_parameters(model):
    """Return the learnable parameters of every width/structure gate in `model`.

    These are the bilevel lambda parameters (optimized on the validation split); the
    rest of the model is theta (optimized on train). `model.modules()` dedups shared
    modules, so each gate's params are returned once.
    """
    params = []
    for module in model.modules():
        if isinstance(module, (HardConcreteGate, L1Gate)):
            params.extend(module.parameters())
    return params


def collect_concrete_dropout_reg(model):
    """Sum reg() over the unique ConcreteDropout modules. Returns a scalar tensor.

    Added (scaled by concrete_dropout_reg) to the TRAIN loss so per-block dropout rates
    are learned without collapsing to zero.
    """
    total = None
    for module in model.modules():
        if isinstance(module, ConcreteDropout):
            term = module.reg()
            total = term if total is None else total + term
    return total if total is not None else torch.zeros(())


@torch.no_grad()
def export_surviving_structure(model, threshold=1e-2):
    """Per named gate: how many groups survived -> the pruned architecture."""
    report = {}
    for name, module in model.named_modules():
        if isinstance(module, (HardConcreteGate, L1Gate)):
            mask = module.active_mask(threshold)
            report[name] = {
                "active": int(mask.sum()),
                "total": int(module.num_gates),
                "kept_indices": mask.nonzero(as_tuple=True)[0].tolist(),
            }
    return report


def make_activation(config, act_fn=None):
    """Return the configured activation module."""
    if act_fn is not None:
        return act_fn
    return config.make_activation()


def _make_concrete_dropout(config, num_units, init_p):
    """Build a per-site ConcreteDropout wired with the configured regularizer coefficients."""
    return ConcreteDropout(
        num_units,
        init_p=init_p if init_p > 0.0 else 0.1,
        weight_reg=getattr(config, "concrete_dropout_weight_reg", 0.0),
        dropout_reg=getattr(config, "concrete_dropout_reg", 0.0),
    )


def make_dropout(config, num_units=None):
    """Return a dropout layer for the regular dropout rate, or empty list.

    When bilevel_dropout is on, each site gets its own learnable ConcreteDropout over
    ``num_units`` features instead of a fixed ``nn.Dropout``.
    """
    if getattr(config, "bilevel_dropout", False) and num_units is not None:
        return [_make_concrete_dropout(config, num_units, config.dropout)]
    return (
        [torch.nn.Dropout(config.dropout)]
        if config.dropout > 0.0
        else []
    )


def make_final_dropout(config, num_units=None):
    """Return a dropout layer for the final dropout rate, or empty list.

    Mirrors make_dropout, but initializes the learnable rate from final_dropout.
    """
    if getattr(config, "bilevel_dropout", False) and num_units is not None:
        return [_make_concrete_dropout(config, num_units, config.final_dropout)]
    return (
        [torch.nn.Dropout(config.final_dropout)]
        if config.final_dropout > 0.0
        else []
    )


def make_extra_hidden_layer(
    input_dim, output_dim, config, act_fn=None, dropout_fn=None
):
    """Return an extra hidden layer if third_layers_in_mlps is True, else empty list.

    When structured sparsity gates the third layer (and dims match), the layer is
    wrapped in a GatedResidual so its scalar gate can prune it back to a 2-layer MLP.
    """
    if not config.third_layers_in_mlps:
        return []

    if dropout_fn is None:
        dropout_fn = make_dropout

    layer = [
        torch.nn.Linear(input_dim, output_dim),
        make_activation(config, act_fn),
        *dropout_fn(config, output_dim),
    ]
    # Per-unit width gate on the extra layer's hidden output (learns its width). Placed
    # inside the sub-block so it composes with the scalar third-layer GatedResidual below.
    insert_hidden_gate(layer, output_dim, config)

    if (
        getattr(config, "structured_sparsity", False)
        and getattr(config, "sparsity_gate_third_layer", False)
        and input_dim == output_dim
    ):
        return [GatedResidual(torch.nn.Sequential(*layer), make_gate(1, config))]
    return layer


def insert_ffn_unit_gate(layers, enlarged, config):
    """Append a per-unit gate over the enlarged FFN units when configured (learns m).

    Tied to the explicit ``structured_sparsity`` + ``sparsity_gate_ffn`` placement, so it
    gates only the FFN blocks (attention / cross-attention feed-forwards), unlike the
    blanket ``insert_hidden_gate`` (``gate_all_mlp_hidden``) which gates every internal
    MLP hidden layer. Called from the inline FFN builders in self_attention.py and
    cross_attention.py."""
    if getattr(config, "structured_sparsity", False) and getattr(
        config, "sparsity_gate_ffn", False
    ):
        gate = make_gate(enlarged, config, dim=-1)
        if gate is not None:
            layers.append(gate)
    return layers


def build_mlp(input_dim, hidden_dim, output_dim, config, act_fn=None, use_final_dropout=False):
    """Build a standard MLP block: Linear → act → dropout → extra_hidden → Linear → act → dropout.

    Args:
        input_dim: Input dimension
        hidden_dim: Hidden layer dimension (enlarged)
        output_dim: Output dimension
        config: ModelConfig instance
        act_fn: Optional activation function override
        use_final_dropout: If True, use final_dropout instead of regular dropout
    """
    dropout_fn = make_final_dropout if use_final_dropout else make_dropout
    activation = make_activation(config, act_fn)
    extra = make_extra_hidden_layer(hidden_dim, hidden_dim, config, act_fn, dropout_fn)

    layers = [torch.nn.Linear(input_dim, hidden_dim), activation, *dropout_fn(config, hidden_dim)]
    insert_ffn_unit_gate(layers, hidden_dim, config)
    insert_hidden_gate(layers, hidden_dim, config)
    layers += [
        *extra,
        torch.nn.Linear(hidden_dim, output_dim),
        activation,
        *dropout_fn(config, output_dim),
    ]
    insert_input_gate(layers, input_dim, config)
    insert_output_gate(layers, output_dim, config)
    link_concrete_dropouts(layers)
    return torch.nn.Sequential(*layers)


def build_ffn_with_residual(dim, config, act_fn=None, use_final_dropout=False, hidden_dim=None):
    """Build a Feed-Forward Network block for attention (used in self-attention).

    Used as: x = x + FFN(x)

    ``hidden_dim`` overrides the usual ``m * dim`` width. It exists so a block can be
    sized to a parameter budget rather than to m: the adversary's attention-substitute
    passes 2 * dim, which makes the two Linears cost 4 * dim^2, the same budget as the
    Q/K/V/O projections of the MultiheadAttention it stands in for.
    """
    enlarged = config.m * dim if hidden_dim is None else int(hidden_dim)
    dropout_fn = make_final_dropout if use_final_dropout else make_dropout
    activation = make_activation(config, act_fn)
    extra = make_extra_hidden_layer(enlarged, enlarged, config, act_fn, dropout_fn)

    layers = [torch.nn.Linear(dim, enlarged), activation, *dropout_fn(config, enlarged)]
    insert_ffn_unit_gate(layers, enlarged, config)
    insert_hidden_gate(layers, enlarged, config)
    layers += [*extra, torch.nn.Linear(enlarged, dim), *dropout_fn(config, dim)]
    insert_input_gate(layers, dim, config)
    insert_output_gate(layers, dim, config)
    link_concrete_dropouts(layers)
    return torch.nn.Sequential(*layers)


class AttentionMLPSubstitute(torch.nn.Module):
    """torch.nn.MultiheadAttention(dim, heads)'s own call contract --
    forward(query, key, value, attn_mask=None, need_weights=True,
    key_padding_mask=None) -> (output, None) -- swapped in wherever
    --mlp_in_place_of_sa is set (see make_self_attention below).

    Reads only `query`: every self-attention call site in this project already
    passes query is key is value, so there is nothing a second/third argument would
    add. Applies a per-token MLP instead of cross-token attention -- there is no
    mixing across the token/node axis at all, which is the point: this ablates
    whether a site needs cross-token attention in the first place, not a cheaper
    approximation of it. Sized to the SAME parameter budget MultiheadAttention(dim,
    heads) spends on its Q/K/V/O projections (4*dim^2, via hidden_dim=2*dim) --
    ResidualAdversary (architecture/final_layer.py) already uses this exact
    budget-matching discipline, for the same reason (a fair substitute, not a
    smaller one).
    """

    def __init__(self, dim, config, act_fn=None):
        super().__init__()
        self.mlp = build_ffn_with_residual(dim, config, act_fn, hidden_dim=2 * dim)

    def forward(self, query, key=None, value=None, attn_mask=None, need_weights=True,
                key_padding_mask=None, **kwargs):
        return self.mlp(query), None


class NodeMLPSubstitute(torch.nn.Module):
    """--mlp_in_place_of_sa's substitute for architecture.geometric_transformer.
    RoPESelfAttention, whose own call contract is forward(x, batch, layout=None) ->
    [nodes, dim] rather than MultiheadAttention's (query, key, value) -- a separate
    class from AttentionMLPSubstitute only because the shape of the call differs;
    the substitute itself is identical (same budget-matched per-token MLP, `batch`/
    `layout` unused since an MLP has no node axis to pad or mask).
    """

    def __init__(self, dim, config, act_fn=None):
        super().__init__()
        self.mlp = build_ffn_with_residual(dim, config, act_fn, hidden_dim=2 * dim)

    def forward(self, x, batch=None, layout=None):
        return self.mlp(x)


def make_self_attention(dim, heads, config, act_fn=None, batch_first=False):
    """torch.nn.MultiheadAttention(dim, heads[, batch_first]), or -- under
    --mlp_in_place_of_sa -- AttentionMLPSubstitute(dim, config, act_fn), same call
    contract either way. One factory for every site in this project that builds a
    plain (non-RoPE) self-attention module, so --mlp_in_place_of_sa covers a new one
    automatically instead of needing its own if/else.
    """
    if getattr(config, "mlp_in_place_of_sa", False):
        return AttentionMLPSubstitute(dim, config, act_fn)
    return torch.nn.MultiheadAttention(dim, heads, batch_first=batch_first)


def make_optional_projection(in_dim, out_dim):
    """Return Identity if dims match, else Linear projection."""
    if in_dim == out_dim:
        return torch.nn.Identity()
    return torch.nn.Linear(in_dim, out_dim, bias=False)


def make_norm_layer(config, dim, use_graph_norm_flag):
    """Return GraphNorm or LayerNorm based on config flag.

    Args:
        config: ModelConfig instance
        dim: Dimension for the norm layer
        use_graph_norm_flag: Config flag name (e.g., 'protein_gat_graph_norm')
    """
    import torch_geometric

    if getattr(config, use_graph_norm_flag, False):
        return torch_geometric.nn.GraphNorm(dim)
    return torch.nn.LayerNorm(dim)


def apply_norm(norm_layer, x, batch=None, use_graph_norm=False):
    """Apply normalization layer, handling optional batch parameter for GraphNorm."""
    if use_graph_norm and batch is not None:
        return norm_layer(x, batch)
    return norm_layer(x)


def build_sequential_compression(input_dim, output_dim, config, act_fn=None, dims=None):
    """Build a multi-layer sequential compression (e.g., for PLM features).

    Args:
        input_dim: Input dimension (e.g., 1536 for PLM)
        output_dim: Final output dimension
        config: ModelConfig instance
        act_fn: Optional activation function override
        dims: Optional list of intermediate dimensions. If None, uses simple linear.
              Example: [512, 171, 57] for 1536 -> ... -> output_dim
    """
    gate_all = getattr(config, "gate_all_mlp_hidden", False) or getattr(
        config, "gate_all_mlp_layers", False
    )

    if dims is None or not dims:
        # Single Linear (e.g. 1536 -> plm_compression_dim). Its output feeds the GAT-input
        # concat, so it is a prunable intermediate: gate its output width when requested.
        if not gate_all:
            return torch.nn.Linear(input_dim, output_dim)
        layers = [torch.nn.Linear(input_dim, output_dim)]
        insert_hidden_gate(layers, output_dim, config)
        return torch.nn.Sequential(*layers)

    activation = make_activation(config, act_fn)
    layers = []

    # Build compression pipeline: input -> dim[0] -> dim[1] -> ... -> output
    current_dim = input_dim
    for next_dim in dims:
        layers.append(torch.nn.Linear(current_dim, next_dim))
        layers.append(activation)
        insert_hidden_gate(layers, next_dim, config)  # learn each compression width
        current_dim = next_dim

    # Final layer to output_dim (also a prunable intermediate feeding the concat).
    layers.append(torch.nn.Linear(current_dim, output_dim))
    insert_hidden_gate(layers, output_dim, config)
    return torch.nn.Sequential(*layers)
