"""Where a label's results live: ``<root>/<family>/<label>/...``.

Every result tree -- run/, test_metrics/, models/, checkpoints/, script_logs/,
graphics/ -- is split by the same families as arg_files/: a label's family is the
arg_files/ subdirectory holding ``<label>.md`` (``arg_files/geometric_edge/ge_s15_x.md``
-> ``geometric_edge``). A label with no arg file (an ad hoc --label, or a config that
was deleted) files under ``unsorted``. The label itself stays the run's key everywhere
(metrics table, report names); the family is only a directory level above it.

scripts/lib/args_file_lib.sh has the shell twin of label_family(); the two must apply
the same rule.
"""

from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARG_FILES_DIR = PROJECT_ROOT / "arg_files"
UNSORTED_FAMILY = "unsorted"


@lru_cache(maxsize=None)
def label_family(label, arg_files_dir=ARG_FILES_DIR):
    """The arg_files/ subdirectory holding ``<label>.md``, or ``unsorted``."""
    arg_files_dir = Path(arg_files_dir)
    for match in sorted(arg_files_dir.glob(f"*/**/{label}.md")):
        return match.relative_to(arg_files_dir).parts[0]
    return UNSORTED_FAMILY


def label_dir(root, label):
    """``<root>/<family>/<label>`` for one result tree (run/, models/, ...)."""
    return Path(root) / label_family(label) / label


def label_dirs(root):
    """Every ``<root>/<family>/<label>`` directory that exists, as (family, label, path)."""
    root = Path(root)
    found = []
    if not root.is_dir():
        return found
    for family_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for label_path in sorted(p for p in family_dir.iterdir() if p.is_dir()):
            found.append((family_dir.name, label_path.name, label_path))
    return found


def split_result_path(relative_parts):
    """(family, label, rest) of a path relative to a result root.

    ``test_metrics/<family>/<label>/<set...>/<file>`` relative to ``test_metrics`` is
    ``(family, label, set..., file)``.
    """
    parts = tuple(relative_parts)
    if len(parts) < 3:
        raise ValueError(
            f"result path lacks <family>/<label>/ directories: {'/'.join(parts)}"
        )
    return parts[0], parts[1], parts[2:]


def known_families(arg_files_dir=ARG_FILES_DIR):
    """Family directory names a result tree may hold: arg_files/ subdirectories + unsorted."""
    arg_files_dir = Path(arg_files_dir)
    names = {p.name for p in arg_files_dir.iterdir() if p.is_dir()} if arg_files_dir.is_dir() else set()
    return names | {UNSORTED_FAMILY}


def in_family_layout(relative_parts, arg_files_dir=ARG_FILES_DIR):
    """True when a path under a result root starts with a known family directory.

    A tree synced from somewhere that still has the old ``<root>/<label>/...`` layout
    fails this, and readers skip it instead of reading the label as a family.
    scripts/tools/migrate_results_to_families.py moves such trees.
    """
    parts = tuple(relative_parts)
    return len(parts) >= 3 and parts[0] in known_families(arg_files_dir)
