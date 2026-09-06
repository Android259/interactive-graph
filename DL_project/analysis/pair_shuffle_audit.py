#!/usr/bin/env python3
"""Pair-shuffling audit for --thematical_paths (files/thematic_interaction_architecture.md,
"Known limitation").

What this checks. ForcedInteraction has no path for a lipid's or a protein's own identity
to reach the classifier except through their product -- but a pattern that only shows up in
the SPECIFIC COMBINATION of one lipid and one protein (not in either alone) passes that
structural check just as easily as real lipid<->protein chemistry would, and the
orthogonality probes cannot see it either (they only ever read one side at a time). The
only way to tell the two apart is to break the pairing and see what happens.

How. Every (protein, lipid) cell in the interaction table is filled in --
dataloader/dataset_source.py's own docstring: "10920 rows, the full 35 x 312 grid" -- so
swapping a held-out family's lipid onto a DIFFERENT real protein from the same family does
not invent a label: that exact combination was screened too, and its true outcome is sitting
in the same table under a different row. For every row of a family's held-out test split,
this script keeps the lipid side of the row exactly as it was, replaces the protein-side
descriptor values with a different real protein's own values (drawn from elsewhere in the
same split), looks up what that new combination's real outcome actually is, and asks the
model for its prediction on that new input.

If accuracy on the swapped pairs looks like accuracy on the real pairs, the model is
transferring correctly to a combination it was never trained or evaluated on before --
consistent with a real, generalizing interaction. If accuracy on the swapped pairs collapses
while the real pairs still scored fine, whatever the model is keying on did not travel with
the correct pairing -- consistent with the "Known limitation" leak.

Reads only. Trains nothing, writes only the requested --out CSV.

    python3 analysis/pair_shuffle_audit.py --labels=thematical_paths_geom_chem,\
thematical_paths_geom_chem_ortweight05 --families=LBP_BPI_CETP,scp2,GLTP \
        --seeds=0,1,2,3,4 --epoch=120 --out /tmp/pair_shuffle.csv

`--epoch` must name an epoch the run actually saved (training/new_train.py's
DYNAMICS_CHECKPOINT_EPOCHS, currently 1, 10, 49, 51, 120). Missing checkpoints and families
with only one protein in the split (nothing to swap onto) are reported as rows with a
`status` other than "ok" rather than silently skipped.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

torch.set_flush_denormal(True)

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pair_descriptors import full_catalog_order  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from analysis.checkpoint_scores import arg_lines, DEFAULT_FAMILIES  # noqa: E402


def confusion_counts(labels, preds):
    labels = np.asarray(labels)
    preds = np.asarray(preds)
    tp = int(((preds == 1) & (labels == 1)).sum())
    tn = int(((preds == 0) & (labels == 0)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    return tp, tn, fp, fn


def balanced_metrics(labels, preds):
    """(balanced_accuracy, sensitivity, specificity); NaN for an entirely one-class split."""
    tp, tn, fp, fn = confusion_counts(labels, preds)
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    ba = float("nan") if (np.isnan(sens) or np.isnan(spec)) else (sens + spec) / 2
    return ba, sens, spec


def build_descriptor_matrix(frame, catalog_order):
    """[n_rows, len(catalog_order)] float32 -- the exact columns/order
    dataloader/Dataloader.py stacked into descriptor_catalog_input for this split, read
    straight back off dataset.csv so no normalisation or coarsening is redone here.
    """
    columns = [f"_descpath_{token}" for token in catalog_order]
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise SystemExit(f"dataset.csv is missing descriptor columns: {missing}")
    return frame[columns].to_numpy(dtype=np.float32)


def pick_protein_donors(frame, rng):
    """donor_row[i] = a row index whose protein is a DIFFERENT real protein than row i's
    own, from the same held-out split. None if the split has only one protein (nothing to
    swap onto).
    """
    proteins = frame["LTPProtein"].to_numpy()
    unique_proteins = np.unique(proteins)
    if len(unique_proteins) < 2:
        return None
    rows_by_protein = {p: np.flatnonzero(proteins == p) for p in unique_proteins}
    donor_row = np.empty(len(proteins), dtype=int)
    for i, own in enumerate(proteins):
        other_proteins = unique_proteins[unique_proteins != own]
        chosen_protein = rng.choice(other_proteins)
        donor_row[i] = rng.choice(rows_by_protein[chosen_protein])
    return donor_row


def audit_one(label, family, seed, epoch, ground_truth, device):
    argv = ["pair_shuffle_audit"] + arg_lines(label) + [
        f"--excluded_groups={family}",
        f"--seed={seed}",
        "--num_workers=0",
    ]
    conf = read_configuration(argv)
    if not conf.thematical_paths:
        raise SystemExit(f"{label} is not a --thematical_paths run -- this audit only covers that architecture")
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    _, _, test_dataset = PLIDataset(
        root_dir=data_dir,
        csv=csv,
        seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups,
        config=conf,
        excluded_groups=conf.excluded_groups,
    )
    del csv

    checkpoint = os.path.join(
        PROJECT_ROOT, "models", label, f"groups_{family}", "dynamics", f"seed{seed}_epoch{epoch}.pt",
    )
    if not os.path.exists(checkpoint):
        return {"label": label, "family": family, "seed": seed, "epoch": epoch, "status": "missing_checkpoint"}

    model = InteractionClassification(conf).to(device)
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    model.eval()

    frame = test_dataset.csv.reset_index(drop=True)
    n_rows = len(frame)
    n_proteins = frame["LTPProtein"].nunique()

    head = model.final_layer.thematical_head
    binar = model.final_layer.binar
    catalog_order = full_catalog_order(conf)
    matrix = build_descriptor_matrix(frame, catalog_order)
    real_labels = frame["Interaction"].to_numpy().astype(int)

    with torch.no_grad():
        probs_real = torch.softmax(binar(head(torch.from_numpy(matrix))), dim=1)[:, 1].numpy()
    real_ba, real_sens, real_spec = balanced_metrics(real_labels, (probs_real > 0.5).astype(int))

    rng = np.random.default_rng(seed)
    donor_row = pick_protein_donors(frame, rng)
    if donor_row is None:
        return {
            "label": label, "family": family, "seed": seed, "epoch": epoch,
            "status": "single_protein_family", "n_rows": n_rows, "n_proteins": n_proteins,
            "real_ba": real_ba, "real_sens": real_sens, "real_spec": real_spec,
        }

    protein_col_idx = np.concatenate([
        head.geom_prot_columns.numpy(), head.chem_prot_columns.numpy(),
    ])
    shuffled_matrix = matrix.copy()
    shuffled_matrix[:, protein_col_idx] = matrix[donor_row][:, protein_col_idx]

    donor_proteins = frame["LTPProtein"].to_numpy()[donor_row]
    lipids = frame["FullIdentityOfLipid"].to_numpy()
    shuffled_labels = np.array([
        ground_truth[(donor_proteins[i], lipids[i])] for i in range(n_rows)
    ], dtype=int)

    with torch.no_grad():
        probs_shuf = torch.softmax(binar(head(torch.from_numpy(shuffled_matrix))), dim=1)[:, 1].numpy()
    shuf_ba, shuf_sens, shuf_spec = balanced_metrics(shuffled_labels, (probs_shuf > 0.5).astype(int))

    return {
        "label": label, "family": family, "seed": seed, "epoch": epoch, "status": "ok",
        "n_rows": n_rows, "n_proteins": n_proteins,
        "real_ba": real_ba, "real_sens": real_sens, "real_spec": real_spec,
        "shuffled_ba": shuf_ba, "shuffled_sens": shuf_sens, "shuffled_spec": shuf_spec,
        "ba_drop": real_ba - shuf_ba,
        "mean_abs_prob_shift": float(np.abs(probs_shuf - probs_real).mean()),
    }


def load_ground_truth(data_dir):
    """(LTPProtein, FullIdentityOfLipid) -> Interaction, over the FULL interaction table --
    dataloader/dataset_source.py's own docstring guarantees every cell of the 35 x 312 grid
    is filled, so any swapped-in combination this script builds is a real screened pair with
    a real answer here, not a fabricated label.
    """
    full = pd.read_csv(interaction_csv_path(data_dir))
    return {
        (row.LTPProtein, row.FullIdentityOfLipid): int(row.Interaction)
        for row in full.itertuples()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--labels", required=True, help="comma-separated sweep labels, all --thematical_paths")
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--epoch", type=int, default=120)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = torch.device("cpu")
    ground_truth = load_ground_truth(os.path.join(PROJECT_ROOT, "data") + os.sep)

    rows = []
    for label in args.labels.split(","):
        for family in [f for f in args.families.split(",") if f]:
            for seed in [int(s) for s in args.seeds.split(",")]:
                result = audit_one(label, family, seed, args.epoch, ground_truth, device)
                rows.append(result)
                print(
                    f"{label} {family} seed{seed} epoch{args.epoch}: "
                    f"{result['status']}"
                    + (
                        f" real_BA={result['real_ba']:.3f} shuffled_BA={result['shuffled_ba']:.3f}"
                        if result["status"] == "ok" else ""
                    ),
                    flush=True,
                )

    table = pd.DataFrame(rows)
    table.to_csv(args.out, index=False)
    print(f"wrote : {args.out}")


if __name__ == "__main__":
    main()
