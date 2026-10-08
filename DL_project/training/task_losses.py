"""Everything the run's task loss depends on, built once from the train split.

Per-row sample weights (Tanimoto / protein / lipid / marginal weighting), the PU class
prior (train-wide or per lipid subclass), class weights, the logit-adjustment bias and
the group-DRO state are all derived here from train rows only, and the three loss
selections -- train batch, validation batch, test batch -- read them from one object.
The selection order (pu_loss > loss_type) is the same in all three.
"""

import torch
import torch.nn.functional as F

from architecture.loss import (
    GroupDROState,
    Non_Negative_Positive_Unlabeled_loss,
    focal_loss,
    logit_adjustment_bias,
    pairwise_ranking_loss,
)
from dataloader.lipid_classes import class_level_positive_labels
from dataloader.lipid_subclass_blocks import article_subclass_species
from dataloader.protein_graph_builder import FAMILY_NAMES


# Below this many train rows a subclass's count-derived prior is noise, not a prior --
# the classification file puts one or two species in several of its 23 subclasses.
PU_SUBCLASS_MINIMUM_TRAIN_ROWS = 20


def build_pu_subclass_priors(conf, dataset, train_labels):
    """(per-subclass PU priors, pair_id -> prior slot) for --pu_rho_by_subclass.

    Each subclass of the source paper gets conf.effective_pu_rho applied to its OWN
    train counts, so a subclass the proteins mostly do take carries a higher prior than
    one they mostly do not, instead of both being told the train-wide number.

    Two deliberate fallbacks, both onto the train-wide conf.pu_rho, both reported:
    a subclass with fewer than PU_SUBCLASS_MINIMUM_TRAIN_ROWS train rows (of 23
    subclasses, several hold one or two species, where a count-derived prior is noise),
    and a species the classification file does not name. They share the last slot.

    The returned row vector is indexed by pair_id (original interaction-table row
    position) and covers train, validation and test rows: the priors are derived from
    train only, but the reported valid/test PU loss has to look a row's subclass up too.
    """
    subclass_of_species = {
        species: name
        for name, members in article_subclass_species().items()
        for species in members
    }
    frames = [dataset.csvtrain, dataset.csvalidate, dataset.csvtest]
    names = sorted({
        subclass_of_species[species]
        for frame in frames
        for species in frame["FullIdentityOfLipid"].astype(str)
        if species in subclass_of_species
    })
    fallback_slot = len(names)
    slot_of_name = {name: slot for slot, name in enumerate(names)}

    train_species = dataset.csvtrain["FullIdentityOfLipid"].astype(str).to_numpy()
    train_slots = torch.as_tensor(
        [
            slot_of_name.get(subclass_of_species.get(species), fallback_slot)
            for species in train_species
        ],
        dtype=torch.long,
    )
    labels = train_labels.view(-1)
    if labels.shape[0] != train_slots.shape[0]:
        raise ValueError(
            f"train labels {labels.shape[0]} do not match train rows {train_slots.shape[0]}"
        )

    priors = torch.full((fallback_slot + 1,), float(conf.pu_rho), dtype=torch.float32)
    derived, fell_back = [], []
    for slot, name in enumerate(names):
        rows = train_slots == slot
        positive_count = float((rows & (labels == 1)).sum())
        unlabeled_count = float((rows & (labels == 0)).sum())
        if positive_count + unlabeled_count < PU_SUBCLASS_MINIMUM_TRAIN_ROWS:
            fell_back.append(f"{name}={int(positive_count + unlabeled_count)}rows")
            continue
        # effective_pu_rho's formula lands on exactly 1.0 for a subclass whose train rows
        # are all labeled positives and on exactly 0.0 when it has no positives and the
        # fraction is 0, and it rejects both. Those are the only two degenerate cases:
        # with unlabeled rows present and a fraction below 1 the value is always interior.
        if not (unlabeled_count > 0.0 and (
            positive_count > 0.0 or conf.pu_unlabeled_positive_fraction > 0.0
        )):
            fell_back.append(f"{name}=one class only")
            continue
        priors[slot] = conf.effective_pu_rho(
            positive_count=positive_count, unlabeled_count=unlabeled_count
        )
        derived.append(f"{name}={float(priors[slot]):.4f}")

    highest_pair_id = max(int(frame["pair_id"].max()) for frame in frames)
    row_group = torch.full((highest_pair_id + 1,), fallback_slot, dtype=torch.long)
    for frame in frames:
        pair_ids = torch.as_tensor(frame["pair_id"].to_numpy(), dtype=torch.long)
        species = frame["FullIdentityOfLipid"].astype(str)
        row_group[pair_ids] = torch.as_tensor(
            [
                slot_of_name.get(subclass_of_species.get(value), fallback_slot)
                for value in species
            ],
            dtype=torch.long,
        )

    print(f"PU rho by subclass : {', '.join(derived)}")
    print(
        "PU rho by subclass fallback to "
        f"{conf.pu_rho:.6f} : {', '.join(fell_back) if fell_back else 'none'}"
        " + unclassified species"
    )
    return priors, row_group


class TaskLosses:
    """Loss weights derived from the train split, and the loss of each phase.

    Construction prints the same setup lines, in the same order, the training script
    always printed, and sets conf.pu_rho under --pu_loss (the train-wide prior is a
    property of the split, so the run report records the value actually used).
    """

    def __init__(self, conf, train_dataset, device):
        self.conf = conf
        self.device = device

        common_weights_parts = []
        if conf.tanimoto_weight:
            common_weights_parts.append(train_dataset.get_tanimoto_weights().to(device))
        if conf.protein_group_weight:
            protein_group_weights = train_dataset.get_protein_weights().to(device)
            common_weights_parts.append(protein_group_weights)
        if conf.protein_balance_weight:
            common_weights_parts.append(
                train_dataset.get_protein_balance_weights().to(device)
            )
        if conf.protein_class_weight:
            protein_class_weights = train_dataset.get_protein_class_weights().to(device)
            common_weights_parts.append(protein_class_weights)
        if conf.protein_class_sqrt_weight:
            protein_class_sqrt_weights = train_dataset.get_protein_class_weights(
                square_root=True,
            ).to(device)
            common_weights_parts.append(protein_class_sqrt_weights)
        if conf.lipid_propensity_weight:
            common_weights_parts.append(
                train_dataset.get_lipid_propensity_weights().to(device)
            )
        if conf.marginal_balance_weight:
            common_weights_parts.append(
                train_dataset.get_marginal_balance_weights().to(device)
            )
        self.common_weights = (
            torch.stack(common_weights_parts).mean(dim=0)
            if common_weights_parts
            else None
        )

        self.train_labels = torch.as_tensor(
            class_level_positive_labels(train_dataset.csvtrain).values
            if conf.lipid_class_targets
            else train_dataset.csvtrain["Interaction"].values,
            dtype=torch.long,
        )
        class_counts = torch.bincount(self.train_labels, minlength=2).float()
        if conf.pu_loss:
            conf.pu_rho = conf.effective_pu_rho(
                positive_count=class_counts[1].item(),
                unlabeled_count=class_counts[0].item(),
            )
            print(f"PU rho : {conf.pu_rho:.6f}")
        self.pu_group_priors, self.pu_row_group = (
            build_pu_subclass_priors(conf, train_dataset, self.train_labels)
            if conf.pu_loss and conf.pu_rho_by_subclass
            else (None, None)
        )

        self.class_weights = None
        if conf.class_weights:
            self.class_weights = (
                class_counts.sum() / (2.0 * class_counts.clamp_min(1.0))
            ).to(device)
            print(f"class weights : {self.class_weights.detach().cpu().tolist()}")
        else:
            print("class weights : disabled")

        self.logit_adjustment_bias_tensor = None
        if conf.logit_adjustment:
            self.logit_adjustment_bias_tensor = logit_adjustment_bias(
                class_counts, tau=conf.logit_adjustment_tau
            ).to(device)
            print(
                "logit adjustment bias : "
                f"{self.logit_adjustment_bias_tensor.detach().cpu().tolist()}"
            )

        self.group_dro_state = None
        if conf.group_dro:
            family_train_counts = torch.tensor(
                [
                    float((train_dataset.csvtrain["ProteinDomain"] == name).sum())
                    for name in FAMILY_NAMES
                ],
                dtype=torch.float32,
            ).to(device)
            self.group_dro_state = GroupDROState(
                family_train_counts,
                step_size=conf.group_dro_step_size,
                group_adj=conf.group_dro_adj,
            )
            print(
                "group DRO train counts : "
                + ", ".join(
                    f"{name}={int(count)}"
                    for name, count in zip(FAMILY_NAMES, family_train_counts.tolist())
                )
            )

    def batch_sample_weights(self, prot, sample_count):
        """Per-row loss weights for this batch, or None when the run weights nothing.

        None rather than a vector of ones. Every loss below already has a None branch that
        takes the plain mean, and that is the *same number*: multiplying by 1.0 is exact in
        IEEE 754, so `(x * ones).sum() / ones.sum().clamp_min(1e-8)` and `x.mean()` agree bit
        for bit -- checked over 8000 random batches at sizes 8, 16, 64 and 1300, zero
        disagreements. What it removes is a weight vector as long as the train split, a
        gather per batch, an elementwise multiply and a second reduction, none of which could
        ever change an unweighted run's result.

        Only reachable from the training loop. Validation and test never pass sample weights,
        which matters because id2pos covers train rows alone: a validation row's tanimoto_pos
        is -1, and -1 indexes the last weight instead of raising.
        """
        common_weights = self.common_weights
        if common_weights is None:
            return None
        pos = prot.tanimoto_pos.view(-1).to(self.device, non_blocking=True)[:sample_count]
        if pos.shape[0] != sample_count:
            raise ValueError(
                f"tanimoto positions count {pos.shape[0]} "
                f"does not match batch size {sample_count}"
            )
        if (pos < 0).any() or (pos >= common_weights.shape[0]).any():
            invalid_positions = pos[
                (pos < 0) | (pos >= common_weights.shape[0])
            ].detach().cpu().tolist()
            raise ValueError(
                "tanimoto positions are outside the train weight table: "
                f"{invalid_positions}"
            )
        return common_weights[pos]

    def pu_prior_and_groups(self, prot, sample_count):
        """(prior, group_ids) for one nnPU call.

        The train-wide scalar unless --pu_rho_by_subclass, in which case the per-subclass
        prior vector plus this batch's subclass index per row, looked up by pair_id.
        """
        if self.pu_group_priors is None:
            return self.conf.pu_rho, None
        pair_ids = prot.pair_id.view(-1)[:sample_count].detach().cpu()
        return self.pu_group_priors, self.pu_row_group[pair_ids]

    def train_loss(self, model, outl, prot, interaction_labels, sample_count):
        """Task loss of one training batch (no adversary or sparsity terms)."""
        conf = self.conf
        loss_logits = (
            outl + self.logit_adjustment_bias_tensor
            if conf.logit_adjustment
            else outl
        )

        if conf.pu_loss:
            sample_weights = self.batch_sample_weights(prot, sample_count)
            pu_prior, pu_groups = self.pu_prior_and_groups(prot, sample_count)
            los = Non_Negative_Positive_Unlabeled_loss(
                loss_logits,
                interaction_labels.long(),
                pu_prior,
                beta=conf.pu_beta,
                gamma=conf.pu_gamma,
                tau=conf.pu_tau,
                cap=conf.pu_loss_cap,
                sample_weights=sample_weights,
                group_ids=pu_groups,
            )
        elif conf.loss_type == "pairwise_rank":
            sample_weights = self.batch_sample_weights(prot, sample_count)
            los = pairwise_ranking_loss(
                loss_logits,
                interaction_labels.long(),
                sample_weights=sample_weights,
                protein_ids=(
                    prot.protein_id.view(-1)[:sample_count]
                    if conf.rank_within_protein else None
                ),
            )
        elif conf.loss_type == "cross_entropy":
            sample_weights = self.batch_sample_weights(prot, sample_count)
            if conf.focal_loss:
                los_unred = focal_loss(
                    loss_logits,
                    interaction_labels.long(),
                    gamma=conf.focal_gamma,
                    class_weights=self.class_weights,
                    reduction="none",
                )
            else:
                los_unred = F.cross_entropy(loss_logits, interaction_labels.long(), weight=self.class_weights, reduction="none")
            if conf.group_dro:
                # Group DRO's own worst-family weighting replaces the plain (or
                # tanimoto-weighted) batch mean below; sample_weights is computed
                # above unconditionally but not read on this path.
                family_index = prot.family.view(sample_count, -1).argmax(dim=1)
                los = self.group_dro_state.step(los_unred, family_index)
            else:
                # The None branch is the same number, not an approximation of it:
                # see batch_sample_weights. It matches what focal_loss and
                # the PU loss already do when handed no weights.
                los = (
                    los_unred.mean()
                    if sample_weights is None
                    else (los_unred * sample_weights).sum()
                    / sample_weights.sum().clamp_min(1e-8)
                )
        else:
            los=conf.loss(outl,interaction_labels.long())
        return los

    def valid_loss(self, model, outl, prot, interaction_labels, sample_count):
        """Task loss of one validation batch: no sample weights, no logit adjustment."""
        conf = self.conf
        if conf.pu_loss:
            pu_prior, pu_groups = self.pu_prior_and_groups(prot, sample_count)
            los = Non_Negative_Positive_Unlabeled_loss(
                outl,
                interaction_labels.long(),
                pu_prior,
                beta=conf.pu_beta,
                gamma=conf.pu_gamma,
                tau=conf.pu_tau,
                cap=conf.pu_loss_cap,
                group_ids=pu_groups,
            )
        elif conf.loss_type == "pairwise_rank":
            los = pairwise_ranking_loss(
                outl,
                interaction_labels.long(),
                protein_ids=(
                    prot.protein_id.view(-1) if conf.rank_within_protein else None
                ),
            )
        else:
            los = conf.loss(outl, interaction_labels.long())
        return los

    def test_losses(self, outl, prot, interaction_labels, sample_count):
        """(batch loss, per-row losses) of one test batch.

        Per-row losses feed the per-protein table of the test report. Where the loss
        does not decompose per row (PU risk, ranking), the batch loss is spread evenly.
        """
        conf = self.conf
        if conf.pu_loss:
            pu_prior, pu_groups = self.pu_prior_and_groups(prot, sample_count)
            los = Non_Negative_Positive_Unlabeled_loss(
                outl,
                interaction_labels.long(),
                pu_prior,
                beta=conf.pu_beta,
                gamma=conf.pu_gamma,
                tau=conf.pu_tau,
                cap=conf.pu_loss_cap,
                group_ids=pu_groups,
            )
            sample_losses = torch.full(
                (sample_count,),
                los.item() if isinstance(los, torch.Tensor) else los,
                device=outl.device,
            )
        elif conf.loss_type == "cross_entropy":
            sample_losses = F.cross_entropy(
                outl,
                interaction_labels.long(),
                reduction="none",
            )
            los = sample_losses.mean()
        elif conf.loss_type == "pairwise_rank":
            los = pairwise_ranking_loss(
                outl,
                interaction_labels.long(),
                protein_ids=(
                    prot.protein_id.view(-1) if conf.rank_within_protein else None
                ),
            )
            sample_losses = torch.full(
                (sample_count,),
                los.item() if isinstance(los, torch.Tensor) else los,
                device=outl.device,
            )
        else:
            los = conf.loss(outl, interaction_labels.long())
            sample_losses = torch.full(
                (sample_count,),
                los.item() if isinstance(los, torch.Tensor) else los,
                device=outl.device,
            )
        return los, sample_losses

    def eval_task_loss(self, outl, labels):
        """Validation-style task loss (mirrors the validation branch), no sample weighting.

        Keeps the train-wide PU prior even under --pu_rho_by_subclass: it is handed logits
        and labels without the pair ids a subclass lookup needs, so a bilevel step scores
        with the pooled prior while the epoch's own train/valid/test losses use per-subclass
        ones.
        """
        conf = self.conf
        if conf.pu_loss:
            return Non_Negative_Positive_Unlabeled_loss(
                outl,
                labels.long(),
                conf.pu_rho,
                beta=conf.pu_beta,
                gamma=conf.pu_gamma,
                tau=conf.pu_tau,
                cap=conf.pu_loss_cap,
            )
        if conf.loss_type == "pairwise_rank":
            # Pooled pairing even under --rank_within_protein: this helper is reached only
            # from bilevel_lambda_step, which is handed logits and labels without the
            # protein graph they came from. Combining --bilevel with --rank_within_protein
            # therefore tunes lambda against the pooled ranking while training minimises the
            # per-protein one; plumb prot through if that combination is ever run for real.
            return pairwise_ranking_loss(outl, labels.long())
        return conf.loss(outl, labels.long())

    def batched_block_loss(self, outl, labels, protein_ids=None):
        """The evaluation loss of one averaged block, computed the way a pass computes it.

        Cross-entropy decomposes per row, so cutting the block into chunks changes nothing.
        The ranking loss and the positive-unlabelled risk do not: both are defined over the
        rows in front of them, and evaluating them once over a whole block forms pairs, and
        estimates class priors, on a sample the training loss never sees at once. The block
        is therefore cut into chunks the size of a training batch and the chunk losses are
        averaged by row count -- the same arithmetic the per-batch path performs, so the
        validation curve stays comparable with the training one.

        Returns (weighted mean loss, row count).
        """
        conf = self.conf
        rows = int(labels.shape[0])
        if rows == 0:
            return 0.0, 0
        size = max(1, int(conf.batch))
        total = 0.0
        for start in range(0, rows, size):
            stop = min(start + size, rows)
            chunk_labels = labels[start:stop]
            if (
                conf.loss_type == "pairwise_rank"
                and conf.rank_within_protein
                and protein_ids is not None
            ):
                chunk_loss = pairwise_ranking_loss(
                    outl[start:stop],
                    chunk_labels.long(),
                    protein_ids=protein_ids.view(-1)[start:stop],
                )
            else:
                chunk_loss = self.eval_task_loss(outl[start:stop], chunk_labels)
            value = (
                chunk_loss.item() if isinstance(chunk_loss, torch.Tensor) else chunk_loss
            )
            total += value * (stop - start)
        return total / rows, rows
