#!/usr/bin/env python3
from pathlib import Path
import hashlib

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem


DATA_DIR = Path(__file__).resolve().parent
INPUT_CSV = DATA_DIR / "Processed_Negative_Interaction_Without_Duplicates.csv"
OUTPUT_DIR = DATA_DIR / "lipid_graphs"
INDEX_CSV = OUTPUT_DIR / "lipid_graph_index.csv"


NODE_COLUMNS = [
    "atom_idx",
    "atomic_num",
    "formal_charge",
    "degree",
    "hybridization",
    "is_aromatic",
    "is_in_ring",
    "chiral_tag",
    "chirality_possible",
    "total_num_hs",
    "mass",
    "gasteiger_charge",
]

EDGE_COLUMNS = [
    "source",
    "target",
    "bond_type",
    "is_conjugated",
    "is_in_ring",
    "stereo",
    "bond_dir",
    "is_aromatic",
]


def iter_smiles(value):
    value = str(value)
    if value in ["", "0", "Empty", "NonConclusive", "nan"]:
        return
    if "//" in value or "\\\\" in value:
        value = value.replace("//", "/")
        value = value.replace("\\\\", "\\")
    for smiles in value.split(";"):
        smiles = smiles.strip()
        if smiles:
            yield smiles


def canonical_isomeric_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, None
    canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
    return canonical, mol


def graph_id_from_smiles(smiles):
    return hashlib.sha1(smiles.encode("utf-8")).hexdigest()[:16]


def atom_features(atom):
    charge = 0.0
    if atom.HasProp("_GasteigerCharge"):
        try:
            charge = float(atom.GetProp("_GasteigerCharge"))
        except ValueError:
            charge = 0.0
    if charge != charge:
        charge = 0.0

    return {
        "atom_idx": atom.GetIdx(),
        "atomic_num": atom.GetAtomicNum(),
        "formal_charge": atom.GetFormalCharge(),
        "degree": atom.GetDegree(),
        "hybridization": int(atom.GetHybridization()),
        "is_aromatic": int(atom.GetIsAromatic()),
        "is_in_ring": int(atom.IsInRing()),
        "chiral_tag": int(atom.GetChiralTag()),
        "chirality_possible": int(atom.HasProp("_ChiralityPossible")),
        "total_num_hs": atom.GetTotalNumHs(),
        "mass": atom.GetMass(),
        "gasteiger_charge": charge,
    }


def bond_features(source, target, bond):
    return {
        "source": source,
        "target": target,
        "bond_type": float(bond.GetBondTypeAsDouble()),
        "is_conjugated": int(bond.GetIsConjugated()),
        "is_in_ring": int(bond.IsInRing()),
        "stereo": int(bond.GetStereo()),
        "bond_dir": int(bond.GetBondDir()),
        "is_aromatic": int(bond.GetIsAromatic()),
    }


def write_lipid_graph(graph_dir, mol):
    AllChem.ComputeGasteigerCharges(mol)

    nodes = pd.DataFrame([atom_features(atom) for atom in mol.GetAtoms()])
    edges = []
    for bond in mol.GetBonds():
        begin = bond.GetBeginAtomIdx()
        end = bond.GetEndAtomIdx()
        edges.append(bond_features(begin, end, bond))
        edges.append(bond_features(end, begin, bond))

    graph_dir.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(graph_dir / "nodes.csv", columns=NODE_COLUMNS, index=False)
    pd.DataFrame(edges).to_csv(graph_dir / "edges.csv", columns=EDGE_COLUMNS, index=False)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_CSV)

    graph_rows = []
    seen = set()
    for column in ["SmileGlobal", "SmileFragment"]:
        for value in df[column].fillna(""):
            for smiles in iter_smiles(value):
                canonical, mol = canonical_isomeric_smiles(smiles)
                if canonical is None or canonical in seen:
                    continue
                seen.add(canonical)
                graph_id = graph_id_from_smiles(canonical)
                write_lipid_graph(OUTPUT_DIR / graph_id, mol)
                graph_rows.append({
                    "graph_id": graph_id,
                    "canonical_smiles": canonical,
                    "source_column": column,
                })

    pd.DataFrame(graph_rows).to_csv(INDEX_CSV, index=False)
    print(f"Saved lipid graphs: {len(graph_rows)}")
    print(f"Saved index: {INDEX_CSV}")


if __name__ == "__main__":
    main()
