"""Interaction-pool and batch sampling utilities."""

import re

import numpy as np
import pandas
import torch

from architecture.mlp_utils import build_mlp

# Full-batch steps for learned_prior_reference: a few thousand rows and a few
# dozen standardized features converge within this limit in ~1 s per dataset.
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
    """Return each candidate's maximum similarity to its group's positives.

    For lipid pools, the group is a protein or family: choose lipids similar
    to anything it binds. Return None for uniform sampling when no positive
    has a similarity entry.
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
    """Return positive matrix positions keyed by the candidate's shared coordinate.

    Lipid pools compare with lipids bound by this protein; protein pools compare
    with proteins binding this lipid. The second reference excludes the candidate's
    protein naturally: the candidate row is labeled 0 for that lipid.

    Use positives across all training families, not just the sampling group;
    a single-protein group would otherwise have no reference.
    Exclude excluded_groups: validation/test labels must not select training
    negatives. Those groups are also exempt from steering.
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
    """Return maximum similarity to each candidate's conditioned reference.

    If its shared coordinate has no training positive, use 0.0 instead of dropping
    the candidate. Preserve the quota; the uniform remainder handles zero or
    unseen similarities.
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
    """Return train positive rates by (protein, lipid subclass) and a global fallback.

    Match analysis/baselines/protein_subclass_label_baseline.py.
    Unknown cells use the overall rate, not zero: unmeasured is not non-binding.
    Exclude excluded_groups to prevent held-out labels steering train negatives,
    as in conditioned_reference.
    Rates already lie in [0, 1]: hard emphasizes positive-looking cells;
    dissimilar emphasizes negative-looking cells, without another transform.
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
    """Fit a small MLP on training-visible labels and return scores for all rows.

    Fit here because the sampler knows excluded_groups; held-out labels must
    not select training negatives, as for cell_prior_reference.
    Save and restore the global torch RNG: dataset construction follows
    seed_everything, and later model initialization and DataLoader shuffling
    use that stream. Steering must not alter them by consuming RNG draws here.
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
        # Balance the ~6% positive table; otherwise the scorer collapses to near-zero
        # scores for all rows, making the steered draw effectively uniform.
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
    """Blend similarity-based hard-negative weights with a uniform remainder.

    Assign share of mass by candidate_similarities: unlabeled candidates
    resembling known binders. Keep 1-share uniform so weak-similarity groups
    fill their quota without concentrating on a few near-zero scores.
    """
    n = len(sims)
    sims = np.clip(sims, 0.0, None)
    total = sims.sum()
    similarity_mass = sims / total if total > 0 else np.full(n, 1.0 / n)
    uniform_mass = np.full(n, 1.0 / n)
    return share * similarity_mass + (1 - share) * uniform_mass


def _dissimilar_negative_weights(sims, share):
    """Blend 1-similarity weights with a uniform remainder of 1-share.

    Favor candidates far from known binders, opposite to hard-negative mining.
    Uniform draws on related lipids can produce near-duplicate positives and
    negatives separable mostly by base rates. Dissimilar mining trades easier
    pairs for broader chemistry. Configuration makes the two modes exclusive.
    """
    n = len(sims)
    distances = np.clip(1.0 - np.clip(sims, 0.0, 1.0), 0.0, None)
    total = distances.sum()
    distance_mass = distances / total if total > 0 else np.full(n, 1.0 / n)
    uniform_mass = np.full(n, 1.0 / n)
    return share * distance_mass + (1 - share) * uniform_mass


def _weighted_negative_draw(candidates, draw_n, weights, seed):
    """Draw draw_n candidates without replacement using weights.

    Use numpy: pandas.sample can reject concentrated weights when
    size * weights.max() > 1 (pandas/core/sample.py), e.g. one close candidate
    and the rest at similarity 0.

    numpy requires at least draw_n nonzero weights. At share=1, hard gives zero
    weight to similarity-0 candidates; dissimilar gives zero to similarity-1
    candidates. Take weighted candidates first, then fill any shortfall uniformly
    from zero-weight rows. Steering changes preferences, never the quota.
    For share<1, the uniform remainder already prevents this zero-weight case.
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
    """Draw ratio negatives per positive within each group.

    ratio=1 gives 1:1. In the recorded 11018-row table, this kept 1512 rows
    and dropped 9506 negative observations. Higher ratios retain more negatives
    without changing between-group balance; --class_weights handles the changed
    class prior seen by the loss.

    Optional hard_negative_pool is a SimilarityPool (matrix, index, lipid/protein/
    pair axis). negative_mode selects hard (toward similarity) or dissimilar
    (away); hard_negative_share controls steered mass in both modes.
    See _hard_negative_weights and _dissimilar_negative_weights.
    Groups in excluded_groups keep the original uniform draw: they become
    validation/test, so steering changes training rows without changing evaluation.
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
        # Build the reference once across training, not per group.
        # See conditioned_reference and cell_prior_reference for axis/leakage rules.
        reference = reference_for(hard_negative_pool, csv, excluded_groups, seed)
    if strata is not None:
        # Match per (group, stratum) across the coming lipid-class cut.
        # Without strata, removed classes may take all of a protein's negatives,
        # leaving positive-only training rows that weights cannot repair.
        # Matching both sides keeps each cut side balanced per protein without dropping it.
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
    """Match unlabeled counts to positives per ProteinDomain (1:1).

    This gives family-level and global balance, unlike the fixed global fraction
    in split_and_sample_interactions. Use random_state=seed and preserve original
    interaction-row indices. See _sample_group_balanced_negatives for
    hard_negative_pool, excluded_groups, and hard_negative_share.
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
    """Match unlabeled counts to positives per LTPProtein (1:1).

    Per-family sampling draws from a shared pool and can skew individual proteins.
    Per-protein matching also balances families and removes the protein positive-rate
    prior. Use random_state=seed and preserve original interaction-row indices.
    See _sample_group_balanced_negatives for hard_negative_pool, excluded_groups,
    and hard_negative_share.
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


# Re-export lipid_classes rules for existing callers. Preprocessing can import
# that torch-free module directly.
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
    """Match negatives to positives within (group, lipid class) cells (1:1).

    Per-protein sampling leaves lipid-class rates uneven. Cell matching removes
    that marginal too; e.g. GLTP sphingolipid positives and START PC positives
    otherwise support a class-only rule that may fail across families.
    Cells without positives contribute no rows.

    Default group_column is ProteinDomain. Recorded family grouping drew
    753 negatives for 756 positives, with class positive rates 0.50-0.51
    (std 0.002). Per-protein sampling gave 0.25-0.68 (std 0.145).
    Grouping cells by LTPProtein had only 376 negatives and worsened class
    skew to 0.50-1.00 (std 0.178). Family is the finest usable grouping here.

    Reuse _sample_group_balanced_negatives weighting inside each cell:
    hard_negative_pool, excluded_groups, hard_negative_share, negative_mode.
    Cell positives provide the reference; steering preserves draw_n and class
    quotas. For lipid pools, the shared head group limits variation mostly to
    acyl composition. Protein pools retain all proteins of the family and their
    full similarity range.
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
        # Here group is ProteinDomain, so check the exemption directly.
        # Per-protein _sample_group_balanced_negatives needs a family lookup.
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
    """Resample excluded-group negatives to match positives (1:1).

    Draw from each group's full negative pool, adding or removing rows relative
    to the global subsample. This removes random held-out ratio skew: the
    recorded global draw gave ~73% positives for GLTP and ~26% for OSBP,
    which does not estimate biological prevalence.
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
    """Yield dataset positions with balanced positive/unlabeled batch counts.

    labels follow dataset order, matching PLIDataset.get. Emit every row once
    per epoch. Divide each class into the required batch count, with chunk
    sizes differing by at most one, spreading remainders without dropping tails.

    Equal pools give batch_size // 2 from each class. Unequal pools retain the
    pool ratio while covering all rows, with at least one row per class in each
    batch. At negatives_per_positive=2, preserve two unlabeled rows per positive.

    Count batches from the total pool size. The old larger-class calculation
    gave only 4+8=12 rows for batch_size=16 at ratio 1:2; equal pools are unchanged.
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
        # Use enough batches for batch_size rows, capped by the smaller pool count.
        # Beyond that cap, some batches would contain only one class.
        # At the cap, accept larger batches instead of single-class batches.
        self.num_batches = min(
            max(1, -(-(positives + unlabeled) // batch_size)),
            positives,
            unlabeled,
        )

    def __len__(self):
        return self.num_batches

    def _chunk(self, pool, batch):
        # i*n//k boundaries spread chunks evenly, with sizes differing by at most one.
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
    """Rotate negative slices each epoch while keeping all positives.

    A fixed dataset draw repeats the same negatives for all 120 epochs.
    With 634 positives and 9271 negatives, ratio 2 retains 1268 negatives and
    discards 86%, depending on the seed (roughly 80% in the broader setting).

    Permute negatives once with a seed. Epoch e takes its consecutive chunk,
    wrapping at the end. Each pass covers every negative; ceil(n_negatives/chunk)
    epochs suffice, and 120 epochs give about sixteen passes at the default chunk.
    Each epoch keeps the same chunk size, class ratio, and work as fixed sampling.
    Positives are all included every epoch.

    With balanced=True, pass active rows to ClassBalancedBatchSampler and map
    subset-local positions back to dataset positions. Otherwise shuffle active
    rows and divide into batch_size batches, as a shuffling DataLoader would.

    labels and emitted positions use dataset order. Call set_epoch before each
    epoch; initial epoch 0 otherwise repeats a fixed slice.
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
        # Permute once so consecutive slices cover every negative per pass.
        # Re-permuting each epoch could repeatedly miss some negatives.
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
            # Wrap by taking the shortfall from the front. Keep epoch size and loss
            # averaging constant, accepting repeated negatives in the wrapping epoch.
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
        # Compute len without building batches: loader and new_train.py query it.
        # Materializing them would consume RNG draws and shift shuffling.
        active = int(self._active.numel())
        if not self.balanced:
            return -(-active // self.batch_size)
        positives = int((self.labels[self._active] == 1).sum())
        return min(
            max(1, -(-active // self.batch_size)), positives, active - positives
        )

    def __iter__(self):
        return iter(self._batches())
