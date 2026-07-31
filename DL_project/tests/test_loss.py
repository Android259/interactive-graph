import pytest
import torch
import torch.nn.functional as F

from architecture.loss import GRAB_loss, Non_Negative_Positive_Unlabeled_loss


def test_pu_loss_uses_positive_and_unlabeled_risks():
    outl = torch.tensor([[0.0, 2.0], [0.0, -1.0], [0.0, 0.5]])
    labels = torch.tensor([1, 0, 0])
    prior = 0.25
    logits = outl[:, 1] - outl[:, 0]
    positive_logits = logits[labels == 1]
    positive_loss = prior * F.softplus(-positive_logits).mean()
    # The marginal term averages over EVERY row, not the unlabeled ones alone: prior is
    # the positive fraction of the whole train set, so the term it is subtracted from
    # has to be estimated on a sample of that same population.
    negative_loss = (
        F.softplus(logits).mean() - prior * F.softplus(positive_logits).mean()
    )

    loss = Non_Negative_Positive_Unlabeled_loss(outl, labels, prior)

    assert torch.allclose(loss, positive_loss + torch.clamp(negative_loss, min=0.0))


def test_pu_loss_uses_nnpu_correction_when_negative_risk_is_too_low():
    outl = torch.tensor([[0.0, 6.0], [0.0, -6.0]], requires_grad=True)
    labels = torch.tensor([1, 0])
    prior = 0.8
    gamma = 2.0
    logits = outl[:, 1] - outl[:, 0]
    positive_logits = logits[labels == 1]
    negative_loss = (
        F.softplus(logits).mean() - prior * F.softplus(positive_logits).mean()
    )
    positive_loss = prior * F.softplus(-positive_logits).mean()

    loss = Non_Negative_Positive_Unlabeled_loss(
        outl,
        labels,
        prior,
        beta=0.0,
        gamma=gamma,
    )

    assert negative_loss < 0
    # Straight-through: the value reported is the clamped estimator positive_risk - beta,
    # while the gradient is the recovery step -gamma * negative_risk. Both are checked,
    # since they are deliberately different expressions.
    assert torch.allclose(loss, positive_loss)

    loss.backward()
    expected_grad = torch.autograd.grad(-gamma * negative_loss, outl)[0]
    assert torch.allclose(outl.grad, expected_grad)


def test_pu_loss_normalizes_sample_weights_within_positive_and_unlabeled_sets():
    outl = torch.tensor([[0.0, 2.0], [0.0, -1.0], [0.0, 1.0]])
    labels = torch.tensor([1, 0, 0])
    sample_weights = torch.tensor([0.5, 0.25, 0.75])
    prior = 0.2
    logits = outl[:, 1] - outl[:, 0]
    positive_mask = labels == 1
    positive_values = F.softplus(-logits[positive_mask])
    negative_positive_values = F.softplus(logits[positive_mask])
    positive_loss = prior * (
        positive_values * sample_weights[positive_mask]
    ).sum() / sample_weights[positive_mask].sum()
    # Weighted mean over the whole batch, matching the marginal population the prior
    # is defined on.
    negative_loss = (
        F.softplus(logits) * sample_weights
    ).sum() / sample_weights.sum()
    negative_loss = negative_loss - prior * (
        negative_positive_values * sample_weights[positive_mask]
    ).sum() / sample_weights[positive_mask].sum()

    loss = Non_Negative_Positive_Unlabeled_loss(
        outl,
        labels,
        prior,
        sample_weights=sample_weights,
    )

    assert torch.allclose(loss, positive_loss + torch.clamp(negative_loss, min=0.0))


def test_pu_loss_combines_sample_weights_with_class_weights_by_label():
    outl = torch.tensor([[0.0, 2.0], [0.0, -1.0], [0.0, 1.0]])
    labels = torch.tensor([1, 0, 0])
    sample_weights = torch.tensor([0.5, 0.25, 0.75])
    class_weights = torch.tensor([2.0, 3.0])
    combined_weights = sample_weights * class_weights[labels]
    prior = 0.2
    logits = outl[:, 1] - outl[:, 0]
    positive_mask = labels == 1

    # class_weights is deliberately no longer a parameter: the prior already carries the
    # class balance in the risk estimator, so weighting by class on top double-counts it.
    with pytest.raises(TypeError):
        Non_Negative_Positive_Unlabeled_loss(
            outl,
            labels,
            prior,
            sample_weights=sample_weights,
            class_weights=class_weights,
        )

    # Passing the combined weights as plain sample weights still works, and is the only
    # way class balance can enter -- through the sample weighting, not a separate term.
    positive_values = F.softplus(-logits[positive_mask])
    negative_positive_values = F.softplus(logits[positive_mask])
    positive_loss = prior * (
        positive_values * combined_weights[positive_mask]
    ).sum() / combined_weights[positive_mask].sum()
    negative_loss = (
        F.softplus(logits) * combined_weights
    ).sum() / combined_weights.sum()
    negative_loss = negative_loss - prior * (
        negative_positive_values * combined_weights[positive_mask]
    ).sum() / combined_weights[positive_mask].sum()

    loss = Non_Negative_Positive_Unlabeled_loss(
        outl,
        labels,
        prior,
        sample_weights=combined_weights,
    )

    assert torch.allclose(loss, positive_loss + torch.clamp(negative_loss, min=0.0))


@pytest.mark.parametrize("prior", [0.0, 1.0, -0.1, 1.1])
def test_pu_loss_rejects_invalid_prior(prior):
    outl = torch.tensor([[0.0, 1.0]])
    labels = torch.tensor([1])

    with pytest.raises(ValueError, match="prior"):
        Non_Negative_Positive_Unlabeled_loss(outl, labels, prior)


def test_pu_loss_rejects_invalid_labels():
    outl = torch.tensor([[0.0, 1.0], [1.0, 0.0]])
    labels = torch.tensor([1, 2])

    with pytest.raises(ValueError, match="classes 0 and 1"):
        Non_Negative_Positive_Unlabeled_loss(outl, labels, prior=0.2)


def test_grab_loss_without_graph_coefficients_matches_cross_entropy():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.zeros((2, 2))

    loss = GRAB_loss(outl, labels, coefficients)

    assert torch.allclose(loss, F.cross_entropy(outl, labels))


def test_grab_loss_rejects_coefficient_batch_mismatch():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.zeros((1, 2))

    with pytest.raises(ValueError, match="coefficients must match logits"):
        GRAB_loss(outl, labels, coefficients)


def test_grab_loss_rejects_invalid_labels():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 2])
    coefficients = torch.zeros((2, 2))

    with pytest.raises(ValueError, match="classes 0 and 1"):
        GRAB_loss(outl, labels, coefficients)


def test_grab_loss_rejects_negative_coefficients():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.tensor([[0.0, -1.0], [0.0, 1.0]])

    with pytest.raises(ValueError, match="negative"):
        GRAB_loss(outl, labels, coefficients)


def test_grab_loss_normalizes_sample_weights_by_weight_sum():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.zeros((2, 2))
    sample_weights = torch.tensor([0.2, 0.8])
    unreduced = F.cross_entropy(outl, labels, reduction="none")
    expected = (unreduced * sample_weights).sum() / sample_weights.sum()

    loss = GRAB_loss(outl, labels, coefficients, sample_weights=sample_weights)

    assert torch.allclose(loss, expected)


def test_grab_loss_adds_graph_term_for_valid_label_coefficients():
    outl = torch.tensor([[2.0, 0.0], [1.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.tensor([[3.0, 1.0], [0.0, 2.0]])
    target_loss = F.cross_entropy(outl, labels)
    log_probs = F.log_softmax(outl, dim=1)
    normalized_coefficients = coefficients / coefficients.sum(dim=1, keepdim=True)
    graph_loss = -(normalized_coefficients * log_probs).sum(dim=1).mean()

    loss = GRAB_loss(outl, labels, coefficients)

    assert torch.allclose(loss, target_loss + graph_loss)


def test_grab_loss_does_not_apply_class_weights_to_graph_term():
    outl = torch.tensor([[2.0, 0.0], [1.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.tensor([[3.0, 1.0], [0.0, 2.0]])
    class_weights = torch.tensor([0.5, 4.0])
    target_loss = F.cross_entropy(outl, labels, weight=class_weights, reduction="none").mean()
    log_probs = F.log_softmax(outl, dim=1)
    normalized_coefficients = coefficients / coefficients.sum(dim=1, keepdim=True)
    graph_loss = -(normalized_coefficients * log_probs).sum(dim=1).mean()

    loss = GRAB_loss(outl, labels, coefficients, class_weights=class_weights)

    assert torch.allclose(loss, target_loss + graph_loss)


def test_grab_loss_ignores_targets_with_zero_coefficients():
    outl = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    labels = torch.tensor([0, 1])
    coefficients = torch.tensor([[0.0, 0.0], [0.0, 1.0]])
    target_loss = F.cross_entropy(outl, labels)
    log_probs = F.log_softmax(outl[1:], dim=1)
    graph_loss = -log_probs[0, 1]

    loss = GRAB_loss(outl, labels, coefficients)

    assert torch.allclose(loss, target_loss + graph_loss)
