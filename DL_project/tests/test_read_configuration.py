import pytest

from training.read_configuration import (
    ModelConfig,
    read_configuration,
    read_excluded_groups,
    read_named_configuration,
)


def test_model_config_lipid_fragment_modes_are_mutually_exclusive():
    config = ModelConfig(lipid_fragments_treatment="fragments_mask")

    config.validate()

    assert config.lipid_fragments_treatment == "fragments_mask"
    assert config.lipid_fragments_mask is True
    assert config.lipid_concat is False
    assert config.lipid_random_choice is False


def test_lipid_first_fragment_only_defaults_off_for_every_treatment():
    for treatment in ("concat", "random_choice", "fragments_mask"):
        config = ModelConfig(lipid_fragments_treatment=treatment)

        config.validate()

        assert config.lipid_first_fragment_only is False


def test_default_treatment_draws_a_candidate_per_presentation():
    config = ModelConfig()

    config.validate()

    assert config.lipid_fragments_treatment == "random_choice"
    assert config.lipid_random_choice is True
    assert config.lipid_first_fragment_only is False


def test_random_choice_rejects_lipid_first_fragment_only():
    config = ModelConfig(
        lipid_fragments_treatment="random_choice",
        lipid_first_fragment_only=True,
    )

    with pytest.raises(ValueError, match="lipid_first_fragment_only"):
        config.validate()


def test_first_fragment_only_still_composes_with_the_other_treatments():
    for treatment in ("concat", "fragments_mask"):
        config = ModelConfig(
            lipid_fragments_treatment=treatment,
            lipid_first_fragment_only=True,
        )

        config.validate()

        assert config.lipid_first_fragment_only is True


@pytest.mark.parametrize(
    "argument",
    ["--no_lipid_first_fragment_only", "--lipid_first_fragment_only=0"],
)
def test_read_configuration_turns_off_lipid_first_fragment_only(argument):
    config = read_named_configuration([
        "train.py",
        "--lipid_fragments_treatment=fragments_mask",
        argument,
    ])

    assert config.lipid_first_fragment_only is False
    assert config.lipid_fragments_mask is True


def test_read_configuration_parses_new_boolean_flags():
    config = read_named_configuration([
        "train.py",
        "--lipid_isomers",
        "--grab_loss",
        "--type_opt",
        "--bidirectional_edges",
        "--single_gat_layer",
        "--transformer_conv",
        "--plm_sequential_compression",
        "--protein_disable_post_sa_mlp",
        "--lipid_disable_post_sa_mlp",
        "--protein_gat_graph_norm",
        "--protein_output_graph_norm",
        "--lipid_gat_graph_norm",
        "--lipid_output_graph_norm",
        "--rnabang_with_esm3",
    ])

    assert config.lipid_isomers is True
    assert config.grab_loss is True
    assert config.type_opt is True
    assert config.bidirectional_edges is True
    assert config.single_gat_layer is True
    assert config.transformer_conv is True
    assert config.plm_sequential_compression is True
    assert config.protein_disable_post_sa_mlp is True
    assert config.lipid_disable_post_sa_mlp is True
    assert config.protein_gat_graph_norm is True
    assert config.protein_output_graph_norm is True
    assert config.lipid_gat_graph_norm is True
    assert config.lipid_output_graph_norm is True
    assert config.rnabang_with_esm3 is True


def test_read_configuration_parses_geometric_transformer():
    config = read_named_configuration([
        "train.py",
        "--geometric_transformer",
        "--geometric_ipa_chunk_size=32",
    ])
    assert config.geometric_transformer is True
    assert config.geometric_ipa_chunk_size == 32


def test_geometric_ipa_chunk_size_rejects_negative_value():
    with pytest.raises(ValueError, match="must be non-negative"):
        ModelConfig(geometric_ipa_chunk_size=-1).validate()


def test_rnabang_frozen_node_adapter_rejects_double_attention():
    with pytest.raises(ValueError, match="cannot be combined with double_attention"):
        ModelConfig(
            rnabang_frozen_node_adapter=True,
            double_attention=True,
        ).validate()


def test_rnabang_residue_type_embedding_flag_and_dependency():
    config = read_named_configuration([
        "train.py",
        "--rnabang_frozen_node_adapter",
        "--rnabang_residue_type_embedding",
    ])
    assert config.rnabang_residue_type_embedding is True
    with pytest.raises(ValueError, match="requires rnabang_frozen_node_adapter"):
        ModelConfig(rnabang_residue_type_embedding=True).validate()


@pytest.mark.parametrize(
    "flag,field",
    [
        ("--rnabang_edge_current", "rnabang_edge_current"),
        ("--rnabang_edge_topk_by_area", "rnabang_edge_topk_by_area"),
        ("--rnabang_edge_deepsets", "rnabang_edge_deepsets"),
        ("--rnabang_edge_pna", "rnabang_edge_pna"),
        ("--rnabang_edge_quantiles", "rnabang_edge_quantiles"),
        ("--rnabang_edge_set_transformer", "rnabang_edge_set_transformer"),
    ],
)
def test_read_configuration_parses_rnabang_edge_mode(flag, field):
    config = read_named_configuration([
        "train.py",
        "--rnabang_frozen_node_adapter",
        flag,
    ])
    assert getattr(config, field) is True


def test_rnabang_edge_modes_are_mutually_exclusive():
    with pytest.raises(ValueError, match="mutually exclusive"):
        ModelConfig(
            rnabang_frozen_node_adapter=True,
            rnabang_edge_topk_by_area=True,
            rnabang_edge_pna=True,
        ).validate()


@pytest.mark.parametrize(
    "flag,field",
    [
        ("--rnabang_replace_esm3", "rnabang_replace_esm3"),
        ("--rnabang_full_protein_encoder", "rnabang_full_protein_encoder"),
        ("--rnabang_with_esm3", "rnabang_with_esm3"),
        ("--rnabang_residual_with_esm3", "rnabang_residual_with_esm3"),
        ("--rnabang_frozen_node_adapter", "rnabang_frozen_node_adapter"),
    ],
)
def test_read_configuration_parses_each_rnabang_mode(flag, field):
    config = read_named_configuration(["train.py", flag])

    assert getattr(config, field) is True
    assert config.rnabang_embedding_dim == 128


def test_rnabang_modes_are_mutually_exclusive():
    with pytest.raises(ValueError, match="mutually exclusive"):
        ModelConfig(
            rnabang_replace_esm3=True,
            rnabang_with_esm3=True,
        ).validate()


def test_rnabang_modes_require_plm_input():
    with pytest.raises(ValueError, match="require plmon"):
        ModelConfig(rnabang_replace_esm3=True, plmon=False).validate()


def test_esm3_v2_is_allowed_only_for_combined_rnabang_mode():
    with pytest.raises(ValueError, match="only meaningful"):
        ModelConfig(
            rnabang_full_protein_encoder=True,
            use_esm3_v2_embeddings=True,
        ).validate()

    ModelConfig(
        rnabang_with_esm3=True,
        use_esm3_v2_embeddings=True,
    ).validate()
    ModelConfig(
        rnabang_residual_with_esm3=True,
        use_esm3_v2_embeddings=True,
    ).validate()


def test_read_configuration_parses_protein_disable_pre_sa_mlp_with_gine_conv():
    # Split out of the bulk flag list rather than dropped: validate() requires gine_conv
    # for this flag while protein_self_attention is on, and gine_conv is mutually
    # exclusive with the transformer_conv the bulk case sets.
    config = read_named_configuration([
        "train.py",
        "--gine_conv",
        "--protein_disable_pre_sa_mlp",
    ])

    assert config.gine_conv is True
    assert config.protein_disable_pre_sa_mlp is True


def test_read_configuration_parses_gine_conv_flag():
    config = read_named_configuration(["train.py", "--gine_conv"])

    assert config.gine_conv is True


def test_balance_negatives_by_family_defaults_false_and_parses():
    assert ModelConfig().balance_negatives_by_family is False

    config = read_named_configuration(["train.py", "--balance_negatives_by_family"])

    assert config.balance_negatives_by_family is True


def test_balanced_proteins_defaults_false_and_parses():
    assert ModelConfig().balanced_proteins is False

    config = read_named_configuration(["train.py", "--balanced_proteins"])

    assert config.balanced_proteins is True


def test_balanced_proteins_combines_with_the_other_balancing_flags():
    config = read_named_configuration([
        "train.py",
        "--balanced_proteins",
        "--balance_negatives_by_family",
        "--balanced_batches",
    ])

    assert config.balanced_proteins is True
    assert config.balance_negatives_by_family is True
    assert config.balanced_batches is True


def test_balanced_batches_defaults_false_and_parses():
    assert ModelConfig().balanced_batches is False

    config = read_named_configuration(["train.py", "--balanced_batches"])

    assert config.balanced_batches is True


def test_balanced_batches_rejects_batch_below_two():
    with pytest.raises(ValueError, match="balanced_batches"):
        read_named_configuration(["train.py", "--balanced_batches", "--batch=1"])


def test_read_configuration_parses_gine_residual_flag():
    config = read_named_configuration([
        "train.py",
        "--gine_conv",
        "--protein_gine_residual",
    ])

    assert config.gine_conv is True
    assert config.protein_gine_residual is True


def test_read_configuration_parses_named_add_max_concat_pool_type():
    config = read_named_configuration(["train.py", "--pool_type=add_max"])

    assert config.pool_type == "add_max"


def test_read_configuration_parses_named_loss_type():
    config = read_named_configuration(["train.py", "--loss_type=cross_entropy"])

    assert config.loss_type == "cross_entropy"


@pytest.mark.parametrize(
    ("option", "expected", "module_cls"),
    [
        ("Leakyrelu", "leakyrelu", "LeakyReLU"),
        ("gelu", "gelu", "GELU"),
    ],
)
def test_read_configuration_parses_named_activation_function(
    option,
    expected,
    module_cls,
):
    config = read_named_configuration(["train.py", f"--act_fn={option}"])

    assert config.act_fn == expected
    assert config.make_activation().__class__.__name__ == module_cls


def test_read_configuration_parses_named_modes_and_numeric_values():
    config = read_configuration([
        "train.py",
        "--label=nps3mlp_gine_residual",
        "--lipid_fragments_treatment=random_choice",
        "--protein_pooling=pooling_by_pockets",
        "--hiddim=32",
        "--HEADS=4",
        "--weight_decay=0.0001",
        "--final_m=2",
        "--final_dropout=0.2",
    ])

    assert config.label == "nps3mlp_gine_residual"
    assert config.lipid_random_choice is True
    assert config.prot_pooling_by_pockets is True
    assert config.hiddim == 32
    assert config.HEADS == 4
    assert config.weight_decay == pytest.approx(0.0001)
    assert config.final_m == 2
    assert config.final_dropout == pytest.approx(0.2)


def test_read_configuration_rejects_unknown_pool_type():
    with pytest.raises(ValueError, match="pool_type"):
        read_named_configuration(["train.py", "--pool_type=median"])


def test_read_configuration_rejects_numeric_pool_type():
    with pytest.raises(ValueError, match="pool_type"):
        read_named_configuration(["train.py", "--pool_type=1"])


def test_read_configuration_rejects_numeric_loss_type():
    with pytest.raises(ValueError, match="loss_type"):
        read_named_configuration(["train.py", "--loss_type=1"])


def test_read_configuration_rejects_unknown_activation_function():
    with pytest.raises(ValueError, match="act_fn"):
        read_named_configuration(["train.py", "--act_fn=relu"])


def test_read_configuration_rejects_numeric_lipid_fragments_treatment():
    with pytest.raises(ValueError, match="lipid_fragments_treatment"):
        read_named_configuration(["train.py", "--lipid_fragments_treatment=1"])


def test_read_configuration_rejects_numeric_protein_pooling():
    with pytest.raises(ValueError, match="protein_pooling"):
        read_named_configuration(["train.py", "--protein_pooling=2"])


@pytest.mark.parametrize(
    "flag",
    [
        "--lipid_concat",
        "--lipid_random_choice",
        "--lipid_fragments_mask",
        "--ordinary_prot_pooling",
        "--prot_attention_pos_bias",
        "--prot_CA_for_pockets",
        "--prot_pooling_by_pockets",
    ],
)
def test_read_configuration_rejects_old_mode_flags(flag):
    with pytest.raises(ValueError, match="Unknown parameter"):
        read_named_configuration(["train.py", flag])


def test_read_configuration_parses_pu_loss_parameters():
    config = read_named_configuration([
        "train.py",
        "--pu_loss",
        "--pu_rho=0.15",
        "--pu_unlabeled_positive_fraction=0.05",
        "--pu_beta=0.1",
        "--pu_gamma=2.0",
    ])

    assert config.pu_loss is True
    assert config.pu_rho == pytest.approx(0.15)
    assert config.pu_unlabeled_positive_fraction == pytest.approx(0.05)
    assert config.pu_beta == pytest.approx(0.1)
    assert config.pu_gamma == pytest.approx(2.0)


def test_pu_unlabeled_positive_fraction_derives_rho_from_train_counts():
    config = ModelConfig(pu_unlabeled_positive_fraction=0.1)

    rho = config.effective_pu_rho(positive_count=760, unlabeled_count=1000)

    assert rho == pytest.approx((760 + 0.1 * 1000) / 1760)


def test_manual_pu_rho_is_used_without_unlabeled_positive_fraction():
    config = ModelConfig(pu_rho=0.15)

    assert config.effective_pu_rho(positive_count=760, unlabeled_count=1000) == pytest.approx(0.15)


@pytest.mark.parametrize(
    ("argument", "message"),
    [
        ("--pu_rho=0.0", "pu_rho"),
        ("--pu_rho=1.0", "pu_rho"),
        ("--pu_unlabeled_positive_fraction=-0.1", "pu_unlabeled_positive_fraction"),
        ("--pu_unlabeled_positive_fraction=1.0", "pu_unlabeled_positive_fraction"),
        ("--pu_beta=-0.1", "pu_beta"),
        ("--pu_gamma=0.0", "pu_gamma"),
        ("--loss_type=3", "loss_type"),
    ],
)
def test_read_configuration_rejects_invalid_pu_loss_parameters(argument, message):
    with pytest.raises(ValueError, match=message):
        read_named_configuration(["train.py", argument])


def test_model_config_weight_decay_defaults_to_small_nonzero():
    assert ModelConfig().weight_decay == 0.00001


def test_disable_early_stopping_is_enabled_by_default_and_stays_on_when_passed():
    # Runs are scored on their whole curve rather than stopped at a patience bound,
    # so the default is to let every epoch run.
    assert ModelConfig().disable_early_stopping is True

    config = read_named_configuration(["train.py", "--disable_early_stopping"])

    assert config.disable_early_stopping is True


def test_model_config_plm_compression_dim_defaults_to_ten():
    assert ModelConfig().plm_compression_dim == 10
    assert ModelConfig().plm_sequential_compression is False


def test_read_configuration_parses_plm_compression_dim():
    config = read_named_configuration(["train.py", "--plm_compression_dim=16"])

    assert config.plm_compression_dim == 16


def test_read_configuration_rejects_non_positive_plm_compression_dim():
    with pytest.raises(ValueError, match="plm_compression_dim"):
        read_named_configuration(["train.py", "--plm_compression_dim=0"])


def test_model_config_final_m_falls_back_to_legacy_m_only_when_cleared():
    # final_m now carries its own default; None is still honoured as "follow m", which
    # is the path Final_Layer and new_train take when a run does not set it.
    assert ModelConfig(m=4).final_m == 4

    config = ModelConfig(m=4, final_m=None)

    assert config.final_m is None
    assert config.final_dropout == 0.0


def test_read_configuration_rejects_non_positive_final_m():
    with pytest.raises(ValueError, match="final_m must be greater than zero"):
        read_named_configuration(["train.py", "--final_m=0"])


@pytest.mark.parametrize("value", ["-0.1", "1.0"])
def test_read_configuration_rejects_invalid_final_dropout(value):
    with pytest.raises(ValueError, match=r"final_dropout must be in the range"):
        read_named_configuration(["train.py", f"--final_dropout={value}"])


def test_class_weights_enabled_by_default_and_can_be_disabled():
    assert ModelConfig().class_weights is True

    config = read_named_configuration(["train.py", "--no_class_weights"])

    assert config.class_weights is False


@pytest.mark.parametrize(
    ("flag", "field"),
    [
        ("--protein_class_weight", "protein_class_weight"),
        ("--protein_class_sqrt_weight", "protein_class_sqrt_weight"),
    ],
)
def test_read_configuration_parses_protein_class_weight_flags(flag, field):
    config = read_named_configuration(["train.py", flag])

    assert getattr(config, field) is True


def test_protein_class_weight_modes_are_disabled_by_default():
    config = ModelConfig()

    assert config.protein_class_weight is False
    assert config.protein_class_sqrt_weight is False


def test_read_configuration_rejects_multiple_protein_class_weight_modes():
    with pytest.raises(ValueError, match="mutually exclusive"):
        read_named_configuration([
            "train.py",
            "--protein_class_weight",
            "--protein_class_sqrt_weight",
        ])


def test_read_configuration_rejects_multiple_protein_conv_modes():
    with pytest.raises(ValueError, match="mutually exclusive"):
        read_named_configuration([
            "train.py",
            "--transformer_conv",
            "--gine_conv",
        ])


def test_read_configuration_rejects_gine_residual_without_gine_conv():
    with pytest.raises(ValueError, match="requires gine_conv"):
        read_named_configuration(["train.py", "--protein_gine_residual"])


def test_read_configuration_rejects_disabling_protein_pre_sa_mlp_without_gine():
    with pytest.raises(ValueError, match="requires gine_conv"):
        read_named_configuration([
            "train.py",
            "--protein_self_attention",
            "--protein_disable_pre_sa_mlp",
        ])


def test_double_attention_enables_cross_attention():
    config = read_named_configuration(["train.py", "--double_attention"])

    assert config.double_attention is True
    assert config.cross_attention is True


def test_protein_attention_position_bias_is_selected_by_named_mode():
    config = read_named_configuration([
        "train.py",
        "--protein_pooling=attention_pos_bias",
    ])

    assert config.prot_attention_pos_bias is True
    assert config.protein_pooling == "attention_pos_bias"


def test_read_configuration_rejects_incompatible_hiddim_and_heads():
    with pytest.raises(ValueError, match="must be divisible"):
        read_named_configuration([
            "train.py",
            "--hiddim=30",
            "--HEADS=8",
        ])


def test_read_excluded_groups_accepts_aliases_and_deduplicates():
    groups = read_excluded_groups("cral_trio,CRAL-TRIO,start")

    assert groups == ["CRAL-TRIO", "START"]


def test_read_configuration_raises_for_unknown_parameter():
    with pytest.raises(ValueError, match="Unknown parameter"):
        read_named_configuration(["train.py", "--does_not_exist"])


def test_read_excluded_groups_raises_for_unknown_group():
    with pytest.raises(ValueError, match="Unknown excluded_groups group"):
        read_excluded_groups("unknown")


def test_model_config_plm_compression_dims_default_to_legacy_widths():
    assert ModelConfig().plm_compression_dims == [512, 171, 57]


def test_read_configuration_parses_plm_compression_dims():
    config = read_named_configuration(["train.py", "--plm_compression_dims=256, 64"])

    assert config.plm_compression_dims == [256, 64]


def test_read_configuration_rejects_non_positive_plm_compression_dims():
    with pytest.raises(ValueError, match="plm_compression_dims"):
        read_named_configuration(["train.py", "--plm_compression_dims=256,0"])


def test_read_configuration_parses_gate_all_mlp_layers():
    config = read_named_configuration(["train.py", "--gate_all_mlp_layers"])

    assert config.gate_all_mlp_layers is True
    assert config.gate_all_mlp_hidden is False


def test_bilevel_accepts_gate_all_mlp_layers():
    config = read_named_configuration(["train.py", "--bilevel", "--gate_all_mlp_layers"])

    assert config.bilevel is True


def test_read_configuration_parses_no_ffns():
    assert ModelConfig().no_ffns is False
    assert read_named_configuration(["train.py", "--no_ffns"]).no_ffns is True


def test_read_configuration_parses_mlp_widths():
    config = read_named_configuration(
        ["train.py", "--mlp_widths=protein_mlp=101, protein_mlp_third=74,final=175"]
    )

    assert config.mlp_widths == {
        "protein_mlp": 101,
        "protein_mlp_third": 74,
        "final": 175,
    }


def test_read_configuration_rejects_unknown_mlp_widths_site():
    with pytest.raises(ValueError, match="Unknown mlp_widths site"):
        read_named_configuration(["train.py", "--mlp_widths=protein_mpl=101"])


def test_read_configuration_rejects_non_positive_mlp_widths():
    with pytest.raises(ValueError, match="mlp_widths"):
        read_named_configuration(["train.py", "--mlp_widths=final=0"])


def test_adversary_flags_parse_and_default_off():
    assert ModelConfig().adv_deep is False
    assert ModelConfig().adv_lambda_ramp is False
    assert ModelConfig().adv_lambda_ramp_by_fit is False

    config = read_named_configuration([
        "train.py",
        "--adversarial_grl",
        "--adv_deep",
        "--adv_lambda_ramp",
    ])

    assert config.adv_deep is True
    assert config.adv_lambda_ramp is True


def test_adv_lambda_is_constant_unless_a_ramp_is_requested():
    config = ModelConfig(adversarial_grl=True, adv_lambda=0.7)

    assert [config.ramped_adv_lambda(p) for p in (0.0, 0.5, 1.0)] == [0.7, 0.7, 0.7]


def test_epoch_ramp_rises_from_zero_to_adv_lambda():
    config = ModelConfig(adversarial_grl=True, adv_lambda=1.0, adv_lambda_ramp=True)

    assert config.ramped_adv_lambda(0.0) == 0.0
    assert config.ramped_adv_lambda(1.0) == pytest.approx(1.0, abs=1e-4)
    # Ganin's sigmoid is front-loaded: a third of the way through training it is already
    # near full strength, which is why the fit-driven ramp exists.
    assert config.ramped_adv_lambda(0.3) > 0.9


def test_fit_ramp_tracks_train_balanced_accuracy_linearly():
    config = ModelConfig(
        adversarial_grl=True, adv_lambda=1.0, adv_lambda_ramp_by_fit=True
    )

    # Chance-level fit means nothing has been learned yet, so nothing to suppress.
    assert config.adv_fit_progress(0.5) == 0.0
    assert config.adv_fit_progress(1.0) == 1.0
    assert config.adv_fit_progress(0.75) == pytest.approx(0.5)
    # Below chance and missing metrics clamp rather than going negative.
    assert config.adv_fit_progress(0.2) == 0.0
    assert config.adv_fit_progress(None) == 0.0

    # Unlike the epoch ramp, a model still stuck near chance keeps a gentle lambda.
    assert config.ramped_adv_lambda(config.adv_fit_progress(0.62)) < 0.3
    assert config.ramped_adv_lambda(config.adv_fit_progress(0.93)) > 0.8


def test_fit_ramp_takes_precedence_and_scales_by_adv_lambda():
    config = ModelConfig(
        adversarial_grl=True,
        adv_lambda=0.5,
        adv_lambda_ramp=True,
        adv_lambda_ramp_by_fit=True,
    )

    assert config.ramped_adv_lambda(1.0) == pytest.approx(0.5)
    assert config.ramped_adv_lambda(0.5) == pytest.approx(0.25)


def test_dann_family_flags_parse_and_default_off():
    assert ModelConfig().dann_family is False
    assert ModelConfig().balanced_lipid_classes is False
    # The class-conditional form is the default because the unconditional one is
    # provably harmful under this dataset's per-family label shift.
    assert ModelConfig().dann_class_conditional is True

    config = read_named_configuration([
        "train.py",
        "--dann_family",
        "--dann_weight=0.3",
        "--dann_lambda=0.5",
        "--dann_lambda_ramp",
        "--balanced_lipid_classes",
    ])

    assert config.dann_family is True
    assert config.dann_weight == pytest.approx(0.3)
    assert config.dann_lambda == pytest.approx(0.5)
    assert config.dann_lambda_ramp is True
    assert config.balanced_lipid_classes is True


def test_dann_lambda_ramp_by_fit_parses_and_defaults_off():
    assert ModelConfig().dann_lambda_ramp_by_fit is False

    config = read_named_configuration([
        "train.py",
        "--dann_family",
        "--dann_lambda_ramp_by_fit",
    ])

    assert config.dann_lambda_ramp_by_fit is True
    assert config.dann_lambda_ramp is False


def test_ramped_dann_lambda_is_constant_without_a_ramp():
    config = ModelConfig(dann_family=True, dann_lambda=0.7)

    assert [config.ramped_dann_lambda(p) for p in (0.0, 0.5, 1.0)] == [0.7, 0.7, 0.7]


def test_ramped_dann_lambda_is_linear_and_clamped_under_either_ramp():
    for flags in ({"dann_lambda_ramp": True}, {"dann_lambda_ramp_by_fit": True}):
        config = ModelConfig(dann_family=True, dann_lambda=0.5, **flags)

        assert config.ramped_dann_lambda(0.0) == pytest.approx(0.0)
        assert config.ramped_dann_lambda(0.5) == pytest.approx(0.25)
        assert config.ramped_dann_lambda(1.0) == pytest.approx(0.5)
        # Out-of-range progress cannot push the reversal past dann_lambda or below 0.
        assert config.ramped_dann_lambda(1.4) == pytest.approx(0.5)
        assert config.ramped_dann_lambda(-0.2) == pytest.approx(0.0)


def test_dann_fit_ramp_reuses_the_adversary_fit_progress_mapping():
    # by_fit changes the clock, not the curve, so the same BA -> progress mapping the
    # per-partner ramp uses drives this one; both stay on one ratchet in the epoch loop.
    config = ModelConfig(dann_family=True, dann_lambda=1.0, dann_lambda_ramp_by_fit=True)

    assert config.ramped_dann_lambda(config.adv_fit_progress(0.5)) == pytest.approx(0.0)
    assert config.ramped_dann_lambda(config.adv_fit_progress(0.75)) == pytest.approx(0.5)
    assert config.ramped_dann_lambda(config.adv_fit_progress(1.0)) == pytest.approx(1.0)


def test_dann_class_conditional_can_be_switched_off_for_ablation():
    config = read_named_configuration([
        "train.py",
        "--dann_family",
        "--dann_class_conditional=0",
    ])

    assert config.dann_class_conditional is False
