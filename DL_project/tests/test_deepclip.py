import pytest
import torch
import torch.nn.functional as F

from architecture.deepclip import DeepCLIP
from architecture.interaction_classification import InteractionClassification
from dataloader.smiles_tokens import SMILES_VOCABULARY
from training.read_configuration import ModelConfig

VOCABULARY = len(SMILES_VOCABULARY)


def make_config(**overrides):
    config = ModelConfig(deepclip=True, lipid_smiles_tokens=True)
    for key, value in overrides.items():
        setattr(config, key, value)
    config.validate()
    return config


def one_hot(lengths, seed=0):
    """A batch of one-hot molecules of the given lengths, plus its batch vector."""
    torch.manual_seed(seed)
    total = sum(lengths)
    rows = torch.zeros(total, VOCABULARY)
    rows[torch.arange(total), torch.randint(0, VOCABULARY, (total,))] = 1.0
    batch = torch.repeat_interleave(
        torch.arange(len(lengths)), torch.tensor(lengths)
    )
    return rows, batch


def test_published_defaults_reproduce_deepclips_own_size():
    """1 filter per width over FILTER_SIZES, 10 LSTM units per direction.

    Convolutions: sum over widths of (vocabulary * width), with NO bias -- DeepCLIP's
    conv layers are built with b=None (oned_convlayer_rectify.py).
    BLSTM: 2 directions * 4 gates * (input*hidden + hidden^2 + hidden), input being
    one channel per width.
    """
    model = DeepCLIP(make_config())

    widths = (4, 5, 6, 7, 8)
    expected_convs = sum(VOCABULARY * width for width in widths)
    expected_lstm = 2 * 4 * (len(widths) * 10 + 10 * 10 + 2 * 10)

    assert all(conv.bias is None for conv in model.convs)
    assert sum(p.numel() for p in model.convs.parameters()) == expected_convs
    assert sum(p.numel() for p in model.lstm.parameters()) == expected_lstm
    assert sum(p.numel() for p in model.parameters()) == expected_convs + expected_lstm


def test_convolutions_use_deepclips_constant_initialisation():
    """W = Constant(0.01). PyTorch's own default here is ~5x larger and saturates."""
    model = DeepCLIP(make_config())

    for conv in model.convs:
        assert torch.equal(conv.weight, torch.full_like(conv.weight, 0.01))


def test_constant_initialisation_is_refused_for_more_than_one_filter():
    """Identical weights mean identical gradients: the copies never differentiate."""
    config = ModelConfig(
        deepclip=True, lipid_smiles_tokens=True, deepclip_filters=4,
    )

    with pytest.raises(ValueError, match="stay one filter"):
        config.validate()

    config.deepclip_conv_init = "normal"
    config.validate()


def test_mean_readout_removes_the_length_dependence_the_sum_has():
    """The reason "mean" is the default.

    DeepCLIP sums the profile over positions, which is length-neutral only because it
    pads every sequence to one fixed length and never masks (slice_n_pad.py). This
    project's molecules span 26-165 characters, so the literal sum reads length: at
    initialisation the per-position profile is nearly constant, and the score is that
    constant times the character count.

    What "mean" leaves behind is a boundary effect, not a length readout: windows
    hanging off the two ends see padding, and their share of the molecule falls as
    1/length, so the mean score converges (measured across 10..600 characters it rises
    0.279 -> 0.301 with the increments shrinking to +0.0004). Across the range this
    dataset actually holds it drifts ~2%, against the sum's ~6x.
    """
    lengths = (26, 96, 165)

    torch.manual_seed(0)
    summed = DeepCLIP(make_config(deepclip_readout="sum")).eval()
    torch.manual_seed(0)
    averaged = DeepCLIP(make_config(deepclip_readout="mean")).eval()

    sum_scores, mean_scores = [], []
    for length in lengths:
        rows, batch = one_hot([length], seed=length)
        sum_scores.append(summed(rows, batch)[0, 1].item())
        mean_scores.append(averaged(rows, batch)[0, 1].item())

    assert sum_scores[-1] > 4 * sum_scores[0]
    assert max(mean_scores) - min(mean_scores) < 0.02 * max(mean_scores)


def test_deepclip_builds_nothing_else_from_this_project():
    """No protein encoder, no lipid encoder, no cross-attention, no Final_Layer."""
    model = InteractionClassification(make_config())

    assert [name for name, _ in model.named_children()] == ["deepclip"]


def test_every_parameter_receives_gradient():
    config = make_config()
    model = InteractionClassification(config)
    rows, batch = one_hot([5, 4])

    out = model(
        config=config, plm=None, bury=None, prot=None, prot_edgidx=None,
        prot_e_attr=None, prot_batch=None, lip=rows, lip_batch=batch,
    )
    F.cross_entropy(out, torch.tensor([0, 1])).backward()

    trainable = [p for p in model.parameters() if p.requires_grad]
    assert trainable
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in trainable)


def test_two_logits_are_deepclips_own_sigmoid():
    """softmax([0, s])[1] == sigmoid(s), so the reported probability is DeepCLIP's."""
    model = DeepCLIP(make_config()).eval()
    rows, batch = one_hot([6, 3])

    logits = model(rows, batch)

    assert torch.equal(logits[:, 0], torch.zeros(2))
    assert torch.allclose(
        logits.softmax(dim=1)[:, 1], torch.sigmoid(logits[:, 1]), atol=1e-6
    )


def test_profile_is_one_number_per_character_and_ignores_padding():
    """The binding profile is what DeepCLIP is known for; padding must not enter it.

    Batched with a longer molecule, the short one's score must equal what it scores
    alone -- otherwise the padded tail is being summed into it.
    """
    model = DeepCLIP(make_config()).eval()
    rows, batch = one_hot([7, 3])

    together = model(rows, batch)
    profile = model.profile

    assert profile.shape == (2, 7)
    # The short molecule owns only its first 3 positions; the rest are padding.
    assert torch.equal(profile[1, 3:], torch.zeros(4))

    alone = model(rows[7:], torch.zeros(3, dtype=torch.long))
    assert torch.allclose(together[1], alone[0], atol=1e-6)


def test_deepclip_requires_the_one_hot_input():
    config = ModelConfig(deepclip=True)

    with pytest.raises(ValueError, match="lipid_smiles_tokens"):
        config.validate()


def test_deepclip_refuses_flags_for_modules_it_does_not_build():
    config = ModelConfig(deepclip=True, lipid_smiles_tokens=True, lipid_only=True)

    with pytest.raises(ValueError, match="has nothing to configure"):
        config.validate()


def test_deepclip_refuses_candidates_sharing_one_sequence_axis():
    config = ModelConfig(
        deepclip=True, lipid_smiles_tokens=True,
        lipid_fragments_treatment="concat",
    )

    with pytest.raises(ValueError, match="slide across the seam"):
        config.validate()


def test_filter_count_and_lstm_width_are_configurable():
    model = DeepCLIP(
        make_config(
            deepclip_filters=4, deepclip_widths="3,5", deepclip_conv_init="normal",
        )
    )

    expected_convs = 4 * VOCABULARY * 3 + 4 * VOCABULARY * 5
    assert sum(p.numel() for p in model.convs.parameters()) == expected_convs
    assert model.lstm.input_size == 8
