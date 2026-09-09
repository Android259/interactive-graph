"""One row per label: test balanced accuracy and AUC, with spread, over a label's runs.

Why this exists
---------------
`analysis/compare_labels.py` answers "A against B" and the leaderboard answers "one
metric, label x excluded set". Neither prints the plain thing a person asks for first --
a table of every variant of one line with its headline numbers and how much they move
between runs -- so that table kept being rebuilt by hand out of metrics_summary.csv.

Three spreads are printed because they answer different questions and are routinely
confused:

    std   how much the runs of this label differ from each other. On a label whose runs
          are (excluded group x seed) this is dominated by which group was held out, not
          by seed noise -- use --by-group to separate the two.
    SEM   how well the MEAN is pinned down = std / sqrt(n). The number to compare two
          labels with.
    n     how many runs are behind both. A label with 20 rows and one with 35 are not
          comparable spreads.

`AUC_within_protein_pairs` rides along as the last column without being the headline:
under --lipid_coldsplit every protein stays in training, so pooled BA/AUC are largely
"which protein is this" (pooled AUC 0.568 against 0.480 within protein on the same rows,
files/lipid_coldsplit_architecture_direction.md, the RULE box). Empty for runs before
2026-09-08, which is why it cannot simply replace the pooled columns here.

Reads only: opens metrics_summary.csv, writes nothing, runs no model.

Examples
--------
    python analysis/label_summary_table.py --preset solo
    python analysis/label_summary_table.py --preset lcs
    python analysis/label_summary_table.py --preset lcs --by-group
    python analysis/label_summary_table.py --contains geometric_edge_attention --sort BA
    python analysis/label_summary_table.py --labels label_a,label_b --date 2026-09-09
"""

import argparse
import csv
import math
import statistics
from collections import defaultdict

# Presets are substring filters, not fixed lists, so a new variant of a line shows up in
# the table the day it lands instead of the day somebody remembers to add it here.
PRESETS = {
    "solo": ("structural_pretrain_family",),
    "lcs": ("_lcs_esm3", "_lcs", "bbp_lcs"),
}
METRICS = [
    ("balanced_accuracy", "BA"),
    ("AUC", "AUC"),
    ("AUC_within_protein_pairs", "in-protein pairs"),
]


def to_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def spread(values):
    """(mean, sem, std, n) over the finite values, or (None, ...) when there are none."""
    values = [value for value in values if value is not None]
    if not values:
        return None, None, None, 0
    if len(values) == 1:
        return values[0], None, 0.0, 1
    std = statistics.stdev(values)
    return statistics.fmean(values), std / math.sqrt(len(values)), std, len(values)


def cell(mean, sem, std, n, width=26):
    if mean is None:
        return f"{'--':>{width}}"
    sem_text = "  --  " if sem is None else f"{sem:.3f}"
    return f"{f'{mean:.3f} ±{sem_text} sd{std:.3f} n{n}':>{width}}"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--table", default="metrics_summary.csv")
    parser.add_argument("--preset", choices=sorted(PRESETS),
                        help="substring filters for a known line (solo / lcs)")
    parser.add_argument("--contains", help="keep labels containing this substring")
    parser.add_argument("--labels", help="comma-separated exact label names")
    parser.add_argument("--date", help="keep only rows whose datetime starts with this "
                                       "prefix -- use it when a label was rerun and only "
                                       "the newest batch should count")
    parser.add_argument("--by-group", action="store_true",
                        help="one row per (label, excluded group) instead of one per label, "
                             "so group spread and seed spread stop being the same number")
    parser.add_argument("--drop-groups", default="",
                        help="comma-separated excluded groups to leave out (e.g. ML,OSBP -- "
                             "two test rows each, and one arm never finished them, so leaving "
                             "them in makes two labels' numbers stop being like for like)")
    parser.add_argument("--sort", default="label",
                        help="label (default), or a metric column name to sort by, descending")
    args = parser.parse_args()

    if args.labels:
        wanted = set(args.labels.split(","))
        keep = lambda label: label in wanted
    elif args.contains:
        keep = lambda label: args.contains in label
    elif args.preset:
        keep = lambda label: any(part in label for part in PRESETS[args.preset])
    else:
        raise SystemExit("give one of --preset / --contains / --labels")

    dropped = {name for name in args.drop_groups.split(",") if name}
    rows = defaultdict(list)
    groups = defaultdict(set)
    with open(args.table, newline="") as handle:
        for row in csv.DictReader(handle):
            if not keep(row["label"]):
                continue
            if args.date and not row["datetime"].startswith(args.date):
                continue
            if row["exclusion_set"].replace("groups_", "") in dropped:
                continue
            key = (row["label"], row["exclusion_set"]) if args.by_group else (row["label"], "")
            rows[key].append(row)
            groups[key].add(row["exclusion_set"])

    if not rows:
        raise SystemExit("no rows matched")

    summaries = {}
    for key, group_rows in rows.items():
        summaries[key] = {
            column: spread([to_float(row[column]) for row in group_rows])
            for column, _ in METRICS
        }

    order = sorted(rows)
    if args.sort != "label":
        column = next((c for c, name in METRICS if args.sort in (c, name)), args.sort)
        order = sorted(rows, key=lambda key: (summaries[key][column][0] is None,
                                              -(summaries[key][column][0] or 0)))

    # Labels on one line share a long prefix (the architecture they are all variants of);
    # printing it 17 times pushes the distinguishing suffix off the right edge, which is
    # the only part anyone reads. Printed once, above the table.
    common = ""
    names = sorted({key[0] for key in rows})
    if len(names) > 1:
        for index, character in enumerate(names[0]):
            if all(len(name) > index and name[index] == character for name in names):
                common += character
            else:
                break
        common = common.rsplit("_", 1)[0] + "_" if "_" in common else ""
    if common:
        print(f"common prefix: {common}\n")
    display = {key: (key[0][len(common):] if key[0].startswith(common) else key[0])
               for key in rows}
    name_width = min(max(len(text) for text in display.values()), 64)
    header = f"{'label':{name_width}}"
    if args.by_group:
        header += f"{'group':18}"
    header += f"{'runs':>6}{'grps':>6}" + "".join(f"{name:>26}" for _, name in METRICS)
    print(header)
    print("-" * len(header))
    for key in order:
        label, group = key
        text = display[key]
        # Truncated head, not tail: what distinguishes one variant of a line from another
        # is always the suffix (the flag that was changed), never the shared stem.
        if len(text) > name_width:
            text = "…" + text[-(name_width - 1):]
        line = f"{text:{name_width}}"
        if args.by_group:
            line += f"{group.replace('groups_', ''):18}"
        line += f"{len(rows[key]):>6}{len(groups[key]):>6}"
        for column, _ in METRICS:
            line += cell(*summaries[key][column])
        print(line)
    print("\n±SEM = std/sqrt(n) -- how well the mean is pinned down; sd = spread of the "
          "runs themselves.\nWithout --by-group the spread mixes excluded groups with "
          "seeds.")


if __name__ == "__main__":
    main()
