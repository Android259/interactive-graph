import torch
import torch.nn.functional as F

from dataloader.pair_descriptors import parse_descriptor_list, split_names_by_side

from .mlp_utils import make_activation, make_final_dropout


class _ModalityMLP(torch.nn.Module):
    """One side's raw scalar descriptors -> one centered vector.

    Linear(n, hidden) -> act -> Linear(hidden, dim), then BatchNorm1d(affine=False).
    This is a TRAINABLE head, not a fixed input, so the classic regression-interaction
    trick of centering a raw feature on a single train-only precomputed constant does
    not apply here -- the head's own output distribution moves as its weights train.
    BatchNorm1d tracks a running mean/var over TRAIN batches and freezes it for eval
    (affine=False: no learned scale/shift after normalising, so nothing here can
    reintroduce the per-side offset centering is meant to remove) -- the standard tool
    for centering a non-stationary activation the way a frozen train statistic centers
    a raw one.
    """

    def __init__(self, n_inputs, hidden, dim, config, act_fn=None):
        super().__init__()
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(n_inputs, hidden),
            make_activation(config, act_fn),
            torch.nn.Linear(hidden, dim),
        )
        self.center = torch.nn.BatchNorm1d(dim, affine=False)

    def forward(self, x):
        return self.center(self.mlp(x))


def _make_probe(dim, act_fn=None):
    """A small 2-layer MLP probe, not a bare Linear(dim, 1).

    A single linear layer only detects LINEAR redundancy between its input and the
    interaction's output (see thematical_orthogonality_loss's HSIC penalty, which
    needs a probe expressive enough that failing to correlate with it is actually
    informative). One hidden layer is enough for a diagnostic probe -- it is not meant
    to compete with the interaction block itself, only to say "this side's own MLP
    output already predicts the label at least this well".
    """
    return torch.nn.Sequential(
        torch.nn.Linear(dim, dim),
        act_fn or torch.nn.LeakyReLU(),
        torch.nn.Linear(dim, 1),
    )


class ForcedInteraction(torch.nn.Module):
    """v_a, v_b (both [batch, dim]) -> one interaction vector, with NO path forward for
    v_a/v_b themselves -- only their low-rank bilinear product does.

    z = FFN(normalize(signed_sqrt(W_a . v_a) * (W_b . v_b))): each side is projected,
    multiplied elementwise (a low-rank stand-in for a full bilinear tensor v_a^T W
    v_b, the MLB design -- Kim et al., "Hadamard Product for Low-rank Bilinear
    Pooling", 2017), then signed-square-rooted and L2-normalised before the FFN. MLB's
    own paper reports slow, hyperparameter-sensitive convergence without this step: an
    elementwise product's scale moves multiplicatively with both inputs' norms and can
    collapse toward a near-constant, near-zero-variance output if the two projections
    drift out of alignment during training -- signed-sqrt + L2-norm (Lin et al.'s
    bilinear-CNN pooling, 2015; reused by MFB, Yu et al. 2017) is the standard fix,
    applied here to the product itself rather than to a whole outer-product matrix
    (there is no full bilinear tensor here to normalise, only its low-rank stand-in).

    There is no concatenation of v_a/v_b alongside the product for a downstream layer
    to read instead of it -- that skip is exactly what would let a classifier
    reconstruct one side's identity directly and ignore the product term.

    This alone does not prove the output cannot reconstruct one side's identity --
    see files/thematic_interaction_architecture.md's "known limitation": a fingerprint
    jointly correlated across both sides at once (present in v_a AND v_b together,
    absent from either alone) survives this structural constraint and the
    orthogonality penalty below unchanged, because it satisfies the exact same "not
    predictable from one side alone" criterion real synergy does. Neither mechanism
    can tell the two apart; only a pair-shuffling audit downstream can.

    When `orth_weight` is truthy, builds two 1-logit MLP probes (_make_probe) reading
    v_a.detach()/v_b.detach() -- see thematical_orthogonality_loss, which trains them
    and penalises this block's OWN output for depending (HSIC, not just linearly) on
    their (detached) predictions.
    """

    def __init__(self, dim, config, act_fn=None, orth_weight=0.0):
        super().__init__()
        self.proj_a = torch.nn.Linear(dim, dim)
        self.proj_b = torch.nn.Linear(dim, dim)
        hidden = max(config.m * dim, dim)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(dim, hidden),
            make_activation(config, act_fn),
            torch.nn.Linear(hidden, dim),
        )
        self.probe_a = _make_probe(dim, act_fn) if orth_weight else None
        self.probe_b = _make_probe(dim, act_fn) if orth_weight else None

    def forward(self, a, b):
        product = self.proj_a(a) * self.proj_b(b)
        product = torch.sign(product) * torch.sqrt(product.abs() + 1e-6)
        product = F.normalize(product, p=2, dim=-1)
        return self.ffn(product)


class ThematicDescriptorHead(torch.nn.Module):
    """--thematical_paths (training/read_configuration.py): two named descriptor
    groups (--geometric_descriptors, --chemical_descriptors), each split into its own
    lipid-side and protein-side tokens (dataloader.pair_descriptors.split_names_by_
    side) and run through one small MLP per side (_ModalityMLP), forced together with
    ForcedInteraction (product-only, no skip) into one group vector. The two group
    vectors are then combined the SAME way at a second level, so the final vector can
    only express what needs BOTH groups, and each group vector only what needs BOTH
    sides of it.

    See files/thematic_interaction_architecture.md for the design discussion, the
    known limitation (a fingerprint jointly correlated across both sides of an
    interaction survives it unchanged), and the risk/benefit writeup this class
    implements.
    """

    def __init__(self, config, geometric_names, chemical_names, catalog_order, act_fn=None):
        super().__init__()
        geom_tokens = parse_descriptor_list(geometric_names)
        chem_tokens = parse_descriptor_list(chemical_names)
        if not geom_tokens or not chem_tokens:
            raise ValueError(
                "thematical_paths needs both --geometric_descriptors and "
                "--chemical_descriptors to name at least one descriptor each"
            )
        geom_lip, geom_prot = split_names_by_side(geom_tokens)
        chem_lip, chem_prot = split_names_by_side(chem_tokens)
        for side_name, side_tokens in (
            ("geometric_descriptors lipid side", geom_lip),
            ("geometric_descriptors protein side", geom_prot),
            ("chemical_descriptors lipid side", chem_lip),
            ("chemical_descriptors protein side", chem_prot),
        ):
            if not side_tokens:
                raise ValueError(
                    f"{side_name} is empty -- a forced interaction needs at least one "
                    "descriptor on each side of each group"
                )

        dim = config.hiddim
        hidden = max(config.m * dim, dim)
        orth_weight = getattr(config, "thematical_orth_weight", 0.0)
        catalog_index = {name: position for position, name in enumerate(catalog_order)}

        def register_columns(attr_name, tokens):
            self.register_buffer(
                attr_name,
                torch.tensor([catalog_index[name] for name in tokens], dtype=torch.long),
                persistent=False,
            )

        register_columns("geom_lip_columns", geom_lip)
        register_columns("geom_prot_columns", geom_prot)
        register_columns("chem_lip_columns", chem_lip)
        register_columns("chem_prot_columns", chem_prot)

        self.geom_lip_mlp = _ModalityMLP(len(geom_lip), hidden, dim, config, act_fn)
        self.geom_prot_mlp = _ModalityMLP(len(geom_prot), hidden, dim, config, act_fn)
        self.chem_lip_mlp = _ModalityMLP(len(chem_lip), hidden, dim, config, act_fn)
        self.chem_prot_mlp = _ModalityMLP(len(chem_prot), hidden, dim, config, act_fn)

        self.geom_interaction = ForcedInteraction(dim, config, act_fn, orth_weight)
        self.chem_interaction = ForcedInteraction(dim, config, act_fn, orth_weight)
        self.group_interaction = ForcedInteraction(dim, config, act_fn, orth_weight)

        self.output_dim = dim
        self.orth_weight = orth_weight
        self._orth_stash = None

    def forward(self, descriptor_catalog_input):
        """descriptor_catalog_input: [batch, len(catalog_order)] (the shared column
        order this head was built with -- see ThematicDescriptorHead.__init__).
        Returns [batch, self.output_dim].
        """
        geom_lip = self.geom_lip_mlp(
            descriptor_catalog_input.index_select(1, self.geom_lip_columns)
        )
        geom_prot = self.geom_prot_mlp(
            descriptor_catalog_input.index_select(1, self.geom_prot_columns)
        )
        chem_lip = self.chem_lip_mlp(
            descriptor_catalog_input.index_select(1, self.chem_lip_columns)
        )
        chem_prot = self.chem_prot_mlp(
            descriptor_catalog_input.index_select(1, self.chem_prot_columns)
        )

        z_geom = self.geom_interaction(geom_lip, geom_prot)
        z_chem = self.chem_interaction(chem_lip, chem_prot)
        z_final = self.group_interaction(z_geom, z_chem)

        if self.orth_weight and self.training:
            # Stashed for the training loop, same convention as Final_Layer's own
            # _dann_features/_adv (architecture/final_layer.py): None outside training
            # so no stale tensor can be read in eval.
            self._orth_stash = (
                ("geom", geom_lip.detach(), geom_prot.detach(), z_geom, self.geom_interaction),
                ("chem", chem_lip.detach(), chem_prot.detach(), z_chem, self.chem_interaction),
                ("level2", z_geom.detach(), z_chem.detach(), z_final, self.group_interaction),
            )
        else:
            self._orth_stash = None

        return z_final


def thematical_orthogonality_loss(head, labels):
    """head._orth_stash (3 (name, a, b, z, interaction) tuples, stashed by
    ThematicDescriptorHead.forward under --thematical_orth_weight) -> (penalty,
    probe_loss), or (None, None) if the stash is empty (orth_weight is 0, or eval).

    Mirrors family_dann_loss/chem_adversary_loss's contract (architecture/
    final_layer.py): the head builds the probes and stashes what a training step
    needs; the training loop supplies labels and calls this once per batch.

    `probe_loss` trains each interaction's probe_a/probe_b (Linear(dim, 1)) to predict
    the binding label from ONE side alone (v_a.detach()/v_b.detach() -- stop-gradient,
    so training the probe cannot reshape the side it reads). `penalty` then pushes the
    interaction's OWN output z away from DEPENDING on what the probe already gets
    from one side, using the probe's DETACHED prediction as a fixed target for an HSIC
    penalty (see `hsic` below) -- so the penalty's gradient reaches z (and the
    interaction block that produced it), never the probe. HSIC, not a raw covariance:
    Cov(z, p) == 0 does not imply z and p are independent, only that they are not
    LINEARLY related -- a covariance penalty can be driven to zero while z still
    depends on p through some nonlinear function, which a redundant representation is
    free to use. HSIC (Gretton et al., "Measuring Statistical Dependence with
    Hilbert-Schmidt Norms", 2005) is zero iff the two are actually independent.

    Averaged over the 3 sites (geom, chem, level2) and over the 2 probes at each, not
    summed, so thematical_orth_weight means the same pressure regardless of how many
    sites happen to be active -- same convention as adversarial_grl's adv_weight/
    dann_family's class-conditional mean (architecture/final_layer.py's own
    docstrings).

    Known blind spot (files/thematic_interaction_architecture.md): a fingerprint
    jointly correlated across a and b at once is invisible to probe_a/probe_b (neither
    side alone predicts it) and therefore untouched by `penalty` -- HSIC closes the
    linear-vs-nonlinear gap a covariance penalty had, but not this one: no single-side
    probe, linear or not, can see a pattern that only exists in the combination of a
    and b.
    """
    stash = head._orth_stash
    if not stash:
        return None, None
    labels = labels.float()
    penalty_terms, probe_terms = [], []
    for _, a, b, z, interaction in stash:
        logit_a = interaction.probe_a(a).squeeze(-1)
        logit_b = interaction.probe_b(b).squeeze(-1)
        probe_terms.append(F.binary_cross_entropy_with_logits(logit_a, labels))
        probe_terms.append(F.binary_cross_entropy_with_logits(logit_b, labels))
        penalty_terms.append(hsic(z, logit_a.detach()))
        penalty_terms.append(hsic(z, logit_b.detach()))
    penalty = torch.stack(penalty_terms).mean()
    probe_loss = torch.stack(probe_terms).mean()
    return penalty, probe_loss


def _rbf_kernel(x):
    """[n] or [n, d] -> [n, n] Gaussian/RBF kernel matrix, bandwidth set by the median
    pairwise squared distance (Gretton et al.'s median heuristic) -- the standard,
    hyperparameter-free bandwidth choice for HSIC.
    """
    if x.dim() == 1:
        x = x.unsqueeze(-1)
    sq_dists = torch.cdist(x, x, p=2) ** 2
    with torch.no_grad():
        off_diagonal = sq_dists[
            torch.triu(torch.ones_like(sq_dists, dtype=torch.bool), diagonal=1)
        ]
        bandwidth = (
            off_diagonal.median().clamp_min(1e-6)
            if off_diagonal.numel() else sq_dists.new_tensor(1.0)
        )
    return torch.exp(-sq_dists / (2.0 * bandwidth))


def hsic(x, y):
    """Empirical Hilbert-Schmidt Independence Criterion between x ([n] or [n, d]) and
    y ([n] or [n, d]) -- ~0 iff x and y are independent, not just linearly
    uncorrelated (Gretton et al., 2005). Needs n >= 2; returns 0 for a smaller batch
    (should not happen in practice, but a single-sample batch has no pairwise
    structure for a kernel to read).

    Caveat this project should keep in mind: the empirical HSIC estimator is biased
    and noisy at small n (the RBF kernel matrices are n x n, built from only n(n-1)/2
    distinct pairwise distances) -- reliable only at the batch sizes real training
    runs use (tens or more), not at the batch=2 this module's own smoke tests use
    (those only check the penalty is finite and produces gradients, not that it is a
    good dependence estimate).
    """
    n = x.shape[0]
    if n < 2:
        return x.new_zeros(())
    k = _rbf_kernel(x)
    l = _rbf_kernel(y)
    centering = torch.eye(n, device=x.device, dtype=x.dtype) - 1.0 / n
    return torch.trace(centering @ k @ centering @ l) / ((n - 1) ** 2)
