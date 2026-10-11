#!/usr/bin/env python3
"""DELETE THIS FILE WHEN THE PROJECT IS FINISHED (marked for deletion by the owner; it only
guards the descriptor loader refactor and is not part of the pipeline).

Do the loader's `_descpath_*` columns equal an independent recomputation?

Builds the dataset once from --descriptor_heads, then for chain / unsaturation / hbond /
heavy / extent recomputes each token from the raw per-candidate values with the plain
recipe -- z-score over the TRAIN candidates only; extent first rounded to
EXTENT_BINS quantile levels cut on TRAIN proteins -- and compares it with the
column Dataloader._compute_descriptors wrote on train, valid and test. Nothing is
written to disk: the descriptor feature cache is bypassed in both directions.

Run when _compute_descriptors changes. It also holds the numbers behind the removal of
the fixed-token descriptor path (the legacy `_desc_*` columns): on START / seed 15 its
chain, unsaturation, hbond, heavy and extent columns were bit-identical to these, its
occupancy and its raw aromatic_share / polar_share tokens were not.

    python3 analysis/probes/descriptor_catalog_columns_check.py [--seed=15] [--group=START]
"""
import os
import sys

import numpy as np
import pandas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))

from dataloader.Dataloader import EXTENT_BINS, PLIDataset  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.pocket_lipid_compatibility import (  # noqa: E402
    chain_lengths_by_row,
    coarsen_to_levels,
    pocket_extent_by_protein,
)
from preprocessing.compute_descriptors import as_arrays, descriptor_values_by_row  # noqa: E402
from read_configuration import read_configuration  # noqa: E402
from reproducibility import seed_everything  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data") + os.sep
TOKENS = "chain,unsaturation,hbond,heavy,extent"


def main():
    seed = next((int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--seed=")), 15)
    group = next((a.split("=")[1] for a in sys.argv[1:] if a.startswith("--group=")), "START")
    config = read_configuration([
        "x", f"--seed={seed}", f"--excluded_groups={group}", "--double_coldsplit",
        "--balanced_batches", "--balanced_proteins", f"--descriptor_heads={TOKENS}",
        "--descriptors_head",
    ])
    seed_everything(seed)
    PLIDataset._save_descriptor_features_cache = staticmethod(lambda path, columns: None)
    PLIDataset._load_descriptor_features_cache = staticmethod(lambda path: None)
    csv = pandas.read_csv(interaction_csv_path(DATA_DIR))
    train, valid, test = PLIDataset(
        root_dir=DATA_DIR, csv=csv, seed=seed, excluded_subgroups=config.excluded_subgroups,
        config=config, excluded_groups=config.excluded_groups,
    )

    raw = {
        "chain": as_arrays(chain_lengths_by_row(csv, False)),
        "unsaturation": as_arrays(descriptor_values_by_row(csv, "unsaturation", False)),
        "hbond": as_arrays(descriptor_values_by_row(csv, "hbond", False)),
        "heavy": as_arrays(descriptor_values_by_row(csv, "heavy_atoms", False)),
    }
    train_rows = train.csv["pair_id"].to_numpy()
    extent = csv["LTPProtein"].map(
        pocket_extent_by_protein(DATA_DIR, sorted(csv["LTPProtein"].unique()))
    ).to_numpy(dtype=float)
    edges = np.quantile(extent[train_rows], np.linspace(0, 1, EXTENT_BINS + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    coarse = coarsen_to_levels(extent, np.unique(edges))

    ok = True
    for token in TOKENS.split(","):
        if token == "extent":
            # One value per ROW, so its train statistics run over train rows, not over
            # train candidates.
            per_row = [np.full(len(raw["chain"][r]), coarse[r]) for r in range(len(csv))]
            mean, spread = coarse[train_rows].mean(), coarse[train_rows].std()
        else:
            per_row = [np.asarray(values, dtype=float) for values in raw[token]]
            flat = np.concatenate([per_row[r] for r in train_rows])
            mean, spread = flat.mean(), flat.std()
        for split, dataset in (("train", train), ("valid", valid), ("test", test)):
            frame = dataset.csv
            expected = np.concatenate([(per_row[r] - mean) / spread for r in frame["pair_id"]])
            got = np.concatenate([np.asarray(v, dtype=float) for v in frame[f"_descpath_{token}"]])
            # coarsen_to_levels returns float32 levels, so extent is exact only to ~1e-7.
            atol = 1e-6 if token == "extent" else 1e-12
            same = expected.shape == got.shape and np.allclose(expected, got, rtol=0, atol=atol)
            ok &= bool(same)
            print(f"  {split:5s} {token:13s} rows={len(frame):5d} match={same}")
    print("ALL MATCH" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
