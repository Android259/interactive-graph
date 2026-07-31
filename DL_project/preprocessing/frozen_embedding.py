#! /usr/bin/env python3
import numpy
from argparse import Namespace
import yaml

with open('../../data/Pretrained MoLFormer/hparams.yaml', 'r') as f:
    config = Namespace(**yaml.safe_load(f))
config

from tokenizer.tokenizer import MolTranBertTokenizer

tokenizer = MolTranBertTokenizer('bert_vocab.txt')

from train_pubchem_light import LightningModule

ckpt = '../../data/Pretrained MoLFormer/checkpoints/N-Step-Checkpoint_3_30000.ckpt'
lm = LightningModule(config, tokenizer.vocab).load_from_checkpoint(ckpt, config=config, vocab=tokenizer.vocab)
lm

import torch
from fast_transformers.masking import LengthMask as LM

def batch_split(data, batch_size=64):
    i = 0
    while i < len(data):
        yield data[i:min(i+batch_size, len(data))]
        i += batch_size
numpy.set_printoptions(threshold=10000)
def embed(model, smiles, tokenizer, batch_size=1):
    model.eval()
    embeddings = []
    dicty={}
    count=0
    for batch in batch_split(smiles, batch_size=batch_size):
        batch_enc = tokenizer.batch_encode_plus(batch, padding=True, add_special_tokens=True)
        #if count==0:
        #    print("-----------batch encoding _______________")
        #    print(batch_enc)
        idx, mask = torch.tensor(batch_enc['input_ids']), torch.tensor(batch_enc['attention_mask'])
        #if count==0:
        #    print("-----------mask __________________")
        #    print(mask)
        with torch.no_grad():
            token_embeddings = model.blocks(model.tok_emb(idx), length_mask=LM(mask.sum(-1)))
        # average pooling over tokens
        if count == 0:
            print("---------------token embedding______________")
            #print(token_embeddings)
            print(token_embeddings.shape)
        #input_mask_expanded = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        #input_mask_expanded
        #sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        #if count==0:
        #    print("------------Sum embeddings _______________")
        #    print(sum_embeddings)
        #    print(sum_embeddings.shape)
        #sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        #embedding = sum_embeddings / sum_mask
        #if count==0:
        #    print("------------embedding _______________")
        #    print(embedding)
        #    print(embedding.shape)
        #embeddings.append(embedding.detach().cpu())
        #if count==0:
        #    print("------------token embeddings _____________")
        #    print(token_embeddings)
        #    print(token_embeddings.shape)
        dicty[batch[0]] = token_embeddings
        count=1
        #break
    #return torch.cat(embeddings)
    return dicty

#understand what the mask does

from rdkit import Chem
from sklearn.linear_model import LogisticRegression

import pandas as pd
import pickle as pkl 
smilist = ["[C@](COP(=O)(O)O)","C(O)(=O)[C@@]([H])(N)COP(OC[C@])(O)(=O)","O(P(OC[C@](OCC)([H])CO)(O)=O)C[C@@]","P(=O)(O)(O)(OC[C@]([H])(NCC)CC)","[C@](OC(COP(=O)(O)O[C@H]1[C@H](O)[C@@H](O)[C@H](O)[C@@H](O)[C@H]1O)COC)","[C@]([H])(OC)(COP(=O)(O)OP(=O)(O)OC[C@@H]1[C@@H](O)[C@@H](O)[C@H](N2C(=O)N=C(N)C=C2)O1)COC","C(OC)NC(COC1C(C(C(C(O1)CO)OC2C(C(C(C(O2)CO)O)O)O)O)O)COC","[C@](COP(=O)(O)OC[C@@]([H])(O)COP(=O)(O)O)([H])(OC)COC","C1[C@@](C)(C)C(/C=C/C(/C)=C/C=C/C(/C)=C/CO)=C(C)CC1","O(P(=O)(OC[C@]([H])(NC(=O))[C@]([H])(O))[O-])CC[N+](C)(C)C","C(OC(=O)C)[C@]([H])(OC(C)=O)COC(C)=O","C(C(COC1C(C(C(C(O1)CO)O)OS(=O)(=O)O)O)NC(=O))O","OC[C@]([H])(NC(=O))[C@]([H])(O)","[C@](COC1C(O)C(O)C(O)C(CO)O1)([H])(NC(C(O))=O)[C@]([H])(O)[C@H](O)","C(=O)(O)CC","[C@](COP(=O)(O)OCC(O)CO)([H])(OC(C)=O)COC(C)=O","P(OC[C@]([H])(OC=O)COC=O)(O)(OC[C@](O)([H])COP(OC[C@]([H])(OC=O)COC=O)(O)=O)=O","[C@](COP(=O)(O)OCCN)([H])(OC=O)COC=O","C(C)CO","[C@](COP(=O)([O-])OCC[N+](C)(C)C)([H])(OC(C)=O)COC(C)=O"]

#df = pd.read_csv('../../data/bace/train.csv').sample(frac=0.05)  # speed things up...
with open("smiles_before_encoding_full.pkl","rb") as f:
    listy = pkl.load(f)
print(len(listy))

def canonicalize(s):
    return Chem.MolToSmiles(Chem.MolFromSmiles(s), canonical=True, isomericSmiles=False)
smiles=[]
for i in listy:
    if i != "Empty" and i != "0" :
        i = i.replace(";","")
        if "//" in i or "\\\\" in i:
            i=i.replace("//", "/")
            i=i.replace("\\\\", "\\")
        if "E" in i:
            i=i.replace("E","")
        #try/except?
        try:
            smiles.append(canonicalize(i))
        except:
            print(i)
            pass
#smiles = listy.apply(canonicalize)
X = embed(lm, smiles, tokenizer)
print(X)
with open("full_embedding.pkl","wb") as f :
    pkl.dump(X,f)

#y = df.Class
