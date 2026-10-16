"""Frozen, calibrated additive prior term(s) added to the logit in Final_Layer.

--chem_prior and --pocket_compat_prior are fit jointly on TRAIN LABELS ONLY
(fit_prior_calibration) and stored as the single column `_frozen_prior`.
"""

import numpy as np

from dataloader.chemistry_prior import (
    fit_prior_calibration,
    knn_scores,
    knn_scores_leave_one_row_out,
    species_similarity,
)
from dataloader.pocket_lipid_compatibility import raw_compatibility
from dataloader.ragged_tensors import candidate_column, ragged_rows


class FrozenPriorBuilder:
    def _raw_frozen_prior_columns(self, csv):
        """Return raw active priors as {name: (train, valid, test) arrays}.

        Used by _compute_frozen_prior for --chem_prior and --pocket_compat_prior.
        csv is the original table, not sampled_split: similarity and compatibility
        use its row positions. Address rows by pair_id, not split-frame indices.
        """
        columns = {}
        # chem_adversary requires chem_prior (ModelConfig.validate).
        if self.config.chem_prior:
            similarity, index = species_similarity(csv, self.ROOT_DIR)
            neighbours = self.config.chem_neighbours
            train = knn_scores_leave_one_row_out(self.csvtrain, similarity, index, neighbours)
            valid = (
                knn_scores(self.csvtrain, self.csvalidate["FullIdentityOfLipid"], similarity, index, neighbours)
                if not self.csvalidate.empty else np.array([], dtype=float)
            )
            test = (
                knn_scores(self.csvtrain, self.csvtest["FullIdentityOfLipid"], similarity, index, neighbours)
                if not self.csvtest.empty else np.array([], dtype=float)
            )
            columns["s_chem"] = (train, valid, test)
        if self.config.pocket_compat_prior:
            # No leave-one-out needed: raw_compatibility never reads Interaction.
            all_values, missing = raw_compatibility(
                csv, self.ROOT_DIR, self.config.lipid_isomers
            )
            train_rows = self._original_rows(self.csvtrain)
            missing_count = sum(int(row.sum()) for row in missing)
            if missing_count:
                train_values = np.concatenate(ragged_rows(all_values, train_rows))
                train_usable = train_values[~np.isnan(train_values)]
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

    def _compute_frozen_prior(self, raw_columns):
        """Jointly calibrate active s_chem and compatibility terms on training labels.

        Store them in _frozen_prior, which Final_Layer adds to the logit.
        Uses fit_prior_calibration for --chem_prior and --pocket_compat_prior.
        """
        wanted = [name for name in ("s_chem", "compat") if (
            (name == "s_chem" and self.config.chem_prior)
            or (name == "compat" and self.config.pocket_compat_prior)
        )]
        if not wanted:
            return
        # One entry per candidate of every row (s_chem is repeated over them); the fit uses
        # all of them with the row's label repeated.
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
