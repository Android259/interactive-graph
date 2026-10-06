"""Branch diagnostics (--save_dynamics, --save_model_in_dynamics).

One question: does the protein half of the model influence the decision, and if it
stops, at which epoch and through which mechanism. Answered by scalars written every
epoch rather than by weights, because the answer is a curve -- the endpoint alone
cannot distinguish a branch that never learned anything from one that was learning
and then got out-competed.

Four measurements, each aimed at a different culprit:
  contribution   what the balanced accuracy loses when one pooled half is zeroed,
                 i.e. how much the classifier's decision rests on that partner
  gradient norm  whether the branch is receiving a learning signal at all
  head weights   whether the classifier itself is discounting the protein columns
  between-protein variance  whether the protein branch still tells proteins apart

Read them together: a protein contribution of zero with healthy protein gradients and
a collapsed between-protein variance is a representation problem; the same zero with
vanishing protein gradients is an optimisation problem; the same zero appearing only
after the lipid handicap is released is the lipid branch taking the decision over.
"""

import os

import torch

from candidate_averaging import CandidateAccumulator
from eval_metrics import aggregate_values, update_aggregate
from forward_args import build_forward_args


# Epochs whose weights --save_model_in_dynamics keeps, placed around the lipid
# handicap's default 50-epoch ramp (ModelConfig.lipid_path_weight_ramp_epochs): the
# first epoch, an early-training point, the two epochs either side of the release, and
# the end of a 120-epoch run. Five files of a few MB, not one per epoch.
DYNAMICS_CHECKPOINT_EPOCHS = (1, 10, 49, 51, 120)

# The model's top-level submodules are lipid1/protein1/cross_attention1 (plus the *2
# twins under double_attention) and final_layer, so a parameter's branch is decided by
# its name prefix and nothing else has to be maintained here.
DYNAMICS_BRANCH_PREFIXES = {
    "protein": ("protein1.", "protein2."),
    "lipid": ("lipid1.", "lipid2."),
    "cross": ("cross_attention1.", "cross_attention2."),
    "head": ("final_layer.",),
}


class BranchDynamics:
    """Per-epoch branch diagnostics of one run.

    `valid_loader` is the run's final validation loader (possibly preassembled), and
    `losses` its TaskLosses, so the ablated passes score exactly like the real one.
    """

    def __init__(self, conf, model, device, valid_loader, writer, losses):
        self.conf = conf
        self.model = model
        self.device = device
        self.valid_loader = valid_loader
        self.writer = writer
        self.losses = losses
        self.branch_parameters = (
            {
                branch: [
                    parameter
                    for name, parameter in model.named_parameters()
                    if name.startswith(prefixes)
                ]
                for branch, prefixes in DYNAMICS_BRANCH_PREFIXES.items()
            }
            if conf.save_dynamics
            else {}
        )
        self.grad_stats = {
            branch: {"sum": 0.0, "batches": 0} for branch in self.branch_parameters
        }

    def reset_grad_stats(self):
        """Start a fresh epoch's gradient-norm average."""
        for accumulator in self.grad_stats.values():
            accumulator["sum"] = 0.0
            accumulator["batches"] = 0

    def accumulate_grad_norms(self):
        """Add this batch's per-branch gradient norm to the epoch's running mean.

        Called between backward() and the optimizer step, so the gradients read are the ones
        the step is about to apply. Under AMP the caller unscales first: otherwise every
        number would carry the loss scaler's factor, which changes on its own schedule and
        would show up as branch dynamics that never happened.
        """
        for branch, parameters in self.branch_parameters.items():
            squared = 0.0
            for parameter in parameters:
                if parameter.grad is not None:
                    squared += float(parameter.grad.detach().pow(2).sum())
            accumulator = self.grad_stats[branch]
            accumulator["sum"] += squared ** 0.5
            accumulator["batches"] += 1

    def _valid_pass(self, collect_pooled=False):
        """One validation pass under whatever ablation flags are currently set.

        Built from the same update_aggregate/aggregate_values pair the real validation uses,
        so the balanced accuracies compared across these passes are one quantity rather than
        two definitions of it.
        """
        conf, model, device = self.conf, self.model, self.device
        model.eval()
        stats = {
            "TP": 0,
            "FP": 0,
            "TN": 0,
            "FN": 0,
            "loss": 0.0,
            "count": 0,
            "loss_count": 0,
        }
        pooled_lipid = []
        pooled_protein = []
        protein_ids = []
        # On an expanded split the rows are candidates, not pairs, so the pass collects them
        # and the metric is computed once from the per-pair averages (see run_test for the
        # same shape). Without the flag this is None and nothing changes.
        accumulator = CandidateAccumulator() if conf.eval_average_candidates else None
        seen_pairs = set()
        with torch.no_grad():
            for prot, lipid in self.valid_loader:
                prot = prot.to(device, non_blocking=True)
                lipid = lipid.to(device, non_blocking=True)
                labels = prot.inter.to(device, non_blocking=True).long()
                outl = model(**build_forward_args(conf, prot, lipid))
                if accumulator is not None:
                    accumulator.add(outl, prot, labels)
                else:
                    loss = self.losses.eval_task_loss(outl, labels)
                    update_aggregate(stats, outl.argmax(dim=1), labels, loss, labels.shape[0])
                # None under --deepclip, which builds no Final_Layer to stash them on --
                # and has no two pooled partners to stash either, the lipid being its whole
                # input. Everything downstream of `partners is not None` (the pooled-vector
                # diagnostics, _head_input_weight_norms) is skipped for it as a result.
                partners = getattr(
                    getattr(model, "final_layer", None), "_pooled_partners", None
                )
                if collect_pooled and partners is not None:
                    # One pooled vector per candidate on an expanded split; keeping the first
                    # row of each pair leaves this diagnostic one row per pair, as it is when
                    # nothing is expanded.
                    keep = slice(None)
                    if accumulator is not None:
                        keep = []
                        for position, pair in enumerate(
                            prot.candidate_group.view(-1).tolist()
                        ):
                            if pair not in seen_pairs:
                                seen_pairs.add(pair)
                                keep.append(position)
                        keep = torch.tensor(keep, dtype=torch.long)
                    pooled_lipid.append(partners[0][keep].cpu())
                    pooled_protein.append(partners[1][keep].cpu())
                    protein_ids.append(prot.protein_id.view(-1)[keep].cpu())
        if accumulator is not None:
            averaged, labels, _ = accumulator.averaged()
            loss = self.losses.eval_task_loss(averaged, labels)
            update_aggregate(stats, averaged.argmax(dim=1), labels, loss, labels.shape[0])
        metrics = aggregate_values(stats)
        if not pooled_protein:
            return metrics, None
        return metrics, (
            torch.cat(pooled_lipid),
            torch.cat(pooled_protein),
            torch.cat(protein_ids),
        )

    def _ablated_valid(self, field, collect_pooled=False):
        """Validate with one pooled half zeroed, then put the flag back as it was.

        The flags are the ones Final_Layer already implements for whole-run ablations, read
        per forward, so switching them here needs nothing from the architecture. What this
        measures is narrower than a real --lipid_only run: cross-attention stays on, so the
        protein's influence on the lipid representation survives and only the classifier's
        direct protein input is removed. That is the intended question -- does the head use
        the protein channel -- and the narrower reading is the reason it is worth stating.
        """
        previous = getattr(self.conf, field)
        setattr(self.conf, field, True)
        try:
            return self._valid_pass(collect_pooled=collect_pooled)
        finally:
            setattr(self.conf, field, previous)

    @staticmethod
    def _between_protein_variance_share(vectors, protein_ids):
        """Share of the pooled protein vector's variance that lies between proteins.

        Near zero means the branch hands the classifier nearly the same vector whichever
        protein it was given, and no downstream layer can recover a distinction that is not
        in its input. Total variance is summed over dimensions, so the number cannot be
        carried by one wide dimension, and lands in [0, 1].
        """
        vectors = vectors.double()
        centered = vectors - vectors.mean(dim=0)
        total = float((centered ** 2).sum())
        if total <= 0.0:
            return 0.0
        grand_mean = vectors.mean(dim=0)
        between = 0.0
        for protein in protein_ids.unique():
            rows = vectors[protein_ids == protein]
            between += float(rows.shape[0] * ((rows.mean(dim=0) - grand_mean) ** 2).sum())
        return between / total

    def _head_input_weight_norms(self, lipid_width):
        """Norms of the classifier's first-layer weights on each half of its input.

        The fusion is a concatenation, [lipid | protein] (Final_Layer.forward), so those
        columns split by partner and their norms say how much of the decision each half is
        even allowed to reach. Bilinear fusion mixes the halves before the layer and leaves
        no such split, hence the None.
        """
        if self.conf.bilinear_fusion:
            return None
        linear = next(
            (
                layer
                for layer in self.model.final_layer.binar
                if isinstance(layer, torch.nn.Linear)
            ),
            None,
        )
        if linear is None or linear.weight.shape[1] <= lipid_width:
            return None
        weight = linear.weight.detach()
        return float(weight[:, :lipid_width].norm()), float(weight[:, lipid_width:].norm())

    def log(self, epoch_index, valid_metrics):
        """Write this epoch's branch diagnostics to TensorBoard and to the run log."""
        full_ba = valid_metrics.get("balanced_accuracy")
        # The pooled halves are collected on the first ablated pass, not on a third full
        # one: the stash in Final_Layer is taken before the zeroing, so an ablated pass
        # reports exactly the vectors the unablated model computed.
        without_protein, pooled = self._ablated_valid("lipid_only", collect_pooled=True)
        without_lipid, _ = self._ablated_valid("protein_only")

        scalars = {
            "valid BA without protein": without_protein.get("balanced_accuracy"),
            "valid BA without lipid": without_lipid.get("balanced_accuracy"),
        }
        if full_ba is not None:
            scalars["protein contribution"] = full_ba - without_protein["balanced_accuracy"]
            scalars["lipid contribution"] = full_ba - without_lipid["balanced_accuracy"]

        for branch, accumulator in self.grad_stats.items():
            if accumulator["batches"]:
                scalars[f"grad norm {branch}"] = accumulator["sum"] / accumulator["batches"]

        between_share = None
        if pooled is not None:
            pooled_lipid, pooled_protein, protein_ids = pooled
            between_share = self._between_protein_variance_share(pooled_protein, protein_ids)
            scalars["pooled protein between-protein variance"] = between_share
            scalars["pooled protein norm"] = float(pooled_protein.norm(dim=1).mean())
            scalars["pooled lipid norm"] = float(pooled_lipid.norm(dim=1).mean())
            head_norms = self._head_input_weight_norms(pooled_lipid.shape[1])
            if head_norms is not None:
                scalars["head weight norm lipid"] = head_norms[0]
                scalars["head weight norm protein"] = head_norms[1]

        for name, value in scalars.items():
            if value is not None:
                self.writer.add_scalar(f"epoch/{name}", value, epoch_index + 1)

        def show(value):
            return "n/a" if value is None else f"{value:.4f}"

        print(
            "dynamics: "
            f"BA full {show(full_ba)} "
            f"| no protein {show(scalars.get('valid BA without protein'))} "
            f"(delta {show(scalars.get('protein contribution'))}) "
            f"| no lipid {show(scalars.get('valid BA without lipid'))} "
            f"(delta {show(scalars.get('lipid contribution'))}) "
            f"| grad protein {show(scalars.get('grad norm protein'))} "
            f"lipid {show(scalars.get('grad norm lipid'))} "
            f"| head |W| protein {show(scalars.get('head weight norm protein'))} "
            f"lipid {show(scalars.get('head weight norm lipid'))} "
            f"| between-protein variance {show(between_share)}"
        )

    def save_milestone(self, epoch_1based, run_models_dir):
        """Keep the weights of a milestone epoch, for probes no scalar can anticipate.

        `run_models_dir` is models/<label>/<excluded_set>/; the files go to its dynamics/.
        """
        if epoch_1based not in DYNAMICS_CHECKPOINT_EPOCHS:
            return
        directory = os.path.join(run_models_dir, "dynamics")
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"seed{self.conf.seed}_epoch{epoch_1based}.pt")
        torch.save(self.model.state_dict(), path)
        print(f"dynamics: saved weights of epoch {epoch_1based} to {path}")
