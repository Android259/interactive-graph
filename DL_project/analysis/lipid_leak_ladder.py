#!/usr/bin/env python3
"""Intermediate splits between the lipid cold split and the random one, measured.

The two ends of the similarity axis differ in one thing that can be dialled: how much
of the evaluated chemistry training has already seen. At the cold end nothing
(`test_seen_lipid_share` 0.000, isolation 0.45-0.77); at the random end everything (share
1.000, isolation exactly 1.000, because a structure's best match in training is itself).
Everything in between is a partial leak, and this script measures the three ways of
building one that the table actually supports:

  A  leave-one-class-in  -- hold out a named set minus one of its classes, so the class
                            that stays is the block's closest relative in training. Moves
                            isolation in whatever jump that class's chemistry happens to
                            be worth, and changes the block (its own rows leave with it).
                            No leak at all in the strict sense: the evaluated species are
                            still unseen, only their relatives are not.
  B  species leak        -- a fraction of the block's SPECIES is returned to training
                            whole; the block keeps the rest. Same as A in kind (relatives,
                            not the molecule itself), finer in step, and it shrinks the
                            block as it goes.
  C  pair leak           -- the evaluated rows are FIXED first, and a fraction of their
                            species is made visible in training through that species'
                            OTHER rows (same molecule, different protein). The block is
                            byte-identical along the whole ladder -- same rows, same
                            positives, same proteins -- and only training changes. This
                            is the one that interpolates the cold split to the random
                            one, because the quantity it moves is exactly the one those
                            two differ in.

Reads the interaction table and the compact Tanimoto artifacts. Trains nothing, writes
nothing outside --output_dir, and proposes no run by itself: it says which blocks are
worth running and what each would sit at on the x axis.

    python3 analysis/lipid_leak_ladder.py
    python3 analysis/lipid_leak_ladder.py --sets anionic,choline --shares 0,0.25,0.5,0.75,1
"""

from __future__ import annotations

import argparse
import os
import sys
import types

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:  # pragma: no cover - depends on the machine, not on the code path
    import torch  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _torch = types.ModuleType("torch")
    _torch.utils = types.ModuleType("torch.utils")
    _torch.utils.data = types.ModuleType("torch.utils.data")
    _torch.utils.data.Sampler = object
    sys.modules.update(
        {
            "torch": _torch,
            "torch.utils": _torch.utils,
            "torch.utils.data": _torch.utils.data,
        }
    )

import numpy as np  # noqa: E402
import pandas  # noqa: E402

from analysis.coldsplit_geometry import isolation  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.sampler import LIPID_COLDSPLIT_SETS  # noqa: E402
from dataloader.tanimoto_compact import load_compact  # noqa: E402

MINIMUM_BLOCK_POSITIVES = 20


def class_inventory(csv, classes, compact):
    """Every head-group class as a candidate block of its own."""
    print("head-group classes: what each is worth as a held-out block")
    print(
        f"{'class':34s} {'rows':>6s} {'pos':>5s} {'species':>7s} {'proteins':>8s} "
        f"{'rows/species':>12s} {'isolation':>9s}"
    )
    rows = []
    for name, part in csv.groupby(classes):
        block = part.index.to_numpy()
        train = csv.index.difference(part.index).to_numpy()
        positives = int(part["Interaction"].sum())
        species = part["FullIdentityOfLipid"].nunique()
        value = isolation(compact, block, train)
        rows.append((name, len(part), positives, species, value))
        print(
            f"{str(name)[:34]:34s} {len(part):6d} {positives:5d} {species:7d} "
            f"{part['LTPProtein'].nunique():8d} {len(part) / max(species, 1):12.1f} "
            f"{value:9.3f}"
        )
    print()
    return rows


def leave_one_class_in(csv, classes, compact, set_names):
    """Family A: hold the set out minus one class, and see where the block lands.

    The class that stays in training is the block's nearest chemistry, so this is the
    coarsest of the three knobs -- one class is one jump, and how big the jump is
    depends on which class it is, not on anything that can be dialled.
    """
    print("A. leave-one-class-in: hold out SET minus CLASS, keep CLASS in training")
    print(
        f"{'set':16s} {'class left in training':34s} {'block pos':>9s} "
        f"{'train pos +':>11s} {'isolation':>9s} {'delta':>7s}"
    )
    for set_name in set_names:
        members = [name.lower() for name in LIPID_COLDSPLIT_SETS[set_name]]
        held = classes.isin(members)
        base = isolation(
            compact, csv.index[held].to_numpy(), csv.index[~held].to_numpy()
        )
        base_positives = int(csv.loc[held, "Interaction"].sum())
        print(
            f"{set_name:16s} {'-- (whole set held out)':34s} {base_positives:9d} "
            f"{0:11d} {base:9.3f} {0.0:7.3f}"
        )
        for member in members:
            keep = classes == member
            if not keep.any():
                continue
            block = held & ~keep
            positives = int(csv.loc[block, "Interaction"].sum())
            if not block.any():
                continue
            value = isolation(
                compact, csv.index[block].to_numpy(), csv.index[~block].to_numpy()
            )
            note = "" if positives >= MINIMUM_BLOCK_POSITIVES else "  [too few positives]"
            print(
                f"{'':16s} {member[:34]:34s} {positives:9d} "
                f"{int(csv.loc[keep, 'Interaction'].sum()):11d} {value:9.3f} "
                f"{value - base:+7.3f}{note}"
            )
        print()


def class_ladder(csv, classes, compact, set_names):
    """Family A, continued: keep classes in training one after another, greedily.

    Answers "one class back, or several": at each step the class whose return raises the
    block's isolation the most is kept, so this is the FASTEST a set can be walked to the
    warm end by class-sized steps. What it shows is how quickly the steps stop paying --
    isolation is a mean of MAXIMA, so once the block's nearest relative is in training,
    the next class barely moves it while the block keeps shrinking.
    """
    print("A2. keep classes in training greedily, nearest relative first")
    print(
        f"{'set':16s} {'kept':>4s} {'last class kept in training':34s} "
        f"{'block pos':>9s} {'isolation':>9s} {'delta':>7s}"
    )
    for set_name in set_names:
        members = [name.lower() for name in LIPID_COLDSPLIT_SETS[set_name]]
        present = [member for member in members if (classes == member).any()]
        kept = []
        held = classes.isin(present)
        current = isolation(
            compact, csv.index[held].to_numpy(), csv.index[~held].to_numpy()
        )
        print(
            f"{set_name:16s} {0:4d} {'-- (whole set held out)':34s} "
            f"{int(csv.loc[held, 'Interaction'].sum()):9d} {current:9.3f} {0.0:+7.3f}"
        )
        while len(kept) < len(present) - 1:
            best = None
            for member in present:
                if member in kept:
                    continue
                block = classes.isin([name for name in present if name not in kept + [member]])
                if not block.any():
                    continue
                value = isolation(
                    compact, csv.index[block].to_numpy(), csv.index[~block].to_numpy()
                )
                if best is None or value > best[1]:
                    best = (member, value, block)
            if best is None:
                break
            member, value, block = best
            kept.append(member)
            positives = int(csv.loc[block, "Interaction"].sum())
            print(
                f"{'':16s} {len(kept):4d} {member[:34]:34s} {positives:9d} "
                f"{value:9.3f} {value - current:+7.3f}"
                + ("" if positives >= MINIMUM_BLOCK_POSITIVES else "  [too few positives]")
            )
            current = value
        print()


def species_leak(csv, classes, compact, set_names, shares, seed):
    """Family B: return a share of the set's species to training, block keeps the rest."""
    print("B. species leak: a share of the set's SPECIES goes back to training whole")
    print(
        f"{'set':16s} {'share':>5s} {'block rows':>10s} {'block pos':>9s} "
        f"{'isolation':>9s} {'seen share':>10s}"
    )
    generator = np.random.default_rng(seed)
    for set_name in set_names:
        members = [name.lower() for name in LIPID_COLDSPLIT_SETS[set_name]]
        held = classes.isin(members)
        species = sorted(csv.loc[held, "FullIdentityOfLipid"].unique())
        order = generator.permutation(len(species))
        for share in shares:
            leaked = {species[index] for index in order[: int(round(share * len(species)))]}
            block = held & ~csv["FullIdentityOfLipid"].isin(leaked)
            if not block.any():
                continue
            block_rows = csv.index[block].to_numpy()
            train_rows = csv.index[~block].to_numpy()
            seen = csv.loc[block, "FullIdentityOfLipid"].isin(
                set(csv.loc[~block, "FullIdentityOfLipid"].unique())
            )
            print(
                f"{set_name:16s} {share:5.2f} {int(block.sum()):10d} "
                f"{int(csv.loc[block, 'Interaction'].sum()):9d} "
                f"{isolation(compact, block_rows, train_rows):9.3f} "
                f"{float(seen.mean()):10.3f}"
            )
        print()


def pair_leak(csv, classes, compact, set_names, shares, seed, block_share):
    """Family C: fixed evaluated block, a share of its species made visible in training.

    The block is drawn ONCE per set -- `block_share` of each species' rows -- and every
    rung of the ladder scores exactly those rows. What moves is the reservoir: the
    species' other rows are either dropped (cold, as the split does today) or handed to
    training (leaked, which is the condition the random split puts every row in). So the
    block's size, positive count, protein coverage and chemistry are constant along the
    ladder by construction, and the only thing that varies is the leak.
    """
    print(
        f"C. pair leak: block fixed at {block_share:.0%} of each species' rows, "
        "a share of its species made visible in training through their other rows"
    )
    print(
        f"{'set':16s} {'leak':>5s} {'block rows':>10s} {'block pos':>9s} "
        f"{'proteins':>8s} {'train pos':>9s} {'isolation':>9s} {'seen share':>10s}"
    )
    for set_name in set_names:
        members = [name.lower() for name in LIPID_COLDSPLIT_SETS[set_name]]
        held = csv.index[classes.isin(members)]
        if len(held) == 0:
            continue
        # One draw per species, so every species is represented in the block in
        # proportion to how many proteins it was measured against.
        generator = np.random.default_rng(seed)
        block_index = []
        for _, rows in csv.loc[held].groupby("FullIdentityOfLipid").groups.items():
            rows = np.asarray(sorted(rows))
            count = max(1, int(round(block_share * len(rows))))
            block_index.extend(
                rows[generator.permutation(len(rows))[:count]].tolist()
            )
        block_rows = np.asarray(sorted(block_index))
        reservoir = np.asarray(sorted(set(held.tolist()) - set(block_index)))
        outside = csv.index.difference(held).to_numpy()

        block_species = sorted(csv.loc[block_rows, "FullIdentityOfLipid"].unique())
        order = np.random.default_rng(seed + 1).permutation(len(block_species))
        for share in shares:
            leaked_species = {
                block_species[index]
                for index in order[: int(round(share * len(block_species)))]
            }
            leaked_rows = (
                reservoir[
                    csv.loc[reservoir, "FullIdentityOfLipid"].isin(leaked_species).to_numpy()
                ]
                if len(reservoir)
                else np.asarray([], dtype=int)
            )
            train_rows = np.concatenate([outside, leaked_rows]).astype(int)
            seen = csv.loc[block_rows, "FullIdentityOfLipid"].isin(
                set(csv.loc[train_rows, "FullIdentityOfLipid"].unique())
            )
            print(
                f"{set_name:16s} {share:5.2f} {len(block_rows):10d} "
                f"{int(csv.loc[block_rows, 'Interaction'].sum()):9d} "
                f"{csv.loc[block_rows, 'LTPProtein'].nunique():8d} "
                f"{int(csv.loc[train_rows, 'Interaction'].sum()):9d} "
                f"{isolation(compact, block_rows, train_rows):9.3f} "
                f"{float(seen.mean()):10.3f}"
            )
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default=os.path.join(PROJECT_ROOT, "data"))
    parser.add_argument("--sets", default=",".join(LIPID_COLDSPLIT_SETS))
    parser.add_argument("--shares", default="0,0.25,0.5,0.75,1.0")
    parser.add_argument("--block_share", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--skip_inventory", action="store_true")
    arguments = parser.parse_args()

    data_dir = arguments.data_dir.rstrip(os.sep) + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    compact = load_compact(arguments.data_dir)
    if compact is None:
        raise SystemExit(
            "compact Tanimoto artifacts are missing; build them with "
            "preprocessing/build_tanimoto_compact.py"
        )
    if len(np.unique(compact.row_ids)) != len(csv):
        raise SystemExit(
            "the compact Tanimoto artifacts cover "
            f"{len(np.unique(compact.row_ids))} rows against {len(csv)} in the table; "
            "rebuild them with preprocessing/build_tanimoto_compact.py"
        )

    classes = lipid_class_series(csv).str.lower()
    set_names = [name.strip() for name in arguments.sets.split(",") if name.strip()]
    shares = [float(value) for value in arguments.shares.split(",") if value]

    print(
        f"table: {len(csv)} rows, {int(csv['Interaction'].sum())} positives, "
        f"{csv['LTPProtein'].nunique()} proteins, "
        f"{csv['FullIdentityOfLipid'].nunique()} species, "
        f"{classes.nunique()} head-group classes\n"
    )
    if not arguments.skip_inventory:
        class_inventory(csv, classes, compact)
    leave_one_class_in(csv, classes, compact, set_names)
    class_ladder(csv, classes, compact, set_names)
    species_leak(csv, classes, compact, set_names, shares, arguments.seed)
    pair_leak(
        csv, classes, compact, set_names, shares, arguments.seed, arguments.block_share
    )


if __name__ == "__main__":
    main()
