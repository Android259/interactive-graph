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

import numpy as np
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
from dataloader.Dataloader import PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pair_descriptors import resolve_similarity_feature_names  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS  # noqa: E402
from dataloader.lipid_subclass_blocks import FIG3_SUBCLASS_BLOCKS  # noqa: E402
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
# The other held-out axis. A --lipid_coldsplit sweep varies these instead of families:
# one run per lipid-class set, every protein in train. Its checkpoints and test reports
# sit under the same "groups_<name>" directory name, so `families` throughout this file
# is really "the excluded-group axis", whichever axis the label holds out.
DEFAULT_LIPID_SETS = tuple(LIPID_COLDSPLIT_SETS)
# training/new_train.py:DYNAMICS_CHECKPOINT_EPOCHS
DEFAULT_EPOCHS = "1,10,49,51,120"


def arg_lines(label):
    """The sweep's argument file, as the shell would have handed it to python.

    A "--flag=value" line whose value continues onto an indented line right after it
    (scripts/lib/args_file_lib.sh's own multi-line convention, for a
    --good_descriptors/--bad_descriptors list too long for one line) is joined back
    onto that flag here, comma-separated, the same way the bash side does --
    read_configuration would otherwise see the continuation as its own bare, unknown
    parameter. Any other line -- unindented, or indented with no flag currently open
    -- is commentary and is dropped, unchanged from before this convention existed.
    """
    path = os.path.join(PROJECT_ROOT, "scripts", "arg_files", f"{label}.md")
    lines = []
    pending = None
    for raw in open(path):
        stripped = raw.strip()
        if stripped.startswith("--"):
            if pending is not None:
                lines.append(pending)
                pending = None
            # The launcher passes the file through a shell, which strips the quotes
            # around --pool_type="gem". Reading the file directly does not, and the
            # configuration validator then rejects '"gem"' as not being one of its
            # pool types.
            if "=" in stripped:
                key, value = stripped.split("=", 1)
                pending = key + "=" + value.strip().strip('"').strip("'")
            else:
                lines.append(stripped)
        elif stripped and raw[:1] in (" ", "\t") and pending is not None:
            fragment = stripped.lstrip(",")
            if fragment:
                pending = pending.rstrip(",") + "," + fragment
        else:
            if pending is not None:
                lines.append(pending)
                pending = None
    if pending is not None:
        lines.append(pending)
    return lines


# Split flags that carry their own block in the args file, in the order
# training/new_train.py assembles the run-directory name from them.
SELF_NAMING_SPLIT_FLAGS = (
    "lipid_coldsplit", "lipid_isolation", "lipid_subclass",
    "lipid_species_coldsplit", "family_only",
)


def valued_flag(lines, name):
    """The value of `--<name>=<value>` in an args file, or "" when it is absent or bare."""
    prefix = f"--{name}="
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):]
    return ""


def self_named_group(lines):
    """The run-directory name a label names outright, or "" when it names none.

    Mirrors training/new_train.py's excluded_set_parts: each part is prefixed
    "groups_" and the parts are joined by "_", so what score_checkpoints needs for its
    f"groups_{family}" path is the parts joined by "_groups_". A label with both
    --lipid_subclass=<spec> and --family_only=<name> therefore gives
    "CerP+Hex2Cer+SHexCer_groups_gltp", which is the directory those runs actually
    wrote.
    """
    parts = []
    for name in SELF_NAMING_SPLIT_FLAGS:
        value = valued_flag(lines, name)
        if not value:
            continue
        if name == "lipid_isolation":
            value = f"iso{value}"
        elif name == "lipid_species_coldsplit":
            value = "species%02d" % int(float(value) * 100 + 0.5)
        parts.append(value)
    return "_groups_".join(parts)


def split_argv(lines, group):
    """`lines` with the bare split marker removed, plus the flag that names `group`.

    A --lipid_coldsplit sweep's arg file carries the flag with NO value: it marks the
    axis for the submitter, which strips the bare line and appends its own
    --lipid_coldsplit=<set> per run. read_configuration requires a value and rejects
    the bare line as an unknown parameter, which is why every reader that rebuilds a
    configuration from an arg file has to do this strip itself -- the same one
    analysis/full_label_report.py's label_coldsplit_params already does, and the reason
    the "AUC vs chemistry null model" section of every --lipid_coldsplit label's report
    used to fail with `ValueError: Unknown parameter: --lipid_coldsplit`.

    The two axes are mutually exclusive (read_configuration rejects them together), so
    --excluded_groups is not appended for a lipid label -- `group` is a lipid-class set
    name there, not a family. --lipid_subclass is the third axis (a Titeca-et-al.
    subclass block, dataloader/lipid_subclass_blocks.py's FIG3_SUBCLASS_BLOCKS) and
    takes the same bare-marker treatment.

    An arg file may instead name its block OUTRIGHT (--lipid_subclass=<spec>,
    --lipid_isolation=<key>, --lipid_species_coldsplit=<share>, --family_only=<name>),
    which is what a single-block label does -- and then there is nothing to append at
    all. Detecting only the bare marker sent such a label down the last branch, where
    the appended --excluded_groups collided with the split flag already in the file and
    read_configuration refused the pair; every gate label
    (deepclip_*_protein_gate_subclass_*) is of this shape.
    """
    if "--lipid_coldsplit" in lines:
        kept = [line for line in lines if line != "--lipid_coldsplit"]
        return kept + [f"--lipid_coldsplit={group}"]
    if "--lipid_subclass" in lines:
        kept = [line for line in lines if line != "--lipid_subclass"]
        return kept + [f"--lipid_subclass={group}"]
    if any(valued_flag(lines, name) for name in SELF_NAMING_SPLIT_FLAGS):
        return list(lines)
    return list(lines) + [f"--excluded_groups={group}"]


def default_groups_for_label(label):
    """The excluded-group names a sweep of this label actually ran, by its own axis.

    Without this a --lipid_coldsplit label reached here with the seven protein
    families, looked for models/<label>/groups_CRAL-TRIO/ that no such run ever wrote,
    reported every checkpoint missing and ended in "no checkpoints scored". Same
    reasoning covers --lipid_subclass: its nine FIG3_SUBCLASS_BLOCKS directory names
    (some "+"-joined, e.g. groups_PS+PGP+DAG+TAG) are neither the seven families nor
    the four LIPID_COLDSPLIT_SETS.
    """
    lines = arg_lines(label)
    if "--lipid_coldsplit" in lines:
        return list(DEFAULT_LIPID_SETS)
    if "--lipid_subclass" in lines:
        return list(FIG3_SUBCLASS_BLOCKS)
    named = self_named_group(lines)
    if named:
        # One block, already spelled out in the args file -- there is no axis to
        # rotate, and the seven families would look for directories no such run wrote.
        return [named]
    return list(DEFAULT_FAMILIES)


def label_descriptor_features(label, families):
    """--good_descriptors/--bad_descriptors/--descriptor_names resolved off `label`'s
    own args file, as a sorted comma-separated base-name list for null_model.py's
    --features (see dataloader.pair_descriptors.resolve_similarity_feature_names) --
    the chemistry null model then runs on exactly the descriptor set the network
    itself was trained to see, instead of a fixed guess (analysis/full_label_report.py,
    analysis/build_rand_results_tables.py). Empty string when the label's config sets
    none of the three (most labels, historically -- no --descriptors_head at all).

    --descriptor_names (ModelConfig docstring) is --descriptors_head's own single-
    head equivalent of --good_descriptors/--bad_descriptors -- validate() guarantees
    at most one of the two pairs is ever non-empty for a given label, so passing all
    three here always resolves to exactly whichever one that label actually set.

    `families[0]` is a dummy held-out group (read_configuration requires one; the
    result does not vary by group) -- same trick full_label_report.py's
    label_coldsplit_params uses for --coldsplit_share/--negatives_per_positive.
    split_argv turns it into whichever flag this label's axis actually takes.
    """
    argv = ["label_descriptor_features"] + split_argv(
        arg_lines(label), families[0]
    ) + ["--seed=0"]
    conf = read_configuration(argv)
    names = resolve_similarity_feature_names(
        conf.good_descriptors, conf.bad_descriptors, conf.descriptor_names
    )
    return ",".join(names)


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


def _average_candidate_rows(frame, probs, labels):
    """Collapse an expanded split's candidate rows into one scored row per pair.

    Mirrors training/candidate_averaging.py: the probability of a pair is the mean over
    its candidate structures, and the pair keeps the identity and the label its rows
    already agree on. First-seen order is preserved, so the result is still in dataset
    order.
    """
    pair_ids = frame["pair_id"].to_numpy()
    order = []
    sums = {}
    counts = {}
    positions = {}
    for position, pair in enumerate(pair_ids):
        pair = int(pair)
        if pair not in sums:
            sums[pair] = float(probs[position])
            counts[pair] = 1
            positions[pair] = position
            order.append(pair)
        else:
            sums[pair] += float(probs[position])
            counts[pair] += 1
    keep = [positions[pair] for pair in order]
    averaged = np.array([sums[pair] / counts[pair] for pair in order], dtype=float)
    return frame.iloc[keep], averaged, labels[keep]


def score_checkpoints(label, epochs, seeds, families, batch=16, device=None, verbose=True,
                      splits=("valid", "test")):
    """Per-row (family, seed, epoch, split, pair_id) scores for one sweep label.

    `splits` may include "train". It is not in the default because scoring it costs a
    pass over a set several times larger than the evaluated block and nothing that
    reads this table asked for it -- but "does this run fit its own train set" cannot
    be answered without it, and that is the first question when a run scores at chance
    (train high and block at chance is memorisation; both at chance is an optimisation
    failure, and the two call for opposite fixes).

    The loop `main()` used to run inline, factored out so analysis/full_label_report.py
    (and anything else that wants scores without a CSV round-trip) can call it directly.
    Returns the concatenated DataFrame `main()` used to write to --out; raises if nothing
    could be scored, same as before.
    """
    device = device or torch.device("cpu")
    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    base = arg_lines(label)

    frames = []
    for family in families:
        for seed in seeds:
            argv = ["checkpoint_scores"] + split_argv(base, family) + [
                f"--seed={seed}",
                f"--batch={batch}",
                "--num_workers=0",
            ]
            conf = read_configuration(argv)
            if conf.final_m is None:
                conf.final_m = conf.m
            seed_everything(conf.seed)
            csv = pd.read_csv(interaction_csv_path(data_dir))
            train_dataset, valid_dataset, test_dataset = PLIDataset(
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
                    PROJECT_ROOT, "models", label, f"groups_{family}",
                    "dynamics", f"seed{seed}_epoch{epoch}.pt",
                )
                if not os.path.exists(checkpoint):
                    if verbose:
                        print(f"missing : {checkpoint}", flush=True)
                    continue
                model.load_state_dict(
                    torch.load(checkpoint, map_location="cpu", weights_only=True)
                )
                by_name = {"train": train_dataset, "valid": valid_dataset, "test": test_dataset}
                for split_name in splits:
                    dataset = by_name[split_name]
                    probs, labels = score_split(model, conf, dataset, device)
                    frame = dataset.csv
                    # Both are the contract this function rests on: the rebuilt split is
                    # the trained-on split, and the scores are aligned to its rows.
                    assert len(frame) == len(probs), (len(frame), len(probs))
                    assert (frame["Interaction"].to_numpy() == labels).all()
                    if "_candidate_index" in frame.columns:
                        # A run with --eval_average_candidates rebuilds its evaluation
                        # splits expanded, one row per candidate structure. Writing them
                        # out as they are would give a multi-candidate pair several score
                        # rows under one pair id, and every reader of this table -- the
                        # AUCs, the chemistry comparison, the increment regression --
                        # counts a row as a pair. Averaged here, the way training scored
                        # them.
                        frame, probs, labels = _average_candidate_rows(
                            frame, probs, labels
                        )
                    frames.append(pd.DataFrame({
                        "label": label,
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
                if verbose:
                    print(f"{family} seed{seed} epoch{epoch} : scored ({parameters} parameters)", flush=True)
            del train_dataset, valid_dataset, test_dataset, model

    if not frames:
        raise SystemExit("no checkpoints scored")
    return pd.concat(frames)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="sweep label, also the arg-file name")
    parser.add_argument("--epochs", default=DEFAULT_EPOCHS)
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument(
        "--families",
        default=None,
        help="held-out group names; default follows the label's own axis "
             "(protein families, or the lipid-class sets under --lipid_coldsplit)",
    )
    parser.add_argument("--batch", type=int, default=16, help="only affects the split's sampler")
    parser.add_argument(
        "--splits", default="valid,test",
        help="which splits to score; add 'train' to answer whether the run fits its "
             "own training set",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    families = (
        [f for f in args.families.split(",") if f]
        if args.families is not None
        else default_groups_for_label(args.label)
    )
    table = score_checkpoints(
        args.label,
        epochs=[int(e) for e in args.epochs.split(",")],
        seeds=[int(s) for s in args.seeds.split(",")],
        families=families,
        batch=args.batch,
        splits=tuple(s for s in args.splits.split(",") if s),
    )
    table.to_csv(args.out, index=False)
    print(f"wrote : {args.out}")


if __name__ == "__main__":
    main()
