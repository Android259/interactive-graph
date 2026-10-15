"""Report lipid classes selected for a cold split.

Use lipid_classes_for_holdout() from dataloader.splitting_on_blocks.lipid_coldsplit_blocks.
For each family, rank classes by:
    family positives / (other-family positives + 1)
Select classes until they cover the requested share of family positives.
Report the held-out rows and the rows removed from other families.
This script reports the split; it does not configure training runs.
"""

import argparse
import os
import sys

import pandas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Allow pandas-only reporting when torch is unavailable; see lipid_marginal_baseline.py.
try:  # pragma: no cover - depends on the machine, not on the code path
    import torch  # noqa: F401
except ModuleNotFoundError:
    import types

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

from dataloader.dataset_source import interaction_csv_path
from dataloader.splitting_on_blocks.lipid_coldsplit_blocks import (
    COLDSPLIT_MINIMUM_TEST_POSITIVES,
    lipid_classes_for_holdout,
)

MINIMUM_TEST_POSITIVES = COLDSPLIT_MINIMUM_TEST_POSITIVES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--share", type=float, default=0.7)
    parser.add_argument("--families", default="")
    parser.add_argument(
        "--flags",
        action="store_true",
        help="print one launch line per family, ready to paste",
    )
    arguments = parser.parse_args()

    csv = pandas.read_csv(interaction_csv_path(arguments.data_dir))
    families = [f for f in arguments.families.split(",") if f] or sorted(
        csv["ProteinDomain"].dropna().unique().tolist()
    )

    for family in families:
        chosen, covered, cost = lipid_classes_for_holdout(
            csv, family, arguments.share
        )
        if arguments.flags:
            if covered >= MINIMUM_TEST_POSITIVES:
                print(f"--excluded_groups={family} --double_coldsplit")
            continue
        usable = "" if covered >= MINIMUM_TEST_POSITIVES else "  [too few positives]"
        print(
            f"{family:<14} {len(chosen):>2} classes | block {covered:>3}+ | "
            f"costs train {cost:>3}+{usable}"
        )
        print(f"{'':14} {', '.join(chosen)}")


if __name__ == "__main__":
    main()
