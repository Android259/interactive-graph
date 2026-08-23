import sys
from pathlib import Path
from types import SimpleNamespace

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "training"))

from candidate_averaging import average_candidate_predictions


def logits(*rows):
    return torch.tensor(rows, dtype=torch.float32)


def test_batch_without_candidate_groups_is_returned_unchanged():
    outl = logits([2.0, -1.0], [0.0, 3.0])
    labels = torch.tensor([1, 0])

    averaged, reduced_labels, first = average_candidate_predictions(
        outl, SimpleNamespace(), labels
    )

    assert averaged is outl
    assert reduced_labels is labels
    assert first is None


def test_probabilities_are_averaged_within_a_pair():
    # Two candidates of pair 7 and one of pair 9. The averaged probability of pair 7 is
    # the mean of its candidates', which is what the returned log-probabilities encode.
    outl = logits([4.0, 0.0], [0.0, 4.0], [1.0, 0.0])
    prot = SimpleNamespace(
        candidate_group=torch.tensor([[7], [7], [9]]),
        protein_id=torch.tensor([[3], [3], [5]]),
    )
    labels = torch.tensor([1, 1, 0])

    averaged, reduced_labels, first = average_candidate_predictions(outl, prot, labels)

    expected = torch.softmax(outl[:2], dim=1).mean(dim=0)
    assert torch.allclose(averaged[0].exp(), expected, atol=1e-6)
    assert torch.allclose(averaged[1].exp(), torch.softmax(outl[2:], dim=1)[0], atol=1e-6)
    assert reduced_labels.tolist() == [1, 0]
    assert first.tolist() == [0, 2]
    assert prot.protein_id.view(-1).tolist() == [3, 5]


def test_averaging_can_flip_the_decision_a_single_candidate_would_give():
    # One candidate says positive with 0.98, two say positive with 0.2: the mean is
    # 0.46, so the pair comes out negative, which the first candidate alone would not.
    outl = torch.log(
        torch.tensor(
            [[0.02, 0.98], [0.80, 0.20], [0.80, 0.20]], dtype=torch.float32
        )
    )
    prot = SimpleNamespace(candidate_group=torch.tensor([[1], [1], [1]]))
    labels = torch.tensor([1, 1, 1])

    averaged, reduced_labels, _ = average_candidate_predictions(outl, prot, labels)

    assert averaged.shape == (1, 2)
    assert int(averaged.argmax(dim=1)) == 0
    assert int(outl[0].argmax()) == 1
    assert reduced_labels.tolist() == [1]


def test_groups_are_formed_by_value_so_a_shuffled_batch_still_averages():
    outl = logits([4.0, 0.0], [1.0, 0.0], [0.0, 4.0])
    prot = SimpleNamespace(candidate_group=torch.tensor([[7], [9], [7]]))
    labels = torch.tensor([1, 0, 1])

    averaged, reduced_labels, first = average_candidate_predictions(outl, prot, labels)

    expected = torch.softmax(outl[[0, 2]], dim=1).mean(dim=0)
    assert torch.allclose(averaged[0].exp(), expected, atol=1e-6)
    assert reduced_labels.tolist() == [1, 0]
    assert first.tolist() == [0, 1]


def test_accumulator_averages_a_pair_split_across_batches():
    from candidate_averaging import CandidateAccumulator

    # The two candidates of pair 7 arrive in different batches, which is what a shuffled
    # fixed-size loader does to them; the average must come out the same as if they had
    # arrived together.
    accumulator = CandidateAccumulator()
    accumulator.add(
        logits([4.0, 0.0], [1.0, 0.0]),
        SimpleNamespace(
            candidate_group=torch.tensor([[7], [9]]),
            protein_id=torch.tensor([[3], [5]]),
        ),
        torch.tensor([1, 0]),
    )
    accumulator.add(
        logits([0.0, 4.0]),
        SimpleNamespace(
            candidate_group=torch.tensor([[7]]), protein_id=torch.tensor([[3]])
        ),
        torch.tensor([1]),
    )

    averaged, labels, protein_ids = accumulator.averaged()

    expected = torch.softmax(logits([4.0, 0.0], [0.0, 4.0]), dim=1).mean(dim=0)
    assert len(accumulator) == 2
    assert torch.allclose(averaged[0].exp(), expected, atol=1e-6)
    assert labels.tolist() == [1, 0]
    assert protein_ids.view(-1).tolist() == [3, 5]


def test_accumulator_weighs_every_pair_once_whatever_its_candidate_count():
    from candidate_averaging import CandidateAccumulator

    accumulator = CandidateAccumulator()
    groups = [1] * 12 + [2]
    accumulator.add(
        logits(*([[1.0, 0.0]] * 12 + [[0.0, 1.0]])),
        SimpleNamespace(candidate_group=torch.tensor([[g] for g in groups])),
        torch.tensor([0] * 12 + [1]),
    )

    averaged, labels, _ = accumulator.averaged()

    # Twelve candidates of pair 1 leave one row behind, exactly like the single
    # candidate of pair 2.
    assert averaged.shape == (2, 2)
    assert labels.tolist() == [0, 1]


def test_original_rows_come_from_pair_id_not_the_frame_index():
    import pandas as pd

    from dataloader.New_dataloader import PLIDataset

    # The sampled pool is re-indexed 0..N-1, so a split frame's labels are pool
    # positions; only pair_id still points at the row of the original table the
    # compatibility term was computed for.
    frame = pd.DataFrame(
        {"pair_id": [10404, 77], "LTPProtein": ["A", "B"]}, index=[969, 3]
    )

    rows = PLIDataset._original_rows(frame)

    assert rows.tolist() == [10404, 77]
    assert PLIDataset._original_rows(frame.iloc[:0]).tolist() == []
