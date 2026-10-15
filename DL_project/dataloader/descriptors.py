"""The descriptor catalog: every name a --descriptor_heads / --protein_descriptors /
--lipid_descriptors / --deepclip_protein_gate token may spell, and how a request for them
is resolved into the one column order of Dataloader.py's descriptor_catalog_input.

Motivated by Lipovsky et al., "Systematic analyses of lipid mobilization by human lipid
transfer proteins" (Nature 2025, s41586-025-10040-y), whose measured LTP-lipid complexes
this project's interaction table draws on: acyl-chain-length and unsaturation
preferences, aromatic clusters contacting acyl double bonds, headgroup hydrogen bonding
and a pocket-occupancy ratio between bound ligand and cavity volume. Two of those need a
bound POSE, which this project has no docking pipeline to produce and would have to
fabricate for every candidate of the ~9905-row grid, so the catalog carries only what 2D
structure and the pocket tables give (same discipline as
pocket_lipid_compatibility.longest_acyl_chain -- no 3D embedding of stereo-ambiguous
candidates). The pair terms are multiplicative or difference proxies built from
pocket-wide chemistry shares instead of a specific residue-double-bond contact.
"""
import functools
import os

import numpy

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# candidates_for_row: imported lazily, inside descriptor_values_by_row, not here --
# dataloader/pocket_lipid_compatibility.py eagerly imports names FROM
# dataloader/graphs_builders/protein_graph_builder.py, which in turn eagerly imports
# PROTEIN_DESCRIPTOR_NAMES from THIS module (see the bottom of protein_graph_builder.py)
# -- an eager import here would complete the triangle into a circular import.

# The full descriptor catalog analysis/baselines/knn_model.py's --features and every
# --descriptor_heads token draw on, named together in one place.
LIPID_DESCRIPTOR_NAMES = (
    "chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2",
    "logp", "tpsa", "molar_refractivity", "rotatable_bond_count",
    "aromatic_ring_count", "ring_count",
    # Tail-only quantities, promoted from CANDIDATE_LIPID_DESCRIPTOR_NAMES once their
    # eta^2 against head-group class had actually been read (files/results/lipid_coldsplit_
    # architecture_direction.md sections 7f-7h): they are the least class-specific of
    # everything measured -- tail_double_bonds 0.31 and tail_length_mean 0.34 against
    # tpsa 0.98 and hbond 0.99 -- and they are the chain half of the two-branch split
    # section 7q proposes. Measuring first, wiring second, was the point of keeping them
    # out until now.
    "tail_length_asymmetry", "tail_length_mean", "tail_double_bonds",
    "tail_unsaturation_density", "tail_double_bond_position",
    "tail_logp", "tail_molar_refractivity", "tail_heavy_atoms",
    # experimental_lipid_volume (data/Lipid_Volumes.csv lookup, see its own comment
    # above _MEASURES): promoted straight in, unlike the tail_* block above, which
    # waited on an eta^2-against-head-group-class measurement first. What was
    # actually checked here is coverage, not eta^2 -- at the CANDIDATE level (a raw
    # SmileFragment/SmileGlobal entry) only ~30% resolve, but chemistry_prior.
    # _lipid_descriptor_table (this name's only consumer through --descriptor_heads/
    # feature_similarity) averages over every resolved candidate PER SPECIES the
    # same way it does for every other name here, and at that grain coverage is
    # 100% (283/283 distinct FullIdentityOfLipid species, positive and negative rows
    # alike -- verified directly against the current interaction table). The
    # eta^2-against-protein-identity check the tail_* promotion ran has NOT been run
    # for this one yet.
    "experimental_lipid_volume",
)
# See pair_descriptor_value below for what each one actually computes.
PAIR_DESCRIPTOR_NAMES = (
    "occupancy", "chain_extent_gap", "aromatic_contact", "hbond_match", "volume_fit",
    "buriedness_match", "depth_bulk_match", "hydropathy_chain_match",
    "aromatic_contact_min", "hbond_match_min", "tail_elongation_fit",
    "hydropathy_rim_match", "elongation_shape_match", "flatness_shape_match",
)
# occupancy/chain_extent_gap are signed differences of a single PHYSICAL quantity
# (both sides converted to angstrom, chain via chain_length_angstrom) -- standardising
# their inputs would replace that physical "does the cavity reach as far as the
# chain" comparison with an abstract standard-deviations-apart one, so --zscore
# (analysis/baselines/knn_model.py) never touches them. The other six multiply two
# DIFFERENT-UNIT quantities together (a share/ratio/burial statistic against a lipid
# count) -- their relative contribution to the product is whatever their raw scales
# happen to be, not a principled 50/50 split, which --zscore fixes by standardising
# both sides before multiplying. See dataloader.chemistry_prior.feature_similarity's
# zscore handling. tail_elongation_fit is a THIRD, separate category -- a ratio, not
# a product or a difference -- see its own entry in pair_descriptor_value for why
# --zscore does not touch it either.
MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES = (
    "aromatic_contact", "hbond_match", "volume_fit", "buriedness_match",
    "depth_bulk_match", "hydropathy_chain_match",
    "hydropathy_rim_match", "elongation_shape_match", "flatness_shape_match",
)
# aromatic_contact/hbond_match's min-variants: min(A, B) instead of A * B is a
# BOTTLENECK reading -- the pair scores no higher than its weaker side, so a pocket
# that is entirely aromatic cannot compensate for a chain with zero unsaturation the
# way a product can (a huge A times a tiny nonzero B can still land mid-range). Unlike
# --zscore (MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES above), which only standardises when
# the flag is passed, min(A, B) is not comparing anything unless A and B are already
# on the same scale -- with raw values, whichever side happens to have the smaller
# native range would win the min every time regardless of which is actually the
# limiting factor, which is not a bottleneck reading at all, just a units artefact.
# So these two always read standardised protein/lipid values, independent of
# --zscore -- see feature_similarity's own handling.
MIN_PAIR_DESCRIPTOR_NAMES = ("aromatic_contact_min", "hbond_match_min")

# One descriptor of the binding cavity per protein, in this order. Aggregated over the
# pocket residues of coarse_graph_nodes.csv plus the pocket atom coordinates of
# pocketness.pdb, by dataloader/graphs_builders/protein_graph_builder.py's pocket_descriptor().
# Documented in files/reference/pocket_shape_descriptors.md, which is to be updated in the same
# commit as any change here. Defined here (not in protein_graph_builder.py, which
# imports it back as POCKET_DESCRIPTOR_NAMES) so the whole descriptor catalog --
# lipid, protein, pair -- names in one file; the VALUES are still computed in
# protein_graph_builder.py, tied to that file's residue-table/Voronota-column
# machinery and the live ProteinGraphBuilder cache, not duplicated here.
#
# The previous set was 13 sums or means over pocket residues and one maximum, which
# cannot express shape at all: a long narrow channel and a round bowl with the same
# total surface and the same mean burial produced identical numbers, though they hold
# different lipids. Three of its entries were also measuring nothing of their own --
# pocket "volume" is the summed Voronoi cell volume of the LINING RESIDUES, not the
# cavity, and since a residue's cell varies by only 21% around 198 A^3 the sum tracks
# the residue count at rho = 0.993; ev56 and the upper half of ev28 saturate at 2.0 for
# nearly every residue of every protein, so as features they had no variance to give.
# Measured on 35 proteins against the mean acyl chain length their positives carry,
# controlling for protein size: volume +0.168 and residue count +0.161 (indistinguishable
# from each other, as duplicates should be), against pocket_volume_per_sasa -0.475 and
# pocket_gyration +0.443 from the shape entries below. No run had ever broadcast this
# tensor onto protein nodes, so replacing the set costs no comparability.
PROTEIN_DESCRIPTOR_NAMES = (
    # Scale-free size. The raw sizes are deliberately gone: on a cold-family split
    # protein size stands in for fold, which is the shortcut the split withholds.
    "pocket_residue_share",
    "pocket_sasa_share",
    # Shape. Lining volume over open surface is the closest thing to "how narrow is
    # it" these columns can express; the rest come from the cavity's own axes.
    "pocket_volume_per_sasa",
    "pocket_extent",           # how far the cavity runs, A -- an acyl chain's limit
    "pocket_elongation",       # tube vs bowl
    "pocket_flatness",         # slit vs tube
    # Enclosure and depth as medians rather than means, and the shallow decile of
    # depth, which measured stronger than either mean it replaces.
    "ev14_q50",
    "buriedness_q50",
    "depth_q10",
    # Chemistry, split where the two questions differ: head-group recognition happens
    # at the mouth, chain packing in the depth, and one average of both answers
    # neither. Aromatics are counted separately because Kyte-Doolittle cannot express
    # them -- it scores Phe with the aliphatics and Trp near zero.
    "apolar_sasa_share",
    "aromatic_share",
    "hydropathy_core",
    "hydropathy_rim",
    # Appended, not interleaved -- dataloader/graphs_builders/protein_graph_builder.py's
    # pocket_descriptor() has the full reasoning. Promoted from the research-only
    # catalog by files/pocket_shape_descriptors.md section 7's eta^2 check.
    "ev28_q10",
    "aromatic_share_rim",
    # Third promotion, same section 7 catalog: whole-pocket mean hydropathy (unlike
    # hydropathy_core/hydropathy_rim above, not split by the burial median). eta^2
    # against family is 0.611 -- well above the family-neutral floor, so this one is
    # NOT part of POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES and is not a safe default
    # under --double_coldsplit/--protein_edge_*'s cross-family generalisation test.
    # Kept anyway: under --lipid_coldsplit the protein axis is not the held-out one
    # (files/results/lipid_coldsplit_architecture_direction.md section 4), so family eta^2 is
    # not a leak risk there, and section 7's partial-correlation ranking against
    # head-group-class diversity placed it ahead of the already-promoted ev28_q10.
    "hydropathy_mean",
    # Fourth promotion, same batch: shallow decile of the ev14 enclosure column (the
    # ev28 analogue already has both its q10 and q50 in production -- ev14 previously
    # had only q50). eta^2=0.238, right at the no-structure floor (~0.235-0.25) --
    # unlike hydropathy_mean above, this one WOULD be family-neutral-safe, but it is
    # new alongside hydropathy_mean in the same session so it is appended here rather
    # than inserted into POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES sight-unseen; add it
    # there once a real run confirms it behaves as advertised.
    "ev14_q10",
    # The three cavity-axis entries computed the OTHER way: sqrt(eigenvalue) ratios on a
    # MinCovDet robust covariance, instead of the percentile-span ratios pocket_extent/
    # pocket_elongation/pocket_flatness above use. Not replacements -- both formulas are
    # nameable, and an arg file picks one by name. Measured in
    # files/results/pocket_shape_metric_comparison.md over seven variants: against the
    # head-group-class target (the one family does not determine, eta^2 0.22),
    # pocket_elongation_lambda_sqrt is the only variant of the seven whose sign holds in
    # all three slices -- CRAL-TRIO +0.115, lipocalin +0.312, pooled +0.401
    # [0.061, 0.658] -- while the span-based pocket_elongation reverses inside both
    # families (-0.071/-0.156 against pooled +0.288), the between-family artifact pattern
    # section 4a of files/reference/pocket_shape_descriptors.md used to reject
    # pocket_volume_per_sasa. eta^2 against family: extent 0.737, elongation 0.479,
    # flatness 0.256 -- all above the 0.235 floor, so none of the three is in
    # POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES (dataloader/graphs_builders/protein_graph_builder.py); under
    # --double_coldsplit they are a deliberate opt-in, not a vetted-safe default. Note
    # the two formulas disagree in OPPOSITE directions per entry: the lambda_sqrt
    # elongation is MORE family-correlated than its span twin (0.479 vs 0.189) and the
    # lambda_sqrt flatness LESS (0.256 vs 0.481).
    "pocket_extent_lambda_sqrt",
    "pocket_elongation_lambda_sqrt",
    "pocket_flatness_lambda_sqrt",
    # Fifth batch, promoted out of the research catalog once pocket_descriptor stopped
    # being a positional tuple: the deep end of every enclosure/depth distribution
    # whose shallow decile or median was already in production, the ev56 column that
    # had neither, and the core half of the aromatic share whose rim half was promoted
    # alone in the second batch.
    "ev14_q90",
    "ev28_q50",
    "ev28_q90",
    "ev56_q10",
    "ev56_q50",
    "ev56_q90",
    "buriedness_q10",
    "buriedness_q90",
    "depth_q50",
    "depth_q90",
    "aromatic_share_core",
)

# Not raw pocket_descriptor() output, so not in PROTEIN_DESCRIPTOR_NAMES itself:
#   polar_share            : 1 - apolar_sasa_share.
#   aromatic_share_coarse,
#   polar_share_coarse     : aromatic_share/polar_share banded into one of 3 fixed
#                             (not train-fit) thirds. Kept for analysis/baselines/
#                             knn_model.py's own --features catalog; --descriptor_heads
#                             tokens use the <name>_coarse=<spec> syntax below instead.
PROTEIN_DERIVED_DESCRIPTOR_NAMES = ("polar_share", "aromatic_share_coarse", "polar_share_coarse")

# Pocket CHEMISTRY and CAVITY descriptors. Protein-side and nameable through
# --descriptor_heads/--protein_descriptors like everything in PROTEIN_DESCRIPTOR_NAMES
# above, but kept out of that tuple. Computed by
# dataloader/graphs_builders/protein_graph_builder.py's pocket_chemistry_descriptor() and merged into
# the per-protein table by dataloader/chemistry_prior.py's protein_descriptor_table,
# exactly the way PROTEIN_DERIVED_DESCRIPTOR_NAMES already is.
#
# Same twelve names, same formulas and same residue-class membership as
# training/pair_baseline_common.py's POCKET_CHEMISTRY_NAMES + POCKET_CAVITY_NAMES --
# that equality is the point. The Kron-RLS side saw these first and searched 16369
# subsets over them (results/tables/cron_test_metrics/exhaustive_protein_side_search.csv); four --
# basic_share_core, pocket_free_volume, basic_share_rim, hbond_donor_share_core --
# appear in nearly every leading combination there, and the winning set beats the
# seven-descriptor incumbent it was asked to defend (AUC_within_protein 0.6888 vs
# 0.6681, the incumbent ranking 1106th of 16369). A set found there can now be named
# here without re-spelling it. Motivation for the names themselves:
# files/binding_determinants_literature_and_feature_proposals.md.
POCKET_CHEMISTRY_DESCRIPTOR_NAMES = (
    "basic_share_core", "basic_share_rim",
    "acidic_share_core", "acidic_share_rim",
    "polar_share_core", "polar_share_rim",
    "hbond_donor_share_core", "hbond_donor_share_rim",
    "hbond_acceptor_share_core", "hbond_acceptor_share_rim",
    "pocket_free_volume", "pocket_packing_density",
)

# --descriptor_heads (training/read_configuration.py, architecture/named_descriptor_head.py):
# every BASE name a live NamedDescriptorHead can be built from -- either bare, or
# coarsened via the <name>_coarse=<spec> syntax below (parse_descriptor_token). "extent"
# is Dataloader's own train-fit-coarsened, leak-safe pocket_extent; "tail_count" is
# acyl_chain_count. Everything else named here is its RAW dataloader/pair_
# descriptors.py or pocket_descriptor() value -- in particular "pocket_extent"
# (inside PROTEIN_DESCRIPTOR_NAMES) is the SAME cavity size "extent" coarsens,
# deliberately left nameable raw too (an explicit, opt-in leak probe, not a
# vetted-safe default). Distinct from
# PROTEIN_DERIVED_DESCRIPTOR_NAMES (still used by analysis/baselines/knn_model.py's own,
# unrelated --features catalog): "aromatic_share_coarse"/"polar_share_coarse" are
# NOT in this catalog, only "polar_share" is -- the new <name>_coarse=<spec> syntax
# replaces that fixed-3-band scheme for this system (see its own docstring for why:
# measured directly on this project's 35 proteins, aromatic_share never leaves the
# scheme's own first fixed third, so 34 of 35 proteins collapsed onto one value).
DESCRIPTOR_CATALOG = (
    LIPID_DESCRIPTOR_NAMES  # now includes "tail_count", "npr1", "npr2" too
    + ("extent",)
    + PROTEIN_DESCRIPTOR_NAMES
    + ("polar_share",)
    + POCKET_CHEMISTRY_DESCRIPTOR_NAMES
    + PAIR_DESCRIPTOR_NAMES
)

# Descriptors that are shares, bounded in [0, 1] BY CONSTRUCTION (a fraction of pocket
# residues, or of SASA) -- the only names for which a FIXED (not train-fit) equal-
# width binning is a principled choice, because [0, 1] is already their whole
# possible domain, not an empirical range that could leak. Every other catalog name
# (a length, a count, a burial statistic, a product of two of those...) has no such
# built-in bound, so fixed-N coarsening for THOSE falls back to the train-observed
# [min, max] instead -- see parse_descriptor_token/_fit_coarse_edges.
BOUNDED_SHARE_DESCRIPTOR_NAMES = (
    "pocket_residue_share", "pocket_sasa_share", "apolar_sasa_share", "aromatic_share",
    "polar_share", "aromatic_share_core",
    # The ten residue-class shares are fractions of the pocket's core (or rim)
    # residues, and pocket_packing_density is a fraction of the cavity's own hull:
    # [0, 1] is their whole possible domain by construction. pocket_free_volume is
    # NOT here -- it is an unbounded angstrom^3 volume, so its fixed-N coarsening
    # falls back to the train-observed range like any other unbounded quantity.
    *(
        name for name in POCKET_CHEMISTRY_DESCRIPTOR_NAMES
        if name != "pocket_free_volume"
    ),
)

# <name>_coarse=<spec>'s default quantile count when <spec> is the bare word
# "quantiles" (no :N suffix) -- matches the band count the fixed-thirds scheme this
# syntax replaces used, so the default reads as "the same idea, fixed the leak-of-
# resolution way" rather than an arbitrary new number.
DEFAULT_QUANTILE_BINS = 3


class CoarseSpec:
    """One <name>_coarse=<spec> descriptor token's parsed instructions -- how many
    bins (`bins`), and whether their edges are FIXED (`mode="fixed"`: [0, 1] for a
    BOUNDED_SHARE_DESCRIPTOR_NAMES entry, else the train-observed [min, max]) or
    train-fit QUANTILES (`mode="quantiles"`: dataloader.pocket_lipid_compatibility.
    coarsen_to_levels on numpy.quantile edges, the same mechanism "extent"
    -- Dataloader.py's own coarse_extent -- already uses for pocket_extent,
    generalised to any base name and any bin count).
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

# Bare-token defaults for the two names the old fixed-thirds coarse_share scheme
# used to own outright (aromatic_share_coarse, polar_share_coarse) -- so
# "aromatic_share_coarse" alone (no explicit =spec) still works as a descriptor
# name, just resolving to a GOOD default instead of the broken one. Chosen by
# measuring bin population directly on this project's 35 proteins (both shares give
# the identical profile, quantile splits being population- not value-driven):
#   N=2 : 35            (degenerate before the coarsen_to_levels fix, still trivial)
#   N=3 : 12, 11, 12     <- picked: matches this project's own established "~12 per
#                            band is far enough from a protein id" reasoning
#                            (files/results/compat_input_audit.md's eta^2 argument for
#                            coarse_extent, which this mirrors) without being any
#                            finer than that already-vetted precedent.
#   N=4 : 9, 8, 9, 9
#   N=5 : 7, 7, 7, 7, 7
#   N=7 : the smallest bin drops to 4-5 -- too fine for 35 proteins.
# mode=quantiles (not "fixed") is the actual fix: aromatic_share's real range
# (0.08-0.348) never reaches fixed thirds' own 1/3 edge, so ANY fixed-edge scheme
# collapses most proteins into one band on this data (verified: 34 of 35 at N=3
# fixed) -- quantiles is population-balanced by construction regardless of the
# underlying value distribution's shape.
DEFAULT_COARSE_SPECS = {
    "aromatic_share_coarse": CoarseSpec("quantiles", 3),
    "polar_share_coarse": CoarseSpec("quantiles", 3),
}


class UnknownDescriptorName(ValueError):
    """A descriptor token naming a base name the catalog does not have."""


# Names an arg file asked for that the catalog no longer has. A removed descriptor
# must not kill a grid of runs that still name it, so parse_descriptor_list drops the
# token and records it here; the run log and the test_metrics report name it.
UNKNOWN_DESCRIPTOR_NAMES: list[str] = []


def parse_descriptor_token(token):
    """One comma-separated --descriptor_heads entry ->
    (base_name, coarse_spec_or_None), validated against DESCRIPTOR_CATALOG.

    A bare `name` (must be in DESCRIPTOR_CATALOG) -> (name, None), read as-is --
    unchanged from before this syntax existed. Two names are the exception:
    "aromatic_share_coarse"/"polar_share_coarse" bare -> (base, DEFAULT_COARSE_
    SPECS[name]) -- see that dict for why those two specific defaults were chosen.
    An explicit `aromatic_share_coarse=<spec>` overrides the default the same way
    any other name's spec would.

    `name_coarse=<N>` (N an integer >= 2) -> (name, CoarseSpec("fixed", N)): N
    equal-WIDTH bins, generalising the old coarse_share's fixed thirds (which this
    replaces for this system -- see DESCRIPTOR_CATALOG's own docstring for why: on
    this project's real data aromatic_share never left the fixed scheme's first
    third, collapsing 34 of 35 proteins onto one value) to any bin count, over [0, 1]
    when `name` is a BOUNDED_SHARE_DESCRIPTOR_NAMES entry (still zero data-
    dependence to leak) or the TRAIN-observed [min, max] otherwise (an unbounded
    quantity has no universal fixed domain to bin over without one -- this is train-
    fit, the same leak-safety class as quantiles below, not the zero-dependence
    class the original fixed thirds were).

    `name_coarse=quantiles` or `name_coarse=quantiles:<N>` -> (name,
    CoarseSpec("quantiles", N or DEFAULT_QUANTILE_BINS)): N train-fit quantile bins
    -- equal population per bin rather than equal value-width, the same mechanism
    "extent" already uses for pocket_extent, generalised to any base name/bin count.

    Raises ValueError for an unknown base name or a malformed spec, same style as
    dataloader.chemistry_prior.feature_similarity's own unknown-name error.
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
    """(base_name, coarse_spec_or_None) -> the one canonical string naming it --
    e.g. "aromatic_share_coarse=quantiles" and "aromatic_share_coarse=quantiles:3"
    (DEFAULT_QUANTILE_BINS) both canonicalise to the same string, so the two
    resolve to the SAME dataloader column and the SAME NamedDescriptorHead token
    instead of silently computing the same thing twice under two names.
    """
    if spec is None:
        return name
    if spec.mode == "quantiles":
        return f"{name}{_COARSE_SUFFIX}quantiles:{spec.bins}"
    return f"{name}{_COARSE_SUFFIX}{spec.bins}"


def parse_descriptor_list(value):
    """Comma-separated string -> tuple of CANONICAL descriptor tokens (see
    canonical_descriptor_token), same convention --features (analysis/baselines/
    knn_model.py) and --excluded_groups use.
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
    """--descriptor_heads string -> tuple of heads, each a tuple of canonical tokens.

    Heads are separated by "/" -- not "|" or ";", which a shell reads as syntax and
    which would need quotes in an arg file. A head that comes out empty is skipped: a
    wrapped arg-file line (scripts/lib/args_file_lib.sh) is joined with a comma, so
    "a,b/" + "c,d" reaches here as "a,b/,c,d".
    """
    heads = (parse_descriptor_list(part) for part in value.split("/"))
    return tuple(head for head in heads if head)


def resolve_requested_tokens(*raw_lists):
    """Any number of comma-separated raw strings -> the sorted, deduped union of their
    canonical tokens -- the SAME deterministic column order dataloader/Dataloader.py's
    descriptor_catalog_input tensor is stacked in and every head and encoder indexes
    into it by. Every caller building the SAME descriptor_catalog_input tensor calls
    this one function against the SAME raw strings, so they always agree without the
    ordering itself needing to be passed between them.
    """
    union = set()
    for raw in raw_lists:
        union |= set(parse_descriptor_list(raw))
    return tuple(sorted(union))


def descriptor_catalog_only(config):
    """True when descriptor_catalog_input is ALL the model reads of a sample.

    --descriptors_head with --descriptor_heads: Final_Layer runs the named heads on that
    one tensor and returns (architecture/final_layer.py), so the protein graph
    (1536-wide ESM3 rows per residue) and the MoLFormer lipid encoding were built,
    collated into every batch and then ignored -- ~26 MB of torch.cat per batch of 16
    against 0.3 kB per sample actually read. Dataloader builds lean samples under this,
    and new_train.py preassembles them exactly as it does for --deepclip.

    --descriptor_mlp (architecture/descriptor_mlp_head.py) reads the exact same
    tensor by name, through the same --descriptor_heads -- DescriptorMLPHead in place of
    NamedDescriptorHead, not a different input, so it gets the identical lean-loading/
    preassembly treatment.
    """
    return bool(
        (
            getattr(config, "descriptors_head", False)
            or getattr(config, "descriptor_mlp", False)
        )
        and getattr(config, "descriptor_heads", "")
    )


def full_catalog_order(config):
    """Every raw name-list that feeds the ONE shared descriptor_catalog_input tensor for
    this config, resolved through resolve_requested_tokens to the single deterministic
    column order every consumer indexes into: --descriptor_heads (all its heads), the
    node-broadcast lists --protein_descriptors/
    --lipid_descriptors (architecture/protein_encoder.py, architecture/lipid_encoder.py)
    and --deepclip_protein_gate (architecture/deepclip.py). Every one of those call
    sites uses THIS function rather than assembling its own tuple, so no destination can
    end up naming a token none of the others built.
    """
    return resolve_requested_tokens(
        getattr(config, "descriptor_heads", "").replace("/", ","),
        getattr(config, "protein_descriptors", ""),
        getattr(config, "lipid_descriptors", ""),
        getattr(config, "deepclip_protein_gate", ""),
    )


def resolve_similarity_feature_names(*raw_lists):
    """Any number of comma-separated raw strings (a --descriptor_heads value may be
    passed whole: "/" separates heads like "," separates tokens) -> the sorted, deduped
    union of their BASE names, with any coarse-bucketing spec dropped.

    A different projection of the same raw strings resolve_requested_tokens reads:
    that one keeps the coarse spec (canonical_descriptor_token) because it names the
    column NamedDescriptorHead indexes into. This one exists for analysis/
    knn_model.py's --features / dataloader.chemistry_prior.feature_similarity,
    which knows only DESCRIPTOR_CATALOG's plain names -- the kNN null model has no
    notion of the head's own bucketing -- so a config's trained descriptor set can be
    handed to the null model as its --features without translating the coarse suffix
    by hand.
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
