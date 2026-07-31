"""Interaction-pool and batch sampling utilities."""

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


def _sample_group_balanced_negatives(csv, seed, group_column):
    """Sample negatives per group to match that group's positive count."""
    groups = csv[group_column].str.lower()
    is_positive = csv["Interaction"] == 1
    is_negative = csv["Interaction"] == 0
    parts = []
    for group in sorted(groups.dropna().unique()):
        group_mask = groups == group
        positive_count = int((is_positive & group_mask).sum())
        if positive_count == 0:
            continue
        candidates = csv[is_negative & group_mask]
        draw_n = min(positive_count, len(candidates))
        if draw_n > 0:
            parts.append(candidates.sample(n=draw_n, random_state=seed))
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def sample_family_balanced_negatives(csv, seed):
    """Sample negatives per protein family to match its positive count (1:1).

    Instead of the global fixed-fraction subsample of `split_and_sample_interactions`,
    this draws, for each of the protein families in `ProteinDomain`, exactly as many
    unlabeled rows as that family has positives, so the working set is 1:1
    positive:negative both globally and within every family. Sampling is seeded
    (`random_state=seed`) and preserves the original interaction-CSV row index.
    """
    return _sample_group_balanced_negatives(csv, seed, "ProteinDomain")


def split_and_sample_family_balanced_interactions(csv, seed):
    """Keep every positive and sample per-family-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_family_balanced_negatives(csv, seed).copy()
    return csvtrue, csvfalse


def sample_protein_balanced_negatives(csv, seed):
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
    """
    return _sample_group_balanced_negatives(csv, seed, "LTPProtein")


def split_and_sample_protein_balanced_interactions(csv, seed):
    """Keep every positive and sample per-protein-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_protein_balanced_negatives(csv, seed).copy()
    return csvtrue, csvfalse


def lipid_class_series(csv):
    """Return the head-group class of every row, e.g. 'Phosphatidylcholine (34:1)' -> 'Phosphatidylcholine'.

    `FullIdentityOfLipid` spells the class out in full and puts the acyl composition in
    a trailing parenthesis; stripping that leaves 36 chemical classes over the 312
    distinct lipids. The class, not the individual species, is the level a binding
    preference actually lives at (a protein that takes PC(32:1) takes PC(34:1) too).
    """
    return (
        csv["FullIdentityOfLipid"]
        .astype(str)
        .str.replace(r"\s*\(.*", "", regex=True)
        .str.strip()
    )


def sample_lipid_class_balanced_negatives(csv, seed, group_column="ProteinDomain"):
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
            draw_n = min(positive_count, len(candidates))
            if draw_n > 0:
                parts.append(candidates.sample(n=draw_n, random_state=seed))
    if parts:
        return pandas.concat(parts)
    return csv[is_negative].iloc[0:0]


def split_and_sample_lipid_class_balanced_interactions(
    csv, seed, group_column="ProteinDomain"
):
    """Keep every positive and sample per-(group, lipid class)-matched negatives (1:1)."""
    csvtrue = csv[csv["Interaction"] == 1].copy()
    csvfalse = sample_lipid_class_balanced_negatives(csv, seed, group_column).copy()
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

    Every row is emitted exactly once per epoch. ``batch_size // 2`` is the
    target per-class size, and the epoch holds however many batches that target
    needs for the larger class. Each class is then split into that many chunks
    whose sizes differ by at most one, so a pool that does not divide evenly
    spreads its remainder across the epoch instead of forming one odd batch or
    leaving a tail unprocessed.

    Equal-sized pools (what ``balance_negatives_by_family`` produces) chunk
    identically, so every batch is exactly balanced. Unequal pools cannot be
    both fully covered and exactly balanced; the split then keeps the per-batch
    ratio as close to the achievable average as the chunking allows, and every
    batch still carries at least one row of each class.
    """

    def __init__(self, labels, batch_size, generator=None):
        if batch_size < 2:
            raise ValueError("balanced batches require batch_size >= 2")
        labels = torch.as_tensor(labels).reshape(-1).long()
        if not ((labels == 0) | (labels == 1)).all():
            raise ValueError("balanced batches require labels in {0, 1}")

        self.positive_indices = torch.nonzero(labels == 1, as_tuple=False).view(-1)
        self.unlabeled_indices = torch.nonzero(labels == 0, as_tuple=False).view(-1)
        self.half = batch_size // 2
        self.generator = generator

        positives = int(self.positive_indices.numel())
        unlabeled = int(self.unlabeled_indices.numel())
        if positives == 0 or unlabeled == 0:
            raise ValueError(
                "balanced batches require both classes to be present, got "
                f"{positives} positive and {unlabeled} unlabeled"
            )
        # Enough batches for the larger pool to hand out ``half`` per batch, but
        # never more than the smaller pool can cover: past that point chunks of
        # the smaller pool would be empty and those batches would carry a single
        # class, which is exactly what this sampler exists to prevent.
        self.num_batches = min(
            max(-(-positives // self.half), -(-unlabeled // self.half)),
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
