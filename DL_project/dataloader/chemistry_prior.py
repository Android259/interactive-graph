"""The chemistry-only lipid propensity score, shared by the dataloader and analysis.

One function, two callers. `analysis/chemistry_null_model.py` uses it as a standalone
predictor to compare against the network. `New_dataloader` (under `--chem_prior`)
attaches it to every row as a frozen input, so the network is scored against it rather
than having to re-derive it -- the point files/interaction_signal_plan.md 4.1 makes.
Kept in one place because the two callers must compute the identical number: a null
model that silently drifted from the number the network is judged against would make
every AUC in that file wrong without anything failing loudly.
"""
import os

import numpy as np
import pandas


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


def null_scores(train, held_species, similarity, index, neighbours):
    """Similarity-weighted train positive rate of the k nearest training lipids."""
    rate = train.groupby("FullIdentityOfLipid")["Interaction"].mean()
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


def null_scores_leave_one_row_out(frame, similarity, index, neighbours):
    """Per-row chemistry score for rows that are themselves part of the reference set.

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
    species_of_row = frame["FullIdentityOfLipid"].to_numpy()
    totals = frame.groupby("FullIdentityOfLipid")["Interaction"].sum()
    counts = frame.groupby("FullIdentityOfLipid")["Interaction"].count()
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
