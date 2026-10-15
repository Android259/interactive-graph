#!/usr/bin/env python3

# Build a head-group-only Tanimoto artifact from the interaction table.
#
# The tail-cutting rule below is project-specific.
#
# Candidates come from build_tanimoto_compact.collect. Remove tails identified by
# _qualifying_tails (>=4 connected non-ring, non-aromatic carbons), retaining atoms
# bonded outside the carbon component. Compare distinct remaining structures with
# Morgan fingerprints and Tanimoto; retain indices back to candidates and table rows.
#
# Output under data/cache/tanimoto_headgroup/:
#   Tanimoto_headgroup_compact_matrix_uint8.npy      head groups x head groups
#   Tanimoto_headgroup_compact_structure_index.npy   candidate -> head-group row
#   Tanimoto_headgroup_compact_row_ids.npy           candidate -> interaction table row
#   Tanimoto_headgroup_compact.manifest.json         counts, head-group SMILES,
#                                                     source table size + mtime
#
# Usage:
#     python3 preprocessing/similarity/build_tanimoto_headgroup.py [--data-dir DIR] [--input CSV]
#                                                        [--isomeric]

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dataloader.dataset_source import INTERACTION_CSV
from preprocessing.compute_descriptors import _qualifying_tails
from preprocessing.similarity.build_tanimoto_compact import distinct_structures
from preprocessing.similarity.build_tanimoto_compact import collect, tanimoto_matrix


DEFAULT_DATA_DIR = Path("data")
PREFIX = "Tanimoto_headgroup_compact"
ISOMERIC_PREFIX = "Tanimoto_headgroup_compact_isomeric"
FORMAT_VERSION = 1


def head_group_smiles(smiles):
    """Remove qualifying tails; return unchanged SMILES if none exist.

    Return None for invalid input or an empty/unparsable remaining fragment.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    tails = _qualifying_tails(smiles)
    if not tails:
        return Chem.MolToSmiles(mol, canonical=True)

    carbon_set = {
        atom.GetIdx() for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic() and not atom.IsInRing()
    }

    def attached_outside(idx):
        return any(
            neighbour.GetIdx() not in carbon_set
            for neighbour in mol.GetAtomWithIdx(idx).GetNeighbors()
        )

    remove = set()
    for tail in tails:
        anchors = {atom for atom in tail["atoms"] if attached_outside(atom)}
        remove.update(atom for atom in tail["atoms"] if atom not in anchors)

    keep = [index for index in range(mol.GetNumAtoms()) if index not in remove]
    if not keep:
        return None
    fragment_smiles = Chem.MolFragmentToSmiles(mol, atomsToUse=keep, canonical=True)
    fragment = Chem.MolFromSmiles(fragment_smiles)
    if fragment is None or fragment.GetNumAtoms() == 0:
        return None
    return Chem.MolToSmiles(fragment, canonical=True)


def head_groups_for(smiles_list):
    """Extract head groups, reporting whole-structure fallbacks to preserve indices."""
    result = []
    fallbacks = 0
    for smiles in smiles_list:
        head = head_group_smiles(smiles)
        if head is None:
            head = smiles
            fallbacks += 1
        result.append(head)
    if fallbacks:
        print(
            f"warning: {fallbacks} structures had no head group left after the cut; "
            "kept the whole structure for those"
        )
    return result


def compact_paths(root_dir, isomeric=False):
    root_dir = Path(root_dir).resolve() / "cache" / "tanimoto_headgroup"
    prefix = ISOMERIC_PREFIX if isomeric else PREFIX
    return (
        root_dir / f"{prefix}_matrix_uint8.npy",
        root_dir / f"{prefix}_structure_index.npy",
        root_dir / f"{prefix}_row_ids.npy",
        root_dir / f"{prefix}.manifest.json",
    )


def write_compact(root_dir, matrix, structure_index, row_ids, source_csv, head_groups, isomeric=False):
    matrix_path, index_path, row_path, manifest_path = compact_paths(root_dir, isomeric=isomeric)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(matrix_path, matrix)
    np.save(index_path, structure_index)
    np.save(row_path, row_ids)
    source_csv = Path(source_csv)
    stat = source_csv.stat()
    manifest_path.write_text(
        json.dumps(
            {
                "format_version": FORMAT_VERSION,
                "isomeric": bool(isomeric),
                "head_groups": int(matrix.shape[0]),
                "candidates": int(row_ids.shape[0]),
                "rows": int(len(set(row_ids.tolist()))),
                "head_group_smiles": head_groups,
                "source": {
                    "path": source_csv.name,
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                },
            },
            indent=2,
        )
        + "\n"
    )
    return matrix_path, index_path, row_path, manifest_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument(
        "--isomeric",
        action="store_true",
        help="Match a run with --lipid_isomers; see build_tanimoto_compact.py",
    )
    args = parser.parse_args()
    RDLogger.DisableLog("rdApp.*")

    input_csv = args.input or (args.data_dir / INTERACTION_CSV)
    table = pd.read_csv(input_csv)
    print(f"input: {input_csv} ({len(table)} rows)")
    print(f"mode: {'isomeric' if args.isomeric else 'non-isomeric'}")

    smiles, row_ids = collect(table, isomeric=args.isomeric)
    print(f"candidates: {len(smiles)} over {len(set(row_ids.tolist()))} rows")

    # Cut each distinct structure once, then expand back to candidate order.
    whole_structures, whole_index = distinct_structures(smiles)
    print(f"distinct structures (whole molecule): {len(whole_structures)}")
    whole_heads = head_groups_for(whole_structures)
    heads = [whole_heads[index] for index in whole_index]

    structures, structure_index = distinct_structures(heads)
    print(f"distinct head groups: {len(structures)}")
    for head in structures:
        print(f"  {head}")

    print(
        f"head-group matrix: {len(structures)}x{len(structures)} uint8 "
        f"({len(structures) ** 2 / 2**20:.2f} MiB)"
    )
    matrix = tanimoto_matrix(structures)

    written = write_compact(
        args.data_dir, matrix, structure_index, row_ids, input_csv, structures,
        isomeric=args.isomeric,
    )
    for path in written:
        print(f"written: {path}")


if __name__ == "__main__":
    main()
