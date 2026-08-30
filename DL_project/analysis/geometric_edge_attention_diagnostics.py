#!/usr/bin/env python3
"""Why a run trains flat at chance instead of learning -- e.g. --protein_edge_attention
stuck at valid balanced_accuracy 0.500000 from EPOCH 1 through EPOCH 120 while
--protein_edge_mlp, same edge geometry, same everything else but the conv, learns fine
on the same excluded groups (script_logs/geometric_edge_attention_seeds01234/START/
geometric_edge_attention_seed3_27187.out vs. .../geometric_edge_mlp_seeds01234/...).
Works for any label with saved dynamics checkpoints under models/<label>/, not just
that pair -- it does not assume which flag, if any, is the culprit.

What this prints, for one real batch of the named run's own training split, using its
saved checkpoint (auto-picked -- see --epoch below) rather than a fresh init, so what
you see is the actual model that got stuck:

  1. Structured edge features (e_attr) sanity, when the model has a structured-edge
     conv (--protein_edge_attention/--protein_edge_mlp): shape, range, any nan/inf --
     rules out the geometry computation silently producing garbage.
  2. EdgeAttentionConv's own attention weights, when the model has one, recomputed from
     its live q_proj/k_proj/v_proj on the same input the model just saw (no changes to
     edge_geometric_conv.py needed -- a forward_pre_hook captures its
     (x, edge_index, edge_attr) call and this script replays the same formula outside
     the class). Reported as raw weight min/mean/max and a degree-normalized entropy
     per reference node (1.0 = uniform over neighbors, 0.0 = one-hot) -- tells apart
     "attention never differentiates neighbors" from "attention is sharp but the model
     still doesn't learn".
  3. Gradient norms after one real backward pass, for every conv/attention submodule
     found plus final_layer, so a dead upstream path shows up as a near-zero ratio to
     final_layer rather than an absolute number with no scale to compare to.
  4. The overfit-one-batch test: fixed real batch, fresh Adam, --steps updates. A model
     with a live gradient path can drive a handful of rows near zero loss; one stuck at
     ~ln 2 after --steps steps means the dead spot is in the network itself, not in the
     data, the sampler, or the learning rate schedule of a full run.

Usage:

    python3 analysis/geometric_edge_attention_diagnostics.py --label geometric_edge_attention
    python3 analysis/geometric_edge_attention_diagnostics.py --label geometric_edge_mlp \\
        --excluded_groups=LBP_BPI_CETP --seed=2 --steps=300

--excluded_groups/--seed are only required when that label's checkpoints cover more
than one group or seed; with exactly one on disk it is picked automatically and named
in the output. Run two labels against the same excluded group/seed and compare the four
sections -- whichever one first diverges between them is where the fault is.
"""

import argparse
import os
import re
import sys

import pandas as pd
import torch
import torch.nn.functional as F

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

import torch_geometric  # noqa: E402

from read_configuration import read_configuration  # noqa: E402
from architecture.interaction_classification import InteractionClassification  # noqa: E402
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from forward_args import build_forward_args  # noqa: E402
from reproducibility import seed_everything  # noqa: E402
from analysis.checkpoint_scores import arg_lines  # noqa: E402


def discover_group(label):
    """The excluded group to inspect, when --excluded_groups was not given: the only
    one this label has any checkpoints for. With more than one on disk there is no
    correct guess, so this lists them and asks for one instead of picking blindly."""
    root = os.path.join(PROJECT_ROOT, "models", label)
    groups = sorted(
        name[len("groups_"):] for name in os.listdir(root)
        if name.startswith("groups_") and os.path.isdir(os.path.join(root, name))
    ) if os.path.isdir(root) else []
    if len(groups) == 1:
        return groups[0]
    raise SystemExit(
        f"--excluded_groups not given, and models/{label}/ has checkpoints for "
        f"{len(groups)} group(s){': ' + ', '.join(groups) if groups else ''}. "
        "Pass one with --excluded_groups."
    )


def discover_seed(label, excluded_groups):
    """Same idea as discover_group, one level down: the only seed this label/group has
    dynamics checkpoints for."""
    dynamics = os.path.join(PROJECT_ROOT, "models", label, f"groups_{excluded_groups}", "dynamics")
    pattern = re.compile(r"seed(\d+)_epoch\d+\.pt$")
    seeds = sorted({
        int(match.group(1))
        for name in (os.listdir(dynamics) if os.path.isdir(dynamics) else [])
        for match in [pattern.match(name)]
        if match
    })
    if len(seeds) == 1:
        return seeds[0]
    raise SystemExit(
        f"--seed not given, and {dynamics} has checkpoints for {len(seeds)} "
        f"seed(s){': ' + ', '.join(map(str, seeds)) if seeds else ''}. Pass one with --seed."
    )


def discover_latest_epoch(label, excluded_groups, seed):
    """The highest-epoch dynamics checkpoint saved for this label/group/seed, or None
    if none exist -- used so the diagnostic inspects the actual model that got stuck,
    not a fresh init, without the caller having to know which epochs were saved."""
    dynamics = os.path.join(PROJECT_ROOT, "models", label, f"groups_{excluded_groups}", "dynamics")
    pattern = re.compile(rf"seed{seed}_epoch(\d+)\.pt$")
    epochs = [
        int(match.group(1))
        for name in (os.listdir(dynamics) if os.path.isdir(dynamics) else [])
        for match in [pattern.match(name)]
        if match
    ]
    return max(epochs) if epochs else None


def build_conf(label, excluded_groups, seed):
    argv = ["geometric_edge_attention_diagnostics"] + arg_lines(label) + [
        f"--excluded_groups={excluded_groups}",
        f"--seed={seed}",
        "--num_workers=0",
    ]
    conf = read_configuration(argv)
    if conf.final_m is None:
        conf.final_m = conf.m
    return conf


def mixed_class_batch(dataset, batch_size):
    """First batch off `dataset` that has both labels present -- an all-one-class
    batch would let the overfit test "succeed" by predicting the batch majority
    without the network doing anything, which defeats the point of the check."""
    loader = torch_geometric.loader.DataLoader(
        dataset, batch_size=batch_size, shuffle=True, num_workers=0
    )
    for prot, lipid in loader:
        labels = prot.inter.view(-1)
        if labels.min() != labels.max():
            return prot, lipid, labels
    raise SystemExit(
        f"no batch of {batch_size} rows had both classes; pass a larger --batch"
    )


def find_edge_attention_modules(model):
    """Every EdgeAttentionConv in the model, by its dotted name (protein1.encodin1,
    lipid1.encodin1, ...) -- whichever branches this config actually built."""
    return [
        (name, module)
        for name, module in model.named_modules()
        if module.__class__.__name__ == "EdgeAttentionConv"
    ]


def report_edge_features(name, edge_attr):
    finite = torch.isfinite(edge_attr)
    print(f"  {name} e_attr: shape={tuple(edge_attr.shape)}", end="  ")
    if not finite.all():
        print(f"NON-FINITE VALUES: {(~finite).sum().item()} of {edge_attr.numel()}")
        return
    print(
        f"min={edge_attr.min().item():.4f} max={edge_attr.max().item():.4f} "
        f"mean={edge_attr.mean().item():.4f} std={edge_attr.std().item():.4f}"
    )


def report_attention_weights(name, module, captured_input):
    """Replay EdgeAttentionConv.forward's own math on the input it was just called
    with, using its live q_proj/k_proj/v_proj, to pull out the softmax weights the
    class itself never returns."""
    x, edge_index, edge_attr = captured_input
    report_edge_features(name, edge_attr)

    reference, neighbor = edge_index[0], edge_index[1]
    num_nodes = x.shape[0]
    q = module.q_proj(x).view(num_nodes, module.heads, module.out_dim)
    kv_input = torch.cat((x[neighbor], edge_attr), dim=-1)
    k = module.k_proj(kv_input).view(-1, module.heads, module.out_dim)
    scores = (q[reference] * k).sum(dim=-1) / (module.out_dim ** 0.5)
    weights = torch_geometric.utils.softmax(scores, index=reference, num_nodes=num_nodes)

    degree = torch.zeros(num_nodes, dtype=torch.long, device=x.device)
    degree.index_add_(0, reference, torch.ones_like(reference))

    neg_w_logw = -(weights * weights.clamp_min(1e-12).log())
    entropy_per_node = torch.zeros(num_nodes, module.heads, dtype=weights.dtype, device=x.device)
    entropy_per_node.index_add_(0, reference, neg_w_logw)
    countable = degree > 1
    max_entropy = degree.clamp_min(2).float().log().unsqueeze(-1)
    normalized_entropy = (entropy_per_node / max_entropy)[countable]

    print(
        f"  {name} attention weights over {edge_index.shape[1]} edges, "
        f"{module.heads} head(s): "
        f"min={weights.min().item():.4f} mean={weights.mean().item():.4f} "
        f"max={weights.max().item():.4f}"
    )
    if normalized_entropy.numel() == 0:
        print(f"  {name} every reference node has degree <= 1; entropy undefined")
    else:
        print(
            f"  {name} degree-normalized entropy over {countable.sum().item()} "
            f"nodes with >1 neighbor: min={normalized_entropy.min().item():.4f} "
            f"mean={normalized_entropy.mean().item():.4f} "
            f"max={normalized_entropy.max().item():.4f}  "
            "(1.0 = uniform over neighbors, 0.0 = all weight on one neighbor)"
        )


def grad_norm(module):
    total = 0.0
    any_grad = False
    for parameter in module.parameters():
        if parameter.grad is not None:
            any_grad = True
            total += parameter.grad.pow(2).sum().item()
    return (total ** 0.5) if any_grad else None


def report_gradients(model, edge_attention_modules):
    print("\nGradient norms after one real backward pass:")
    reference = grad_norm(model.final_layer)
    print(f"  final_layer                : {reference!r}")
    for name, module in edge_attention_modules:
        for sub_name in ("q_proj", "k_proj", "v_proj"):
            sub = getattr(module, sub_name)
            norm = grad_norm(sub)
            ratio = "n/a" if not (norm and reference) else f"{norm / reference:.6f}"
            print(f"  {name}.{sub_name:<8}: {norm!r:<22} (/ final_layer = {ratio})")


def overfit_one_batch(model, conf, prot, lipid, labels, steps, lr):
    print(f"\nOverfitting this one batch ({labels.shape[0]} rows) for {steps} steps, lr={lr}:")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    checkpoints = sorted({1, steps // 4, steps // 2, (3 * steps) // 4, steps} - {0})
    for step in range(1, steps + 1):
        optimizer.zero_grad(set_to_none=True)
        out = model(**build_forward_args(conf, prot, lipid))
        loss = F.cross_entropy(out, labels)
        loss.backward()
        optimizer.step()
        if step in checkpoints:
            print(f"  step {step:>5}: loss={loss.item():.6f}")
    if loss.item() < 0.3:
        print(
            "  -> dropped well below ln(2); this path CAN fit these rows -- a full "
            "run's flat 0.5 is not a dead conv, look at the sampler/lr/schedule instead."
        )
    elif loss.item() > 0.65:
        print(
            "  -> stayed at/near ln(2)=0.693 after fitting one small batch; the "
            "gradient path from this loss back through the model is not doing "
            "anything -- look at whichever module in the gradient-norm table above "
            "has a near-zero ratio to final_layer."
        )
    else:
        print("  -> moved, but did not clearly converge; rerun with more --steps.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True, help="arg-file name under scripts/arg_files/, and the models/<label>/ checkpoint directory")
    parser.add_argument("--excluded_groups", default=None, help="auto-detected if this label has checkpoints for only one group")
    parser.add_argument("--seed", type=int, default=None, help="auto-detected if only one seed has checkpoints for the chosen group")
    parser.add_argument("--epoch", type=int, default=None, help="which dynamics checkpoint epoch to load; default is the latest one found on disk")
    parser.add_argument("--fresh", action="store_true", help="skip checkpoint loading even if one exists -- inspect a fresh random init instead")
    parser.add_argument("--batch", type=int, default=32, help="diagnostic batch size (independent of the run's own --batch)")
    parser.add_argument("--steps", type=int, default=300, help="overfit-one-batch iterations")
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    device = torch.device(args.device)
    excluded_groups = args.excluded_groups or discover_group(args.label)
    seed = args.seed if args.seed is not None else discover_seed(args.label, excluded_groups)
    conf = build_conf(args.label, excluded_groups, seed)
    print(
        f"label={args.label} excluded_groups={excluded_groups} seed={seed} "
        f"protein_edge_attention={conf.protein_edge_attention} "
        f"protein_edge_mlp={conf.protein_edge_mlp}"
    )

    seed_everything(conf.seed)
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pd.read_csv(interaction_csv_path(data_dir))
    train_dataset, _valid, _test = PLIDataset(
        root_dir=data_dir,
        csv=csv,
        seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups,
        config=conf,
        excluded_groups=conf.excluded_groups,
    )
    del csv

    model = InteractionClassification(conf).to(device)
    epoch = None if args.fresh else (args.epoch if args.epoch is not None else discover_latest_epoch(args.label, excluded_groups, seed))
    if epoch is not None:
        checkpoint = os.path.join(
            PROJECT_ROOT, "models", args.label, f"groups_{excluded_groups}",
            "dynamics", f"seed{seed}_epoch{epoch}.pt",
        )
        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
        print(f"loaded checkpoint: {checkpoint}")
    else:
        print("fresh random init (no saved checkpoint found, or --fresh given)")

    edge_attention_modules = find_edge_attention_modules(model)
    if not edge_attention_modules:
        print(
            "\nNo EdgeAttentionConv in this model -- either --protein_edge_attention "
            "is off (e.g. this label uses --protein_edge_mlp's EdgeMLPConv instead, or "
            "GATv2Conv/plain), or it only applies on the lipid side under a config "
            "this run doesn't use. Nothing attention-specific to report; the "
            "gradient-norm and overfit sections below still run as a general capacity "
            "check."
        )

    prot, lipid, labels = mixed_class_batch(train_dataset, args.batch)
    prot, lipid, labels = prot.to(device), lipid.to(device), labels.to(device)

    captured = {}
    handles = [
        module.register_forward_pre_hook(
            lambda _module, inputs, _name=name: captured.__setitem__(_name, inputs)
        )
        for name, module in edge_attention_modules
    ]
    model.zero_grad(set_to_none=True)
    out = model(**build_forward_args(conf, prot, lipid))
    loss = F.cross_entropy(out, labels)
    loss.backward()
    for handle in handles:
        handle.remove()

    print(f"\nOne real batch ({labels.shape[0]} rows, {int(labels.sum())} positive): loss={loss.item():.6f}")
    print(f"logits: min={out.min().item():.4f} max={out.max().item():.4f} std={out.std().item():.4f}")
    if out.std().item() < 1e-4:
        print(
            "  -> the model outputs nearly the SAME logits for every row in this "
            "batch -- whatever feeds final_layer is not carrying per-row information."
        )

    if edge_attention_modules:
        print("\nAttention weights (recomputed from the live q_proj/k_proj/v_proj):")
        for name, module in edge_attention_modules:
            if name not in captured:
                print(f"  {name}: never called for this batch (unreachable branch?)")
                continue
            report_attention_weights(name, module, captured[name])

    report_gradients(model, edge_attention_modules)
    overfit_one_batch(model, conf, prot, lipid, labels, args.steps, args.lr)


if __name__ == "__main__":
    main()
