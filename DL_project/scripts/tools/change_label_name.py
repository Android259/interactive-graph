#!/usr/bin/env python3
"""Rename a run label everywhere it has already appeared in the project.

Usage: change_label_name.py OLD NEW

OLD is the config name as the launchers accept it: a bare stem
(``ge_s15_prothid32_hid64_noreg``), ``<stem>.md`` or a path to the arg file. NEW is
a bare stem.

What changes:

- the config itself: ``arg_files/<family>/OLD.md`` -> ``NEW.md`` (same subdirectory,
  so the family, and with it every ``<tree>/<family>/`` level, stays the same);
- result directories in run/, test_metrics/, models/, checkpoints/, graphics/,
  script_logs/ (and the same trees under testmode_outputs/), in both the flat
  ``<tree>/OLD/`` and the family ``<tree>/<family>/OLD/`` layout
  (training/results_layout.py); script_logs also has ``OLD_seeds<...>/``;
- file names inside the label's graphics/ and script_logs/ directories that start
  with the label (``OLD.md``, ``OLD_split_similarity_*.png``, ``OLD_seed0_*.log``),
  and links to those files in text;
- every text file of the project that mentions the label: metrics_summary.csv and
  the other tables, ``label: OLD`` in test reports, ``--label=OLD`` in
  ``models/**/*.args.json``, logs, graphics reports, files/*.md, other configs'
  comments, scripts.

A mention counts only as a whole name: the characters around it must not be
letters, digits, ``_`` or ``-`` (``OLD_seed1``/``OLD_seeds01234`` are the one
allowed continuation), and a longer existing label that starts with OLD
(``OLD_lre-5``) is never touched.

Not changed: binary files (TensorBoard event files, ``*.pt`` weights) -- they are
listed so you know the old name survives inside them -- and data/, .git/,
external/ and the stale DL_project/ copy.

A run still going on a cluster keeps writing under OLD there; the next sync brings
the old name back. Rename after the label's jobs have finished and been synced.
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import os
import re
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from training.results_layout import ARG_FILES_DIR, known_families  # noqa: E402

RESULT_TREES = ("run", "test_metrics", "models", "checkpoints", "graphics", "script_logs")
ARTIFACT_ROOTS = (PROJECT_ROOT, PROJECT_ROOT / "testmode_outputs")
# Trees whose file names carry the label; in the others names are fixed
# (test_metrics_*.txt, train<timestamp>_*, seed<N>.pt) and a short label such as
# "test" would otherwise eat the "test_" of "test_metrics_".
NAME_CARRYING_TREES = ("graphics", "script_logs")

SKIP_DIRS = {".git", "external", "DL_project", "data", "__pycache__"}
BINARY_SUFFIXES = {
    ".pt", ".pth", ".ckpt", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".npy", ".npz",
    ".pkl", ".pickle", ".h5", ".hdf5", ".gz", ".zip", ".tar", ".so", ".pyc", ".bin",
    ".parquet", ".feather",
}
LABEL_CHARS = "A-Za-z0-9_\\-"
VALID_LABEL = re.compile(f"^[{LABEL_CHARS}.]+$")


def resolve_old_label(name: str) -> tuple[str, Path | None]:
    """Label stem and its arg file (None when the config no longer exists)."""
    path = Path(name)
    if path.is_file():
        return path.stem, path.resolve()
    stem = name[:-3] if name.endswith(".md") else name
    matches = sorted(ARG_FILES_DIR.rglob(f"{stem}.md"))
    if len(matches) > 1:
        raise SystemExit(f"ambiguous config name {stem}: " + ", ".join(map(str, matches)))
    return stem, (matches[0] if matches else None)


def label_dir_candidates(tree: Path, families: set[str]) -> list[Path]:
    """Directories of a result tree that may be a label: <tree>/X and <tree>/<family>/X."""
    found = []
    if not tree.is_dir():
        return found
    for entry in tree.iterdir():
        if not entry.is_dir():
            continue
        found.append(entry)
        if entry.name in families:
            found.extend(sub for sub in entry.iterdir() if sub.is_dir())
    return found


def strip_seeds_axis(name: str) -> str:
    return re.sub(r"_seeds\w*$", "", name)


def collect_known_labels(families: set[str]) -> set[str]:
    labels = {path.stem for path in ARG_FILES_DIR.rglob("*.md")}
    for root in ARTIFACT_ROOTS:
        for tree_name in RESULT_TREES:
            for path in label_dir_candidates(root / tree_name, families):
                labels.add(strip_seeds_axis(path.name) if tree_name == "script_logs" else path.name)
        table = root / "results" / "tables" / "metrics_summary.csv"
        if table.is_file():
            with open(table, newline="", encoding="utf-8") as handle:
                labels.update(row.get("label", "") for row in csv.DictReader(handle))
    labels.discard("")
    return labels


class LabelMatcher:
    """Whole-name occurrences of one label, never the prefix of a longer known label."""

    def __init__(self, old: str, known_labels: set[str]):
        self.old = old
        self.pattern = re.compile(
            f"(?<![{LABEL_CHARS}]){re.escape(old)}(?=$|[^{LABEL_CHARS}]|_seeds?\\d)"
        )
        self.longer = sorted(
            (label for label in known_labels if label != old and label.startswith(old)),
            key=len,
            reverse=True,
        )
        self.file_names = None

    def add_file_names(self, names: dict[str, str]) -> None:
        """Renamed file names (OLD_split_similarity_FP_share.png): links to them follow."""
        self.file_names = names
        if names:
            alternation = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
            self.file_names_pattern = re.compile(f"(?<![{LABEL_CHARS}])(?:{alternation})(?![{LABEL_CHARS}])")

    def _is_longer_label(self, text: str, start: int) -> bool:
        for label in self.longer:
            end = start + len(label)
            if text.startswith(label, start) and (end == len(text) or not re.match(f"[{LABEL_CHARS}]", text[end])):
                return True
        return False

    def substitute(self, text: str, new: str) -> tuple[str, int]:
        count = 0
        if self.file_names:
            def replace_name(match: re.Match) -> str:
                nonlocal count
                count += 1
                return self.file_names[match.group(0)]

            text = self.file_names_pattern.sub(replace_name, text)

        def replace(match: re.Match) -> str:
            nonlocal count
            if self._is_longer_label(text, match.start()):
                return match.group(0)
            count += 1
            return new

        return self.pattern.sub(replace, text), count

    def renamed_file_name(self, name: str, new: str) -> str | None:
        """New name for a file inside the label's own directory, or None."""
        if name == self.old:
            return new
        if len(name) > len(self.old) and name.startswith(self.old) and name[len(self.old)] in "_.-":
            if self._is_longer_label(name, 0):
                return None
            return new + name[len(self.old):]
        return None


def plan_renames(old: str, new: str, matcher: LabelMatcher, families: set[str]) -> list[tuple[Path, Path]]:
    """(source, target) pairs, deepest first so a parent moves after its children."""
    seeds_axis = re.compile(f"^{re.escape(old)}(_seeds\\w*)?$")
    renames = []
    for root in ARTIFACT_ROOTS:
        for tree_name in RESULT_TREES:
            for label_path in label_dir_candidates(root / tree_name, families):
                if tree_name == "script_logs":
                    match = seeds_axis.match(label_path.name)
                    if match is None:
                        continue
                    target_name = new + (match.group(1) or "")
                elif label_path.name == old:
                    target_name = new
                else:
                    continue
                if tree_name in NAME_CARRYING_TREES:
                    for dirpath, dirnames, filenames in os.walk(label_path, topdown=False):
                        for name in filenames + dirnames:
                            renamed = matcher.renamed_file_name(name, new)
                            if renamed is not None:
                                renames.append((Path(dirpath) / name, Path(dirpath) / renamed))
                renames.append((label_path, label_path.with_name(target_name)))
    return renames


def is_binary(path: Path, data: bytes) -> bool:
    return (
        path.suffix.lower() in BINARY_SUFFIXES
        or path.name.startswith("events.out.tfevents")
        or b"\0" in data[:8192]
    )


def plan_content_edits(old: str, new: str, matcher: LabelMatcher):
    """(path, new text, count) for text files, plus binary files that mention the label."""
    edits, binary_mentions = [], []
    needle = old.encode("utf-8")
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        if Path(dirpath) == PROJECT_ROOT:
            dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        else:
            dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__"}]
        for name in filenames:
            path = Path(dirpath) / name
            # Leftover tempfiles of an interrupted metrics_summary.csv write, and locks.
            if name.startswith(".metrics_summary.csv.") or name.endswith(".lock"):
                continue
            if path.suffix.lower() in BINARY_SUFFIXES or name.startswith("events.out.tfevents"):
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if needle not in data:
                continue
            if is_binary(path, data):
                binary_mentions.append(path)
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                binary_mentions.append(path)
                continue
            updated, count = matcher.substitute(text, new)
            if count:
                edits.append((path, updated, count))
    return edits, binary_mentions


def write_atomically(path: Path, text: str) -> None:
    mode = path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(text)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, path)
    os.chmod(path, mode)


def apply_content_edit(path: Path, old: str, new: str, matcher: LabelMatcher) -> None:
    # metrics_summary.csv is rewritten by the watcher under this lock
    # (analysis/build_metrics_table.py upsert_row); re-read inside it so a row
    # added since the plan is not lost.
    if path.name == "metrics_summary.csv":
        with open(f"{path}.lock", "w") as lock_handle:
            fcntl.flock(lock_handle, fcntl.LOCK_EX)
            try:
                text = path.read_text(encoding="utf-8")
                write_atomically(path, matcher.substitute(text, new)[0])
            finally:
                fcntl.flock(lock_handle, fcntl.LOCK_UN)
        return
    text = path.read_bytes().decode("utf-8")
    write_atomically(path, matcher.substitute(text, new)[0])


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("old", help="current label: bare name, <name>.md or path to the arg file")
    parser.add_argument("new", help="new label, bare name")
    args = parser.parse_args()

    old, arg_file = resolve_old_label(args.old)
    new = args.new[:-3] if args.new.endswith(".md") else args.new
    if not VALID_LABEL.match(new):
        raise SystemExit(f"new label {new!r} may contain only letters, digits, '_', '-', '.'")
    if new == old:
        raise SystemExit("old and new labels are the same")

    families = known_families()
    known_labels = collect_known_labels(families)
    if new in known_labels:
        raise SystemExit(f"label {new} already exists (config, result directory or metrics_summary row)")
    if old not in known_labels:
        raise SystemExit(f"label {old} not found: no config, no result directory, no metrics_summary row")
    if arg_file is None:
        print(f"note: no arg file for {old}; only its results are renamed")

    matcher = LabelMatcher(old, known_labels)
    renames = plan_renames(old, new, matcher, families)
    matcher.add_file_names(
        {source.name: target.name for source, target in renames if source.name not in (old, f"{old}.md")}
    )
    if arg_file is not None:
        renames.append((arg_file, arg_file.with_name(f"{new}.md")))
    edits, binary_mentions = plan_content_edits(old, new, matcher)

    collisions = [target for _, target in renames if target.exists()]
    if collisions:
        raise SystemExit("targets already exist:\n  " + "\n  ".join(map(relative, collisions)))

    print(f"{old} -> {new}\n")
    print(f"Renames ({len(renames)}):")
    for source, target in renames:
        print(f"  {relative(source)}\n    -> {relative(target)}")
    print(f"\nText files with the name inside ({len(edits)}, {sum(c for _, _, c in edits)} mentions):")
    for path, _, count in edits:
        print(f"  {relative(path)}  ({count})")
    if binary_mentions:
        print(f"\nBinary files that mention {old} and stay as they are ({len(binary_mentions)}):")
        for path in binary_mentions:
            print(f"  {relative(path)}")

    # Contents first, at the paths just scanned; then move files and directories.
    for path, _, _ in edits:
        apply_content_edit(path, old, new, matcher)
    for source, target in renames:
        source.rename(target)
    print(f"\nDone: {len(edits)} files edited, {len(renames)} paths renamed.")


if __name__ == "__main__":
    main()
