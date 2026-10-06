"""Per-batch and per-epoch metric helpers of the training loop.

Pure functions of predictions, labels and confusion counts, plus the TensorBoard writers
that log them. Nothing here reads the run's configuration or model, so the same numbers
are computed for train, validation and test, and by analysis scripts that mirror them.
Run-level summaries over the whole epoch history live in run_metrics.py.
"""

import torch


def safe_div(num, denom):
    """Divide two values and return None for a zero denominator."""
    return None if denom == 0 else num / denom

def format_metric(value):
    """Format an optional metric for logs and report files."""
    return "undefined" if value is None else f"{value:.6f}"

def binary_auc(scores, labels):
    """Rank-based ROC AUC over one binary split, or None when a class is missing.

    The only metric in this file that is NOT a function of the confusion counts:
    everything else answers "how good is the split at threshold 0.5", this one answers
    "how good is the ordering, whatever the threshold". That distinction is the reason
    it exists here -- on the cold splits sensitivity sits at 0.2-0.35 against
    specificity 0.77, so a fixed 0.5 threshold cannot separate "learned nothing" from
    "learned something, threshold in the wrong place", and balanced_accuracy alone
    reports both as the same number.

    Mann-Whitney U over midranks:
        AUC = (sum of positive midranks - n_pos*(n_pos+1)/2) / (n_pos * n_neg)
    Tied scores share the average of the ranks they span, which is what makes this
    agree with the trapezoidal ROC integral instead of depending on input order --
    it matters here because a collapsed model emits long runs of identical scores.

    Written out rather than imported: scikit-learn is not a dependency of this project
    anywhere, and this is the whole of what would be taken from it. `scores` may be any
    monotone function of the model's confidence (probability or logit margin) -- only
    their order is read.
    """
    pairs = sorted(zip(scores, labels), key=lambda item: item[0])
    positives = sum(1 for _, label in pairs if label == 1)
    negatives = len(pairs) - positives
    if positives == 0 or negatives == 0:
        return None
    positive_rank_sum = 0.0
    start = 0
    while start < len(pairs):
        stop = start
        while stop + 1 < len(pairs) and pairs[stop + 1][0] == pairs[start][0]:
            stop += 1
        # One 1-based midrank shared by the whole tie group [start, stop].
        midrank = (start + stop) / 2.0 + 1.0
        for position in range(start, stop + 1):
            if pairs[position][1] == 1:
                positive_rank_sum += midrank
        start = stop + 1
    return (
        positive_rank_sum - positives * (positives + 1) / 2.0
    ) / (positives * negatives)

# per_protein_auc's own bar (analysis/null_model.py): a protein with fewer rows, or with
# only one class present, carries no ranking to read.
WITHIN_PROTEIN_MINIMUM_ROWS = 6


def within_protein_auc(subgroup_stats):
    """(mean AUC inside a protein, how many proteins that mean is over).

    THE metric for a lipid cold split, and the reason it is computed by the run itself
    rather than only post-hoc: under --lipid_coldsplit every protein is in training, so
    the pooled AUC can be won outright by "which protein is this" -- a protein marginal
    that says nothing about which lipid it binds. Measured on
    ..._lcs_esm3_balanced_lipid_classes: pooled AUC 0.568 while this number is 0.480, and
    on the two sets with enough protein blocks to read (11 and 10) it is 0.460 and 0.457
    -- chance. The pooled figure was almost entirely the marginal
    (files/results/lipid_coldsplit_architecture_direction.md section 7j).

    Comparisons never cross a protein boundary here, so that marginal cannot contribute:
    a protein is ranked only against its own candidate lipids. It is the quantity a
    ranking objective (--rank_within_protein) optimises, and the one to read first on
    this split.

    The block count travels with the value on purpose -- a mean over two proteins is not
    the same claim as a mean over eleven, and both occur across the four lipid sets.
    """
    values = []
    for stats in subgroup_stats.values():
        labels = stats.get("labels") or []
        if len(labels) < WITHIN_PROTEIN_MINIMUM_ROWS or len(set(labels)) < 2:
            continue
        value = binary_auc(stats["scores"], labels)
        if value is not None:
            values.append(value)
    if not values:
        return None, 0
    return sum(values) / len(values), len(values)


def within_protein_pair_auc(subgroup_stats):
    """Same question as within_protein_auc, counted over PAIRS instead of proteins.

    The per-protein average needs a protein to carry a readable ranking on its own
    (>= WITHIN_PROTEIN_MINIMUM_ROWS rows, both classes), and on this data most do not:
    on the sphingolipids and phosphorus_free blocks only about two proteins qualify per
    run, so that column came out empty for half the seeds and its per-group means were
    over one to five runs. A number that absent cannot be the metric a split is judged
    by.

    This pools the comparisons themselves: every (positive, negative) pair of rows
    SHARING a protein, concordant pairs over total pairs, ties counted as half -- the
    rank-based AUC identity, applied to the union of the per-protein pair sets. A
    protein contributes as soon as it has one row of each class, so nearly every protein
    in the block contributes, and a protein with more candidates weighs more, which is
    what "how well are this block's within-protein comparisons ordered" should mean.

    Comparisons still never cross a protein boundary, so the protein marginal cannot
    contribute -- the property the whole metric exists for is unchanged.
    """
    concordant = 0.0
    total = 0
    proteins = 0
    for stats in subgroup_stats.values():
        scores, labels = stats.get("scores") or [], stats.get("labels") or []
        positives = [s for s, y in zip(scores, labels) if y == 1]
        negatives = [s for s, y in zip(scores, labels) if y != 1]
        if not positives or not negatives:
            continue
        proteins += 1
        for positive in positives:
            for negative in negatives:
                if positive > negative:
                    concordant += 1.0
                elif positive == negative:
                    concordant += 0.5
                total += 1
    if total == 0:
        return None, 0
    return concordant / total, proteins


def metric_values(tp, fp, tn, fn, total_loss, total_loss_count, auc=None):
    """Compute aggregate binary-classification metrics from confusion counts.

    `auc` is passed in rather than computed here because it is the one metric the
    counts do not determine -- it needs the per-sample scores, which only the test
    path keeps. Callers that have no scores (the per-epoch train/valid aggregates)
    leave it None and it reports as "undefined", exactly like precision on an empty
    predicted-positive set.
    """
    sensitivity = safe_div(tp, tp + fn)
    specificity = safe_div(tn, tn + fp)
    return {
        "total": tp + fp + tn + fn,
        "real_positive": tp + fn,
        "real_negative": tn + fp,
        "predicted_positive": tp + fp,
        "predicted_negative": tn + fn,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "accuracy": safe_div(tp + tn, tp + fp + tn + fn),
        "sensitivity": sensitivity,
        "precision": safe_div(tp, tp + fp),
        "specificity": specificity,
        "IoU": safe_div(tp, tp + fp + fn),
        "FAR": safe_div(fp, fp + tn),
        "F1": safe_div(2 * tp, 2 * tp + fp + fn),
        "balanced_accuracy": None if sensitivity is None or specificity is None else (sensitivity + specificity) / 2,
        "AUC": auc,
        "loss": safe_div(total_loss, total_loss_count),
    }

def update_aggregate(
    stats,
    pred_class,
    labels,
    loss,
    sample_count,
    loss_count=None,
    scores=None,
):
    """Accumulate confusion counts and sample-weighted loss for one batch.

    `scores` is the per-row positive-class probability, and it is optional because the
    confusion counts below throw the ordering away: everything the counts answer is a
    question about the 0.5 threshold, and AUC is the one question about the ORDER. A
    caller that wants a per-epoch AUC (the validation pass does; see the epoch print and
    RUN_METRIC_FIELDS' *_valid_AUC entries) passes them and gets `stats["scores"]`/
    `stats["score_labels"]` filled; a caller that does not passes nothing and pays no
    memory for lists it will not read.
    """
    if loss_count is None:
        loss_count = sample_count
    if scores is not None:
        # Sliced the same way the caller sliced the scores: a forward pass can return
        # more rows than the batch has labels (validate_prediction_label_shapes), and a
        # score paired with the wrong label would be a silently wrong AUC, not a crash.
        stats["scores"].extend(scores)
        stats["score_labels"].extend(
            int(value) for value in labels[: len(scores)].detach().cpu().tolist()
        )
    # Two comparisons and three reductions instead of eight and four. Predictions come
    # from argmax over two classes, so "predicted positive" and "correct" each split the
    # batch in two and the four cells are fixed by three of them:
    #   predicted positives = TP + FP,  correct = TP + TN,  batch = TP + FP + TN + FN.
    # Pure integer counting, so this is the same arithmetic identity either way -- there
    # is no rounding here to preserve, only work to skip.
    correct = pred_class == labels
    predicted_positive = pred_class == 1
    true_positive = int((correct & predicted_positive).sum())
    false_positive = int(predicted_positive.sum()) - true_positive
    true_negative = int(correct.sum()) - true_positive
    stats["TP"] += true_positive
    stats["FP"] += false_positive
    stats["TN"] += true_negative
    stats["FN"] += (
        pred_class.numel() - true_positive - false_positive - true_negative
    )
    stats["loss"] += (
        loss.item() if isinstance(loss, torch.Tensor) else loss
    ) * loss_count
    stats["count"] += sample_count
    stats["loss_count"] += loss_count


def aggregate_values(stats):
    """Convert accumulated counts and loss into aggregate metrics.

    AUC only when `update_aggregate` was given scores (the validation pass) -- otherwise
    `metric_values` leaves the field None exactly as before, so train-side callers and
    the branch-dynamics passes are unchanged.
    """
    return metric_values(
        stats["TP"],
        stats["FP"],
        stats["TN"],
        stats["FN"],
        stats["loss"],
        stats["loss_count"],
        auc=(
            binary_auc(stats["scores"], stats["score_labels"])
            if stats.get("scores")
            else None
        ),
    )


def log_epoch_metrics(writer, epoch_index, mode, metrics):
    """Write aggregate epoch metrics to TensorBoard.

    AUC included here for the first time: aggregate_values() has always computed it on
    the validation pass (metrics.get("AUC") is None on train, where no scores are
    collected -- see aggregate_values' own docstring), but nothing wrote the value out,
    so no run before this change has an "epoch/valid AUC" scalar to plot a learning
    curve from. analysis/plot_group_learning_curve.py's METRIC_SERIES/read logic is
    updated alongside this to read a valid-only series for AUC.
    """
    for key in ("accuracy", "sensitivity", "precision", "specificity", "F1", "balanced_accuracy", "AUC", "loss"):
        value = metrics.get(key)
        if value is not None:
            writer.add_scalar(f"epoch/{mode} {key}", value, epoch_index + 1)



def log_tb(writer,step,los,mode,pred,label, print_metrics=True):
    """Compute and log per-batch metrics for the requested phase."""
    #might hve to round at this very step
    if mode == "train":
        
        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()

        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 

        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        if print_metrics:
            print(f"train accuracy : {acc}")
            print(
                f"train pred 0/1 : {int((pred_class == 0).sum().item())}/{int((pred_class == 1).sum().item())} "
                f"label 0/1 : {int((label == 0).sum().item())}/{int((label == 1).sum().item())}"
            )
        writer.add_scalar("train sensitivity", sensitivity.item(),step)
        writer.add_scalar("train precision", precision.item(),step)
        writer.add_scalar("train specificity", specificity.item(),step)
        writer.add_scalar("train accuracy",acc.item(),step)
        writer.add_scalar("train F1 score",F1.item(),step)
        writer.add_scalar("train balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("train loss",los,step)
       #writer_tb.flush()
    if mode == "valid":

        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        if print_metrics:
            print(f"valid accuracy : {acc}")
            print(
                f"valid pred 0/1 : {int((pred_class == 0).sum().item())}/{int((pred_class == 1).sum().item())} "
                f"label 0/1 : {int((label == 0).sum().item())}/{int((label == 1).sum().item())}"
            )
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 

        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0

        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        writer.add_scalar("valid sensitivity", sensitivity.item(),step)
        writer.add_scalar("valid precision", precision.item(),step)
        writer.add_scalar("valid specificity", specificity.item(),step)
        writer.add_scalar("valid accuracy",acc.item(),step)
        writer.add_scalar("valid F1 score",F1.item(),step)
        writer.add_scalar("valid balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("valid loss",los,step)

    if mode == "test":

        pred_class = pred.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        print(f"test accuracy : {acc}")
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 
        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        metrics = {
            "accuracy": acc.item(),
            "sensitivity": sensitivity.item(),
            "precision": precision.item(),
            "specificity": specificity.item(),
            "F1": F1.item(),
            "balanced_accuracy": balanced_acc.item(),
            "loss": los.item() if isinstance(los, torch.Tensor) else los
        }
        return metrics
        #writer_tb.flush()


def validate_prediction_label_shapes(predictions, labels, phase, batch_index):
    """Validate one-to-one alignment between binary logits and labels."""
    if predictions.ndim != 2 or predictions.shape[1] != 2:
        raise ValueError(
            f"{phase} batch {batch_index}: expected predictions shaped [batch, 2], "
            f"got {tuple(predictions.shape)}"
        )
    if labels.ndim != 1:
        raise ValueError(
            f"{phase} batch {batch_index}: expected labels shaped [batch], "
            f"got {tuple(labels.shape)}"
        )
    if predictions.shape[0] != labels.shape[0]:
        raise ValueError(
            f"{phase} batch {batch_index}: prediction count "
            f"{predictions.shape[0]} does not match label count {labels.shape[0]}"
        )
    return labels.shape[0]
