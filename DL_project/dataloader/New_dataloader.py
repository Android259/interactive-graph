#cross attention on every layer, +=, 
# weight by pocketness, cross attention some times else, try another normalisation, regular normalisato=ion everywhere, geometric attention in far future
#look on the number of parameters
import copy
import gc
import os
import pickle
import random

import numpy as np
import pandas
import torch
from torch_geometric.data import Data, Dataset

from dataloader.grab_dataset_graph import GrabDatasetGraphMixin
from dataloader.lipid_graph_builder import LipidGraphBuilder
from dataloader.lipid_isomer_graph_builder import (
    LipidGraphData,
    LipidIsomerGraphBuilder,
)
from dataloader.protein_graph_builder import ProteinGraphBuilder, ProteinGraphData
from dataloader.protein_graph_tensor_cache import load_protein_graph_tensor_cache
from dataloader.sampler import (
    lipid_class_series,
    rebalance_excluded_group_negatives,
    sample_family_balanced_negatives,
    sample_lipid_class_balanced_negatives,
    sample_protein_balanced_negatives,
    split_and_sample_family_balanced_interactions,
    split_and_sample_interactions,
    split_and_sample_lipid_class_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
)

# 9 CRAL-TRIO, 2 LBP_BPI_CETP, 2 GLTP, 1 ML, 10 lipocalin, 3 START, 3 IP_trans, 3 scp2, 2 OSBP





#sample balanced way
class PLIDataset(
    GrabDatasetGraphMixin,
    LipidGraphBuilder,
    LipidIsomerGraphBuilder,
    ProteinGraphBuilder,
    Dataset,
):
    def __init__(self, root_dir, csv:pandas.DataFrame, seed, excluded_subgroups, config, excluded_groups=None) -> None:
        super().__init__(root=None, transform=None, pre_transform=None, pre_filter=None)

        self.ROOT_DIR = root_dir
        self.config = config
        self.seed = seed
        self.excluded_groups = {group.lower() for group in excluded_groups or []}
        self.excluded_subgroups = set(excluded_subgroups)
        self.protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
        self.protein_name_to_id = {name: idx for idx, name in enumerate(self.protein_names)}
        self.protein_id_to_name = {idx: name for name, idx in self.protein_name_to_id.items()}

        self._configure_sampling(config)
        self.csvtrue, self.csvfalse = self._sample_interactions(csv, seed)
        self.csvtrue["_tanimoto_orig_idx"] = self.csvtrue.index
        self.csvfalse["_tanimoto_orig_idx"] = self.csvfalse.index

        sampled_csv = pandas.concat([self.csvtrue, self.csvfalse])
        self.csvt = sampled_csv.set_index(
            pandas.Index(list(range(len(sampled_csv))))
        )
        del self.csvtrue, self.csvfalse, sampled_csv

        self.csvtrain, self.csvalidate, self.csvtest = self._split_interactions(seed)
        self.train_orig_indexes = torch.as_tensor(self.csvtrain["_tanimoto_orig_idx"].values, dtype=torch.long)

        # Two files with very different costs and very different reach:
        #
        #   Total_multiple_lipid_batch.npy    (214 KB) -- the pair id of every row.
        #       Needed by EVERY run: `id2pos` below is built from it, and that is what
        #       `tanimoto_pos` indexes for any sample weighting at all (protein group,
        #       protein class, ...), not just the Tanimoto one.
        #   Total_tanimoto_matrix_uint8.npy   (2.8 GB) -- the pairwise similarities.
        #       Read by `get_tanimoto_weights` and nothing else, so only --tanimoto_weight
        #       actually needs it.
        #
        # Loading the 2.8 GB matrix unconditionally made every run depend on a file that
        # is excluded from the cluster sync (scripts/cluster_sync_excludes.sh keeps
        # /data/*.csv and the embedding dirs, not *.npy). When it went missing on
        # Bigfoot, all 45 jobs of a batch died in `__init__` within seconds -- including
        # the ones that never asked for Tanimoto weights.
        tanimoto_batch_path = root_dir + "/Total_multiple_lipid_batch.npy"
        tanimoto_batch = np.load(tanimoto_batch_path, mmap_mode="r")
        train_idx = self.train_orig_indexes.numpy()
        selected = np.flatnonzero(np.isin(tanimoto_batch, train_idx))
        self.train_tanimoto_batch = torch.from_numpy(
            np.array(tanimoto_batch[selected], copy=True)
        )

        self.train_tanimoto_matrix = None
        if self.config.tanimoto_weight:
            tanimoto_matrix_path = root_dir + "/Total_tanimoto_matrix_uint8.npy"
            tanimoto_matrix = np.load(tanimoto_matrix_path, mmap_mode="r")
            self.train_tanimoto_matrix = torch.from_numpy(
                np.array(tanimoto_matrix[np.ix_(selected, selected)], copy=True)
            )
            del tanimoto_matrix
        del tanimoto_batch
        gc.collect()

        unique_batch_ids = torch.unique(self.train_tanimoto_batch, sorted=True)
        self.id2pos = {int(g): int((unique_batch_ids == g).nonzero(as_tuple=True)[0]) for g in unique_batch_ids.tolist()}

        self._indices = None
        self.transform = None

        self.smiles_encoding = None
        if not getattr(self.config, "lipid_graph_isomers", False):
            lipid_embedding_file = (
                "lipid_SMILES_isomeric_embedding.pkl"
                if self.config.lipid_isomers
                else "lipid_SMILES_embedding.pkl"
            )
            with open(os.path.join(self.ROOT_DIR, lipid_embedding_file), "rb") as f:
                self.smiles_encoding = pickle.load(f)
        self.lipid_graph_dir = os.path.join(self.ROOT_DIR, "lipid_graphs")
        self.lipid_graph_index = {}
        # Per-sample rebuild caches. Every entry is a pure function of inputs that are
        # fixed for the whole run -- the protein name (which fixes its graph files and
        # embedding), the lipid SMILES, the lipid embedding width -- so serving a cached
        # object is bit-identical to rebuilding it, only without the file parse.
        #
        # What they remove, measured at 89.5 ms per get() on the standard configuration:
        # the complete lipid edge graph (77 ms, rebuilt identically 1095 times an epoch),
        # the protein CSV/pocket/embedding parse (5.8 ms, and only 32 distinct proteins
        # back those 1095 rows), and the RDKit canonicalization behind the embedding
        # lookup.
        #
        # __iter__ clones the dataset with copy.copy, which is shallow, so the train,
        # validation and test clones share these dicts rather than filling three copies.
        # DataLoader workers fork after warm_caches(), so a pre-warmed cache is shared
        # copy-on-write instead of being rebuilt once per worker.
        self._protein_graph_cache = {}
        self._protein_tensor_cache = load_protein_graph_tensor_cache(self.ROOT_DIR)
        self._lipid_encoding_cache = {}
        self._lipid_graph_cache = {}
        self._complete_edge_index_cache = {}
        lipid_graph_index_path = os.path.join(self.lipid_graph_dir, "lipid_graph_index.csv")
        if getattr(self.config, "lipid_graph_isomers", False) and os.path.exists(lipid_graph_index_path):
            lipid_graph_index = pandas.read_csv(lipid_graph_index_path)
            self.lipid_graph_index = dict(
                zip(lipid_graph_index["canonical_smiles"], lipid_graph_index["graph_id"]))
        print(f"train : {self.csvtrain.shape}")
        print(f"valid : {self.csvalidate.shape}")
        print(f"test : {self.csvtest.shape}")
        self.csv = self.csvtrain
        self.pair_graph = None
        
        self.labelOH = {'PC':[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PC-O':[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PE':[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PS':[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PI':[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'BMP':[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PG/BMP':[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*HexCer':[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*HexCer':[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*Hex2Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*SM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*CerP':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHSM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*SM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'VA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DAG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PE-O':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'dCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'TAG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'tCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHOH*Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'FA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'LPE':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        'LPC':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                        'LPG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                        'FAL':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                        'd*SHexCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                        'LPE-O':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                        'PA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                        'PGP':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                        'CL':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}

        self._default_lipid_label = torch.tensor(
            self.labelOH["PC"], dtype=torch.int
        )

    def _configure_sampling(self, config):
        self.balance_excluded_group_negatives = getattr(
            config, "balance_excluded_group_negatives", False
        )
        self.balance_negatives_by_family = getattr(
            config, "balance_negatives_by_family", False
        )
        self.balanced_proteins = getattr(config, "balanced_proteins", False)
        self.balanced_lipid_classes = getattr(
            config, "balanced_lipid_classes", False
        )
        self.test_group = str(getattr(config, "test_group", "") or "").lower()

    def _sample_interactions(self, csv, seed):
        # Lipid-class balancing is a trade against protein balancing, not a
        # refinement. Per-protein matching already implies per-family matching.
        if self.balanced_lipid_classes:
            csvtrue, csvfalse = split_and_sample_lipid_class_balanced_interactions(
                csv, seed
            )
        elif self.balanced_proteins:
            csvtrue, csvfalse = split_and_sample_protein_balanced_interactions(
                csv, seed
            )
        elif self.balance_negatives_by_family:
            csvtrue, csvfalse = split_and_sample_family_balanced_interactions(
                csv, seed
            )
        else:
            csvtrue, csvfalse = split_and_sample_interactions(csv, seed)
        if self.excluded_groups and self.balance_excluded_group_negatives:
            csvfalse = rebalance_excluded_group_negatives(
                csv, csvfalse, self.excluded_groups, seed
            )
        return csvtrue, csvfalse

    def _split_interactions(self, seed):
        if self.excluded_groups:
            csvtrain = self.csvt[
                ~self.csvt["ProteinDomain"].str.lower().isin(self.excluded_groups)
            ]
        elif self.excluded_subgroups:
            csvtrain = self.csvt
        else:
            csvtrain = self.csvt.sample(frac=0.85, random_state=seed)

        if self.excluded_subgroups:
            csvtrain = csvtrain[
                ~csvtrain["LTPProtein"].isin(self.excluded_subgroups)
            ]

        excluded_data = self.csvt.drop(csvtrain.index)
        if self.test_group:
            domain_lower = excluded_data["ProteinDomain"].str.lower()
            csvtest = excluded_data[domain_lower == self.test_group].sample(frac=1)
            csvalidate = excluded_data[domain_lower != self.test_group].sample(frac=1)
        elif self.balance_excluded_group_negatives:
            positive_pool = excluded_data[excluded_data["Interaction"] == 1]
            negative_pool = excluded_data[excluded_data["Interaction"] == 0]
            positive_validate = positive_pool.sample(frac=0.5, random_state=seed)
            negative_validate = negative_pool.sample(frac=0.5, random_state=seed)
            csvalidate = pandas.concat(
                [positive_validate, negative_validate]
            ).sample(frac=1, random_state=seed)
            csvtest = excluded_data.drop(csvalidate.index).sample(frac=1)
        else:
            csvalidate = excluded_data.sample(frac=0.5, random_state=seed)
            csvtest = excluded_data.drop(csvalidate.index).sample(frac=1)
        return csvtrain, csvalidate, csvtest

    def get_tanimoto_weights(self):
        if self.train_tanimoto_matrix is None:
            raise RuntimeError(
                "Tanimoto weights need Total_tanimoto_matrix_uint8.npy, which is only "
                "loaded when tanimoto_weight is set. Pass --tanimoto_weight, or do not "
                "call this."
            )
        meany = self.train_tanimoto_matrix.float().mean(dim=1) / 255.0
        single_raws = torch.unique(self.train_tanimoto_batch)
        weights = torch.zeros(len(single_raws), dtype=torch.float32)
        for i, uid in enumerate(single_raws):
            weights[i] = 1.0 - meany[self.train_tanimoto_batch == uid].mean()

        return weights

    def get_protein_weights(self):
        protein_names = self.csvtrain["LTPProtein"].str.lower()
        groups = sorted(protein_names.dropna().unique().tolist())
        counts = torch.tensor(
            [(protein_names == group).sum() for group in groups],
            dtype=torch.float32,
        )
        group_weights = 1 - (counts / counts.sum())
        weight_by_group = dict(zip(groups, group_weights.tolist()))
        protein_group_weights = torch.zeros(len(self.id2pos), dtype=torch.float32)
        for pair_id, protein_name in zip(
            self.csvtrain["_tanimoto_orig_idx"].astype(int),
            protein_names,
        ):
            position = self.id2pos[int(pair_id)]
            protein_group_weights[position] = weight_by_group[protein_name]

        return protein_group_weights

    def get_protein_class_weights(self, square_root=False):
        """Return normalized inverse-frequency weights by protein and class."""
        protein_names = self.csvtrain["LTPProtein"].str.lower()
        labels = self.csvtrain["Interaction"].astype(int)
        counts = (
            pandas.DataFrame({"protein": protein_names, "label": labels})
            .value_counts()
            .to_dict()
        )
        weights = torch.zeros(len(self.id2pos), dtype=torch.float32)

        for pair_id, protein_name, label in zip(
            self.csvtrain["_tanimoto_orig_idx"].astype(int),
            protein_names,
            labels,
        ):
            count = counts[(protein_name, int(label))]
            denominator = count ** 0.5 if square_root else count
            weights[self.id2pos[int(pair_id)]] = 1.0 / denominator

        return weights / weights.mean().clamp_min(1e-8)

    def warm_caches(self, csv=None):
        """Build every protein graph and lipid encoding this split needs, up front.

        Called before the DataLoader forks its workers, so the workers inherit one warm
        cache copy-on-write instead of each filling its own during the first epoch.
        Lipid warming is skipped under lipid_random_choice, where the encoding path
        draws from the RNG and pre-touching rows would shift the random stream.

        Returns the entry count of each cache, for reporting.
        """
        frame = self.csv if csv is None else csv
        for prot_file in frame["LTPProtein"].dropna().unique().tolist():
            self.protein_graph_parts(prot_file)
        if not self.config.lipid_random_choice:
            seen = set()
            for _, row in frame.iterrows():
                key = (str(row["SmileGlobal"]), str(row["SmileFragment"]))
                if key in seen:
                    continue
                seen.add(key)
                if getattr(self.config, "lipid_graph_isomers", False):
                    self.make_graph_lipid(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
                else:
                    self.cached_lipid_encoding(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
        return {
            "proteins": len(self._protein_graph_cache),
            "lipid_encodings": len(self._lipid_encoding_cache),
            "lipid_graphs": len(self._lipid_graph_cache),
        }

    def cache_memory_bytes(self):
        """Resident bytes held by the caches, counting each storage once."""
        seen = {}

        def add(tensor):
            storage = tensor.untyped_storage()
            seen[storage.data_ptr()] = storage.nbytes()

        for parts, tenfam in self._protein_graph_cache.values():
            for value in parts.values():
                add(value)
            add(tenfam)
        for value in self._lipid_encoding_cache.values():
            for tensor in (value if isinstance(value, tuple) else (value,)):
                add(tensor)
        for entry in self._lipid_graph_cache.values():
            for tensor in entry.values():
                add(tensor)
        for tensor in self._complete_edge_index_cache.values():
            add(tensor)
        return sum(seen.values())

    def release_source_artifacts(self):
        """Release initialization-only objects after weights and caches exist."""
        released = []
        for name in ("full_csv", "csvtrue", "csvfalse", "csvtt"):
            if hasattr(self, name):
                delattr(self, name)
                released.append(name)

        for name in ("train_tanimoto_matrix", "train_tanimoto_batch"):
            if getattr(self, name, None) is not None:
                setattr(self, name, None)
                released.append(name)

        if getattr(self, "_protein_tensor_cache", None):
            self._protein_tensor_cache = {}
            released.append("protein_tensor_cache")

        can_release_embeddings = (
            self.smiles_encoding is not None
            and not self.config.lipid_random_choice
        )
        if can_release_embeddings:
            expected_keys = {
                (str(row["SmileGlobal"]), str(row["SmileFragment"]))
                for _, row in self.csvt.iterrows()
            }
            if expected_keys.issubset(self._lipid_encoding_cache):
                self.smiles_encoding = None
                released.append("smiles_encoding")
        if hasattr(self, "csvt"):
            del self.csvt
            released.append("csvt")
        return released

    def len(self):
        #lenght of combinations or lenght of structures/smiles?
        return len(self.csv)

    def _prepare_indexed_fields(self):
        """Materialize the columns and scalar tensors read by every get()."""
        self._protein_by_idx = self.csv["LTPProtein"].to_numpy(copy=False)
        self._smile_global_by_idx = self.csv["SmileGlobal"].to_numpy(copy=False)
        self._smile_fragment_by_idx = self.csv["SmileFragment"].to_numpy(
            copy=False
        )
        self._interaction_tensor = torch.tensor(
            self.csv["Interaction"].to_numpy(),
            dtype=torch.long,
        )
        orig_indexes = self.csv["_tanimoto_orig_idx"].to_numpy()
        self._sample_index_tensor = torch.tensor(
            orig_indexes, dtype=torch.long
        ).view(-1, 1)
        self._tanimoto_pos_tensor = torch.tensor(
            [
                self.id2pos.get(int(orig_idx), -1)
                for orig_idx in orig_indexes
            ],
            dtype=torch.long,
        ).view(-1, 1)
        self._protein_id_tensor = torch.tensor(
            [
                self.protein_name_to_id[protein]
                for protein in self._protein_by_idx
            ],
            dtype=torch.long,
        ).view(-1, 1)

    def __iter__(self):
        train_dataset = copy.copy(self)
        valid_dataset = copy.copy(self)
        test_dataset = copy.copy(self)
        train_dataset.csv = self.csvtrain
        valid_dataset.csv = self.csvalidate
        test_dataset.csv = self.csvtest
        train_dataset._prepare_indexed_fields()
        valid_dataset._prepare_indexed_fields()
        test_dataset._prepare_indexed_fields()
        train_dataset.pair_graph = train_dataset.build_current_pair_graph() if self.config.grab_loss else None
        valid_dataset.pair_graph = None
        test_dataset.pair_graph = None
        return iter((train_dataset, valid_dataset, test_dataset))

    def get(self, idx):
        protein = self._protein_by_idx[idx]
        smile_global = self._smile_global_by_idx[idx]
        smile_fragment = self._smile_fragment_by_idx[idx]
        if getattr(self.config, "lipid_graph_isomers", False):
            lipid_enc = None
            lipid_batch = None
        elif self.config.lipid_fragments_mask:
            lipid_enc, lipid_batch = self.cached_lipid_encoding(
                smile_global, smile_fragment
            )
        else:
            lipid_enc = self.cached_lipid_encoding(
                smile_global, smile_fragment
            )
            lipid_batch = None

        parts, tenfam = self.protein_graph_parts(protein)

        protein_graph = self.assemble_protein_graph(
            parts, self._interaction_tensor[idx], tenfam
        )
        return self.finish_sample(
            idx,
            protein_graph,
            lipid_enc,
            lipid_batch,
            smile_global,
            smile_fragment,
        )


    def finish_sample(
        self,
        idx,
        protein_graph,
        lipid_enc,
        lipid_batch,
        smile_global,
        smile_fragment,
    ):
        """Attach the per-row identifiers and build the lipid side of one sample."""
        #print(f"pocket shape : {pok.shape}")
        #print(pok)
        protein_graph.sample_index = self._sample_index_tensor[idx]
        protein_graph.tanimoto_pos = self._tanimoto_pos_tensor[idx]
        protein_graph.protein_id = self._protein_id_tensor[idx]
        if getattr(self.config, "lipid_graph_isomers", False):
            lipid_graph = self.make_graph_lipid(
                smile_global, smile_fragment
            )
        else:
            # No edge_index here any more. It used to hold the complete graph over the
            # 768 embedding columns (295296 edges), which nothing consumed: lip_edgidx
            # reaches the model only under lipid_graph_isomers, handled above, and
            # num_nodes is taken from x (72 rows), so the tensor never influenced
            # batching either. Building it cost 77 ms of the 89.5 ms spent per sample,
            # collating it 11.7 ms per batch, and shipping it from the workers 76 MB per
            # batch. complete_graph_edge_index still builds it, memoized, for any caller
            # that needs the complete graph back.
            #
            # Key order matters -- PyG collates a batch store key by key -- so the
            # remaining keys keep the order the two literal Data() calls used.
            lipid_kwargs = {
                "x": lipid_enc,
                "liplab": self._default_lipid_label,
            }
            if self.config.lipid_fragments_mask:
                lipid_kwargs["lipid_batch"] = lipid_batch
            lipid_graph = Data(**lipid_kwargs)

        return protein_graph , lipid_graph
