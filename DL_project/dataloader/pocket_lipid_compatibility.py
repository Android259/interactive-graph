"""Compare pocket dimensions with candidate lipid dimensions.

Compute pocket_extent(p) - chain_length(l). Extent is the PCA-axis span used
by POCKET_DESCRIPTOR_NAMES (graphs_builders/protein_graph_builder);
length is the longest unbranched aliphatic run.
See files/reference/pocket_lipid_compatibility.md for measurements against
the chemistry prior in files/history/geometric_edge.md.

Protein-only descriptors showed family eta^2 0.28-0.85 on 35 proteins and
9 families (analysis/feature_identity_check.py). A joint quantity varies
with the lipid as well, instead of identifying only the protein.

Dataloader --pocket_compat_prior adds the frozen calibrated term to the
logit. If --chem_prior is enabled, both are calibrated jointly through
chemistry_prior.py.
"""
import os

import numpy
from rdkit import Chem

from preprocessing.compute_descriptors import (
    pocket_atom_coordinates,
    pocket_shape,
)

# Missing-structure sentinels shared with analysis/protein_profile_probe.py
# (mode correlate), which imports EMPTY instead of keeping a copy.
EMPTY = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def smiles_for_row(row):
    """Return the first usable candidate, or None.

    Prefer SmileGlobal, then SmileFragment, as the former chain_length_per_protein
    did. Fields use semicolon-separated candidates; candidates_for_row returns all.
    """
    candidates = candidates_for_row(row)
    return candidates[0] if candidates else None


def candidates_for_row(row):
    """Return all candidate structures for a row, in field order.

    Candidates are isomers unresolved by the spectrum. Callers average the full
    list, as candidate-averaged evaluation averages predictions; choosing the
    first would make the value depend on annotation order.
    """
    for column in ("SmileGlobal", "SmileFragment"):
        text = str(row.get(column, "")).strip()
        if text in EMPTY:
            continue
        parts = [part.strip() for part in text.split(";")]
        return [part for part in parts if part and part not in EMPTY]
    return []


def candidate_fields_by_row(csv):
    """Apply candidates_for_row to a table, returning one tuple per row.

    Avoid iterrows Series creation and memoize repeated raw column texts.
    Recorded cost: 21 measures x 11018 rows created 221k Series, taking 4.8 s
    of a 9.1 s build without RDKit parsing.
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
            # Use the first non-sentinel column, as candidates_for_row does.
            # If all its parts filter out, return empty instead of trying the next column.
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
    """Return longest acyl-chain lengths per candidate, keyed by FullIdentityOfLipid.

    Compute once per species instead of repeating RDKit parsing and BFS for its
    hundreds of protein rows. Keep candidates separate: PC(34:1) as 16:0/18:1
    has longest chain 18, while 14:0/20:1 has 20. Training draws and averaged
    evaluation select candidates, so the value must describe the encoded structure.

    Use NaN for failed RDKit parses or candidates without qualifying carbon.
    A species with no usable candidate gets [NaN]; callers choose imputation
    (see raw_compatibility_matrix).
    """
    # Defer the descriptors import to avoid a cycle: descriptors imports
    # candidates_for_row from this module.
    from preprocessing.compute_descriptors import chain

    lengths = {}
    for species, rows in csv.groupby("FullIdentityOfLipid"):
        candidates = []
        for _, row in rows.iterrows():
            candidates = candidates_for_row(row)
            if candidates:
                break
        measured = [chain(smiles) for smiles in candidates]
        lengths[species] = numpy.array(
            [numpy.nan if length is None else float(length) for length in measured]
            or [numpy.nan],
            dtype=float,
        )
    return lengths


def chain_length_by_species(csv):
    """Return mean candidate longest-chain length per species.

    Use for candidate-blind analysis and train-only statistics, independent of
    sample draws. Per-sample values come from chain_lengths_by_row in encoder order.
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
    """Return per-row candidate chain lengths in encoder order.

    Deduplicate canonical SMILES as LipidGraphBuilder._lipid_fragment_keys does.
    Rows of a species share a candidate set after complete_lipid_candidate_sets.py,
    but keep their own annotation first. Index k must identify the same structure
    in the encoder and compatibility term, so do not use one species-wide order.

    Cache field texts and candidate strings: parsing scales with unique structures.
    Optional cache is descriptor_cache_reader.load_lipid_descriptor_cache's
    {"raw_to_canonical", "values", ...}. Hits skip canonicalization and computation;
    new raw strings fall back to direct computation, preserving the source of truth.

    Return per-row lists, with None for failed parses or no qualifying carbon.
    A row without usable candidates gets [None].
    """
    from preprocessing.compute_descriptors import chain

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
                        cached["chain"] if cached is not None else chain(key)
                    )
                lengths.append(by_smiles[key])
            lengths = lengths or [None]
            by_field[field] = lengths
        per_row.append(lengths)
    return per_row


def _candidate_arrays(per_row):
    """Return ragged candidate-chain arrays, one per row.

    Padding to the maximum 37 candidates would overweight a one-candidate row
    37-fold by repeating its last value. Keep only real candidates; lookups
    clamp to each row's own length.
    """
    return [
        numpy.array(
            [numpy.nan if length is None else float(length) for length in lengths],
            dtype=float,
        )
        for lengths in per_row
    ]


def pocket_extent_by_protein(root_dir, protein_names, cache=None):
    """Return pocket_extent for each protein using the model's geometry.

    Reuse pocket_atom_coordinates and pocket_shape, as POCKET_DESCRIPTOR_NAMES does.
    Optional cache is {protein: {"extent": value}}. Hits skip PDB parsing;
    missing names fall back to parsing.
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
    """Round values to the midpoint of their edge band.

    Pocket extent has 35 distinct values for 35 proteins, spanning [13.6, 32.0].
    Its protein-identity eta^2 is 0.78, within the 0.28-0.85 range of rejected
    POCKET_DESCRIPTOR_NAMES family proxies (analysis/feature_identity_check.py).
    A few levels preserve size ordering while removing unique values.

    Callers must fit edges on training proteins only. Fitting all 35 would let
    held-out proteins influence their own bands.
    """
    which = numpy.clip(numpy.searchsorted(edges, values, side="right") - 1, 0,
                       len(edges) - 2)
    centres = numpy.asarray([
        0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)
    ])
    # Use the nearest finite cut for infinite outer-band midpoints.
    # With two bands, both would use the same interior cut and collapse to one value;
    # use the observed spread to keep them distinct. The >=3-band case is unchanged.
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
    """Return pocket_extent(protein) - chain_length(candidate) per row.

    Return (values, missing_chain_mask), both ragged arrays in candidate order.
    Dataloader.get selects the encoded candidate; index 0 is the fixed first one.
    Neither term reads Interaction, so reference rows need no leave-one-out handling.

    Failed parses or candidates without non-aromatic, non-ring carbon get NaN.
    The mask lets callers impute and log missing values explicitly. This function
    has no training split and cannot choose a safe fill value itself.
    """
    protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
    extents = pocket_extent_by_protein(root_dir, protein_names)

    chain = _candidate_arrays(chain_lengths_by_row(csv, isomeric))
    extent = csv["LTPProtein"].map(extents).to_numpy(dtype=float)
    values = [extent[position] - lengths for position, lengths in enumerate(chain)]
    return values, [numpy.isnan(row) for row in values]
