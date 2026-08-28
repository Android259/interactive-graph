"""The chemistry-only lipid propensity score, shared by the dataloader and analysis.

One function, two callers. `analysis/null_model.py` uses it as a standalone
predictor to compare against the network. `Dataloader` (under `--chem_prior`)
attaches it to every row as a frozen input, so the network is scored against it rather
than having to re-derive it -- the point files/interaction_signal_plan.md 4.1 makes.
Kept in one place because the two callers must compute the identical number: a null
model that silently drifted from the number the network is judged against would make
every AUC in that file wrong without anything failing loudly.
"""
import os

import numpy as np
import pandas

from dataloader.pair_descriptors import (
    LIPID_DESCRIPTOR_NAMES,
    MIN_PAIR_DESCRIPTOR_NAMES,
    MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES,
    PAIR_DESCRIPTOR_NAMES,
    PROTEIN_DERIVED_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
    acyl_chain_count,
    coarse_share,
    heavy_atom_count,
    hbond_capacity,
    longest_acyl_chain,
    pair_descriptor_value,
    unsaturation_count,
)


def species_similarity(csv, data_dir):
    """Species x species Tanimoto, max over each species' candidate structures.

    A row of the interaction table can list several isomer candidates, and the compact
    matrix is indexed per distinct structure; a species therefore owns a set of rows of
    it. Taking the max is the same reduction the loader applies when it turns candidate
    similarities into one number per pair.
    """
    matrix = np.load(
        os.path.join(data_dir, "Tanimoto_compact_isomeric_matrix_uint8.npy")
    ).astype(np.float32) / 255.0
    structure_index = np.load(
        os.path.join(data_dir, "Tanimoto_compact_isomeric_structure_index.npy")
    )
    row_ids = np.load(os.path.join(data_dir, "Tanimoto_compact_isomeric_row_ids.npy"))

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


def _lipid_descriptor_table(csv):
    """{species: {LIPID_DESCRIPTOR_NAMES: value}}, mean over each species' candidate
    structures (pocket_lipid_compatibility.candidates_for_row's own convention: a
    candidate list is a spectroscopic ambiguity, not a choice, so every candidate
    counts equally -- taking only the first would report an arbitrary member of the
    ambiguity as if it were the lipid's own property).
    """
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    measures = {
        "chain": longest_acyl_chain,
        "unsaturation": unsaturation_count,
        "hbond": hbond_capacity,
        "heavy": heavy_atom_count,
        "tail_count": acyl_chain_count,
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
                    name: fn(smiles) for name, fn in measures.items()
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


def protein_descriptor_table(data_dir):
    """{protein: {PROTEIN_DESCRIPTOR_NAMES + PROTEIN_DERIVED_DESCRIPTOR_NAMES: value}},
    read straight off data/graphs/<protein>/{coarse_graph_nodes.csv,pocketness.pdb} --
    the same recipe preprocessing/pocket_descriptor_identity_check.py uses, standalone
    (no ProteinGraphBuilder/ModelConfig instance needed: pocket_descriptor's own
    `config` argument is only used to cross-check pocket_descriptor_count, which is
    skipped when config is None).

    The two derived names (aromatic_share_coarse/polar_share_coarse) are computed
    here too, from the raw aromatic_share/apolar_sasa_share this function already
    reads, so a caller can look either kind up by name the same way -- see
    coarse_share/PROTEIN_DERIVED_DESCRIPTOR_NAMES in dataloader/pair_descriptors.py.
    """
    from pathlib import Path

    import pandas as pd

    from dataloader.protein_graph_builder import pocket_descriptor
    from dataloader.protein_graph_tensor_cache import _pocket_tensor

    graphs_dir = os.path.join(data_dir, "graphs")
    values = {}
    for protein in sorted(os.listdir(graphs_dir)):
        protein_dir = os.path.join(graphs_dir, protein)
        pocketness_path = os.path.join(protein_dir, "pocketness.pdb")
        nodes_path = os.path.join(protein_dir, "coarse_graph_nodes.csv")
        if not os.path.isfile(pocketness_path) or not os.path.isfile(nodes_path):
            continue
        vertices = pd.read_csv(nodes_path)
        pocket = _pocket_tensor(Path(pocketness_path))
        descriptor = pocket_descriptor(
            vertices, pocket, None, pocketness_path=pocketness_path
        )[0]
        raw = {
            name: float(descriptor[position])
            for position, name in enumerate(PROTEIN_DESCRIPTOR_NAMES)
        }
        raw["polar_share"] = 1.0 - raw["apolar_sasa_share"]
        raw["aromatic_share_coarse"] = coarse_share(raw["aromatic_share"])
        raw["polar_share_coarse"] = coarse_share(raw["polar_share"])
        values[protein] = raw
    return values


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

    pocket_names = set(PROTEIN_DESCRIPTOR_NAMES) | set(PROTEIN_DERIVED_DESCRIPTOR_NAMES)
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
      lipid-only   : LIPID_DESCRIPTOR_NAMES (chain, unsaturation, hbond, heavy).
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
    """Species x species similarity from the 4 lipid-only pair_descriptor tokens
    (chain, unsaturation, hbond, heavy). Thin LIPID_DESCRIPTOR_NAMES-only wrapper
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
    and this project's own measurements (files/signal_state.md, train BA reaching
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
    never appears in `train` at all (0% overlap, files/marginals_and_cold_split.md
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
