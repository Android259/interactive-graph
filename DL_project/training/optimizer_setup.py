"""Optimizer parameter groups, the bilevel hyper-optimizer and the lr schedule.

Which parameters get their own group, and why:
  gate params (width gates)        stepped on VALIDATION by the hyper-optimizer (--bilevel)
  ConcreteDropout logits           train objective, never weight-decayed
  Final_Layer.bilinear             --bilinear_weight_decay
  DeepCLIP gate                    --deepclip_gate_weight_decay
  thematic ForcedInteraction       --thematical_interaction_lr (lr multiplier)
  lipid branch                     --lipid_path_handicap (lr scaled per epoch)
"""

import torch

from architecture.mlp_utils import collect_gate_parameters, ConcreteDropout


THEMATICAL_INTERACTION_LR_MULTIPLIER = 5.0


class OptimizerSetup:
    """Builds `optimizer` (and `hyper_optimizer` under --bilevel) for one model."""

    def __init__(self, conf, model):
        # Parameter split for bilevel width search. Gate params (lambda) are optimized on the
        # validation split; theta (weights) on train. ConcreteDropout logits are trained on the
        # train objective (like theta) but always excluded from weight decay.
        gate_params = collect_gate_parameters(model)
        gate_param_ids = {id(p) for p in gate_params}
        dropout_logit_params = [
            module.logit for module in model.modules() if isinstance(module, ConcreteDropout)
        ]
        dropout_logit_ids = {id(p) for p in dropout_logit_params}
        # --bilinear_weight_decay: self.bilinear's weight/bias get their own optimizer group
        # instead of following the global --weight_decay, so that one tensor (the only one
        # whose output has no built-in ceiling, and whose size grows cubically with --hiddim
        # under bilinear_fusion) can be reined in harder without over-penalising the rest of
        # the network. Empty list, no-op group, when bilinear_fusion is off.
        # getattr on the MODEL, not just on final_layer: --deepclip builds architecture/
        # deepclip.py alone and has no Final_Layer at all (InteractionClassification.__init__
        # returns before building one), so this and the thematic lookup below have nothing to
        # read. Both resolve to None there, which is the same no-op empty optimizer group a
        # run with bilinear_fusion/thematical_paths off already gets.
        final_layer = getattr(model, "final_layer", None)
        bilinear_module = getattr(final_layer, "bilinear", None)
        bilinear_params = list(bilinear_module.parameters()) if bilinear_module is not None else []
        bilinear_param_ids = {id(p) for p in bilinear_params}
        # --deepclip_gate_weight_decay: architecture/deepclip.py's DeepCLIP.gate (the
        # --deepclip_protein_gate MLP) gets its own optimizer group the same way bilinear_
        # module does just above -- getattr on the MODEL so a non-deepclip run (no
        # self.deepclip attribute at all) resolves to the same no-op empty group.
        deepclip_module = getattr(model, "deepclip", None)
        deepclip_gate_module = getattr(deepclip_module, "gate", None)
        deepclip_gate_params = (
            list(deepclip_gate_module.parameters()) if deepclip_gate_module is not None else []
        )
        deepclip_gate_param_ids = {id(p) for p in deepclip_gate_params}
        # --thematical_interaction_lr (ModelConfig docstring, files/results/thematical_paths_dynamics_
        # and_pair_auc.md section 7): ForcedInteraction's parameters sit behind two chained
        # hard-normalisation ops MLB's own paper reports as slow/hyperparameter-sensitive to
        # converge -- give all three sites (geom/chem/level2) their own optimizer group at a
        # higher lr instead of raising --lr globally. Empty list, no-op group, when off or
        # not a thematical_paths run.
        thematic_head = getattr(final_layer, "thematical_head", None)
        thematic_interaction_params = (
            list(thematic_head.geom_interaction.parameters())
            + list(thematic_head.chem_interaction.parameters())
            + list(thematic_head.group_interaction.parameters())
            if (thematic_head is not None and conf.thematical_interaction_lr)
            else []
        )
        thematic_interaction_param_ids = {id(p) for p in thematic_interaction_params}
        bilinear_weight_decay = (
            conf.weight_decay if conf.bilinear_weight_decay is None else conf.bilinear_weight_decay
        )
        deepclip_gate_weight_decay = (
            conf.weight_decay
            if conf.deepclip_gate_weight_decay is None
            else conf.deepclip_gate_weight_decay
        )
        theta_params = [
            p
            for p in model.parameters()
            if id(p) not in gate_param_ids
            and id(p) not in dropout_logit_ids
            and id(p) not in bilinear_param_ids
            and id(p) not in thematic_interaction_param_ids
            and id(p) not in deepclip_gate_param_ids
        ]

        self.lipid_branch_param_ids = (
            {id(p) for p in model.lipid_branch_parameters()}
            if conf.lipid_path_handicap
            else set()
        )

        self.gate_params = gate_params
        self.hyper_optimizer = None
        if conf.bilevel and gate_params:
            # theta (with weight decay) + dropout logits (no weight decay) on train; the main
            # optimizer never touches the gate params -- those are stepped on validation below.
            main_groups = [{"params": theta_params, "weight_decay": conf.weight_decay}]
            if bilinear_params:
                main_groups.append(
                    {"params": bilinear_params, "weight_decay": bilinear_weight_decay}
                )
            if deepclip_gate_params:
                main_groups.append(
                    {"params": deepclip_gate_params, "weight_decay": deepclip_gate_weight_decay}
                )
            if dropout_logit_params:
                main_groups.append({"params": dropout_logit_params, "weight_decay": 0.0})
            if thematic_interaction_params:
                main_groups.append({
                    "params": thematic_interaction_params,
                    "weight_decay": conf.weight_decay,
                    "lr": conf.lr * THEMATICAL_INTERACTION_LR_MULTIPLIER,
                })
            self.optimizer = torch.optim.Adam(self.split_lipid_branch(main_groups), lr=conf.lr)
            self.hyper_optimizer = torch.optim.Adam(gate_params, lr=conf.bilevel_lr)
        elif dropout_logit_params:
            # Not bilevel: everything trains on the train objective, but keep dropout logits out
            # of weight decay. Gates (if any) are learned via the train-loss penalty below.
            groups = [
                {
                    "params": theta_params + gate_params,
                    "weight_decay": conf.weight_decay,
                },
                {"params": dropout_logit_params, "weight_decay": 0.0},
            ]
            if bilinear_params:
                groups.append({"params": bilinear_params, "weight_decay": bilinear_weight_decay})
            if deepclip_gate_params:
                groups.append(
                    {"params": deepclip_gate_params, "weight_decay": deepclip_gate_weight_decay}
                )
            if thematic_interaction_params:
                groups.append({
                    "params": thematic_interaction_params,
                    "weight_decay": conf.weight_decay,
                    "lr": conf.lr * THEMATICAL_INTERACTION_LR_MULTIPLIER,
                })
            self.optimizer = torch.optim.Adam(self.split_lipid_branch(groups), lr=conf.lr)
        else:
            # No bilevel, no ConcreteDropout: everything (including gate_params, if any exist
            # without bilevel search being on) trains as one plain group at the top-level
            # weight_decay, same as before this split existed -- only bilinear_params and
            # deepclip_gate_params are carved out, not theta_params, since theta_params also
            # drops gate_param_ids/dropout_logit_ids that this branch never re-adds.
            base_params = [
                p for p in model.parameters()
                if id(p) not in bilinear_param_ids
                and id(p) not in thematic_interaction_param_ids
                and id(p) not in deepclip_gate_param_ids
            ]
            groups = [{"params": base_params}]
            if bilinear_params:
                groups.append({"params": bilinear_params, "weight_decay": bilinear_weight_decay})
            if deepclip_gate_params:
                groups.append(
                    {"params": deepclip_gate_params, "weight_decay": deepclip_gate_weight_decay}
                )
            if thematic_interaction_params:
                groups.append({
                    "params": thematic_interaction_params,
                    "lr": conf.lr * THEMATICAL_INTERACTION_LR_MULTIPLIER,
                })
            self.optimizer = torch.optim.Adam(
                self.split_lipid_branch(groups),
                lr=conf.lr,
                weight_decay=conf.weight_decay,
            )

        # Resolved once. param_groups is a stable list of stable dicts, so holding the dicts
        # themselves saves rescanning it on every epoch and every log line, and keeps the
        # handicap's two call sites from each re-deriving which group is which.
        self.lipid_lr_groups = [g for g in self.optimizer.param_groups if g.get("lipid_branch")]
        self.lipid_lr_reference = next(
            (g for g in self.optimizer.param_groups if not g.get("lipid_branch")), None
        )

    def split_lipid_branch(self, groups):
        """Give the lipid branch its own optimizer group so its lr can be handicapped.

        Splitting by PARAMETER, not by a hook on the graph, is what makes the handicap
        stay off the protein: past cross-attention the lipid activations are a function of
        both partners, so anything attached there would slow the protein encoder too. Each
        split group inherits its parent's settings (weight decay above all) and differs
        only in lr, and is tagged so apply_lipid_path_handicap can find it again.
        """
        if not self.lipid_branch_param_ids:
            return groups
        split = []
        for group in groups:
            lipid = [p for p in group["params"] if id(p) in self.lipid_branch_param_ids]
            rest = [p for p in group["params"] if id(p) not in self.lipid_branch_param_ids]
            if rest:
                split.append({**group, "params": rest})
            if lipid:
                split.append({**group, "params": lipid, "lipid_branch": True})
        return split

    def apply_lipid_path_handicap(self, weight):
        """Set the lipid branch's lr to ``weight`` times the rest of the model's.

        Read off a sibling group rather than off conf.lr so whatever the lr schedule has
        done this epoch is inherited: lr_warmup_cosine rewrites every group's lr from its
        own previous value, so anchoring to conf.lr would silently undo the warm-up and the
        cosine decay for the lipid branch alone. Called at the top of each epoch, after the
        previous epoch's scheduler step.
        """
        for group in self.lipid_lr_groups:
            group["lr"] = self.lipid_lr_reference["lr"] * weight


def build_lr_scheduler(conf, optimizer):
    """Linear warm-up then cosine decay under --lr_warmup_cosine, else None."""
    lr_scheduler = None
    if conf.lr_warmup_cosine:
        warmup_epochs = min(conf.lr_warmup_epochs, max(conf.ep - 1, 0))
        cosine_epochs = max(conf.ep - warmup_epochs, 1)
        cosine_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=cosine_epochs, eta_min=conf.lr * conf.lr_min_factor
        )
        if warmup_epochs > 0:
            lr_scheduler = torch.optim.lr_scheduler.SequentialLR(
                optimizer,
                schedulers=[
                    torch.optim.lr_scheduler.LinearLR(
                        optimizer, start_factor=0.1, total_iters=warmup_epochs
                    ),
                    cosine_scheduler,
                ],
                milestones=[warmup_epochs],
            )
        else:
            lr_scheduler = cosine_scheduler
    return lr_scheduler
