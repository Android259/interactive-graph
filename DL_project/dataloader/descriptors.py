"""Descriptor names and the shared descriptor_catalog_input column order.

Used by --descriptor_heads, --protein_descriptors, --lipid_descriptors, and
--deepclip_protein_gate.

The catalog follows Lipovsky et al., "Systematic analyses of lipid mobilization
by human lipid transfer proteins" (Nature 2025, s41586-025-10040-y), the source
of the interaction measurements. It covers chain length, unsaturation,
aromatic contacts, head-group hydrogen bonding, and pocket occupancy.
Two reported interactions require a bound pose. This project has no docking
pipeline for the ~9905-row grid, so it uses 2D structures and pocket tables.
As in pocket_lipid_compatibility, ambiguous candidates are not assigned a pose.
Pair terms use products or differences of pocket-wide properties as proxies
for residue-specific contacts.
"""
import functools
import os

import numpy

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# Import candidates_for_row inside descriptor_values_by_row to avoid a cycle:
# pocket_lipid_compatibility -> protein_graph_builder -> this module.

# Shared catalog for knn_model.py --features and --descriptor_heads.
LIPID_DESCRIPTOR_NAMES = (
    "chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2",
    "logp", "tpsa", "molar_refractivity", "rotatable_bond_count",
    "aromatic_ring_count", "ring_count",
    # Tail-only measures were added after checking head-group eta^2:
    # tail_double_bonds 0.31, tail_length_mean 0.34, tpsa 0.98, hbond 0.99.
    # They form the chain branch proposed in sections 7f-7h and 7q of
    # files/results/lipid_coldsplit_architecture_direction.md.
    "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
    "tail_unsaturation_density", "tail_double_bond_position",
    "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
    # experimental_lipid_volume uses data/Lipid_Volumes.csv (_LIPID_MEASURES).
    # It was added after a coverage check, without the eta^2 checks used for tail_*.
    # About 30% of candidates resolve, but species averaging in
    # chemistry_prior._lipid_descriptor_table covers 283/283 species across both labels.
    # The protein-identity eta^2 check has not been run for this descriptor.
    "experimental_lipid_volume",
)
# See pair_descriptor_value below for what each one actually computes.
PAIR_DESCRIPTOR_NAMES = (
    "occupancy", "chain_extent_gap", "aromatic_contact", "hbond_match", "volume_fit",
    "buriedness_match", "depth_bulk_match", "hydropathy_chain_match",
    "aromatic_contact_min", "hbond_match_min", "tail_elongation_fit",
    "hydropathy_rim_match", "elongation_shape_match", "flatness_shape_match",
)
# --zscore behavior follows each formula's registered kind: product,
# bottleneck, physical, or ratio (compute_descriptors._pair_measure).
# pair_names_of_kind derives the sets; do not duplicate them here.
# See chemistry_prior.feature_similarity for their use.

# Protein descriptors come from data/protein_descriptors.csv, one row per
# protein, computed by compute_descriptors._PROTEIN_MEASURES.
# Raw sizes and residue counts are excluded: they can identify the fold in a cold split.
PROTEIN_DESCRIPTOR_NAMES = (
    # Cavity: scale-free size, shape, enclosure/depth quantiles, chemistry shares.
    "pocket_residue_share", "pocket_sasa_share", "pocket_volume_per_sasa",
    "pocket_extent", "pocket_elongation", "pocket_flatness",
    "ev14_q50", "buriedness_q50", "depth_q10",
    "apolar_sasa_share", "aromatic_share", "hydropathy_core",
    "hydropathy_rim", "ev28_q10", "aromatic_share_rim",
    "hydropathy_mean", "ev14_q10", "pocket_extent_lambda_sqrt",
    "pocket_elongation_lambda_sqrt", "pocket_flatness_lambda_sqrt", "ev14_q90",
    "ev28_q50", "ev28_q90", "ev56_q10",
    "buriedness_q10", "buriedness_q90", "depth_q50",
    "depth_q90", "aromatic_share_core",
    # Pocket residue-class shares, split at the burial median, and the cavity.
    "basic_share_core", "basic_share_rim",
    "acidic_share_core", "acidic_share_rim",
    "polar_share_core", "polar_share_rim",
    "hbond_donor_share_core", "hbond_donor_share_rim",
    "hbond_acceptor_share_core", "hbond_acceptor_share_rim",
    "pocket_free_volume", "pocket_packing_density",
    # Derived as 1 - apolar_sasa_share.
    "polar_share",
)

# Base names accepted by --descriptor_heads and NamedDescriptorHead.
# Names may be raw or use <name>_coarse=<spec> (parse_descriptor_token).
# extent is train-fit-coarsened pocket_extent; tail_count is unchanged.
# Other entries are raw pair_descriptors.py or pocket_descriptor() values.
# Raw pocket_extent remains available as an opt-in identity-leak probe.
# aromatic_share_coarse and polar_share_coarse are token aliases, not catalog names;
# DEFAULT_COARSE_SPECS maps them to base names and train-fit quantile bins.
# They replace fixed thirds, which put 34/35 proteins into one aromatic-share bin.
DESCRIPTOR_CATALOG = (
    LIPID_DESCRIPTOR_NAMES  # now includes "tail_count", "npr1", "npr2" too
    + ("extent",)
    + PROTEIN_DESCRIPTOR_NAMES
    + PAIR_DESCRIPTOR_NAMES
)

# Shares are bounded in [0, 1], so fixed bins can use that domain without
# fitting data. Other descriptors use the training [min, max] range;
# see parse_descriptor_token and Dataloader.fit_coarse_edges.
# Derive membership from names: a manual list once omitted aromatic_share_rim
# while including aromatic_share_core, giving the two different bin domains.
# Keep the _share naming convention. pocket_packing_density is also bounded
# (the cavity's free hull fraction); pocket_free_volume is unbounded angstrom^3.
BOUNDED_SHARE_DESCRIPTOR_NAMES = tuple(
    name for name in DESCRIPTOR_CATALOG if "share" in name
) + ("pocket_packing_density",)

# Default count for coarse=quantiles without :N. Keep the old three-band count.
DEFAULT_QUANTILE_BINS = 3


class CoarseSpec:
    """Bin count and edge mode for a <name>_coarse=<spec> token.

    fixed: equal-width bins over [0, 1] for BOUNDED_SHARE_DESCRIPTOR_NAMES,
    otherwise over the training range.
    quantiles: train-fit numpy.quantile edges passed to
    pocket_lipid_compatibility.coarsen_to_levels, as for Dataloader.coarse_extent.
    Both modes support any base descriptor and bin count.
    """

    __slots__ = ("mode", "bins")

    def __init__(self, mode, bins):
        self.mode = mode
        self.bins = bins

    def __eq__(self, other):
        return (
            isinstance(other, CoarseSpec) and self.mode == other.mode
            and self.bins == other.bins
        )

    def __hash__(self):
        return hash((self.mode, self.bins))

    def __repr__(self):
        return f"CoarseSpec({self.mode!r}, {self.bins!r})"


_COARSE_SUFFIX = "_coarse="

# Use three quantile bins when these descriptors have no explicit specification.
# Fixed thirds put most observed values in one bin.
DEFAULT_COARSE_SPECS = {
    "aromatic_share_coarse": CoarseSpec("quantiles", 3),
    "polar_share_coarse": CoarseSpec("quantiles", 3),
}


class UnknownDescriptorName(ValueError):
    """A descriptor token naming a base name the catalog does not have."""


# parse_descriptor_list skips removed names and records them here.
# Run logs and test_metrics report them so older arg-file grids can continue.
UNKNOWN_DESCRIPTOR_NAMES: list[str] = []


def parse_descriptor_token(token):
    """Parse one --descriptor_heads token into (base_name, coarse_spec_or_None).

    name: use the value directly. Bare aromatic_share_coarse and
    polar_share_coarse use DEFAULT_COARSE_SPECS.
    name_coarse=N: N equal-width bins (N >= 2).
    name_coarse=quantiles[:N]: train-fit quantile bins; N defaults to
    DEFAULT_QUANTILE_BINS.

    Fixed bins span [0, 1] for bounded shares, or the training range otherwise.
    Unknown names and invalid specifications raise ValueError.
    """
    name, _, spec = token.partition(_COARSE_SUFFIX)
    if not spec:
        if token in DEFAULT_COARSE_SPECS:
            base = token[: -len("_coarse")]
            return base, DEFAULT_COARSE_SPECS[token]
        if token not in DESCRIPTOR_CATALOG:
            raise UnknownDescriptorName(
                f"Unknown descriptor name(s): ['{token}']. Known: {DESCRIPTOR_CATALOG} "
                f"(plus {tuple(DEFAULT_COARSE_SPECS)} bare)"
            )
        return token, None
    if name not in DESCRIPTOR_CATALOG:
        raise UnknownDescriptorName(
            f"Unknown descriptor name(s): ['{name}']. Known: {DESCRIPTOR_CATALOG}"
        )
    if spec == "quantiles":
        return name, CoarseSpec("quantiles", DEFAULT_QUANTILE_BINS)
    if spec.startswith("quantiles:"):
        count = spec[len("quantiles:"):]
        if not count.isdigit() or int(count) < 2:
            raise ValueError(
                f"Bad coarse spec {token!r}: quantiles:N needs an integer N >= 2"
            )
        return name, CoarseSpec("quantiles", int(count))
    if spec.isdigit() and int(spec) >= 2:
        return name, CoarseSpec("fixed", int(spec))
    raise ValueError(
        f"Bad coarse spec {token!r}: expected <name>_coarse=<N> (N >= 2), "
        f"<name>_coarse=quantiles, or <name>_coarse=quantiles:<N>"
    )


def canonical_descriptor_token(name, spec):
    """Return one canonical token for (base_name, coarse_spec_or_None).

    For example, aromatic_share_coarse=quantiles and
    aromatic_share_coarse=quantiles:3 (DEFAULT_QUANTILE_BINS) name the same column
    and NamedDescriptorHead token, so they are not computed twice.
    """
    if spec is None:
        return name
    if spec.mode == "quantiles":
        return f"{name}{_COARSE_SUFFIX}quantiles:{spec.bins}"
    return f"{name}{_COARSE_SUFFIX}{spec.bins}"


def parse_descriptor_list(value):
    """Return canonical tokens from a comma-separated string.

    Use the same separator as knn_model.py --features and --excluded_groups.
    """
    tokens = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            name, spec = parse_descriptor_token(raw)
        except UnknownDescriptorName:
            if raw not in UNKNOWN_DESCRIPTOR_NAMES:
                UNKNOWN_DESCRIPTOR_NAMES.append(raw)
            continue
        tokens.append(canonical_descriptor_token(name, spec))
    return tuple(tokens)


def parse_descriptor_heads(value):
    """Return heads as tuples of canonical tokens from --descriptor_heads.

    Separate heads with "/"; "|" and ";" require shell quoting in arg files.
    Skip empty heads. args_file_lib.sh joins wrapped lines with commas, so
    "a,b/" followed by "c,d" arrives as "a,b/,c,d".
    """
    heads = (parse_descriptor_list(part) for part in value.split("/"))
    return tuple(head for head in heads if head)


def resolve_requested_tokens(*raw_lists):
    """Return the sorted union of canonical tokens from comma-separated lists.

    All descriptor_catalog_input builders and consumers use this column order.
    Passing the same lists gives the same order without passing it separately.
    """
    union = set()
    for raw in raw_lists:
        union |= set(parse_descriptor_list(raw))
    return tuple(sorted(union))


def descriptor_catalog_only(config):
    """Return whether the model reads only descriptor_catalog_input.

    --descriptor_mlp uses DescriptorMLPHead instead of NamedDescriptorHead,
    with the same --descriptor_heads input and lean loading/preassembly path.
    """
    return bool((
            getattr(config, "descriptors_head", False)
            or getattr(config, "descriptor_mlp", False))
        and getattr(config, "descriptor_heads", "")
    )


def full_catalog_order(config):
    """Return the shared descriptor_catalog_input column order for this config.

    Combine --descriptor_heads, --protein_descriptors, --lipid_descriptors, and
    --deepclip_protein_gate through resolve_requested_tokens. All heads, node
    broadcasts (protein_encoder.py/lipid_encoder.py), and deepclip.py gates use it.
    """
    return resolve_requested_tokens(
        getattr(config, "descriptor_heads", "").replace("/", ","),
        getattr(config, "protein_descriptors", ""),
        getattr(config, "lipid_descriptors", ""),
        getattr(config, "deepclip_protein_gate", ""),
    )


def resolve_similarity_feature_names(*raw_lists):
    """Return sorted, unique base names, dropping coarse-bin specifications.

    Accept comma-separated lists and whole --descriptor_heads values,
    where "/" also separates tokens.
    """
    names = set()
    for value in raw_lists:
        for raw in value.replace("/", ",").split(","):
            raw = raw.strip()
            if not raw:
                continue
            name, _ = parse_descriptor_token(raw)
            names.add(name)
    return tuple(sorted(names))
