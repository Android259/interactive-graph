#!/usr/bin/env python3
"""Does DeepCLIP give two proteins of one family different answers on the same lipid?

Why this exists. The --deepclip_protein_gate capacity test
(arg_files/deepclip/deepclip_gltp_protein_gate_ep120.md) asks one question: can the
gate make GLTP and GLTPD1 disagree on identical chemistry -- the thing published
DeepCLIP, whose forward takes the lipid alone, provably cannot do. None of the numbers
a run reports answers it:

  * the random split inside a two-protein family leaves ~20 test rows, and in 7 of 10
    seeds only ONE protein has both classes there (metrics_summary.csv,
    AUC_within_protein_proteins == 1), so "per protein" is really "for one protein";
  * a within-protein AUC can be high for a protein-blind model too: inside one protein
    it only has to rank lipids, and a lipid prior does that;
  * --negatives_per_positive=2 samples ~a quarter of each protein's negatives, so the
    rows where the two proteins actually disagree on one lipid are mostly not in the
    dataset at all.

What it does instead. In DeepCLIP the protein enters through ONE place: the gate's
columns of descriptor_catalog_input (architecture/deepclip.py, gate_columns), which are
pocket descriptors -- constant per protein. So the model's answer for ANY (protein,
lipid) pair can be computed exactly by pairing that lipid's one-hot SMILES with that
protein's gate columns, both taken from the run's own rebuilt split (so the train-fitted
standardisation is the one the run saw). This scores the full matrix
  every lipid present in the rebuilt split  x  every protein of the family
with the selected checkpoint, and reads it against the family table's labels:

  mirror accuracy   over every (lipid, protein that binds it, protein that does not)
                    triple: how often the binder scores higher. Ties count 1/2. A
                    protein-blind model scores every lipid identically across proteins,
                    so it sits at EXACTLY 0.500 -- which makes the no-gate control a
                    check on this script rather than a number that needs its own seeds.
                    Split by whether both cells were training rows (capacity), the
                    lipid was seen in training with some protein, or never (held out).
  per-protein AUC   each protein's own ranking of the matrix lipids, same three strata.
  gate              per protein: spread of the channel weights (mean is 1 by
                    construction), max |w - 1|, and the additive bias. Zero everywhere
                    means the gate never left its initialisation.

Sanity check printed per run: the matrix score of every sampled row is compared with
the score the ordinary model forward gives that row. They must agree; a mismatch means
some lipid is spelled differently in two rows and the matrix used the other spelling.

Reads only. Trains nothing, writes only --out / --summary.

    scripts/env.sh python3 analysis/probes/deepclip_mirror_pairs.py \
        --labels deepclip_gltp_protein_gate_ep120,deepclip_gltp_warm_ep120 \
        --seeds 0,1,2,3,4,5,6,7,8,9 --summary /tmp/gltp_mirror.csv

Weights: --checkpoint selected (default) reads models/<label>/<group>/seed<N>.pt, the
pick the run's test metric was computed on (needs --save_model); final reads
seed<N>_final.pt; an integer reads the --save_model_in_dynamics milestone of that epoch.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)
from training.results_layout import label_family  # noqa: E402
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

# Same reason as new_train.py: set before any thread exists.
torch.set_flush_denormal(True)

import torch_geometric  # noqa: E402

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from checkpoint_scores import arg_lines, self_named_group, split_argv  # noqa: E402
from cross_sampler_eval import binary_auc  # noqa: E402

SPLITS = ("train", "valid", "test")
STRATA = ("train_pair", "seen_lipid", "unseen_lipid")


def checkpoint_path(label, group, seed, which):
    directory = os.path.join(PROJECT_ROOT, "models", label_family(label), label, f"groups_{group}")
    if which == "selected":
        return os.path.join(directory, f"seed{seed}.pt")
    if which == "final":
        return os.path.join(directory, f"seed{seed}_final.pt")
    return os.path.join(directory, "dynamics", f"seed{seed}_epoch{int(which)}.pt")


def build_run(label, group, seed):
    """(conf, {split: dataset}) exactly as the run built them."""
    argv = ["deepclip_mirror_pairs"] + split_argv(arg_lines(label), group) + [
        f"--seed={seed}",
        "--num_workers=0",
    ]
    conf = read_configuration(argv)
    if not conf.deepclip:
        raise SystemExit(f"{label}: not a --deepclip label")
    if conf.relabel_fig3a_disputed_negatives:
        # The matrix reads labels off the table; that flag rewrites some of them inside
        # the loader, and this script does not replicate it.
        raise SystemExit(f"{label}: --relabel_fig3a_disputed_negatives is not supported")
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    datasets = PLIDataset(
        root_dir=data_dir,
        csv=csv,
        seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups,
        config=conf,
        excluded_groups=conf.excluded_groups,
    )
    return conf, dict(zip(SPLITS, datasets)), csv


def table_labels(csv, conf):
    """{(protein, lipid): label} over the family the run was restricted to."""
    frame = csv
    if conf.family_only:
        frame = frame[frame["ProteinDomain"].str.lower() == conf.family_only.lower()]
    drop = set(getattr(conf, "drop_proteins", None) or ())
    if drop:
        frame = frame[~frame["LTPProtein"].isin(drop)]
    keyed = frame.groupby(["LTPProtein", "FullIdentityOfLipid"])["Interaction"]
    if (keyed.nunique() > 1).any():
        raise SystemExit("the table gives one (protein, lipid) pair two labels")
    return keyed.first().to_dict()


def collect_rows(model, conf, datasets):
    """Per sampled row: identity, split, forward score; per lipid/protein: inputs.

    Batch size 1 so every lipid's one-hot tensor comes back on its own; the rows are a
    few hundred, and each forward is a ~2000-parameter network.
    """
    deepclip = model.deepclip
    gate_columns = deepclip.gate_columns
    rows = []
    lipid_input = {}
    lipid_catalog = {}
    protein_gate = {}
    model.eval()
    with torch.no_grad():
        for split, dataset in datasets.items():
            loader = torch_geometric.loader.DataLoader(
                dataset, batch_size=1, shuffle=False, num_workers=0
            )
            frame = dataset.csv
            for position, (prot, lipid) in enumerate(loader):
                catalog = getattr(prot, "descriptor_catalog_input", None)
                logits = deepclip(lipid.x, lipid.batch, catalog)
                score = float(torch.softmax(logits.float(), dim=1)[0, 1])
                protein = frame["LTPProtein"].iloc[position]
                lipid_name = frame["FullIdentityOfLipid"].iloc[position]
                label = int(frame["Interaction"].iloc[position])
                assert label == int(prot.inter.view(-1)[0])
                rows.append({
                    "split": split,
                    "protein": protein,
                    "lipid": lipid_name,
                    "label": label,
                    "row_prob": score,
                })
                lipid_input.setdefault(lipid_name, lipid.x.clone())
                if catalog is not None:
                    lipid_catalog.setdefault(lipid_name, catalog.clone())
                    if gate_columns is not None:
                        values = catalog[0].index_select(0, gate_columns)
                        seen = protein_gate.setdefault(protein, values.clone())
                        # The whole method rests on this: the gate reads protein-only
                        # columns, identical on every row of a protein.
                        if not torch.allclose(seen, values, atol=1e-6):
                            raise SystemExit(
                                f"gate input of {protein} differs between rows -- a "
                                "gate column is not protein-only, the matrix is invalid"
                            )
    return pd.DataFrame(rows), lipid_input, lipid_catalog, protein_gate


def score_matrix(model, proteins, lipid_input, lipid_catalog, protein_gate):
    """{(protein, lipid): prob} for every lipid x protein, one forward per lipid."""
    deepclip = model.deepclip
    gate_columns = deepclip.gate_columns
    scores = {}
    with torch.no_grad():
        for lipid_name, x in lipid_input.items():
            count = len(proteins)
            lip = x.repeat(count, 1)
            lip_batch = torch.arange(count).repeat_interleave(x.shape[0])
            catalog = None
            if lipid_name in lipid_catalog:
                catalog = lipid_catalog[lipid_name].repeat(count, 1)
                if gate_columns is not None:
                    catalog[:, gate_columns] = torch.stack(
                        [protein_gate[protein] for protein in proteins]
                    )
            logits = deepclip(lip, lip_batch, catalog)
            probs = torch.softmax(logits.float(), dim=1)[:, 1]
            for protein, prob in zip(proteins, probs.tolist()):
                scores[(protein, lipid_name)] = prob
    return scores


def gate_summary(model, proteins, protein_gate):
    """Per protein: channel-weight spread, max |w - 1|, bias. Empty without a gate.

    Mirrors DeepCLIP.forward's gate arithmetic (tanh, channel mean-centring, last
    column split off as the bias); keep the two in step.
    """
    gate = model.deepclip.gate
    if gate is None:
        return {}
    out = {}
    with torch.no_grad():
        for protein in proteins:
            raw = torch.tanh(gate(protein_gate[protein].unsqueeze(0).float()))[0]
            channels = raw[:-1] - raw[:-1].mean()
            weights = 1.0 + channels
            out[protein] = {
                "gate_weight_std": float(weights.std()),
                "gate_max_departure": float((weights - 1.0).abs().max()),
                "gate_bias": float(raw[-1]),
            }
    return out


def mirror_accuracy(cells):
    """Concordance over (lipid, binder, non-binder) triples, ties 1/2, by stratum."""
    result = {}
    for stratum in STRATA + ("all",):
        concordant, total = 0.0, 0
        for lipid, group in cells.groupby("lipid"):
            positive = group[group["label"] == 1]
            negative = group[group["label"] == 0]
            if not len(positive) or not len(negative):
                continue
            lipid_seen = bool(group["lipid_in_train"].iloc[0])
            for p_split, p_prob in zip(positive["split"], positive["prob"]):
                for n_split, n_prob in zip(negative["split"], negative["prob"]):
                    both_train = p_split == "train" and n_split == "train"
                    if stratum == "train_pair" and not both_train:
                        continue
                    if stratum == "seen_lipid" and (both_train or not lipid_seen):
                        continue
                    if stratum == "unseen_lipid" and lipid_seen:
                        continue
                    difference = p_prob - n_prob
                    concordant += 1.0 if difference > 0 else (0.5 if difference == 0 else 0.0)
                    total += 1
        result[f"mirror_{stratum}"] = concordant / total if total else float("nan")
        result[f"mirror_{stratum}_n"] = total
    return result


def per_protein_auc(cells, proteins):
    result = {}
    for protein in proteins:
        own = cells[cells["protein"] == protein]
        result[f"auc_{protein}"] = binary_auc(own["label"], own["prob"])
        unseen = own[~own["lipid_in_train"]]
        result[f"auc_{protein}_unseen_lipid"] = binary_auc(unseen["label"], unseen["prob"])
    return result


def analyse(label, seed, which):
    lines = arg_lines(label)
    group = self_named_group(lines)
    if not group:
        raise SystemExit(f"{label}: names no split of its own (expected --family_only)")
    path = checkpoint_path(label, group, seed, which)
    if not os.path.exists(path):
        print(f"missing : {path}", flush=True)
        return None, None

    conf, datasets, csv = build_run(label, group, seed)
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    model.eval()

    rows, lipid_input, lipid_catalog, protein_gate = collect_rows(model, conf, datasets)
    proteins = sorted(rows.protein.unique())
    if model.deepclip.gate is not None and set(protein_gate) != set(proteins):
        raise SystemExit(f"{label}: gate input missing for some protein")
    scores = score_matrix(model, proteins, lipid_input, lipid_catalog, protein_gate)

    rows["matrix_prob"] = [scores[(p, l)] for p, l in zip(rows.protein, rows.lipid)]
    reproduction = float((rows.row_prob - rows.matrix_prob).abs().max())

    labels = table_labels(csv, conf)
    split_of = {(p, l): s for p, l, s in zip(rows.protein, rows.lipid, rows.split)}
    train_lipids = set(rows.lipid[rows.split == "train"])
    cells = pd.DataFrame([
        {
            "protein": protein,
            "lipid": lipid_name,
            "label": int(labels[(protein, lipid_name)]),
            "split": split_of.get((protein, lipid_name), "unsampled"),
            "lipid_in_train": lipid_name in train_lipids,
            "prob": scores[(protein, lipid_name)],
        }
        for (protein, lipid_name) in scores
        if (protein, lipid_name) in labels
    ])

    summary = {
        "label": label,
        "seed": seed,
        "checkpoint": which,
        "proteins": len(proteins),
        "lipids": len(lipid_input),
        "sampled_rows": len(rows),
        "reproduction_max_abs_diff": reproduction,
        # Spread of one lipid's score across proteins, averaged over lipids: exactly 0
        # for a protein-blind model, the plainest "does the protein change anything".
        "score_spread_across_proteins": float(
            cells.groupby("lipid").prob.agg(lambda s: s.max() - s.min()).mean()
        ),
    }
    summary.update(mirror_accuracy(cells))
    summary.update(per_protein_auc(cells, proteins))
    for protein, values in gate_summary(model, proteins, protein_gate).items():
        for key, value in values.items():
            summary[f"{key}_{protein}"] = value
    cells.insert(0, "seed", seed)
    cells.insert(0, "label", label)
    return summary, cells


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--labels", required=True, help="comma-separated --deepclip labels")
    parser.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    parser.add_argument(
        "--checkpoint", default="selected",
        help="selected (seed<N>.pt, default), final (seed<N>_final.pt), or a "
             "--save_model_in_dynamics epoch",
    )
    parser.add_argument("--summary", help="write one row per (label, seed) here")
    parser.add_argument("--out", help="write the scored matrix, one row per cell, here")
    args = parser.parse_args()

    summaries, matrices = [], []
    for label in [x for x in args.labels.split(",") if x]:
        for seed in [int(x) for x in args.seeds.split(",") if x]:
            summary, cells = analyse(label, seed, args.checkpoint)
            if summary is None:
                continue
            summaries.append(summary)
            matrices.append(cells)
            print(
                f"{label} seed{seed} : mirror all {summary['mirror_all']:.3f} "
                f"(n={summary['mirror_all_n']}), train_pair "
                f"{summary['mirror_train_pair']:.3f}, unseen_lipid "
                f"{summary['mirror_unseen_lipid']:.3f} | spread "
                f"{summary['score_spread_across_proteins']:.4f} | reproduction "
                f"{summary['reproduction_max_abs_diff']:.2e}",
                flush=True,
            )
    if not summaries:
        raise SystemExit("no checkpoints scored")

    table = pd.DataFrame(summaries)
    numeric = table.select_dtypes(include=[np.number]).columns.drop("seed")
    print()
    print("mean over seeds:")
    print(table.groupby("label")[list(numeric)].mean().T.to_string(float_format="%.4f"))
    if args.summary:
        table.to_csv(args.summary, index=False)
        print(f"wrote : {args.summary}")
    if args.out:
        pd.concat(matrices).to_csv(args.out, index=False)
        print(f"wrote : {args.out}")


if __name__ == "__main__":
    main()
