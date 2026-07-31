#! /usr/bon/env python3


from dataloader.DataLoader import PLIDataset
import pandas
import torch_geometric
import torch
import sys
from torch_geometric.nn import global_add_pool,global_max_pool,global_mean_pool
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime

if len(sys.argv) != 10:
    print("ProtPred.py [loss_type] [PLM on] [buriedness on] [task] [learning rate] [batch] [hidden_dim] [pool_type] [epoch]")
    print("\t loss_type : (0) MSE Loss,(1) Cross Entropy Loss,(2) Binary Cross Entropy Loss")
    print("\t task : (0) buriedness node (1) family class")
    print("\t global pool : (0) add (1) max (2) mean")
    exit()

loslis = [torch.nn.MSELoss(),torch.nn.CrossEntropyLoss(),torch.nn.BCELoss()]
poolist=[global_add_pool,global_max_pool,global_mean_pool]
loss = loslis[int(sys.argv[1])]
plmon=bool(int(sys.argv[2]))
buryon = bool(int(sys.argv[3]))
taskfam=bool(int(sys.argv[4]))
lr=float(sys.argv[5])
batch=int(sys.argv[6]) 
hiddim=int(sys.argv[7])
pool=poolist[int(sys.argv[8])]
ep=int(sys.argv[9])

class GNN(torch.nn.Module):
    def __init__(self,indim =3,mdim=hiddim,nlayers=1) -> None:
        super(GNN,self).__init__()
        self.enc_plm = torch_geometric.nn.conv.GCNConv(1536,10,add_self_loops=True) # ESM3 => 1536 // ESM2 => 1280
        indim += 10 if plmon else 0
        indim += 1 if buryon else 0
        self.encodin = torch_geometric.nn.conv.GCNConv(indim,mdim,add_self_loops=True)
        self.GCN = torch_geometric.nn.conv.GCNConv(mdim,mdim,add_self_loops=True)
        self.GAT = torch_geometric.nn.conv.GATv2Conv(4*mdim,mdim,heads=4,edge_dim=3)
        self.GAT2 = torch_geometric.nn.conv.GATv2Conv(mdim,mdim,heads=4,edge_dim=3)
        outdim = 9 if taskfam else 1
        self.decodin = torch_geometric.nn.conv.GCNConv(mdim*4,outdim,add_self_loops=True)
        self.ln1 = torch.nn.LayerNorm(mdim*4)
        self.sof = torch.nn.Softmax(-1)

    def forward(self,node,edgidx,plm,e_attr,batch,bury,pocket):
        print(pocket.shape[0] == node.shape[0])
        if plmon:
            plm = self.enc_plm(plm,edgidx)
            node = torch.cat((node,plm),-1)
        if buryon:
            node = torch.cat((node,bury.unsqueeze(1)),-1)
        inn = self.encodin(node,edgidx)
        gcn = self.GAT(self.ln1(self.GAT2(inn,edgidx)),edgidx,e_attr)
        out = self.decodin(gcn,edgidx)
        if taskfam:

            return self.sof(pool(out[pocket],batch[pocket]))
        else:
            return out 
model = GNN()


path="/Users/florianechelard/phd/ltp_gnn/structures/all/"

csv=pandas.read_csv("FullTrainIncomplete.csv")
train_dataset = PLIDataset(root_dir=path, csv = csv, state="train", seed=150, interac=False)
valid_dataset = PLIDataset(root_dir=path, csv = csv, state="validation", seed=150, interac=False)

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

optimizer = torch.optim.Adam(model.parameters(), lr = lr)


timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
writer_tb = SummaryWriter(f'run/train{timestamp}_{"plm" if plmon else ""}_{"bury" if buryon else ""}_{lr}_{batch}_{hiddim}')
sig=torch.nn.Sigmoid()

def log_tb(writer,step,los,mode,pred,label):
    #might hve to round at this very step
    if mode == "train":
        if taskfam:
            acc = torch.mean(torch.floor(torch.mean((label == torch.round(pred)).to(torch.int).to(torch.float),dim=1)))
            print(acc)
            writer.add_scalar("train accuracy",acc,step)
        writer.add_scalar("train loss",los,step)
    if mode == "valid":
        if taskfam:
            acc = torch.mean(torch.floor(torch.mean((label == torch.round(pred)).to(torch.int).to(torch.float),dim=1)))
            print(acc)
            writer.add_scalar("valid accuracy",acc,step)
        writer.add_scalar("valid loss",los,step)

def epoch(idx,count):
    un_l=0
    ll=0
    for i, graph in enumerate(train_loader):
        if i < 200/batch:
            prot,lipid = graph
            optimizer.zero_grad()
            outl=model(prot.x,prot.edge_index,prot.plm,prot.edge_attr,prot.batch,prot.bury,prot.pocket)
            if taskfam:
                los=loss(outl,prot.family.view(outl.shape))
                log_tb(writer_tb, count, los,"train",outl,prot.family.view(outl.shape))
            else: 
                los=loss(outl,prot.bury.view(outl.shape))
                log_tb(writer_tb, count, los,"train",outl,prot.bury.view(outl.shape))

            if taskfam:
                print(prot.family.view(outl.shape))
            else:
                print(prot.bury.view(outl.shape))
            print(torch.round(outl))
            print(los)
            los.backward()
            optimizer.step()
            un_l+=los.item()
            count+=1
        else:
            break
    for i , graph in enumerate(valid_loader):
        prot,lipid = graph
        outl=model(prot.x,prot.edge_index,prot.plm,prot.edge_attr,prot.batch,prot.bury,prot.pocket)
        if taskfam:
            los=loss(outl,prot.family.view(outl.shape))
            log_tb(writer_tb, i, los,"valid",outl,prot.family.view(outl.shape))
        else: 
            los=loss(outl,prot.bury.view(outl.shape))
            log_tb(writer_tb, i, los,"valid",outl,prot.bury.view(outl.shape))
    return los,count


epoch_number = 0
EPOCHS = ep
count =0
for eepoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch_number + 1))
    model.train(True)
    los, count = epoch(epoch_number,count)
    epoch_number += 1