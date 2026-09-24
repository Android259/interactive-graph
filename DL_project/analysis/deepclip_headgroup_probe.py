#!/usr/bin/env python3
"""Can DeepCLIP's lipid branch see a head group at all, with no protein involved?

The question this isolates. GLTP binds glycosphingolipids (HexCer/Hex2Cer/SHexCer)
and not sphingomyelin; GLTPD1 is the exact mirror. Both sit on the same sphingoid
backbone, so the ONLY thing separating them is the head group -- a hexose ring for
one, a phosphocholine for the other. Before asking whether any fusion mechanism can
use that distinction, it is worth knowing whether the lipid branch can represent it
at all, which is a pure lipid classification task: HexCer vs SM, no protein, no
interaction label, no split over proteins.

Why it might not. dataloader/smiles_tokens.py states the design assumption plainly --
"a motif being a head group, which canonical SMILES writes as a contiguous substring
('OP(=O)(O)OCC[N+](C)(C)C' for phosphocholine)". That holds for phosphocholine. It
does not hold for a sugar: measured over this table's own species, a hexose ring
closes across 32-38 SMILES characters, while DeepCLIP's widest published filter is 8
(FILTER_SIZES = [4, 5, 6, 7, 8]). A window of 8 cannot pair "1"..."1" across 35
positions, so the ring is not visible as a ring -- only as more C and O, which a
plain acyl chain also is.

What this prints. Leave-one-out accuracy over the species of both subclasses, for
each --deepclip_widths setting given. The published widths against a set that adds
one wide filter is the comparison that matters: if the published widths cannot do
this and the wide one can, the ring really is the missing piece and widening is the
fix; if neither can, the representation is not where the problem is; if both can,
the lipid branch was never the bottleneck and the fusion is.

Trains (small models, seconds each) but touches nothing the sweeps use -- no
metrics_summary.csv row, no run/ directory, no checkpoint.

    python3 analysis/deepclip_headgroup_probe.py
    python3 analysis/deepclip_headgroup_probe.py --widths 4,5,6,7,8 --widths 4,5,6,7,8,40
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for path in (PROJECT_ROOT, PROJECT_ROOT / "training"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from dataloader.lipid_subclass_blocks import article_subclass_species  # noqa: E402
from dataloader.smiles_tokens import smiles_one_hot  # noqa: E402
from architecture.deepclip import DeepCLIP  # noqa: E402
from read_configuration import read_configuration  # noqa: E402
import pair_baseline_common as pbc  # noqa: E402


def species_smiles(subclasses):
    """{subclass: [canonical SMILES]} for the species of each named subclass.

    One SMILES per species: the interaction table's SmileGlobal can carry several
    candidate structures joined by "; " (the loader splits these into candidates),
    and this probe asks only whether the head group is visible, so the first
    candidate stands for the species.
    """
    table = pbc.read_interactions()
    assignment = article_subclass_species()
    out = {}
    for name in subclasses:
        members = assignment[name]
        rows = table[table["FullIdentityOfLipid"].isin(members)]
        rows = rows.drop_duplicates("FullIdentityOfLipid")
        smiles = []
        for raw in rows["SmileGlobal"]:
            first = str(raw).split(";")[0].strip()
            if first:
                smiles.append(first)
        out[name] = smiles
    return out


def encode(smiles_list):
    """[(characters, vocabulary) float tensor] for each SMILES, skipping any the
    project's strict alphabet refuses (Cl/Br/aromatic forms raise by design)."""
    encoded, kept = [], []
    for smiles in smiles_list:
        try:
            encoded.append(smiles_one_hot(smiles).squeeze(0).float())
            kept.append(smiles)
        except (ValueError, KeyError) as error:
            print(f"  skipped one species: {error}", file=sys.stderr)
    return encoded


def build_config(widths):
    argv = [
        "probe", "--deepclip", "--lipid_smiles_tokens", f"--deepclip_widths={widths}",
        "--ep=1", "--excluded_groups=CRAL-TRIO",
    ]
    conf = read_configuration(argv)
    if conf.final_m is None:
        conf.final_m = conf.m
    return conf


def run_fold(conf, train_x, train_y, test_x, epochs, lr, seed):
    torch.manual_seed(seed)
    model = DeepCLIP(conf)
    optimiser = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimiser.zero_grad()
        flat = torch.cat(train_x, dim=0)
        batch = torch.cat([
            torch.full((len(x),), i, dtype=torch.long) for i, x in enumerate(train_x)
        ])
        out = model(flat, batch)
        loss = loss_fn(out, train_y)
        loss.backward()
        optimiser.step()
    model.eval()
    with torch.no_grad():
        flat = torch.cat(test_x, dim=0)
        batch = torch.cat([
            torch.full((len(x),), i, dtype=torch.long) for i, x in enumerate(test_x)
        ])
        return model(flat, batch).argmax(dim=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--subclasses", default="HexCer,SM", help="the two subclasses to tell apart")
    parser.add_argument("--widths", action="append", default=None,
                        help="a --deepclip_widths value to test; repeatable")
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--seeds", type=int, default=3)
    args = parser.parse_args()

    widths_list = args.widths or ["4,5,6,7,8", "4,5,6,7,8,40"]
    first, second = [s.strip() for s in args.subclasses.split(",")]

    smiles = species_smiles([first, second])
    print(f"{first}: {len(smiles[first])} species | {second}: {len(smiles[second])} species")
    x_a, x_b = encode(smiles[first]), encode(smiles[second])
    data = x_a + x_b
    labels = torch.tensor([0] * len(x_a) + [1] * len(x_b))
    lengths = [len(x) for x in data]
    print(f"encoded {len(data)} molecules, {min(lengths)}-{max(lengths)} characters\n")

    for widths in widths_list:
        conf = build_config(widths)
        n_params = sum(p.numel() for p in DeepCLIP(conf).parameters() if p.requires_grad)
        accuracies = []
        for seed in range(args.seeds):
            correct = 0
            for held in range(len(data)):
                train_x = [x for i, x in enumerate(data) if i != held]
                train_y = torch.tensor([int(labels[i]) for i in range(len(data)) if i != held])
                prediction = run_fold(conf, train_x, train_y, [data[held]], args.epochs, args.lr, seed)
                correct += int(prediction.item() == int(labels[held]))
            accuracies.append(correct / len(data))
        mean = float(np.mean(accuracies))
        print(f"widths {widths:16} параметров {n_params:5}  "
              f"leave-one-out точность {mean:.3f}  (по сидам: {[f'{a:.3f}' for a in accuracies]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
