#!/usr/bin/env python3
"""How much of a protein's lipid preference the protein branch can predict on its own.

The pair task mixes two questions: what the protein is like, and how a given lipid fits
it. This asks only the first. The target is the protein's binding PROFILE -- for each
head-group class, the share of that class's lipids the protein binds -- so one vector of
34 numbers per protein, 35 proteins in all, and no lipid input anywhere.

Why bother when the pair model already trains the same branch end to end: the ceiling is
known independently. With a whole family held out, predicting its proteins' profiles as
the mean of the training proteins scores 0.169 by cosine on average, and copying the
three nearest neighbours in mean-pooled ESM3 space scores 0.190 -- on four families of
seven the neighbours do worse than the mean. Those bracket what any method reading this
input can reach here. A branch that lands on the mean is extracting nothing and the
fault is in the branch; one that reaches the neighbour line is extracting what there is
and the fault is in the input. Both references are printed per split, because both vary
by family far more than they differ from each other.

(Holding out one PROTEIN instead of one family is a much easier problem -- its relatives
stay in training -- and reaches 0.259 and 0.335. Those numbers do not apply here.)

What it cannot do is add information. The bound belongs to the input, not to the head.

The branch is the real one -- the configured Protein_encoder and its pooling, reached by
hooking the pooling module of a fully built model -- so a result here transfers to the
model that runs. Only the 34-wide head on top is new.

Usage (same config flags as training; the split flags choose which family is held out):

    python3 analysis/protein_profile_probe.py --excluded_groups=START --ep=200 \\
        --protein_disable_post_sa_mlp --lipid_disable_post_sa_mlp \\
        --third_layers_in_mlps --fast_attention --hiddim=64 --plm_compression_dim=64
"""

import glob
import os
import sys

import numpy as np
import pandas
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataloader.New_dataloader import PLIDataset
from dataloader.dataset_source import interaction_csv_path
from dataloader.sampler import lipid_class_series
from architecture.interaction_classification import InteractionClassification
from training.read_configuration import read_configuration

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def class_profiles(csv):
    """One row per protein: the share of each head-group class's lipids it binds."""
    frame = csv.copy()
    frame["lipid_class"] = lipid_class_series(frame)
    table = (
        frame.pivot_table(
            index="LTPProtein",
            columns="lipid_class",
            values="Interaction",
            aggfunc="mean",
        )
        .fillna(0.0)
        .sort_index(axis=1)
    )
    return table


def cosine(a, b):
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denominator) if denominator else 0.0


def esm3_neighbour_reference(train_names, held_names, profiles):
    """Profile cosine reached by copying the three nearest training proteins.

    The reference the learned head has to beat, computed for THIS split rather than
    quoted from another one. Holding a whole family out is a different problem from
    holding one protein out: leave-one-protein-out leaves the protein's own relatives in
    training and reaches 0.335 on average, while leaving the family out reaches 0.190,
    and on four families of seven it does worse than ignoring the protein entirely.
    Printing the easier number next to a family-held-out result would flatter the head
    or damn it for no reason.
    """
    import pickle

    means = {}
    for path in glob.glob(os.path.join(PROJECT_ROOT, "data", "embedding_ESM3", "*")):
        name = os.path.basename(path).split("_")[0]
        with open(path, "rb") as handle:
            stored = pickle.load(handle)
        if isinstance(stored, dict):
            stored = next(iter(stored.values()))
        tensor = torch.as_tensor(stored).float()
        if tensor.dim() == 3:
            tensor = tensor[0]
        means[name] = tensor.numpy().mean(axis=0)

    usable = [n for n in train_names if n in means]
    scores = []
    for name in held_names:
        if name not in means:
            continue
        nearest = sorted(usable, key=lambda t: -cosine(means[name], means[t]))[:3]
        predicted = profiles.loc[nearest].to_numpy().mean(axis=0)
        scores.append(cosine(profiles.loc[name].to_numpy(), predicted))
    return float(np.mean(scores)) if scores else float("nan")


def one_row_per_protein(dataset):
    """Positions in `dataset.csv` of the first row of each protein it holds."""
    seen = {}
    for position, protein in enumerate(dataset.csv["LTPProtein"].tolist()):
        seen.setdefault(protein, position)
    return seen


def forward_args(conf, prot, lipid):
    """The model's forward kwargs for one batch.

    A copy of training/new_train.py's `_build_forward_args`, which is a module-level
    closure over that script's `conf` and cannot be imported without running the whole
    training file. Only the branches the probe's own flags can reach are kept; anything
    else this configuration needs would raise inside the encoder rather than pass
    silently, which is the failure mode worth having.
    """
    args = dict(
        config=conf,
        plm=prot.plm,
        bury=prot.bury,
        prot=prot.x,
        prot_edgidx=prot.edge_index,
        prot_e_attr=prot.edge_attr,
        prot_batch=prot.batch,
        lip=lipid.x,
        lip_batch=lipid.batch,
    )
    if conf.lipid_fragments_mask:
        args["lipid_batch"] = lipid.lipid_batch
    if conf.prot_attention_pos_bias or conf.prot_pooling_by_pockets:
        args["pocket_mask"] = prot.pocket
    if getattr(conf, "pocket_descriptors", False):
        args["pocket_descriptor"] = prot.pocket_descriptor
    return args


def pooled_protein_vectors(conf, model, loader, device):
    """Run the real branch over one loader pass and catch what its pooling produces.

    A forward hook rather than final_layer._pooled_partners: that one is detached and
    filled only outside training, and this needs gradients.
    """
    pooling = getattr(model.final_layer, "prot_gem_pool", None)
    if pooling is None:
        raise RuntimeError(
            "the probe reads the protein vector off prot_gem_pool, which only exists "
            "under --pool_type=gem; run it with the pooling the model uses"
        )
    captured = []
    handle = pooling.register_forward_hook(
        lambda _module, _inputs, output: captured.append(output)
    )
    try:
        for prot, lipid in loader:
            prot = prot.to(device)
            lipid = lipid.to(device)
            model(**forward_args(conf, prot, lipid))
        if not captured:
            raise RuntimeError("the pooling hook never fired")
        return torch.cat(captured, dim=0)
    finally:
        handle.remove()


def main():
    conf = read_configuration()
    conf.save_dynamics = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data")))
    profiles = class_profiles(csv)

    # The loader joins root_dir with plain file names, so it wants the data directory
    # itself -- the trailing separator is what training/new_train.py passes too.
    train_dataset, valid_dataset, test_dataset = PLIDataset(
        root_dir=os.path.join(PROJECT_ROOT, "data") + os.sep,
        csv=csv,
        seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups,
        config=conf,
        excluded_groups=conf.excluded_groups,
    )

    train_positions = one_row_per_protein(train_dataset)
    held_positions = one_row_per_protein(test_dataset)
    print(f"proteins in train : {len(train_positions)}")
    print(f"proteins held out : {len(held_positions)} ({', '.join(sorted(held_positions))})")

    model = InteractionClassification(conf).to(device)
    head = torch.nn.Linear(conf.hiddim, profiles.shape[1]).to(device)
    optimiser = torch.optim.Adam(
        list(model.protein1.parameters()) + list(head.parameters()), lr=conf.lr
    )

    import torch_geometric

    # Micro-batched on purpose: all 32 protein graphs at once, each hundreds of
    # residues wide with a 1536-long embedding per residue, was enough to have the
    # frontend's OOM killer take the process before the first epoch. The hook collects
    # every batch's pooled vectors and they are concatenated, so the gradient is the
    # same as a single batch would give -- only the peak differs.
    probe_batch = max(1, int(getattr(conf, "batch", 8)))

    def loader_for(dataset, positions, names):
        subset = torch.utils.data.Subset(dataset, [positions[n] for n in names])
        return torch_geometric.loader.DataLoader(
            subset, batch_size=min(probe_batch, len(names)), shuffle=False
        )

    train_names = sorted(train_positions)
    held_names = sorted(held_positions)
    train_loader = loader_for(train_dataset, train_positions, train_names)
    held_loader = loader_for(test_dataset, held_positions, held_names)
    target = torch.tensor(
        profiles.loc[train_names].to_numpy(dtype="float32"), device=device
    )

    for epoch in range(conf.ep):
        model.train(True)
        optimiser.zero_grad(set_to_none=True)
        pooled = pooled_protein_vectors(conf, model, train_loader, device)
        loss = torch.nn.functional.mse_loss(head(pooled), target)
        loss.backward()
        optimiser.step()
        if (epoch + 1) % 25 == 0:
            print(f"epoch {epoch + 1:>4} : train mse {loss.item():.5f}")

    model.train(False)
    with torch.no_grad():
        predicted = head(
            pooled_protein_vectors(conf, model, held_loader, device)
        ).cpu().numpy()

    truth = profiles.loc[held_names].to_numpy()
    mean_profile = profiles.loc[train_names].to_numpy().mean(axis=0)
    learned = float(np.mean([cosine(t, p) for t, p in zip(truth, predicted)]))
    constant = float(np.mean([cosine(t, mean_profile) for t in truth]))
    print()
    neighbour = esm3_neighbour_reference(train_names, held_names, profiles)
    print(f"held-out profile cosine, learned head   : {learned:.3f}")
    print(f"held-out profile cosine, mean of train  : {constant:.3f}")
    print(f"held-out profile cosine, 3 nearest ESM3 : {neighbour:.3f}")


if __name__ == "__main__":
    main()
