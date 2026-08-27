#!/usr/bin/env python3
"""How much genuine pair content each candidate form of the compatibility feature has.

The finding that makes this necessary (files/compat_input_audit.md 1): the shipped
feature is `pocket_extent(p) - chain_length(l)`, a DIFFERENCE of one protein-only number
and one lipid-only number. A difference is additive, and an additive function of (p, l) is
by definition a protein main effect plus a lipid main effect with an interaction term of
exactly zero -- double-centring annihilates it. So the number the model receives carries
no pair information at all, and every pair-shaped result measured from it was created by
the network applying a protein-conditioned nonlinearity, not read out of the input.

That is not an argument against the feature, but it is an argument against the FORM. A
non-additive combination of the same two quantities survives double-centring and hands the
network pair content instead of asking it to manufacture some. This script measures, for
each candidate form, the three things that decide whether it is worth a run:

  interaction_share -- fraction of the feature's variance left after removing the protein
      main effect and the lipid main effect, over the full protein x lipid grid. Zero for
      the shipped difference, by the argument above; anything above it is real pair
      content. This is the number the whole file exists for.
  eta2_family -- fraction of the feature's variance explained by which FAMILY the protein
      belongs to, the same identity check preprocessing/pocket_descriptor_identity_check.py
      applies to POCKET_DESCRIPTOR_NAMES (which rejected every descriptor at 0.28-0.85).
      A pair feature that scores high here is a fold label wearing a disguise.
  AUC on the held-out block, pooled and inside protein, so a form with more pair content
      but no predictive value is not mistaken for an improvement.

Candidate forms, all built from the same two quantities so nothing new has to be computed:

  difference      extent - chain                     (shipped; additive, share = 0)
  abs_mismatch    |extent - chain|                   non-additive
  clash           relu(chain - extent)               tail longer than the cavity
  slack           relu(extent - chain)               cavity longer than the tail
  fit_gaussian    exp(-((extent-chain)/sigma)^2)     smooth "right size" score
  ratio           chain / extent                     non-additive in raw space

`clash` and `slack` are reported apart rather than as one signed number because the two
directions are not the same physics: a tail that does not fit is a steric exclusion, a
cavity with room to spare is a weaker contact, and a signed difference forces one
coefficient onto both.

Reads only. Trains nothing, appends to no shared table.

    scripts/env.sh python3 analysis/compat_feature_forms.py
    scripts/env.sh python3 analysis/compat_feature_forms.py --split test
"""
import argparse
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "preprocessing"))

from analysis.null_model import (  # noqa: E402
    DEFAULT_FAMILIES,
    WORKING,
    auc,
    per_protein_auc,
    working_set,
)
from lipid_marginal_baseline import split as split_func  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pocket_lipid_compatibility import (  # noqa: E402
    chain_length_by_species,
    pocket_extent_by_protein,
)
from dataloader.sampler import lipid_classes_for_holdout  # noqa: E402


def coarsen(values, bins, edges=None):
    """Replace each value by the midpoint of its quantile bin, or return it unchanged.

    The identity channel this closes: `pocket_extent` takes 35 distinct values over 35
    proteins in [13.6, 32.0], so at full resolution it is very nearly a protein id, and
    `eta2_protein` measures how nearly. Rounding it to a handful of levels keeps the
    physical claim -- this cavity is longer than that one -- while destroying the
    one-to-one map that makes it a label. `edges` is passed in when the block must be cut
    at the same places the whole table was, so a held-out protein cannot land in a bin
    that only exists because of its own value.
    """
    if not bins:
        return values, None
    values = np.asarray(values, dtype=float)
    if edges is None:
        edges = np.nanquantile(values, np.linspace(0, 1, bins + 1))
        edges[0], edges[-1] = -np.inf, np.inf
    which = np.clip(np.searchsorted(edges, values, side="right") - 1, 0, bins - 1)
    centres = np.array([
        np.nanmean(values[which == b]) if (which == b).any() else np.nan
        for b in range(bins)
    ])
    filled = pandas.Series(centres).ffill().bfill().to_numpy()
    return filled[which], edges


def candidate_forms(extent, chain, sigma):
    """Every candidate as a dict name -> values, given aligned extent/chain arrays."""
    difference = extent - chain
    return {
        "difference": difference,
        "abs_mismatch": -np.abs(difference),
        "clash": -np.maximum(chain - extent, 0.0),
        "slack": -np.maximum(extent - chain, 0.0),
        "fit_gaussian": np.exp(-((difference / sigma) ** 2)),
        "ratio": -(chain / np.where(extent == 0, np.nan, extent)),
        "chain_only": -chain,
    }


def interaction_share(values, protein_codes, lipid_codes):
    """Fraction of variance left after removing both main effects (two-way ANOVA).

    Fits the additive model `grand + a(protein) + b(lipid)` by alternating means -- the
    grid is unbalanced (not every protein was screened against every lipid in a sampled
    pool), so a single pass of row and column means does not remove the main effects
    exactly and the residual would keep a sliver of them. Twenty passes bring the
    remaining main-effect variance below 1e-9 on this table, checked by re-measuring.
    """
    values = np.asarray(values, dtype=float)
    residual = values - np.nanmean(values)
    for _ in range(20):
        for codes in (protein_codes, lipid_codes):
            means = pandas.Series(residual).groupby(codes).transform("mean").to_numpy()
            residual = residual - means
    total = np.nanvar(values)
    return float(np.nanvar(residual) / total) if total > 1e-12 else float("nan")


def eta_squared(values, groups):
    """Fraction of the feature's variance explained by a categorical label."""
    frame = pandas.DataFrame({"v": np.asarray(values, dtype=float), "g": list(groups)})
    grand = frame["v"].mean()
    between = (
        frame.groupby("g")["v"].agg(["mean", "count"])
        .assign(ss=lambda f: f["count"] * (f["mean"] - grand) ** 2)["ss"].sum()
    )
    total = ((frame["v"] - grand) ** 2).sum()
    return float(between / total) if total > 1e-12 else float("nan")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    parser.add_argument("--seeds", default="0,1")
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--ratio", type=int, default=2)
    parser.add_argument("--split", default="valid", choices=("valid", "test"))
    parser.add_argument(
        "--sigma", type=float, default=5.75,
        help="width of fit_gaussian; default is the std of the shipped difference",
    )
    parser.add_argument(
        "--extent_bins", type=int, default=0,
        help="round pocket_extent to this many quantile levels first (0 = full "
             "resolution, which is where it is nearly a protein id)",
    )
    args = parser.parse_args()

    families = [f for f in args.families.split(",") if f]
    seeds = [int(s) for s in args.seeds.split(",")]

    data_dir = os.path.join(PROJECT_ROOT, "data") + os.sep
    csv = pandas.read_csv(interaction_csv_path(data_dir))
    lengths = chain_length_by_species(csv)
    extents = pocket_extent_by_protein(
        data_dir, sorted(csv["LTPProtein"].dropna().unique().tolist())
    )

    # --- structure of each form, on the whole table (no split, no labels) ---
    whole = csv.dropna(subset=["LTPProtein", "FullIdentityOfLipid"]).copy()
    whole["_chain"] = whole["FullIdentityOfLipid"].map(lengths).astype(float)
    whole["_extent"] = whole["LTPProtein"].map(extents).astype(float)
    whole = whole.dropna(subset=["_chain", "_extent"])
    protein_codes = pandas.Categorical(whole["LTPProtein"]).codes
    lipid_codes = pandas.Categorical(whole["FullIdentityOfLipid"]).codes
    # The bin edges are cut once, on the whole table, and reused for every held-out
    # block below -- cutting them per block would let a protein define the bin it lands
    # in, which is the kind of quiet difference that turns a control into a confound.
    coarse_extent, extent_edges = coarsen(
        whole["_extent"].to_numpy(), args.extent_bins
    )
    forms = candidate_forms(coarse_extent, whole["_chain"].to_numpy(), args.sigma)

    print(f"table : {len(whole)} rows, {whole['LTPProtein'].nunique()} proteins, "
          f"{whole['FullIdentityOfLipid'].nunique()} lipids, sigma = {args.sigma}, "
          f"extent_bins = {args.extent_bins or 'full resolution'}\n")

    structure = pandas.DataFrame([
        {
            "form": name,
            "interaction_share": interaction_share(values, protein_codes, lipid_codes),
            "eta2_family": eta_squared(values, whole["ProteinDomain"]),
            "eta2_protein": eta_squared(values, whole["LTPProtein"]),
        }
        for name, values in forms.items()
    ]).set_index("form")
    print("=== structure of the feature itself (no labels, no split) ===")
    print(structure.round(4).to_string())
    print("\ninteraction_share = variance left after removing the protein main effect")
    print("and the lipid main effect. 0 means the form carries no pair content at all.")
    print("eta2_family: the bar preprocessing/pocket_descriptor_identity_check.py")
    print("rejected pocket descriptors at is 0.28-0.85.\n")

    # --- what each form is worth on the held-out blocks ---
    rows = []
    for family in families:
        held_classes = lipid_classes_for_holdout(csv, family, args.share)[0]
        for seed in seeds:
            csvt = working_set(csv, seed, args.ratio, held_classes)
            train, valid, test = split_func(
                csvt, family, seed, held_classes, double=True
            )
            block = valid if args.split == "valid" else test
            labels = block["Interaction"].to_numpy()
            if len(set(labels)) < 2:
                continue
            chain = block["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
            extent = block["LTPProtein"].map(extents).to_numpy(dtype=float)
            train_chain = train["FullIdentityOfLipid"].map(lengths).to_numpy(dtype=float)
            chain = np.where(np.isnan(chain), np.nanmean(train_chain), chain)
            extent, _ = coarsen(extent, args.extent_bins, extent_edges)
            for name, values in candidate_forms(extent, chain, args.sigma).items():
                pooled = auc(labels, values)
                inside, proteins = per_protein_auc(block, values)
                rows.append({
                    "fam": family, "seed": seed, "form": name,
                    "pooled": pooled, "inside": inside, "proteins": proteins,
                })

    table = pandas.DataFrame(rows)
    print(f"=== AUC of each form on the {args.split} block, no network ===")
    summary = pandas.DataFrame({
        "pooled, all seven": table.groupby("form")["pooled"].mean(),
        "inside, all seven": table.groupby("form")["inside"].mean(),
        "inside, working three": table[table["fam"].isin(WORKING)]
            .groupby("form")["inside"].mean(),
        "inside, other four": table[~table["fam"].isin(WORKING)]
            .groupby("form")["inside"].mean(),
    })
    print(summary.round(3).to_string())
    print()
    print("=== inside protein, per family ===")
    print(table.pivot_table(
        index="form", columns="fam", values="inside", aggfunc="mean"
    ).round(3).to_string())
    print()


if __name__ == "__main__":
    main()
