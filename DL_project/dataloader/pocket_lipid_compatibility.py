"""How well a pocket's own dimensions match a candidate lipid's own dimensions.

Every descriptor in POCKET_DESCRIPTOR_NAMES describes the protein alone, and every one
of them turns out to be a family fingerprint to some degree (η² 0.28-0.85,
preprocessing/pocket_descriptor_identity_check.py) -- on 35 proteins / 9 families,
almost any sufficiently informative protein-only summary is. A quantity that depends on
BOTH the protein and the candidate lipid together cannot collapse to a protein label the
same way, because it is not a function of the protein alone.

The one built here: pocket_extent(p) - chain_length(l), where pocket_extent is the same
PCA-axis span POCKET_DESCRIPTOR_NAMES already computes (dataloader/graphs_builders/protein_graph_builder)
and chain_length is the longest unbranched aliphatic run of the candidate lipid --
literally "does the cavity reach as far as the tail is long". Documented in
files/reference/pocket_lipid_compatibility.md, which also carries the measurement of whether it
adds anything over files/history/geometric_edge.md chemistry prior.

Consumer of the raw value, wired in Dataloader:
  --pocket_compat_prior : frozen, calibrated, added to the logit outside the network
                          (same mechanism as --chem_prior, and jointly calibrated with
                          it when both are on -- see dataloader/chemistry_prior.py).
"""
import os

import numpy
from rdkit import Chem

from preprocessing.compute_descriptors import (
    pocket_atom_coordinates,
    pocket_shape,
)

# Sentinels this project's SMILES columns use for "no structure recorded", matching
# analysis/protein_profile_probe.py (mode `correlate`), which imports EMPTY from here rather than
# keeping its own copy.
EMPTY = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def smiles_for_row(row):
    """The first usable SMILES string for one interaction-table row, or None.

    SmileGlobal first, SmileFragment as fallback -- the same preference order
    chain_length_per_protein used before this was factored out. A cell can carry
    several candidates separated by ';'; this returns the first of them, and
    candidates_for_row returns all.
    """
    candidates = candidates_for_row(row)
    return candidates[0] if candidates else None


def candidates_for_row(row):
    """Every candidate structure listed for one row, in field order.

    The candidates are the isomers the spectrum could not separate, so which of them the
    measured molecule was is unknown. A quantity derived from the structure is therefore
    a quantity with a spread, and taking the first candidate reports one arbitrary member
    of it -- the member the annotation happened to list first, which is not a property of
    the lipid. The callers here average over the whole list instead, which is also what
    the averaged evaluation does to the model's own predictions.
    """
    for column in ("SmileGlobal", "SmileFragment"):
        text = str(row.get(column, "")).strip()
        if text in EMPTY:
            continue
        parts = [part.strip() for part in text.split(";")]
        return [part for part in parts if part and part not in EMPTY]
    return []


def candidate_fields_by_row(csv):
    """`candidates_for_row` for a whole table at once, one tuple per row.

    Identical result, without a Series per row: `csv.iterrows()` builds one, and the
    callers ask for this table once per measure -- 21 measures x 11018 rows was 221k
    Series constructions, 4.8 s of a 9.1 s dataset build with not one RDKit parse
    among them. Memoized by the raw column texts as well, since rows of one species
    repeat them.
    """
    length = len(csv)
    columns = [
        csv[name].to_numpy(dtype=object) if name in csv.columns else [""] * length
        for name in ("SmileGlobal", "SmileFragment")
    ]
    by_text = {}
    per_row = []
    for texts in zip(*columns):
        field = by_text.get(texts)
        if field is None:
            # The first column whose text is not a sentinel decides the row, exactly as
            # candidates_for_row returns on it -- including when its parts all filter
            # out, which yields an empty field rather than falling through to the next.
            field = ()
            for text in texts:
                text = str(text).strip()
                if text in EMPTY:
                    continue
                field = tuple(
                    part
                    for part in (part.strip() for part in text.split(";"))
                    if part and part not in EMPTY
                )
                break
            by_text[texts] = field
        per_row.append(field)
    return per_row


def chain_lengths_by_species(csv):
    """Longest acyl chain of EVERY candidate structure, per FullIdentityOfLipid.

    A species can appear hundreds of times (once per protein it was screened against);
    computing this per ROW would redo the same RDKit parse and BFS that many times.

    One value per candidate rather than one per species, because the candidates differ
    in how the carbons are split between the two chains and their longest chains differ
    with them -- PC(34:1) as 16:0/18:1 is 18 long, as 14:0/20:1 it is 20. Which of them
    the model is looking at is decided per sample (the draw during training, the
    candidate index during averaged evaluation), so the term that describes it has to be
    available per candidate too; collapsing the list to one number would describe a
    molecule that was never encoded.

    Entries are NaN where RDKit cannot parse the candidate or it carries no qualifying
    carbon at all, and a species with no usable candidate gets a single NaN -- the caller
    decides how to fill that in (see raw_compatibility_matrix).
    """
    # Local import: dataloader/descriptors.py (longest_acyl_chain's home, see
    # that module's LIPID_DESCRIPTOR_NAMES) imports candidates_for_row from THIS
    # module at its own top level, so importing descriptors here at module load
    # time would cycle -- deferred to call time, by when both modules are already
    # fully loaded either way round.
    from preprocessing.compute_descriptors import longest_acyl_chain

    lengths = {}
    for species, rows in csv.groupby("FullIdentityOfLipid"):
        candidates = []
        for _, row in rows.iterrows():
            candidates = candidates_for_row(row)
            if candidates:
                break
        measured = [longest_acyl_chain(smiles) for smiles in candidates]
        lengths[species] = numpy.array(
            [numpy.nan if length is None else float(length) for length in measured]
            or [numpy.nan],
            dtype=float,
        )
    return lengths


def chain_length_by_species(csv):
    """Mean longest acyl chain per species -- the candidate-blind summary.

    What a caller that has no candidate to look at should use: the analysis scripts, and
    the train-only statistics that must not depend on which candidate a row happened to
    draw. The per-sample values come from chain_lengths_by_row instead, which numbers
    the candidates the way the encoder does.
    """
    return {
        species: (
            None
            if numpy.isnan(lengths).all()
            else float(numpy.nanmean(lengths))
        )
        for species, lengths in chain_lengths_by_species(csv).items()
    }


def chain_lengths_by_row(csv, isomeric=False, cache=None):
    """Longest acyl chain per candidate, in the order the encoder numbers them.

    Per ROW rather than per species, and deduplicated by canonical SMILES the way
    LipidGraphBuilder._lipid_fragment_keys deduplicates: candidate index k has to name
    the same structure on both sides. Rows of one species carry the same candidate SET
    after preprocessing/complete_lipid_candidate_sets.py, but not the same ORDER -- each
    row keeps its own annotation first -- so numbering off one arbitrary row of the
    species would hand the compatibility term the length of a structure the encoder gave
    a different index to.

    Parsing is cached by field text and by candidate string, so the whole table costs
    about as many RDKit parses as it has distinct structures.

    `cache`, when given, is a dataloader/descriptor_cache_reader.py load result
    ({"raw_to_canonical", "values", ...}): a raw candidate present there skips both the
    canonicalising parse and the length computation entirely. A raw string the cache has
    never seen (a candidate added to the table since the cache was built) falls back to
    computing it here exactly as without a cache -- an accelerator, not a second source
    of truth this table could disagree with.

    Returns a list of per-row lists; entries are None where RDKit cannot parse the
    candidate or it has no qualifying carbon, and a row with no usable candidate gets
    [None].
    """
    from preprocessing.compute_descriptors import longest_acyl_chain

    raw_to_canonical = cache["raw_to_canonical"] if cache else {}
    cached_values = cache["values"] if cache else {}
    by_field = {}
    by_smiles = {}
    per_row = []
    for field in candidate_fields_by_row(csv):
        lengths = by_field.get(field)
        if lengths is None:
            lengths = []
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
                    by_smiles[key] = (
                        cached["chain"] if cached is not None else longest_acyl_chain(key)
                    )
                lengths.append(by_smiles[key])
            lengths = lengths or [None]
            by_field[field] = lengths
        per_row.append(lengths)
    return per_row


def _candidate_arrays(per_row):
    """Per-candidate chain lengths, one array per row and each its own length.

    Ragged on purpose. A rectangle would have to be padded to the widest candidate list
    in the table -- 37 -- and every statistic computed over it would then count a row's
    last structure once per padding slot, so a row with one candidate would weigh
    thirty-seven times what it should. Each row carries exactly its own candidates
    instead, and a lookup clamps the index to the row's own length.
    """
    return [
        numpy.array(
            [numpy.nan if length is None else float(length) for length in lengths],
            dtype=float,
        )
        for lengths in per_row
    ]


def pocket_extent_by_protein(root_dir, protein_names, cache=None):
    """pocket_extent(p) for each named protein, reusing the model-facing geometry.

    Same pocket_atom_coordinates + pocket_shape that POCKET_DESCRIPTOR_NAMES' own
    pocket_extent entry uses -- this is that entry, not a second measurement of it.

    `cache`, when given, is a per-protein dict ({name: {"extent"}}); a name present
    there skips the PDB re-parse. A name the cache has never seen falls back to parsing
    it here, same as without a cache.
    """
    cache = cache or {}
    extents = {}
    for protein in protein_names:
        cached = cache.get(protein)
        if cached is not None:
            extents[protein] = cached["extent"]
            continue
        path = os.path.join(root_dir, "graphs", protein, "pocketness.pdb")
        extents[protein] = pocket_shape(pocket_atom_coordinates(path))[0]
    return extents


def coarsen_to_levels(values, edges):
    """Round `values` to the midpoint of whichever band of `edges` they fall in.

    The channel this closes: `pocket_extent` takes 35 distinct values over 35 proteins
    in [13.6, 32.0], so at full resolution it is very nearly a protein id -- eta^2
    against protein identity 0.78, squarely inside the 0.28-0.85 band that got every
    entry of POCKET_DESCRIPTOR_NAMES rejected as a fold label
    (preprocessing/pocket_descriptor_identity_check.py). Rounding to a handful of levels
    keeps the physical claim -- this cavity is longer than that one -- and destroys the
    one-to-one map that makes it a label.

    `edges` comes from the caller because it must be cut on TRAIN proteins only: edges
    fitted on all 35 would let a held-out protein help decide the band it lands in.
    """
    which = numpy.clip(numpy.searchsorted(edges, values, side="right") - 1, 0,
                       len(edges) - 2)
    centres = numpy.asarray([
        0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)
    ])
    # The outer bands are half-open, so their midpoints would be infinite; the nearest
    # finite cut is the honest stand-in and keeps the levels monotone. With exactly 2
    # bands (3 edges) that "nearest finite cut" is the SAME single interior edge for
    # both bands -- centres[0] and centres[-1] would collapse onto one number, making
    # the two bands indistinguishable as a feature (verified directly: a 2-band call
    # returned one repeated value for every input). Falling back to the values' own
    # spread keeps the two bands apart without touching the >= 3-band case at all,
    # where centres[0] != centres[-1] already.
    if len(edges) == 3:
        spread = float(numpy.std(values)) if len(values) else 1.0
        spread = spread if spread > 1e-9 else 1.0
        centres[0] = edges[1] - 0.5 * spread
        centres[-1] = edges[1] + 0.5 * spread
    else:
        centres[0] = edges[1]
        centres[-1] = edges[-2]
    return centres[which]


def raw_compatibility(csv, root_dir, isomeric=False):
    """pocket_extent(protein) - chain_length(lipid) for every row of `csv`.

    Both terms are pure geometry/chemistry -- neither reads Interaction -- so unlike
    dataloader/chemistry_prior.py's leave-one-out score, there is no label to leak and
    no special handling is needed for rows that are themselves part of a reference set.

    Both are one array per row, as long as that row's candidate list: the lipid half of
    the term depends on which candidate structure the sample is encoded as, so the
    difference does too, and which entry a sample reads is chosen where that structure is
    chosen (Dataloader.get). Entry 0 is the row's first candidate, which is what a
    run that never draws sees.

    Returns (values, missing_chain_mask): a lipid whose SMILES RDKit cannot parse, or
    that has no non-aromatic non-ring carbon at all, gets NaN rather than a silently
    wrong number; the mask says which entries those are so the caller can impute
    explicitly (raw_compatibility itself has no notion of "train", so it cannot decide
    what a safe fill value is) and log how many were affected rather than losing them
    quietly.
    """
    protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
    extents = pocket_extent_by_protein(root_dir, protein_names)

    chain = _candidate_arrays(chain_lengths_by_row(csv, isomeric))
    extent = csv["LTPProtein"].map(extents).to_numpy(dtype=float)
    values = [extent[position] - lengths for position, lengths in enumerate(chain)]
    return values, [numpy.isnan(row) for row in values]
