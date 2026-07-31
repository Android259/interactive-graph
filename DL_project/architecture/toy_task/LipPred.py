#! /usr/bin/env python3
from .dataloader.DataLoader import PLIDataset 
import pandas
import torch_geometric
import torch

from torch.utils.tensorboard import SummaryWriter
from datetime import datetime

torch.set_printoptions(threshold=10000)

class FusedSelfMHA(torch.nn.Module):
    def __init__(self, dim) -> None:
        super(FusedSelfMHA,self).__init__()
        self.dim = dim
        self.sattl = torch.nn.MultiheadAttention(dim,8)
        self.layer_norm2 = torch.nn.LayerNorm(dim)
        self.layer_norm4 = torch.nn.LayerNorm(dim)
        self.slipFF = torch.nn.Sequential(torch.nn.Linear(dim,4*dim),torch.nn.LeakyReLU(),torch.nn.Linear(4*dim,dim))

    def forward(self,lip):
        lip = self.layer_norm2(lip)
        slip, sattl = self.sattl(lip,lip,lip)
        alip = torch.add(lip,slip)
        sflip= self.slipFF(alip)
        out_l = self.layer_norm4(torch.add(alip,sflip))
        return out_l

class MLP(torch.nn.Module):
    def __init__(self,mdim=32,act_fn = torch.nn.LeakyReLU()):
        super(MLP,self).__init__()
        self.encodin = torch.nn.Linear(768,mdim)
        self.mlpL1 = [torch.nn.Linear(mdim,mdim),act_fn,torch.nn.Linear(mdim,mdim)]
        self.mlpL2 = [torch.nn.Linear(mdim,mdim),act_fn,torch.nn.Linear(mdim,3),act_fn]
        self.mlp1 = torch.nn.Sequential(*self.mlpL1)
        self.mlp2 = torch.nn.Sequential(*self.mlpL2)
        self.act_fn = act_fn
        self.mha = FusedSelfMHA(mdim)

    def forward(self,lipLM,lipbatch):
        idxlst =[]
        temp = torch.tensor(-5)
        for i in range(len(lipbatch)):
            if lipbatch[i] != temp:
                idxlst.append(i)
                temp=lipbatch[i]
        return torch_geometric.nn.global_mean_pool(self.mlp2(self.mha(self.mlp1(self.encodin(lipLM)))),lipbatch)
        #return self.mlp2(self.mlp1(self.mha(self.encodin(lipLM))))[idxlst,:]

model = MLP()

batch=8
path="/Users/florianechelard/phd/ltp_gnn/data_norm/"

csv=pandas.read_csv("FullTrainIncomplete.csv")
train_dataset = PLIDataset(root_dir=path, csv = csv, state="train", seed=150)
valid_dataset = PLIDataset(root_dir=path, csv = csv, state="valid", seed=150)

train_loader = torch_geometric.loader.DataLoader(
        train_dataset,
        batch_size=batch,
        shuffle=True,
        )

valid_loader = torch_geometric.loader.DataLoader(
        valid_dataset,
        batch_size=batch,
        shuffle=True,
        )

loss = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.001)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
writer_tb = SummaryWriter(f'run/train{timestamp}')

def log_tb(label, pred, writer,step,los,batch,mode):
    #might hve to round at this very step
    if mode == "train":
        pred = pred.view(label.shape)
        n = (int(max(batch))+1)
        print(torch.mean((label - pred)*(label - pred)))
        acc = torch.mean((label - pred)*(label - pred))
        writer.add_scalar("train accuracy",acc,step)
        writer.add_scalar("train loss",los,step)
    if mode == "valid": 
        pred = pred.view(label.shape)
        n = (int(max(batch))+1)
        print(torch.mean((label - pred)*(label - pred)))
        acc = torch.mean((label - pred)*(label - pred))
        writer.add_scalar("train accuracy",acc,step)
        writer.add_scalar("train loss",los,step)


def epoch(idx,count):
    un_l=0
    ll=0
    for i, graph in enumerate(train_loader):
        data,lipid = graph
        optimizer.zero_grad()
        outl=model(lipid.x,lipid.batch)#,lipid.mass,lipid.length,lipid.unsat)
        print(lipid.x)
        print(outl)
        print(lipid.pred.view(outl.shape))
        los=loss(outl.to(torch.float),lipid.pred.view(outl.shape).to(torch.float)).to(torch.float)
        log_tb(lipid.pred.view(outl.shape).to(torch.float),outl.to(torch.float),writer_tb, count, los,lipid.batch,"train")
        print(los)
        los.backward()
        optimizer.step()
        un_l+=los.item()

    running_vloss = 0.0
    for i , graph in enumerate(valid_loader):
        vdata, lipid = graph
        vout= model(vdata.x,vdata.coords.float(),vdata.edge_index,vdata.edge_attr,lipid.x)
        vout = torch_geometric.nn.global_mean_pool(vout, vdata.batch).view(vdata.inter.shape[0])
        vloss = loss(vout,vdata.inter.to(torch.float))
        running_vloss+=vloss
    avg_vloss = running_vloss / (i+1)
    print(f"loss train = {avg_loss} // loss valid = {avg_vloss}")
    writer_tb.add_scalars('Training vs. Validation Loss', { 'Training' : avg_loss, 'Validation' : avg_vloss }, epoch_number + 1)
    writer_tb.flush()
    if avg_vloss < best_vloss:
        best_vloss = avg_vloss
        torch.save(model.state_dict(), 'model_{}.pth'.format(timestamp))
    
    count+=1
    return los,count
epoch_number = 0
EPOCHS = 10
count =0
for eepoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch_number + 1))
    model.train(True)
    los, count = epoch(epoch_number,count)
    epoch_number += 1
    
    

writer_tb.close()