import gc
import tracemalloc

import pytest
import torch
import torch.nn.functional as F
import torch_geometric

from architecture.interaction_classification import InteractionClassification
from architecture.loss import Non_Negative_Positive_Unlabeled_loss
from architecture.mlp_utils import export_surviving_structure
from architecture.protein_edge_geometry import (
    STRUCTURED_EDGE_DIM, rbf, structured_edge_features,
)
from dataloader.smiles_tokens import SMILES_VOCABULARY
from training.read_configuration import ModelConfig


def make_config(
    lipid_isomers=False,
    lipid_graph_isomers=False,
    lipid_mode="concat",
    lipid_self_attention=False,
):
    config = ModelConfig(
        hiddim=8,
        HEADS=2,
        m=2,
        batch=2,
        num_workers=0,
        lipid_isomers=lipid_isomers,
        lipid_graph_isomers=lipid_graph_isomers,
        lipid_self_attention=lipid_self_attention,
        pool_type="mean",
    )
    config.lipid_fragments_treatment = lipid_mode
    config.validate()
    return config


def synthetic_forward_args(config):
    prot = torch.randn(4, 3)
    if getattr(config, "rnabang_residue_type_embedding", False):
        prot[:, 0] = torch.tensor([0, 1, 18, 19], dtype=prot.dtype)
    plm_dim = 1536
    if (
        config.rnabang_replace_esm3
        or config.rnabang_full_protein_encoder
        or config.rnabang_frozen_node_adapter
    ):
        plm_dim = config.rnabang_embedding_dim
    elif config.rnabang_with_esm3 or config.rnabang_residual_with_esm3:
        plm_dim += config.rnabang_embedding_dim
    plm = torch.randn(4, plm_dim)
    bury = torch.randn(4)
    prot_batch = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    prot_edge_index = torch.tensor(
        [[0, 1, 2, 3], [1, 0, 3, 2]],
        dtype=torch.long,
    )
    prot_edge_attr = torch.randn(4, 3)

    lip_batch = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    args = {
        "config": config,
        "plm": plm,
        "bury": bury,
        "prot": prot,
        "prot_edgidx": prot_edge_index,
        "prot_e_attr": prot_edge_attr,
        "prot_batch": prot_batch,
        "lip_batch": lip_batch,
        # prot_attention_pos_bias defaults on, and the model asserts a mask is present
        # whenever it is. One pocket node per graph, since pocket pooling rejects a
        # sample with none.
        "pocket_mask": torch.tensor([True, False, True, False]),
    }
    if (
        getattr(config, "geometric_transformer", False)
        or getattr(config, "protein_edge_attention", False)
        or getattr(config, "protein_edge_mlp", False)
    ):
        args["prot_frame_rotation"] = torch.eye(3).repeat(4, 1, 1)
        args["prot_frame_translation"] = torch.randn(4, 3)
    if (
        getattr(config, "geometric_transformer", False)
        or getattr(config, "rnabang_frozen_node_adapter", False)
    ):
        edge_feature_dim = (
            43 if config.rnabang_edge_topk_by_area
            else 13 if config.rnabang_edge_pna
            else 18 if config.rnabang_edge_quantiles
            else 2
        )
        args["prot_geometric_node_attr"] = torch.randn(4, edge_feature_dim)
    if config.rnabang_frozen_node_adapter:
        args["prot_edge_node_degree"] = torch.tensor([3, 2, 4, 1])
    if config.rnabang_edge_deepsets or config.rnabang_edge_set_transformer:
        args["prot_edge_node_pairs"] = torch.randn(4, 21, 2)

    if getattr(config, "lipid_graph_isomers", False):
        args["lip"] = torch.randn(4, 11)
        args["lip_edgidx"] = torch.tensor(
            [[0, 1, 2, 3], [1, 0, 3, 2]],
            dtype=torch.long,
        )
        args["lip_e_attr"] = torch.randn(4, 22)
        if getattr(config, "cross_attention_chain_bias", False):
            args["chain_rank"] = torch.rand(4)
    else:
        # --lipid_smiles_tokens narrows a lipid node from MoLFormer's 768 to one
        # one-hot column per SMILES character; randn rather than a real one-hot is
        # enough here, since nothing in the forward path reads the values as a
        # distribution -- only the width has to match what Lipid_encoder built.
        args["lip"] = torch.randn(
            4,
            len(SMILES_VOCABULARY)
            if getattr(config, "lipid_smiles_tokens", False)
            else 768,
        )

    if config.lipid_fragments_mask:
        args["lipid_batch"] = torch.tensor([0, 0, 1, 1], dtype=torch.long)

    from dataloader.descriptors import full_catalog_order

    catalog_order = full_catalog_order(config)
    if catalog_order:
        args["descriptor_catalog_input"] = torch.randn(2, len(catalog_order))

    return args


def one_training_step(config):
    torch.manual_seed(0)
    model = InteractionClassification(config)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
    labels = torch.tensor([0, 1], dtype=torch.long)

    optimizer.zero_grad(set_to_none=True)
    out = model(**synthetic_forward_args(config))
    assert out.shape == (2, 2)
    assert torch.isfinite(out).all()

    if config.pu_loss:
        loss = Non_Negative_Positive_Unlabeled_loss(
            out,
            labels,
            config.pu_rho,
            beta=config.pu_beta,
            gamma=config.pu_gamma,
        )
    else:
        loss = F.cross_entropy(out, labels)

    assert torch.isfinite(loss)
    loss.backward()
    assert any(
        parameter.grad is not None and torch.isfinite(parameter.grad).all()
        for parameter in model.parameters()
        if parameter.requires_grad
    )
    optimizer.step()
    return float(loss.detach())


def test_fast_attention_builds_two_reused_layouts_and_skips_global_masks(monkeypatch):
    config = make_config(lipid_self_attention=True)
    config.fast_attention = True
    config.cross_attention = True
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)

    import architecture.interaction_classification as interaction_module

    original_make_layout = interaction_module.make_grouped_attention_layout
    layouts = []

    def record_layout(batch, num_graphs=None):
        layout = original_make_layout(batch, num_graphs)
        layouts.append(layout)
        return layout

    monkeypatch.setattr(
        interaction_module, "make_grouped_attention_layout", record_layout
    )

    seen_masks = {}
    original_protein_forward = model.protein1.forward
    original_lipid_forward = model.lipid1.forward
    original_cross_forward = model.cross_attention1.forward

    def protein_forward(*call_args, **kwargs):
        seen_masks["protein_self"] = call_args[7]
        return original_protein_forward(*call_args, **kwargs)

    def lipid_forward(*call_args, **kwargs):
        seen_masks["lipid_self"] = call_args[2]
        return original_lipid_forward(*call_args, **kwargs)

    def cross_forward(*call_args, **kwargs):
        seen_masks["lip_cross"] = call_args[2]
        seen_masks["protein_cross"] = call_args[3]
        return original_cross_forward(*call_args, **kwargs)

    monkeypatch.setattr(model.protein1, "forward", protein_forward)
    monkeypatch.setattr(model.lipid1, "forward", lipid_forward)
    monkeypatch.setattr(model.cross_attention1, "forward", cross_forward)

    output = model(**args)
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert len(layouts) == 2
    assert all(mask is None for mask in seen_masks.values())
    assert any(parameter.grad is not None for parameter in model.parameters())


def test_fast_attention_with_mlp_in_place_of_sa_builds_no_layouts_and_real_masks(
    monkeypatch,
):
    # --mlp_in_place_of_sa forces can_use_grouped_attention False everywhere (its
    # substitute has no in_proj_weight/out_proj for the grouped path to reach into),
    # so under --fast_attention too, interaction_classification.py must fall back to
    # building real -inf masks (not None, unlike the plain --fast_attention test just
    # above) -- ProteinSelfAttention/SelfAttention's fallback branch needs one, even
    # though the substitute itself ignores it.
    config = make_config(lipid_self_attention=True)
    config.fast_attention = True
    config.mlp_in_place_of_sa = True
    config.cross_attention = True
    config.validate()
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)

    import architecture.interaction_classification as interaction_module

    layouts = []
    original_make_layout = interaction_module.make_grouped_attention_layout

    def record_layout(batch, num_graphs=None):
        layout = original_make_layout(batch, num_graphs)
        layouts.append(layout)
        return layout

    monkeypatch.setattr(
        interaction_module, "make_grouped_attention_layout", record_layout
    )

    seen_masks = {}
    original_protein_forward = model.protein1.forward

    def protein_forward(*call_args, **kwargs):
        seen_masks["protein_self"] = call_args[7]
        return original_protein_forward(*call_args, **kwargs)

    monkeypatch.setattr(model.protein1, "forward", protein_forward)

    output = model(**args)
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert len(layouts) == 0
    assert seen_masks["protein_self"] is not None
    assert any(parameter.grad is not None for parameter in model.parameters())


@pytest.mark.parametrize(
    "config",
    [
        make_config(lipid_isomers=False, lipid_mode="concat"),
        make_config(lipid_isomers=False, lipid_mode="fragments_mask"),
        make_config(lipid_isomers=True, lipid_mode="concat"),
        make_config(lipid_isomers=True, lipid_mode="random_choice"),
        make_config(
            lipid_isomers=True,
            lipid_mode="fragments_mask",
            lipid_self_attention=True,
        ),
        make_config(lipid_graph_isomers=True, lipid_mode="concat"),
        ModelConfig(hiddim=8, HEADS=2, m=2, batch=2, num_workers=0, pu_loss=True),
    ],
)
def test_one_cpu_training_step_for_core_modes(config):
    one_training_step(config)


def test_smiles_token_lipid_branch_completes_one_cpu_training_step():
    """The character input on this project's own tower (not DeepCLIP).

    DeepCLIP is a separate network and is covered by tests/test_deepclip.py; this
    only checks that swapping MolFormer's 768 for the one-hot alphabet leaves the
    existing lipid branch trainable.
    """
    config = ModelConfig(
        hiddim=8,
        HEADS=2,
        m=2,
        batch=2,
        num_workers=0,
        pool_type="mean",
        lipid_self_attention=True,
        lipid_smiles_tokens=True,
    )
    config.lipid_fragments_treatment = "random_choice"
    config.validate()

    one_training_step(config)


@pytest.mark.parametrize(
    "config",
    [
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_replace_esm3=True,
        ),
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_full_protein_encoder=True,
            protein_self_attention=False,
        ),
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_full_protein_encoder=True,
            protein_self_attention=True,
        ),
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_with_esm3=True,
        ),
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_residual_with_esm3=True,
        ),
        ModelConfig(
            hiddim=8,
            HEADS=2,
            m=2,
            pool_type="mean",
            rnabang_frozen_node_adapter=True,
        ),
    ],
)
def test_rnabang_modes_complete_one_cpu_training_step(config):
    one_training_step(config)


@pytest.mark.parametrize(
    "mode",
    [
        "rnabang_replace_esm3",
        "rnabang_full_protein_encoder",
        "rnabang_with_esm3",
        "rnabang_residual_with_esm3",
        "rnabang_frozen_node_adapter",
    ],
)
def test_rnabang_modes_have_no_unreachable_trainable_parameters(mode):
    config = make_config()
    setattr(config, mode, True)
    config.validate()
    model = InteractionClassification(config)

    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    unused = [
        name
        for name, parameter in model.named_parameters()
        if parameter.requires_grad and parameter.grad is None
    ]
    assert unused == []


def test_rnabang_residual_mode_replaces_gatv2_and_uses_all_protein_inputs():
    config = ModelConfig(
        hiddim=8,
        HEADS=2,
        m=2,
        pool_type="mean",
        rnabang_residual_with_esm3=True,
        protein_self_attention=False,
        double_attention=True,
        dropout=0.0,
    )
    model = InteractionClassification(config).eval()
    assert not any(
        isinstance(module, torch_geometric.nn.GATv2Conv)
        for module in model.protein1.modules()
    )
    assert not any(
        isinstance(module, torch_geometric.nn.GATv2Conv)
        for module in model.protein2.modules()
    )
    assert model.protein1.encodin1 is None
    assert model.protein1.encodin2 is None
    assert model.protein2.encodin1 is None
    assert model.protein2.encodin2 is None

    args = synthetic_forward_args(config)
    with torch.no_grad():
        model.protein1.rnabang_residual_alpha.fill_(1.0)
        reference = model(**args)
        for field in ("plm", "prot", "bury", "prot_e_attr"):
            changed = dict(args)
            changed[field] = args[field] + 1.0
            assert not torch.allclose(reference, model(**changed))


def test_rnabang_frozen_node_adapter_has_no_graph_or_ipa_layer():
    config = make_config()
    config.rnabang_frozen_node_adapter = True
    model = InteractionClassification(config)

    assert not any(
        isinstance(module, torch_geometric.nn.GATv2Conv)
        for module in model.protein1.modules()
    )
    assert not hasattr(model.protein1, "geometric_block")
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()
    assert all(
        parameter.grad is not None
        for parameter in model.protein1.rnabang_node_adapter.parameters()
    )


@pytest.mark.parametrize(
    "mode",
    [
        "rnabang_edge_current",
        "rnabang_edge_topk_by_area",
        "rnabang_edge_deepsets",
        "rnabang_edge_pna",
        "rnabang_edge_quantiles",
        "rnabang_edge_set_transformer",
    ],
)
def test_rnabang_edge_to_node_modes_train(mode):
    config = make_config()
    config.rnabang_frozen_node_adapter = True
    setattr(config, mode, True)
    one_training_step(config)


def test_rnabang_residue_type_embedding_trains_only_when_enabled():
    config = make_config()
    config.rnabang_frozen_node_adapter = True
    config.rnabang_residue_type_embedding = True
    one_training_step(config)
    model = InteractionClassification(config)
    assert model.protein1.residue_type_embedding.num_embeddings == 20
    assert model.protein1.residue_type_embedding.embedding_dim == 8


def test_double_attention_isomer_graph_training_step():
    config = make_config(lipid_graph_isomers=True, lipid_mode="concat")
    config.double_attention = True

    one_training_step(config)


def test_optional_attention_modules_are_created_only_when_used():
    base_config = make_config()
    base_config.cross_attention = False
    base = InteractionClassification(base_config)
    assert not hasattr(base, "cross_attention1")
    assert not hasattr(base, "lipid2")
    assert not hasattr(base, "protein2")
    assert not hasattr(base, "cross_attention2")

    cross_config = make_config()
    cross_config.cross_attention = True
    cross = InteractionClassification(cross_config)
    assert hasattr(cross, "cross_attention1")
    assert not hasattr(cross, "cross_attention2")

    double_config = make_config()
    double_config.double_attention = True
    double = InteractionClassification(double_config)
    assert hasattr(double, "cross_attention1")
    assert hasattr(double, "lipid2")
    assert hasattr(double, "protein2")
    assert hasattr(double, "cross_attention2")


def test_single_gat_layer_skips_second_protein_gat():
    config = make_config()
    config.single_gat_layer = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )
    # Not merely unused -- not built, so it cannot inflate the parameter count.
    assert model.protein1.encodin2 is None


def test_transformer_conv_protein_encoder_forward_backward():
    config = make_config()
    config.transformer_conv = True
    # Both convs must exist for this to check the type is applied to each of them.
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.protein1.encodin1.__class__.__name__ == "TransformerConv"
    assert model.protein1.encodin2.__class__.__name__ == "TransformerConv"
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin2.parameters()
    )


def test_geometric_transformer_replaces_gat_and_backpropagates():
    config = make_config()
    config.geometric_transformer = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert not hasattr(model.protein1, "encodin1")
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.geometric_block.parameters()
    )


def test_fast_geometric_transformer_matches_full_attention():
    config = make_config()
    config.geometric_transformer = True
    model = InteractionClassification(config).eval()
    args = synthetic_forward_args(config)
    with torch.no_grad():
        reference = model(**args)
        config.fast_attention = True
        fast = model(**args)
    torch.testing.assert_close(fast, reference, atol=1e-5, rtol=1e-5)


def test_fast_geometric_transformer_chunking_is_exact():
    config = make_config()
    config.geometric_transformer = True
    config.fast_attention = True
    model = InteractionClassification(config).eval()
    args = synthetic_forward_args(config)
    with torch.no_grad():
        config.geometric_ipa_chunk_size = 1
        chunked = model(**args)
        config.geometric_ipa_chunk_size = 0
        unchunked = model(**args)
    torch.testing.assert_close(chunked, unchunked, atol=1e-6, rtol=1e-6)


def test_gine_conv_protein_encoder_forward_backward():
    config = make_config()
    config.gine_conv = True
    # Both convs must exist for this to check the type is applied to each of them.
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.protein1.encodin1.__class__.__name__ == "GINEConv"
    assert model.protein1.encodin2.__class__.__name__ == "GINEConv"
    assert model.protein1.gat_ln.normalized_shape == (config.hiddim,)
    assert model.protein1.mlp[0].in_features == config.hiddim
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin2.parameters()
    )


def test_gine_conv_can_use_pre_conv_residual_projection():
    config = make_config()
    config.gine_conv = True
    config.protein_gine_residual = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.protein1.gine_residual1.__class__.__name__ == "Linear"
    assert model.protein1.gine_residual1.out_features == config.hiddim
    assert model.protein1.gine_residual1.weight.grad is not None


def test_protein_pre_sa_mlp_can_be_disabled_with_gine_conv():
    config = make_config()
    config.gine_conv = True
    config.protein_self_attention = True
    config.protein_disable_pre_sa_mlp = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert all(parameter.grad is None for parameter in model.protein1.mlp.parameters())
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.attention.parameters()
    )


def _random_rotations(n):
    matrices = torch.linalg.qr(torch.randn(n, 3, 3)).Q
    matrices[:, :, 0] *= torch.sign(torch.det(matrices)).unsqueeze(-1)
    return matrices


def test_rbf_shape_and_peak_bin():
    distance = torch.tensor([2.0, 12.0, 22.0])
    values = rbf(distance)
    assert values.shape == (3, 16)
    # bin 0 is centered at d_min=2, bin 15 at d_max=22 -- each endpoint distance
    # should peak its own nearest-center bin.
    assert values[0].argmax().item() == 0
    assert values[2].argmax().item() == 15


def test_structured_edge_features_shape_and_bidirectional_orientation():
    torch.manual_seed(0)
    frame_rotation = _random_rotations(3)
    frame_translation = torch.randn(3, 3) * 5
    edge_index = torch.tensor([[0, 1], [1, 2]])
    edge_attr = torch.tensor([[7.0, 3.0, 1.0], [8.0, 4.0, 2.0]])

    bidi_index, bidi_attr = structured_edge_features(
        edge_index, frame_rotation, frame_translation, edge_attr
    )
    assert bidi_index.shape == (2, 4)
    assert bidi_attr.shape == (4, STRUCTURED_EDGE_DIM)

    # Forward edge 0 (0->1) and its native reverse (1->0, at index 2) must carry
    # the same quaternion real part and negated vector part (conjugate), not a
    # naive copy -- copying would break under the direction-dependent formula.
    forward_quat = bidi_attr[0, 19:23]
    backward_quat = bidi_attr[2, 19:23]
    assert torch.allclose(forward_quat[0], backward_quat[0], atol=1e-5)
    assert torch.allclose(forward_quat[1:], -backward_quat[1:], atol=1e-5)


def test_protein_edge_attention_forward_backward():
    config = make_config()
    config.protein_edge_attention = True
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.protein1.encodin1.__class__.__name__ == "EdgeAttentionConv"
    assert model.protein1.encodin2.__class__.__name__ == "EdgeAttentionConv"
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin2.parameters()
    )


def test_protein_edge_mlp_forward_backward():
    config = make_config()
    config.protein_edge_mlp = True
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.protein1.encodin1.__class__.__name__ == "EdgeMLPConv"
    assert model.protein1.encodin2.__class__.__name__ == "EdgeMLPConv"
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin2.parameters()
    )


def test_protein_edge_rbf_count_forward_backward():
    config = make_config()
    config.protein_edge_mlp = True
    config.protein_edge_rbf_count = 4
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    expected_edge_dim = 4 + 3 + 4 + 1 + 1
    node_in_features = model.protein1.encodin1.mlp[0].in_features - expected_edge_dim
    assert node_in_features > 0
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )


def test_protein_edge_orientation_scalar_forward_backward():
    config = make_config()
    config.protein_edge_attention = True
    config.protein_edge_orientation_scalar = True
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    expected_edge_dim = 16 + 3 + 1 + 1 + 1
    node_in_features = model.protein1.encodin1.k_proj.in_features - expected_edge_dim
    assert node_in_features > 0
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )


def test_protein_edge_raw3_forward_backward():
    config = make_config()
    config.protein_edge_mlp = True
    config.protein_edge_raw3 = True
    config.single_gat_layer = False
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    node_in_features = model.protein1.encodin1.mlp[0].in_features - 3
    assert node_in_features > 0
    assert any(
        parameter.grad is not None
        for parameter in model.protein1.encodin1.parameters()
    )


def test_lipid_edge_attention_forward_backward():
    config = make_config(lipid_graph_isomers=True, lipid_mode="concat")
    config.protein_edge_attention = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.lipid1.encodin1.__class__.__name__ == "EdgeAttentionConv"
    assert any(
        parameter.grad is not None
        for parameter in model.lipid1.encodin1.parameters()
    )


def test_lipid_edge_mlp_forward_backward():
    config = make_config(lipid_graph_isomers=True, lipid_mode="concat")
    config.protein_edge_mlp = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    assert model.lipid1.encodin1.__class__.__name__ == "EdgeMLPConv"
    assert any(
        parameter.grad is not None
        for parameter in model.lipid1.encodin1.parameters()
    )


@pytest.mark.parametrize("fast", [True, False])
def test_cross_attention_bury_bias_trains(fast):
    config = make_config()
    config.cross_attention_bury_bias = True
    config.fast_attention = fast
    config.validate()
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    loss = F.cross_entropy(output, torch.tensor([0, 1]))
    assert loss == loss
    loss.backward()
    assert model.cross_attention1.bury_bias_scale.grad is not None


@pytest.mark.parametrize("fast", [True, False])
def test_cross_attention_chain_bias_trains(fast):
    config = make_config(lipid_graph_isomers=True, lipid_mode="concat")
    config.cross_attention_chain_bias = True
    config.fast_attention = fast
    config.validate()
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    loss = F.cross_entropy(output, torch.tensor([0, 1]))
    assert loss == loss
    loss.backward()
    assert model.cross_attention1.chain_bias_scale.grad is not None


def test_cross_attention_chain_bias_requires_lipid_graph_isomers():
    config = make_config()
    config.cross_attention_chain_bias = True
    with pytest.raises(ValueError, match="lipid_graph_isomers"):
        config.validate()


def test_protein_edge_modes_reject_bidirectional_edges():
    config = make_config()
    config.protein_edge_attention = True
    config.bidirectional_edges = True
    with pytest.raises(ValueError, match="bidirectional_edges"):
        config.validate()


def test_protein_edge_modes_are_mutually_exclusive_with_other_convs():
    config = make_config()
    config.protein_edge_mlp = True
    config.gine_conv = True
    with pytest.raises(ValueError, match="mutually exclusive"):
        config.validate()


def test_protein_edge_rbf_count_requires_edge_mode():
    config = make_config()
    config.protein_edge_rbf_count = 4
    with pytest.raises(ValueError, match="protein_edge_rbf_count"):
        config.validate()


def test_protein_edge_raw3_rejects_rbf_count_override():
    config = make_config()
    config.protein_edge_mlp = True
    config.protein_edge_raw3 = True
    config.protein_edge_rbf_count = 4
    with pytest.raises(ValueError, match="protein_edge_raw3"):
        config.validate()


def test_protein_post_sa_mlp_can_be_disabled():
    config = make_config()
    config.protein_self_attention = True
    config.protein_disable_post_sa_mlp = True
    model = InteractionClassification(config)
    x = torch.randn(3, config.hiddim)

    assert model.protein1.post_sa(x) is x


def test_plm_compression_dim_changes_protein_projection_width():
    config = make_config()
    config.plm_compression_dim = 16
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))

    assert output.shape == (2, 2)
    assert model.protein1.enc_plm.out_features == 16


def test_plm_sequential_compression_uses_fixed_projection_layers():
    config = make_config()
    config.plm_sequential_compression = True
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    linear_layers = [
        layer for layer in model.protein1.enc_plm if isinstance(layer, torch.nn.Linear)
    ]

    assert output.shape == (2, 2)
    assert [(layer.in_features, layer.out_features) for layer in linear_layers] == [
        (1536, 512),
        (512, 171),
        (171, 57),
        (57, config.plm_compression_dim),
    ]


def test_plm_compression_dims_are_configurable():
    config = make_config()
    config.plm_sequential_compression = True
    config.plm_compression_dims = [256, 64]
    model = InteractionClassification(config)
    linear_layers = [
        layer for layer in model.protein1.enc_plm if isinstance(layer, torch.nn.Linear)
    ]

    assert [(layer.in_features, layer.out_features) for layer in linear_layers] == [
        (1536, 256),
        (256, 64),
        (64, config.plm_compression_dim),
    ]


def test_final_layer_uses_legacy_m_when_final_m_is_not_set():
    config = make_config()
    config.final_m = None
    model = InteractionClassification(config)
    linear_layers = [
        layer for layer in model.final_layer.binar if isinstance(layer, torch.nn.Linear)
    ]

    assert [(layer.in_features, layer.out_features) for layer in linear_layers] == [
        (16, 16),
        (16, 8),
        (8, 2),
    ]


def test_final_m_changes_only_final_classifier_width():
    config = make_config()
    config.final_m = 1
    model = InteractionClassification(config)
    linear_layers = [
        layer for layer in model.final_layer.binar if isinstance(layer, torch.nn.Linear)
    ]

    assert [(layer.in_features, layer.out_features) for layer in linear_layers] == [
        (16, 8),
        (8, 8),
        (8, 2),
    ]
    assert model.protein1.mlp[0].out_features == config.m * config.hiddim


def test_final_layer_can_concatenate_add_and_max_pooling():
    config = make_config()
    config.pool_type = "add_max"
    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    linear_layers = [
        layer for layer in model.final_layer.binar if isinstance(layer, torch.nn.Linear)
    ]

    assert output.shape == (2, 2)
    assert linear_layers[0].in_features == 4 * config.hiddim


def test_final_dropout_is_optional_and_applies_only_to_final_classifier():
    base = InteractionClassification(make_config())
    assert not any(
        isinstance(layer, torch.nn.Dropout) for layer in base.final_layer.binar
    )

    config = make_config()
    config.final_dropout = 0.2
    model = InteractionClassification(config)
    dropout_layers = [
        layer for layer in model.final_layer.binar if isinstance(layer, torch.nn.Dropout)
    ]

    assert [layer.p for layer in dropout_layers] == [0.2, 0.2]
    assert not any(
        isinstance(module, torch.nn.Dropout)
        for name, module in model.named_modules()
        if not name.startswith("final_layer")
    )


@pytest.mark.parametrize("mode", ["base", "cross", "double"])
def test_active_configuration_has_no_parameters_without_gradients(mode):
    config = make_config()
    if mode == "cross":
        config.cross_attention = True
    elif mode == "double":
        config.double_attention = True

    model = InteractionClassification(config)
    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()

    unused = [
        name
        for name, parameter in model.named_parameters()
        if parameter.requires_grad and parameter.grad is None
    ]
    assert unused == []


def heads_config(heads, **flags):
    config = make_config()
    config.descriptor_heads = heads
    for name, value in flags.items():
        setattr(config, name, value)
    config.validate()
    return config


def assert_every_parameter_gets_a_gradient(model):
    output = model(**synthetic_forward_args(model.config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()
    unused = [
        name for name, parameter in model.named_parameters()
        if parameter.requires_grad and parameter.grad is None
    ]
    assert unused == []


def test_descriptor_heads_alongside_the_towers_train_and_get_gradients():
    from architecture.named_descriptor_head import NamedDescriptorHead

    config = heads_config("chain,unsaturation,aromatic_share")
    model = InteractionClassification(config)
    # Without a sufficiency-test flag the normal towers are still built.
    assert hasattr(model, "protein1")
    assert hasattr(model, "lipid1")
    assert hasattr(model, "cross_attention1")
    head = model.final_layer.descriptor_head
    assert isinstance(head, NamedDescriptorHead)
    assert head.token_names == ("chain", "unsaturation", "aromatic_share")
    assert len(model.final_layer.descriptor_extra_heads) == 0

    loss = one_training_step(config)
    assert loss == loss  # not NaN
    assert_every_parameter_gets_a_gradient(model)


def test_one_head_adds_no_state_dict_key_beyond_the_single_head():
    """A checkpoint saved with one head keeps the keys it was saved under:
    descriptor_head.* and nothing for the (empty) list of extra heads."""
    model = InteractionClassification(heads_config("chain,unsaturation"))
    keys = model.final_layer.state_dict().keys()
    assert any(key.startswith("descriptor_head.") for key in keys)
    assert not any(key.startswith("descriptor_extra_heads") for key in keys)


def test_descriptor_heads_reject_bilinear_fusion():
    config = make_config()
    config.descriptor_heads = "chain,unsaturation"
    config.bilinear_fusion = True
    with pytest.raises(ValueError, match="bilinear_fusion"):
        config.validate()


def test_descriptor_heads_separator_needs_no_quotes():
    from dataloader.descriptors import full_catalog_order, parse_descriptor_heads
    from training.read_configuration import read_configuration

    config = read_configuration(
        ["x", "--descriptors_head", "--descriptor_heads=chain,unsaturation/tpsa,heavy",
         "--double_coldsplit", "--excluded_groups=START"]
    )
    assert parse_descriptor_heads(config.descriptor_heads) == (
        ("chain", "unsaturation"), ("tpsa", "heavy"),
    )
    # One sorted, deduplicated column order for every head and encoder to index into.
    assert full_catalog_order(config) == ("chain", "heavy", "tpsa", "unsaturation")


def test_wrapped_arg_file_line_does_not_leave_an_empty_head():
    """scripts/lib/args_file_lib.sh joins a wrapped value with a comma, so a line that
    ends in the separator reaches the parser as "a,b/,c,d"."""
    from dataloader.descriptors import parse_descriptor_heads

    assert parse_descriptor_heads("chain,hbond/,tpsa,heavy") == (
        ("chain", "hbond"), ("tpsa", "heavy"),
    )


def test_protein_descriptors_broadcasts_onto_protein_nodes_and_trains():
    config = make_config()
    config.protein_descriptors = "chain,unsaturation,aromatic_share"
    config.validate()

    model = InteractionClassification(config)
    assert model.protein1.protein_descriptor_columns.shape == (3,)

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_lipid_descriptors_broadcasts_onto_lipid_nodes_and_trains():
    config = make_config()
    config.lipid_descriptors = "chain,unsaturation,hydropathy_core"
    config.validate()

    model = InteractionClassification(config)
    assert model.lipid1.lipid_descriptor_columns.shape == (3,)

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_node_broadcast_and_descriptor_heads_share_one_catalog_order_and_coexist():
    config = heads_config(
        "chain,unsaturation", protein_descriptors="chain,hbond", lipid_descriptors="heavy",
    )
    model = InteractionClassification(config)
    catalog = ("chain", "hbond", "heavy", "unsaturation")
    from dataloader.descriptors import full_catalog_order

    assert full_catalog_order(config) == catalog
    assert model.protein1.protein_descriptor_columns.tolist() == [0, 1]
    assert model.lipid1.lipid_descriptor_columns.tolist() == [2]

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_protein_descriptors_rejects_unknown_descriptor_name():
    config = make_config()
    config.protein_descriptors = "not_a_real_descriptor"
    with pytest.raises(ValueError, match="Unknown descriptor name"):
        config.validate()


def test_no_protein_geometry_requires_protein_descriptors():
    config = make_config()
    config.no_protein_geometry = True
    with pytest.raises(ValueError, match="no_protein_geometry"):
        config.validate()
    config.protein_descriptors = "pocket_extent"
    config.validate()


@pytest.mark.parametrize("mode", ["descriptors_head", "descriptor_mlp"])
def test_head_modes_require_descriptor_heads(mode):
    config = make_config()
    setattr(config, mode, True)
    with pytest.raises(ValueError, match="requires --descriptor_heads"):
        config.validate()


def test_descriptors_head_builds_no_encoder_or_cross_attention_modules():
    config = heads_config("chain,unsaturation,aromatic_share", descriptors_head=True)
    model = InteractionClassification(config)
    assert not hasattr(model, "lipid1")
    assert not hasattr(model, "protein1")
    assert not hasattr(model, "cross_attention1")
    assert hasattr(model.final_layer, "descriptor_head")

    loss = one_training_step(config)
    assert loss == loss  # not NaN
    assert_every_parameter_gets_a_gradient(model)


def test_two_heads_build_two_named_heads_and_no_towers():
    config = heads_config("chain,extent,polar_share/pocket_extent,heavy", descriptors_head=True)
    model = InteractionClassification(config)
    assert not hasattr(model, "lipid1")
    assert not hasattr(model, "protein1")
    assert not hasattr(model, "cross_attention1")
    final_layer = model.final_layer
    assert final_layer.descriptor_head.token_names == ("chain", "extent", "polar_share")
    assert len(final_layer.descriptor_extra_heads) == 1
    assert final_layer.descriptor_extra_heads[0].token_names == ("pocket_extent", "heavy")

    loss = one_training_step(config)
    assert loss == loss  # not NaN
    assert_every_parameter_gets_a_gradient(model)


def test_two_heads_wire_coarse_tokens_correctly():
    # <name>_coarse=<spec> tokens (dataloader.descriptors.parse_descriptor_token) must
    # reach NamedDescriptorHead as CANONICAL tokens and index into the SAME shared
    # column order on both heads -- this pins that wiring (not the coarsening
    # arithmetic itself, which dataloader/Dataloader.py owns and this synthetic-tensor
    # harness bypasses; that path is exercised separately against real data).
    config = heads_config(
        "chain,aromatic_share_coarse=5/pocket_extent_coarse=quantiles,heavy_coarse=quantiles:3",
        descriptors_head=True,
    )
    model = InteractionClassification(config)
    assert model.final_layer.descriptor_head.token_names == (
        "chain", "aromatic_share_coarse=5",
    )
    # heavy_coarse=quantiles:3 canonicalises identically to pocket_extent_coarse=
    # quantiles (both default to DEFAULT_QUANTILE_BINS=3) -- pinning the exact
    # string confirms the two heads and the shared catalog_order all agree on it.
    assert model.final_layer.descriptor_extra_heads[0].token_names == (
        "pocket_extent_coarse=quantiles:3", "heavy_coarse=quantiles:3",
    )

    loss = one_training_step(config)
    assert loss == loss  # not NaN
    assert_every_parameter_gets_a_gradient(model)


@pytest.mark.parametrize("pool_type", ["mean", "max", "add_max", "gem"])
@pytest.mark.parametrize("head_mode", [False, True])
def test_two_heads_train_under_every_pool_type(pool_type, head_mode):
    config = heads_config(
        "chain,extent/pocket_extent,heavy", pool_type=pool_type, descriptors_head=head_mode,
    )
    assert_every_parameter_gets_a_gradient(InteractionClassification(config))


def test_descriptor_heads_reject_unknown_descriptor_name():
    config = make_config()
    config.descriptor_heads = "chain/not_a_real_descriptor"
    with pytest.raises(ValueError, match="Unknown descriptor"):
        config.validate()


@pytest.mark.parametrize("pool_type", ["add", "max", "mean", "gem"])
def test_descriptor_head_pool_type_output_matches_hiddim(pool_type):
    config = heads_config("chain,unsaturation", pool_type=pool_type)
    head = InteractionClassification(config).final_layer.descriptor_head
    assert head.output_dim == config.hiddim
    if pool_type == "gem":
        assert hasattr(head, "gem_pool")

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_descriptor_head_pool_type_add_max_doubles_output_dim():
    config = heads_config("chain,unsaturation", pool_type="add_max")
    head = InteractionClassification(config).final_layer.descriptor_head
    assert head.output_dim == 2 * config.hiddim

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_descriptors_head_rejects_the_full_architecture_options():
    config = make_config()
    config.descriptor_heads = "chain,unsaturation"
    config.descriptors_head = True
    config.dann_family = True
    with pytest.raises(ValueError, match="descriptors_head"):
        config.validate()


def test_head_modes_conflict_with_each_other():
    config = make_config()
    config.descriptor_heads = "chain"
    config.descriptors_head = True
    config.descriptor_mlp = True
    with pytest.raises(ValueError, match="different sufficiency-test branches"):
        config.validate()


def test_mlp_in_place_of_sa_replaces_descriptor_head_attention():
    config = heads_config("chain,unsaturation", descriptors_head=True, mlp_in_place_of_sa=True)
    model = InteractionClassification(config)
    assert not isinstance(
        model.final_layer.descriptor_head.attention, torch.nn.MultiheadAttention
    )

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_mlp_in_place_of_sa_replaces_self_attention_and_still_trains():
    config = make_config(lipid_self_attention=True)
    config.mlp_in_place_of_sa = True
    config.validate()

    model = InteractionClassification(config)
    assert not isinstance(
        model.protein1.attention.self_attention, torch.nn.MultiheadAttention
    )
    assert not isinstance(
        model.lipid1.attention.self_attention, torch.nn.MultiheadAttention
    )

    loss = one_training_step(config)
    assert loss == loss  # not NaN


def test_mlp_in_place_of_sa_does_not_leave_pocket_attention_bias_ungradiented():
    # Regression test: prot_attention_pos_bias defaults True, so pocket_attention_bias
    # (architecture/self_attention.py) is built by default -- but AttentionMLPSubstitute
    # never reads the attn_mask it would be folded into, so building it under
    # --mlp_in_place_of_sa left it permanently without a gradient (the exact failure
    # test_active_configuration_has_no_parameters_without_gradients exists to catch,
    # just never parametrized with this flag).
    config = make_config()
    config.mlp_in_place_of_sa = True
    config.validate()

    model = InteractionClassification(config)
    assert not hasattr(model.protein1.attention, "pocket_attention_bias")

    output = model(**synthetic_forward_args(config))
    F.cross_entropy(output, torch.tensor([0, 1])).backward()
    unused = [
        name for name, parameter in model.named_parameters()
        if parameter.requires_grad and parameter.grad is None
    ]
    assert unused == []


def mlp_config(**flags):
    return heads_config("chain,unsaturation,aromatic_share", descriptor_mlp=True, **flags)


def test_descriptor_mlp_needs_exactly_one_head():
    config = make_config()
    config.descriptor_mlp = True
    config.descriptor_heads = "chain/unsaturation"
    with pytest.raises(ValueError, match="exactly one"):
        config.validate()


def test_descriptor_mlp_builds_no_encoder_or_cross_attention_modules():
    from architecture.descriptor_mlp_head import DescriptorMLPHead

    config = mlp_config()
    model = InteractionClassification(config)
    assert not hasattr(model, "lipid1")
    assert not hasattr(model, "protein1")
    assert not hasattr(model, "cross_attention1")
    assert isinstance(model.final_layer.descriptor_mlp_head, DescriptorMLPHead)
    assert model.final_layer.descriptor_mlp_head.token_names == (
        "chain", "unsaturation", "aromatic_share",
    )
    assert model.final_layer.descriptor_mlp_head.token_count == 3

    loss = one_training_step(config)
    assert loss == loss  # not NaN
    assert_every_parameter_gets_a_gradient(model)


def test_descriptor_mlp_rejects_the_full_architecture_options():
    config = make_config()
    config.descriptor_mlp = True
    config.descriptor_heads = "chain,unsaturation,aromatic_share"
    config.dann_family = True
    with pytest.raises(ValueError, match="descriptor_mlp"):
        config.validate()


def test_descriptor_mlp_does_not_build_named_descriptor_head():
    """The whole point: DescriptorMLPHead in place of NamedDescriptorHead's shared
    per-token Linear(1, dim) embedding (files/results/descriptors_head_bottleneck.md)."""
    from architecture.named_descriptor_head import NamedDescriptorHead

    model = InteractionClassification(mlp_config())
    assert not isinstance(model.final_layer.descriptor_mlp_head, NamedDescriptorHead)
    assert not hasattr(model.final_layer, "descriptor_head")


def test_single_attention_pooling_uses_only_pocket_nodes():
    config = make_config()
    config.protein_pooling = "pooling_by_pockets"
    config.validate()
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)
    args["pocket_mask"] = torch.tensor([True, False, True, False])
    pooled = {}

    def capture_final_inputs(_module, inputs):
        pooled["protein_nodes"] = inputs[1].shape[0]
        pooled["protein_batch"] = inputs[3].tolist()

    handle = model.final_layer.register_forward_pre_hook(capture_final_inputs)
    output = model(**args)
    handle.remove()

    assert output.shape == (2, 2)
    assert pooled == {"protein_nodes": 2, "protein_batch": [0, 1]}


def test_pocket_pooling_rejects_sample_without_pocket_nodes():
    config = make_config()
    config.protein_pooling = "pooling_by_pockets"
    config.validate()
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)
    args["pocket_mask"] = torch.tensor([True, False, False, False])

    with pytest.raises(ValueError, match=r"without pocket nodes.*\[1\]"):
        model(**args)


def test_no_unbounded_python_memory_growth_in_repeated_cpu_steps():
    config = make_config(
        lipid_isomers=True,
        lipid_mode="fragments_mask",
        lipid_self_attention=True,
    )

    gc.collect()
    tracemalloc.start()
    for _ in range(3):
        one_training_step(config)
    gc.collect()
    _, warm_peak = tracemalloc.get_traced_memory()

    for _ in range(3):
        one_training_step(config)
    gc.collect()
    current, second_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert current < 2_000_000
    assert second_peak - warm_peak < 2_000_000


def test_gate_all_mlp_layers_gates_block_input_and_output():
    config = make_config()
    config.third_layers_in_mlps = True
    config.dropout = 0.1  # gate indices below assume a dropout module per hidden site
    config.gate_all_mlp_layers = True
    model = InteractionClassification(config)
    report = export_surviving_structure(model)

    # One gate per representation boundary of the block: input, both hidden, output.
    assert {
        name: info["total"]
        for name, info in report.items()
        if name.startswith("protein1.mlp.")
    } == {
        "protein1.mlp.0": config.hiddim * config.HEADS,
        "protein1.mlp.4": config.hiddim * config.m,
        "protein1.mlp.8": config.hiddim * config.m,
        "protein1.mlp.12": config.hiddim,
    }


def test_gate_all_mlp_hidden_leaves_block_boundaries_ungated():
    config = make_config()
    config.third_layers_in_mlps = True
    config.dropout = 0.1  # gate indices below assume a dropout module per hidden site
    config.gate_all_mlp_hidden = True
    model = InteractionClassification(config)
    report = export_surviving_structure(model)

    assert {
        name: info["total"]
        for name, info in report.items()
        if name.startswith("protein1.mlp.")
    } == {
        "protein1.mlp.3": config.hiddim * config.m,
        "protein1.mlp.7": config.hiddim * config.m,
    }


def test_no_ffns_removes_feed_forward_blocks():
    config = make_config(lipid_self_attention=True)
    config.cross_attention = True
    config.no_ffns = True
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)
    args["pocket_mask"] = torch.tensor([True, False, True, False])
    output = model(**args)

    assert output.shape == (2, 2)
    assert model.protein1.attention.FFN is None
    assert model.lipid1.attention.FFN is None
    assert model.cross_attention1.lipFFN is None
    assert model.cross_attention1.protFFN is None
    assert not any("FFN" in name for name, _ in model.named_parameters())


def test_mlp_widths_set_deterministic_layer_widths():
    config = make_config()
    config.third_layers_in_mlps = True
    config.mlp_widths = {"protein_mlp": 13, "protein_mlp_third": 7, "final": 11}
    model = InteractionClassification(config)
    args = synthetic_forward_args(config)
    args["pocket_mask"] = torch.tensor([True, False, True, False])
    output = model(**args)
    shapes = lambda block: [
        (layer.in_features, layer.out_features)
        for layer in block
        if isinstance(layer, torch.nn.Linear)
    ]

    assert output.shape == (2, 2)
    assert shapes(model.protein1.mlp) == [
        (config.hiddim * config.HEADS, 13),
        (13, 7),
        (7, config.hiddim),
    ]
    assert shapes(model.final_layer.binar) == [
        (2 * config.hiddim, 11),
        (11, 11),  # _third defaults to the site's own width
        (11, config.hiddim),
        (config.hiddim, 2),
    ]
    # An unset site keeps m * hiddim.
    assert shapes(model.protein1.attention.FFN)[0][1] == config.m * config.hiddim


def test_adv_deep_matches_the_cross_attention_block_it_replaces():
    """The deep adversary is sized to the block it must keep honest, not to m.

    A shallow probe loses to cross-attention by an order of magnitude, so leakage it
    cannot decode survives the reversal. The replacement mirrors one side of the block
    -- an MLP for the multihead part, the FFN itself, both LayerNorms, both residuals --
    and its hidden width of 2 * dim spends 4 * dim^2 on Linears, the same budget as the
    Q/K/V/O projections.
    """
    from architecture.cross_attention import CrossAttention

    config = make_config()
    config.adversarial_grl = True
    config.adv_deep = True
    model = InteractionClassification(config)
    adversary = model.final_layer.lip_adversary

    cross = CrossAttention(config.hiddim, config.hiddim, config)
    one_side = sum(
        parameter.numel()
        for module in (
            cross.lip_cross_attention,
            cross.lipFFN,
            cross.lip_ln1,
            cross.lip_ln2,
        )
        for parameter in module.parameters()
    )
    adversary_size = sum(parameter.numel() for parameter in adversary.parameters())
    head_size = sum(parameter.numel() for parameter in adversary.head.parameters())

    # Exact, not approximate: both spend 4 * dim^2 on the substituted part and share the
    # FFN and LayerNorms, so the only gap is bias count -- MHA carries 4 * dim of bias
    # across Q/K/V/O against the substitute MLP's 3 * dim. The binary head is extra on
    # the adversary side because the block itself does not classify.
    assert adversary_size - head_size == one_side - config.hiddim

    shallow_config = make_config()
    shallow_config.adversarial_grl = True
    shallow = InteractionClassification(shallow_config).final_layer.lip_adversary
    assert sum(parameter.numel() for parameter in shallow.parameters()) < adversary_size


def test_adversary_reversal_scales_with_the_ramped_lambda():
    config = make_config()
    config.adversarial_grl = True
    model = InteractionClassification(config)
    model.train()

    # One fixed input across all three lambdas, so the only thing varying is the
    # reversal strength.
    args = synthetic_forward_args(config)
    args["lip"] = args["lip"].requires_grad_(True)

    gradients = {}
    for lam in (0.0, 0.5, 1.0):
        model.final_layer.adv_lambda_now = lam
        model.zero_grad(set_to_none=True)
        args["lip"].grad = None
        model(**args)
        lip_logits, prot_logits = model.final_layer._adv
        (lip_logits.sum() + prot_logits.sum()).backward()
        gradients[lam] = args["lip"].grad.abs().sum().item()

    # lambda = 0 severs the adversary from the encoder; the rest scales linearly.
    assert gradients[0.0] == 0.0
    assert gradients[1.0] == pytest.approx(2.0 * gradients[0.5], rel=1e-4)


def test_adversary_is_inert_outside_training():
    config = make_config()
    config.adversarial_grl = True
    model = InteractionClassification(config)
    model.eval()

    model(**synthetic_forward_args(config))

    # No stale logits for the training loop to add to the task loss.
    assert model.final_layer._adv is None


@pytest.mark.parametrize("class_conditional", [True, False])
def test_family_dann_head_reverses_gradient_into_the_fused_representation(
    class_conditional,
):
    from architecture.final_layer import PROTEIN_FAMILY_COUNT, family_dann_loss

    config = make_config()
    config.dann_family = True
    config.dann_class_conditional = class_conditional
    model = InteractionClassification(config)
    model.train()

    assert len(model.final_layer.family_adversaries) == (2 if class_conditional else 1)

    args = synthetic_forward_args(config)
    args["lip"] = args["lip"].requires_grad_(True)
    model(**args)
    features = model.final_layer._dann_features
    assert features is not None

    batch_size = features.shape[0]
    family = torch.zeros(batch_size, PROTEIN_FAMILY_COUNT)
    family[torch.arange(batch_size), torch.arange(batch_size) % PROTEIN_FAMILY_COUNT] = 1
    labels = torch.arange(batch_size) % 2

    def encoder_gradient(lam):
        model.final_layer.dann_lambda_now = lam
        model.zero_grad(set_to_none=True)
        args["lip"].grad = None
        model(**args)
        loss = family_dann_loss(
            model.final_layer._dann_features,
            family,
            labels,
            model.final_layer.family_adversaries,
            class_conditional,
        )
        loss.backward()
        return args["lip"].grad.clone()

    # Reversal, not merely scaling: flipping lambda's sign negates the encoder gradient.
    assert torch.allclose(encoder_gradient(1.0), -encoder_gradient(-1.0), atol=1e-6)
    assert encoder_gradient(0.0).abs().sum() == 0.0


def test_family_dann_leaves_no_features_outside_training():
    config = make_config()
    config.dann_family = True
    model = InteractionClassification(config)
    model.eval()

    model(**synthetic_forward_args(config))

    assert model.final_layer._dann_features is None


def test_family_dann_penalty_scale_does_not_depend_on_batch_composition():
    """Averaging, not summing, over the classes present in the batch.

    Summing would give the conditional variant one CE per class where the unconditional
    one gives a single CE, so the same dann_weight would mean twice the pressure and the
    dann_class_conditional ablation would not be a controlled comparison.
    """
    from architecture.final_layer import PROTEIN_FAMILY_COUNT, family_dann_loss

    config = make_config()
    config.dann_family = True
    model = InteractionClassification(config)
    heads = model.final_layer.family_adversaries

    torch.manual_seed(0)
    features = torch.randn(4, 2 * config.hiddim)
    family = torch.zeros(4, PROTEIN_FAMILY_COUNT)
    family[torch.arange(4), torch.arange(4)] = 1

    single_class = family_dann_loss(
        features, family, torch.zeros(4, dtype=torch.long), heads, True
    )
    mixed = family_dann_loss(
        features, family, torch.tensor([0, 1, 0, 1]), heads, True
    )

    # A mixed batch must not cost about twice a single-class one.
    assert mixed < 1.5 * single_class


def test_family_dann_rejects_a_sample_with_no_family_set():
    from architecture.final_layer import PROTEIN_FAMILY_COUNT, family_dann_loss

    config = make_config()
    config.dann_family = True
    model = InteractionClassification(config)

    features = torch.randn(4, 2 * config.hiddim)
    # argmax would silently call this the first family instead of failing.
    family = torch.zeros(4, PROTEIN_FAMILY_COUNT)

    with pytest.raises(ValueError, match="no family set"):
        family_dann_loss(
            features,
            family,
            torch.tensor([0, 1, 0, 1]),
            model.final_layer.family_adversaries,
            True,
        )


# --- --protein_hiddim / --lipid_hiddim -------------------------------------------
# Three properties, because the flags' whole promise is "you can widen ONE branch and
# nothing else moves": a default run must be untouched, an asymmetric run must actually
# train, and the widened branch must be the only one that grew.

def _width_config(**overrides):
    config = ModelConfig(hiddim=8, HEADS=2, m=2, batch=2, num_workers=0,
                         pool_type="mean", **overrides)
    config.validate()
    return config


def test_branch_widths_default_to_hiddim_and_build_no_adapter():
    """Setting the flags to hiddim must be indistinguishable from not setting them.

    number_of_parameters names run directories and is a column of metrics_summary.csv,
    so a default run that silently gained an adapter would corrupt the identity of
    every past run rather than just its memory use.
    """
    plain = InteractionClassification(_width_config())
    explicit = InteractionClassification(
        _width_config(protein_hiddim=8, lipid_hiddim=8)
    )
    assert plain.protein_width_adapter is None
    assert plain.lipid_width_adapter is None
    assert explicit.protein_width_adapter is None
    assert explicit.lipid_width_adapter is None
    count = lambda model: sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert count(plain) == count(explicit)


@pytest.mark.parametrize(
    "overrides,widened,untouched",
    [
        ({"lipid_hiddim": 16}, "lipid", "protein"),
        ({"protein_hiddim": 16}, "protein", "lipid"),
    ],
)
def test_one_branch_widens_alone_and_still_trains(overrides, widened, untouched):
    config = _width_config(**overrides)
    model = InteractionClassification(config)
    assert getattr(model, f"{widened}_width_adapter") is not None
    assert getattr(model, f"{untouched}_width_adapter") is None
    # The adapter lands the widened tower back on config.hiddim, which is what
    # cross-attention, the fusion and the classifier are all built at.
    assert getattr(model, f"{widened}_width_adapter").out_features == config.hiddim
    one_training_step(config)


def test_asymmetric_width_is_rejected_with_double_attention():
    """Its second encoder pass reads cross-attention output, always hiddim wide."""
    with pytest.raises(ValueError, match="double_attention"):
        _width_config(lipid_hiddim=16, double_attention=True)


# --- --lipid_edge_mlp / --lipid_edge_attention / --lipid_edge_mlp_lambda ----------
# The lipid graph gets its own conv choice and its own EdgeMLPConv divisor. The
# property that matters most is the boring one: an arg file that names only the protein
# flag must build exactly what it built before these flags existed.

def _graph_config(**overrides):
    config = ModelConfig(hiddim=8, HEADS=2, m=2, batch=2, num_workers=0,
                         pool_type="mean", lipid_graph_isomers=True,
                         lipid_fragments_treatment="concat", **overrides)
    config.validate()
    return config


@pytest.mark.parametrize(
    "protein_flag,expected",
    [
        ({"protein_edge_mlp": True}, "mlp"),
        ({"protein_edge_attention": True}, "attention"),
        ({}, "gatv2"),
    ],
)
def test_lipid_edge_mode_inherits_the_protein_flag_when_unset(protein_flag, expected):
    from architecture.mlp_utils import lipid_edge_mode
    assert lipid_edge_mode(_graph_config(**protein_flag)) == expected


def test_lipid_edge_flags_override_the_protein_choice_independently():
    """--protein_edge_mlp with --lipid_edge_attention must give the LIPID graph
    attention only -- not both, which would take EdgeMLPConv's narrow conv_out_dim
    while building EdgeAttentionConv layers."""
    from architecture.mlp_utils import lipid_edge_mode
    config = _graph_config(protein_edge_mlp=True, lipid_edge_attention=True)
    assert lipid_edge_mode(config) == "attention"
    model = InteractionClassification(config)
    assert not model.lipid1.use_edge_mlp
    one_training_step(config)


def test_lipid_lambda_defaults_to_the_protein_one_and_can_be_set_apart():
    from architecture.mlp_utils import lipid_edge_mlp_lambda
    inherited = _graph_config(protein_edge_mlp=True)
    assert lipid_edge_mlp_lambda(inherited) == inherited.protein_edge_mlp_lambda == 30.0
    own = _graph_config(protein_edge_mlp=True, lipid_edge_mlp_lambda=2.0)
    assert lipid_edge_mlp_lambda(own) == 2.0
    assert own.protein_edge_mlp_lambda == 30.0
    assert InteractionClassification(own).lipid1.encodin1.lam == 2.0
    one_training_step(own)


@pytest.mark.parametrize(
    "overrides,match",
    [
        ({"lipid_edge_mlp": True, "lipid_edge_attention": True}, "mutually exclusive"),
        ({"protein_edge_attention": True, "lipid_edge_mlp_lambda": 2.0}, "no effect"),
        ({"lipid_edge_mlp_lambda": -1.0, "protein_edge_mlp": True}, "greater than zero"),
    ],
)
def test_lipid_edge_flag_misuse_is_rejected(overrides, match):
    with pytest.raises(ValueError, match=match):
        _graph_config(**overrides)


def test_lipid_edge_flags_need_the_lipid_graph():
    """Without --lipid_graph_isomers there are no lipid edges, so these would be
    recorded in the run report as if they had shaped the model while changing nothing."""
    config = ModelConfig(hiddim=8, HEADS=2, m=2, batch=2, num_workers=0,
                         protein_edge_mlp=True, lipid_edge_mlp_lambda=2.0)
    with pytest.raises(ValueError, match="lipid_graph_isomers"):
        config.validate()


# --- --lipid_descriptors on its own is the ordinary broadcast ---------------------------

def test_chain_half_alone_is_the_ordinary_broadcast():
    config = ModelConfig(hiddim=8, HEADS=2, m=2, batch=2, num_workers=0, pool_type="mean",
                         lipid_descriptors="tail_length_mean,tail_double_bonds")
    config.validate()
    model = InteractionClassification(config)
    assert not hasattr(model.final_layer, "lipid_head_interaction")
    one_training_step(config)
