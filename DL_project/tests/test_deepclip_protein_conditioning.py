"""The ways the protein can enter architecture/deepclip.py.

Each mechanism is behind its own flag. What is checked for every one: it starts as
plain DeepCLIP (except --deepclip_protein_tokens, which changes the input itself),
every parameter it adds receives a gradient, and padding never reaches the score.
"""
import pytest
import torch
import torch.nn.functional as F

from architecture.deepclip import DeepCLIP
from dataloader.pair_descriptors import full_catalog_order
from dataloader.protein_graph_builder import POCKET_TOKEN_WIDTH
from dataloader.smiles_tokens import SMILES_VOCABULARY
from training.read_configuration import ModelConfig, read_configuration

VOCABULARY = len(SMILES_VOCABULARY)
NAMES = "aromatic_share,hydropathy_rim"

DESCRIPTOR_VARIANTS = {
    "film": dict(deepclip_protein_film=NAMES),
    "hyperconv": dict(deepclip_protein_hyperconv=NAMES),
    "bilinear": dict(deepclip_protein_bilinear=NAMES),
    "gate_signed": dict(deepclip_protein_gate=NAMES, deepclip_gate_signed=True),
    "gate_positional": dict(deepclip_protein_gate=NAMES, deepclip_gate_positional=True),
}
TOKEN_VARIANTS = {
    "cross_attention": dict(deepclip_pocket_cross_attention=True),
    "tokens": dict(deepclip_protein_tokens=True),
}


def make_config(**overrides):
    config = ModelConfig(
        deepclip=True, lipid_smiles_tokens=True, deepclip_conv_init="normal",
        pair_descriptors=True, pocket_descriptors=True,
    )
    for key, value in overrides.items():
        setattr(config, key, value)
    config.validate()
    return config


def batch(lengths, config, pocket_sizes=(3, 5), longest=6, seed=0):
    """One-hot molecules, a catalog row per molecule and left-aligned pocket tokens."""
    generator = torch.Generator().manual_seed(seed)
    total = sum(lengths)
    rows = torch.zeros(total, VOCABULARY)
    rows[torch.arange(total), torch.randint(0, VOCABULARY, (total,), generator=generator)] = 1.0
    lip_batch = torch.repeat_interleave(torch.arange(len(lengths)), torch.tensor(lengths))
    catalog = torch.randn(len(lengths), len(full_catalog_order(config)), generator=generator)
    tokens = torch.zeros(len(lengths), longest, POCKET_TOKEN_WIDTH)
    mask = torch.zeros(len(lengths), longest, dtype=torch.bool)
    for row, size in enumerate(pocket_sizes):
        types = torch.randint(0, POCKET_TOKEN_WIDTH - 1, (size,), generator=generator)
        tokens[row, torch.arange(size), types] = 1.0
        tokens[row, :size, -1] = torch.rand(size, generator=generator)
        mask[row, :size] = True
    return dict(
        lip=rows, lip_batch=lip_batch, descriptor_catalog_input=catalog,
        pocket_tokens=tokens, pocket_token_mask=mask,
    )


def paired(overrides):
    """(plain DeepCLIP, variant) with the variant's shared weights copied from plain."""
    torch.manual_seed(0)
    plain = DeepCLIP(make_config())
    torch.manual_seed(0)
    variant = DeepCLIP(make_config(**overrides))
    variant.load_state_dict(plain.state_dict(), strict=False)
    return plain.eval(), variant.eval()


@pytest.mark.parametrize(
    "overrides",
    [*DESCRIPTOR_VARIANTS.values(), TOKEN_VARIANTS["cross_attention"]],
    ids=[*DESCRIPTOR_VARIANTS, "cross_attention"],
)
def test_every_mechanism_but_tokens_starts_as_plain_deepclip(overrides):
    plain, variant = paired(overrides)
    inputs = batch([7, 4], variant.config)

    expected = plain(**inputs)
    got = variant(**inputs)

    assert torch.allclose(got, expected, atol=1e-6)


@pytest.mark.parametrize(
    "overrides",
    [*DESCRIPTOR_VARIANTS.values(), *TOKEN_VARIANTS.values()],
    ids=[*DESCRIPTOR_VARIANTS, *TOKEN_VARIANTS],
)
def test_every_parameter_receives_gradient(overrides):
    config = make_config(**overrides)
    model = DeepCLIP(config).train()
    inputs = batch([7, 4], config)

    F.cross_entropy(model(**inputs), torch.tensor([0, 1])).backward()

    for name, parameter in model.named_parameters():
        assert parameter.grad is not None, name
        assert torch.isfinite(parameter.grad).all(), name


def _perturb(model, seed=1):
    """Move every zero-initialised protein layer off zero, so the protein matters."""
    generator = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        for name, parameter in model.named_parameters():
            if not name.startswith(("convs", "extra_convs", "lstm")):
                parameter.copy_(torch.randn(parameter.shape, generator=generator) * 0.5)


@pytest.mark.parametrize(
    "overrides",
    [*DESCRIPTOR_VARIANTS.values(), *TOKEN_VARIANTS.values()],
    ids=[*DESCRIPTOR_VARIANTS, *TOKEN_VARIANTS],
)
def test_the_same_lipid_scores_differently_for_two_proteins(overrides):
    """The capacity published DeepCLIP lacks: one lipid, two proteins, two answers."""
    config = make_config(**overrides)
    model = DeepCLIP(config).eval()
    _perturb(model)
    inputs = batch([6, 6], config)
    inputs["lip"][6:] = inputs["lip"][:6]

    scores = model(**inputs)[:, 1]

    assert not torch.isclose(scores[0], scores[1], atol=1e-5)


@pytest.mark.parametrize(
    "overrides", list(TOKEN_VARIANTS.values()), ids=list(TOKEN_VARIANTS)
)
def test_pocket_padding_does_not_reach_the_score(overrides):
    """Tokens past a protein's own pocket are masked: changing them changes nothing."""
    config = make_config(**overrides)
    model = DeepCLIP(config).eval()
    _perturb(model)
    inputs = batch([5, 8], config, pocket_sizes=(2, 4), longest=6)
    reference = model(**inputs)

    noisy = dict(inputs)
    noisy["pocket_tokens"] = inputs["pocket_tokens"].clone()
    noisy["pocket_tokens"][~inputs["pocket_token_mask"]] = 7.0
    assert torch.allclose(model(**noisy), reference, atol=1e-6)

    wider = dict(inputs)
    wider["pocket_tokens"] = torch.cat(
        (inputs["pocket_tokens"], torch.zeros(2, 3, POCKET_TOKEN_WIDTH)), dim=1
    )
    wider["pocket_token_mask"] = torch.cat(
        (inputs["pocket_token_mask"], torch.zeros(2, 3, dtype=torch.bool)), dim=1
    )
    assert torch.allclose(model(**wider), reference, atol=1e-5)


def test_protein_tokens_read_the_score_from_lipid_positions_only():
    config = make_config(deepclip_protein_tokens=True)
    model = DeepCLIP(config).eval()
    inputs = batch([5, 3], config, pocket_sizes=(2, 4), longest=4)

    model(**inputs)

    # Molecule 0: 2 residues, separator at 2, lipid at 3..7. Molecule 1: 4 residues,
    # separator at 4, lipid at 5..7.
    profile = model.profile
    assert torch.equal(profile[0, :3], torch.zeros(3))
    assert torch.equal(profile[1, :5], torch.zeros(5))
    assert (profile[0, 3:8] != 0).all()
    assert (profile[1, 5:8] != 0).all()


def test_hyperconv_delta_cannot_raise_every_character_at_once():
    """Centred over the alphabet: the per-protein filters keep the shared filters' sum."""
    config = make_config(deepclip_protein_hyperconv=NAMES)
    model = DeepCLIP(config).eval()
    _perturb(model)
    descriptors = torch.randn(3, 2)

    delta = torch.tanh(model.hyperconv(descriptors))
    offset = 0
    for width in model.widths:
        size = model.filters * model.conv_in * width
        part = delta[:, offset: offset + size].view(3, model.filters, model.conv_in, width)
        offset += size
        centred = part - part.mean(dim=2, keepdim=True)
        assert torch.allclose(centred.sum(dim=2), torch.zeros(3, model.filters, width), atol=1e-5)


def test_signed_gate_doubles_the_gate_range():
    assert DeepCLIP(make_config(deepclip_protein_gate=NAMES)).gate_scale == 1.0
    signed = DeepCLIP(make_config(deepclip_protein_gate=NAMES, deepclip_gate_signed=True))
    assert signed.gate_scale == 2.0


def test_protein_columns_collect_every_protein_pathway():
    config = make_config(
        deepclip_protein_gate="aromatic_share", deepclip_protein_bilinear=NAMES,
    )
    model = DeepCLIP(config)
    order = full_catalog_order(config)

    assert sorted(order[i] for i in model.protein_columns.tolist()) == sorted(
        NAMES.split(",")
    )


def test_gate_modifiers_need_the_gate():
    for flag in ("deepclip_gate_signed", "deepclip_gate_positional"):
        config = ModelConfig(
            deepclip=True, lipid_smiles_tokens=True, **{flag: True}
        )
        with pytest.raises(ValueError, match="do nothing without it"):
            config.validate()


def test_descriptor_mechanisms_need_pair_descriptors():
    config = ModelConfig(
        deepclip=True, lipid_smiles_tokens=True, deepclip_protein_film=NAMES,
        pocket_descriptors=True,
    )
    with pytest.raises(ValueError, match="add --pair_descriptors"):
        config.validate()


def test_protein_tokens_refuse_lipid_descriptors():
    config = ModelConfig(
        deepclip=True, lipid_smiles_tokens=True, deepclip_protein_tokens=True,
        pair_descriptors=True, pocket_descriptors=True,
        deepclip_lipid_descriptors="aromatic_share",
    )
    with pytest.raises(ValueError, match="pick one"):
        config.validate()


def test_new_flags_default_off_and_parse():
    defaults = ModelConfig()
    assert defaults.deepclip_protein_film == ""
    assert defaults.deepclip_protein_hyperconv == ""
    assert defaults.deepclip_protein_bilinear == ""
    assert defaults.deepclip_gate_signed is False
    assert defaults.deepclip_gate_positional is False
    assert defaults.deepclip_pocket_cross_attention is False
    assert defaults.deepclip_protein_tokens is False

    config = read_configuration([
        "train.py", "--label=deepclip_conditioning", "--deepclip",
        "--lipid_smiles_tokens", "--pair_descriptors",
        "--pocket_descriptors", f"--deepclip_protein_gate={NAMES}",
        "--deepclip_gate_signed", "--deepclip_gate_positional",
        f"--deepclip_protein_film={NAMES}", f"--deepclip_protein_hyperconv={NAMES}",
        f"--deepclip_protein_bilinear={NAMES}", "--deepclip_pocket_cross_attention",
        "--deepclip_protein_tokens",
    ])
    assert config.deepclip_gate_signed and config.deepclip_gate_positional
    assert config.deepclip_protein_film == NAMES
    assert config.deepclip_protein_hyperconv == NAMES
    assert config.deepclip_protein_bilinear == NAMES
    assert config.deepclip_pocket_cross_attention and config.deepclip_protein_tokens
