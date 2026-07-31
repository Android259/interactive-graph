#!/usr/bin/env python3

import argparse
from pathlib import Path

import pandas as pd

try:
    from rdkit import Chem
except ModuleNotFoundError:
    Chem = None


DEFAULT_INPUT = Path("data/Processed_dataset.csv")
DEFAULT_OUTPUT = Path("data/Processed_dataset_smiles_identity_audit.csv")
DEFAULT_MISMATCH_OUTPUT = Path("data/Processed_dataset_smiles_identity_mismatches.csv")
RULES_DOC = Path("preprocessing/lipid_identity_smiles_rules.md")
SMILES_COLUMNS = ["SmileGlobal", "SmileFragment"]


NAME_TO_CLASS = {
    "Sphingomyelin": "Sphingomyelin",
    "Ceramide phosphate": "Ceramide phosphate",
    "Sulfohexosyl ceramide": "SHexCer",
    "Dihexosyl ceramide": "Hex2Cer",
    "Hexosyl ceramide": "HexCer",
    "Ceramide": "Ceramide",
    "Cardiolipin": "Cardiolipin",
    "Bismonoacylglycerolphosphate": "BMP",
    "Phosphatidylcholine": "PC",
    ": Phosphatidylcholine": "PC",
    "Phosphatidylethanolamine": "PE",
    "Phosphatidylglycerol": "PG",
    "Phosphatidylinositol": "PI",
    "Phosphatidylserine": "PS",
    "Lysophosphatidylcholine": "LPC",
    "Lysophosphatidylethanolamine": "LPE",
    "Lysophosphatidylglycerol": "LPG",
    "Triacylglycerol": "TAG",
    "Diacylglycerol": "DAG",
    "Retinol": "Retinol",
}

FATTY_ACYL_NAMES = {
    "docosapentaenoate",
    "docosatetraenoate",
    "docosatrienoate",
    "eicosapentaenoate",
    "eicosatetraenoate",
    "eicosatrienoate",
    "heptadecenoate",
    "hexadecenoate",
    "nonadecenoate",
    "octadecadienoate",
    "octadecatrienoate",
    "octadecenoate",
    "octadecatrienol",
}

CARBOXYL_SMARTS = (
    Chem.MolFromSmarts("[CX3](=O)[OX1H0-,OX2H1]") if Chem is not None else None
)
CHOLINE_SMARTS = (
    Chem.MolFromSmarts("[OX2][CX4][CX4][N+](C)(C)C") if Chem is not None else None
)
ETHANOLAMINE_SMARTS = (
    Chem.MolFromSmarts("[OX2][CX4][CX4][NX3;!$([N+])]") if Chem is not None else None
)


def atom_has_double_oxygen(atom):
    for bond in atom.GetBonds():
        neighbor = bond.GetOtherAtom(atom)
        if neighbor.GetAtomicNum() == 8 and bond.GetBondType() == Chem.BondType.DOUBLE:
            return True
    return False


def atom_is_ester_carbonyl(atom):
    if atom.GetAtomicNum() != 6 or not atom_has_double_oxygen(atom):
        return False
    for oxygen in atom.GetNeighbors():
        if oxygen.GetAtomicNum() != 8:
            continue
        bond = atom.GetOwningMol().GetBondBetweenAtoms(atom.GetIdx(), oxygen.GetIdx())
        if bond.GetBondType() != Chem.BondType.SINGLE:
            continue
        if any(
            neighbor.GetAtomicNum() == 6 and neighbor.GetIdx() != atom.GetIdx()
            for neighbor in oxygen.GetNeighbors()
        ):
            return True
    return False


def count_rdkit_acyl_esters(mol):
    if mol is None:
        return None
    return sum(1 for atom in mol.GetAtoms() if atom_is_ester_carbonyl(atom))


def count_sugar_rings(mol):
    if mol is None:
        return None
    count = 0
    for ring in mol.GetRingInfo().AtomRings():
        ring_atoms = [mol.GetAtomWithIdx(index) for index in ring]
        oxygen_count = sum(atom.GetAtomicNum() == 8 for atom in ring_atoms)
        carbon_count = sum(atom.GetAtomicNum() == 6 for atom in ring_atoms)
        if len(ring) not in (5, 6) or oxygen_count != 1 or carbon_count < 4:
            continue

        ring_set = set(ring)
        hydroxyl_count = 0
        for atom in ring_atoms:
            if atom.GetAtomicNum() != 6:
                continue
            for neighbor in atom.GetNeighbors():
                if neighbor.GetIdx() not in ring_set and neighbor.GetAtomicNum() == 8:
                    hydroxyl_count += 1
        if hydroxyl_count >= 2:
            count += 1
    return count


def has_alcohol(mol):
    if mol is None:
        return False
    for oxygen in mol.GetAtoms():
        if oxygen.GetAtomicNum() != 8:
            continue
        if any(neighbor.GetAtomicNum() == 15 for neighbor in oxygen.GetNeighbors()):
            continue
        if any(atom_is_ester_carbonyl(neighbor) for neighbor in oxygen.GetNeighbors()):
            continue
        if any(neighbor.GetAtomicNum() == 6 for neighbor in oxygen.GetNeighbors()):
            return True
    return False


def count_carbon_double_bonds(mol):
    if mol is None:
        return None
    count = 0
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        begin = bond.GetBeginAtom()
        end = bond.GetEndAtom()
        if begin.GetAtomicNum() == 6 and end.GetAtomicNum() == 6:
            count += 1
    return count


def oxygen_tail_type(oxygen, glycerol_carbon):
    for neighbor in oxygen.GetNeighbors():
        if neighbor.GetIdx() == glycerol_carbon.GetIdx():
            continue
        if neighbor.GetAtomicNum() == 15:
            return "phosphate"
        if neighbor.GetAtomicNum() != 6:
            continue
        if atom_is_ester_carbonyl(neighbor):
            return "ester"
        return "ether"
    return None


def glycerol_layout_features(mol):
    if mol is None:
        return {
            "pg_tail_layout_present": False,
            "bmp_tail_layout_present": False,
            "rdkit_glycerol_backbone_present": False,
            "rdkit_glycerol_head_present": False,
            "rdkit_tail_count": None,
        }

    units_by_phosphate = {}
    all_tail_attachments = set()
    for center in mol.GetAtoms():
        if center.GetAtomicNum() != 6 or center.GetIsAromatic():
            continue

        carbon_neighbors = [
            neighbor
            for neighbor in center.GetNeighbors()
            if neighbor.GetAtomicNum() == 6 and not neighbor.GetIsAromatic()
        ]
        for left_index, left in enumerate(carbon_neighbors):
            for right in carbon_neighbors[left_index + 1 :]:
                glycerol_carbons = (left, center, right)
                if any(carbon.IsInRing() for carbon in glycerol_carbons):
                    continue
                if not all(
                    any(neighbor.GetAtomicNum() == 8 for neighbor in carbon.GetNeighbors())
                    for carbon in glycerol_carbons
                ):
                    continue

                phosphate_indices = set()
                acylated_carbons = set()
                ether_carbons = set()
                for carbon in glycerol_carbons:
                    for oxygen in carbon.GetNeighbors():
                        if oxygen.GetAtomicNum() != 8:
                            continue
                        tail_type = oxygen_tail_type(oxygen, carbon)
                        if tail_type == "phosphate":
                            for neighbor in oxygen.GetNeighbors():
                                if neighbor.GetAtomicNum() == 15:
                                    phosphate_indices.add(neighbor.GetIdx())
                        if tail_type == "ester":
                            acylated_carbons.add(carbon.GetIdx())
                            all_tail_attachments.add((carbon.GetIdx(), oxygen.GetIdx()))
                        if tail_type == "ether":
                            ether_carbons.add(carbon.GetIdx())
                            all_tail_attachments.add((carbon.GetIdx(), oxygen.GetIdx()))

                if not phosphate_indices:
                    continue

                unit_key = tuple(sorted(carbon.GetIdx() for carbon in glycerol_carbons))
                for phosphate_index in phosphate_indices:
                    units_by_phosphate.setdefault(phosphate_index, {})[unit_key] = (
                        len(acylated_carbons),
                        len(ether_carbons),
                    )

    pg_tail_layout_present = False
    bmp_tail_layout_present = False
    rdkit_glycerol_head_present = False
    for acyl_counts_by_unit in units_by_phosphate.values():
        tail_counts = [
            acyl_count + ether_count
            for acyl_count, ether_count in acyl_counts_by_unit.values()
        ]
        if 2 in tail_counts and 0 in tail_counts:
            pg_tail_layout_present = True
        if 0 in tail_counts:
            rdkit_glycerol_head_present = True
        if sum(tail_count == 1 for tail_count in tail_counts) >= 2:
            bmp_tail_layout_present = True

    return {
        "pg_tail_layout_present": pg_tail_layout_present,
        "bmp_tail_layout_present": bmp_tail_layout_present,
        "rdkit_glycerol_backbone_present": bool(units_by_phosphate),
        "rdkit_glycerol_head_present": rdkit_glycerol_head_present,
        "rdkit_tail_count": len(all_tail_attachments),
    }


def count_acyl_esters(smiles):
    count = 0
    start = 0
    while True:
        pos = smiles.find("OC(", start)
        if pos == -1:
            break
        window = smiles[pos : pos + 80]
        if ")=O" in window or "=O)" in window:
            count += 1
        start = pos + 3
    return count

def features(smiles):
    mol = Chem.MolFromSmiles(smiles) if Chem is not None else None
    glycerol_features = glycerol_layout_features(mol)
    phosphate_count = smiles.count("P(")
    rdkit_ester_count = count_rdkit_acyl_esters(mol)
    ester_count = rdkit_ester_count if rdkit_ester_count is not None else count_acyl_esters(smiles)
    ether_tail_count = sum(
        smiles.count(pattern) for pattern in ("COCCCC", "CO/C=C", "CO\\C=C")
    )
    amide_present = (
        "NC(" in smiles and ")=O" in smiles
    ) or "NC(=O)" in smiles
    amide_tail_count = 1 if amide_present else 0

    serine_present = (
        "C(O)(=O)" in smiles
        and "(N)" in smiles
        and "COP" in smiles
    ) or (
        "C(=O)O" in smiles
        and "(N)" in smiles
        and "COP" in smiles
    )
    choline_present = bool(
        mol is not None and CHOLINE_SMARTS is not None and mol.HasSubstructMatch(CHOLINE_SMARTS)
    ) or "OCC[N+](C)(C)C" in smiles
    ethanolamine_present = (
        bool(
            mol is not None
            and ETHANOLAMINE_SMARTS is not None
            and mol.HasSubstructMatch(ETHANOLAMINE_SMARTS)
        )
        or "OCCN" in smiles
    ) and not choline_present and not serine_present
    inositol_present = "[C@H]1" in smiles and "O1" not in smiles and smiles.count("(O)") >= 4
    glycerol_head_present = (
        glycerol_features["rdkit_glycerol_head_present"]
        or "(O)(CO)COP" in smiles
        or "OCC(O)CO" in smiles
    )
    sulfate_present = (
        "S(=O)(=O)" in smiles
        or "S(O)(=O)=O" in smiles
        or "S(=O)(O)=O" in smiles
    )
    rdkit_sugar_ring_count = count_sugar_rings(mol)
    sugar_ring_count = (
        rdkit_sugar_ring_count
        if rdkit_sugar_ring_count is not None
        else smiles.count("O1") + smiles.count("O2") + smiles.count("O3")
    )

    sphingoid_base_present = amide_present and (
        "[C@]([H])(O)" in smiles
        or "[C@@]([H])(O)" in smiles
        or "[C@H](O)" in smiles
        or "[C@@H](O)" in smiles
    )

    glycerol_backbone_count = smiles.count("[C@](") + smiles.count("[C@@](")
    glycerol_backbone_present = (
        glycerol_features["rdkit_glycerol_backbone_present"]
        or "COP" in smiles
        or "COC(" in smiles
        or "OC[C@]" in smiles
        or "[C@](CO" in smiles
        or "OC[C@@]" in smiles
    ) and not sphingoid_base_present

    free_oh_count = smiles.count("(O)")
    if smiles.startswith("OC"):
        free_oh_count += 1
    free_oh_count += smiles.count("CO)")
    free_oh_count += smiles.count("CO;")
    carboxyl_present = bool(
        mol is not None
        and CARBOXYL_SMARTS is not None
        and mol.HasSubstructMatch(CARBOXYL_SMARTS)
    ) or (
        "(=O)O" in smiles
        or "C(=O)O" in smiles
        or "C(O)(=O)" in smiles
        or "C(O)=O" in smiles
        or "C(=O)[O-]" in smiles
    )
    carbon_count = smiles.count("C")
    hydrocarbon_chain_present = carbon_count >= 8
    carbon_double_bond_count = count_carbon_double_bonds(mol)
    polyene_alcohol_present = (
        (carbon_double_bond_count if carbon_double_bond_count is not None else smiles.count("C=C")) >= 3
        and (has_alcohol(mol) or "(O)" in smiles)
        and "(=O)O" not in smiles
        and "C(O)=O" not in smiles
        and phosphate_count == 0
        and ester_count == 0
        and not amide_present
    )
    tail_count = (
        glycerol_features["rdkit_tail_count"] + amide_tail_count
        if glycerol_features["rdkit_tail_count"] is not None
        and glycerol_features["rdkit_tail_count"] > 0
        else ester_count + ether_tail_count + amide_tail_count
    )

    return {
        "amide_present": amide_present,
        "sphingoid_base_present": sphingoid_base_present,
        "phosphate_count": phosphate_count,
        "choline_present": choline_present,
        "sugar_ring_count": sugar_ring_count,
        "sulfate_present": sulfate_present,
        "glycerol_backbone_count": glycerol_backbone_count,
        "glycerol_backbone_present": glycerol_backbone_present,
        "tail_count": tail_count,
        "free_oh_count": free_oh_count,
        "ethanolamine_present": ethanolamine_present,
        "serine_present": serine_present,
        "inositol_present": inositol_present,
        "glycerol_head_present": glycerol_head_present,
        "pg_tail_layout_present": glycerol_features["pg_tail_layout_present"],
        "bmp_tail_layout_present": glycerol_features["bmp_tail_layout_present"],
        "ester_count": ester_count,
        "carboxyl_present": carboxyl_present,
        "carbon_count": carbon_count,
        "hydrocarbon_chain_present": hydrocarbon_chain_present,
        "polyene_alcohol_present": polyene_alcohol_present,
    }


def infer_class(f):
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["phosphate_count"] >= 1
        and f["choline_present"]
    ):
        return "Sphingomyelin"
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["phosphate_count"] >= 1
        and not f["choline_present"]
        and f["sugar_ring_count"] == 0
    ):
        return "Ceramide phosphate"
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["sugar_ring_count"] >= 1
        and f["sulfate_present"]
    ):
        return "SHexCer"
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["sugar_ring_count"] >= 2
        and not f["sulfate_present"]
    ):
        return "Hex2Cer"
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["sugar_ring_count"] == 1
        and not f["sulfate_present"]
        and f["phosphate_count"] == 0
    ):
        return "HexCer"
    if (
        f["amide_present"]
        and f["sphingoid_base_present"]
        and f["phosphate_count"] == 0
        and f["sugar_ring_count"] == 0
    ):
        return "Ceramide"
    if (
        f["phosphate_count"] == 2
        and f["glycerol_backbone_count"] >= 3
        and f["tail_count"] == 4
    ):
        return "Cardiolipin"
    if (
        f["phosphate_count"] == 1
        and f["bmp_tail_layout_present"]
        and f["free_oh_count"] >= 2
        and not f["choline_present"]
        and not f["ethanolamine_present"]
        and not f["serine_present"]
        and not f["inositol_present"]
    ):
        return "BMP"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["choline_present"]
        and f["tail_count"] == 2
        and not f["amide_present"]
    ):
        return "PC"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["ethanolamine_present"]
        and f["tail_count"] == 2
        and not f["amide_present"]
    ):
        return "PE"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["glycerol_head_present"]
        and f["pg_tail_layout_present"]
        and not f["amide_present"]
    ):
        return "PG"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["inositol_present"]
        and f["tail_count"] == 2
        and not f["amide_present"]
    ):
        return "PI"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["serine_present"]
        and f["tail_count"] == 2
        and not f["amide_present"]
    ):
        return "PS"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["choline_present"]
        and f["tail_count"] == 1
        and f["free_oh_count"] >= 1
        and not f["amide_present"]
    ):
        return "LPC"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["ethanolamine_present"]
        and f["tail_count"] == 1
        and f["free_oh_count"] >= 1
        and not f["amide_present"]
    ):
        return "LPE"
    if (
        f["phosphate_count"] == 1
        and f["glycerol_backbone_present"]
        and f["glycerol_head_present"]
        and f["tail_count"] == 1
        and f["free_oh_count"] >= 1
        and not f["amide_present"]
    ):
        return "LPG"
    if (
        f["phosphate_count"] == 0
        and f["glycerol_backbone_present"]
        and f["ester_count"] == 3
        and f["free_oh_count"] == 0
        and not f["amide_present"]
    ):
        return "TAG"
    if (
        f["phosphate_count"] == 0
        and f["glycerol_backbone_present"]
        and f["ester_count"] == 2
        and f["free_oh_count"] >= 1
        and not f["amide_present"]
    ):
        return "DAG"
    if (
        f["phosphate_count"] == 0
        and f["carboxyl_present"]
        and f["hydrocarbon_chain_present"]
        and not f["glycerol_backbone_present"]
        and not f["amide_present"]
        and f["sugar_ring_count"] == 0
    ):
        return "Fatty acyl"
    if (
        f["polyene_alcohol_present"]
        and f["phosphate_count"] == 0
        and f["ester_count"] == 0
        and not f["amide_present"]
        and not f["glycerol_backbone_present"]
    ):
        return "Retinol"
    return "Unknown"


def failed_conditions(f, expected_class):
    checks = {
        "Sphingomyelin": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("phosphate_count >= 1", f["phosphate_count"] >= 1),
            ("choline_present", f["choline_present"]),
        ],
        "Ceramide phosphate": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("phosphate_count >= 1", f["phosphate_count"] >= 1),
            ("NOT choline_present", not f["choline_present"]),
            ("sugar_ring_count == 0", f["sugar_ring_count"] == 0),
        ],
        "SHexCer": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("sugar_ring_count >= 1", f["sugar_ring_count"] >= 1),
            ("sulfate_present", f["sulfate_present"]),
        ],
        "Hex2Cer": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("sugar_ring_count >= 2", f["sugar_ring_count"] >= 2),
            ("NOT sulfate_present", not f["sulfate_present"]),
        ],
        "HexCer": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("sugar_ring_count == 1", f["sugar_ring_count"] == 1),
            ("NOT sulfate_present", not f["sulfate_present"]),
            ("phosphate_count == 0", f["phosphate_count"] == 0),
        ],
        "Ceramide": [
            ("amide_present", f["amide_present"]),
            ("sphingoid_base_present", f["sphingoid_base_present"]),
            ("phosphate_count == 0", f["phosphate_count"] == 0),
            ("sugar_ring_count == 0", f["sugar_ring_count"] == 0),
        ],
        "Cardiolipin": [
            ("phosphate_count == 2", f["phosphate_count"] == 2),
            ("glycerol_backbone_count >= 3", f["glycerol_backbone_count"] >= 3),
            ("tail_count == 4", f["tail_count"] == 4),
        ],
        "BMP": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("bmp_tail_layout_present", f["bmp_tail_layout_present"]),
            ("free_oh_count >= 2", f["free_oh_count"] >= 2),
            ("NOT choline_present", not f["choline_present"]),
            ("NOT ethanolamine_present", not f["ethanolamine_present"]),
            ("NOT serine_present", not f["serine_present"]),
            ("NOT inositol_present", not f["inositol_present"]),
        ],
        "PC": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("choline_present", f["choline_present"]),
            ("tail_count == 2", f["tail_count"] == 2),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "PE": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("ethanolamine_present", f["ethanolamine_present"]),
            ("tail_count == 2", f["tail_count"] == 2),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "PG": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("glycerol_head_present", f["glycerol_head_present"]),
            ("pg_tail_layout_present", f["pg_tail_layout_present"]),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "PI": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("inositol_present", f["inositol_present"]),
            ("tail_count == 2", f["tail_count"] == 2),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "PS": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("serine_present", f["serine_present"]),
            ("tail_count == 2", f["tail_count"] == 2),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "LPC": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("choline_present", f["choline_present"]),
            ("tail_count == 1", f["tail_count"] == 1),
            ("free_oh_count >= 1", f["free_oh_count"] >= 1),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "LPE": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("ethanolamine_present", f["ethanolamine_present"]),
            ("tail_count == 1", f["tail_count"] == 1),
            ("free_oh_count >= 1", f["free_oh_count"] >= 1),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "LPG": [
            ("phosphate_count == 1", f["phosphate_count"] == 1),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("glycerol_head_present", f["glycerol_head_present"]),
            ("tail_count == 1", f["tail_count"] == 1),
            ("free_oh_count >= 1", f["free_oh_count"] >= 1),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "TAG": [
            ("phosphate_count == 0", f["phosphate_count"] == 0),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("ester_count == 3", f["ester_count"] == 3),
            ("free_oh_count == 0", f["free_oh_count"] == 0),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "DAG": [
            ("phosphate_count == 0", f["phosphate_count"] == 0),
            ("glycerol_backbone_present", f["glycerol_backbone_present"]),
            ("ester_count == 2", f["ester_count"] == 2),
            ("free_oh_count >= 1", f["free_oh_count"] >= 1),
            ("NOT amide_present", not f["amide_present"]),
        ],
        "Fatty acyl": [
            ("phosphate_count == 0", f["phosphate_count"] == 0),
            ("carboxyl_present", f["carboxyl_present"]),
            ("hydrocarbon_chain_present", f["hydrocarbon_chain_present"]),
            ("NOT glycerol_backbone_present", not f["glycerol_backbone_present"]),
            ("NOT amide_present", not f["amide_present"]),
            ("sugar_ring_count == 0", f["sugar_ring_count"] == 0),
        ],
        "Retinol": [
            ("polyene_alcohol_present", f["polyene_alcohol_present"]),
            ("phosphate_count == 0", f["phosphate_count"] == 0),
            ("ester_count == 0", f["ester_count"] == 0),
            ("amide_present == false", not f["amide_present"]),
            ("glycerol_backbone_present == false", not f["glycerol_backbone_present"]),
        ],
    }
    if expected_class == "Unknown":
        return ""
    return "; ".join(name for name, passed in checks.get(expected_class, []) if not passed)


def expected_classes(full_identity):
    result = []
    for raw_part in str(full_identity).split(";"):
        name = raw_part.split("=>", 1)[0].split("(", 1)[0].strip()
        name = name.strip('"').strip()
        if name in NAME_TO_CLASS:
            result.append(NAME_TO_CLASS[name])
        elif name in FATTY_ACYL_NAMES:
            result.append("Fatty acyl")
        else:
            result.append("Unknown")
    return sorted(set(result))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Audit Processed_dataset lipid identities by classifying available "
            "SMILES with structural feature rules."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mismatch-output", type=Path, default=DEFAULT_MISMATCH_OUTPUT)
    args = parser.parse_args()

    table = pd.read_csv(args.input, sep=";")
    rows = []
    for row_index, row in table.iterrows():
        expected = expected_classes(row["FullIdentityOfLipid"])
        for column in SMILES_COLUMNS:
            if pd.isna(row[column]):
                continue
            smiles = str(row[column]).strip()
            if not smiles or smiles == "0" or smiles.lower() == "nan":
                continue
            f = features(smiles)
            inferred = infer_class(f)
            failed = []
            if inferred not in expected:
                for expected_class in expected:
                    failed_for_class = failed_conditions(f, expected_class)
                    if failed_for_class:
                        failed.append(f"{expected_class}: {failed_for_class}")
                if not failed:
                    failed.append(
                        "expected rule conditions passed, "
                        f"but earlier rule matched first: {inferred}"
                    )
            rows.append(
                {
                    "source_row": row_index,
                    "smiles_column": column,
                    "LTPProtein": row["LTPProtein"],
                    "FullIdentityOfLipid": row["FullIdentityOfLipid"],
                    "Lipid": row["Lipid"],
                    "expected_classes": "|".join(expected),
                    "inferred_class": inferred,
                    "status": "match" if inferred in expected else "mismatch",
                    "unknown_class": inferred == "Unknown",
                    "failed_conditions": " | ".join(failed),
                    "Smile": smiles,
                    **f,
                }
            )

    report = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output, index=False)

    mismatch_columns = [
        "source_row",
        "smiles_column",
        "LTPProtein",
        "FullIdentityOfLipid",
        "Lipid",
        "expected_classes",
        "inferred_class",
        "failed_conditions",
        "Smile",
    ]
    mismatches = report[report["status"].eq("mismatch")][mismatch_columns]
    args.mismatch_output.parent.mkdir(parents=True, exist_ok=True)
    mismatches.to_csv(args.mismatch_output, index=False)

    print(f"Wrote: {args.output}")
    print(f"Wrote mismatches: {args.mismatch_output}")
    print(f"Rows audited: {len(report)}")
    if len(report):
        print(report["status"].value_counts(dropna=False).to_string())
        print("Unknown inferred:", int(report["unknown_class"].sum()))


if __name__ == "__main__":
    main()
