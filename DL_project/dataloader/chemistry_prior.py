"""Shared chemistry-only lipid propensity scores for loading and analysis.

analysis/baselines/knn_model.py uses them as a standalone predictor.
Dataloader --chem_prior attaches the same score as a frozen input, so the
network models the remainder (files/history/geometric_edge.md).
Keep both callers on one implementation: different reference scores would
invalidate their AUC comparisons without necessarily raising an error.
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas

import preprocessing.compute_descriptors as compute_descriptors
from dataloader.descriptor_cache_reader import load_lipid_descriptor_cache
from dataloader.descriptors import (
    LIPID_DESCRIPTOR_NAMES,
    PAIR_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES,
)
from preprocessing.compute_descriptors import (
    tail_count,
    aromatic_ring_count,
    heavy,
    hbond,
    logp,
    chain,
    molar_refractivity,
    pair_descriptor_value,
    protein_descriptor_table,
    ring_count,
    rotatable_bond_count,
    tpsa,
    unsaturation,
)
from preprocessing.compute_descriptors import pair_names_of_kind
from preprocessing.compute_descriptors import npr1 as _compute_npr1
from preprocessing.compute_descriptors import npr2 as _compute_npr2

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def species_similarity(csv, data_dir):
    """Return species-by-species Tanimoto, maximized over candidate structures.

    Each species maps to several rows of the compact structure matrix.
    Use the loader's same maximum reduction to one similarity per pair.
    """
    cache_dir = os.path.join(data_dir, "cache", "tanimoto")
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
    """Load species similarity from mean-pooled MolFormer embeddings.

    preprocessing/build_molformer_similarity_matrix.py writes
     data/molformer_species_similarity_matrix.npy and
     data/molformer_species_index.json (row/column names).
    Values use 1/(1 + Euclidean distance), as in _standardised_similarity.
    Candidates are pooled before writing, so keys are species, not structures.
    Return (similarity, index), like species_similarity; this is knn_model.py's
    --features=molformer alternative to Tanimoto and named descriptors.
    """
    import json
    similarity = np.load(os.path.join(data_dir, "molformer_species_similarity_matrix.npy"))
    with open(os.path.join(data_dir, "molformer_species_index.json")) as handle:
        species = json.load(handle)
    index = {name: position for position, name in enumerate(species)}
    return similarity, index


def _lipid_descriptor_table(csv, data_dir=None):
    """Return {species: {lipid descriptor name: mean candidate value}}.

    Average all candidates equally, as in candidates_for_row: they represent
    spectroscopic ambiguity, and the first candidate is arbitrary.
    Only candidate values are persisted, in data/lipid_descriptors.csv.
    data_dir is unused and retained for caller compatibility.
    """
    from dataloader.pocket_lipid_compatibility import candidates_for_row

    # Per-candidate lookup in the on-disk descriptor table first, computing only on a miss.
    npr_cache = load_lipid_descriptor_cache(PROJECT_ROOT / "data", isomeric=False)

    def _cached_measure(measure, compute, smiles):
        if npr_cache is not None:
            canonical = npr_cache["raw_to_canonical"].get(smiles)
            if canonical is not None:
                cached_entry = npr_cache["values"].get(canonical)
                if cached_entry is not None and measure in cached_entry:
                    return cached_entry[measure]
        return compute(smiles)

    measures = {
        "chain": chain,
        "unsaturation": unsaturation,
        "hbond": hbond,
        "heavy": heavy,
        "tail_count": tail_count,
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
    """Standardize each descriptor across entities to mean 0 and standard deviation 1.

    Keep the {entity: {name: value}} shape. Feeds the pair formulas whose kind asks
    for standardised inputs ("product" under --zscore, "bottleneck" always -- see
    compute_descriptors._pair_measure), so raw units do not set input scales (e.g.
    [0, 1] shares versus atom counts). The product then measures relative joint
    extremes, not a physical quantity. This is the analysis path only: training
    z-scores the finished descriptor column on train statistics instead.
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
    """Standardize columns, then return 1/(1 + Euclidean distance).

    Similarity lies in (0, 1], with 1 for identical vectors, comparable to
    Tanimoto's [0, 1] range for nearest-neighbor weighting.
    Compute squared distances as ||a||^2 + ||b||^2 - 2 a.b:
    O(N^2) + O(N*D) storage/work avoids an O(N^2*D) broadcast.
    This matters for thousands of interaction rows, less for ~283 lipids or
    ~35 proteins.
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
    """Return (entities, matrix, entity_column, column_names) before standardization.

    Expose feature_similarity's raw values for uses such as per-descriptor eta^2
    in analysis/feature_identity_check.py. column_names[i] labels matrix[:, i].
    Pair-granularity columns are ordered lipid, protein, then pair descriptors.
    See feature_similarity for names, zscore, and entity granularity; it wraps
    this assembly with _standardised_similarity.
    """
    names = list(dict.fromkeys(names))  # de-duplicate, keep first-seen order
    if not names:
        raise ValueError("feature_similarity needs at least one descriptor name")

    pocket_names = set(PROTEIN_DESCRIPTOR_NAMES)
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
        bottleneck = pair_names_of_kind("bottleneck")
        multiplicative = pair_names_of_kind("product")
        needs_zscore_table = any(name in bottleneck for name in pair_names) or (
            zscore and any(name in multiplicative for name in pair_names)
        )
        if needs_zscore_table:
            zscored_lipid_table = _standardise_descriptor_table(lipid_table)
            zscored_protein_table = _standardise_descriptor_table(protein_table)
        for name in pair_names:
            # Bottleneck formulas always use standardized inputs, regardless of --zscore:
            # min() across different raw units is not meaningful (compute_descriptors._pair_measure).
            use_zscore = name in bottleneck or (zscore and name in multiplicative)
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
    """Build null-model similarity from named lipid, protein, or pair descriptors.

    names can mix:
    - LIPID_DESCRIPTOR_NAMES: chain, unsaturation, hbond, heavy, tail_count,
      npr1, npr2, logp, tpsa, molar_refractivity, rotatable_bond_count,
      aromatic_ring_count, ring_count.
    - POCKET_DESCRIPTOR_NAMES: pocket_residue_share, pocket_sasa_share,
      pocket_volume_per_sasa, pocket_extent, pocket_elongation, pocket_flatness,
      ev14_q50, buriedness_q50, depth_q10, apolar_sasa_share, aromatic_share,
      hydropathy_core, hydropathy_rim; also twelve pocket chemistry/cavity
      shares and polar_share = 1 - apolar_sasa_share.
    - PAIR_DESCRIPTOR_NAMES: e.g. occupancy, chain_extent_gap, aromatic_contact,
      hbond_match, volume_fit. pair_descriptor_value loads formula inputs even
      if they were not separately requested (see dataloader.descriptors).

    zscore standardizes inputs of product formulas. Physical comparisons such
    as occupancy/chain_extent_gap keep raw angstrom-based inputs.

    Lipid-only names give one entity per species; protein-only names give one
    per protein. Mixed names or any pair formula give one per csv row (pair_id).

    Return (similarity, index, entity_column), extending the species_similarity
    and knn_scores contracts. entity_column is FullIdentityOfLipid, LTPProtein,
    or pair_id; callers use it to look up held/train rows.
    """
    entities, matrix, entity_column, _ = raw_feature_matrix(csv, data_dir, names, zscore=zscore)
    index = {entity: position for position, entity in enumerate(entities)}
    similarity = _standardised_similarity(matrix)
    return similarity, index, entity_column


def lipid_descriptor_similarity(csv, data_dir=None):
    """Build species similarity from all LIPID_DESCRIPTOR_NAMES.

    Wrap feature_similarity and drop entity_column (always FullIdentityOfLipid),
    returning (similarity, index) for existing species_similarity callers.
    The lipid names are listed in feature_similarity.
    data_dir is accepted for signature compatibility but unused: values come
    from csv, whereas species_similarity reads Tanimoto_compact_isomeric_*.npy.
    """
    similarity, index, _ = feature_similarity(csv, None, LIPID_DESCRIPTOR_NAMES)
    return similarity, index


def knn_scores(train, held_species, similarity, index, neighbours,
                 entity_column="FullIdentityOfLipid"):
    """Return the similarity-weighted positive rate of k nearest training entities.

    entity_column selects FullIdentityOfLipid (default), LTPProtein, or pair_id,
    as determined by feature_similarity. held_species retains its old argument
    name but carries keys on whichever axis similarity/index use.
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


def knn_scores_within_protein(train, held, similarity, index, neighbours,
                                entity_column="FullIdentityOfLipid",
                                protein_column="LTPProtein"):
    """Run knn_scores using only training rows of each held row's protein.

    The pooled lipid score asks whether similar lipids bind across all proteins;
    this score asks whether this protein binds them. Compare both: a higher
    pooled score suggests chemistry-only signal, a higher within-protein score
    suggests protein context matters, and chance scores suggest neither suffices.
    The network sees both partners and should be compared with this stronger
    reference before attributing its score to pair learning.

    Return NaN when the protein has no training rows; do not borrow other
    proteins' rates. Callers filter NaNs before AUC evaluation.
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


def knn_scores_contrastive(train, held, similarity, index, neighbours,
                            entity_column="FullIdentityOfLipid",
                            protein_column="LTPProtein"):
    """Subtract mean top-k negative similarity from mean top-k positive similarity.

    Use each protein's training rows, comparing labels separately. At k=1 this
    asks whether the nearest positive or nearest negative is closer.
    Unlike knn_scores_within_protein's pooled rate, separate label averages
    remove its direct dependence on the sampled class ratio. At ratio 2,
    negatives occupy two thirds of the pool and can dominate pooled neighbors.

    Recorded example: --family_only=gltp --lipid_subclass=CerP+Hex2Cer+SHexCer.
    The pooled method scored AUC 0.456 at k=1 and 0.726 at k=15 on the same rows;
    this method scored 0.93-1.00 across ten seeds, a stronger reference.

    Return NaN if either label has no training rows for the protein.
    analysis/baselines/knn_model.py auc_on_scored filters these values.
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
    """Fit label ~ standardized(design): one intercept and one weight per covariate.

    design_train has shape (rows, covariates), containing frozen scores such as
    s_chem, pocket-versus-chain compatibility, or both. Fit columns jointly:
    separate fits would duplicate intercepts and ignore their shared contribution.

    Fit on training labels before network optimization, then freeze the result.
    This fixes the allocation between nuisance scores and the encoder, instead of letting both compete by gradient descent or setting weights to 1.
    The two-stage residualization follows the Frisch-Waugh-Lovell rationale.
    Project motivation: train BA 0.87-0.99 with collapsing generalization
    (files/results/signal_state.md) shows the network can exploit shortcuts.

    Use plain gradient descent for a few covariates and thousands of rows,
    without another solver dependency. Results are read only as frozen numbers.
    Return (means, spreads, intercept, weights); arrays follow design column
    order and have length design_train.shape[1].
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
    """Wrap fit_prior_calibration for the --chem_prior-only path and its unit test.

    Return scalars instead of length-1 arrays for existing callers.
    """
    means, spreads, intercept, weights = fit_prior_calibration(
        np.asarray(s_chem_train, dtype=float)[:, None], labels_train, steps, learning_rate
    )
    return float(means[0]), float(spreads[0]), intercept, float(weights[0])


def knn_scores_leave_one_row_out(frame, similarity, index, neighbours,
                                   entity_column="FullIdentityOfLipid"):
    """Score reference rows with their own labels excluded from species rates.

    frame provides both reference and scored rows. For a row of species s, use
    (sum - row_label)/(count - 1) for s; exclude s entirely when count == 1.
    Other species keep ordinary rates. A species is its own nearest neighbor
    (similarity 1), so using its full rate would leak the scored row's label.

    At pair_id granularity each entity has one row, so the count == 1 branch
    always applies. entity_column follows knn_scores.
    Held-out knn_scores is safe under --double_coldsplit because species overlap
    is 0% (files/reference/marginals_and_cold_split.md section 6).
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
            # Exclude singleton species: removing this row leaves no rate to estimate.
            similarities[self_position] = -1.0
        nearest = np.argsort(-similarities)[:neighbours]
        weights = np.clip(similarities[nearest], 0.0, None)
        scores[row_index] = float(
            (weights * rates[nearest]).sum() / max(weights.sum(), 1e-9)
        )
    return scores


MOLFORMER_EMBEDDING_FILE = "lipid_SMILES_embedding_deterministic.pkl"


def molformer_canonical_key(smiles):
    """Return the default non-isomeric MoLFormer key (isomericSmiles=False).

    Match LipidGraphBuilder._canonical_embedding_key and the deterministic table.
    """
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False)


def species_embeddings(csv, smiles_encoding):
    """Return {species: 768-dim vector}, mean-pooled over tokens and candidates.

    Use each FullIdentityOfLipid's first candidate list, as in
    feature_identity_check.candidate_matrix; that list is a species property
    shared by its rows.
    """
    import torch

    from dataloader.pocket_lipid_compatibility import candidates_for_row

    vectors, missing_species, missing_keys = {}, [], set()
    seen = set()
    for _, row in csv.iterrows():
        species = row["FullIdentityOfLipid"]
        if species in seen:
            continue
        seen.add(species)
        pooled = []
        for candidate in candidates_for_row(row):
            key = molformer_canonical_key(candidate)
            if key is None:
                continue
            encoding = smiles_encoding.get(key)
            if encoding is None:
                missing_keys.add(key)
                continue
            pooled.append(torch.as_tensor(encoding).squeeze(0).mean(dim=0).numpy())
        if pooled:
            vectors[species] = np.mean(np.stack(pooled), axis=0)
        else:
            missing_species.append(species)
    return vectors, missing_species, missing_keys
