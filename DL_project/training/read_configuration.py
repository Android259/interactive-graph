import sys
from dataclasses import dataclass, field


# Width of the cavity descriptor --pocket_descriptors appends to the fused pair vector.
# The list itself is POCKET_DESCRIPTOR_NAMES in dataloader/protein_graph_builder.py,
# which checks the descriptor it builds against this number and names the mismatch;
# change the list and this changes with it (files/pocket_shape_descriptors.md too).
POCKET_DESCRIPTOR_COUNT = 13

POOL_TYPES = ("add", "max", "mean", "add_max", "gem")
LOSS_TYPES = ("mse", "cross_entropy", "bce", "pairwise_rank")
LIPID_FRAGMENTS_TREATMENTS = ("concat", "random_choice", "fragments_mask")
PROTEIN_POOLINGS = ("ordinary", "attention_pos_bias", "pooling_by_pockets")
# Narrows which attention site attention_by_pockets restricts. Not passing it means
# both, which is what --attention_by_pockets alone already says, so "both" is the
# default value and not an accepted one. "cross" is the interesting middle: the GAT
# and the protein self-attention still see the whole chain, so structural context is
# intact, but the lipid can only look at the binding site -- that separates "what the
# protein encodes" from "what the partner may read".
POCKET_ATTENTION_SITES = ("self", "cross")

# Frozen per-residue protein embeddings that REPLACE the ESM3 vector. Each entry is
# (config flag, file suffix, width attribute); files live in
# data/embedding_<suffix>/<protein>_<suffix>.pkl, one row per coarse_graph_nodes.csv
# row, exactly like data/embedding_ESM3_v2 and data/embedding_RNABANG.
#
# All three are structure-conditioned: a residue's vector is a function of its local
# geometry rather than of where its sequence sits in a family. That is the property
# ESM3 lacks and the reason to try them -- the cold-family split withholds precisely
# the evolutionary/family statistics ESM3 is best at.
FROZEN_PROTEIN_EMBEDDINGS = (
    ("proteinmpnn_replace_esm3", "PROTEINMPNN", "proteinmpnn_embedding_dim"),
    ("esmif1_replace_esm3", "ESMIF1", "esmif1_embedding_dim"),
    ("saprot_replace_esm3", "SAPROT", "saprot_embedding_dim"),
)
ACT_FNS = ("leakyrelu", "gelu", "prelu")


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
# in LIPID_COLDSPLIT_SETS (dataloader/sampler.py, which also records how each set was
# chosen and how isolated it is); only the names are repeated here, so that a typo fails
# at parse time instead of after a job reaches a GPU. PLIDataset checks the two agree.
LIPID_COLDSPLIT_NAMES = ("sphingolipids", "phosphorus_free", "choline", "anionic")


def read_lipid_coldsplit(value):
    """Resolve the name of a lipid-class set held out of training."""
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
    """Parse a permissive command-line boolean value."""
    if value is True:
        return True
    value = str(value).lower()
    return value in ["1", "true", "yes", "on"]


def read_value(argument):
    """Return the value component from a name=value argument."""
    return argument.split("=", 1)[1]


def read_excluded_groups(value):
    """Parse and normalize excluded protein-group names."""
    values = [item.strip() for item in str(value).split(",") if item.strip()]
    excluded_groups = []

    for item in values:
        group_name = EXCLUDED_GROUP_ALIASES.get(item.lower().replace("-", "_"))
        if group_name is None:
            raise ValueError(f"Unknown excluded_groups group: {item}")
        excluded_groups.append(group_name)

    return list(dict.fromkeys(excluded_groups))


def read_test_group(value):
    """Resolve a single protein-group name to its canonical form."""
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
    """Parse the site narrowing; "both" is the default and not passed explicitly."""
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
    """Parse per-block MLP hidden widths, e.g. "protein_mlp=101,final=175".

    Each site defaults to ``m * hiddim``; ``<site>_third`` sets the third layer's width
    separately (it defaults to the site's own width). This is how widths discovered by a
    gate/bilevel run are baked into a clean production run.
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
    """Parse the hidden widths of the sequential PLM compression, e.g. "512,171,57"."""
    return [int(item.strip()) for item in str(value).split(",") if item.strip()]


def read_excluded_subgroups(value):
    """Parse excluded protein subgroup names while preserving order."""
    excluded_subgroups = []
    values = [item.strip() for item in str(value).split(",") if item.strip()]

    for item in values:
        excluded_subgroups.append(item)

    return list(dict.fromkeys(excluded_subgroups))


@dataclass
class ModelConfig:
    third_layers_in_mlps: bool = False
    cross_attention: bool = True
    # Fuse the two pooled partners with an interaction vector lip^T W prot
    # (torch.nn.Bilinear) instead of concatenating them, so the classifier's
    # discriminative signal is multiplicative in both partners and a single-
    # partner (lipid-identity) shortcut cannot survive. See Final_Layer.
    bilinear_fusion: bool = False
    # Adversarial anti-shortcut training (Ganin-style gradient reversal): add a
    # per-partner adversary head that predicts the label from one partner's pooled
    # PRE-cross-attention representation alone (before cross-attention mixes in the
    # counterpart); a gradient-reversal layer pushes that single-partner encoder to
    # be individually uninformative, forcing the decision onto the interaction.
    # adv_weight scales the adversary CE added to the task loss; adv_lambda is the
    # gradient-reversal strength. Complementary to bilinear_fusion.
    adversarial_grl: bool = False
    adv_weight: float = 1.0
    adv_lambda: float = 1.0
    # adv_deep swaps each adversary's 2-layer MLP for the cross-attention block's
    # shape minus the multihead attention (residual FFN + LayerNorm, then the binary
    # head), closing the capacity gap that lets cross-attention decode single-partner
    # leakage the shallow probe never penalised. adv_lambda_ramp replaces the constant
    # reversal strength with Ganin's sigmoid schedule (see ramped_adv_lambda).
    adv_deep: bool = False
    # Which partner each adversary polices. Both on reproduces the original behaviour.
    # Turning one off is the only way to ask what that side alone contributes, which
    # matters because the lipid side is the one that carries the transferable signal
    # (lipid_only generalises better than the full model) -- suppressing it may cost
    # more than the shortcut it removes.
    adv_lipid: bool = True
    adv_protein: bool = True
    adv_lambda_ramp: bool = False
    adv_lambda_ramp_by_fit: bool = False
    # Family DANN (Ganin's domain-adversarial setup proper): a head on the FUSED,
    # post-cross-attention representation predicts which of the 9 protein families the
    # sample came from, behind a gradient reversal. Unlike the per-partner adversary it
    # can reach the joint representation, which is where family-specific pocket/lipid
    # memorisation lives. dann_class_conditional is not cosmetic -- see
    # ramped_dann_lambda and proposals.md: unconditional family invariance is provably
    # harmful on this dataset because family IS the binding specificity, so the honest
    # version aligns P(features | label, family) per class rather than P(features | family).
    dann_family: bool = False
    dann_weight: float = 1.0
    dann_lambda: float = 1.0
    dann_class_conditional: bool = True
    dann_lambda_ramp: bool = False
    dann_lambda_ramp_by_fit: bool = False
    # Chemistry prior (files/interaction_signal_plan.md 4.1, 4.3). score = learned
    # scalar * s_chem(lipid) + the ordinary classifier logit, s_chem frozen and computed
    # once from train-split labels only (dataloader/chemistry_prior.py). Because s_chem
    # is added AFTER the classifier rather than fed into it, the task loss has no need
    # for the fused representation to carry a copy of it -- which is what makes
    # chem_adversary (below) safe to run without fighting the task loss over genuinely
    # shared, label-relevant variance. See interaction_signal_plan.md 4.3 for why this
    # ordering matters and chem_adversary must not be applied without it.
    chem_prior: bool = False
    chem_neighbours: int = 15
    # Regression GRL on the FUSED post-cross-attention representation (same hook as
    # dann_family) against s_chem, not the label: it discourages the fused vector from
    # carrying a redundant copy of the chemistry marginal, while leaving room for
    # genuinely protein-specific reliance on chemical similarity (an interaction with s_chem, not a marginal correlation with it) to survive -- a regression head reading only
    # the fused vector cannot cheaply reconstruct a per-protein modulation of a
    # lipid-only target the way it can reconstruct the marginal itself.
    chem_adversary: bool = False
    chem_weight: float = 1.0
    chem_lambda: float = 1.0
    chem_lambda_ramp: bool = False
    chem_lambda_ramp_by_fit: bool = False
    # Pocket-vs-chain-length pair term (files/pocket_lipid_compatibility.md): unlike
    # every entry in POCKET_DESCRIPTOR_NAMES, this depends on BOTH the protein and the
    # candidate lipid, so it cannot collapse to a pure family label the way a
    # protein-only summary can. Two independent consumers of the same raw value:
    #
    # --pocket_compat_prior : frozen and added to the logit outside the network, same
    #     mechanism as --chem_prior -- fit_prior_calibration in dataloader/
    #     chemistry_prior.py fits it JOINTLY with s_chem when both are on, so the two
    #     terms do not double-count shared variance and neither steals the other's
    #     credit for it.
    # --compatibility_input : standardised (not calibrated) and concatenated into the
    #     fused representation before the classifier, so the network's own weights
    #     decide how much to trust it and can combine it nonlinearly with everything
    #     else -- no guaranteed floor, unlike the frozen path, and unverified without
    #     a real run. Incompatible with --bilinear_fusion (see validate()): the pair
    #     value has nowhere well-defined to enter a bilinear form of exactly two
    #     vectors.
    # --compatibility_split_input : the same two quantities, unmixed, as TWO inputs --
    #     -chain_length and relu(chain - extent) on a coarsened extent. Why the split
    #     exists (files/compat_input_audit.md): the difference above is additive, so its
    #     own pair content is exactly 0.0000, and its whole ranking value inside a
    #     protein IS the chain length -- a lipid-only rule that the doubly-cold split
    #     leaves available, since it holds out head-group classes and chain length is
    #     orthogonal to those. Split apart, the lipid-only half is named and can be
    #     reported against or adversarially removed, and the pair half is measurable on
    #     its own. The coarsening is what keeps pocket_extent from doubling as a protein
    #     id: at full resolution it carries eta^2 0.78 against protein identity, the
    #     same fold-label channel that got POCKET_DESCRIPTOR_NAMES rejected.
    # --compat_extent_bins : how many quantile levels the extent is rounded to, cut on
    #     TRAIN proteins only. 1 removes the extent entirely, which makes the clash term
    #     constant and is the degenerate case, not a useful setting.
    pocket_compat_prior: bool = False
    compatibility_input: bool = False
    # --compat_input_parts : which halves the split form feeds -- "chain,clash" (both),
    #     "chain" (the marginal with the protein removed entirely) or "clash" (the pair
    #     term with the marginal removed). Three arms, because with both columns present
    #     a model free to lean on either one answers neither question.
    compatibility_split_input: bool = False
    compat_input_parts: str = "chain,clash"
    compat_extent_bins: int = 4
    # Descriptors from Lipovsky et al. (Nature 2025, s41586-025-10040-y), the paper
    # behind this project's LTP-lipid measurements (dataloader/pair_descriptors.py):
    # chain length (reusing pocket_lipid_compatibility.chain_lengths_by_row),
    # unsaturation count, an H-bond-capacity proxy, and an occupancy term (heavy-atom
    # count vs the SAME coarsened pocket_extent --compatibility_split_input's "clash"
    # uses, so a held-out protein's raw cavity size cannot leak through it either).
    # architecture/pair_descriptor_head.py embeds each as a token, adds two more
    # multiplicative pair terms (pocket aromatic_share x unsaturation, pocket polar
    # share x H-bond capacity -- proxies for the paper's pose-specific Phe/H-bond
    # findings, since this project has no docking pipeline to place them properly),
    # runs one self-attention layer over the token set, and mean-pools it to one
    # vector concatenated into the fused representation (Final_Layer), the same slot
    # --compatibility_input uses. Requires --pocket_descriptors (the aromatic_share /
    # apolar_sasa_share source) and is incompatible with --bilinear_fusion for the
    # same reason --compatibility_input is (see validate()).
    pair_descriptors: bool = False
    # Whether aromatic_share/polar_share (pocket_descriptor-derived, protein-only)
    # are among the head's tokens. Default True, matching every run so far. Set
    # --no_pair_descriptor_pocket_shares to drop them and keep only the 6
    # dataloader-computed tokens (chain, unsaturation, hbond, heavy, occupancy,
    # extent): those two are read straight off POCKET_DESCRIPTOR_NAMES, which
    # dataloader/pocket_lipid_compatibility.py's own docstring already flags as a
    # family fingerprint (eta^2 0.28-0.85 against protein identity,
    # preprocessing/pocket_descriptor_identity_check.py) -- see project memory
    # [[descriptors-path-fingerprint-leak]]: on descriptors_path (--descriptors_head),
    # LBP_BPI_CETP's net_AUC_prot (0.869) exceeded the protein-blind chemistry null
    # (0.699) by more than the null's own richer lipid-structure input could explain,
    # and aromatic_share/polar_share were the only channel left that could carry it.
    # This flag reruns that same label with the suspect channel removed, to confirm
    # or kill the attribution.
    pair_descriptor_pocket_shares: bool = True
    # Diagnostic ablation, mirroring --lipid_only/--protein_only: zeroes BOTH pooled
    # partners so the classifier reads only the descriptor head's output. Meant to be
    # set at EVAL time on a checkpoint trained with --pair_descriptors on, to measure
    # what that head alone (its already-trained weights) predicts -- not a training
    # mode of its own.
    pair_descriptors_only: bool = False
    # Sufficiency test for --pair_descriptors alone: InteractionClassification never
    # builds protein1/lipid1/cross_attention1 (or their double_attention pairs) under
    # this flag, and Final_Layer builds only the descriptor head and a small 2-layer
    # classifier on its hiddim-wide output -- no pooling, bilinear, adversary, DANN or
    # chem-prior machinery. A genuinely separate, cheap model (GPU cost is the ~3% of
    # parameters architecture/pair_descriptor_head.py spends, not the ~93% the encoders
    # and cross-attention spend, see analysis/model_parameter_breakdown.py), not an
    # ablation of the full one: a checkpoint trained under --descriptors_head has a
    # different state_dict than one trained without it and the two cannot load into
    # each other. Requires --pair_descriptors (which requires --pocket_descriptors);
    # everything that assumes the full architecture's modules is rejected in
    # combination (see validate()) since Final_Layer would not have built them.
    descriptors_head: bool = False
    # Give the lipid branch a smaller learning rate than the rest of the model, leaving
    # the forward pass exactly as it was: the lipid stream learns proportionally slower
    # while the protein branch keeps its full step, which is the warm-up remedy for the
    # protein path never being used. Matched runs put lipid_only at 0.621 test BA
    # against 0.603 for the full model, i.e. the protein branch currently costs more
    # than it adds, and one explanation is that the lipid path reaches a good solution
    # first and the protein path stops receiving useful gradient. Unlike the adversary
    # this does not push the lipid representation to be unpredictive -- it only slows it
    # down, so nothing that transfers is destroyed.
    #
    # Implemented as a separate optimizer param group, not as a gradient scale on the
    # activations, for two reasons. Adam's step m/sqrt(v) is invariant to a constant
    # rescaling of the gradient, so scaling the lipid gradient is very nearly a no-op
    # under this optimizer (what little it does is a relative weight-decay boost, since
    # torch.optim.Adam's coupled L2 is added AFTER the scale). And selecting parameters
    # is the only way to keep the handicap off the protein: past cross-attention the
    # lipid activations are a function of both partners, so a hook there would run back
    # into the protein encoder through the very interaction channel this exists to
    # protect. InteractionClassification.lipid_branch_parameters draws the boundary.
    #
    # The two numbers below only apply when this is on, and nothing about the handicap
    # runs when it is off: no split param group, no per-epoch schedule.
    lipid_path_handicap: bool = False
    # The lipid branch's lr as a fraction of the rest of the model's, at epoch 0, in
    # [0, 1). 0.0 is rejected as a default choice rather than by validate(): a frozen
    # lipid encoder means the head spends the first epochs learning to read a random
    # projection, which is a different intervention than a head start.
    lipid_path_weight: float = 0.1
    # Epochs over which lipid_path_weight ramps linearly back to 1.0 (0 = never ramps,
    # a permanent handicap rather than a warm-up). Epoch 0 uses lipid_path_weight,
    # epoch >= this uses 1.0.
    #
    # Neither number means anything alone; what the pair buys is how many epochs of
    # lipid learning the ramp REMOVES. A linear ramp lets the lipid branch through
    # R*(w0+1)/2 effective epochs out of R, so
    #
    #     delay = R * (1 - w0) / 2
    #
    # and 0.1/50 removes 22.5 epochs of lipid training.
    #
    # R is set by how long the handicap has to PERSIST to still matter at the end, not
    # by how long the lipid path's early phase lasts. A short ramp is self-defeating on
    # a 150-epoch run: lift it at epoch 10 and the lipid branch has 140 epochs at full
    # speed to reassert itself and erase whatever room the protein branch was given.
    # (An earlier version capped R at 10 to keep the full model's median peak, epoch 16,
    # outside the ramp. That was backwards -- the point of the handicap is to move that
    # peak, so a peak reached under it is the thing being measured, not a contaminated
    # reading.) 50 leaves 100 epochs of unhandicapped training after it, and the 90th
    # percentile of runs peaks by epoch ~113, so the budget still covers them.
    #
    # ramp_epochs=0 -- a permanent handicap, never lifted -- is the logical extreme of
    # the same argument and is supported; it is not the default only because it changes
    # the optimisation problem for the whole run rather than front-loading the change.
    #
    # What is NOT known is how long the protein branch actually needs; protonly is
    # degenerate (a constant predictor, peak at epoch 1), so the protein side has no
    # convergence timescale in this data. The delay is the thing to vary if these need
    # tuning.
    lipid_path_weight_ramp_epochs: int = 50
    # Match negatives to positives inside every (family, lipid class) cell, which removes
    # the per-lipid-class prior the coarser samplers leave behind (measured: per-class
    # positive rate 0.25-0.68 -> 0.50-0.51). It does NOT also balance per protein --
    # that trade is unavoidable on this data, see
    # New_dataloader.sample_lipid_class_balanced_negatives -- and it currently overrides
    # balanced_proteins when both are set.
    balanced_lipid_classes: bool = False
    # Compute attention block-diagonally on a dense (graphs, max_nodes, dim) layout
    # instead of one long padded sequence with an N x N -inf mask, which is the same
    # attention over ~9x fewer logits. See architecture/fast_attention.py -- results
    # match the default path to float32 rounding (~6e-08), not bitwise, so runs started
    # with it are not bit-comparable against runs without it.
    fast_attention: bool = False
    protein_self_attention: bool = True
    lipid_self_attention: bool = True
    double_attention: bool = False
    single_gat_layer: bool = True
    geometric_transformer: bool = False
    geometric_ipa_chunk_size: int = 64
    transformer_conv: bool = False
    gine_conv: bool = False
    protein_gine_residual: bool = False
    attention_residual_gates: bool = False
    protein_gat_residual: bool = False
    # Structured-sparsity gates: learn architecture size (m/FFN width, heads,
    # blocks, third layer, cross-attention) in one run by gating prunable groups
    # and penalizing active gates (L0 hard-concrete or L1 scale).
    structured_sparsity: bool = False
    sparsity_mode: str = "l0"
    sparsity_lambda: float = 0.0
    target_sparsity: float | None = None
    sparsity_gate_ffn: bool = False
    sparsity_gate_heads: bool = False
    sparsity_gate_blocks: bool = False
    sparsity_gate_third_layer: bool = False
    sparsity_gate_cross_attention: bool = False
    # Bilevel hyperparameter discovery: gate every internal MLP hidden layer (learn
    # widths) and/or learn per-block dropout, optimizing these lambda parameters on the
    # validation split (first-order alternating) while weights train on the train split.
    # Discovered widths/dropout are recorded to test_metrics for later plain runs.
    gate_all_mlp_hidden: bool = False
    gate_all_mlp_layers: bool = False
    no_ffns: bool = False
    mlp_widths: dict = field(default_factory=dict)
    bilevel: bool = False
    bilevel_dropout: bool = False
    bilevel_lr: float = 1e-3
    # Per-layer learnable dropout is realized as Concrete Dropout (Gal et al. 2017)
    # trained on the TRAIN objective (first-order bilevel would degenerate p->0, like
    # weight_decay). Each dropout site has its own p and the full KL surrogate
    #   concrete_dropout_weight_reg * ||W||^2/(1-p) - concrete_dropout_reg * K * H(p)
    # over the Linear it feeds. Canonically weight_reg = l^2/(tau*N), dropout_reg = 2/(tau*N).
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
    ep: int = 150
    checkpoint_window: int = 5
    seed: int = 0
    excluded_groups: list = field(default_factory=list)
    # Head-group classes held out of training alongside excluded_groups. With both set
    # the split is cold on both axes: a row of the held-out family in a held-out class
    # has neither its protein nor its lipid class anywhere in train, so no per-lipid
    # label prior carries over to it. Empty means the old one-axis behaviour.
    # The second axis of the cold split. Both flags hold whole head-group classes out of
    # training on top of excluded_groups; which classes is DERIVED from the held-out
    # family by dataloader.sampler.lipid_classes_for_holdout, not typed in, because the
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
    double_coldsplit: bool = False
    mixed_coldsplit: bool = False
    # The other axis on its own: a whole chemical family of lipids leaves training while
    # every protein stays. Answers "a lipid of a chemistry never seen arrives -- which of
    # the known proteins bind it", which is the question that matters when the screening
    # panel grows rather than the protein list. Takes the name of one set; the launcher
    # expands a bare --lipid_coldsplit into one run per set.
    lipid_coldsplit: str = ""
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
    coldsplit_share: float = 0.8
    excluded_subgroups: list = field(default_factory=list)
    balance_excluded_group_negatives: bool = False
    balance_negatives_by_family: bool = False
    balanced_proteins: bool = False
    balanced_batches: bool = False
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
    negatives_per_positive: int = 2
    # Bias the negatives drawn for a protein's TRAIN-side rows toward its own chemistry
    # hard cases -- unlabeled lipids Tanimoto-similar to a lipid that protein IS
    # positive for -- instead of drawing them uniformly, so the loss must separate
    # binder from non-binder chemistry rather than lean on the base rate. Applies only
    # to groups whose family is not in --excluded_groups: a held-out family's rows
    # become validation/test after the split, and this flag must not change what those
    # measure, only what training sees. See dataloader/sampler.py's
    # _sample_group_balanced_negatives and _hard_negative_weights.
    hard_negative_mining: bool = False
    # Sampling-weight mass steered toward the hardest candidates; the rest (1 - share)
    # stays uniform, so a protein whose positives have no chemically close negatives in
    # its own pool still draws its full quota instead of concentrating on whatever is
    # least-far-from-zero similarity.
    hard_negative_share: float = 0.5
    test_group: str = ""
    cold_split: bool = False
    # Diagnostic shortcut ablation: zero one pooled partner before the final
    # classifier (and disable cross-attention) so the model must decide from the
    # other partner alone. lipid_only hides the protein, protein_only hides the
    # lipid. Used to confirm which partner's identity is being memorized on cold
    # splits (lipid_only and protein_only are mutually exclusive).
    lipid_only: bool = False
    protein_only: bool = False
    batch: int = 16
    num_workers: int = 4
    lipid_fragments_treatment: str = "random_choice"
    protein_pooling: str = "attention_pos_bias"
    
    lipid_concat: bool = False
    lipid_random_choice: bool = True
    lipid_fragments_mask: bool = False
    # The ";"-separated SMILES of a row are candidate structures for one measured lipid
    # species (sn-positional / double-bond isomers the spectrum cannot separate), and
    # the embedding path used to keep only the first of them regardless of
    # lipid_fragments_treatment -- which made all three treatments the same run. This
    # flag is that behaviour. It is now OFF by default, so the chosen treatment sees
    # the whole candidate set; runs before this change had it on and encoded the first
    # candidate alone, whichever treatment they named. Turning it back on
    # (--lipid_first_fragment_only) is only meaningful with concat or fragments_mask,
    # which then degenerate to that single candidate; with random_choice the draw would
    # have nothing to draw from, so validate() rejects the pair. It governs the
    # embedding path only; the lipid_graph_isomers path has always used every candidate.
    lipid_first_fragment_only: bool = False
    # Marginalize evaluation over the candidate set instead of scoring one member of it.
    # Training under random_choice teaches invariance to the degrees of freedom the mass
    # spectrum left open, and this is that invariance on the reading side: a validation
    # or test row is scored once per candidate and the probabilities are averaged before
    # the threshold, so the metric is one quantity across epochs and is the answer for
    # the species rather than for an arbitrary member of it.
    eval_average_candidates: bool = False
    # How many candidates of a pair the averaged evaluation actually scores. A species
    # can list up to 37 of them and scoring every one makes the evaluation blocks larger
    # than the training epoch (2912 rows against 345 pairs on START), while the
    # candidates of one species sit at cosine 0.98 of each other in the embedding, so
    # four evenly spread over the list carry nearly all of the variation at 2.7x the
    # rows rather than 8.4x. 0 means every candidate.
    eval_candidates_per_pair: int = 4
    lipid_isomers: bool = False
    lipid_graph_isomers: bool = False

    ordinary_prot_pooling: bool = True
    prot_attention_pos_bias: bool = True
    prot_pooling_by_pockets: bool = False
    prot_pos_bias_per_head: bool = False
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
    # Under fast_attention the restriction is applied by compaction rather than by
    # writing -inf into non-pocket keys: the key layout is built over pocket nodes
    # only, so the padded key axis shrinks from the largest protein (458 residues) to
    # the largest pocket (64), a factor 7.2 on the padded rectangle. Queries stay every
    # residue -- each one is still updated, only what it may read changes -- so the
    # logit count falls by the key ratio alone: median pocket is 33 of 203 residues,
    # giving ~5.3x at the protein self-attention and ~6x at the lipid-protein
    # cross-attention, not the square of that. Both spellings are the same attention to
    # float rounding (measured 1.5e-08, the same order as fast_attention's own ~6e-08
    # against the default path), so there is nothing to choose between them and no
    # flag: the cheaper one is simply used whenever the dense layout it needs exists.
    attention_by_pockets: bool = False
    # Which of the two sites the restriction applies to, see POCKET_ATTENTION_SITES.
    pocket_attention_sites: str = "both"
    # Derived in validate() from the two above; read by the attention modules.
    pocket_attention_self: bool = False
    pocket_attention_cross: bool = False
    # Feed only pocket residues from the dataloader on: node features, PLM rows,
    # buriedness and confidence are subset, and the graph keeps only edges whose both
    # endpoints survive. Unlike attention_by_pockets the GAT no longer sees the rest of
    # the protein at all, so structural context outside the site is gone rather than
    # merely unattendable.
    protein_pockets_only: bool = False
    # Keep this many randomly chosen residues per TRAINING sample, redrawn every epoch;
    # 0 is off. Aimed at the one thing regularisation cannot touch: a protein is
    # memorable because its residue set is fixed, so the encoder can learn the set
    # rather than what the site is like. A subsample redrawn each epoch leaves the
    # site's statistics intact and makes the exact set unlearnable.
    #
    # Not what dropout does. Dropout zeroes DIMENSIONS of the hidden vector,
    # independently at every residue, and the pooled protein vector averages over ~200
    # of them -- so the noise cancels and the pooled vector is nearly unchanged, which
    # is precisely why it cannot hide a fingerprint. Dropping residues changes the set
    # being averaged, so the pooled vector genuinely moves.
    #
    # A FIXED count, not a fraction: the residue count is itself a fingerprint (pocket
    # size tracks protein size at rho = 0.72), and only a fixed count erases it. Pocket
    # sizes run 22 to 64 with a median of 33, so 20 is drawable from every protein
    # without replacement. A protein with fewer residues than this keeps all of them --
    # and, for that protein, keeps its size visible.
    protein_residue_subsample: int = 0
    # Replace the ESM3 vector with a frozen structure-conditioned one. Mutually
    # exclusive with each other and with every RNA-BAnG mode; see
    # FROZEN_PROTEIN_EMBEDDINGS and proposals.md.
    #
    # ProteinMPNN: ~1.7M parameters, message passing over each residue's k nearest
    # neighbours with N/CA/C/O/Cb distances. Encoder output, before any sequence
    # decoding -- pure local geometry, the cheapest of the three by two orders of
    # magnitude.
    proteinmpnn_replace_esm3: bool = False
    proteinmpnn_embedding_dim: int = 128
    # ESM-IF1: ~142M, inverse folding over backbone coordinates. Its vector answers
    # "which residue belongs in this geometry", which is a description of the site.
    esmif1_replace_esm3: bool = False
    esmif1_embedding_dim: int = 512
    # SaProt: Foldseek 3Di structure tokens interleaved with residues. A hybrid --
    # part of its signal is still sequence-family, so it partly reproduces what makes
    # ESM3 fail here.
    saprot_replace_esm3: bool = False
    saprot_embedding_dim: int = 1280
    # Append three more Voronota per-residue columns to the protein node vector, which
    # otherwise carries only residue_type, residue_sas_area and residue_volume:
    #   residue_mean_ev28, residue_mean_ev56  -- exposure/burial at two probe radii,
    #     i.e. how enclosed the residue is at two length scales; a lipid cavity is
    #     defined by exactly this and the GAT currently has to infer it from contacts
    #   hydrophobicity                        -- Kyte-Doolittle index of residue_type
    # All three are already in data/graphs/<protein>/coarse_graph_nodes.csv, computed
    # offline; nothing new is generated. This is the fold-independent half of the
    # protein description, which is what a cold-family split needs: unlike the PLM
    # embedding these say what the site is like rather than which protein it belongs
    # to. The columns are appended, so node[:, 0..2] keep their meaning for every path
    # that indexes them positionally (see Protein_encoder's frozen node adapter).
    protein_extra_node_features: bool = False
    # One fixed-length descriptor of the binding cavity per protein, concatenated to
    # the fused pair vector just before the classifier MLP. Built offline from the
    # Voronota columns already in coarse_graph_nodes.csv, aggregated over the pocket
    # residues -- no fpocket, no new data. See POCKET_DESCRIPTOR_NAMES in
    # dataloader/protein_graph_builder.py for the exact list.
    #
    # Measured before implementing, on the 32 proteins whose positives carry a parsable
    # chain length (Spearman against the mean acyl carbon count of what each protein
    # binds): pocket SASA +0.687 (p=2e-4), pocket volume +0.548, pocket residue count
    # +0.559. But protein size alone gives +0.512, and pocket size tracks protein size
    # at +0.707, so most of that is confounded. Controlling for protein residue count,
    # only **pocket SASA survives** (+0.569, p=7e-4); volume (+0.332, p=0.06) and
    # residue count (+0.323, p=0.07) do not. Burial (ev14/ev28/ev56), depth,
    # hydrophobicity and apolar share showed nothing against chain length or head-group
    # diversity (|r| < 0.35, all p > 0.05).
    #
    # The size-like entries are kept anyway, but note what they are on a cold-family
    # split: protein size is close to fold identity, which is exactly the shortcut the
    # split is meant to withhold. If this flag helps, check it is not helping through
    # them -- the shares (pocket_sasa_share, pocket_volume_share) are the scale-free
    # versions and neither correlated with chain length on its own.
    pocket_descriptors: bool = False
    # Width of the descriptor, derived in validate(); 0 when the flag is off.
    pocket_descriptor_count: int = 0
    # Width of the protein node vector, derived in validate(). Single source of truth
    # for the loader that builds it and the encoder that sizes its input layer, so the
    # two cannot drift; also recorded in metrics_summary, where a run's node width is
    # otherwise invisible.
    protein_node_feature_count: int = 3
    bidirectional_edges: bool = False
    tanimoto_weight: bool = False
    class_weights: bool = True
    protein_group_weight: bool = False
    protein_class_weight: bool = False
    protein_class_sqrt_weight: bool = False
    # Restore each protein's pos:neg ratio inside train by weighting rather than by
    # discarding. What a two-axis split needs: holding lipid classes out cuts across
    # proteins and leaves some of them badly skewed (STARD2 at 4 positive against 91
    # unlabeled), and re-matching by subsampling would cut hardest from exactly those.
    # See PLIDataset.get_protein_balance_weights.
    protein_balance_weight: bool = False
    grab_loss: bool = False
    pu_loss: bool = False
    disable_early_stopping: bool = True
    testmode: bool = False
    pu_rho: float = 0.2
    pu_unlabeled_positive_fraction: float | None = None
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
    buryon: bool = True #  возможно лучше обрезать структуру протеинов, чтобы не заворачивались и не образоыаввали ложные покеты потенциально как bias  в  SA CA, анотация всех атомтв обкатка шарами двумя iарами, поверхность  solvent acessible surface, 1 poinnt 4 extreme.  Пустоты -  tangent spheres статья  nature, voronota pockets.  
    loss_type: str = "cross_entropy"
    # Pair rows only with rows of the SAME protein when ranking. Without it the ranking
    # loss optimises the pooled-block AUC, which on this dataset is mostly the chemical
    # marginal a protein-blind null model already answers (files/interaction_signal_plan.md
    # 3). With it the loss optimises what ranks a protein's own lipids against each
    # other, which is the interaction term. Costs pair count: batches are drawn across
    # proteins, so most of the pair matrix is discarded.
    rank_within_protein: bool = False
    pool_type: str = "max"
    # Learned attention pooling (one learnable query per partner) instead of the fixed
    # pool_type reduction: out = sum_i softmax_i(w·x_i) x_i over each graph's nodes -- a
    # content-weighted readout rather than a flat mean/max. attention_pooling_pocket_bias
    # adds a learnable scalar to protein pooling logits for pocket residues, so pooling
    # can prefer the binding site during training (requires attention_pooling).
    attention_pooling: bool = False
    attention_pooling_pocket_bias: bool = False
    # Sliced-Wasserstein pooling (architecture/final_layer.py:SlicedWassersteinPool):
    # reads the SHAPE of a graph's node distribution instead of its average, by matching
    # its quantiles to swe_reference_points learned reference points along learned
    # directions. Aimed at the measurement in files/signal_state.md 4.3 -- the 35
    # proteins sit at ESM3 cosine 0.974 of each other under mean pooling while their
    # binding profiles are at 0.000, so the average is exactly the statistic that does
    # not separate them. swe_freeze_reference keeps the reference points at their random
    # init (the source paper's "SWE_Simple"), leaving only the directions and the output
    # map to be learned, which is the variant to reach for on a protein axis of 21-33.
    swe_pooling: bool = False
    swe_reference_points: int = 32
    swe_freeze_reference: bool = False
    # Use the v2 ESM3 embeddings (preprocessing/embed_protein_esm3_v2.py, read from
    # data/embedding_ESM3_v2/) built from a real structure+coordinates+SASA+confidence
    # input (data/esm3_input/<stem>.pdb, preprocessing/build_consistent_esm3_pdb.py)
    # instead of the v1 sequence-only embeddings in data/embedding_ESM3/. When this is
    # on and attention_pooling_pocket_bias is also on, the pocket-bias term in
    # AttentionPool uses the real per-node pLDDT/B-factor-derived confidence in
    # data/esm3_input/<stem>_node_confidence.csv instead of the binary pocket flag
    # from pocketness.pdb (that flag is a Voronota pocket-membership marker, not a
    # confidence value -- see proposals_plm.md).
    use_esm3_v2_embeddings: bool = False
    # RNA-BAnG protein representations are generated offline by
    # preprocessing/embed_protein_rnabang.py and have one 128-dimensional row per
    # graph residue. The five ways of consuming them below are mutually exclusive.
    # Feed RNA-BAnG rows instead of ESM3 into the existing protein GNN.
    rnabang_replace_esm3: bool = False
    # Treat RNA-BAnG as the complete first protein encoder (projection, optional
    # self-attention, post-SA MLP), so no graph convolution runs on it at all.
    rnabang_full_protein_encoder: bool = False
    # Concatenate the ESM3 and RNA-BAnG rows before the existing protein GNN.
    rnabang_with_esm3: bool = False
    # Replace GATv2 with an edge-aware residual path over ESM3/node(SASA+volume)/
    # buriedness and add the frozen RNA-BAnG geometric-transformer output through a
    # zero-initialized gate.
    rnabang_residual_with_esm3: bool = False
    # Drop every graph and attention layer and encode each residue independently with
    # an MLP adapter over frozen RNA-BAnG + residue type + SASA/volume/buriedness +
    # the edge-to-node summary picked by the rnabang_edge_* flags below.
    rnabang_frozen_node_adapter: bool = False
    # In the frozen-adapter path, encode residue type with a learned 20x8 embedding
    # instead of passing the raw integer residue index as one feature.
    rnabang_residue_type_embedding: bool = False
    # Edge-to-node summaries for the frozen adapter, mutually exclusive; this default
    # keeps the two aggregate columns log1p(sum of incident contact areas) and
    # boundary/area exposure ratio.
    rnabang_edge_current: bool = False
    # Keep the top-21 incident edges ranked by contact area as (area, boundary) pairs
    # plus normalized degree (43 features), zeroing the ranks past the true degree.
    rnabang_edge_topk_by_area: bool = False
    # Encode the padded incident-edge set with a learned permutation-invariant DeepSets
    # encoder instead of using precomputed statistics.
    rnabang_edge_deepsets: bool = False
    # Use PNA-style statistics of the incident edges: sum/mean/std/min/max of area and
    # boundary plus degree, exposed fraction and boundary/area ratio (13 features).
    rnabang_edge_pna: bool = False
    # Use the 0/10/25/50/75/90/100 quantiles of incident-edge area and boundary plus
    # their log totals, degree and boundary/area ratio (18 features).
    rnabang_edge_quantiles: bool = False
    # Encode the padded incident-edge set with a learned set transformer (one
    # self-attention block plus PMA-style pooling).
    rnabang_edge_set_transformer: bool = False
    # Width of one RNA-BAnG residue row, i.e. the input dimension every path above
    # expects from the precomputed embeddings.
    rnabang_embedding_dim: int = 128
    act_fn: str = "leakyrelu"
    HEADS: int = 8
    lr_warmup_cosine: bool = False
    lr_warmup_epochs: int = 0
    lr_min_factor: float = 0.1
    swa: bool = False
    swa_start_frac: float = 0.75
    swa_lr: float | None = None
    save_checkpoint: bool = False
    save_model: bool = False
    # Branch diagnostics, for the question "is the protein half of the model used at
    # all, and from which epoch is it not". save_dynamics adds per-epoch scalars only
    # -- two extra validation passes with the pooled halves ablated in turn, the
    # per-branch gradient norms, the classifier's per-half input weight norms and the
    # between-protein spread of the pooled protein vector. Kilobytes over a whole run,
    # against the hundreds of megabytes that saving every epoch's weights would cost.
    # save_model_in_dynamics adds weights at a few milestone epochs on top, for the
    # probes that cannot be reduced to a scalar decided in advance; it turns
    # save_dynamics on by itself, since milestone weights without the curves they are
    # meant to explain would be weights nobody knows where to look in.
    save_dynamics: bool = False
    save_model_in_dynamics: bool = False

    def validate(self):
        """Validate dependent model dimensions and implied options."""
        if self.HEADS <= 0:
            raise ValueError("HEADS must be greater than zero")
        # Milestone weights are read alongside the per-epoch curves, never on their own.
        if self.save_model_in_dynamics:
            self.save_dynamics = True
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

        if self.hard_negative_mining and not (
            self.balanced_proteins or self.balance_negatives_by_family
        ):
            raise ValueError(
                "hard_negative_mining reweights the per-group negative draw in "
                "_sample_group_balanced_negatives and needs one of "
                "balanced_proteins/balance_negatives_by_family to select that draw"
            )

        if not 0.0 <= self.hard_negative_share <= 1.0:
            raise ValueError(
                "hard_negative_share is the sampling-weight mass steered toward "
                f"chemistry-hard candidates and belongs in [0, 1]; got "
                f"{self.hard_negative_share}"
            )

        if (self.double_coldsplit or self.mixed_coldsplit) and not self.excluded_groups:
            raise ValueError(
                "a lipid-class holdout without excluded_groups leaves every protein in "
                "train, which is a one-axis split on the other axis rather than the "
                "two-axis one it looks like, and there is no held-out family to derive "
                "the classes from. Pass --excluded_groups as well."
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
        # Kept as a literal rather than imported: dataloader.protein_graph_builder is
        # the source of truth for the list, but importing it here would pull torch and
        # torch_geometric into every consumer of ModelConfig, including the analysis
        # scripts that only want to read a run's settings. pocket_descriptor() checks
        # this number against the descriptor it actually built and names the mismatch,
        # so the two cannot drift silently.
        self.pocket_descriptor_count = POCKET_DESCRIPTOR_COUNT if self.pocket_descriptors else 0
        self.protein_node_feature_count = 3 + (
            3 if self.protein_extra_node_features else 0
        )
        if self.pocket_attention_sites != "both" and not self.attention_by_pockets:
            raise ValueError(
                "pocket_attention_sites narrows attention_by_pockets and does "
                "nothing on its own; enable --attention_by_pockets"
            )
        self.pocket_attention_self = self.attention_by_pockets and (
            self.pocket_attention_sites in ("both", "self")
        )
        # pocket_attention_cross is derived at the end of validate(), after the
        # lipid_only/protein_only branch has had its say on cross_attention.
        if (
            self.prot_attention_pos_bias
            and self.pocket_attention_self
            and self.pocket_attention_sites == "both"
        ):
            # Only "both" is a conflict. With the restriction on one site the other
            # site's pocket bias is still a live, trainable preference, which is the
            # point of pocket_attention_sites in the first place.
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
        # Checked whatever lipid_path_handicap says, so a typo in a value is caught at
        # parse time rather than lying dormant until someone turns the handicap on.
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
        if self.lr_warmup_epochs < 0:
            raise ValueError("lr_warmup_epochs must be non-negative")
        if not 0.0 < self.lr_min_factor <= 1.0:
            raise ValueError("lr_min_factor must be in the range (0, 1]")
        if not 0.0 < self.swa_start_frac < 1.0:
            raise ValueError("swa_start_frac must be in the range (0, 1)")
        if self.swa_lr is not None and self.swa_lr <= 0.0:
            raise ValueError("swa_lr must be greater than zero")
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
        # Compatible with the RNA-BAnG modes that CONCATENATE with the ESM3 vector:
        # there the replacement simply takes ESM3's place in the concatenation, so
        # rnabang_with_esm3 + proteinmpnn_replace_esm3 means cat(ProteinMPNN, RNA-BAnG)
        # -- two structure-conditioned descriptions side by side, which is a sensible
        # thing to ask for. Incompatible with the modes that ARE the whole vector
        # (replace_esm3, full_protein_encoder, frozen_node_adapter): two sources cannot
        # both be the sole input, and the frozen adapter additionally asserts the
        # RNA-BAnG width on the tensor it receives.
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
        protein_conv_modes = (
            self.geometric_transformer,
            self.transformer_conv,
            self.gine_conv,
        )
        if sum(protein_conv_modes) > 1:
            raise ValueError(
                "geometric_transformer, transformer_conv and gine_conv are "
                "mutually exclusive"
            )
        if self.geometric_transformer and any(rnabang_modes):
            raise ValueError(
                "geometric_transformer cannot be combined with RNA-BAnG embedding modes"
            )
        if self.rnabang_frozen_node_adapter and self.double_attention:
            raise ValueError(
                "rnabang_frozen_node_adapter cannot be combined with double_attention"
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
            # Only the width gates are optimized on validation; per-block dropout is a
            # train-objective Concrete Dropout, so bilevel needs gate_all_mlp_hidden.
            raise ValueError("bilevel requires gate_all_mlp_hidden (the width gates it optimizes)")
        if self.gate_all_mlp_hidden or self.gate_all_mlp_layers:
            # gate_all_mlp_hidden reuses the structured-sparsity gate machinery
            # (make_gate keys off sparsity_mode / sparsity_lambda) even when
            # structured_sparsity itself is off, so normalize/validate the mode here too.
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
            # common_weights_parts averages its parts, so two per-protein schemes
            # combine into a third that balances neither.
            raise ValueError(
                "protein_balance_weight cannot be combined with protein_class_weight "
                "or protein_class_sqrt_weight: the parts are averaged, and the mean of "
                "two per-protein balancing tables balances neither"
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
        if self.focal_loss and not (
            self.grab_loss or self.loss_type == "cross_entropy"
        ):
            raise ValueError(
                "focal_loss requires grab_loss or loss_type=cross_entropy"
            )
        if self.logit_adjustment_tau < 0.0:
            raise ValueError("logit_adjustment_tau must be non-negative")
        if self.logit_adjustment and self.pu_loss:
            raise ValueError(
                "logit_adjustment is not supported together with pu_loss "
                "(pu_rho already encodes the class prior)"
            )
        if self.logit_adjustment and not (self.grab_loss or self.loss_type == "cross_entropy"):
            raise ValueError(
                "logit_adjustment requires grab_loss or loss_type=cross_entropy"
            )
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
            # Bilinear fusion is multiplicative in both partners, so zeroing one
            # partner collapses the interaction vector to a constant bias -- the
            # single-partner ablation would be meaningless. Keep them separate.
            raise ValueError(
                "bilinear_fusion cannot be combined with lipid_only/protein_only"
            )
        if self.adversarial_grl and (self.lipid_only or self.protein_only):
            # The GRL adversaries penalize per-partner label leakage; zeroing a
            # partner makes its adversary trivial and the ablation meaningless.
            raise ValueError(
                "adversarial_grl cannot be combined with lipid_only/protein_only"
            )
        if self.lipid_path_handicap and (self.lipid_only or self.protein_only):
            # The handicap buys the protein branch a head start over the lipid branch,
            # which needs both to exist. Under protein_only the lipid output is zeroed,
            # so it slows a branch nothing reads; under lipid_only the lipid branch is
            # the whole model, so it is just a lower global learning rate.
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
        if self.chem_adversary and not (self.chem_prior or self.pocket_compat_prior):
            raise ValueError(
                "chem_adversary requires chem_prior and/or pocket_compat_prior -- it "
                "regresses on whichever frozen prior terms are attached, and needs at "
                "least one"
            )
        if (self.compatibility_input or self.compatibility_split_input) and self.bilinear_fusion:
            raise ValueError(
                "compatibility_input/compatibility_split_input cannot be combined with "
                "bilinear_fusion -- the pair values have nowhere well-defined to enter "
                "a bilinear form of exactly two vectors"
            )
        if self.compatibility_input and self.compatibility_split_input:
            raise ValueError(
                "compatibility_input and compatibility_split_input are two forms of the "
                "same quantity -- the difference, and the two halves it is built from. "
                "Running both feeds the model the same information twice and makes the "
                "comparison between the forms unreadable; pick one"
            )
        if self.compat_extent_bins < 1:
            raise ValueError(
                f"compat_extent_bins must be at least 1, got {self.compat_extent_bins}"
            )
        if self.pair_descriptors and self.bilinear_fusion:
            # Same reasoning as compatibility_input/compatibility_split_input above:
            # the descriptor head's pooled vector is concatenated after fusion, which
            # is exactly the single-partner-survivable shortcut bilinear_fusion exists
            # to close.
            raise ValueError(
                "pair_descriptors cannot be combined with bilinear_fusion -- its "
                "pooled vector would be concatenated after the bilinear product, the "
                "same shortcut bilinear_fusion is meant to close"
            )
        if self.pair_descriptors and not self.pocket_descriptors:
            raise ValueError(
                "pair_descriptors requires pocket_descriptors -- the descriptor "
                "head's aromatic/H-bond pair terms read aromatic_share and "
                "apolar_sasa_share off the pocket descriptor tensor"
            )
        if self.pair_descriptors_only and not self.pair_descriptors:
            raise ValueError("pair_descriptors_only requires pair_descriptors")
        if self.pair_descriptors_only and (self.lipid_only or self.protein_only):
            raise ValueError(
                "pair_descriptors_only already zeroes both pooled partners; combining "
                "it with lipid_only/protein_only is redundant and their zeroing order "
                "would be ambiguous"
            )
        if self.descriptors_head and not self.pair_descriptors:
            raise ValueError("descriptors_head requires pair_descriptors")
        if self.descriptors_head:
            # Final_Layer builds only pair_descriptor_head + a small binar under this
            # flag (see its docstring above); none of these have anything to attach to.
            unsupported = [
                name for name in (
                    "bilinear_fusion", "adversarial_grl", "dann_family", "chem_prior",
                    "chem_adversary", "pocket_compat_prior", "compatibility_input",
                    "compatibility_split_input", "attention_pooling", "swe_pooling",
                    "lipid_only", "protein_only", "pair_descriptors_only",
                    "lipid_path_handicap", "double_attention",
                )
                if getattr(self, name)
            ]
            if unsupported:
                raise ValueError(
                    "descriptors_head builds only the descriptor self-attention head "
                    "and a small classifier -- protein1/lipid1/cross_attention1/"
                    "final_layer's usual modules are never built, so these options "
                    "have nothing to attach to: " + ", ".join(unsupported)
                )
        if self.compatibility_split_input:
            named = [n.strip() for n in self.compat_input_parts.split(",") if n.strip()]
            unknown = [n for n in named if n not in ("chain", "clash")]
            if unknown or not named:
                raise ValueError(
                    f"compat_input_parts must name one or both of chain,clash -- got "
                    f"{self.compat_input_parts!r}"
                )
        if (self.chem_lambda_ramp or self.chem_lambda_ramp_by_fit) and not self.chem_adversary:
            raise ValueError("chem_lambda_ramp/chem_lambda_ramp_by_fit require chem_adversary")
        if self.swe_pooling and self.attention_pooling:
            # Both replace the pool_type reduction outright, and Final_Layer has to pick
            # one. Failing here rather than letting a precedence rule decide keeps the
            # label of a run an honest description of what ran.
            raise ValueError("swe_pooling cannot be combined with attention_pooling")
        if self.swe_pooling and self.swe_reference_points < 2:
            raise ValueError("swe_reference_points must be at least 2")
        if self.swe_freeze_reference and not self.swe_pooling:
            raise ValueError("swe_freeze_reference requires swe_pooling")
        if self.lipid_only or self.protein_only:
            # Strict single-partner ablation: cross-attention would leak the
            # hidden partner's context into the surviving branch, so the pooled
            # zeroing in Final_Layer would not isolate a single pathway. Disable
            # it here.
            if self.double_attention:
                raise ValueError(
                    "lipid_only/protein_only cannot be used with double_attention"
                )
            self.cross_attention = False
        # After cross_attention is final: a restriction on cross-attention keys means
        # nothing if there is no cross-attention, and silently keeping the flag on
        # would make the run report claim a restriction the model never applied.
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
        """Return manual or train-count-derived PU rho."""
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
        """Active ESM3 replacement as ``(file suffix, width)``, or None.

        Single source of truth for the loader, which reads the file, and the encoder,
        which sizes its PLM input layer: the two cannot disagree about the width.
        """
        for flag, suffix, dim_attr in FROZEN_PROTEIN_EMBEDDINGS:
            if getattr(self, flag, False):
                return suffix, int(getattr(self, dim_attr))
        return None

    def ramped_lipid_path_weight(self, epoch_index):
        """Gradient scale for the lipid branch at the start of one epoch.

        Constant ``lipid_path_weight`` unless a ramp length is set, in which case it
        interpolates linearly from ``lipid_path_weight`` at epoch 0 to 1.0 at
        ``lipid_path_weight_ramp_epochs``. Linear rather than Ganin's sigmoid because
        this is a head start for the protein branch, not an adversary that has to stay
        weak while representations are noise: the useful part is the early epochs, and
        a sigmoid spends them all near the starting value.

        Assumes ``lipid_path_handicap``; callers gate, as they do for ramped_adv_lambda.
        """
        if not self.lipid_path_weight_ramp_epochs:
            return self.lipid_path_weight
        progress = min(
            1.0, max(0.0, epoch_index / float(self.lipid_path_weight_ramp_epochs))
        )
        return self.lipid_path_weight + progress * (1.0 - self.lipid_path_weight)

    def ramped_adv_lambda(self, progress):
        """Return the gradient-reversal strength for one point in training.

        A constant reversal fights the task gradient from step one, when representations
        are still noise and there is no shortcut to suppress yet; ramping lets the encoder
        fit first and tightens the adversary as it goes. Returns the constant adv_lambda
        when neither ramp flag is set.

        ``adv_lambda_ramp`` uses Ganin & Lempitsky's schedule over *elapsed epochs*:
        lambda(p) = adv_lambda * (2/(1+exp(-10p)) - 1). ``adv_lambda_ramp_by_fit`` keeps
        the same lambda(0)=0 -> lambda(1)=adv_lambda envelope but drives p with *how far
        the model has fit the training data*, and does so linearly, because the sigmoid
        on top of an already-saturating fit signal reaches full strength far too early.

        Which one to prefer is an empirical question with a clear prior: what the ramp is
        supposed to buy is time for the encoder to learn before shortcuts get suppressed,
        and "has it learned yet" is a property of the fit, not of the epoch counter. On a
        run that sits near chance for a third of training and only then starts to
        memorise, an epoch clock spends its whole gentle phase on the plateau and is
        already near full strength exactly when memorisation begins -- backwards. The fit
        clock instead stays near zero while nothing is being learned and tightens as the
        model starts to fit, which is when there is finally a shortcut worth suppressing.
        """
        import math

        if self.adv_lambda_ramp_by_fit:
            return self.adv_lambda * min(max(float(progress), 0.0), 1.0)
        if not self.adv_lambda_ramp:
            return self.adv_lambda
        return self.adv_lambda * (2.0 / (1.0 + math.exp(-10.0 * progress)) - 1.0)

    def ramped_dann_lambda(self, progress):
        """Return the family-DANN reversal strength for one point in training.

        Same envelope as the epoch ramp this replaces -- lambda(0)=0 -> lambda(1)=
        dann_lambda, linear -- so ``dann_lambda_ramp`` keeps its previous behaviour
        exactly; the clamp only guards a caller that hands in an out-of-range progress.
        ``dann_lambda_ramp_by_fit`` changes not the curve but the *clock*: progress comes
        from adv_fit_progress (how far the model has fit the train split) instead of the
        epoch counter, for the reason spelled out in ramped_adv_lambda -- a run that sits
        near chance for a third of training gets a reversal that is already near full
        strength exactly when memorisation begins, which is backwards. Unlike the
        per-partner adversary the family head reads the fused representation, so its
        reversal is the one that can actually reach the joint memorisation, and mistiming
        it is correspondingly more expensive.

        Returns the constant dann_lambda when neither ramp flag is set. by_fit takes
        precedence over the epoch ramp, mirroring adv_lambda_ramp_by_fit.
        """
        if self.dann_lambda_ramp_by_fit or self.dann_lambda_ramp:
            return self.dann_lambda * min(max(float(progress), 0.0), 1.0)
        return self.dann_lambda

    def ramped_chem_lambda(self, progress):
        """Reversal strength for the chemistry adversary. Mirrors ramped_dann_lambda.

        Same reasoning applies unchanged: this reversal reaches the fused representation
        (like dann_family, unlike the per-partner adversary), so ramping it by how far
        training has actually fit rather than by epoch number matters here too --
        pushing against s_chem before the model has learned anything wastes the budget
        on a representation that has nothing to lose yet.
        """
        if self.chem_lambda_ramp_by_fit or self.chem_lambda_ramp:
            return self.chem_lambda * min(max(float(progress), 0.0), 1.0)
        return self.chem_lambda

    def adv_fit_progress(self, train_balanced_accuracy):
        """Map one epoch's train balanced accuracy to ramp progress in [0, 1].

        Balanced accuracy is 0.5 at chance and 1.0 at a perfect fit, so
        (BA - 0.5) / 0.5 reads directly as "how much of the way to memorising the train
        split the model has come" -- the quantity the fit-driven ramp wants. Below chance
        clamps to 0.

        The caller is expected to ratchet this (never let it fall), which is what keeps
        lambda a schedule rather than a feedback loop: lambda changes the very fit it is
        computed from, so a freely falling p could oscillate -- suppress, fit drops,
        suppress less, fit recovers -- and never settle. Monotone p cannot.
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
            # Starts identical to the fixed leakyrelu slope (0.01), then learns
            # its own negative slope per call site (each make_activation() call
            # creates an independent PReLU with its own parameter).
            return torch.nn.PReLU(init=0.01)
        return torch.nn.GELU()

    @property
    def loslis(self):
        """Return supported loss functions by canonical option name."""
        import torch

        return {
            "mse": torch.nn.MSELoss(),
            "cross_entropy": torch.nn.CrossEntropyLoss(),
            "bce": torch.nn.BCELoss(),
        }

    @property
    def loss(self):
        """Return the loss function selected by loss_type."""
        return self.loslis[self.loss_type]

    @property
    def pool_list(self):
        """Return supported graph pooling functions by canonical option name."""
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
            # "gem" has a learnable exponent and is instantiated as a submodule
            # (architecture.final_layer.GeMPool) rather than a stateless
            # function, so Final_Layer never calls the value resolved here.
            "gem": None,
        }

    @property
    def pool(self):
        """Return the graph pooling function selected by pool_type."""
        return self.pool_list[self.pool_type]


def set_config_field(field, cast=lambda value: value):
    """Return a handler that assigns a parsed value to a config field."""
    return lambda config, value: setattr(config, field, cast(value))


def set_config_flag(field, value=True):
    """Return a handler that assigns a fixed value to a config field."""
    return lambda config: setattr(config, field, value)


SIMPLE_BOOL_FLAGS = {
    "third_layers_in_mlps": "third_layers_in_mlps",
    "--third_layers_in_mlps": "third_layers_in_mlps",
    "cross_attention": "cross_attention",
    "--cross_attention": "cross_attention",
    "bilinear_fusion": "bilinear_fusion",
    "--bilinear_fusion": "bilinear_fusion",
    "hard_negative_mining": "hard_negative_mining",
    "--hard_negative_mining": "hard_negative_mining",
    "adversarial_grl": "adversarial_grl",
    "--adversarial_grl": "adversarial_grl",
    "adv_deep": "adv_deep",
    "--adv_deep": "adv_deep",
    "adv_lambda_ramp": "adv_lambda_ramp",
    "--adv_lambda_ramp": "adv_lambda_ramp",
    "adv_lambda_ramp_by_fit": "adv_lambda_ramp_by_fit",
    "--adv_lambda_ramp_by_fit": "adv_lambda_ramp_by_fit",
    "lipid_path_handicap": "lipid_path_handicap",
    "--lipid_path_handicap": "lipid_path_handicap",
    "dann_family": "dann_family",
    "--dann_family": "dann_family",
    "chem_prior": "chem_prior",
    "--chem_prior": "chem_prior",
    "chem_adversary": "chem_adversary",
    "--chem_adversary": "chem_adversary",
    "pocket_compat_prior": "pocket_compat_prior",
    "--pocket_compat_prior": "pocket_compat_prior",
    "compatibility_input": "compatibility_input",
    "--compatibility_input": "compatibility_input",
    "compatibility_split_input": "compatibility_split_input",
    "--compatibility_split_input": "compatibility_split_input",
    "compat_extent_bins": "compat_extent_bins",
    "--compat_extent_bins": "compat_extent_bins",
    "pair_descriptors": "pair_descriptors",
    "--pair_descriptors": "pair_descriptors",
    "pair_descriptors_only": "pair_descriptors_only",
    "--pair_descriptors_only": "pair_descriptors_only",
    "descriptors_head": "descriptors_head",
    "--descriptors_head": "descriptors_head",
    "pair_descriptor_pocket_shares": "pair_descriptor_pocket_shares",
    "--pair_descriptor_pocket_shares": "pair_descriptor_pocket_shares",
    "dann_lambda_ramp": "dann_lambda_ramp",
    "--dann_lambda_ramp": "dann_lambda_ramp",
    "dann_lambda_ramp_by_fit": "dann_lambda_ramp_by_fit",
    "--dann_lambda_ramp_by_fit": "dann_lambda_ramp_by_fit",
    "chem_lambda_ramp_by_fit": "chem_lambda_ramp_by_fit",
    "--chem_lambda_ramp_by_fit": "chem_lambda_ramp_by_fit",
    "balanced_lipid_classes": "balanced_lipid_classes",
    "--balanced_lipid_classes": "balanced_lipid_classes",
    "attention_pooling": "attention_pooling",
    "--attention_pooling": "attention_pooling",
    "attention_pooling_pocket_bias": "attention_pooling_pocket_bias",
    "--attention_pooling_pocket_bias": "attention_pooling_pocket_bias",
    "rank_within_protein": "rank_within_protein",
    "--rank_within_protein": "rank_within_protein",
    "swe_pooling": "swe_pooling",
    "--swe_pooling": "swe_pooling",
    "swe_freeze_reference": "swe_freeze_reference",
    "--swe_freeze_reference": "swe_freeze_reference",
    "use_esm3_v2_embeddings": "use_esm3_v2_embeddings",
    "--use_esm3_v2_embeddings": "use_esm3_v2_embeddings",
    "rnabang_replace_esm3": "rnabang_replace_esm3",
    "--rnabang_replace_esm3": "rnabang_replace_esm3",
    "rnabang_full_protein_encoder": "rnabang_full_protein_encoder",
    "--rnabang_full_protein_encoder": "rnabang_full_protein_encoder",
    "rnabang_with_esm3": "rnabang_with_esm3",
    "--rnabang_with_esm3": "rnabang_with_esm3",
    "rnabang_residual_with_esm3": "rnabang_residual_with_esm3",
    "--rnabang_residual_with_esm3": "rnabang_residual_with_esm3",
    "rnabang_frozen_node_adapter": "rnabang_frozen_node_adapter",
    "--rnabang_frozen_node_adapter": "rnabang_frozen_node_adapter",
    "rnabang_residue_type_embedding": "rnabang_residue_type_embedding",
    "--rnabang_residue_type_embedding": "rnabang_residue_type_embedding",
    "rnabang_edge_current": "rnabang_edge_current",
    "--rnabang_edge_current": "rnabang_edge_current",
    "rnabang_edge_topk_by_area": "rnabang_edge_topk_by_area",
    "--rnabang_edge_topk_by_area": "rnabang_edge_topk_by_area",
    "rnabang_edge_deepsets": "rnabang_edge_deepsets",
    "--rnabang_edge_deepsets": "rnabang_edge_deepsets",
    "rnabang_edge_pna": "rnabang_edge_pna",
    "--rnabang_edge_pna": "rnabang_edge_pna",
    "rnabang_edge_quantiles": "rnabang_edge_quantiles",
    "--rnabang_edge_quantiles": "rnabang_edge_quantiles",
    "rnabang_edge_set_transformer": "rnabang_edge_set_transformer",
    "--rnabang_edge_set_transformer": "rnabang_edge_set_transformer",
    "fast_attention": "fast_attention",
    "--fast_attention": "fast_attention",
    "protein_self_attention": "protein_self_attention",
    "--protein_self_attention": "protein_self_attention",
    "lipid_self_attention": "lipid_self_attention",
    "--lipid_self_attention": "lipid_self_attention",
    "double_attention": "double_attention",
    "--double_attention": "double_attention",
    "single_gat_layer": "single_gat_layer",
    "--single_gat_layer": "single_gat_layer",
    "geometric_transformer": "geometric_transformer",
    "--geometric_transformer": "geometric_transformer",
    "transformer_conv": "transformer_conv",
    "--transformer_conv": "transformer_conv",
    "gine_conv": "gine_conv",
    "--gine_conv": "gine_conv",
    "protein_gine_residual": "protein_gine_residual",
    "--protein_gine_residual": "protein_gine_residual",
    "attention_residual_gates": "attention_residual_gates",
    "--attention_residual_gates": "attention_residual_gates",
    "protein_gat_residual": "protein_gat_residual",
    "--protein_gat_residual": "protein_gat_residual",
    "structured_sparsity": "structured_sparsity",
    "--structured_sparsity": "structured_sparsity",
    "sparsity_gate_ffn": "sparsity_gate_ffn",
    "--sparsity_gate_ffn": "sparsity_gate_ffn",
    "sparsity_gate_heads": "sparsity_gate_heads",
    "--sparsity_gate_heads": "sparsity_gate_heads",
    "sparsity_gate_blocks": "sparsity_gate_blocks",
    "--sparsity_gate_blocks": "sparsity_gate_blocks",
    "sparsity_gate_third_layer": "sparsity_gate_third_layer",
    "--sparsity_gate_third_layer": "sparsity_gate_third_layer",
    "sparsity_gate_cross_attention": "sparsity_gate_cross_attention",
    "--sparsity_gate_cross_attention": "sparsity_gate_cross_attention",
    "gate_all_mlp_hidden": "gate_all_mlp_hidden",
    "--gate_all_mlp_hidden": "gate_all_mlp_hidden",
    "gate_all_mlp_layers": "gate_all_mlp_layers",
    "--gate_all_mlp_layers": "gate_all_mlp_layers",
    "no_ffns": "no_ffns",
    "--no_ffns": "no_ffns",
    "bilevel": "bilevel",
    "--bilevel": "bilevel",
    "bilevel_dropout": "bilevel_dropout",
    "--bilevel_dropout": "bilevel_dropout",
    "protein_disable_pre_sa_mlp": "protein_disable_pre_sa_mlp",
    "--protein_disable_pre_sa_mlp": "protein_disable_pre_sa_mlp",
    "protein_disable_post_sa_mlp": "protein_disable_post_sa_mlp",
    "--protein_disable_post_sa_mlp": "protein_disable_post_sa_mlp",
    "lipid_disable_post_sa_mlp": "lipid_disable_post_sa_mlp",
    "--lipid_disable_post_sa_mlp": "lipid_disable_post_sa_mlp",
    "protein_gat_graph_norm": "protein_gat_graph_norm",
    "--protein_gat_graph_norm": "protein_gat_graph_norm",
    "protein_output_graph_norm": "protein_output_graph_norm",
    "--protein_output_graph_norm": "protein_output_graph_norm",
    "lipid_gat_graph_norm": "lipid_gat_graph_norm",
    "--lipid_gat_graph_norm": "lipid_gat_graph_norm",
    "lipid_output_graph_norm": "lipid_output_graph_norm",
    "--lipid_output_graph_norm": "lipid_output_graph_norm",
    "lipid_first_fragment_only": "lipid_first_fragment_only",
    "--lipid_first_fragment_only": "lipid_first_fragment_only",
    "eval_average_candidates": "eval_average_candidates",
    "--eval_average_candidates": "eval_average_candidates",
    "lipid_isomers": "lipid_isomers",
    "--lipid_isomers": "lipid_isomers",
    "lipid_graph_isomers": "lipid_graph_isomers",
    "--lipid_graph_isomers": "lipid_graph_isomers",
    "bidirectional_edges": "bidirectional_edges",
    "--bidirectional_edges": "bidirectional_edges",
    "prot_pos_bias_per_head": "prot_pos_bias_per_head",
    "--prot_pos_bias_per_head": "prot_pos_bias_per_head",
    "attention_by_pockets": "attention_by_pockets",
    "--attention_by_pockets": "attention_by_pockets",
    "protein_pockets_only": "protein_pockets_only",
    "--protein_pockets_only": "protein_pockets_only",
    "proteinmpnn_replace_esm3": "proteinmpnn_replace_esm3",
    "--proteinmpnn_replace_esm3": "proteinmpnn_replace_esm3",
    "esmif1_replace_esm3": "esmif1_replace_esm3",
    "--esmif1_replace_esm3": "esmif1_replace_esm3",
    "saprot_replace_esm3": "saprot_replace_esm3",
    "--saprot_replace_esm3": "saprot_replace_esm3",
    "protein_extra_node_features": "protein_extra_node_features",
    "--protein_extra_node_features": "protein_extra_node_features",
    "pocket_descriptors": "pocket_descriptors",
    "--pocket_descriptors": "pocket_descriptors",
    "protein_group_weight": "protein_group_weight",
    "--protein_group_weight": "protein_group_weight",
    "double_coldsplit": "double_coldsplit",
    "--double_coldsplit": "double_coldsplit",
    "mixed_coldsplit": "mixed_coldsplit",
    "--mixed_coldsplit": "mixed_coldsplit",
    "protein_balance_weight": "protein_balance_weight",
    "--protein_balance_weight": "protein_balance_weight",
    "protein_class_weight": "protein_class_weight",
    "--protein_class_weight": "protein_class_weight",
    "protein_class_sqrt_weight": "protein_class_sqrt_weight",
    "--protein_class_sqrt_weight": "protein_class_sqrt_weight",
    "grab_loss": "grab_loss",
    "--grab_loss": "grab_loss",
    "pu_loss": "pu_loss",
    "--pu_loss": "pu_loss",
    "focal_loss": "focal_loss",
    "--focal_loss": "focal_loss",
    "logit_adjustment": "logit_adjustment",
    "--logit_adjustment": "logit_adjustment",
    "disable_early_stopping": "disable_early_stopping",
    "--disable_early_stopping": "disable_early_stopping",
    "testmode": "testmode",
    "--testmode": "testmode",
    "type_opt": "type_opt",
    "--type_opt": "type_opt",
    "plmon": "plmon",
    "--plmon": "plmon",
    "plm_sequential_compression": "plm_sequential_compression",
    "--plm_sequential_compression": "plm_sequential_compression",
    "buryon": "buryon",
    "--buryon": "buryon",
    "lr_warmup_cosine": "lr_warmup_cosine",
    "--lr_warmup_cosine": "lr_warmup_cosine",
    "swa": "swa",
    "--swa": "swa",
    "save_checkpoint": "save_checkpoint",
    "--save_checkpoint": "save_checkpoint",
    "save_model": "save_model",
    "--save_model": "save_model",
    "save_dynamics": "save_dynamics",
    "--save_dynamics": "save_dynamics",
    "save_model_in_dynamics": "save_model_in_dynamics",
    "--save_model_in_dynamics": "save_model_in_dynamics",
    "balance_excluded_group_negatives": "balance_excluded_group_negatives",
    "--balance_excluded_group_negatives": "balance_excluded_group_negatives",
    "balance_negatives_by_family": "balance_negatives_by_family",
    "--balance_negatives_by_family": "balance_negatives_by_family",
    "balanced_proteins": "balanced_proteins",
    "--balanced_proteins": "balanced_proteins",
    "balanced_batches": "balanced_batches",
    "--balanced_batches": "balanced_batches",
    "cold_split": "cold_split",
    "--cold_split": "cold_split",
    "lipid_only": "lipid_only",
    "--lipid_only": "lipid_only",
    "protein_only": "protein_only",
    "--protein_only": "protein_only",
}


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
    # Both default True and had only the affirmative flag (SIMPLE_BOOL_FLAGS above),
    # so there was no way to turn either off from the command line -- needed to test
    # whether self-attention earns its capacity on --double_coldsplit, which no run
    # ever has (138/138 double_coldsplit runs have both on; files/interaction_signal_plan.md).
    "no_protein_self_attention": set_config_flag("protein_self_attention", False),
    "--no_protein_self_attention": set_config_flag("protein_self_attention", False),
    "no_lipid_self_attention": set_config_flag("lipid_self_attention", False),
    "--no_lipid_self_attention": set_config_flag("lipid_self_attention", False),
    "no_cross_attention": set_config_flag("cross_attention", False),
    "--no_cross_attention": set_config_flag("cross_attention", False),
    "no_pair_descriptor_pocket_shares": set_config_flag(
        "pair_descriptor_pocket_shares", False
    ),
    "--no_pair_descriptor_pocket_shares": set_config_flag(
        "pair_descriptor_pocket_shares", False
    ),
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
    "--m=": set_config_field("m", int),
    "--final_m=": set_config_field("final_m", int),
    "--dropout=": set_config_field("dropout", float),
    "--final_dropout=": set_config_field("final_dropout", float),
    "--lr=": set_config_field("lr", float),
    "--weight_decay=": set_config_field("weight_decay", float),
    "--hiddim=": set_config_field("hiddim", int),
    "--sparsity_mode=": set_config_field("sparsity_mode", str),
    "--sparsity_lambda=": set_config_field("sparsity_lambda", float),
    "--bilevel_lr=": set_config_field("bilevel_lr", float),
    "--concrete_dropout_reg=": set_config_field("concrete_dropout_reg", float),
    "--concrete_dropout_weight_reg=": set_config_field("concrete_dropout_weight_reg", float),
    "--target_sparsity=": set_config_field("target_sparsity", float),
    "--ep=": set_config_field("ep", int),
    "--checkpoint_window=": set_config_field("checkpoint_window", int),
    "--seed=": set_config_field("seed", int),
    "--label=": set_config_field("label"),
    "--excluded_subgroups=": set_config_field(
        "excluded_subgroups", read_excluded_subgroups
    ),
    "--excluded_groups=": set_config_field("excluded_groups", read_excluded_groups),
    "--negatives_per_positive=": set_config_field("negatives_per_positive", int),
    "--hard_negative_share=": set_config_field("hard_negative_share", float),
    "--eval_candidates_per_pair=": set_config_field(
        "eval_candidates_per_pair", int
    ),
    "--coldsplit_share=": set_config_field("coldsplit_share", float),
    "--lipid_coldsplit=": set_config_field("lipid_coldsplit", read_lipid_coldsplit),
    "--test_group=": set_config_field("test_group", read_test_group),
    "--batch=": set_config_field("batch", int),
    "--num_workers=": set_config_field("num_workers", int),
    "--lipid_fragments_treatment=": set_config_field("lipid_fragments_treatment"),
    "--lipid_first_fragment_only=": set_config_field(
        "lipid_first_fragment_only", read_bool
    ),
    "--protein_pooling=": set_config_field("protein_pooling"),
    "--pocket_attention_sites=": set_config_field(
        "pocket_attention_sites", read_pocket_attention_sites
    ),
    "--tanimoto_weight=": set_config_field("tanimoto_weight", read_bool),
    "--plm_compression_dim=": set_config_field("plm_compression_dim", int),
    "--protein_residue_subsample=": set_config_field("protein_residue_subsample", int),
    "--rnabang_embedding_dim=": set_config_field("rnabang_embedding_dim", int),
    "--proteinmpnn_embedding_dim=": set_config_field("proteinmpnn_embedding_dim", int),
    "--esmif1_embedding_dim=": set_config_field("esmif1_embedding_dim", int),
    "--saprot_embedding_dim=": set_config_field("saprot_embedding_dim", int),
    "--geometric_ipa_chunk_size=": set_config_field(
        "geometric_ipa_chunk_size", int
    ),
    "--mlp_widths=": set_config_field("mlp_widths", read_mlp_widths),
    "--plm_compression_dims=": set_config_field(
        "plm_compression_dims", read_plm_compression_dims
    ),
    "--loss_type=": set_config_field("loss_type"),
    "--act_fn=": set_config_field("act_fn"),
    "--pu_rho=": set_config_field("pu_rho", float),
    "--pu_unlabeled_positive_fraction=": set_config_field(
        "pu_unlabeled_positive_fraction", float
    ),
    "--pu_beta=": set_config_field("pu_beta", float),
    "--pu_gamma=": set_config_field("pu_gamma", float),
    "--pu_tau=": set_config_field("pu_tau", float),
    "--pu_loss_cap=": set_config_field("pu_loss_cap", float),
    "--focal_gamma=": set_config_field("focal_gamma", float),
    "--logit_adjustment_tau=": set_config_field("logit_adjustment_tau", float),
    "--adv_weight=": set_config_field("adv_weight", float),
    "--adv_lambda=": set_config_field("adv_lambda", float),
    "--lipid_path_weight=": set_config_field("lipid_path_weight", float),
    "--lipid_path_weight_ramp_epochs=": set_config_field(
        "lipid_path_weight_ramp_epochs", int
    ),
    "--dann_weight=": set_config_field("dann_weight", float),
    "--dann_lambda=": set_config_field("dann_lambda", float),
    "--chem_weight=": set_config_field("chem_weight", float),
    "--chem_lambda=": set_config_field("chem_lambda", float),
    "--chem_neighbours=": set_config_field("chem_neighbours", int),
    "--compat_extent_bins=": set_config_field("compat_extent_bins", int),
    "--compat_input_parts=": set_config_field("compat_input_parts"),
    "--dann_class_conditional=": set_config_field("dann_class_conditional", read_bool),
    "--pool_type=": set_config_field("pool_type"),
    "--swe_reference_points=": set_config_field("swe_reference_points", int),
    "--HEADS=": set_config_field("HEADS", int),
    "--lr_warmup_epochs=": set_config_field("lr_warmup_epochs", int),
    "--lr_min_factor=": set_config_field("lr_min_factor", float),
    "--swa_start_frac=": set_config_field("swa_start_frac", float),
    "--swa_lr=": set_config_field("swa_lr", float),
}


def apply_value_handler(config, argument):
    """Apply a name=value handler and report whether the argument was handled."""
    for prefix, handler in VALUE_HANDLERS.items():
        if argument.startswith(prefix):
            handler(config, read_value(argument))
            return True

    return False


def read_named_configuration(argv):
    """Parse named command-line options into a validated ModelConfig."""
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
    """Read configuration from the supplied arguments or the process command line."""
    if argv is None:
        argv = sys.argv

    return read_named_configuration(argv)
