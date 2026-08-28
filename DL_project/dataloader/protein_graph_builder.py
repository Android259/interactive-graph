"""Load precomputed protein artifacts and assemble cached PyG graphs."""

import glob
import os
import pickle

import numpy
import pandas
import torch
from torch_geometric.data import Data

from dataloader.pair_descriptors import PROTEIN_DESCRIPTOR_NAMES as POCKET_DESCRIPTOR_NAMES

MAX_INCIDENT_EDGES = 21
EDGE_QUANTILES = (0, 10, 25, 50, 75, 90, 100)

# Base protein node vector. Positional: several paths index node[:, 0..2] directly
# (residue type, SASA, volume), so anything optional must be appended after these.
BASE_NODE_COLUMNS = ("residue_type", "residue_sas_area", "residue_volume")
# Appended by --protein_extra_node_features, in this order.
EXTRA_NODE_COLUMNS = ("residue_mean_ev28", "residue_mean_ev56")
# + hydrophobicity, which is derived rather than read. Must equal the increment
# ModelConfig.validate applies to protein_node_feature_count.
EXTRA_NODE_FEATURE_COUNT = len(EXTRA_NODE_COLUMNS) + 1

# Kyte & Doolittle (1982) hydropathy index, indexed by Voronota's residue_type code.
# That code is the alphabetical rank of the three-letter name, verified against
# ID_resName over all 35 proteins in data/graphs (one name per code, no collisions):
# ALA=0 ARG=1 ASN=2 ASP=3 CYS=4 GLN=5 GLU=6 GLY=7 HIS=8 ILE=9
# LEU=10 LYS=11 MET=12 PHE=13 PRO=14 SER=15 THR=16 TRP=17 TYR=18 VAL=19
KYTE_DOOLITTLE = (
    1.8, -4.5, -3.5, -3.5, 2.5, -3.5, -3.5, -0.4, -3.2, 4.5,
    3.8, -3.9, 1.9, 2.8, -1.6, -0.8, -0.7, -0.9, -1.3, 4.2,
)


# POCKET_DESCRIPTOR_NAMES itself now lives in dataloader/pair_descriptors.py
# (PROTEIN_DESCRIPTOR_NAMES, imported above) so the whole descriptor catalog --
# lipid, protein, pair -- is named in one file; the VALUES are still computed here,
# by pocket_descriptor() below, from coarse_graph_nodes.csv plus pocketness.pdb --
# ModelConfig.pocket_descriptor_count must equal len(POCKET_DESCRIPTOR_NAMES).

# --pocket_descriptors_family_neutral (training/read_configuration.py): the seven
# POCKET_DESCRIPTOR_NAMES entries whose eta^2 against the 9-family split sits at or
# near the no-structure floor of 0.24 (files/pocket_shape_descriptors.md section 5,
# preprocessing/pocket_descriptor_identity_check.py). Excludes the six entries closest
# to a pure family label: pocket_sasa_share (0.85), hydropathy_core (0.77),
# pocket_residue_share (0.71), pocket_extent (0.62), ev14_q50 (0.59), depth_q10 (0.55).
# Indices resolved from POCKET_DESCRIPTOR_NAMES itself so a reordering there cannot
# silently desync this list. Consumed only by architecture/protein_encoder.py's
# expand_pocket_descriptor (the --pocket_descriptors broadcast under the ordinary
# protein branch / --descriptors_in_protein_lipid) -- --descriptors_head's
# PairDescriptorHead never reads this full vector at all, only aromatic_share/
# polar_share (and hydropathy_core/rim under --pair_descriptor_pocket_shares_split) at
# their own fixed indices, so this flag has no effect there.
POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES = (
    "pocket_volume_per_sasa", "pocket_elongation", "pocket_flatness",
    "buriedness_q50", "apolar_sasa_share", "aromatic_share", "hydropathy_rim",
)
POCKET_DESCRIPTOR_FAMILY_NEUTRAL_INDICES = tuple(
    POCKET_DESCRIPTOR_NAMES.index(name) for name in POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES
)

# Voronota's residue_type code is alphabetical by one-letter code (verified against
# ID_resName), the same order KYTE_DOOLITTLE is indexed in; Phe, Trp, Tyr sit here.
AROMATIC_RESIDUE_TYPES = (13, 17, 18)
# Side chains only: a backbone atom is in every residue and says nothing about which
# ones line a cavity. Same set the pocket mask itself is built from.
POCKET_BACKBONE_ATOMS = ("C", "CA", "CB", "O", "N")


def pocket_atom_coordinates(pocketness_path):
    """Coordinates of the side-chain atoms pocketness.pdb marks as pocket.

    The same lines and the same flag column the pocket mask is read from, so the cloud
    measured here is the site the model is given, not a second opinion about it.
    """
    coordinates = []
    with open(pocketness_path) as handle:
        for line in handle:
            if len(line) < 63 or not line.startswith(("ATOM", "HETATM")):
                continue
            if line[13:17].strip() in POCKET_BACKBONE_ATOMS:
                continue
            if int(line[62]) <= 0:
                continue
            coordinates.append(
                (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            )
    return numpy.array(coordinates, dtype=float)


def pocket_shape(coordinates):
    """Extent, elongation and flatness of the cavity's atom cloud.

    The three axes are the principal components of the coordinates (PCA via the
    covariance matrix's eigenvectors -- only the DIRECTIONS are taken from it).
    Each axis' own LENGTH is the 5th-to-95th percentile span of the coordinates'
    projection onto it, not the axis' eigenvalue (or its square root) -- covariance
    is not robust, so a single stray atom at the cavity's rim can inflate the
    variance along its own direction by an amount ordinary PCA has no defence
    against. Percentile-trimming every axis this way, not just the first, closes
    that: an earlier version measured extent (axis 0's own span) exactly this way
    already, but took elongation/flatness straight from the eigenvalues, so the same
    stray atom that could not move extent could still distort the two ratios --
    verified: the ratio is between LENGTHS, not raw spread, so "twice as long" reads
    as 2 rather than 4, matching the earlier eigenvalue-ratio's own intent.

    Four atoms are the minimum for a covariance worth taking; below that the cavity is
    described by its residue-level entries alone and the shape entries are zeros, which
    the train-only standardisation then leaves at the mean.
    """
    if len(coordinates) < 4:
        return 0.0, 0.0, 0.0
    centered = coordinates - coordinates.mean(axis=0)
    eigenvalues, eigenvectors = numpy.linalg.eigh(numpy.cov(centered, rowvar=False))
    order = numpy.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, order]
    spans = numpy.array([
        numpy.percentile(projection, 95) - numpy.percentile(projection, 5)
        for projection in (centered @ eigenvectors).T
    ])
    spans = numpy.clip(spans, 1e-9, None)
    extent = float(spans[0])
    return extent, float(spans[0] / spans[1]), float(spans[1] / spans[2])


def pocket_descriptor(vertices, pocket, config=None, pocketness_path=None):
    """Aggregate one cavity descriptor from a protein's residue table and pocket mask.

    Returns ``[1, len(POCKET_DESCRIPTOR_NAMES)]`` so PyG collation stacks one row per
    sample. Shares and ratios are bounded and the two angstrom quantities span well
    under an order of magnitude across proteins, so nothing here is log-compressed; the
    train-only standardisation installed later handles the rest.

    ``pocketness_path`` supplies the atom coordinates the shape entries need. Without
    it those entries are zero -- a caller that has no PDB gets a usable descriptor
    rather than an exception, but it gets one with no shape in it.
    """
    mask = pocket.bool().numpy() if hasattr(pocket, "bool") else pocket
    site = vertices[mask]
    if len(site) == 0:
        raise ValueError("pocket_descriptors requires at least one pocket residue")
    residue_types = site["residue_type"].to_numpy(copy=True).astype(int)
    hydropathy = numpy.asarray(KYTE_DOOLITTLE)[residue_types]
    aromatic = numpy.isin(residue_types, AROMATIC_RESIDUE_TYPES)
    sasa = site["residue_sas_area"].values
    pocket_sasa = float(sasa.sum())
    pocket_volume = float(site["residue_volume"].sum())
    burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
    # The pocket's own median splits it into a depth and a mouth. Median, not a fixed
    # threshold: burial is not comparable across proteins, the split within one is.
    core = burial >= numpy.median(burial)
    rim = ~core
    extent, elongation, flatness = pocket_shape(
        pocket_atom_coordinates(pocketness_path)
        if pocketness_path is not None
        else numpy.empty((0, 3))
    )
    values = (
        len(site) / max(len(vertices), 1),
        pocket_sasa / max(float(vertices["residue_sas_area"].sum()), 1e-9),
        pocket_volume / max(pocket_sasa, 1e-9),
        extent,
        elongation,
        flatness,
        float(numpy.median(site["residue_mean_ev14"].to_numpy(dtype=float))),
        float(numpy.median(burial)),
        float(numpy.percentile(
            site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 10
        )),
        float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9)),
        float(aromatic.mean()),
        float(hydropathy[core].mean()),
        float(hydropathy[rim].mean()) if rim.any() else float(hydropathy.mean()),
    )
    if len(values) != len(POCKET_DESCRIPTOR_NAMES):
        raise ValueError("pocket descriptor list and name list disagree")
    expected = getattr(config, "pocket_descriptor_count", None)
    if expected not in (None, 0) and expected != len(values):
        # Caught here rather than as a shape mismatch inside the classifier, where the
        # number would arrive as an unexplained dimension.
        raise ValueError(
            f"pocket_descriptor_count is {expected} but the descriptor has "
            f"{len(values)} entries; ModelConfig and POCKET_DESCRIPTOR_NAMES disagree"
        )
    return torch.tensor(values, dtype=torch.float32).unsqueeze(0)


def restrict_parts_to_mask(parts, keep):
    """One protein's tensors reduced to the residues ``keep`` marks.

    Node tensors are subset and the graph keeps only edges whose *both* endpoints
    survive, renumbered into the compacted node range. Two callers want exactly this:
    the pocket restriction, whose mask is fixed and structural, and the residue
    subsampling augmentation, whose mask is redrawn per sample.

    ``edge_node_degree`` / ``edge_node_pairs`` are precomputed descriptions of each
    residue's contact environment in the *full* protein. They are subset, not
    recomputed, deliberately: they encode how buried the residue is, which is a property
    of the intact structure and is exactly what a reduced graph can no longer derive on
    its own.
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
        "x", "bury", "plm", "pocket", "geometric_node_attr", "edge_node_pairs",
        "edge_node_degree", "frame_rotation", "frame_translation", "node_confidence",
    ):
        value = restricted.get(name)
        if value is not None:
            restricted[name] = value[keep]
    return restricted


def protein_node_columns(config):
    """Voronota columns making up the protein node vector for this configuration.

    --no_protein_geometry drops BASE_NODE_COLUMNS (and EXTRA_NODE_COLUMNS with it,
    since the latter is meaningless without the former) -- the node vector is then
    built entirely from --descriptors_in_protein_lipid's broadcast and/or ESM,
    neither of which this function's caller reads.
    """
    if getattr(config, "no_protein_geometry", False):
        return []
    if getattr(config, "protein_extra_node_features", False):
        return list(BASE_NODE_COLUMNS) + list(EXTRA_NODE_COLUMNS)
    return list(BASE_NODE_COLUMNS)


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
        # Both are row identifiers rather than node indices: pair_id names the row in
        # the interaction table, candidate_group names the pair whose candidates the
        # averaged evaluation puts back together. Shifting either by the node count of
        # the preceding graphs, which is what PyG does by default, would turn them into
        # numbers that identify nothing.
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
        """Node vector width must match what the encoder's input layer was sized for.

        Also the guard against a stale cache: each column set (BASE_NODE_COLUMNS,
        or --no_protein_geometry's empty one) reads its own cache file (see
        protein_node_columns and protein_graph_tensor_cache._cache_files), but that
        file can still predate a source CSV changing shape, or --protein_extra_node_features
        can be turned on without its hydrophobicity-augmented cache existing yet --
        either way this is where the mismatch would otherwise turn into an
        unexplained shape error inside the GAT instead of a plain one here.
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
        """Drop every non-pocket residue from one protein's tensors.

        This is a stronger statement than ``attention_by_pockets``: there the GAT still
        propagates over the whole protein and only attention keys are restricted, here
        the rest of the structure is not in the graph at all. Median pocket is 33 of 203
        residues, so the surviving graph is small and may be disconnected -- edges
        between two pocket residues on opposite sides of the cavity do not exist in the
        contact graph.
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
            or getattr(self.config, "rnabang_frozen_node_adapter", False)
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        # protein_edge_attention/protein_edge_mlp only need the rigid frame below,
        # not geometric_node_attr/edge_node_pairs/edge_node_degree (those feed the
        # IPA/rnabang paths) -- loading them anyway is harmless (unused columns
        # from the same already-open CSV) and keeps this one boolean shared instead
        # of adding a third near-identical variant.
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
                    "is required by --geometric_transformer/--rnabang_frozen_node_adapter/"
                    "--protein_edge_attention/--protein_edge_mlp; rebuild the protein "
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
        if getattr(self.config, "pocket_descriptors", False):
            parts["pocket_descriptor"] = cached.get(
                "pocket_descriptor"
            ) if cached.get("pocket_descriptor") is not None else (
                self._memoized_pocket_descriptor(nodes_path, parts["pocket"])
            )
        return parts

    def _memoized_pocket_descriptor(self, nodes_path, pocket):
        """Cavity descriptor for one protein, read from its residue table once.

        The on-disk tensor cache predates this flag and does not carry the descriptor.
        Rather than force a rebuild of data/protein_graph_tensors.pt, recompute it here
        and keep it: the descriptor depends on the protein alone, so one CSV read per
        protein covers every interaction row that mentions it -- the same reasoning the
        surrounding per-protein cache is built on.
        """
        memo = getattr(self, "_pocket_descriptor_memo", None)
        if memo is None:
            memo = {}
            self._pocket_descriptor_memo = memo
        cached = memo.get(nodes_path)
        if cached is None:
            # pocketness.pdb sits beside the residue table, and the shape entries are
            # read from it -- the tensor cache carries the mask but not the atoms.
            cached = pocket_descriptor(
                pandas.read_csv(nodes_path),
                pocket,
                self.config,
                pocketness_path=os.path.join(
                    os.path.dirname(nodes_path), "pocketness.pdb"
                ),
            )
            memo[nodes_path] = cached
        return cached

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
        if "pocket_descriptor" in parts:
            # [1, D] per protein, so PyG concatenates it to [num_graphs, D] -- one row
            # per sample, aligned with the pooled partners rather than with nodes.
            graph_kwargs["pocket_descriptor"] = parts["pocket_descriptor"]
        return ProteinGraphData(**graph_kwargs)

    @staticmethod
    def _feature_mean_std(values):
        values = values.float()
        return (
            values.mean(dim=0),
            values.std(dim=0, unbiased=False).clamp_min(1e-6),
        )

    def pocket_descriptor_stats(self):
        """Mean/std of the cavity descriptor over unique TRAIN proteins only.

        Same rule as every other statistic here: validation and test proteins never
        contribute, so a held-out family cannot shift the scale the model was fitted
        under. Returns None when the flag is off.
        """
        if not getattr(self.config, "pocket_descriptors", False):
            return None
        descriptors = torch.cat([
            self.protein_graph_parts(name)[0]["pocket_descriptor"]
            for name in sorted(self.csvtrain["LTPProtein"].unique())
        ])
        mean, std = self._feature_mean_std(descriptors)
        return {"pocket_descriptor_mean": mean, "pocket_descriptor_std": std}

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
        if getattr(self.config, "pocket_descriptors", False):
            # Computed on the intact residue table on purpose: the shares compare the
            # pocket against the whole protein, which protein_pockets_only would have
            # already thrown away by the time _restrict_to_pockets runs.
            parts["pocket_descriptor"] = pocket_descriptor(
                vertices, poket, self.config, pocketness_path=pok
            )
        use_precomputed_geometric_nodes = (
            getattr(self.config, "geometric_transformer", False)
            or getattr(self.config, "rnabang_frozen_node_adapter", False)
            or getattr(self.config, "protein_edge_attention", False)
            or getattr(self.config, "protein_edge_mlp", False)
        )
        # protein_edge_attention/protein_edge_mlp only need the rigid frame below,
        # not geometric_node_attr/edge_node_pairs/edge_node_degree (those feed the
        # IPA/rnabang paths) -- loading them anyway is harmless (unused columns
        # from the same already-open CSV) and keeps this one boolean shared instead
        # of adding a third near-identical variant.
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
                    "--rnabang_frozen_node_adapter/--protein_edge_attention/"
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

    def protein_family(self, prot_file):
        """The protein's family, straight from the interaction table's ProteinDomain.

        ProteinDomain is a per-protein constant in the table (verified: exactly one
        value per LTPProtein across all 35), so it is the family. It used to be copied
        into data/protein_registry.csv and read back from there; the table is the
        source, and a second copy could only drift from it.
        """
        domains = self.csvt.loc[
            self.csvt["LTPProtein"] == prot_file, "ProteinDomain"
        ].unique()
        if len(domains) != 1:
            raise ValueError(
                f"{prot_file!r}: expected exactly one ProteinDomain in the interaction "
                f"table, found {list(domains)}"
            )
        return str(domains[0])

    def protein_graph_parts(self, prot_file):
        """Graph tensors and family one-hot of one protein, parsed once per protein.

        The train split holds 1095 rows over 32 distinct proteins, so without this the
        same two CSVs, pocketness PDB and ESM3 embedding were re-read about 34 times an
        epoch each, and 5100 times over a 150-epoch run.
        """
        cached = self._protein_graph_cache.get(prot_file)
        if cached is not None:
            return cached

        # Artifacts are filed under the interaction table's own protein name, so the
        # name in LTPProtein IS the directory / file prefix -- no rename map, no
        # registry lookup.
        prot_file_emb = prot_file

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
            # Both variants have one row per residue plus a BOS/EOS pair, and every
            # protein's graph now has one node per residue of the sequence ESM3 saw
            # (MSE residues are converted, not dropped -- see
            # preprocessing/convert_mse_to_met.py), so this is the whole adjustment.
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
                    "flag (see proposals.md and preprocessing/embed_protein_rnabang.py "
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

        if (
            getattr(self.config, "rnabang_with_esm3", False)
            or getattr(self.config, "rnabang_residual_with_esm3", False)
        ):
            # The frozen replacement takes ESM3's slot in the concatenation, so these
            # modes compose with it: cat(ProteinMPNN, RNA-BAnG) rather than
            # cat(ESM3, RNA-BAnG). Scales differ wildly between sources -- see the bng
            # post-mortem in proposals.md -- so whatever goes in here should be brought
            # to a comparable magnitude before it can contribute.
            first = (
                frozen_tensor
                if frozen_tensor is not None
                else torch.as_tensor(esm3_tensor, dtype=torch.float32)
            )
            plm_tensor = torch.cat((first, rnabang_tensor), dim=-1)
        elif use_rnabang:
            plm_tensor = rnabang_tensor
        elif frozen_tensor is not None:
            # Replaces ESM3 outright: validate() rejects combining this with any
            # RNA-BAnG mode, so exactly one source reaches the encoder.
            plm_tensor = frozen_tensor
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


        family = self.protein_family(prot_file)
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
