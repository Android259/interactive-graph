"""The chemistry-only lipid propensity score, shared by the dataloader and analysis.

One function, two callers. `analysis/null_model.py` uses it as a standalone
predictor to compare against the network. `Dataloader` (under `--chem_prior`)
attaches it to every row as a frozen input, so the network is scored against it rather
than having to re-derive it -- the point files/history/geometric_edge.md makes.
Kept in one place because the two callers must compute the identical number: a null
model that silently drifted from the number the network is judged against would make
every AUC in that file wrong without anything failing loudly.
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas

import preprocessing.compute_descriptors as compute_descriptors
from dataloader.pair_descriptor_cache import load_pair_descriptor_cache
from dataloader.pair_descriptors import (
    LIPID_DESCRIPTOR_NAMES,
    MIN_PAIR_DESCRIPTOR_NAMES,
    MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES,
    PAIR_DESCRIPTOR_NAMES,
    POCKET_CHEMISTRY_DESCRIPTOR_NAMES,
    PROTEIN_DERIVED_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
)
from preprocessing.compute_descriptors import (
    acyl_chain_count,
    aromatic_ring_count,
    heavy_atom_count,
    hbond_capacity,
    logp,
    longest_acyl_chain,
    molar_refractivity,
    pair_descriptor_value,
    protein_descriptor_table,
    ring_count,
    rotatable_bond_count,
    tpsa,
    unsaturation_count,
)
from preprocessing.compute_descriptors import npr1 as _compute_npr1
from preprocessing.compute_descriptors import npr2 as _compute_npr2

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def species_similarity(csv, data_dir):
    """Species x species Tanimoto, max over each species' candidate structures.

    A row of the interaction table can list several isomer candidates, and the compact
    matrix is indexed per distinct structure; a species therefore owns a set of rows of
    it. Taking the max is the same reduction the loader applies when it turns candidate
    similarities into one number per pair.
    """
    cache_dir = os.path.join(data_dir, "cache")
    matrix = np.load(
        os.path.join(cache_dir, "Tanimoto_compact_isomeric_matrix_uint8.npy")
    ).astype(np.float32) / 255.0
    structure_index = np.load(
        os.path.join(cache_dir, "Tanimoto_compact_isomeric_structure_index.npy")
    )
    row_ids = np.load(os.path.join(cache_dir, "Tanimoto_compact_isomeric_row_ids.npy"))

    structures_of_row = {}
    for row, structure in zip(row_ids, structure_index):
        structures_of_row.setdefault(int(row), set()).add(int(structure))
    structures_of_species = {}
    for position, species in enumerate(csv["FullIdentityOfLipid"]):
        structures_of_species.setdefault(species, set()).update(
            structures_of_row.get(position, set())
        )

    species = sorted(structures_of_species)
    index = {name: position for position, name in enumerate(species)}
    similarity = np.zeros((len(species), len(species)), dtype=np.float32)
    for position, name in enumerate(species):
        rows = matrix[sorted(structures_of_species[name]), :].max(axis=0)
        similarity[position] = [
            rows[sorted(structures_of_species[other])].max() for other in species
        ]
    return similarity, index


def molformer_species_similarity(data_dir):
    """Species x species similarity from MolFormer's mean-pooled per-lipid embedding,
    precomputed by preprocessing/build_molformer_similarity_matrix.py into
    data/molformer_species_similarity_matrix.npy (already the same
    1/(1+euclidean-distance) transform feature_similarity applies to every named
    descriptor set, see _standardised_similarity) and data/molformer_species_index.json
    (the row/column order, one species name per row).

    Same (similarity, index) 2-tuple contract as species_similarity, so
    analysis/null_model.py's --features=molformer branch is a drop-in third option
    beside tanimoto (Morgan-fingerprint) and named hand-built descriptors -- this one
    is keyed per species like species_similarity, not per structure, because
    build_molformer_similarity_matrix.py already reduces each species' candidate
    isomers to one mean-pooled vector before this file is written.
    """
    import json
    similarity = np.load(os.path.join(data_dir, "molformer_species_similarity_matrix.npy"))
    with open(os.path.join(data_dir, "molformer_species_index.json")) as handle:
        species = json.load(handle)
    index = {name: position for position, name in enumerate(species)}
    return similarity, index


def _lipid_descriptor_table(csv, data_dir=None):
    """{species: {LIPID_DESCRIPTOR_NAMES: value}}, mean over each species' candidate
    structures (pocket_lipid_compatibility.candidates_for_row's own convention: a
    candidate list is a spectroscopic ambiguity, not a choice, so every candidate
    counts equally -- taking only the first would report an arbitrary member of the
    ambiguity as if it were the lipid's own property).

    No longer self-persists ITS OWN output (the species-mean dict): averaging over a
    species' candidates is now cheap arithmetic over values that are themselves already
    cached on disk per candidate (data/lipid_descriptors.csv, see below) -- this is the
    "caches are built from the values in the table" shape the species-mean dict used to
    approximate with a second, redundant JSON file. `data_dir` is kept only for call-site
    compatibility; it was never read for anything but that now-removed persistence (the
    npr_cache lookup below always reads the project's own data/ regardless of it, exactly
    as before).
    """
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    # npr1/npr2 are conformer-based (a 10-conformer ETKDG+MMFF embed per candidate,
    # not microseconds like the other five) -- look them up in the project's on-disk
    # per-candidate lipid table first (same table dataloader/pair_descriptors.py's
    # network path and training/pair_baseline_common.py's explicit_lipid_features
    # read), and only fall back to a fresh embed on a miss, same fallback discipline as
    # descriptor_values_by_row's own `cache` parameter.
    npr_cache = load_pair_descriptor_cache(PROJECT_ROOT / "data", isomeric=False)

    # data/lipid_descriptors.csv (built by data/build_pair_descriptor_cache.py) already
    # stores every one of these under the SAME name, except "heavy" (stored as
    # "heavy_atoms" -- see that module's own build_pair_value_cache comment on the
    # rename). A cache hit is a dict lookup instead of a live RDKit reparse (or, for
    # experimental_lipid_volume, a pandas.read_csv of data/Lipid_Volumes.csv) --
    # generalized from what previously only covered npr1/npr2.
    _CACHE_MEASURE_ALIAS = {"heavy": "heavy_atoms"}

    def _cached_measure(measure, compute, smiles):
        if npr_cache is not None:
            canonical = npr_cache["raw_to_canonical"].get(smiles)
            if canonical is not None:
                cached_entry = npr_cache["values"].get(canonical)
                cache_key = _CACHE_MEASURE_ALIAS.get(measure, measure)
                if cached_entry is not None and cache_key in cached_entry:
                    return cached_entry[cache_key]
        return compute(smiles)

    measures = {
        "chain": longest_acyl_chain,
        "unsaturation": unsaturation_count,
        "hbond": hbond_capacity,
        "heavy": heavy_atom_count,
        "tail_count": acyl_chain_count,
        "logp": logp,
        "tpsa": tpsa,
        "molar_refractivity": molar_refractivity,
        "rotatable_bond_count": rotatable_bond_count,
        "aromatic_ring_count": aromatic_ring_count,
        "ring_count": ring_count,
        "npr1": _compute_npr1,
        "npr2": _compute_npr2,
        # Tail-only, see LIPID_DESCRIPTOR_NAMES.
        "tail_length_asymmetry": compute_descriptors.tail_length_asymmetry,
        "tail_length_mean": compute_descriptors.tail_length_mean,
        "tail_double_bonds": compute_descriptors.tail_double_bonds,
        "tail_unsaturation_density": compute_descriptors.tail_unsaturation_density,
        "tail_double_bond_position": compute_descriptors.tail_double_bond_position,
        "tail_logp": compute_descriptors.tail_logp,
        "tail_molar_refractivity": compute_descriptors.tail_molar_refractivity,
        "tail_heavy_atoms": compute_descriptors.tail_heavy_atoms,
        # data/Lipid_Volumes.csv lookup, not an RDKit formula -- see its own comment
        # in dataloader/pair_descriptors.py. A per-candidate miss is common (~70%);
        # per-species below, every one of the 283 distinct FullIdentityOfLipid
        # species resolves from at least one candidate.
        "experimental_lipid_volume": compute_descriptors.experimental_lipid_volume,
    }
    per_species_values = {}
    smiles_cache = {}
    for _, row in csv.iterrows():
        species = row["FullIdentityOfLipid"]
        if species in per_species_values:
            continue
        collected = {name: [] for name in measures}
        for smiles in candidates_for_row(row):
            if smiles not in smiles_cache:
                smiles_cache[smiles] = {
                    name: _cached_measure(name, fn, smiles) for name, fn in measures.items()
                }
            values = smiles_cache[smiles]
            for name in measures:
                if values[name] is not None:
                    collected[name].append(values[name])
        per_species_values[species] = {
            name: (float(np.mean(vals)) if vals else 0.0)
            for name, vals in collected.items()
        }
    return per_species_values




def _standardise_descriptor_table(table):
    """{entity: {name: value}} -> same shape, every column (descriptor name)
    standardised (mean 0, std 1) across all entities in `table`.

    For --zscore's z-scored product pair descriptors (MULTIPLICATIVE_PAIR_
    DESCRIPTOR_NAMES): multiplying two raw-scale quantities together means whichever
    has the larger absolute scale dominates the product's own variance by however
    much larger its scale happens to be -- a coincidence of units (a share bounded
    [0, 1] against an unbounded atom count, say), not a principled weighting.
    Standardising both sides first gives each an equal say regardless of native
    units, at the cost of the result no longer being a physical quantity in any
    unit -- purely a relative/joint-extremeness measure instead.
    """
    if not table:
        return table
    names = next(iter(table.values())).keys()
    entities = list(table)
    stats = {}
    for name in names:
        values = np.array([table[entity][name] for entity in entities], dtype=float)
        std = values.std()
        stats[name] = (values.mean(), std if std > 1e-9 else 1.0)
    return {
        entity: {
            name: (table[entity][name] - stats[name][0]) / stats[name][1]
            for name in names
        }
        for entity in entities
    }


def _standardised_similarity(matrix):
    """Standardise columns (mean 0, std 1) then similarity = 1/(1 + euclidean
    distance) -- bounded in (0, 1], 1 only for an identical vector, the same rough
    range Tanimoto's own [0, 1] occupies so k-nearest-neighbour weighting behaves
    comparably whichever descriptor set produced the matrix.

    Squared distance via ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b (O(N^2) + O(N*D))
    rather than the direct [:, None, :] - [None, :, :] broadcast (O(N^2*D)): fine for
    the ~283-lipid or ~35-protein case either way, but a row-granularity (pair) matrix
    is one row per interaction-table row -- N in the thousands -- where the broadcast's
    extra factor of D would blow well past available memory.
    """
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std = np.where(std > 1e-9, std, 1.0)
    standardised = (matrix - mean) / std
    sq_norms = (standardised ** 2).sum(axis=1)
    dot = standardised @ standardised.T
    sq_distance = np.clip(sq_norms[:, None] + sq_norms[None, :] - 2 * dot, 0.0, None)
    distance = np.sqrt(sq_distance)
    return (1.0 / (1.0 + distance)).astype(np.float32)


def raw_feature_matrix(csv, data_dir, names, zscore=False):
    """(entities, matrix, entity_column, column_names): the not-yet-standardised
    per-entity descriptor values `feature_similarity` turns into a similarity matrix,
    exposed on its own for a caller that needs the raw numbers themselves rather than
    a pairwise similarity built from them -- e.g. analysis/feature_identity_check.py's
    per-descriptor variance decomposition (eta^2) against identity, which needs to see
    one entry at a time rather than an already-collapsed distance.

    `column_names` gives `matrix`'s columns their names, in the same order the matrix
    itself was assembled in (lipid names, then protein names, then pair names for the
    "pair" granularity -- see below); a caller reading `matrix[:, i]` reads
    `column_names[i]`.

    See `feature_similarity` for what `names`/`zscore`/the return granularity mean --
    this function does the assembly `feature_similarity` used to do inline; that
    function is now a two-line wrapper calling this and then `_standardised_similarity`.
    """
    names = list(dict.fromkeys(names))  # de-duplicate, keep first-seen order
    if not names:
        raise ValueError("feature_similarity needs at least one descriptor name")

    pocket_names = (
        set(PROTEIN_DESCRIPTOR_NAMES)
        | set(PROTEIN_DERIVED_DESCRIPTOR_NAMES)
        | set(POCKET_CHEMISTRY_DESCRIPTOR_NAMES)
    )
    lipid_names = [n for n in names if n in LIPID_DESCRIPTOR_NAMES]
    protein_names = [n for n in names if n in pocket_names]
    pair_names = [n for n in names if n in PAIR_DESCRIPTOR_NAMES]
    unknown = sorted(set(names) - set(lipid_names) - set(protein_names) - set(pair_names))
    if unknown:
        raise ValueError(
            f"Unknown descriptor name(s): {unknown}. Known: "
            f"lipid={LIPID_DESCRIPTOR_NAMES}, protein={tuple(sorted(pocket_names))}, "
            f"pair={PAIR_DESCRIPTOR_NAMES}"
        )

    lipid_table = _lipid_descriptor_table(csv) if (lipid_names or pair_names) else {}
    protein_table = (
        protein_descriptor_table(data_dir) if (protein_names or pair_names) else {}
    )

    if pair_names or (lipid_names and protein_names):
        granularity = "pair"
    elif protein_names:
        granularity = "protein"
    else:
        granularity = "lipid"

    if granularity == "lipid":
        entities = sorted(lipid_table)
        matrix = np.array(
            [[lipid_table[entity][n] for n in lipid_names] for entity in entities],
            dtype=np.float64,
        )
        entity_column = "FullIdentityOfLipid"
        column_names = list(lipid_names)
    elif granularity == "protein":
        entities = sorted(protein_table)
        matrix = np.array(
            [[protein_table[entity][n] for n in protein_names] for entity in entities],
            dtype=np.float64,
        )
        entity_column = "LTPProtein"
        column_names = list(protein_names)
    else:
        species_col = csv["FullIdentityOfLipid"]
        protein_col = csv["LTPProtein"]
        columns = [
            species_col.map(lambda s, n=n: lipid_table[s][n]).to_numpy(dtype=float)
            for n in lipid_names
        ] + [
            protein_col.map(lambda p, n=n: protein_table[p][n]).to_numpy(dtype=float)
            for n in protein_names
        ]
        zscored_lipid_table = None
        zscored_protein_table = None
        needs_zscore_table = any(name in MIN_PAIR_DESCRIPTOR_NAMES for name in pair_names) or (
            zscore and any(name in MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES for name in pair_names)
        )
        if needs_zscore_table:
            zscored_lipid_table = _standardise_descriptor_table(lipid_table)
            zscored_protein_table = _standardise_descriptor_table(protein_table)
        for name in pair_names:
            # MIN_PAIR_DESCRIPTOR_NAMES always reads standardised values -- min() of
            # raw-scale quantities is a units artefact, not a bottleneck reading (see
            # dataloader.pair_descriptors.MIN_PAIR_DESCRIPTOR_NAMES) -- independent of
            # whether --zscore was passed.
            use_zscore = name in MIN_PAIR_DESCRIPTOR_NAMES or (
                zscore and name in MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES
            )
            lt = zscored_lipid_table if use_zscore else lipid_table
            pt = zscored_protein_table if use_zscore else protein_table
            columns.append(np.array(
                [
                    pair_descriptor_value(name, lt[s], pt[p])
                    for s, p in zip(species_col, protein_col)
                ],
                dtype=float,
            ))
        matrix = np.column_stack(columns)
        entities = list(csv.index)
        entity_column = "pair_id"
        column_names = list(lipid_names) + list(protein_names) + list(pair_names)

    return entities, matrix, entity_column, column_names


def feature_similarity(csv, data_dir, names, zscore=False):
    """Generalised null-model similarity from an arbitrary named subset of
    protein-only, lipid-only and pair descriptors -- one flag's worth of comma-
    separated names covers every combination analysis/null_model.py needs,
    instead of one hardcoded function per combination.

    `zscore`: for MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES entries only (occupancy/
    chain_extent_gap are a physical angstrom-vs-angstrom comparison and never
    standardised regardless of this flag -- see dataloader.pair_descriptors), feed
    pair_descriptor_value standardised protein/lipid values instead of raw ones, so
    the product's variance is not accidentally dominated by whichever raw input
    happens to have the larger native scale.

    `names`: any mix of
      lipid-only   : LIPID_DESCRIPTOR_NAMES (chain, unsaturation, hbond, heavy,
                     tail_count, npr1, npr2, logp, tpsa, molar_refractivity,
                     rotatable_bond_count, aromatic_ring_count, ring_count).
      protein-only : dataloader.protein_graph_builder.POCKET_DESCRIPTOR_NAMES
                     (pocket_residue_share, pocket_sasa_share, pocket_volume_per_sasa,
                     pocket_extent, pocket_elongation, pocket_flatness, ev14_q50,
                     buriedness_q50, depth_q10, apolar_sasa_share, aromatic_share,
                     hydropathy_core, hydropathy_rim), plus
                     PROTEIN_DERIVED_DESCRIPTOR_NAMES (polar_share = 1 -
                     apolar_sasa_share, PairDescriptorHead's own token name for the
                     plain pocket-shares pair; aromatic_share_coarse/
                     polar_share_coarse, the same fixed-3-band --pair_descriptor_
                     pocket_shares_coarse reads -- for an exact-token-set comparison
                     against a --descriptors_head label trained with either).
      pair         : PAIR_DESCRIPTOR_NAMES (occupancy, chain_extent_gap,
                     aromatic_contact, hbond_match, volume_fit -- see
                     dataloader.pair_descriptors.pair_descriptor_value for what each
                     one computes; every one reads whichever raw lipid/protein
                     values it needs internally, even if those are not separately
                     requested).

    Granularity -- what one ENTITY of the null model is -- follows from which of the
    three kinds `names` touches: lipid-only names alone -> one entity per lipid
    SPECIES (species_similarity/the old lipid_descriptor_similarity's own grain);
    protein-only names alone -> one entity per PROTEIN; anything spanning both kinds,
    or any pair name, -> one entity per ROW of `csv` (a specific protein-lipid pair,
    keyed by pair_id) -- neither species nor protein alone determines that vector.

    Returns (similarity, index, entity_column): the same (similarity, index) contract
    species_similarity/null_scores/null_scores_leave_one_row_out already use, plus
    entity_column naming which column of a frame (FullIdentityOfLipid / LTPProtein /
    pair_id) `index` is keyed by, so a caller building `held`/`train` frames knows
    which column to hand null_scores.
    """
    entities, matrix, entity_column, _ = raw_feature_matrix(csv, data_dir, names, zscore=zscore)
    index = {entity: position for position, entity in enumerate(entities)}
    similarity = _standardised_similarity(matrix)
    return similarity, index, entity_column


def lipid_descriptor_similarity(csv, data_dir=None):
    """Species x species similarity from every lipid-only pair_descriptor token
    (LIPID_DESCRIPTOR_NAMES -- chain, unsaturation, hbond, heavy, tail_count, npr1,
    npr2, logp, tpsa, molar_refractivity, rotatable_bond_count, aromatic_ring_count,
    ring_count). Thin LIPID_DESCRIPTOR_NAMES-only wrapper
    around feature_similarity, kept as a named entry point for existing callers --
    same (similarity, index) 2-tuple contract as species_similarity (drops
    feature_similarity's entity_column, always "FullIdentityOfLipid" at this
    granularity).

    data_dir accepted, unused: kept only so this is a drop-in for species_similarity's
    call signature (that one reads Tanimoto_compact_isomeric_*.npy from it; every value
    here comes from `csv` alone).
    """
    similarity, index, _ = feature_similarity(csv, None, LIPID_DESCRIPTOR_NAMES)
    return similarity, index


def null_scores(train, held_species, similarity, index, neighbours,
                 entity_column="FullIdentityOfLipid"):
    """Similarity-weighted train positive rate of the k nearest training entities.

    `entity_column` names which identity axis `similarity`/`index` are keyed by --
    FullIdentityOfLipid (lipid species, the default), LTPProtein, or pair_id (one
    specific protein-lipid row) -- see feature_similarity, whose descriptor-set
    granularity decides which. `held_species` (kept under its original name for the
    lipid-only callers already using it) carries that same axis' values for the rows
    being scored.
    """
    rate = train.groupby(entity_column)["Interaction"].mean()
    train_positions = np.array([index[name] for name in rate.index])
    rates = rate.to_numpy()
    scores = []
    for name in held_species:
        similarities = similarity[index[name], train_positions]
        nearest = np.argsort(-similarities)[:neighbours]
        weights = np.clip(similarities[nearest], 0.0, None)
        scores.append(float((weights * rates[nearest]).sum() / max(weights.sum(), 1e-9)))
    return np.array(scores)


def null_scores_within_protein(train, held, similarity, index, neighbours,
                                entity_column="FullIdentityOfLipid",
                                protein_column="LTPProtein"):
    """`null_scores`, but each held row asks only about ITS OWN protein.

    The difference is the whole comparison. `null_scores` above averages the training
    positive rate of the nearest entities over EVERY protein at once -- "are lipids like
    this one generally bound" -- so it is a lipid-only predictor: two held rows sharing a
    lipid get the same score however different their proteins are. This one restricts
    the reference rows to the held row's own protein first: "did THIS protein bind the
    lipids most like this one". It is the stronger competitor of the two, and the one a
    network has to beat before "it learned the pair" means anything, because a network
    also sees both sides.

    Read them as a pair, not one instead of the other. Lipid-only above the pair version
    says the signal is in the chemistry alone; the reverse says the protein matters;
    both near chance says neither is enough on this split.

    A protein with no training rows left (possible on a narrow feature granularity or a
    small block) scores nan for its held rows rather than silently borrowing another
    protein's rate; `auc` already ignores nan-free blocks only, so callers filter.
    """
    train_by_protein = {
        name: frame.groupby(entity_column)["Interaction"].mean()
        for name, frame in train.groupby(protein_column)
    }
    scores = []
    for entity, protein in zip(held[entity_column], held[protein_column]):
        rate = train_by_protein.get(protein)
        if rate is None or rate.empty:
            scores.append(float("nan"))
            continue
        train_positions = np.array([index[name] for name in rate.index])
        rates = rate.to_numpy()
        similarities = similarity[index[entity], train_positions]
        nearest = np.argsort(-similarities)[:neighbours]
        weights = np.clip(similarities[nearest], 0.0, None)
        scores.append(float((weights * rates[nearest]).sum() / max(weights.sum(), 1e-9)))
    return np.array(scores)


def null_scores_contrastive(train, held, similarity, index, neighbours,
                            entity_column="FullIdentityOfLipid",
                            protein_column="LTPProtein"):
    """`null_scores_within_protein`, but comparing the two labels separately.

    The one above averages the training positive RATE over a protein's k nearest
    training lipids, so it inherits whatever class ratio the pool was sampled at. At
    --negatives_per_positive=2 two thirds of a protein's training lipids are negatives,
    so the k nearest are usually negatives whatever the held lipid is, the score barely
    varies, and the competitor reads as chance for a reason that has nothing to do with
    the chemistry: measured on --family_only=gltp --lipid_subclass=CerP+Hex2Cer+SHexCer,
    it gives AUC 0.456 at k=1 against 0.726 at k=15 on identical rows.

    This one asks the comparison directly -- is the held lipid closer to something this
    protein BINDS than to something it does not -- as `top-k mean similarity to the
    protein's training positives` minus `the same over its training negatives`. The
    subtraction cancels the class ratio, so the number does not move with
    --negatives_per_positive, and at k=1 it is the plain "closer to a positive or to a
    negative" rule. On the block above it scores AUC 0.93-1.00 across ten seeds, which
    makes it the harder of the two bars and the one worth quoting.

    nan when the protein has no training rows on one of the two sides -- there is no
    comparison to make then, and callers already filter nan (see
    lipid_coldsplit_null_model.auc_on_scored).
    """
    positives, negatives = {}, {}
    for name, frame in train.groupby(protein_column):
        rate = frame.groupby(entity_column)["Interaction"].mean()
        positives[name] = np.array(
            [index[entity] for entity in rate.index[rate > 0.5]], dtype=int
        )
        negatives[name] = np.array(
            [index[entity] for entity in rate.index[rate <= 0.5]], dtype=int
        )
    scores = []
    for entity, protein in zip(held[entity_column], held[protein_column]):
        bound, unbound = positives.get(protein), negatives.get(protein)
        if bound is None or not len(bound) or not len(unbound):
            scores.append(float("nan"))
            continue
        row = similarity[index[entity]]
        best_bound = np.sort(row[bound])[::-1][:neighbours].mean()
        best_unbound = np.sort(row[unbound])[::-1][:neighbours].mean()
        scores.append(float(best_bound - best_unbound))
    return np.array(scores)


def fit_prior_calibration(design_train, labels_train, steps=400, learning_rate=0.5):
    """Intercept and one weight per column of `label ~ standardised(design)`.

    `design_train` is (rows, covariates) -- one or several frozen, protein/lipid-derived
    scores computed before the network exists (dataloader/chemistry_prior.py's s_chem,
    dataloader/pocket_lipid_compatibility.py's pocket-vs-chain-length term, or both).
    Fit JOINTLY when there is more than one column, with a single shared intercept,
    rather than fitting each column on its own and adding the results: two independent
    single-covariate fits would each carry their own intercept (double-counting it) and
    would not give either covariate credit only for what it explains ON TOP OF the
    other, the way a real multiple regression does.

    Why fit rather than fix weights at 1.0, and why frozen rather than a
    torch.nn.Parameter trained jointly with the rest of the network: a scalar (or a
    handful of them) and a many-parameter encoder competing by gradient descent to
    explain the SAME variance is underdetermined -- nothing pins the split between them,
    and this project's own measurements (files/results/signal_state.md, train BA reaching
    0.87-0.99 while generalisation collapses) are exactly the evidence that this network
    takes whichever shortcut is available rather than the "correct" one when several
    routes reach the same loss. Fitting on train labels ALONE, before the rest of the
    network ever sees a gradient tied to it, removes the ambiguity outright: this is the
    standard two-stage (Frisch-Waugh-Lovell) trick of residualising against nuisance
    terms with their own coefficients fit first, rather than jointly with the model that
    is meant to explain what is left over.

    Plain gradient descent rather than a closed-form solve: at most a handful of
    covariates and a few thousand rows, and the result is only ever read as frozen
    numbers -- not worth a solver dependency for.

    Returns (means, spreads, intercept, weights): means/spreads/weights are arrays of
    length `design_train.shape[1]`, in column order.
    """
    design = np.asarray(design_train, dtype=float)
    if design.ndim == 1:
        design = design[:, None]
    labels = np.asarray(labels_train, dtype=float)
    means = design.mean(axis=0)
    spreads = design.std(axis=0)
    spreads = np.where(spreads > 1e-12, spreads, 1.0)
    standardised = (design - means) / spreads
    intercept = 0.0
    weights = np.zeros(design.shape[1])
    for _ in range(steps):
        prediction = 1.0 / (1.0 + np.exp(-(intercept + standardised @ weights)))
        gradient = prediction - labels
        intercept -= learning_rate * gradient.mean()
        weights -= learning_rate * (standardised * gradient[:, None]).mean(axis=0)
    return means, spreads, float(intercept), weights


def fit_chem_calibration(s_chem_train, labels_train, steps=400, learning_rate=0.5):
    """Single-covariate convenience wrapper around fit_prior_calibration.

    Kept for the --chem_prior-only path and for its existing unit test; returns plain
    scalars instead of length-1 arrays so that call site does not have to unwrap them.
    """
    means, spreads, intercept, weights = fit_prior_calibration(
        np.asarray(s_chem_train, dtype=float)[:, None], labels_train, steps, learning_rate
    )
    return float(means[0]), float(spreads[0]), intercept, float(weights[0])


def null_scores_leave_one_row_out(frame, similarity, index, neighbours,
                                   entity_column="FullIdentityOfLipid"):
    """Per-row chemistry score for rows that are themselves part of the reference set.

    `entity_column` -- see null_scores. At row (pair_id) granularity every entity has
    exactly one row by construction, so `count == 1` always and the code below's
    "exclude this entity from its own neighbour set" branch fires for every row rather
    than the `count > 1` leave-one-out branch -- still correct, just always the same
    one of the two paths.

    `null_scores` is safe for held-out rows: under `--double_coldsplit` their species
    never appears in `train` at all (0% overlap, files/reference/marginals_and_cold_split.md
    section 6), so a held row cannot see its own label. Training rows are not so lucky
    -- every training row's species IS in the training reference set, and a species has
    similarity 1.0 to itself, so its own species is always the nearest (or tied-nearest)
    neighbour of itself. Scoring a training row against the plain per-species rate
    therefore partly scores it against its OWN label: a species with few rows has a rate
    dominated by any one of them.

    This computes the same similarity-weighted k-NN average, but for a row of species s
    the rate contributed by s itself excludes that row: `(sum - this row's label) /
    (count - 1)`, with the term skipped for the s-with-count-1 case (only this row) since
    there would be nothing left to average. Everything else -- other species' rates -- is
    ordinary, because a different species' rate does not depend on this row at all.

    `frame` doubles as both the reference set and the rows to score, which is why this
    takes one argument where `null_scores` takes two.
    """
    labels = frame["Interaction"].to_numpy(dtype=float)
    species_of_row = frame[entity_column].to_numpy()
    totals = frame.groupby(entity_column)["Interaction"].sum()
    counts = frame.groupby(entity_column)["Interaction"].count()
    all_species = sorted(totals.index)
    species_position = {name: position for position, name in enumerate(all_species)}
    positions = np.array([index[name] for name in all_species])

    scores = np.empty(len(frame), dtype=float)
    for row_index, (species, label) in enumerate(zip(species_of_row, labels)):
        similarities = similarity[index[species], positions].copy()
        rates = (totals.loc[all_species].to_numpy() - 0.0) / np.maximum(
            counts.loc[all_species].to_numpy(), 1
        )
        self_position = species_position[species]
        self_count = counts.loc[species]
        if self_count > 1:
            rates[self_position] = (totals.loc[species] - label) / (self_count - 1)
        else:
            # This row is the only one of its species: no leave-one-out rate is
            # computable, so its own species is excluded from its own neighbour set
            # rather than left leaking the single label it has.
            similarities[self_position] = -1.0
        nearest = np.argsort(-similarities)[:neighbours]
        weights = np.clip(similarities[nearest], 0.0, None)
        scores[row_index] = float(
            (weights * rates[nearest]).sum() / max(weights.sum(), 1e-9)
        )
    return scores
