from pathlib import Path
import random

import pandas as pd
import torch


PAIR_COLUMNS = [
    "LTPProtein",
    "FullIdentityOfLipid",
    "Interaction"]


def load_pair_table(csv_path, positive_label=1, unlabeled_label=0):
    pair_table = pd.read_csv(csv_path, sep=None, engine="python").reset_index(drop=True)
    missing_columns = [column for column in PAIR_COLUMNS if column not in pair_table.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    pair_table = pair_table.copy()
    pair_table["pair_id"] = range(len(pair_table))
    pair_table["grab_label"] = pair_table["Interaction"].map(
        lambda value: positive_label if int(value) == 1 else unlabeled_label)

    return pair_table


def edges_from_grouped_pairs(pair_table, group_column):
    weighted_edges = []
    for _, group in pair_table.groupby(group_column, dropna=False):
        pair_ids = group["pair_id"].tolist()
        if len(pair_ids) < 2:
            continue
        for source in pair_ids:
            for target in pair_ids:
                if source != target:
                    weighted_edges.append((source, target, 1.0))
    return weighted_edges


def keep_top_k_edges_per_pair(weighted_edges, top_k_edges_per_pair, random_seed=0):
    if top_k_edges_per_pair is None:
        return sorted(weighted_edges)
    if top_k_edges_per_pair <= 0:
        return []

    edges_by_target = {}
    for source, target, weight in weighted_edges:
        edges_by_target.setdefault(target, []).append((source, weight))

    top_edges = []
    rng = random.Random(random_seed)
    for target, sources in edges_by_target.items():
        rng.shuffle(sources)
        sources.sort(key=lambda edge: -edge[1])
        for source, weight in sources[:top_k_edges_per_pair]:
            top_edges.append((source, target, weight))

    return sorted(top_edges)


def add_reverse_edges(weighted_edges):
    edge_weights = {
        (source, target): weight
        for source, target, weight in weighted_edges}

    for source, target, weight in weighted_edges:
        edge_weights[(target, source)] = max(edge_weights.get((target, source), 0.0), weight)

    return sorted(
        (source, target, weight)
        for (source, target), weight in edge_weights.items())


def build_pair_graph_edges(
    pair_table,
    connect_same_protein=True,
    connect_same_lipid=True,
    top_k_edges_per_pair=20,
    random_seed=0):

    weighted_edges = []

    if connect_same_protein:
        weighted_edges.extend(edges_from_grouped_pairs(pair_table, "LTPProtein"))

    if connect_same_lipid:
        weighted_edges.extend(edges_from_grouped_pairs(pair_table, "FullIdentityOfLipid"))

    if not weighted_edges:
        return (
            torch.empty((2, 0), dtype=torch.long),
            torch.empty((0,), dtype=torch.float32))

    edge_weights = {}
    for source, target, weight in weighted_edges:
        edge_weights[(source, target)] = edge_weights.get((source, target), 0.0) + weight

    weighted_edges = [
        (source, target, weight)
        for (source, target), weight in edge_weights.items()]
    weighted_edges = keep_top_k_edges_per_pair(
        weighted_edges,
        top_k_edges_per_pair,
        random_seed=random_seed)
    weighted_edges = add_reverse_edges(weighted_edges)
    if not weighted_edges:
        return (
            torch.empty((2, 0), dtype=torch.long),
            torch.empty((0,), dtype=torch.float32))

    edge_pairs = [(source, target) for source, target, _ in weighted_edges]
    weights = [weight for _, _, weight in weighted_edges]

    return (
        torch.tensor(edge_pairs, dtype=torch.long).t().contiguous(),
        torch.tensor(weights, dtype=torch.float32))


def build_grab_pair_graph(
    csv_path,
    connect_same_protein=True,
    connect_same_lipid=True,
    top_k_edges_per_pair=20,
    random_seed=0):

    pair_table = load_pair_table(csv_path)
    edge_index, edge_weight = build_pair_graph_edges(
        pair_table,
        connect_same_protein=connect_same_protein,
        connect_same_lipid=connect_same_lipid,
        top_k_edges_per_pair=top_k_edges_per_pair,
        random_seed=random_seed)

    labels = torch.as_tensor(pair_table["grab_label"].to_numpy(copy=True), dtype=torch.long)

    return {
        "pair_table": pair_table,
        "edge_index": edge_index,
        "edge_weight": edge_weight,
        "labels": labels,
    }


def save_grab_pair_graph(graph, output_prefix):
    graph["pair_table"].to_csv(f"{output_prefix}_pairs.csv", index=False)
    torch.save(graph["edge_index"], f"{output_prefix}_edge_index.pt")
    torch.save(graph["edge_weight"], f"{output_prefix}_edge_weight.pt")
    torch.save(graph["labels"], f"{output_prefix}_labels.pt")


def grab_edge_table(graph):
    """Return the CSV representation shared by both edge-save functions."""
    edge_index = graph["edge_index"].t().cpu().numpy()
    edge_weight = graph["edge_weight"].cpu().numpy()
    return pd.DataFrame({
        "source_pair_id": edge_index[:, 0],
        "target_pair_id": edge_index[:, 1],
        "edge_weight": edge_weight,
    })


def save_grab_pair_graph_csv(graph, output_prefix):
    graph["pair_table"].to_csv(f"{output_prefix}_pairs.csv", index=False)
    grab_edge_table(graph).to_csv(f"{output_prefix}_edges.csv", index=False)


def save_grab_edges_csv(graph, output_path):
    grab_edge_table(graph).to_csv(output_path, index=False)


if __name__ == "__main__":
    from dataloader.dataset_source import INTERACTION_CSV

    input_csv = f"data/{INTERACTION_CSV}"
    output_edges_csv = Path("data/grab_pair_graph_edges.csv")
    top_k_edges_per_pair = 20

    output_edges_csv.parent.mkdir(parents=True, exist_ok=True)

    graph = build_grab_pair_graph(
        input_csv,
        connect_same_protein=True,
        connect_same_lipid=True,
        top_k_edges_per_pair=top_k_edges_per_pair,
        random_seed=0)
    save_grab_edges_csv(graph, output_edges_csv)

    print(f"Saved edges CSV: {output_edges_csv}")
