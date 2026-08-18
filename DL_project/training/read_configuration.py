import sys
from dataclasses import dataclass, field


# Width of the cavity descriptor --pocket_descriptors appends to the fused pair vector.
# The list itself is POCKET_DESCRIPTOR_NAMES in dataloader/protein_graph_builder.py,
# which checks the descriptor it builds against this number and names the mismatch;
# change the list and this changes with it (files/pocket_shape_descriptors.md too).
POCKET_DESCRIPTOR_COUNT = 13

POOL_TYPES = ("add", "max", "mean", "add_max", "gem")
LOSS_TYPES = ("mse", "cross_entropy", "bce")
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
    excluded_subgroups: list = field(default_factory=list)
    balance_excluded_group_negatives: bool = False
    balance_negatives_by_family: bool = False
    balanced_proteins: bool = False
    balanced_batches: bool = False
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
    lipid_fragments_treatment: str = "concat"
    protein_pooling: str = "attention_pos_bias"
    
    lipid_concat: bool = False
    lipid_random_choice: bool = True
    lipid_fragments_mask: bool = False
    # The ";"-separated SMILES of a row are candidate structures for one measured lipid
    # species (sn-positional / double-bond isomers the spectrum cannot separate), and
    # the embedding path used to keep only the first of them regardless of
    # lipid_fragments_treatment -- which made all three treatments the same run. This
    # flag is that behaviour, kept on by default so earlier runs stay reproducible;
    # turn it off (no_lipid_first_fragment_only) to let the chosen treatment actually
    # see the whole candidate set. It composes with every treatment: with it on,
    # concat and fragments_mask degenerate to the single first candidate and
    # random_choice always draws that same one. It governs the embedding path only;
    # the lipid_graph_isomers path has always used every candidate.
    lipid_first_fragment_only: bool = True
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
    pool_type: str = "max"
    # Learned attention pooling (one learnable query per partner) instead of the fixed
    # pool_type reduction: out = sum_i softmax_i(w·x_i) x_i over each graph's nodes -- a
    # content-weighted readout rather than a flat mean/max. attention_pooling_pocket_bias
    # adds a learnable scalar to protein pooling logits for pocket residues, so pooling
    # can prefer the binding site during training (requires attention_pooling).
    attention_pooling: bool = False
    attention_pooling_pocket_bias: bool = False
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
    "dann_lambda_ramp": "dann_lambda_ramp",
    "--dann_lambda_ramp": "dann_lambda_ramp",
    "dann_lambda_ramp_by_fit": "dann_lambda_ramp_by_fit",
    "--dann_lambda_ramp_by_fit": "dann_lambda_ramp_by_fit",
    "balanced_lipid_classes": "balanced_lipid_classes",
    "--balanced_lipid_classes": "balanced_lipid_classes",
    "attention_pooling": "attention_pooling",
    "--attention_pooling": "attention_pooling",
    "attention_pooling_pocket_bias": "attention_pooling_pocket_bias",
    "--attention_pooling_pocket_bias": "attention_pooling_pocket_bias",
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
    "--dann_class_conditional=": set_config_field("dann_class_conditional", read_bool),
    "--pool_type=": set_config_field("pool_type"),
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
