"""Interaction-pool and batch sampling utilities."""

import re

import numpy as np
import pandas
import torch


def split_and_sample_interactions(csv, seed, unlabeled_fraction=0.056):
    """Keep every positive row and sample only rows labeled as unlabeled."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = csv[csv["Interaction"] == 0].sample(
        frac=unlabeled_fraction,
        random_state=seed,
    ).copy()
    return csvtrue, csvfalse


def _hard_negative_weights(candidates, positive_lipid_names, similarity, species_index, share):
    """Sampling weight per candidate, blending chemistry-hardness with uniform.

    `share` of the mass goes to candidates by how similar (Tanimoto, max over the
    group's own positives) their lipid is to a lipid this SAME group is already
    positive for -- a hard negative, chemically close enough to look like a binder yet
    labeled unlabeled. The rest of the mass stays uniform, so a group whose positives
    have no chemically close negatives in its pool still draws its full quota instead
    of concentrating on the handful nearest zero similarity. Returns None (fall back to
    plain uniform sampling) when none of the group's positives have a similarity entry.
    """
    positive_positions = [
        species_index[name] for name in positive_lipid_names.unique() if name in species_index
    ]
    if not positive_positions:
        return None
    n = len(candidates)
    sims = np.array(
        [
            similarity[species_index[name], positive_positions].max() if name in species_index else 0.0
            for name in candidates["FullIdentityOfLipid"]
        ]
    )
    sims = np.clip(sims, 0.0, None)
    total = sims.sum()
    similarity_mass = sims / total if total > 0 else np.full(n, 1.0 / n)
    uniform_mass = np.full(n, 1.0 / n)
    return share * similarity_mass + (1 - share) * uniform_mass


def _sample_group_balanced_negatives(
    csv,
    seed,
    group_column,
    ratio=1,
    strata=None,
    hard_negative_pool=None,
    excluded_groups=None,
    hard_negative_share=0.5,
):
    """Sample `ratio` negatives per positive within each group.

    `ratio` is 1 for the exact 1:1 the samplers were written for. Higher values keep
    proportionally more of the negative pool: at 1 the working set is 1512 of the
    table's 11018 rows, and the 9506 rows dropped are the record of which lipids each
    protein does NOT bind. The ratio is per group, so raising it does not reintroduce
    the between-protein prior the grouping exists to remove -- every group keeps the
    same pos:neg proportion, just a coarser one. What it does change is the class prior
    the loss sees, which is `--class_weights`' job.

    `hard_negative_pool`, if given, is `(similarity, species_index)` from
    `dataloader.chemistry_prior.species_similarity`: negatives are then drawn weighted
    toward chemistry-hard candidates (see `_hard_negative_weights`) instead of
    uniformly. `excluded_groups`, if given alongside it, exempts any group whose
    ProteinDomain is in it from the reweighting -- those rows become validation/test
    after the coming split, and must be drawn exactly as a run without
    `--hard_negative_mining` would draw them, so enabling the flag changes what
    training sees and nothing about what is measured.
    """
    if ratio < 1:
        raise ValueError(f"negatives per positive must be at least 1, got {ratio}")
    groups = csv[group_column].str.lower()
    family_of_group = None
    if hard_negative_pool is not None and excluded_groups:
        family_of_group = csv.groupby(groups)["ProteinDomain"].first().str.lower()
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
                similarity, species_index = hard_negative_pool
                positive_lipids = csv.loc[is_positive & group_mask, "FullIdentityOfLipid"]
                weights = _hard_negative_weights(
                    candidates, positive_lipids, similarity, species_index, hard_negative_share
                )
        if weights is None:
            parts.append(candidates.sample(n=draw_n, random_state=seed))
        else:
            # pandas' own weighted .sample(replace=False) refuses whenever one
            # candidate's normalized weight alone exceeds 1/draw_n
            # (pandas/core/sample.py's `size * weights.max() > 1` guard), which a
            # concentrated hard-negative pool (one very close candidate, the rest at
            # similarity 0) hits routinely. numpy's sequential without-replacement
            # draw has no such restriction and is well-defined for any nonnegative
            # weights, so it takes over for exactly this path.
            rng = np.random.default_rng(seed)
            chosen = rng.choice(
                len(candidates), size=draw_n, replace=False, p=weights / weights.sum()
            )
            parts.append(candidates.iloc[chosen])
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def sample_family_balanced_negatives(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5,
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
        hard_negative_pool, excluded_groups, hard_negative_share,
    )


def split_and_sample_family_balanced_interactions(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5,
):
    """Keep every positive and sample per-family-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_family_balanced_negatives(
        csv, seed, ratio, strata, hard_negative_pool, excluded_groups, hard_negative_share
    ).copy()
    return csvtrue, csvfalse


def sample_protein_balanced_negatives(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5,
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
        hard_negative_pool, excluded_groups, hard_negative_share,
    )


def split_and_sample_protein_balanced_interactions(
    csv, seed, ratio=1, strata=None, hard_negative_pool=None, excluded_groups=None,
    hard_negative_share=0.5,
):
    """Keep every positive and sample per-protein-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_protein_balanced_negatives(
        csv, seed, ratio, strata, hard_negative_pool, excluded_groups, hard_negative_share
    ).copy()
    return csvtrue, csvfalse


# lipid_class_series and the ambiguity table live in dataloader.lipid_classes so the
# preprocessing scripts can apply the same rule without importing torch. Re-exported
# here because everything already reaches for them through this module.
from dataloader.lipid_classes import (  # noqa: F401
    AMBIGUOUS_CLASS_RESOLUTION,
    class_level_positive_labels,
    head_group_class,
    lipid_class_series,
)


# Lipid-class sets for --lipid_coldsplit: whole chemical families held out of training
# while every protein stays in it. The question they ask is the other one from the
# protein-family split -- a lipid of a chemistry never seen arrives, which of the known
# proteins bind it -- and it is the one that matters when the screening panel grows.
#
# Grouped by chemistry rather than by count, because a set is only cold if its close
# relatives leave with it. Measured on the compact Tanimoto matrix as the mean over the
# set's structures of the highest similarity to anything left in training:
#
#   sphingolipids    0.458   85 positives (11.2%)   sphingoid backbone, all of it
#   phosphorus_free  0.553   61 positives ( 8.1%)   no phosphate: neutral glycerolipids,
#                                                   free fatty acids, retinol
#   choline          0.653  258 positives (34.1%)   phosphocholine head, di- and lyso-
#   anionic          0.766  228 positives (30.2%)   anionic glycerophospholipid heads
#
# The first three are genuinely isolated. `anionic` is not, and cannot be: PA, PI, PS,
# PG and their relatives differ from the phosphatidylcholines that stay behind only in
# the head group, while a fingerprint sees mostly the two acyl chains, so 0.77 is what
# the chemistry allows. Splitting it makes that worse, not better (PG+LPG+PGP alone
# comes out at 0.872, BMP+cardiolipin alone at 0.946). Kept as the hardest of the four:
# it asks whether the model reads the head group at all.
#
# Phosphatidyl- and lysophosphatidylethanolamine are in no set. They would isolate no
# better than `anionic` (0.778) and there is no reason to spend a fifth run on them;
# they stay in training throughout.
LIPID_COLDSPLIT_SETS = {
    "sphingolipids": (
        "Sphingomyelin",
        "Ceramide",
        "Ceramide phosphate",
        "Hexosyl ceramide",
        "Dihexosyl ceramide",
        "Sulfohexosyl ceramide",
    ),
    "phosphorus_free": (
        "Diacylglycerol",
        "Triacylglycerol",
        "Retinol",
        "docosapentaenoate",
        "docosatetraenoate",
        "docosatrienoate",
        "eicosapentaenoate",
        "eicosatetraenoate",
        "eicosatrienoate",
        "heptadecenoate",
        "hexadecenoate",
        "nonadecenoate",
        "octadecadienoate",
        "octadecatrienoate",
        "octadecatrienol",
        "octadecenoate",
    ),
    "choline": (
        "Phosphatidylcholine",
        "Lysophosphatidylcholine",
    ),
    "anionic": (
        "Phosphatidate",
        "Phosphatidylinositol",
        "Phosphatidylserine",
        "Phosphatidylglycerol",
        "Lysophosphatidylglycerol",
        "Phosphatidylglycerophosphate",
        "Bismonoacylglycerolphosphate",
        "Cardiolipin",
    ),
}


COLDSPLIT_MINIMUM_TEST_POSITIVES = 20


def lipid_classes_for_holdout(csv, family, share):
    """The head-group classes to hold out of training when `family` is held out.

    The second axis of the cold split needs its own class set per family, not one shared
    set: a family's positives sit in its own classes -- START's in phosphatidylcholines,
    GLTP's in sphingolipids -- so any set fixed in advance is arbitrary for whichever
    family is being held out. Classes are scored by concentration,

        score(class) = family positives in class / (everyone else's positives there + 1)

    and taken by descending score until the family's covered positives reach `share` of
    its total. The numerator is what the held-out block gains, the denominator what
    training loses elsewhere, so what gets held out is what the family owns. GLTP comes
    out at two classes costing training a single positive; the three families that need
    phosphatidylcholine cost it 128-238.

    `share` is not cosmetic. Stopping early leaves only the cheap classes, and for a
    family whose cheap classes are thin on rows the held-out block ends up almost
    entirely familiar lipids -- the split looks two-axis while the per-lipid label prior
    still carries it. At 0.3 the lipocalin lookup baseline stays at 0.618; 0.7 is the
    smallest value at which no family sits further than one standard error from 0.5.

    Whether the rule worked is not decided here but by
    preprocessing/lipid_marginal_baseline.py, which measures that prior on the split it
    produces. Families too small for a test block at all (ML and OSBP, 10 and 8
    positives) come back with fewer than COLDSPLIT_MINIMUM_TEST_POSITIVES covered;
    callers that care report it, the split itself does not special-case them.
    """
    positives = csv[csv["Interaction"] == 1]
    lipid_classes = lipid_class_series(positives)
    family_rows = positives["ProteinDomain"].str.lower() == str(family).lower()

    everywhere = lipid_classes.value_counts()
    mine = lipid_classes[family_rows].value_counts()
    if mine.empty:
        return [], 0, 0

    elsewhere = everywhere.reindex(mine.index).fillna(0) - mine
    score = (mine / (elsewhere + 1)).sort_values(ascending=False)

    target = max(
        COLDSPLIT_MINIMUM_TEST_POSITIVES,
        int(round(int(family_rows.sum()) * share)),
    )
    chosen = []
    covered = 0
    for lipid_class in score.index:
        if covered >= target:
            break
        chosen.append(lipid_class)
        covered += int(mine[lipid_class])

    cost = int(everywhere.reindex(chosen).sum()) - covered
    return chosen, covered, cost


def sample_lipid_class_balanced_negatives(
    csv, seed, group_column="ProteinDomain", ratio=1
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
    """
    groups = csv[group_column].astype(str).str.lower()
    lipid_classes = lipid_class_series(csv)
    is_positive = csv["Interaction"] == 1
    is_negative = csv["Interaction"] == 0
    parts = []
    for group in sorted(groups.dropna().unique()):
        group_mask = groups == group
        for lipid_class in sorted(lipid_classes[group_mask].dropna().unique()):
            cell_mask = group_mask & (lipid_classes == lipid_class)
            positive_count = int((is_positive & cell_mask).sum())
            if positive_count == 0:
                continue
            candidates = csv[is_negative & cell_mask]
            draw_n = min(positive_count * ratio, len(candidates))
            if draw_n > 0:
                parts.append(candidates.sample(n=draw_n, random_state=seed))
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def split_and_sample_lipid_class_balanced_interactions(
    csv, seed, group_column="ProteinDomain", ratio=1
):
    """Keep every positive and sample per-(group, lipid class)-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_lipid_class_balanced_negatives(
        csv, seed, group_column, ratio
    ).copy()
    return csvtrue, csvfalse


def rebalance_excluded_group_negatives(csv, csvfalse, excluded_groups, seed):
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
        return csvfalse
    excluded_lower = {group.lower() for group in excluded_groups}
    domain_lower = csv["ProteinDomain"].str.lower()
    csvfalse_domain = domain_lower.loc[csvfalse.index]
    parts = [csvfalse[~csvfalse_domain.isin(excluded_lower)]]
    for group in excluded_lower:
        group_mask = domain_lower == group
        positive_count = int(((csv["Interaction"] == 1) & group_mask).sum())
        current_negatives = csvfalse[csvfalse_domain == group]
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

