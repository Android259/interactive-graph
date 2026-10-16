"""Load precomputed protein artifacts and assemble cached PyG graphs."""

import glob
import os
import pickle

import numpy
import pandas
import torch
from torch_geometric.data import Data

from dataloader.descriptors import PROTEIN_DESCRIPTOR_NAMES as POCKET_DESCRIPTOR_NAMES
# Descriptor values and residue tables live in compute_descriptors.py;
# this module assembles node features. Both share KYTE_DOOLITTLE.
from preprocessing.compute_descriptors import KYTE_DOOLITTLE


# Family one-hot order, shared with --group_dro in training/new_train.py
# for ProteinDomain-based training counts.
FAMILY_NAMES = (
    "CRAL-TRIO", "LBP_BPI_CETP", "GLTP", "ML", "lipocalin",
    "START", "IP_trans", "scp2", "OSBP",
)

# Keep residue type/SASA/volume at node[:, 0..2]; append optional features.
BASE_NODE_COLUMNS = ("residue_type", "residue_sas_area", "residue_volume")
# Appended by --protein_extra_node_features, in this order.
EXTRA_NODE_COLUMNS = ("residue_mean_ev28", "residue_mean_ev56")
# Add derived hydrophobicity; match ModelConfig.validate's node-width increment.
EXTRA_NODE_FEATURE_COUNT = len(EXTRA_NODE_COLUMNS) + 1


# POCKET_DESCRIPTOR_NAMES aliases descriptors.PROTEIN_DESCRIPTOR_NAMES,
# keeping all descriptor names in one catalog. compute_descriptors.pocket_descriptor
# computes values from coarse_graph_nodes.csv and pocketness.pdb.

# Reference-only selection of seven descriptors near the 9-family eta^2
# floor 0.24 (files/reference/pocket_shape_descriptors.md section 5;
# analysis/feature_identity_check.py).
# Excluded: pocket_sasa_share 0.85, hydropathy_core 0.77, pocket_residue_share
# 0.71, pocket_extent 0.62, ev14_q50 0.59, depth_q10 0.55.
# No runtime consumer remains: --pocket_descriptors_family_neutral and its
# unstandardized per-node broadcast were removed. Keep the measured selection
# for cited reference documents. Individual names remain available through
# --protein_descriptors as standardized descriptor_catalog_input columns.
POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES = (
    "pocket_volume_per_sasa", "pocket_elongation", "pocket_flatness",
    "buriedness_q50", "apolar_sasa_share", "aromatic_share", "hydropathy_rim",
)






def restrict_parts_to_mask(parts, keep):
    """Subset protein nodes by keep, retaining edges only when both endpoints survive.

    Renumber surviving edges. Used for fixed pocket masks and per-sample random
    residue-subsampling masks.
    """
    kept = int(keep.sum())
    renumber = torch.full((keep.numel(),), -1, dtype=torch.long)
    renumber[keep] = torch.arange(kept)
    edge_index = parts["edge_index"]
    edge_keep = keep[edge_index[0]] & keep[edge_index[1]]
    restricted = dict(parts)
    restricted["edge_index"] = renumber[edge_index[:, edge_keep]]
    restricted["edge_attr"] = parts["edge_attr"][edge_keep]
    for name in (
        "x", "bury", "plm", "pocket", "geometric_node_attr", "frame_rotation", "frame_translation", "node_confidence",
    ):
        value = restricted.get(name)
        if value is not None:
            restricted[name] = value[keep]
    return restricted


def protein_node_columns(config):
    """Return Voronota node columns for this configuration.

    --no_protein_geometry drops BASE_NODE_COLUMNS and dependent EXTRA_NODE_COLUMNS.
    The node vector then uses descriptor broadcasts and/or ESM, loaded elsewhere.
    """
    if getattr(config, "no_protein_geometry", False):
        return []
    if getattr(config, "protein_extra_node_features", False):
        return list(BASE_NODE_COLUMNS) + list(EXTRA_NODE_COLUMNS)
    return list(BASE_NODE_COLUMNS)




class ProteinGraphData(Data):
    def __inc__(self, key, value, *args, **kwargs):
        # pair_id and candidate_group identify interaction rows/pairs, not nodes.
        # Do not apply PyG's default node-count offsets; candidate averaging needs
        # these original identifiers.
        if key in ("pair_id", "candidate_group"):
            return 0
        return super().__inc__(key, value, *args, **kwargs)


class ProteinGraphBuilder:
    @staticmethod
    def _cached_columns(geometric, columns, dtype=torch.float32):
        return torch.stack(
            [geometric[column].to(dtype=dtype) for column in columns],
            dim=-1,
        )

    def _check_node_width(self, parts, nodes_path):
        """Check node width against the encoder input, reporting mismatches before GAT.

        Each column set has its own cache (protein_node_columns and
        protein_graph_tensor_cache._cache_files), but CSV shape changes or missing
        hydrophobicity-augmented --protein_extra_node_features caches can still
        produce stale widths.
        """
        expected = getattr(self.config, "protein_node_feature_count", 3)
        width = int(parts["x"].shape[1])
        if width != expected:
            raise ValueError(
                f"{nodes_path}: protein node vector is {width} wide but the encoder "
                f"is sized for {expected}. Rebuild the matching tensor cache "
                "(data/build_protein_graph_tensor_cache.py, with --no_protein_geometry "
                "if that's this config's flag) or delete it so it gets rebuilt live "
                "during warm_caches"
            )
        return parts

    def _restrict_to_pockets(self, parts):
        """Remove non-pocket residues from the graph entirely.

        Unlike attention_by_pockets, which restricts attention keys but keeps full GAT
        propagation, this leaves only the pocket. Median size is 33/203 residues.
        The contact subgraph may be disconnected: opposite cavity sides need not touch.
        """
        if not getattr(self.config, "protein_pockets_only", False):
            return parts
        keep = parts["pocket"].bool()
        if int(keep.sum()) == 0:
            raise ValueError(
                "protein_pockets_only left a protein with no residues; its "
                "pocketness.pdb marks no side-chain atom as pocket"
            )
        return restrict_parts_to_mask(parts, keep)

    def _cached_protein_parts(
        self, cached, plm, node_confidence, nodes_path
    ):
        parts = dict(cached["base"])
        parts["plm"] = plm
        use_precomputed_geometric_nodes = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        # protein_edge_attention/protein_edge_mlp use the rigid frame, not the
        # geometric transformer's geometric_node_attr. Loading unused columns from
        # the same CSV is harmless and avoids another near-identical boolean path.
        use_frame = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        if use_precomputed_geometric_nodes:
            geometric = cached.get("geometric")
            if geometric is None:
                raise FileNotFoundError(
                    f"{os.path.dirname(nodes_path)}/geometric_transformer_nodes.csv "
                    "is required by --geometric_transformer/"
                    "--protein_edge_attention/--protein_edge_mlp; rebuild the protein "
                    "tensor cache after generating it"
                )
            parts["geometric_node_attr"] = self._cached_columns(
                geometric,
                ["contact_area", "contact_exposure"],
            )
            if use_frame:
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
        """Load real pLDDT/B-factor-derived confidence in graph-node order.

        build_consistent_esm3_pdb.py uses coarse_graph_nodes.csv order, so CSV row i,
        graph node i, and PLM row i align without another mapping.
        """
        confidence_df = pandas.read_csv(path)
        return torch.tensor(confidence_df["confidence"].values, dtype=torch.float32)

    def make_graph_protein(self,nodes,edges,inter,family,plm,pok,name,node_confidence=None) -> Data:
        """Build a protein graph from the named node and edge files."""
        parts = self.protein_graph_tensors(nodes, edges, plm, pok, node_confidence)
        return self.assemble_protein_graph(parts, inter, family)

    def assemble_protein_graph(self, parts, inter, family) -> Data:
        """Wrap cached protein tensors for one interaction row, adding its inter label.

        Reuse protein-only parts across rows. Preserve original key insertion order,
        which PyG uses when collating.
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
        if "frame_rotation" in parts:
            graph_kwargs["frame_rotation"] = parts["frame_rotation"]
            graph_kwargs["frame_translation"] = parts["frame_translation"]
        if "node_confidence" in parts:
            # Attach confidence only with use_esm3_v2_embeddings. PyG requires the same
            # keys across a batch and cannot mix tensors with missing/None fields.
            graph_kwargs["node_confidence"] = parts["node_confidence"]
        return ProteinGraphData(**graph_kwargs)



    def protein_graph_tensors(self, nodes, edges, plm, pok, node_confidence=None):
        """Parse one protein's node/edge CSVs, pocketness PDB, and embedding.

        get() caches these protein-only tensors by name instead of rereading per pair.
        """
        protein_name = os.path.basename(os.path.dirname(nodes))
        cached = getattr(self, "_protein_tensor_cache", {}).get(protein_name)
        if cached is not None:
            return self._restrict_to_pockets(
                self._check_node_width(
                    self._cached_protein_parts(cached, plm, node_confidence, nodes),
                    nodes,
                )
            )

        vertices=pandas.read_csv(nodes)
        edges=pandas.read_csv(edges)

        #vertices["hydrophobicity"]=vertices["residue_type"].map(hydrophobicity_keys)
        #bury=torch.tensor(vertices[["residue_mean_buriedness", "residue_min_buriedness", "residue_max_buriedness"]].values, dtype=torch.float32)
        bury=torch.tensor(vertices["residue_mean_buriedness"].values, dtype=torch.float32)
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56", "hydrophobicity"]].values, dtype=torch.float32) 
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56"]].values, dtype=torch.float32)
        x=torch.tensor(vertices[protein_node_columns(self.config)].values, dtype=torch.float32)
        if getattr(self.config, "protein_extra_node_features", False):
            residue_type = x[:, 0].long()
            if torch.any((residue_type < 0) | (residue_type >= len(KYTE_DOOLITTLE))):
                raise ValueError(
                    f"{nodes}: residue_type outside 0..{len(KYTE_DOOLITTLE) - 1}, "
                    "so the hydropathy lookup would be wrong rather than merely absent"
                )
            hydrophobicity = torch.tensor(
                KYTE_DOOLITTLE, dtype=torch.float32
            )[residue_type]
            x = torch.cat((x, hydrophobicity.unsqueeze(-1)), dim=-1)
        edge_index=torch.tensor(edges[["ID1_resSeq","ID2_resSeq"]].values, dtype=torch.int64) 
        edge_attr=torch.tensor(edges[["distance","area","boundary"]].values, dtype=torch.float32) # TODO: verify edge indexing.
        # TODO: consider covalent-bond features from the full graph.
        """
        if inter == 1:
            intera = torch.tensor([1,0],dtype=torch.int32)
        else:
            intera = torch.tensor([0,1],dtype=torch.int32)
        """
        dic={}
        for i in range(len(vertices["ID_resSeq"])):
            dic[int(vertices["ID_resSeq"][i])]=i
        # Disabled edge diagnostics built an unused list in Python:
        # 0.15 ms/sample, 0.4 s/epoch after the prints below were disabled.
        # import itertools
        # all_nodes = list(itertools.chain.from_iterable(edge_index.tolist()))
        # missing_keys = [x for x in all_nodes if dic.get(x) is None]
        #print("Missing keys in dic:", missing_keys)
        #print("Missing keys in dic:", missing_keys)
        edge_index.apply_(lambda x: dic.get(x, 0))  # -1 or some other sentinel
        #edge_index.apply_(dic.get())
        #pocket
        # Exclude backbone atoms from pocket membership.
        aal=["C","CA","CB","O","N"]
        dic={}
        lis=[]

        # TODO: simplify atom-feature parsing, possibly with CSV filtering.

        with open(pok,"r") as f:
            lines = f.readlines()
            if os.path.normpath(pok).endswith(os.path.normpath("graphs/RBP4/pocketness.pdb")):
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
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        # protein_edge_attention/protein_edge_mlp use the rigid frame, not the
        # geometric transformer's geometric_node_attr. Loading unused columns from
        # the same CSV is harmless and avoids another near-identical boolean path.
        use_frame = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        if use_precomputed_geometric_nodes:
            geometric_path = os.path.join(
                os.path.dirname(nodes), "geometric_transformer_nodes.csv"
            )
            if not os.path.exists(geometric_path):
                raise FileNotFoundError(
                    f"{geometric_path} is required by --geometric_transformer/"
                    "--protein_edge_attention/"
                    "--protein_edge_mlp; run "
                    "preprocessing/build_geometric_protein_graphs.py"
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
                geometric[["contact_area", "contact_exposure"]].values,
                dtype=torch.float32,
            )
            if use_frame:
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
        return self._restrict_to_pockets(self._check_node_width(parts, nodes))



    def protein_family(self, prot_file):
        """Read the protein family directly from interaction-table ProteinDomain.

        The recorded table has one value per LTPProtein across all 35 proteins.
        Do not duplicate it in the former data/protein_registry.csv, which could drift.
        """
        domains = self.sampled_split.loc[
            self.sampled_split["LTPProtein"] == prot_file, "ProteinDomain"
        ].unique()
        if len(domains) != 1:
            raise ValueError(
                f"{prot_file!r}: expected exactly one ProteinDomain in the interaction "
                f"table, found {list(domains)}"
            )
        return str(domains[0])

    def protein_family_one_hot(self, prot_file):
        """Return the 9-wide family one-hot without loading the graph.

        Match protein_graph_parts. Memoize before sampled_split is released after init.
        """
        cached = self._protein_family_cache.get(prot_file)
        if cached is not None:
            return cached
        family = self.protein_family(prot_file)
        tenfam = torch.zeros(9)
        for i in range(len(FAMILY_NAMES)):
            if FAMILY_NAMES[i] == family.strip():
                tenfam[i] = 1
        self._protein_family_cache[prot_file] = tenfam
        return tenfam

    def protein_graph_parts(self, prot_file):
        """Cache graph tensors and family one-hot per protein.

        Recorded train size: 1095 rows / 32 proteins. Without caching, each protein's
        two CSVs, pocketness PDB, and ESM3 embedding were read ~34 times per epoch,
        or ~5100 times in 150 epochs.
        """
        cached = self._protein_graph_cache.get(prot_file)
        if cached is not None:
            return cached

        # Use LTPProtein as artifact directory/prefix; no rename map or registry lookup.
        prot_file_emb = prot_file

        node_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_nodes.csv"
        edge_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_links.csv"
        pok = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/pocketness.pdb"
        use_esm3_v2 = getattr(self.config, "use_esm3_v2_embeddings", False)
        use_rnabang = any(
            (
                getattr(self.config, "rnabang_replace_esm3", False),
                getattr(self.config, "rnabang_full_protein_encoder", False),
            )
        )
        # v2 embeddings (preprocessing/embeddings/embed_protein_esm3_v2.py) use
        #  data/esm3_input/<stem>.pdb with normalized MSE/alt-conformations
        # (build_consistent_esm3_pdb.py). Only standard BOS/EOS trimming is needed,
        # unlike v1's per-protein token adjustments.
        esm3_tensor = None
        if not (
            getattr(self.config, "rnabang_replace_esm3", False)
            or getattr(self.config, "rnabang_full_protein_encoder", False)
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
            # Both variants add BOS/EOS around residue rows. Graph nodes match the ESM3
            # sequence after MSE conversion, so only these two rows are removed
            # (preprocessing/convert_mse_to_met.py).
            esm3_tensor = esm3_tensor[1:-1]

        frozen_replacement = (
            self.config.frozen_protein_embedding()
            if hasattr(self.config, "frozen_protein_embedding") else None
        )
        frozen_tensor = None
        if frozen_replacement is not None:
            suffix, expected_dim = frozen_replacement
            frozen_path = os.path.join(
                self.ROOT_DIR, f"embedding_{suffix}", f"{prot_file_emb}_{suffix}.pkl"
            )
            if not os.path.isfile(frozen_path):
                raise FileNotFoundError(
                    f"Expected {frozen_path}; generate it before training with this "
                    "flag (see proposals.md and preprocessing/embeddings/embed_protein_rnabang.py "
                    "for the alignment contract: one row per coarse_graph_nodes.csv row)"
                )
            with open(frozen_path, "rb") as handle:
                frozen_tensor = torch.as_tensor(
                    pickle.load(handle), dtype=torch.float32
                )
            if frozen_tensor.shape[-1] != expected_dim:
                raise ValueError(
                    f"{frozen_path}: width {frozen_tensor.shape[-1]} but the encoder "
                    f"is sized for {expected_dim}; set the matching "
                    "--<name>_embedding_dim"
                )

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

        if use_rnabang:
            plm_tensor = rnabang_tensor
        elif frozen_tensor is not None:
            # Replace ESM3; validate() forbids RNA-BAnG combinations, leaving one source.
            plm_tensor = frozen_tensor
        else:
            plm_tensor = esm3_tensor
        with open(node_file, 'r') as f:
            num_lines = sum(1 for line in f)
        # PLM row i must match graph node i (protein_encoder).
        # Raise on row-count mismatch instead of attaching shifted embeddings;
        # tests/test_esm3_alignment.py checks this invariant without training.
        if num_lines - plm_tensor.shape[0] != 1:
            raise ValueError(
                f"protein embedding<->graph node misalignment for {prot_file}: "
                f"{plm_tensor.shape[0]} trimmed embedding rows vs {num_lines - 1} "
                f"graph nodes (expected equal). Check RNA-BAnG/ESM3 preprocessing "
                f"input and residue alignment."
            )


        family = self.protein_family(prot_file)
        tenfam=torch.zeros(9)
        for i in range(len(FAMILY_NAMES)):
            if FAMILY_NAMES[i] == family.strip():
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
