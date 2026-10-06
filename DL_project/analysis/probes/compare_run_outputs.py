#!/usr/bin/env python3
"""Are two training runs the same run? Checkpoints bit for bit, reports line for line.

Written to check a change that must not move any number (the --deepclip preassembled
loader, dataloader/preassembled_loader.py): run the same arg file on the code before and
after, then point this at the two outputs.

    python3 analysis/probes/compare_run_outputs.py OLD.pt NEW.pt OLD_test_metrics.txt NEW_test_metrics.txt

Checkpoints: every tensor compared with torch.equal -- equal, not close. Reports: every
line compared verbatim except the ones that legitimately differ between two otherwise
identical runs (wall-clock durations, timestamps, the label, and paths containing it).
Exit status 0 only when everything matches.
"""

import re
import sys

import torch

# Lines that differ between two runs of the same computation: how long it took, when
# it ran, and the label/paths the comparison itself had to make distinct.
VOLATILE = re.compile(
    r"duration|_sec\b|seconds|time|date|timestamp|label|path|/|train\d{8}_\d{6}",
    re.IGNORECASE,
)


def compare_checkpoints(old_path, new_path):
    old = torch.load(old_path, map_location="cpu")
    new = torch.load(new_path, map_location="cpu")
    problems = []
    if old.keys() != new.keys():
        problems.append(f"parameter names differ: {sorted(old.keys() ^ new.keys())}")
    for key in sorted(old.keys() & new.keys()):
        if not torch.equal(old[key], new[key]):
            difference = (old[key].double() - new[key].double()).abs().max().item()
            problems.append(f"{key}: max |difference| {difference:.3e}")
    return problems, len(old)


def compare_reports(old_path, new_path):
    def lines(path):
        with open(path) as handle:
            return [line.rstrip("\n") for line in handle if not VOLATILE.search(line)]

    old, new = lines(old_path), lines(new_path)
    problems = [
        f"line {number}: {a!r} != {b!r}"
        for number, (a, b) in enumerate(zip(old, new), start=1)
        if a != b
    ]
    if len(old) != len(new):
        problems.append(f"line counts differ: {len(old)} vs {len(new)}")
    return problems, len(old)


def main(argv):
    if len(argv) != 5:
        print(__doc__)
        return 2
    checkpoint_problems, tensors = compare_checkpoints(argv[1], argv[2])
    report_problems, report_lines = compare_reports(argv[3], argv[4])
    print(f"checkpoint: {tensors} tensors, {len(checkpoint_problems)} differ")
    for problem in checkpoint_problems:
        print(f"  {problem}")
    print(f"report: {report_lines} lines compared, {len(report_problems)} differ")
    for problem in report_problems:
        print(f"  {problem}")
    return 0 if not (checkpoint_problems or report_problems) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
