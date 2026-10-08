"""One training epoch followed by one full validation pass.

Order of a training step: forward -> task loss (TaskLosses.train_loss) -> the task loss
is banked into the epoch metrics -> sparsity / Concrete Dropout / adversary / thematic
penalties are added -> backward -> optimizer step -> bilevel gate step on validation.
Penalties are added after the banking on purpose: `epoch/train loss` stays the task
loss alone and comparable across configurations; the penalties get their own scalars.
"""

import torch
import torch.nn.functional as F

from architecture.final_layer import chem_adversary_loss, family_dann_loss
from architecture.loss import get_pu_loss_diagnostics, reset_pu_loss_diagnostics
from architecture.mlp_utils import collect_concrete_dropout_reg, collect_sparsity_penalty
from architecture.thematic_descriptor_head import thematical_orthogonality_loss
from candidate_averaging import CandidateAccumulator, average_candidate_predictions
from dataloader.protein_graph_builder import FAMILY_NAMES
from eval_metrics import (
    aggregate_values,
    format_metric,
    log_epoch_metrics,
    update_aggregate,
    validate_prediction_label_shapes,
)
from forward_args import build_forward_args


TENSORBOARD_FLUSH_EVERY_EPOCHS = 5


def endless_batches(loader):
    """Yield validation batches forever for the bilevel lambda step."""
    while True:
        for batch in loader:
            yield batch


def bilevel_lambda_step(run):
    """First-order validation update of the width gates (the bilevel lambda params).

    Theta is held fixed: its grads from this step are discarded on the next
    optimizer.zero_grad(); hyper_optimizer only steps the gate params. The gate grads
    left by the preceding train-loss backward are cleared here before the val backward.
    """
    conf, model, device = run.conf, run.model, run.device
    hyper_optimizer = run.optim.hyper_optimizer
    prot_v, lipid_v = next(run.hyper_val_iter)
    prot_v = prot_v.to(device, non_blocking=True)
    lipid_v = lipid_v.to(device, non_blocking=True)
    labels_v = prot_v.inter.to(device, non_blocking=True)
    hyper_optimizer.zero_grad()
    outl_v = model(**build_forward_args(conf, prot_v, lipid_v))
    # The bilevel step reads the validation split, so on an expanded one its batches are
    # candidate copies; averaging them here keeps the hyper loss a per-pair quantity,
    # the same one the reported validation loss is.
    outl_v, labels_v, _ = average_candidate_predictions(outl_v, prot_v, labels_v)
    validate_prediction_label_shapes(outl_v, labels_v, "bilevel", 0)
    val_loss = run.losses.eval_task_loss(outl_v, labels_v)
    val_loss = val_loss + conf.sparsity_lambda * collect_sparsity_penalty(model).to(val_loss.device)
    val_loss.backward()
    hyper_optimizer.step()


def log_adversary_metrics(run, epoch_index, stats):
    """Write the epoch's mean adversary penalties, plus the reversal strengths in force.

    Read the losses as leakage gauges, not as objectives. Each per-partner adversary is
    a 2-class problem, so ln 2 = 0.693 means the partner alone says nothing about the
    label and there is no shortcut left to suppress; well below that means there is.
    The family head is 9-class, where the corresponding no-information value is
    ln 9 = 2.197. The chem head is a regression, so there is no analogous
    no-information constant -- read it relative to Var(s_chem) on this run's batches
    instead. Logging the lambdas alongside them makes a ramped run readable after the
    fact -- otherwise the schedule is invisible and the loss curve uninterpretable.
    """
    conf, model, writer = run.conf, run.model, run.writer
    for key, batches_key, name in (
        ("adv", "adv_batches", "adversary loss"),
        ("dann", "dann_batches", "family dann loss"),
        ("chem", "chem_batches", "chem adversary loss"),
        ("thematical_orth", "thematical_orth_batches", "thematical orthogonality penalty"),
    ):
        batches = stats.get(batches_key, 0)
        if batches:
            writer.add_scalar(
                f"epoch/train {name}", stats[key] / batches, epoch_index + 1
            )
    if conf.adversarial_grl:
        writer.add_scalar(
            "epoch/adv lambda", model.final_layer.adv_lambda_now, epoch_index + 1
        )
    if conf.dann_family:
        writer.add_scalar(
            "epoch/dann lambda", model.final_layer.dann_lambda_now, epoch_index + 1
        )
    if conf.chem_adversary:
        writer.add_scalar(
            "epoch/chem lambda", model.final_layer.chem_lambda_now, epoch_index + 1
        )
    if conf.lipid_path_handicap:
        # The lr the handicap actually produced, not just the multiplier: the multiplier
        # alone would hide whatever the lr schedule did underneath it.
        writer.add_scalar(
            "epoch/lipid path weight", run.lipid_path_weight_now, epoch_index + 1
        )
        writer.add_scalar(
            "epoch/lipid branch lr", run.optim.lipid_lr_groups[0]["lr"], epoch_index + 1
        )


def train_one_epoch(run, idx, counttrain, countval):
    """Run one training epoch followed by full validation.

    Returns (counttrain, countval, train_metrics, valid_metrics); the two counters are
    the running batch counts across epochs.
    """
    conf, model, device = run.conf, run.model, run.device
    losses = run.losses
    optimizer = run.optim.optimizer
    gate_params = run.optim.gate_params
    scaler = run.scaler
    use_amp = run.use_amp
    # Batches whose loss carried no gradient (see the skip below).
    skipped_no_gradient = 0
    if conf.pu_loss:
        reset_pu_loss_diagnostics()
    train_stats = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
        "loss": 0.0,
        "count": 0,
        "loss_count": 0,
    }
    # Adversary penalties are added to the backward pass after update_aggregate has
    # already banked the task loss, so without their own accumulators they leave no
    # trace in TensorBoard at all. They are what says whether a partner is still
    # individually decodable -- the premise the whole GRL setup rests on -- so they are
    # tracked separately rather than folded into "epoch/train loss".
    adversary_stats = {
        "adv": 0.0, "adv_batches": 0, "dann": 0.0, "dann_batches": 0,
        "chem": 0.0, "chem_batches": 0,
        "thematical_orth": 0.0, "thematical_orth_batches": 0,
    }
    for i, graph in enumerate(run.train_loader):
        #dataset is reduced because of high variety of experience parameters
        if i < run.train_batches_to_run:
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)

            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            optimizer.zero_grad()

            forward_args = build_forward_args(conf, prot, lipid)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                outl = model(**forward_args)

                sample_count = validate_prediction_label_shapes(
                    outl, interaction_labels, "train", i + 1
                )
                los = losses.train_loss(model, outl, prot, interaction_labels, sample_count)
            # Batch-level logging is temporarily disabled; keep it for re-enabling.
            # print(f"epoch : {idx+1}")
            # print(f"batch : {i+1}/{run.train_batches_to_run}")
            # log_tb(run.writer, counttrain, los,"train",outl,interaction_labels)
            pred_class = outl.argmax(dim=1)
            update_aggregate(
                train_stats,
                pred_class,
                interaction_labels.long(),
                los,
                sample_count,
                loss_count=sample_count,
            )

            # Gate penalty on the TRAIN loss only when NOT bilevel; in bilevel mode the
            # gate penalty is applied on the validation step (bilevel_lambda_step).
            if gate_params and conf.sparsity_lambda > 0.0 and not conf.bilevel:
                los = los + conf.sparsity_lambda * collect_sparsity_penalty(model).to(los.device)
            # Per-layer Concrete Dropout KL surrogate is always a train-objective term
            # (its weight_reg/dropout_reg coefficients are baked into each module).
            if conf.bilevel_dropout:
                los = los + collect_concrete_dropout_reg(model).to(los.device)

            # Adversarial anti-shortcut penalty: the per-partner adversary logits
            # stashed by Final_Layer sit behind a gradient-reversal layer, so
            # adding their CE here and one backward() trains the heads to predict
            # the label from one partner while pushing the encoder to make each
            # partner individually uninformative. Kept out of the logged task loss.
            if conf.adversarial_grl:
                adv = model.final_layer._adv
                if adv is not None:
                    # A side disabled by --no_adv_lipid / --no_adv_protein comes back
                    # None and contributes no term. Averaged over the sides in use so
                    # adv_weight means the same pressure whether one or both are on.
                    terms = [
                        F.cross_entropy(logits, interaction_labels.long())
                        for logits in adv
                        if logits is not None
                    ]
                    adv_loss = torch.stack(terms).mean() if terms else None
                if adv is not None and adv_loss is not None:
                    los = los + conf.adv_weight * adv_loss
                    adversary_stats["adv"] += float(adv_loss.detach())
                    adversary_stats["adv_batches"] += 1

            # Family DANN on the fused representation. prot.family is a per-graph 9-wide
            # one-hot, which PyG concatenates flat, so it is reshaped back per sample.
            if conf.dann_family:
                dann_features = model.final_layer._dann_features
                if dann_features is not None:
                    dann_loss = family_dann_loss(
                        dann_features,
                        prot.family.view(dann_features.shape[0], -1),
                        interaction_labels.long(),
                        model.final_layer.family_adversaries,
                        conf.dann_class_conditional,
                    )
                    los = los + conf.dann_weight * dann_loss
                    adversary_stats["dann"] += float(dann_loss.detach())
                    adversary_stats["dann_batches"] += 1

            # Chemistry adversary, same fused representation, s_chem instead of family.
            if conf.chem_adversary:
                chem_features = model.final_layer._chem_features
                if chem_features is not None:
                    chem_loss = chem_adversary_loss(
                        chem_features,
                        prot.frozen_prior.view(chem_features.shape[0]),
                        model.final_layer.chem_head,
                    )
                    los = los + conf.chem_weight * chem_loss
                    adversary_stats["chem"] += float(chem_loss.detach())
                    adversary_stats["chem_batches"] += 1

            # Thematic-interaction non-redundancy penalty: pushes each --thematical_
            # paths ForcedInteraction's output away from correlating with what a
            # stop-gradient probe already predicts from ONE side alone. Read as a
            # narrower leak gauge than adversarial_grl/dann_family, not a replacement
            # for them -- see thematical_orthogonality_loss's own docstring for the
            # blind spot it does not close (a fingerprint jointly correlated across
            # both sides at once).
            if conf.thematical_paths and conf.thematical_orth_weight:
                orth_penalty, probe_loss = thematical_orthogonality_loss(
                    model.final_layer.thematical_head, interaction_labels
                )
                if orth_penalty is not None:
                    los = los + conf.thematical_orth_weight * (orth_penalty + probe_loss)
                    adversary_stats["thematical_orth"] += float(orth_penalty.detach())
                    adversary_stats["thematical_orth_batches"] += 1

            # A batch whose loss carries no gradient is a real, documented outcome, not
            # a bug to crash on: pairwise_ranking_loss returns a plain zero when the
            # batch holds no rankable pair (under --rank_within_protein, no two rows of
            # the same protein with opposite labels), and
            # Non_Negative_Positive_Unlabeled_loss does the same with no labeled
            # positives. Both docstrings promise that degradation -- and calling
            # .backward() on it unconditionally defeated the promise one level up:
            # "element 0 of tensors does not require grad and does not have a grad_fn",
            # which killed the first --rank_within_protein run under --lipid_coldsplit
            # at epoch 1. Skipping the step is what those docstrings already describe;
            # the count is printed at the end of the epoch, because a run skipping most
            # of its batches is training on almost nothing and must not look healthy.
            if not getattr(los, "requires_grad", False):
                skipped_no_gradient += 1
            elif use_amp:
                scaler.scale(los).backward()
                if conf.save_dynamics:
                    # Before the norms are read, never after: scaler.step() would have
                    # unscaled them itself, but only inside its own call.
                    scaler.unscale_(optimizer)
                    run.dynamics.accumulate_grad_norms()
                scaler.step(optimizer)
                scaler.update()
            else:
                los.backward()
                if conf.save_dynamics:
                    run.dynamics.accumulate_grad_norms()
                optimizer.step()

            if run.optim.hyper_optimizer is not None:
                bilevel_lambda_step(run)
            counttrain+=1
        else:
            break
    if skipped_no_gradient:
        print(
            f"batches skipped for having no gradient: {skipped_no_gradient}/{counttrain} "
            "-- under --rank_within_protein this is batches with no same-protein pair; "
            "a large share means the run is training on almost nothing, raise --batch"
        )
    if conf.pu_loss:
        pu_diag = get_pu_loss_diagnostics()
        if pu_diag["calls"] > 0:
            print(
                "PU nnPU correction: "
                f"{pu_diag['corrections']}/{pu_diag['calls']} batches, "
                f"negative_risk[min={pu_diag['min_negative_loss']:.6f}, "
                f"mean={pu_diag['sum_negative_loss'] / pu_diag['calls']:.6f}, "
                f"max={pu_diag['max_negative_loss']:.6f}]"
            )
    if conf.group_dro:
        print(
            "group DRO weights : "
            + ", ".join(
                f"{name}={weight:.4f}"
                for name, weight in zip(FAMILY_NAMES, losses.group_dro_state.probs.detach().cpu().tolist())
            )
        )
    model.eval()
    valid_stats = {
        "TP": 0,
        "FP": 0,
        "TN": 0,
        "FN": 0,
        "loss": 0.0,
        "count": 0,
        "loss_count": 0,
        # Per-row positive-class probabilities and their labels, for this epoch's AUC.
        # Only the validation pass keeps them: it is the one pass whose per-epoch number
        # is read as a curve (checkpoint selection, early stopping, "is it still
        # learning"), and balanced accuracy alone cannot separate "learned nothing" from
        # "learned something, threshold in the wrong place" -- under --adversarial_grl it
        # sits at 0.500 for whole runs while the ordering underneath does move.
        "scores": [],
        "score_labels": [],
    }
    collect_valid_scores = True
    valid_accumulator = (
        CandidateAccumulator() if conf.eval_average_candidates else None
    )
    with torch.no_grad():
        print("VALIDATION")
        for i , graph in enumerate(run.valid_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            forward_args = build_forward_args(conf, prot, lipid)
            outl = model(**forward_args)
            if valid_accumulator is not None:
                # Candidates of one pair are scattered over the shuffled batches; the
                # pass collects them and the block is scored once below, so the loss and
                # the counters see pairs rather than candidates.
                valid_accumulator.add(outl, prot, interaction_labels)
                continue
            sample_count = validate_prediction_label_shapes(
                outl, interaction_labels, "valid", i + 1
            )
            # print(f"valid batch : {i+1}/{len(run.valid_loader)}")

            los = losses.valid_loss(model, outl, prot, interaction_labels, sample_count)
            # log_tb(run.writer, countval, los,"valid",outl,interaction_labels.to(torch.float))
            pred_class = outl.argmax(dim=1)
            labels = interaction_labels.long()
            update_aggregate(
                valid_stats,
                pred_class,
                labels,
                los,
                sample_count,
                scores=(
                    torch.softmax(outl.float(), dim=1)[:sample_count, 1]
                    .detach().cpu().tolist()
                    if collect_valid_scores
                    else None
                ),
            )
            countval +=1
    if valid_accumulator is not None:
        outl, interaction_labels, averaged_protein_ids = valid_accumulator.averaged()
        sample_count = validate_prediction_label_shapes(
            outl, interaction_labels, "valid", 1
        )
        # Chunked to the training batch size, so a loss defined over a batch keeps its
        # scale; the ranking loss also needs the protein ids that survived the reduction.
        los, _ = losses.batched_block_loss(outl, interaction_labels, averaged_protein_ids)
        update_aggregate(
            valid_stats,
            outl.argmax(dim=1),
            interaction_labels.long(),
            los,
            sample_count,
            scores=(
                torch.softmax(outl.float(), dim=1)[:sample_count, 1]
                .detach().cpu().tolist()
                if collect_valid_scores
                else None
            ),
        )
        countval += 1
    train_metrics = aggregate_values(train_stats)
    valid_metrics = aggregate_values(valid_stats)
    log_epoch_metrics(run.writer, idx, "train", train_metrics)
    log_epoch_metrics(run.writer, idx, "valid", valid_metrics)
    log_adversary_metrics(run, idx, adversary_stats)
    if (idx + 1) % TENSORBOARD_FLUSH_EVERY_EPOCHS == 0:
        run.writer.flush()
    print(f"valid epoch balanced_accuracy: {format_metric(valid_metrics['balanced_accuracy'])}")
    # Its own line rather than appended to the one above: scripts/lib/progress_table.sh
    # parses that line by field position, and the summarize/graphics path reads the
    # epoch history, not this print.
    print(f"valid epoch AUC: {format_metric(valid_metrics['AUC'])}")

    return counttrain, countval, train_metrics, valid_metrics
