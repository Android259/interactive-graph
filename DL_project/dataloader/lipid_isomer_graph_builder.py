"""Load and assemble atom-level lipid graphs for lipid_graph_isomers mode."""

import hashlib
import os
import random

import pandas
import torch
from rdkit import Chem
from torch_geometric.data import Data


class LipidGraphData(Data):
    def __inc__(self, key, value, *args, **kwargs):
        if key == "lipid_batch":
            return int(value.max()) + 1 if value.numel() > 0 else 0
        return super().__inc__(key, value, *args, **kwargs)


class LipidIsomerGraphBuilder:
    def normalize_lipid_smiles_text(self, value):
        value = str(value)
        if "//" in value or "\\\\" in value:
            value = value.replace("//", "/")
            value = value.replace("\\\\", "\\")
        return value

    def canonical_lipid_smiles_list(self, value):
        value = self.normalize_lipid_smiles_text(value)
        if value == "0":
            return []

        canonical_smiles = []
        seen = set()
        lipid_candidates = value.split(";") if ";" in value else [value]
        for lipid in lipid_candidates:
            lipid = lipid.strip()
            if not lipid or lipid == "0":
                continue
            mol = Chem.MolFromSmiles(lipid)
            if mol is None:
                continue
            canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
            if canonical not in seen:
                canonical_smiles.append(canonical)
                seen.add(canonical)
        return canonical_smiles

    def lipid_graph_smiles(self, smile_global, smile_fragment=None):
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        global_smiles = self.canonical_lipid_smiles_list(smile_global)
        fragment_smiles = self.canonical_lipid_smiles_list(smile_fragment)

        # Same rule as the embedding path: the draw is a training-split augmentation,
        # marked per clone in New_dataloader.__iter__. Validation and test fall through
        # to the fixed first candidate below.
        if self._draw_lipid_candidate and fragment_smiles:
            return [random.choice(fragment_smiles)]
        if self.config.lipid_concat or self.config.lipid_fragments_mask:
            if fragment_smiles:
                return fragment_smiles
            if global_smiles:
                return [global_smiles[0]]
            return [self.fallback_lipid_smiles()]
        if global_smiles:
            return [global_smiles[0]]
        if fragment_smiles:
            return [fragment_smiles[0]]
        return [self.fallback_lipid_smiles()]

    def select_lipid_smiles(self, smile_global, smile_fragment=None):
        return self.lipid_graph_smiles(smile_global, smile_fragment)[0]

    def lipid_graph_id(self, canonical_smiles):
        if canonical_smiles in self.lipid_graph_index:
            return self.lipid_graph_index[canonical_smiles]
        graph_id = hashlib.sha1(canonical_smiles.encode("utf-8")).hexdigest()[:16]
        graph_path = os.path.join(self.lipid_graph_dir, graph_id)
        if os.path.exists(graph_path):
            return graph_id
        raise FileNotFoundError(
            f"Lipid isomer graph not found for SMILES: {canonical_smiles}. "
            "Run data/build_lipid_isomer_graphs.py first."
        )

    def read_lipid_graph_tables(self, canonical_smiles):
        graph_id = self.lipid_graph_id(canonical_smiles)
        graph_path = os.path.join(self.lipid_graph_dir, graph_id)
        nodes = pandas.read_csv(os.path.join(graph_path, "nodes.csv"))
        edges = pandas.read_csv(os.path.join(graph_path, "edges.csv"))
        return nodes, edges

    def make_graph_lipid(self, smile_global, smile_fragment=None):
        node_columns = [
            "atomic_num",
            "formal_charge",
            "degree",
            "hybridization",
            "is_aromatic",
            "is_in_ring",
            "chiral_tag",
            "chirality_possible",
            "total_num_hs",
            "mass",
            "gasteiger_charge",
        ]
        edge_columns = [
            "bond_type",
            "is_conjugated",
            "is_in_ring",
            "stereo",
            "bond_dir",
            "is_aromatic",
        ]

        canonical_smiles_list = self.lipid_graph_smiles(
            smile_global, smile_fragment
        )
        cache_key = tuple(canonical_smiles_list)
        cached = self._lipid_graph_cache.get(cache_key)
        if cached is not None:
            lipid_graph = LipidGraphData(
                x=cached["x"],
                edge_index=cached["edge_index"],
                edge_attr=cached["edge_attr"],
                liplab=cached["liplab"],
            )
            if self.config.lipid_fragments_mask:
                lipid_graph.lipid_batch = cached["lipid_batch"]
            return lipid_graph

        xs = []
        edge_indices = []
        edge_attrs = []
        lipid_batches = []
        node_offset = 0
        for fragment_id, canonical_smiles in enumerate(canonical_smiles_list):
            nodes, edges = self.read_lipid_graph_tables(canonical_smiles)
            x = torch.tensor(nodes[node_columns].values, dtype=torch.float32)
            edge_index = torch.tensor(
                edges[["source", "target"]].values, dtype=torch.long
            ).t().contiguous()
            edge_attr = torch.tensor(
                edges[edge_columns].values, dtype=torch.float32
            )
            xs.append(x)
            edge_indices.append(edge_index + node_offset)
            edge_attrs.append(edge_attr)
            lipid_batches.append(
                torch.full((x.shape[0],), fragment_id, dtype=torch.long)
            )
            node_offset += x.shape[0]

        x = torch.cat(xs, dim=0)
        edge_index = torch.cat(edge_indices, dim=1)
        edge_attr = torch.cat(edge_attrs, dim=0)
        lipidlabel = self.lipidlabel_enc("PC")
        liplab = torch.tensor(lipidlabel, dtype=torch.int)
        entry = {
            "x": x,
            "edge_index": edge_index,
            "edge_attr": edge_attr,
            "liplab": liplab,
        }
        lipid_graph = LipidGraphData(
            x=x, edge_index=edge_index, edge_attr=edge_attr, liplab=liplab
        )
        if self.config.lipid_fragments_mask:
            lipid_batch = torch.cat(lipid_batches, dim=0)
            entry["lipid_batch"] = lipid_batch
            lipid_graph.lipid_batch = lipid_batch
        self._lipid_graph_cache[cache_key] = entry
        return lipid_graph

    def lipidlabel_enc(self, lipdata):
        oh = torch.zeros(41)
        try:
            oh = self.labelOH[lipdata]
        except:
            print(lipdata)
            print(self.labelOH[lipdata])
            pass
        return oh
