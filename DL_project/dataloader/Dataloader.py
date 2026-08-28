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
from dataloader.pocket_lipid_compatibility import (
    chain_lengths_by_row,
    coarsen_to_levels,
    compat_input_parts,
    pocket_extent_by_protein,
    pocket_rim_core_aromatic_share_by_protein,
    raw_compatibility,
    raw_compatibility_parts,
)
from dataloader.pair_descriptors import (
    as_arrays,
    chain_length_angstrom,
    descriptor_values_by_row,
    resolve_requested_tokens,
)
from dataloader.pair_descriptor_cache import load_pair_descriptor_cache
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
    protein_node_columns,
    restrict_parts_to_mask,
)
from dataloader.protein_graph_tensor_cache import load_protein_graph_tensor_cache
from dataloader.lipid_graph_tensor_cache import load_lipid_graph_tensor_cache
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
def candidate_column(values):
    """Per-candidate values as one DataFrame column, one tuple per row.

    The prior and the compatibility input depend on which candidate structure a sample
    is encoded as, so they are per row AND per candidate, and a row has as many of them
    as it has candidates -- from one to thirty-seven. Carrying them as a tuple per row
    keeps them attached to the row through everything that reshapes the table (the
    split, the negative sampling, the per-candidate expansion of an evaluation split)
    and keeps each row exactly its own length, with nothing padded and nothing to mask.
    """
    return [tuple(float(value) for value in row) for row in values]


def _ragged_tensor(columns):
    """One flat tensor plus row offsets for a column (or columns) of per-row tuples.

    (None, None) when the column is absent, which is the ordinary run: neither the
    frozen prior nor the compatibility input exists unless its flag asked for it.
    """
    if columns is None:
        return None, None
    if not isinstance(columns, list):
        columns = [columns]
    rows = [np.asarray(row, dtype="float32") for row in columns[0].to_numpy()]
    lengths = [len(row) for row in rows]
    stacked = np.stack(
        [np.concatenate([np.asarray(row, dtype="float32") for row in column.to_numpy()])
         for column in columns],
        axis=-1,
    )
    offsets = np.zeros(len(rows) + 1, dtype=np.int64)
    np.cumsum(lengths, out=offsets[1:])
    return torch.from_numpy(stacked), torch.from_numpy(offsets)


def _candidate_position(offsets, idx, candidate_index):
    """Where this row's chosen candidate sits in the flat tensor.

    Clamped to the row's own candidate count, the same clamp the encoding side applies,
    so a row asked for a candidate it does not have reads its last one.
    """
    start = int(offsets[idx])
    count = int(offsets[idx + 1]) - start
    return start + min(candidate_index or 0, count - 1)


def ragged_rows(values, rows):
    """The per-row arrays at the given positions of the original table."""
    return [values[int(row)] for row in rows]


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
        self._protein_tensor_cache = load_protein_graph_tensor_cache(
            self.ROOT_DIR, protein_node_columns(config)
        )
        # Same idea for --lipid_graph_isomers' per-graph_id tensors (dataloader/
        # lipid_graph_tensor_cache.py, built by data/build_lipid_graph_tensor_cache.py):
        # {} when no cache has been built or data/lipid_graphs/ changed since, which
        # LipidIsomerGraphBuilder._one_lipid_graph_parts falls back on exactly as
        # before this cache existed.
        self._lipid_graph_tensor_cache = load_lipid_graph_tensor_cache(self.ROOT_DIR)
        self._lipid_encoding_cache = {}
        # lipid_random_choice fills this one instead: the drawn encoding must not be
        # cached (that would freeze the draw for the whole run), only the canonical
        # keys it draws from. See LipidGraphBuilder._drawn_lipid_encoding.
        self._lipid_candidate_key_cache = {}
        self._lipid_graph_cache = {}
        self._complete_edge_index_cache = {}
        # Assembled samples, keyed by pair_id -- see get(). Only sound while a row's
        # sample is a pure function of the row, which it stops being on whichever split
        # draws a lipid candidate per access: a cached sample would freeze that draw for
        # the whole run, degenerating the mode into "one arbitrary fixed candidate per
        # row" -- precisely what it exists to replace. Enabled here, switched off in
        # __iter__ for the drawing split alone.
        self._sample_cache = {}
        self._sample_cache_enabled = True
        # The lipid draw and residue subsampling are both per split and set from outside
        # -- the split in __iter__, the epoch by the training loop through set_epoch.
        # Neither belongs on validation or test: a metric computed on a different draw
        # every epoch is not the same quantity twice, and the epoch-to-epoch wobble it
        # adds is indistinguishable from learning, while checkpoint selection and early
        # stopping read exactly that metric.
        self._draw_lipid_candidate = False
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
        self._compute_pair_descriptors(csv)
        if getattr(self.config, "lipid_propensity_weight", False):
            self._lipid_propensity_weights = self._compute_lipid_propensity_weights(csv)
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
        self.hard_negative_mining = bool(getattr(config, "hard_negative_mining", False))
        self.hard_negative_share = float(
            getattr(config, "hard_negative_share", 0.5) or 0.5
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

    @staticmethod
    def _original_rows(frame):
        """A split frame's positions in the ORIGINAL interaction table.

        pair_id, not the frame's index: __init__ re-indexes the sampled pool 0..N-1, so
        index labels stop being original positions the moment negatives are sampled.
        """
        if frame.empty:
            return np.array([], dtype=int)
        return frame["pair_id"].to_numpy(dtype=int)

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
        # Rows of `csv` are addressed by pair_id, never by a split frame's index: the
        # sampled pool is re-indexed 0..N-1 in __init__, so a frame's index labels are
        # positions in the POOL and using them here would read the wrong rows of the
        # original table -- pool row 969 against original row 969, which are different
        # (protein, lipid) pairs. pair_id is the original position and is what survives
        # sampling, splitting and the per-candidate expansion.
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
        if getattr(self.config, "compatibility_split_input", False):
            # The two halves unmixed, so _compute_compatibility_input can build a
            # NON-additive pair term out of them. raw_compatibility's difference cannot
            # carry one: its two-way interaction is identically zero
            # (files/compat_input_audit.md 1). Reads Interaction nowhere, same as the
            # difference does not.
            chain, extent, missing = raw_compatibility_parts(
                csv, self.ROOT_DIR, getattr(self.config, "lipid_isomers", False)
            )
            train_rows = self._original_rows(self.csvtrain)
            missing_count = sum(int(row.sum()) for row in missing)
            if missing_count:
                train_values = np.concatenate(ragged_rows(chain, train_rows))
                train_usable = train_values[~np.isnan(train_values)]
                fill = float(train_usable.mean()) if len(train_usable) else 0.0
                print(
                    f"pocket-lipid compatibility : {missing_count} of "
                    f"{sum(len(row) for row in chain)} candidates "
                    f"had no parseable chain length, filled with the train mean ({fill:.2f})"
                )
                chain = [np.where(np.isnan(row), fill, row) for row in chain]
            columns["compat_parts"] = tuple(
                (ragged_rows(chain, rows), extent[rows]) if len(rows) else ([], np.array([], dtype=float))
                for rows in (
                    self._original_rows(self.csvtrain),
                    self._original_rows(self.csvalidate),
                    self._original_rows(self.csvtest),
                )
            )
        if getattr(self.config, "pocket_compat_prior", False) or getattr(self.config, "compatibility_input", False):
            # raw_compatibility reads Interaction nowhere, so unlike s_chem there is no
            # leave-one-out to do: a training row's own label cannot leak into a
            # quantity built from pocket geometry and lipid structure alone.
            all_values, missing = raw_compatibility(
                csv, self.ROOT_DIR, getattr(self.config, "lipid_isomers", False)
            )
            train_rows = self._original_rows(self.csvtrain)
            missing_count = sum(int(row.sum()) for row in missing)
            if missing_count:
                train_values = np.concatenate(ragged_rows(all_values, train_rows))
                train_usable = train_values[~np.isnan(train_values)]
                # 0.0 only if EVERY train candidate is unparseable, which would mean the
                # term carries no information for this run at all; the print makes
                # that degenerate case visible rather than a silent constant.
                fill = float(train_usable.mean()) if len(train_usable) else 0.0
                print(
                    f"pocket-lipid compatibility : {missing_count} of "
                    f"{sum(len(row) for row in all_values)} candidates "
                    f"had no parseable chain length, filled with the train mean ({fill:.2f})"
                )
                all_values = [
                    np.where(np.isnan(row), fill, row) for row in all_values
                ]
            columns["compat"] = tuple(
                ragged_rows(all_values, rows) if len(rows) else []
                for rows in (
                    self._original_rows(self.csvtrain),
                    self._original_rows(self.csvalidate),
                    self._original_rows(self.csvtest),
                )
            )
        return columns

    def _compute_lipid_propensity_weights(self, csv):
        """Per-train-row loss weight, |label - s_chem|, class-normalized to mean 1.

        s_chem is the same leave-one-out, similarity-weighted k-NN score
        --chem_prior uses (null_scores_leave_one_row_out, dataloader/
        chemistry_prior.py) -- not a second measurement of it. Downweights rows a
        pure lipid-chemistry baseline already predicts correctly (label agrees
        with s_chem), upweights rows where the label disagrees with what the
        lipid alone predicts -- concentrates the loss on rows that need
        protein-specific signal, not the lipid's own marginal propensity to bind
        SOMETHING (--lipid_propensity_weight).

        `csv` must be the ORIGINAL, unsampled interaction table: species_similarity
        indexes rows by their position in it (Tanimoto_compact_isomeric_row_ids.npy),
        which self.csvtrain no longer matches once negative sampling has
        re-indexed it -- same requirement as _raw_frozen_prior_columns, which is
        why this is called from __init__ with __init__'s own `csv` local rather
        than from get_lipid_propensity_weights after the fact.

        Normalized separately within each class (mean 1.0 for positives, mean 1.0
        for negatives) so this reweights WITHIN each class only and leaves the
        positive:negative balance --balanced_batches/--balanced_proteins already
        set at the sampling level untouched -- a within-class emphasis shift, not
        a second class-balancing mechanism.
        """
        similarity, index = species_similarity(csv, self.ROOT_DIR)
        s_chem = null_scores_leave_one_row_out(
            self.csvtrain, similarity, index, self.config.chem_neighbours
        )
        labels = self.csvtrain["Interaction"].to_numpy(dtype=float)
        raw_weight = np.abs(labels - s_chem)
        for class_label in (0.0, 1.0):
            mask = labels == class_label
            if mask.any():
                class_mean = raw_weight[mask].mean()
                if class_mean > 1e-9:
                    raw_weight[mask] = raw_weight[mask] / class_mean
        weights = torch.zeros(len(self.id2pos), dtype=torch.float32)
        for pair_id, weight in zip(self.csvtrain["pair_id"].astype(int), raw_weight):
            weights[self.id2pos[int(pair_id)]] = float(weight)
        return weights

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
        # One entry per candidate of every row: compatibility depends on which candidate
        # structure the sample is encoded as, s_chem does not and is repeated over that
        # row's candidates. The calibration is fit on all of them with the row's label
        # repeated -- those are the values the model will actually be handed, and fitting
        # on one arbitrary candidate would tune the weights to a structure most samples
        # never see.
        def candidate_lengths(split_index):
            for name in wanted:
                values = raw_columns[name][split_index]
                if isinstance(values, list):
                    return [len(row) for row in values]
            return [1] * len(raw_columns[wanted[0]][split_index])

        def flatten(name, split_index, lengths):
            values = raw_columns[name][split_index]
            if isinstance(values, list):
                return np.concatenate(values) if values else np.array([], dtype=float)
            return np.repeat(np.asarray(values, dtype=float), lengths)

        train_lengths = candidate_lengths(0)
        design_train = np.column_stack([
            flatten(name, 0, train_lengths) for name in wanted
        ])
        means, spreads, intercept, weights = fit_prior_calibration(
            design_train,
            np.repeat(self.csvtrain["Interaction"].to_numpy(), train_lengths),
        )
        print(
            "frozen prior calibration : intercept {:.3f}, weights {} (covariates: {}, "
            "fit on {} train rows)".format(
                intercept, {n: round(float(w), 3) for n, w in zip(wanted, weights)},
                wanted, len(design_train),
            )
        )

        def combine(split_index):
            lengths = candidate_lengths(split_index)
            design = np.column_stack([
                flatten(name, split_index, lengths) for name in wanted
            ])
            combined = intercept + ((design - means) / spreads) @ weights
            return np.split(combined, np.cumsum(lengths)[:-1])

        self.csvtrain = self.csvtrain.assign(
            _frozen_prior=candidate_column(combine(0))
        )
        for split_index, name in ((1, "csvalidate"), (2, "csvtest")):
            frame = getattr(self, name)
            value = (
                candidate_column(combine(split_index)) if not frame.empty else []
            )
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
        if getattr(self.config, "compatibility_split_input", False):
            self._compute_compatibility_split_input(raw_columns)
            return
        if not getattr(self.config, "compatibility_input", False):
            return
        train_raw, valid_raw, test_raw = raw_columns["compat"]
        # Over every candidate of every train row: that is the distribution the
        # standardised input is drawn from once a sample can be encoded as any of its
        # candidates.
        train_values = np.concatenate(train_raw) if train_raw else np.array([0.0])
        mean, spread = train_values.mean(), train_values.std()
        spread = spread if spread > 1e-12 else 1.0
        self.csvtrain = self.csvtrain.assign(
            _compat_input=candidate_column(
                [(row - mean) / spread for row in train_raw]
            )
        )
        for raw, name in ((valid_raw, "csvalidate"), (test_raw, "csvtest")):
            frame = getattr(self, name)
            value = (
                candidate_column([(row - mean) / spread for row in raw])
                if not frame.empty else []
            )
            setattr(self, name, frame.assign(_compat_input=value))

    def _compute_compatibility_split_input(self, raw_columns):
        """Two inputs instead of one difference -- the marginal and the pair term apart.

        What the single difference conflates, measured in files/compat_input_audit.md:

          * its whole ranking value inside a protein IS the chain length -- `chain_only`
            and `difference` score 0.579 there, identically, in every family. That half
            is a lipid-only rule, and a lipid-only rule is the thing the doubly-cold
            split exists to make the model beat, not something it may quietly ride.
          * it carries eta^2 0.78 against protein identity, through `pocket_extent` at
            full resolution -- the same fold-label channel that got pocket descriptors
            rejected, entering through a feature advertised as immune to it.
          * and it is additive, so its own pair content is exactly zero.

        So: `-chain_length`, standardised, as an input the run can name, report against
        and adversarially remove; and `relu(chain - extent)` on a COARSENED extent as
        the pair term -- non-additive (interaction share 0.23 against the difference's
        0.00) and the only candidate form whose family eta^2, 0.21, falls below the band
        that rejected the descriptors. Both are oriented so larger means "more likely to
        bind", matching the direction the AUCs were measured in.

        `--compat_input_parts` feeds either half alone, which is what makes the two
        claims separately testable: `chain` alone is the marginal with the protein
        removed entirely, `clash` alone is the pair term with the marginal removed.
        With both columns present a model free to lean on either one answers neither
        question, so the three arms are how the result gets attributed to a half.

        Every train-only decision lives here together: the fill for an unparseable
        chain, the quantile cuts for the coarsening, and the standardisation. A held-out
        protein therefore cannot influence the band it lands in.
        """
        (train_chain, train_extent), (valid_chain, valid_extent), (test_chain, test_extent) = \
            raw_columns["compat_parts"]

        parts = compat_input_parts(self.config)
        bins = max(int(getattr(self.config, "compat_extent_bins", 4) or 0), 1)
        if bins > 1 and len(train_extent):
            edges = np.quantile(train_extent, np.linspace(0, 1, bins + 1))
            edges[0], edges[-1] = -np.inf, np.inf
            # Ties collapse bands; keeping only distinct cuts means `bins` is an upper
            # bound on the levels, not a promise, and the print says which happened.
            edges = np.unique(edges)
            levels = len(edges) - 1
        else:
            edges, levels = None, 1
        print(
            f"compatibility split input : {' + '.join(parts)} "
            f"(pocket extent rounded to {levels} level(s))"
        )

        def raw_parts(chain, extent):
            if not len(chain):
                return {name: [] for name in parts}
            coarse = coarsen_to_levels(extent, edges) if edges is not None else extent
            # chain is one array per row and the pocket half is one value per row: the
            # cavity does not change with which isomer is being considered, the tail
            # that has to fit in it does.
            both = {
                "chain": [-row for row in chain],
                "clash": [
                    -np.maximum(row - float(coarse[position]), 0.0)
                    for position, row in enumerate(chain)
                ],
            }
            return {name: both[name] for name in parts}

        # Standardisation constants from TRAIN, same discipline as everywhere else a
        # train-only statistic feeds a split it was not computed from.
        stats = {}
        for name, values in raw_parts(train_chain, train_extent).items():
            real = np.concatenate(values) if values else np.array([], dtype=float)
            spread = real.std() if len(real) else 0.0
            stats[name] = (
                real.mean() if len(real) else 0.0,
                spread if spread > 1e-12 else 1.0,
            )

        def columns(chain, extent):
            return {
                f"_compat_input_{name}": candidate_column(
                    [(row - stats[name][0]) / stats[name][1] for row in values]
                )
                for name, values in raw_parts(chain, extent).items()
            }

        self.csvtrain = self.csvtrain.assign(**columns(train_chain, train_extent))
        for (chain, extent), name in (
            ((valid_chain, valid_extent), "csvalidate"),
            ((test_chain, test_extent), "csvtest"),
        ):
            frame = getattr(self, name)
            assigned = (
                {f"_compat_input_{part}": [] for part in parts}
                if frame.empty else columns(chain, extent)
            )
            setattr(self, name, frame.assign(**assigned))

    def _compute_pair_descriptors(self, csv):
        """Attach --pair_descriptors' 6 standardised columns (5 under
        --no_pair_descriptor_extent, 8 under --pair_descriptor_pocket_shares_split).

        Fed to architecture/pair_descriptor_head.py's self-attention token set, one
        token each: chain length, unsaturation count and H-bond capacity (lipid-only),
        coarsened pocket extent (protein-only -- coarsened the same way
        --compatibility_split_input's "clash" coarsens it, on TRAIN-only quantile
        edges, so a held-out protein's raw cavity size cannot identify it the way full-
        resolution pocket_extent does, eta^2 0.78 against protein identity per
        files/compat_input_audit.md), and occupancy = relu(cbrt(heavy_atom_count) -
        coarse_extent), the one genuine pair term here -- a cheap, docking-free stand-in
        for the paper's bound-ligand/cavity volume ratio (see
        dataloader/pair_descriptors.py for why 3D volume itself is not attempted). Two
        more protein-only tokens (aromatic_share, polar_share) are read directly off the
        pocket descriptor tensor at forward time instead of duplicated here --
        --pair_descriptors requires --pocket_descriptors (ModelConfig.validate) and
        that tensor already carries them.

        --pair_descriptor_pocket_shares_split swaps that pair for aromatic_share_core/
        aromatic_share_rim (computed here, per protein, same as extent -- no split of
        aromatic_share exists in the pocket descriptor tensor to read at forward time
        the way extent's replacement, hydropathy_core/hydropathy_rim, does) plus
        hydropathy_core/hydropathy_rim (read at forward time, already in that tensor).
        See architecture/pair_descriptor_head.py and project memory
        [[descriptors-path-fingerprint-leak]].

        --no_pair_descriptor_extent drops the standalone extent token (the highest
        family-identity signal of the three protein-only entries, eta^2 0.78 at full
        resolution). occupancy keeps reading coarse_extent regardless -- it is a pair
        term (heavy_atom_count vs extent), not a duplicate of the extent token, so
        dropping the token does not remove the quantity from the model, only its
        standalone exposure to self-attention.

        Standardised on TRAIN candidates only, same discipline as
        _compute_compatibility_input; missing (RDKit-unparseable) values are filled
        with the train mean, same as _raw_frozen_prior_columns.

        --two_pair_descriptors_paths (training/read_configuration.py, architecture/
        named_descriptor_head.py) additionally attaches `_descpath_<token>` for every
        token dataloader.pair_descriptors.resolve_requested_tokens resolves out of
        --good_descriptors/--bad_descriptors -- NOT the full DESCRIPTOR_CATALOG
        unconditionally, only whatever those two flags actually name, bare (e.g.
        "pocket_extent") or coarsened (e.g. "hydropathy_core_coarse=quantiles:5" --
        see dataloader.pair_descriptors.parse_descriptor_token for the full <name>_
        coarse=<spec> grammar: N fixed equal-width bins, or N train-fit quantile
        bins, generalising the "extent" token's own train-fit-quantile coarsening
        below -- coarsen_to_levels -- to any base name and any bin count). Every
        base name is its RAW pocket_descriptor()/dataloader.pair_descriptors value
        unless a request coarsens it -- --good_descriptors/--bad_descriptors decide
        per name which of raw or coarse (and how coarse) an experiment reads; see
        ModelConfig.two_pair_descriptors_paths for the leak-safety reasoning. Pair-
        formula names are computed with dataloader.pair_descriptors.
        pair_descriptor_value, the identical function analysis/null_model.py's
        chemistry null model uses, so a name means the same number in both places.
        Independent of --pair_descriptors (ModelConfig.validate rejects combining
        the two -- they build different Final_Layer branches), so this runs the
        shared lipid/extent computation below even when --pair_descriptors itself
        is off.
        """
        pair_descriptors_on = getattr(self.config, "pair_descriptors", False)
        two_paths_on = getattr(self.config, "two_pair_descriptors_paths", False)
        if not (pair_descriptors_on or two_paths_on):
            return

        # --descriptor_names (ModelConfig docstring): --descriptors_head's own single-
        # head equivalent of --good_descriptors/--bad_descriptors -- only meaningful
        # when descriptors_head is actually on (validate() rejects it otherwise), and
        # shares the SAME arbitrary-name catalog materialisation two_paths_on triggers
        # below, just off one raw string instead of two.
        descriptor_names = (
            getattr(self.config, "descriptor_names", "")
            if getattr(self.config, "descriptors_head", False) else ""
        )
        named_catalog_on = two_paths_on or bool(descriptor_names.strip())

        isomeric = getattr(self.config, "lipid_isomers", False)
        # None (no current cache -- never built, or the interaction table/data/graphs
        # changed since it was) falls every lookup below back to computing directly,
        # exactly as before this cache existed. See dataloader/pair_descriptor_cache.py
        # and data/build_pair_descriptor_cache.py, which scripts/run_local.sh runs once
        # before a grid launches so its N (group, seed) processes share one build.
        pair_cache = load_pair_descriptor_cache(self.ROOT_DIR, isomeric)
        protein_cache = pair_cache["proteins"] if pair_cache else None
        chain = as_arrays(chain_lengths_by_row(csv, isomeric, cache=pair_cache))
        unsaturation = as_arrays(
            descriptor_values_by_row(csv, "unsaturation", isomeric, cache=pair_cache)
        )
        hbond = as_arrays(descriptor_values_by_row(csv, "hbond", isomeric, cache=pair_cache))
        heavy = as_arrays(
            descriptor_values_by_row(csv, "heavy_atoms", isomeric, cache=pair_cache)
        )
        lipid_shape_on = getattr(self.config, "pair_descriptor_lipid_shape", False)
        lipid_shape = {}
        if lipid_shape_on:
            from dataloader.pair_descriptors import LIPID_SHAPE_DESCRIPTOR_NAMES
            for name in LIPID_SHAPE_DESCRIPTOR_NAMES:
                lipid_shape[name] = as_arrays(
                    descriptor_values_by_row(csv, name, isomeric, cache=pair_cache)
                )
        extents = pocket_extent_by_protein(
            self.ROOT_DIR, self.protein_names, cache=protein_cache
        )
        extent = csv["LTPProtein"].map(extents).to_numpy(dtype=float)

        # --no_pair_descriptor_extent drops only the standalone extent TOKEN below;
        # coarse_extent (right after) still feeds occupancy either way, since occupancy
        # is a pair term (heavy_atom_count vs extent) regardless of whether extent is
        # also exposed on its own. two_paths_on always wants "extent" available (its
        # own catalog has no separate on/off flag for one name -- --good_descriptors/
        # --bad_descriptors simply do or don't name it).
        include_extent = (
            pair_descriptors_on and getattr(self.config, "pair_descriptor_extent", True)
        ) or two_paths_on

        split_pocket_shares = pair_descriptors_on and getattr(
            self.config, "pair_descriptor_pocket_shares_split", False
        ) and getattr(self.config, "pair_descriptor_pocket_shares", True)
        if split_pocket_shares:
            rim_core = pocket_rim_core_aromatic_share_by_protein(
                self.ROOT_DIR, self.protein_names, cache=protein_cache
            )
            core_by_protein = {protein: value[0] for protein, value in rim_core.items()}
            rim_by_protein = {protein: value[1] for protein, value in rim_core.items()}
            aromatic_share_core = csv["LTPProtein"].map(core_by_protein).to_numpy(dtype=float)
            aromatic_share_rim = csv["LTPProtein"].map(rim_by_protein).to_numpy(dtype=float)

        train_rows = self._original_rows(self.csvtrain)

        def fill_train_mean(values, label):
            missing = sum(int(np.isnan(row).sum()) for row in values)
            if not missing:
                return values
            train_values = (
                np.concatenate(ragged_rows(values, train_rows))
                if len(train_rows) else np.array([], dtype=float)
            )
            usable = train_values[~np.isnan(train_values)]
            fill = float(usable.mean()) if len(usable) else 0.0
            print(
                f"pair descriptors : {missing} of {sum(len(row) for row in values)} "
                f"{label} candidates unparseable, filled with the train mean ({fill:.2f})"
            )
            return [np.where(np.isnan(row), fill, row) for row in values]

        chain = fill_train_mean(chain, "chain-length")
        unsaturation = fill_train_mean(unsaturation, "unsaturation")
        hbond = fill_train_mean(hbond, "H-bond-capacity")
        heavy = fill_train_mean(heavy, "heavy-atom")
        if lipid_shape_on:
            lipid_shape = {
                name: fill_train_mean(values, name)
                for name, values in lipid_shape.items()
            }

        bins = max(int(getattr(self.config, "compat_extent_bins", 4) or 0), 1)
        edges = None
        if len(train_rows) and bins > 1:
            train_extent = extent[train_rows]
            edges = np.quantile(train_extent, np.linspace(0, 1, bins + 1))
            edges[0], edges[-1] = -np.inf, np.inf
            edges = np.unique(edges)
        coarse_extent = coarsen_to_levels(extent, edges) if edges is not None else extent
        # chain_length_angstrom(chain), not cbrt(heavy_atom_count): the latter is a
        # UNITLESS ~2.6-4.6 number on this project's data, next to coarse_extent's
        # ~13.6-32.0 angstrom range -- coarse_extent always won, and relu clipped
        # occupancy to exactly 0.0 on every row (verified directly), a dead token in
        # every --pair_descriptors run to date. chain_length_angstrom converts the
        # chain's own carbon count to an estimated angstrom length (Tanford's
        # extended-chain formula, see dataloader/pair_descriptors.py) so both sides
        # of the comparison are the same unit. Same fix as dataloader/pair_
        # descriptors.py's pair_descriptor_value("occupancy") -- kept in sync there.
        occupancy = [
            np.maximum(chain_length_angstrom(chain_row) - coarse_extent[position], 0.0)
            for position, chain_row in enumerate(chain)
        ]

        raw = {
            "chain": chain, "unsaturation": unsaturation, "hbond": hbond,
            "heavy": heavy, "occupancy": occupancy,
        }
        # Appended after occupancy, before "extent" (added below by `columns()`) --
        # architecture/pair_descriptor_head.py's base_tokens builds the identical order.
        raw.update(lipid_shape)
        stats = {}
        for name, values in raw.items():
            train_values = (
                np.concatenate(ragged_rows(values, train_rows))
                if len(train_rows) else np.array([0.0])
            )
            spread = train_values.std() if len(train_values) else 1.0
            stats[name] = (
                train_values.mean() if len(train_values) else 0.0,
                spread if spread > 1e-12 else 1.0,
            )
        extent_train = coarse_extent[train_rows] if len(train_rows) else np.array([0.0])
        extent_mean = extent_train.mean() if len(extent_train) else 0.0
        extent_spread = extent_train.std() if len(extent_train) else 1.0
        extent_spread = extent_spread if extent_spread > 1e-12 else 1.0

        def train_stats(values):
            train_values = values[train_rows] if len(train_rows) else np.array([0.0])
            mean = train_values.mean() if len(train_values) else 0.0
            spread = train_values.std() if len(train_values) else 1.0
            return mean, (spread if spread > 1e-12 else 1.0)

        if split_pocket_shares:
            aromatic_share_core_mean, aromatic_share_core_spread = train_stats(
                aromatic_share_core
            )
            aromatic_share_rim_mean, aromatic_share_rim_spread = train_stats(
                aromatic_share_rim
            )

        # --two_pair_descriptors_paths: resolve exactly the tokens --good_descriptors/
        # --bad_descriptors actually request (bare base names AND <name>_coarse=<spec>
        # ones -- dataloader.pair_descriptors.resolve_requested_tokens/
        # parse_descriptor_token), build raw values only for the BASE names those
        # tokens reference (not the full catalog unconditionally), then materialise
        # -- coarsen if requested, then standardise train-only, same discipline as
        # everywhere else in this function -- exactly those tokens.
        requested_tokens = ()
        raw_values = {}  # base_name -> (values, is_ragged)
        materialised = {}  # canonical token -> (values, is_ragged, mean, spread)
        if named_catalog_on:
            from dataloader.chemistry_prior import protein_descriptor_table
            from dataloader.pair_descriptors import (
                BOUNDED_SHARE_DESCRIPTOR_NAMES,
                PAIR_DESCRIPTOR_NAMES as _CATALOG_PAIR_NAMES,
                PROTEIN_DESCRIPTOR_NAMES as _CATALOG_PROTEIN_NAMES,
                pair_descriptor_value,
                parse_descriptor_token,
                resolve_requested_tokens,
            )

            requested_tokens = resolve_requested_tokens(
                getattr(self.config, "good_descriptors", ""),
                getattr(self.config, "bad_descriptors", ""),
                descriptor_names,
            )
            base_names_needed = {
                parse_descriptor_token(token)[0] for token in requested_tokens
            }

            raw_values["chain"] = (chain, True)
            raw_values["unsaturation"] = (unsaturation, True)
            raw_values["hbond"] = (hbond, True)
            raw_values["heavy"] = (heavy, True)
            raw_values["extent"] = (coarse_extent, False)

            protein_names_needed = base_names_needed & (
                set(_CATALOG_PROTEIN_NAMES) | {"polar_share"}
            )
            pair_names_needed = base_names_needed & set(_CATALOG_PAIR_NAMES)
            # tail_count is needed whenever it is named directly OR a pair formula
            # reads it (tail_elongation_fit) -- pair_descriptor_value's lipid dict
            # below must carry it unconditionally in that second case even though
            # nobody asked for the bare "tail_count" token itself.
            if "tail_count" in base_names_needed or pair_names_needed:
                tail_count = fill_train_mean(
                    as_arrays(
                        descriptor_values_by_row(
                            csv, "tail_count", isomeric, cache=pair_cache
                        )
                    ),
                    "tail-count",
                )
                raw_values["tail_count"] = (tail_count, True)

            if protein_names_needed or pair_names_needed:
                protein_raw = protein_descriptor_table(self.ROOT_DIR)
                protein_column = csv["LTPProtein"].to_numpy()
                for name in protein_names_needed:
                    raw_values[name] = (
                        np.array(
                            [protein_raw[protein][name] for protein in protein_column],
                            dtype=float,
                        ),
                        False,
                    )
                for name in pair_names_needed:
                    values = [
                        np.array(
                            [
                                pair_descriptor_value(
                                    name,
                                    {
                                        "chain": chain_row[candidate],
                                        "unsaturation": unsaturation[row_position][candidate],
                                        "hbond": hbond[row_position][candidate],
                                        "heavy": heavy[row_position][candidate],
                                        "tail_count": tail_count[row_position][candidate],
                                    },
                                    protein_raw[protein_column[row_position]],
                                )
                                for candidate in range(len(chain_row))
                            ],
                            dtype=float,
                        )
                        for row_position, chain_row in enumerate(chain)
                    ]
                    raw_values[name] = (values, True)

            def train_flat(values, ragged):
                if not len(train_rows):
                    return np.array([0.0])
                return (
                    np.concatenate(ragged_rows(values, train_rows)) if ragged
                    else values[train_rows]
                )

            def fit_coarse_edges(values, ragged, spec, bounded):
                flat = train_flat(values, ragged)
                if spec.mode == "fixed":
                    if bounded:
                        lo, hi = 0.0, 1.0
                    elif len(flat):
                        lo, hi = float(flat.min()), float(flat.max())
                    else:
                        lo, hi = 0.0, 1.0
                    if hi <= lo:
                        # Degenerate train spread (e.g. a constant column) -- mirrors
                        # the spread-floor every stats dict in this function already
                        # applies, so a single-value column still gets a well-defined,
                        # if uninformative, set of edges instead of a numpy error.
                        hi = lo + 1.0
                    edges = np.linspace(lo, hi, spec.bins + 1)
                else:
                    edges = (
                        np.quantile(flat, np.linspace(0, 1, spec.bins + 1)) if len(flat)
                        else np.linspace(0.0, 1.0, spec.bins + 1)
                    )
                edges = edges.astype(float)
                edges[0], edges[-1] = -np.inf, np.inf
                # Ties collapse bands, same as _compute_compatibility_input's own
                # edges -- compat_extent_bins is an upper bound on levels, not a
                # promise, for the identical reason.
                return np.unique(edges)

            for token in requested_tokens:
                name, spec = parse_descriptor_token(token)
                values, ragged = raw_values[name]
                if spec is not None:
                    edges = fit_coarse_edges(
                        values, ragged, spec, name in BOUNDED_SHARE_DESCRIPTOR_NAMES
                    )
                    values = (
                        [coarsen_to_levels(row, edges) for row in values] if ragged
                        else coarsen_to_levels(values, edges)
                    )
                flat = train_flat(values, ragged)
                mean = flat.mean() if len(flat) else 0.0
                spread = flat.std() if len(flat) else 1.0
                materialised[token] = (
                    values, ragged, mean, spread if spread > 1e-12 else 1.0
                )

        def columns(rows):
            names = list(raw) + (["extent"] if include_extent else []) + (
                ["aromatic_share_core", "aromatic_share_rim"] if split_pocket_shares else []
            )
            if not len(rows):
                out = {f"_pair_desc_{name}": [] for name in names}
                if named_catalog_on:
                    out.update({f"_descpath_{token}": [] for token in requested_tokens})
                return out
            out = {}
            for name, values in raw.items():
                mean, spread = stats[name]
                out[f"_pair_desc_{name}"] = candidate_column(
                    [(row - mean) / spread for row in ragged_rows(values, rows)]
                )
            # Extent, and (under the split) aromatic_share_core/rim, are one value per
            # ROW (protein-level), repeated over that row's candidates -- chain gives
            # the candidate count, not the value.
            counts = [len(row) for row in ragged_rows(chain, rows)]
            if include_extent:
                out["_pair_desc_extent"] = candidate_column([
                    np.full(count, (coarse_extent[row] - extent_mean) / extent_spread)
                    for count, row in zip(counts, rows)
                ])
            if split_pocket_shares:
                out["_pair_desc_aromatic_share_core"] = candidate_column([
                    np.full(
                        count,
                        (aromatic_share_core[row] - aromatic_share_core_mean)
                        / aromatic_share_core_spread,
                    )
                    for count, row in zip(counts, rows)
                ])
                out["_pair_desc_aromatic_share_rim"] = candidate_column([
                    np.full(
                        count,
                        (aromatic_share_rim[row] - aromatic_share_rim_mean)
                        / aromatic_share_rim_spread,
                    )
                    for count, row in zip(counts, rows)
                ])
            if named_catalog_on:
                for token in requested_tokens:
                    values, ragged, mean, spread = materialised[token]
                    if ragged:
                        out[f"_descpath_{token}"] = candidate_column(
                            [(row - mean) / spread for row in ragged_rows(values, rows)]
                        )
                    else:
                        out[f"_descpath_{token}"] = candidate_column([
                            np.full(count, (values[row] - mean) / spread)
                            for count, row in zip(counts, rows)
                        ])
            return out

        self.csvtrain = self.csvtrain.assign(**columns(train_rows))
        for name in ("csvalidate", "csvtest"):
            frame = getattr(self, name)
            rows = self._original_rows(frame) if not frame.empty else np.array([], dtype=int)
            setattr(self, name, frame.assign(**columns(rows)))

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

        # --hard_negative_mining: built once per dataset (not per group) since it is
        # the same Tanimoto matrix every group's weighting reads. Only the samplers
        # that go through _sample_group_balanced_negatives accept it; validate()
        # already requires one of them to be active whenever the flag is set.
        hard_negative_pool = None
        if self.hard_negative_mining:
            hard_negative_pool = species_similarity(csv, self.ROOT_DIR)

        if self.balanced_lipid_classes:
            csvtrue, csvfalse = split_and_sample_lipid_class_balanced_interactions(
                csv, seed, ratio=self.negatives_per_positive
            )
        elif self.balanced_proteins:
            csvtrue, csvfalse = split_and_sample_protein_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata,
                hard_negative_pool, self.excluded_groups, self.hard_negative_share,
            )
        elif self.balance_negatives_by_family:
            csvtrue, csvfalse = split_and_sample_family_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata,
                hard_negative_pool, self.excluded_groups, self.hard_negative_share,
            )
        else:
            csvtrue, csvfalse = split_and_sample_interactions(csv, seed)
        # Not under the two-axis split. This redraws the excluded group's negatives to
        # 1:1 over its whole domain, blind to `strata`, so the negatives it adds land in
        # held-out and retained classes alike and only the first kind survives into the
        # block. Measured on the seven families it both shrank the block (lipocalin 216
        # rows to 138-145) and made its size depend on the seed, which the per-(protein,
        # class-side) match above is precisely what removes. With that match in place the
        # ratio is already exact, so there is nothing for this to repair.
        if (
            self.excluded_groups
            and self.balance_excluded_group_negatives
            and not self.excluded_lipid_classes
        ):
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
        # to train either, since their protein is held out. Dropping costs 1.1-5.1% of
        # the working set at share 0.80 and two negatives per positive (scp2 1.1%, LBP
        # 1.3%, IP_trans 1.8%, GLTP and lipocalin 2.4%, START 3.3%, CRAL-TRIO 5.1%) and
        # nothing from train, which never contained them.
        # The block is also restricted to the held-out proteins. A row of another
        # protein in a removed class is cold on the lipid axis only -- its own family
        # sits in train, and the model has seen that family bind and not bind -- so
        # scoring it answers the one-axis question, not this one. Left in, it dominated:
        # the held-out family held 20-44% of its own block (98% for GLTP, whose classes
        # no other protein binds), so five of the seven per-family numbers were majority
        # other-protein. Those rows cannot go to train either, since their class is what
        # the second axis removes, so they are dropped like the ones above. What remains
        # is the intersection the split is named for: neither the protein nor the lipid
        # chemistry anywhere in train.
        if self.double_coldsplit and self.excluded_lipid_classes:
            excluded_classes = lipid_class_series(excluded_data).str.lower()
            in_cold_chemistry = excluded_classes.isin(self.excluded_lipid_classes)
            if self.excluded_groups:
                held_out_protein = (
                    excluded_data["ProteinDomain"].str.lower().isin(self.excluded_groups)
                )
            elif self.excluded_subgroups:
                held_out_protein = excluded_data["LTPProtein"].isin(
                    self.excluded_subgroups
                )
            else:
                held_out_protein = pandas.Series(True, index=excluded_data.index)
            excluded_data = excluded_data[in_cold_chemistry & held_out_protein]
        if self.test_group:
            domain_lower = excluded_data["ProteinDomain"].str.lower()
            csvtest = excluded_data[domain_lower == self.test_group].sample(frac=1)
            csvalidate = excluded_data[domain_lower != self.test_group].sample(frac=1)
        else:
            # Halve the two labels separately rather than the block as a whole. An
            # undivided draw fixes only the total, so the positives fall where the seed
            # puts them: on the two-axis blocks, which run from 108 to 328 rows, that
            # put 23 of scp2's 36 positives in test and 13 in valid, and the two halves
            # then measure different quantities. Splitting each label in half makes
            # valid and test carry the same positive rate by construction, which is what
            # lets a threshold picked on one be read on the other.
            positive_pool = excluded_data[excluded_data["Interaction"] == 1]
            negative_pool = excluded_data[excluded_data["Interaction"] == 0]
            positive_validate = positive_pool.sample(frac=0.5, random_state=seed)
            negative_validate = negative_pool.sample(frac=0.5, random_state=seed)
            csvalidate = pandas.concat(
                [positive_validate, negative_validate]
            ).sample(frac=1, random_state=seed)
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

    def get_lipid_propensity_weights(self):
        """The --lipid_propensity_weight tensor computed in __init__, or zeros.

        Computed there (not here) because it needs the ORIGINAL, unsampled
        interaction table for species_similarity's row-position indexing, which
        __init__ still has as a local and this method does not (self.csv is
        reassigned to self.csvtrain by the time __init__ returns, same reason
        _raw_frozen_prior_columns takes csv as an argument rather than reading
        self.csv). The zeros fallback matches get_protein_weights' contract of
        always returning a same-shaped tensor, for a caller that toggled the
        flag off mid-run without rebuilding the dataset.
        """
        return getattr(
            self, "_lipid_propensity_weights",
            torch.zeros(len(self.id2pos), dtype=torch.float32),
        )

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

        On the drawing split the warmed entries are the row's candidate key list and the
        fixed encoding the other two splits read, so warming performs no draw and leaves
        the random stream where it was. (It used to skip lipid warming here precisely
        because the draw sat inside the cache; it no longer does.) The isomer-graph path
        still draws inside make_graph_lipid, so that one stays skipped.

        Returns the entry count of each cache, for reporting.
        """
        frame = self.csv if csv is None else csv
        for prot_file in frame["LTPProtein"].dropna().unique().tolist():
            self.protein_graph_parts(prot_file)
        isomer_graphs = getattr(self.config, "lipid_graph_isomers", False)
        if not (isomer_graphs and self._draw_lipid_candidate):
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

        # Unlike the protein cache, the isomer-graph drawing split (lipid_graph_isomers
        # + lipid_random_choice) never gets a chance to warm every combination it will
        # need up front -- warm_caches() explicitly skips it (see its docstring) because
        # the draw happens inside make_graph_lipid on every access. Releasing the raw
        # per-graph_id tensor cache there would force every later draw back onto reading
        # CSVs directly; every other config warms every SMILES it needs during
        # warm_caches(), so this source cache is safe to drop once initialization ends.
        can_release_lipid_tensor_cache = not (
            getattr(self.config, "lipid_graph_isomers", False)
            and self._draw_lipid_candidate
        )
        if can_release_lipid_tensor_cache and getattr(self, "_lipid_graph_tensor_cache", None):
            self._lipid_graph_tensor_cache = {}
            released.append("lipid_graph_tensor_cache")

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
        # Present only on an expanded evaluation split (_expand_candidate_rows). The
        # group tensor is the pair id repeated over the row's candidates, which is what
        # the averaging in new_train groups by.
        self._candidate_index_by_idx = (
            self.csv["_candidate_index"].to_numpy(copy=False)
            if "_candidate_index" in self.csv.columns
            else None
        )
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
        # Which samples of a batch are the same pair seen through different candidates.
        # Only built on an expanded split, where it is what the averaging groups by.
        self._candidate_group_tensor = (
            torch.tensor(orig_indexes, dtype=torch.long).view(-1, 1)
            if self._candidate_index_by_idx is not None
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
        # Flat values plus row offsets rather than a rectangle: rows have between one
        # and thirty-seven candidates, and get() reads the entry of the candidate the
        # sample is encoded as, clamped to the row's own count.
        self._frozen_prior_tensor, self._frozen_prior_offsets = _ragged_tensor(
            self.csv["_frozen_prior"] if "_frozen_prior" in self.csv.columns else None
        )
        # Only columns under --compatibility_input / --compatibility_split_input
        # (_compute_compatibility_input). One column for the difference, two for the
        # split form; the width the model sizes itself for comes from the same
        # compat_input_width(config), so the two cannot disagree about it.
        compat_columns = [
            name for name in
            ("_compat_input", "_compat_input_chain", "_compat_input_clash")
            if name in self.csv.columns
        ]
        # Stored one row per sample, (N, 1, width): indexing gives (1, width), which
        # collates to (batch, width) under the default concatenation. A flat (N, width)
        # store would index to (width,) and collate to (batch*width,), which happens to
        # reshape correctly today and would stop doing so the moment anything about the
        # collation changed -- the shape is made explicit rather than relied upon.
        # The same flat form, one column per part: indexing a candidate gives (width,),
        # which get() views as (1, width) -- the shape a sample carried before the
        # candidate axis existed, so the collation and the model are unchanged.
        self._compat_input_tensor, self._compat_input_offsets = _ragged_tensor(
            [self.csv[name] for name in compat_columns] if compat_columns else None
        )
        # Only columns under --pair_descriptors (_compute_pair_descriptors): the 6
        # standardised tokens, in a fixed order architecture/pair_descriptor_head.py
        # relies on (chain, unsaturation, hbond, heavy, occupancy, extent) -- 5 under
        # --no_pair_descriptor_extent, which _compute_pair_descriptors never creates
        # the extent column for -- plus, under --pair_descriptor_lipid_shape,
        # LIPID_SHAPE_DESCRIPTOR_NAMES (dataloader/pair_descriptors.py) inserted between
        # occupancy and extent, plus, under --pair_descriptor_pocket_shares_split,
        # aromatic_share_core and aromatic_share_rim, in the same fixed order
        # PairDescriptorHead.DATALOADER_TOKENS + SPLIT_DATALOADER_TOKENS relies on.
        pair_descriptor_names = ["chain", "unsaturation", "hbond", "heavy", "occupancy"]
        if getattr(self.config, "pair_descriptor_lipid_shape", False):
            from dataloader.pair_descriptors import LIPID_SHAPE_DESCRIPTOR_NAMES
            pair_descriptor_names += list(LIPID_SHAPE_DESCRIPTOR_NAMES)
        if getattr(self.config, "pair_descriptor_extent", True):
            pair_descriptor_names.append("extent")
        if getattr(
            self.config, "pair_descriptor_pocket_shares_split", False
        ) and getattr(self.config, "pair_descriptor_pocket_shares", True):
            pair_descriptor_names += ["aromatic_share_core", "aromatic_share_rim"]
        pair_descriptor_columns = [
            f"_pair_desc_{name}" for name in pair_descriptor_names
            if f"_pair_desc_{name}" in self.csv.columns
        ]
        self._pair_descriptor_tensor, self._pair_descriptor_offsets = _ragged_tensor(
            [self.csv[name] for name in pair_descriptor_columns]
            if pair_descriptor_columns else None
        )
        # --two_pair_descriptors_paths: the wider, arbitrary-name catalog, one column
        # per token dataloader.pair_descriptors.resolve_requested_tokens resolves out
        # of --good_descriptors/--bad_descriptors, in THAT (sorted, deduped) order --
        # architecture/named_descriptor_head.py's NamedDescriptorHead instances call
        # the SAME function against the SAME config fields to compute the identical
        # order independently, so both heads index into this ONE tensor correctly
        # regardless of how their name lists overlap. --descriptors_head's own
        # --descriptor_names builds the identical tensor off one field instead of two
        # (ModelConfig.descriptor_names docstring) -- validate() guarantees at most one
        # of the two triples (good/bad, descriptor_names) is ever non-empty, so passing
        # all three here always resolves to exactly the active branch's own tokens.
        descriptor_names = (
            getattr(self.config, "descriptor_names", "")
            if getattr(self.config, "descriptors_head", False) else ""
        )
        named_catalog_on = (
            getattr(self.config, "two_pair_descriptors_paths", False)
            or bool(descriptor_names.strip())
        )
        requested_tokens = resolve_requested_tokens(
            getattr(self.config, "good_descriptors", ""),
            getattr(self.config, "bad_descriptors", ""),
            descriptor_names,
        ) if named_catalog_on else ()
        descriptor_catalog_columns = [
            f"_descpath_{token}" for token in requested_tokens
            if f"_descpath_{token}" in self.csv.columns
        ]
        self._descriptor_catalog_tensor, self._descriptor_catalog_offsets = _ragged_tensor(
            [self.csv[name] for name in descriptor_catalog_columns]
            if descriptor_catalog_columns else None
        )

    def _expand_candidate_rows(self, frame):
        """One row per candidate structure, so evaluation can average over the set.

        A measured species is a set of candidate isomers, and under random_choice
        training is taught to answer the same thing for all of them. Reading the model
        back on one arbitrary member throws that away, so an evaluation split is
        expanded here: the row is repeated once per candidate, each copy carries the
        index it must encode, and new_train averages the predictions back per pair
        before the threshold. Rows with a single candidate are untouched, which is most
        of the table's negatives.
        """
        cap = int(getattr(self.config, "eval_candidates_per_pair", 0) or 0)
        chosen = [
            self._candidate_indices_to_score(
                len(
                    self.candidate_keys_for_row(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
                ),
                cap,
            )
            for _, row in frame.iterrows()
        ]
        expanded = frame.loc[
            frame.index.repeat([len(indices) for indices in chosen])
        ].copy()
        expanded["_candidate_index"] = [
            index for indices in chosen for index in indices
        ]
        return expanded

    @staticmethod
    def _candidate_indices_to_score(count, cap):
        """Which candidates of a row the averaged evaluation scores.

        Everything up to the cap, and evenly spread over the list beyond it -- the ends
        included -- rather than the first few: a completed candidate list carries the
        row's own annotation first and the isomers collected from other rows after it,
        so a prefix would sample one annotation rather than the species. 0 or a cap the
        row does not reach means every candidate, and the indices are the row's own, so
        the encoding side needs no translation.
        """
        if cap <= 0 or count <= cap:
            return list(range(count))
        if cap == 1:
            return [0]
        step = (count - 1) / (cap - 1)
        return sorted({int(round(position * step)) for position in range(cap)})

    def __iter__(self):
        train_dataset = copy.copy(self)
        valid_dataset = copy.copy(self)
        test_dataset = copy.copy(self)
        train_dataset.csv = self.csvtrain
        valid_dataset.csv = self.csvalidate
        test_dataset.csv = self.csvtest
        if getattr(self.config, "eval_average_candidates", False):
            valid_dataset.csv = self._expand_candidate_rows(valid_dataset.csv)
            test_dataset.csv = self._expand_candidate_rows(test_dataset.csv)
        # protein_id exists so run_test() can split the test metrics by protein. Only the
        # test split is ever asked for that, yet the field used to ride along in every
        # training and validation batch too -- one more tensor to slice per sample and one
        # more torch.cat per collation, for 150 epochs, read by no one. Marked per clone
        # here, before the fields are materialized, so the other two never build it.
        # Residue subsampling trains on a different random subset of each protein every
        # epoch, so it belongs to the training split alone: on validation it would turn
        # the metric into a draw, and the epoch-to-epoch wobble would be indistinguishable
        # from learning. The sample cache goes with it -- a cached sample freezes the
        # draw, and one frozen subset per row is not an augmentation but a smaller fixed
        # fingerprint. The per-protein and per-lipid caches stay, so what is paid per
        # access is tensor indexing, not a file parse.
        #
        # lipid_random_choice is the same kind of augmentation on the other partner: a
        # row lists several candidate structures for one measured species and the draw
        # picks one of them per access. It is marked here for the same reason -- on
        # validation and test the drawn molecule would change every epoch, so the metric
        # that selects the checkpoint and stops training early would move for a reason
        # unrelated to the model. Those two splits take the first candidate instead,
        # which is what the deterministic treatments encode as well, so their rows stay
        # comparable across epochs and across runs.
        train_dataset._draw_lipid_candidate = bool(self.config.lipid_random_choice)
        train_dataset._augment_residues = bool(
            getattr(self.config, "protein_residue_subsample", 0)
        )
        if train_dataset._augment_residues or train_dataset._draw_lipid_candidate:
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
        # On an expanded split the pair id alone no longer identifies a sample: the same
        # pair appears once per candidate, and keying by it would serve one candidate's
        # sample for all of them.
        candidate_index = (
            None
            if self._candidate_index_by_idx is None
            else int(self._candidate_index_by_idx[idx])
        )
        protein = self._protein_by_idx[idx]
        smile_global = self._smile_global_by_idx[idx]
        smile_fragment = self._smile_fragment_by_idx[idx]
        if candidate_index is None and self._draw_lipid_candidate:
            # Drawn here rather than inside the encoder, so the frozen prior and the
            # compatibility input can be read for the same candidate the encoding is
            # built from instead of for whichever one the list happens to start with.
            candidate_index = self.draw_candidate_index(smile_global, smile_fragment)
        cache_key = pair_id if candidate_index is None else (pair_id, candidate_index)
        cached = self._sample_cache.get(cache_key)
        if cached is not None:
            return cached

        if getattr(self.config, "lipid_graph_isomers", False) or getattr(
            self.config, "no_embeddings", False
        ):
            # no_embeddings: MolFormer is not used at all -- finish_sample builds the
            # lipid graph's single node from pair_descriptor_input instead (see
            # there). Skipped here too, not just unused later, so the embedding
            # cache is never even looked up for this run.
            lipid_enc = None
            lipid_batch = None
        elif self.config.lipid_fragments_mask:
            lipid_enc, lipid_batch = self.cached_lipid_encoding(
                smile_global, smile_fragment
            )
        else:
            lipid_enc = self.cached_lipid_encoding(
                smile_global, smile_fragment, candidate_index=candidate_index
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
            candidate_index,
        )
        if self._sample_cache_enabled:
            self._sample_cache[cache_key] = sample
        return sample


    def finish_sample(
        self,
        idx,
        protein_graph,
        lipid_enc,
        lipid_batch,
        smile_global,
        smile_fragment,
        candidate_index=None,
    ):
        """Attach the per-row identifiers and build the lipid side of one sample."""
        #print(f"pocket shape : {pok.shape}")
        #print(pok)
        # Both are None when this run has no reader for them (see
        # _prepare_indexed_fields). Skipping the attachment is what removes their
        # torch.cat from every collation; nothing that produces a number reads either.
        if self._pair_id_tensor is not None:
            protein_graph.pair_id = self._pair_id_tensor[idx]
        if self._candidate_group_tensor is not None:
            protein_graph.candidate_group = self._candidate_group_tensor[idx]
        protein_graph.tanimoto_pos = self._tanimoto_pos_tensor[idx]
        if self._protein_id_tensor is not None:
            protein_graph.protein_id = self._protein_id_tensor[idx]
        # Both carry a candidate axis: the term describes the structure the sample is
        # encoded as, so it moves with the draw and with the candidate index of an
        # expanded evaluation row. Clamped the same way the encoding side clamps, so a
        # row asked for a candidate it does not have reads its last one.
        if self._frozen_prior_tensor is not None:
            position = _candidate_position(
                self._frozen_prior_offsets, idx, candidate_index
            )
            protein_graph.frozen_prior = self._frozen_prior_tensor[position].view(1)
        if self._compat_input_tensor is not None:
            position = _candidate_position(
                self._compat_input_offsets, idx, candidate_index
            )
            protein_graph.compat_input = self._compat_input_tensor[position].view(1, -1)
        if self._pair_descriptor_tensor is not None:
            position = _candidate_position(
                self._pair_descriptor_offsets, idx, candidate_index
            )
            protein_graph.pair_descriptor_input = (
                self._pair_descriptor_tensor[position].view(1, -1)
            )
        if self._descriptor_catalog_tensor is not None:
            position = _candidate_position(
                self._descriptor_catalog_offsets, idx, candidate_index
            )
            protein_graph.descriptor_catalog_input = (
                self._descriptor_catalog_tensor[position].view(1, -1)
            )
        if getattr(self.config, "lipid_graph_isomers", False):
            lipid_graph = self.make_graph_lipid(
                smile_global, smile_fragment
            )
        elif getattr(self.config, "no_embeddings", False):
            # No MolFormer, and without it no per-token structure to build multiple
            # nodes from (validate() requires descriptors_in_protein_lipid for
            # exactly this reason) -- one node, whose feature vector is the same
            # chain/unsaturation/hbond/heavy columns architecture/lipid_encoder.py
            # broadcasts onto every node when embeddings ARE on. Sliced from
            # protein_graph.pair_descriptor_input (attached above) rather than
            # recomputed -- same tensor, same fixed DATALOADER_TOKENS column order
            # (architecture/pair_descriptor_head.py), one read instead of two.
            if not hasattr(protein_graph, "pair_descriptor_input"):
                raise ValueError(
                    "no_embeddings requires pair_descriptors (pair_descriptor_input "
                    "was not attached -- check --pocket_descriptors/--pair_descriptors "
                    "are set, per ModelConfig.validate)"
                )
            lipid_graph = Data(x=protein_graph.pair_descriptor_input[:, :4].clone())
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
