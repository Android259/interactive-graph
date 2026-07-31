"""Precompute node inputs for the optional protein geometric transformer."""

from pathlib import Path

import numpy as np
import pandas


ROOT = Path(__file__).resolve().parents[1]
GRAPHS_DIR = ROOT / "data" / "graphs"
OUTPUT_NAME = "geometric_transformer_nodes.csv"
MAX_INCIDENT_EDGES = 21
QUANTILES = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)


def _clean_id(value):
    value = str(value).strip()
    return "" if value in {"", ".", "nan"} else value


def _node_key(chain, residue, insertion_code):
    return (_clean_id(chain), int(residue), _clean_id(insertion_code))


def read_backbone(pdb_path):
    backbone = {}
    with open(pdb_path, "r") as handle:
        for line in handle:
            if not line.startswith(("ATOM  ", "HETATM")):
                continue
            atom = line[12:16].strip()
            if atom not in {"N", "CA", "C"}:
                continue
            if line[16].strip() not in {"", "A"}:
                continue
            key = _node_key(line[21], line[22:26], line[26])
            backbone.setdefault(key, {})[atom] = np.asarray(
                [
                    float(line[30:38]),
                    float(line[38:46]),
                    float(line[46:54]),
                ],
                dtype=np.float64,
            )
    return backbone


def build_table(nodes_path, edges_path, pdb_path):
    nodes = pandas.read_csv(nodes_path)
    edges = pandas.read_csv(edges_path)
    keys = [
        _node_key(row.ID_chainID, row.ID_resSeq, row.ID_iCode)
        for row in nodes.itertuples(index=False)
    ]
    key_to_index = {key: index for index, key in enumerate(keys)}
    if len(key_to_index) != len(keys):
        raise ValueError(f"{nodes_path}: duplicate residue identifiers")

    area_sum = np.zeros(len(nodes), dtype=np.float64)
    boundary_sum = np.zeros(len(nodes), dtype=np.float64)
    incident_edges = [[] for _ in range(len(nodes))]
    skipped_edges = []
    for row in edges.itertuples(index=False):
        key1 = _node_key(row.ID1_chainID, row.ID1_resSeq, row.ID1_iCode)
        key2 = _node_key(row.ID2_chainID, row.ID2_resSeq, row.ID2_iCode)
        missing = [key for key in (key1, key2) if key not in key_to_index]
        if missing:
            skipped_edges.append((key1, key2))
            continue
        area = max(float(row.area), 0.0)
        boundary = max(float(row.boundary), 0.0)
        for key in (key1, key2):
            index = key_to_index[key]
            area_sum[index] += area
            boundary_sum[index] += boundary
            incident_edges[index].append((area, boundary))
    if skipped_edges:
        print(
            f"warning: {edges_path}: skipped {len(skipped_edges)} edges outside "
            f"the node-induced graph: {skipped_edges}"
        )

    backbone = read_backbone(pdb_path)
    rotations = []
    translations = []
    for key in keys:
        atoms = backbone.get(key, {})
        missing = {"N", "CA", "C"} - atoms.keys()
        if missing:
            raise ValueError(
                f"{pdb_path}: residue {key} lacks frame atoms {sorted(missing)}"
            )
        origin = atoms["CA"]
        axis_x = atoms["C"] - origin
        axis_x /= np.linalg.norm(axis_x)
        n_direction = atoms["N"] - origin
        axis_y = n_direction - np.dot(n_direction, axis_x) * axis_x
        axis_y /= np.linalg.norm(axis_y)
        axis_z = np.cross(axis_x, axis_y)
        rotations.append(np.stack((axis_x, axis_y, axis_z), axis=-1))
        translations.append(origin)

    rotations = np.stack(rotations)
    translations = np.stack(translations)
    output = nodes[["ID_chainID", "ID_resSeq", "ID_iCode"]].copy()
    output["contact_area"] = np.log1p(area_sum)
    output["contact_exposure"] = boundary_sum / np.maximum(area_sum, 1e-8)
    degrees = np.asarray([len(values) for values in incident_edges])
    if degrees.max(initial=0) > MAX_INCIDENT_EDGES:
        raise ValueError(
            f"{edges_path}: maximum degree {degrees.max()} exceeds "
            f"MAX_INCIDENT_EDGES={MAX_INCIDENT_EDGES}"
        )
    output["edge_degree"] = degrees
    padded = np.zeros((len(nodes), MAX_INCIDENT_EDGES, 2), dtype=np.float64)
    for node_index, values in enumerate(incident_edges):
        # Descending order gives stable rank semantics: slot 0 is the largest
        # contact. With no truncation this does not alter the edge multiset.
        values = sorted(values, key=lambda pair: (pair[0], pair[1]), reverse=True)
        if values:
            padded[node_index, : len(values)] = np.log1p(np.asarray(values))
    for rank in range(MAX_INCIDENT_EDGES):
        output[f"edge_area_rank_{rank}"] = padded[:, rank, 0]
        output[f"edge_boundary_rank_{rank}"] = padded[:, rank, 1]

    log_area = padded[:, :, 0]
    log_boundary = padded[:, :, 1]
    valid = np.arange(MAX_INCIDENT_EDGES)[None, :] < degrees[:, None]
    safe_degree = np.maximum(degrees, 1)
    for name, values in (("area", log_area), ("boundary", log_boundary)):
        masked = np.where(valid, values, 0.0)
        output[f"pna_{name}_sum"] = masked.sum(axis=1)
        output[f"pna_{name}_mean"] = masked.sum(axis=1) / safe_degree
        centered = np.where(
            valid,
            values - output[f"pna_{name}_mean"].to_numpy()[:, None],
            0.0,
        )
        output[f"pna_{name}_std"] = np.sqrt(
            (centered ** 2).sum(axis=1) / safe_degree
        )
        output[f"pna_{name}_min"] = np.asarray(
            [row[:degree].min() for row, degree in zip(values, degrees)]
        )
        output[f"pna_{name}_max"] = np.asarray(
            [row[:degree].max() for row, degree in zip(values, degrees)]
        )
        for quantile in QUANTILES:
            label = str(int(round(100 * quantile)))
            output[f"quantile_{name}_{label}"] = np.asarray(
                [
                    np.quantile(row[:degree], quantile)
                    for row, degree in zip(values, degrees)
                ]
            )
    output["edge_degree_normalized"] = degrees / MAX_INCIDENT_EDGES
    output["edge_exposed_fraction"] = np.asarray(
        [
            np.count_nonzero(np.asarray(values)[:, 1] > 0) / len(values)
            for values in incident_edges
        ]
    )
    output["edge_boundary_area_ratio"] = (
        boundary_sum / np.maximum(area_sum, 1e-8)
    )
    output["quantile_area_total"] = np.log1p(area_sum)
    output["quantile_boundary_total"] = np.log1p(boundary_sum)
    for row in range(3):
        for column in range(3):
            output[f"rotation_{row}{column}"] = rotations[:, row, column]
    for column, name in enumerate(("x", "y", "z")):
        output[f"translation_{name}"] = translations[:, column]
    return output


def build_all(graphs_dir=GRAPHS_DIR):
    generated = []
    for graph_dir in sorted(Path(graphs_dir).iterdir()):
        if not graph_dir.is_dir():
            continue
        nodes_path = graph_dir / "coarse_graph_nodes.csv"
        edges_path = graph_dir / "coarse_graph_links.csv"
        pdb_path = graph_dir / "pocketness.pdb"
        if not all(path.exists() for path in (nodes_path, edges_path, pdb_path)):
            continue
        output_path = graph_dir / OUTPUT_NAME
        build_table(nodes_path, edges_path, pdb_path).to_csv(
            output_path, index=False
        )
        generated.append(output_path)
    return generated


if __name__ == "__main__":
    outputs = build_all()
    print(f"generated {len(outputs)} geometric protein graphs")
