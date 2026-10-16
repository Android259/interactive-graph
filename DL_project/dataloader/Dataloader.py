"""Build train/validation/test datasets once, then serve samples.

Construction (__init__ and helpers) loads/filters the CSV, samples negatives,
splits rows, computes descriptor/weight columns, and warms protein/lipid caches.

Per-sample methods (__iter__, get, sample_for_candidate, finish_sample)
read those artifacts each batch/epoch. preassembled_loader.py uses only this
phase, replaying sample_for_candidate's draw/assembly logic.

For --eval_average_candidates, _expand_candidate_rows supplies candidates;
training/candidate_averaging.py combines predictions per pair after forward.

PLIDataset composes FrozenPriorBuilder (frozen_prior.py),
LipidGraphBuilder/LipidIsomerGraphBuilder, and ProteinGraphBuilder
(graphs_builders/).
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
    pair_values_by_row,
    protein_descriptor_table,
)
from dataloader.descriptor_cache_reader import load_lipid_descriptor_cache, load_pair_value_cache
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
    # Construction: load/filter the CSV, sample/split, and warm caches once per run.
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
            # Keep index labels equal to positions after filtering: pair_id uses .index,
            # while descriptor arrays use .to_numpy().
            csv = csv.reset_index(drop=True)
        # Retain unsampled negatives for --rotate_train_negatives;
        # _add_rotating_negatives drops this reference after use.
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

        # Training-pool diagnostic, not a hyperparameter: share of negatives whose
        # (protein, article subclass) cell also has a positive. These pairs differ
        # only by lipids within a subclass and may be hard to separate from inputs.
        # Across seven --lipid_species_coldsplit=0.15 configurations, this share had
        # correlation -0.96 with test BA: 0.110 -> 0.923 versus 0.736 -> 0.769;
        # training error increased fourfold. Use only csvtrain cells and negatives,
        # excluding held-out data.
        self.suspect_negative_share = self._suspect_negative_share()

        # Only --tanimoto_weight loads compact similarities. Other runs rank train
        # row IDs for id2pos; weights need only a bijection to 0..N-1 addresses.
        self._needs_tanimoto_rows = bool(self.config.tanimoto_weight)

        self.train_tanimoto_batch = None
        self.train_tanimoto_matrix = None
        if self._needs_tanimoto_rows:
            train_idx = self.train_orig_indexes.numpy()
            # Use isomeric artifacts with --lipid_isomers. Older --tanimoto_weight runs
            # used non-isomeric similarities and are not comparable.
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
        # Skip MoLFormer for lipid_graph_isomers, --lipid_smiles_tokens, and descriptor_catalog_only.
        if (
            not self.config.lipid_graph_isomers
            and not self.config.lipid_smiles_tokens
            and not descriptor_catalog_only(self.config)
        ):
            # The non-isomeric table is a deterministic rebuild over all candidates with
            # one fixed random-feature matrix; old lipid_SMILES_embedding.pkl runs differ.
            # The isomeric table retains the old representation.
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
        # Cache run-fixed inputs, preserving rebuilt values. __iter__ shallow-copies
        # share these dicts across splits; workers fork after warm_caches().
        self._protein_graph_cache = {}
        # Skip protein tensors for --deepclip and descriptor_catalog_only: neither builds a graph.
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
        # lipid_random_choice caches canonical keys, never draws (_drawn_lipid_encoding).
        self._lipid_candidate_key_cache = {}
        self._lipid_graph_cache = {}
        self._complete_edge_index_cache = {}
        # Cache assembled samples by pair_id. __iter__ disables this for per-access
        # draws, which cached samples would freeze.
        self._sample_cache = {}
        self._sample_cache_enabled = True
        # Set train-only augmentations in __iter__ and epoch in set_epoch.
        # Keep validation/test inputs fixed across epochs.
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
        # Distant-negative steering; validate forbids combining with hard_negative_mining.
        self.dissimilar_negative_mining = config.dissimilar_negative_mining
        self.dissimilar_negative_share = config.dissimilar_negative_share
        # Similarity source and optional descriptor list for either steering direction;
        # see similarity_pool.py.
        self.negative_similarity = config.negative_similarity
        self.negative_similarity_descriptors = config.negative_similarity_descriptors
        # Derive held-out lipid classes from the full table in _derive_lipid_class_holdout.
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
        # Drop evaluated rows lacking a training (protein, subclass) cell;
        # _covered_protein_subclass leaves train unchanged.
        self.drop_uncovered_protein_subclass = config.drop_uncovered_protein_subclass
        self.test_group = config.test_group.lower()

    # Lipid cold split: shared class/species mask, independent of the protein axis.
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

    # No-model diagnostics: print lipid/species-class prior scores and coverage.
    @staticmethod
    def _protein_subclass_key(frame):
        """Return (LTPProtein, article subclass) as a string key per row.

        Match protein_subclass_label_baseline.py: same classification,
        ?unclassified fallback, and | join, so baseline/model evaluate the same rows.
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
        """Mark rows whose (protein, subclass) cell occurs in training.
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
        """Print lipid/species-class prior BA and coverage on validation/test.

        A protein-only cold split can score 0.55-0.57 from lipid priors alone.
        --double_coldsplit should give 0.500 for both priors with zero coverage.
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

    # Descriptor/propensity features: _descpath_<token> and --lipid_propensity_weight.
    @staticmethod
    def _original_rows(frame):
        """A split frame's positions in the ORIGINAL table: pair_id, not the index
        (the sampled pool is re-indexed 0..N-1)."""
        if frame.empty:
            return np.array([], dtype=int)
        return frame["pair_id"].to_numpy(dtype=int)

    def _compute_lipid_propensity_weights(self, csv):
        """Weight training rows by |label - s_chem| (--lipid_propensity_weight).

        Use --chem_prior's leave-one-out k-NN score: easy lipid-only predictions get
        less weight, disagreements more. Normalize each label separately to mean 1,
        preserving the sampled positive/negative balance.

        csv must be the original table because species_similarity uses its row
        positions; compute from __init__.
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
        """Fingerprint the finished _compute_descriptors columns.

        Include full config, every split's exact pair_id set, lipid/protein descriptor
        manifest sizes/mtimes, and _compute_descriptors source. Training statistics
        depend on split membership. Unrelated config edits may cost a cache miss;
        excluding a relevant input could silently serve stale values.
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
        """Load {split: {column: array}} for csvtrain/csvalidate/csvtest, or None.

        The fingerprinted filename determines validity.
        """
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
        """Attach _descpath_<token> columns for descriptor_catalog_input.

        full_catalog_order combines --descriptor_heads, --protein_descriptors,
        --lipid_descriptors, and --deepclip_protein_gate. Accept raw names or
        <name>_coarse=<spec> for equal-width/quantile bins (parse_descriptor_token).
        Pair formulas prefer data/pair_descriptors.csv (pair_values_by_row); the
        same pair_descriptor_value formulas back baselines/knn_model.py.

        Always coarsen extent to EXTENT_BINS training quantiles, preventing raw
        held-out cavity sizes acting as IDs. Standardize on training candidates only.
        Raise on missing values.
        """
        if not full_catalog_order(self.config):
            return

        # Cache finished columns by full config and split pair_ids
        # (_descriptor_features_cache_key).
        features_cache_key = self._descriptor_features_cache_key()
        features_cache_path = self._descriptor_features_cache_path(features_cache_key)
        cached_features = self._load_descriptor_features_cache(features_cache_path)
        if cached_features is not None:
            self.csvtrain = self.csvtrain.assign(**cached_features["csvtrain"])
            self.csvalidate = self.csvalidate.assign(**cached_features["csvalidate"])
            self.csvtest = self.csvtest.assign(**cached_features["csvtest"])
            return

        isomeric = self.config.lipid_isomers
        # Missing caches fall back to direct computation. Tables hold all measures;
        # runs read requested keys (descriptor_cache_reader.py, data/build_descriptor_cache.py).
        lipid_cache = load_lipid_descriptor_cache(self.ROOT_DIR, isomeric)
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
                values = chain_lengths_by_row(csv, isomeric, cache=lipid_cache)
            else:
                values = descriptor_values_by_row(csv, key, isomeric, cache=lipid_cache)
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

        # Build requested base values, then coarsen and standardize on training data.
        raw_values = {}  # base_name -> (values, is_ragged)
        materialised = {}  # token -> (values, is_ragged, mean, spread)
        from dataloader.descriptors import BOUNDED_SHARE_DESCRIPTOR_NAMES, LIPID_DESCRIPTOR_NAMES as _CATALOG_LIPID_NAMES, PAIR_DESCRIPTOR_NAMES as _CATALOG_PAIR_NAMES, PROTEIN_DESCRIPTOR_NAMES as _CATALOG_PROTEIN_NAMES, parse_descriptor_token
        from preprocessing.compute_descriptors import PAIR_DESCRIPTOR_LIPID_INPUTS

        requested_tokens = full_catalog_order(self.config)
        base_names_needed = {
            parse_descriptor_token(token)[0] for token in requested_tokens
        }
        protein_names_needed = base_names_needed & set(_CATALOG_PROTEIN_NAMES)
        pair_names_needed = base_names_needed & set(_CATALOG_PAIR_NAMES)

        # Always build chain/unsaturation/hbond/heavy. Also build tail_count/npr1/npr2
        # when needed by tail_elongation_fit/elongation_shape_match/flatness_shape_match,
        # even if not explicitly requested.
        lipid_keys = ["chain", "unsaturation", "hbond", "heavy"]
        if "tail_count" in base_names_needed:
            lipid_keys.append("tail_count")
        if "npr1" in base_names_needed:
            lipid_keys.append("npr1")
        if "npr2" in base_names_needed:
            lipid_keys.append("npr2")
        lipid_keys += [
            name for name in _CATALOG_LIPID_NAMES
            if name in base_names_needed and name not in PAIR_DESCRIPTOR_LIPID_INPUTS
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
            if pair_names_needed:
                # Pair formulas read data/pair_descriptors.csv when it is current,
                # falling back to the two source tables for a candidate it lacks.
                pair_cache_table = load_pair_value_cache(self.ROOT_DIR, isomeric)
                for name in pair_names_needed:
                    values = as_arrays(
                        pair_values_by_row(
                            csv, name, protein_raw, isomeric=isomeric,
                            lipid_cache=lipid_cache, pair_cache=pair_cache_table,
                        )
                    )
                    raw_values[name] = (require_no_missing(values, name), True)

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

    # Continue lipid holdout derivation; see _cold_chemistry/_has_cold_chemistry.
    def _derive_lipid_class_holdout(self, csv):
        """Derive excluded head-group classes from each held-out protein family.

        Use the full table via lipid_classes_for_holdout, independent of seed or
        negatives_per_positive. Union multiple excluded groups' sets.
        Print selected classes; the run log is their only record.
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
        """Return the train-negative share sharing a (protein, subclass) positive cell.

        Return None when classification is absent. This optional diagnostic must
        not stop training, unlike --lipid_subclass, which needs it to define a split.
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
        # Use ?unclassified and the same cell key as
        # analysis/baselines/protein_subclass_label_baseline.protein_subclass_key.
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

    # Sampling/splitting: positive_pairs/unlabeled_pairs, then train/validation/test.
    def _sample_interactions(self, csv, seed):
        # Per-protein/family samplers balance within each side of the lipid-class cut.
        # Per-(group, class) sampling needs no strata: each class leaves as a whole.
        strata = None
        if self._has_cold_chemistry:
            strata = self._cold_chemistry(csv)

        # Share one pool across all three balanced samplers for hard/dissimilar mining.
        # --negative_similarity selects the matrix and entity axis.
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
        # Skip this redraw for lipid cold splits: it ignores strata and makes block
        # size seed-dependent. Per-side matching already gives the required ratio.
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
            # For lipid-axis cuts, keep all proteins until the chemistry filter below.
            csvtrain = self.sampled_split
        else:
            csvtrain = self.sampled_split.sample(frac=0.85, random_state=seed)

        if self.excluded_subgroups:
            csvtrain = csvtrain[
                ~csvtrain["LTPProtein"].isin(self.excluded_subgroups)
            ]

        # Remove held-out chemistry for every protein; removed rows join excluded_data.
        if self._has_cold_chemistry:
            csvtrain = csvtrain[~self._cold_chemistry(csvtrain)]

        excluded_data = self.sampled_split.drop(csvtrain.index)

        # --double_coldsplit evaluates only held-out proteins AND chemistry.
        # Drop held-out-protein rows with familiar lipids (lipid-prior shortcut), and
        # known-protein rows with held-out lipids (only lipid-cold). Neither can train.
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

        # Apply --drop_uncovered_protein_subclass before label-wise halving,
        # keeping validation/test positive rates equal.
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
        """Add eligible unsampled negatives to train for --rotate_train_negatives.

        Do this after sampled_split's validation/test cut, so evaluation stays fixed.
        Exclude sampled_split rows, held-out proteins, and _cold_chemistry.
        Add no positives: all were already sampled.
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

    # Sample-weight accessors: one entry per id2pos, used by training/task_losses.py.
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
        """Return train weights balancing positives and negatives per protein.

        Lipid-class holdout can leave skew, e.g. STARD2 with 4 positives and
        91 unlabeled rows. Keep all rows: positives weigh 1; negatives weigh
        protein_positive_count/protein_negative_count. Each label then has equal
        total weight per protein. Proteins without positives get zero weight.
        Normalize by the mean and index by id2pos, as for other weights.
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
        """Return weights removing protein, class, and species positive-rate priors.

        Use iterative proportional fitting (raking) over LTPProtein, lipid class,
        and FullIdentityOfLipid. Match each key's weighted rate to the train-wide
        rate, not 0.5, preserving class balance. Leave two-key joint structure intact.
        Single-label keys cannot be balanced; keep their weights and print the count.
        Normalize by the mean and index by id2pos.
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

    # Cache lifecycle: warm per-sample caches before worker forks, then release sources.
    def warm_caches(self, csv=None):
        """Build needed protein graphs and lipid encodings before worker forks.

        Workers then share warm caches. Warming makes no random draws; skip only
        the isomer-graph per-access draw path inside make_graph_lipid.
        Return each cache's entry count for reporting.
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

        # Keep raw tensors for unwarmed isomer-graph draws (warm_caches).
        # Other configurations can release them.
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

    # Per-sample serving
    
    # Per-sample serving reads artifacts built during construction.
    # __iter__ sets split flags/tensors once per run, not per epoch.
    # preassembled_loader.py uses only this phase. For --eval_average_candidates,
    # _expand_candidate_rows prepares inputs; training/candidate_averaging.py
    # combines output predictions.
    def len(self):
        # TODO: clarify whether length counts pairs or structures.
        return len(self.csv)

    def _weight_positions(self, pair_ids):
        """Return each pair_id's weight position, or -1 outside training.

        Binary-search sorted train pair IDs, equivalent to id2pos.get(pair_id, -1).
        Validation/test -1 would index the last weight; losses use these only in train.
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
        # --lipid_class_targets uses training rows only: positive if the protein
        # binds any species in this head-group class.
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
        # Flat values and offsets for 1-37 candidates per row;
        # present only with --chem_prior/--pocket_compat_prior.
        self._frozen_prior_tensor, self._frozen_prior_offsets = _ragged_tensor(
            self.csv["_frozen_prior"] if "_frozen_prior" in self.csv.columns else None
        )
        # Heads and encoders share full_catalog_order(config), one column per token.
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
        """Expand evaluation to one row per candidate, carrying its candidate index.

        new_train averages predictions per pair before thresholding.
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
        """Return candidate indices for averaged evaluation, limited by the cap.

        If capped, spread indices evenly including both ends; a prefix would favor
        the row's own annotation. A zero or unreached cap includes all candidates.
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
        # Use residue subsampling and lipid_random_choice only in training.
        # Validation/test use the first candidate, keeping checkpoint selection fixed.
        # Disable sample caching to preserve draws; retain protein/lipid caches.
        train_dataset._use_lipid_class_targets = bool(
            self.config.lipid_class_targets
        )
        train_dataset._draw_lipid_candidate = bool(self.config.lipid_random_choice)
        train_dataset._augment_residues = bool(
            self.config.protein_residue_subsample
        )
        if train_dataset._augment_residues or train_dataset._draw_lipid_candidate:
            train_dataset._sample_cache_enabled = False
        # Carry protein_id for train ranking loss, validation save_dynamics/ranking
        # loss (to keep losses comparable), and run_test per-protein metrics.
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
        """Set the epoch for residue subsampling; called once per training epoch.

        Seed masks by (run seed, pair_id, epoch), independent of batch order/workers.
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
        # Key shared sample caches by pair_id (plus expanded candidate), not split-local idx.
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
        """Encode row idx as candidate_index, or use its fixed encoding for None.

        This is get() after the draw. preassembled_loader.py builds each candidate
        once and replays only the draw per access.
        """
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
            # No protein graph for DeepCLIP (lipid input) or catalog-only descriptors.
            # Keep labels, group-DRO family one-hot, and finish_sample identifiers.
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
            # No edge_index/liplab is read here; complete_graph_edge_index builds on demand.
            lipid_kwargs = {
                "x": lipid_enc,
            }
            if self.config.lipid_fragments_mask:
                lipid_kwargs["lipid_batch"] = lipid_batch
            lipid_graph = Data(**lipid_kwargs)

        return protein_graph, lipid_graph


# finish_sample outputs by configuration:
# protein_graph: full x/edge_index/edge_attr/bury/plm/pocket/... normally;
#   label inter + family (+ optional protein_tokens) for --deepclip or dh/mlp.
# lipid_graph: 768-wide embedding normally; x/edge_index/edge_attr/liplab/chain_rank
#   atom graph for --lipid_graph_isomers; empty Data for dh/mlp, overriding isomers.
# Attach descriptor_catalog_input independently when --descriptor_heads,
# --protein_descriptors, --lipid_descriptors, or --deepclip_protein_gate is set,
# including alongside real graphs.

