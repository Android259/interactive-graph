"""Build train-only GRAB graphs and batch label coefficients."""

import os

import pandas
import torch
from torch_geometric.data import Data


class GrabDatasetGraphMixin:
    def load_pair_edges(self, edge_csv_path=None):
        if edge_csv_path is None:
            edge_csv_path = os.path.join(self.ROOT_DIR, "grab_pair_graph_edges.csv")

        if not os.path.exists(edge_csv_path):
            raise FileNotFoundError(
                f"Pair edges file not found: {edge_csv_path}. "
                "Run dataloader/GRAB_graph.py first."
            )

        edges = pandas.read_csv(edge_csv_path)
        required_columns = {"source_pair_id", "target_pair_id", "edge_weight"}
        missing_columns = required_columns.difference(edges.columns)
        if missing_columns:
            raise ValueError(f"Missing required edge columns: {sorted(missing_columns)}")
        return edges

    def build_current_pair_graph(self, edge_csv_path=None):
        neighbors_per_target = 20
        split_pair_ids = set(self.csv["_tanimoto_orig_idx"].astype(int).tolist())
        edges = self.load_pair_edges(edge_csv_path)

        source = edges["source_pair_id"].astype(int)
        target = edges["target_pair_id"].astype(int)
        edge_mask = source.isin(split_pair_ids) & target.isin(split_pair_ids)
        split_edges = edges.loc[edge_mask].copy()
        split_edges = (
            split_edges.sample(frac=1, random_state=getattr(self, "seed", 0))
            .sort_values(
                ["target_pair_id", "edge_weight"],
                ascending=[True, False],
                kind="stable",
            )
            .groupby("target_pair_id", sort=False)
            .head(neighbors_per_target)
            .reset_index(drop=True)
        )

        graph_pair_ids = set()
        graph_pair_ids.update(split_edges["source_pair_id"].astype(int).tolist())
        graph_pair_ids.update(split_edges["target_pair_id"].astype(int).tolist())
        graph_pair_ids.update(split_pair_ids)
        graph_pair_ids = sorted(graph_pair_ids)
        pair_id_to_node_id = {
            pair_id: node_id for node_id, pair_id in enumerate(graph_pair_ids)
        }

        if split_edges.empty:
            edge_index = torch.empty((2, 0), dtype=torch.long)
            edge_weight = torch.empty((0,), dtype=torch.float32)
        else:
            edge_index = torch.tensor(
                [
                    [
                        pair_id_to_node_id[int(source_id)],
                        pair_id_to_node_id[int(target_id)],
                    ]
                    for source_id, target_id in split_edges[
                        ["source_pair_id", "target_pair_id"]
                    ].values
                ],
                dtype=torch.long,
            ).t().contiguous()
            edge_weight = torch.tensor(
                split_edges["edge_weight"].values, dtype=torch.float32
            )

        pair_ids = torch.tensor(graph_pair_ids, dtype=torch.long)
        target_mask = torch.tensor(
            [pair_id in split_pair_ids for pair_id in graph_pair_ids], dtype=torch.bool
        )
        target_node_index = torch.tensor(
            [pair_id_to_node_id[pair_id] for pair_id in sorted(split_pair_ids)],
            dtype=torch.long,
        )
        target_pair_id = torch.tensor(sorted(split_pair_ids), dtype=torch.long)

        train_labels_by_pair_id = dict(
            zip(
                self.csv["_tanimoto_orig_idx"].astype(int),
                self.csv["Interaction"].astype(int),
            )
        )
        labels = torch.full((len(graph_pair_ids),), -1, dtype=torch.long)
        for node_id, pair_id in enumerate(graph_pair_ids):
            if pair_id in train_labels_by_pair_id:
                labels[node_id] = train_labels_by_pair_id[pair_id]

        edge_ids_by_target = {}
        for edge_id, target_id in enumerate(
            split_edges["target_pair_id"].astype(int).tolist()
        ):
            edge_ids_by_target.setdefault(target_id, []).append(edge_id)
        edge_ids_by_target = {
            target_id: torch.tensor(edge_ids, dtype=torch.long)
            for target_id, edge_ids in edge_ids_by_target.items()
        }

        pair_graph = Data(
            x=torch.ones((len(graph_pair_ids), 1), dtype=torch.float32),
            edge_index=edge_index,
            edge_weight=edge_weight,
            edge_attr=edge_weight.view(-1, 1),
            y=labels,
            pair_id=pair_ids,
            train_mask=target_mask,
            target_mask=target_mask,
            target_node_index=target_node_index,
            target_pair_id=target_pair_id,
        )
        pair_graph.edge_ids_by_target = edge_ids_by_target
        pair_graph.node_id_by_pair_id = pair_id_to_node_id

        label_coefficients_by_target = {
            pair_id: torch.zeros(2, dtype=torch.float32) for pair_id in split_pair_ids
        }
        for target_id, edge_ids in edge_ids_by_target.items():
            source_node_ids = edge_index[0, edge_ids]
            source_labels = labels[source_node_ids]
            source_weights = edge_weight[edge_ids]
            label_coefficients = torch.zeros(2, dtype=torch.float32)
            valid_source_mask = source_labels >= 0
            if valid_source_mask.any():
                label_coefficients.scatter_add_(
                    0,
                    source_labels[valid_source_mask].long(),
                    source_weights[valid_source_mask],
                )
            label_coefficients_by_target[target_id] = label_coefficients
        pair_graph.label_coefficients_by_target = label_coefficients_by_target
        zero_neighbor_targets = sum(
            int(coefficients.sum().item() == 0)
            for coefficients in label_coefficients_by_target.values()
        )
        print(
            "GRAB graph: "
            f"targets={len(split_pair_ids)}, "
            f"edges={split_edges.shape[0]}, "
            f"zero_neighbor_targets={zero_neighbor_targets}"
        )
        return pair_graph

    def get_grab_batch_inputs(self, batch_pair_ids, device):
        if self.pair_graph is None:
            raise RuntimeError("GRAB pair graph has not been built for this dataset")

        batch_pair_ids = batch_pair_ids.detach().cpu().long().tolist()
        if not batch_pair_ids:
            raise ValueError("GRAB batch contains no pair IDs")

        available = self.pair_graph.label_coefficients_by_target
        missing_pair_ids = sorted(
            {
                int(pair_id)
                for pair_id in batch_pair_ids
                if int(pair_id) not in available
            }
        )
        if missing_pair_ids:
            raise ValueError(
                "GRAB batch pair IDs are absent from the train-only pair graph: "
                f"{missing_pair_ids}"
            )

        coefficients = torch.stack(
            [available[int(pair_id)] for pair_id in batch_pair_ids]
        )
        if coefficients.shape != (len(batch_pair_ids), 2):
            raise ValueError(
                "GRAB coefficients must have shape "
                f"({len(batch_pair_ids)}, 2), got {tuple(coefficients.shape)}"
            )
        if not torch.isfinite(coefficients).all():
            raise ValueError("GRAB coefficients contain non-finite values")
        if (coefficients < 0).any():
            raise ValueError("GRAB coefficients contain negative values")

        return coefficients.to(device, non_blocking=True)
