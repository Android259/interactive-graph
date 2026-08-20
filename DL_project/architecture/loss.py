import torch
import torch.nn.functional as F


# Instrumentation for the nnPU negative risk: how often the non-negative
# correction (negative_risk < -beta) triggers, and the per-epoch range of the
# raw (pre-clamp) negative_risk. That range is what you read off the logs to
# pick the loss cap M (pu_loss_cap) and the recovery rate gamma.
_pu_loss_diagnostics = {
    "calls": 0,
    "corrections": 0,
    "min_negative_loss": float("inf"),
    "max_negative_loss": float("-inf"),
    "sum_negative_loss": 0.0,
}


def reset_pu_loss_diagnostics():
    """Reset the nnPU negative-risk diagnostics."""
    _pu_loss_diagnostics.update(
        calls=0,
        corrections=0,
        min_negative_loss=float("inf"),
        max_negative_loss=float("-inf"),
        sum_negative_loss=0.0,
    )


def get_pu_loss_diagnostics():
    """Return a snapshot of the nnPU negative-risk diagnostics."""
    return dict(_pu_loss_diagnostics)


def _weighted_mean(values, weights=None):
    if weights is None:
        return values.mean()
    return (values * weights).sum() / weights.sum().clamp_min(1e-8)


def focal_loss(
    outl,
    interaction_labels,
    gamma=2.0,
    class_weights=None,
    sample_weights=None,
    reduction="mean",
):
    """Multi-class focal loss (Lin et al., 2017) down-weighting easy examples."""
    if outl.dim() != 2 or outl.shape[1] != 2:
        raise ValueError(f"focal loss logits must have shape (batch, 2), got {tuple(outl.shape)}")
    if gamma < 0.0:
        raise ValueError("focal loss gamma must be non-negative")

    labels = interaction_labels.to(outl.device).long()
    if labels.dim() != 1 or labels.shape[0] != outl.shape[0]:
        raise ValueError(
            "focal loss labels must have shape (batch,), "
            f"got {tuple(labels.shape)} for logits {tuple(outl.shape)}"
        )

    log_probs = F.log_softmax(outl, dim=1)
    label_log_probs = log_probs.gather(1, labels.unsqueeze(1)).squeeze(1)
    label_probs = label_log_probs.exp()
    focal_term = (1.0 - label_probs).clamp_min(0.0).pow(gamma)
    per_sample_loss = -focal_term * label_log_probs

    if class_weights is not None:
        class_weights = class_weights.to(outl.device).float()
        if class_weights.shape != (outl.shape[1],):
            raise ValueError(
                "focal loss class_weights must have shape "
                f"({outl.shape[1]},), got {tuple(class_weights.shape)}"
            )
        per_sample_loss = per_sample_loss * class_weights[labels]

    if sample_weights is not None:
        sample_weights = sample_weights.to(outl.device).float()
        if sample_weights.shape != (outl.shape[0],):
            raise ValueError(
                "focal loss sample_weights must have shape "
                f"({outl.shape[0]},), got {tuple(sample_weights.shape)}"
            )
        per_sample_loss = per_sample_loss * sample_weights

    if reduction == "none":
        return per_sample_loss
    if reduction == "sum":
        return per_sample_loss.sum()
    return per_sample_loss.mean()


def logit_adjustment_bias(class_counts, tau=1.0):
    """Return the additive per-class log-prior bias from Menon et al. (2020)."""
    class_counts = class_counts.float()
    if (class_counts < 0).any():
        raise ValueError("logit adjustment class_counts must be non-negative")
    total = class_counts.sum()
    if total <= 0:
        raise ValueError("logit adjustment class_counts must not all be zero")
    class_prior = (class_counts / total).clamp_min(1e-12)
    return tau * class_prior.log()


def Non_Negative_Positive_Unlabeled_loss(
    outl,
    interaction_labels,
    prior,
    beta=0.0,
    gamma=1.0,
    sample_weights=None,
    tau=1.0,
    cap=float("inf"),
):
    """nnPU risk estimator (Kiryo et al., 2017).

    Surrogate: the unbounded logistic loss l(z,+1)=softplus(-z),
    l(z,-1)=softplus(z). The earlier version used the bounded, symmetric sigmoid
    (sigmoid(z)+sigmoid(-z)=1, kept commented out below): its symmetry gives a
    clean unbiased-PU identity, but its ceiling of 1 makes the gradient vanish on
    confidently-wrong points and underfits the train set. The logistic surrogate
    has no ceiling, so the gradient stays alive on wrong points; the negative-
    risk collapse it can otherwise cause (positive logits -> +inf) is caught by
    the nnPU non-negative correction below, not by bounding the loss.

    prior is the class prior P(y=1) over the whole train set -- labeled
    positives plus the hidden positives among the unlabeled rows -- supplied by
    the caller (config) and not re-derived here. Because it is defined on that
    whole population, the risk term it is subtracted from is the mean over
    every row of the batch, not over the unlabeled rows alone. Class weights are
    intentionally not applied: the prior already carries the class balance in
    the risk estimator.

    tau (>0) is a temperature on the surrogate margin z: the loss becomes
    softplus(-z/tau). tau<1 sharpens the transition and raises the gradient near
    the decision boundary; tau=1 is the unscaled margin.

    cap (>0) clamps each surrogate value at that ceiling: l = min(softplus(.),
    cap). cap=inf is the pure logistic loss; a finite cap keeps the loss bounded
    (so Kiryo's estimation-error theory still applies) while the gradient stays
    alive up to a margin ~cap, and it limits how far negative_risk can dive
    (floor ~ (batch_positive_fraction - prior) * cap).
    """
    if outl.dim() != 2 or outl.shape[1] != 2:
        raise ValueError(f"PU logits must have shape (batch, 2), got {tuple(outl.shape)}")
    if not 0.0 < float(prior) < 1.0:
        raise ValueError("PU prior must be in the range (0, 1)")
    if beta < 0.0:
        raise ValueError("PU beta must be non-negative")
    if gamma <= 0.0:
        raise ValueError("PU gamma must be positive")
    if tau <= 0.0:
        raise ValueError("PU tau must be positive")
    if cap <= 0.0:
        raise ValueError("PU cap must be positive")

    labels = interaction_labels.to(outl.device)
    if labels.dim() != 1 or labels.shape[0] != outl.shape[0]:
        raise ValueError(
            "PU labels must have shape (batch,), "
            f"got {tuple(labels.shape)} for logits {tuple(outl.shape)}"
        )
    if not torch.isin(labels.long(), torch.tensor([0, 1], device=labels.device)).all():
        raise ValueError("PU labels must contain only classes 0 and 1")

    if sample_weights is not None:
        sample_weights = sample_weights.to(outl.device).float()
        if sample_weights.shape != (outl.shape[0],):
            raise ValueError(
                "PU sample_weights must have shape "
                f"({outl.shape[0]},), got {tuple(sample_weights.shape)}"
            )
        if not torch.isfinite(sample_weights).all():
            raise ValueError("PU sample_weights contain non-finite values")
        if (sample_weights < 0).any():
            raise ValueError("PU sample_weights contain negative values")

    # Margin z, optionally sharpened by temperature tau (<1 = sharper).
    logits = (outl[:, 1] - outl[:, 0]) / tau
    positive_mask = labels.long() == 1
    unlabeled_mask = labels.long() == 0
    positive_weights = sample_weights[positive_mask] if sample_weights is not None else None
    unlabeled_weights = sample_weights[unlabeled_mask] if sample_weights is not None else None

    # Previous bounded, symmetric surrogate (kept for reference): its ceiling of 1
    # makes the gradient vanish on confidently-wrong points -> underfitting.
    # loss_as_positive = torch.sigmoid(-logits)  # l(f, +1)
    # loss_as_negative = torch.sigmoid(logits)   # l(f, -1)
    # Logistic surrogate with a raised, tunable ceiling `cap`: the gradient stays
    # alive on wrong points up to a margin ~cap (fixes the underfit), but the loss
    # is still bounded (cap=inf recovers the pure unbounded softplus). The nnPU
    # non-negative correction below guards the residual negative-risk collapse.
    loss_as_positive = torch.clamp(F.softplus(-logits), max=cap)  # l(f, +1)
    loss_as_negative = torch.clamp(F.softplus(logits), max=cap)   # l(f, -1)

    if not positive_mask.any():
        # No labeled positives in this batch: fall back to the unlabeled risk.
        return _weighted_mean(loss_as_negative[unlabeled_mask], unlabeled_weights)

    positive_risk = prior * _weighted_mean(loss_as_positive[positive_mask], positive_weights)
    negative_risk_positive = prior * _weighted_mean(
        loss_as_negative[positive_mask], positive_weights
    )
    # prior is the positive fraction of the whole train set, so the term it is
    # subtracted from has to be the mean over a sample of that same population:
    # every row in the batch, not the unlabeled rows alone. Averaging over the
    # unlabeled rows only would leave the two terms defined on different
    # populations and drive negative_risk far below zero at separation, firing
    # the correction branch on batches where nothing is wrong.
    risk_marginal_as_negative = _weighted_mean(loss_as_negative, sample_weights)

    negative_risk = risk_marginal_as_negative - negative_risk_positive
    negative_risk_value = negative_risk.detach().item()
    _pu_loss_diagnostics["calls"] += 1
    _pu_loss_diagnostics["sum_negative_loss"] += negative_risk_value
    if negative_risk_value < _pu_loss_diagnostics["min_negative_loss"]:
        _pu_loss_diagnostics["min_negative_loss"] = negative_risk_value
    if negative_risk_value > _pu_loss_diagnostics["max_negative_loss"]:
        _pu_loss_diagnostics["max_negative_loss"] = negative_risk_value
    if negative_risk < -beta:
        _pu_loss_diagnostics["corrections"] += 1
        # Straight-through (Kiryo et al., 2017): report the value of the clamped
        # non-negative risk estimator, positive_risk - beta, but backpropagate
        # the recovery step -gamma * negative_risk.
        gradient_surrogate = -gamma * negative_risk
        reported_value = positive_risk - beta
        return gradient_surrogate + (reported_value - gradient_surrogate).detach()

    return positive_risk + negative_risk


def pairwise_ranking_loss(outl, interaction_labels, sample_weights=None, protein_ids=None):
    """RankNet-style pairwise logistic loss: a smooth surrogate for AUC, not for BA.

    Cross-entropy asks each row on its own: "is this side of 0.5?" On this dataset that
    question has a wrong answer baked in before training starts -- the chemistry-only
    null model in files/marginals_and_cold_split.md 8.1 scores balanced accuracy 0.512
    with a threshold fit on train while it ranks the same rows at AUC 0.565, so most of
    what a fixed-threshold loss is graded on here is where the threshold sits, not what
    the model knows. This asks a different question that has no threshold in it: "does
    the positive row of this pair score higher than the negative row?" AUC is exactly
    the fraction of such pairs answered correctly, so this loss is a direct smooth
    surrogate for the metric this project now reports.

    Two pairings, chosen by `protein_ids`.

    Without it, every positive row in the batch pairs with every negative row, which
    optimises the POOLED-block AUC. That number is a mixture: "does this lipid bind
    anything at all", which the chemistry null model already answers, and "does it bind
    THIS protein", which is the interaction term. On this dataset the first half is
    saturated -- the null model reaches 0.569 pooled while the network reaches 0.542 --
    so a loss aimed at the mixture spends its gradient where there is nothing left to
    win.

    With `protein_ids` (one id per row, `--rank_within_protein`), a pair is only formed
    between rows sharing a protein. Then the marginal cannot help: inside one protein
    every row has the same partner, so the only thing left to rank by is the pair. This
    is the quantity files/interaction_signal_plan.md 3 argues the project should be
    optimising, and analysis/chemistry_null_model.py reports it as `net_AUC_prot`.

    The cost is pair count. Batches are drawn across proteins, so most of the pair
    matrix is discarded and a batch may contribute very few pairs, or none. Rather than
    raise, a batch with no same-protein pair returns zero with no gradient, exactly as
    an all-one-class batch does -- but a run whose batches rarely share a protein is
    training on almost nothing, and the pair count is worth logging before trusting a
    result. For each surviving pair the loss is
    -log(sigmoid(score_positive - score_negative)) with score = logit(class 1) -
    logit(class 0), the same margin the PU loss uses. Class imbalance drops out on its
    own: every pair already has exactly one positive and one negative, so
    --class_weights, --focal_loss and --logit_adjustment have nothing left to correct
    and are not read by this path.

    Under --balanced_batches (the setting this is meant to run under) every batch holds
    both classes by construction. Without it, an all-one-class batch carries no pair to
    rank; rather than raise, this returns a zero with no gradient for that batch, the
    same degradation Non_Negative_Positive_Unlabeled_loss falls back to when a batch has
    no labeled positives.
    """
    if outl.dim() != 2 or outl.shape[1] != 2:
        raise ValueError(f"pairwise ranking logits must have shape (batch, 2), got {tuple(outl.shape)}")

    labels = interaction_labels.to(outl.device).long()
    if labels.dim() != 1 or labels.shape[0] != outl.shape[0]:
        raise ValueError(
            "pairwise ranking labels must have shape (batch,), "
            f"got {tuple(labels.shape)} for logits {tuple(outl.shape)}"
        )
    if not torch.isin(labels, torch.tensor([0, 1], device=labels.device)).all():
        raise ValueError("pairwise ranking labels must contain only classes 0 and 1")

    score = outl[:, 1] - outl[:, 0]
    positive_mask = labels == 1
    negative_mask = labels == 0
    positive_scores = score[positive_mask]
    negative_scores = score[negative_mask]
    if positive_scores.numel() == 0 or negative_scores.numel() == 0:
        return score.new_zeros(())

    # (positives, negatives) matrix of margins; batch=16 at negatives_per_positive=2
    # makes this at most ~5x11, so the full pair set costs nothing to materialise.
    margin = positive_scores.unsqueeze(1) - negative_scores.unsqueeze(0)
    per_pair_loss = F.softplus(-margin)

    pair_mask = None
    if protein_ids is not None:
        protein_ids = protein_ids.to(outl.device).view(-1)
        if protein_ids.shape[0] != outl.shape[0]:
            raise ValueError(
                "pairwise ranking protein_ids must have one id per row, "
                f"got {tuple(protein_ids.shape)} for logits {tuple(outl.shape)}"
            )
        pair_mask = protein_ids[positive_mask].unsqueeze(1) == protein_ids[negative_mask].unsqueeze(0)
        if not pair_mask.any():
            # Every pair in this batch straddles two proteins. Nothing to rank.
            return score.new_zeros(())

    if sample_weights is None:
        if pair_mask is None:
            return per_pair_loss.mean()
        # Mean over surviving pairs only: dividing by the full matrix would shrink the
        # gradient by however many cross-protein pairs happened to be in the batch,
        # making the effective learning rate depend on the batch's protein mix.
        return (per_pair_loss * pair_mask).sum() / pair_mask.sum()

    sample_weights = sample_weights.to(outl.device).float()
    if sample_weights.shape != (outl.shape[0],):
        raise ValueError(
            "pairwise ranking sample_weights must have shape "
            f"({outl.shape[0]},), got {tuple(sample_weights.shape)}"
        )
    if not torch.isfinite(sample_weights).all():
        raise ValueError("pairwise ranking sample_weights contain non-finite values")
    if (sample_weights < 0).any():
        raise ValueError("pairwise ranking sample_weights contain negative values")
    positive_weights = sample_weights[positive_mask]
    negative_weights = sample_weights[negative_mask]
    pair_weights = positive_weights.unsqueeze(1) * negative_weights.unsqueeze(0)
    if pair_mask is not None:
        pair_weights = pair_weights * pair_mask
    return (per_pair_loss * pair_weights).sum() / pair_weights.sum().clamp_min(1e-8)


def GRAB_loss(
    outl,
    interaction_labels,
    grab_label_coefficients,
    class_weights=None,
    sample_weights=None,
    graph_weight=1.0,
    focal_gamma=None):

    if outl.dim() != 2 or outl.shape[1] != 2:
        raise ValueError(f"GRAB logits must have shape (batch, 2), got {tuple(outl.shape)}")
    if focal_gamma is not None and focal_gamma < 0.0:
        raise ValueError("GRAB focal_gamma must be non-negative")

    labels = interaction_labels.to(outl.device)
    if labels.dim() != 1 or labels.shape[0] != outl.shape[0]:
        raise ValueError(
            "GRAB labels must have shape (batch,), "
            f"got {tuple(labels.shape)} for logits {tuple(outl.shape)}"
        )
    if not torch.isin(labels.long(), torch.tensor([0, 1], device=labels.device)).all():
        raise ValueError("GRAB labels must contain only classes 0 and 1")

    label_coefficients = grab_label_coefficients.to(outl.device).float()
    if label_coefficients.shape != outl.shape:
        raise ValueError(
            "GRAB coefficients must match logits shape "
            f"{tuple(outl.shape)}, got {tuple(label_coefficients.shape)}"
        )
    if not torch.isfinite(label_coefficients).all():
        raise ValueError("GRAB coefficients contain non-finite values")
    if (label_coefficients < 0).any():
        raise ValueError("GRAB coefficients contain negative values")

    if class_weights is not None:
        class_weights = class_weights.to(outl.device).float()
        if class_weights.shape != (outl.shape[1],):
            raise ValueError(
                "GRAB class_weights must have shape "
                f"({outl.shape[1]},), got {tuple(class_weights.shape)}"
            )

    if sample_weights is not None:
        sample_weights = sample_weights.to(outl.device).float()
        if sample_weights.shape != (outl.shape[0],):
            raise ValueError(
                "GRAB sample_weights must have shape "
                f"({outl.shape[0]},), got {tuple(sample_weights.shape)}"
            )
        if not torch.isfinite(sample_weights).all():
            raise ValueError("GRAB sample_weights contain non-finite values")
        if (sample_weights < 0).any():
            raise ValueError("GRAB sample_weights contain negative values")

    if focal_gamma is None:
        target_loss = F.cross_entropy(outl, labels.long(), weight=class_weights, reduction="none")
    else:
        target_loss = focal_loss(
            outl, labels.long(), gamma=focal_gamma, class_weights=class_weights, reduction="none"
        )
    if sample_weights is not None:
        target_loss = (target_loss * sample_weights).sum() / sample_weights.sum().clamp_min(1e-8)
    else:
        target_loss = target_loss.mean()

    coefficient_sum = label_coefficients.sum(dim=1)
    valid_target_mask = coefficient_sum > 0
    if not valid_target_mask.any():
        return target_loss

    log_probs = F.log_softmax(outl[valid_target_mask], dim=1)
    label_coefficients = label_coefficients[valid_target_mask]
    coefficient_sum = coefficient_sum[valid_target_mask].view(-1, 1)
    label_coefficients = label_coefficients / coefficient_sum.clamp_min(1e-8)
    graph_loss = -(label_coefficients * log_probs).sum(dim=1)
    graph_loss = graph_loss.mean()

    return target_loss + graph_weight * graph_loss
