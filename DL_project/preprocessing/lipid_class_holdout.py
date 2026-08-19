"""Show which lipid classes the cold split will hold out, and what each costs.

Reporting only: the rule itself lives in `dataloader.sampler.lipid_classes_for_holdout`
and the loader applies it on its own, so nothing here is passed to a run. Use it to see
what --double_coldsplit is about to do, and to compare values of --coldsplit_share.

The second axis of the cold split needs a class set per family, not one shared set: a
family's positives sit in its own classes -- START's in phosphatidylcholines, GLTP's in
sphingolipids -- so any set fixed in advance is arbitrary for whichever family is being
held out. This scores every class by concentration,

    score(class) = family positives in class / (everyone else's positives in class + 1)

and takes classes by descending score until the family's covered positives reach
`share` of its total. The numerator is what the test block gains, the denominator what
training loses elsewhere, so the classes chosen are the ones the family owns.

`share` is not cosmetic. Stopping early leaves the cheap classes only, and for a family
whose cheap classes are thin on rows the test block ends up almost entirely familiar
lipids -- the split looks two-axis while the per-lipid label prior still carries it. At
share 0.3 the lipocalin lookup baseline stays at 0.618; 0.7 is the smallest value in
{0.3 ... 0.8} at which no family sits further than one standard error from 0.5, which is
why it is the default here. Verify with preprocessing/lipid_marginal_baseline.py after
changing anything: that check, not this rule, is what says the split is honest.

Families whose whole positive count is too small for a test block (ML, OSBP: 10 and 8)
are reported and skipped, exactly as they already are under the one-axis split.
"""

import argparse
import os
import sys

import pandas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# See the note in preprocessing/lipid_marginal_baseline.py: the pool samplers are pure
# pandas, torch is only there for the batch sampler, and analysis machines have neither.
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
from dataloader.sampler import (
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
