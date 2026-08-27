#!/usr/bin/env python3
"""Score a --compatibility_input checkpoint twice: with its feature, and with it removed.

The question. `analysis/compatibility_probe.py` finds that a `--compatibility_input` run
ranks the held-out block far above the base run (0.751 vs 0.546 inside protein) while its
score correlates with the compatibility feature at r = 0.015 -- it does not look like the
network is reading the feature out. But a near-zero linear correlation does not rule out
the network using it nonlinearly, and the two readings imply opposite conclusions:

  the feature carries the gain  -> the result is the feature, and the same number is
                                  obtainable without a network (the probe's fit columns)
  the feature only shaped training -> the gain is in the weights, and the feature is
                                  scaffolding that inference no longer needs

Only an ablation separates them, and it is cheap because it trains nothing: the
standardised feature has train mean 0 by construction (`_compute_compatibility_input` in
dataloader/New_dataloader.py), so substituting zero feeds the classifier exactly the value
an average training row carried -- the neutral input, not an out-of-range one.

Reports both AUCs on the same rows, pooled and inside protein, so the difference is the
feature's contribution at inference and nothing else.

Reads only. Trains nothing, appends to no shared table.

    scripts/env.sh python3 analysis/compat_input_ablation.py --label <label>
    scripts/env.sh python3 analysis/compat_input_ablation.py --label <label> --split test
"""
import argparse
import os
import sys

import pandas
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

torch.set_flush_denormal(True)

import torch_geometric  # noqa: E402

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.New_dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from forward_args import build_forward_args  # noqa: E402
from reproducibility import seed_everything  # noqa: E402

from checkpoint_scores import DEFAULT_FAMILIES, arg_lines  # noqa: E402
from null_model import WORKING, auc, per_protein_auc  # noqa: E402


def score_split(model, conf, dataset, device, zero_compat):
    """Class-1 probability per row, optionally with compat_input replaced by zero.

    Same loader settings as analysis/checkpoint_scores.py -- `shuffle=False` so the
    scores line up with `dataset.csv` row for row, `eval()` so nothing is order
    dependent.
    """
    loader = torch_geometric.loader.DataLoader(
        dataset, batch_size=32, shuffle=False, num_workers=0
    )
    probs, labels = [], []
    model.eval()
    with torch.no_grad():
        for prot, lipid in loader:
            prot = prot.to(device)
            lipid = lipid.to(device)
            if zero_compat:
                prot.compat_input = torch.zeros_like(prot.compat_input)
            out = model(**build_forward_args(conf, prot, lipid))
            probs.append(torch.softmax(out.float(), dim=1)[:, 1].cpu())
            labels.append(prot.inter.view(-1).cpu())
    return torch.cat(probs).numpy(), torch.cat(labels).numpy()


def ablation_table(label, epoch, seeds, families, split, batch=16, device=None,
                    verbose=True):
    """One row per (family, seed): AUC with the feature and with it zeroed."""
    device = device or torch.device("cpu")
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    base = arg_lines(label)

    rows = []
    for family in families:
        for seed in seeds:
            argv = ["compat_input_ablation"] + base + [
                f"--excluded_groups={family}", f"--seed={seed}",
                f"--batch={batch}", "--num_workers=0",
            ]
            conf = read_configuration(argv)
            if not getattr(conf, "compatibility_input", False):
                raise SystemExit(
                    f"{label} was not trained with --compatibility_input -- there is no "
                    "feature to ablate"
                )
            if conf.final_m is None:
                conf.final_m = conf.m
            seed_everything(conf.seed)
            csv = pandas.read_csv(interaction_csv_path(data_dir))
            _, valid_dataset, test_dataset = PLIDataset(
                root_dir=data_dir, csv=csv, seed=conf.seed,
                excluded_subgroups=conf.excluded_subgroups, config=conf,
                excluded_groups=conf.excluded_groups,
            )
            del csv
            dataset = valid_dataset if split == "valid" else test_dataset

            checkpoint = os.path.join(
                PROJECT_ROOT, "models", label, f"groups_{family}", "dynamics",
                f"seed{seed}_epoch{epoch}.pt",
            )
            if not os.path.exists(checkpoint):
                if verbose:
                    print(f"missing : {checkpoint}", flush=True)
                continue
            model = InteractionClassification(conf).to(device)
            model.load_state_dict(
                torch.load(checkpoint, map_location="cpu", weights_only=True)
            )

            frame = dataset.csv
            with_feature, labels = score_split(model, conf, dataset, device, False)
            without, labels_again = score_split(model, conf, dataset, device, True)
            assert (labels == labels_again).all()
            assert (frame["Interaction"].to_numpy() == labels).all()

            record = {
                "fam": family, "seed": seed, "rows": len(frame),
                "with": auc(labels, with_feature),
                "zeroed": auc(labels, without),
            }
            record["with_prot"], record["proteins"] = per_protein_auc(
                frame, with_feature
            )
            record["zeroed_prot"], _ = per_protein_auc(frame, without)
            rows.append(record)
            if verbose:
                print(
                    f"{family} seed{seed} : {record['with']:.3f} -> "
                    f"{record['zeroed']:.3f} pooled, {record['with_prot']:.3f} -> "
                    f"{record['zeroed_prot']:.3f} inside protein",
                    flush=True,
                )

    table = pandas.DataFrame(rows)
    table["drop"] = table["with"] - table["zeroed"]
    table["drop_prot"] = table["with_prot"] - table["zeroed_prot"]
    return table


def print_ablation_report(table, split, epoch, label):
    pandas.set_option("display.width", 220)
    print(f"\n=== {split} block, epoch {epoch}, {label} ===")
    print(table.round(3).to_string(index=False))

    columns = ["with", "zeroed", "drop", "with_prot", "zeroed_prot", "drop_prot"]
    print("\n=== per family (mean over seeds) ===")
    print(table.groupby("fam")[columns].mean().round(3).to_string())

    print("\n=== grouped (files/signal_state.md 6.4) ===")
    print(pandas.DataFrame({
        "all seven": table[columns].mean(),
        "working three": table[table["fam"].isin(WORKING)][columns].mean(),
        "other four": table[~table["fam"].isin(WORKING)][columns].mean(),
        "scp2 only": table[table["fam"] == "scp2"][columns].mean(),
    }).round(3).to_string())
    print()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--epoch", type=int, default=120)
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument("--out", help="write the per-split table here")
    args = parser.parse_args()

    table = ablation_table(
        args.label, args.epoch,
        seeds=[int(s) for s in args.seeds.split(",")],
        families=[f for f in args.families.split(",") if f],
        split=args.split, batch=args.batch,
    )
    print_ablation_report(table, args.split, args.epoch, args.label)
    if args.out:
        table.to_csv(args.out, index=False)
        print(f"wrote : {args.out}")


if __name__ == "__main__":
    main()
