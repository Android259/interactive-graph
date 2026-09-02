#!/usr/bin/env python3
"""Shared, data-closed utilities for the two-axis non-neural baselines.

The functions in this module deliberately consume only the interaction table, the
compact isomeric Tanimoto artefacts, and the already generated pocket graphs.  They do
not download annotations, structures, or assays, and they never modify the data tree.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

from dataloader.dataset_source import interaction_csv_path
from dataloader.sampler import lipid_class_series, lipid_classes_for_holdout
from preprocessing.audit_lipid_identity_by_smiles import features as smiles_features

try:
    from rdkit import Chem
except ModuleNotFoundError:  # pragma: no cover - project environments include RDKit
    Chem = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
# The canonical, deduplicated interaction table (dataloader.dataset_source is the single
# source of truth for which file that is) -- every artefact indexed by row position
# (pair_id, the compact Tanimoto arrays) is built against this exact file.
DEFAULT_CSV = Path(interaction_csv_path(str(PROJECT_ROOT / "data")))
DEFAULT_GRAPHS = PROJECT_ROOT / "data" / "graphs"

POCKET13_NAMES = (
    "pocket_residue_share",
    "pocket_sasa_share",
    "pocket_volume_per_sasa",
    "pocket_extent",
    "pocket_elongation",
    "pocket_flatness",
    "ev14_q50",
    "buriedness_q50",
    "depth_q10",
    "apolar_sasa_share",
    "aromatic_share",
    "hydropathy_core",
    "hydropathy_rim",
)

# The added values are deliberately simple shares over the same pocket residues the
# model already sees.  They capture the charged/polar part of head-group recognition
# absent from the existing shape/hydropathy descriptor without adding a new source.
POCKET_CHEMISTRY_NAMES = (
    "basic_share_core",
    "basic_share_rim",
    "acidic_share_core",
    "acidic_share_rim",
    "polar_share_core",
    "polar_share_rim",
    "hbond_donor_share_core",
    "hbond_donor_share_rim",
    "hbond_acceptor_share_core",
    "hbond_acceptor_share_rim",
)
POCKET23_NAMES = POCKET13_NAMES + POCKET_CHEMISTRY_NAMES

RESIDUE_ORDER = "A R N D C Q E G H I L K M F P S T W Y V".split()
KYTE_DOOLITTLE = np.array(
    [
        1.8,
        -4.5,
        -3.5,
        -3.5,
        2.5,
        -3.5,
        -3.5,
        -0.4,
        -3.2,
        4.5,
        3.8,
        -3.9,
        1.9,
        2.8,
        -1.6,
        -0.8,
        -0.7,
        -0.9,
        -1.3,
        4.2,
    ]
)
AROMATIC = {"F", "W", "Y"}
BASIC = {"R", "K", "H"}
ACIDIC = {"D", "E"}
POLAR = {"N", "Q", "S", "T", "Y", "C"}
HBOND_DONOR = {"R", "K", "H", "N", "Q", "S", "T", "Y", "W", "C"}
HBOND_ACCEPTOR = {"D", "E", "H", "N", "Q", "S", "T", "Y", "C"}


def read_interactions(csv_path: Path | str = DEFAULT_CSV) -> pd.DataFrame:
    """Read the immutable source table and attach its stable original row id."""
    table = pd.read_csv(csv_path)
    table = table.copy()
    table["pair_id"] = table.index.astype(int)
    return table


def csv_classes(table: pd.DataFrame) -> pd.Series:
    """Canonical full-name head-group class, matching the active dataloader."""
    return lipid_class_series(table)


def raw_double_cold_pool(
    table: pd.DataFrame, family: str, share: float
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[str, ...]]:
    """Return all P-vs-U rows of one two-axis held-out block, without sampling.

    The class choice is the existing project rule.  Train removes the held protein
    family and held lipid classes globally.  The reported pool contains exactly the
    intersection: the unseen family *and* unseen head-group classes.
    """
    held_classes = tuple(lipid_classes_for_holdout(table, family, share)[0])
    classes = csv_classes(table).str.lower()
    held = {name.lower() for name in held_classes}
    train = table[
        (table["ProteinDomain"].str.lower() != family.lower()) & ~classes.isin(held)
    ].copy()
    evaluation = table[
        (table["ProteinDomain"].str.lower() == family.lower()) & classes.isin(held)
    ].copy()
    if train.empty or evaluation.empty:
        raise ValueError(f"{family}: empty train or held-out block")
    return train, evaluation, held_classes


def raw_single_cold_pool(
    table: pd.DataFrame, family: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return all P-vs-U rows of a protein-only cold split (parity with --excluded_groups
    without --double_coldsplit): only the protein family is held out, every lipid class
    stays available in training.
    """
    domain = table["ProteinDomain"].str.lower()
    train = table[domain != family.lower()].copy()
    evaluation = table[domain == family.lower()].copy()
    if train.empty or evaluation.empty:
        raise ValueError(f"{family}: empty train or held-out block")
    return train, evaluation


def split_held_pairs(
    held: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a held pool by pair, keeping duplicate assay rows together.

    There are 98 repeated protein--lipid pairs under different `Screen` values.  A
    row-wise split would put the same pair in validation and test; the pair-level split
    avoids that leakage while retaining all Screen rows in the relevant half.
    """
    pairs = held[["LTPProtein", "FullIdentityOfLipid"]].drop_duplicates()
    valid_pairs = pairs.sample(frac=0.5, random_state=seed)
    valid_index = pd.MultiIndex.from_frame(valid_pairs)
    held_index = pd.MultiIndex.from_frame(held[["LTPProtein", "FullIdentityOfLipid"]])
    in_valid = held_index.isin(valid_index)
    return held.loc[in_valid].copy(), held.loc[~in_valid].copy()


def aggregate_pair_labels(table: pd.DataFrame) -> pd.DataFrame:
    """Collapse duplicate assay rows into a complete protein-by-lipid P-vs-U matrix.

    `Interaction=0` is unlabelled rather than a confirmed negative.  A duplicate pair
    is therefore positive whenever either existing screen observed a positive.  Screen
    remains available in the separate row-level diagnostic.
    """
    labels = table.groupby(["LTPProtein", "FullIdentityOfLipid"], sort=True)["Interaction"].max()
    matrix = labels.unstack("FullIdentityOfLipid")
    if matrix.isna().any().any():
        missing = int(matrix.isna().sum().sum())
        raise ValueError(
            f"training rectangle is incomplete ({missing} missing protein-lipid cells); "
            "KronRLS must not silently treat missing assays as unlabelled"
        )
    return matrix.astype(float)


def auc_p_vs_u(truth: np.ndarray | pd.Series, scores: np.ndarray | pd.Series) -> float:
    """Tie-aware rank AUC for observed positives versus unlabelled rows."""
    truth = np.asarray(truth, dtype=int)
    scores = np.asarray(scores, dtype=float)
    positive_count = int(truth.sum())
    negative_count = len(truth) - positive_count
    if positive_count == 0 or negative_count == 0:
        return float("nan")
    ranks = pd.Series(scores).rank(method="average").to_numpy()
    return float(
        (ranks[truth == 1].sum() - positive_count * (positive_count + 1) / 2)
        / (positive_count * negative_count)
    )


def _pocket_mask(nodes: pd.DataFrame, pocket_path: Path) -> np.ndarray:
    """Pocket mask with the same B-factor and side-chain convention as the loader."""
    from analysis.pocket_shape_descriptors import read_pocket_atoms

    _, pocket_residues, _ = read_pocket_atoms(pocket_path)
    keys = [
        str(int(value)) if float(value).is_integer() else str(value)
        for value in nodes["ID_resSeq"]
    ]
    mask = np.asarray([residue in pocket_residues for residue in keys], dtype=bool)
    if not mask.any():
        raise ValueError(f"{pocket_path}: no pocket residues match coarse_graph_nodes.csv")
    return mask


def _shape_values(pocket_path: Path) -> tuple[float, float, float]:
    from analysis.pocket_shape_descriptors import read_pocket_atoms, shape_from_coordinates

    coordinates, _, _ = read_pocket_atoms(pocket_path)
    shape = shape_from_coordinates(coordinates)
    if shape is None:
        return 0.0, 0.0, 0.0
    return shape["pocket_extent"], shape["pocket_elongation"], shape["pocket_flatness"]


def _share(residue_letters: np.ndarray, allowed: set[str]) -> float:
    return float(np.isin(residue_letters, list(allowed)).mean())


def protein_pocket_features(
    proteins: list[str] | tuple[str, ...], graphs: Path | str = DEFAULT_GRAPHS
) -> pd.DataFrame:
    """Build pocket13 and its residue-chemistry extension from existing graph files."""
    rows = []
    for protein in proteins:
        protein_dir = Path(graphs) / str(protein)
        nodes_path = protein_dir / "coarse_graph_nodes.csv"
        pocket_path = protein_dir / "pocketness.pdb"
        if not nodes_path.is_file() or not pocket_path.is_file():
            raise FileNotFoundError(f"missing existing graph artefacts for {protein}: {protein_dir}")
        nodes = pd.read_csv(nodes_path)
        mask = _pocket_mask(nodes, pocket_path)
        site = nodes.loc[mask]
        residue_types = site["residue_type"].to_numpy(dtype=int)
        residue_letters = np.asarray([RESIDUE_ORDER[index] for index in residue_types])
        hydropathy = KYTE_DOOLITTLE[residue_types]
        aromatic = np.isin(residue_letters, list(AROMATIC))
        sasa = site["residue_sas_area"].to_numpy(dtype=float)
        pocket_sasa = float(sasa.sum())
        burial = site["residue_mean_buriedness"].to_numpy(dtype=float)
        core = burial >= np.median(burial)
        rim = ~core
        if not rim.any():
            rim = np.ones(len(site), dtype=bool)
        extent, elongation, flatness = _shape_values(pocket_path)
        row = {
            "LTPProtein": protein,
            "pocket_residue_share": len(site) / max(len(nodes), 1),
            "pocket_sasa_share": pocket_sasa
            / max(float(nodes["residue_sas_area"].sum()), 1e-9),
            "pocket_volume_per_sasa": float(site["residue_volume"].sum())
            / max(pocket_sasa, 1e-9),
            "pocket_extent": extent,
            "pocket_elongation": elongation,
            "pocket_flatness": flatness,
            "ev14_q50": float(np.median(site["residue_mean_ev14"].to_numpy(dtype=float))),
            "buriedness_q50": float(np.median(burial)),
            "depth_q10": float(
                np.percentile(site["residue_mean_voromqa_depth"].to_numpy(dtype=float), 10)
            ),
            "apolar_sasa_share": float(sasa[hydropathy > 0].sum() / max(pocket_sasa, 1e-9)),
            "aromatic_share": float(aromatic.mean()),
            "hydropathy_core": float(hydropathy[core].mean()),
            "hydropathy_rim": float(hydropathy[rim].mean()),
        }
        for name, allowed in (
            ("basic", BASIC),
            ("acidic", ACIDIC),
            ("polar", POLAR),
            ("hbond_donor", HBOND_DONOR),
            ("hbond_acceptor", HBOND_ACCEPTOR),
        ):
            row[f"{name}_share_core"] = _share(residue_letters[core], allowed)
            row[f"{name}_share_rim"] = _share(residue_letters[rim], allowed)
        rows.append(row)
    return pd.DataFrame(rows).set_index("LTPProtein").loc[list(proteins)]


def protein_features_for_kernel(
    table: pd.DataFrame, kernel: str, graphs: Path | str = DEFAULT_GRAPHS
) -> pd.DataFrame:
    """Select the canonical 13 or 13+10 data-closed pocket descriptor set."""
    proteins = sorted(table["LTPProtein"].unique())
    features = protein_pocket_features(proteins, graphs)
    if kernel == "pocket13":
        return features.loc[:, POCKET13_NAMES]
    if kernel == "pocket23":
        return features.loc[:, POCKET23_NAMES]
    raise ValueError(f"unknown protein kernel {kernel!r}; expected pocket13 or pocket23")


def _candidate_smiles(value: object) -> list[str]:
    return [part.strip() for part in str(value).split(";") if part.strip()]


def _chain_composition(chain_fragments: object, lipid_name: object) -> tuple[float, float, float, float, float]:
    """Count tails/length/unsaturation from existing ChainFragments, then Lipid text."""
    fragments = str(chain_fragments) if pd.notna(chain_fragments) else ""
    pairs = re.findall(r"(\d+)\s*:\s*(\d+)", fragments)
    if not pairs:
        pairs = re.findall(r"(?:[A-Za-z*\-]+)?(\d+)\s*:\s*(\d+)", str(lipid_name))
    values = [(float(carbons), float(double_bonds)) for carbons, double_bonds in pairs]
    if not values:
        return (np.nan, np.nan, np.nan, np.nan, np.nan)
    carbons = np.asarray([value[0] for value in values])
    unsaturation = np.asarray([value[1] for value in values])
    return (
        float(len(values)),
        float(carbons.sum()),
        float(carbons.mean()),
        float(carbons.max()),
        float(unsaturation.sum()),
    )


def _candidate_explicit_features(smiles: str) -> dict[str, float]:
    parsed = smiles_features(smiles)
    mol = Chem.MolFromSmiles(smiles) if Chem is not None else None
    formal_charge = 0.0
    positive_atoms = 0.0
    negative_atoms = 0.0
    carbon_double_bonds = np.nan
    if mol is not None:
        charges = [atom.GetFormalCharge() for atom in mol.GetAtoms()]
        formal_charge = float(sum(charges))
        positive_atoms = float(sum(charge > 0 for charge in charges))
        negative_atoms = float(sum(charge < 0 for charge in charges))
        carbon_double_bonds = float(
            sum(
                bond.GetBondType() == Chem.BondType.DOUBLE
                and bond.GetBeginAtom().GetAtomicNum() == 6
                and bond.GetEndAtom().GetAtomicNum() == 6
                for bond in mol.GetBonds()
            )
        )
    ether_tail_count = max(
        0.0,
        float(parsed["tail_count"])
        - float(parsed["ester_count"])
        - float(bool(parsed["amide_present"])),
    )
    return {
        "formal_charge": formal_charge,
        "positive_atom_count": positive_atoms,
        "negative_atom_count": negative_atoms,
        "phosphate_count": float(parsed["phosphate_count"]),
        "glycerol_backbone": float(bool(parsed["glycerol_backbone_present"])),
        "sphingoid_backbone": float(bool(parsed["sphingoid_base_present"])),
        "tail_count": float(parsed["tail_count"]),
        "ester_tail_count": float(parsed["ester_count"]),
        "ether_tail_count": ether_tail_count,
        "amide_tail": float(bool(parsed["amide_present"])),
        "sugar_ring_count": float(parsed["sugar_ring_count"]),
        "sulfate_present": float(bool(parsed["sulfate_present"])),
        "carbon_count": float(parsed["carbon_count"]),
        "carbon_double_bond_count": carbon_double_bonds,
    }


def explicit_lipid_features(table: pd.DataFrame) -> pd.DataFrame:
    """Interpretable lipid features, derived only from fields already in the CSV.

    Head-group is one-hot encoded from the table's canonical full-name class.  Chemical
    counts are medians across the documented candidate isomers, while acyl composition
    uses ChainFragments when present.  Thus a candidate enumeration cannot turn into an
    arbitrary first-isomer choice.
    """
    records = []
    classes = csv_classes(table)
    species_rows = table.assign(_lipid_class=classes).drop_duplicates("FullIdentityOfLipid")
    all_classes = sorted(classes.unique())
    for _, row in species_rows.iterrows():
        candidates = [_candidate_explicit_features(smiles) for smiles in _candidate_smiles(row["SmileGlobal"])]
        if not candidates:
            raise ValueError(f"{row['FullIdentityOfLipid']}: empty SmileGlobal candidate set")
        candidate_table = pd.DataFrame(candidates)
        values = candidate_table.median(numeric_only=True).to_dict()
        chain_count, total_carbon, mean_carbon, max_carbon, total_unsaturation = _chain_composition(
            row.get("ChainFragments", ""), row.get("Lipid", "")
        )
        if not np.isfinite(chain_count):
            chain_count = values["tail_count"]
        if not np.isfinite(total_carbon):
            total_carbon = values["carbon_count"]
        if not np.isfinite(mean_carbon):
            mean_carbon = total_carbon / max(chain_count, 1.0)
        if not np.isfinite(max_carbon):
            max_carbon = mean_carbon
        if not np.isfinite(total_unsaturation):
            total_unsaturation = values["carbon_double_bond_count"]
        values.update(
            {
                "chain_count": chain_count,
                "total_chain_carbons": total_carbon,
                "mean_chain_carbons": mean_carbon,
                "max_chain_carbons": max_carbon,
                "total_unsaturation": total_unsaturation,
            }
        )
        values["FullIdentityOfLipid"] = row["FullIdentityOfLipid"]
        lipid_class = row["_lipid_class"]
        for name in all_classes:
            values[f"headgroup::{name}"] = float(lipid_class == name)
        records.append(values)
    return pd.DataFrame(records).set_index("FullIdentityOfLipid").sort_index()


def standardize_from_train(
    features: pd.DataFrame, train_names: list[str] | tuple[str, ...]
) -> pd.DataFrame:
    """Standardize only by training objects; constants remain zero."""
    train = features.loc[list(train_names)]
    mean = train.mean(axis=0)
    scale = train.std(axis=0, ddof=0).replace(0.0, 1.0)
    return (features - mean) / scale


def rbf_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Unit-diagonal RBF kernel with train-only z-scoring and fixed gamma=1/d."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    squared_distance = ((left[:, None, :] - right[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-squared_distance / max(left.shape[1], 1))


def linear_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Train-only z-scored dot product. A cheaper alternative to `rbf_kernel` for
    feature vectors where scale, not just direction, carries information."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    return left @ right.T


def cosine_kernel(
    features: pd.DataFrame,
    left_names: list[str] | tuple[str, ...],
    right_names: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    """Train-only z-scored cosine similarity. Suited to embedding-style vectors (e.g. a
    user-supplied protein language model pooling) where only direction should count."""
    scaled = standardize_from_train(features, train_names)
    left = scaled.loc[list(left_names)].to_numpy(dtype=float)
    right = scaled.loc[list(right_names)].to_numpy(dtype=float)
    left = left / np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-12)
    right = right / np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-12)
    return left @ right.T


KERNEL_FUNCTIONS = {"rbf": rbf_kernel, "linear": linear_kernel, "cosine": cosine_kernel}


def _feature_kernel(
    kernel_type: str,
    features: pd.DataFrame,
    entities: list[str],
    train_names: list[str] | tuple[str, ...],
) -> np.ndarray:
    try:
        function = KERNEL_FUNCTIONS[kernel_type]
    except KeyError:
        raise ValueError(
            f"unknown kernel_type {kernel_type!r}; expected one of {sorted(KERNEL_FUNCTIONS)}"
        )
    return function(features, entities, entities, train_names)


def load_feature_table(path: Path | str, index_name: str) -> pd.DataFrame:
    """Arbitrary externally supplied entity vectors: first CSV column is the entity id
    (must match `LTPProtein` / `FullIdentityOfLipid` values exactly), the rest are
    numeric features of any kind -- there is no fixed schema here by design."""
    table = pd.read_csv(path)
    id_column = table.columns[0]
    table = table.set_index(id_column)
    table.index = table.index.astype(str)
    table.index.name = index_name
    numeric = table.apply(pd.to_numeric, errors="coerce")
    bad = numeric.index[numeric.isna().any(axis=1)]
    if len(bad):
        raise ValueError(f"{path}: non-numeric or missing feature values for {list(bad)}")
    return numeric


def load_precomputed_kernel(
    path: Path | str, names_path: Path | str
) -> tuple[np.ndarray, dict[str, int]]:
    """A user-supplied square similarity/kernel matrix (e.g. an ESM3-embedding cosine
    matrix, or any other precomputed measure) used as-is, without recomputing it from
    feature vectors. `names_path` lists one entity name per line, in the matrix's row
    and column order."""
    matrix = np.load(path).astype(np.float64)
    names = [line.strip() for line in Path(names_path).read_text().splitlines() if line.strip()]
    if matrix.shape != (len(names), len(names)):
        raise ValueError(
            f"{path}: matrix shape {matrix.shape} does not match {len(names)} names in {names_path}"
        )
    return matrix, {name: position for position, name in enumerate(names)}


def _kernel_from_index(
    matrix: np.ndarray, index: dict[str, int], entities: list[str], source: str
) -> np.ndarray:
    missing = sorted(set(entities) - set(index))
    if missing:
        raise ValueError(f"{source} is missing entities: {missing}")
    positions = [index[name] for name in entities]
    return matrix[np.ix_(positions, positions)]


def build_protein_kernel(
    kind: str,
    entities: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
    graphs: Path | str = DEFAULT_GRAPHS,
    kernel_type: str = "rbf",
    descriptor_names: list[str] | tuple[str, ...] | None = None,
    features_path: Path | str | None = None,
    kernel_path: Path | str | None = None,
    names_path: Path | str | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build a protein x protein kernel over `entities`, standardized by `train_names`
    only. `kind` selects the feature source:

    - "pocket13" / "pocket23": the full 13- or 23-name pocket-shape descriptor set.
    - "pocket_subset": the same pocket descriptors, restricted to `descriptor_names`
      (any subset of POCKET23_NAMES) -- use this to match a network run's own
      `--pocket_descriptor_names` exactly, e.g. the project's "protgeom8" set.
    - "custom_features": any vectors of your own (`features_path`, see
      `load_feature_table`), turned into a kernel via `kernel_type`.
    - "custom_kernel": a precomputed similarity/kernel matrix of your own
      (`kernel_path` + `names_path`, see `load_precomputed_kernel`), used directly.
    """
    entities = list(entities)
    if kind in ("pocket13", "pocket23"):
        features = protein_pocket_features(entities, graphs)
        names = POCKET13_NAMES if kind == "pocket13" else POCKET23_NAMES
        kernel = _feature_kernel(kernel_type, features.loc[:, names], entities, train_names)
    elif kind == "pocket_subset":
        if not descriptor_names:
            raise ValueError("descriptor_names is required for protein_kernel=pocket_subset")
        unknown = sorted(set(descriptor_names) - set(POCKET23_NAMES))
        if unknown:
            raise ValueError(f"unknown pocket descriptor names: {unknown}")
        features = protein_pocket_features(entities, graphs)
        kernel = _feature_kernel(
            kernel_type, features.loc[:, list(descriptor_names)], entities, train_names
        )
    elif kind == "custom_features":
        if features_path is None:
            raise ValueError("--protein_features is required for protein_kernel=custom_features")
        features = load_feature_table(features_path, index_name="LTPProtein")
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"{features_path} is missing proteins: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_kernel":
        if kernel_path is None or names_path is None:
            raise ValueError(
                "--protein_kernel_matrix and --protein_kernel_names are required "
                "for protein_kernel=custom_kernel"
            )
        matrix, index = load_precomputed_kernel(kernel_path, names_path)
        kernel = _kernel_from_index(matrix, index, entities, str(kernel_path))
    else:
        raise ValueError(
            f"unknown protein kernel {kind!r}; expected pocket13, pocket23, "
            "pocket_subset, custom_features, or custom_kernel"
        )
    return kernel, {name: position for position, name in enumerate(entities)}


def build_lipid_kernel(
    kind: str,
    table: pd.DataFrame,
    entities: list[str] | tuple[str, ...],
    train_names: list[str] | tuple[str, ...],
    kernel_type: str = "rbf",
    features_path: Path | str | None = None,
    kernel_path: Path | str | None = None,
    names_path: Path | str | None = None,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build a lipid x lipid kernel over `entities`, standardized by `train_names` only.
    `kind` selects the feature source:

    - "tanimoto": the existing Morgan-fingerprint species similarity. `table` MUST be
      the full, unfiltered, original-row-order interaction table (see
      `species_tanimoto_similarity` -- it is positionally aligned to the compact
      Tanimoto artefacts, not to any subset).
    - "explicit": the existing interpretable lipid descriptors, turned into a kernel
      via `kernel_type`.
    - "custom_features" / "custom_kernel": your own vectors or precomputed kernel, same
      contract as `build_protein_kernel`.
    """
    entities = list(entities)
    if kind == "tanimoto":
        similarity, index = species_tanimoto_similarity(table)
        kernel = _kernel_from_index(similarity.astype(float), index, entities, "tanimoto similarity")
    elif kind == "explicit":
        features = explicit_lipid_features(table)
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"explicit lipid features are missing: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_features":
        if features_path is None:
            raise ValueError("--lipid_features is required for lipid_kernel=custom_features")
        features = load_feature_table(features_path, index_name="FullIdentityOfLipid")
        missing = sorted(set(entities) - set(features.index))
        if missing:
            raise ValueError(f"{features_path} is missing lipids: {missing}")
        kernel = _feature_kernel(kernel_type, features, entities, train_names)
    elif kind == "custom_kernel":
        if kernel_path is None or names_path is None:
            raise ValueError(
                "--lipid_kernel_matrix and --lipid_kernel_names are required "
                "for lipid_kernel=custom_kernel"
            )
        matrix, index = load_precomputed_kernel(kernel_path, names_path)
        kernel = _kernel_from_index(matrix, index, entities, str(kernel_path))
    else:
        raise ValueError(
            f"unknown lipid kernel {kind!r}; expected tanimoto, explicit, "
            "custom_features, or custom_kernel"
        )
    return kernel, {name: position for position, name in enumerate(entities)}


def species_tanimoto_similarity(table: pd.DataFrame) -> tuple[np.ndarray, dict[str, int]]:
    """Species Tanimoto, max-reduced over the same candidate structures as the loader."""
    data_dir = PROJECT_ROOT / "data"
    matrix = np.load(data_dir / "Tanimoto_compact_isomeric_matrix_uint8.npy").astype(np.float32) / 255.0
    structure_index = np.load(data_dir / "Tanimoto_compact_isomeric_structure_index.npy")
    row_ids = np.load(data_dir / "Tanimoto_compact_isomeric_row_ids.npy")
    structures_of_row: dict[int, set[int]] = {}
    for row_id, structure in zip(row_ids, structure_index):
        structures_of_row.setdefault(int(row_id), set()).add(int(structure))
    structures_of_species: dict[str, set[int]] = {}
    for row_position, species in enumerate(table["FullIdentityOfLipid"]):
        structures_of_species.setdefault(species, set()).update(
            structures_of_row.get(row_position, set())
        )
    names = sorted(structures_of_species)
    index = {name: position for position, name in enumerate(names)}
    similarity = np.empty((len(names), len(names)), dtype=np.float32)
    for position, name in enumerate(names):
        source = matrix[sorted(structures_of_species[name]), :].max(axis=0)
        similarity[position] = [
            source[sorted(structures_of_species[other])].max() for other in names
        ]
    return similarity, index


def two_step_kronrls(
    protein_kernel: np.ndarray,
    lipid_kernel: np.ndarray,
    labels: np.ndarray,
    protein_lambda: float,
    lipid_lambda: float,
) -> np.ndarray:
    """Solve the regularized two-step KronRLS coefficient matrix.

    For a train label matrix Y, predictions are Kp_test,train @ A @
    Kl_train,test, with A = (Kp + λp I)^−1 Y (Kl + λl I)^−1.
    """
    if labels.shape != (protein_kernel.shape[0], lipid_kernel.shape[0]):
        raise ValueError("labels must align with the train protein and lipid kernels")
    left = np.linalg.solve(
        protein_kernel + protein_lambda * np.eye(len(protein_kernel)), labels
    )
    return np.linalg.solve(
        lipid_kernel + lipid_lambda * np.eye(len(lipid_kernel)), left.T
    ).T


def predict_kronrls(
    coefficients: np.ndarray,
    protein_kernel_query_train: np.ndarray,
    lipid_kernel_train_query: np.ndarray,
) -> np.ndarray:
    """Score (protein, lipid) pairs whose protein and/or lipid need not have been in
    training. `coefficients` is `two_step_kronrls`'s return value, `A = (Kp+lambda_p I)^-1
    Y (Kl+lambda_l I)^-1`. `protein_kernel_query_train` is `[n_query_proteins,
    n_train_proteins]`, `lipid_kernel_train_query` is `[n_train_lipids,
    n_query_lipids]`; querying exactly the training entities (i.e. passing the training
    kernels themselves) recovers the fitted training-block scores, `Kp @ A @ Kl`.
    """
    return protein_kernel_query_train @ coefficients @ lipid_kernel_train_query


def pair_prediction_frame(
    held: pd.DataFrame,
    protein_scores: np.ndarray,
    proteins: list[str],
    lipid_scores: np.ndarray,
    lipids: list[str],
) -> pd.DataFrame:
    """Map a score rectangle back to every original held-out assay row."""
    p_index = {name: position for position, name in enumerate(proteins)}
    l_index = {name: position for position, name in enumerate(lipids)}
    result = held.copy()
    result["score"] = [
        float(protein_scores[p_index[p], l_index[l]])
        for p, l in zip(result["LTPProtein"], result["FullIdentityOfLipid"])
    ]
    return result
