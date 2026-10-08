#!/usr/bin/env python3
"""Remove old-layout duplicates from models/.

models/ is written as ``models/<family>/<label>/<excluded_set>/`` (training/run_paths.py).
A tree synced from a cluster whose checkout predates that split arrives as
``models/<label>/<excluded_set>/`` instead, so the same weights end up stored twice --
once under the family directory and once directly under models/.

This deletes a file from the old-layout copy only when the new-layout counterpart
exists AND has the same size and the same sha256. Anything else is reported and left
alone: a file with no counterpart is the only copy of those weights, and a file whose
counterpart differs is not a duplicate at all.

Dry run by default; pass --apply to delete.

    python3 scripts/tools/dedupe_models.py
    python3 scripts/tools/dedupe_models.py --apply
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UNSORTED_FAMILY = "unsorted"
HASH_CHUNK = 1 << 20


def known_families(arg_files_dir: Path) -> set[str]:
    """Family directory names models/ may hold: arg_files/ subdirectories + unsorted."""
    names = {p.name for p in arg_files_dir.iterdir() if p.is_dir()} if arg_files_dir.is_dir() else set()
    return names | {UNSORTED_FAMILY}


def label_family(label: str, arg_files_dir: Path) -> str:
    """The arg_files/ subdirectory holding ``<label>.md``, or ``unsorted``.

    The same rule as training/results_layout.label_family(), repeated here so this
    script needs no PYTHONPATH and no torch -- it must stay runnable on a full disk.
    """
    for match in sorted(arg_files_dir.glob(f"*/**/{label}.md")):
        return match.relative_to(arg_files_dir).parts[0]
    return UNSORTED_FAMILY


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prune_empty_dirs(root: Path) -> None:
    """Drop directories left empty by the deletions, deepest first."""
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-root", type=Path, default=PROJECT_ROOT / "models")
    parser.add_argument("--arg-files-dir", type=Path, default=PROJECT_ROOT / "arg_files")
    parser.add_argument("--apply", action="store_true", help="actually delete (default: dry run)")
    args = parser.parse_args()

    models_root: Path = args.models_root
    if not models_root.is_dir():
        print(f"No models directory at {models_root}")
        return

    families = known_families(args.arg_files_dir)
    old_layout_dirs = sorted(
        p for p in models_root.iterdir() if p.is_dir() and p.name not in families
    )
    if not old_layout_dirs:
        print("No old-layout <label>/ directories under models/; nothing to deduplicate.")
        return

    duplicate_bytes = 0
    duplicates = 0
    only_copy = []
    differing = []

    for label_dir in old_layout_dirs:
        label = label_dir.name
        family = label_family(label, args.arg_files_dir)
        new_label_dir = models_root / family / label

        for old_file in sorted(p for p in label_dir.rglob("*") if p.is_file()):
            new_file = new_label_dir / old_file.relative_to(label_dir)
            if not new_file.is_file():
                only_copy.append(old_file)
                continue
            if old_file.stat().st_size != new_file.stat().st_size:
                differing.append((old_file, new_file))
                continue
            if file_hash(old_file) != file_hash(new_file):
                differing.append((old_file, new_file))
                continue

            duplicates += 1
            duplicate_bytes += old_file.stat().st_size
            if args.apply:
                old_file.unlink()

        if args.apply:
            prune_empty_dirs(label_dir)

    verb = "Deleted" if args.apply else "Would delete"
    print(f"{verb} {duplicates} duplicate files ({duplicate_bytes / 2**30:.2f} GiB).")

    if only_copy:
        print(f"\nKept -- no counterpart under models/<family>/ ({len(only_copy)} files, the only copy):")
        for path in only_copy[:20]:
            print(f"  {path.relative_to(models_root)}")
        if len(only_copy) > 20:
            print(f"  ... and {len(only_copy) - 20} more")
        print("  Move these with scripts/tools/migrate_results_to_families.py rather than deleting them.")

    if differing:
        print(f"\nKept -- counterpart exists but differs ({len(differing)} files, not duplicates):")
        for old_file, _ in differing[:20]:
            print(f"  {old_file.relative_to(models_root)}")
        if len(differing) > 20:
            print(f"  ... and {len(differing) - 20} more")

    if not args.apply and duplicates:
        print("\nDry run. Re-run with --apply to delete.")


if __name__ == "__main__":
    main()
