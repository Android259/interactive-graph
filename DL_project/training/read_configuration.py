import sys
from dataclasses import dataclass, field

POOL_TYPES = ("add", "max", "mean", "add_max", "gem")
LOSS_TYPES = ("mse", "cross_entropy", "bce", "pairwise_rank")
LIPID_FRAGMENTS_TREATMENTS = ("concat", "random_choice", "fragments_mask")
PROTEIN_POOLINGS = ("ordinary", "attention_pos_bias", "pooling_by_pockets")
# Sites restricted by attention_by_pockets. Omitting the option restricts both;
# "both" is the default but cannot be passed explicitly. "cross" keeps full-chain
# GAT and protein self-attention context while the lipid reads only the pocket.
# This separates protein encoding from partner access.
POCKET_ATTENTION_SITES = ("self", "cross")

# Frozen per-residue protein embeddings that REPLACE the ESM3 vector. Each entry is
# (config flag, file suffix, width attribute); files live in
# data/embedding_<suffix>/<protein>_<suffix>.pkl, one row per coarse_graph_nodes.csv
# row, exactly like data/embedding_ESM3_v2 and data/embedding_RNABANG.
#
# Both are structure-conditioned.
FROZEN_PROTEIN_EMBEDDINGS = (
    ("proteinmpnn_replace_esm3", "PROTEINMPNN", "proteinmpnn_embedding_dim"),
    ("esmif1_replace_esm3", "ESMIF1", "esmif1_embedding_dim"),
)
ACT_FNS = ("leakyrelu", "gelu", "prelu", "relu")


def parse_deepclip_widths(widths):
    """Parse --deepclip_widths as ordered positive integers.

    Validate without importing torch; architecture/deepclip.py imports this helper,
    as interaction_classification.py imports ModelConfig. Width order assigns
    convolutions to LSTM input slices and must match the checkpoint's training order.
    """
    parsed = []
    for part in str(widths).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            width = int(part)
        except ValueError:
            raise ValueError(
                f"deepclip_widths must be comma-separated integers, got {part!r}"
            ) from None
        if width <= 0:
            raise ValueError(f"deepclip_widths must be positive, got {width}")
        parsed.append(width)
    if not parsed:
        raise ValueError(
            "deepclip_widths is empty -- give at least one window width, e.g. "
            '"4,5,6,7,8" (DeepCLIP\'s own FILTER_SIZES)'
        )
    return tuple(parsed)


EXCLUDED_SUBGROUPS_BY_NAME = {
    "CRAL-TRIO": [
        "ATCAY",
        "BNIPL",
        "RLBP1",
        "SEC14L2",
        "SEC14L4",
        "SEC14L5",
        "SEC14L6",
        "TTPA",
        "TTPAL",
    ],
    "START": [
        "STARD10",
        "STARD11",
        "STARD2",
    ],
    "lipocalin": [
        "CRABP2",
        "FABP1",
        "FABP5",
        "FABP7",
        "LCN1",
        "LCN15",
        "PMP2",
        "RBP1",
        "RBP4",
        "RBP5",
    ],
    "GLTP": [
        "GLTP",
        "GLTPD1",
    ],
    "IP_trans": [
        "PITPNA",
        "PITPNB",
        "PITPNC1",
    ],
    "LBP_BPI_CETP": [
        "BPI",
        "BPIFB2",
    ],
    "scp2": [
        "HSDL2",
        "SCP2",
        "SCP2D1",
    ],
    "ML": [
        "GM2A",
    ],
    "OSBP": [
        "OSBPL5",
        "OSBPL9",
    ],
}

EXCLUDED_GROUP_ALIASES = {
    name.lower().replace("-", "_"): name for name in EXCLUDED_SUBGROUPS_BY_NAME
}
EXCLUDED_GROUP_ALIASES.update({
    name.lower(): name for name in EXCLUDED_SUBGROUPS_BY_NAME
})

# Names of the lipid-class sets --lipid_coldsplit accepts. The classes themselves live
# in LIPID_COLDSPLIT_SETS (dataloader/splitting_on_blocks/lipid_coldsplit_blocks.py,
# which also records how each set was
# chosen and how isolated it is); only the names are repeated here, so that a typo fails
# at parse time instead of after a job reaches a GPU. PLIDataset checks the two agree.
LIPID_COLDSPLIT_NAMES = ("sphingolipids", "phosphorus_free", "choline", "anionic")

# The same axis addressed by distance instead of by chemistry. The keys are the
# requested isolation values, and they are read straight off the generated registry
# rather than repeated here: that file IS the list, and a second copy is how the two
# would drift (which is exactly what the comment above LIPID_COLDSPLIT_NAMES guards
# against for the class sets, where the names and the classes live in two files).
from dataloader.splitting_on_blocks.lipid_isolation_blocks import (  # noqa: E402
    LIPID_ISOLATION_BLOCKS,
)

LIPID_ISOLATION_KEYS = tuple(LIPID_ISOLATION_BLOCKS)


def read_lipid_isolation(value):
    """Resolve a distance-based lipid holdout key."""
    name = str(value).strip()
    if not name:
        return ""
    if name not in LIPID_ISOLATION_BLOCKS:
        raise ValueError(
            f"Unknown lipid_isolation block: {value}; "
            f"expected one of {', '.join(LIPID_ISOLATION_KEYS)}"
        )
    return name


def read_lipid_subclass(value):
    """Resolve "+"-joined Titeca et al. lipid subclasses for holdout.

    Canonicalize and validate during parsing, before GPU startup, as in
    read_lipid_coldsplit. Membership: data/lipid_article_classification.json;
    see dataloader/splitting_on_blocks/lipid_subclass_blocks.py.
    """
    from dataloader.splitting_on_blocks.lipid_subclass_blocks import canonical_subclass_spec

    return canonical_subclass_spec(value)


def read_lipid_coldsplit(value):
    """Resolve a lipid-class holdout name."""
    name = str(value).strip().lower()
    if not name:
        return ""
    if name not in LIPID_COLDSPLIT_NAMES:
        raise ValueError(
            f"Unknown lipid_coldsplit set: {value}; "
            f"expected one of {', '.join(LIPID_COLDSPLIT_NAMES)}"
        )
    return name


def read_bool(value):
    """Parse a CLI boolean, accepting common true values."""
    if value is True:
        return True
    value = str(value).lower()
    return value in ["1", "true", "yes", "on"]


def read_value(argument):
    """Extract the value from name=value."""
    return argument.split("=", 1)[1]


def read_excluded_groups(value):
    """Parse and normalize excluded protein groups."""
    values = [item.strip() for item in str(value).split(",") if item.strip()]
    excluded_groups = []

    for item in values:
        group_name = EXCLUDED_GROUP_ALIASES.get(item.lower().replace("-", "_"))
        if group_name is None:
            raise ValueError(f"Unknown excluded_groups group: {item}")
        excluded_groups.append(group_name)

    return list(dict.fromkeys(excluded_groups))


def read_test_group(value):
    """Normalize one protein-group name."""
    item = str(value).strip()
    if not item:
        return ""
    group_name = EXCLUDED_GROUP_ALIASES.get(item.lower().replace("-", "_"))
    if group_name is None:
        raise ValueError(f"Unknown test_group group: {item}")
    return group_name


MLP_WIDTH_SITES = (
    "protein_mlp",
    "protein_post_sa",
    "lipid_mlp",
    "lipid_post_sa",
    "protein_ffn",
    "lipid_ffn",
    "cross_lip_ffn",
    "cross_prot_ffn",
    "final",
)


def read_pocket_attention_sites(value):
    """Parse "self" or "cross"; "both" is the implicit default."""
    site = str(value).strip().lower()
    if site == "both":
        raise ValueError(
            "pocket_attention_sites=both is the default of --attention_by_pockets; "
            "pass the flag alone for both sites, or "
            f"--pocket_attention_sites={'/'.join(POCKET_ATTENTION_SITES)} to narrow it"
        )
    if site not in POCKET_ATTENTION_SITES:
        raise ValueError(
            f"pocket_attention_sites must be one of {', '.join(POCKET_ATTENTION_SITES)}"
        )
    return site


def read_mlp_widths(value):
    """Parse MLP widths, e.g. "protein_mlp=101,final=175".

    Sites default to m * hiddim. <site>_third overrides the third layer,
    which defaults to the site width. Reuse gate/bilevel widths in plain runs.
    """
    widths = {}
    for item in str(value).split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"mlp_widths entries must be site=width, got: {item}")
        site, width = (part.strip() for part in item.split("=", 1))
        base = site[: -len("_third")] if site.endswith("_third") else site
        if base not in MLP_WIDTH_SITES:
            raise ValueError(
                f"Unknown mlp_widths site: {site} "
                f"(known: {', '.join(MLP_WIDTH_SITES)}, each also with a _third suffix)"
            )
        widths[site] = int(width)
    return widths


def read_plm_compression_dims(value):
    """Parse sequential PLM widths, e.g. "512,171,57"."""
    return [int(item.strip()) for item in str(value).split(",") if item.strip()]


def read_excluded_subgroups(value):
    """Parse excluded subgroups in input order."""
    excluded_subgroups = []
    values = [item.strip() for item in str(value).split(",") if item.strip()]

    for item in values:
        excluded_subgroups.append(item)

    return list(dict.fromkeys(excluded_subgroups))


@dataclass
class ModelConfig:
    third_layers_in_mlps: bool = False
    cross_attention: bool = True
    bilinear_fusion: bool = False
    bilinear_weight_decay: float | None = None
    deepclip_gate_weight_decay: float | None = None
    bilinear_pooled_norm: bool = False
    node_bilinear_fusion: bool = False
    cross_attention_forced_interaction: bool = False
    adversarial_grl: bool = False
    adv_weight: float = 1.0
    adv_lambda: float = 1.0
    adv_deep: bool = False
    adv_lipid: bool = True
    adv_protein: bool = True
    adv_lambda_ramp: bool = False
    adv_lambda_ramp_by_fit: bool = False
    dann_family: bool = False
    dann_weight: float = 1.0
    dann_lambda: float = 1.0
    dann_class_conditional: bool = True
    dann_lambda_ramp: bool = False
    dann_lambda_ramp_by_fit: bool = False
    chem_prior: bool = False
    chem_neighbours: int = 15
    lipid_propensity_weight: bool = False
    chem_adversary: bool = False
    chem_weight: float = 1.0
    chem_lambda: float = 1.0
    chem_lambda_ramp: bool = False
    chem_lambda_ramp_by_fit: bool = False
    pocket_compat_prior: bool = False
    descriptor_heads: str = ""
    descriptors_head: bool = False
    descriptor_mlp: bool = False
    lipid_smiles_tokens: bool = False
    deepclip: bool = False
    deepclip_filters: int = 1
    deepclip_widths: str = "4,5,6,7,8"
    deepclip_lstm: int = 10
    deepclip_lstm_dropout: float = 0.1
    deepclip_out_dropout: float = 0.0
    deepclip_conv_init: str = "constant"
    deepclip_readout: str = "mean"
    deepclip_profile_weights: bool = False
    deepclip_conv_layers: int = 1
    deepclip_protein_gate: str = ""
    deepclip_gate_hidden: int = 8
    deepclip_protein_tokens: str = ""
    no_protein_embeddings: bool = False
    no_protein_geometry: bool = False
    lipid_path_handicap: bool = False
    lipid_path_weight: float = 0.1
    lipid_path_weight_ramp_epochs: int = 50
    balanced_lipid_classes: bool = False
    lipid_class_targets: bool = False
    fast_attention: bool = False
    protein_self_attention: bool = True
    lipid_self_attention: bool = True
    mlp_in_place_of_sa: bool = False
    double_attention: bool = False
    single_gat_layer: bool = True
    geometric_transformer: bool = False
    geometric_ipa_chunk_size: int = 64
    transformer_conv: bool = False
    gine_conv: bool = False
    protein_edge_attention: bool = False
    protein_edge_mlp: bool = False
    protein_edge_mlp_lambda: float = 30.0
    lipid_edge_attention: bool | None = None
    lipid_edge_mlp: bool | None = None
    lipid_edge_mlp_lambda: float | None = None
    protein_edge_rbf_count: int = 16
    protein_edge_orientation_scalar: bool = False
    protein_edge_raw3: bool = False
    protein_gine_residual: bool = False
    attention_residual_gates: bool = False
    protein_gat_residual: bool = False
    structured_sparsity: bool = False
    sparsity_mode: str = "l0"
    sparsity_lambda: float = 0.0
    target_sparsity: float | None = None
    sparsity_gate_ffn: bool = False
    sparsity_gate_heads: bool = False
    sparsity_gate_blocks: bool = False
    sparsity_gate_third_layer: bool = False
    sparsity_gate_cross_attention: bool = False
    gate_all_mlp_hidden: bool = False
    gate_all_mlp_layers: bool = False
    no_ffns: bool = False
    mlp_widths: dict = field(default_factory=dict)
    bilevel: bool = False
    bilevel_dropout: bool = False
    bilevel_lr: float = 1e-3
    concrete_dropout_reg: float = 1e-5
    concrete_dropout_weight_reg: float = 1e-6
    protein_disable_pre_sa_mlp: bool = False
    protein_disable_post_sa_mlp: bool = True
    lipid_disable_post_sa_mlp: bool = True
    protein_gat_graph_norm: bool = False
    protein_output_graph_norm: bool = False
    lipid_gat_graph_norm: bool = False
    lipid_output_graph_norm: bool = False

    label: str = ""
    m: int = 4
    final_m: int = 4
    dropout: float = 0.0
    final_dropout: float = 0.0
    lr: float = 0.0001
    weight_decay: float = 0.00001
    hiddim: int = 64
    protein_hiddim: int | None = None
    lipid_hiddim: int | None = None
    ep: int = 150
    checkpoint_window: int = 5
    checkpoint_selection_metric: str = ""
    seed: int = 0
    excluded_groups: list = field(default_factory=list)
    double_coldsplit: bool = False
    mixed_coldsplit: bool = False
    lipid_coldsplit: str = ""
    lipid_isolation: str = ""
    lipid_subclass: str = ""
    lipid_species_coldsplit: float = 0.0
    drop_uncovered_protein_subclass: bool = False
    coldsplit_share: float = 0.8
    excluded_subgroups: list = field(default_factory=list)
    balance_excluded_group_negatives: bool = False
    balance_negatives_by_family: bool = False
    balanced_proteins: bool = False
    balanced_batches: bool = False
    negatives_per_positive: int = 2
    rotate_train_negatives: bool = False
    rotate_negatives_per_epoch: int = 0
    hard_negative_mining: bool = False
    hard_negative_share: float = 0.5
    dissimilar_negative_mining: bool = False
    dissimilar_negative_share: float = 0.5
    negative_similarity: str = "tanimoto"
    negative_similarity_descriptors: str = ""
    test_group: str = ""
    cold_split: bool = False
    lipid_only: bool = False
    protein_only: bool = False
    batch: int = 16
    num_workers: int = 4
    lipid_fragments_treatment: str = "random_choice"
    protein_pooling: str = "attention_pos_bias"
    
    lipid_concat: bool = False
    lipid_random_choice: bool = True
    lipid_fragments_mask: bool = False
    lipid_first_fragment_only: bool = False
    eval_average_candidates: bool = False
    eval_candidates_per_pair: int = 4
    lipid_isomers: bool = False
    lipid_graph_isomers: bool = False

    ordinary_prot_pooling: bool = True
    prot_attention_pos_bias: bool = True
    prot_pooling_by_pockets: bool = False
    prot_pos_bias_per_head: bool = False
    cross_attention_bury_bias: bool = False
    cross_attention_chain_bias: bool = False
    attention_by_pockets: bool = False
    pocket_attention_sites: str = "both"
    # Derived in validate() from attention_by_pockets and pocket_attention_sites.
    pocket_attention_self: bool = False
    pocket_attention_cross: bool = False
    protein_pockets_only: bool = False
    protein_residue_subsample: int = 0
    proteinmpnn_replace_esm3: bool = False
    proteinmpnn_embedding_dim: int = 128
    esmif1_replace_esm3: bool = False
    esmif1_embedding_dim: int = 512
    protein_extra_node_features: bool = False
    protein_descriptors: str = ""
    lipid_descriptors: str = ""
    # Protein node width, derived in validate() and shared by loader and
    # encoder to prevent mismatches. Recorded in metrics_summary, where
    # node width would otherwise be invisible.
    protein_node_feature_count: int = 3
    bidirectional_edges: bool = False
    tanimoto_weight: bool = False
    class_weights: bool = True
    protein_group_weight: bool = False
    protein_class_weight: bool = False
    protein_class_sqrt_weight: bool = False
    protein_balance_weight: bool = False
    marginal_balance_weight: bool = False
    pu_loss: bool = False
    disable_early_stopping: bool = True
    testmode: bool = False
    pu_rho: float = 0.2
    pu_unlabeled_positive_fraction: float | None = None
    pu_rho_by_subclass: bool = False
    pu_beta: float = 0.0
    pu_gamma: float = 1.0
    pu_tau: float = 1.0
    pu_loss_cap: float = float("inf")
    focal_loss: bool = False
    focal_gamma: float = 2.0
    logit_adjustment: bool = False
    logit_adjustment_tau: float = 1.0
    type_opt: bool = False
    plmon: bool = True
    plm_sequential_compression: bool = False
    plm_compression_dim: int = 10
    plm_compression_dims: list = field(default_factory=lambda: [512, 171, 57])
    buryon: bool = True
    loss_type: str = "cross_entropy"
    rank_within_protein: bool = False
    group_dro: bool = False
    group_dro_step_size: float = 0.01
    group_dro_adj: float = 0.0
    pool_type: str = "max"
    attention_pooling: bool = False
    attention_pooling_pocket_bias: bool = False
    swe_pooling: bool = False
    swe_reference_points: int = 32
    swe_freeze_reference: bool = False
    use_esm3_v2_embeddings: bool = False
    rnabang_replace_esm3: bool = False
    rnabang_full_protein_encoder: bool = False
    rnabang_with_esm3: bool = False
    rnabang_residual_with_esm3: bool = False
    rnabang_frozen_node_adapter: bool = False
    rnabang_residue_type_embedding: bool = False
    rnabang_edge_current: bool = False
    rnabang_edge_topk_by_area: bool = False
    rnabang_edge_deepsets: bool = False
    rnabang_edge_pna: bool = False
    rnabang_edge_quantiles: bool = False
    rnabang_edge_set_transformer: bool = False
    rnabang_embedding_dim: int = 128
    act_fn: str = "leakyrelu"
    HEADS: int = 8
    lr_warmup_cosine: bool = False
    lr_warmup_epochs: int = 0
    lr_min_factor: float = 0.1
    save_checkpoint: bool = False
    save_model: bool = True
    save_dynamics: bool = False
    save_model_in_dynamics: bool = False
    family_only: str = ""

    def validate(self):
        """Validate dimensions, dependencies, and implied options."""
        if self.HEADS <= 0:
            raise ValueError("HEADS must be greater than zero")
        self.loss_type = str(self.loss_type).lower()
        if self.loss_type not in LOSS_TYPES:
            raise ValueError(f"loss_type must be one of {', '.join(LOSS_TYPES)}")
        self.lipid_fragments_treatment = str(self.lipid_fragments_treatment).lower()
        if self.lipid_fragments_treatment not in LIPID_FRAGMENTS_TREATMENTS:
            raise ValueError(
                "lipid_fragments_treatment must be one of "
                f"{', '.join(LIPID_FRAGMENTS_TREATMENTS)}"
            )
        self.protein_pooling = str(self.protein_pooling).lower()
        if self.protein_pooling not in PROTEIN_POOLINGS:
            raise ValueError(
                f"protein_pooling must be one of {', '.join(PROTEIN_POOLINGS)}"
            )
        if self.lipid_isolation and (
            self.lipid_coldsplit
            or self.double_coldsplit
            or self.mixed_coldsplit
            or self.excluded_groups
            or self.excluded_subgroups
        ):
            raise ValueError(
                "lipid_isolation holds a fixed set of lipid species out with every "
                "protein left in training -- the same axis lipid_coldsplit is on, and "
                "it cannot be combined with another holdout on either axis"
            )
        if self.lipid_subclass and (
            self.lipid_coldsplit
            or self.lipid_isolation
            or self.double_coldsplit
            or self.mixed_coldsplit
            or self.excluded_groups
            or self.excluded_subgroups
        ):
            raise ValueError(
                "lipid_subclass holds one article lipid subclass out with every protein "
                "left in training -- the same axis lipid_coldsplit/lipid_isolation are "
                "on, and it cannot be combined with another holdout on either axis"
            )
        if self.lipid_species_coldsplit and (
            self.lipid_coldsplit
            or self.lipid_isolation
            or self.lipid_subclass
            or self.double_coldsplit
            or self.mixed_coldsplit
            or self.excluded_groups
            or self.excluded_subgroups
        ):
            raise ValueError(
                "lipid_species_coldsplit draws individual lipids out with every protein "
                "left in training -- the same axis lipid_coldsplit/lipid_isolation/"
                "lipid_subclass are on, and it cannot be combined with another holdout "
                "on either axis"
            )
        if not 0.0 <= self.lipid_species_coldsplit < 1.0:
            raise ValueError(
                "lipid_species_coldsplit is the share of the table's positives the "
                "held-out block has to carry and belongs in [0, 1); 0 turns it off. "
                f"Got {self.lipid_species_coldsplit}"
            )

        if self.drop_uncovered_protein_subclass and not self.lipid_species_coldsplit:
            # Require the measured lipid_species_coldsplit: every protein stays in
            # train. A protein holdout would leave empty cells and delete all eval
            # rows. This requirement also inherits the protein-holdout exclusion.
            raise ValueError(
                "drop_uncovered_protein_subclass is a rule for the "
                "lipid_species_coldsplit block and needs "
                "--lipid_species_coldsplit set"
            )

        if self.lipid_coldsplit and (self.double_coldsplit or self.mixed_coldsplit):
            raise ValueError(
                "lipid_coldsplit holds a fixed chemical family out with every protein "
                "left in training; double_coldsplit and mixed_coldsplit derive their "
                "classes from a held-out protein family instead. They answer different "
                "questions and cannot be combined"
            )

        if self.lipid_coldsplit and self.excluded_groups:
            raise ValueError(
                "lipid_coldsplit is the lipid axis on its own -- every protein stays in "
                "training. Combining it with excluded_groups makes a two-axis split, "
                "which is what --double_coldsplit is for"
            )

        if self.double_coldsplit and self.mixed_coldsplit:
            raise ValueError(
                "double_coldsplit and mixed_coldsplit are the two answers to the same "
                "question -- what to do with the held-out family's rows in the classes "
                "that stayed in train -- so exactly one of them applies"
            )

        if not 0.0 < self.coldsplit_share <= 1.0:
            raise ValueError(
                "coldsplit_share is the share of the held-out family's positives the "
                f"derived class set must cover and belongs in (0, 1]; got "
                f"{self.coldsplit_share}"
            )

        if self.negatives_per_positive < 1:
            raise ValueError(
                "negatives_per_positive is how many negatives each positive draws "
                "inside its balancing group and must be at least 1; "
                f"got {self.negatives_per_positive}"
            )

        if self.rotate_negatives_per_epoch < 0:
            raise ValueError(
                "rotate_negatives_per_epoch is how many negatives one epoch holds "
                "under rotate_train_negatives and cannot be negative; 0 means "
                f"negatives_per_positive x train positives. Got "
                f"{self.rotate_negatives_per_epoch}"
            )
        if self.rotate_negatives_per_epoch and not self.rotate_train_negatives:
            raise ValueError(
                "rotate_negatives_per_epoch sizes the per-epoch slice of "
                "rotate_train_negatives -- there is no slice to size without it"
            )
        if self.rotate_train_negatives and self.eval_average_candidates:
            # Candidate expansion changes only valid/test, but shares __iter__ with
            # train cloning. The combination is untested, so reject it.
            raise ValueError(
                "rotate_train_negatives and eval_average_candidates have not been "
                "run together; pass one of them"
            )

        if self.hard_negative_mining and not (
            self.balanced_proteins
            or self.balance_negatives_by_family
            or self.balanced_lipid_classes
        ):
            raise ValueError(
                "hard_negative_mining reweights the balanced negative draw in "
                "_sample_group_balanced_negatives/sample_lipid_class_balanced_negatives "
                "and needs one of balanced_proteins/balance_negatives_by_family/"
                "balanced_lipid_classes to select that draw"
            )

        if not 0.0 <= self.hard_negative_share <= 1.0:
            raise ValueError(
                "hard_negative_share is the sampling-weight mass steered toward "
                f"chemistry-hard candidates and belongs in [0, 1]; got "
                f"{self.hard_negative_share}"
            )

        if self.dissimilar_negative_mining and not (
            self.balanced_proteins
            or self.balance_negatives_by_family
            or self.balanced_lipid_classes
        ):
            raise ValueError(
                "dissimilar_negative_mining reweights the balanced negative draw in "
                "_sample_group_balanced_negatives/sample_lipid_class_balanced_negatives "
                "and needs one of balanced_proteins/balance_negatives_by_family/"
                "balanced_lipid_classes to select that draw"
            )

        if self.dissimilar_negative_mining and self.hard_negative_mining:
            raise ValueError(
                "hard_negative_mining and dissimilar_negative_mining steer the same "
                "per-group negative draw in opposite directions; pass one of them"
            )

        if not 0.0 <= self.dissimilar_negative_share <= 1.0:
            raise ValueError(
                "dissimilar_negative_share is the sampling-weight mass steered toward "
                f"chemistry-DISTANT candidates and belongs in [0, 1]; got "
                f"{self.dissimilar_negative_share}"
            )

        if self.negative_similarity != "tanimoto" or self.negative_similarity_descriptors:
            # Import locally: similarity_pool reaches rdkit through chemistry_prior;
            # the default pool should not load it.
            from dataloader.similarity_pool import (  # noqa: PLC0415
                NAMED_FEATURE_SOURCES,
                NEGATIVE_SIMILARITY_SOURCES,
            )

            if self.negative_similarity not in NEGATIVE_SIMILARITY_SOURCES:
                raise ValueError(
                    f"unknown negative_similarity {self.negative_similarity!r}; "
                    f"expected one of {', '.join(NEGATIVE_SIMILARITY_SOURCES)}"
                )

            if not (self.hard_negative_mining or self.dissimilar_negative_mining):
                raise ValueError(
                    "negative_similarity picks WHICH similarity the negative draw is "
                    "steered by, and nothing steers it without "
                    "hard_negative_mining or dissimilar_negative_mining; the pool "
                    "would be built, recorded in the run report and never read"
                )

            if self.negative_similarity_descriptors:
                if self.negative_similarity not in NAMED_FEATURE_SOURCES:
                    raise ValueError(
                        "negative_similarity_descriptors names the descriptor set a "
                        f"descriptor-fed pool is built from, but negative_similarity "
                        f"is {self.negative_similarity!r}, which has its own fixed "
                        f"matrix; pass one of {', '.join(NAMED_FEATURE_SOURCES)}"
                    )
                from dataloader.descriptors import parse_descriptor_list  # noqa: PLC0415

                parse_descriptor_list(self.negative_similarity_descriptors)

            # Protein similarity uses proteins binding the candidate's lipid, not the
            # sampling group's positives (which would all score 1.0 per protein).
            # This cross-family reference works with every balanced sampler.
            # See dataloader/sampler.py: conditioned_reference.

        if (self.double_coldsplit or self.mixed_coldsplit) and not self.excluded_groups:
            raise ValueError(
                "a lipid-class holdout without excluded_groups leaves every protein in "
                "train, which is a one-axis split on the other axis rather than the "
                "two-axis one it looks like, and there is no held-out family to derive "
                "the classes from. Pass --excluded_groups as well."
            )

        if self.family_only and (
            self.excluded_groups
            or self.double_coldsplit
            or self.mixed_coldsplit
            or self.lipid_coldsplit
            or self.cold_split
        ):
            raise ValueError(
                "family_only already restricts the whole table to one family "
                "before any split runs -- it cannot be combined with "
                "excluded_groups/double_coldsplit/mixed_coldsplit/lipid_coldsplit/"
                "cold_split, which all assume other families are present to hold "
                "out from"
            )

        if self.test_group:
            if not self.excluded_groups:
                raise ValueError("test_group requires excluded_groups to be set")
            if self.test_group not in self.excluded_groups:
                raise ValueError("test_group must be one of excluded_groups")
            if len(self.excluded_groups) < 2:
                raise ValueError(
                    "test_group requires excluded_groups to contain at least one "
                    "other group to source validation data from"
                )
        if self.cold_split and not self.test_group:
            raise ValueError(
                "cold_split requires test_group (a held-out test group distinct "
                "from the validation group); the cold-split submitter sets both "
                "via --excluded_groups=TEST,VAL --test_group=TEST"
            )
        self.lipid_concat = self.lipid_fragments_treatment == "concat"
        self.lipid_random_choice = self.lipid_fragments_treatment == "random_choice"
        self.lipid_fragments_mask = self.lipid_fragments_treatment == "fragments_mask"

        if self.eval_candidates_per_pair < 0:
            raise ValueError(
                "eval_candidates_per_pair is how many candidate structures of a pair "
                "the averaged evaluation scores and cannot be negative; pass 0 for all "
                f"of them. Got {self.eval_candidates_per_pair}"
            )

        if self.eval_average_candidates and not self.lipid_random_choice:
            raise ValueError(
                "eval_average_candidates marginalizes a row over its candidate "
                "structures, which only means something when the treatment picks one "
                "of them: concat and fragments_mask already put every candidate into "
                "the same input. Use it with --lipid_fragments_treatment=random_choice"
            )

        if self.lipid_random_choice and self.lipid_first_fragment_only:
            raise ValueError(
                "lipid_first_fragment_only truncates a row's candidate list to its "
                "first entry before the draw happens, so random_choice would draw the "
                "same structure every time and the two options cancel each other. Drop "
                "lipid_first_fragment_only for a real draw over the candidates, or ask "
                "for the single first candidate through "
                "--lipid_fragments_treatment=concat instead"
            )
        self.ordinary_prot_pooling = self.protein_pooling == "ordinary"
        self.prot_attention_pos_bias = self.protein_pooling == "attention_pos_bias"
        self.prot_pooling_by_pockets = self.protein_pooling == "pooling_by_pockets"
        self.pocket_attention_sites = str(self.pocket_attention_sites).lower()
        if self.pocket_attention_sites not in POCKET_ATTENTION_SITES + ("both",):
            raise ValueError(
                "pocket_attention_sites must be one of "
                f"{', '.join(POCKET_ATTENTION_SITES)}; leave it unset for both, "
                "which is what --attention_by_pockets alone means"
            )
        self.protein_node_feature_count = (
            0 if self.no_protein_geometry
            else 3 + (3 if self.protein_extra_node_features else 0)
        )
        if self.lipid_smiles_tokens and self.lipid_graph_isomers:
            raise ValueError(
                "lipid_smiles_tokens and lipid_graph_isomers are two different lipid "
                "inputs -- a character sequence vs an atom/bond graph -- and "
                "Lipid_encoder builds one branch or the other, never both"
            )
        if self.deepclip:
            if not self.lipid_smiles_tokens:
                raise ValueError(
                    "deepclip reads a one-hot character sequence -- add "
                    "--lipid_smiles_tokens, which is its input (MolFormer's 768-wide "
                    "per-token embedding is a different representation and its own "
                    "experiment)"
                )
            if self.deepclip_filters <= 0:
                raise ValueError("deepclip_filters must be positive")
            if self.deepclip_conv_init not in ("constant", "normal"):
                raise ValueError(
                    "deepclip_conv_init must be 'constant' (DeepCLIP's own 0.01) or "
                    "'normal'"
                )
            if self.deepclip_filters > 1 and self.deepclip_conv_init == "constant":
                raise ValueError(
                    "deepclip_conv_init='constant' sets every weight to the same "
                    "0.01, so the filters of one width start identical and receive "
                    "identical gradients -- they stay one filter in "
                    "deepclip_filters copies forever. That is DeepCLIP's own init and "
                    "is only safe at its own deepclip_filters=1. Use "
                    "--deepclip_conv_init=normal to sweep the filter count"
                )
            if self.deepclip_readout not in ("sum", "mean"):
                raise ValueError("deepclip_readout must be 'sum' or 'mean'")
            if self.deepclip_lstm <= 0:
                raise ValueError("deepclip_lstm must be positive")
            if self.deepclip_conv_layers < 1:
                raise ValueError("deepclip_conv_layers must be at least 1")
            if self.deepclip_gate_hidden <= 0:
                raise ValueError("deepclip_gate_hidden must be positive")
            if self.deepclip_protein_gate and self.deepclip_profile_weights:
                raise ValueError(
                    "deepclip_protein_gate and deepclip_profile_weights are two "
                    "sources for the SAME vector -- the per-channel weights of the "
                    "profile sum. The gate derives them from the pocket, the other "
                    "learns them as one constant for every protein; asking for both "
                    "would silently drop one. Pick one."
                )
            if self.deepclip_protein_tokens:
                from dataloader.protein_tokens import (  # noqa: PLC0415
                    parse_protein_token_alphabets,
                )
                if not parse_protein_token_alphabets(self.deepclip_protein_tokens):
                    raise ValueError("deepclip_protein_tokens names no alphabet")
                if self.deepclip_profile_weights:
                    raise ValueError(
                        "deepclip_protein_tokens feeds the gate, which writes the same "
                        "per-channel profile weights deepclip_profile_weights learns -- "
                        "pick one"
                    )
            if self.deepclip_protein_gate:
                # Import descriptor machinery only when needed; validate tokens before
                # model construction.
                from dataloader.descriptors import parse_descriptor_list  # noqa: PLC0415
                parse_descriptor_list(self.deepclip_protein_gate)
            # Reject invalid --deepclip_widths before model construction.
            parse_deepclip_widths(self.deepclip_widths)
            if self.lipid_concat or self.lipid_fragments_mask:
                raise ValueError(
                    "deepclip cannot be combined with "
                    "--lipid_fragments_treatment=concat/fragments_mask: those lay "
                    "several candidate STRUCTURES end to end on one sequence axis "
                    "(dataloader/graphs_builders/lipid_graph_builder.py), so a window would slide "
                    "across the seam and read a motif spanning two different "
                    "molecules. Use --lipid_fragments_treatment=random_choice (the "
                    "default), which encodes one candidate per sample"
                )
            # DeepCLIP lacks protein encoders, cross-attention, and Final_Layer.
            # Reject alternative architectures and flags whose training/new_train.py
            # model.<attr> accesses need missing modules: final_layer, protein1,
            # lipid_branch_parameters(), or normalization setters. Harmless ignored
            # flags are outside this list. Name flags individually in the error.
            for name in (
                "lipid_only", "protein_only", "descriptors_head",
                "descriptor_heads", "descriptor_mlp", "lipid_graph_isomers",
                "adversarial_grl", "bilinear_fusion",
                "double_attention", "attention_pooling", "swe_pooling",
                "dann_family", "chem_adversary", "lipid_path_handicap",
                "rnabang_frozen_node_adapter",
            ):
                if getattr(self, name, False):
                    raise ValueError(
                        f"deepclip builds only architecture/deepclip.py -- no "
                        f"protein encoder, no cross-attention, no Final_Layer -- so "
                        f"--{name} has nothing to configure. Drop it"
                    )
        if self.deepclip_protein_tokens and not self.deepclip:
            raise ValueError(
                "deepclip_protein_tokens feeds architecture/deepclip.py's gate -- add "
                "--deepclip"
            )
        if self.no_protein_geometry and not self.protein_descriptors:
            raise ValueError(
                "no_protein_geometry drops residue_type/sas_area/volume from every "
                "protein node -- without protein_descriptors a protein node could end "
                "up with no base features at all"
            )
        if self.no_protein_embeddings:
            # Reuse plmon so existing checks also disable frozen replacements,
            # RNA-BAnG adapters, and compression without separate conditions.
            self.plmon = False
        if self.pocket_attention_sites != "both" and not self.attention_by_pockets:
            raise ValueError(
                "pocket_attention_sites narrows attention_by_pockets and does "
                "nothing on its own; enable --attention_by_pockets"
            )
        self.pocket_attention_self = self.attention_by_pockets and (
            self.pocket_attention_sites in ("both", "self")
        )
        # Derive pocket_attention_cross last, after single-partner ablations
        # finalize cross_attention.
        if (
            self.prot_attention_pos_bias
            and self.pocket_attention_self
            and self.pocket_attention_sites == "both"
        ):
            # Only "both" conflicts: restricting one site leaves trainable pocket
            # bias at the other.
            raise ValueError(
                "attention_by_pockets removes non-pocket keys outright, which makes "
                "the prot_attention_pos_bias parameter a constant shift over the "
                "surviving keys -- a no-op under softmax that would never receive "
                "gradient. Either restrict one site only "
                "(--pocket_attention_sites=cross keeps the bias in self-attention, "
                "=self keeps it in cross-attention), or pick another pooling "
                "(--protein_pooling=ordinary / pooling_by_pockets)"
            )
        if self.protein_pockets_only and self.attention_by_pockets:
            raise ValueError(
                "protein_pockets_only already drops every non-pocket residue before "
                "the encoder, so attention_by_pockets has nothing left to mask"
            )
        if self.protein_pockets_only and self.prot_pooling_by_pockets:
            raise ValueError(
                "protein_pockets_only already restricts the nodes; "
                "protein_pooling=pooling_by_pockets would filter an all-pocket set"
            )
        # Validate values even when lipid_path_handicap is off to catch typos now.
        if not 0.0 <= self.lipid_path_weight < 1.0:
            raise ValueError(
                "lipid_path_weight is the lipid branch's handicap and must be in "
                "[0, 1); at 1.0 there is no handicap, above it the lipid branch is "
                "sped up instead"
            )
        if self.lipid_path_weight_ramp_epochs < 0:
            raise ValueError("lipid_path_weight_ramp_epochs must be non-negative")
        if self.hiddim <= 0:
            raise ValueError("hiddim must be greater than zero")
        if self.checkpoint_window <= 0:
            raise ValueError("checkpoint_window must be greater than zero")
        if self.checkpoint_selection_metric and self.checkpoint_selection_metric not in (
            "balanced_accuracy", "auc", "loss",
        ):
            raise ValueError(
                "checkpoint_selection_metric must be one of balanced_accuracy/auc/loss, "
                f"got {self.checkpoint_selection_metric!r}"
            )
        if self.lr_warmup_epochs < 0:
            raise ValueError("lr_warmup_epochs must be non-negative")
        if not 0.0 < self.lr_min_factor <= 1.0:
            raise ValueError("lr_min_factor must be in the range (0, 1]")
        if self.plm_compression_dim <= 0:
            raise ValueError("plm_compression_dim must be greater than zero")
        if self.rnabang_embedding_dim <= 0:
            raise ValueError("rnabang_embedding_dim must be greater than zero")
        if self.geometric_ipa_chunk_size < 0:
            raise ValueError("geometric_ipa_chunk_size must be non-negative")
        rnabang_modes = (
            self.rnabang_replace_esm3,
            self.rnabang_full_protein_encoder,
            self.rnabang_with_esm3,
            self.rnabang_residual_with_esm3,
            self.rnabang_frozen_node_adapter,
        )
        frozen_modes = [
            flag for flag, _, _ in FROZEN_PROTEIN_EMBEDDINGS
            if getattr(self, flag, False)
        ]
        if len(frozen_modes) > 1:
            raise ValueError(
                "these frozen protein embeddings each replace ESM3 and are mutually "
                f"exclusive: {', '.join(frozen_modes)}"
            )
        # ESM3 replacements work with concatenating RNA-BAnG modes, e.g.
        # cat(ProteinMPNN, RNA-BAnG) gives two structure-conditioned inputs.
        # Whole-vector modes (replace_esm3, full_protein_encoder, frozen_node_adapter)
        # allow only one source; the frozen adapter also checks RNA-BAnG width.
        exclusive_rnabang = [
            name for name in (
                "rnabang_replace_esm3",
                "rnabang_full_protein_encoder",
                "rnabang_frozen_node_adapter",
            )
            if getattr(self, name, False)
        ]
        if frozen_modes and exclusive_rnabang:
            raise ValueError(
                f"{frozen_modes[0]} and {exclusive_rnabang[0]} both want to be the "
                "whole protein vector; combine the replacement with "
                "rnabang_with_esm3 or rnabang_residual_with_esm3 instead, which "
                "concatenate"
            )
        if frozen_modes and not self.plmon:
            raise ValueError(f"{frozen_modes[0]} requires plmon")
        for flag, _, dim_attr in FROZEN_PROTEIN_EMBEDDINGS:
            if int(getattr(self, dim_attr)) <= 0:
                raise ValueError(f"{dim_attr} must be greater than zero")
        if sum(rnabang_modes) > 1:
            raise ValueError(
                "rnabang_replace_esm3, rnabang_full_protein_encoder and "
                "rnabang_with_esm3, rnabang_residual_with_esm3 and "
                "rnabang_frozen_node_adapter are mutually exclusive"
            )
        if any(rnabang_modes) and not self.plmon:
            raise ValueError("RNA-BAnG protein modes require plmon")
        if (
            self.use_esm3_v2_embeddings
            and (
                self.rnabang_replace_esm3
                or self.rnabang_full_protein_encoder
                or self.rnabang_frozen_node_adapter
            )
        ):
            raise ValueError(
                "use_esm3_v2_embeddings is only meaningful with "
                "rnabang_with_esm3 or rnabang_residual_with_esm3, not "
                "RNA-BAnG-only modes"
            )
        self.mlp_widths = {site: int(width) for site, width in self.mlp_widths.items()}
        if any(width <= 0 for width in self.mlp_widths.values()):
            raise ValueError("mlp_widths must all be greater than zero")
        self.plm_compression_dims = [int(dim) for dim in self.plm_compression_dims]
        if any(dim <= 0 for dim in self.plm_compression_dims):
            raise ValueError("plm_compression_dims must all be greater than zero")
        if self.final_m is not None and self.final_m <= 0:
            raise ValueError("final_m must be greater than zero")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in the range [0, 1)")
        if not 0.0 <= self.final_dropout < 1.0:
            raise ValueError("final_dropout must be in the range [0, 1)")
        if self.final_dropout == 0.0 and self.dropout > 0.0:
            self.final_dropout = self.dropout
        if self.hiddim % self.HEADS != 0:
            raise ValueError(
                f"hiddim ({self.hiddim}) must be divisible by HEADS ({self.HEADS})"
            )
        # Apply hiddim constraints: branch width sets self-attention embed_dim
        # and conv per-head output width.
        for field_name in ("protein_hiddim", "lipid_hiddim"):
            width = getattr(self, field_name)
            if width is None:
                continue
            if width <= 0:
                raise ValueError(f"{field_name} must be greater than zero")
            if width % self.HEADS != 0:
                raise ValueError(
                    f"{field_name} ({width}) must be divisible by HEADS ({self.HEADS})"
                )
        asymmetric = [
            name for name in ("protein_hiddim", "lipid_hiddim")
            if getattr(self, name) is not None and getattr(self, name) != self.hiddim
        ]
        if asymmetric and self.double_attention:
            # The second encoder receives hiddim-wide cross-attention output but
            # uses branch width, so widths must match. A second adapter would change
            # the tested architecture. No current config uses --double_attention.
            raise ValueError(
                f"{'/'.join(asymmetric)} differs from hiddim ({self.hiddim}), which "
                "--double_attention does not support: its second encoder pass reads "
                "cross-attention output, always hiddim wide"
            )
        protein_conv_modes = (
            self.geometric_transformer,
            self.transformer_conv,
            self.gine_conv,
            self.protein_edge_attention,
            self.protein_edge_mlp,
        )
        if sum(protein_conv_modes) > 1:
            raise ValueError(
                "geometric_transformer, transformer_conv, gine_conv, "
                "protein_edge_attention and protein_edge_mlp are mutually exclusive"
            )
        if self.lipid_edge_attention and self.lipid_edge_mlp:
            raise ValueError(
                "lipid_edge_attention and lipid_edge_mlp are mutually exclusive"
            )
        lipid_edge_fields = (
            self.lipid_edge_attention,
            self.lipid_edge_mlp,
            self.lipid_edge_mlp_lambda,
        )
        if any(value is not None for value in lipid_edge_fields) and not self.lipid_graph_isomers:
            # Without a lipid graph, these flags would describe unused settings.
            raise ValueError(
                "lipid_edge_attention/lipid_edge_mlp/lipid_edge_mlp_lambda only apply "
                "to the chemical graph --lipid_graph_isomers builds; without that flag "
                "the lipid branch is a MolFormer projection with no edges"
            )
        if self.lipid_edge_mlp_lambda is not None and self.lipid_edge_mlp_lambda <= 0:
            raise ValueError("lipid_edge_mlp_lambda must be greater than zero")
        if self.lipid_edge_mlp_lambda is not None and not (
            self.lipid_edge_mlp
            or (self.lipid_edge_mlp is None and self.protein_edge_mlp)
        ):
            # Only EdgeMLPConv uses this divisor; attention and GATv2 ignore it.
            raise ValueError(
                "lipid_edge_mlp_lambda has no effect unless the lipid graph uses "
                "EdgeMLPConv -- set --lipid_edge_mlp, or leave it inheriting "
                "--protein_edge_mlp"
            )
        if self.geometric_transformer and any(rnabang_modes):
            raise ValueError(
                "geometric_transformer cannot be combined with RNA-BAnG embedding modes"
            )
        if (self.protein_edge_attention or self.protein_edge_mlp) and self.bidirectional_edges:
            raise ValueError(
                "protein_edge_attention/protein_edge_mlp build native bidirectional "
                "structured edges (direction- and rotation-dependent); "
                "bidirectional_edges would incorrectly copy them onto the reversed "
                "edge instead of recomputing the orientation"
            )
        edge_geometry_variants = (
            self.protein_edge_rbf_count != 16
            or self.protein_edge_orientation_scalar
            or self.protein_edge_raw3
        )
        if edge_geometry_variants and not (self.protein_edge_attention or self.protein_edge_mlp):
            raise ValueError(
                "protein_edge_rbf_count/protein_edge_orientation_scalar/"
                "protein_edge_raw3 only apply to the structured edge vector built "
                "under protein_edge_attention/protein_edge_mlp"
            )
        if self.protein_edge_raw3 and (
            self.protein_edge_rbf_count != 16 or self.protein_edge_orientation_scalar
        ):
            raise ValueError(
                "protein_edge_raw3 bypasses structured_edge_features entirely, so "
                "protein_edge_rbf_count/protein_edge_orientation_scalar would be "
                "silently ignored -- combining them is almost certainly a mistake"
            )
        if self.protein_edge_rbf_count <= 0:
            raise ValueError("protein_edge_rbf_count must be positive")
        if self.rnabang_frozen_node_adapter and self.double_attention:
            raise ValueError(
                "rnabang_frozen_node_adapter cannot be combined with double_attention"
            )
        if self.cross_attention_chain_bias and not self.lipid_graph_isomers:
            raise ValueError(
                "cross_attention_chain_bias needs per-atom chain_rank, which only "
                "exists under lipid_graph_isomers"
            )
        edge_node_modes = (
            self.rnabang_edge_current,
            self.rnabang_edge_topk_by_area,
            self.rnabang_edge_deepsets,
            self.rnabang_edge_pna,
            self.rnabang_edge_quantiles,
            self.rnabang_edge_set_transformer,
        )
        if sum(edge_node_modes) > 1:
            raise ValueError("RNA-BAnG edge-to-node modes are mutually exclusive")
        if any(edge_node_modes) and not self.rnabang_frozen_node_adapter:
            raise ValueError(
                "RNA-BAnG edge-to-node modes require rnabang_frozen_node_adapter"
            )
        if (
            self.rnabang_residue_type_embedding
            and not self.rnabang_frozen_node_adapter
        ):
            raise ValueError(
                "rnabang_residue_type_embedding requires "
                "rnabang_frozen_node_adapter"
            )
        if self.rnabang_residual_with_esm3 and (
            self.transformer_conv or self.gine_conv
        ):
            raise ValueError(
                "rnabang_residual_with_esm3 replaces the protein graph convolution "
                "and cannot be combined with transformer_conv or gine_conv"
            )
        self.pool_type = str(self.pool_type).lower()
        if self.pool_type not in POOL_TYPES:
            raise ValueError(f"pool_type must be one of {', '.join(POOL_TYPES)}")
        act_fn_key = str(self.act_fn).lower()
        if act_fn_key not in ACT_FNS:
            raise ValueError(f"act_fn must be one of {', '.join(ACT_FNS)}")
        self.act_fn = act_fn_key
        if self.protein_gine_residual and not self.gine_conv:
            raise ValueError("protein_gine_residual requires gine_conv")
        if self.protein_gat_residual and self.gine_conv:
            raise ValueError("protein_gat_residual requires gine_conv to be disabled")
        if self.protein_gat_residual and self.rnabang_residual_with_esm3:
            raise ValueError(
                "protein_gat_residual is unavailable with "
                "rnabang_residual_with_esm3 because that mode does not use GATv2"
            )
        if self.structured_sparsity:
            self.sparsity_mode = str(self.sparsity_mode).lower()
            if self.sparsity_mode not in ("l0", "l1"):
                raise ValueError("sparsity_mode must be 'l0' or 'l1'")
            if self.sparsity_lambda < 0.0:
                raise ValueError("sparsity_lambda must be non-negative")
            if self.target_sparsity is not None and not 0.0 <= self.target_sparsity < 1.0:
                raise ValueError("target_sparsity must be in [0, 1)")
        if self.bilevel_lr <= 0.0:
            raise ValueError("bilevel_lr must be greater than zero")
        if self.concrete_dropout_reg < 0.0:
            raise ValueError("concrete_dropout_reg must be non-negative")
        if self.concrete_dropout_weight_reg < 0.0:
            raise ValueError("concrete_dropout_weight_reg must be non-negative")
        if self.bilevel and not (self.gate_all_mlp_hidden or self.gate_all_mlp_layers):
            # Validation optimizes width gates; Concrete Dropout uses train loss.
            # Thus bilevel needs width gates.
            raise ValueError("bilevel requires gate_all_mlp_hidden (the width gates it optimizes)")
        if self.gate_all_mlp_hidden or self.gate_all_mlp_layers:
            # Width gates reuse make_gate's sparsity_mode/sparsity_lambda even
            # without structured_sparsity; validate those settings here too.
            self.sparsity_mode = str(self.sparsity_mode).lower()
            if self.sparsity_mode not in ("l0", "l1"):
                raise ValueError("sparsity_mode must be 'l0' or 'l1'")
            if self.sparsity_lambda < 0.0:
                raise ValueError("sparsity_lambda must be non-negative")
        if (
            self.protein_self_attention
            and self.protein_disable_pre_sa_mlp
            and not self.gine_conv
            and not self.rnabang_full_protein_encoder
            and not self.rnabang_residual_with_esm3
            and not self.rnabang_frozen_node_adapter
        ):
            raise ValueError(
                "protein_disable_pre_sa_mlp requires gine_conv when "
                "protein_self_attention is enabled"
            )
        if self.protein_balance_weight and (
            self.protein_class_weight or self.protein_class_sqrt_weight
        ):
            # Averaging two per-protein weight schemes balances neither.
            raise ValueError(
                "protein_balance_weight cannot be combined with protein_class_weight "
                "or protein_class_sqrt_weight: the parts are averaged, and the mean of "
                "two per-protein balancing tables balances neither"
            )

        if self.marginal_balance_weight and (
            self.protein_balance_weight or self.protein_class_weight
            or self.protein_class_sqrt_weight
        ):
            # marginal_balance_weight already balances proteins. Averaging it with
            # another protein scheme in common_weights_parts breaks that balance.
            raise ValueError(
                "marginal_balance_weight cannot be combined with protein_balance_weight, "
                "protein_class_weight or protein_class_sqrt_weight: the parts are "
                "averaged, and it already balances every protein on its own"
            )
        if self.protein_class_weight and self.protein_class_sqrt_weight:
            raise ValueError(
                "protein_class_weight and protein_class_sqrt_weight "
                "are mutually exclusive"
            )
        if self.balanced_batches and self.batch < 2:
            raise ValueError("balanced_batches requires batch >= 2")
        if not 0.0 < self.pu_rho < 1.0:
            raise ValueError("pu_rho must be in the range (0, 1)")
        if self.pu_unlabeled_positive_fraction is not None:
            if not 0.0 <= self.pu_unlabeled_positive_fraction < 1.0:
                raise ValueError(
                    "pu_unlabeled_positive_fraction must be in the range [0, 1)"
                )
        if self.pu_rho_by_subclass:
            if not self.pu_loss:
                raise ValueError("pu_rho_by_subclass requires pu_loss")
            if self.pu_unlabeled_positive_fraction is None:
                raise ValueError(
                    "pu_rho_by_subclass derives each subclass's prior from its own "
                    "train counts, which needs pu_unlabeled_positive_fraction; a "
                    "single manual pu_rho has nothing to vary by subclass"
                )
        if self.pu_beta < 0.0:
            raise ValueError("pu_beta must be non-negative")
        if self.pu_gamma <= 0.0:
            raise ValueError("pu_gamma must be positive")
        if self.pu_tau <= 0.0:
            raise ValueError("pu_tau must be positive")
        if self.pu_loss_cap <= 0.0:
            raise ValueError("pu_loss_cap must be positive")
        if self.focal_gamma < 0.0:
            raise ValueError("focal_gamma must be non-negative")
        if self.focal_loss and self.pu_loss:
            raise ValueError(
                "focal_loss is not supported together with pu_loss: the focal "
                "modulation breaks the bounded, symmetric surrogate the nnPU "
                "risk estimator relies on"
            )
        if self.focal_loss and self.loss_type != "cross_entropy":
            raise ValueError("focal_loss requires loss_type=cross_entropy")
        if self.logit_adjustment_tau < 0.0:
            raise ValueError("logit_adjustment_tau must be non-negative")
        if self.logit_adjustment and self.pu_loss:
            raise ValueError(
                "logit_adjustment is not supported together with pu_loss "
                "(pu_rho already encodes the class prior)"
            )
        if self.logit_adjustment and self.loss_type != "cross_entropy":
            raise ValueError("logit_adjustment requires loss_type=cross_entropy")
        if self.prot_pos_bias_per_head and not (
            self.prot_attention_pos_bias or self.prot_pooling_by_pockets
        ):
            raise ValueError(
                "prot_pos_bias_per_head requires protein_pooling=attention_pos_bias "
                "or pooling_by_pockets"
            )
        if self.double_attention:
            self.cross_attention = True
        if self.lipid_only and self.protein_only:
            raise ValueError("lipid_only and protein_only are mutually exclusive")
        if self.bilinear_fusion and (self.lipid_only or self.protein_only):
            # Zeroing either partner reduces bilinear fusion to a constant bias,
            # making single-partner ablation meaningless.
            raise ValueError(
                "bilinear_fusion cannot be combined with lipid_only/protein_only"
            )
        if self.bilinear_weight_decay is not None and not self.bilinear_fusion:
            raise ValueError(
                "bilinear_weight_decay requires bilinear_fusion -- there is no "
                "self.bilinear parameter group to apply it to otherwise"
            )
        if self.deepclip_gate_weight_decay is not None and not (
            self.deepclip_protein_gate or self.deepclip_protein_tokens
        ):
            raise ValueError(
                "deepclip_gate_weight_decay requires deepclip_protein_gate or "
                "deepclip_protein_tokens -- there is "
                "no gate parameter group to apply it to otherwise"
            )
        if self.deepclip_gate_weight_decay is not None and self.deepclip_gate_weight_decay < 0.0:
            raise ValueError("deepclip_gate_weight_decay must be non-negative")
        if self.bilinear_weight_decay is not None and self.bilinear_weight_decay < 0.0:
            raise ValueError("bilinear_weight_decay must be non-negative")
        if self.bilinear_pooled_norm and not self.bilinear_fusion:
            raise ValueError(
                "bilinear_pooled_norm requires bilinear_fusion -- there is no pooled "
                "product to normalise the inputs of otherwise"
            )
        if self.adversarial_grl and (self.lipid_only or self.protein_only):
            # Zeroing a partner makes its label adversary trivial and invalidates ablation.
            raise ValueError(
                "adversarial_grl cannot be combined with lipid_only/protein_only"
            )
        if self.lipid_path_handicap and (self.lipid_only or self.protein_only):
            # The protein head start needs both branches. With protein_only, it slows
            # an unused branch; with lipid_only, it just lowers the global LR.
            raise ValueError(
                "lipid_path_handicap cannot be combined with lipid_only/protein_only"
            )
        if self.adv_weight < 0.0:
            raise ValueError("adv_weight must be non-negative")
        if self.adv_lambda < 0.0:
            raise ValueError("adv_lambda must be non-negative")
        if self.attention_pooling_pocket_bias and not self.attention_pooling:
            raise ValueError(
                "attention_pooling_pocket_bias requires attention_pooling"
            )
        if self.rank_within_protein and self.loss_type != "pairwise_rank":
            raise ValueError("rank_within_protein requires loss_type=pairwise_rank")
        if self.group_dro:
            if self.loss_type != "cross_entropy":
                raise ValueError("group_dro requires loss_type=cross_entropy")
            if self.pu_loss:
                raise ValueError("group_dro is incompatible with pu_loss")
            if self.group_dro_step_size <= 0.0:
                raise ValueError("group_dro_step_size must be positive")
            if self.group_dro_adj < 0.0:
                raise ValueError("group_dro_adj must be non-negative")
        if self.chem_adversary and not (self.chem_prior or self.pocket_compat_prior):
            raise ValueError(
                "chem_adversary requires chem_prior and/or pocket_compat_prior -- it "
                "regresses on whichever frozen prior terms are attached, and needs at "
                "least one"
            )
        head_modes = [
            name for name in ("descriptors_head", "descriptor_mlp")
            if getattr(self, name)
        ]
        if len(head_modes) > 1:
            raise ValueError(
                ", ".join(head_modes) + " are different sufficiency-test branches "
                "Final_Layer can build -- pick one"
            )
        heads = ()
        if self.descriptor_heads or head_modes:
            # Import locally to keep ModelConfig-only analysis free of rdkit.
            # Validate descriptor tokens before model construction.
            from dataloader.descriptors import parse_descriptor_heads

            heads = parse_descriptor_heads(self.descriptor_heads)
        if head_modes and not heads:
            raise ValueError(
                f"{head_modes[0]} requires --descriptor_heads to name at least one "
                "descriptor"
            )
        if self.descriptor_mlp and len(heads) != 1:
            raise ValueError(
                "descriptor_mlp reads exactly one --descriptor_heads segment (one "
                f"MLP over one token list), got {len(heads)}"
            )
        if heads and not head_modes and self.bilinear_fusion:
            # Post-fusion descriptor concat restores the shortcut bilinear_fusion blocks.
            raise ValueError(
                "descriptor_heads cannot be combined with bilinear_fusion -- its "
                "vector would be concatenated after the bilinear product, the same "
                "shortcut bilinear_fusion is meant to close"
            )
        if head_modes:
            # Descriptor-only Final_Layer builds a descriptor path and small classifier;
            # these flags need modules it does not build (see __init__).
            unsupported = [
                name for name in (
                    "bilinear_fusion", "adversarial_grl", "dann_family", "chem_prior",
                    "chem_adversary", "pocket_compat_prior",
                    "attention_pooling", "swe_pooling",
                    "lipid_only", "protein_only", "lipid_path_handicap",
                    "double_attention", "protein_descriptors", "lipid_descriptors",
                    "node_bilinear_fusion",
                )
                if getattr(self, name)
            ]
            if unsupported:
                raise ValueError(
                    f"{head_modes[0]} builds only the descriptor path and a small "
                    "classifier -- protein1/lipid1/cross_attention1/final_layer's "
                    "usual modules are never built, so these options have nothing to "
                    "attach to: " + ", ".join(unsupported)
                )
        if self.protein_descriptors or self.lipid_descriptors:
            from dataloader.descriptors import parse_descriptor_list

            if self.protein_descriptors:
                parse_descriptor_list(self.protein_descriptors)
            if self.lipid_descriptors:
                parse_descriptor_list(self.lipid_descriptors)
        if (self.chem_lambda_ramp or self.chem_lambda_ramp_by_fit) and not self.chem_adversary:
            raise ValueError("chem_lambda_ramp/chem_lambda_ramp_by_fit require chem_adversary")
        if self.swe_pooling and self.attention_pooling:
            # Both replace pool_type. Reject the conflict so the run label matches
            # the actual pooling choice.
            raise ValueError("swe_pooling cannot be combined with attention_pooling")
        if self.swe_pooling and self.swe_reference_points < 2:
            raise ValueError("swe_reference_points must be at least 2")
        if self.swe_freeze_reference and not self.swe_pooling:
            raise ValueError("swe_freeze_reference requires swe_pooling")
        if self.lipid_only or self.protein_only:
            # Disable cross-attention: partner leakage would prevent pooled zeroing
            # from isolating one branch.
            if self.double_attention:
                raise ValueError(
                    "lipid_only/protein_only cannot be used with double_attention"
                )
            self.cross_attention = False
        if self.node_bilinear_fusion and not self.cross_attention:
            # node_bilinear_fusion needs CrossAttention's node pairs, which disappear
            # when cross_attention is disabled or a single-partner ablation turns it off.
            raise ValueError(
                "node_bilinear_fusion requires cross_attention -- there is no lipid/"
                "protein node pairing to reuse otherwise"
            )
        # Derive key restrictions after cross_attention is final; otherwise the
        # run report could claim a restriction never applied.
        self.pocket_attention_cross = self.attention_by_pockets and (
            self.pocket_attention_sites in ("both", "cross")
        ) and self.cross_attention
        if (
            self.attention_by_pockets
            and self.pocket_attention_sites == "cross"
            and not self.cross_attention
        ):
            raise ValueError(
                "pocket_attention_sites=cross restricts the cross-attention keys, "
                "but cross_attention is off"
            )
        if self.attention_by_pockets and not (
            self.pocket_attention_self or self.pocket_attention_cross
        ):
            raise ValueError(
                "attention_by_pockets is on but restricts no site; check "
                "pocket_attention_sites and cross_attention"
            )

    def effective_pu_rho(self, positive_count, unlabeled_count):
        """Return manual or train-derived PU rho."""
        if self.pu_unlabeled_positive_fraction is None:
            return self.pu_rho

        positive_count = float(positive_count)
        unlabeled_count = float(unlabeled_count)
        total_count = positive_count + unlabeled_count
        if total_count <= 0.0:
            raise ValueError("PU rho cannot be derived from an empty train set")

        rho = (
            positive_count
            + self.pu_unlabeled_positive_fraction * unlabeled_count
        ) / total_count
        if not 0.0 < rho < 1.0:
            raise ValueError(
                "derived PU rho must be in the range (0, 1); "
                f"got {rho:.6f}"
            )
        return rho

    def frozen_protein_embedding(self):
        """Return the active ESM3 replacement as (file suffix, width), or None.

        Loader and encoder share this width to prevent input mismatches.
        """
        for flag, suffix, dim_attr in FROZEN_PROTEIN_EMBEDDINGS:
            if getattr(self, flag, False):
                return suffix, int(getattr(self, dim_attr))
        return None

    def ramped_lipid_path_weight(self, epoch_index):
        """Return the lipid branch's epoch-start gradient scale.

        Without a ramp, use lipid_path_weight. Otherwise ramp linearly from that
        value at epoch 0 to 1.0 at lipid_path_weight_ramp_epochs. Linear growth
        gives the protein branch an early head start; Ganin's sigmoid would spend
        those epochs near the starting value. This is not adversarial warm-up.
        Callers check lipid_path_handicap, as they check flags for ramped_adv_lambda.
        """
        if not self.lipid_path_weight_ramp_epochs:
            return self.lipid_path_weight
        progress = min(
            1.0, max(0.0, epoch_index / float(self.lipid_path_weight_ramp_epochs))
        )
        return self.lipid_path_weight + progress * (1.0 - self.lipid_path_weight)

    def ramped_adv_lambda(self, progress):
        """Return per-partner gradient-reversal strength.

        Without ramp flags, use adv_lambda. Ramping lets noisy encoders learn
        before adversaries suppress shortcuts.
        adv_lambda_ramp uses Ganin & Lempitsky's epoch schedule:
        lambda(p) = adv_lambda * (2/(1+exp(-10p)) - 1).
        adv_lambda_ramp_by_fit takes precedence and uses linear fit progress,
        from 0 to adv_lambda. A sigmoid on saturating fit progress peaks too early.
        The choice is empirical, but fit progress tracks learning directly: after
        a long chance plateau, an epoch ramp may already be strong when
        memorization starts; a fit ramp stays weak until learning begins.
        """
        import math

        if self.adv_lambda_ramp_by_fit:
            return self.adv_lambda * min(max(float(progress), 0.0), 1.0)
        if not self.adv_lambda_ramp:
            return self.adv_lambda
        return self.adv_lambda * (2.0 / (1.0 + math.exp(-10.0 * progress)) - 1.0)

    def ramped_dann_lambda(self, progress):
        """Return family-DANN gradient-reversal strength.

        Without ramp flags, use dann_lambda. Both ramps are linear from 0 to
        dann_lambda; clamp progress to [0, 1]. The epoch ramp preserves prior
        behavior. dann_lambda_ramp_by_fit takes precedence and uses
        adv_fit_progress, for the timing reasons in ramped_adv_lambda.
        This head reaches joint memorization in the fused vector, so poor timing
        costs more than for a per-partner adversary.
        """
        if self.dann_lambda_ramp_by_fit or self.dann_lambda_ramp:
            return self.dann_lambda * min(max(float(progress), 0.0), 1.0)
        return self.dann_lambda

    def ramped_chem_lambda(self, progress):
        """Return chemistry-adversary reversal strength, as in ramped_dann_lambda.

        Fit-based timing matters because this head reaches the fused vector.
        Suppressing s_chem before the model learns wastes the training budget.
        """
        if self.chem_lambda_ramp_by_fit or self.chem_lambda_ramp:
            return self.chem_lambda * min(max(float(progress), 0.0), 1.0)
        return self.chem_lambda

    def adv_fit_progress(self, train_balanced_accuracy):
        """Map train balanced accuracy to fit progress in [0, 1].

        Use (BA - 0.5) / 0.5: chance maps to 0, perfect fit to 1; clamp below chance.
        Callers must keep progress monotone. Lambda changes the fit it measures;
        allowing progress to fall creates a suppress/recover feedback loop.
        """
        if train_balanced_accuracy is None:
            return 0.0
        return min(max((float(train_balanced_accuracy) - 0.5) / 0.5, 0.0), 1.0)

    def make_activation(self):
        """Return the configured activation module."""
        import torch

        if self.act_fn == "leakyrelu":
            return torch.nn.LeakyReLU()
        if self.act_fn == "prelu":
            # Start at leakyrelu's slope 0.01, then learn an independent negative
            # slope for each make_activation() call.
            return torch.nn.PReLU(init=0.01)
        if self.act_fn == "relu":
            return torch.nn.ReLU()
        return torch.nn.GELU()

    @property
    def loslis(self):
        """Return supported losses by name."""
        import torch

        return {
            "mse": torch.nn.MSELoss(),
            "cross_entropy": torch.nn.CrossEntropyLoss(),
            "bce": torch.nn.BCELoss(),
        }

    @property
    def loss(self):
        """Return the loss selected by loss_type."""
        return self.loslis[self.loss_type]

    @property
    def pool_list(self):
        """Return supported graph pooling functions by name."""
        from torch_geometric.nn import global_add_pool, global_max_pool, global_mean_pool
        import torch

        def global_add_max_pool(nodes, batch):
            return torch.cat(
                [
                    global_add_pool(nodes, batch),
                    global_max_pool(nodes, batch),
                ],
                dim=1,
            )

        return {
            "add": global_add_pool,
            "max": global_max_pool,
            "mean": global_mean_pool,
            "add_max": global_add_max_pool,
            # Learnable GeMPool is a submodule (architecture.final_layer), not a
            # stateless function. Final_Layer never calls this placeholder.
            "gem": None,
        }

    @property
    def pool(self):
        """Return the pooling function selected by pool_type."""
        return self.pool_list[self.pool_type]


def set_config_field(field, cast=lambda value: value):
    """Create a handler that parses and sets a config field."""
    return lambda config, value: setattr(config, field, cast(value))


def set_config_flag(field, value=True):
    """Create a handler that sets a fixed config value."""
    return lambda config: setattr(config, field, value)


# Each name is both the CLI flag (--name) and the ModelConfig field it sets to
# True. A flag's own comment, where one exists, explains a non-obvious consequence.
BOOL_FLAG_NAMES = (
    # --- 1. Global model type (whole-architecture replacement) ---
    # Build DeepCLIP (architecture/deepclip.py) and nothing else -- no protein
    # encoder, no cross-attention, no Final_Layer. This is a different network, not a
    # branch or an ablation of this project's model: one-hot SMILES -> convolutions
    # -> BLSTM -> per-position profile -> sum. Requires --lipid_smiles_tokens, which
    # is its input. DeepCLIP defaults come from its constants.py.
    "deepclip",
    "descriptors_head",  # self-attention model; see --descriptor_heads; excl. descriptor_mlp, deepclip, most other heads
    "descriptor_mlp",  # MLP model; see --descriptor_heads; excl. descriptors_head
    # Diagnostic shortcut ablation: zero one pooled partner before the final
    # classifier (and disable cross-attention) so the model must decide from the
    # other partner alone. lipid_only hides the protein, protein_only hides the
    # lipid. Used to confirm which partner's identity is being memorized on cold
    # splits (lipid_only and protein_only are mutually exclusive).
    # excl. protein_only, double_attention, bilinear_fusion, lipid_path_handicap.
    "lipid_only",
    "protein_only",  # protein-side version of lipid_only; same exclusions

    # --- 2. Protein graph encoder (conv architecture + edge features) ---
    "transformer_conv",  # PyG TransformerConv instead of GATv2Conv for the protein graph; excl. other protein conv modes, rnabang_residual_with_esm3
    "gine_conv",  # GINEConv (with optional residual) instead of GATv2Conv; also the lipid graph's default conv under lipid_graph_isomers; excl. other protein conv modes
    # Literal Ingraham (attention) / Dauparas (MLP message-passing) conv layers over
    # the 25-dim structured edge features (architecture/protein_edge_geometry.py),
    # replacing GATv2Conv/TransformerConv/GINEConv's own edge_dim=3 input in
    # _make_protein_conv. The same choice also swaps GATv2Conv in
    # architecture/lipid_encoder.py's --lipid_graph_isomers path -- one switch for
    # both graphs, not a separate lipid flag.
    # excl. other protein conv modes, bidirectional_edges.
    "protein_edge_attention",
    "protein_edge_mlp",  # Dauparas-style edge-MLP conv over the same structured edge features; excl. other protein conv modes, bidirectional_edges
    "geometric_transformer",  # RoPE/IPA transformer block over SE(3) residue frames instead of the GAT conv; excl. transformer_conv/gine_conv/protein_edge_attention/_mlp, RNA-BAnG embeddings
    "single_gat_layer",  # one GATv2 layer for the protein graph instead of two; default on
    "protein_gat_residual",  # residual connection around the single GAT conv output; requires gine_conv to be off; excl. rnabang_residual_with_esm3
    "protein_gine_residual",  # gated residual around the GINEConv message; requires gine_conv
    "bidirectional_edges",  # mirrors each protein edge onto its reverse direction for the plain GATv2/TransformerConv/GINEConv path; excl. protein_edge_attention/_mlp (already natively bidirectional)
    # Replace the 4-dim relative-orientation quaternion with 1 scalar (cosine
    # between the two residues' local Z axes -- parallel/antiparallel packing).
    # Requires protein_edge_attention/mlp.
    # excl. protein_edge_raw3.
    "protein_edge_orientation_scalar",
    # Use the plain [distance, area, boundary] edge_attr (edge_dim=3) as input to
    # EdgeAttentionConv/EdgeMLPConv instead of the structured RBF/direction/
    # orientation vector -- isolates the message-passing mechanism itself from
    # the geometric feature expansion. Requires protein_edge_attention/mlp.
    # excl. protein_edge_orientation_scalar and a non-default --protein_edge_rbf_count.
    "protein_edge_raw3",
    "protein_gat_graph_norm",  # graph-norm on the GAT/conv output before self-attention

    # --- 3. Lipid graph encoder / input representation ---
    "lipid_isomers",  # dataset-level: selects the isomeric data table/CSV the dataloader reads, not an architecture switch
    "lipid_graph_isomers",  # chemical-graph lipid encoder (GATv2 over atoms/bonds) instead of the MolFormer-embedding path; excl. lipid_smiles_tokens, deepclip
    # One lipid node per canonical SMILES character: 20-column one-hot
    # SMILES_VOCABULARY (dataloader/smiles_tokens.py), replacing 768-dim
    # MoLFormer tokens. Dataloader.py then skips loading the MoLFormer table.
    # Uses DeepCLIP's one-hot input idea (Gronning et al., NAR 2020);
    # --lipid_conv_filters scans contiguous substrings such as head groups.
    # Sequence is preserved, but pretrained chemistry is lost: one-hot tokens
    # encode no oxygen properties. The branch must learn chemistry from this
    # project's ~1287 distinct structures.
    # excl. lipid_graph_isomers.
    "lipid_smiles_tokens",

    # Bare flags only enable a lipid conv. No flag selects plain lipid GATv2
    # while the protein uses EdgeMLPConv; that option has not been requested.
    # Override lipid graph conv and EdgeMLPConv divisor. None inherits the
    # protein settings, preserving existing arg files and run behavior.
    # Protein graphs use Voronota contacts (~30 neighbors/residue, 25-dim SE(3)
    # frame edges); lipid graphs use 2-4 bonds/atom and 22-dim bond features
    # (LIPID_ISOMER_EDGE_DIM). Sharing settings has two effects:
    # - EdgeMLPConv divides message sums by a constant. Dauparas et al.'s 30
    #   approximates a protein mean, but makes lipid updates ~10x too small.
    #   Use measured mean degree (analysis/probes/lipid_graph_degree.py).
    # - edge_mlp outputs hiddim, while attention/GATv2 outputs hiddim * HEADS.
    #   In past runs, choosing protein edge_mlp also narrowed lipid output 8x,
    #   already the --lipid_coldsplit bottleneck.
    # All past --lipid_graph_isomers runs inherited protein conv and lambda=30.
    # The direct graph ablation was flat for both conv variants, including
    # attention without either scaling or width issue. The
    # mis-scaled divisor is real, but does not explain those flat results.
    # See architecture/lipid_encoder.py.
    # excl. lipid_edge_mlp.
    "lipid_edge_attention",
    "lipid_edge_mlp",  # forces the lipid graph conv to edge-MLP; requires lipid_graph_isomers; excl. lipid_edge_attention
    "lipid_gat_graph_norm",  # graph-norm on the lipid GAT conv output

    # --- 4. Protein input / frozen embeddings ---
    "plmon",  # master switch (default on) for whether ESM3/any replacement contributes to protein nodes ; forced off by no_protein_embeddings
    # Disable --plmon on the protein side. MolFormer and lipid graphs stay
    # unchanged. No companion flag is needed: protein_node_columns() keeps
    # geometry unless --no_protein_geometry is set. That flag independently
    # requires --protein_descriptors, so combining them cannot empty nodes.
    "no_protein_embeddings",
    # Drop residue_type/sas_area/volume and any --protein_extra_node_features
    # from protein_node_columns() in dataloader/graphs_builders/protein_graph_builder.py.
    # Requires --protein_descriptors to prevent empty nodes (validate()).
    # Independent of --no_protein_embeddings; ESM and MolFormer stay unchanged.
    "no_protein_geometry",
    # Frozen structure-conditioned ESM3 replacement; see FROZEN_PROTEIN_EMBEDDINGS.
    # ProteinMPNN: ~1.7M parameters, message passing over each residue's k nearest
    # neighbours with N/CA/C/O/Cb distances. Encoder output, before any sequence
    # decoding -- pure local geometry, the cheapest of the three by two orders of
    # magnitude.
    # excl. esmif1_replace_esm3 and the whole-vector RNA-BAnG modes.
    "proteinmpnn_replace_esm3",
    # ESM-IF1: ~142M, inverse folding over backbone coordinates. Its vector answers
    # "which residue belongs in this geometry", which is a description of the site.
    # excl. proteinmpnn_replace_esm3 and the whole-vector RNA-BAnG modes.
    "esmif1_replace_esm3",
    # Use the v2 ESM3 embeddings (preprocessing/embed_protein_esm3_v2.py, read from
    # data/embedding_ESM3_v2/) built from a real structure+coordinates+SASA+confidence
    # input (data/esm3_input/<stem>.pdb, preprocessing/build_consistent_esm3_pdb.py)
    # instead of the v1 sequence-only embeddings in data/embedding_ESM3/. When this is
    # on and attention_pooling_pocket_bias is also on, the pocket-bias term in
    # AttentionPool uses the real per-node pLDDT/B-factor-derived confidence in
    # data/esm3_input/<stem>_node_confidence.csv instead of the binary pocket flag
    # from pocketness.pdb, which marks Voronota pocket membership, not confidence.
    # requires rnabang_with_esm3/rnabang_residual_with_esm3.
    "use_esm3_v2_embeddings",
    # RNA-BAnG protein representations are generated offline by
    # preprocessing/embed_protein_rnabang.py and have one 128-dimensional row per
    # graph residue. The five ways of consuming them below are mutually exclusive.
    # Feed RNA-BAnG rows instead of ESM3 into the existing protein GNN.
    "rnabang_replace_esm3",
    # Treat RNA-BAnG as the complete first protein encoder (projection, optional
    # self-attention, post-SA MLP), so no graph convolution runs on it .
    "rnabang_full_protein_encoder",
    # Concatenate the ESM3 and RNA-BAnG rows before the existing protein GNN.
    "rnabang_with_esm3",
    # Replace GATv2 with an edge-aware residual path over ESM3/node(SASA+volume)/
    # buriedness and add the frozen RNA-BAnG geometric-transformer output through a
    # zero-initialized gate.
    # excl. transformer_conv/gine_conv/protein_gat_residual.
    "rnabang_residual_with_esm3",
    # Drop every graph and attention layer and encode each residue independently with
    # an MLP adapter over frozen RNA-BAnG + residue type + SASA/volume/buriedness +
    # the edge-to-node summary picked by the rnabang_edge_* flags.
    # excl. double_attention, deepclip.
    "rnabang_frozen_node_adapter",
    # In the frozen-adapter path, encode residue type with a learned 20x8 embedding
    # instead of passing the raw integer residue index as one feature.
    # requires rnabang_frozen_node_adapter.
    "rnabang_residue_type_embedding",
    # Edge-to-node summaries for the frozen adapter, mutually exclusive; this default
    # keeps the two aggregate columns log1p(sum of incident contact areas) and
    # boundary/area exposure ratio.
    # requires rnabang_frozen_node_adapter.
    "rnabang_edge_current",
    # Keep the top-21 incident edges ranked by contact area as (area, boundary) pairs
    # plus normalized degree (43 features), zeroing the ranks past the true degree.
    "rnabang_edge_topk_by_area",
    # Encode the padded incident-edge set with a learned permutation-invariant DeepSets
    # encoder instead of using precomputed statistics.
    "rnabang_edge_deepsets",
    # Use PNA-style statistics of the incident edges: sum/mean/std/min/max of area and
    # boundary plus degree, exposed fraction and boundary/area ratio (13 features).
    "rnabang_edge_pna",
    # Use the 0/10/25/50/75/90/100 quantiles of incident-edge area and boundary plus
    # their log totals, degree and boundary/area ratio (18 features).
    "rnabang_edge_quantiles",
    # Encode the padded incident-edge set with a learned set transformer (one
    # self-attention block plus PMA-style pooling).
    "rnabang_edge_set_transformer",
    # Append three more Voronota per-residue columns to the protein node vector, which
    # otherwise carries only residue_type, residue_sas_area and residue_volume:
    # residue_mean_ev28, residue_mean_ev56 -- exposure/burial at two probe radii,
    # i.e. how enclosed the residue is at two length scales; a lipid cavity is
    # defined by exactly this and the GAT currently has to infer it from contacts
    # hydrophobicity -- Kyte-Doolittle index of residue_type
    # All three are already in data/graphs/<protein>/coarse_graph_nodes.csv, computed
    # offline; nothing new is generated. This is the fold-independent half of the
    # protein description, which is what a cold-family split needs: unlike the PLM
    # embedding these say what the site is like rather than which protein it belongs
    # to. The columns are appended, so node[:, 0..2] keep their meaning for every path
    # that indexes them positionally (see Protein_encoder's frozen node adapter).
    "protein_extra_node_features",
    "plm_sequential_compression",  # multi-layer compression stack for the PLM vector instead of one Linear projection; uses --plm_compression_dims for the intermediate widths
    # Ideas: trim protein structures to avoid artificial pockets or use pocket
    # geometry as SA/CA bias. Consider solvent-accessible surface, two probe
    # radii, tangent-sphere cavities (Nature), and Voronota pockets.
    "buryon",  # concatenates a per-residue buriedness scalar onto the protein node vector; default on

    # --- 5. Self-attention (protein and lipid) ---
    "protein_self_attention",  # self-attention over protein nodes after the GAT conv; default on, off only via --no_protein_self_attention
    "lipid_self_attention",  # self-attention over lipid nodes; default on, off only via --no_lipid_self_attention
    # Ablation: swap every configurable self-attention block in the project for a
    # per-token MLP of the same parameter budget (mlp_utils.AttentionMLPSubstitute/
    # NodeMLPSubstitute -- the same 4*dim^2 Q/K/V/O budget, via hidden_dim=2*dim,
    # ResidualAdversary in final_layer.py already uses for the same reason). Covers
    # ProteinSelfAttention (protein_self_attention), SelfAttention (lipid_self_attention),
    # NamedDescriptorHead's own attention (descriptor_heads), and RoPESelfAttention
    # (geometric_transformer) --
    # every SITE still has to be individually enabled by its own flag; this only
    # decides what runs there once it is. CrossAttention is not covered: it reads the
    # OTHER partner (query != key/value), so "self-attention" does not describe it and
    # an MLP has no well-defined substitute for a two-input block. Sets fast_attention's
    # grouped path aside too (architecture/fast_attention.can_use_grouped_attention) --
    # that path reaches into nn.MultiheadAttention's own projection weights directly,
    # which the substitute does not have.
    "mlp_in_place_of_sa",
    # Compute block-diagonal attention on dense (graphs, max_nodes, dim)
    # tensors, instead of a long padded sequence with an N x N -inf mask.
    # Uses ~9x fewer logits (architecture/fast_attention.py). Results agree
    # to float32 rounding (~6e-08), not bitwise; runs are not bit-comparable.
    "fast_attention",
    "attention_residual_gates",  # learnable scalar gates (init 0) on the attention- and FFN-output residual branches, so each starts as a pure skip connection
    "protein_disable_pre_sa_mlp",  # skips the MLP block before protein self-attention; requires gine_conv when protein_self_attention is on
    "protein_disable_post_sa_mlp",  # skips the MLP block after protein self-attention; default on
    "lipid_disable_post_sa_mlp",  # skips the MLP block after lipid self-attention; default on
    "protein_output_graph_norm",  # graph-norm on the protein encoder's final output
    "lipid_output_graph_norm",  # graph-norm on the lipid encoder's final output

    # --- 6. Cross-attention & fusion ---
    "cross_attention",  # bidirectional protein<->lipid attention feeding each side the other's pooled context; default on
    # Replace the additive residual in CrossAttention.finish with
    # ForcedInteraction(own_content, attention_output). No skip path remains
    # when attention becomes uniform or near-zero. Requires --cross_attention.
    "cross_attention_forced_interaction",
    "double_attention",  # two full cross-attention rounds with a second pair of encoders; implies cross_attention; excl. lipid_only/protein_only, rnabang_frozen_node_adapter
    # Fuse pooled partners with lip^T W prot (torch.nn.Bilinear), not concat.
    # The classifier then uses both partners multiplicatively, blocking a
    # single-partner lipid-identity shortcut. See Final_Layer.
    # excl. lipid_only/protein_only, descriptor heads.
    "bilinear_fusion",
    # LayerNorm on lip_outs/prot_outs after _pool_partners and before
    # self.bilinear in Final_Layer.forward. CrossAttention normalizes nodes,
    # but add-pooling sums variable atom/residue counts, so pooled magnitudes
    # still vary. This second normalization removes that variation.
    # Requires --bilinear_fusion (validate()).
    "bilinear_pooled_norm",
    # Add a node-pair product before pooling, alongside existing attention
    # updates and pooled representations. --bilinear_fusion acts only after
    # pooling. CrossAttention's Q.K scores are scalars; its feature update is
    # a weighted sum of partner values, with no Hadamard product of contents
    # (see architecture/cross_attention.py, "Current compact variant").
    # For each pair scored by lipid-query attention, compute
    # signed_sqrt(proj_a(lip_i) * proj_b(prot_j)) from ForcedInteraction
    # (architecture/forced_interaction.py). Keys are pocket-restricted when
    # that site uses --attention_by_pockets; otherwise all same-sample pairs
    # are used. Sum pair vectors per graph pair and concatenate the result
    # into Final_Layer.common_out. This also works with --bilinear_fusion.
    # Requires --cross_attention to supply node pairs (validate()).
    "node_bilinear_fusion",
    # Hard pocket restriction: non-pocket protein residues are removed as attention
    # *keys* in protein self-attention and in lipid-query cross-attention, so the
    # lipid only ever sees the binding site. They stay queries and are still updated.
    # This is the restriction counterpart of prot_attention_pos_bias, which only adds
    # a learnable preference and keeps every residue reachable; the two are mutually
    # exclusive because a constant bias on the surviving keys is a no-op under softmax
    # and would leave prot_attention_pos_bias's parameter without gradient.
    # Measured against the bound ligand in 18 raw structures, pocketness.pdb recovers
    # 77% of the residues within 5 A of the real ligand (median 80%, min 40% on BPI,
    # which has two lipid sites and one crystallised ligand), at precision 0.63.
    # So this drops roughly a fifth of the true contact residues along with ~82% of
    # the protein.
    "attention_by_pockets",
    "prot_pos_bias_per_head",  # makes the pocket positional bias a per-head vector instead of one shared value; requires --protein_pooling=attention_pos_bias or pooling_by_pockets
    # Cross-attention key bias, softplus-scaled so a bigger feature value always
    # contributes more in the same direction (never silently inverts sign):
    # bury (protein keys, restricted to pocket residues, extends prot_attention_pos_bias's
    # 0/1 mask to a continuous buriedness term) and chain_rank (lipid keys, position
    # along the acyl chain from head=0 to tail=1). Independent flags -- neither
    # requires the other. See architecture/cross_attention.py's make_key_bias.
    "cross_attention_bury_bias",
    "cross_attention_chain_bias",  # requires lipid_graph_isomers for chain_rank

    # --- 7. Final pooling ---
    # Learned attention pooling (one learnable query per partner) instead of the fixed
    # pool_type reduction: out = sum_i softmax_i(w·x_i) x_i over each graph's nodes -- a
    # content-weighted readout rather than a flat mean/max.
    # excl. swe_pooling.
    "attention_pooling",
    "attention_pooling_pocket_bias",  # adds a learnable bias toward pocket residues in attention pooling; requires attention_pooling
    # Sliced-Wasserstein pooling (architecture/final_layer.py:SlicedWassersteinPool):
    # reads the SHAPE of a graph's node distribution instead of its average, by matching
    # its quantiles to swe_reference_points learned reference points along learned
    # directions. Under mean pooling, the 35
    # proteins sit at ESM3 cosine 0.974 of each other under mean pooling while their
    # binding profiles are at 0.000, so the average does not separate them.
    # Freezing references leaves directions and output mapping trainable, as in
    # "SWE_Simple", suited to a protein axis of 21-33.
    # excl. attention_pooling.
    "swe_pooling",
    "swe_freeze_reference",  # keeps swe_pooling's reference points at random init instead of learning them; requires swe_pooling
    # Keep only pocket residues in node features, PLM rows, buriedness and
    # confidence; keep edges only when both endpoints remain. Unlike
    # attention_by_pockets, the GAT loses all outside-site structural context.
    # excl. attention_by_pockets, --protein_pooling=pooling_by_pockets.
    "protein_pockets_only",

    # --- 8. Dimensions & layer counts ---
    "third_layers_in_mlps",  # adds a 3rd hidden layer to every configurable MLP (width via --mlp_widths's _third suffix)

    # --- 9. Sparsity / gating / bilevel ---
    # Structured-sparsity gates: learn architecture size (m/FFN width, heads,
    # blocks, third layer, cross-attention) in one run by gating prunable groups
    # and penalizing active gates (L0 hard-concrete or L1 scale).
    "structured_sparsity",
    "sparsity_gate_ffn",  # per-unit gate over the enlarged FFN hidden units; requires structured_sparsity, otherwise a no-op
    "sparsity_gate_heads",  # per-head gate after GATv2/TransformerConv protein and lipid graph layers; requires structured_sparsity
    "sparsity_gate_blocks",  # declared but unwired in architecture/training -- currently has no effect
    "sparsity_gate_third_layer",  # gates the MLP's optional third layer so training can prune back to a plain 2-layer MLP; requires structured_sparsity and third_layers_in_mlps
    "sparsity_gate_cross_attention",  # single scalar gate around the cross-attention block, letting it prune to identity; requires structured_sparsity and cross_attention
    # Bilevel hyperparameter discovery: gate every internal MLP hidden layer (learn
    # widths) and/or learn per-block dropout, optimizing these lambda parameters on the
    # validation split (first-order alternating) while weights train on the train split.
    # Discovered widths/dropout are recorded to test_metrics for later plain runs.
    "gate_all_mlp_hidden",
    "gate_all_mlp_layers",  # superset of gate_all_mlp_hidden: also gates each block's input/output boundary, not just hidden units
    "no_ffns",  # removes the feed-forward sub-block entirely from both self-attention and cross-attention layers
    "bilevel",  # steps width-gate parameters on a held-out validation batch each step instead of the train-loss sparsity penalty; requires gate_all_mlp_hidden or gate_all_mlp_layers; suppresses --sparsity_lambda's train-loss term
    "bilevel_dropout",  # learnable per-site Concrete Dropout instead of fixed dropout rates; independent of bilevel (train-objective, not validation-objective)

    # --- 10. Adversarial / DANN / chem-adversary heads ---
    # Ganin-style gradient reversal against single-partner label shortcuts.
    # Each adversary predicts the label from one pooled PRE-cross-attention
    # partner, before partner mixing. Reversed gradients make that encoder
    # uninformative alone and push the decision toward the interaction.
    # Complements bilinear_fusion.
    "adversarial_grl",
    # Replace each adversary's 2-layer MLP with a residual FFN + LayerNorm
    # and binary head, matching cross-attention without multihead attention.
    # This closes the capacity gap that lets cross-attention decode leakage
    # a shallow probe misses.
    # requires adversarial_grl.
    "adv_deep",
    "adv_lambda_ramp",  # ramps adversary reversal strength by elapsed epoch instead of a constant --adv_lambda; requires adversarial_grl; superseded by adv_lambda_ramp_by_fit
    "adv_lambda_ramp_by_fit",  # same ramp, driven by the model's ratcheted fit progress instead of raw epoch count; requires adversarial_grl; takes precedence over adv_lambda_ramp
    # Family DANN: a GRL head predicts the 9 protein families from the FUSED
    # post-cross-attention vector. Unlike per-partner adversaries, it reaches
    # joint family-specific pocket/lipid memorization. Unconditional family
    # invariance is provably harmful here because family defines binding
    # specificity. dann_class_conditional aligns P(features | label, family)
    # per class, not P(features | family). See ramped_dann_lambda.
    "dann_family",
    "dann_lambda_ramp",  # ramps DANN reversal strength by elapsed epoch; requires dann_family; superseded by dann_lambda_ramp_by_fit
    "dann_lambda_ramp_by_fit",  # same ramp by fit progress, takes precedence over dann_lambda_ramp; requires dann_family
    # Regression GRL against s_chem on the FUSED post-cross-attention vector,
    # at the same hook as dann_family. It removes redundant chemistry marginal
    # signal while allowing protein-specific interactions with s_chem. A head
    # reading only the fused vector can reconstruct the lipid marginal more
    # easily than its per-protein modulation.
    # requires chem_prior and/or pocket_compat_prior.
    "chem_adversary",
    "chem_lambda_ramp_by_fit",  # ramps the chem-adversary reversal strength by fit progress (no plain-epoch variant exists); requires chem_adversary

    # --- 11. Chemical / pocket priors (non-adversarial) ---
    # Add learned_scalar * s_chem(lipid) to the ordinary classifier logit.
    # s_chem is frozen and computed once from train labels only
    # (dataloader/chemistry_prior.py). Adding it AFTER the classifier means
    # the task loss need not store it in the fused vector. chem_adversary can
    # then remove redundant chemistry without fighting label-relevant signal.
    # chem_adversary requires this ordering.
    "chem_prior",
    # Pocket-vs-chain-length prior.
    # It depends on both protein and lipid, unlike PROTEIN_DESCRIPTOR_NAMES,
    # so it cannot reduce to a protein-only family label. Frozen and added
    # outside the network like --chem_prior. When both are on,
    # fit_prior_calibration (dataloader/chemistry_prior.py) fits them jointly
    # to avoid double-counting shared variance or misattributing it.
    "pocket_compat_prior",
    # Per-row loss weight, valid under any architecture. Unlike chem_prior
    # and chem_adversary, it needs no fused vector or added module; those
    # options are rejected under --descriptors_head (validate()).
    # Uses common_weights_parts (dataloader/Dataloader.py) and training/new_train.py:
    # weight = |label - s_chem| / mean(|label - s_chem| for the same label).
    # s_chem is chem_prior's leave-one-row-out score (null_scores_leave_one_row_out,
    # dataloader/chemistry_prior.py). Each class keeps mean weight 1.0, preserving
    # --balanced_batches/--balanced_proteins class balance. Lipid-predictable
    # rows weigh less; contradictory rows weigh more, emphasizing protein signal.
    "lipid_propensity_weight",

    # --- 12. Loss function & class/sample weighting ---
    # Pair rows only with rows of the SAME protein when ranking. Without it the ranking
    # loss optimises the pooled-block AUC, which on this dataset is mostly the chemical
    # marginal a protein-blind null model already answers. This flag ranks a protein's
    # own lipids against each
    # other, which is the interaction term. Costs pair count: batches are drawn across
    # proteins, so most of the pair matrix is discarded.
    # requires --loss_type=pairwise_rank.
    "rank_within_protein",
    # Group DRO (Sagawa et al., 2019): replace the plain batch mean with a moving
    # worst-family weighted mean over the 9 protein families, so a
    # family the model currently fits worst dominates the gradient instead of being
    # averaged away by families already easy. Requires loss_type=cross_entropy (the
    # branch that already has an unreduced per-sample loss to regroup by family) and
    # is mutually exclusive with pu_loss, whose loss terms are population-
    # or pair-level rather than per-row. See architecture.loss.GroupDROState.
    "group_dro",
    "pu_loss",  # replaces the task loss with the non-negative PU risk estimator everywhere (train/valid/test); excl. group_dro; supersedes loss_type/focal_loss selection
    # One PU class prior per lipid subclass of the source paper instead of one for the
    # whole train set: the same pu_unlabeled_positive_fraction formula applied to each
    # subclass's own train counts (training/new_train.py), and the nnPU estimator then
    # run inside each subclass (architecture/loss.py's _grouped_pu_loss). The reason the
    # grain is the subclass: within one the head groups are the same, so "does this
    # protein take this subclass" is close to settled while "which species of it" is
    # not, and an unlabeled row in a subclass the protein does take is a likely hidden
    # positive, which a single train-wide prior cannot express -- per-subclass positive
    # rates run 0.25-0.68. Subclass membership is read from
    # data/lipid_article_classification.json, the same file --lipid_subclass uses.
    "pu_rho_by_subclass",
    "focal_loss",  # focal loss instead of plain cross-entropy; only applies inside the loss_type=cross_entropy branch, no effect under pu_loss or pairwise_rank
    "logit_adjustment",  # adds a fixed prior-derived bias to the logits before the task loss; composes with class_weights/focal_loss without double-correcting
    "protein_group_weight",  # adds per-protein-group sample weights to the loss; no effect under group_dro (weights computed but unused)
    # Restore each protein's pos:neg ratio inside train by weighting instead of by
    # discarding. What a two-axis split needs: holding lipid classes out cuts across
    # proteins and leaves some of them badly skewed (STARD2 at 4 positive against 91
    # unlabeled), and re-matching by subsampling would cut hardest from exactly those.
    # See PLIDataset.get_protein_balance_weights.
    "protein_balance_weight",
    # Rake the train rows' loss weights (iterative proportional fitting) so that the
    # weighted positive rate is the SAME inside every protein, every lipid class and
    # every individual lipid: the train-wide rate, so --class_weights keeps its meaning.
    # Each of the three one-dimensional priors ("this protein binds", "this class
    # binds", "this lipid binds") then carries no information, while the joint
    # (protein x class) is left intact -- measured on --lipid_species_coldsplit=0.15,
    # npp=5: marginal AUCs 0.634/0.615 -> 0.458/0.471, joint 0.930 -> 0.930
    # A loss weight, so it works under
    # every architecture. See PLIDataset.get_marginal_balance_weights.
    "marginal_balance_weight",
    "protein_class_weight",  # adds per-protein-class sample weights; no effect under group_dro
    "protein_class_sqrt_weight",  # same as protein_class_weight but sqrt-damped; no effect under group_dro
    # Train positives mean "this protein has a screened positive in this
    # lipid's head-group class", rather than for this exact lipid.
    # Uses dataloader.lipid_classes.class_level_positive_labels and the same
    # classes as --lipid_coldsplit/--double_coldsplit. Inputs and architecture
    # stay unchanged; valid/test still score exact-molecule Interaction labels.
    "lipid_class_targets",

    # --- 13. Cold-split / holdout axes ---
    # Both double_coldsplit and mixed_coldsplit hold out head-group classes alongside
    # excluded_groups. Derive the classes from the held-out
    # family by dataloader.splitting_on_blocks.lipid_coldsplit_blocks.lipid_classes_for_holdout, not typed in, because the
    # right set differs per family and the rule that finds it is what makes the split
    # honest. The derived list is printed at load time so a run's log records it.
    #
    # They differ in what happens to the held-out family's rows in the classes that
    # STAYED in train. mixed_coldsplit leaves them in the evaluation pool, so valid and
    # test mix three regimes and 6-39% of their lipids are ones training has seen; the
    # per-lipid label prior measures 0.498 there, diluted but present. double_coldsplit
    # drops those rows entirely -- they cannot go to train either, their protein is held
    # out -- so no evaluated lipid has been seen and the prior measures exactly 0.500.
    # That costs 3-17% of the working set and nothing from train, which never held them.
    # excl. family_only.
    "double_coldsplit",
    "mixed_coldsplit",  # same derived lipid-class holdout as double_coldsplit but without the intersection narrowing; requires excluded_groups; excl. family_only
    "cold_split",  # marks the cold-split submitter convention; requires --test_group to be set; excl. family_only
    # Drop from valid/test every row whose (LTPProtein, article lipid subclass) cell has
    # no training row , instead of scoring it.
    #
    # Such a row is not a hard case, it is an unanswerable one: the no-model planka this
    # project measures the network against -- the train positive rate of that cell,
    # analysis/baselines/protein_subclass_label_baseline.py -- has nothing to estimate from and
    # falls back to "negative", so it scores balanced accuracy 0.500 there by
    # construction. Measured on --lipid_species_coldsplit=0.15 over the five standard
    # seeds, those rows are 10.1% of test and 9.8% of valid but carry only 2.9%/2.5% of
    # the positives, so dropping them moves the planka 0.871 -> 0.879 and the block's
    # positive rate 0.335 -> 0.362, keeping 90% of the rows and 97% of the positives
    #
    # The point is comparability, not a higher number: with these rows in, part of what
    # separates a model from the planka is which side of an uninformative fallback each
    # happens to land on. The key is the JOINT (protein, subclass) cell, matching that
    # baseline exactly, so the two are measured on the same rows.
    "drop_uncovered_protein_subclass",

    # --- 14. Negative sampling ---
    # Match negatives to positives per (family, lipid class), removing the
    # class prior left by coarser samplers: positive rates 0.25-0.68 become
    # 0.50-0.51. Per-protein balance cannot also be kept on this data; see
    # Dataloader.sample_lipid_class_balanced_negatives. Overrides balanced_proteins.
    "balanced_lipid_classes",
    "balance_negatives_by_family",  # draws negatives per protein family to match that family's positive count; overridden by balanced_proteins/balanced_lipid_classes
    "balanced_proteins",  # draws negatives per protein to match its own positive count; overridden by balanced_lipid_classes, overrides balance_negatives_by_family
    "balanced_batches",  # balances the class composition within each drawn batch; composes with rotate_train_negatives
    # --rotate_train_negatives: show the model EVERY negative over the course of a run
    # instead of the one draw negatives_per_positive fixed at dataset build time. The
    # draw above decides what a single epoch holds; without this flag it also decides
    # what the whole RUN ever sees, which at this table's 634:9271 ratio is 14% of the
    # negative evidence, chosen by the seed. With it, train keeps every eligible
    # negative and each epoch is handed a different consecutive slice of a fixed
    # permutation (dataloader/sampler.py's RotatingNegativeBatchSampler), so the epoch
    # costs exactly what it cost before and the run covers the pool about sixteen times
    # over at 120 epochs. Only TRAIN changes: the evaluated block is sampled exactly as
    # before, so a rotating run's metrics stay comparable with a fixed one's.
    # excl. eval_average_candidates.
    "rotate_train_negatives",
    "balance_excluded_group_negatives",  # rewrites negatives in the held-out (validation/test) groups to class-stratified 50/50; requires excluded_groups; no-op under cold lipid-chemistry splits
    # Bias the negatives drawn for a protein's TRAIN-side rows toward its own chemistry
    # hard cases -- unlabeled lipids Tanimoto-similar to a lipid that protein IS
    # positive for -- instead of drawing them uniformly, so the loss must separate
    # binder from non-binder chemistry rather than lean on the base rate. Applies only
    # to groups whose family is not in --excluded_groups: a held-out family's rows
    # become validation/test after the split, and this flag must not change what those
    # measure, only what training sees. See dataloader/sampler.py's
    # _sample_group_balanced_negatives and _hard_negative_weights. Which balanced
    # sampler it steers follows the balancing flag in force: the per-protein and
    # per-family ones draw per group, --balanced_lipid_classes per (family, class) cell,
    # where the steering is therefore between congeners of one head group.
    # excl. dissimilar_negative_mining.
    "hard_negative_mining",
    # The opposite direction on the same axis: bias the negatives drawn for a protein's
    # TRAIN-side rows AWAY from its own chemistry -- unlabeled lipids Tanimoto-DISTANT
    # from every lipid that protein is positive for -- instead of drawing them
    # uniformly. Mutually exclusive with --hard_negative_mining, which steers the same
    # draw the other way; everything else about it is that flag's, including the
    # exemption of --excluded_groups families, so the evaluated block is drawn exactly
    # as a run without either flag would draw it. See dataloader/sampler.py's
    # _dissimilar_negative_weights.
    #
    # What it is for: this panel's lipids are largely congeneric, so a uniform draw
    # hands a protein near-duplicates of its own positives as negatives and leaves the
    # base rate as the only thing that separates them. Steering away spreads each
    # protein's negatives over the panel's chemistry instead. The class ratio is
    # untouched -- --negatives_per_positive still fixes it per group, so the pool stays
    # balanced 0/1 exactly as it was; only WHICH negatives fill the quota changes.
    "dissimilar_negative_mining",

    # --- 15. Lipid candidates / fragments ---
    # The ";"-separated SMILES of a row are candidate structures for one measured lipid
    # species (sn-positional / double-bond isomers the spectrum cannot separate), and
    # the embedding path used to keep only the first of them regardless of
    # lipid_fragments_treatment -- which made all three treatments the same run. This
    # flag is that behaviour. It is now OFF by default, so the chosen treatment sees
    # the whole candidate set; runs before this change had it on and encoded the first
    # candidate alone, whichever treatment they named. Turning it back on
    # (--lipid_first_fragment_only) is requires concat or fragments_mask,
    # which then degenerate to that single candidate; with random_choice the draw would
    # have nothing to draw from, so validate() rejects the pair. It governs the
    # embedding path only; the lipid_graph_isomers path has always used every candidate.
    "lipid_first_fragment_only",
    # Marginalize evaluation over the candidate set instead of scoring one member of it.
    # Training under random_choice teaches invariance to the degrees of freedom the mass
    # spectrum left open, and this is that invariance on the reading side: a validation
    # or test row is scored once per candidate and the probabilities are averaged before
    # the threshold, so the metric is one quantity across epochs and is the answer for
    # the species rather than for an arbitrary member of it.
    # requires --lipid_fragments_treatment=random_choice; excl. rotate_train_negatives.
    "eval_average_candidates",

    # --- 16. Training mechanics ---
    "disable_early_stopping",  # default on: never breaks the training loop early, so runs are always scored on the whole curve
    "type_opt",  # enables AMP mixed precision, but only on CUDA; stays off on CPU so CPU runs remain valid
    "lr_warmup_cosine",  # linear warm-up over --lr_warmup_epochs then cosine decay to lr*lr_min_factor, instead of a flat learning rate
    # Give the lipid branch a lower LR so the protein branch gets a head start;
    # forward behavior stays unchanged. Matched test BA is 0.621 for lipid_only
    # and 0.603 for the full model. The lipid path may solve the task first,
    # leaving little useful protein gradient. Slowing it preserves transferable
    # lipid signal, unlike adversarial suppression.
    # Use a separate optimizer group: Adam's m/sqrt(v) nearly cancels constant
    # gradient scaling, except for a relative L2 boost (coupled L2 is added
    # after scaling). Activation hooks after cross-attention would also affect
    # the protein through partner mixing. InteractionClassification.
    # lipid_branch_parameters selects only lipid parameters.
    # When off, no split optimizer group or per-epoch schedule is used;
    # the next two values apply only when on.
    # excl. lipid_only/protein_only, deepclip, descriptor heads.
    "lipid_path_handicap",

    # --- 17. Checkpointing / IO ---
    "testmode",  # redirects every output artifact (run/, models/, checkpoints/, metrics) under testmode_outputs/ so a smoke run can't pollute real results
    "save_checkpoint",  # writes the selected-epoch weights to checkpoints/<family>/<label>/...; independent of save_model (separate directory tree)
    # Save by default: run_test() uses best_model_state selected by rolling
    # validation and loaded before testing. Other saved weights are only five
    # save_model_in_dynamics milestones, missing the selected epoch ~80% of
    # the time. Without selected weights, later per-row/subclass analysis or
    # new metrics need a nearby milestone approximation. Unsaved sweeps have
    # already been lost to reanalysis; weights cost a few hundred KB per run.
    "save_model",
    # Track whether and when the protein branch is used: per-epoch branch
    # gradient norms, classifier input-weight norms, pooled protein spread,
    # and two extra validation passes with each pooled partner ablated.
    # Scalars cost KB per run; saving every epoch's weights would cost hundreds
    # of MB. save_model_in_dynamics independently saves milestone weights
    # (DYNAMICS_CHECKPOINT_EPOCHS, training/branch_dynamics.py).
    # Checkpoint-only runs avoid extra validation
    # and gradient bookkeeping. This matters for --descriptors_head probes,
    # whose branch ablations do nothing because Final_Layer returns first
    "save_dynamics",
    "save_model_in_dynamics",  # enable milestone weights described above

    # --- 18. DeepCLIP-specific ---
    # Learn channel weights in DeepCLIP's Sum_last_ax profile:
    # sum_h w_h * states[:, :, h], instead of fixed unit weights.
    # The original has no parameters and no downstream channel selection.
    # Initialize w to 1.0 to start with published DeepCLIP and change only
    # through gradients. Adds deepclip_lstm parameters (default 10).
    # excl. deepclip_protein_gate/_tokens.
    "deepclip_profile_weights",
)

SIMPLE_BOOL_FLAGS = {f"--{name}": name for name in BOOL_FLAG_NAMES}


FLAG_HANDLERS = {
    **{
        argument: set_config_flag(field)
        for argument, field in SIMPLE_BOOL_FLAGS.items()
    },
    "no_tanimoto_weight": set_config_flag("tanimoto_weight", False),
    "--no_tanimoto_weight": set_config_flag("tanimoto_weight", False),
    "tanimoto_weight": set_config_flag("tanimoto_weight", True),
    "--tanimoto_weight": set_config_flag("tanimoto_weight", True),
    "no_class_weights": set_config_flag("class_weights", False),
    "--no_class_weights": set_config_flag("class_weights", False),
    "no_protein_self_attention": set_config_flag("protein_self_attention", False),
    "--no_protein_self_attention": set_config_flag("protein_self_attention", False),
    "no_lipid_self_attention": set_config_flag("lipid_self_attention", False),
    "--no_lipid_self_attention": set_config_flag("lipid_self_attention", False),
    "no_cross_attention": set_config_flag("cross_attention", False),
    "--no_cross_attention": set_config_flag("cross_attention", False),
    "no_lipid_first_fragment_only": set_config_flag(
        "lipid_first_fragment_only", False
    ),
    "--no_lipid_first_fragment_only": set_config_flag(
        "lipid_first_fragment_only", False
    ),
    "no_adv_lipid": set_config_flag("adv_lipid", False),
    "--no_adv_lipid": set_config_flag("adv_lipid", False),
    "no_adv_protein": set_config_flag("adv_protein", False),
    "--no_adv_protein": set_config_flag("adv_protein", False),
}


VALUE_HANDLERS = {
    # --- 1. Global model type ---
    # Descriptors from Lipovsky et al. (Nature 2025, s41586-025-10040-y),
    # the source of this project's LTP-lipid measurements (dataloader/descriptors.py).
    # --descriptor_heads names DESCRIPTOR_CATALOG tokens from shared
    # descriptor_catalog_input, bare or <name>_coarse=<spec>
    # (parse_descriptor_token). Commas group tokens into a head; "/" separates
    # heads: "a,b/c,d" gives two. pool_type reduces their vectors to one
    # (named_descriptor_head.pool_descriptor_head_outputs). "/" avoids the
    # shell quoting needed for "|" or ";" in arg files.
    # By default, concatenate the head vector beside normal towers. This is
    # incompatible with --bilinear_fusion: post-product concat restores a
    # single-partner shortcut. The flags below instead build only a descriptor
    # path and small classifier, with incompatible state_dicts and no full-model
    # modules; validate() rejects options that need those modules:
    # --descriptors_head: token self-attention per segment (NamedDescriptorHead).
    # --descriptor_mlp: exactly one segment through DescriptorMLPHead.
    # NamedDescriptorHead shares Linear(1, dim) token_embed, so its value
    # response cannot depend on descriptor identity. On an 11-descriptor
    # species15 block it gave test BA 0.535 versus 0.853 for a 2-hidden-layer
    # MLP using the same columns.
    # MLPs use hiddim/m/third_layers_in_mlps/dropout/act_fn as usual.
    # Raw pocket scalars (pocket_extent, pocket_elongation, buriedness_q50,
    # hydropathy_core, ...) are also accepted. The safe "extent" token uses
    # train-fit quantile coarsening: raw pocket_extent identifies held-out
    # proteins at eta^2=0.78. Other raw
    # protein scalars are unaudited, so they are opt-in probes, not safe defaults
    # All catalog tokens are scalars
    # embedded by Linear(1, hiddim); pooled PLM vectors are unsupported and
    # would need a separate embedding path.
    "--descriptor_heads=": set_config_field("descriptor_heads"),

    # --- 2. Protein graph encoder (conv architecture + edge features) ---
    "--protein_edge_mlp_lambda=": set_config_field(
        "protein_edge_mlp_lambda", float
    ),  # divisor EdgeMLPConv divides its summed protein messages by; also the inherited default for the lipid graph's EdgeMLPConv unless lipid_edge_mlp_lambda overrides it
    # Width of the distance RBF expansion inside the 25-dim structured edge
    # vector (architecture/protein_edge_geometry.py); default 16 reproduces the
    # original width unchanged. Requires protein_edge_attention/mlp.
    # excl. protein_edge_raw3.
    "--protein_edge_rbf_count=": set_config_field(
        "protein_edge_rbf_count", int
    ),
    "--geometric_ipa_chunk_size=": set_config_field(
        "geometric_ipa_chunk_size", int
    ),  # chunk size for the IPA attention computation inside geometric_transformer, trading memory for speed

    # --- 3. Lipid graph encoder / input representation ---
    "--lipid_edge_mlp_lambda=": set_config_field("lipid_edge_mlp_lambda", float),  # per-lipid-graph override of the EdgeMLPConv message divisor; requires lipid_graph_isomers and an active lipid edge-MLP conv
    "--lipid_descriptors=": set_config_field("lipid_descriptors"),  # named lipid descriptors concatenated into the lipid-side input; no hard prerequisite

    # --- 4. Protein input / frozen embeddings ---
    "--plm_compression_dim=": set_config_field("plm_compression_dim", int),  # output width of the single-Linear PLM compression path when plm_sequential_compression is off
    "--plm_compression_dims=": set_config_field(
        "plm_compression_dims", read_plm_compression_dims
    ),  # intermediate widths for the multi-layer PLM compression stack used when plm_sequential_compression is on
    # Width of one RNA-BAnG residue row, i.e. the input dimension every path above
    # expects from the precomputed embeddings.
    "--rnabang_embedding_dim=": set_config_field("rnabang_embedding_dim", int),
    "--proteinmpnn_embedding_dim=": set_config_field("proteinmpnn_embedding_dim", int),  # width of the frozen ProteinMPNN embedding; requires proteinmpnn_replace_esm3
    "--esmif1_embedding_dim=": set_config_field("esmif1_embedding_dim", int),  # width of the frozen ESM-IF1 embedding; requires esmif1_replace_esm3
    # Randomly keep this many residues per training sample, redrawn each
    # epoch; 0 disables it. Changing the set preserves site statistics while
    # preventing memorization of a fixed residue fingerprint.
    # Dropout instead zeros hidden dimensions per residue: noise averages
    # out over ~200 residues, leaving the pooled fingerprint nearly unchanged.
    # Use a fixed count to hide size too (pocket/protein size rho=0.72).
    # Pockets have 22-64 residues, median 33; 20 needs no replacement.
    # Proteins with fewer residues keep all of them and retain a size signal.
    "--protein_residue_subsample=": set_config_field("protein_residue_subsample", int),
    # --protein_descriptors / --lipid_descriptors: an arbitrary, comma-separated subset of
    # the FULL DESCRIPTOR_CATALOG (dataloader/descriptors.py -- lipid, protein/pocket,
    # AND pair-level names, bare or <name>_coarse=<spec>), broadcast onto every node of the
    # protein branch / lipid branch respectively -- the same name resolution
    # --descriptor_heads uses (dataloader.descriptors.full_catalog_order/
    # parse_descriptor_list), just read as a raw broadcast instead of pooled through a
    # head. No derived width field: architecture/protein_encoder.py and
    # architecture/lipid_encoder.py each compute their own broadcast width inline from this
    # string via parse_descriptor_list, so there is nothing here that could drift from it.
    "--protein_descriptors=": set_config_field("protein_descriptors"),

    # --- 6. Cross-attention & fusion ---
    # Which of the two sites the restriction applies to, see POCKET_ATTENTION_SITES.
    # requires attention_by_pockets.
    "--pocket_attention_sites=": set_config_field(
        "pocket_attention_sites", read_pocket_attention_sites
    ),
    # Separate weight decay for self.bilinear's optimizer group.
    # Its tensor is pooled_lip_dim x pooled_prot_dim x middim: with default
    # add-pooling, all three scale with hiddim, so its size grows cubically.
    # Other tensors grow roughly linearly or quadratically. The bilinear
    # product also lacks concatenation's built-in output ceiling, so global
    # weight decay may not restrain this large tensor enough.
    # None uses --weight_decay. Requires --bilinear_fusion (validate()).
    "--bilinear_weight_decay=": set_config_field("bilinear_weight_decay", float),

    # --- 7. Final pooling ---
    "--pool_type=": set_config_field("pool_type"),  # fixed graph-pooling reduction (add/max/mean/add_max/gem); superseded entirely when attention_pooling or swe_pooling is on
    "--swe_reference_points=": set_config_field("swe_reference_points", int),  # number of learned reference points swe_pooling matches each graph's node-feature quantiles to; must be >=2; requires swe_pooling
    "--protein_pooling=": set_config_field("protein_pooling"),  # protein pooling mode: "ordinary" / "attention_pos_bias" (pocket bias in attention) / "pooling_by_pockets" (pocket-only pooling)

    # --- 8. Dimensions & layer counts ---
    "--hiddim=": set_config_field("hiddim", int),  # global hidden width for both branches, cross-attention, fusion and classifier; must be >0 and divisible by HEADS
    # Separate branch widths; None uses hiddim and preserves existing models.
    # The branches carry different information: 35 protein identities fit in
    # about one dimension, while lipid
    # chemistry passes through Linear(768, hiddim) on MolFormer embeddings
    # (architecture/lipid_encoder.py). Under --lipid_coldsplit, this projection
    # is the only entry for unseen head groups; known proteins can be memorized.
    # Raising both widths from 8 to 64 changed test BA 0.5530 -> 0.5511 and
    # train sensitivity 0.837 -> 0.897, adding memorization without test gains
    # Each width covers its branch's projections, convs, self-attention, MLPs
    # and norms. Cross-attention, fusion and classifier keep hiddim. A differing
    # width adds Linear(branch_width, hiddim) at the boundary
    # (architecture/interaction_classification.py); equal widths add nothing.
    # Full cross-attention asymmetry would need MultiheadAttention(kdim=, vdim=),
    # which the fast path rejects: kdim == vdim == embed_dim is required
    # (architecture/fast_attention.py, _check_supported).
    "--protein_hiddim=": set_config_field("protein_hiddim", int),
    "--lipid_hiddim=": set_config_field("lipid_hiddim", int),  # width override for the lipid tower; same constraints as protein_hiddim
    "--HEADS=": set_config_field("HEADS", int),  # attention head count for every self-/cross-attention module; hiddim (and protein/lipid_hiddim if set) must be divisible by it
    "--m=": set_config_field("m", int),  # hidden-width multiplier (m * hiddim) for protein/lipid-branch MLP blocks
    "--final_m=": set_config_field("final_m", int),  # same multiplier for Final_Layer's classifier MLP; own default (4), None means "follow m"
    "--mlp_widths=": set_config_field("mlp_widths", read_mlp_widths),  # per-block hidden-width overrides ("site=width,...") over the named MLP sites, each defaulting to m*hiddim
    "--dropout=": set_config_field("dropout", float),  # dropout inside the configurable MLP blocks; must be in [0,1); final_dropout inherits it if left unset
    "--final_dropout=": set_config_field("final_dropout", float),  # dropout for Final_Layer's classifier MLP specifically; must be in [0,1)
    "--act_fn=": set_config_field("act_fn"),  # activation used throughout the network's MLPs (leakyrelu default/gelu/prelu/relu)

    # --- 9. Sparsity / gating / bilevel ---
    "--sparsity_mode=": set_config_field("sparsity_mode", str),  # gate family ("l0"/"l1") used by every sparsity gate; requires structured_sparsity or gate_all_mlp_hidden/layers
    "--sparsity_lambda=": set_config_field("sparsity_lambda", float),  # weight on the summed gate penalty added to the training loss; requires some gate-producing flag is on; suppressed under bilevel
    "--bilevel_lr=": set_config_field("bilevel_lr", float),  # learning rate for the hyper-optimizer that steps gate parameters under bilevel; meaningless without it
    # Per-layer learnable dropout is realized as Concrete Dropout (Gal et al. 2017)
    # trained on the TRAIN objective (first-order bilevel would degenerate p->0, like
    # weight_decay). Each dropout site has its own p and the full KL surrogate
    # concrete_dropout_weight_reg * ||W||^2/(1-p) - concrete_dropout_reg * K * H(p)
    # over the Linear it feeds. Canonically weight_reg = l^2/(tau*N), dropout_reg = 2/(tau*N).
    # requires bilevel_dropout.
    "--concrete_dropout_reg=": set_config_field("concrete_dropout_reg", float),
    "--concrete_dropout_weight_reg=": set_config_field("concrete_dropout_weight_reg", float),  # weight-decay-like term coefficient of the same surrogate; requires bilevel_dropout
    "--target_sparsity=": set_config_field("target_sparsity", float),  # range-validated under structured_sparsity but not read anywhere else -- currently inert

    # --- 10. Adversarial / DANN / chem-adversary heads ---
    "--adv_weight=": set_config_field("adv_weight", float),  # multiplier on the per-partner adversary loss added to the backward pass; requires adversarial_grl
    "--adv_lambda=": set_config_field("adv_lambda", float),  # constant GRL reversal strength for adversarial_grl; overwritten per-epoch under adv_lambda_ramp/_by_fit; never read directly in forward
    "--dann_weight=": set_config_field("dann_weight", float),  # multiplier on the family-DANN loss; requires dann_family
    "--dann_lambda=": set_config_field("dann_lambda", float),  # constant DANN reversal strength; overridden per-epoch under dann_lambda_ramp/_by_fit
    "--dann_class_conditional=": set_config_field("dann_class_conditional", read_bool),  # builds 2 family-adversary heads (one per label) instead of 1, so DANN aligns features within each class; default on, requires dann_family
    "--chem_weight=": set_config_field("chem_weight", float),  # multiplier on the chem-adversary loss; requires chem_adversary
    "--chem_lambda=": set_config_field("chem_lambda", float),  # constant chem-adversary reversal strength; overridden by chem_lambda_ramp_by_fit

    # --- 11. Chemical / pocket priors (non-adversarial) ---
    "--chem_neighbours=": set_config_field("chem_neighbours", int),  # number of nearest-neighbour lipids used when fitting the chemistry prior; used by chem_prior and/or pocket_compat_prior

    # --- 12. Loss function & class/sample weighting ---
    "--loss_type=": set_config_field("loss_type"),  # task loss selection (cross_entropy/mse/bce/pairwise_rank); pu_loss takes precedence over this when both are set
    "--pu_rho=": set_config_field("pu_rho", float),  # initial PU positive-class prior, overwritten by the value derived from measured train class counts; requires pu_loss
    "--pu_unlabeled_positive_fraction=": set_config_field(
        "pu_unlabeled_positive_fraction", float
    ),  # feeds the derivation of pu_rho from train class counts; requires pu_loss
    "--pu_rho_by_subclass=": set_config_field("pu_rho_by_subclass", read_bool),  # value form of pu_rho_by_subclass; see that bool flag
    "--pu_beta=": set_config_field("pu_beta", float),  # non-negative-risk clamp threshold in the nnPU estimator; requires pu_loss
    "--pu_gamma=": set_config_field("pu_gamma", float),  # scale of the straight-through gradient surrogate once the nnPU correction triggers; requires pu_loss
    "--pu_tau=": set_config_field("pu_tau", float),  # shape/temperature parameter passed into the PU loss; requires pu_loss
    "--pu_loss_cap=": set_config_field("pu_loss_cap", float),  # cap parameter passed into the PU loss at every call site; requires pu_loss
    "--group_dro_step_size=": set_config_field("group_dro_step_size", float),  # step size of the exponential multiplicative-weights update on per-family DRO probabilities; requires group_dro
    # Add group_dro_adj / sqrt(train_count) before the family weight update,
    # without backpropagating it. This is the paper's generalization adjustment:
    # it reduces trust in noisy small-family losses. 0.0 gives plain group DRO.
    "--group_dro_adj=": set_config_field("group_dro_adj", float),
    "--focal_gamma=": set_config_field("focal_gamma", float),  # focusing exponent of the focal-loss term; requires focal_loss
    "--logit_adjustment_tau=": set_config_field("logit_adjustment_tau", float),  # temperature scaling the prior-derived logit bias; requires logit_adjustment
    "--tanimoto_weight=": set_config_field("tanimoto_weight", read_bool),  # value form of the tanimoto_weight sample-weighting flag; also gates opening the Tanimoto cache files at load time

    # --- 13. Cold-split / holdout axes ---
    "--excluded_groups=": set_config_field("excluded_groups", read_excluded_groups),  # protein-family groups pulled into the eval split; required by double_coldsplit/mixed_coldsplit/test_group; excl. lipid_coldsplit/isolation/subclass/species_coldsplit, family_only
    "--excluded_subgroups=": set_config_field(
        "excluded_subgroups", read_excluded_subgroups
    ),  # head-group classes held out alongside excluded_groups; stacks with it, appends to the excluded-set directory name
    # How much of the held-out family's positives the derived class set has to cover.
    #
    # 0.8 rather than 0.7: the value decides how many of a family's own classes leave
    # with it, and the classes it stops short of are its lipids' closest relatives, so
    # what it really sets is how far the held-out chemistry ends up from the chemistry
    # left behind. Measured as the mean best Tanimoto similarity from the block to
    # training (analysis/coldsplit_geometry.py --sweep), 0.7 leaves START at 0.828 and
    # CRAL-TRIO at 0.902, while 0.8 brings them to 0.654 and 0.784 and the seven-family
    # mean from 0.810 to 0.768. Past 0.8 the trade turns: 0.85 buys 0.02 more for fifty
    # training positives, and 0.9 drops CRAL-TRIO to 142 of them.
    #
    # Both lookup baselines stay at 0.500 for every family at any value from 0.4 up
    # (preprocessing/lipid_marginal_baseline.py), so this choice is about the distance,
    # not about the guarantee; 0.3 is the one value in the sweep that breaks it.
    "--coldsplit_share=": set_config_field("coldsplit_share", float),
    # The other axis on its own: a whole chemical family of lipids leaves training while
    # every protein stays. Answers "a lipid of a chemistry never seen arrives -- which of
    # the known proteins bind it", which is the question that matters when the screening
    # panel grows rather than the protein list. Takes the name of one set; the launcher
    # expands a bare --lipid_coldsplit into one run per set.
    # excl. lipid_isolation/subclass/species_coldsplit, excluded_groups, family_only.
    "--lipid_coldsplit=": set_config_field("lipid_coldsplit", read_lipid_coldsplit),
    # The same axis, addressed by how far the block sits from training instead of by
    # which chemistry it is. Takes the key of a block in
    # dataloader/splitting_on_blocks/lipid_isolation_blocks.py, each one a set of lipid SPECIES chosen by
    # analysis/lipid_block_search.py so that its isolation -- the mean over the block's
    # structures of the best Tanimoto similarity to a structure left in training --
    # lands on that value. Exists because the named class sets only reach 0.46-0.88 and
    # the rest of the axis cannot be measured with them; everything else about the split
    # (every protein stays, the block is halved label-by-label into validation and test)
    # is what --lipid_coldsplit already does.
    "--lipid_isolation=": set_config_field("lipid_isolation", read_lipid_isolation),
    # The same axis cut by the SOURCE PAPER'S own subclass: one (or several, joined by
    # "+") of the lipid subclasses on the y axis of Titeca et al.'s LTP x lipid-subclass
    # matrix leaves training for every protein. Neither of the two above is this
    # partition -- LIPID_COLDSPLIT_SETS merges PC with LPC and lumps six anionic classes
    # together, and an isolation block is whatever sits at a requested distance -- and
    # this one is the task as the collaborators state it ("classify binders and
    # non-binders by lipid subclass"), which is why it gets its own flag rather than a
    # re-spelling of either. Same species-level machinery as lipid_isolation from here
    # on; see dataloader/splitting_on_blocks/lipid_subclass_blocks.py.
    "--lipid_subclass=": set_config_field("lipid_subclass", read_lipid_subclass),
    # The same axis again, cut at the CONCRETE LIPID instead of at a named chemical set:
    # a seeded draw of individual lipids leaves training for every protein, sized so the
    # block carries this share of the table's positives. 0.0 means the flag is off.
    #
    # What it holds out is not a set of FullIdentityOfLipid names. A name is a measured
    # sum composition carrying a bag of candidate structures, and those bags overlap --
    # 149 of 1226 structures are offered by more than one name -- so a name-level draw
    # leaves 12-22% of the drawn structures in training under another name. The unit is
    # therefore the connected component of the name-structure graph, which is the finest
    # structure-disjoint cut that exists; see dataloader/splitting_on_blocks/lipid_species_blocks.py.
    "--lipid_species_coldsplit=": set_config_field(
        "lipid_species_coldsplit", float
    ),
    # Filter the table to one protein family before splitting, following
    # DeepCLIP/BERT-RBP's training on each protein's own data. The normal
    # 85/15 random split then runs within that family
    # (Dataloader._split_interactions, no-excluded_groups branch).
    # Using --excluded_groups for the other 8 families would instead leave
    # this family with no valid/test rows.
    # excl. excluded_groups, double/mixed_coldsplit, lipid_coldsplit, cold_split.
    "--family_only=": set_config_field("family_only"),
    "--test_group=": set_config_field("test_group", read_test_group),  # names which excluded_groups member is the held-out TEST group rather than validation; requires excluded_groups; required by cold_split

    # --- 14. Negative sampling ---
    # Negatives drawn per positive inside each balancing group. 1 is the exact 1:1 the
    # samplers produced before this existed, and it costs the 9506 rows of the table
    # that the match discards. Raising it keeps the grouping -- so the between-protein
    # prior the grouping removes stays removed -- and only coarsens the class ratio: 2
    # gives about 32-38% positives in train, 3 about 24-30%, against the table's own
    # 6.9%. The class ratio the loss then sees is --class_weights' business, and the
    # per-protein skew a two-axis split leaves behind is --protein_balance_weight's.
    #
    # DEFAULT 2, not 1: the exact match throws away 86% of the table for a precision the
    # loss can supply instead, and the rows it throws away are the record of which
    # lipids each protein does not bind. Runs that want the old pool pass
    # --negatives_per_positive=1 explicitly; results from before this default are 1:1
    # and are not directly comparable.
    "--negatives_per_positive=": set_config_field("negatives_per_positive", int),
    # How many negatives one epoch holds under the flag above. 0 means
    # negatives_per_positive x (train positives), i.e. the same per-epoch class ratio
    # the run would have had without rotation -- raise it to trade epoch cost for a
    # shorter pass over the pool.
    # requires rotate_train_negatives.
    "--rotate_negatives_per_epoch=": set_config_field("rotate_negatives_per_epoch", int),
    # WHICH similarity the two mining flags above steer by. They used to have only one
    # answer -- Morgan-fingerprint Tanimoto between lipid species -- but neither the
    # reduction ("max similarity to anything this group already binds") nor the blend
    # with uniform ever depended on that, so the pool is now a choice. One of:
    #
    # tanimoto lipid species, Morgan fingerprints (the default: this is
    # what every run before this flag drew, so their numbers are
    # reproduced exactly)
    # molformer lipid species, MolFormer's mean-pooled embedding
    # (preprocessing/build_molformer_similarity_matrix.py)
    # lipid_descriptors lipid species, the hand-built lipid descriptor set
    # protein_descriptors PROTEIN, the pocket descriptor set
    # protein_identity PROTEIN, sequence identity after global alignment
    # protein_blosum62 PROTEIN, the same alignment's conservative substitutions
    # protein_tmscore PROTEIN, TM-align structural TM-score
    #
    # The last three read data/protein_similarity/ (preprocessing/build_protein_sequence_
    # similarity.py, preprocessing/build_protein_tmscore.py); see
    # dataloader/similarity_pool.py for the axis each source puts a row on.
    #
    # A protein-axis source asks "is this candidate's protein like the proteins this
    # group already has positives for", which is a question only a group spanning
    # several proteins can answer -- so it is refused under --balanced_proteins, whose
    # group IS one protein and where every candidate would score exactly 1.0. The
    # per-family and per-(family, class) samplers are the ones it works with.
    # requires hard_negative_mining or dissimilar_negative_mining.
    "--negative_similarity=": set_config_field("negative_similarity"),
    # Comma-separated descriptor names overriding the default set of a *_descriptors
    # source, same convention as --lipid_descriptors/--protein_descriptors (which this
    # deliberately does NOT reuse: those configure the model's descriptor inputs, and a
    # run should not change its negative draw by adding a descriptor head). Naming both
    # sides at once moves the axis to the PAIR -- one entity per interaction-table row --
    # since neither the lipid nor the protein alone determines that vector.
    "--negative_similarity_descriptors=": set_config_field("negative_similarity_descriptors"),
    # Sampling-weight mass steered toward the hardest candidates; the rest (1 - share)
    # stays uniform, so a protein whose positives have no chemically close negatives in
    # its own pool still draws its full quota instead of concentrating on whatever is
    # least-far-from-zero similarity.
    # requires hard_negative_mining.
    "--hard_negative_share=": set_config_field("hard_negative_share", float),
    # Sampling-weight mass steered toward the most distant candidates; the rest
    # (1 - share) stays uniform, so a protein whose positives are close to everything in
    # its own pool still draws its full quota instead of concentrating on the handful
    # that happen to be least-close.
    # requires dissimilar_negative_mining.
    "--dissimilar_negative_share=": set_config_field(
        "dissimilar_negative_share", float
    ),

    # --- 15. Lipid candidates / fragments ---
    "--lipid_fragments_treatment=": set_config_field("lipid_fragments_treatment"),  # how a lipid's candidate-fragment set is treated: concat (0) / random_choice (1, default) / fragments_mask (2); deepclip only accepts random_choice
    "--lipid_first_fragment_only=": set_config_field(
        "lipid_first_fragment_only", read_bool
    ),  # value form of lipid_first_fragment_only; see that bool flag
    # How many candidates of a pair the averaged evaluation actually scores. A species
    # can list up to 37 of them and scoring every one makes the evaluation blocks larger
    # than the training epoch (2912 rows against 345 pairs on START), while the
    # candidates of one species sit at cosine 0.98 of each other in the embedding, so
    # four evenly spread over the list carry nearly all of the variation at 2.7x the
    # rows rather than 8.4x. 0 means every candidate.
    "--eval_candidates_per_pair=": set_config_field(
        "eval_candidates_per_pair", int
    ),

    # --- 16. Training mechanics ---
    "--ep=": set_config_field("ep", int),  # total training epochs; also the upper bound lr_warmup_epochs and the cosine-decay length are carved out of
    "--lr=": set_config_field("lr", float),  # base Adam learning rate; also the anchor for lr_warmup_cosine's decay floor (lr * lr_min_factor)
    "--weight_decay=": set_config_field("weight_decay", float),  # global Adam weight decay; fallback value for bilinear_weight_decay/deepclip_gate_weight_decay when unset
    "--lr_warmup_epochs=": set_config_field("lr_warmup_epochs", int),  # epochs over which lr_warmup_cosine's linear warm-up ramps before cosine decay; clamped to ep-1; requires lr_warmup_cosine
    "--lr_min_factor=": set_config_field("lr_min_factor", float),  # fraction of lr the cosine schedule decays down to as its floor, in (0,1]; requires lr_warmup_cosine
    "--checkpoint_window=": set_config_field("checkpoint_window", int),  # rolling-average window (epochs) smoothing the validation selection metric before comparing "best so far"; must be >0
    # Rolling validation metric for checkpoint selection. Empty uses
    # balanced_accuracy at threshold 0.5. Small --family_only/--lipid_subclass
    # validation blocks may have only a dozen rows (~0.06-0.1 BA per row),
    # making selection noisy (see new_train.py's AUC-vs-BA comment).
    # "auc" selects by threshold-independent ranking. This changes the chosen
    # epoch, not calibration: reported sensitivity/specificity/BA still use 0.5.
    "--checkpoint_selection_metric=": set_config_field("checkpoint_selection_metric"),
    "--seed=": set_config_field("seed", int),  # seeds all reproducible randomness and the train/valid/test split itself; part of the metrics_summary.csv row key
    "--label=": set_config_field("label"),  # human run name; becomes the top-level directory under every result tree; falls back to the OAR job name or an attention-flag-derived name if blank
    "--batch=": set_config_field("batch", int),  # DataLoader batch size; overridden (batch_size/shuffle dropped) by a custom batch_sampler under balanced_batches or rotate_train_negatives
    "--num_workers=": set_config_field("num_workers", int),  # DataLoader worker-process count; >0 also enables persistent_workers and gates the cached-tensor "preassembly" fast path
    # Lipid LR as a fraction of the rest of the model at epoch 0, in [0, 1).
    # 0.0 is allowed by validate() but avoided as a default: freezing a random
    # lipid encoder makes the head learn a random projection, not a head start.
    # requires lipid_path_handicap.
    "--lipid_path_weight=": set_config_field("lipid_path_weight", float),
    # Linearly ramp lipid_path_weight to 1.0 over R epochs. Epoch 0 uses w0;
    # epoch >= R uses 1.0. R=0 keeps a permanent handicap.
    # Together, R and w0 remove delay = R * (1 - w0) / 2 effective lipid epochs:
    # the ramp allows R*(w0+1)/2 out of R, so 0.1/50 removes 22.5 epochs.
    # R must keep the handicap relevant late in training. Ending at epoch 10
    # of 150 leaves 140 full-speed epochs to erase the protein head start.
    # An earlier R<=10 cap tried to avoid the old median peak at epoch 16;
    # that was wrong because moving the peak is the intended effect.
    # R=50 leaves 100 full-speed epochs, covering the 90th-percentile peak
    # at ~113. R=0 is supported but changes optimization for the whole run,
    # so it is not the default. Protein learning time is unknown: protonly
    # is a constant predictor peaking at epoch 1. Tune the effective delay.
    # requires lipid_path_handicap.
    "--lipid_path_weight_ramp_epochs=": set_config_field(
        "lipid_path_weight_ramp_epochs", int
    ),

    # --- 18. DeepCLIP-specific ---
    # NUM_FILTERS: learned windows PER WIDTH, not in total. DeepCLIP's value is 1.
    "--deepclip_filters=": set_config_field("deepclip_filters", int),
    # FILTER_SIZES: the window widths, in characters.
    "--deepclip_widths=": set_config_field("deepclip_widths"),
    # LSTM_NODES: hidden units per direction of the single bidirectional LSTM.
    "--deepclip_lstm=": set_config_field("deepclip_lstm", int),
    # LSTM_DROPOUT and DROPOUT_OUT.
    "--deepclip_lstm_dropout=": set_config_field("deepclip_lstm_dropout", float),
    "--deepclip_out_dropout=": set_config_field("deepclip_out_dropout", float),  # dropout after the LSTM/profile stage before readout; requires deepclip
    # "constant" uses DeepCLIP's W=0.01, b=None
    # (oned_convlayer_rectify.py, lasagne.init.Constant). Same-width filters
    # stay identical, which works for NUM_FILTERS=1 but adds no capacity above
    # it. validate() requires "normal" (random, scale 0.01) for >1 filters.
    "--deepclip_conv_init=": set_config_field("deepclip_conv_init"),
    # "sum" reproduces DeepCLIP's DenseLayer(num_units=1, W=Constant(1.0),
    # b=None). DeepCLIP pads all sequences to one fixed length without masks
    # (slice_n_pad.py), so each sum covers the same number of positions.
    # Here lengths are 26-165 characters. At initialization, profile values
    # are nearly constant (0.556 +/- 0.027), so sum reads molecule size:
    # score = 0.556 * length, or 14.2 at 26 chars and 91.9 at 165.
    # Default "mean" divides by each molecule's length; "sum" stays available
    # to reproduce the published readout.
    "--deepclip_readout=": set_config_field("deepclip_readout"),
    # Stack convolutions to widen DeepCLIP's receptive field. One layer
    # sees at most 8 characters at published widths; two width-W layers see
    # 2W-1. Hexose rings span 32-38 SMILES characters in this table
    # (analysis/probes/deepclip_headgroup_probe.py), so one layer sees C/O
    # content but cannot recognize the whole ring. Later layers read
    # concatenated filter channels, not one-hot input.
    "--deepclip_conv_layers=": set_config_field("deepclip_conv_layers", int),
    # Protein DESCRIPTOR_CATALOG entries -> one-hidden-layer MLP -> one
    # weight per LSTM channel for the profile sum. Published DeepCLIP has no
    # protein input, so it gives GLTP and GLTPD1 the same prediction despite
    # their opposite glycosphingolipid/sphingomyelin specificity, necessarily
    # missing one. Multiplicative gating can mirror specificity; an additive
    # protein term cannot. The per-position profile stays interpretable and
    # shows which molecular regions each pocket reads.
    # excl. deepclip_profile_weights.
    "--deepclip_protein_gate=": set_config_field("deepclip_protein_gate"),
    # Hidden width of that gate's MLP.
    "--deepclip_gate_hidden=": set_config_field("deepclip_gate_hidden", int),
    # THE PROTEIN, as a token sequence feeding that same gate: the pocket residues in
    # chain order (dataloader/protein_tokens.py), each one-hot in the named alphabets
    # -- "aa" (amino acid), "3di" (Foldseek structural letter, data/protein_3di.csv)
    # or "aa,3di" -- plus a chain-break channel. A conv+BiLSTM tower of DeepCLIP's own
    # shape (--deepclip_widths/filters/lstm/conv_init) reads it, and its mean state is
    # the gate's input, next to any --deepclip_protein_gate descriptors. The gate's
    # zero-initialised last layer keeps the run starting as published DeepCLIP.
    # excl. deepclip_profile_weights.
    "--deepclip_protein_tokens=": set_config_field("deepclip_protein_tokens"),
    # Separate weight decay for the --deepclip_protein_gate MLP in
    # architecture/deepclip.py. This limits gate overfitting on small
    # --family_only runs (a few hundred rows, ~9 proteins) without penalizing
    # the sequence conv/LSTM trunk. None uses --weight_decay.
    # Requires --deepclip_protein_gate (validate()).
    "--deepclip_gate_weight_decay=": set_config_field("deepclip_gate_weight_decay", float),
}


def apply_value_handler(config, argument):
    """Apply a name=value handler; return whether it matched."""
    for prefix, handler in VALUE_HANDLERS.items():
        if argument.startswith(prefix):
            handler(config, read_value(argument))
            return True

    return False


def read_named_configuration(argv):
    """Parse CLI options and validate ModelConfig."""
    config = ModelConfig()
    for argument in argv[1:]:
        flag_handler = FLAG_HANDLERS.get(argument)
        if flag_handler is not None:
            flag_handler(config)
        elif not apply_value_handler(config, argument):
            raise ValueError(f"Unknown parameter: {argument}")

    config.validate()
    return config


def read_configuration(argv=None):
    """Read supplied arguments or sys.argv."""
    if argv is None:
        argv = sys.argv

    return read_named_configuration(argv)
