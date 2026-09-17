#!/usr/bin/env python3

# Build a head-group-only Tanimoto artifact from the interaction table.
#
# Each candidate SMILES (same rule as build_tanimoto_matrix.collect: SmileGlobal
# unless it is "0", candidates split on ";", canonicalized, deduplicated per row)
# has its acyl chains cut off, keeping only the head group. A "tail" is exactly
# what pair_descriptors._qualifying_tails already calls one: a connected run of
# >=4 non-aromatic, non-ring carbons. Its outermost anchor atom -- the one bonded
# to something outside that carbon-only run, typically the ester/amide carbonyl
# carbon -- stays with the head group; only the carbons further down the chain
# are removed. That keeps the ester/amide oxygens attached instead of turning
# them into orphan atoms once their carbon neighbour is cut.
#
# Candidates that differ only in chain length or unsaturation collapse onto the
# same head-group structure, so this is stored the same way
# build_tanimoto_compact.py stores whole-structure Tanimoto: one row per DISTINCT
# structure (here, distinct head group) plus the index needed to expand back to
# per-candidate similarities, instead of one row per candidate instance.
#
# Output (same layout/dtypes as dataloader/tanimoto_compact.py's files, under a
# separate prefix so this is never confused with or read as whole-molecule data):
#   Tanimoto_headgroup_compact_matrix_uint8.npy      head groups x head groups
#   Tanimoto_headgroup_compact_structure_index.npy   candidate -> head-group row
#   Tanimoto_headgroup_compact_row_ids.npy           candidate -> interaction table row
#   Tanimoto_headgroup_compact.manifest.json         counts, head-group SMILES,
#                                                     source table size + mtime
#
# Usage:
#     python3 preprocessing/build_tanimoto_headgroup.py [--data-dir DIR] [--input CSV]
#                                                        [--isomeric]

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV
from dataloader.pair_descriptors import _qualifying_tails
from preprocessing.build_tanimoto_compact import distinct_structures
from preprocessing.build_tanimoto_matrix import collect, tanimoto_matrix


DEFAULT_DATA_DIR = Path("data")
PREFIX = "Tanimoto_headgroup_compact"
ISOMERIC_PREFIX = "Tanimoto_headgroup_compact_isomeric"
FORMAT_VERSION = 1


def head_group_smiles(smiles):
    """Canonical SMILES of ``smiles`` with every qualifying acyl tail cut off.

    A molecule with no qualifying tail (already just a head group, e.g. a sterol
    or a short-chain ligand) passes through unchanged. Returns None only when
    RDKit cannot parse ``smiles`` at all, or when the cut leaves nothing behind
    (a bare chain with no anchor atom to keep) -- distinct from "unchanged"
    because a caller must not silently treat "nothing left" as "no tail found".
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
    """Head-group SMILES for every entry, falling back to the whole structure
    when the cut leaves nothing (reported, never silently dropped: an empty
    fallback would misalign the index built from this list)."""
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
    root_dir = Path(root_dir).resolve()
    prefix = ISOMERIC_PREFIX if isomeric else PREFIX
    return (
        root_dir / f"{prefix}_matrix_uint8.npy",
        root_dir / f"{prefix}_structure_index.npy",
        root_dir / f"{prefix}_row_ids.npy",
        root_dir / f"{prefix}.manifest.json",
    )


def write_compact(root_dir, matrix, structure_index, row_ids, source_csv, head_groups, isomeric=False):
    matrix_path, index_path, row_path, manifest_path = compact_paths(root_dir, isomeric=isomeric)
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

    # Cut every DISTINCT whole structure once, then fan the result back out over
    # the full candidate list -- cheaper than re-cutting duplicate candidates.
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
