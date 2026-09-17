#!/usr/bin/env python3
"""Find a held-out lipid block at a REQUESTED Tanimoto distance from training.

The four named sets in `dataloader/sampler.py` were chosen as chemistry and their
isolation measured afterwards -- 0.458, 0.553, 0.653, 0.766. This asks the question the
other way round: given a target isolation and a size the evaluation can read, which
block sits there? That is what turns "the metric falls as the chemistry gets further"
from four scattered measurements into a curve with points where they are needed.

    isolation = mean over the block's structures of the highest Tanimoto similarity to
                any structure that stays in training

exactly as `analysis/coldsplit_geometry.isolation` defines it and as every x value in
files/split_similarity_vs_metric.md is measured.

What it does, and why that is not a search over subsets. Start from one species. Sort
every other species by how similar it is to that one, and move them into the block one
at a time, most similar first. After each move, measure how similar the block still is
to what is left in training. Repeat from each of the 283 species in turn and keep the
block that came closest to the target.

Taking them in that order is what removes the combinatorics. A species that moves into
the block stops being a relative IN TRAINING for the species already there, so every
step can only lower the block's similarity to training, never raise it. The numbers
along one pass therefore run downwards, and finding the requested value means walking
the list and stopping -- no backtracking, no combinations, 283 passes instead of 2^283
subsets. One measurement is a masked max over the compact matrix (1226 x 1226 bytes,
resident), about two milliseconds, and a pass only measures the prefixes whose positive
count is already inside the requested window.

Two granularities, and the choice is not cosmetic:

    --granularity species   the block grows by species (FullIdentityOfLipid). Fine control of
                            the target, blocks that no head-group name describes, and
                            the loader cannot hold them out today: --lipid_coldsplit
                            takes class names. Use it to see what is reachable.
    --granularity class     the block grows by head-group classes. Coarser steps, but the block
                            IS a chemistry with a name, and holding it out needs nothing
                            but a new entry in LIPID_COLDSPLIT_SETS plus its name in
                            LIPID_COLDSPLIT_NAMES and in the two launchers' lists.

Reads the interaction table and the compact Tanimoto artifacts. Trains nothing and
writes nothing unless --out is given.

    python3 analysis/lipid_block_search.py --targets 0.80,0.85,0.90
    python3 analysis/lipid_block_search.py --targets 0.85 --granularity species --out blocks.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from collections import defaultdict

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

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.lipid_classes import lipid_class_series  # noqa: E402
from dataloader.tanimoto_compact import load_compact  # noqa: E402


class Units:
    """The table seen as the units a block is built from, plus their chemistry.

    A unit is a species or a head-group class, depending on the granularity. For each
    one: which rows of the table it owns, how many positives those rows carry, and which
    structures of the compact matrix its candidates point at. Everything the search does
    afterwards is boolean algebra over these, so the table is touched once.

    `family` restricts both the units AND the notion of "training" to one protein
    family's own rows, mirroring --family_only (Dataloader.py:141-166): every OTHER
    family's rows are simply absent, not merely excluded, so a unit's isolation is
    measured against what THIS family's own panel would leave in training, not against
    the whole table. `csv` keeps its ORIGINAL row index when this is set (no
    reset_index), because that index is what `compact.row_ids` is expressed in --
    candidates are matched by id, not by position, so the restriction and the lookup
    stay consistent without renumbering anything.
    """

    def __init__(self, csv, compact, granularity, family=None):
        if family:
            csv = csv[csv["ProteinDomain"].str.lower() == family.lower()]
        key = (
            csv["FullIdentityOfLipid"]
            if granularity == "species"
            else lipid_class_series(csv).str.lower()
        )
        self.names = sorted(key.dropna().unique().tolist())
        index_of = {name: index for index, name in enumerate(self.names)}
        self.count = len(self.names)
        self.structures = compact.matrix.shape[0]

        self.rows = [None] * self.count
        self.positives = np.zeros(self.count, dtype=np.int64)
        self.row_count = np.zeros(self.count, dtype=np.int64)
        self.proteins = [set() for _ in range(self.count)]
        self.classes = [defaultdict(int) for _ in range(self.count)]
        head_class = lipid_class_series(csv).str.lower()
        for name, part in csv.groupby(key):
            position = index_of[name]
            self.rows[position] = part.index.to_numpy()
            self.positives[position] = int(part["Interaction"].sum())
            self.row_count[position] = len(part)
            self.proteins[position] = set(part["LTPProtein"].unique())
            for value, size in head_class.loc[part.index].value_counts().items():
                self.classes[position][value] += int(size)

        # unit -> its structures, as a boolean row; the union of a block's rows is then
        # one OR, and the training side is its complement over the structures that
        # actually occur. Same definition as coldsplit_geometry.structures_of_rows:
        # a structure counts for a unit when any candidate of any of its rows is that
        # structure, so a structure shared by two units belongs to both -- which is what
        # makes such a block's isolation 1.0 for that structure, correctly.
        # Keyed by the ORIGINAL table row id rather than position, so a family
        # restriction (whose rows are a scattered subset of 0..len(full table)-1, not a
        # contiguous 0..len(this family)-1 range) still matches compact.row_ids
        # correctly. A candidate whose row belongs to another family, or to no unit at
        # all, is simply invisible here -- which is the whole point under a family
        # restriction: another family's chemistry is not "training", it does not exist.
        unit_of_row = {}
        for position, rows in enumerate(self.rows):
            for row in rows:
                unit_of_row[int(row)] = position
        self.structure_mask = np.zeros((self.count, self.structures), dtype=bool)
        units_of_candidates = np.array(
            [unit_of_row.get(int(row), -1) for row in compact.row_ids]
        )
        owned = units_of_candidates >= 0
        self.structure_mask[
            units_of_candidates[owned], compact.structure_index[owned]
        ] = True

        self.matrix = np.asarray(compact.matrix, dtype=np.uint8)
        # How many units own each structure. The block grows one unit at a time, and
        # this is what lets the training side be maintained incrementally: a structure
        # is still in training while at least one unit that owns it is outside the
        # block. Recomputing `structure_mask[~block].any(axis=0)` at every step instead
        # is the whole cost of the species run (283 x 1226 booleans per evaluation).
        self.owners = self.structure_mask.sum(axis=0)

        self.similarity = self._unit_similarity()

    def _unit_similarity(self):
        """Unit x unit similarity: the closest pair of structures they own.

        The closest pair rather than the average, because that is what isolation reads --
        a block is warm as soon as ONE relative of each structure stayed behind. This is
        the order the block grows in: for a starting unit, every other unit sorted by
        this number.
        """
        similarity = np.zeros((self.count, self.count), dtype=np.float32)
        for position in range(self.count):
            columns = self.matrix[self.structure_mask[position]]
            if not columns.size:
                continue
            best = columns.max(axis=0)
            for other in range(self.count):
                mask = self.structure_mask[other]
                similarity[position, other] = best[mask].max() / 255.0 if mask.any() else 0.0
        return similarity

    def isolation(self, block):
        """Mean over the block's structures of the best similarity to a training one."""
        held = self.structure_mask[block].any(axis=0)
        owned = self.structure_mask[block].sum(axis=0)
        return self.isolation_from_masks(held, self.owners - owned > 0)

    def isolation_from_masks(self, held, kept):
        """The same number from masks a caller already maintains incrementally."""
        if not held.any() or not kept.any():
            return float("nan")
        return float(
            (self.matrix[np.ix_(held, kept)].max(axis=1).astype(np.float32) / 255.0).mean()
        )


def search(units, target, minimum_positives, maximum_positives, seeds):
    """The best block at `target`, started from every unit in turn, within the size window.

    One pass per starting unit: sort the others by similarity to it, move them into the
    block one at a time most-similar-first, and measure isolation only while the block's
    positive count is inside the window. Every candidate returned therefore satisfies
    the size constraint by construction, and the one that wins is the closest to the
    requested isolation.
    """
    best = []
    evaluations = 0
    for seed in seeds:
        order = np.argsort(-units.similarity[seed])
        order = np.concatenate([[seed], order[order != seed]])
        block = np.zeros(units.count, dtype=bool)
        # Maintained as the block grows instead of rebuilt each step: `held` gains the new
        # unit's structures, and a structure leaves training only when the LAST unit
        # owning it has joined the block.
        held = np.zeros(units.structures, dtype=bool)
        owned = np.zeros(units.structures, dtype=np.int64)
        positives = 0
        for position in order:
            block[position] = True
            mine = units.structure_mask[position]
            held |= mine
            owned += mine
            positives += int(units.positives[position])
            if positives < minimum_positives:
                continue
            if positives > maximum_positives:
                break
            evaluations += 1
            value = units.isolation_from_masks(held, units.owners - owned > 0)
            best.append((abs(value - target), value, block.copy(), positives))
    best.sort(key=lambda item: item[0])
    return best, evaluations


def search_groups(units, count, minimum_positives, maximum_positives, target=None):
    """`count` disjoint blocks, each as cold as the ones already taken allow.

    The four named sets are already a design like this -- four blocks that do not
    overlap, each held out by its own runs -- so asking for k of them is asking what the
    table supports when several cold folds have to coexist. The blocks are taken one at
    a time, coldest first, and each pass may only grow through units no earlier block
    claimed.

    Taking one block does not change what an earlier block measures: a block is held out
    BY ITS OWN RUNS, and the other blocks stay in training there. What it does change is
    what is left to build the next block from, which is the whole difficulty -- the
    second group cannot reuse the first group's relatives, and by the fifth there may be
    no isolated chemistry left at all.
    """
    taken = np.zeros(units.count, dtype=bool)
    groups = []
    for _ in range(count):
        best = None
        for seed in range(units.count):
            if taken[seed]:
                continue
            order = np.argsort(-units.similarity[seed])
            order = np.concatenate([[seed], order[order != seed]])
            order = order[~taken[order]]
            block = np.zeros(units.count, dtype=bool)
            held = np.zeros(units.structures, dtype=bool)
            owned = np.zeros(units.structures, dtype=np.int64)
            positives = 0
            for position in order:
                block[position] = True
                mine = units.structure_mask[position]
                held |= mine
                owned += mine
                positives += int(units.positives[position])
                if positives < minimum_positives:
                    continue
                if positives > maximum_positives:
                    break
                value = units.isolation_from_masks(held, units.owners - owned > 0)
                score = abs(value - target) if target is not None else value
                if best is None or score < best[0]:
                    best = (score, value, block.copy())
        if best is None:
            break
        _, value, block = best
        groups.append((value, block))
        taken |= block
    return groups


def isolation_with_all_groups_out(units, groups, index):
    """One group's isolation when EVERY group is out of training at the same time.

    The other reading of "k groups at once": instead of k separate runs, one training
    set with all k blocks removed, each block scored on its own. Removing more from
    training can only lower a structure's best match there, so this number is always at
    or below the one a single-block run measures -- it is the colder, more expensive
    design, and the gap between the two says how much of each block's warmth came from
    its neighbours in the other groups.
    """
    everything_out = np.zeros(units.count, dtype=bool)
    for _, block in groups:
        everything_out |= block
    block = groups[index][1]
    held = units.structure_mask[block].any(axis=0)
    kept = units.structure_mask[~everything_out].any(axis=0)
    return units.isolation_from_masks(held, kept)


def describe(units, block):
    members = np.flatnonzero(block)
    composition = defaultdict(int)
    proteins = set()
    for position in members:
        for name, size in units.classes[position].items():
            composition[name] += size
        proteins |= units.proteins[position]
    total = sum(composition.values())
    top = sorted(composition.items(), key=lambda item: -item[1])
    return {
        "units": [units.names[position] for position in members],
        "rows": int(units.row_count[members].sum()),
        "positives": int(units.positives[members].sum()),
        "proteins": len(proteins),
        "composition": " ".join(
            f"{name}({100 * size / max(total, 1):.0f}%)" for name, size in top[:4]
        )
        + (f" +{len(top) - 4}" if len(top) > 4 else ""),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default=os.path.join(PROJECT_ROOT, "data"))
    parser.add_argument(
        "--targets",
        default="0.80,0.85,0.90",
        help="comma-separated isolation values to find a block for",
    )
    parser.add_argument(
        "--granularity", default="class", choices=("class", "species")
    )
    parser.add_argument(
        "--family",
        default="",
        help=(
            "restrict both the candidate chemistry and the notion of training to one "
            "protein family's own rows (case-insensitive ProteinDomain match), for a "
            "--family_only + --lipid_isolation ladder: isolation is then measured "
            "against what THAT family's own panel leaves in training, not the whole "
            "table's"
        ),
    )
    parser.add_argument(
        "--min_positives",
        type=int,
        default=40,
        help=(
            "the block is halved into validation and test, so this is twice the "
            "positives each half gets (COLDSPLIT_MINIMUM_TEST_POSITIVES is 20)"
        ),
    )
    parser.add_argument("--max_positives", type=int, default=140)
    parser.add_argument(
        "--candidates", type=int, default=3, help="blocks to print per target"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=0,
        help="how many seed units to try, 0 for all of them",
    )
    parser.add_argument("--out", default="", help="write the chosen blocks as JSON")
    parser.add_argument(
        "--groups",
        default="",
        help=(
            "comma-separated group counts, e.g. 3,4,5: instead of one block per target, "
            "find that many DISJOINT blocks and report how isolated each of them came "
            "out. Reported twice -- as each block's own runs would see it (the other "
            "blocks stay in training) and with every block out of training at once"
        ),
    )
    parser.add_argument(
        "--emit_module",
        default="",
        help=(
            "write the chosen blocks as dataloader/lipid_isolation_blocks.py, the "
            "registry --lipid_isolation reads. Split definitions live in code in this "
            "project (LIPID_COLDSPLIT_SETS is a dict in dataloader/sampler.py), so that "
            "a run's block is reviewable in a diff and cannot change under a finished "
            "experiment -- a file regenerated on a whim would silently redefine what "
            "past runs held out"
        ),
    )
    arguments = parser.parse_args()

    data_dir = arguments.data_dir.rstrip(os.sep) + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    compact = load_compact(arguments.data_dir)
    if compact is None or len(np.unique(compact.row_ids)) != len(csv):
        raise SystemExit(
            "the compact Tanimoto artifacts are missing or cover a different table; "
            "rebuild them with preprocessing/build_tanimoto_compact.py"
        )

    started = time.time()
    units = Units(csv, compact, arguments.granularity, family=arguments.family or None)
    prepared = time.time() - started
    scope = f" within {arguments.family}" if arguments.family else ""
    print(
        f"{units.count} {arguments.granularity} units over {units.structures} "
        f"structures{scope}, prepared in {prepared:.1f}s\n"
    )

    seeds = range(units.count)
    if arguments.seeds:
        seeds = np.random.default_rng(0).permutation(units.count)[: arguments.seeds]

    if arguments.groups:
        # A mode, not an extra report: --groups asks what the table supports when
        # several cold folds have to coexist, and the per-target search answers a
        # different question on the same data.
        for count in [int(value) for value in arguments.groups.split(",") if value]:
            started = time.time()
            groups = search_groups(
                units, count, arguments.min_positives, arguments.max_positives
            )
            elapsed = time.time() - started
            print(f"=== {count} disjoint groups (found in {elapsed:.1f}s) ===")
            if len(groups) < count:
                print(
                    f"  only {len(groups)} groups fit the size window; the table has no "
                    "chemistry left for the rest"
                )
            print(
                f"{'group':>5s} {'alone':>7s} {'all out':>7s} {'pos':>4s} {'rows':>5s} "
                f"{'units':>5s} {'prot':>4s}  head-group composition"
            )
            for index, (value, block) in enumerate(groups):
                report = describe(units, block)
                together = isolation_with_all_groups_out(units, groups, index)
                print(
                    f"{index + 1:5d} {value:7.3f} {together:7.3f} "
                    f"{report['positives']:4d} {report['rows']:5d} "
                    f"{len(report['units']):5d} {report['proteins']:4d}  "
                    f"{report['composition']}"
                )
            if groups:
                alone = [value for value, _ in groups]
                together = [
                    isolation_with_all_groups_out(units, groups, index)
                    for index in range(len(groups))
                ]
                print(
                    f"      worst {max(alone):.3f} / {max(together):.3f}, "
                    f"mean {sum(alone) / len(alone):.3f} / "
                    f"{sum(together) / len(together):.3f}"
                )
            print()
        return

    chosen = {}
    for target in [float(value) for value in arguments.targets.split(",") if value]:
        started = time.time()
        best, evaluations = search(
            units, target, arguments.min_positives, arguments.max_positives, seeds
        )
        elapsed = time.time() - started
        print(
            f"=== target isolation {target:.3f} "
            f"({evaluations} blocks evaluated in {elapsed:.1f}s) ==="
        )
        if not best:
            print("  no block satisfies the size window at all\n")
            continue
        print(
            f"{'isolation':>9s} {'pos':>4s} {'rows':>5s} {'units':>5s} {'prot':>4s}  "
            "head-group composition"
        )
        seen = set()
        printed = 0
        for _, value, block, _ in best:
            key = tuple(np.flatnonzero(block))
            if key in seen:
                continue
            seen.add(key)
            report = describe(units, block)
            print(
                f"{value:9.3f} {report['positives']:4d} {report['rows']:5d} "
                f"{len(report['units']):5d} {report['proteins']:4d}  "
                f"{report['composition']}"
            )
            if printed == 0:
                # "__" rather than ":" -- the key becomes a directory-name component
                # (new_train.py's excluded_set_name), and a colon is legal on Linux but
                # an unnecessary risk through shell quoting, OAR job names and any
                # regex elsewhere that parses that path assuming no punctuation beyond
                # "_"/"-". FAMILY names never contain "__" themselves.
                key = (
                    f"{arguments.family.lower()}__{target:.2f}"
                    if arguments.family
                    else f"{target:.2f}"
                )
                chosen[key] = {"isolation": value, **report}
            printed += 1
            if printed >= arguments.candidates:
                break
        print()

    if arguments.out:
        with open(arguments.out, "w") as handle:
            json.dump(chosen, handle, indent=2, ensure_ascii=False)
        print(f"wrote {arguments.out}")

    if arguments.emit_module:
        emit_module(arguments.emit_module, chosen, arguments, csv)
        print(f"wrote {arguments.emit_module}")


def load_existing_module(path):
    """The registry's own two dicts, if `path` already holds one -- else empty.

    --emit_module MERGES rather than overwrites: this file is regenerated by different
    invocations for different targets and different --family scopes (bare keys "0.85"
    for a global block, "cral-trio:0.85" for a family-scoped one), and each invocation
    only knows about the keys it was just asked to find. Clobbering the file on every
    call would silently delete whatever an earlier call put there -- including blocks
    that finished runs already reference.
    """
    if not os.path.exists(path):
        return {}, {}
    namespace = {}
    with open(path) as handle:
        exec(compile(handle.read(), path, "exec"), namespace)  # noqa: S102
    return (
        dict(namespace.get("LIPID_ISOLATION_BLOCKS", {})),
        dict(namespace.get("BLOCK_GEOMETRY", {})),
    )


def emit_module(path, chosen, arguments, csv):
    """Write the registry --lipid_isolation reads, merging with what is already there.

    Merges rather than overwrites: this file is regenerated by different invocations
    for different targets and different --family scopes (bare keys like "0.85" for a
    global block, "cral-trio:0.85" for one scoped to a family), and each invocation only
    knows about the keys it was just asked to find. Clobbering the file on every call
    would silently delete whatever an earlier call put there -- including blocks that
    finished runs already reference.
    """
    blocks, geometry = load_existing_module(path)
    overwritten = sorted(set(blocks) & set(chosen))
    if overwritten:
        print(
            f"  redefining {len(overwritten)} existing key(s) in {path}: "
            f"{', '.join(overwritten)}"
        )
    for key, report in chosen.items():
        blocks[key] = tuple(report["units"])
        geometry[key] = (
            report["isolation"],
            report["positives"],
            report["rows"],
            len(report["units"]),
            report["proteins"],
        )

    command = (
        "python3 analysis/lipid_block_search.py "
        f"--granularity {arguments.granularity} --targets {arguments.targets} "
        f"--min_positives {arguments.min_positives} "
        f"--max_positives {arguments.max_positives}"
        + (f" --family {arguments.family}" if arguments.family else "")
        + f" --emit_module {path}"
    )
    lines = [
        '"""Held-out lipid blocks at requested distances from training -- generated.',
        "",
        "Written by analysis/lipid_block_search.py; do not edit by hand. Each entry is a",
        "set of lipid species (FullIdentityOfLipid) whose rows leave training for every",
        "protein, exactly as a --lipid_coldsplit class set does, chosen so that the",
        "block's isolation -- the mean over its structures of the best Tanimoto",
        "similarity to a structure still in training -- lands on the requested value.",
        "",
        "A bare key (0.85) is a global block, chosen against the whole table: any",
        "protein may train on the chemistry left behind. A <family>__<value> key",
        "(cral-trio__0.85) is scoped to one --family_only run: chosen so that",
        "training on THAT family's own remaining rows alone reaches the requested",
        "isolation, which a global block does not promise once every other family's",
        "chemistry is unavailable.",
        "",
        "The key is the REQUESTED isolation and the value --lipid_isolation takes;",
        "BLOCK_GEOMETRY below records what each block actually measures, which is what",
        "belongs on a plot -- and a run measures it again for itself anyway",
        "(analysis/split_similarity_vs_metric.py rebuilds every run's own split).",
        "",
        "This file accumulates across separate `--emit_module` calls (see",
        "load_existing_module): each call below regenerated or added the keys it names,",
        "not necessarily every key present.",
        "",
        f"    {command}",
        '"""',
        "",
        "LIPID_ISOLATION_BLOCKS = {",
    ]
    for key in sorted(blocks):
        lines.append(f'    "{key}": (')
        for name in blocks[key]:
            lines.append(f'        "{name}",')
        lines.append("    ),")
    lines.append("}")
    lines.append("")
    lines.append("# What each block measures on the table it was chosen on:")
    lines.append("# key -> (isolation, positives, rows, species, proteins)")
    lines.append("BLOCK_GEOMETRY = {")
    for key in sorted(geometry):
        isolation_value, positives, rows, species, proteins = geometry[key]
        lines.append(
            f'    "{key}": ({isolation_value:.3f}, {positives}, {rows}, {species}, '
            f"{proteins}),"
        )
    lines.append("}")
    lines.append("")
    scope_csv = (
        csv[csv["ProteinDomain"].str.lower() == arguments.family.lower()]
        if arguments.family
        else csv
    )
    scope = f"the {arguments.family} family's own rows" if arguments.family else "the whole table"
    lines.append(
        f"# This call's own chosen keys against {scope}: {len(scope_csv)} rows, "
        f"{int(scope_csv['Interaction'].sum())} positives."
    )
    lines.append("")
    with open(path, "w") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    main()
