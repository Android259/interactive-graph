# geometric_edge_mlp_protgeom8_v2

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_v2'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.7612      0.3934      0.7800      0.5581      0.7264      0.4409
groups_GLTP            3      0.6000      0.3733      0.7414      0.4440      0.6026      0.4615
groups_IP_trans        3      0.4638      0.7589      0.7961      0.5716      0.5278      0.8014
groups_LBP_BPI_CETP    3      0.4638      0.6667      0.6727      0.5103      0.5833      0.6312
groups_START           3      0.8154      0.3371      0.8328      0.5341      0.8490      0.3296
groups_lipocalin       3      0.3333      0.8472      0.5892      0.6137      0.3981      0.8657
groups_scp2            3      0.5882      0.6275      0.8000      0.5226      0.7451      0.7255
ALL                   21      0.5751      0.5720      0.7446      0.5363      0.6332      0.6080

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6206      0.6106     0.0841  21
max valid BA                0.6730      0.6791     0.0761  21
best valid F1               0.6389      0.6545     0.0879  21
test BA                     0.5736      0.5768     0.0582  21
test F1                     0.4903      0.5205     0.1724  21
test sensitivity            0.5751      0.5882     0.2606  21
test specificity            0.5720      0.5957     0.2559  21
test precision              0.4886      0.4900     0.0755  20
test loss                   0.7484      0.6805     0.1838  21
FPR (FP/(FP+TN))            0.4280      0.4043     0.2559  21
FNR (FN/(FN+TP))            0.4249      0.4118     0.2606  21

=== abs(sensitivity-specificity) gap: mean=0.4007 median=0.2800 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5836      0.5745     0.0238  3
  max valid BA                0.6043      0.5941     0.0360  3
  best valid F1               0.7081      0.7128     0.0088  3
  test BA                     0.5773      0.5765     0.0026  3
  test F1                     0.6522      0.6395     0.0568  3
  test sensitivity            0.7612      0.7015     0.1864  3
  test specificity            0.3934      0.4590     0.1891  3
  test precision              0.5823      0.5875     0.0152  3
  test loss                   0.7203      0.6805     0.0728  3
  FPR (FP/(FP+TN))            0.6066      0.5410     0.1891  3
  FNR (FN/(FN+TP))            0.2388      0.2985     0.1864  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5321      0.5192     0.0222  3
  max valid BA                0.6538      0.6538     0.0962  3
  best valid F1               0.6899      0.6757     0.0327  3
  test BA                     0.4867      0.5000     0.0611  3
  test F1                     0.5277      0.4912     0.0868  3
  test sensitivity            0.6000      0.5600     0.2227  3
  test specificity            0.3733      0.2800     0.2723  3
  test precision              0.4977      0.5000     0.0591  3
  test loss                   0.7330      0.7048     0.0539  3
  FPR (FP/(FP+TN))            0.6267      0.7200     0.2723  3
  FNR (FN/(FN+TP))            0.4000      0.4400     0.2227  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6646      0.6946     0.0716  3
  max valid BA                0.7057      0.7371     0.0549  3
  best valid F1               0.6221      0.6531     0.0548  3
  test BA                     0.6113      0.6115     0.0345  3
  test F1                     0.4509      0.4783     0.1170  3
  test sensitivity            0.4638      0.4783     0.2395  3
  test specificity            0.7589      0.7447     0.1707  3
  test precision              0.5201      0.4783     0.0914  3
  test loss                   0.6083      0.5983     0.0432  3
  FPR (FP/(FP+TN))            0.2411      0.2553     0.1707  3
  FNR (FN/(FN+TP))            0.5362      0.5217     0.2395  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6073      0.6427     0.0773  3
  max valid BA                0.6649      0.7247     0.1161  3
  best valid F1               0.5406      0.6462     0.1862  3
  test BA                     0.5652      0.5583     0.0685  3
  test F1                     0.3572      0.4314     0.2516  3
  test sensitivity            0.4638      0.4783     0.4132  3
  test specificity            0.6667      0.6383     0.2777  3
  test precision              0.3810      0.3929     0.0429  3
  test loss                   1.0904      1.2103     0.2713  3
  FPR (FP/(FP+TN))            0.3333      0.3617     0.2777  3
  FNR (FN/(FN+TP))            0.5362      0.5217     0.4132  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5893      0.6053     0.0733  3
  max valid BA                0.6245      0.6129     0.0498  3
  best valid F1               0.6328      0.6321     0.0415  3
  test BA                     0.5762      0.5848     0.0232  3
  test F1                     0.5979      0.5926     0.0112  3
  test sensitivity            0.8154      0.7538     0.1202  3
  test specificity            0.3371      0.4157     0.1663  3
  test precision              0.4764      0.4851     0.0240  3
  test loss                   0.8032      0.7759     0.0879  3
  FPR (FP/(FP+TN))            0.6629      0.5843     0.1663  3
  FNR (FN/(FN+TP))            0.1846      0.2462     0.1202  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6319      0.6667     0.1185  3
  max valid BA                0.7130      0.6875     0.0630  3
  best valid F1               0.6157      0.5758     0.0859  3
  test BA                     0.5903      0.6319     0.0783  3
  test F1                     0.3402      0.5000     0.2948  3
  test sensitivity            0.3333      0.4722     0.2900  3
  test specificity            0.8472      0.7917     0.1339  3
  test precision              0.5224      0.5224     0.0125  2
  test loss                   0.6439      0.6496     0.0236  3
  FPR (FP/(FP+TN))            0.1528      0.2083     0.1339  3
  FNR (FN/(FN+TP))            0.6667      0.5278     0.2900  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7353      0.7353     0.0294  3
  max valid BA                0.7451      0.7500     0.0370  3
  best valid F1               0.6630      0.6667     0.0390  3
  test BA                     0.6078      0.6324     0.0425  3
  test F1                     0.5063      0.5143     0.0250  3
  test sensitivity            0.5882      0.5882     0.0588  3
  test specificity            0.6275      0.6765     0.1390  3
  test precision              0.4518      0.4762     0.0639  3
  test loss                   0.6395      0.6338     0.0250  3
  FPR (FP/(FP+TN))            0.3725      0.3235     0.1390  3
  FNR (FN/(FN+TP))            0.4118      0.4118     0.0588  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.625     4.000              0.348         0.495   5.000               0.467          0.658
GLTP                     0.595         0.484    0.479     2.000              0.488         0.551   3.000               0.494          0.459
IP_trans                 0.727         0.726    0.679     3.000              0.719         0.691   2.667               0.664          0.591
LBP_BPI_CETP             0.721         0.811    0.736     2.000              0.812         0.764   1.667               0.792          0.580
START                    0.574         0.487    0.536     3.000              0.461         0.500   4.000               0.517          0.526
lipocalin                0.558         0.302    0.627     5.000              0.222         0.691   2.000               0.681          0.508
scp2                     0.632         0.430    0.710     2.667              0.528         0.662   2.667               0.630          0.582

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.627               0.630                  0.067                     0.093

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.622               0.625                  0.079                     0.106

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.558               0.542                  0.140                     0.065

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.572      0.511     0.574
10     0.531  0.590      0.511     0.576
49     0.531  0.571      0.511     0.556
51     0.531  0.594      0.511     0.570
120    0.531  0.627      0.511     0.622

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.670      0.046          0.656              0.683           0.027
10        0.623         0.656      0.033          0.656              0.685           0.029
49        0.623         0.684      0.061          0.656              0.709           0.053
51        0.623         0.681      0.058          0.656              0.703           0.048
120       0.623         0.675      0.052          0.656              0.703           0.047

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.625      0.348     0.495     0.525         0.621      0.096          0.589              0.682           0.092
GLTP          0.484  0.479      0.488     0.551     0.519         0.571      0.052          0.547              0.599           0.052
IP_trans      0.726  0.679      0.719     0.691     0.726         0.767      0.041          0.729              0.779           0.050
LBP_BPI_CETP  0.811  0.736      0.812     0.764     0.811         0.820      0.009          0.815              0.827           0.012
START         0.487  0.536      0.461     0.500     0.513         0.579      0.066          0.559              0.614           0.054
lipocalin     0.302  0.627      0.222     0.691     0.698         0.709      0.011          0.696              0.716           0.019
scp2          0.430  0.710      0.528     0.662     0.570         0.660      0.090          0.655              0.705           0.050

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.627               0.630                  0.067                     0.093
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.675               0.651                  0.050                     0.095
increment         0.052               0.038                  0.038                     0.035

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.622               0.625                  0.079                     0.106
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.703               0.716                  0.071                     0.082
increment_prot         0.047               0.040                  0.049                     0.026
```
