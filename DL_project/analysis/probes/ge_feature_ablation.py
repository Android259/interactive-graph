#!/usr/bin/env python3
"""Inference-time input ablation for geometric_edge (`ge_*`) checkpoints.

The ge models read, per protein node, residue features (`node_x`), the ESM3 embedding
(`esm3`), a burial value (`bury`) and the named pocket descriptors broadcast from
`descriptor_catalog_input` (`--protein_descriptors`); the lipid side reads the MolFormer
token embedding (`molformer`). This replaces one or several of those inputs of an already
trained checkpoint (models/<label>/groups_<g>/seed<N>.pt, the weights run_test measures)
and re-scores the held-out TEST and VALID blocks. Nothing is retrained.

Replacement modes
    zero   the input is set to 0. For the named descriptors that is the train mean (they are
           standardised on train); for ESM3, MolFormer, `bury` and `node_x` it is a literal
           zero -- ESM3 zeroed means the protein-language-model channel is switched off.
    mean   the input is replaced by its mean over the TRAIN proteins' nodes (lipids' tokens
           for `molformer`). Same as `zero` for the descriptors; a less off-manifold reading
           for the four unstandardised inputs.

What is evaluated (per checkpoint): the untouched model; every single feature; every pair of
features (zero); a few named groups; and a sampled Shapley value of every feature for
v(S) = metric with exactly S KEPT, estimated from random permutations (the full 2^n subset
sweep that analysis/probes/mlp_feature_subsets.py does for the descriptor MLP is not available
here -- one scoring pass is a protein-graph forward, ~0.4 s for a 144-row block).

Speed. In a ge model the protein tower is the whole cost (~90% of a pass) and it is a function
of ONE protein's inputs only, while the lipid tower, cross-attention and head together are
cheap. So per ablation the protein tower runs once per UNIQUE protein of the block (25
instead of 144 graphs), its node embeddings are cached per (protein-side mask), and the
per-row passes reuse them through a patched `protein1.forward`. `--verify` re-scores random
masks through the plain, unpatched model and requires the same probabilities.

Run one process per seed (`--workers` spawns them) and then summarise:

    python3 analysis/probes/ge_feature_ablation.py --label ge_s15_prothid32_hid64_noreg \\
        --out_dir /tmp/ge_ablation --workers 5

Reads only; trains nothing, appends to no shared table.
"""
import argparse
import itertools
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import torch
import torch_geometric

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
from training.results_layout import label_family  # noqa: E402
sys.path.insert(0, os.path.join(PROJECT_ROOT, "analysis"))

from checkpoint_scores import (  # noqa: E402
    read_configuration,
    seed_everything,
    PLIDataset,
    InteractionClassification,
    interaction_csv_path,
)
from forward_args import build_forward_args  # noqa: E402
from dataloader.pair_descriptors import full_catalog_order  # noqa: E402
from mlp_feature_ablation import confusion_metrics  # noqa: E402

torch.set_flush_denormal(True)

NON_DESCRIPTOR = ("esm3", "bury", "node_x", "molformer")
PROTEIN_SIDE_NON_DESCRIPTOR = ("esm3", "bury", "node_x")
BATCH = 32


def load_checkpoint(label, group, seed):
    models_dir = os.path.join(PROJECT_ROOT, "models", label_family(label), label, f"groups_{group}")
    argv = json.load(open(os.path.join(models_dir, f"seed{seed}.args.json")))
    conf = read_configuration(["ge_feature_ablation"] + argv)
    if conf.final_m is None:
        conf.final_m = conf.m
    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    datasets = PLIDataset(
        root_dir=data_dir, csv=csv, seed=conf.seed, excluded_subgroups=conf.excluded_subgroups,
        config=conf, excluded_groups=conf.excluded_groups,
    )
    del csv
    model = InteractionClassification(conf)
    model.load_state_dict(torch.load(
        os.path.join(models_dir, f"seed{seed}.pt"), map_location="cpu", weights_only=True
    ))
    model.eval()
    return conf, model, datasets


def collate(dataset, indices):
    subset = torch.utils.data.Subset(dataset, [int(i) for i in indices])
    loader = torch_geometric.loader.DataLoader(
        subset, batch_size=max(len(indices), 1), shuffle=False, num_workers=0
    )
    return next(iter(loader))


class Block:
    """One held-out split, pre-collated: row batches, a one-graph-per-protein batch, labels."""

    def __init__(self, dataset):
        self.dataset = dataset
        frame = dataset.csv
        self.frame = frame
        loader = torch_geometric.loader.DataLoader(
            dataset, batch_size=BATCH, shuffle=False, num_workers=0
        )
        self.batches = list(loader)
        self.labels = torch.cat([p.inter.view(-1) for p, _ in self.batches]).numpy()
        proteins = frame["LTPProtein"].to_numpy()
        codes, uniques = pd.factorize(proteins)
        self.row_protein = codes
        first = np.zeros(len(uniques), dtype=int)
        first[codes[::-1]] = np.arange(len(codes))[::-1]
        self.unique_batch = collate(dataset, first)
        counts = torch.bincount(self.unique_batch[0].batch)
        self.unique_counts = counts.tolist()
        self.expanded = "_candidate_index" in frame.columns
        if self.expanded:
            self.pair_index, _ = pd.factorize(frame["pair_id"].to_numpy())
            pair_first = np.zeros(self.pair_index.max() + 1, dtype=int)
            pair_first[self.pair_index[::-1]] = np.arange(len(self.pair_index))[::-1]
            self.pair_labels = self.labels[pair_first]
        else:
            self.pair_labels = self.labels

    def pool(self, probs):
        if not self.expanded:
            return probs
        sums = np.zeros(self.pair_index.max() + 1)
        counts = np.zeros_like(sums)
        np.add.at(sums, self.pair_index, probs)
        np.add.at(counts, self.pair_index, 1)
        return sums / counts


def train_means(model, train_dataset):
    """Per-dimension mean over the TRAIN proteins' nodes / lipids' tokens, one graph per unique."""
    frame = train_dataset.csv
    p_codes, p_unique = pd.factorize(frame["LTPProtein"].to_numpy())
    p_first = np.zeros(len(p_unique), dtype=int)
    p_first[p_codes[::-1]] = np.arange(len(p_codes))[::-1]
    l_codes, l_unique = pd.factorize(frame["FullIdentityOfLipid"].to_numpy())
    l_first = np.zeros(len(l_unique), dtype=int)
    l_first[l_codes[::-1]] = np.arange(len(l_codes))[::-1]
    prot, _ = collate(train_dataset, p_first)
    _, lip = collate(train_dataset, l_first)
    present = prot.bury != 2  # 2 marks a missing burial value
    return {
        "esm3": prot.plm.float().mean(0),
        "node_x": prot.x.float().mean(0),
        "bury": prot.bury[present].float().mean() if present.any() else prot.bury.float().mean(),
        "molformer": lip.x.float().mean(0),
    }


class Ablation:
    """Forward-pre-hook on the model: replaces chosen inputs in the kwargs of one forward."""

    def __init__(self, descriptor_columns, descriptor_names, means):
        self.columns = descriptor_columns
        self.names = descriptor_names
        self.means = means
        self.zeroed = frozenset()
        self.mode = "zero"
        self.lipid_only = False  # protein-side replacements are cached instead of applied

    def __call__(self, module, args, kwargs):
        if not self.zeroed:
            return None
        kwargs = dict(kwargs)
        if not self.lipid_only:
            cols = [c for c, n in zip(self.columns, self.names) if n in self.zeroed]
            if cols and kwargs.get("descriptor_catalog_input") is not None:
                catalog = kwargs["descriptor_catalog_input"].clone()
                catalog[:, cols] = 0.0
                kwargs["descriptor_catalog_input"] = catalog
            for name, key in (("esm3", "plm"), ("node_x", "prot"), ("bury", "bury")):
                if name in self.zeroed:
                    tensor = kwargs[key]
                    if self.mode == "mean":
                        kwargs[key] = (self.means[name].to(tensor.dtype)).expand_as(tensor).clone()
                    else:
                        kwargs[key] = torch.zeros_like(tensor)
        if "molformer" in self.zeroed:
            tensor = kwargs["lip"]
            if self.mode == "mean":
                kwargs["lip"] = self.means["molformer"].to(tensor.dtype).expand_as(tensor).clone()
            else:
                kwargs["lip"] = torch.zeros_like(tensor)
        return args, kwargs


class Scorer:
    def __init__(self, conf, model, blocks, means):
        self.conf = conf
        self.model = model
        self.blocks = blocks
        columns = model.protein1.protein_descriptor_columns
        catalog = full_catalog_order(conf)
        self.descriptor_columns = [int(c) for c in columns.tolist()]
        self.descriptor_names = [catalog[c] for c in self.descriptor_columns]
        self.ablation = Ablation(self.descriptor_columns, self.descriptor_names, means)
        model.register_forward_pre_hook(self.ablation, with_kwargs=True)
        self.features = list(self.descriptor_names) + list(NON_DESCRIPTOR)
        self.cache = {}

    def _protein_key(self, zeroed, mode, split):
        protein_side = frozenset(
            z for z in zeroed if z in self.descriptor_names or z in PROTEIN_SIDE_NON_DESCRIPTOR
        )
        uses_mode = any(z in PROTEIN_SIDE_NON_DESCRIPTOR for z in protein_side)
        return (protein_side, mode if uses_mode else "zero", split)

    @torch.no_grad()
    def _protein_embeddings(self, zeroed, mode, split):
        key = self._protein_key(zeroed, mode, split)
        if key in self.cache:
            return self.cache[key]
        block = self.blocks[split]
        captured = []
        handle = self.model.protein1.register_forward_hook(lambda m, a, o: captured.append(o))
        self.ablation.zeroed = key[0]
        self.ablation.mode = key[1]
        self.ablation.lipid_only = False
        try:
            prot, lip = block.unique_batch
            self.model(**build_forward_args(self.conf, prot, lip))
        finally:
            handle.remove()
        embedding = captured[0].detach()
        pieces = list(torch.split(embedding, block.unique_counts))
        self.cache[key] = pieces
        if len(self.cache) > 4096:
            self.cache.pop(next(iter(self.cache)))
        return pieces

    @torch.no_grad()
    def probs(self, zeroed, mode, split, plain=False):
        """Probability of class 1 per row of the block's split (before candidate pooling)."""
        block = self.blocks[split]
        zeroed = frozenset(zeroed)
        out = []
        if plain:
            self.ablation.zeroed = zeroed
            self.ablation.mode = mode
            self.ablation.lipid_only = False
            for prot, lip in block.batches:
                logits = self.model(**build_forward_args(self.conf, prot, lip))
                out.append(torch.softmax(logits.float(), dim=1)[:, 1])
            return torch.cat(out).numpy()
        pieces = self._protein_embeddings(zeroed, mode, split)
        self.ablation.zeroed = frozenset(z for z in zeroed if z == "molformer")
        self.ablation.mode = mode
        self.ablation.lipid_only = True
        offset = 0
        protein_tower = self.model.protein1

        def patched(*args, **kwargs):
            nonlocal offset
            graphs = int(args[5].max()) + 1
            rows = block.row_protein[offset:offset + graphs]
            offset += graphs
            return torch.cat([pieces[j] for j in rows])

        protein_tower.forward = patched
        try:
            for prot, lip in block.batches:
                logits = self.model(**build_forward_args(self.conf, prot, lip))
                out.append(torch.softmax(logits.float(), dim=1)[:, 1])
        finally:
            del protein_tower.__dict__["forward"]
        return torch.cat(out).numpy()

    def metrics(self, zeroed, mode, split, plain=False):
        block = self.blocks[split]
        pooled = block.pool(self.probs(zeroed, mode, split, plain))
        return confusion_metrics(pooled, block.pair_labels)


def run_seed(args, seed):
    started = time.perf_counter()
    torch.set_num_threads(args.threads)
    conf, model, (train_dataset, valid_dataset, test_dataset) = load_checkpoint(
        args.label, args.group, seed
    )
    means = train_means(model, train_dataset)
    blocks = {"test": Block(test_dataset), "valid": Block(valid_dataset)}
    scorer = Scorer(conf, model, blocks, means)
    features = scorer.features
    rng = np.random.default_rng(seed)
    results = {}

    def evaluate(zeroed, mode):
        zeroed = frozenset(zeroed)
        effective = mode if any(z in NON_DESCRIPTOR for z in zeroed) else "zero"
        key = (zeroed, effective)
        if key not in results:
            results[key] = {s: scorer.metrics(zeroed, effective, s) for s in ("test", "valid")}
        return results[key]

    base = evaluate(frozenset(), "zero")
    rows = []

    def record(kind, name, zeroed, mode):
        measured = evaluate(zeroed, mode)
        effective = mode if any(z in NON_DESCRIPTOR for z in zeroed) else "zero"
        for split in ("test", "valid"):
            rows.append(dict(kind=kind, name=name, mode=effective, split=split, seed=seed,
                             **measured[split]))

    record("baseline", "baseline", [], "zero")
    for feature in features:
        record("single", feature, [feature], "zero")
        if feature in NON_DESCRIPTOR:
            record("single", feature, [feature], "mean")
    for a, b in itertools.combinations(features, 2):
        record("pair", f"{a}+{b}", [a, b], "zero")
    descriptors = list(scorer.descriptor_names)
    groups = {
        "all_descriptors": descriptors,
        "esm3+molformer": ["esm3", "molformer"],
        "protein_nondescriptor": list(PROTEIN_SIDE_NON_DESCRIPTOR),
        "protein_all": descriptors + list(PROTEIN_SIDE_NON_DESCRIPTOR),
        "lipid_all": ["molformer"],
        "everything": features,
    }
    for name, members in groups.items():
        record("group", name, members, "zero")
        if any(m in NON_DESCRIPTOR for m in members):
            record("group", name, members, "mean")

    # Sampled Shapley for v(S) = metric with exactly S KEPT, replacement mode args.shapley_mode.
    shapley = {s: {m: np.zeros(len(features)) for m in ("BA", "F1")} for s in ("test", "valid")}
    for _ in range(args.permutations):
        order = rng.permutation(len(features))
        zeroed = set(features)
        previous = evaluate(zeroed, args.shapley_mode)
        for index in order:
            zeroed.discard(features[index])
            current = evaluate(zeroed, args.shapley_mode)
            for split in ("test", "valid"):
                for metric in ("BA", "F1"):
                    shapley[split][metric][index] += current[split][metric] - previous[split][metric]
            previous = current
    shapley_out = {
        f"{split}_{metric}": (values / max(args.permutations, 1)).tolist()
        for split, per in shapley.items() for metric, values in per.items()
    }
    if args.verify:
        worst = 0.0
        for _ in range(args.verify):
            size = int(rng.integers(1, len(features)))
            zeroed = frozenset(rng.choice(features, size=size, replace=False).tolist())
            mode = "mean" if rng.random() < 0.5 else "zero"
            fast = scorer.probs(zeroed, mode, "test")
            slow = scorer.probs(zeroed, mode, "test", plain=True)
            worst = max(worst, float(np.abs(fast - slow).max()))
        print(f"seed {seed}: max |p_fast - p_plain| over {args.verify} random masks = {worst:.2e}",
              flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(os.path.join(args.out_dir, f"scores_seed{seed}.csv"), index=False)
    with open(os.path.join(args.out_dir, f"shapley_seed{seed}.json"), "w") as handle:
        json.dump(dict(features=features, permutations=args.permutations,
                       mode=args.shapley_mode, **shapley_out), handle)
    print(f"seed {seed}: {len(results)} distinct masks scored in "
          f"{time.perf_counter() - started:.0f}s; baseline test BA {base['test']['BA']:.4f} "
          f"F1 {base['test']['F1']:.4f}", flush=True)


def check_table(args, seeds):
    table = pd.read_csv(os.path.join(PROJECT_ROOT, "results", "tables", "metrics_summary.csv"), low_memory=False)
    table = table[table["label"] == args.label].sort_values("datetime")
    latest = table.groupby(["exclusion_set", "seed"]).tail(1)
    scores = pd.concat([pd.read_csv(os.path.join(args.out_dir, f"scores_seed{s}.csv")) for s in seeds])
    base = scores[(scores["kind"] == "baseline") & (scores["split"] == "test")]
    merged = base.merge(latest, on="seed", suffixes=("", "_table"))
    gap = (merged["BA"] - merged["balanced_accuracy"].astype(float)).abs()
    print(f"\ncheck vs metrics_summary.csv: {len(merged)} seeds matched; max |BA diff| "
          f"{gap.max():.4f}, mean {gap.mean():.4f}")


def summarise(args, seeds):
    scores = pd.concat([pd.read_csv(os.path.join(args.out_dir, f"scores_seed{s}.csv")) for s in seeds])
    shapleys = [json.load(open(os.path.join(args.out_dir, f"shapley_seed{s}.json"))) for s in seeds]
    features = shapleys[0]["features"]
    base = scores[scores["kind"] == "baseline"].set_index(["split", "seed"])
    for column in ("BA", "F1"):
        pass

    def delta(frame, split):
        indexed = frame[frame["split"] == split].set_index("seed")
        reference = base.loc[split]
        return pd.DataFrame({
            "dBA": indexed["BA"] - reference["BA"].reindex(indexed.index),
            "dF1": indexed["F1"] - reference["F1"].reindex(indexed.index),
            "dAUC": indexed["AUC"] - reference["AUC"].reindex(indexed.index),
        })

    def aggregate(kind):
        part = scores[scores["kind"] == kind]
        rows = []
        for (name, mode), group in part.groupby(["name", "mode"]):
            test = delta(group, "test")
            valid = delta(group, "valid")
            rows.append(dict(name=name, mode=mode, dBA_test=test.dBA.mean(), dF1_test=test.dF1.mean(),
                             dAUC_test=test.dAUC.mean(), dBA_valid=valid.dBA.mean(),
                             worse=int((test.dBA < -0.005).sum()), better=int((test.dBA > 0.005).sum()),
                             n=len(test)))
        return pd.DataFrame(rows).sort_values("dBA_test").reset_index(drop=True)

    singles, pairs, groups = aggregate("single"), aggregate("pair"), aggregate("group")
    ref_t = base.loc["test"]
    ref_v = base.loc["valid"]
    print(f"\n{len(seeds)} seeds. Untouched: test BA {ref_t['BA'].mean():.3f} F1 {ref_t['F1'].mean():.3f} "
          f"AUC {ref_t['AUC'].mean():.3f} | valid BA {ref_v['BA'].mean():.3f}")

    # Sampled Shapley, mean and sd across seeds, ranked by test BA.
    ba = np.array([s["test_BA"] for s in shapleys])
    f1 = np.array([s["test_F1"] for s in shapleys])
    bav = np.array([s["valid_BA"] for s in shapleys])
    shap = pd.DataFrame({
        "feature": features, "shapley_BA_test": ba.mean(0), "sd_across_seeds": ba.std(0, ddof=1) if len(seeds) > 1 else 0.0,
        "shapley_F1_test": f1.mean(0), "shapley_BA_valid": bav.mean(0),
    }).sort_values("shapley_BA_test", ascending=False)
    shap.insert(0, "rank", range(1, len(features) + 1))
    single_zero = singles[singles["mode"] == "zero"].set_index("name")["dBA_test"]
    single_mean = singles[singles["mode"] == "mean"].set_index("name")["dBA_test"]
    shap["single_zero_dBA"] = shap["feature"].map(single_zero)
    shap["single_mean_dBA"] = shap["feature"].map(single_mean)
    perms = shapleys[0]["permutations"]
    print(f"\nSampled Shapley value of each input for test BA ({perms} permutations per seed, "
          f"replacement mode '{shapleys[0]['mode']}'), ranked by importance; sum over inputs = "
          f"untouched - everything replaced:")
    print(shap.round(4).to_string(index=False))
    print("\nNamed groups replaced together (test dBA, ascending = most damaging first):")
    print(groups.round(4).to_string(index=False))
    print("\nMost damaging pairs (test dBA; zero mode):")
    print(pairs.head(15).round(4).to_string(index=False))
    sums = {row["name"]: row["dBA_test"] for _, row in singles[singles["mode"] == "zero"].iterrows()}
    pairs = pairs.copy()
    pairs["sum_singles"] = [sums[n.split("+")[0]] + sums[n.split("+")[1]] for n in pairs["name"]]
    pairs["extra"] = pairs["dBA_test"] - pairs["sum_singles"]
    print("\nLargest synergy (pair worse than the sum of its singles):")
    print(pairs.sort_values("extra").head(6)[["name", "dBA_test", "sum_singles", "extra"]].round(4).to_string(index=False))
    print("\nLargest redundancy (pair milder than the sum of its singles):")
    print(pairs.sort_values("extra").tail(6)[["name", "dBA_test", "sum_singles", "extra"]].round(4).to_string(index=False))
    shap.to_csv(os.path.join(args.out_dir, "shapley.csv"), index=False)
    singles.to_csv(os.path.join(args.out_dir, "singles.csv"), index=False)
    pairs.to_csv(os.path.join(args.out_dir, "pairs.csv"), index=False)
    groups.to_csv(os.path.join(args.out_dir, "groups.csv"), index=False)
    print(f"\nwrote shapley.csv, singles.csv, pairs.csv, groups.csv in {args.out_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--group", default=None, help="excluded-group directory name (default: the only one)")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--permutations", type=int, default=100, help="Shapley permutations per seed")
    parser.add_argument("--shapley_mode", default="zero", choices=("zero", "mean"))
    parser.add_argument("--verify", type=int, default=4, help="random masks per seed re-scored unpatched")
    parser.add_argument("--workers", type=int, default=1, help="parallel processes (one per seed)")
    parser.add_argument("--threads", type=int, default=None)
    parser.add_argument("--seed_child", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--summarize_only", action="store_true")
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    root = os.path.join(PROJECT_ROOT, "models", label_family(args.label), args.label)
    if args.group is None:
        found = sorted(d[len("groups_"):] for d in os.listdir(root) if d.startswith("groups_"))
        if len(found) != 1:
            raise SystemExit(f"--group required, found {found}")
        args.group = found[0]
    seeds = [int(s) for s in args.seeds.split(",")]
    if args.threads is None:
        args.threads = max(1, (os.cpu_count() or 4) // max(args.workers, 1) - 1)

    if args.seed_child is not None:
        run_seed(args, args.seed_child)
        return
    if not args.summarize_only:
        started = time.perf_counter()
        pending = list(seeds)
        running = []
        while pending or running:
            while pending and len(running) < args.workers:
                seed = pending.pop(0)
                command = [sys.executable, os.path.abspath(__file__), "--label", args.label,
                           "--group", args.group, "--out_dir", args.out_dir,
                           "--permutations", str(args.permutations), "--shapley_mode", args.shapley_mode,
                           "--verify", str(args.verify), "--threads", str(args.threads),
                           "--seed_child", str(seed)]
                running.append(subprocess.Popen(command))
            time.sleep(1)
            running = [p for p in running if p.poll() is None]
        print(f"all seeds done in {time.perf_counter() - started:.0f}s")
    check_table(args, seeds)
    summarise(args, seeds)


if __name__ == "__main__":
    main()
