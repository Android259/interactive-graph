#!/usr/bin/env python3
"""Greedy forward-selection search over protein/lipid descriptor combinations for the
Figure-3 lipid-subclass cold split (scripts/run_cron.py's --excluded_lipid_groups
run, same 9 groups as cron_test_metrics/cron_fig3_lipidgroups.txt), calling analysis/
kronrls_baseline.py's own evaluate_block directly in-process -- not a subprocess per
combination, which would re-pay loading the interaction table and recomputing raw
protein/lipid features on every one of the several hundred combinations this
evaluates.

NOT a full grid: dataloader/pair_descriptors.py has 20 protein x 22 lipid descriptor
names; every subset with >=2 protein and >=1 lipid names is ~4.4 trillion
combinations, computationally impossible regardless of optimization. Joint greedy
instead:

SEED: every protein PAIR (C(20,2) = 190, the >=2-protein floor) against the lipid
side at PINNED_LIPID_DESCRIPTOR alone -- the smallest combination the constraints
allow, nothing hand-picked going in.

THEN one JOINT greedy loop over both sides at once: each step evaluates every
remaining candidate from EITHER pool (add a protein descriptor, or add a lipid one)
and takes whichever single addition improves mean test_BA most across every (group,
seed), stopping when none does. Not two separate phases -- a lipid descriptor can win
a step before the protein side is done and vice versa, so neither side is forced to
finish first.

Worst case ~970 evaluations (190 seed pairs + 39+38+...+1 joint steps), ~27 CPU-
seconds each at 9 groups x 10 seeds -- roughly 7 CPU-hours, so ~1h45 on 4 cores, ~55
min on 8. A FULL grid over both sides (with the pinned lipid descriptor) would be
2.2e12 combinations, about 1e6 CPU-years; that is why this is greedy.

Selection criterion is test_BA (test_F1 tracked alongside, per the original spec --
no --lambda_grid, so merge_valid_test makes valid and test one block, here and in the
logged CSV too, same as scripts/run_cron.py). AUC_within_protein (per_protein_auc) is
also computed and logged on every row, purely as an extra reference column -- it
never decides a step. Caveat worth keeping in mind reading the log: test_BA/test_F1
both come from a threshold (best_threshold_for_metric) fit on the same pool it is
then scored on, so the number is "the best cutoff achievable in hindsight on this
known block", not a frozen cutoff that would carry over to a genuinely new, unlabeled
lipid -- AUC_within_protein is the one column here that has no such threshold in it.

Every combination evaluated is appended to a CSV log as it runs; only
the single best combination (protein set, lipid set, test_BA, test_F1) prints at
the end.

    python3 analysis/search_lipidgroups_descriptors.py
    python3 analysis/search_lipidgroups_descriptors.py --processes 8 \\
        --log cron_test_metrics/descriptor_search.csv
"""
from __future__ import annotations

import argparse
import csv
import functools
import multiprocessing as mp
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.kronrls_baseline import build_parser, evaluate_block, load_table  # noqa: E402
from dataloader.pair_descriptors import (  # noqa: E402
    LIPID_DESCRIPTOR_NAMES,
    PROTEIN_DESCRIPTOR_NAMES as _NETWORK_PROTEIN_DESCRIPTOR_NAMES,
)
import training.pair_baseline_common as pbc  # noqa: E402

# The pool this search picks protein descriptors FROM -- deliberately wider than
# dataloader.pair_descriptors.PROTEIN_DESCRIPTOR_NAMES, and deliberately a separate
# name rather than an extension of it: that list's LENGTH is ModelConfig.
# pocket_descriptor_count and its POSITIONS are indexed by bare integer literals in
# architecture/pair_descriptor_head.py, so appending to it would silently break the
# network. What a feature search may choose from is a search concern, not the
# network's own catalog.
#
# Added over that list:
#   POCKET_CHEMISTRY_NAMES -- basic/acidic/polar/hbond-donor/hbond-acceptor share,
#     each split core vs rim. training.pair_baseline_common.protein_pocket_features
#     has always computed these (they are part of pocket23) but they were never in
#     PROTEIN_DESCRIPTOR_NAMES, so no feature search had ever been able to pick one.
#     basic_share_rim is the direct measure of the mechanism the literature calls
#     primary for anionic head-group recognition (Lys/Arg at the pocket mouth), and
#     five of the nine Figure-3 groups here are anionic (PG, PA, PS, PI, PGP). The
#     core/rim split matches the source paper's own two-channel picture: the mouth
#     recognises the head group, the interior packs the tail.
#   POCKET_CAVITY_NAMES -- free cavity volume and packing density, see
#     pair_baseline_common._cavity_values.
# Full reasoning and sources: files/binding_determinants_literature_and_feature_proposals.md
PROTEIN_DESCRIPTOR_NAMES = (
    tuple(_NETWORK_PROTEIN_DESCRIPTOR_NAMES)
    + tuple(pbc.POCKET_CHEMISTRY_NAMES)
    + tuple(pbc.POCKET_CAVITY_NAMES)
)

# Same 9 Figure-3 groups as cron_test_metrics/cron_fig3_lipidgroups.txt's own
# --excluded_lipid_groups=PC,PG,FA,PE,Cer+CerP+HexCer+Hex2Cer+SHexCer+SM,PI,
# LPC+LPE+LPG,PA,PS+PGP+DAG+TAG -- kept in code, not re-parsed from a CLI string,
# so a worker process never needs argparse to reconstruct them.
EXCLUDED_LIPID_GROUP_SPECS = (
    ("PC", ("PC",)),
    ("PG", ("PG",)),
    ("FA", ("FA",)),
    ("PE", ("PE",)),
    ("Cer+CerP+HexCer+Hex2Cer+SHexCer+SM",
     ("Cer", "CerP", "HexCer", "Hex2Cer", "SHexCer", "SM")),
    ("PI", ("PI",)),
    ("LPC+LPE+LPG", ("LPC", "LPE", "LPG")),
    ("PA", ("PA",)),
    ("PS+PGP+DAG+TAG", ("PS", "PGP", "DAG", "TAG")),
)
# The ONE descriptor pinned into every combination (the user's own constraint). It is
# also the lipid side's whole starting point: every other lipid descriptor has to be
# earned by a greedy step, exactly like every protein one past the seed pair.
PINNED_LIPID_DESCRIPTOR = "experimental_lipid_volume"
SEEDS = tuple(range(10))

_TABLE = None
_GROUPS = None


def _base_args() -> argparse.Namespace:
    """kronrls_baseline's own parser, all defaults, just the kernel *kind* pinned to
    the descriptor-subset branches this search drives by name -- everything else
    (share, eval_negatives_per_positive, no --lambda_grid so merge_valid_test's
    valid=test merge applies here exactly as in scripts/run_cron.py) stays whatever
    build_parser() already defaults to. threshold_metric/select_metric are left at
    their defaults too -- irrelevant here since nothing threshold-shaped drives this
    search's choices (see module docstring).
    """
    args = build_parser().parse_args([])
    args.protein_kernel = "pocket_subset"
    args.protein_kernel_type = "rbf"
    args.lipid_kernel = "explicit_subset"
    args.lipid_kernel_type = "rbf"
    return args


def _patch_protein_pocket_features() -> None:
    """protein_pocket_features re-reads all 35 proteins' graph files from disk on
    EVERY call -- no cache of its own, unlike the lipid side (explicit_lipid_features/
    _lipid_descriptor_table are already memoized). This search calls it hundreds of
    times over the exact same 35-protein list; memoize it here so only the first call
    per worker process pays for the disk reads.
    """
    original = pbc.protein_pocket_features

    @functools.lru_cache(maxsize=None)
    def cached(proteins_tuple, graphs_str):
        return original(list(proteins_tuple), graphs_str)

    def patched(proteins, graphs=pbc.DEFAULT_GRAPHS):
        return cached(tuple(proteins), str(graphs))

    pbc.protein_pocket_features = patched


def evaluate_combo(
    protein_names: tuple[str, ...], lipid_names: tuple[str, ...]
) -> tuple[float, float, float]:
    """(mean test_BA, mean test_F1, mean AUC_within_protein) across every (group,
    seed) for one descriptor combination -- evaluate_block directly (not build_
    report's own one-shot kernel_cache={}), with a kernel_cache LOCAL to this combo:
    the protein kernel is identical across all 9 groups x 10 seeds of one combo
    (--lipid_coldsplit style, no protein ever excluded), so this cache turns 90
    kernel builds into 1 for the protein side alone. Raw feature tables (the actually
    expensive part) are cached at module level (see _patch_protein_pocket_features /
    pbc's own lipid caches), not here, so they survive across DIFFERENT combos too.

    test_BA is what joint_greedy_search compares on (the spec:
    "критерий - test BA и test F1"); AUC_within_protein rides along in the return
    value purely so it lands in the log too, see module docstring's caveat.
    """
    args = _base_args()
    args.protein_descriptor_names = list(protein_names)
    args.lipid_descriptor_names = list(lipid_names)
    args.excluded_lipids_species = _GROUPS
    kernel_cache: dict = {}
    rows = [
        evaluate_block(_TABLE, family, seed, args, kernel_cache=kernel_cache)
        for family in _GROUPS for seed in SEEDS
    ]
    report = pd.DataFrame(rows)
    return (
        float(report["test_ba"].mean()),
        float(report["test_f1"].mean()),
        float(report["per_protein_auc"].mean()),
    )


def _worker_init() -> None:
    global _TABLE, _GROUPS
    _patch_protein_pocket_features()
    _TABLE = load_table(_base_args())
    _GROUPS = {
        label: pbc.resolve_excluded_lipids(_TABLE, list(tokens))
        for label, tokens in EXCLUDED_LIPID_GROUP_SPECS
    }


def _worker_evaluate(job: tuple[str, tuple[str, ...], tuple[str, ...]]) -> dict:
    phase, protein_names, lipid_names = job
    test_ba, test_f1, auc_in_protein = evaluate_combo(protein_names, lipid_names)
    return {
        "phase": phase, "protein_names": protein_names, "lipid_names": lipid_names,
        "test_ba": test_ba, "test_f1": test_f1, "auc_in_protein": auc_in_protein,
    }


class ResultLogger:
    """Appends one CSV row per evaluated combination as it lands -- the ALL-results
    log the search must not lose even if interrupted partway through.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not self.path.exists()
        self._file = open(self.path, "a", newline="")
        self._writer = csv.writer(self._file)
        if is_new:
            self._writer.writerow(
                ["phase", "protein_descriptors", "lipid_descriptors",
                 "test_ba", "test_f1", "auc_in_protein"]
            )

    def log(self, row: dict) -> None:
        self._writer.writerow([
            row["phase"], ",".join(row["protein_names"]), ",".join(row["lipid_names"]),
            f"{row['test_ba']:.6f}", f"{row['test_f1']:.6f}", f"{row['auc_in_protein']:.6f}",
        ])
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def _run_batch(pool: mp.pool.Pool, jobs: list, logger: ResultLogger) -> list[dict]:
    results = []
    for row in pool.imap_unordered(_worker_evaluate, jobs):
        logger.log(row)
        results.append(row)
    return results


def _signature(protein_names, lipid_names) -> tuple:
    """Order-independent identity of a combination -- two search paths that reach the
    same descriptor SET must not be evaluated twice (a beam of several paths reaches
    the same set constantly; without this the beam would spend most of its budget
    re-scoring duplicates).
    """
    return (frozenset(protein_names), frozenset(lipid_names))


def _run_unique(pool, jobs, logger, seen: dict) -> list[dict]:
    """_run_batch, minus anything already evaluated -- `seen` maps signature -> row,
    and an already-known row is returned from there instead of recomputed. Duplicates
    WITHIN one batch are collapsed too (several beam paths routinely expand into the
    same set on the same step), which is why `queued` is tracked separately from
    `seen`: a signature queued but not yet evaluated has no row to return.
    """
    fresh, known, queued = [], [], set()
    for job in jobs:
        signature = _signature(job[1], job[2])
        if signature in seen:
            known.append(seen[signature])
        elif signature not in queued:
            queued.add(signature)
            fresh.append(job)
    results = _run_batch(pool, fresh, logger) if fresh else []
    for row in results:
        seen[_signature(row["protein_names"], row["lipid_names"])] = row
    return known + results


def beam_search(
    pool: mp.pool.Pool, logger: ResultLogger, beam_width: int, patience: int,
    deadline: float | None,
) -> dict:
    """Forward BEAM search over both descriptor sides at once, then one backward
    elimination pass over the winner.

    Beam rather than plain greedy specifically because greedy starves one side: with
    a single surviving path, whichever side happens to give the larger first-step gain
    keeps winning, and the other side never grows past the seed. A beam of `beam_width`
    keeps that many DIFFERENT partial sets alive, so a path that invested in protein
    descriptors stays in contention even when a lipid addition looked better on the
    step it was made.

    Seed: every protein PAIR (C(20,2), the >=2-protein floor) against the lipid side
    at PINNED_LIPID_DESCRIPTOR alone -- the smallest combination the constraints allow.
    Each step then expands EVERY beam state by EVERY remaining candidate from EITHER
    pool, and the best `beam_width` distinct resulting sets (by test_BA) become the
    next beam. Stops when no state in the new beam beats the best test_BA seen so far,
    or when `deadline` (wall-clock, --hours) passes.

    Backward pass: from the winner, try dropping each descriptor in turn (never below
    2 protein names, never PINNED_LIPID_DESCRIPTOR); keep any drop that does not hurt
    test_BA. Forward selection routinely leaves in an early pick that a later addition
    made redundant -- this is what removes it.
    """
    names = list(PROTEIN_DESCRIPTOR_NAMES)
    pairs = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))]
    seed_lipids = (PINNED_LIPID_DESCRIPTOR,)
    seen: dict = {}
    print(f"seed: {len(pairs)} protein pairs x lipid={PINNED_LIPID_DESCRIPTOR}")
    started = time.time()
    results = _run_unique(
        pool, [("seed_pair", pair, seed_lipids) for pair in pairs], logger, seen
    )
    results.sort(key=lambda row: row["test_ba"], reverse=True)
    beam = results[:beam_width]
    best = beam[0]
    print(f"  seed done in {time.time() - started:.0f}s, best test_BA={best['test_ba']:.4f}")
    for rank, row in enumerate(beam, 1):
        print(f"    beam {rank}: {list(row['protein_names'])} test_BA={row['test_ba']:.4f}")

    step = 0
    stale = 0
    # Each beam state carries the id() of the seed row it descends from, so the
    # per-parent cap below can tell lineages apart.
    for row in beam:
        row["_lineage"] = id(row)
    while True:
        step += 1
        if deadline is not None and time.time() > deadline:
            print(f"  stopping: --hours budget reached at step {step}")
            break
        jobs, lineage_of = [], {}
        for state in beam:
            proteins, lipids = list(state["protein_names"]), list(state["lipid_names"])
            for candidate in PROTEIN_DESCRIPTOR_NAMES:
                if candidate not in proteins:
                    job = ("add_protein", tuple(proteins + [candidate]), tuple(lipids))
                    jobs.append(job)
                    lineage_of.setdefault(_signature(job[1], job[2]), state["_lineage"])
            for candidate in LIPID_DESCRIPTOR_NAMES:
                if candidate not in lipids:
                    job = ("add_lipid", tuple(proteins), tuple(lipids + [candidate]))
                    jobs.append(job)
                    lineage_of.setdefault(_signature(job[1], job[2]), state["_lineage"])
        if not jobs:
            break
        results = _run_unique(pool, jobs, logger, seen)
        results.sort(key=lambda row: row["test_ba"], reverse=True)
        # Distinct SETS, and at most `per_lineage` of them from any one parent line.
        # Without that cap the whole beam fills with children of the single best
        # state ("best set + each possible addition"), the diverse seeds die off after
        # one step, and a width-K beam degenerates into plain greedy -- which is
        # exactly what the first run of this script did.
        per_lineage = max(1, beam_width // 2)
        next_beam, taken, used = [], set(), {}
        for row in results:
            signature = _signature(row["protein_names"], row["lipid_names"])
            if signature in taken:
                continue
            lineage = lineage_of.get(signature)
            if used.get(lineage, 0) >= per_lineage:
                continue
            taken.add(signature)
            used[lineage] = used.get(lineage, 0) + 1
            row["_lineage"] = lineage
            next_beam.append(row)
            if len(next_beam) == beam_width:
                break
        if not next_beam:
            break
        beam = next_beam
        improved = beam[0]["test_ba"] > best["test_ba"]
        if improved:
            best = beam[0]
            stale = 0
        else:
            stale += 1
        marker = "" if improved else f"  (no gain, {stale}/{patience})"
        leader = beam[0]
        print(
            f"  step {step}: test_BA={leader['test_ba']:.4f} test_F1={leader['test_f1']:.4f} "
            f"AUC_in_protein={leader['auc_in_protein']:.4f} "
            f"({len(leader['protein_names'])} protein / {len(leader['lipid_names'])} lipid)"
            f"{marker}"
        )
        # Patience: forward selection routinely plateaus for a step or two before a
        # later addition pays off, so a single flat step is not a reason to stop.
        # `best` keeps the record across the plateau, so wandering costs nothing.
        if stale >= patience:
            print(f"  stopping: {patience} steps without improving on test_BA={best['test_ba']:.4f}")
            break

    print()
    print("backward elimination pass")
    while True:
        proteins, lipids = list(best["protein_names"]), list(best["lipid_names"])
        jobs = []
        if len(proteins) > 2:
            for name in proteins:
                jobs.append((
                    "drop_protein", tuple(n for n in proteins if n != name), tuple(lipids)
                ))
        for name in lipids:
            if name != PINNED_LIPID_DESCRIPTOR:
                jobs.append((
                    "drop_lipid", tuple(proteins), tuple(n for n in lipids if n != name)
                ))
        if not jobs:
            break
        results = _run_unique(pool, jobs, logger, seen)
        candidate = max(results, key=lambda row: row["test_ba"])
        # ">=" not ">": a drop that merely TIES is still worth taking, it is the same
        # test_BA from a smaller, less overfittable descriptor set.
        if candidate["test_ba"] < best["test_ba"]:
            print("  nothing droppable without losing test_BA")
            break
        dropped = (
            set(proteins) - set(candidate["protein_names"])
            or set(lipids) - set(candidate["lipid_names"])
        )
        best = candidate
        print(
            f"  -{next(iter(dropped))}: test_BA={best['test_ba']:.4f} "
            f"({len(best['protein_names'])} protein / {len(best['lipid_names'])} lipid)"
        )

    return best


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--processes", type=int, default=mp.cpu_count())
    parser.add_argument(
        "--beam", type=int, default=3,
        help=(
            "how many partial descriptor sets stay alive per step. 1 is plain greedy "
            "(one side can then starve the other -- see beam_search's docstring); 3-4 "
            "is what a 4-5h budget on 8 cores affords."
        ),
    )
    parser.add_argument(
        "--patience", type=int, default=3,
        help=(
            "how many consecutive steps may fail to improve test_BA before the "
            "forward search stops. 1 stops at the first plateau (what the first run "
            "of this script did, finishing in 16 min with only 5 descriptors); 3 "
            "lets it push through a flat step or two, which forward selection "
            "routinely has."
        ),
    )
    parser.add_argument(
        "--hours", type=float, default=None,
        help="wall-clock budget; the forward search stops at the next step boundary once it passes (the backward pass still runs)",
    )
    parser.add_argument(
        "--log", type=Path,
        default=PROJECT_ROOT / "cron_test_metrics" / "descriptor_search_fig3_lipidgroups.csv",
    )
    args = parser.parse_args()

    logger = ResultLogger(args.log)
    print(f"logging every combination to {args.log}")
    print(f"beam width {args.beam}, patience {args.patience}, {args.processes} processes"
          + (f", {args.hours}h budget" if args.hours else ""))
    started = time.time()
    deadline = started + args.hours * 3600 if args.hours else None
    with mp.get_context("fork").Pool(processes=args.processes, initializer=_worker_init) as pool:
        best = beam_search(pool, logger, args.beam, args.patience, deadline)
    logger.close()

    print()
    print(f"=== best in {(time.time() - started) / 60:.0f} min ===")
    print(f"test_BA={best['test_ba']:.4f}  test_F1={best['test_f1']:.4f}  "
          f"AUC_in_protein={best['auc_in_protein']:.4f}")
    print(f"protein_descriptors ({len(best['protein_names'])}): "
          f"{','.join(best['protein_names'])}")
    print(f"lipid_descriptors ({len(best['lipid_names'])}): "
          f"{','.join(best['lipid_names'])}")
    print()
    print("reproduce with:")
    print(f"  python3 scripts/run_cron.py <label> --no_logs \\")
    print(f"      --excluded_lipid_groups="
          f"{','.join(label for label, _ in EXCLUDED_LIPID_GROUP_SPECS)} \\")
    print(f"      --protein_features={','.join(best['protein_names'])} \\")
    print(f"      --lipid_features={','.join(best['lipid_names'])} \\")
    print(f"      --seeds {','.join(str(s) for s in SEEDS)}")


if __name__ == "__main__":
    main()
