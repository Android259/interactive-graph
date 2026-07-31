import torch
import pandas as pd
import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

CSV_PATH = "DL_project/data/Processed_Negative_Interaction_Without_Duplicates.csv"
SMILES_DEFAULT = r"C(COP(=O)([O-])OCC[N+](C)(C)C)([H])(O)COC(CCCCCCC/C=C\CCCCCCCC)=O"

def row_to_smiles(row):
    if row.get("SmileGlobal", "0") != "0":
        lipid_enc = row["SmileGlobal"]
    elif row.get("SmileFragment", "0") != "0":
        lipid_enc = row["SmileFragment"]
    else:
        lipid_enc = SMILES_DEFAULT
    # normalization
    lipid_enc = lipid_enc.replace("//", "/").replace("\\\\", "\\")
    lipid = lipid_enc.split(";") if ";" in lipid_enc else [lipid_enc]
    # canonization RDKit
    if type(lipid)== type(list()):
        out = []
        for i in lipid:
            i = i.strip()
            if not i or i == " ":
                #print("wrong")
                continue
            lipidy = Chem.MolToSmiles(Chem.MolFromSmiles(i), canonical=True, isomericSmiles=False)
            out.append(lipidy)
        #out = torch.cat(out,dim=1)
    else:
        lipidy = [Chem.MolToSmiles(Chem.MolFromSmiles(lipid), canonical=True, isomericSmiles=False)]
    batch_length = len(out)

    return out,batch_length

def calculate_tanimoto_matrix_from_csv(csv_path, nBits=1024, radius=2):
    df = pd.read_csv(csv_path)
    all_smiles = []
    tanimoto_batch = []
    for i, row in df.iterrows():
        list, length = row_to_smiles(row)
        all_smiles.extend(list)
        tanimoto_batch.extend([i]*length)
    # RDKit fingerprints
    mols = [Chem.MolFromSmiles(s) for s in all_smiles]
    fingerprints = [AllChem.GetMorganFingerprintAsBitVect(m, radius, nBits) for m in mols]
    # tanimoto matrix
    n = len(fingerprints)
    M = np.zeros((n, n), dtype=np.uint8)
    for i in range(n):
        sims = DataStructs.BulkTanimotoSimilarity(fingerprints[i], fingerprints[i:])
        sims_uint8 = np.round(np.array(sims, dtype=np.float32) * 255).astype(np.uint8)
        M[i, i:] = sims_uint8
        M[i:, i] = sims_uint8  # заполняем нижний треугольник без создания копии
        M[i, i] = 255   
    return tanimoto_batch,M


multiple_lipid_batch, M = calculate_tanimoto_matrix_from_csv(CSV_PATH)
np.save("Total_tanimoto_matrix_float32.npy", M)   
np.save("Total_multiple_lipid_batch.npy",multiple_lipid_batch)  

M_loaded = np.load("Total_tanimoto_matrix_float32.npy")
batch_loaded = np.load("Total_multiple_lipid_batch.npy")

print("Tanimoto matrix (shape {}):".format(M_loaded.shape))
print(M_loaded)

print("\nMultiple lipid batch (shape {}):".format(batch_loaded.shape))
print(batch_loaded)