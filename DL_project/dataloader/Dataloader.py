"""PLIDataset: builds the train/valid/test split once, then serves samples from it.

Construction (__init__ and its helpers): load and filter the interaction csv, sample
negatives, split into train/valid/test, compute descriptor/weight columns, warm the
protein/lipid caches. Runs once per training run.

Per-sample serving (__iter__, get(), sample_for_candidate(), finish_sample(), below the
construction methods): everything called on every batch, every epoch, reading only what
__init__ already built. dataloader/preassembled_loader.py depends on that half alone --
it replays sample_for_candidate()'s draw-then-assemble logic, never anything from
construction.

Under --eval_average_candidates, _expand_candidate_rows here is the input-side half of
one feature; training/candidate_averaging.py is the output-side half, collapsing the
per-candidate predictions this produces back into one per pair after the forward pass.

PLIDataset also composes FrozenPriorBuilder (frozen_prior.py), LipidGraphBuilder /
LipidIsomerGraphBuilder (graphs_builders/), and ProteinGraphBuilder (graphs_builders/)
"""

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
    knn_scores_leave_one_row_out,
    species_similarity,
)
from dataloader.pocket_lipid_compatibility import (
    chain_lengths_by_row,
    coarsen_to_levels,
    pocket_extent_by_protein,
)
from dataloader.descriptors import (
    descriptor_catalog_only,
    full_catalog_order,
    parse_descriptor_list,
)
from dataloader.similarity_pool import (
    resolve_similarity_pool,
    pool_report,
)
from preprocessing.compute_descriptors import (
    as_arrays,
    descriptor_values_by_row,
    protein_descriptor_table,
)
from dataloader.descriptor_cache_reader import load_lipid_descriptor_cache
from dataloader.descriptor_missing_values import (
    LIPID_LEVEL_MEASURES,
    require_no_missing,
    share_value_within_lipid,
)
from dataloader.tensors_reading.lipid_embedding_tensors_reader import load_lipid_embedding_store
from dataloader.graphs_builders.lipid_graph_builder import LipidGraphBuilder
from dataloader.graphs_builders.lipid_isomer_graph_builder import (
    LipidGraphData,
    LipidIsomerGraphBuilder,
)
from dataloader.graphs_builders.protein_graph_builder import (
    ProteinGraphBuilder,
    ProteinGraphData,
    protein_node_columns,
    restrict_parts_to_mask,
)
from dataloader.tensors_reading.protein_graph_tensors_reader import load_protein_graph_tensor_cache
from dataloader.protein_tokens import (
    build_protein_token_table,
    parse_protein_token_alphabets,
)
from dataloader.tensors_reading.lipid_graph_tensors_reader import load_lipid_graph_tensor_cache
from dataloader.tensors_reading.tanimoto_compact_tensors_reader import load_compact
from dataloader.splitting_on_blocks.lipid_isolation_blocks import (
    BLOCK_GEOMETRY,
    LIPID_ISOLATION_BLOCKS,
)
from dataloader.splitting_on_blocks.lipid_subclass_blocks import (
    BLOCK_TANIMOTO,
    subclass_block_species,
)
from dataloader.splitting_on_blocks.lipid_species_blocks import species_coldsplit_block
from dataloader.splitting_on_blocks.lipid_coldsplit_blocks import (
    COLDSPLIT_MINIMUM_TEST_POSITIVES,
    LIPID_COLDSPLIT_SETS,
    lipid_classes_for_holdout,
)
from dataloader.sampler import (
    class_level_positive_labels,
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
from dataloader.ragged_tensors import candidate_column, _candidate_position, _ragged_tensor, ragged_rows
from dataloader.frozen_prior import FrozenPriorBuilder

# Quantile levels the "extent" token rounds the pocket extent to (cut on TRAIN proteins only).
EXTENT_BINS = 4


class PLIDataset(
    FrozenPriorBuilder,
    LipidGraphBuilder,
    LipidIsomerGraphBuilder,
    ProteinGraphBuilder,
    Dataset,
):
    ##################################################################################
    #                                   CONSTRUCTION
    ##################################################################################
    # Runs once per training run: load/filter the csv, sample and split, warm caches.
    def __init__(self, root_dir, csv:pandas.DataFrame, seed, excluded_subgroups, config, excluded_groups=None) -> None:
        super().__init__(root=None, transform=None, pre_transform=None, pre_filter=None)

        self.ROOT_DIR = root_dir
        self.config = config
        self.seed = seed
        # --family_only: keep one family's rows before sampling and splitting.
        if config.family_only:
            csv = csv[
                csv["ProteinDomain"].str.lower() == config.family_only.lower()
            ]
            # pair_id is read off .index while the descriptor arrays are positional
            # (.to_numpy()), so index label must equal row position after any filter.
            csv = csv.reset_index(drop=True)
        # --rotate_train_negatives needs the negatives the sampler did NOT draw; the
        # reference is dropped by _add_rotating_negatives once used.
        self._rotation_source = (
            csv if config.rotate_train_negatives else None
        )
        self.excluded_groups = {group.lower() for group in excluded_groups or []}
        self.excluded_subgroups = set(excluded_subgroups)
        self.protein_names = sorted(csv["LTPProtein"].dropna().unique().tolist())
        self.protein_name_to_id = {name: idx for idx, name in enumerate(self.protein_names)}
        self.protein_id_to_name = {idx: name for name, idx in self.protein_name_to_id.items()}

        self._configure_sampling(config)
        self._derive_lipid_class_holdout(csv)
        self.positive_pairs, self.unlabeled_pairs = self._sample_interactions(csv, seed)
        self.positive_pairs["pair_id"] = self.positive_pairs.index
        self.unlabeled_pairs["pair_id"] = self.unlabeled_pairs.index

        sampled_csv = pandas.concat([self.positive_pairs, self.unlabeled_pairs])
        self.sampled_split = sampled_csv.set_index(
            pandas.Index(list(range(len(sampled_csv))))
        )
        del self.positive_pairs, self.unlabeled_pairs, sampled_csv

        self.csvtrain, self.csvalidate, self.csvtest = self._split_interactions(seed)
        self.train_orig_indexes = torch.as_tensor(self.csvtrain["pair_id"].values, dtype=torch.long)

        # Диагностика обучающего пула, не гиперпараметр: доля его отрицательных строк,
        # стоящих в ячейке (белок, подкласс статьи), где у ТОГО ЖЕ белка уже есть
        # положительная строка. Такая пара отличается от известного связывания только
        # конкретным липидом внутри одного подкласса, то есть почти не отличается на
        # входе -- разделить её нечем, и отбор, который такие пары накапливает, портит
        # результат: по семи конфигурациям на --lipid_species_coldsplit=0.15 эта доля
        # коррелирует с test BA на -0.96 (0.110 -> 0.923 против 0.736 -> 0.769), а
        # обучающая ошибка растёт вчетверо. Считается по тому, что видит прогон: и
        # ячейки, и отрицательные берутся из csvtrain, поэтому отложенный блок в число
        # не подмешивается.
        self.suspect_negative_share = self._suspect_negative_share()

        # Only --tanimoto_weight reads Tanimoto similarities (compact artifacts). Every other
        # run builds id2pos by ranking the train row ids; the weights use it only as cell
        # addresses, so any bijection row-id -> 0..N-1 gives the same vector.
        self._needs_tanimoto_rows = bool(self.config.tanimoto_weight)

        self.train_tanimoto_batch = None
        self.train_tanimoto_matrix = None
        if self._needs_tanimoto_rows:
            train_idx = self.train_orig_indexes.numpy()
            # Isomeric artifacts for an isomeric run. --lipid_isomers --tanimoto_weight runs
            # used to get the non-isomeric similarities, so they are not comparable with
            # earlier ones.
            compact = load_compact(
                root_dir,
                source_csv=interaction_csv_path(root_dir),
                isomeric=bool(self.config.lipid_isomers),
            )
            if compact is None:
                raise FileNotFoundError(
                    "--tanimoto_weight needs current compact Tanimoto artifacts "
                    f"(Tanimoto_compact{'_isomeric' if self.config.lipid_isomers else ''}_* "
                    f"in {root_dir}/cache); they are missing or older than the interaction table. "
                    "Rebuild: python3 preprocessing/similarity/build_tanimoto_compact.py"
                    + (" --isomeric" if self.config.lipid_isomers else "")
                )
            selected = np.flatnonzero(np.isin(compact.row_ids, train_idx))
            self.train_tanimoto_batch = torch.from_numpy(
                np.array(compact.row_ids[selected], copy=True)
            )
            self.train_tanimoto_matrix = torch.from_numpy(
                compact.submatrix(selected)
            )
            gc.collect()

            unique_batch_ids = torch.unique(self.train_tanimoto_batch, sorted=True)
            self.id2pos = {int(g): int((unique_batch_ids == g).nonzero(as_tuple=True)[0]) for g in unique_batch_ids.tolist()}
        else:
            self.id2pos = {int(pair_id): position for position, pair_id in enumerate(sorted(set(self.train_orig_indexes.tolist())))}

        self._indices = None
        self.transform = None

        self.smiles_encoding = None
        # lipid_graph_isomers, --lipid_smiles_tokens and descriptor_catalog_only never read
        # the MoLFormer table, so it is not loaded for them.
        if (
            not self.config.lipid_graph_isomers
            and not self.config.lipid_smiles_tokens
            and not descriptor_catalog_only(self.config)
        ):
            # The non-isomeric table is the deterministic rebuild (every candidate of every
            # row, one fixed random-feature matrix); runs on lipid_SMILES_embedding.pkl are
            # not comparable with it. The isomeric table is still the old kind.
            lipid_embedding_file = (
                "lipid_SMILES_isomeric_embedding.pkl"
                if self.config.lipid_isomers
                else "lipid_SMILES_embedding_deterministic.pkl"
            )
            # Memory-mapped store if current (shared across jobs), else the pickle.
            self.smiles_encoding = load_lipid_embedding_store(
                self.ROOT_DIR, lipid_embedding_file
            )
            if self.smiles_encoding is None:
                with open(os.path.join(self.ROOT_DIR, lipid_embedding_file), "rb") as f:
                    self.smiles_encoding = pickle.load(f)
        self._load_lipid_graph_index()
        # Per-sample rebuild caches: each entry depends only on run-fixed inputs, so a cached
        # object equals a rebuilt one. The three splits (shallow copy.copy in __iter__)
        # share these dicts, and workers fork after warm_caches().
        self._protein_graph_cache = {}
        # --deepclip and descriptor_catalog_only build no protein graph, so the protein
        # tensors are not loaded for them.
        self._protein_tensor_cache = (
            {}
            if config.deepclip or descriptor_catalog_only(config)
            else load_protein_graph_tensor_cache(
                self.ROOT_DIR, protein_node_columns(config)
            )
        )
        # Family one-hot per LTPProtein for --deepclip (protein_family_one_hot).
        self._protein_family_cache = {}
        # --deepclip_protein_tokens: pocket token codes, padded to the longest protein.
        protein_token_alphabets = parse_protein_token_alphabets(
            config.deepclip_protein_tokens
        )
        self._protein_tokens, self._protein_token_counts = (
            build_protein_token_table(
                self.ROOT_DIR, self.protein_names, protein_token_alphabets
            )
            if protein_token_alphabets
            else ({}, {})
        )
        # Per-graph_id lipid tensors; {} if no current cache (the builder then reads CSVs).
        self._lipid_graph_tensor_cache = load_lipid_graph_tensor_cache(self.ROOT_DIR)
        self._lipid_encoding_cache = {}
        # lipid_random_choice caches only the canonical keys it draws from, never the draw
        # (see LipidGraphBuilder._drawn_lipid_encoding).
        self._lipid_candidate_key_cache = {}
        self._lipid_graph_cache = {}
        self._complete_edge_index_cache = {}
        # Assembled samples by pair_id (see get()); switched off in __iter__ for a split
        # that draws per access, since a cached sample would freeze the draw.
        self._sample_cache = {}
        self._sample_cache_enabled = True
        # Train-only augmentations, set per split in __iter__ (epoch via set_epoch):
        # validation and test must be the same quantity every epoch.
        self._draw_lipid_candidate = False
        self._augment_residues = False
        self._augmentation_epoch = 0
        # --lipid_class_targets: train split only, set in __iter__.
        self._use_lipid_class_targets = False
        print(f"train : {self.csvtrain.shape}")
        print(f"valid : {self.csvalidate.shape}")
        print(f"test : {self.csvtest.shape}")
        self._report_lipid_prior_baseline()
        raw_columns = self._raw_frozen_prior_columns(csv)
        self._compute_frozen_prior(raw_columns)
        self._compute_descriptors(csv)
        if self.config.lipid_propensity_weight:
            self._lipid_propensity_weights = self._compute_lipid_propensity_weights(csv)
        self.csv = self.csvtrain

    def _configure_sampling(self, config):
        self.balance_excluded_group_negatives = config.balance_excluded_group_negatives
        self.balance_negatives_by_family = config.balance_negatives_by_family
        self.balanced_proteins = config.balanced_proteins
        self.balanced_lipid_classes = config.balanced_lipid_classes
        # Negatives drawn per positive inside each balancing group (dataloader/sampler.py).
        self.negatives_per_positive = config.negatives_per_positive
        self.hard_negative_mining = config.hard_negative_mining
        self.hard_negative_share = config.hard_negative_share
        # Same draw steered toward DISTANT negatives; exclusive with
        # hard_negative_mining (validate refuses the pair).
        self.dissimilar_negative_mining = config.dissimilar_negative_mining
        self.dissimilar_negative_share = config.dissimilar_negative_share
        # Which similarity either direction steers by, and the descriptor names a
        # *_descriptors source is built from. See dataloader/similarity_pool.py.
        self.negative_similarity = config.negative_similarity
        self.negative_similarity_descriptors = config.negative_similarity_descriptors
        # Lipid axis of the cold split: head-group classes held out of training. The classes
        # are derived in _derive_lipid_class_holdout, which needs the full table.
        self.double_coldsplit = config.double_coldsplit
        self.mixed_coldsplit = config.mixed_coldsplit
        self.coldsplit_share = config.coldsplit_share
        # The lipid axis alone: a fixed named class set leaves training, every protein stays.
        self.lipid_coldsplit = config.lipid_coldsplit
        self.excluded_lipid_classes = set()
        # Same axis by species (they share excluded_lipid_species), see
        # dataloader/splitting_on_blocks/: a block at a requested Tanimoto isolation,
        self.lipid_isolation = config.lipid_isolation
        # the source paper's lipid subclass,
        self.lipid_subclass = config.lipid_subclass
        # or a seeded draw of structure-disjoint lipids carrying this share of positives.
        self.lipid_species_coldsplit = config.lipid_species_coldsplit
        self.excluded_lipid_species = set()
        # Drops evaluated rows whose (protein, subclass) cell is absent from train
        # (_covered_protein_subclass); never changes train.
        self.drop_uncovered_protein_subclass = config.drop_uncovered_protein_subclass
        self.test_group = config.test_group.lower()

    ##################################################################################
    #                              LIPID COLD-SPLIT AXIS
    ##################################################################################
    # Which chemistry (classes or species) leaves training, independent of protein axis.
    def _cold_chemistry(self, frame):
        """Which rows of `frame` carry the chemistry this run holds out of training
        (named by class or by species; one mask for every caller)."""
        held = pandas.Series(False, index=frame.index)
        if self.excluded_lipid_classes:
            held |= lipid_class_series(frame).str.lower().isin(self.excluded_lipid_classes)
        if self.excluded_lipid_species:
            held |= frame["FullIdentityOfLipid"].isin(self.excluded_lipid_species)
        return held

    @property
    def _has_cold_chemistry(self):
        return bool(self.excluded_lipid_classes or self.excluded_lipid_species)

    ##################################################################################
    #                     NO-MODEL BASELINE / COVERAGE DIAGNOSTICS
    ##################################################################################
    # What a per-lipid / per-class label prior alone scores, printed for reference.
    @staticmethod
    def _protein_subclass_key(frame):
        """(LTPProtein, article lipid subclass) of every row, as one string key.

        Must match analysis/baselines/protein_subclass_label_baseline.py exactly (same
        classification, "?unclassified" fallback and "|" join), so the network and the
        no-model baseline are scored on the same rows.
        """
        from dataloader.splitting_on_blocks.lipid_subclass_blocks import article_subclass_species

        subclass_of = {
            name: subclass
            for subclass, species in article_subclass_species().items()
            for name in species
        }
        subclass = frame["FullIdentityOfLipid"].map(subclass_of).fillna("?unclassified")
        return frame["LTPProtein"].astype(str) + "|" + subclass.astype(str)

    def _covered_protein_subclass(self, frame, csvtrain):
        """Which rows of `frame` have their (protein, subclass) cell present in train.

        The no-model baseline is that cell's train positive rate; with no train row it
        falls back to "negative" (balanced accuracy 0.500 by construction), so such rows
        would compare the model to an uninformative fallback.
        """
        return self._protein_subclass_key(frame).isin(
            set(self._protein_subclass_key(csvtrain))
        )

    @staticmethod
    def _label_only_baseline(csvtrain, held, key_train, key_held):
        """Balanced accuracy of "this key was usually positive in train", and coverage.

        Unseen keys take the train majority label.
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
        """Print what a per-lipid / per-class label prior alone scores on valid and test.

        The reference for this run's metrics: on a protein-only cold split "this lipid is
        usually positive" already reaches 0.55-0.57 balanced accuracy. Under
        --double_coldsplit both numbers must be 0.500 with coverage 0.
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

    ##################################################################################
    #                         DESCRIPTOR & PROPENSITY FEATURES
    ##################################################################################
    # The _descpath_<token> columns and the --lipid_propensity_weight tensor.
    @staticmethod
    def _original_rows(frame):
        """A split frame's positions in the ORIGINAL table: pair_id, not the index
        (the sampled pool is re-indexed 0..N-1)."""
        if frame.empty:
            return np.array([], dtype=int)
        return frame["pair_id"].to_numpy(dtype=int)

    def _compute_lipid_propensity_weights(self, csv):
        """Per-train-row loss weight, |label - s_chem|, class-normalized to mean 1.

        s_chem is the leave-one-out k-NN score of --chem_prior. Rows the lipid alone already
        predicts get low weight, rows where the label disagrees get high weight
        (--lipid_propensity_weight).

        `csv` must be the ORIGINAL table (species_similarity indexes by its row positions),
        hence the call from __init__.

        Normalized to mean 1 separately for positives and negatives, so the
        positive:negative balance set at sampling is untouched.
        """
        similarity, index = species_similarity(csv, self.ROOT_DIR)
        s_chem = knn_scores_leave_one_row_out(
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

    def _descriptor_features_cache_key(self):
        """Fingerprint of the finished descriptor feature columns _compute_descriptors writes.

        Covers the full config, the exact pair_id set of every split (train-only
        statistics depend on it), the lipid/protein descriptor tables (size and mtime of
        their manifests) and the source of _compute_descriptors itself. An unrelated
        config field only costs a cache miss; a stale hit would be a silent error.
        """
        import hashlib
        import inspect
        import json
        from pathlib import Path

        config_dict = {
            name: value for name, value in vars(self.config).items()
            if isinstance(value, (bool, int, float, str, type(None)))
        }

        def table_state(path):
            path = Path(path)
            if not path.exists():
                return None
            stat = path.stat()
            return [stat.st_size, stat.st_mtime_ns]

        root_dir = Path(self.ROOT_DIR)
        payload = {
            "config": config_dict,
            "train_pair_ids": sorted(int(x) for x in self.csvtrain["pair_id"]),
            "valid_pair_ids": (
                sorted(int(x) for x in self.csvalidate["pair_id"])
                if not self.csvalidate.empty else []
            ),
            "test_pair_ids": (
                sorted(int(x) for x in self.csvtest["pair_id"])
                if not self.csvtest.empty else []
            ),
            "lipid_table": table_state(root_dir / "lipid_descriptors.manifest.json"),
            "protein_table": table_state(root_dir / "protein_descriptors.manifest.json"),
            "code": hashlib.sha256(
                inspect.getsource(PLIDataset._compute_descriptors).encode()
            ).hexdigest()[:16],
        }
        blob = json.dumps(payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()[:24]

    def _descriptor_features_cache_path(self, key):
        from pathlib import Path

        return Path(self.ROOT_DIR) / "cache" / f"descriptor_features_{key}.pt"

    @staticmethod
    def _load_descriptor_features_cache(path):
        """{"csvtrain"/"csvalidate"/"csvtest": {column: array}} if a cache for this
        fingerprint exists, else None (the name is the validity check)."""
        if not path.exists():
            return None
        try:
            return torch.load(path, weights_only=False)
        except Exception:
            return None  # corrupt file: recompute

    @staticmethod
    def _save_descriptor_features_cache(path, split_columns):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(split_columns, path)
        except OSError:
            pass  # read-only data/: values stay correct, just not persisted

    def _compute_descriptors(self, csv):
        """Attach one `_descpath_<token>` column per token of descriptor_catalog_input.

        Tokens come from dataloader.descriptors.full_catalog_order (--descriptor_heads,
        --protein_descriptors, --lipid_descriptors, --deepclip_protein_gate): bare names
        or `<name>_coarse=<spec>` (N equal-width or N train-fit quantile bins, see
        parse_descriptor_token). Pair-formula names use pair_descriptor_value, the same
        function as analysis/baselines/knn_model.py.

        "extent" is always rounded to EXTENT_BINS train-fit quantile levels, so a held-out
        protein's raw cavity size cannot identify it.

        Standardised on TRAIN candidates only; a missing value raises.
        """
        if not full_catalog_order(self.config):
            return

        # Finished columns are cached on disk under a key covering the full config and
        # every split's pair_id set (see _descriptor_features_cache_key).
        features_cache_key = self._descriptor_features_cache_key()
        features_cache_path = self._descriptor_features_cache_path(features_cache_key)
        cached_features = self._load_descriptor_features_cache(features_cache_path)
        if cached_features is not None:
            self.csvtrain = self.csvtrain.assign(**cached_features["csvtrain"])
            self.csvalidate = self.csvalidate.assign(**cached_features["csvalidate"])
            self.csvtest = self.csvtest.assign(**cached_features["csvtest"])
            return

        isomeric = self.config.lipid_isomers
        # None (no current cache) falls every lookup back to computing directly; the
        # cache holds every measure and a run reads only the keys it requests
        # (dataloader/descriptor_cache_reader.py, data/build_descriptor_cache.py).
        pair_cache = load_lipid_descriptor_cache(self.ROOT_DIR, isomeric)
        protein_raw = protein_descriptor_table(self.ROOT_DIR)
        protein_cache = {
            protein: {"extent": values["pocket_extent"]}
            for protein, values in protein_raw.items()
        }
        extents = pocket_extent_by_protein(
            self.ROOT_DIR, self.protein_names, cache=protein_cache
        )
        extent = csv["LTPProtein"].map(extents).to_numpy(dtype=float)

        train_rows = self._original_rows(self.csvtrain)

        def lipid_values(key):
            """Per-row arrays (one value per candidate) of one lipid measure."""
            if key == "chain":
                values = chain_lengths_by_row(csv, isomeric, cache=pair_cache)
            else:
                measure = "heavy_atoms" if key == "heavy" else key
                values = descriptor_values_by_row(csv, measure, isomeric, cache=pair_cache)
            values = as_arrays(values)
            if key in LIPID_LEVEL_MEASURES:
                values = share_value_within_lipid(
                    values, csv["FullIdentityOfLipid"].to_numpy(), key, LIPID_LEVEL_MEASURES[key]
                )
            return require_no_missing(values, key)

        bins = EXTENT_BINS
        edges = None
        if len(train_rows) and bins > 1:
            train_extent = extent[train_rows]
            edges = np.quantile(train_extent, np.linspace(0, 1, bins + 1))
            edges[0], edges[-1] = -np.inf, np.inf
            edges = np.unique(edges)
        coarse_extent = coarsen_to_levels(extent, edges) if edges is not None else extent

        # Build raw values only for the BASE names the requested tokens reference; the
        # coarsening and the train-only standardisation come after.
        raw_values = {}  # base_name -> (values, is_ragged)
        materialised = {}  # token -> (values, is_ragged, mean, spread)
        from dataloader.descriptors import BOUNDED_SHARE_DESCRIPTOR_NAMES, LIPID_DESCRIPTOR_NAMES as _CATALOG_LIPID_NAMES, PAIR_DESCRIPTOR_NAMES as _CATALOG_PAIR_NAMES, POCKET_CHEMISTRY_DESCRIPTOR_NAMES as _CATALOG_POCKET_CHEMISTRY_NAMES, PROTEIN_DESCRIPTOR_NAMES as _CATALOG_PROTEIN_NAMES, parse_descriptor_token
        from preprocessing.compute_descriptors import pair_descriptor_value

        requested_tokens = full_catalog_order(self.config)
        base_names_needed = {
            parse_descriptor_token(token)[0] for token in requested_tokens
        }
        protein_names_needed = base_names_needed & (
            set(_CATALOG_PROTEIN_NAMES)
            | set(_CATALOG_POCKET_CHEMISTRY_NAMES)
            | {"polar_share"}
        )
        pair_names_needed = base_names_needed & set(_CATALOG_PAIR_NAMES)

        # Lipid measures. chain/unsaturation/hbond/heavy are always built; tail_count,
        # npr1 and npr2 also when a pair formula reads them (tail_elongation_fit,
        # elongation_shape_match, flatness_shape_match), even if nobody named them.
        lipid_keys = ["chain", "unsaturation", "hbond", "heavy"]
        if "tail_count" in base_names_needed or pair_names_needed:
            lipid_keys.append("tail_count")
        if "npr1" in base_names_needed or "elongation_shape_match" in pair_names_needed:
            lipid_keys.append("npr1")
        if "npr2" in base_names_needed or "flatness_shape_match" in pair_names_needed:
            lipid_keys.append("npr2")
        lipid_keys += [
            name for name in _CATALOG_LIPID_NAMES
            if name in base_names_needed and name not in (
                "chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2"
            )
        ]
        lipid = {key: lipid_values(key) for key in lipid_keys}
        for key, values in lipid.items():
            raw_values[key] = (values, True)
        raw_values["extent"] = (coarse_extent, False)

        if protein_names_needed or pair_names_needed:
            protein_column = csv["LTPProtein"].to_numpy()
            for name in protein_names_needed:
                raw_values[name] = (
                    np.array(
                        [protein_raw[protein][name] for protein in protein_column],
                        dtype=float,
                    ),
                    False,
                )
            # A pair formula reads these lipid fields (npr1/npr2 only if they were built).
            pair_lipid_keys = [
                key for key in ("chain", "unsaturation", "hbond", "heavy", "tail_count", "npr1", "npr2")
                if key in lipid
            ]
            for name in pair_names_needed:
                raw_values[name] = (
                    [
                        np.array(
                            [
                                pair_descriptor_value(
                                    name,
                                    {key: lipid[key][row_position][candidate] for key in pair_lipid_keys},
                                    protein_raw[protein_column[row_position]],
                                )
                                for candidate in range(len(row))
                            ],
                            dtype=float,
                        )
                        for row_position, row in enumerate(lipid["chain"])
                    ],
                    True,
                )

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
                if hi <= lo:  # constant column
                    hi = lo + 1.0
                edges = np.linspace(lo, hi, spec.bins + 1)
            else:
                edges = (
                    np.quantile(flat, np.linspace(0, 1, spec.bins + 1)) if len(flat)
                    else np.linspace(0.0, 1.0, spec.bins + 1)
                )
            edges = edges.astype(float)
            edges[0], edges[-1] = -np.inf, np.inf
            return np.unique(edges)  # ties collapse bins: N is an upper bound

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
            if not len(rows):
                return {f"_descpath_{token}": [] for token in requested_tokens}
            # Protein-level tokens are one value per row, repeated over its candidates.
            counts = [len(row) for row in ragged_rows(lipid["chain"], rows)]
            out = {}
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

        split_columns = {"csvtrain": columns(train_rows)}
        for name in ("csvalidate", "csvtest"):
            frame = getattr(self, name)
            rows = self._original_rows(frame) if not frame.empty else np.array([], dtype=int)
            split_columns[name] = columns(rows)

        self._save_descriptor_features_cache(features_cache_path, split_columns)

        self.csvtrain = self.csvtrain.assign(**split_columns["csvtrain"])
        self.csvalidate = self.csvalidate.assign(**split_columns["csvalidate"])
        self.csvtest = self.csvtest.assign(**split_columns["csvtest"])

    ##################################################################################
    #                        LIPID COLD-SPLIT AXIS (CONTINUED)
    ##################################################################################
    # Which classes/species a held-out family's holdout derives to (back to the
    # _cold_chemistry/_has_cold_chemistry block above).
    def _derive_lipid_class_holdout(self, csv):
        """Work out which head-group classes leave training, from the held-out family.

        The set differs per family, so it is derived (lipid_classes_for_holdout) from the
        FULL table, not the sampled pool, and does not drift with seed or
        negatives_per_positive. Several excluded groups take the union of their sets.
        The list is printed because the run log is the only record of it.
        """
        if self.lipid_isolation:
            species = LIPID_ISOLATION_BLOCKS.get(self.lipid_isolation)
            if species is None:
                raise ValueError(
                    f"lipid_isolation block {self.lipid_isolation!r} is accepted by the "
                    "configuration but absent from LIPID_ISOLATION_BLOCKS"
                )
            self.excluded_lipid_species = set(species)
            positives = int(
                csv.loc[csv["FullIdentityOfLipid"].isin(self.excluded_lipid_species),
                        "Interaction"].sum()
            )
            geometry = BLOCK_GEOMETRY.get(self.lipid_isolation)
            print(
                f"lipid isolation block '{self.lipid_isolation}' : {len(species)} "
                f"species held out of training for every protein, {positives} positives"
                + (f", isolation {geometry[0]:.3f} when chosen" if geometry else "")
            )
            return

        if self.lipid_subclass:
            species = subclass_block_species(self.lipid_subclass, self.ROOT_DIR)
            self.excluded_lipid_species = set(species)
            positives = int(
                csv.loc[csv["FullIdentityOfLipid"].isin(self.excluded_lipid_species),
                        "Interaction"].sum()
            )
            tanimoto = BLOCK_TANIMOTO.get(self.lipid_subclass)
            print(
                f"lipid subclass block '{self.lipid_subclass}' : {len(species)} species "
                f"held out of training for every protein, {positives} positives"
                + (
                    f", Tanimoto to train {tanimoto[0]:.3f} whole / "
                    f"{tanimoto[1]:.3f} head group"
                    if tanimoto else
                    " (block Tanimoto not in BLOCK_TANIMOTO -- measure it with "
                    "analysis/probes/lipid_subclass_report.py blocks)"
                )
            )
            return

        if self.lipid_species_coldsplit:
            species, stats = species_coldsplit_block(
                csv,
                self.lipid_species_coldsplit,
                self.seed,
                isomeric=bool(self.config.lipid_isomers),
            )
            self.excluded_lipid_species = set(species)
            print(
                f"lipid species cold split {self.lipid_species_coldsplit:.2f} : "
                f"{stats['species']} lipids in {stats['components_used']} of "
                f"{stats['components']} structure-disjoint components held out of "
                f"training for every protein, {stats['block_positives']} positives in "
                f"{stats['block_rows']} rows over {stats['block_proteins']} proteins; "
                f"train keeps {stats['train_positives']} positives"
            )
            if stats["proteins_without_train_positive"]:
                # Not repaired here (a silent redraw would change what the share means per seed).
                print(
                    f"  warning: {stats['proteins_without_train_positive']} protein(s) "
                    "have no positive left anywhere in training at this share"
                )
            return

        if self.lipid_coldsplit:
            classes = LIPID_COLDSPLIT_SETS.get(self.lipid_coldsplit)
            if classes is None:
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

    def _suspect_negative_share(self):
        """Share of train negatives sharing a (protein, article subclass) cell with a
        train positive, or None when the subclass classification is not built.

        None rather than an exception: this is a diagnostic every run reports, not an
        input any run depends on, so a missing classification file must not stop
        training the way it stops --lipid_subclass (which cannot even define its split
        without it).
        """
        try:
            from dataloader.splitting_on_blocks.lipid_subclass_blocks import (
                article_subclass_species,
            )

            subclasses = article_subclass_species(self.ROOT_DIR)
        except (FileNotFoundError, ValueError):
            return None
        if self.csvtrain.empty:
            return None

        subclass_of = {
            name: subclass
            for subclass, species in subclasses.items()
            for name in species
        }
        # "?unclassified" for a species the article does not place, exactly as
        # analysis/baselines/protein_subclass_label_baseline.protein_subclass_key does,
        # so the two agree on what a cell is.
        cells = (
            self.csvtrain["LTPProtein"].astype(str)
            + "|"
            + self.csvtrain["FullIdentityOfLipid"].map(subclass_of).fillna("?unclassified")
        )
        is_positive = self.csvtrain["Interaction"] == 1
        positive_cells = set(cells[is_positive])
        negatives = cells[~is_positive]
        if negatives.empty:
            return None
        return float(negatives.isin(positive_cells).mean())

    ##################################################################################
    #                               SAMPLING & SPLITTING
    ##################################################################################
    # Which rows become positive_pairs/unlabeled_pairs, then train/valid/test.
    def _sample_interactions(self, csv, seed):
        # Which side of the lipid-class cut each row falls on, so the per-protein and
        # per-family samplers match negatives to positives within each side. The
        # per-(group, class) sampler needs none: a class is held out whole.
        strata = None
        if self._has_cold_chemistry:
            strata = self._cold_chemistry(csv)

        # --hard_negative_mining / --dissimilar_negative_mining: one similarity pool for
        # the whole dataset, accepted by all three balanced samplers. --negative_similarity
        # picks which similarity it holds and therefore which axis a row is identified on.
        hard_negative_pool = None
        negative_mode = "hard"
        negative_share = self.hard_negative_share
        if self.hard_negative_mining or self.dissimilar_negative_mining:
            hard_negative_pool = resolve_similarity_pool(
                self.negative_similarity,
                csv,
                self.ROOT_DIR,
                parse_descriptor_list(self.negative_similarity_descriptors)
                if self.negative_similarity_descriptors
                else (),
                self.config,
            )
            print(pool_report(hard_negative_pool), flush=True)
            if self.dissimilar_negative_mining:
                negative_mode = "dissimilar"
                negative_share = self.dissimilar_negative_share

        if self.balanced_lipid_classes:
            positive_pairs, unlabeled_pairs = split_and_sample_lipid_class_balanced_interactions(
                csv, seed, ratio=self.negatives_per_positive,
                hard_negative_pool=hard_negative_pool,
                excluded_groups=self.excluded_groups,
                hard_negative_share=negative_share,
                negative_mode=negative_mode,
            )
        elif self.balanced_proteins:
            positive_pairs, unlabeled_pairs = split_and_sample_protein_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata,
                hard_negative_pool, self.excluded_groups, negative_share,
                negative_mode,
            )
        elif self.balance_negatives_by_family:
            positive_pairs, unlabeled_pairs = split_and_sample_family_balanced_interactions(
                csv, seed, self.negatives_per_positive, strata,
                hard_negative_pool, self.excluded_groups, negative_share,
                negative_mode,
            )
        else:
            positive_pairs, unlabeled_pairs = split_and_sample_interactions(csv, seed)
        # Not under a lipid cold split: the redraw is blind to `strata`, which shrinks the
        # block and makes its size seed-dependent; the per-side match above already gives
        # the exact ratio.
        if (
            self.excluded_groups
            and self.balance_excluded_group_negatives
            and not self._has_cold_chemistry
        ):
            unlabeled_pairs = rebalance_excluded_group_negatives(
                csv, unlabeled_pairs, self.excluded_groups, seed
            )
        return positive_pairs, unlabeled_pairs

    def _split_interactions(self, seed):
        if self.excluded_groups:
            csvtrain = self.sampled_split[
                ~self.sampled_split["ProteinDomain"].str.lower().isin(self.excluded_groups)
            ]
        elif (
            self.excluded_subgroups
            or self.lipid_coldsplit
            or self.lipid_isolation
            or self.lipid_subclass
            or self.lipid_species_coldsplit
        ):
            # Lipid-axis splits keep every protein: the whole table is train until the class
            # filter below removes the held-out chemistry.
            csvtrain = self.sampled_split
        else:
            csvtrain = self.sampled_split.sample(frac=0.85, random_state=seed)

        if self.excluded_subgroups:
            csvtrain = csvtrain[
                ~csvtrain["LTPProtein"].isin(self.excluded_subgroups)
            ]

        # Lipid axis: held-out chemistry leaves train for EVERY protein; what the filter
        # removes joins excluded_data below.
        if self._has_cold_chemistry:
            csvtrain = csvtrain[~self._cold_chemistry(csvtrain)]

        excluded_data = self.sampled_split.drop(csvtrain.index)

        # --double_coldsplit keeps only the intersection: held-out proteins AND held-out
        # chemistry. The held-out family's rows in classes that stayed in train are dropped
        # (their lipids are in train, so a per-lipid prior would score on them), and so are
        # other proteins' rows in removed classes (cold on the lipid axis only). Neither
        # group can go to train.
        if self.double_coldsplit and self._has_cold_chemistry:
            in_cold_chemistry = self._cold_chemistry(excluded_data)
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

        # --drop_uncovered_protein_subclass: applied to the whole block BEFORE the label-wise
        # halving below, which keeps the valid and test positive rates equal.
        if self.drop_uncovered_protein_subclass:
            covered = self._covered_protein_subclass(excluded_data, csvtrain)
            dropped = excluded_data[~covered]
            excluded_data = excluded_data[covered]
            print(
                "drop_uncovered_protein_subclass : "
                f"{len(dropped)} of {len(dropped) + len(excluded_data)} block rows "
                f"dropped ({int(dropped['Interaction'].sum())} positives) -- their "
                "(protein, subclass) cell has no training row, so the no-model planka "
                "scores 0.500 on them by construction; "
                f"{len(excluded_data)} rows and "
                f"{int(excluded_data['Interaction'].sum())} positives remain"
            )
            if excluded_data.empty:
                raise ValueError(
                    "drop_uncovered_protein_subclass removed every valid/test row -- no "
                    "(protein, subclass) cell of the block appears in training at all"
                )
        if self.test_group:
            domain_lower = excluded_data["ProteinDomain"].str.lower()
            csvtest = excluded_data[domain_lower == self.test_group].sample(frac=1)
            csvalidate = excluded_data[domain_lower != self.test_group].sample(frac=1)
        else:
            # Halve each label separately so valid and test carry the same positive rate.
            positive_pool = excluded_data[excluded_data["Interaction"] == 1]
            negative_pool = excluded_data[excluded_data["Interaction"] == 0]
            positive_validate = positive_pool.sample(frac=0.5, random_state=seed)
            negative_validate = negative_pool.sample(frac=0.5, random_state=seed)
            csvalidate = pandas.concat(
                [positive_validate, negative_validate]
            ).sample(frac=1, random_state=seed)
            csvtest = excluded_data.drop(csvalidate.index).sample(frac=1)
        return self._add_rotating_negatives(csvtrain), csvalidate, csvtest

    def _add_rotating_negatives(self, csvtrain):
        """--rotate_train_negatives: put every eligible unsampled negative into train.

        Added after valid and test are cut out of self.sampled_split (not by widening the draw,
        which would change the evaluated block too), so it only grows train.

        Eligible: not already in self.sampled_split (that would leak the valid/test block), not a
        held-out protein, and not held-out chemistry (_cold_chemistry). Positives are
        never added; every positive is already in the pool.
        """
        source = self._rotation_source
        self._rotation_source = None
        if source is None:
            return csvtrain
        candidates = source[source["Interaction"] == 0]
        candidates = candidates[~candidates.index.isin(self.sampled_split["pair_id"].astype(int))]
        if self.excluded_groups:
            candidates = candidates[
                ~candidates["ProteinDomain"].str.lower().isin(self.excluded_groups)
            ]
        if self.excluded_subgroups:
            candidates = candidates[
                ~candidates["LTPProtein"].isin(self.excluded_subgroups)
            ]
        if self._has_cold_chemistry and not candidates.empty:
            candidates = candidates[~self._cold_chemistry(candidates)]
        if candidates.empty:
            print("rotate_train_negatives : no unsampled negative was eligible")
            return csvtrain
        candidates = candidates.copy()
        candidates["pair_id"] = candidates.index
        # Index positions past self.sampled_split's range (pair_id is untouched).
        candidates.index = pandas.Index(
            range(len(self.sampled_split), len(self.sampled_split) + len(candidates))
        )
        combined = pandas.concat([csvtrain, candidates])
        print(
            f"rotate_train_negatives : train negatives "
            f"{int((csvtrain['Interaction'] == 0).sum())} -> "
            f"{int((combined['Interaction'] == 0).sum())} "
            f"({len(candidates)} added), positives "
            f"{int((combined['Interaction'] == 1).sum())} unchanged"
        )
        return combined

    ##################################################################################
    #                             SAMPLE-WEIGHT ACCESSORS
    ##################################################################################
    # get_*_weights(): one tensor per id2pos position, read by training/task_losses.py.
    def get_tanimoto_weights(self):
        if self.train_tanimoto_matrix is None:
            raise RuntimeError(
                "Tanimoto weights need the compact Tanimoto artifacts, which are only "
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
        """The --lipid_propensity_weight tensor computed in __init__ (it needs the original
        table), or zeros of the same shape."""
        return getattr(
            self, "_lipid_propensity_weights",
            torch.zeros(len(self.id2pos), dtype=torch.float32),
        )

    def get_protein_balance_weights(self):
        """Per-row weights that restore each protein's pos:neg ratio inside train.

        Holding out lipid classes cuts unevenly across proteins (STARD2 ends a two-axis
        split at 4 positive against 91 unlabeled). Instead of re-matching by discarding,
        a positive weighs 1 and a negative weighs its protein's positives over its
        negatives, so both sides of every protein carry equal total weight. A protein
        with no positives left gets zero weight.

        Normalized by the mean and indexed by ``id2pos`` like the other weight tables.
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

    MARGINAL_BALANCE_ITERATIONS = 100

    def get_marginal_balance_weights(self):
        """Per-row weights under which no protein, lipid class or lipid is "usually positive".

        Iterative proportional fitting (raking) over ``LTPProtein``, the lipid class and
        ``FullIdentityOfLipid``: each key's weighted positive rate is rescaled to the
        train-wide rate until all three hold at once. The joint of two keys is left alone.

        The target is the train-wide rate, not 0.5, so the class balance the loss sees
        is not moved twice. Single-label keys cannot be rebalanced and keep their
        weights (their count is printed).

        Normalized by the mean and indexed by ``id2pos``.
        """
        labels = self.csvtrain["Interaction"].astype(int).to_numpy()
        keys = {
            "protein": self.csvtrain["LTPProtein"].astype(str).str.lower(),
            "lipid class": lipid_class_series(self.csvtrain).astype(str).str.lower(),
            "lipid": self.csvtrain["FullIdentityOfLipid"].astype(str),
        }
        codes = {name: pandas.factorize(values)[0] for name, values in keys.items()}
        positive = labels == 1
        target = float(positive.mean())
        row_weight = np.ones(len(labels), dtype=np.float64)

        def cell_sums(code):
            positive_sum = np.bincount(code, weights=row_weight * positive)
            total_sum = np.bincount(code, weights=row_weight)
            return positive_sum, total_sum

        for _ in range(self.MARGINAL_BALANCE_ITERATIONS):
            for code in codes.values():
                positive_sum, total_sum = cell_sums(code)
                negative_sum = total_sum - positive_sum
                mixed = (positive_sum > 0) & (negative_sum > 0)
                positive_factor = np.where(
                    mixed, target * total_sum / np.maximum(positive_sum, 1e-12), 1.0
                )
                negative_factor = np.where(
                    mixed, (1.0 - target) * total_sum / np.maximum(negative_sum, 1e-12), 1.0
                )
                row_weight *= np.where(positive, positive_factor[code], negative_factor[code])
            row_weight /= row_weight.mean()

        report = []
        for name, code in codes.items():
            positive_sum, total_sum = cell_sums(code)
            mixed = (positive_sum > 0) & (positive_sum < total_sum)
            residual = (
                float(np.abs(positive_sum[mixed] / total_sum[mixed] - target).max())
                if mixed.any() else 0.0
            )
            report.append(
                f"{name} {int(mixed.sum())} keys (residual {residual:.1e}, "
                f"{int((~mixed).sum())} single-label)"
            )
        print(
            f"marginal balance weights : target positive rate {target:.3f} | "
            + " | ".join(report)
            + f" | weight range {row_weight.min():.3f}-{row_weight.max():.3f}"
        )

        weights = torch.zeros(len(self.id2pos), dtype=torch.float32)
        for pair_id, weight in zip(self.csvtrain["pair_id"].astype(int), row_weight):
            weights[self.id2pos[int(pair_id)]] = float(weight)
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

    ##################################################################################
    #                                 CACHE LIFECYCLE
    ##################################################################################
    # Warm every per-sample cache before DataLoader workers fork; release the rest after.
    def warm_caches(self, csv=None):
        """Build every protein graph and lipid encoding this split needs, up front.

        Called before the DataLoader forks its workers, so they share one warm cache.
        Warming performs no random draw; only the isomer-graph path with a per-access
        draw (which draws inside make_graph_lipid) is skipped.

        Returns the entry count of each cache, for reporting.
        """
        frame = self.csv if csv is None else csv
        catalog_only = descriptor_catalog_only(self.config)
        for prot_file in frame["LTPProtein"].dropna().unique().tolist():
            if self.config.deepclip or catalog_only:
                # Not lazy: protein_family reads sampled_split, dropped by release_source_artifacts().
                self.protein_family_one_hot(prot_file)
            else:
                self.protein_graph_parts(prot_file)
        isomer_graphs = self.config.lipid_graph_isomers
        if not (isomer_graphs and self._draw_lipid_candidate):
            seen = set()
            for _, row in frame.iterrows():
                key = (str(row["SmileGlobal"]), str(row["SmileFragment"]))
                if key in seen:
                    continue
                seen.add(key)
                if catalog_only:
                    # Only the candidate keys the draw picks from.
                    self.candidate_keys_for_row(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
                elif isomer_graphs:
                    self.make_graph_lipid(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
                else:
                    self.warm_lipid_encoding(
                        row["SmileGlobal"], row["SmileFragment"]
                    )
        return {
            "proteins": len(self._protein_graph_cache),
            # One of the two caches is used per run.
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
        for name in ("full_csv", "positive_pairs", "unlabeled_pairs", "csvtt"):
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

        # The isomer-graph drawing split is not warmed (see warm_caches), so it keeps the
        # raw tensor cache; every other config can drop it.
        can_release_lipid_tensor_cache = not (
            self.config.lipid_graph_isomers
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
                for _, row in self.sampled_split.iterrows()
            }
            if expected_keys.issubset(self._lipid_encoding_cache):
                self.smiles_encoding = None
                released.append("smiles_encoding")
        if hasattr(self, "sampled_split"):
            del self.sampled_split
            released.append("sampled_split")
        return released

    ##################################################################################
    #                              PER-SAMPLE SERVING
    ##################################################################################
    
    # Everything below runs on every get() call, every epoch -- reads only what
    # construction above already built. __iter__ is the bridge: runs once per training
    # run, not per epoch, to set the per-split flags/tensors get() then reads.
    # dataloader/preassembled_loader.py depends only on this half. Under
    # --eval_average_candidates, _expand_candidate_rows is the input-side half of one
    # feature; training/candidate_averaging.py is the output-side half.
    def len(self):
        #lenght of combinations or lenght of structures/smiles?
        return len(self.csv)

    def _weight_positions(self, pair_ids):
        """Each row's slot in the sample-weight vector, or -1 when it has none.

        id2pos is the rank among sorted train pair ids, so this is a binary search; it
        equals ``id2pos.get(pair_id, -1)``. Validation and test rows get -1, which would
        index the LAST weight, safe only because the loss reads positions in training alone.
        """
        known = np.sort(np.fromiter(self.id2pos, dtype=np.int64, count=len(self.id2pos)))
        if known.size == 0:
            return np.full(len(pair_ids), -1, dtype=np.int64)
        # searchsorted gives an insertion point; confirm each hit by comparing back.
        positions = np.searchsorted(known, pair_ids)
        inside = positions < known.size
        found = np.zeros(len(pair_ids), dtype=bool)
        found[inside] = known[positions[inside]] == np.asarray(pair_ids)[inside]
        return np.where(found, positions, -1)

    def _prepare_indexed_fields(self):
        """Materialize the columns and scalar tensors read by every get()."""
        # Present only on an expanded evaluation split (_expand_candidate_rows).
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
        # --lipid_class_targets (train only): the target widens to "this protein has a
        # positive somewhere in this species' head-group class", built from this split's
        # rows alone.
        interaction_source = (
            class_level_positive_labels(self.csv)
            if self._use_lipid_class_targets
            else self.csv["Interaction"]
        )
        self._interaction_tensor = torch.tensor(
            interaction_source.to_numpy(),
            dtype=torch.long,
        )
        orig_indexes = self.csv["pair_id"].to_numpy()
        # The sample cache's key (see get()).
        self._pair_id_by_idx = orig_indexes
        # Only read by --pu_rho_by_subclass (TaskLosses.pu_prior_and_groups).
        self._pair_id_tensor = (
            torch.tensor(orig_indexes, dtype=torch.long).view(-1, 1)
            if self.config.pu_rho_by_subclass
            else None
        )
        # Pair id per sample on an expanded split; new_train averages candidates by it.
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
        # Flat values plus row offsets (rows have 1-37 candidates); a column only under
        # --chem_prior / --pocket_compat_prior.
        self._frozen_prior_tensor, self._frozen_prior_offsets = _ragged_tensor(
            self.csv["_frozen_prior"] if "_frozen_prior" in self.csv.columns else None
        )
        # One column per token of full_catalog_order(config), in that order; every head and
        # encoder calls the same function, so all index this one tensor consistently.
        requested_tokens = full_catalog_order(self.config)
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

        Each copy carries the candidate index it encodes; new_train averages the
        predictions back per pair before the threshold.
        """
        cap = self.config.eval_candidates_per_pair
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

        Everything up to the cap, evenly spread (ends included) beyond it, since the list
        starts with the row's own annotation and a prefix would sample just that. 0 or an
        unreached cap means every candidate.
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
        if self.config.eval_average_candidates:
            valid_dataset.csv = self._expand_candidate_rows(valid_dataset.csv)
            test_dataset.csv = self._expand_candidate_rows(test_dataset.csv)
        # Residue subsampling and lipid_random_choice are train-only augmentations: on
        # validation and test they would make the checkpoint-selection metric a random draw
        # (those splits take the first candidate). Both disable the sample cache, which
        # would freeze the draw; the protein and lipid caches stay.
        train_dataset._use_lipid_class_targets = bool(
            self.config.lipid_class_targets
        )
        train_dataset._draw_lipid_candidate = bool(self.config.lipid_random_choice)
        train_dataset._augment_residues = bool(
            self.config.protein_residue_subsample
        )
        if train_dataset._augment_residues or train_dataset._draw_lipid_candidate:
            train_dataset._sample_cache_enabled = False
        # protein_id is carried only where something reads it: the ranking loss in train,
        # save_dynamics (or the ranking loss, to keep the loss comparable) in validation,
        # and run_test()'s per-protein metrics in test.
        train_dataset._needs_protein_id = bool(
            self.config.rank_within_protein
        )
        valid_dataset._needs_protein_id = bool(
            self.config.save_dynamics
            or self.config.rank_within_protein
        )
        test_dataset._needs_protein_id = True
        train_dataset._prepare_indexed_fields()
        valid_dataset._prepare_indexed_fields()
        test_dataset._prepare_indexed_fields()
        return iter((train_dataset, valid_dataset, test_dataset))

    def set_epoch(self, epoch):
        """Rotate the residue subsample (called once per epoch by the training loop).

        The mask is seeded from (run seed, pair_id, epoch) alone, so it does not depend
        on batch order or worker count.
        """
        self._augmentation_epoch = int(epoch)

    def _subsample_residues(self, parts, pair_id):
        """Keep a fixed number of randomly chosen residues, redrawn every epoch."""
        count = int(self.config.protein_residue_subsample or 0)
        if count <= 0 or not self._augment_residues:
            return parts
        total = int(parts["x"].shape[0])
        if total <= count:
            return parts
        seed = ((int(self.config.seed) * 1_000_003 + int(pair_id)) * 1_000_003
                + int(self._augmentation_epoch)) % (2 ** 63 - 1)
        generator = torch.Generator().manual_seed(seed)
        keep = torch.zeros(total, dtype=torch.bool)
        keep[torch.randperm(total, generator=generator)[:count]] = True
        return restrict_parts_to_mask(parts, keep)

    def get(self, idx):
        # The sample cache is keyed by pair_id (plus candidate on an expanded split), never
        # by idx: idx is a position within one split, and the splits share these dicts.
        candidate_index = (
            None
            if self._candidate_index_by_idx is None
            else int(self._candidate_index_by_idx[idx])
        )
        if candidate_index is None and self._draw_lipid_candidate:
            # Drawn here so the prior and descriptor columns use the encoded candidate.
            candidate_index = self.draw_candidate_index(
                self._smile_global_by_idx[idx], self._smile_fragment_by_idx[idx]
            )
        return self.sample_for_candidate(idx, candidate_index)

    def candidate_count(self, idx):
        """How many candidates draw_candidate_index chooses among for row `idx`."""
        smile_global, smile_fragment = self._smiles_pair(
            self._smile_global_by_idx[idx], self._smile_fragment_by_idx[idx]
        )
        return len(self.candidate_keys_for_row(smile_global, smile_fragment))

    def sample_for_candidate(self, idx, candidate_index):
        """Row `idx`'s sample encoded as candidate `candidate_index` (None: the row's
        fixed encoding). Everything get() does after the draw -- split out so
        dataloader/preassembled_loader.py can build each candidate's sample once and
        leave only the draw itself to each access."""
        pair_id = int(self._pair_id_by_idx[idx])
        protein = self._protein_by_idx[idx]
        smile_global = self._smile_global_by_idx[idx]
        smile_fragment = self._smile_fragment_by_idx[idx]
        cache_key = pair_id if candidate_index is None else (pair_id, candidate_index)
        cached = self._sample_cache.get(cache_key)
        if cached is not None:
            return cached

        catalog_only = descriptor_catalog_only(self.config)
        if self.config.lipid_graph_isomers or catalog_only:
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

        if self.config.deepclip or catalog_only:
            # No protein graph: DeepCLIP's input is the lipid alone and the catalog-only
            # path reads just descriptor_catalog_input. Kept are the label, the family
            # one-hot (group DRO) and the identifiers finish_sample attaches.
            protein_graph = ProteinGraphData(
                inter=self._interaction_tensor[idx],
                family=self.protein_family_one_hot(protein),
            )
            if self._protein_tokens:
                # Graph-level [1, longest, 3], stacked to [batch, longest, 3] on collation.
                protein_graph.protein_tokens = self._protein_tokens[protein]
                protein_graph.protein_token_count = self._protein_token_counts[protein]
        else:
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
        # pair_id / candidate_group are None when nothing reads them (_prepare_indexed_fields).
        if self._pair_id_tensor is not None:
            protein_graph.pair_id = self._pair_id_tensor[idx]
        if self._candidate_group_tensor is not None:
            protein_graph.candidate_group = self._candidate_group_tensor[idx]
        protein_graph.tanimoto_pos = self._tanimoto_pos_tensor[idx]
        if self._protein_id_tensor is not None:
            protein_graph.protein_id = self._protein_id_tensor[idx]
        # Both follow the candidate the sample is encoded as.
        if self._frozen_prior_tensor is not None:
            position = _candidate_position(
                self._frozen_prior_offsets, idx, candidate_index
            )
            protein_graph.frozen_prior = self._frozen_prior_tensor[position].view(1)
        if self._descriptor_catalog_tensor is not None:
            position = _candidate_position(
                self._descriptor_catalog_offsets, idx, candidate_index
            )
            protein_graph.descriptor_catalog_input = (
                self._descriptor_catalog_tensor[position].view(1, -1)
            )
        if descriptor_catalog_only(self.config):
            lipid_graph = Data()  # only the descriptor columns above are read
        elif self.config.lipid_graph_isomers:
            lipid_graph = self.make_graph_lipid(
                smile_global, smile_fragment
            )
        else:
            # No edge_index and no liplab on this path: nothing reads them
            # (complete_graph_edge_index still builds the graph on demand).
            lipid_kwargs = {
                "x": lipid_enc,
            }
            if self.config.lipid_fragments_mask:
                lipid_kwargs["lipid_batch"] = lipid_batch
            lipid_graph = Data(**lipid_kwargs)

        return protein_graph, lipid_graph


# What finish_sample() above actually puts in (protein_graph, lipid_graph), by config:
#   protein_graph: real graph (x/edge_index/edge_attr/bury/plm/pocket/...) normally;
#                  just inter (label) + family (+ protein_tokens if set) under
#                  --deepclip or dh/mlp (descriptor_catalog_only).
#   lipid_graph:   x=768-wide embedding normally; a real atom graph
#                  (x/edge_index/edge_attr/liplab/chain_rank) under
#                  --lipid_graph_isomers; empty Data() under dh/mlp (wins over isomers).
#   descriptor_catalog_input is bolted onto protein_graph independently of the above
#   whenever --descriptor_heads/--protein_descriptors/--lipid_descriptors/
#   --deepclip_protein_gate is non-empty -- including alongside a real graph.

