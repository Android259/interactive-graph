import torch
import torch.nn.functional as F

from .mlp_utils import make_activation


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
    applied here to the product itself instead of to a whole outer-product matrix
    (there is no full bilinear tensor here to normalise, only its low-rank stand-in).

    There is no concatenation of v_a/v_b alongside the product for a downstream layer
    to read instead of it -- that skip is exactly what would let a classifier
    reconstruct one side's identity directly and ignore the product term.

    This alone does not prove the output cannot reconstruct one side's identity: a
    fingerprint jointly correlated across both sides at once (present in v_a AND v_b
    together, absent from either alone) survives this structural constraint unchanged,
    because it satisfies the exact same "not predictable from one side alone"
    criterion real synergy does. Only a pair-shuffling audit downstream can tell the
    two apart.
    """

    def __init__(self, dim, config, act_fn=None):
        super().__init__()
        self.proj_a = torch.nn.Linear(dim, dim)
        self.proj_b = torch.nn.Linear(dim, dim)
        hidden = max(config.m * dim, dim)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(dim, hidden),
            make_activation(config, act_fn),
            torch.nn.Linear(hidden, dim),
        )

    def forward(self, a, b):
        product = self.proj_a(a) * self.proj_b(b)
        product = torch.sign(product) * torch.sqrt(product.abs() + 1e-6)
        product = F.normalize(product, p=2, dim=-1)
        return self.ffn(product)
