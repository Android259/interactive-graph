"""The test pass and the test report it writes.

Run once, after training, on the weights checkpoint selection picked. Writes
test_metrics/<label>/<excluded_set>/test_metrics_<timestamp>_....txt -- the run's
configuration, its run-level summary, the test metrics and a per-protein table -- and
upserts that report into results/tables/metrics_summary.csv.
"""

import json
import os

import torch
import torch.nn.functional as F

from training.append_metric_to_table import append_metric
from candidate_averaging import CandidateAccumulator
from eval_metrics import (
    binary_auc,
    format_metric,
    metric_values,
    validate_prediction_label_shapes,
    within_protein_auc,
    within_protein_pair_auc,
)
from forward_args import build_forward_args
from run_metrics import RUN_METRIC_FIELDS


def score_averaged_block(run, accumulator):
    """Confusion counts, loss and per-protein counts for one averaged evaluation block.

    The counterpart of the per-batch bookkeeping in run_test, run once on the per-pair
    averages instead of once per batch. The per-row loss is the cross-entropy of the
    averaged probability where the run's loss decomposes per row, and the block loss
    spread evenly over the rows where it does not -- the same substitution the per-batch
    path makes for the ranking and positive-unlabelled losses.

    The AUC scores are read off the SAME averaged `outl` the confusion counts come
    from, so both describe one prediction per pair. Taking them per candidate instead
    would make AUC and balanced_accuracy describe different objects on the same run.
    """
    conf = run.conf
    outl, labels, protein_ids = accumulator.averaged()
    labels = labels.long()
    if conf.loss_type == "cross_entropy" and not conf.pu_loss:
        sample_losses = F.cross_entropy(outl, labels, reduction="none")
        block_loss = float(sample_losses.mean())
    else:
        block_loss, _ = run.losses.batched_block_loss(outl, labels, protein_ids)
        sample_losses = torch.full(labels.shape, block_loss, device=outl.device)

    predictions = outl.argmax(dim=1)
    correct = predictions == labels
    positive = predictions == 1
    total_tp = int((correct & positive).sum())
    total_fp = int((~correct & positive).sum())
    total_tn = int((correct & ~positive).sum())
    total_fn = int((~correct & ~positive).sum())

    label_values = labels.cpu().tolist()
    score_values = torch.softmax(outl.float(), dim=1)[:, 1].detach().cpu().tolist()

    subgroup_stats = {}
    if protein_ids is not None:
        for protein_id, prediction, label, sample_loss, score in zip(
            protein_ids.view(-1).cpu().tolist(),
            predictions.cpu().tolist(),
            label_values,
            sample_losses.detach().cpu().tolist(),
            score_values,
        ):
            stats = subgroup_stats.setdefault(
                protein_id,
                {
                    "TP": 0, "FP": 0, "TN": 0, "FN": 0, "loss": 0.0, "count": 0,
                    "scores": [], "labels": [],
                },
            )
            if prediction == label and prediction == 1:
                stats["TP"] += 1
            elif prediction != label and prediction == 1:
                stats["FP"] += 1
            elif prediction == label and prediction == 0:
                stats["TN"] += 1
            else:
                stats["FN"] += 1
            stats["loss"] += sample_loss
            stats["count"] += 1
            stats["scores"].append(score)
            stats["labels"].append(label)

    return (
        total_tp,
        total_fp,
        total_tn,
        total_fn,
        block_loss * labels.shape[0],
        int(labels.shape[0]),
        subgroup_stats,
        score_values,
        label_values,
    )


def run_test(run, run_summary, surviving_structure, discovered_dropout_report):
    """Evaluate the test split and write global and per-protein metrics."""
    conf, model, device, paths = run.conf, run.model, run.device, run.paths

    model.eval()

    total_tp = 0
    total_fp = 0
    total_tn = 0
    total_fn = 0
    total_loss = 0.0
    total_loss_count = 0
    subgroup_stats = {}
    # Per-sample positive-class probabilities and their labels, kept only for AUC --
    # the confusion counts above throw the ordering away, and it cannot be recovered
    # afterwards from a written report. Two flat lists over the whole test split, in
    # loader order; binary_auc sorts them itself.
    test_scores = []
    test_labels = []

    # Expanded split: one row per candidate structure. The pass collects them and the
    # block is scored once, below, so a pair contributes one prediction to the totals and
    # to its protein's subgroup whatever its candidate count.
    test_accumulator = CandidateAccumulator() if conf.eval_average_candidates else None
    with torch.no_grad():
        for i , graph in enumerate(run.test_loader):
            prot,lipid = graph
            prot = prot.to(device, non_blocking=True)
            lipid = lipid.to(device, non_blocking=True)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device, non_blocking=True)

            forward_args = build_forward_args(conf, prot, lipid)
            outl = model(**forward_args)
            if test_accumulator is not None:
                test_accumulator.add(outl, prot, interaction_labels)
                continue
            sample_count = validate_prediction_label_shapes(
                outl, interaction_labels, "test", i + 1
            )

            los, sample_losses = run.losses.test_losses(
                outl, prot, interaction_labels, sample_count
            )
            pred_class = outl.argmax(dim=1)
            labels = interaction_labels.long()
            protein_ids = prot.protein_id.view(-1)[:sample_count].detach().cpu().tolist()
            sample_loss_values = sample_losses.detach().cpu().tolist()
            # Sliced to sample_count for the same reason protein_ids above is: the
            # forward pass can return more rows than the batch has labels.
            batch_scores = (
                torch.softmax(outl.float(), dim=1)[:sample_count, 1]
                .detach().cpu().tolist()
            )
            batch_labels = labels.detach().cpu().tolist()[:sample_count]
            test_scores.extend(batch_scores)
            test_labels.extend(batch_labels)
            total_tp += int(((pred_class == labels) & (pred_class == 1)).sum().item())
            total_fp += int(((pred_class != labels) & (pred_class == 1)).sum().item())
            total_tn += int(((pred_class == labels) & (pred_class == 0)).sum().item())
            total_fn += int(((pred_class != labels) & (pred_class == 0)).sum().item())
            total_loss += (los.item() if isinstance(los, torch.Tensor) else los) * sample_count
            total_loss_count += sample_count
            for protein_id, pred_value, label_value, sample_loss, score_value in zip(
                protein_ids,
                pred_class.detach().cpu().tolist(),
                labels.detach().cpu().tolist(),
                sample_loss_values,
                batch_scores,
            ):
                stats = subgroup_stats.setdefault(
                    protein_id,
                    {
                        "TP": 0, "FP": 0, "TN": 0, "FN": 0, "loss": 0.0, "count": 0,
                        "scores": [], "labels": [],
                    },
                )
                if pred_value == label_value and pred_value == 1:
                    stats["TP"] += 1
                elif pred_value != label_value and pred_value == 1:
                    stats["FP"] += 1
                elif pred_value == label_value and pred_value == 0:
                    stats["TN"] += 1
                elif pred_value != label_value and pred_value == 0:
                    stats["FN"] += 1
                stats["loss"] += sample_loss
                stats["count"] += 1
                stats["scores"].append(score_value)
                stats["labels"].append(label_value)

    if test_accumulator is not None:
        (
            total_tp,
            total_fp,
            total_tn,
            total_fn,
            total_loss,
            total_loss_count,
            subgroup_stats,
            test_scores,
            test_labels,
        ) = score_averaged_block(run, test_accumulator)

    metrics = metric_values(
        total_tp,
        total_fp,
        total_tn,
        total_fn,
        total_loss,
        total_loss_count,
        auc=binary_auc(test_scores, test_labels),
    )

    print(f"accuracy: {format_metric(metrics['accuracy'])}")
    print(f"sensitivity: {format_metric(metrics['sensitivity'])}")
    print(f"precision: {format_metric(metrics['precision'])}")
    print(f"specificity: {format_metric(metrics['specificity'])}")
    print(f"IoU: {format_metric(metrics['IoU'])}")
    print(f"FAR: {format_metric(metrics['FAR'])}")
    print(f"F1: {format_metric(metrics['F1'])}")
    print(f"balanced_accuracy: {format_metric(metrics['balanced_accuracy'])}")
    print(f"AUC: {format_metric(metrics['AUC'])}")
    within_auc, within_blocks = within_protein_auc(subgroup_stats)
    metrics["AUC_within_protein"] = within_auc
    metrics["AUC_within_protein_proteins"] = within_blocks
    pair_auc, pair_proteins = within_protein_pair_auc(subgroup_stats)
    metrics["AUC_within_protein_pairs"] = pair_auc
    metrics["AUC_within_protein_pairs_proteins"] = pair_proteins
    print(f"AUC_within_protein: {format_metric(within_auc)}")
    print(f"AUC_within_protein_proteins: {within_blocks}")
    print(f"AUC_within_protein_pairs: {format_metric(pair_auc)}")
    print(f"AUC_within_protein_pairs_proteins: {pair_proteins}")
    print(f"loss: {format_metric(metrics['loss'])}")

    test_metrics_path = os.path.join(paths.test_metrics_dir, f"test_metrics_{paths.timestamp}_{run.number_of_parameters}parameters_{conf.m}_{conf.HEADS}_{conf.seed}_{conf.lr}_{conf.batch}_{conf.hiddim}.txt")
    subgroup_columns = [
        "subgroup",
        "total",
        "real_positive",
        "real_negative",
        "predicted_positive",
        "predicted_negative",
        "TP",
        "FP",
        "TN",
        "FN",
        "accuracy",
        "sensitivity",
        "precision",
        "specificity",
        "IoU",
        "FAR",
        "F1",
        "balanced_accuracy",
        "AUC",
        "loss",
    ]
    subgroup_rows = []
    for protein_id, stats in sorted(subgroup_stats.items(), key=lambda item: run.train_dataset.protein_id_to_name[item[0]]):
        # "undefined" for every protein whose test rows are all one class -- common
        # here (a protein with no positive in its held-out block), same convention
        # precision already follows on an empty predicted-positive set.
        subgroup_metrics = metric_values(
            stats["TP"], stats["FP"], stats["TN"], stats["FN"], stats["loss"], stats["count"],
            auc=binary_auc(stats["scores"], stats["labels"]),
        )
        subgroup_name = run.train_dataset.protein_id_to_name[protein_id]
        subgroup_rows.append([
            subgroup_name,
            str(subgroup_metrics["total"]),
            str(subgroup_metrics["real_positive"]),
            str(subgroup_metrics["real_negative"]),
            str(subgroup_metrics["predicted_positive"]),
            str(subgroup_metrics["predicted_negative"]),
            str(subgroup_metrics["TP"]),
            str(subgroup_metrics["FP"]),
            str(subgroup_metrics["TN"]),
            str(subgroup_metrics["FN"]),
            format_metric(subgroup_metrics["accuracy"]),
            format_metric(subgroup_metrics["sensitivity"]),
            format_metric(subgroup_metrics["precision"]),
            format_metric(subgroup_metrics["specificity"]),
            format_metric(subgroup_metrics["IoU"]),
            format_metric(subgroup_metrics["FAR"]),
            format_metric(subgroup_metrics["F1"]),
            format_metric(subgroup_metrics["balanced_accuracy"]),
            format_metric(subgroup_metrics["AUC"]),
            format_metric(subgroup_metrics["loss"]),
        ])
    subgroup_widths = [
        max(len(row[i]) for row in [subgroup_columns] + subgroup_rows)
        for i in range(len(subgroup_columns))
    ]

    def format_subgroup_row(row):
        """Format one fixed-width per-protein metrics table row."""
        formatted = [row[0].ljust(subgroup_widths[0])]
        formatted.extend(row[i].rjust(subgroup_widths[i]) for i in range(1, len(row)))
        return "  ".join(formatted)

    with open(test_metrics_path, "w") as f:
        for key, value in vars(conf).items():
            if isinstance(value, bool):
                value = int(value)
            elif isinstance(value, (list, dict)):
                # Compact JSON (no ": ") so the "key: value" report parser splits cleanly.
                value = json.dumps(value, separators=(",", ":"))
            f.write(f"{key}: {value}\n")
        for key in RUN_METRIC_FIELDS:
            value = run_summary[key]
            if isinstance(value, bool):
                value = int(value)
            if isinstance(value, float):
                value = format_metric(value)
            elif value is None:
                value = "undefined"
            f.write(f"{key}: {value}\n")
        # Discovered hyperparameters (aggregatable across seeds/groups), each keyed by the
        # module path so it is clear which layer it belongs to. Compact JSON (no ": ") so
        # the report parser splits cleanly. Blank when the discovery features are off.
        discovered_widths_value = (
            json.dumps(
                {name: info["active"] for name, info in surviving_structure.items()},
                separators=(",", ":"),
            )
            if surviving_structure
            else ""
        )
        discovered_dropout_value = (
            json.dumps(
                {name: round(p, 6) for name, p in discovered_dropout_report.items()},
                separators=(",", ":"),
            )
            if discovered_dropout_report
            else ""
        )
        f.write(f"discovered_widths: {discovered_widths_value}\n")
        f.write(f"discovered_dropout: {discovered_dropout_value}\n")
        for key in ["total", "real_positive", "real_negative", "predicted_positive", "predicted_negative", "TP", "FP", "TN", "FN"]:
            f.write(f"{key}: {metrics[key]}\n")
        for key in ["accuracy", "sensitivity", "precision", "specificity", "IoU", "FAR", "F1", "balanced_accuracy", "AUC", "AUC_within_protein", "AUC_within_protein_pairs", "loss"]:
            f.write(f"{key}: {format_metric(metrics[key])}\n")
        # An integer count, not a rate -- format_metric would print it as 11.000000.
        f.write(f"AUC_within_protein_proteins: {metrics['AUC_within_protein_proteins']}\n")
        f.write(f"AUC_within_protein_pairs_proteins: {metrics['AUC_within_protein_pairs_proteins']}\n")
        # What --lipid_isolation actually removed from training. The flag's value is a
        # key into a registry (dataloader/lipid_isolation_blocks.py), so the report
        # would otherwise record "0.85" and nothing about which chemistry that was --
        # and a report has to be readable years after the registry moved on. Taken from
        # the dataset rather than re-read from the registry: this is what the run held
        # out, not what a lookup says it should have.
        held_species = sorted(getattr(run.train_dataset, "excluded_lipid_species", set()) or [])
        if held_species:
            f.write(f"lipid_isolation_species_count: {len(held_species)}\n")
            # Counted on the run's own working set (positives plus the negatives its
            # sampler drew), not on the full table: that is what this run actually
            # removed from training, and it is also what the held-out block then holds.
            pool = getattr(run.train_dataset, "csvt", None)
            if pool is not None:
                held_rows = pool["FullIdentityOfLipid"].isin(held_species)
                f.write(f"lipid_isolation_rows: {int(held_rows.sum())}\n")
                f.write(
                    "lipid_isolation_positives: "
                    f"{int(pool.loc[held_rows, 'Interaction'].sum())}\n"
                )
        f.write("\nper_protein_subgroup_metrics:\n")
        f.write(format_subgroup_row(subgroup_columns) + "\n")
        f.write(format_subgroup_row(["-" * width for width in subgroup_widths]) + "\n")
        for row in subgroup_rows:
            f.write(format_subgroup_row(row) + "\n")
        # After the per-protein table on purpose: analysis/build_metrics_table.py's
        # parser stops reading key/value pairs at that heading, so a list this long
        # cannot turn into a metrics_summary.csv column by accident. One name per line,
        # because a species name carries commas and colons of its own.
        if held_species:
            f.write(
                f"\nlipid_isolation_species ({len(held_species)} held out of "
                "training for every protein):\n"
            )
            for name in held_species:
                f.write(f"  {name}\n")
    run.writer.flush()
    append_metric(
        test_metrics_path,
        metrics_root=paths.test_metrics_root,
        run_root=paths.run_root,
        table=paths.metrics_table_path,
        config=conf,
    )
