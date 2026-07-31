import pytest
import torch

from dataloader.sampler import ClassBalancedBatchSampler


def make_labels(positives, unlabeled):
    """Interleave so class membership never follows dataset order."""
    labels = [1] * positives + [0] * unlabeled
    return torch.as_tensor(labels)[torch.randperm(positives + unlabeled)]


@pytest.mark.parametrize(
    ("positives", "unlabeled", "batch_size"),
    [(556, 556, 16), (40, 40, 8), (37, 37, 16), (40, 600, 16), (600, 40, 16)],
)
def test_every_row_is_emitted_exactly_once_per_epoch(positives, unlabeled, batch_size):
    labels = make_labels(positives, unlabeled)
    sampler = ClassBalancedBatchSampler(labels, batch_size)

    drawn = sorted(index for batch in sampler for index in batch)

    assert drawn == list(range(positives + unlabeled))


@pytest.mark.parametrize(("count", "batch_size"), [(556, 16), (37, 16), (40, 8)])
def test_equal_pools_give_exactly_balanced_batches(count, batch_size):
    labels = make_labels(positives=count, unlabeled=count)
    sampler = ClassBalancedBatchSampler(labels, batch_size)

    for batch in sampler:
        assert int(labels[batch].sum()) * 2 == len(batch)


def test_uneven_pool_spreads_the_remainder_across_batches():
    # 556 positives over 70 batches: 4 chunks of 7 among 66 chunks of 8.
    labels = make_labels(positives=556, unlabeled=556)
    sampler = ClassBalancedBatchSampler(labels, batch_size=16)

    sizes = [len(batch) for batch in sampler]

    assert len(sizes) == 70
    assert sorted(set(sizes)) == [14, 16]
    assert sizes.count(14) == 4
    assert sum(sizes) == 1112
    # Spread through the epoch rather than bunched together.
    short = [i for i, size in enumerate(sizes) if size == 14]
    gaps = [b - a for a, b in zip(short, short[1:])]
    assert min(gaps) >= len(sizes) // len(short) - 1


def test_batch_count_never_outruns_the_smaller_pool():
    labels = make_labels(positives=40, unlabeled=600)
    sampler = ClassBalancedBatchSampler(labels, batch_size=16)

    # 600 unlabeled would want 75 batches, but 40 positives cannot fill them
    # without leaving some batch without a single positive row.
    assert len(sampler) == 40
    assert len(list(sampler)) == 40
    for batch in sampler:
        assert int(labels[batch].sum()) >= 1


def test_epochs_repartition_the_same_rows():
    labels = make_labels(positives=556, unlabeled=556)
    sampler = ClassBalancedBatchSampler(
        labels, batch_size=16, generator=torch.Generator().manual_seed(0)
    )

    first = [batch for batch in sampler]
    second = [batch for batch in sampler]

    assert first != second
    assert sorted(i for b in first for i in b) == sorted(i for b in second for i in b)


def test_same_generator_seed_reproduces_the_epoch():
    labels = make_labels(positives=40, unlabeled=60)

    def epoch():
        sampler = ClassBalancedBatchSampler(
            labels, batch_size=8, generator=torch.Generator().manual_seed(7)
        )
        return [batch for batch in sampler]

    assert epoch() == epoch()


def test_odd_batch_size_targets_the_floor_half():
    labels = make_labels(positives=40, unlabeled=40)
    sampler = ClassBalancedBatchSampler(labels, batch_size=9)

    for batch in sampler:
        assert len(batch) == 8
        assert int(labels[batch].sum()) == 4


@pytest.mark.parametrize(
    ("labels", "batch_size", "message"),
    [
        (torch.tensor([1, 0, 1, 0]), 1, "batch_size >= 2"),
        (torch.tensor([1, 0, 2, 0]), 4, "labels in"),
        (torch.tensor([1, 1, 1, 1]), 4, "both classes"),
        (torch.tensor([0, 0, 0, 0]), 4, "both classes"),
    ],
)
def test_invalid_inputs_are_rejected(labels, batch_size, message):
    with pytest.raises(ValueError, match=message):
        ClassBalancedBatchSampler(labels, batch_size=batch_size)
