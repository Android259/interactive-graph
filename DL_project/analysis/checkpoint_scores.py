#!/usr/bin/env python3
"""Per-row model scores from the weights `--save_model_in_dynamics` kept.

Why this exists. Every number a run reports about the held-out block is a decision at a
fixed 0.5 threshold: balanced accuracy, sensitivity, specificity. That cannot separate
"the model ranks the block no better than chance" from "the model ranks it fine and the
threshold sits in the wrong place", and on this split the two are not academic -- the
chemistry null model in `files/marginals_and_cold_split.md` scores BA 0.512 with a
threshold fitted on training and AUC 0.59 on the same rows. Comparing a network to it
therefore needs the network's *ranking*, which needs per-row scores, which no run writes.

What it does. Rebuilds the configuration from `scripts/arg_files/<label>.md` plus the
`--excluded_groups`/`--seed` the sweep varied, rebuilds the split from that (the loader
is deterministic in the seed, so the rows come back identical), loads a checkpoint into
a freshly constructed model, and writes one CSV row per
(family, seed, epoch, split, pair_id) with the probability of class 1.

Checked against the training logs: reconstructing scp2/seed0/epoch120 of
`bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120` reproduces the logged validation
balanced accuracy as 0.6090891361, digit for digit, so the weights land in the model
they were trained in and the rows are the rows that were validated on.

Reads only. Trains nothing, appends to no shared table.

    python3 analysis/checkpoint_scores.py --label bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 \
        --out /tmp/scores.csv
    python3 analysis/checkpoint_scores.py --label <label> --families=scp2 --seeds=0 --epochs=120 --out ...

`--epochs` must name epochs the run actually saved: `DYNAMICS_CHECKPOINT_EPOCHS` in
training/new_train.py, currently 1, 10, 49, 51, 120. Missing files are reported and
skipped rather than raising, so a partially finished sweep still yields what it has.
"""
import argparse
import os
import sys

import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

# Same reason as new_train.py: set before any thread exists, so intra-op workers inherit
# it. Without it a checkpoint whose dead blocks decayed into denormals evaluates orders
# of magnitude slower, for bit-identical output.
torch.set_flush_denormal(True)

import torch_geometric  # noqa: E402

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.New_dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from forward_args import build_forward_args  # noqa: E402
from reproducibility import seed_everything  # noqa: E402


DEFAULT_FAMILIES = (
    "CRAL-TRIO",
    "GLTP",
    "IP_trans",
    "LBP_BPI_CETP",
    "START",
    "lipocalin",
    "scp2",
)
# training/new_train.py:DYNAMICS_CHECKPOINT_EPOCHS
DEFAULT_EPOCHS = "1,10,49,51,120"


def arg_lines(label):
    """The sweep's argument file, as the shell would have handed it to python."""
    path = os.path.join(PROJECT_ROOT, "scripts", "arg_files", f"{label}.md")
    lines = []
    for raw in open(path):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # The launcher passes the file through a shell, which strips the quotes around
        # --pool_type="gem". Reading the file directly does not, and the configuration
        # validator then rejects '"gem"' as not being one of its pool types.
        if "=" in line:
            key, value = line.split("=", 1)
            line = key + "=" + value.strip().strip('"').strip("'")
        lines.append(line)
    return lines


def score_split(model, conf, dataset, device):
    """Probability of class 1 for every row of `dataset`, in dataset order.

    `shuffle=False` so the scores line up with `dataset.csv` row for row. Nothing in the
    model is order-dependent under `eval()` -- pooling, attention and the norms are all
    per-graph -- so the numbers are the ones a shuffled validation pass would produce.
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
            out = model(**build_forward_args(conf, prot, lipid))
            probs.append(torch.softmax(out.float(), dim=1)[:, 1].cpu())
            labels.append(prot.inter.view(-1).cpu())
    return torch.cat(probs).numpy(), torch.cat(labels).numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="sweep label, also the arg-file name")
    parser.add_argument("--epochs", default=DEFAULT_EPOCHS)
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--batch", type=int, default=16, help="only affects the split's sampler")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    epochs = [int(e) for e in args.epochs.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    families = [f for f in args.families.split(",") if f]
    device = torch.device("cpu")
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    base = arg_lines(args.label)

    frames = []
    for family in families:
        for seed in seeds:
            argv = ["checkpoint_scores"] + base + [
                f"--excluded_groups={family}",
                f"--seed={seed}",
                f"--batch={args.batch}",
                "--num_workers=0",
            ]
            conf = read_configuration(argv)
            if conf.final_m is None:
                conf.final_m = conf.m
            seed_everything(conf.seed)
            csv = pd.read_csv(interaction_csv_path(data_dir))
            _, valid_dataset, test_dataset = PLIDataset(
                root_dir=data_dir,
                csv=csv,
                seed=conf.seed,
                excluded_subgroups=conf.excluded_subgroups,
                config=conf,
                excluded_groups=conf.excluded_groups,
            )
            del csv
            model = InteractionClassification(conf).to(device)
            parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)

            for epoch in epochs:
                checkpoint = os.path.join(
                    PROJECT_ROOT, "models", args.label, f"groups_{family}",
                    "dynamics", f"seed{seed}_epoch{epoch}.pt",
                )
                if not os.path.exists(checkpoint):
                    print(f"missing : {checkpoint}", flush=True)
                    continue
                model.load_state_dict(
                    torch.load(checkpoint, map_location="cpu", weights_only=True)
                )
                for split_name, dataset in (("valid", valid_dataset), ("test", test_dataset)):
                    probs, labels = score_split(model, conf, dataset, device)
                    frame = dataset.csv
                    # Both are the contract this script rests on: the rebuilt split is
                    # the trained-on split, and the scores are aligned to its rows.
                    assert len(frame) == len(probs), (len(frame), len(probs))
                    assert (frame["Interaction"].to_numpy() == labels).all()
                    frames.append(pd.DataFrame({
                        "label": args.label,
                        "parameters": parameters,
                        "fam": family,
                        "seed": seed,
                        "epoch": epoch,
                        "split": split_name,
                        "pair_id": frame["pair_id"].to_numpy(),
                        "protein": frame["LTPProtein"].to_numpy(),
                        "lipid": frame["FullIdentityOfLipid"].to_numpy(),
                        "label_value": labels,
                        "prob": probs,
                    }))
                print(f"{family} seed{seed} epoch{epoch} : scored ({parameters} parameters)", flush=True)
            del valid_dataset, test_dataset, model

    if not frames:
        raise SystemExit("no checkpoints scored")
    pd.concat(frames).to_csv(args.out, index=False)
    print(f"wrote : {args.out}")


if __name__ == "__main__":
    main()
