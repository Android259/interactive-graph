#!/usr/bin/env python3
"""Per-epoch training dynamics from TensorBoard run logs.

End-point statistics (final / mean / max over a run) wash out the *dynamics*:
a validation-sensitivity collapse that develops over training is hidden behind
noisy early epochs. This tool reads the per-epoch scalars straight from the
TensorBoard event files and surfaces the trajectory instead of a summary number:

  * binned per-epoch trajectory of each metric, averaged across a run family;
  * per-run early->late delta of validation sensitivity (does it learn, stay
    flat, or collapse?), so aggregation does not hide per-run behaviour;
  * optional paired comparison of two run families matched on (group, seed).

Layout assumed (leave-one-group-out sweeps):
    <run_root>/<label>/groups_<GROUP>/train<...>parameters_<m>_<HEADS>_<seed>_..._<hiddim>/
        events.out.tfevents.*
Runs without the groups_ level (group="") and a label pointing straight at a
single run directory are both handled.

Examples:
    python analysis/run_dynamics.py my_experiment
    python analysis/run_dynamics.py grl_label baseline_label lipidonly_label
    python analysis/run_dynamics.py grl_label --baseline baseline_label
    python analysis/run_dynamics.py exp --metrics vsens vba --nbins 15 --maxep 200
"""
from __future__ import annotations

import argparse
import glob
import os
import statistics
from pathlib import Path

# Short key -> TensorBoard scalar tag. Extend freely; unknown tags are skipped.
EPOCH_SERIES = {
    "vsens": "epoch/valid sensitivity",
    "vspec": "epoch/valid specificity",
    "vba": "epoch/valid balanced_accuracy",
    "vloss": "epoch/valid loss",
    "tsens": "epoch/train sensitivity",
    "tspec": "epoch/train specificity",
    "tba": "epoch/train balanced_accuracy",
    "tloss": "epoch/train loss",
}
LABELS = {
    "vsens": "valid SENS", "vspec": "valid SPEC", "vba": "valid BA",
    "vloss": "valid LOSS", "tsens": "train SENS", "tspec": "train SPEC",
    "tba": "train BA", "tloss": "train LOSS",
}
DEFAULT_ROOT = str(Path(__file__).resolve().parent.parent / "run")


def parse_seed(run_dir: str) -> str:
    """Seed = 3rd underscore token after 'parameters_' (m, HEADS, seed, ...)."""
    name = os.path.basename(run_dir.rstrip(os.sep))
    if "parameters_" in name:
        tail = name.split("parameters_", 1)[1].split("_")
        if len(tail) >= 3:
            return tail[2]
    return "?"


def parse_group(run_dir: str) -> str:
    for part in Path(run_dir).parts:
        if part.startswith("groups_"):
            return part[len("groups_"):]
    return ""


def discover_runs(root: str, label: str) -> list[str]:
    """Return every run directory (holding tfevents) under a run family label."""
    base = os.path.join(root, label)
    dirs = sorted(glob.glob(os.path.join(base, "groups_*", "train*")))
    if not dirs:
        dirs = sorted(glob.glob(os.path.join(base, "train*")))
    if not dirs and glob.glob(os.path.join(base, "events.out.tfevents.*")):
        dirs = [base]
    return [d for d in dirs if glob.glob(os.path.join(d, "events.out.tfevents.*"))]


def load_run(run_dir: str) -> dict[str, list[float]]:
    """Per-epoch value lists (step-ordered) for every known scalar present."""
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

    acc = EventAccumulator(run_dir, size_guidance={"scalars": 0})
    acc.Reload()
    available = set(acc.Tags().get("scalars", []))
    out: dict[str, list[float]] = {}
    for key, tag in EPOCH_SERIES.items():
        if tag in available:
            events = sorted(acc.Scalars(tag), key=lambda e: e.step)
            out[key] = [e.value for e in events]
    return out


def load_experiment(root: str, label: str) -> list[dict]:
    runs = []
    for run_dir in discover_runs(root, label):
        series = load_run(run_dir)
        if series:
            runs.append({
                "group": parse_group(run_dir),
                "seed": parse_seed(run_dir),
                "series": series,
                "dir": run_dir,
            })
    return runs


def _finite(xs):
    return [x for x in xs if x == x]


def nanmean(xs) -> float:
    xs = _finite(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def binned_trajectory(runs, key, nbins, maxep):
    """Cross-run mean of `key`, averaged within nbins equal epoch windows."""
    width = max(1, maxep // nbins)
    bins = []
    for b in range(nbins):
        lo, hi = b * width, (b + 1) * width
        per_run = [nanmean(r["series"].get(key, [])[lo:hi]) for r in runs]
        bins.append(nanmean(per_run))
    return bins, width


def per_run_summary(runs, key, early, late):
    rows = []
    for r in runs:
        seq = r["series"].get(key, [])
        if not seq:
            continue
        e = nanmean(seq[early[0]:early[1]])
        l = nanmean(seq[late[0]:late[1]])
        peak = max(_finite(seq), default=float("nan"))
        rows.append((r["group"], r["seed"], e, l, l - e, peak))
    return rows


def max_valid_ba(runs):
    return [max(_finite(r["series"].get("vba", [])), default=float("nan")) for r in runs]


def print_trajectories(runs, metrics, nbins, maxep):
    width = max(1, maxep // nbins)
    header = "".join(f"{f'{b*width+1}-{(b+1)*width}':>9}" for b in range(nbins))
    print(f"{'epoch-bin':>11} |" + header)
    for key in metrics:
        bins, _ = binned_trajectory(runs, key, nbins, maxep)
        print(f"{LABELS.get(key, key):>11} |" + "".join(f"{b:>9.3f}" for b in bins))


def print_per_run_vsens(runs, early, late, rise_thresh=0.05):
    print(f"\n  per-run VALID SENSITIVITY  early(ep{early[0]+1}-{early[1]}) -> "
          f"late(ep{late[0]+1}-{late[1]}), peak:")
    rows = per_run_summary(runs, "vsens", early, late)
    rising = 0
    for group, seed, e, l, d, peak in rows:
        flag = "UP  " if d > rise_thresh else ("down" if d < -rise_thresh else "flat")
        rising += d > rise_thresh
        print(f"    {group:>14} s{seed}  early={e:.3f} late={l:.3f} "
              f"d={d:+.3f} peak={peak:.3f}  {flag}")
    early_m = nanmean([r[2] for r in rows])
    late_m = nanmean([r[3] for r in rows])
    print(f"  -> valid sens rises >{rise_thresh:+.2f} early->late in {rising}/{len(rows)} runs")
    print(f"  MEAN valid sens: early={early_m:.3f} late={late_m:.3f} "
          f"delta={late_m - early_m:+.3f}")
    return rows


def analyze(root, label, metrics, nbins, maxep, early, late, title=None):
    runs = load_experiment(root, label)
    print(f"\n{'=' * 96}\n{title or label}   [{label}]   nruns={len(runs)}\n{'=' * 96}")
    if not runs:
        print("  (no runs found)")
        return runs
    print_trajectories(runs, metrics, nbins, maxep)
    print_per_run_vsens(runs, early, late)
    mvba = max_valid_ba(runs)
    print(f"  mean max valid BA (checkpoint proxy): {nanmean(mvba):.3f}")
    return runs


def paired_comparison(root, label_a, label_b, late):
    """Match runs on (group, seed) and report A-B deltas on key late metrics."""
    a = {(r["group"], r["seed"]): r for r in load_experiment(root, label_a)}
    b = {(r["group"], r["seed"]): r for r in load_experiment(root, label_b)}
    keys = sorted(set(a) & set(b))
    print(f"\n{'#' * 96}\nPAIRED  {label_a}  -  {label_b}   (matched (group,seed) pairs: {len(keys)})\n{'#' * 96}")
    if not keys:
        print("  (no matching pairs)")
        return

    def late_mean(run, key):
        return nanmean(run["series"].get(key, [])[late[0]:late[1]])

    metrics = [("vsens", "late valid SENS"), ("vba", "late valid BA"),
               ("vspec", "late valid SPEC")]
    metrics += [("__maxvba", "max valid BA")]
    print(f"    {'group':>14} {'seed':>4} | " +
          " | ".join(f"{name:>16}" for _, name in metrics))
    deltas = {k: [] for k, _ in metrics}
    for group, seed in keys:
        cells = []
        for key, _ in metrics:
            if key == "__maxvba":
                va = max(_finite(a[(group, seed)]["series"].get("vba", [])), default=float("nan"))
                vb = max(_finite(b[(group, seed)]["series"].get("vba", [])), default=float("nan"))
            else:
                va = late_mean(a[(group, seed)], key)
                vb = late_mean(b[(group, seed)], key)
            d = va - vb
            deltas[key].append(d)
            cells.append(f"{va:.3f}/{vb:.3f} {d:+.3f}")
        print(f"    {group:>14} {seed:>4} | " + " | ".join(f"{c:>16}" for c in cells))
    print("    " + "-" * 88)
    for key, name in metrics:
        ds = _finite(deltas[key])
        pos = sum(d > 0 for d in ds)
        med = statistics.median(ds) if ds else float("nan")
        print(f"    {name:>16}:  mean d={nanmean(ds):+.3f}  median d={med:+.3f}  "
              f"A>B in {pos}/{len(ds)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels", nargs="+", help="run-family label(s) under --run-root")
    ap.add_argument("--run-root", default=DEFAULT_ROOT)
    ap.add_argument("--baseline", default=None,
                    help="if set, pair every label against this label on (group,seed)")
    ap.add_argument("--metrics", nargs="+", default=["vsens", "vspec", "vba", "tsens", "tba", "vloss"],
                    choices=list(EPOCH_SERIES))
    ap.add_argument("--nbins", type=int, default=10)
    ap.add_argument("--maxep", type=int, default=150)
    ap.add_argument("--early", type=int, nargs=2, default=(0, 15), metavar=("LO", "HI"))
    ap.add_argument("--late", type=int, nargs=2, default=(120, 150), metavar=("LO", "HI"))
    args = ap.parse_args()

    for label in args.labels:
        analyze(args.run_root, label, args.metrics, args.nbins, args.maxep,
                tuple(args.early), tuple(args.late))
    if args.baseline:
        analyze(args.run_root, args.baseline, args.metrics, args.nbins, args.maxep,
                tuple(args.early), tuple(args.late), title="BASELINE")
        for label in args.labels:
            if label != args.baseline:
                paired_comparison(args.run_root, label, args.baseline, tuple(args.late))


if __name__ == "__main__":
    main()
