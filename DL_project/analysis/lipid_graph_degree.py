#!/usr/bin/env python3
"""Mean degree of this project's lipid graphs -- the value --lipid_edge_mlp_lambda wants.

EdgeMLPConv (architecture/edge_geometric_conv.py, Dauparas et al. ProteinMPNN Sec 3.4.2)
aggregates a node's incoming messages as `sum(m_ij) / lambda` with lambda a CONSTANT, not
the node's actual degree. The paper's experimentally-found 30 is the mean degree of a
protein contact graph, which is what makes that division approximately a mean there.

Every --lipid_graph_isomers run in this project so far also used 30 on the LIPID graph,
because until --lipid_edge_mlp_lambda existed the divisor was shared with the protein
one. A molecule is not a contact graph: an atom has a handful of bonds, not thirty. This
script measures how many, so the flag is set from the data rather than from an estimate.

Reads only: counts rows in data/lipid_graphs/<hash>/{nodes,edges}.csv, parses nothing
else, builds no molecule, touches no GPU.

edges.csv stores BOTH directions of every bond (the first two rows of any file are
`0,1,...` and `1,0,...`), which is exactly what EdgeMLPConv sums over -- one message per
directed edge into the reference node -- so mean degree = edge rows / node rows, with no
factor of two to apply. The same file's `degree` column in nodes.csv is RDKit's
heavy-atom degree and is reported alongside as an independent check that the two agree.

Usage:
    scripts/env.sh python3 analysis/lipid_graph_degree.py
    scripts/env.sh python3 analysis/lipid_graph_degree.py --out /tmp/lipid_degrees.csv
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LIPID_GRAPH_ROOT = PROJECT_ROOT / "data" / "lipid_graphs"
# architecture/edge_geometric_conv.py's EdgeMLPConv default, and ModelConfig's.
PROTEIN_LAMBDA = 30.0


def graph_counts(graph_dir):
    """(nodes, directed_edges, mean RDKit degree) for one lipid, or None if incomplete."""
    nodes_path = graph_dir / "nodes.csv"
    edges_path = graph_dir / "edges.csv"
    if not (nodes_path.is_file() and edges_path.is_file()):
        return None
    with nodes_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return None
    with edges_path.open(newline="", encoding="utf-8") as handle:
        edge_count = sum(1 for _ in csv.reader(handle)) - 1  # minus the header
    rdkit_degrees = [float(row["degree"]) for row in rows if row.get("degree") not in (None, "")]
    mean_rdkit = statistics.fmean(rdkit_degrees) if rdkit_degrees else float("nan")
    return len(rows), max(edge_count, 0), mean_rdkit


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", help="write one row per lipid graph to this CSV")
    args = parser.parse_args()

    if not LIPID_GRAPH_ROOT.is_dir():
        raise SystemExit(f"no lipid graphs at {LIPID_GRAPH_ROOT}")

    rows = []
    for graph_dir in sorted(p for p in LIPID_GRAPH_ROOT.iterdir() if p.is_dir()):
        counts = graph_counts(graph_dir)
        if counts is None:
            continue
        nodes, edges, mean_rdkit = counts
        rows.append({
            "graph": graph_dir.name,
            "nodes": nodes,
            "directed_edges": edges,
            "mean_degree": edges / nodes,
            "mean_rdkit_degree": mean_rdkit,
        })

    if not rows:
        raise SystemExit(f"no readable lipid graphs under {LIPID_GRAPH_ROOT}")

    # Pooled over ATOMS, not over graphs: EdgeMLPConv divides once per node, so the
    # quantity lambda should match is the degree an average atom has, not the average
    # over molecules of their own per-molecule means (which would weight a 20-atom
    # molecule the same as a 150-atom one).
    total_nodes = sum(row["nodes"] for row in rows)
    total_edges = sum(row["directed_edges"] for row in rows)
    pooled = total_edges / total_nodes
    per_graph = [row["mean_degree"] for row in rows]

    print(f"lipid graphs read      : {len(rows)}  ({total_nodes} atoms, "
          f"{total_edges} directed edges)")
    print(f"pooled mean degree     : {pooled:.3f}   <- the value --lipid_edge_mlp_lambda wants")
    print(f"per-graph mean degree  : mean {statistics.fmean(per_graph):.3f}  "
          f"median {statistics.median(per_graph):.3f}  "
          f"min {min(per_graph):.3f}  max {max(per_graph):.3f}")
    print(f"RDKit `degree` column  : {statistics.fmean(r['mean_rdkit_degree'] for r in rows):.3f} "
          "(independent check, should track the pooled figure)")
    print()
    print(f"protein lambda in use  : {PROTEIN_LAMBDA:g}")
    print(f"ratio                  : {PROTEIN_LAMBDA / pooled:.1f}x -- how much smaller "
          "every lipid node update arrived while the divisor was shared")

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nwrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
