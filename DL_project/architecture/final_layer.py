import torch
import torch.nn.functional as F
import torch_geometric

from dataloader.descriptors import full_catalog_order, parse_descriptor_heads
from torch_geometric.utils import softmax as scatter_softmax
from torch_geometric.utils import to_dense_batch

from .mlp_utils import (
    make_activation, make_final_dropout, make_extra_hidden_layer,
    insert_hidden_gate, insert_input_gate, insert_output_gate,
    mlp_hidden_dims, link_concrete_dropouts, build_ffn_with_residual,
)
from .named_descriptor_head import NamedDescriptorHead, pool_descriptor_head_outputs
from .descriptor_mlp_head import DescriptorMLPHead


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


# Width of the one-hot family vector the dataloader attaches as prot.family
# (Dataloader.fam_enc). The family DANN head predicts over exactly these.
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
        # (Dataloader.fam_enc), so a miss means a family name drifted, not a data
        # point worth training on.
        raise ValueError(
            "family one-hot has a row with no family set; check Dataloader.fam_enc "
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


def chem_adversary_loss(features, frozen_prior, head):
    """MSE of the chemistry adversary on already-reversed features.

    Mirrors family_dann_loss's contract: `features` must already have passed through
    grad_reverse. MSE rather than cross-entropy because the target is a continuous
    score, not a class -- there is no head-per-class analogue of
    dann_class_conditional needed here, because the target is not the label (nothing
    about it inverts in meaning across families the way P(bind | lipid class) does for
    family identity, files/history/geometric_edge.md "Почему family-DANN...").

    `frozen_prior` is whatever Dataloader attached under --chem_prior and/or
    --pocket_compat_prior -- the SAME combined value added to the logit in forward(),
    not s_chem specifically. Both are added outside common_out, so decorrelating
    common_out from either costs the task loss nothing it needed (files/
    pocket_lipid_compatibility.md); with --chem_prior alone this is byte-identical to
    regressing on s_chem, since the combination is then a single term.
    """
    prediction = head(features).squeeze(-1)
    return F.mse_loss(prediction, frozen_prior)


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


class SlicedWassersteinPool(torch.nn.Module):
    """Pool a graph's nodes by the SHAPE of their distribution, not by their average.

    Why this exists here. Mean pooling answers one question -- "what is the average
    node" -- and on this dataset every protein answers it almost identically: the
    median ESM3 cosine between the 35 proteins is 0.974 while the median similarity of
    their binding profiles is 0.000 (files/results/signal_state.md 4.3). Averaging 300-700
    residue vectors is a lossy summary, and what it keeps is exactly the part that does
    not distinguish these proteins.

    What this does instead. A graph's nodes are treated as a sample from a distribution
    over R^dim. That distribution is compared against M learned reference points by
    1-D optimal transport along L learned directions:

        1. project every node and every reference point onto direction l;
        2. sort both sides -- in one dimension the optimal-transport plan between two
           point sets IS the sort, so the k-th smallest node projection is matched to
           the k-th smallest reference projection (the Monge coupling);
        3. record the displacement, i.e. how far this graph's matched quantile sits
           from that reference point.

    Node counts differ between graphs, so the sorted projections are resampled to M
    quantiles first; that is what makes a 300-residue protein and a 700-residue one
    comparable without averaging either. The result is M x L numbers describing the
    whole distribution -- its spread, its skew, where its tails sit relative to the
    references -- where mean pooling produced one number per dimension.

    Naderializadeh et al., "Pooling by Sliced-Wasserstein Embedding" (NeurIPS 2021);
    applied to residue-level protein language model embeddings for drug-target tasks in
    Bioinformatics Advances 5(1) vbaf060 (2025), where it beats average pooling across
    model sizes, lets a smaller PLM match an average-pooled larger one, and gains more
    the longer the chain.

    A final linear map brings M*L back to `dim`, so this is a drop-in for mean / GeM /
    attention pooling and nothing downstream changes width. With `freeze_reference` the
    reference points keep their random init and only the directions and that map are
    learned -- the paper's cheap "SWE_Simple" variant, which matters here because the
    protein axis has 21-33 independent examples and every learned parameter is spent
    against that.
    """

    def __init__(self, dim, reference_points=32, slices=None, freeze_reference=False):
        super().__init__()
        self.slices = int(slices or dim)
        self.reference_points = int(reference_points)
        # Normalised to unit length in forward, so the directions' scale is not a free
        # parameter competing with the projection that follows them.
        self.slicer = torch.nn.Parameter(torch.randn(dim, self.slices) / (dim ** 0.5))
        self.reference = torch.nn.Parameter(
            torch.randn(self.reference_points, dim), requires_grad=not freeze_reference
        )
        self.project = torch.nn.Linear(self.reference_points * self.slices, dim)

    def forward(self, x, batch):
        theta = F.normalize(self.slicer, dim=0)
        dense, mask = to_dense_batch(x, batch)
        projected = dense @ theta
        # Padding rows must not win a sort position. Pushed above every real value they
        # land past the end of each graph's own count, and the quantile lookup below --
        # which indexes strictly inside that count -- never reaches them.
        projected = projected.masked_fill(
            ~mask.unsqueeze(-1), torch.finfo(projected.dtype).max
        )
        ordered, _ = projected.sort(dim=1)

        counts = mask.sum(dim=1).clamp(min=1)
        steps = torch.arange(self.reference_points, device=x.device, dtype=ordered.dtype)
        # Midpoints of M equal bins of the empirical quantile function, linearly
        # interpolated between order statistics: the standard resampling of a sample of
        # n points onto M, and what makes graphs of different size comparable.
        position = ((steps + 0.5) / self.reference_points).unsqueeze(0) * counts.unsqueeze(1)
        last = (counts - 1).unsqueeze(1)
        lower = torch.minimum(position.floor().long().clamp(min=0), last)
        upper = torch.minimum(lower + 1, last)
        weight = (position - lower.to(position.dtype)).clamp(0.0, 1.0).unsqueeze(-1)
        index_shape = (-1, -1, self.slices)
        at_lower = ordered.gather(1, lower.unsqueeze(-1).expand(*index_shape))
        at_upper = ordered.gather(1, upper.unsqueeze(-1).expand(*index_shape))
        resampled = at_lower + weight * (at_upper - at_lower)

        reference = self.reference @ theta
        order = reference.argsort(dim=0)
        # Scatter the sorted quantiles back onto the reference points they were matched
        # to. Leaving them in sorted order would work too, but then a reference point
        # that training moves past its neighbour would change which output slot -- and
        # so which weight of `project` -- it feeds, and the map would be chasing a
        # permutation that keeps moving.
        coupled = torch.zeros_like(resampled)
        coupled.scatter_(
            1, order.unsqueeze(0).expand(resampled.shape[0], -1, -1), resampled
        )
        return self.project((coupled - reference.unsqueeze(0)).flatten(1))


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
        self.config = config

        if config.descriptors_head or config.descriptor_mlp:
            # Sufficiency tests (ModelConfig docstring on --descriptor_heads): nothing but
            # the descriptor path and a small classifier on its output. No pooling/
            # bilinear/adversary/DANN/chem-prior machinery -- none of it applies
            # (validate() rejects the combinations that would need it), and
            # InteractionClassification never builds protein1/lipid1/cross_attention1
            # under these flags, so forward() must not read anything else either.
            heads = parse_descriptor_heads(config.descriptor_heads)
            catalog_order = full_catalog_order(config)
            if config.descriptor_mlp:
                # An ordinary feedforward network over the one head's tokens, with none
                # of NamedDescriptorHead's shared per-token Linear(1, dim) embedding --
                # see files/results/descriptors_head_bottleneck.md for why that
                # embedding was suspected of bottlenecking the self-attention head.
                self.descriptor_mlp_head = DescriptorMLPHead(
                    config, heads[0], catalog_order, act_fn
                )
                head_dim = self.descriptor_mlp_head.output_dim
            else:
                head_dim = self._build_descriptor_heads(heads, catalog_order, act_fn)
            self.binar = torch.nn.Sequential(
                torch.nn.Linear(head_dim, config.hiddim),
                make_activation(config, act_fn),
                *make_final_dropout(config, config.hiddim),
                torch.nn.Linear(config.hiddim, 2),
            )
            self._adv = None
            self._pooled_partners = None
            self._dann_features = None
            self._chem_features = None
            return

        middim = config.hiddim
        lip_dim = config.hiddim
        prot_dim = config.hiddim
        final_m = config.m if config.final_m is None else config.final_m
        self.lip_dim = lip_dim
        self.prot_dim = prot_dim
        enlarged, last = mlp_hidden_dims(self.config, "final", final_m * middim)
        # Attention and sliced-Wasserstein pooling each emit one vector per graph
        # (multiplier 1), overriding the pool_type width (add_max would otherwise
        # double it).
        if self.config.attention_pooling or self.config.swe_pooling:
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
            # --bilinear_pooled_norm: LayerNorm on lip_outs/prot_outs right before the
            # product, in forward() below. The LayerNorms inside CrossAttention
            # normalise each NODE before pooling; pool_type="add" (the default) then
            # sums a different number of nodes per sample (lipid atom count, pocket
            # residue count both vary), so the pooled vector's magnitude still varies
            # sample-to-sample no matter how well-normalised the summands were -- this
            # catches that second, separate source of scale.
            if self.config.bilinear_pooled_norm:
                self.lip_pool_norm = torch.nn.LayerNorm(pooled_lip_dim)
                self.prot_pool_norm = torch.nn.LayerNorm(pooled_prot_dim)
        else:
            classifier_input_dim = pooled_lip_dim + pooled_prot_dim
        # Extra columns concatenated into common_out in forward() are added to
        # classifier_input_dim here, before every head that reads it (binar,
        # family_adversaries, chem_head) is built, so all of them size correctly for
        # the wider vector without a second special case each.

        # --node_bilinear_fusion (training/read_configuration.py, architecture/
        # cross_attention.py): CrossAttention stashes one interaction vector per graph
        # pair -- a genuine elementwise/Hadamard fusion of a lipid node's own content
        # and a protein node's own content (ForcedInteraction's signed_sqrt(proj_a(lip)
        # * proj_b(prot)) recipe, architecture/forced_interaction.py), summed
        # over every lipid/protein node pair the cross-attention already scores,
        # BEFORE either side is pooled. Concatenated into common_out just below -- but
        # unlike the descriptor heads this is NOT rejected alongside
        # --bilinear_fusion (ModelConfig.validate): it is
        # already a bottlenecked multiplicative quantity in its own right, so stacking
        # it next to the pool-level bilinear product adds a second, independent
        # bilinear channel rather than reopening the single-partner shortcut
        # --bilinear_fusion exists to close. Width is lip_dim == prot_dim (both
        # config.hiddim; see CrossAttention.__init__ for why the two always match).
        self.node_bilinear_fusion = bool(getattr(self.config, "node_bilinear_fusion", False))
        if self.node_bilinear_fusion:
            classifier_input_dim += lip_dim

        # --descriptor_heads without a sufficiency-test flag: the heads' vector is
        # concatenated into common_out and rejected in combination with bilinear_fusion
        # (ModelConfig.validate). Width is the heads' output_dim, not a hardcoded hiddim -- see _build_descriptor_heads for
        # when pool_type widens it.
        self.descriptor_head = None
        if self.config.descriptor_heads:
            classifier_input_dim += self._build_descriptor_heads(
                parse_descriptor_heads(self.config.descriptor_heads),
                full_catalog_order(self.config), act_fn,
            )

        if self.config.attention_pooling:
            # Learned-query attention pooling replaces the fixed reduction; the protein
            # pool optionally biases pocket residues (attention_pooling_pocket_bias).
            self.lip_attn_pool = AttentionPool(pooled_lip_dim)
            self.prot_attn_pool = AttentionPool(
                pooled_prot_dim, pocket_bias=self.config.attention_pooling_pocket_bias
            )
        elif self.config.swe_pooling:
            # Sized per partner: the lipid graph has tens of nodes and the protein
            # hundreds, but the reference count is what the pooling reads them onto and
            # a lipid with fewer nodes than reference points just resamples its own
            # quantile function more finely, which is well defined.
            self.lip_swe_pool = SlicedWassersteinPool(
                pooled_lip_dim,
                reference_points=self.config.swe_reference_points,
                freeze_reference=self.config.swe_freeze_reference,
            )
            self.prot_swe_pool = SlicedWassersteinPool(
                pooled_prot_dim,
                reference_points=self.config.swe_reference_points,
                freeze_reference=self.config.swe_freeze_reference,
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

        # Filled by forward() under save_dynamics so the training loop can measure the
        # two pooled halves that reach the classifier without re-deriving the pooling.
        self._pooled_partners = None

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

        # Frozen prior (files/history/geometric_edge.md; files/
        # pocket_lipid_compatibility.md): score = frozen_prior + the ordinary logit.
        # frozen_prior is attached per row by Dataloader under --chem_prior and/or
        # --pocket_compat_prior -- whichever are on -- and it already carries its own
        # calibration, fit JOINTLY across whichever terms are active
        # (fit_prior_calibration) on TRAIN LABELS ONLY, before this network exists, and
        # frozen (see that function's docstring for why it is not a torch.nn.Parameter
        # trained jointly with the rest of the model: a scalar and a whole encoder
        # competing by gradient descent for the same variance is underdetermined, and
        # this project's own measurements are the evidence that this network takes
        # whichever shortcut is available rather than the "correct" one). There is
        # therefore nothing to initialise here; the value read at forward() time is
        # already in logit units, and it is the SAME value whether it came from
        # chemistry alone, compatibility alone, or a joint fit of both.
        if self.config.chem_prior or self.config.pocket_compat_prior:
            if self.config.chem_adversary:
                # Regression head on the FUSED representation, same hook dann_family
                # uses (common_out, the one place the per-partner adversary at
                # compute_adversary cannot reach). Predicts frozen_prior, not the
                # label: the label is what the task loss already wants common_out to
                # predict, and an adversary against it would fight that loss over
                # genuinely shared, label-relevant variance. frozen_prior is
                # different -- it is added to the score OUTSIDE this representation
                # (see forward), so the task loss has no need for common_out to carry
                # a copy of it, and decorrelating the two costs the task nothing it
                # was using.
                self.chem_head = torch.nn.Sequential(
                    torch.nn.Linear(classifier_input_dim, middim),
                    make_activation(self.config, act_fn),
                    torch.nn.Linear(middim, 1),
                )
                self.chem_lambda_now = self.config.chem_lambda

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
        if self.config.swe_pooling:
            return (
                self.lip_swe_pool(lip, lip_batch),
                self.prot_swe_pool(prot, prot_batch),
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

    def _build_descriptor_heads(self, heads, catalog_order, act_fn):
        """One NamedDescriptorHead per --descriptor_heads segment; returns the width of
        the vector they reduce to.

        The first head is `descriptor_head` and any others sit in
        `descriptor_extra_heads` (empty for one head, which adds no state_dict key), so
        a one-head checkpoint keeps the keys it was saved under. All heads are built
        against the SAME catalog_order, so they agree on where their tokens live in the
        one tensor they read. Several heads' vectors are reduced to one with
        pool_descriptor_head_outputs: the same pool_type reduction each head already
        uses internally on its own tokens, applied again over the head axis.
        """
        built = [
            NamedDescriptorHead(self.config, head, catalog_order, act_fn) for head in heads
        ]
        self.descriptor_head = built[0]
        self.descriptor_extra_heads = torch.nn.ModuleList(built[1:])
        head_dim = built[0].output_dim
        self.descriptor_combine_pool_type = getattr(self.config, "pool_type", "mean")
        if len(built) == 1:
            return head_dim
        if self.descriptor_combine_pool_type == "gem":
            self.descriptor_combine_gem_pool = GeMPool()
        # add_max concatenates add-pool and max-pool over the head axis, so it doubles
        # the width on TOP of whatever head_dim already is (itself doubled by add_max if
        # that is how EACH head reduced its own tokens -- one doubling per pooling step).
        return 2 * head_dim if self.descriptor_combine_pool_type == "add_max" else head_dim

    def _descriptor_vector(self, descriptor_catalog_input):
        """The descriptor heads' vector for a batch: [batch, width]."""
        if descriptor_catalog_input is None:
            raise ValueError(
                "descriptor_heads is set but forward() got no descriptor_catalog_input "
                "-- Dataloader and forward_args only attach it when the flag was set at "
                "data-load time too; check the flags match."
            )
        flat = descriptor_catalog_input.view(descriptor_catalog_input.shape[0], -1)
        vectors = [self.descriptor_head(flat)]
        vectors += [head(flat) for head in self.descriptor_extra_heads]
        if len(vectors) == 1:
            return vectors[0]
        return pool_descriptor_head_outputs(
            vectors,
            self.descriptor_combine_pool_type,
            self.config.pool,
            gem_pool=getattr(self, "descriptor_combine_gem_pool", None),
        )

    def forward(
        self, lip, prot, lip_batch, prot_batch, pool, prot_pocket=None,
        frozen_prior=None, descriptor_catalog_input=None,
        node_bilinear_input=None,
    ):
        """Pool both modalities by sample and return binary logits."""
        if self.config.descriptor_mlp:
            if descriptor_catalog_input is None:
                raise ValueError(
                    "descriptor_mlp is set but forward() got no descriptor_catalog_input "
                    "-- Dataloader and forward_args only attach it when "
                    "--descriptor_heads was set at data-load time too; check the flags "
                    "match."
                )
            flat = descriptor_catalog_input.view(descriptor_catalog_input.shape[0], -1)
            return self.binar(self.descriptor_mlp_head(flat))

        if self.config.descriptors_head:
            return self.binar(self._descriptor_vector(descriptor_catalog_input))

        lip_outs, prot_outs = self._pool_partners(lip, prot, lip_batch, prot_batch, pool, prot_pocket)

        # Stashed BEFORE the ablations below, which is what lets one diagnostic pass do
        # both jobs: zeroing a half changes only what the classifier reads, never the
        # pooling that produced it, so the halves measured during an ablated pass are
        # the ones the unablated model computes. Evaluation only, and detached, so no
        # graph is held alive between batches.
        self._pooled_partners = (
            (lip_outs.detach(), prot_outs.detach())
            if getattr(self.config, "save_dynamics", False) and not self.training
            else None
        )

        if getattr(self.config, "lipid_only", False):
            # Diagnostic shortcut ablation: hide the protein half from the
            # classifier so the decision must come from the lipid alone. Keeps
            # pooled_input_dim unchanged, so the MLP shapes are untouched.
            prot_outs = torch.zeros_like(prot_outs)
        elif getattr(self.config, "protein_only", False):
            # Mirror ablation: hide the lipid half instead.
            lip_outs = torch.zeros_like(lip_outs)

        if self.config.bilinear_fusion:
            if self.config.bilinear_pooled_norm:
                lip_outs = self.lip_pool_norm(lip_outs)
                prot_outs = self.prot_pool_norm(prot_outs)
            common_out = self.bilinear(lip_outs, prot_outs)
        else:
            common_out = torch.cat([lip_outs, prot_outs], dim=1)

        if self.node_bilinear_fusion:
            if node_bilinear_input is None:
                raise ValueError(
                    "node_bilinear_fusion is set but forward() got no "
                    "node_bilinear_input -- InteractionClassification only attaches "
                    "it when cross_attention ran with the flag on; check the two "
                    "match."
                )
            common_out = torch.cat([common_out, node_bilinear_input], dim=1)

        if self.descriptor_head is not None:
            common_out = torch.cat(
                [common_out, self._descriptor_vector(descriptor_catalog_input)], dim=1
            )

        # Family DANN reads the FUSED vector -- the one place the per-partner adversary
        # cannot reach, and where cross-attention deposits the family-specific
        # pocket/lipid pairing. Only the reversed features are stashed, not the family
        # logits: the class-conditional variant has to pick a head per row from the
        # labels, which live in the training loop, not here.
        if self.config.dann_family and self.training:
            self._dann_features = grad_reverse(common_out, self.dann_lambda_now)
        else:
            self._dann_features = None

        if self.config.chem_adversary and self.training:
            # Same representation dann_family reverses, different target: this one
            # predicts frozen_prior (chemistry, compatibility, or their joint fit --
            # whatever Dataloader combined), not family. See __init__ for why
            # targeting it here is safe rather than a fight with the task loss.
            self._chem_features = grad_reverse(common_out, self.chem_lambda_now)
        else:
            self._chem_features = None

        logits = self.binar(common_out)
        if self.config.chem_prior or self.config.pocket_compat_prior:
            if frozen_prior is None:
                raise ValueError(
                    "chem_prior/pocket_compat_prior is set but forward() got no "
                    "frozen_prior -- Dataloader only attaches it when the "
                    "matching flag was set at data-load time too; check the flags "
                    "match."
                )
            # Added to the class-1 logit only. Under 2-class softmax this is exactly
            # equivalent to splitting +-delta/2 across both logits (softmax is
            # shift-invariant to a constant added to every entry), so there is no
            # asymmetry hiding in this being the simpler of the two to write.
            prior_term = frozen_prior.view(-1)
            logits = logits + torch.stack(
                [torch.zeros_like(prior_term), prior_term], dim=1
            )
        return logits
