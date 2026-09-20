#!/usr/bin/env python3
"""EXHAUSTIVE protein-side search over the incumbent winner PLUS the newly added
pocket-chemistry / cavity descriptors, with the lipid side held fixed.

The question this answers is narrower than exhaustive_descriptor_search.py's, and
because it is narrower it can be answered without a pre-screen that cuts the
incumbent: given that the 32-name pool now contains ten pocket-chemistry shares and
two cavity descriptors that no earlier search could see, is the incumbent 7-descriptor
set still the best combination -- or do some of its members become redundant once the
new ones are available and drop out?

"Pin the incumbent and only test additions" cannot answer that. The new descriptors
land on axes three incumbents already occupy: pocket_packing_density (free fraction of
the pocket) against pocket_volume_per_sasa (volume per surface) is the same
space-per-protein ratio twice, and polar_share_core/rim is the complement of
apolar_sasa_share and hydropathy_mean. An RBF kernel weights every dimension equally
and cannot damp a duplicate, so a near-duplicate column silently doubles that axis's
weight -- add-only can pile that on but never undo it. Every subset here is free to
drop an incumbent, so a replacement is findable; and the incumbent set itself is one
of the enumerated subsets, so its RANK among all of them is reported directly.

Holding the lipid side fixed is what buys the exhaustiveness. It is defensible here:
in exhaustive_descriptor_search.py's completed 16064-combination run the top four
rows carry the IDENTICAL five-name lipid set (FIXED_LIPID_DESCRIPTORS below). That is
an observation about this model on this split, not a proof the lipid side is settled
-- a joint protein+lipid optimum could in principle sit elsewhere, and only a rerun
of the full two-sided search would see it.

Two stages:

1. PRE-SCREEN of the NEW descriptors only (24 evaluations, a few minutes). The
   incumbent seven are never screened -- they enter stage 2 unconditionally. Each new
   name is measured twice in two identical contexts, because the two measure different
   things and a descriptor worth keeping can win either way:
     A. ANCHOR + name -- standalone strength, the way exhaustive_descriptor_search's
        lipid screen works. Catches a strong descriptor that merely overlaps what the
        incumbent already covers, which is exactly a replacement candidate.
     B. incumbent seven + name -- marginal gain on top of everything. Catches a
        descriptor that adds a direction none of the seven has.
   Ranked by mean rank across A and B, so a name has to lose both to be cut.

2. EXHAUSTIVE over the incumbent seven + the top --new_pool survivors: every subset
   with >= 2 members, lipid side fixed. 7 + 7 = 14 names is 2^14 - 1 - 14 = 16369
   subsets, about the same wall clock as the two-sided run that produced the
   incumbent. Within that pool the winner is the true optimum by the chosen metric.

Selection metric is AUC_within_protein (--metric auc, the default), matching the run
that produced the incumbent -- a threshold-free rank metric, so it carries over to a
different model class, which a BA/F1 optimum tied to this model's score scale does not.

    python3 analysis/exhaustive_protein_side_search.py --processes 10
    python3 analysis/exhaustive_protein_side_search.py --processes 10 --new_pool 5
"""
from __future__ import annotations

import argparse
import itertools
import multiprocessing as mp
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import training.pair_baseline_common as pbc  # noqa: E402
from analysis.search_lipidgroups_descriptors import (  # noqa: E402
    EXCLUDED_LIPID_GROUP_SPECS,
    PROTEIN_DESCRIPTOR_NAMES,
    SEEDS,
    ResultLogger,
    _run_batch,
    _worker_init,
)

METRIC_COLUMN = {"auc": "auc_in_protein", "ba": "test_ba", "f1": "test_f1"}

# The winner of cron_test_metrics/exhaustive_descriptor_search.csv (16064 combinations,
# AUC_within_protein 0.6681) -- the set this run is asked to either confirm or improve
# on. Entering stage 2 unscreened is the whole point: it must be free to lose members.
INCUMBENT_PROTEIN_DESCRIPTORS = (
    "pocket_elongation",
    "ev14_q50",
    "apolar_sasa_share",
    "pocket_elongation_lambda_sqrt",
    "hydropathy_mean",
    "pocket_volume_per_sasa",
    "depth_q10",
)
# The lipid side of that same winner, and of the three runners-up behind it.
FIXED_LIPID_DESCRIPTORS = (
    "experimental_lipid_volume",
    "unsaturation",
    "tail_double_bonds",
    "logp",
    "tail_unsaturation_density",
)
# The twelve names that only became visible to a search when the pool went 20 -> 32.
NEW_PROTEIN_DESCRIPTORS = tuple(pbc.POCKET_CHEMISTRY_NAMES) + tuple(pbc.POCKET_CAVITY_NAMES)
# Fixed partner for pre-screen A. The incumbent's strongest single member (it appears
# in 70 of the previous run's top 100 rows) -- a weak anchor would rank the candidates
# by who rescues it rather than by their own strength.
PRESCREEN_ANCHOR = "apolar_sasa_share"

# Measured on the completed 16274-combination run: 392 min on 10 processes.
CPU_SECONDS_PER_COMBO = 14.5


def _check_names() -> None:
    """Fail loudly at startup rather than deep inside a worker: every name below has
    to exist in the search pool, and the new ones must not already be incumbents.
    """
    pool = set(PROTEIN_DESCRIPTOR_NAMES)
    missing = [
        n for n in INCUMBENT_PROTEIN_DESCRIPTORS + NEW_PROTEIN_DESCRIPTORS if n not in pool
    ]
    if missing:
        raise SystemExit(f"not in PROTEIN_DESCRIPTOR_NAMES: {missing}")
    overlap = set(INCUMBENT_PROTEIN_DESCRIPTORS) & set(NEW_PROTEIN_DESCRIPTORS)
    if overlap:
        raise SystemExit(f"incumbent and new sets overlap: {sorted(overlap)}")


def prescreen(pool, logger: ResultLogger, metric: str) -> list[str]:
    """Stage 1 -- see the module docstring. Returns the new names ranked best-first by
    mean rank across the two contexts, FULL list; the caller truncates.
    """
    print(f"stage 1: {len(NEW_PROTEIN_DESCRIPTORS)} new descriptors x 2 contexts")
    started = time.time()
    jobs = [
        ("prescreen_anchor", (PRESCREEN_ANCHOR, name), FIXED_LIPID_DESCRIPTORS)
        for name in NEW_PROTEIN_DESCRIPTORS
    ] + [
        ("prescreen_marginal", INCUMBENT_PROTEIN_DESCRIPTORS + (name,), FIXED_LIPID_DESCRIPTORS)
        for name in NEW_PROTEIN_DESCRIPTORS
    ]
    rows = _run_batch(pool, jobs, logger)
    anchor = {
        next(n for n in r["protein_names"] if n != PRESCREEN_ANCHOR): r[metric]
        for r in rows if r["phase"] == "prescreen_anchor"
    }
    marginal = {
        next(n for n in r["protein_names"] if n not in INCUMBENT_PROTEIN_DESCRIPTORS): r[metric]
        for r in rows if r["phase"] == "prescreen_marginal"
    }
    rank_a = {n: i for i, n in enumerate(sorted(anchor, key=lambda n: -anchor[n]), 1)}
    rank_b = {n: i for i, n in enumerate(sorted(marginal, key=lambda n: -marginal[n]), 1)}
    ranked = sorted(NEW_PROTEIN_DESCRIPTORS, key=lambda n: (rank_a[n] + rank_b[n]) / 2)
    print(f"  done in {time.time() - started:.0f}s")
    print(f"    {'':2s} {'descriptor':28s} {'anchor':>8s} {'rk':>3s} {'+incumb':>8s} {'rk':>3s}")
    for place, name in enumerate(ranked, 1):
        print(f"    {place:2d}. {name:28s} {anchor[name]:8.4f} {rank_a[name]:3d} "
              f"{marginal[name]:8.4f} {rank_b[name]:3d}")
    return ranked


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--processes", type=int, default=mp.cpu_count())
    parser.add_argument(
        "--new_pool", type=int, default=7,
        help=(
            "how many of the 12 new descriptors survive the pre-screen into the "
            "exhaustive stage. The pool is that many plus the 7 incumbents, and the "
            "cost doubles per extra name: 5 -> 4083 subsets, 7 -> 16369, 8 -> 32752"
        ),
    )
    parser.add_argument(
        "--metric", choices=("auc", "ba", "f1"), default="auc",
        help="what both stages rank by; auc = AUC_within_protein (default, see docstring)",
    )
    parser.add_argument(
        "--log", type=Path,
        default=PROJECT_ROOT / "cron_test_metrics" / "exhaustive_protein_side_search.csv",
    )
    args = parser.parse_args()
    metric = METRIC_COLUMN[args.metric]
    _check_names()

    pool_size = len(INCUMBENT_PROTEIN_DESCRIPTORS) + args.new_pool
    subsets = 2 ** pool_size - 1 - pool_size
    hours = subsets * CPU_SECONDS_PER_COMBO / args.processes / 3600
    print(f"logging every combination to {args.log}")
    print(f"metric: {metric}, {args.processes} processes")
    print(f"lipid side FIXED at: {','.join(FIXED_LIPID_DESCRIPTORS)}")
    print(f"exhaustive stage: every subset of {pool_size} protein names with >= 2 "
          f"members = {subsets} combinations, roughly {hours:.1f} h")
    print()

    logger = ResultLogger(args.log)
    started = time.time()
    with mp.get_context("fork").Pool(processes=args.processes, initializer=_worker_init) as pool:
        ranked_new = prescreen(pool, logger, metric)
        survivors = ranked_new[:args.new_pool]
        protein_pool = list(INCUMBENT_PROTEIN_DESCRIPTORS) + survivors
        print()
        print(f"stage 2: incumbent 7 + {len(survivors)} new = {len(protein_pool)} names")
        print(f"  cut here, never to return: {ranked_new[args.new_pool:]}")

        jobs = []
        for size in range(2, len(protein_pool) + 1):
            for subset in itertools.combinations(protein_pool, size):
                jobs.append(("exhaustive", subset, FIXED_LIPID_DESCRIPTORS))
        print(f"  {len(jobs)} combinations to evaluate")
        stage2_started = time.time()
        rows = _run_batch(pool, jobs, logger)
        print(f"  done in {(time.time() - stage2_started) / 60:.0f} min")
    logger.close()

    rows.sort(key=lambda row: -row[metric])
    best = rows[0]
    new_in_best = [n for n in best["protein_names"] if n in NEW_PROTEIN_DESCRIPTORS]
    dropped = [n for n in INCUMBENT_PROTEIN_DESCRIPTORS if n not in best["protein_names"]]
    print()
    print(f"=== OPTIMUM over the pool, in {(time.time() - started) / 60:.0f} min ===")
    print(f"ranked by {metric}")
    print(f"  AUC_in_protein={best['auc_in_protein']:.4f}  "
          f"test_BA={best['test_ba']:.4f}  test_F1={best['test_f1']:.4f}")
    print(f"protein_descriptors ({len(best['protein_names'])}): {','.join(best['protein_names'])}")
    print(f"  new descriptors it kept ({len(new_in_best)}): {','.join(new_in_best) or '-'}")
    print(f"  incumbents it dropped ({len(dropped)}): {','.join(dropped) or '- (none)'}")

    # The direct answer to "is the incumbent still at least as good". It is one of the
    # enumerated subsets, so its rank among all of them is exact, not an estimate.
    incumbent_set = frozenset(INCUMBENT_PROTEIN_DESCRIPTORS)
    incumbent_rank = next(
        (i for i, r in enumerate(rows, 1) if frozenset(r["protein_names"]) == incumbent_set), None
    )
    print()
    if incumbent_rank is None:
        print("incumbent set was not evaluated (unexpected -- check the pool)")
    else:
        row = rows[incumbent_rank - 1]
        print(f"incumbent 7-descriptor set ranks {incumbent_rank} of {len(rows)}: "
              f"{metric}={row[metric]:.4f} vs optimum {best[metric]:.4f} "
              f"(delta {best[metric] - row[metric]:+.4f})")

    print()
    print("runner-up combinations (next 4 by the same metric):")
    for row in rows[1:5]:
        print(f"  {row[metric]:.4f}  [{','.join(row['protein_names'])}]")

    print()
    print("best per protein descriptor count:")
    by_size: dict[int, dict] = {}
    for row in rows:
        size = len(row["protein_names"])
        if size not in by_size or row[metric] > by_size[size][metric]:
            by_size[size] = row
    for size in sorted(by_size):
        row = by_size[size]
        print(f"  {size:2d}P: {metric}={row[metric]:.4f}  AUC={row['auc_in_protein']:.4f} "
              f"BA={row['test_ba']:.4f} F1={row['test_f1']:.4f}")
        print(f"        [{','.join(row['protein_names'])}]")

    # Per-name presence in the top rows: one descriptor winning the single best subset
    # can be luck at a 0.005-wide plateau; a name that sits in most of the top 100 is
    # carrying something. Marked so the new ones are readable at a glance.
    print()
    print("presence in the top 100 subsets:")
    counts = {name: 0 for name in INCUMBENT_PROTEIN_DESCRIPTORS}
    counts.update({name: 0 for name in NEW_PROTEIN_DESCRIPTORS})
    for row in rows[:100]:
        for name in row["protein_names"]:
            counts[name] += 1
    for name, count in sorted(counts.items(), key=lambda item: -item[1]):
        if count or name in INCUMBENT_PROTEIN_DESCRIPTORS:
            mark = "NEW" if name in NEW_PROTEIN_DESCRIPTORS else "   "
            print(f"  {count:4d}  {mark}  {name}")

    print()
    print("reproduce the optimum with:")
    print("  python3 scripts/run_cron.py <label> --no_logs \\")
    print(f"      --excluded_lipid_groups="
          f"{','.join(label for label, _ in EXCLUDED_LIPID_GROUP_SPECS)} \\")
    print(f"      --protein_features={','.join(best['protein_names'])} \\")
    print(f"      --lipid_features={','.join(FIXED_LIPID_DESCRIPTORS)} \\")
    print(f"      --seeds {','.join(str(s) for s in SEEDS)}")


if __name__ == "__main__":
    main()
