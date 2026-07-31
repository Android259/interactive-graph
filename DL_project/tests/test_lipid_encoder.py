import pytest
import torch

from architecture.lipid_encoder import Lipid_encoder
from architecture.self_attention import SelfAttention
from training.read_configuration import ModelConfig


def make_config(**overrides):
    """Build a small real ModelConfig for the lipid encoder.

    The real dataclass rather than a hand-listed stub: the encoder reads a growing set
    of config fields, and a stub only gets fixed once each new one crashes a test.
    """
    config = ModelConfig(
        lipid_isomers=False,
        lipid_fragments_mask=False,
        lipid_self_attention=False,
        lipid_disable_post_sa_mlp=False,
        lipid_gat_graph_norm=False,
        lipid_output_graph_norm=False,
        third_layers_in_mlps=False,
        hiddim=4,
        HEADS=2,
        m=2,
    )
    for key, value in overrides.items():
        setattr(config, key, value)
    return config


def test_embedding_lipid_encoder_forward_shape():
    config = make_config()
    encoder = Lipid_encoder(config)
    lipids = torch.randn(3, 768)
    attn_mask = torch.zeros((3, 3), dtype=torch.bool)

    out = encoder(lipids, None, attn_mask)

    assert out.shape == (3, config.hiddim)


def test_lipid_post_sa_mlp_can_be_disabled():
    config = make_config(lipid_disable_post_sa_mlp=True)
    encoder = Lipid_encoder(config)
    x = torch.randn(3, config.hiddim)

    assert encoder.post_sa(x) is x


def test_embedding_lipid_encoder_requires_mult_mask_for_fragment_mask():
    config = make_config(lipid_fragments_mask=True)
    encoder = Lipid_encoder(config)
    lipids = torch.randn(3, 768)
    attn_mask = torch.zeros((3, 3), dtype=torch.bool)

    with pytest.raises(AssertionError):
        encoder(lipids, None, attn_mask)


def test_isomer_graph_lipid_encoder_forward_shape():
    config = make_config(lipid_graph_isomers=True)
    encoder = Lipid_encoder(config)
    x = torch.randn(3, 11)
    edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)
    edge_attr = torch.randn(4, 6)
    attn_mask = torch.zeros((3, 3), dtype=torch.bool)

    out = encoder(x, None, attn_mask, edge_index=edge_index, edge_attr=edge_attr)

    assert out.shape == (3, config.hiddim)


def test_isomer_graph_lipid_encoder_requires_edge_tensors():
    config = make_config(lipid_graph_isomers=True)
    encoder = Lipid_encoder(config)
    x = torch.randn(3, 11)
    attn_mask = torch.zeros((3, 3), dtype=torch.bool)

    with pytest.raises(AssertionError):
        encoder(x, None, attn_mask)


def test_second_isomer_graph_lipid_encoder_uses_edges():
    config = make_config(lipid_graph_isomers=True)
    encoder = Lipid_encoder(config, start=False)
    x = torch.randn(3, config.hiddim)
    edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)
    edge_attr = torch.randn(4, 6)
    attn_mask = torch.zeros((3, 3), dtype=torch.bool)

    out = encoder(
        x,
        None,
        attn_mask,
        edge_index=edge_index,
        edge_attr=edge_attr,
        start=False,
    )

    assert out.shape == (3, config.hiddim)


def test_isomer_graph_lipid_encoder_uses_fragment_mask_with_self_attention():
    config = make_config(
        lipid_graph_isomers=True,
        lipid_fragments_mask=True,
        lipid_self_attention=True,
    )
    encoder = Lipid_encoder(config)
    x = torch.randn(4, 11)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 0, 3, 2]], dtype=torch.long)
    edge_attr = torch.randn(4, 6)
    attn_mask = torch.zeros((4, 4), dtype=torch.bool)
    fragment_ids = torch.tensor([0, 0, 1, 1])
    mult_mask = fragment_ids.unsqueeze(0) == fragment_ids.unsqueeze(1)

    out = encoder(
        x,
        None,
        attn_mask,
        mult_mask=mult_mask,
        edge_index=edge_index,
        edge_attr=edge_attr,
    )

    assert out.shape == (4, config.hiddim)


def test_fragment_attention_blocks_other_samples_and_fragments(monkeypatch):
    config = make_config(
        lipid_fragments_mask=True,
        lipid_self_attention=True,
    )
    attention = SelfAttention(config.hiddim, config)
    captured = {}

    def capture_mask(query, key, value, attn_mask, need_weights=True):
        captured["attn_mask"] = attn_mask.clone()
        return torch.zeros_like(query), None

    monkeypatch.setattr(attention.self_attention, "forward", capture_mask)
    x = torch.randn(6, config.hiddim)
    sample_ids = torch.tensor([0, 0, 0, 0, 1, 1])
    fragment_ids = torch.tensor([0, 0, 1, 1, 2, 2])
    sample_mask = sample_ids.unsqueeze(0) != sample_ids.unsqueeze(1)
    same_fragment = fragment_ids.unsqueeze(0) == fragment_ids.unsqueeze(1)

    attention(x, sample_mask, same_fragment)

    expected = sample_mask | ~same_fragment
    assert torch.equal(captured["attn_mask"], expected)
