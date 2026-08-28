#!/usr/bin/env python3
"""Rank every pair descriptor by how lopsidedly it leaks identity, all at once.

analysis/feature_identity_check.py answers this one --features set at a time: run
it, read the eta^2 table, run it again for the next descriptor. This runs all of
dataloader.pair_descriptors.PAIR_DESCRIPTOR_NAMES through the same measurement in one
pass and sorts the result, so the comparison this question is actually about --which
pair descriptor to keep, drop, or redesign -- reads off one table instead of several
separate runs held in your head.

Why this question, not residualising the descriptors instead: analysis/
feature_identity_check.py's own --features "<name>_neutral" subtracts each
descriptor's per-protein and per-lipid_class mean, but under this project's
--double_coldsplit (the regime most of scripts/arg_files/*.md actually train under)
the held family's protein rows and the held classes' lipid rows are removed from
TRAIN unconditionally -- so for exactly the rows this measures, that mean is computed
from zero TRAIN rows. A residual built that way cannot be reproduced at inference on
a genuinely novel protein or lipid; a descriptor picked or redesigned by the ranking
this script prints needs no group statistic to exist at inference at all.

Two numbers per descriptor, both from analysis/feature_identity_check.py's own
eta_squared/build_axis_labels (see rank_pair_descriptors' docstring there):

  imbalance    |eta^2(lipid) - eta^2(protein)| -- near 0: leans on lipid and protein
               identity about equally (or neither). Large: dominated by one side's
               identity alone, which is the shape of a fingerprint, not compatibility.

  excess_pair  eta^2(lipid_class x protein_family) minus whichever single COARSE axis
               (lipid_class or protein_family) already explains more on its own.
               Positive: the descriptor responds to the PAIRING itself, not just to
               one side -- the part worth keeping. Near 0: the pair axis adds nothing
               a single axis did not already say.

Sorted by `imbalance` descending -- the most one-sided descriptors first, since a
descriptor dominated by a single identity axis fails to generalise regardless of what
`excess_pair` says about it.

    python3 analysis/rank_pair_descriptors.py
    python3 analysis/rank_pair_descriptors.py --features occupancy,chain_extent_gap,aromatic_contact

Reads only. Trains nothing.
"""
import argparse
import os
import sys

import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)

from analysis.feature_identity_check import rank_pair_descriptors  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pair_descriptors import PAIR_DESCRIPTOR_NAMES  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--features", default=",".join(PAIR_DESCRIPTOR_NAMES),
        help="Comma-separated pair descriptor names to rank (default: every name in "
             "dataloader.pair_descriptors.PAIR_DESCRIPTOR_NAMES).",
    )
    parser.add_argument(
        "--zscore", action="store_true",
        help="See analysis/null_model.py --zscore; forwarded unchanged to each descriptor's own resolution.",
    )
    args = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    data_dir = os.path.join(PROJECT_ROOT, "data")
    descriptor_names = [name for name in args.features.split(",") if name]

    pandas.set_option("display.width", 200)
    table = rank_pair_descriptors(csv, data_dir, descriptor_names, args.zscore)
    print(table.round(3).to_string())


if __name__ == "__main__":
    main()
