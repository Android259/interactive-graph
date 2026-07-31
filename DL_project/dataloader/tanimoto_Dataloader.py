#cross attention on every layer, +=, 
# weight by pocketness, cross attention some times else, try another normalisation, regular normalisato=ion everywhere, geometric attention in far future
#look on the number of parameters
import sys
import gc
import numpy as np
import glob
import pandas
import torch_geometric
import torch
import random
import pickle as pkl
from rdkit import Chem

batch=int(sys.argv[12])# batch size

lipid_fragments_treatment= int(sys.argv[13]) # 0 if concat, 1 if random, 2 if mask
lipid_concat = bool(lipid_fragments_treatment==0)
lipid_random_choice  =bool(lipid_fragments_treatment==1)
lipid_fragments_mask = bool(lipid_fragments_treatment==2)

protein_pooling=int(sys.argv[14]) # 0 if concat, 1 if random, 2 if mask
ordinary_prot_pooling = bool(protein_pooling==0)
prot_CA_for_pockets = bool(protein_pooling==1)
prot_pooling_by_pockets  =bool(protein_pooling==2)
# 9 CRAL-TRIO, 2 LBP_BPI_CETP, 2 GLTP, 1 ML, 10 lipocalin, 3 START, 3 IP_trans, 3 scp2, 2 OSBP

familydic ={'ATCAY':'CRAL-TRIO','BNIPL':'CRAL-TRIO','BPI':'LBP_BPI_CETP','BPIFB2':'LBP_BPI_CETP','GLTP':'GLTP','GLTPD1':'GLTP','GM2A':'ML','LCN1':'lipocalin','OSBPL9':'OSBP','PITPNA':'IP_trans','PITPNB':'IP_trans','RBP1':'lipocalin','RBP4':'lipocalin','SEC14L2':'CRAL-TRIO','SEC14L6':'CRAL-TRIO','STARD2':'START','STARD10':'START','STARD11':'START','CRABP2':'lipocalin','FABP1':'lipocalin','FABP5':'lipocalin','FABP7':'lipocalin','HSDL2':'scp2','LCN15':'lipocalin','OSBPL5':'OSBP','PITPNC1':'IP_trans','PMP2':'lipocalin','RBP5':'lipocalin','RLBP1':'CRAL-TRIO','SCP2':'scp2','SCP2D1':'scp2','SEC14L4':'CRAL-TRIO','SEC14L5':'CRAL-TRIO','TTPA':'CRAL-TRIO','TTPAL':'CRAL-TRIO'}
Gene_uni={"ATCAY":"Q86WG3", "GM2A":"P17900","PMP2":"P02689","SEC14L6":"B5MCN3","BPI":"P17213", "HSDL2":"Q6YN16", "RBP1":"P09455","STARD10":"Q9Y365","BPIFB2":"Q8N4F0","LCN1":"P31025","RBP4":"P02753","STARD11":"Q9Y5P4","CRABP2":"P29373","LCN15":"Q6UWW0", "RBP5":"P82980","STARD2":"Q9UKL6","FABP1":"P07148", "OSBPL5":"Q9H0X9","RLBP1":"P12271", "TTPA":"P49638","FABP5":"Q01469", "OSBPL9":"Q96SU4","SCP2":"P22307","TTPAL":"Q9BTX7","FABP7":"O15540", "PITPNA":"Q00169","SEC14L2":"O76054","GLTP":"Q9NZD2","PITPNB":"P48739","SEC14L4":"Q9UDX3","GLTPD1":"Q5TA50","PITPNC1":"Q9UKF7", "SEC14L5":"O43304","SCP2D1":"Q9UJQ7","BNIPL":"Q7Z465"}

#sample balanced way
class PLIDataset(torch_geometric.data.Dataset):
    def __init__(self, root_dir, csv:pandas.DataFrame, state, seed, exclusion_set) -> None:
        super().__init__(root=None, transform=None, pre_transform=None, pre_filter=None)
        self.ROOT_DIR = root_dir
        self._indices = None
        self.csvtrue = csv[:760]
        self.csvfalse = csv[760:].sample(frac=0.056, random_state=seed)
        if exclusion_set != 1:
            self.csvfalse = self.csvfalse[self.csvfalse['ProteinDomain'].str.lower() !='lbp_bpi_cetp'].copy()
            self.csvtrue = self.csvtrue[self.csvtrue['ProteinDomain'].str.lower() !='lbp_bpi_cetp'].copy()

        self.csvt = pandas.concat([self.csvtrue,self.csvfalse])
        #self.csvt = self.csvtt.set_index(pandas.Index(list(range(len(self.csvtt)))))
        if exclusion_set == 0:
            self.csvtrain = self.csvt.sample(frac=0.85, random_state=seed).copy()
        elif exclusion_set == 1:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower() !='lbp_bpi_cetp'].copy()
        elif exclusion_set == 2:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='lipocalin'].copy()
        elif exclusion_set == 3:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='osbp'].copy()
        elif exclusion_set == 4:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='scp2'].copy()
        elif exclusion_set == 5:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='ip_trans'].copy()  
        elif exclusion_set == 6:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='ml'].copy() 
        elif exclusion_set == 7:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='cral-trio'].copy()
        elif exclusion_set == 8:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='start'].copy()    
        elif exclusion_set == 9:
            self.csvtrain = self.csvt[self.csvt['ProteinDomain'].str.lower()!='gltp'].copy()
        self.csvalidate =  self.csvt.drop(self.csvtrain.index).sample(frac=0.5,random_state=seed)
        self.csvtest = self.csvt.drop(self.csvtrain.index).drop(self.csvalidate.index).sample(frac=1)
        self.train_orig_indexes = torch.as_tensor(self.csvtrain.index.values, dtype=torch.long)
        #if state=="train":

            #self.train_orig_indexes = torch.as_tensor(self.csvtrain.index.values, dtype=torch.long) 

        tanimoto_matrix_path = root_dir + "/Total_tanimoto_matrix_uint8.npy"
        tanimoto_batch_path = root_dir + "/Total_multiple_lipid_batch.npy"
        tanimoto_matrix = torch.from_numpy(np.load(tanimoto_matrix_path))
        tanimoto_batch = torch.from_numpy(np.load(tanimoto_batch_path))
            # indexes of original dataset
        train_idx = torch.tensor(self.csvtrain.index.values, dtype=torch.long)

        mask = torch.isin(tanimoto_batch, train_idx)

        selected = torch.nonzero(mask, as_tuple=True)[0]

        self.train_tanimoto_matrix = tanimoto_matrix.index_select(0, selected).index_select(1, selected)
        self.train_tanimoto_batch = tanimoto_batch[selected]
            #print(f"train index values : {self.csvtrain.index.values}")
            #print(f"selected indices for train Tanimoto matrix : {self.train_tanimoto_batch}")
        del tanimoto_matrix, tanimoto_batch
        gc.collect()

        unique_batch_ids = torch.unique(self.train_tanimoto_batch, sorted=True)
        self.id2pos = {int(g): int((unique_batch_ids == g).nonzero(as_tuple=True)[0]) for g in unique_batch_ids.tolist()}

        with open(self.ROOT_DIR+"/lipid_SMILES_embedding.pkl","rb") as f:
            self.smiles_encoding = pkl.load(f)

        if state=="train":
            self.csv = self.csvtrain

            print(f"tanimoto_matrix shape : {self.train_tanimoto_matrix.shape}")
            #print(f"Tanimoto matrix : {self.train_tanimoto_matrix}")
            print(f"tanimoto_batch shape : {self.train_tanimoto_batch.shape}")
            #print(f"Tanimoto batch : {self.train_tanimoto_batch}")
            print(f"train : {self.csvtrain.shape}")
        if state=="test":
            self.csv = self.csvtest
            print(f"test : {self.csvtest.shape}")
        if state=="validation":
            self.csv = self.csvalidate
            print(f"valid : {self.csvalidate.shape}")
        
        
        # for LipidAmbiguity
        #self.labelOH = {'PC':[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PC-O':[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PE':[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PS':[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PI':[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'BMP':[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Lyso-PC':[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PG':[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #                'Hex-DHCer-OH':[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex-tCer':    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex-dCer-OH':  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex-dCer':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex-DHCer':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
        #                'Hex2-tCer':   [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex2-dCer-OH':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Hex2-DHCer-OH':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'dSM':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0], 'DHSM':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
        #                'dCer-1P':     [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'DHCer-1P':    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'DHSM-OH':      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'tSM':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0], 'dSM-OH':   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0], 'VA':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0], 'DAG':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
        #                'PE-O':        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'dCer':        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'DHCer':        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'TAG':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0], 'tCer':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0], 'DHCer-OH':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0], 'FA':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        #                'Lyso-PE':     [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'Lyso-PG':     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'FAL':          [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'SHex-dCer':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0], 'SHex-DHCer':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
        #                'Lyso-PE-O':   [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PA':          [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'PGP':          [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'CL':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        #for LikelySubclass
        self.labelOH = {'PC':[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PC-O':[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PE':[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PS':[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PI':[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'BMP':[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PG/BMP':[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*HexCer':[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*HexCer':[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*Hex2Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*SM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*CerP':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHSM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        't*SM':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'VA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DAG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PE-O':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'dCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'd*Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'TAG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'tCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'DHOH*Cer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'FA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'LPE':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'PG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        'LPC':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                        'LPG':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                        'FAL':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                        'd*SHexCer':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                        'LPE-O':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                        'PA':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                        'PGP':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                        'CL':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}
    def get_tanimoto_weights(self):

        #M = self.train_tanimoto_matrix.float()/255.0
        meany = self.train_tanimoto_matrix.float().mean(dim=1)/255.0
        single_raws = torch.unique(self.train_tanimoto_batch)
        weights = torch.zeros(len(single_raws), dtype=torch.float32)
        for i, uid in enumerate(single_raws):
            weights[i]= 1.0 - meany[self.train_tanimoto_batch == uid].mean()

        return weights
    def get_protein_weights(self):
        groups = ['lipocalin','osbp','scp2','ip_trans','ml','cral-trio','start','gltp']
        counts = torch.tensor([ (self.csvtrain["LTPProtein"].str.lower() == g).sum() for g in groups], dtype=torch.float32)
        
        group_weights = 1 - (counts / counts.sum())

        prot_groups = self.csvtrain["LTPProtein"].str.lower().tolist()
        protein_group_weights = torch.zeros(len(prot_groups), dtype=torch.float32)
        for i, g in enumerate(groups):
            mask = [pg == g for pg in prot_groups]
            protein_group_weights[mask] = group_weights[i]

        return protein_group_weights
    
    def make_graph_protein(self,nodes,edges,inter,family,plm,pok,name) -> torch_geometric.data.Data:
        """
        Input : nodes is the name of the file containing node graph, edges is the same for links between nodes

        """
        vertices=pandas.read_csv(nodes)
        edges=pandas.read_csv(edges)

        #vertices["hydrophobicity"]=vertices["residue_type"].map(hydrophobicity_keys)
        #bury=torch.tensor(vertices[["residue_mean_buriedness", "residue_min_buriedness", "residue_max_buriedness"]].values, dtype=torch.float32)
        bury=torch.tensor(vertices["residue_mean_buriedness"].values, dtype=torch.float32)
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56", "hydrophobicity"]].values, dtype=torch.float32) 
        #x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume", "residue_mean_ev28", "residue_mean_ev56"]].values, dtype=torch.float32)
        x=torch.tensor(vertices[["residue_type", "residue_sas_area", "residue_volume"]].values, dtype=torch.float32)
        edge_index=torch.tensor(edges[["ID1_resSeq","ID2_resSeq"]].values, dtype=torch.int64) 
        edge_attr=torch.tensor(edges[["distance","area","boundary"]].values, dtype=torch.float32) #maybe a problem here? about how the edges are indexed OH YES THERE IS
        #also can we pool covalent bond y/n from the non coarse grained structure?
        """
        if inter == 1:
            intera = torch.tensor([1,0],dtype=torch.int32)
        else:
            intera = torch.tensor([0,1],dtype=torch.int32)
        """
        intera = torch.tensor(inter, dtype=torch.long)
        dic={}
        for i in range(len(vertices["ID_resSeq"])):
            dic[int(vertices["ID_resSeq"][i])]=i
        import itertools
        all_nodes = list(itertools.chain.from_iterable(edge_index.tolist()))
        missing_keys = [x for x in all_nodes if dic.get(x) is None]
        #print("Missing keys in dic:", missing_keys)
        #print("Missing keys in dic:", missing_keys)
        edge_index.apply_(lambda x: dic.get(x, 0))  # -1 or some other sentinel
        #edge_index.apply_(dic.get())
        #pocket
        #discard backbone atoms for contributoin to pocket
        aal=["C","CA","CB","O","N"]
        dic={}
        lis=[]

        #need to parse this better, maybe load csv and filter on atom fetures and 

        with open(pok,"r") as f:
            lines = f.readlines()
            if pok== "DL_project/data//graphs/RET4/pocketness.pdb":
                lines = lines[:-1]
            for line in lines:
                    dic[line[22:28].strip()]=0
            for line in lines:
                if line[13:17].strip() in aal:
                    continue
                dic[line[22:28].strip()]+=int(line[62])
        for i,j in dic.items():
            lis.append(j>0)
        poket = torch.tensor(lis, dtype=torch.int16).to(torch.bool)
        #print(poket)
        graph=torch_geometric.data.Data(x=x, edge_index=edge_index.t().contiguous(), edge_attr=edge_attr, inter=intera,family=family,bury=bury,plm=plm,pocket=poket) 
        #print(poket.shape)
        #print(f"poket shape : {poket.shape}")
        #print(f"x shape : {x.shape}")
        return graph

    def lipid_encoding(self,row):
        lipid_enc=""
        if row["SmileGlobal"] == "0" : 
            lipid_enc = row["SmileFragment"]
        elif row["SmileFragment"] == "0" :
            lipid_enc = row["SmileGlobal"]
        elif row["SmileGlobal"] == '0' and row["SmileFragment"] == '0':
            lipid_enc = r"C(COP(=O)([O-])OCC[N+](C)(C)C)([H])(O)COC(CCCCCCC/C=C\CCCCCCCC)=O"
        else:
            #The "Empty" lines or unknown, for now just put most abundant lipid
            lipid_enc = r"C(COP(=O)([O-])OCC[N+](C)(C)C)([H])(O)COC(CCCCCCC/C=C\CCCCCCCC)=O"
        
        #for now we only take the first smile available
        #implement random choice?

        #if "//" in lipid_enc or "\\\\" in lipid_enc:
        #    lipid_enc=lipid_enc.replace("//", "/")
        #    lipid_enc=lipid_enc.replace("\\\\", "\\")
        lipid_enc = lipid_enc.replace("//", "/").replace("\\\\", "\\")

        if ";" in lipid_enc:
            lipid = lipid_enc.split(";")
        else:
            lipid = lipid_enc
        passin = False
        if type(lipid)== type(list()):
            #print("LISTLISTLISTLISTLISTLISTLISTLISTLISTLISTLISTLISTLIST")
            passin = True
            #print(f"lipid.shape {len(lipid)}")
            meany = []#torch.zeros([768])
            if lipid_fragments_mask:
                multiple_lipid_batch = []
                j=0
            for i in lipid:
                try:
                    if i != " ":
                        lipidy = Chem.MolToSmiles(Chem.MolFromSmiles(i), canonical=True, isomericSmiles=False)
                        lipid_encodin_tmp = self.smiles_encoding[lipidy]
                        #print(f"smiles encoding shape : {lipid_encodin_tmp.shape}")
                        #print(f"smiles encoding shape : {lipid_encodin_tmp.shape}")
                        if lipid_fragments_mask:
                            batch_indices = torch.full((lipid_encodin_tmp.shape[1],), j, dtype=torch.long)
                            #print(f"batch indices : {batch_indices}")
                            multiple_lipid_batch.append(batch_indices)
                            meany.append(lipid_encodin_tmp)
                            j+=1
                        else :
                            meany.append(lipid_encodin_tmp)
                        #break
                except:
                    pass
                    #do something?
            if lipid_concat:
                lipid_encodin = torch.cat(meany,dim=1)
            elif lipid_random_choice:
                lipid_encodin = random.choice(meany)
            elif lipid_fragments_mask:
                lipid_encodin = torch.cat(meany,dim=1)
                print(f"lipid encodin shape {lipid_encodin.shape}")
                multiple_lipid_batch = torch.cat(multiple_lipid_batch, dim=0)
                print(f"multiple lipid batch shape {multiple_lipid_batch.shape}")
        if lipid_enc == "0":
            passin=True
            lipid = r"C(COP(=O)([O-])OCC[N+](C)(C)C)([H])(O)COC(CCCCCCC/C=C\CCCCCCCC)=O"
            print("wrong")
            print(row)
            return torch.rand([65,768])

        if not passin :
            try:
                #returns caninical format of SMILES
                lipidy = Chem.MolToSmiles(Chem.MolFromSmiles(lipid), canonical=True, isomericSmiles=False)
                lipid_encodin = self.smiles_encoding[lipidy]
                if lipid_fragments_mask:
                    multiple_lipid_batch = torch.zeros((lipid_encodin.shape[1],), dtype=torch.long)

            except:
                lipid_encodin = torch.rand([65, 768])
                print("ow")
                print(row)

        if lipid_fragments_mask:
            
            return torch.squeeze(lipid_encodin), multiple_lipid_batch
        else:
            return torch.squeeze(lipid_encodin)
    
    def lipidlabel_enc(self,lipdata):
        oh = torch.zeros(41)
        try:
            oh=self.labelOH[lipdata]
        except:
            print(lipdata)
            print(self.labelOH[lipdata])
            pass
        return oh

    def len(self):
        #lenght of combinations or lenght of structures/smiles?
        return len(self.csv['LTPProtein'])

    def get(self, idx):
        
        row = self.csv.iloc[idx]
        if lipid_fragments_mask:
            lipid_enc, lipid_batch = self.lipid_encoding(row)
            print(f"final lipid enc shape {lipid_enc.shape}")
            print(f"final lipid batch shape {lipid_batch.shape}")
            #print(f"lipid_batch{lipid_batch}")
        else:
            lipid_enc = self.lipid_encoding(row)
        #print(row['LTPProtein'])
        lipidlabel = self.lipidlabel_enc('PC')#row['LikelySubclass'])

        prot_file = row["LTPProtein"]
        replace={"RBP1":"RET1","RBP4":"RET4","RBP5":"RET5","STARD11":"CERT"}
        if prot_file in replace.keys():
            prot_file_emb=replace[prot_file]
        else:
            prot_file_emb = prot_file

        node_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_nodes.csv"
        edge_file = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/coarse_graph_links.csv"
        pok = self.ROOT_DIR+"/graphs/"+prot_file_emb+"/pocketness.pdb"
        #with open(self.ROOT_DIR+prot_file+"/"+Gene_uni[prot_file]+"_ESM3pdb.pkl","rb") as f:
        embed_file = glob.glob(self.ROOT_DIR+"/embedding_ESM3/"+prot_file_emb+"_"+"*")
        #print(f"prot file {prot_file}")
        #print(embed_file)
        with open(embed_file[0],'rb') as f:
            plm_tensor= pkl.load(f)
            #print(plm_tensor.shape)
            #potentialy special tokens while making embedings
            if prot_file =="GM2A":
                #if not to impose in a particular condotion - breaks 
                plm_tensor= plm_tensor[1:-1]
            elif prot_file_emb=="PITPNA":
                plm_tensor=plm_tensor[4:-4]
            plm_tensor= plm_tensor[1:-1]
            #print(f"embedings shape : {plm_tensor.shape}")
        with open(node_file, 'r') as f:
            num_lines = sum(1 for line in f)
            if num_lines-plm_tensor.shape[0] !=1:
                print(prot_file)
                print(f"embedings shape : {plm_tensor.shape}")
                print(f"Nodes shape : {num_lines}")


        family=familydic[row['LTPProtein']]
        fam_enc =["CRAL-TRIO","LBP_BPI_CETP","GLTP","ML","lipocalin","START","IP_trans","scp2","OSBP"]
        tenfam=torch.zeros(9)
        for i in range(len(fam_enc)):
            if fam_enc[i] == family.strip():
                tenfam[i]=1

        interaction = row["Interaction"]

        a = list(range(lipid_enc.shape[1]))
        lipedge =[(a[i], a[j+i+1]) for i in range(len(a))  for j in range(len(a[i+1:]))]
        lipedge+=[(a[i],a[i]) for i in range(len(a))]

        protein_graph = self.make_graph_protein(node_file,edge_file, interaction, tenfam,plm_tensor,pok,row["LTPProtein"])
        #print(pok)
        """
        orig_idx = self.train_orig_indexes[idx]
        protein_graph.sample_index  = orig_idx.view(1)
        protein_graph.id2batch = self.id2batch
        """

        orig_idx = int(self.train_orig_indexes[idx])
        pos = self.id2pos[orig_idx]          # KeyError — если этого id нет в батче Tanimoto
        protein_graph.sample_index = torch.tensor([orig_idx], dtype=torch.long)
        protein_graph.tanimoto_pos = torch.tensor([pos], dtype=torch.long)

        if lipid_fragments_mask:
            lipid_graph = torch_geometric.data.Data(x=lipid_enc,edge_index=torch.tensor(lipedge).t().contiguous(),liplab=torch.tensor(lipidlabel,dtype=torch.int), lipid_batch=lipid_batch)
        else:
            lipid_graph = torch_geometric.data.Data(x=lipid_enc,edge_index=torch.tensor(lipedge).t().contiguous(),liplab=torch.tensor(lipidlabel,dtype=torch.int))
        #lipid_graph = torch_geometric.data.Data(x=lipid_enc,edge_index=torch.tensor(lipedge).t().contiguous(),liplab=torch.tensor(lipidlabel,dtype=torch.int), lipid_batch=lipid_batch)
        return protein_graph , lipid_graph
