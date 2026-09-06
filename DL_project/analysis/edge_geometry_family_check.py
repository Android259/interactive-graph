#!/usr/bin/env python3
"""How much the structured protein-edge geometry vector already *is* family identity.

descriptor_catalog.md section 6 flags this as the one open measurement gap left over
from the family-neutral-descriptor exercise: every one of the 15 PROTEIN_DESCRIPTOR_NAMES
(section 2) has a measured eta^2 against protein family, and the 7 lowest ones were
picked as the "family-neutral" set every geometric_edge_*_family_neutral* baseline uses
-- but the 25-dim structured edge vector that --protein_edge_mlp/--protein_edge_attention
also feeds the network (architecture/protein_edge_geometry.py: 16-bin distance RBF, a
3-dim local direction, a 4-dim relative-orientation quaternion, log-area, log-boundary-
ratio) has never had the same check. This script closes that gap with the same method
(analysis/feature_identity_check.py's own eta_squared, reused rather than reimplemented),
applied to the only thing that makes an edge-level vector comparable across proteins
with different residue counts: per-pocket mean/std of each of the 25 columns, across
every directed contact edge inside that protein's pocket.

Pocket-only, on purpose, to match section 2's own subject (the binding cavity), even
though the current family-neutral baselines do not set --protein_pockets_only
themselves -- this script forces it on its own throwaway config so "pocket edge
geometry" means the same 33-residue-median subgraph section 2's own descriptors are
computed over, not the whole ~200-residue protein contact graph.

Usage:
    scripts/env.sh python3 analysis/edge_geometry_family_check.py
    scripts/env.sh python3 analysis/edge_geometry_family_check.py --out edge_geometry_family_eta2.csv

Reads only (per-protein CSVs/PDB already on disk via the project's own
ProteinGraphBuilder.protein_graph_tensors). Trains nothing, appends to no shared table.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))
sys.path.insert(0, PROJECT_ROOT)

from read_configuration import read_configuration  # noqa: E402

from architecture.protein_edge_geometry import structured_edge_features  # noqa: E402
from dataloader.protein_graph_builder import ProteinGraphBuilder  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from analysis.checkpoint_scores import arg_lines  # noqa: E402
from analysis.feature_identity_check import eta_squared, protein_family_map  # noqa: E402

GRAPH_ROOT = os.path.join(PROJECT_ROOT, "data", "graphs")
BASELINE_LABEL = "geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm"

_RBF_CENTERS = np.linspace(2.0, 22.0, 16)
COLUMN_NAMES = (
    [f"rbf_{center:.1f}A" for center in _RBF_CENTERS]
    + ["dir_x", "dir_y", "dir_z"]
    + ["quat_0", "quat_1", "quat_2", "quat_3"]
    + ["log_area", "log_boundary_ratio"]
)


class _Builder(ProteinGraphBuilder):
    """Bare instance carrying only the .config protein_graph_tensors reads."""

    def __init__(self, config):
        self.config = config


def build_config():
    """The real family-neutral baseline config, plus --protein_pockets_only so the
    edge geometry this script measures is restricted to the pocket subgraph (see
    module docstring) -- everything else (protein_edge_mlp, no structured-edge-
    incompatible flags) comes straight from the baseline's own arg file so this is
    provably the same edge geometry that baseline's --protein_edge_mlp consumes.
    """
    argv = (
        ["edge_geometry_family_check"]
        + arg_lines(BASELINE_LABEL)
        + ["--protein_pockets_only"]
        # This script never touches PLIDataset/the coldsplit itself -- it calls
        # protein_graph_tensors() directly per protein -- but the baseline's own
        # --double_coldsplit still requires a nonempty --excluded_groups to pass
        # validate(). The value is otherwise inert here.
        + ["--excluded_groups=LBP_BPI_CETP"]
    )
    return read_configuration(argv)


def pocket_edge_columns(protein, builder):
    """[2E, 25] structured edge vector for one protein's pocket subgraph, both
    directions, default RBF count / quaternion (no --protein_edge_rbf_count /
    --protein_edge_orientation_scalar override -- this measures the vector the
    family-neutral baselines actually use today).
    """
    protein_dir = os.path.join(GRAPH_ROOT, protein)
    nodes = os.path.join(protein_dir, "coarse_graph_nodes.csv")
    edges = os.path.join(protein_dir, "coarse_graph_links.csv")
    pocketness = os.path.join(protein_dir, "pocketness.pdb")
    num_residues = len(pd.read_csv(nodes))
    plm = torch.zeros(num_residues, 1)
    parts = builder.protein_graph_tensors(nodes, edges, plm, pocketness)
    _, e_attr = structured_edge_features(
        parts["edge_index"], parts["frame_rotation"], parts["frame_translation"],
        parts["edge_attr"],
    )
    return e_attr.numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="write the full eta^2 table to this CSV")
    args = parser.parse_args()

    csv = pd.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    family_map = protein_family_map(csv)
    config = build_config()
    builder = _Builder(config)

    rows = []
    skipped = []
    for protein, family in sorted(family_map.items()):
        try:
            values = pocket_edge_columns(protein, builder)
        except (FileNotFoundError, ValueError) as error:
            skipped.append((protein, str(error)))
            continue
        if values.shape[0] == 0:
            skipped.append((protein, "no pocket-internal contact edges"))
            continue
        row = {"protein": protein, "family": family, "n_directed_edges": values.shape[0]}
        for i, name in enumerate(COLUMN_NAMES):
            row[f"{name}_mean"] = float(values[:, i].mean())
            row[f"{name}_std"] = float(values[:, i].std())
        rows.append(row)

    if skipped:
        print(f"skipped {len(skipped)} protein(s):")
        for protein, reason in skipped:
            print(f"  {protein}: {reason}")

    frame = pd.DataFrame(rows)
    n = len(frame)
    k = frame["family"].nunique()
    floor = (k - 1) / (n - 1) if n > 1 else float("nan")
    print(f"\n{n} proteins, {k} families, eta^2 chance floor (k-1)/(n-1) = {floor:.3f}\n")

    results = []
    for name in COLUMN_NAMES:
        for stat in ("mean", "std"):
            column = f"{name}_{stat}"
            results.append({
                "column": column,
                "eta2_family": eta_squared(frame[column].values, frame["family"].values),
            })
    result_frame = pd.DataFrame(results).sort_values("eta2_family", ascending=False)
    print(result_frame.round(3).to_string(index=False))

    if args.out:
        result_frame.to_csv(args.out, index=False)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
