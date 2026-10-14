"""Interaction-pool and batch sampling utilities."""

import re

import numpy as np
import pandas
import torch

from architecture.mlp_utils import build_mlp

# Full-batch steps for the learned negative-prior scorer (learned_prior_reference).
# A few thousand rows by a few dozen standardised features: this converges well
# inside it and costs about a second, once per dataset build.
LEARNED_PRIOR_STEPS = 400


def split_and_sample_interactions(csv, seed, unlabeled_fraction=0.056):
    """Keep every positive row and sample only rows labeled as unlabeled."""
    positive_pairs = csv[csv["Interaction"] == 1].copy()
    unlabeled_pairs = csv[csv["Interaction"] == 0].sample(
        frac=unlabeled_fraction,
        random_state=seed,
    ).copy()
    return positive_pairs, unlabeled_pairs


def _shared_similarities(pool, candidates, positives):
    """Per-candidate max similarity to the positives of its own sampling group.

    The original reduction, and the one every lipid-axis pool keeps: a candidate is
    weighted by how close it is to ANYTHING the group is already positive for. On a
    lipid axis that reads as "a lipid like the ones this protein binds", because the
    group is a protein or a family of them.

    None (fall back to plain uniform sampling) when none of the group's positives have a
    similarity entry.
    """
    positions = [
        pool.index[key]
        for key in pandas.unique(pool.row_keys(positives))
        if key in pool.index
    ]
    if not positions:
        return None
    return np.array(
        [
            pool.similarity[pool.index[key], positions].max()
            if key in pool.index
            else 0.0
            for key in pool.row_keys(candidates)
        ]
    )


def conditioned_reference(pool, csv, excluded_groups=None):
    """Matrix positions of the positives a candidate is compared against, keyed by the
    coordinate the candidate SHARES with them.

    Why a protein-axis pool cannot use `_shared_similarities`. That reduction asks "is
    this candidate close to anything the group already binds", and on a protein axis the
    answer is 1.0 for nearly every candidate: the candidate's own protein is itself one
    of the group's positive proteins (it binds something, just not this lipid), and a
    protein is identical to itself. Measured on the table with the per-family sampler,
    all three of identity/blosum62/tmscore gave mean 1.000 steered either way -- the
    flag was wired up and could not move anything.

    The question that is actually the mirror of the lipid one conditions on the OTHER
    coordinate instead:

        lipid axis    how like the lipids THIS PROTEIN binds is the candidate's lipid
        protein axis  how like the proteins THAT BIND THIS LIPID is the candidate's protein

    Conditioning this way also excludes the candidate's own entity for free: a row is a
    candidate because it is labeled 0, so its protein is by definition not among the
    proteins positive for its lipid. Nothing has to be filtered out by hand.

    The reference spans every training family rather than the candidate's own group,
    because "which proteins bind this lipid" is a cross-family question by nature -- a
    group of one protein would leave it empty. `excluded_groups` families are dropped
    from it: their rows become validation/test, and letting them decide which TRAIN
    negatives get drawn would leak the held-out block into training, the same reason
    those groups are exempt from being steered at all.
    """
    rows = csv[csv["Interaction"] == 1]
    if excluded_groups:
        families = rows["ProteinDomain"].astype(str).str.lower()
        rows = rows[~families.isin({str(group).lower() for group in excluded_groups})]
    positions = {}
    for value, key in zip(rows[pool.condition_column], pool.row_keys(rows)):
        if key in pool.index:
            positions.setdefault(value, set()).add(pool.index[key])
    return {value: sorted(found) for value, found in positions.items()}


def _conditioned_similarities(pool, candidates, reference):
    """Per-candidate max similarity to the positives `reference` pairs it with.

    A candidate whose shared coordinate has no positive anywhere in training (a lipid
    nothing is known to bind) scores 0.0 rather than being dropped: the quota is what
    every sampler here promises to fill, and 0.0 leaves it to the uniform remainder of
    the mass exactly as an unseen key already does.
    """
    if not reference:
        return None
    return np.array(
        [
            pool.similarity[pool.index[key], reference[value]].max()
            if key in pool.index and value in reference
            else 0.0
            for value, key in zip(
                candidates[pool.condition_column], pool.row_keys(candidates)
            )
        ]
    )


def cell_prior_reference(pool, csv, excluded_groups=None):
    """Train positive rate per (protein, lipid subclass) cell, plus the global fallback.

    The naive competitor's own recipe (analysis/baselines/protein_subclass_label_baseline.py):
    the rate is estimated on the rows a run can see, and a cell absent from them falls
    back to the overall rate rather than to zero -- a cell nobody measured is not
    evidence of a non-binder. `excluded_groups` families are dropped for the reason
    `conditioned_reference` gives: their rows become validation/test, and letting their
    labels pick train negatives would leak the held-out block.

    A rate is a score in [0, 1] already, so it needs no transform before the weighting:
    "hard" puts the mass on the cells the lookup table calls positive, "dissimilar" on
    the ones it calls negative.
    """
    rows = csv
    if excluded_groups:
        families = rows["ProteinDomain"].astype(str).str.lower()
        rows = rows[~families.isin({str(group).lower() for group in excluded_groups})]
    labels = rows["Interaction"].astype(float)
    overall = float(labels.mean()) if len(labels) else 0.0
    rates = labels.groupby(pool.cell_keys(rows)).mean().to_dict()
    return {"rates": rates, "overall": overall}


def _cell_prior_scores(pool, candidates, reference):
    if not reference:
        return None
    rates, overall = reference["rates"], reference["overall"]
    return np.array(
        [rates.get(key, overall) for key in pool.cell_keys(candidates)]
    )


def learned_prior_reference(pool, csv, excluded_groups=None, seed=0):
    """Fit the small MLP on the training-visible labels; return one score per row.

    Fit here rather than inside the pool for the reason `cell_prior_reference` is here:
    only the sampler knows `excluded_groups`, and a held-out family's labels must not
    decide which train negatives get drawn.

    The global torch RNG is saved and restored around the fit. That is not tidiness: the
    dataset is built after `seed_everything`, and the model's own initialisation and the
    DataLoader's shuffle draw from that same stream afterwards. Consuming it here would
    silently shift every one of them, so a run with this flag would differ from the base
    in more than the negatives it drew -- which is exactly the comparison the flag
    exists to make.
    """
    rows = csv
    mask = np.ones(len(csv), dtype=bool)
    if excluded_groups:
        families = csv["ProteinDomain"].astype(str).str.lower()
        mask = ~families.isin({str(group).lower() for group in excluded_groups}).to_numpy()
        rows = csv[mask]
    if not mask.any():
        return None

    features = np.asarray(pool.features, dtype=np.float64)
    mean = features[mask].mean(axis=0)
    std = features[mask].std(axis=0)
    std = np.where(std > 1e-9, std, 1.0)
    standardised = (features - mean) / std
    labels = rows["Interaction"].to_numpy(dtype=np.float64)

    state = torch.get_rng_state()
    try:
        torch.manual_seed(int(seed))
        config = pool.config
        model = torch.nn.Sequential(
            build_mlp(
                standardised.shape[1], config.m * config.hiddim, config.hiddim, config
            ),
            torch.nn.Linear(config.hiddim, 1),
        )
        x_fit = torch.as_tensor(standardised[mask], dtype=torch.float32)
        y_fit = torch.as_tensor(labels, dtype=torch.float32).reshape(-1, 1)
        positives = float(y_fit.sum())
        # The table is ~6% positive; without this the scorer collapses onto the majority
        # class and every candidate gets the same near-zero score, which is a uniform
        # draw wearing a flag's name.
        pos_weight = torch.tensor(
            [(len(y_fit) - positives) / max(positives, 1.0)], dtype=torch.float32
        )
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        optimiser = torch.optim.Adam(model.parameters(), lr=1e-3)
        model.train()
        for _ in range(LEARNED_PRIOR_STEPS):
            optimiser.zero_grad()
            loss = loss_fn(model(x_fit), y_fit)
            loss.backward()
            optimiser.step()
        model.eval()
        with torch.no_grad():
            scores = torch.sigmoid(
                model(torch.as_tensor(standardised, dtype=torch.float32))
            ).reshape(-1).numpy()
    finally:
        torch.set_rng_state(state)

    return pandas.Series(scores.astype(np.float64), index=csv.index)


def _learned_prior_scores(pool, candidates, reference):
    if reference is None:
        return None
    return reference.loc[candidates.index].to_numpy()


def reference_for(pool, csv, excluded_groups=None, seed=0):
    """Whatever `candidate_similarities` needs per pool kind, built once per draw."""
    if pool.kind == "cell_prior":
        return cell_prior_reference(pool, csv, excluded_groups)
    if pool.kind == "learned_prior":
        return learned_prior_reference(pool, csv, excluded_groups, seed)
    if pool.condition_column:
        return conditioned_reference(pool, csv, excluded_groups)
    return None


def candidate_similarities(pool, candidates, positives, reference):
    """One number per candidate, from whichever reference this pool calls for."""
    if pool.kind == "cell_prior":
        return _cell_prior_scores(pool, candidates, reference)
    if pool.kind == "learned_prior":
        return _learned_prior_scores(pool, candidates, reference)
    if pool.condition_column is None:
        return _shared_similarities(pool, candidates, positives)
    return _conditioned_similarities(pool, candidates, reference)


def _hard_negative_weights(sims, share):
    """Sampling weight per candidate, blending similarity-hardness with uniform.

    `share` of the mass goes to candidates by how similar they are to something already
    known to bind (`candidate_similarities`) -- a hard negative, close enough to look
    like a binder yet labeled unlabeled. The rest of the mass stays uniform, so a group
    whose positives have no close negatives in its pool still draws its full quota
    instead of concentrating on the handful nearest zero similarity.
    """
    n = len(sims)
    sims = np.clip(sims, 0.0, None)
    total = sims.sum()
    similarity_mass = sims / total if total > 0 else np.full(n, 1.0 / n)
    uniform_mass = np.full(n, 1.0 / n)
    return share * similarity_mass + (1 - share) * uniform_mass


def _dissimilar_negative_weights(sims, share):
    """Sampling weight per candidate, blending similarity-DISTANCE with uniform.

    The mirror of `_hard_negative_weights` over the same numbers: `share` of the mass
    goes to candidates by `1 - similarity`, so the negatives a group trains against are
    the ones furthest from anything it is known to bind. The rest of the mass stays
    uniform for the same reason as there.

    Why one would want this rather than hard negatives: a uniform draw over a panel
    whose lipids are largely congeneric hands a protein many near-duplicates of its own
    positives as negatives, so a decision rule can only separate them by the base rate.
    Steering AWAY spreads the negatives over the panel's chemistry instead, which is the
    opposite trade from hard mining -- an easier separation per pair, over a wider span
    of chemistry. The two directions are mutually exclusive by configuration.
    """
    n = len(sims)
    distances = np.clip(1.0 - np.clip(sims, 0.0, 1.0), 0.0, None)
    total = distances.sum()
    distance_mass = distances / total if total > 0 else np.full(n, 1.0 / n)
    uniform_mass = np.full(n, 1.0 / n)
    return share * distance_mass + (1 - share) * uniform_mass


def _weighted_negative_draw(candidates, draw_n, weights, seed):
    """Draw `draw_n` of `candidates` without replacement, weighted by `weights`.

    pandas' own weighted `.sample(replace=False)` refuses whenever one candidate's
    normalized weight alone exceeds `1 / draw_n` (pandas/core/sample.py's
    `size * weights.max() > 1` guard), which a concentrated pool (one very close
    candidate, the rest at similarity 0) hits routinely. numpy's sequential
    without-replacement draw has no such restriction, so it takes over for this path.

    numpy does refuse one thing: a without-replacement draw asking for more items than
    there are NON-ZERO weights. At `share=1.0` nothing is left uniform, so a candidate
    whose own Tanimoto reduction is exactly 0 gets weight exactly 0 -- a negative
    identical to one of the group's positives under "dissimilar", one with no similarity
    at all to any of them under "hard". Where the quota exceeds the number of candidates
    that survive that, the steered ones are taken first and the rest of the quota is
    filled uniformly from the zero-weight remainder. The quota is what every sampler in
    this module promises to draw in full -- steering is a preference over which
    candidates fill it, never a filter that shrinks it -- which is the same reason
    `_hard_negative_weights` keeps `1 - share` uniform at every share below 1.
    """
    rng = np.random.default_rng(seed)
    probabilities = weights / weights.sum()
    steerable = int((probabilities > 0).sum())
    if steerable >= draw_n:
        chosen = rng.choice(
            len(candidates), size=draw_n, replace=False, p=probabilities
        )
        return candidates.iloc[chosen]
    steered = rng.choice(
        len(candidates), size=steerable, replace=False, p=probabilities
    )
    remainder = np.setdiff1d(np.arange(len(candidates)), steered)
    filler = rng.choice(remainder, size=draw_n - steerable, replace=False)
    return candidates.iloc[np.concatenate([steered, filler])]


def _sample_group_balanced_negatives(
    csv,
    seed,
    group_column,
    ratio=1,
    strata=None,
    hard_negative_pool=None,
    excluded_groups=None,
    hard_negative_share=0.5,
    negative_mode="hard",
):
    """Sample `ratio` negatives per positive within each group.

    `ratio` is 1 for the exact 1:1 the samplers were written for. Higher values keep
    proportionally more of the negative pool: at 1 the working set is 1512 of the
    table's 11018 rows, and the 9506 rows dropped are the record of which lipids each
    protein does NOT bind. The ratio is per group, so raising it does not reintroduce
    the between-protein prior the grouping exists to remove -- every group keeps the
    same pos:neg proportion, just a coarser one. What it does change is the class prior
    the loss sees, which is `--class_weights`' job.

    `hard_negative_pool`, if given, is a `dataloader.similarity_pool.SimilarityPool`
    -- a similarity matrix, its index, and the axis a row is identified on (lipid
    species, protein, or pair): negatives are then drawn weighted by that similarity
    instead of uniformly, whichever of the sources built it. `negative_mode` picks the
    direction --
    "hard" steers the draw TOWARD candidates similar to the group's own positives
    (`_hard_negative_weights`, `--hard_negative_mining`), "dissimilar" steers it AWAY
    from them (`_dissimilar_negative_weights`, `--dissimilar_negative_mining`) -- and
    `hard_negative_share` is the steered mass in either direction. `excluded_groups`,
    if given alongside the pool, exempts any group whose ProteinDomain is in it from
    the reweighting -- those rows become validation/test after the coming split, and
    must be drawn exactly as a run without either flag would draw them, so enabling one
    changes what training sees and nothing about what is measured.
    """
    if ratio < 1:
        raise ValueError(f"negatives per positive must be at least 1, got {ratio}")
    if negative_mode not in ("hard", "dissimilar"):
        raise ValueError(
            f"negative_mode must be 'hard' or 'dissimilar', got {negative_mode!r}"
        )
    groups = csv[group_column].str.lower()
    family_of_group = None
    if hard_negative_pool is not None and excluded_groups:
        family_of_group = csv.groupby(groups)["ProteinDomain"].first().str.lower()
    reference = None
    if hard_negative_pool is not None:
        # Built once from the whole training side, not per group -- see
        # `conditioned_reference` for why a protein axis cannot use the group, and
        # `cell_prior_reference` for the naive-prior kind.
        reference = reference_for(hard_negative_pool, csv, excluded_groups, seed)
    if strata is not None:
        # Matching per (group, stratum) instead of per group. The cold split's second
        # axis needs this: without it the negatives of a protein are drawn from its
        # whole lipid panel, and if they all land in classes that later leave training,
        # the protein arrives in the train block with positives and nothing to contrast
        # them against -- one-sided, unfixable by weighting, and not something to paper
        # over by discarding it. Matching inside each stratum draws the two sides of
        # every protein from the same side of the coming cut, so each side of the cut
        # is balanced per protein on its own.
        groups = groups + "\x00" + strata.astype(str)
    is_positive = csv["Interaction"] == 1
    is_negative = csv["Interaction"] == 0
    parts = []
    for group in sorted(groups.dropna().unique()):
        group_mask = groups == group
        positive_count = int((is_positive & group_mask).sum())
        if positive_count == 0:
            continue
        candidates = csv[is_negative & group_mask]
        draw_n = min(positive_count * ratio, len(candidates))
        if draw_n == 0:
            continue
        weights = None
        if hard_negative_pool is not None:
            plain_group = group.split("\x00", 1)[0] if strata is not None else group
            group_excluded = (
                family_of_group is not None and family_of_group.get(plain_group) in excluded_groups
            )
            if not group_excluded:
                sims = candidate_similarities(
                    hard_negative_pool,
                    candidates,
                    csv[is_positive & group_mask],
                    reference,
                )
                if sims is not None:
                    weigh = (
                        _dissimilar_negative_weights
                        if negative_mode == "dissimilar"
                        else _hard_negative_weights
                    )
                    weights = weigh(sims, hard_negative_share)
        if weights is None:
            parts.append(candidates.sample(n=draw_n, random_state=seed))
        else:
            parts.append(
                _weighted_negative_draw(candidates, draw_n, weights, seed)
            )
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def sample_family_balanced_negatives(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5, negative_mode="hard",
):
    """Sample negatives per protein family to match its positive count (1:1).

    Instead of the global fixed-fraction subsample of `split_and_sample_interactions`,
    this draws, for each of the protein families in `ProteinDomain`, exactly as many
    unlabeled rows as that family has positives, so the working set is 1:1
    positive:negative both globally and within every family. Sampling is seeded
    (`random_state=seed`) and preserves the original interaction-CSV row index.

    `hard_negative_pool`/`excluded_groups`/`hard_negative_share`: see
    `_sample_group_balanced_negatives`.
    """
    return _sample_group_balanced_negatives(
        csv, seed, "ProteinDomain", ratio, strata,
        hard_negative_pool, excluded_groups, hard_negative_share, negative_mode,
    )


def split_and_sample_family_balanced_interactions(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5, negative_mode="hard",
):
    """Keep every positive and sample per-family-matched negatives (1:1)."""
    positive_pairs = csv[csv["Interaction"] == 1].copy()
    unlabeled_pairs = sample_family_balanced_negatives(
        csv, seed, ratio, strata, hard_negative_pool, excluded_groups,
        hard_negative_share, negative_mode,
    ).copy()
    return positive_pairs, unlabeled_pairs


def sample_protein_balanced_negatives(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5, negative_mode="hard",
):
    """Sample negatives per protein to match its positive count (1:1).

    `sample_family_balanced_negatives` matches counts per `ProteinDomain`, which
    leaves individual proteins inside a family free to skew: the family draws its
    negatives from one shared pool, so a positive-rich protein keeps far more
    positives than negatives while a positive-poor one gets the opposite. This
    matches counts per `LTPProtein` instead, which balances every family as well
    (a sum of balanced parts is balanced) and additionally removes the per-protein
    prior a model could otherwise learn as "this protein is usually positive".
    Sampling is seeded (`random_state=seed`) and preserves the original
    interaction-CSV row index.

    `hard_negative_pool`/`excluded_groups`/`hard_negative_share`: see
    `_sample_group_balanced_negatives`.
    """
    return _sample_group_balanced_negatives(
        csv, seed, "LTPProtein", ratio, strata,
        hard_negative_pool, excluded_groups, hard_negative_share, negative_mode,
    )


def split_and_sample_protein_balanced_interactions(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5, negative_mode="hard",
):
    """Keep every positive and sample per-protein-matched negatives (1:1)."""
    positive_pairs = csv[csv["Interaction"] == 1].copy()
    unlabeled_pairs = sample_protein_balanced_negatives(
        csv, seed, ratio, strata, hard_negative_pool, excluded_groups,
        hard_negative_share, negative_mode,
    ).copy()
    return positive_pairs, unlabeled_pairs


# lipid_class_series and the ambiguity table live in dataloader.lipid_classes so the
# preprocessing scripts can apply the same rule without importing torch. Re-exported
# here because everything already reaches for them through this module.
from dataloader.lipid_classes import (  # noqa: F401
    AMBIGUOUS_CLASS_RESOLUTION,
    class_level_positive_labels,
    head_group_class,
    lipid_class_series,
)


def sample_lipid_class_balanced_negatives(
    csv, seed, group_column="ProteinDomain", ratio=1, hard_negative_pool=None,
    excluded_groups=None, hard_negative_share=0.5, negative_mode="hard",
):
    """Sample negatives per (group, lipid class) cell to match its positive count (1:1).

    `sample_protein_balanced_negatives` removes the per-protein prior ("this protein is
    usually positive") but leaves the per-lipid-class prior untouched: the negatives it
    draws for a protein come from that protein's whole lipid panel, so a class the
    screen rarely calls positive stays rare among the negatives too, and the model can
    still answer from the lipid class alone. Matching inside each (group, class) cell
    removes that second marginal, leaving only the pairing itself to learn from.

    This bites hardest where the two priors disagree, which on this dataset is most
    places: GLTP's positives are sphingolipids and START's are phosphatidylcholines, so
    a class-blind sampler hands the model a usable "SM implies positive" rule that does
    not survive the change of family.

    Cells with no positives contribute nothing, as in the other samplers.

    `group_column` defaults to the family rather than the protein deliberately. Measured
    on the current CSV, grouping by ProteinDomain draws 753 negatives against 756
    positives and flattens the per-class positive rate to 0.50-0.51 (std 0.002, versus
    0.25-0.68 / std 0.145 for the per-protein sampler). Grouping by LTPProtein instead
    makes the cells too small to fill: only 376 negatives are available, and the
    surviving classes come out *more* skewed (0.50-1.00, std 0.178) than before. The
    family is the finest grouping this dataset can actually balance.

    `hard_negative_pool`/`excluded_groups`/`hard_negative_share`/`negative_mode`: see
    `_sample_group_balanced_negatives`, whose weighting this reuses verbatim, scoped to
    each (group, class) CELL rather than to the whole group. The cell's own positives
    are the reference, and `draw_n` is untouched, so steering changes which candidate
    inside a class fills that cell's quota and nothing about the per-class matching this
    sampler exists for -- the two are orthogonal, not a trade.

    What a cell leaves the pool to separate depends on the pool's axis. On a lipid axis
    every candidate in a cell already shares the head group, so Tanimoto is down to acyl
    composition -- a narrower span than the same flag reaches under `balanced_proteins`.
    On a protein axis the cell is the opposite case: it holds every protein of the
    family, so a protein-similarity pool has its full range to work with here.
    """
    if negative_mode not in ("hard", "dissimilar"):
        raise ValueError(
            f"negative_mode must be 'hard' or 'dissimilar', got {negative_mode!r}"
        )
    groups = csv[group_column].astype(str).str.lower()
    lipid_classes = lipid_class_series(csv)
    is_positive = csv["Interaction"] == 1
    is_negative = csv["Interaction"] == 0
    excluded = (
        {str(group).lower() for group in excluded_groups} if excluded_groups else set()
    )
    reference = None
    if hard_negative_pool is not None:
        reference = reference_for(hard_negative_pool, csv, excluded_groups, seed)
    parts = []
    for group in sorted(groups.dropna().unique()):
        group_mask = groups == group
        # `group` IS the ProteinDomain here (that is this sampler's grouping), so the
        # exemption reads it directly instead of the family lookup
        # `_sample_group_balanced_negatives` needs for its per-protein grouping.
        group_excluded = group in excluded
        for lipid_class in sorted(lipid_classes[group_mask].dropna().unique()):
            cell_mask = group_mask & (lipid_classes == lipid_class)
            positive_count = int((is_positive & cell_mask).sum())
            if positive_count == 0:
                continue
            candidates = csv[is_negative & cell_mask]
            draw_n = min(positive_count * ratio, len(candidates))
            if draw_n == 0:
                continue
            weights = None
            if hard_negative_pool is not None and not group_excluded:
                sims = candidate_similarities(
                    hard_negative_pool,
                    candidates,
                    csv[is_positive & cell_mask],
                    reference,
                )
                if sims is not None:
                    weigh = (
                        _dissimilar_negative_weights
                        if negative_mode == "dissimilar"
                        else _hard_negative_weights
                    )
                    weights = weigh(sims, hard_negative_share)
            if weights is None:
                parts.append(candidates.sample(n=draw_n, random_state=seed))
            else:
                parts.append(
                    _weighted_negative_draw(candidates, draw_n, weights, seed)
                )
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def split_and_sample_lipid_class_balanced_interactions(
    csv, seed, group_column="ProteinDomain", ratio=1, hard_negative_pool=None,
    excluded_groups=None, hard_negative_share=0.5, negative_mode="hard",
):
    """Keep every positive and sample per-(group, lipid class)-matched negatives (1:1)."""
    positive_pairs = csv[csv["Interaction"] == 1].copy()
    unlabeled_pairs = sample_lipid_class_balanced_negatives(
        csv, seed, group_column, ratio, hard_negative_pool, excluded_groups,
        hard_negative_share, negative_mode,
    ).copy()
    return positive_pairs, unlabeled_pairs


def rebalance_excluded_group_negatives(csv, unlabeled_pairs, excluded_groups, seed):
    """Resample each excluded group's negatives to match its positive count (1:1).

    `split_and_sample_interactions` only keeps a global random subsample of
    negatives, so a small excluded group can end up with far fewer -- or far more
    -- negatives than positives purely by luck of that subsample -- e.g. GLTP ends
    up ~73% positive and OSBP ~26% positive in the held-out data, which has
    nothing to do with true biological prevalence. This draws extra negatives (or
    drops surplus ones) per excluded group, using the group's full per-domain
    negative pool rather than the global subsample, so the group's held-out
    pos:neg ratio is 1:1 either way.
    """
    if not excluded_groups:
        return unlabeled_pairs
    excluded_lower = {group.lower() for group in excluded_groups}
    domain_lower = csv["ProteinDomain"].str.lower()
    unlabeled_domain = domain_lower.loc[unlabeled_pairs.index]
    parts = [unlabeled_pairs[~unlabeled_domain.isin(excluded_lower)]]
    for group in excluded_lower:
        group_mask = domain_lower == group
        positive_count = int(((csv["Interaction"] == 1) & group_mask).sum())
        current_negatives = unlabeled_pairs[unlabeled_domain == group]
        current_count = len(current_negatives)
        if positive_count == 0 or current_count == positive_count:
            parts.append(current_negatives)
        elif current_count < positive_count:
            needed = positive_count - current_count
            candidates = csv[(csv["Interaction"] == 0) & group_mask].drop(
                current_negatives.index, errors="ignore"
            )
            draw_n = min(needed, len(candidates))
            extra = candidates.sample(n=draw_n, random_state=seed) if draw_n > 0 else candidates.iloc[0:0]
            parts.append(pandas.concat([current_negatives, extra]))
        else:
            parts.append(current_negatives.sample(n=positive_count, random_state=seed))
    return pandas.concat(parts)


class ClassBalancedBatchSampler(torch.utils.data.Sampler):
    """Yield batches holding as close to equal positive and unlabeled counts.

    ``labels`` are the training interaction labels in dataset order, so the
    yielded entries are positional dataset indices, matching ``PLIDataset.get``.

    Every row is emitted exactly once per epoch. The epoch holds as many batches as
    ``batch_size`` rows per batch requires, and each class is split into that many
    chunks whose sizes differ by at most one, so a pool that does not divide evenly
    spreads its remainder across the epoch instead of forming one odd batch or
    leaving a tail unprocessed.

    Equal-sized pools (what ``balance_negatives_by_family`` produces) chunk
    identically, so every batch is exactly balanced and holds ``batch_size // 2`` of
    each class. Unequal pools cannot be both fully covered and exactly balanced; the
    batch then inherits the pool's ratio, which is the point -- at
    ``negatives_per_positive=2`` the model should see two unlabeled rows per positive,
    not one -- while the batch still holds ``batch_size`` rows and at least one of each
    class.

    The batch count comes from the TOTAL, not from the larger class needing
    ``batch_size // 2``. Those agree exactly whenever the pools are equal, so nothing
    changes for a 1:1 run; they part company when the pools are not, and the older
    reading handed the larger class ``batch_size // 2`` and let the smaller one supply
    proportionally less, so ``--batch=16`` against a 1:2 pool yielded 4 + 8 = 12 rows
    rather than the 16 asked for. ``batch_size`` is the batch size.
    """

    def __init__(self, labels, batch_size, generator=None):
        if batch_size < 2:
            raise ValueError("balanced batches require batch_size >= 2")
        labels = torch.as_tensor(labels).reshape(-1).long()
        if not ((labels == 0) | (labels == 1)).all():
            raise ValueError("balanced batches require labels in {0, 1}")

        self.positive_indices = torch.nonzero(labels == 1, as_tuple=False).view(-1)
        self.unlabeled_indices = torch.nonzero(labels == 0, as_tuple=False).view(-1)
        self.batch_size = batch_size
        self.generator = generator

        positives = int(self.positive_indices.numel())
        unlabeled = int(self.unlabeled_indices.numel())
        if positives == 0 or unlabeled == 0:
            raise ValueError(
                "balanced batches require both classes to be present, got "
                f"{positives} positive and {unlabeled} unlabeled"
            )
        # Enough batches to hand out batch_size rows each, but never more than the
        # smaller pool can cover: past that point chunks of the smaller pool would be
        # empty and those batches would carry a single class, which is exactly what
        # this sampler exists to prevent. (Hitting that cap means one class is thinner
        # than one row per batch, and the batches come out larger than asked rather
        # than single-class.)
        self.num_batches = min(
            max(1, -(-(positives + unlabeled) // batch_size)),
            positives,
            unlabeled,
        )

    def __len__(self):
        return self.num_batches

    def _chunk(self, pool, batch):
        # Boundaries at i*n//k keep chunk sizes within one of each other and
        # spread the larger chunks evenly through the epoch.
        start = (batch * pool.numel()) // self.num_batches
        stop = ((batch + 1) * pool.numel()) // self.num_batches
        return pool[start:stop]

    def __iter__(self):
        positives = self.positive_indices[
            torch.randperm(self.positive_indices.numel(), generator=self.generator)
        ]
        unlabeled = self.unlabeled_indices[
            torch.randperm(self.unlabeled_indices.numel(), generator=self.generator)
        ]
        for batch in range(self.num_batches):
            yield torch.cat(
                (self._chunk(positives, batch), self._chunk(unlabeled, batch))
            ).tolist()



class RotatingNegativeBatchSampler(torch.utils.data.Sampler):
    """Every negative reaches the model, a different slice of them each epoch.

    The problem this exists for. Negatives are drawn ONCE, when the dataset is built
    (``_sample_interactions``), and the same ``negatives_per_positive`` of them are
    replayed for all 120 epochs while the other ~80% of the table is never seen at all.
    At the project's own ratio that is 634 positives against 9271 negatives: a 2:1 draw
    shows 1268 of those 9271 and discards 86% of the negative evidence, and WHICH 86%
    is a property of the seed rather than of the data.

    What it does instead. The epoch's cost is unchanged -- it still emits ``chunk``
    negatives, so a rotating run and a fixed one do the same amount of work per epoch --
    but the chunk moves: the negatives are permuted once (seeded, so the whole schedule
    is reproducible) and epoch *e* takes the *e*-th consecutive slice, wrapping around at
    the end. Over ``ceil(n_negatives / chunk)`` epochs every negative has been shown
    exactly once, and a 120-epoch run makes about sixteen such passes at the default
    chunk. Positives are NOT rotated: there are few enough that every epoch gets all of
    them, which is also what keeps the per-epoch class ratio fixed at what
    ``negatives_per_positive`` asked for.

    Composition with --balanced_batches. When ``balanced`` is set the epoch's active
    rows are handed to a fresh ClassBalancedBatchSampler, so batch composition is
    decided by exactly the code that decides it without this flag; the positions it
    yields are subset-local and are mapped back to dataset positions here. When it is
    not set, the active rows are shuffled and cut into ``batch_size`` batches, which is
    what a plain shuffling DataLoader would have done to them.

    ``labels`` are the training interaction labels in dataset order, as for
    ClassBalancedBatchSampler, and the yielded entries are dataset positions.
    ``set_epoch`` must be called before each epoch; epoch 0 is the state it is built in,
    so a caller that forgets it trains on one fixed slice rather than on nothing.
    """

    def __init__(self, labels, batch_size, chunk, balanced, generator=None):
        if batch_size < 1:
            raise ValueError("rotating negatives require batch_size >= 1")
        if chunk < 1:
            raise ValueError("rotating negatives require at least one negative per epoch")
        labels = torch.as_tensor(labels).reshape(-1).long()
        if not ((labels == 0) | (labels == 1)).all():
            raise ValueError("rotating negatives require labels in {0, 1}")

        self.labels = labels
        self.positive_indices = torch.nonzero(labels == 1, as_tuple=False).view(-1)
        negatives = torch.nonzero(labels == 0, as_tuple=False).view(-1)
        if self.positive_indices.numel() == 0 or negatives.numel() == 0:
            raise ValueError(
                "rotating negatives require both classes to be present, got "
                f"{int(self.positive_indices.numel())} positive and "
                f"{int(negatives.numel())} negative"
            )
        self.batch_size = batch_size
        self.balanced = bool(balanced)
        self.generator = generator
        # Permuted ONCE, not per epoch: consecutive slices of one fixed permutation are
        # what makes "every negative exactly once per pass" true. Re-permuting each
        # epoch would sample with replacement across epochs and leave some negatives
        # unseen for a long time, which is the behaviour this class replaces.
        self.negative_order = negatives[
            torch.randperm(negatives.numel(), generator=generator)
        ]
        self.chunk = min(int(chunk), int(negatives.numel()))
        self.epochs_per_pass = -(-int(negatives.numel()) // self.chunk)
        self._epoch = 0
        self._active = None
        self.set_epoch(0)

    def set_epoch(self, epoch):
        """Point the sampler at epoch `epoch`'s slice of the negative order."""
        self._epoch = int(epoch)
        count = int(self.negative_order.numel())
        start = (self._epoch * self.chunk) % count
        take = self.negative_order[start:start + self.chunk]
        if take.numel() < self.chunk:
            # The pass wraps here. Taking the shortfall from the FRONT keeps every epoch
            # the same size (so the loss is averaged over a constant number of rows) at
            # the price of showing a few negatives twice in the wrapping epoch -- the
            # alternative, a short final epoch, changes the epoch's meaning instead.
            take = torch.cat((take, self.negative_order[: self.chunk - take.numel()]))
        self._active = torch.cat((self.positive_indices, take))
        return self

    @property
    def active_indices(self):
        return self._active

    def _batches(self):
        active = self._active
        if self.balanced:
            inner = ClassBalancedBatchSampler(
                self.labels[active], self.batch_size, generator=self.generator
            )
            return [active[torch.as_tensor(batch)].tolist() for batch in inner]
        order = active[torch.randperm(active.numel(), generator=self.generator)]
        return [
            order[start:start + self.batch_size].tolist()
            for start in range(0, order.numel(), self.batch_size)
        ]

    def __len__(self):
        # Counted, not materialized: len() is asked for once per epoch by the loader and
        # once at startup by new_train.py's batch cap, and building every batch to
        # answer it would draw from the generator and shift the epoch's own shuffle.
        active = int(self._active.numel())
        if not self.balanced:
            return -(-active // self.batch_size)
        positives = int((self.labels[self._active] == 1).sum())
        return min(
            max(1, -(-active // self.batch_size)), positives, active - positives
        )

    def __iter__(self):
        return iter(self._batches())
