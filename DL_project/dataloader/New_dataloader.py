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

from dataloader.dataset_source import interaction_csv_path
from dataloader.chemistry_prior import (
    fit_prior_calibration,
    null_scores,
    null_scores_leave_one_row_out,
    species_similarity,
)
from dataloader.pocket_lipid_compatibility import raw_compatibility
from dataloader.grab_dataset_graph import GrabDatasetGraphMixin
from dataloader.lipid_embedding_store import load_lipid_embedding_store
from dataloader.lipid_graph_builder import LipidGraphBuilder
from dataloader.lipid_isomer_graph_builder import (
    LipidGraphData,
    LipidIsomerGraphBuilder,
)
from dataloader.protein_graph_builder import (
    ProteinGraphBuilder,
    ProteinGraphData,
    restrict_parts_to_mask,
)
from dataloader.protein_graph_tensor_cache import load_protein_graph_tensor_cache
from dataloader.tanimoto_compact import load_compact
from dataloader.sampler import (
    COLDSPLIT_MINIMUM_TEST_POSITIVES,
    LIPID_COLDSPLIT_SETS,
    lipid_class_series,
    lipid_classes_for_holdout,
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
        self._derive_lipid_class_holdout(csv)
        self.csvtrue, self.csvfalse = self._sample_interactions(csv, seed)
        self.csvtrue["pair_id"] = self.csvtrue.index
        self.csvfalse["pair_id"] = self.csvfalse.index

        sampled_csv = pandas.concat([self.csvtrue, self.csvfalse])
        self.csvt = sampled_csv.set_index(
            pandas.Index(list(range(len(sampled_csv))))
        )
        del self.csvtrue, self.csvfalse, sampled_csv

        self.csvtrain, self.csvalidate, self.csvtest = self._split_interactions(seed)
        self.train_orig_indexes = torch.as_tensor(self.csvtrain["pair_id"].values, dtype=torch.long)

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
        # Only Tanimoto weighting needs this file. The protein-group and protein-class
        # weights use id2pos purely as *cell addresses*: get_protein_weights writes
        # weights[id2pos[pair_id]] and the loss reads that same cell back through
        # tanimoto_pos, so any bijection row-id -> 0..N-1 yields the identical vector.
        # get_tanimoto_weights is the one that cannot: it averages similarity over the
        # matrix rows belonging to one interaction, and which rows those are is exactly
        # what this file records and what no renumbering can reconstruct.
        #
        # Ranking the train row ids reproduces the file's own bijection rather than
        # merely an equivalent one, because the file covers the interaction table
        # completely -- 11018 rows, 11018 distinct ids, none missing, checked against
        # Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted.csv.
        # Both maps are then "rank among the sorted train ids", entry for entry. Should a
        # future table stop covering every row, the two would diverge: the file's map
        # omits the uncovered ids and id2pos.get(..., -1) hands those rows position -1,
        # which indexes the LAST weight rather than raising, so they would silently carry
        # another protein's weight. The ranked map has a position for every train row and
        # cannot do that.
        self._needs_tanimoto_rows = bool(self.config.tanimoto_weight)

        self.train_tanimoto_batch = None
        self.train_tanimoto_matrix = None
        if self._needs_tanimoto_rows:
            train_idx = self.train_orig_indexes.numpy()
            # The compact pair (preprocessing/build_tanimoto_compact.py) stores one row
            # per distinct structure instead of one per candidate instance, so it
            # expands to the identical submatrix out of 1.4 MiB rather than slicing it
            # out of a 2.89 GB file with random access. Byte-identical by construction --
            # see dataloader/tanimoto_compact.py -- and verified against the full matrix.
            #
            # Which pair: the isomeric artifacts for an isomeric run, matching the
            # canonicalization the loader itself uses. NOTE this is a real change for
            # --lipid_isomers --tanimoto_weight runs, which previously got the
            # non-isomeric similarities because only one full matrix ever existed; those
            # runs are not comparable with earlier ones. Non-isomeric runs are unaffected.
            compact = load_compact(
                root_dir,
                source_csv=interaction_csv_path(root_dir),
                isomeric=bool(getattr(self.config, "lipid_isomers", False)),
            )
            if compact is not None:
                selected = np.flatnonzero(np.isin(compact.row_ids, train_idx))
                self.train_tanimoto_batch = torch.from_numpy(
                    np.array(compact.row_ids[selected], copy=True)
                )
                self.train_tanimoto_matrix = torch.from_numpy(
                    compact.submatrix(selected)
                )
            else:
                tanimoto_batch_path = root_dir + "/Total_multiple_lipid_batch.npy"
                tanimoto_batch = np.load(tanimoto_batch_path, mmap_mode="r")
                selected = np.flatnonzero(np.isin(tanimoto_batch, train_idx))
                self.train_tanimoto_batch = torch.from_numpy(
                    np.array(tanimoto_batch[selected], copy=True)
                )
                tanimoto_matrix_path = root_dir + "/Total_tanimoto_matrix_uint8.npy"
                tanimoto_matrix = np.load(tanimoto_matrix_path, mmap_mode="r")
                self.train_tanimoto_matrix = torch.from_numpy(
                    np.array(tanimoto_matrix[np.ix_(selected, selected)], copy=True)
                )
                del tanimoto_matrix, tanimoto_batch
            gc.collect()

            unique_batch_ids = torch.unique(self.train_tanimoto_batch, sorted=True)
            self.id2pos = {int(g): int((unique_batch_ids == g).nonzero(as_tuple=True)[0]) for g in unique_batch_ids.tolist()}
        else:
            # Same mapping the file's own path builds (see above), without the file: the
            # pass of np.isin over all 53762 matrix rows and the quadratic scan that
            # turned them into id2pos are both startup work that a run without
            # --tanimoto_weight never had a use for.
            self.id2pos = {
                int(pair_id): position
                for position, pair_id in enumerate(
                    sorted(set(self.train_orig_indexes.tolist()))
                )
            }

        self._indices = None
        self.transform = None

        self.smiles_encoding = None
        if not getattr(self.config, "lipid_graph_isomers", False):
            # The non-isomeric table is the deterministic rebuild: 1226 entries, every
            # candidate of every row (the previous one held 434 and covered all
            # candidates of only 44% of rows), and all of them encoded with the
            # checkpoint's trained random-feature matrix. MoLFormer's linear attention
            # resamples that matrix on every forward, so the older table gave each entry
            # its own draw and could not be reproduced -- two encodings of one SMILES
            # differ by up to 8.8 on values spanning +-10. Runs on the two tables are
            # therefore not comparable; lipid_SMILES_embedding.pkl is kept for the old
            # ones. The isomeric table still has the old behaviour and is due the same
            # rebuild.
            lipid_embedding_file = (
                "lipid_SMILES_isomeric_embedding.pkl"
                if self.config.lipid_isomers
                else "lipid_SMILES_embedding_deterministic.pkl"
            )
            # Prefer the memory-mapped store, so concurrent jobs share one copy of the
            # table through the page cache instead of unpickling 267 MiB apiece (see
            # dataloader/lipid_embedding_store.py, and data/build_lipid_embedding_store.py
            # which writes it). Same tensors either way; None means no store has been
            # built for this table yet, or the table has been regenerated since, and the
            # pickle is read exactly as before.
            self.smiles_encoding = load_lipid_embedding_store(
                self.ROOT_DIR, lipid_embedding_file
            )
            if self.smiles_encoding is None:
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
        # lipid_random_choice fills this one instead: the drawn encoding must not be
        # cached (that would freeze the draw for the whole run), only the canonical
        # keys it draws from. See LipidGraphBuilder._drawn_lipid_encoding.
        self._lipid_candidate_key_cache = {}
        self._lipid_graph_cache = {}
        self._complete_edge_index_cache = {}
        # Assembled samples, keyed by pair_id -- see get(). Only sound while a row's
        # sample is a pure function of the row: lipid_random_choice draws a fresh
        # candidate on every access by design, and a cached sample would freeze that draw
        # for the whole run, degenerating the mode into "one arbitrary fixed candidate per
        # row" -- precisely what it exists to replace. It can be supported by caching the
        # protein graph plus one Data per candidate and drawing among them, but that has
        # to be checked against the random stream first, so for now the mode simply keeps
        # rebuilding.
        self._sample_cache = {}
        self._sample_cache_enabled = not self.config.lipid_random_choice
        # Residue subsampling is per split and per epoch; both are set from outside --
        # the split in __iter__, the epoch by the training loop through set_epoch.
        self._augment_residues = False
        self._augmentation_epoch = 0
        lipid_graph_index_path = os.path.join(self.lipid_graph_dir, "lipid_graph_index.csv")
        if getattr(self.config, "lipid_graph_isomers", False) and os.path.exists(lipid_graph_index_path):
            lipid_graph_index = pandas.read_csv(lipid_graph_index_path)
            self.lipid_graph_index = dict(
                zip(lipid_graph_index["canonical_smiles"], lipid_graph_index["graph_id"]))
        print(f"train : {self.csvtrain.shape}")
        print(f"valid : {self.csvalidate.shape}")
        print(f"test : {self.csvtest.shape}")
        self._report_lipid_prior_baseline()
        raw_columns = self._raw_frozen_prior_columns(csv)
        self._compute_frozen_prior(raw_columns)
        self._compute_compatibility_input(raw_columns)
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

        # labelOH itself stays: the isomer graph path reads it for the real per-lipid
        # class. What is gone is the constant "PC" tensor that used to be attached to
        # every sample of the embedding path as `liplab` -- see finish_sample.

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
        # Negatives drawn per positive inside each balancing group. 1 is the exact 1:1
        # the samplers were written for; see dataloader/sampler.py.
        self.negatives_per_positive = int(
            getattr(config, "negatives_per_positive", 2) or 2
        )
        # Head-group classes held out of training alongside excluded_groups: the second
        # axis of the cold split. Compared case-insensitively, as the groups are.
        # The second axis of the cold split; the classes themselves are derived in
        # _derive_lipid_class_holdout, which needs the full table.
        self.double_coldsplit = bool(getattr(config, "double_coldsplit", False))
        self.mixed_coldsplit = bool(getattr(config, "mixed_coldsplit", False))
        self.coldsplit_share = float(getattr(config, "coldsplit_share", 0.7) or 0.7)
        # The lipid axis on its own: a named chemical family leaves training, every
        # protein stays. Unlike the two above it needs no held-out family to derive its
        # classes from -- the sets are fixed.
        self.lipid_coldsplit = str(getattr(config, "lipid_coldsplit", "") or "")
        self.excluded_lipid_classes = set()
        self.test_group = str(getattr(config, "test_group", "") or "").lower()

    @staticmethod
    def _label_only_baseline(csvtrain, held, key_train, key_held):
        """Balanced accuracy of "this key was usually positive in train", and coverage.

        No protein, no structure, no model: the train positive rate of the key,
        thresholded at 0.5, with the train majority standing in for keys train never
        saw. Keys with no training rows therefore score at chance by construction.
        """
        rate = csvtrain.groupby(key_train)["Interaction"].mean()
        fallback = int(csvtrain["Interaction"].mean() > 0.5)
        looked_up = key_held.map(rate)
        seen = looked_up.notna()
        prediction = (looked_up > 0.5).astype(int).where(seen, fallback)

        truth = held["Interaction"] == 1
        if not truth.any() or truth.all():
            return float("nan"), float(seen.mean())
        sensitivity = float((prediction[truth] == 1).mean())
        specificity = float((prediction[~truth] == 0).mean())
        return (sensitivity + specificity) / 2, float(seen.mean())

    def _report_lipid_prior_baseline(self):
        """Print what a per-lipid label prior alone scores on this run's valid and test.

        The number every metric of this run has to be read against. The split is cold in
        the protein only unless a lipid-class holdout is on, and the lipids of a held-out
        family have all been seen in train paired with other proteins, so "this lipid is
        usually positive" transfers across the cut and reaches 0.55-0.57 balanced
        accuracy with no model involved -- on some families 0.77. Comparing a run to 0.5
        instead of to this makes a lookup table look like a working model.

        Printed here, from the same frames the run trains on, so the figure lives in the
        run's own log rather than having to be reconstructed afterwards by
        preprocessing/lipid_marginal_baseline.py -- which computes the same thing and is
        the place to look for the cross-family picture.

        Under --double_coldsplit both columns come out at 0.500 and coverage at 0: every
        evaluated lipid belongs to a held-out class, every lookup falls back. That is the
        check that the split is what it claims to be, and it costs one groupby.
        """
        classes = lipid_class_series(self.csvtrain)
        for name, held in (("valid", self.csvalidate), ("test", self.csvtest)):
            if held.empty:
                continue
            by_lipid, seen = self._label_only_baseline(
                self.csvtrain,
                held,
                self.csvtrain["FullIdentityOfLipid"],
                held["FullIdentityOfLipid"],
            )
            by_class, _ = self._label_only_baseline(
                self.csvtrain, held, classes, lipid_class_series(held)
            )
            print(
                f"lipid prior baseline {name} : balanced accuracy "
                f"{by_lipid:.3f} by lipid, {by_class:.3f} by class "
                f"| {seen:.0%} of rows have their lipid in train"
            )

    def _raw_frozen_prior_columns(self, csv):
        """Raw, uncalibrated values for whichever frozen-prior covariates are on.

        Returns an ordered dict name -> (train_values, valid_values, test_values).
        Shared by _compute_frozen_prior (--chem_prior, --pocket_compat_prior) and
        _compute_compatibility_input (--compatibility_input) so a run using both
        --pocket_compat_prior and --compatibility_input pays for the pocket-atom read
        and the RDKit parse once, not twice.

        `csv` is the ORIGINAL interaction table as passed into __init__, not
        `self.csvt` -- both species_similarity (Tanimoto_compact_isomeric_row_ids.npy)
        and pocket_lipid_compatibility index by that file's row positions, and
        self.csvt has already been through negative sampling, which would shift them.
        """
        columns = {}
        # chem_adversary requires chem_prior (ModelConfig.validate), so checking
        # chem_prior alone already covers both.
        if getattr(self.config, "chem_prior", False):
            similarity, index = species_similarity(csv, self.ROOT_DIR)
            neighbours = self.config.chem_neighbours
            train = null_scores_leave_one_row_out(self.csvtrain, similarity, index, neighbours)
            valid = (
                null_scores(self.csvtrain, self.csvalidate["FullIdentityOfLipid"], similarity, index, neighbours)
                if not self.csvalidate.empty else np.array([], dtype=float)
            )
            test = (
                null_scores(self.csvtrain, self.csvtest["FullIdentityOfLipid"], similarity, index, neighbours)
                if not self.csvtest.empty else np.array([], dtype=float)
            )
            columns["s_chem"] = (train, valid, test)
        if getattr(self.config, "pocket_compat_prior", False) or getattr(self.config, "compatibility_input", False):
            # raw_compatibility reads Interaction nowhere, so unlike s_chem there is no
            # leave-one-out to do: a training row's own label cannot leak into a
            # quantity built from pocket geometry and lipid structure alone.
            all_values, missing = raw_compatibility(csv, self.ROOT_DIR)
            if missing.any():
                train_missing = missing[self.csvtrain.index]
                train_usable = all_values[self.csvtrain.index][~train_missing]
                # 0.0 only if EVERY train row is unparseable, which would mean the
                # term carries no information for this run at all; the print makes
                # that degenerate case visible rather than a silent constant.
                fill = float(train_usable.mean()) if len(train_usable) else 0.0
                print(
                    f"pocket-lipid compatibility : {int(missing.sum())} of {len(all_values)} rows "
                    f"had no parseable chain length, filled with the train mean ({fill:.2f})"
                )
                all_values = np.where(missing, fill, all_values)
            columns["compat"] = (
                all_values[self.csvtrain.index],
                all_values[self.csvalidate.index] if not self.csvalidate.empty else np.array([], dtype=float),
                all_values[self.csvtest.index] if not self.csvtest.empty else np.array([], dtype=float),
            )
        return columns

    def _compute_frozen_prior(self, raw_columns):
        """Attach the frozen, calibrated additive term(s) -- variant A.

        Whichever of s_chem (--chem_prior) and compatibility (--pocket_compat_prior)
        are active are fit JOINTLY (fit_prior_calibration, dataloader/chemistry_prior.py)
        on TRAIN LABELS ONLY and frozen -- see that function's docstring for why this is
        not a torch.nn.Parameter, and why joint rather than independent fits when both
        terms are present. The combined value is stored as `_frozen_prior`, the single
        number Final_Layer adds to the logit; the model never sees s_chem and
        compatibility as separate quantities on this path, only their calibrated sum.
        """
        wanted = [name for name in ("s_chem", "compat") if (
            (name == "s_chem" and getattr(self.config, "chem_prior", False))
            or (name == "compat" and getattr(self.config, "pocket_compat_prior", False))
        )]
        if not wanted:
            return
        design_train = np.column_stack([raw_columns[name][0] for name in wanted])
        means, spreads, intercept, weights = fit_prior_calibration(
            design_train, self.csvtrain["Interaction"].to_numpy()
        )
        print(
            "frozen prior calibration : intercept {:.3f}, weights {} (covariates: {}, "
            "fit on {} train rows)".format(
                intercept, {n: round(float(w), 3) for n, w in zip(wanted, weights)},
                wanted, len(design_train),
            )
        )

        def combine(split_index):
            design = np.column_stack([raw_columns[name][split_index] for name in wanted])
            return intercept + ((design - means) / spreads) @ weights

        self.csvtrain = self.csvtrain.assign(_frozen_prior=combine(0))
        for split_index, name in ((1, "csvalidate"), (2, "csvtest")):
            frame = getattr(self, name)
            value = combine(split_index) if not frame.empty else np.array([], dtype=float)
            setattr(self, name, frame.assign(_frozen_prior=value))

    def _compute_compatibility_input(self, raw_columns):
        """Attach the standardised (not calibrated) compatibility term -- variant B.

        No fitted weight: this is meant to be read by the network itself
        (Final_Layer concatenates it into the fused representation under
        --compatibility_input), so a fitted coefficient here would just be redone,
        redundantly, by the classifier's own first layer. Standardised on TRAIN values
        only, same discipline as everywhere else a train-only statistic feeds a split
        it was not computed from.
        """
        if not getattr(self.config, "compatibility_input", False):
            return
        train_raw, valid_raw, test_raw = raw_columns["compat"]
        mean, spread = train_raw.mean(), train_raw.std()
        spread = spread if spread > 1e-12 else 1.0
        self.csvtrain = self.csvtrain.assign(_compat_input=(train_raw - mean) / spread)
        for raw, name in ((valid_raw, "csvalidate"), (test_raw, "csvtest")):
            frame = getattr(self, name)
            value = (raw - mean) / spread if not frame.empty else np.array([], dtype=float)
            setattr(self, name, frame.assign(_compat_input=value))

    def _derive_lipid_class_holdout(self, csv):
        """Work out which head-group classes leave training, from the held-out family.

        Derived rather than configured: the right set differs per family -- START's
        positives are phosphatidylcholines, GLTP's are sphingolipids -- so a set fixed
        in advance would be arbitrary for whichever family this run holds out. The rule
        lives in dataloader.sampler.lipid_classes_for_holdout and is read off the FULL
        table, not the sampled pool, so the class set does not drift with the seed or
        with negatives_per_positive.

        Several excluded groups take the union of their sets, which is the conservative
        reading: every one of them must find its own classes absent from training.

        Printed because the list is a property of the split that nothing else records,
        and a run's log is where that has to be recoverable from.
        """
        if self.lipid_coldsplit:
            classes = LIPID_COLDSPLIT_SETS.get(self.lipid_coldsplit)
            if classes is None:
                # Only reachable if the name table in read_configuration and the class
                # table here drift apart; say so rather than failing on a KeyError.
                raise ValueError(
                    f"lipid_coldsplit set {self.lipid_coldsplit!r} is accepted by the "
                    "configuration but absent from LIPID_COLDSPLIT_SETS"
                )
            self.excluded_lipid_classes = {name.lower() for name in classes}
            positives = int(
                csv.loc[lipid_class_series(csv).isin(classes), "Interaction"].sum()
            )
            print(
                f"lipid cold split '{self.lipid_coldsplit}' : {len(classes)} classes "
                f"held out of training for every protein, {positives} positives"
            )
            print(f"  {', '.join(classes)}")
            return

        if not (self.double_coldsplit or self.mixed_coldsplit):
            return

        chosen = {}
        for group in sorted(self.excluded_groups):
            classes, covered, cost = lipid_classes_for_holdout(
                csv, group, self.coldsplit_share
            )
            chosen.update({name.lower(): name for name in classes})
            note = (
                ""
                if covered >= COLDSPLIT_MINIMUM_TEST_POSITIVES
                else f"  [only {covered} positives, too few for a test block]"
            )
            print(
                f"lipid class holdout for {group} : {len(classes)} classes, "
                f"{covered} positives held out, costing train {cost} positives{note}"
            )
            print(f"  {', '.join(classes)}")
        self.excluded_lipid_classes = set(chosen)

    def _sample_interactions(self, csv, seed):
        # Lipid-class balancing is a trade against protein balancing, not a
        # refinement. Per-protein matching already implies per-family matching.
        # Which side of the coming lipid-class cut each row falls on. Passed to the
        # per-protein and per-family samplers so they match negatives to positives
        # WITHIN each side: otherwise a protein's negatives can all be drawn from
        # classes that then leave training, and it reaches the train block with
        # positives and nothing to contrast them against. The per-(group, class)
        # sampler needs no such hint -- a class is held out whole, so its cells already
        # sit on one side of the cut.
        strata = None
        if self.excluded_lipid_classes:
            strata = (
                lipid_class_series(csv).str.lower().isin(self.excluded_lipid_classes)
            )

        if self.balanced_lipid_classes:
            csvtrue, csvfalse = split_and_sample_lipid_class_balanced_interactions(
                csv, seed, ratio=self.negatives_per_positive
            )
        elif self.balanced_proteins:
            csvtrue, csvfalse = split_and_sample_protein_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata
            )
        elif self.balance_negatives_by_family:
            csvtrue, csvfalse = split_and_sample_family_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata
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
        elif self.excluded_subgroups or self.lipid_coldsplit:
            # lipid_coldsplit keeps every protein: the whole table is train until the
            # class filter below removes the held-out chemistry. The random 85% draw of
            # the last branch would mix an ordinary split into it and make the held-out
            # classes only part of what is evaluated.
            csvtrain = self.csvt
        else:
            csvtrain = self.csvt.sample(frac=0.85, random_state=seed)

        if self.excluded_subgroups:
            csvtrain = csvtrain[
                ~csvtrain["LTPProtein"].isin(self.excluded_subgroups)
            ]

        # The second axis. Held-out classes leave train for EVERY protein, not only the
        # held-out family, which is the whole point: a row of the held-out family in a
        # held-out class then has neither its protein nor its lipid class anywhere in
        # train, so the per-lipid label prior that carries a one-axis split (0.55-0.57
        # balanced accuracy on its own) has nothing to be estimated from. Everything the
        # filter removes joins excluded_data below and is split into valid and test by
        # the same code as before -- only train's definition narrows here.
        if self.excluded_lipid_classes:
            train_classes = lipid_class_series(csvtrain).str.lower()
            csvtrain = csvtrain[~train_classes.isin(self.excluded_lipid_classes)]

        excluded_data = self.csvt.drop(csvtrain.index)

        # --double_coldsplit: the held-out family's rows in classes that stayed in train
        # are dropped rather than evaluated. Their lipids ARE in train -- paired with
        # other proteins -- so keeping them lets a per-lipid label prior score on them,
        # which is the leak the class holdout exists to close; measured, they hold the
        # prior at 0.498 instead of the 0.500 the rest of the pool gives. They cannot go
        # to train either, since their protein is held out. Dropping costs 3-17% of the
        # working set and nothing from train, which never contained them.
        if self.double_coldsplit and self.excluded_lipid_classes:
            excluded_classes = lipid_class_series(excluded_data).str.lower()
            excluded_data = excluded_data[
                excluded_classes.isin(self.excluded_lipid_classes)
            ]
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
            self.csvtrain["pair_id"].astype(int),
            protein_names,
        ):
            position = self.id2pos[int(pair_id)]
            protein_group_weights[position] = weight_by_group[protein_name]

        return protein_group_weights

    def get_protein_balance_weights(self):
        """Per-row weights that restore each protein's pos:neg ratio inside train.

        The negative sampler matches counts per protein over the WHOLE table, before
        the split. Holding out protein families keeps that match intact -- whole
        proteins leave, the survivors' cells are untouched -- but holding out lipid
        classes cuts across proteins, and it cuts unevenly: a protein whose positives
        sat in a held-out class loses almost all of them and almost none of its
        negatives. STARD2 comes out of a two-axis split at 4 positive against 91
        unlabeled.

        Re-running the 1:1 match inside the train block would restore the ratio by
        discarding, and it would discard hardest from exactly those proteins -- STARD2
        would fall from 95 rows to 8. This restores it by weighting instead: a positive
        weighs 1, a negative weighs its protein's positives over its negatives, so the
        two sides of every protein carry equal total weight and no row is thrown away.

        Proteins left with no positives at all contribute zero weight on both sides,
        which is correct: train holds no labelled example of them any more.

        Returned normalized by the mean, matching the other weight tables here, and
        indexed by ``id2pos`` like them so ``batch_sample_weights`` can gather it.
        """
        protein_names = self.csvtrain["LTPProtein"].str.lower()
        labels = self.csvtrain["Interaction"].astype(int)
        counts = (
            pandas.DataFrame({"protein": protein_names, "label": labels})
            .value_counts()
            .to_dict()
        )
        weights = torch.zeros(len(self.id2pos), dtype=torch.float32)

        for pair_id, protein_name, label in zip(
            self.csvtrain["pair_id"].astype(int),
            protein_names,
            labels,
        ):
            if int(label) == 1:
                weight = 1.0
            else:
                positives = counts.get((protein_name, 1), 0)
                negatives = counts.get((protein_name, 0), 0)
                weight = positives / negatives if negatives else 0.0
            weights[self.id2pos[int(pair_id)]] = weight

        return weights / weights.mean().clamp_min(1e-8)

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
            self.csvtrain["pair_id"].astype(int),
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

        Under lipid_random_choice the warmed entry is the row's candidate key list, not
        an encoding, so warming performs no draw and leaves the random stream where it
        was. (It used to skip lipid warming here precisely because the draw sat inside
        the cache; it no longer does.) The isomer-graph path still draws inside
        make_graph_lipid, so that one stays skipped.

        Returns the entry count of each cache, for reporting.
        """
        frame = self.csv if csv is None else csv
        for prot_file in frame["LTPProtein"].dropna().unique().tolist():
            self.protein_graph_parts(prot_file)
        isomer_graphs = getattr(self.config, "lipid_graph_isomers", False)
        if not (isomer_graphs and self.config.lipid_random_choice):
            seen = set()
            for _, row in frame.iterrows():
                key = (str(row["SmileGlobal"]), str(row["SmileFragment"]))
                if key in seen:
                    continue
                seen.add(key)
                if isomer_graphs:
                    self.make_graph_lipid(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
                else:
                    self.warm_lipid_encoding(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
        return {
            "proteins": len(self._protein_graph_cache),
            # Exactly one of the two is used per run, so their sum is "lipid rows
            # warmed" in either mode.
            "lipid_encodings": (
                len(self._lipid_encoding_cache)
                + len(self._lipid_candidate_key_cache)
            ),
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

    def _weight_positions(self, pair_ids):
        """Each row's slot in the sample-weight vector, or -1 when it has none.

        id2pos maps a pair id to its rank among the sorted train pair ids -- both of the
        branches that build it in __init__ do exactly that -- so the lookup is a binary
        search over its sorted keys rather than a dict walk. That replaces a Python loop
        over every row of the split; the integers it produces are the same ones
        ``id2pos.get(pair_id, -1)`` produced.

        Validation and test rows are not in id2pos at all -- weights exist for train rows
        only -- and they keep the -1 the dict lookup gave them. Note -1 indexes the LAST
        weight rather than raising, which is safe only because the loss reads these
        positions in the training loop alone.
        """
        known = np.sort(np.fromiter(self.id2pos, dtype=np.int64, count=len(self.id2pos)))
        if known.size == 0:
            return np.full(len(pair_ids), -1, dtype=np.int64)
        # searchsorted gives the insertion point, which for an absent id is the slot of
        # some other id -- so every hit has to be confirmed by comparing back.
        positions = np.searchsorted(known, pair_ids)
        inside = positions < known.size
        found = np.zeros(len(pair_ids), dtype=bool)
        found[inside] = known[positions[inside]] == np.asarray(pair_ids)[inside]
        return np.where(found, positions, -1)

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
        orig_indexes = self.csv["pair_id"].to_numpy()
        # The sample cache's key, per row of this split (see get()).
        self._pair_id_by_idx = orig_indexes
        # Only the GRAB loss reads a sample's original row id: it keys the pair-graph
        # coefficients by it (batch_pair_ids in new_train.py). ProteinGraphData.__inc__
        # exempts it from PyG's node-index shifting, which is handling of the field, not a
        # second use of it -- nothing else in the project touches it. Without --grab_loss
        # it is therefore built, sliced per sample and concatenated per batch for nobody.
        self._pair_id_tensor = (
            torch.tensor(orig_indexes, dtype=torch.long).view(-1, 1)
            if self.config.grab_loss
            else None
        )
        self._tanimoto_pos_tensor = torch.as_tensor(
            self._weight_positions(orig_indexes), dtype=torch.long
        ).view(-1, 1)
        self._protein_id_tensor = (
            torch.tensor(
                [
                    self.protein_name_to_id[protein]
                    for protein in self._protein_by_idx
                ],
                dtype=torch.long,
            ).view(-1, 1)
            if getattr(self, "_needs_protein_id", True)
            else None
        )
        # Only a column when --chem_prior and/or --pocket_compat_prior added it
        # (_compute_frozen_prior); everything else costs nothing when both are off.
        self._frozen_prior_tensor = (
            torch.tensor(self.csv["_frozen_prior"].to_numpy(dtype="float32")).view(-1, 1)
            if "_frozen_prior" in self.csv.columns
            else None
        )
        # Only a column under --compatibility_input (_compute_compatibility_input).
        self._compat_input_tensor = (
            torch.tensor(self.csv["_compat_input"].to_numpy(dtype="float32")).view(-1, 1)
            if "_compat_input" in self.csv.columns
            else None
        )

    def __iter__(self):
        train_dataset = copy.copy(self)
        valid_dataset = copy.copy(self)
        test_dataset = copy.copy(self)
        train_dataset.csv = self.csvtrain
        valid_dataset.csv = self.csvalidate
        test_dataset.csv = self.csvtest
        # protein_id exists so run_test() can split the test metrics by protein. Only the
        # test split is ever asked for that, yet the field used to ride along in every
        # training and validation batch too -- one more tensor to slice per sample and one
        # more torch.cat per collation, for 150 epochs, read by no one. Marked per clone
        # here, before the fields are materialized, so the other two never build it.
        # Residue subsampling trains on a different random subset of each protein every
        # epoch, so it belongs to the training split alone: on validation it would turn
        # the metric into a draw, and the epoch-to-epoch wobble would be indistinguishable
        # from learning. The sample cache goes with it, for the reason spelled out where
        # lipid_random_choice disables it -- a cached sample freezes the draw, and one
        # frozen subset per row is not an augmentation but a smaller fixed fingerprint.
        # The per-protein and per-lipid caches stay, so what is paid per access is tensor
        # indexing, not a file parse.
        train_dataset._augment_residues = bool(
            getattr(self.config, "protein_residue_subsample", 0)
        )
        if train_dataset._augment_residues:
            train_dataset._sample_cache_enabled = False
        # --rank_within_protein is the one training-time consumer: the ranking loss can
        # only form same-protein pairs if it knows which rows share a protein. Everything
        # else keeps paying nothing, which is why this is a flag and not a default.
        train_dataset._needs_protein_id = bool(
            getattr(self.config, "rank_within_protein", False)
        )
        # Validation carries it only under save_dynamics, whose between-protein variance
        # needs to know which rows share a protein. Off by default, so the ordinary run
        # keeps paying nothing for it.
        valid_dataset._needs_protein_id = bool(
            getattr(self.config, "save_dynamics", False)
            # Under --rank_within_protein the validation loss has to be the SAME
            # quantity the training loss minimises, or the two curves are not
            # comparable and "valid loss stopped falling" stops meaning anything.
            or getattr(self.config, "rank_within_protein", False)
        )
        test_dataset._needs_protein_id = True
        train_dataset._prepare_indexed_fields()
        valid_dataset._prepare_indexed_fields()
        test_dataset._prepare_indexed_fields()
        train_dataset.pair_graph = train_dataset.build_current_pair_graph() if self.config.grab_loss else None
        valid_dataset.pair_graph = None
        test_dataset.pair_graph = None
        return iter((train_dataset, valid_dataset, test_dataset))

    def set_epoch(self, epoch):
        """Rotate the residue subsample. Called once per epoch by the training loop.

        The draw is seeded from (run seed, pair_id, epoch) rather than taken from the
        global generator, so a mask depends on nothing but those three: not on how many
        other random numbers have been drawn before it, not on batch order, not on the
        worker count. Two runs of the same configuration therefore see the same masks
        even if num_workers differs, which is the property every comparison in this
        project rests on.
        """
        self._augmentation_epoch = int(epoch)

    def _subsample_residues(self, parts, pair_id):
        """Keep a fixed number of randomly chosen residues, redrawn every epoch."""
        count = int(getattr(self.config, "protein_residue_subsample", 0) or 0)
        if count <= 0 or not self._augment_residues:
            return parts
        total = int(parts["x"].shape[0])
        # Fewer residues than asked for: keep them all. The protein's size stays visible
        # in that case, which is the one thing this is meant to hide -- see the flag's
        # note in ModelConfig on choosing a count every protein can supply.
        if total <= count:
            return parts
        seed = ((int(self.config.seed) * 1_000_003 + int(pair_id)) * 1_000_003
                + int(self._augmentation_epoch)) % (2 ** 63 - 1)
        generator = torch.Generator().manual_seed(seed)
        keep = torch.zeros(total, dtype=torch.bool)
        keep[torch.randperm(total, generator=generator)[:count]] = True
        return restrict_parts_to_mask(parts, keep)

    def get(self, idx):
        # Assembling a sample is a pure function of its row: the same protein graph, the
        # same lipid encoding, the same label, every epoch. It was nevertheless rebuilt
        # once per epoch -- 150 times per run for each row -- so the cache below keeps the
        # first result and the other 149 accesses become a dict lookup.
        #
        # Keyed by pair_id, never by idx. idx is the position inside THIS split, and the
        # three splits share these dicts (copy.copy in __iter__ is shallow, deliberately,
        # so the protein and lipid caches are filled once rather than three times). Train
        # row 0, validation row 0 and test row 0 are three different rows of data, so an
        # idx-keyed cache would serve one split's sample to another -- silently, with no
        # error and no crash, just wrong numbers. pair_id is the row's position in the
        # interaction table and is unique across all three.
        pair_id = int(self._pair_id_by_idx[idx])
        cached = self._sample_cache.get(pair_id)
        if cached is not None:
            return cached

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
        parts = self._subsample_residues(parts, pair_id)

        protein_graph = self.assemble_protein_graph(
            parts, self._interaction_tensor[idx], tenfam
        )
        sample = self.finish_sample(
            idx,
            protein_graph,
            lipid_enc,
            lipid_batch,
            smile_global,
            smile_fragment,
        )
        if self._sample_cache_enabled:
            self._sample_cache[pair_id] = sample
        return sample


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
        # Both are None when this run has no reader for them (see
        # _prepare_indexed_fields). Skipping the attachment is what removes their
        # torch.cat from every collation; nothing that produces a number reads either.
        if self._pair_id_tensor is not None:
            protein_graph.pair_id = self._pair_id_tensor[idx]
        protein_graph.tanimoto_pos = self._tanimoto_pos_tensor[idx]
        if self._protein_id_tensor is not None:
            protein_graph.protein_id = self._protein_id_tensor[idx]
        if self._frozen_prior_tensor is not None:
            protein_graph.frozen_prior = self._frozen_prior_tensor[idx]
        if self._compat_input_tensor is not None:
            protein_graph.compat_input = self._compat_input_tensor[idx]
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
            # No liplab here any more either. It was the 34-wide lipid-class one-hot, but
            # on this path it was never the sample's class: it was a fixed
            # labelOH["PC"] handed to every lipid alike. Nothing in the project read it --
            # the only readers of a lipid label are in the isomer path, which builds its
            # own from the real class -- so it was a constant vector concatenated into
            # every batch for 150 epochs and then dropped. Removing it takes one
            # torch.cat out of every collation and cannot change a computed number,
            # because no computation ever saw it.
            lipid_kwargs = {
                "x": lipid_enc,
            }
            if self.config.lipid_fragments_mask:
                lipid_kwargs["lipid_batch"] = lipid_batch
            lipid_graph = Data(**lipid_kwargs)

        return protein_graph , lipid_graph
