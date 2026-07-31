"""Load precomputed protein artifacts and assemble cached PyG graphs."""

import glob
import os
import pickle

import pandas
import torch
from torch_geometric.data import Data

from dataloader.protein_registry import protein_record

MAX_INCIDENT_EDGES = 21
EDGE_QUANTILES = (0, 10, 25, 50, 75, 90, 100)


def rnabang_edge_node_mode(config):
    for name in (
        "current",
        "sorted",
        "deepsets",
        "pna",
        "quantiles",
        "set_transformer",
    ):
        if getattr(config, f"rnabang_edge_{name}", False):
            return name
    return "current"


class ProteinGraphData(Data):
    def __inc__(self, key, value, *args, **kwargs):
        if key == "sample_index":
            return 0
        return super().__inc__(key, value, *args, **kwargs)


class ProteinGraphBuilder:
    @staticmethod
    def _cached_columns(geometric, columns, dtype=torch.float32):
        return torch.stack(
            [geometric[column].to(dtype=dtype) for column in columns],
            dim=-1,
        )

    def _cached_protein_parts(
        self, cached, plm, node_confidence, nodes_path
    ):
        parts = dict(cached["base"])
        parts["plm"] = plm
        use_precomputed_geometric_nodes = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "rnabang_frozen_node_adapter", False)
        )
        if use_precomputed_geometric_nodes:
            geometric = cached.get("geometric")
            if geometric is None:
                raise FileNotFoundError(
                    f"{os.path.dirname(nodes_path)}/geometric_transformer_nodes.csv "
                    "is required by --geometric_transformer; rebuild the protein "
                    "tensor cache after generating it"
                )
            parts["geometric_node_attr"] = self._cached_columns(
                geometric,
                self._frozen_edge_node_columns(),
            )
            edge_mode = rnabang_edge_node_mode(self.config)
            if edge_mode in {"sorted", "deepsets", "set_transformer"}:
                pair_columns = [
                    column
                    for rank in range(MAX_INCIDENT_EDGES)
                    for column in (
                        f"edge_area_rank_{rank}",
                        f"edge_boundary_rank_{rank}",
                    )
                ]
                parts["edge_node_pairs"] = self._cached_columns(
                    geometric, pair_columns
                ).reshape(-1, MAX_INCIDENT_EDGES, 2)
            parts["edge_node_degree"] = geometric["edge_degree"].long()
            if getattr(self.config, "geometric_transformer", False):
                rotation_columns = [
                    f"rotation_{row}{column}"
                    for row in range(3)
                    for column in range(3)
                ]
                parts["frame_rotation"] = self._cached_columns(
                    geometric, rotation_columns
                ).reshape(-1, 3, 3)
                parts["frame_translation"] = self._cached_columns(
                    geometric,
                    ["translation_x", "translation_y", "translation_z"],
                )
        if node_confidence is not None:
            parts["node_confidence"] = node_confidence
        return parts

    def _load_node_confidence(self, path):
        """Per-node real pLDDT/B-factor-derived confidence, aligned to graph node order.

        Built by preprocessing/build_consistent_esm3_pdb.py from the same
        coarse_graph_nodes.csv row order used elsewhere, so no extra alignment is
        needed here -- row i of this CSV is node i, same as plm row i.
        """
        confidence_df = pandas.read_csv(path)
        return torch.tensor(confidence_df["confidence"].values, dtype=torch.float32)

    def make_graph_protein(self,nodes,edges,inter,family,plm,pok,name,node_confidence=None) -> Data:
        """
        Input : nodes is the name of the file containing node graph, edges is the same for links between nodes

        """
        parts = self.protein_graph_tensors(nodes, edges, plm, pok, node_confidence)
        return self.assemble_protein_graph(parts, inter, family)

    def assemble_protein_graph(self, parts, inter, family) -> Data:
        """Wrap cached per-protein tensors into the graph for one interaction row.

        Split out of make_graph_protein so the parts, which depend only on the protein,
        can be reused across the rows that share it while `inter` stays per row. Key
        insertion order matches the original single-shot construction, because PyG
        collates by store key order.
        """
        intera = (
            inter
            if isinstance(inter, torch.Tensor)
            else torch.tensor(inter, dtype=torch.long)
        )
        graph_kwargs = dict(
            x=parts["x"], edge_index=parts["edge_index"], edge_attr=parts["edge_attr"],
            inter=intera, family=family, bury=parts["bury"], plm=parts["plm"],
            pocket=parts["pocket"],
        )
        if "geometric_node_attr" in parts:
            graph_kwargs["geometric_node_attr"] = parts["geometric_node_attr"]
        if "edge_node_pairs" in parts:
            graph_kwargs["edge_node_pairs"] = parts["edge_node_pairs"]
        if "edge_node_degree" in parts:
            graph_kwargs["edge_node_degree"] = parts["edge_node_degree"]
        if "frame_rotation" in parts:
            graph_kwargs["frame_rotation"] = parts["frame_rotation"]
            graph_kwargs["frame_translation"] = parts["frame_translation"]
        if "node_confidence" in parts:
            # Only attached when use_esm3_v2_embeddings is on, so every sample in a
            # given run consistently has (or lacks) this key -- PyG's default batch
            # collation cannot mix a real tensor and a missing/None value for one key
            # across a batch.
            graph_kwargs["node_confidence"] = parts["node_confidence"]
        return ProteinGraphData(**graph_kwargs)

    @staticmethod
    def _feature_mean_std(values):
        values = values.float()
        return (
            values.mean(dim=0),
            values.std(dim=0, unbiased=False).clamp_min(1e-6),
        )

    def rnabang_normalization_stats(self):
        """Compute fixed statistics from unique training proteins only."""
        if not getattr(self.config, "rnabang_frozen_node_adapter", False):
            return None
        train_parts = [
            self.protein_graph_parts(name)[0]
            for name in sorted(self.csvtrain["LTPProtein"].unique())
        ]
        x = torch.cat([part["x"] for part in train_parts])
        bury = torch.cat([part["bury"] for part in train_parts])
        valid_bury = bury[bury != 2]
        if valid_bury.numel() == 0:
            raise ValueError("training proteins contain no valid buriedness values")
        sasa_mean, sasa_std = self._feature_mean_std(
            torch.log1p(x[:, 1].clamp_min(0))
        )
        volume_mean, volume_std = self._feature_mean_std(x[:, 2])
        bury_mean, bury_std = self._feature_mean_std(valid_bury)
        structural_mean = torch.stack((sasa_mean, volume_mean, bury_mean))
        structural_std = torch.stack((sasa_std, volume_std, bury_std))

        edge_values = torch.cat(
            [part["geometric_node_attr"] for part in train_parts]
        )
        edge_mean, edge_std = self._feature_mean_std(edge_values)
        pair_mean = torch.zeros(2)
        pair_std = torch.ones(2)
        mode = rnabang_edge_node_mode(self.config)
        if mode in {"sorted", "deepsets", "set_transformer"}:
            pairs = torch.cat([part["edge_node_pairs"] for part in train_parts])
            degrees = torch.cat(
                [part["edge_node_degree"] for part in train_parts]
            )
            mask = (
                torch.arange(MAX_INCIDENT_EDGES).unsqueeze(0)
                < degrees.unsqueeze(1)
            )
            pair_mean, pair_std = self._feature_mean_std(pairs[mask])
            if mode == "sorted":
                edge_mean[:42] = pair_mean.repeat(MAX_INCIDENT_EDGES)
                edge_std[:42] = pair_std.repeat(MAX_INCIDENT_EDGES)
            else:
                # The learned encoders use pair_mean/std at their two-channel input
                # and already LayerNorm their 32-dimensional output.
                edge_mean = torch.zeros(32)
                edge_std = torch.ones(32)
        return {
            "structural_mean": structural_mean,
            "structural_std": structural_std,
            "edge_feature_mean": edge_mean,
            "edge_feature_std": edge_std,
            "edge_pair_mean": pair_mean,
            "edge_pair_std": pair_std,
        }

    def protein_graph_tensors(self, nodes, edges, plm, pok, node_confidence=None):
        """Parse the node/edge/pocket files of one protein into its graph tensors.

        Everything here is a function of the protein alone, so get() caches the result
        per protein name instead of re-reading two CSVs, the pocketness PDB and the
        embedding for every interaction row that mentions the protein.
        """
        protein_name = os.path.basename(os.path.dirname(nodes))
        cached = getattr(self, "_protein_tensor_cache", {}).get(protein_name)
        if cached is not None:
            return self._cached_protein_parts(
                cached, plm, node_confidence, nodes
            )

        vertices=pandas.read_csv(nodes)
        edges=pandas.read_csv(edges)

        #vertices["hydrophobicity"]=vertices["residue_type"].map(hydrophobicity_keys)
        #bury=torch.tensor(vertices[["residue_mean_buriedness", "residue_min_buriedness", "residue_max_buriedness"]].values, dtype=torch.float32)
        bury=torch.tensor(vertices["residue_mean_buriedness"].values, dtype=torch.float32)
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56", "hydrophobicity"]].values, dtype=torch.float32) 
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56"]].values, dtype=torch.float32)
        x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume"]].values, dtype=torch.float32)
        edge_index=torch.tensor(edges[["ID1_resSeq","ID2_resSeq"]].values, dtype=torch.int64) 
        edge_attr=torch.tensor(edges[["distance","area","boundary"]].values, dtype=torch.float32) #maybe a problem here? about how the edges are indexed OH YES THERE IS
        #also can we pool covalent bond y/n from the non coarse grained structure?
        """
        if inter == 1:
            intera = torch.tensor([1,0],dtype=torch.int32)
        else:
            intera = torch.tensor([0,1],dtype=torch.int32)
        """
        dic={}
        for i in range(len(vertices["ID_resSeq"])):
            dic[int(vertices["ID_resSeq"][i])]=i
        # Dead since the print below was commented out: both lines walk every edge in
        # Python (0.15 ms per sample, 0.4 s per epoch) to build a list nothing reads.
        # import itertools
        # all_nodes = list(itertools.chain.from_iterable(edge_index.tolist()))
        # missing_keys = [x for x in all_nodes if dic.get(x) is None]
        #print("Missing keys in dic:", missing_keys)
        #print("Missing keys in dic:", missing_keys)
        edge_index.apply_(lambda x: dic.get(x, 0))  # -1 or some other sentinel
        #edge_index.apply_(dic.get())
        #pocket
        #discard backbone atoms for contributoin to pocket
        aal=["C","CA","CB","O","N"]
        dic={}
        lis=[]

        #need to parse this better, maybe load csv and filter on atom fetures and 

        with open(pok,"r") as f:
            lines = f.readlines()
            if os.path.normpath(pok).endswith(os.path.normpath("graphs/RET4/pocketness.pdb")):
                lines = lines[:-1]
            for line in lines:
                    dic[line[22:28].strip()]=0
            for line in lines:
                if line[13:17].strip() in aal:
                    continue
                dic[line[22:28].strip()]+=int(line[62])
        for i,j in dic.items():
            lis.append(j>0)
        poket = torch.tensor(lis, dtype=torch.int16).to(torch.bool)

        parts = {
            "x": x, "edge_index": edge_index.t().contiguous(), "edge_attr": edge_attr,
            "bury": bury, "plm": plm, "pocket": poket,
        }
        use_precomputed_geometric_nodes = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "rnabang_frozen_node_adapter", False)
        )
        if use_precomputed_geometric_nodes:
            geometric_path = os.path.join(
                os.path.dirname(nodes), "geometric_transformer_nodes.csv"
            )
            if not os.path.exists(geometric_path):
                raise FileNotFoundError(
                    f"{geometric_path} is required by --geometric_transformer; "
                    "run preprocessing/build_geometric_protein_graphs.py"
                )
            geometric = pandas.read_csv(geometric_path)
            expected_ids = vertices[
                ["ID_chainID", "ID_resSeq", "ID_iCode"]
            ].astype(str).reset_index(drop=True)
            actual_ids = geometric[
                ["ID_chainID", "ID_resSeq", "ID_iCode"]
            ].astype(str).reset_index(drop=True)
            if not expected_ids.equals(actual_ids):
                raise ValueError(
                    f"{geometric_path}: residue rows do not align with {nodes}"
                )
            rotation_columns = [
                f"rotation_{row}{column}"
                for row in range(3)
                for column in range(3)
            ]
            parts["geometric_node_attr"] = torch.tensor(
                self._frozen_edge_node_features(geometric),
                dtype=torch.float32,
            )
            edge_mode = rnabang_edge_node_mode(self.config)
            if edge_mode in {"sorted", "deepsets", "set_transformer"}:
                pair_columns = [
                    column
                    for rank in range(MAX_INCIDENT_EDGES)
                    for column in (
                        f"edge_area_rank_{rank}",
                        f"edge_boundary_rank_{rank}",
                    )
                ]
                parts["edge_node_pairs"] = torch.tensor(
                    geometric[pair_columns].values.reshape(
                        -1, MAX_INCIDENT_EDGES, 2
                    ),
                    dtype=torch.float32,
                )
                parts["edge_node_degree"] = torch.tensor(
                    geometric["edge_degree"].values,
                    dtype=torch.long,
                )
            else:
                parts["edge_node_degree"] = torch.tensor(
                    geometric["edge_degree"].values,
                    dtype=torch.long,
                )
            if getattr(self.config, "geometric_transformer", False):
                parts["frame_rotation"] = torch.tensor(
                    geometric[rotation_columns].values.reshape(-1, 3, 3),
                    dtype=torch.float32,
                )
                parts["frame_translation"] = torch.tensor(
                    geometric[
                        ["translation_x", "translation_y", "translation_z"]
                    ].values,
                    dtype=torch.float32,
                )
        if node_confidence is not None:
            parts["node_confidence"] = node_confidence
        #print(poket.shape)
        #print(f"poket shape : {poket.shape}")
        #print(f"x shape : {x.shape}")
        return parts

    def _frozen_edge_node_features(self, geometric):
        """Select one mutually exclusive precomputed edge→node representation."""
        return geometric[self._frozen_edge_node_columns()].values

    def _frozen_edge_node_columns(self):
        """Columns for the selected precomputed edge→node representation."""
        mode = rnabang_edge_node_mode(self.config)
        if mode in {"current", "deepsets", "set_transformer"}:
            columns = ["contact_area", "contact_exposure"]
        elif mode == "sorted":
            columns = [
                column
                for rank in range(MAX_INCIDENT_EDGES)
                for column in (
                    f"edge_area_rank_{rank}",
                    f"edge_boundary_rank_{rank}",
                )
            ] + ["edge_degree_normalized"]
        elif mode == "pna":
            columns = [
                f"pna_{feature}_{statistic}"
                for feature in ("area", "boundary")
                for statistic in ("sum", "mean", "std", "min", "max")
            ] + [
                "edge_degree_normalized",
                "edge_exposed_fraction",
                "edge_boundary_area_ratio",
            ]
        elif mode == "quantiles":
            columns = [
                f"quantile_{feature}_{quantile}"
                for feature in ("area", "boundary")
                for quantile in EDGE_QUANTILES
            ] + [
                "quantile_area_total",
                "quantile_boundary_total",
                "edge_degree_normalized",
                "edge_boundary_area_ratio",
            ]
        else:
            raise ValueError(f"unknown RNA-BAnG edge-to-node mode: {mode}")
        return columns

    def protein_graph_parts(self, prot_file):
        """Graph tensors and family one-hot of one protein, parsed once per protein.

        The train split holds 1095 rows over 32 distinct proteins, so without this the
        same two CSVs, pocketness PDB and ESM3 embedding were re-read about 34 times an
        epoch each, and 5100 times over a 150-epoch run.
        """
        cached = self._protein_graph_cache.get(prot_file)
        if cached is not None:
            return cached

        record = protein_record(prot_file, self.ROOT_DIR)
        prot_file_emb = record["artifact_stem"]

        node_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_nodes.csv"
        edge_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_links.csv"
        pok = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/pocketness.pdb"
        use_esm3_v2 = getattr(self.config, "use_esm3_v2_embeddings", False)
        use_rnabang = any(
            (
                getattr(self.config, "rnabang_replace_esm3", False),
                getattr(self.config, "rnabang_full_protein_encoder", False),
                getattr(self.config, "rnabang_with_esm3", False),
                getattr(self.config, "rnabang_residual_with_esm3", False),
                getattr(self.config, "rnabang_frozen_node_adapter", False),
            )
        )
        # v2 embeddings (preprocessing/embed_protein_esm3_v2.py) are built from
        # data/esm3_input/<stem>.pdb, where Voronota has already normalized MSE and
        # alt-conformations (see build_consistent_esm3_pdb.py header) -- no per-protein
        # special-token hacks needed beyond the standard BOS/EOS trim, unlike v1.
        esm3_tensor = None
        if not (
            getattr(self.config, "rnabang_replace_esm3", False)
            or getattr(self.config, "rnabang_full_protein_encoder", False)
            or getattr(self.config, "rnabang_frozen_node_adapter", False)
        ):
            embed_dir = "embedding_ESM3_v2" if use_esm3_v2 else "embedding_ESM3"
            embed_files = glob.glob(
                self.ROOT_DIR + f"/{embed_dir}/" + prot_file_emb + "_*"
            )
            if len(embed_files) != 1:
                raise FileNotFoundError(
                    f"Expected one ESM3 embedding for {prot_file_emb} in "
                    f"{embed_dir}, found {len(embed_files)}"
                )
            with open(embed_files[0], "rb") as f:
                esm3_tensor = pickle.load(f)
            if use_esm3_v2:
                esm3_tensor = esm3_tensor[1:-1]
            else:
                # Historical v1 special-token trimming is part of the existing
                # ESM3/node alignment contract.
                extra_trim = record["esm3_v1_extra_trim_pairs"]
                if extra_trim:
                    esm3_tensor = esm3_tensor[extra_trim:-extra_trim]
                esm3_tensor = esm3_tensor[1:-1]

        rnabang_tensor = None
        if use_rnabang:
            rnabang_files = glob.glob(
                self.ROOT_DIR
                + "/embedding_RNABANG/"
                + prot_file_emb
                + "_RNABANG.pkl"
            )
            if len(rnabang_files) != 1:
                raise FileNotFoundError(
                    f"Expected data/embedding_RNABANG/"
                    f"{prot_file_emb}_RNABANG.pkl, found {len(rnabang_files)}"
                )
            with open(rnabang_files[0], "rb") as f:
                rnabang_tensor = torch.as_tensor(
                    pickle.load(f), dtype=torch.float32
                )

        if (
            getattr(self.config, "rnabang_with_esm3", False)
            or getattr(self.config, "rnabang_residual_with_esm3", False)
        ):
            plm_tensor = torch.cat(
                (
                    torch.as_tensor(esm3_tensor, dtype=torch.float32),
                    rnabang_tensor,
                ),
                dim=-1,
            )
        elif use_rnabang:
            plm_tensor = rnabang_tensor
        else:
            plm_tensor = esm3_tensor
        with open(node_file, 'r') as f:
            num_lines = sum(1 for line in f)
        # PLM row i is aligned with graph node i (see protein_encoder), so the
        # embedding must have exactly one row per graph residue. Fail loudly
        # instead of silently attaching a shifted / wrong-length embedding. The same
        # invariant is checked in bulk (no training) by tests/test_esm3_alignment.py.
        if num_lines - plm_tensor.shape[0] != 1:
            raise ValueError(
                f"protein embedding<->graph node misalignment for {prot_file}: "
                f"{plm_tensor.shape[0]} trimmed embedding rows vs {num_lines - 1} "
                f"graph nodes (expected equal). Check RNA-BAnG/ESM3 preprocessing "
                f"input and residue alignment."
            )


        family = record["family"]
        fam_enc =["CRAL-TRIO","LBP_BPI_CETP","GLTP","ML","lipocalin","START","IP_trans","scp2","OSBP"]
        tenfam=torch.zeros(9)
        for i in range(len(fam_enc)):
            if fam_enc[i] == family.strip():
                tenfam[i]=1

        node_confidence = None
        if use_esm3_v2:
            confidence_file = self.ROOT_DIR+"/esm3_input/"+prot_file_emb+"_node_confidence.csv"
            node_confidence = self._load_node_confidence(confidence_file)

        parts = self.protein_graph_tensors(
            node_file, edge_file, plm_tensor, pok, node_confidence,
        )
        self._protein_graph_cache[prot_file] = (parts, tenfam)
        return parts, tenfam
