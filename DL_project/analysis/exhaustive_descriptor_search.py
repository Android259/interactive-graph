#!/usr/bin/env python3
"""EXHAUSTIVE descriptor search for the Figure-3 lipid-subclass cold split -- a real
optimum over a pre-screened pool, not a heuristic.

analysis/search_lipidgroups_descriptors.py is a beam search: it explores well but
guarantees nothing, and a beam can plateau out before reaching the best set. This
script trades pool size for an actual guarantee. Over 32 protein x 22 lipid names a
full grid is ~9e15 combinations (about 8e9 CPU-years); over a pre-screened
--protein_pool x --lipid_pool it is a few thousand, which fits an afternoon -- and
within that pool EVERY subset is evaluated, so the winner is the true optimum by the
chosen metric. What the guarantee does NOT cover is the pre-screen itself: a
descriptor cut in stage 1 can never come back, so the result is "optimal among the
pre-screened", not "optimal among all 54".

Two stages:

1. PRE-SCREEN (cheap, ~20 min on 10 cores). Protein side: all C(32,2) = 496 pairs
   against the lipid side at PINNED_LIPID_DESCRIPTOR alone -- every protein name then
   appears in exactly 31 comparable combinations, so ranking them by mean
   AUC_within_protein is a controlled comparison, not an artefact of which ones a
   search happened to visit more. Lipid side: each of the other 21 names paired with
   the pinned one against a FIXED protein pair (stage 1's winner), one evaluation per
   name, all in identical context.

2. EXHAUSTIVE over the survivors: every subset of the top --protein_pool protein
   names with >= 2 members, crossed with every subset of the top --lipid_pool lipid
   names that contains PINNED_LIPID_DESCRIPTOR.

Selection metric is AUC_within_protein (--metric auc, the default), NOT test_BA: the
chosen descriptors are meant to be reused on other models (a small MLP), and BA
depends on a decision threshold, which is a property of THIS model's score scale
(Kron-RLS scores sit near the training positive rate, ~0.06-0.10) rather than of the
descriptors. A rank metric carries over to a different model class; a threshold-based
one does not. test_BA/test_F1 are still computed and logged on every row.

    python3 analysis/exhaustive_descriptor_search.py --processes 10
    python3 analysis/exhaustive_descriptor_search.py --processes 10 \\
        --protein_pool 8 --lipid_pool 5 --metric auc
"""
from __future__ import annotations

import argparse
import itertools
import multiprocessing as mp
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.search_lipidgroups_descriptors import (  # noqa: E402
    EXCLUDED_LIPID_GROUP_SPECS,
    LIPID_DESCRIPTOR_NAMES,
    PINNED_LIPID_DESCRIPTOR,
    PROTEIN_DESCRIPTOR_NAMES,
    SEEDS,
    ResultLogger,
    _run_batch,
    _worker_init,
)

METRIC_COLUMN = {"auc": "auc_in_protein", "ba": "test_ba", "f1": "test_f1"}


def prescreen(pool, logger, metric: str) -> tuple[list[str], list[str]]:
    """Stage 1 -- see the module docstring. Returns (protein names, lipid names),
    each ranked best-first by `metric`, both FULL lists; the caller truncates.
    """
    names = list(PROTEIN_DESCRIPTOR_NAMES)
    pairs = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))]
    seed_lipids = (PINNED_LIPID_DESCRIPTOR,)
    print(f"stage 1a: {len(pairs)} protein pairs over a pool of {len(names)} "
          f"(every name in exactly {len(names) - 1} of them)")
    started = time.time()
    rows = _run_batch(pool, [("prescreen_protein", p, seed_lipids) for p in pairs], logger)
    scores = defaultdict(list)
    for row in rows:
        for name in row["protein_names"]:
            scores[name].append(row[metric])
    protein_ranked = sorted(scores, key=lambda name: -statistics.mean(scores[name]))
    print(f"  done in {time.time() - started:.0f}s")
    for rank, name in enumerate(protein_ranked, 1):
        print(f"    {rank:2d}. {name:32s} {statistics.mean(scores[name]):.4f}")

    # Fixed context for the lipid screen: the best PAIR outright, so every lipid
    # candidate is measured against identical protein input.
    best_pair = max(rows, key=lambda row: row[metric])["protein_names"]
    # aromatic_ring_count is CONSTANT across all 283 species in this table (zero
    # variance, verified directly) -- in an RBF kernel it is a dead dimension that
    # can only dilute the informative ones, so it is dropped before ranking rather
    # than left to lose on its own and waste an evaluation.
    candidates = [
        n for n in LIPID_DESCRIPTOR_NAMES
        if n != PINNED_LIPID_DESCRIPTOR and n != "aromatic_ring_count"
    ]
    print(f"\nstage 1b: {len(candidates)} lipid candidates against fixed protein "
          f"pair {list(best_pair)}")
    started = time.time()
    rows = _run_batch(
        pool,
        [("prescreen_lipid", tuple(best_pair), (PINNED_LIPID_DESCRIPTOR, c)) for c in candidates],
        logger,
    )
    by_name = {
        next(n for n in row["lipid_names"] if n != PINNED_LIPID_DESCRIPTOR): row[metric]
        for row in rows
    }
    lipid_ranked = sorted(by_name, key=lambda name: -by_name[name])
    print(f"  done in {time.time() - started:.0f}s")
    for rank, name in enumerate(lipid_ranked, 1):
        print(f"    {rank:2d}. {name:32s} {by_name[name]:.4f}")
    return protein_ranked, lipid_ranked


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--processes", type=int, default=mp.cpu_count())
    parser.add_argument(
        "--protein_pool", type=int, default=8,
        help="how many top protein descriptors survive the pre-screen into the exhaustive stage",
    )
    parser.add_argument(
        "--lipid_pool", type=int, default=5,
        help=(
            "how many lipid descriptors survive, PINNED_LIPID_DESCRIPTOR included "
            "(so 5 means the pinned one plus the 4 best others)"
        ),
    )
    parser.add_argument(
        "--metric", choices=("auc", "ba", "f1"), default="auc",
        help=(
            "what both stages rank by. auc = AUC_within_protein, threshold-free and "
            "therefore the one that transfers to another model class (the default, "
            "see module docstring); ba/f1 are threshold-based."
        ),
    )
    parser.add_argument(
        "--log", type=Path,
        default=PROJECT_ROOT / "cron_test_metrics" / "exhaustive_descriptor_search.csv",
    )
    args = parser.parse_args()
    metric = METRIC_COLUMN[args.metric]

    protein_subsets = 2 ** args.protein_pool - 1 - args.protein_pool
    lipid_subsets = 2 ** (args.lipid_pool - 1)
    print(f"logging every combination to {args.log}")
    print(f"metric: {metric}, {args.processes} processes")
    print(f"exhaustive stage will be {protein_subsets} x {lipid_subsets} = "
          f"{protein_subsets * lipid_subsets} combinations")
    print()

    logger = ResultLogger(args.log)
    started = time.time()
    with mp.get_context("fork").Pool(processes=args.processes, initializer=_worker_init) as pool:
        protein_ranked, lipid_ranked = prescreen(pool, logger, metric)
        protein_pool = protein_ranked[:args.protein_pool]
        lipid_pool = [PINNED_LIPID_DESCRIPTOR] + lipid_ranked[:args.lipid_pool - 1]
        print()
        print(f"stage 2: exhaustive over protein={protein_pool}")
        print(f"                          lipid={lipid_pool}")

        jobs = []
        for p_size in range(2, len(protein_pool) + 1):
            for p_subset in itertools.combinations(protein_pool, p_size):
                others = [n for n in lipid_pool if n != PINNED_LIPID_DESCRIPTOR]
                for l_size in range(0, len(others) + 1):
                    for l_extra in itertools.combinations(others, l_size):
                        jobs.append((
                            "exhaustive", p_subset, (PINNED_LIPID_DESCRIPTOR,) + l_extra
                        ))
        print(f"  {len(jobs)} combinations to evaluate")
        stage2_started = time.time()
        rows = _run_batch(pool, jobs, logger)
        print(f"  done in {(time.time() - stage2_started) / 60:.0f} min")
    logger.close()

    best = max(rows, key=lambda row: row[metric])
    print()
    print(f"=== OPTIMUM over the pre-screened pool, in {(time.time() - started) / 60:.0f} min ===")
    print(f"ranked by {metric}")
    print(f"  AUC_in_protein={best['auc_in_protein']:.4f}  "
          f"test_BA={best['test_ba']:.4f}  test_F1={best['test_f1']:.4f}")
    print(f"protein_descriptors ({len(best['protein_names'])}): {','.join(best['protein_names'])}")
    print(f"lipid_descriptors ({len(best['lipid_names'])}): {','.join(best['lipid_names'])}")
    print()
    print("runner-up combinations (next 4 by the same metric):")
    for row in sorted(rows, key=lambda r: -r[metric])[1:5]:
        print(f"  {row[metric]:.4f}  P[{','.join(row['protein_names'])}]  "
              f"L[{','.join(row['lipid_names'])}]")

    # Best set AT EACH SIZE, not just the global best. The global optimum alone
    # cannot say whether a larger set costs anything: if size 7 scores the same as
    # size 3, the extra descriptors are free here AND carry more into a model that
    # weights its inputs (an MLP does; an RBF kernel, which this search scores on,
    # weights every dimension equally and so is biased toward small sets). If the
    # metric instead falls off with size, that is evidence the other way. Either way
    # it is the curve, not one number, that answers "how many descriptors".
    print()
    print("best per total descriptor count (protein + lipid):")
    by_size: dict[int, dict] = {}
    for row in rows:
        size = len(row["protein_names"]) + len(row["lipid_names"])
        if size not in by_size or row[metric] > by_size[size][metric]:
            by_size[size] = row
    for size in sorted(by_size):
        row = by_size[size]
        print(
            f"  {size:2d} total ({len(row['protein_names'])}P+{len(row['lipid_names'])}L): "
            f"{metric}={row[metric]:.4f}  AUC={row['auc_in_protein']:.4f} "
            f"BA={row['test_ba']:.4f} F1={row['test_f1']:.4f}"
        )
        print(f"        P[{','.join(row['protein_names'])}] L[{','.join(row['lipid_names'])}]")
    print()
    print("reproduce with:")
    print("  python3 scripts/run_cron.py <label> --no_logs \\")
    print(f"      --excluded_lipid_groups="
          f"{','.join(label for label, _ in EXCLUDED_LIPID_GROUP_SPECS)} \\")
    print(f"      --protein_features={','.join(best['protein_names'])} \\")
    print(f"      --lipid_features={','.join(best['lipid_names'])} \\")
    print(f"      --seeds {','.join(str(s) for s in SEEDS)}")


if __name__ == "__main__":
    main()
