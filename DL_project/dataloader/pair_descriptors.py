"""Cheap, docking-free descriptors for --pair_descriptors (architecture/pair_descriptor_head.py).

Motivated by Lipovsky et al., "Systematic analyses of lipid mobilization by human lipid
transfer proteins" (Nature 2025, s41586-025-10040-y), whose measured LTP-lipid complexes
this project's interaction table draws on. That paper reports acyl-chain-length and
unsaturation preferences per LTP, aromatic (Phe) clusters contacting acyl double bonds in
MD-simulated poses, headgroup hydrogen bonding, and a pocket-occupancy ("buffer zone")
ratio between bound-ligand and cavity volume.

Two of those need a bound POSE (which residue sits near which double bond, which residue
H-bonds which headgroup atom) -- this project has no docking pipeline and the paper's own
solved poses cover only the ~110 purified complexes, not the ~9905-row candidate grid this
model scores. Building them here would mean fabricating a pose for every candidate, which
is worse than not having the feature. What IS computed here, per row, from 2D structure
alone (same discipline as pocket_lipid_compatibility.longest_acyl_chain -- no 3D
embedding, which is slow and fails unpredictably across ~10k rows of stereo-ambiguous
candidates):

    unsaturation_count(l)  : non-aromatic C=C bonds -- the paper's chain-saturation axis.
    hbond_capacity(l)      : RDKit NumHDonors + NumHAcceptors -- a headgroup H-bonding
                              PROXY, not the pose-specific pattern the paper measured.
    heavy_atom_count(l)    : a cheap, robust size proxy standing in for the paper's
                              bound-ligand volume (no 3D embedding).

architecture/pair_descriptor_head.py combines these with the pocket's own aromatic_share
and (1 - apolar_sasa_share) (POCKET_DESCRIPTOR_NAMES, already scale-free) as multiplicative
pair terms -- proxies for "aromatic residues near double bonds" and "polar pocket surface
meets an H-bonding headgroup" that need no pose because they use pocket-wide chemistry
shares instead of a specific residue-double-bond contact. Dataloader.py separately
builds the occupancy term (heavy_atom_count vs the SAME coarsened pocket_extent
--compatibility_split_input's "clash" term uses) with pocket_lipid_compatibility's own
coarsen_to_levels, so a held-out protein's raw cavity size still cannot leak through it
(files/compat_input_audit.md).
"""
import functools

import numpy

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# candidates_for_row: imported lazily, inside descriptor_values_by_row, not here --
# dataloader/pocket_lipid_compatibility.py eagerly imports names FROM
# dataloader/protein_graph_builder.py, which in turn eagerly imports
# PROTEIN_DESCRIPTOR_NAMES from THIS module (see the bottom of protein_graph_builder.py)
# -- an eager import here would complete the triangle into a circular import.

# The full descriptor catalog analysis/null_model.py's --features and
# architecture/pair_descriptor_head.py's token set both draw on, named together in one
# place.
LIPID_DESCRIPTOR_NAMES = (
    "chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2",
    "logp", "tpsa", "molar_refractivity", "rotatable_bond_count",
    "aromatic_ring_count", "ring_count",
)
# See pair_descriptor_value below for what each one actually computes.
PAIR_DESCRIPTOR_NAMES = (
    "occupancy", "chain_extent_gap", "aromatic_contact", "hbond_match", "volume_fit",
    "buriedness_match", "depth_bulk_match", "hydropathy_chain_match",
    "aromatic_contact_min", "hbond_match_min", "tail_elongation_fit",
)
# occupancy/chain_extent_gap are signed differences of a single PHYSICAL quantity
# (both sides converted to angstrom, chain via chain_length_angstrom) -- standardising
# their inputs would replace that physical "does the cavity reach as far as the
# chain" comparison with an abstract standard-deviations-apart one, so --zscore
# (analysis/null_model.py) never touches them. The other six multiply two
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
# pocketness.pdb, by dataloader/protein_graph_builder.py's pocket_descriptor() --
# ModelConfig.pocket_descriptor_count must equal len(PROTEIN_DESCRIPTOR_NAMES).
# Documented in files/pocket_shape_descriptors.md, which is to be updated in the same
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
# pocket_gyration +0.443 from the shape entries below. No run had ever set
# --pocket_descriptors, so replacing the set costs no comparability.
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
    # Appended, not interleaved -- dataloader/protein_graph_builder.py's
    # pocket_descriptor() has the full reasoning (architecture/pair_descriptor_head.py
    # indexes earlier entries by bare integer literal, so their positions are load-
    # bearing). Promoted from the research-only catalog by files/pocket_shape_
    # descriptors.md section 7's eta^2 check.
    "ev28_q10",
    "aromatic_share_rim",
)

# Not raw pocket_descriptor() output, so not in PROTEIN_DESCRIPTOR_NAMES itself --
# these are exactly what architecture/pair_descriptor_head.py's PairDescriptorHead
# actually reads, under --pair_descriptors alone (polar_share) or with
# --pair_descriptor_pocket_shares_coarse on top (the two _coarse names):
#   polar_share            : 1 - apolar_sasa_share. PairDescriptorHead's own token
#                             name for the plain (uncoarsened) pocket-shares pair
#                             (aromatic_share needs no rename -- it already matches
#                             its raw PROTEIN_DESCRIPTOR_NAMES entry).
#   aromatic_share_coarse,
#   polar_share_coarse     : aromatic_share/polar_share banded into one of 3 fixed
#                             (not train-fit) thirds -- see coarse_share below, which
#                             duplicates _SHARE_BAND_EDGES/_SHARE_BAND_CENTRES as
#                             plain floats rather than importing them (that module
#                             pulls in torch; this one -- the descriptor catalog --
#                             should not depend on architecture/). Verified against
#                             torch.bucketize's own output at both edges and interior
#                             points.
PROTEIN_DERIVED_DESCRIPTOR_NAMES = ("polar_share", "aromatic_share_coarse", "polar_share_coarse")
_SHARE_BAND_EDGES = (1.0 / 3, 2.0 / 3)
_SHARE_BAND_CENTRES = (1.0 / 6, 0.5, 5.0 / 6)

# --two_pair_descriptors_paths' --good_descriptors/--bad_descriptors (training/
# read_configuration.py, architecture/named_descriptor_head.py): every BASE name a
# live NamedDescriptorHead can be built from -- either bare, or coarsened via the
# <name>_coarse=<spec> syntax below (parse_descriptor_token). "extent" is
# Dataloader's own train-fit-coarsened, leak-safe pocket_extent (the same value
# PairDescriptorHead's DATALOADER_TOKENS "extent" already reads); "tail_count" is
# acyl_chain_count. Everything else named here is its RAW dataloader/pair_
# descriptors.py or pocket_descriptor() value -- in particular "pocket_extent"
# (inside PROTEIN_DESCRIPTOR_NAMES) is the SAME cavity size "extent" coarsens,
# deliberately left nameable raw too -- see ModelConfig.two_pair_descriptors_paths
# for why (an explicit, opt-in leak probe, not a vetted-safe default). Distinct from
# PROTEIN_DERIVED_DESCRIPTOR_NAMES (still used by analysis/null_model.py's own,
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
    "polar_share",
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
#                            (files/compat_input_audit.md's eta^2 argument for
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


def parse_descriptor_token(token):
    """One --good_descriptors/--bad_descriptors comma-separated entry ->
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
            raise ValueError(
                f"Unknown descriptor name(s): ['{token}']. Known: {DESCRIPTOR_CATALOG} "
                f"(plus {tuple(DEFAULT_COARSE_SPECS)} bare)"
            )
        return token, None
    if name not in DESCRIPTOR_CATALOG:
        raise ValueError(
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
    """"--good_descriptors"/"--bad_descriptors" string -> tuple of CANONICAL
    descriptor tokens (see canonical_descriptor_token), comma-separated input, same
    convention --features (analysis/null_model.py) and --excluded_groups use.
    """
    tokens = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        name, spec = parse_descriptor_token(raw)
        tokens.append(canonical_descriptor_token(name, spec))
    return tuple(tokens)


def resolve_requested_tokens(*raw_lists):
    """Any number of --good_descriptors/--bad_descriptors/--descriptor_names-style raw
    strings -> the sorted, deduped union of their canonical tokens -- the SAME
    deterministic column order dataloader/Dataloader.py's descriptor_catalog_input
    tensor is stacked in and architecture/named_descriptor_head.py's NamedDescriptorHead
    instances index into it by. Every caller building the SAME descriptor_catalog_input
    tensor calls this one function against the SAME raw strings -- two, under
    --two_pair_descriptors_paths' --good_descriptors/--bad_descriptors pair; one, under
    --descriptors_head's --descriptor_names -- so they always agree without the
    ordering itself needing to be passed between them.
    """
    union = set()
    for raw in raw_lists:
        union |= set(parse_descriptor_list(raw))
    return tuple(sorted(union))


def full_catalog_order(config):
    """Every raw name-list that feeds the ONE shared descriptor_catalog_input tensor for
    this config, resolved through resolve_requested_tokens to the single deterministic
    column order every consumer indexes into: --good_descriptors/--bad_descriptors
    (--two_pair_descriptors_paths), --descriptor_names (usable under --descriptors_head OR
    --pair_descriptors -- architecture/final_layer.py builds a NamedDescriptorHead instead
    of PairDescriptorHead/the fixed head-only descriptor head under either), the two
    node-broadcast lists --protein_descriptors/--lipid_descriptors (architecture/
    protein_encoder.py, architecture/lipid_encoder.py), and --geometric_descriptors/
    --chemical_descriptors (--thematical_paths, architecture/thematic_descriptor_head.py).
    Every one of those call sites uses THIS function rather than assembling its own tuple,
    so no destination can end up naming a token none of the others built.
    """
    named_descriptor_names = (
        getattr(config, "descriptor_names", "")
        if getattr(config, "descriptors_head", False) or getattr(config, "pair_descriptors", False)
        else ""
    )
    return resolve_requested_tokens(
        getattr(config, "good_descriptors", ""),
        getattr(config, "bad_descriptors", ""),
        named_descriptor_names,
        getattr(config, "protein_descriptors", ""),
        getattr(config, "lipid_descriptors", ""),
        getattr(config, "geometric_descriptors", ""),
        getattr(config, "chemical_descriptors", ""),
    )


def split_names_by_side(names):
    """Canonical descriptor tokens (parse_descriptor_list's output) -> (lipid_names,
    protein_names), both tuples, preserving `names`' own order within each side.

    --thematical_paths (architecture/thematic_descriptor_head.py) needs this: each of
    --geometric_descriptors/--chemical_descriptors names a GROUP, and a forced
    lipid<->protein interaction within that group needs to know which of the group's
    tokens are lipid-side and which are protein-side. LIPID_DESCRIPTOR_NAMES and
    PROTEIN_DESCRIPTOR_NAMES + ("extent", "polar_share") are disjoint from each other
    by construction (DESCRIPTOR_CATALOG concatenates them once each), so every
    non-pair token lands on exactly one side.

    Raises ValueError for a PAIR_DESCRIPTOR_NAMES entry (occupancy, aromatic_contact,
    ...) or a <name>_coarse=<spec> token built from one -- those already combine both
    sides by formula (pair_descriptor_value), so there is no single side of a forced
    interaction to put them on. A caller that wants a PAIR_DESCRIPTOR_NAMES value
    belongs in a plain --pair_descriptors/--good_descriptors self-attention head
    instead, not a --thematical_paths group.
    """
    protein_side = PROTEIN_DESCRIPTOR_NAMES + ("extent", "polar_share")
    lipid, protein = [], []
    for token in names:
        base = token.partition(_COARSE_SUFFIX)[0]
        if base in LIPID_DESCRIPTOR_NAMES:
            lipid.append(token)
        elif base in protein_side:
            protein.append(token)
        else:
            raise ValueError(
                f"Descriptor {token!r} is a pair descriptor (already combines lipid "
                "and protein) and has no single side to assign in a --thematical_paths "
                f"group. Known pair descriptors: {PAIR_DESCRIPTOR_NAMES}"
            )
    return tuple(lipid), tuple(protein)


def resolve_similarity_feature_names(*raw_lists):
    """Any number of --good_descriptors/--bad_descriptors/--descriptor_names-style raw
    strings -> the sorted, deduped union of their BASE names, with any coarse-
    bucketing spec dropped.

    A different projection of the same raw strings resolve_requested_tokens reads:
    that one keeps the coarse spec (canonical_descriptor_token) because it names the
    column NamedDescriptorHead indexes into. This one exists for analysis/
    null_model.py's --features / dataloader.chemistry_prior.feature_similarity,
    which knows only DESCRIPTOR_CATALOG's plain names -- the kNN null model has no
    notion of the head's own bucketing -- so a config's trained descriptor set can be
    handed to the null model as its --features without translating the coarse suffix
    by hand.
    """
    names = set()
    for value in raw_lists:
        for raw in value.split(","):
            raw = raw.strip()
            if not raw:
                continue
            name, _ = parse_descriptor_token(raw)
            names.add(name)
    return tuple(sorted(names))


def coarse_share(value):
    """value (already in [0, 1]) -> the centre of its fixed-width third.

    torch.bucketize(value, edges, right=False)'s own rule: a value exactly on an
    edge stays in the LOWER band (edge itself is the band's upper, exclusive, bound).
    """
    band = sum(1 for edge in _SHARE_BAND_EDGES if value > edge)
    return _SHARE_BAND_CENTRES[band]


_MINIMUM_TAIL_CARBONS = 4
# Below this many carbons, a non-aromatic/non-ring component is more likely an
# N-methyl/ethyl branch (e.g. the choline headgroup's three methyls, each its own
# 1-carbon component) than an actual acyl tail -- acyl_chain_count would otherwise
# count every headgroup methyl as its own "tail". 4 is the shortest fatty-acid tail
# this project's SMILES actually carry (butyryl); verified DOPC (2 real C18 tails)
# -> 2, lyso-PC (1 real tail + headgroup methyls) -> 1 at this threshold.


def _acyl_chain_component_lengths(smiles):
    """Carbon count of EVERY connected non-aromatic, non-ring component of a
    molecule's carbon skeleton -- the shared computation longest_acyl_chain and
    acyl_chain_count both read, one taking the max, the other counting how many
    clear _MINIMUM_TAIL_CARBONS. Head groups, rings and sugars drop out by
    construction (same discipline as longest_acyl_chain always used). None for
    anything RDKit cannot parse, [] for a molecule with no such carbon at all.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    carbons = [
        atom.GetIdx() for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic() and not atom.IsInRing()
    ]
    if not carbons:
        return []
    index = {atom: position for position, atom in enumerate(carbons)}
    neighbours = {position: [] for position in index.values()}
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a in index and b in index:
            neighbours[index[a]].append(index[b])
            neighbours[index[b]].append(index[a])

    # Longest shortest-path in each connected component: on a chain that is its length,
    # and a double breadth-first search finds it without enumerating paths.
    def farthest(start):
        seen = {start: 0}
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in neighbours[node]:
                if neighbour not in seen:
                    seen[neighbour] = seen[node] + 1
                    queue.append(neighbour)
        end = max(seen, key=seen.get)
        return end, seen[end], set(seen)

    lengths = []
    unvisited = set(neighbours)
    while unvisited:
        start = next(iter(unvisited))
        end, _, component = farthest(start)
        _, distance, _ = farthest(end)
        lengths.append(distance + 1)
        unvisited -= component
    return lengths


def longest_acyl_chain(smiles):
    """Carbons in the longest unbranched aliphatic run of a molecule.

    The lipid's tail is what a cavity has to accommodate lengthwise, so the measure is
    the longest path through non-aromatic, non-ring carbons -- head groups, rings and
    sugars drop out by construction. Returns None for anything RDKit cannot parse OR
    with no qualifying carbon at all (same convention _acyl_chain_component_lengths'
    other caller, acyl_chain_count, uses, for the two to agree on what "missing" means).
    """
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:  # None (unparseable) or [] (no qualifying carbon) alike
        return None
    return max(lengths)


def acyl_chain_count(smiles):
    """How many SEPARATE acyl tails a molecule has (>= _MINIMUM_TAIL_CARBONS carbons
    each), not just the longest one -- longest_acyl_chain reports one number for a
    diacylglycerol/phospholipid's two esterified tails and a single-tailed lyso lipid
    alike (verified: both report chain=18 for a same-length-tailed pair, see
    dataloader.pair_descriptors.DESCRIPTOR_CATALOG's "tail_count" entry). None for
    anything RDKit cannot parse OR with no qualifying carbon at all -- same convention
    longest_acyl_chain uses (see its own docstring).
    """
    lengths = _acyl_chain_component_lengths(smiles)
    if not lengths:
        return None
    return float(sum(1 for length in lengths if length >= _MINIMUM_TAIL_CARBONS))


def unsaturation_count(smiles):
    """Non-aromatic C=C double bonds in one molecule, or None if RDKit cannot parse it."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(sum(
        1 for bond in mol.GetBonds()
        if bond.GetBondTypeAsDouble() == 2.0
        and not bond.GetIsAromatic()
        and bond.GetBeginAtom().GetSymbol() == "C"
        and bond.GetEndAtom().GetSymbol() == "C"
    ))


def hbond_capacity(smiles):
    """RDKit H-bond donor + acceptor count -- a headgroup polarity proxy, not a pose."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.NumHDonors(mol) + Descriptors.NumHAcceptors(mol))


def heavy_atom_count(smiles):
    """Heavy-atom count -- a cheap, robust size proxy standing in for ligand volume."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(mol.GetNumHeavyAtoms())


# Whole-molecule RDKit descriptors (the lipid-side analogues of the protein pocket's own
# family_neutral axes -- pocket_volume_per_sasa/apolar_sasa_share/hydropathy_rim/
# pocket_extent/aromatic_share): logp/tpsa are the two orthogonal hydrophobicity/
# polarity axes, molar_refractivity is the volume/polarizability analogue of
# pocket_volume_per_sasa, rotatable_bond_count is how much the lipid can conform to a
# cavity's shape (an absolute count, unlike rotatable_fraction above), and
# aromatic_ring_count/ring_count are the direct counterparts of the pocket's own
# aromatic_share. All purely topological (no conformer needed), same convention as
# unsaturation_count/hbond_capacity/heavy_atom_count above: None where RDKit cannot
# parse the candidate.
def logp(smiles):
    """RDKit Crippen logP -- octanol/water partition coefficient."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.MolLogP(mol))


def tpsa(smiles):
    """Topological polar surface area (Angstrom^2)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.TPSA(mol))


def molar_refractivity(smiles):
    """RDKit molar refractivity."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(Descriptors.MolMR(mol))


def rotatable_bond_count(smiles):
    """Absolute rotatable-bond count."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumRotatableBonds(mol))


def aromatic_ring_count(smiles):
    """Aromatic ring count."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumAromaticRings(mol))


def ring_count(smiles):
    """Total ring count (aromatic + aliphatic)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(rdMolDescriptors.CalcNumRings(mol))


# --pair_descriptor_lipid_shape (LIPID_SHAPE_DESCRIPTOR_NAMES below): the one deliberate
# exception to this module's own "no 3D embedding" rule stated in its docstring above --
# ETKDG is indeed slow and fails unpredictably per-molecule, which is why it is opt-in,
# ensemble-averaged (not a single arbitrary conformer -- a flexible acyl tail has many
# near-isoenergetic shapes; one draw would teach the model the generator's seed, not the
# molecule), and wrapped in the same random-coords retry data/build_lipid_isomer_graphs.py
# uses for its own bond-length feature (which reuses generate_conformer_ensemble below,
# rather than duplicating this embed+optimize logic a second time).
CONFORMER_COUNT = 10
CONFORMER_SEED = 0xF00D


def generate_conformer_ensemble(mol, n_confs=CONFORMER_COUNT, seed=CONFORMER_SEED):
    """Explicit-H copy of `mol` with `n_confs` ETKDG+MMFF conformers.

    Returns (mol_h, conf_ids); mol_h's heavy-atom indices match `mol`'s (Chem.AddHs
    appends new atoms after the existing ones). Raises ValueError if ETKDG embedding
    fails even after a useRandomCoords retry -- callers should let that propagate
    rather than silently write a placeholder into the data.
    """
    mol_h = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    conf_ids = list(AllChem.EmbedMultipleConfs(mol_h, numConfs=n_confs, params=params))
    if not conf_ids:
        params.useRandomCoords = True
        conf_ids = list(
            AllChem.EmbedMultipleConfs(mol_h, numConfs=n_confs, params=params)
        )
    if not conf_ids:
        raise ValueError(
            f"ETKDG conformer embedding failed for {Chem.MolToSmiles(mol)}"
        )
    try:
        AllChem.MMFFOptimizeMoleculeConfs(mol_h, maxIters=500)
    except Exception:
        pass  # MMFF parameters missing for some atom types -- keep raw ETKDG geometry
    return mol_h, conf_ids


@functools.lru_cache(maxsize=4096)
def _cached_conformer_ensemble(smiles):
    """(mol_h, conf_ids) for `smiles`, memoized by canonical SMILES.

    radius_of_gyration/asphericity/molecular_volume below each want their own mean
    over the SAME 10-conformer ensemble (CONFORMER_SEED is fixed, so it is a pure
    function of `smiles`) -- calling generate_conformer_ensemble independently per
    measure paid the ETKDG embed + MMFF optimize three times over for identical
    geometry. Measured as most of why data/build_pair_descriptor_cache.py's rebuild
    took ~20 minutes on this project's ~1300 unique candidates even after pinning
    OMP_NUM_THREADS=1 (which fixed a separate, smaller BLAS-thread-thrashing cost).
    None (not raised) for anything RDKit cannot parse, matching every other measure
    here's convention.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return generate_conformer_ensemble(mol)


def _mean_over_conformers(smiles, per_conformer_fn):
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(sum(values) / len(values))


def radius_of_gyration(smiles):
    """Ensemble-mean radius of gyration (Angstrom) -- overall size/compactness."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: rdMolDescriptors.CalcRadiusOfGyration(
            mol_h, confId=conf_id
        ),
    )


def asphericity(smiles):
    """Ensemble-mean asphericity (unitless, 0=spherical) -- elongated vs globular."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: rdMolDescriptors.CalcAsphericity(mol_h, confId=conf_id),
    )


def molecular_volume(smiles):
    """Ensemble-mean van-der-Waals volume (Angstrom^3) -- real size, not a heavy-atom proxy."""
    return _mean_over_conformers(
        smiles,
        lambda mol_h, conf_id: AllChem.ComputeMolVolume(mol_h, confId=conf_id),
    )


def rotatable_fraction(smiles):
    """Rotatable bonds / total bonds -- conformational flexibility, purely topological
    (does not need a conformer, unlike the three functions above)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    total_bonds = mol.GetNumBonds()
    if total_bonds == 0:
        return 0.0
    return float(rdMolDescriptors.CalcNumRotatableBonds(mol)) / total_bonds


def _median_over_conformers(smiles, per_conformer_fn):
    """Same 10-conformer ensemble as _mean_over_conformers, reduced by MEDIAN instead
    -- npr1/npr2 below live in a bounded triangular shape space (Sauer & Schwarz,
    2003) where one poorly-optimized outlier conformer's ratio can sit far from the
    rest, and a median resists that the way a mean does not.
    """
    ensemble = _cached_conformer_ensemble(smiles)
    if ensemble is None:
        return None
    mol_h, conf_ids = ensemble
    values = [per_conformer_fn(mol_h, conf_id) for conf_id in conf_ids]
    return float(numpy.median(values))


def npr1(smiles):
    """Median normalized principal moment ratio PMI1/PMI3 (Sauer & Schwarz, 2003)
    over the same 10-conformer ensemble radius_of_gyration/asphericity/
    molecular_volume already share -- how elongated the lipid's own 3D conformation
    is, the direct lipid-side counterpart of the pocket's own pocket_elongation
    (unlike chain/tail_count, which only stand in for shape via carbon-count
    topology)."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR1(mol_h, confId=conf_id)
    )


def npr2(smiles):
    """Median normalized principal moment ratio PMI2/PMI3 -- how flat/planar the
    lipid's own 3D conformation is, the counterpart of pocket_flatness."""
    return _median_over_conformers(
        smiles, lambda mol_h, conf_id: rdMolDescriptors.CalcNPR2(mol_h, confId=conf_id)
    )


LIPID_SHAPE_DESCRIPTOR_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "rotatable_fraction",
    "npr1", "npr2",
)

# The five _MEASURES entries whose per-candidate cost is a real 10-conformer
# ETKDG+MMFF embed, not microseconds -- dataloader/pair_descriptor_cache.py's build
# routes exactly these through its process pool (_parallel_measures) rather than
# computing every measure serially; npr1/npr2 share the SAME cached ensemble
# radius_of_gyration/asphericity/molecular_volume already pay for, so adding them
# here costs no extra embedding, only two more cheap reductions over conformers
# already generated.
CONFORMER_MEASURE_NAMES = (
    "radius_of_gyration", "asphericity", "molecular_volume", "npr1", "npr2",
)


_MEASURES = {
    "unsaturation": unsaturation_count,
    "hbond": hbond_capacity,
    "heavy_atoms": heavy_atom_count,
    "tail_count": acyl_chain_count,
    "radius_of_gyration": radius_of_gyration,
    "asphericity": asphericity,
    "molecular_volume": molecular_volume,
    "rotatable_fraction": rotatable_fraction,
    "npr1": npr1,
    "npr2": npr2,
    "logp": logp,
    "tpsa": tpsa,
    "molar_refractivity": molar_refractivity,
    "rotatable_bond_count": rotatable_bond_count,
    "aromatic_ring_count": aromatic_ring_count,
    "ring_count": ring_count,
}


def descriptor_values_by_row(csv, measure, isomeric=False, cache=None):
    """One of `_MEASURES`, per candidate, in the order the encoder numbers them.

    Same shape and the same per-field/per-SMILES caching discipline as
    pocket_lipid_compatibility.chain_lengths_by_row: entries are None where RDKit
    cannot parse the candidate, and a row with no usable candidate gets [None].
    `isomeric` MUST match chain_lengths_by_row's own -- it controls which candidates
    within a row collapse into one canonical-SMILES entry, so a mismatch would make
    this function's per-row list a different length than chain's, and
    Dataloader._ragged_tensor stacks columns on the assumption they agree.

    `cache`, when given, is a dataloader/pair_descriptor_cache.py load result: a raw
    candidate present in its "raw_to_canonical" skips the canonicalising parse, and a
    canonical key present in its "values" skips `fn`. Same fallback discipline as
    chain_lengths_by_row -- an entry the cache has never seen is computed here exactly
    as without a cache.
    """
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    fn = _MEASURES[measure]
    raw_to_canonical = cache["raw_to_canonical"] if cache else {}
    cached_values = cache["values"] if cache else {}
    by_field = {}
    by_smiles = {}
    per_row = []
    for _, row in csv.iterrows():
        field = tuple(candidates_for_row(row))
        values = by_field.get(field)
        if values is None:
            values = []
            seen = set()
            for raw in field:
                if raw in raw_to_canonical:
                    key = raw_to_canonical[raw]
                    if key is None:
                        continue
                else:
                    molecule = Chem.MolFromSmiles(raw)
                    if molecule is None or molecule.GetNumAtoms() == 0:
                        continue
                    key = Chem.MolToSmiles(
                        molecule, canonical=True, isomericSmiles=isomeric
                    )
                if key in seen:
                    continue
                seen.add(key)
                if key not in by_smiles:
                    cached = cached_values.get(key)
                    # `measure in cached` first, not cached.get(measure, fn(key)): the
                    # latter's default is evaluated eagerly regardless of the lookup,
                    # which would call fn (an ETKDG embed, for the three lipid_shape
                    # measures) on every candidate even on a cache hit. A cache built
                    # with lipid_shape=False (dataloader/pair_descriptor_cache.py)
                    # carries every OTHER measure for a SMILES it has seen, just not
                    # those three, so this still must fall back per-measure rather than
                    # KeyError.
                    if cached is not None and measure in cached:
                        by_smiles[key] = cached[measure]
                    else:
                        by_smiles[key] = fn(key)
                values.append(by_smiles[key])
            values = values or [None]
            by_field[field] = values
        per_row.append(values)
    return per_row


def as_arrays(per_row):
    """`descriptor_values_by_row`'s (or chain_lengths_by_row's) output as NaN-arrays.

    Same conversion pocket_lipid_compatibility._candidate_arrays does for chain
    lengths; shared here since --pair_descriptors needs it for three more measures.
    """
    return [
        numpy.array(
            [numpy.nan if value is None else float(value) for value in row],
            dtype=float,
        )
        for row in per_row
    ]


# Tanford's formula for the maximum extended (all-trans, zig-zag) length of a
# saturated hydrocarbon chain (Tanford, C., "The Hydrophobic Effect", 1980; standard
# in lipid biophysics) -- L = 1.5 + 1.265*(n-1) angstrom for n carbons. Needed
# because `chain` (LIPID_DESCRIPTOR_NAMES, a plain carbon COUNT, unitless) is not
# comparable to `pocket_extent`/`depth_q10` (POCKET_DESCRIPTOR_NAMES, angstrom spans)
# without converting one to the other's units first -- see pair_descriptor_value's
# occupancy/chain_extent_gap, and the bug this fixes: comparing cbrt(heavy_atom_
# count) (a UNITLESS ~2.6-4.6 range) directly against pocket_extent (an ANGSTROM
# ~13.6-32.0 range) meant pocket_extent always won by a wide margin, occupancy's
# relu clipped every single row to exactly 0.0 (verified directly on this project's
# data: 100% of rows), and it silently carried zero information in every null-model
# run AND every trained --pair_descriptors run (dataloader/Dataloader.py uses
# the identical formula for the live training path -- fixed there too, in the same
# commit as this).
_CHAIN_BOND_PROJECTION_A = 1.265
_CHAIN_TERMINAL_A = 1.5


def chain_length_angstrom(chain):
    """`chain` (a carbon count) -> an estimated physical length in angstrom, via
    Tanford's extended-chain formula -- see the module-level comment above it.
    """
    return _CHAIN_TERMINAL_A + _CHAIN_BOND_PROJECTION_A * (chain - 1.0)


def pair_descriptor_value(name, lipid_values, protein_values):
    """One PAIR_DESCRIPTOR_NAMES entry, combined from a lipid's own descriptor dict
    (dataloader.chemistry_prior._lipid_descriptor_table's per-species entry -- every
    LIPID_DESCRIPTOR_NAMES key) and a protein's own (protein_descriptor_table's
    per-protein entry -- every PROTEIN_DESCRIPTOR_NAMES + PROTEIN_DERIVED_DESCRIPTOR_
    NAMES key). Both tables are computed unconditionally in full whenever a pair name
    is requested (see feature_similarity), so every key read here is always present
    regardless of which OTHER names the caller asked for.

    architecture/pair_descriptor_head.py's own module docstring names the two
    remaining pair phenomena the paper (Lipovsky et al., Nature 2025,
    s41586-025-10040-y) reports beyond occupancy -- "aromatic residues near double
    bonds" and "polar pocket surface meets an H-bonding headgroup" -- as things the
    self-attention token set is left to learn to combine on its own, never spelled
    out as an explicit formula anywhere (there is nothing FOR a null model, which has
    no attention weights, to read). aromatic_contact/hbond_match below are that
    formula -- the null-model-usable, unlearned version of what PairDescriptorHead's
    tokens ask the network to discover for itself.

        occupancy         : relu(chain_length_angstrom(chain) - pocket_extent) --
                             the acyl chain's own estimated physical length (see
                             chain_length_angstrom above) against the cavity's own
                             angstrom span, both now the same unit. Bound at 0: a
                             chain shorter than the pocket is not a clash, only a
                             chain LONGER than it is. NOT cbrt(heavy_atom_count)
                             (an earlier version of this formula, and still what
                             architecture/pair_descriptor_head.py's own occupancy
                             token computes) -- that compared a UNITLESS ~2.6-4.6
                             number directly against pocket_extent's ~13.6-32.0
                             angstrom range with no conversion between them, so
                             pocket_extent always won and relu clipped every single
                             row on this project's data to exactly 0.0, carrying
                             zero information (verified directly; see project memory
                             or dataloader/Dataloader.py's matching fix).
        chain_extent_gap   : pocket_extent - chain_length_angstrom(chain), signed (no
                              relu), same angstrom-length conversion as occupancy --
                              positive when the cavity runs longer than the chain,
                              negative when the chain overhangs it. (An earlier
                              version compared pocket_extent directly against the
                              raw carbon COUNT, unitless -- numerically similar
                              enough in raw magnitude on this data to not clip to a
                              constant the way occupancy's old formula did, but not
                              a principled unit match either; fixed the same way.)
        aromatic_contact   : aromatic_share * unsaturation -- an aromatic-rich pocket
                              paired with an unsaturated (kinked, pi-contact-prone)
                              chain scores higher than either alone; zero if the
                              pocket has no aromatics or the chain is fully saturated.
        hbond_match        : polar_share * hbond -- a polar pocket surface paired
                              with a headgroup that has H-bond donors/acceptors to
                              offer scores higher than either alone.
        volume_fit         : pocket_volume_per_sasa * heavy -- an alternative to
                              occupancy on the pocket's volume-to-surface ratio
                              (how enclosed/deep, not how long) against the same
                              ligand-bulk proxy.
        buriedness_match   : buriedness_q50 * heavy -- how enclosed the pocket's
                              lining residues are (median voromqa buriedness)
                              against ligand bulk: a buried, enclosed site may
                              specifically favour (or specifically exclude) a bulkier
                              ligand differently than an exposed one would.
        depth_bulk_match   : depth_q10 * heavy -- how deeply the pocket's shallowest
                              lining residues (10th percentile voromqa burial, a
                              LOCAL per-residue statistic, not a spatial reach the
                              way pocket_extent is) sit, against ligand bulk. NOT a
                              signed gap against chain length (an earlier version of
                              this entry, "depth_chain_gap" = depth_q10 - chain):
                              depth_q10 (~1.0-1.4 on this data) is not a length
                              comparable to a chain's own reach in the first place --
                              subtracting it from chain (~8-30) left depth_q10
                              contributing negligible variance regardless of any
                              rescaling, because the two were never the same kind of
                              quantity to begin with (chain_extent_gap already covers
                              the genuine reach-vs-length question, correctly, using
                              pocket_extent). Multiplication against heavy (like
                              buriedness_match, aromatic_contact, hbond_match) sidesteps
                              needing them to be the same unit at all -- a real
                              alternative to buriedness_match, not a duplicate: this is
                              the SHALLOWEST decile specifically, buriedness_match is
                              the pocket's own median.
        hydropathy_chain_match : hydropathy_core * chain -- core-residue
                              hydrophobicity (Kyte-Doolittle mean) against chain
                              length: a longer hydrophobic tail may specifically
                              favour a more hydrophobic core than a short one would.
        aromatic_contact_min : min(aromatic_share, unsaturation), BOTH STANDARDISED
                              first (always, independent of --zscore -- see
                              MIN_PAIR_DESCRIPTOR_NAMES) -- a bottleneck reading of
                              aromatic_contact: the pair scores no higher than its
                              weaker side, so an aromatic-rich pocket paired with a
                              fully saturated chain scores low regardless of how
                              aromatic-rich, unlike the product which a large enough
                              one side can still inflate.
        hbond_match_min    : min(polar_share, hbond), both standardised first
                              (same always-on standardisation as aromatic_contact_min)
                              -- the bottleneck reading of hbond_match.
        tail_elongation_fit : tail_count / max(pocket_elongation, 1.0) -- how many
                              SEPARATE acyl tails (dataloader.pair_descriptors.
                              acyl_chain_count) a pocket's own SHAPE, not its size,
                              can plausibly hold side by side. pocket_elongation is
                              axis0/axis1 of the cavity's atom cloud (tube vs bowl,
                              >= 1 by construction -- protein_graph_builder.
                              pocket_shape); a long narrow channel (high elongation)
                              has room lengthwise for one chain, not width for a
                              second one alongside it, while a rounder pocket
                              (elongation near 1) is the shape a multi-tailed lipid
                              (a diacylglycerol/phospholipid's two esterified tails,
                              a triacylglycerol's three) could plausibly sit packed
                              into side by side. A RATIO rather than a product
                              (like volume_fit/buriedness_match/depth_bulk_match/
                              hydropathy_chain_match) or a difference (like
                              occupancy/chain_extent_gap) -- a THIRD category of its
                              own -- because the relationship is "elongation divides
                              down how much capacity is usable", not "elongation and
                              tail_count both push the same way" (a product) or "the
                              two measure the same physical quantity" (a
                              difference); --zscore does not touch it for the same
                              reason it does not touch occupancy/chain_extent_gap --
                              standardising elongation first could make the
                              denominator cross zero or go negative, which the ratio
                              has no sensible reading of. max(..., 1.0) guards the
                              one degenerate case pocket_shape's own docstring
                              already flags: fewer than 4 pocket atoms returns
                              elongation = 0.0 rather than a real ratio, which would
                              otherwise divide UP instead of down.

    None of these eleven needs a bound pose (which residue contacts which double
    bond, which residue H-bonds which headgroup atom) -- same discipline as the rest
    of this module: pocket-wide chemistry shares and lipid-wide scalars, not a
    specific residue-atom contact this project has no docking pipeline to place.
    """
    if name == "occupancy":
        return max(
            0.0,
            chain_length_angstrom(lipid_values["chain"]) - protein_values["pocket_extent"],
        )
    if name == "chain_extent_gap":
        return protein_values["pocket_extent"] - chain_length_angstrom(lipid_values["chain"])
    if name == "aromatic_contact":
        return protein_values["aromatic_share"] * lipid_values["unsaturation"]
    if name == "hbond_match":
        return protein_values["polar_share"] * lipid_values["hbond"]
    if name == "volume_fit":
        return protein_values["pocket_volume_per_sasa"] * lipid_values["heavy"]
    if name == "buriedness_match":
        return protein_values["buriedness_q50"] * lipid_values["heavy"]
    if name == "depth_bulk_match":
        return protein_values["depth_q10"] * lipid_values["heavy"]
    if name == "hydropathy_chain_match":
        return protein_values["hydropathy_core"] * lipid_values["chain"]
    if name == "aromatic_contact_min":
        return min(protein_values["aromatic_share"], lipid_values["unsaturation"])
    if name == "hbond_match_min":
        return min(protein_values["polar_share"], lipid_values["hbond"])
    if name == "tail_elongation_fit":
        return lipid_values["tail_count"] / max(protein_values["pocket_elongation"], 1.0)
    raise ValueError(f"Unknown pair descriptor: {name}. Known: {PAIR_DESCRIPTOR_NAMES}")
