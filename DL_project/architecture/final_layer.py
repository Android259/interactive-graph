import torch
import torch.nn.functional as F
import torch_geometric
from torch_geometric.utils import softmax as scatter_softmax

try:
    from .mlp_utils import (
        make_activation, make_final_dropout, make_extra_hidden_layer,
        insert_hidden_gate, insert_input_gate, insert_output_gate,
        mlp_hidden_dims, link_concrete_dropouts, build_ffn_with_residual,
    )
except ImportError:
    from mlp_utils import (
        make_activation, make_final_dropout, make_extra_hidden_layer,
        insert_hidden_gate, insert_input_gate, insert_output_gate,
        mlp_hidden_dims, link_concrete_dropouts, build_ffn_with_residual,
    )


class _GradientReversal(torch.autograd.Function):
    """Identity on the forward pass; scales the gradient by -lambda on the way back.

    Ganin & Lempitsky (2015). Placed between the encoder output and an adversary
    head, it makes a single loss.backward() train the adversary to predict well
    (its own params get the normal gradient) while pushing the encoder in the
    opposite direction, i.e. to make that representation *un*predictive.
    """

    @staticmethod
    def forward(ctx, x, lambda_):
        ctx.lambda_ = float(lambda_)
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.lambda_ * grad_output, None  # None: no grad for lambda_


def grad_reverse(x, lambda_=1.0):
    """Reverse-and-scale the gradient flowing back through x (forward is identity)."""
    return _GradientReversal.apply(x, lambda_)


class _GradientScale(torch.autograd.Function):
    """Identity forward; multiplies the gradient by a non-negative weight backward.

    The same trick as _GradientReversal without the sign flip. Used to hand the lipid
    branch a smaller learning step than the protein branch while leaving the function
    the model computes untouched -- unlike scaling the activations, which the following
    LayerNorm would undo, and unlike a lower learning rate, which would also slow the
    shared layers downstream of both branches.
    """

    @staticmethod
    def forward(ctx, x, weight):
        ctx.weight = float(weight)
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return ctx.weight * grad_output, None  # None: no grad for weight


def grad_scale(x, weight=1.0):
    """Scale the gradient flowing back through x (forward is identity)."""
    if weight == 1.0:
        return x
    return _GradientScale.apply(x, weight)


# Width of the one-hot family vector the dataloader attaches as prot.family
# (New_dataloader.fam_enc). The family DANN head predicts over exactly these.
PROTEIN_FAMILY_COUNT = 9


def family_dann_loss(features, family_onehot, labels, heads, class_conditional):
    """Cross-entropy of the family adversaries on already-reversed features.

    Lives here rather than in the training loop so the per-class routing sits next to
    the heads it selects. ``features`` must already have passed through grad_reverse:
    one backward then trains each head to name the family while pushing the encoder to
    make the family undecodable.

    With ``class_conditional`` the batch is split by binding label and each part scored
    by its own head, so what gets aligned across families is P(features | label, family).
    That is the distinction that matters on this dataset: the families differ in their
    positive rate by 16x (OSBP 1.3% to START 20%), and under that label shift aligning
    the raw P(features | family) provably raises the combined error (Zhao et al. 2019)
    because the only way to erase the family is to erase the specificity that defines it.
    Conditioning on the label removes that particular escape route.

    Returns a scalar; a class with no rows in the batch contributes nothing.
    """
    if family_onehot.sum(dim=1).min() <= 0:
        # argmax of an all-zero row silently returns 0, which would relabel the sample
        # as the first family instead of failing. The one-hot comes from a name lookup
        # (New_dataloader.fam_enc), so a miss means a family name drifted, not a data
        # point worth training on.
        raise ValueError(
            "family one-hot has a row with no family set; check New_dataloader.fam_enc "
            "covers every ProteinDomain value"
        )
    family_index = family_onehot.argmax(dim=1)
    if not class_conditional:
        return F.cross_entropy(heads[0](features), family_index)

    # Averaged over the classes actually present, not summed: summing would make the
    # conditional variant apply one CE per class where the unconditional one applies a
    # single CE, so the same dann_weight would mean twice the pressure and the
    # dann_class_conditional ablation would not be a controlled comparison. It would
    # also make the penalty depend on whether a batch happened to contain both classes.
    terms = []
    for class_value, head in enumerate(heads):
        mask = labels == class_value
        if not bool(mask.any()):
            continue
        terms.append(F.cross_entropy(head(features[mask]), family_index[mask]))
    if not terms:
        return features.new_zeros(())
    return torch.stack(terms).mean()


class GeMPool(torch.nn.Module):
    """Generalized-mean graph pooling with a learnable, sign-preserving exponent.

    At initialization p ~= 1 + eps, matching mean pooling; gradient descent can
    move p toward higher values to interpolate continuously toward max-like
    pooling instead of committing to one pool_type up front.
    """

    def __init__(self, init_p=0.0, eps=1e-6):
        super().__init__()
        self.raw_p = torch.nn.Parameter(torch.tensor(float(init_p)))
        self.eps = eps

    def forward(self, x, batch):
        p = F.elu(self.raw_p) + 1.0 + self.eps
        signed_power = torch.sign(x) * x.abs().clamp_min(self.eps).pow(p)
        pooled = torch_geometric.nn.global_mean_pool(signed_power, batch)
        return torch.sign(pooled) * pooled.abs().clamp_min(self.eps).pow(1.0 / p)


class AttentionPool(torch.nn.Module):
    """Learned-query attention pooling over a graph's nodes.

    Replaces the flat mean/GeM reduction with a content-weighted readout:
        out_g = sum_{i in g} softmax_i(w . x_i [+ pocket_bias * is_pocket_i]) * x_i
    A single learnable gate (equivalently one learned query) scores each node and a
    per-graph softmax turns the scores into weights, so pooling can emphasise the
    residues that matter instead of averaging everything equally. With pocket_bias a
    learnable scalar (init 1.0, matching the cross-attention pocket bias) is added to
    pocket residues' logits, giving the binding site an initial, trainable preference.
    """

    def __init__(self, dim, pocket_bias=False):
        super().__init__()
        self.gate = torch.nn.Linear(dim, 1)
        self.pocket_bias = torch.nn.Parameter(torch.ones(())) if pocket_bias else None

    def forward(self, x, batch, pocket=None):
        logit = self.gate(x).squeeze(-1)
        if self.pocket_bias is not None and pocket is not None:
            logit = logit + self.pocket_bias * pocket.to(logit.dtype)
        alpha = scatter_softmax(logit, batch)
        return torch_geometric.nn.global_add_pool(x * alpha.unsqueeze(-1), batch)


class ResidualAdversary(torch.nn.Module):
    """Adversary matched, layer for layer, to the CrossAttention block it must police.

    One side of that block is `x = ln1(x + attn(x, partner)); x = ln2(x + FFN(x))`.
    Attention cannot be reused here: it reads the *other* partner over a node sequence,
    while an adversary sees one pooled vector and must stay single-partner for its test
    to mean anything. So each of the two residual sub-blocks becomes an MLP instead --
    the first standing in for the attention, the second reusing the FFN itself -- and
    the two LayerNorms and both residual paths are kept as they are.

    The substitute is sized to the budget it replaces rather than to m: hidden width
    2 * dim puts 4 * dim^2 in its Linears, which is exactly what MultiheadAttention
    spends on Q/K/V/O. The whole adversary therefore matches the block it is meant to
    keep honest, instead of the 2-layer probe that used to lose to it by ~12x.
    """

    def __init__(self, dim, config, act_fn=None):
        super().__init__()
        self.attn_mlp = build_ffn_with_residual(dim, config, act_fn, hidden_dim=2 * dim)
        self.norm1 = torch.nn.LayerNorm(dim)
        self.ffn = build_ffn_with_residual(dim, config, act_fn)
        self.norm2 = torch.nn.LayerNorm(dim)
        self.head = torch.nn.Linear(dim, 2)

    def forward(self, x):
        x = self.norm1(x + self.attn_mlp(x))
        x = self.norm2(x + self.ffn(x))
        return self.head(x)


class Final_Layer(torch.nn.Module):
    def __init__(self, config, act_fn=None) -> None:
        """Initialize the pooled protein-lipid binary classifier."""
        super(Final_Layer, self).__init__()
        middim = config.hiddim
        lip_dim = config.hiddim
        prot_dim = config.hiddim
        final_m = config.m if config.final_m is None else config.final_m
        self.lip_dim = lip_dim
        self.prot_dim = prot_dim
        self.config = config
        enlarged, last = mlp_hidden_dims(self.config, "final", final_m * middim)
        # Attention pooling emits one vector per graph (multiplier 1), overriding the
        # pool_type width (add_max would otherwise double it).
        if self.config.attention_pooling:
            pool_output_multiplier = 1
        else:
            pool_output_multiplier = 2 if self.config.pool_type == "add_max" else 1
        pooled_lip_dim = pool_output_multiplier * lip_dim
        pooled_prot_dim = pool_output_multiplier * prot_dim
        # Fusion of the two pooled partners feeds the classifier MLP. The default
        # concatenation exposes each partner's pooled features to the MLP, which
        # lets it decide from one partner's identity alone (the lipid-identity
        # shortcut). Bilinear fusion replaces the concat with an interaction
        # vector lip^T W prot, so the discriminative signal is multiplicative in
        # both partners: a lipid-only (or protein-only) representation cannot
        # survive the product, forcing the decision to use protein-lipid matching.
        if self.config.bilinear_fusion:
            self.bilinear = torch.nn.Bilinear(pooled_lip_dim, pooled_prot_dim, middim)
            classifier_input_dim = middim
        else:
            classifier_input_dim = pooled_lip_dim + pooled_prot_dim

        if self.config.attention_pooling:
            # Learned-query attention pooling replaces the fixed reduction; the protein
            # pool optionally biases pocket residues (attention_pooling_pocket_bias).
            self.lip_attn_pool = AttentionPool(pooled_lip_dim)
            self.prot_attn_pool = AttentionPool(
                pooled_prot_dim, pocket_bias=self.config.attention_pooling_pocket_bias
            )
        elif self.config.pool_type == "gem":
            self.lip_gem_pool = GeMPool()
            self.prot_gem_pool = GeMPool()

        extra = make_extra_hidden_layer(
            enlarged, last, self.config, act_fn, make_final_dropout
        )

        binar_layers = [
            torch.nn.Linear(classifier_input_dim, enlarged),
            make_activation(self.config, act_fn),
            *make_final_dropout(self.config, enlarged),
        ]
        insert_hidden_gate(binar_layers, enlarged, self.config)
        binar_layers += [
            *extra,
            torch.nn.Linear(last, middim),
            make_activation(self.config, act_fn),
            *make_final_dropout(self.config, middim),
        ]
        insert_input_gate(binar_layers, classifier_input_dim, self.config)
        insert_output_gate(binar_layers, middim, self.config)
        binar_layers.append(torch.nn.Linear(middim, 2))
        link_concrete_dropouts(binar_layers)
        self.binar = torch.nn.Sequential(*binar_layers)

        # Adversarial anti-shortcut heads (Ganin-style gradient reversal): each
        # tries to predict the label from ONE partner's pooled PRE-cross-attention
        # representation alone (compute_adversary is called from the model forward
        # before cross-attention mixes in the counterpart). Behind a gradient-
        # reversal layer, this pushes that single-partner encoder to be individually
        # uninformative about the label, so the decision must come from the protein-
        # lipid interaction, not from one partner's identity. A 2-layer MLP is used
        # so the adversary is strong enough to catch non-linearly decodable leakage.
        self._adv = None
        if self.config.adversarial_grl:
            # Built only for the sides in use, so a disabled one cannot sit in the
            # parameter count without ever taking a gradient.
            if self.config.adv_lipid:
                self.lip_adversary = self._make_adversary(pooled_lip_dim, middim, act_fn)
            if self.config.adv_protein:
                self.prot_adversary = self._make_adversary(pooled_prot_dim, middim, act_fn)
            # Overwritten per epoch by the training loop when adv_lambda_ramp is set;
            # the constant keeps the module usable on its own.
            self.adv_lambda_now = self.config.adv_lambda

        self._dann_features = None
        if self.config.dann_family:
            # One head per class when class-conditional, so the reversal aligns
            # P(features | label, family) instead of P(features | family). Two heads is
            # the whole fix: this dataset's families differ in BOTH what they bind and
            # how often, and a single head cannot help but erase the second along with
            # the first.
            head_count = 2 if self.config.dann_class_conditional else 1
            self.family_adversaries = torch.nn.ModuleList(
                self._make_family_head(classifier_input_dim, middim, act_fn)
                for _ in range(head_count)
            )
            self.dann_lambda_now = self.config.dann_lambda

    def _make_family_head(self, in_dim, hidden_dim, act_fn):
        """Map the fused pair representation to logits over the 9 protein families."""
        return torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden_dim),
            make_activation(self.config, act_fn),
            torch.nn.Linear(hidden_dim, PROTEIN_FAMILY_COUNT),
        )

    def _make_adversary(self, in_dim, hidden_dim, act_fn):
        """Map one pooled partner to binary label logits, 2-layer or CA-shaped."""
        if self.config.adv_deep:
            return ResidualAdversary(in_dim, self.config, act_fn)
        return torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden_dim),
            make_activation(self.config, act_fn),
            torch.nn.Linear(hidden_dim, 2),
        )

    def _pool_partners(self, lip, prot, lip_batch, prot_batch, pool, prot_pocket=None):
        """Pool each partner's node features to one vector per sample."""
        if self.config.attention_pooling:
            return (
                self.lip_attn_pool(lip, lip_batch),
                self.prot_attn_pool(prot, prot_batch, prot_pocket),
            )
        if self.config.pool_type == "gem":
            return self.lip_gem_pool(lip, lip_batch), self.prot_gem_pool(prot, prot_batch)
        return pool(lip, lip_batch), pool(prot, prot_batch)

    def compute_adversary(self, lip, prot, lip_batch, prot_batch, pool, prot_pocket=None):
        """Run the per-partner adversaries on PRE-cross-attention representations.

        Invoked from the model forward BEFORE cross-attention, where each partner is
        still genuinely single-partner. Cross-attention injects the counterpart into
        each stream (its values ARE the other partner, added residually), so running
        the adversary on its output would penalise the interaction summary cross-
        attention builds rather than the single-partner identity shortcut we mean to
        suppress. Stashes (lip_logits, prot_logits) in _adv for the training loop;
        resets to None when GRL is off or in eval so no stale logits are read.
        """
        if not (self.config.adversarial_grl and self.training):
            self._adv = None
            return
        lip_outs, prot_outs = self._pool_partners(lip, prot, lip_batch, prot_batch, pool, prot_pocket)
        lam = self.adv_lambda_now
        # A side switched off yields None rather than a zeroed logit, so the training
        # loop adds no term for it and its head takes no gradient at all.
        self._adv = (
            self.lip_adversary(grad_reverse(lip_outs, lam))
            if self.config.adv_lipid
            else None,
            self.prot_adversary(grad_reverse(prot_outs, lam))
            if self.config.adv_protein
            else None,
        )

    def forward(self, lip, prot, lip_batch, prot_batch, pool, prot_pocket=None):
        """Pool both modalities by sample and return binary logits."""
        lip_outs, prot_outs = self._pool_partners(lip, prot, lip_batch, prot_batch, pool, prot_pocket)

        if getattr(self.config, "lipid_only", False):
            # Diagnostic shortcut ablation: hide the protein half from the
            # classifier so the decision must come from the lipid alone. Keeps
            # pooled_input_dim unchanged, so the MLP shapes are untouched.
            prot_outs = torch.zeros_like(prot_outs)
        elif getattr(self.config, "protein_only", False):
            # Mirror ablation: hide the lipid half instead.
            lip_outs = torch.zeros_like(lip_outs)

        if self.config.bilinear_fusion:
            common_out = self.bilinear(lip_outs, prot_outs)
        else:
            common_out = torch.cat([lip_outs, prot_outs], dim=1)

        # Family DANN reads the FUSED vector -- the one place the per-partner adversary
        # cannot reach, and where cross-attention deposits the family-specific
        # pocket/lipid pairing. Only the reversed features are stashed, not the family
        # logits: the class-conditional variant has to pick a head per row from the
        # labels, which live in the training loop, not here.
        if self.config.dann_family and self.training:
            self._dann_features = grad_reverse(common_out, self.dann_lambda_now)
        else:
            self._dann_features = None

        return self.binar(common_out)
