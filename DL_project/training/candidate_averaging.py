"""Averaging a pair's candidate structures back into one prediction.

Under ``--eval_average_candidates`` an evaluation split carries one row per candidate
structure of a measured lipid species (``Dataloader._expand_candidate_rows``),
because the spectrum does not say which isomer was in the protein and training under
``random_choice`` answers the same thing for all of them. Reading the model back on one
arbitrary member would throw that invariance away, so the copies are collapsed here.
"""

import torch


def average_candidate_predictions(outl, prot, labels):
    """Collapse a batch's candidate copies of a pair into one averaged prediction.

    Under --eval_average_candidates the evaluation split carries one row per candidate
    structure of the measured species (Dataloader._expand_candidate_rows), and this
    is where they come back together: the class probabilities are averaged over a pair's
    candidates and the result is returned as log-probabilities, which are logits for
    every reader downstream -- softmax and argmax are unchanged by the missing constant,
    and cross-entropy on them is exactly the negative log of the averaged probability of
    the true class.

    The labels and the protein ids are reduced alongside, taking the first member of
    each group: candidates of one row share both, so nothing is chosen there. Groups are
    formed by value rather than by position, so a shuffled loader is handled too.

    Returns ``(outl, labels, first)``, where ``first`` is the position of each group's
    first member, for callers that have further per-sample tensors to reduce, and None
    when the split was not expanded and nothing was collapsed.
    """
    group = getattr(prot, "candidate_group", None)
    if group is None:
        return outl, labels, None
    group = group.view(-1)
    unique, inverse = torch.unique(group, sorted=True, return_inverse=True)
    probabilities = torch.softmax(outl, dim=1)
    summed = torch.zeros(
        (unique.shape[0], probabilities.shape[1]),
        dtype=probabilities.dtype,
        device=probabilities.device,
    )
    summed.index_add_(0, inverse, probabilities)
    counts = torch.zeros(
        unique.shape[0], dtype=probabilities.dtype, device=probabilities.device
    )
    counts.index_add_(0, inverse, torch.ones_like(inverse, dtype=probabilities.dtype))
    averaged = (summed / counts.unsqueeze(1)).clamp_min(1e-12).log()

    first = torch.zeros(unique.shape[0], dtype=torch.long, device=group.device)
    first.scatter_(
        0,
        inverse.flip(0),
        torch.arange(group.shape[0], device=group.device).flip(0),
    )
    if getattr(prot, "protein_id", None) is not None:
        prot.protein_id = prot.protein_id.view(-1)[first].view(-1, 1)
    return averaged, labels.view(-1)[first], first


class CandidateAccumulator:
    """Sum a pair's class probabilities across a whole evaluation pass.

    Averaging inside a batch needs every candidate of a pair to be in that batch, which
    forces the batches to be built around the groups: measured on the two-axis split,
    that leaves 128 of 198 test batches holding a single pair, so anything the batch
    computes jointly -- the ranking loss, the positive-unlabelled risk estimate, the
    reported loss -- stops seeing a mixture. Accumulating instead lets the loader keep
    its ordinary fixed-size shuffled batches: candidates meet by pair id rather than by
    proximity, and the average is taken once the pass is over.

    The reduction is exact regardless of the order rows arrive in, and each pair leaves
    exactly one row behind, so it weighs the same in the metric as a pair with a single
    candidate.
    """

    def __init__(self):
        self._sums = {}
        self._counts = {}
        self._labels = {}
        self._protein_ids = {}
        self._order = []

    def add(self, outl, prot, labels):
        """Accumulate one batch. Groups by candidate_group, which names the pair."""
        group = prot.candidate_group.view(-1).tolist()
        probabilities = torch.softmax(outl, dim=1).detach()
        labels = labels.view(-1)
        protein_ids = (
            prot.protein_id.view(-1)
            if getattr(prot, "protein_id", None) is not None
            else None
        )
        for position, pair in enumerate(group):
            if pair not in self._sums:
                self._sums[pair] = probabilities[position].clone()
                self._counts[pair] = 1
                self._labels[pair] = labels[position]
                if protein_ids is not None:
                    self._protein_ids[pair] = protein_ids[position]
                self._order.append(pair)
            else:
                self._sums[pair] += probabilities[position]
                self._counts[pair] += 1

    def __len__(self):
        return len(self._order)

    def averaged(self):
        """(log-probabilities, labels, protein ids) -- one row per pair, or None.

        Log-probabilities rather than probabilities because every reader downstream
        treats the model output as logits: softmax and argmax are unchanged by the
        constant they lack, and cross-entropy on them is exactly the negative log of the
        averaged probability of the true class.
        """
        if not self._order:
            return None
        averaged = torch.stack(
            [self._sums[pair] / self._counts[pair] for pair in self._order]
        )
        labels = torch.stack([self._labels[pair] for pair in self._order])
        protein_ids = (
            torch.stack([self._protein_ids[pair] for pair in self._order])
            if self._protein_ids
            else None
        )
        return averaged.clamp_min(1e-12).log(), labels, protein_ids
