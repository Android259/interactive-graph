#!/usr/bin/env python3
"""Greedy forward search for a --descriptor_names set to train --descriptors_head with.

The task stated the way the rest of analysis/feature_identity_check.py and this
file's own sibling analysis/rank_pair_descriptors.py already have it: generalise to a
protein-lipid pair neither side of which training has seen, not memorise which
specific protein or lipid a row names. Three existing, already-vetted numbers this
project computes, combined into one search objective:

  AUC       analysis/null_model.py's own null_AUC_pair_k{k} -- rows ranked jointly
            inside each protein AND inside each lipid class (per_pair_auc), not the
            family-marginal null_AUC_k{k} -- on the --double_coldsplit block, mean
            over --families x --seeds. The project's existing, most direct
            measurement of "does this feature set let you rank a genuinely novel
            protein-lipid PAIR's compatibility correctly", as opposed to the
            marginal null_AUC_k{k}, which a descriptor can score well on just by
            tracking one side's row-level prior. This is the actual task, not a
            proxy for it.

  auc_std   std, ACROSS families, of that same per-family null_AUC_pair_k{k} mean
            (families/signal_state.md 6.4: "never average across families" -- 0.529
            is not a property of the model when it is a mix of 0.594 on three
            families and 0.470 on three others). A descriptor set that wins on
            average by being excellent on two families and useless on the rest is
            not what "generalises" means here; this term prices that mix down.

  leak      analysis/feature_identity_check.py's eta_squared_joint, on the "lipid"
            and "protein" axes specifically (the FINE, ungeneralisable ones --
            family/class-level correlation is not penalised: real biology ties
            related proteins to related pockets, and that part is expected to
            transfer to an unseen member of a known family; see feature_identity_
            check.py's own module docstring). The mean of the two is how much of the
            combined descriptor vector is "which exact protein"/"which exact lipid"
            and nothing else -- the shortcut --double_coldsplit exists to withhold,
            and neither AUC term above can see it: a descriptor set can score well
            on THIS PARTICULAR held family by leaning on identity that happens to
            correlate with it here without that correlation holding for a different
            held-out family.

    score = AUC - AUC_STD_WEIGHT * auc_std - LEAK_WEIGHT * leak

Search: start from the empty set, repeatedly add whichever untried descriptor raises
`score` the most, stop when no remaining descriptor improves it (or --max is hit).
Forward, not exhaustive (11 pair descriptors -> 2**11 subsets is not needed): O(n^2)
evaluations, each one an actual analysis/null_model.py run, printed as it goes so a
long search is legible while it runs rather than only at the end.

    python3 analysis/select_descriptors.py
    python3 analysis/select_descriptors.py --candidates occupancy,volume_fit,chain_extent_gap,aromatic_contact,hbond_match
    python3 analysis/select_descriptors.py --leak-weight 0.3 --auc-std-weight 0.5 --seeds 0,1,2,3,4

Reads only. Trains nothing itself -- prints a --descriptor_names value for an actual
training run to use.
"""
import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)

from analysis.feature_identity_check import (  # noqa: E402
    build_axis_labels, eta_squared_joint, protein_family_map, species_class_map,
)
from analysis.null_model import (  # noqa: E402
    DEFAULT_FAMILIES, null_model_table, resolve_similarity,
)
from dataloader.chemistry_prior import raw_feature_matrix  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES  # noqa: E402


def auc_for(csv, data_dir, feature_list, families, seeds, k, share, ratio):
    """Mean and cross-family std of null_AUC_pair_k{k} over --families x --seeds for
    this exact feature_list -- analysis/null_model.py's own per_pair_auc measurement
    (rows ranked jointly inside each protein AND inside each lipid class), not the
    family-marginal null_AUC_k{k}; `label` is the sorted feature list itself, so
    null_model.py's own on-disk cache (CACHE_PATH) is reused automatically across
    repeated runs of this script, not just within one.

    The std is taken BETWEEN families (mean over seeds within each family first,
    then std of those 7 family means), matching null_model.py's own "(std families)"
    column -- not the within-family std across seeds, which is a different question
    (measurement noise for one family, not generalisation spread across families).
    """
    label = ",".join(sorted(feature_list))
    similarity, index, entity_column, resolved_label, resolved_features = resolve_similarity(
        csv, data_dir, ",".join(sorted(feature_list)), label=label, zscore=False
    )
    table = null_model_table(
        csv, similarity, index, families=families, seeds=seeds,
        neighbour_counts=(k,), share=share, ratio=ratio, split="valid",
        entity_column=entity_column, label=label, features=resolved_features,
    )
    per_family = table.groupby("fam")[f"null_AUC_pair_k{k}"].mean()
    return float(per_family.mean()), float(per_family.std())


def leak_for(csv, data_dir, feature_list, species_class, protein_family):
    """Mean of eta_squared_joint on the "lipid" and "protein" (fine, ungeneralisable)
    axes for this exact feature_list -- analysis/feature_identity_check.py's own
    joint-vector eta^2, computed once on the whole dataset (this is a property of the
    feature vectors themselves, not of any one coldsplit -- see that module's GLOBAL
    section docstring), not the coarser lipid_class/protein_family axes, which real
    biology is expected to correlate with and this search should not penalise.
    """
    entities, matrix, entity_column, _ = raw_feature_matrix(csv, data_dir, feature_list, zscore=False)
    axes = build_axis_labels(entity_column, entities, csv, species_class, protein_family)
    fine_axes = [name for name in ("lipid", "protein") if name in axes]
    if not fine_axes:
        # A single-axis feature_list (e.g. one lipid-only name) has no protein axis
        # to read at all -- its own matching fine axis is degenerate by construction
        # (see build_axis_labels), so there is nothing here to penalise or reward.
        return 0.0
    return float(np.mean([eta_squared_joint(matrix, axes[name]) for name in fine_axes]))


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--candidates", default=",".join(PAIR_DESCRIPTOR_NAMES),
        help="Comma-separated pool of descriptor names to search over (default: "
             "every name in dataloader.pair_descriptors.PAIR_DESCRIPTOR_NAMES).",
    )
    parser.add_argument(
        "--leak-weight", type=float, default=0.15,
        help="LEAK_WEIGHT in score = AUC - AUC_STD_WEIGHT*auc_std - LEAK_WEIGHT*leak "
             "(default 0.15). Higher = more willing to give up AUC to avoid identity leak.",
    )
    parser.add_argument(
        "--auc-std-weight", type=float, default=0.5,
        help="AUC_STD_WEIGHT above (default 0.5). Higher = more willing to give up "
             "mean AUC for a descriptor set that performs more EVENLY across the 7 "
             "families, instead of winning on average by being excellent on a couple "
             "and useless on the rest (files/signal_state.md 6.4).",
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help="Stop after at most this many descriptors even if score is still "
             "improving (default: no cap -- stop only when no addition helps).",
    )
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument(
        "--seeds", default="0,1,2",
        help="Fewer than analysis/null_model.py's own default (0,1,2,3,4) -- each "
             "round of this search is several full null_model.py runs, and the search "
             "only needs enough seeds to rank candidates against each other reliably, "
             "not the tightest possible single AUC estimate. Widen for a final check "
             "on the winning set.",
    )
    parser.add_argument("--k", type=int, default=15, help="Neighbour count for null_model.py's own AUC.")
    parser.add_argument("--share", type=float, default=0.7, help="--coldsplit_share of the run")
    parser.add_argument("--ratio", type=int, default=2, help="--negatives_per_positive of the run")
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    data_dir = os.path.join(PROJECT_ROOT, "data")
    species_class = species_class_map(csv)
    protein_family = protein_family_map(csv)
    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]
    candidates = [name for name in args.candidates.split(",") if name]

    def score_of(feature_list):
        auc_mean, auc_std = auc_for(csv, data_dir, feature_list, families, seeds, args.k, args.share, args.ratio)
        leak = leak_for(csv, data_dir, feature_list, species_class, protein_family)
        score = auc_mean - args.auc_std_weight * auc_std - args.leak_weight * leak
        return score, auc_mean, auc_std, leak

    chosen = []
    remaining = list(candidates)
    best_score = float("-inf")
    print(f"searching {len(candidates)} candidates, leak_weight={args.leak_weight}, "
          f"auc_std_weight={args.auc_std_weight}, families={len(families)}, seeds={len(seeds)}\n")
    print(f"{'round':<7}{'added':<24}{'score':>8}{'AUC_pair':>10}{'auc_std':>9}{'leak':>8}")

    round_number = 0
    while remaining and (args.max is None or len(chosen) < args.max):
        round_number += 1
        round_results = []
        for name in remaining:
            trial = chosen + [name]
            score, auc_mean, auc_std, leak = score_of(trial)
            round_results.append((score, auc_mean, auc_std, leak, name))
        round_results.sort(reverse=True)
        top_score, top_auc, top_auc_std, top_leak, top_name = round_results[0]
        if top_score <= best_score:
            print(f"{round_number:<7}(none improve score={best_score:.3f} -- stopping)")
            break
        best_score = top_score
        chosen.append(top_name)
        remaining.remove(top_name)
        print(f"{round_number:<7}{top_name:<24}{top_score:>8.3f}{top_auc:>10.3f}{top_auc_std:>9.3f}{top_leak:>8.3f}")

    print(f"\n--descriptor_names={','.join(chosen)}")
    print(f"final: score={best_score:.3f}")
    if len(seeds) < 5:
        print(
            f"\n(searched with --seeds {args.seeds} for speed -- re-check the winning "
            f"set with more seeds: python3 analysis/null_model.py --features "
            f"{','.join(chosen)} --seeds 0,1,2,3,4)"
        )


if __name__ == "__main__":
    main()
