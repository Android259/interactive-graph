#!/usr/bin/env python3
"""Move result trees from <tree>/<label>/ to <tree>/<family>/<label>/.

The family of a label is the arg_files/ subdirectory holding <label>.md, or
"unsorted" (training/results_layout.py). Trees: run/, test_metrics/, models/,
checkpoints/, graphics/, script_logs/ and the same four under testmode_outputs/.
script_logs/ directories are named <label>_<axis> (e.g. ..._seeds01234,
..._species15); the axis suffix is stripped to find the label.

Idempotent: a directory that is already a family directory is left alone, so the
script can be re-run after a cluster sync brings in old-layout directories, and on
each cluster's own copy of the project. Files at the top of a tree, and directories
starting with "_" or "." (script_logs/_cross_label_packs/), stay where they are.

    python3 scripts/tools/migrate_results_to_families.py            # show the plan
    python3 scripts/tools/migrate_results_to_families.py --apply    # move
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from training.results_layout import known_families, label_family  # noqa: E402


TREES = (
    "run", "test_metrics", "models", "checkpoints", "graphics", "script_logs",
    "testmode_outputs/run", "testmode_outputs/test_metrics",
    "testmode_outputs/models", "testmode_outputs/checkpoints",
)
# Output-root suffixes the launchers append to a label under script_logs/
# (scripts/launch/submit_grid.sh, scripts/run_local.sh).
LOG_SUFFIX = re.compile(
    r"_(coldval_seeds\d+|seeds\d+|lipidsets|familyonly|random|subclass|"
    r"lipidsubclasses|iso.+|species\d+)$"
)


def label_of(tree, name):
    if tree.endswith("script_logs"):
        return LOG_SUFFIX.sub("", name)
    return name


def is_family_dir(tree, path, families):
    """A family directory holds only label directories of that family."""
    if path.name not in families:
        return False
    children = [child for child in path.iterdir() if child.is_dir()]
    return all(label_family(label_of(tree, child.name)) == path.name for child in children)


def merge_into(source, target, apply, conflicts):
    """Move source's entries into an existing target, never overwriting."""
    for entry in sorted(source.iterdir()):
        destination = target / entry.name
        if destination.exists():
            if entry.is_dir() and destination.is_dir():
                merge_into(entry, destination, apply, conflicts)
            else:
                conflicts.append(str(entry))
            continue
        if apply:
            shutil.move(str(entry), str(destination))
    if apply:
        try:
            source.rmdir()
        except OSError:
            pass


def migrate_tree(tree, apply):
    root = PROJECT_ROOT / tree
    if not root.is_dir():
        return 0, []
    families = known_families()
    moved, conflicts = 0, []
    # Labels named like a family directory go first: until they have stepped aside,
    # their directory occupies the path every other label of that family moves into.
    for path in sorted(
        (p for p in root.iterdir() if p.is_dir()),
        key=lambda p: (p.name not in families, p.name),
    ):
        if path.name.startswith(("_", ".")) or is_family_dir(tree, path, families):
            continue
        family = label_family(label_of(tree, path.name))
        target = root / family / path.name
        moved += 1
        if not apply:
            print(f"  {tree}/{path.name} -> {tree}/{family}/{path.name}")
            continue
        if path.name == family:
            # A label named like its own family (arg_files/descriptors/descriptors.md):
            # step aside first, then create the family directory and move in.
            aside = root / f".{path.name}.migrating"
            path.rename(aside)
            (root / family).mkdir(exist_ok=True)
            aside.rename(target)
        elif target.exists():
            merge_into(path, target, apply, conflicts)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
    return moved, conflicts


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="move (default: show the plan)")
    args = parser.parse_args()
    total = 0
    for tree in TREES:
        moved, conflicts = migrate_tree(tree, args.apply)
        total += moved
        if moved or conflicts:
            print(f"{tree}: {moved} director{'y' if moved == 1 else 'ies'}"
                  f"{' moved' if args.apply else ' to move'}")
        for item in conflicts:
            print(f"  NOT MOVED (exists at target): {item}")
    if not args.apply:
        print(f"{total} directories would move; rerun with --apply")


if __name__ == "__main__":
    main()
