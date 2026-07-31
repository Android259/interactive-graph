import sys
import os
# Add the parent directory of your script's directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dataloader.Dataloader import PLIDataset

import pandas
import torch_geometric
import torch
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import torch.nn.functional as F

import threading
import webbrowser
from tensorboard import program
import time
from torch_geometric.nn import global_add_pool,global_max_pool,global_mean_pool

def launch_tensorboard(log_dir="run"):
    tb = program.TensorBoard()
    tb.configure(argv=[None, "--logdir", "run"])
    url = tb.launch()
    webbrowser.open(url)

third_layers_in_mlps = bool(int(sys.argv[1]))
cross_attention = bool(int(sys.argv[2]))
protein_self_attention = bool(int(sys.argv[3]))
lipid_self_attention = bool(int(sys.argv[4]))
double_attention = bool(int(sys.argv[5]))
m = int(sys.argv[6])#multiplication coef for hidden mlp's dimensions
lr=float(sys.argv[7]) #learning rate
hiddim=int(sys.argv[8]) # hidden dimensions
ep=int(sys.argv[9]) #number of epochs
Seed = int(sys.argv[10])
exclusion_set = int(sys.argv[11])# protein group to exclude for a validation/test, 0 means random split
batch=int(sys.argv[12])# batch size

lipid_fragments_treatment= int(sys.argv[13]) # 0 if concat, 1 if random, 2 if mask
lipid_concat = bool(lipid_fragments_treatment==0)
lipid_random_choice  =bool(lipid_fragments_treatment==1)
lipid_fragments_mask = bool(lipid_fragments_treatment==2)

#there was a mistake, one value for lipid-fragments-treatment and for protein pooling
protein_pooling=int(sys.argv[14]) 
ordinary_prot_pooling = bool(protein_pooling==0)
prot_CA_for_pockets = bool(protein_pooling==1)
prot_pooling_by_pockets  =bool(protein_pooling==2)
protein_group_weight = bool(int(sys.argv[15])) # whether to use protein group weights
#"""

plmon = True
buryon = True
loslis = [torch.nn.MSELoss(),torch.nn.CrossEntropyLoss(),torch.nn.BCELoss()]
loss_type = 1
loss = loslis[loss_type]
#batch=16# batch size
poolist=[global_add_pool,global_max_pool,global_mean_pool]
pool = poolist[1] #pooling type
HEADS = 8

from architecture.HybridPred import InteractionClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print()

model = InteractionClassification(hiddim, hiddim, hiddim, plmon, buryon, m,HEADS)

model = model.to(device)
number_of_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"number of parameters : {number_of_parameters}")
path="DL_project/data/"

csv = pandas.read_csv("DL_project/data/Processed_Negative_Interaction_Without_Duplicates.csv")

train_dataset = PLIDataset(root_dir=path, csv = csv, state="train", seed=Seed,exclusion_set=exclusion_set)
valid_dataset = PLIDataset(root_dir=path, csv = csv, state="validation", seed=Seed,exclusion_set=exclusion_set)
test_dataset = PLIDataset(root_dir=path, csv = csv, state="test", seed=Seed,exclusion_set=exclusion_set)

tanimoto_weights = train_dataset.get_tanimoto_weights().to(device)
common_weights = tanimoto_weights
if  protein_group_weight:
    protein_group_weights = train_dataset.get_protein_weights().to(device)
    common_weights = (tanimoto_weights+protein_group_weights)/2.0
#print(f"common weights : {common_weights}")
#print(f"tanimoto weights : {tanimoto_weights}")
#print(f"tanimoto weights shape : {tanimoto_weights.shape}")
#train_dataset, valid_dataset, test_dataset = PLIDataset(root_dir=path, csv = csv, seed=Seed,exclusion_set=exclusion_set)
#exit()
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
test_loader = torch_geometric.loader.DataLoader(
        test_dataset,
        batch_size=batch,
        shuffle=True,
        )
print("data extracted")
optimizer = torch.optim.Adam(model.parameters(), lr = lr)

if lipid_concat:
    lipid_processing = ""
elif lipid_fragments_mask:
    lipid_processing = "lipMask"
elif lipid_random_choice:
    lipid_processing = "lipRandom"
if prot_CA_for_pockets:
    prot_processing = "pocketsCA"
elif prot_pooling_by_pockets:
    prot_processing="pocketsPooling"
elif ordinary_prot_pooling:
    prot_processing=""

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = f'run/train{timestamp}_{"added_Layers" if third_layers_in_mlps else ""}_{"protSA" if protein_self_attention else ""}_{"lipSA" if lipid_self_attention else ""}_{"CA" if cross_attention else ""}_{"doubleAtt" if double_attention else ""}_{prot_processing}_{lipid_processing}_{"protGroupWeights" if protein_group_weight else ""}_{number_of_parameters}parameters_{m}_{HEADS}_{Seed}_{lr}_{batch}_{hiddim}_{exclusion_set}'
writer_tb = SummaryWriter(log_dir)


threading.Thread(target=launch_tensorboard, args=(log_dir,), daemon=True).start()
time.sleep(3)
sig=torch.nn.Sigmoid()

def log_tb(writer,step,los,mode,pred,label):
    #might hve to round at this very step
    if mode == "train":
        pred_class = pred.argmax(dim=1)

        acc = (pred_class == label).float().mean()

        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        #print(f"TP {TP}")
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        #print(f"FP {FP}")
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        #print(f"TN {TN}")
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        #print(f"FN {FN}")
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 
        #sensitivity = sensitivity.half()
        #print(f"sensitivity : {sensitivity}")
        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        #print(f"precision : {precision}")
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        #print(f"specificity : {specificity}")
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        print(f"train accuracy : {acc}")
        writer.add_scalar("train sensitivity", sensitivity.item(),step)
        writer.add_scalar("train precision", precision.item(),step)
        writer.add_scalar("train specificity", specificity.item(),step)
        writer.add_scalar("train accuracy",acc.item(),step)
        writer.add_scalar("train F1 score",F1.item(),step)
        writer.add_scalar("train balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("train loss",los,step)
       #writer_tb.flush()
    if mode == "valid":
        #acc = torch.mean(torch.floor(torch.mean((label == torch.round(pred)).to(torch.int).to(torch.float),dim=1)))
        #pred_class = torch.round(sig(pred))
        pred_class = pred.argmax(dim=1)
        #label_class = label.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        print(f"valid accuracy : {acc}")
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        #print(f"TP {TP}")
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        #print(f"FP {FP}")
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        #print(f"TN {TN}")
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        #print(f"FN {FN}")
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 
        #print(f"sensitivity : {sensitivity}")
        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        #print(f"precision : {precision}")
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        #print(f"specificity : {specificity}")
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        writer.add_scalar("valid sensitivity", sensitivity.item(),step)
        writer.add_scalar("valid precision", precision.item(),step)
        writer.add_scalar("valid specificity", specificity.item(),step)
        writer.add_scalar("valid accuracy",acc.item(),step)
        writer.add_scalar("valid F1 score",F1.item(),step)
        writer.add_scalar("valid balanced accuracy",balanced_acc.item(),step)
        writer.add_scalar("valid loss",los,step)

    if mode == "test":
        #acc = torch.mean(torch.floor(torch.mean((label == torch.round(pred)).to(torch.int).to(torch.float),dim=1)))
        #pred_class = torch.round(sig(pred))
        pred_class = pred.argmax(dim=1)
        #label_class = label.argmax(dim=1)
        acc = (pred_class == label).float().mean()
        print(f"test accuracy : {acc}")
        TP = ((pred_class==label) & (pred_class==1)).float().sum()
        #print(f"TP {TP}")
        FP = ((pred_class !=label) & (pred_class ==1)).float().sum()
        #print(f"FP {FP}")
        TN = ((pred_class == label) & (pred_class == 0)).float().sum()
        #print(f"TN {TN}")
        FN = ((pred_class != label) & (pred_class == 0)).float().sum()
        #print(f"FN {FN}")
        sensitivity = TP / (TP+FN)#proportion of true 1 to all genuine 1 
        #print(f"sensitivity : {sensitivity}")
        precision = TP / (TP+FP)#proportion of correct 1 to all predicted 1
        #print(f"precision : {precision}")
        specificity = TN / (TN + FP) # proportion of corrrect 0 to all the real 0
        #print(f"specificity : {specificity}")
        F1 = (2*TP) / (2*TP + FP + FN)
        balanced_acc = (sensitivity + specificity) / 2
        metrics = {
            "accuracy": acc.item(),
            "sensitivity": sensitivity.item(),
            "precision": precision.item(),
            "specificity": specificity.item(),
            "F1": F1.item(),
            "balanced_accuracy": balanced_acc.item(),
            "loss": los.item() if isinstance(los, torch.Tensor) else los
        }
        return metrics
        #writer_tb.flush()
        
sof2 = torch.nn.Softmax(-1)
def epoch(idx,counttrain,countval):
    un_l=0
    #ll=0
    for i, graph in enumerate(train_loader):
        #dataset is reduced because of high variety of experience parameters 
        if i < 1740/batch:
            #print(f"step: {i}")
            prot,lipid = graph
            prot = prot.to(device)
            lipid = lipid.to(device)
            #prot_batch = prot.batch
            #lip_batch = lipid.batch
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device)

            optimizer.zero_grad()

            forward_args = dict(plmon=plmon,buryon=buryon,pool=pool,
                        plm=prot.plm,bury=prot.bury,prot=prot.x,prot_edgidx=prot.edge_index,prot_e_attr=prot.edge_attr,prot_batch=prot.batch,
                        lip=lipid.x,lip_batch=lipid.batch,
            )
            if lipid_fragments_mask:
                forward_args["lipid_batch"] = lipid.lipid_batch
            if prot_CA_for_pockets or prot_pooling_by_pockets:
                forward_args["pocket_mask"] = prot.pocket

            outl = model(**forward_args)
            #print("forward_args has lipid_batch:", "lipid_batch" in forward_args)
            if "lipid_batch" in forward_args:
                print("lipid_batch value:", forward_args["lipid_batch"])
            min_len = min(outl.shape[0], interaction_labels.shape[0])
            outl = outl[:min_len]
            interaction_labels = interaction_labels[:min_len]
            if i % 10 == 0: 
                print(f"epoch : {idx+1}")
            print(f"batch : {i+1}/35")
            #print(f"outl : {outl}")
            #idxs = prot.sample_index.view(-1).to(device)
            #id2batch = prot.id2batch.to(device)
            #idxs = prot.sample_index.view(-1).to(device)       
            pos  = prot.tanimoto_pos.view(-1).to(device)
            sample_weights = common_weights[pos]
            #sample_weights = prot.sample_weights.to(device)
            #print(f"sample weights : {sample_weights}")
            #print(f"sample idxs : {idxs}")
            sample_weights = common_weights[pos]
            #print(f"sample weights : {sample_weights}")    
            los_unred=F.cross_entropy(outl,interaction_labels.long(), reduction = 'none')
            #print(f"unreduced loss shape : {los_unred.shape}")
            #print(f"unreduced loss : {los_unred}")
            #print(f"sample weights shape : {sample_weights.shape}")
            #print(f"sample weights : {sample_weights}")
            los = (los_unred*sample_weights).mean()
            #print(f"weighted loss : {los}")
            log_tb(writer_tb, counttrain, los,"train",outl,interaction_labels)
            #print(f"loss: {los}")
            los.backward()
            optimizer.step()
            un_l+=los.item()
            counttrain+=1
        else:
            break
    writer_tb.flush()
    for i , graph in enumerate(valid_loader):
        print("VALIDATION")
        prot,lipid = graph
        prot = prot.to(device)
        lipid = lipid.to(device)
        interaction_labels = prot.inter
        interaction_labels = interaction_labels.to(device)
        forward_args = dict(plmon=plmon,buryon=buryon,pool=pool,
            plm=prot.plm,bury=prot.bury,prot=prot.x,prot_edgidx=prot.edge_index,prot_e_attr=prot.edge_attr,prot_batch=prot.batch,
            lip=lipid.x,lip_batch=lipid.batch,
            )
        if lipid_fragments_mask:
            forward_args["lipid_batch"] = lipid.lipid_batch
        if prot_CA_for_pockets or prot_pooling_by_pockets:
            forward_args["pocket_mask"] = prot.pocket

        outl = model(**forward_args)
        min_len = min(outl.shape[0], interaction_labels.shape[0])
        outl = outl[:min_len]
        interaction_labels = interaction_labels[:min_len]
        print(f"batch : {i+1}/4")
        pos  = prot.tanimoto_pos.view(-1).to(device)
        sample_weights = common_weights[pos]
        los_unred=F.cross_entropy(outl,interaction_labels.long(), reduction = 'none')
        #los=loss(outl,interaction_labels.long())
        log_tb(writer_tb, countval, los,"valid",outl,interaction_labels.to(torch.float))
        #print(f"los : {los}")
        countval +=1
    writer_tb.flush()

    if idx==ep-1:
        accuracy_list = []
        sensitivity_list = []
        precision_list = []
        specificity_list = []
        f1_list = []
        balanced_acc_list = []
        loss_list = []
        for i , graph in enumerate(test_loader):
            print("TEST")
            prot,lipid = graph
            prot = prot.to(device)
            lipid = lipid.to(device)
            interaction_labels = prot.inter
            interaction_labels = interaction_labels.to(device)
            forward_args = dict(plmon=plmon,buryon=buryon,pool=pool,
                                plm=prot.plm,bury=prot.bury,prot=prot.x,prot_edgidx=prot.edge_index,prot_e_attr=prot.edge_attr,prot_batch=prot.batch,
                                lip=lipid.x,lip_batch=lipid.batch,
            )
            if lipid_fragments_mask:
                forward_args["lipid_batch"] = lipid.lipid_batch
                print(lipid.lipid_batch)
            if prot_CA_for_pockets or prot_pooling_by_pockets:
                forward_args["pocket_mask"] = prot.pocket

            outl = model(**forward_args)
            min_len = min(outl.shape[0], interaction_labels.shape[0])
            outl = outl[:min_len]
            interaction_labels = interaction_labels[:min_len]

            print(f"batch : {i+1}/4")
            counttest=0
            los=loss(outl,interaction_labels.long())
            metrics = log_tb(writer_tb, counttest, los,"test",outl,interaction_labels.to(torch.float))   
            accuracy_list.append(metrics["accuracy"])
            sensitivity_list.append(metrics["sensitivity"])
            precision_list.append(metrics["precision"])
            specificity_list.append(metrics["specificity"])
            f1_list.append(metrics["F1"])
            balanced_acc_list.append(metrics["balanced_accuracy"])
            loss_list.append(metrics["loss"])
        print(f"accuracy: {torch.stack([torch.tensor(x) for x in accuracy_list]).mean().item():.6f}")
        print(f"sensitivity: {torch.stack([torch.tensor(x) for x in sensitivity_list]).mean().item():.6f}")
        print(f"precision: {torch.stack([torch.tensor(x) for x in precision_list]).mean().item():.6f}")
        print(f"specificity: {torch.stack([torch.tensor(x) for x in specificity_list]).mean().item():.6f}")
        print(f"F1: {torch.stack([torch.tensor(x) for x in f1_list]).mean().item():.6f}")
        print(f"balanced_accuracy: {torch.stack([torch.tensor(x) for x in balanced_acc_list]).mean().item():.6f}")
        print(f"loss: {torch.stack([torch.tensor(x) for x in loss_list]).mean().item():.6f}")
        with open(f"test_metrics_{timestamp}_exclusion_set_{exclusion_set}.txt", "w") as f:
            def write_metric(name, values):
                t = torch.stack([torch.tensor(x) for x in values], dim=0)
                mean = t.mean().item()
                std = t.std(unbiased=True).item()
                f.write(f"{name}: {mean:.6f} ± {std:.6f}\n")

            write_metric("accuracy", accuracy_list)
            write_metric("sensitivity", sensitivity_list)
            write_metric("precision", precision_list)
            write_metric("specificity", specificity_list)
            write_metric("F1", f1_list)
            write_metric("balanced_accuracy", balanced_acc_list)
            write_metric("loss", loss_list)
        """
        with open(f"test_metrics_{logdir}.txt", "w") as f:
            f.write(f"accuracy: {torch.stack([torch.tensor(x) for x in accuracy_list]).mean().item():.6f}\n")
            f.write(f"sensitivity: {torch.stack([torch.tensor(x) for x in sensitivity_list]).mean().item():.6f}\n")
            f.write(f"precision: {torch.stack([torch.tensor(x) for x in precision_list]).mean().item():.6f}\n")
            f.write(f"specificity: {torch.stack([torch.tensor(x) for x in specificity_list]).mean().item():.6f}\n")
            f.write(f"F1: {torch.stack([torch.tensor(x) for x in f1_list]).mean().item():.6f}\n")
            f.write(f"balanced_accuracy: {torch.stack([torch.tensor(x) for x in balanced_acc_list]).mean().item():.6f}\n")
            f.write(f"loss: {torch.stack([torch.tensor(x) for x in loss_list]).mean().item():.6f}\n")
        """    
        writer_tb.flush()
    
    return los,counttrain, countval


epoch_number = 0
EPOCHS = ep
countrain =0
countval =0
#counttest = 0
for eepoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch_number + 1))
    model.train(True)
    los, countrain,countval = epoch(epoch_number,countrain,countval)
    #plot_metrics()
    epoch_number += 1
    torch.cuda.empty_cache()
    """
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=20)  

print("optimal parameters :", study.best_params)
"""