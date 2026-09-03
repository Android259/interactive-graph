# geometric_edge_mlp_protgeom_family_neutral_dro

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_dro'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.9204      0.2295      0.5076      0.5692      0.8756      0.2258
groups_GLTP            3      0.6267      0.3867      0.7239      0.4892      0.5897      0.5000
groups_IP_trans        3      0.3768      0.7376      0.7062      0.5266      0.5139      0.7518
groups_LBP_BPI_CETP    3      0.5217      0.5957      0.6091      0.6632      0.5556      0.6241
groups_START           3      0.6154      0.4082      0.7031      0.5802      0.6146      0.4419
groups_lipocalin       3      0.6574      0.6944      0.7278      0.5194      0.7685      0.6852
groups_scp2            3      0.6863      0.5294      0.7355      0.4620      0.7647      0.6471
ALL                   21      0.6292      0.5117      0.6733      0.5443      0.6689      0.5537

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6113      0.6006     0.0833  21
max valid BA                0.6928      0.7132     0.0817  21
best valid F1               0.6723      0.6667     0.0517  21
test BA                     0.5704      0.5596     0.0728  21
test F1                     0.5017      0.5385     0.1757  21
test sensitivity            0.6292      0.6667     0.3069  21
test specificity            0.5117      0.5972     0.3243  21
test precision              0.4829      0.5000     0.0969  20
test loss                   0.7817      0.6954     0.3039  21
FPR (FP/(FP+TN))            0.4883      0.4028     0.3243  21
FNR (FN/(FN+TP))            0.3708      0.3333     0.3069  21

=== abs(sensitivity-specificity) gap: mean=0.5265 median=0.4752 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5507      0.5437     0.0216  3
  max valid BA                0.6092      0.6306     0.0676  3
  best valid F1               0.7062      0.6993     0.0166  3
  test BA                     0.5750      0.5670     0.0205  3
  test F1                     0.7017      0.7033     0.0096  3
  test sensitivity            0.9204      0.9552     0.0736  3
  test specificity            0.2295      0.1639     0.1136  3
  test precision              0.5688      0.5603     0.0180  3
  test loss                   0.7561      0.7357     0.0958  3
  FPR (FP/(FP+TN))            0.7705      0.8361     0.1136  3
  FNR (FN/(FN+TP))            0.0796      0.0448     0.0736  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5449      0.5192     0.0618  3
  max valid BA                0.6603      0.6731     0.0777  3
  best valid F1               0.7116      0.6849     0.0544  3
  test BA                     0.5067      0.5000     0.0115  3
  test F1                     0.5318      0.5385     0.1383  3
  test sensitivity            0.6267      0.5600     0.3449  3
  test specificity            0.3867      0.4800     0.3495  3
  test precision              0.5062      0.5000     0.0107  3
  test loss                   0.7134      0.7152     0.0171  3
  FPR (FP/(FP+TN))            0.6133      0.5200     0.3495  3
  FNR (FN/(FN+TP))            0.3733      0.4400     0.3449  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6328      0.6033     0.0535  3
  max valid BA                0.7072      0.7132     0.0634  3
  best valid F1               0.6300      0.6389     0.0635  3
  test BA                     0.5572      0.5467     0.0723  3
  test F1                     0.3671      0.3913     0.1745  3
  test sensitivity            0.3768      0.3913     0.2395  3
  test specificity            0.7376      0.7021     0.1005  3
  test precision              0.3860      0.3913     0.0835  3
  test loss                   0.6151      0.6009     0.0468  3
  FPR (FP/(FP+TN))            0.2624      0.2979     0.1005  3
  FNR (FN/(FN+TP))            0.6232      0.6087     0.2395  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5898      0.5931     0.0457  3
  max valid BA                0.7531      0.7358     0.0395  3
  best valid F1               0.6732      0.6557     0.0398  3
  test BA                     0.5587      0.5666     0.0447  3
  test F1                     0.4143      0.4000     0.0795  3
  test sensitivity            0.5217      0.3043     0.4148  3
  test specificity            0.5957      0.8723     0.4976  3
  test precision              0.4722      0.5000     0.1273  3
  test loss                   0.8185      0.7522     0.2556  3
  FPR (FP/(FP+TN))            0.4043      0.1277     0.4976  3
  FNR (FN/(FN+TP))            0.4783      0.6957     0.4148  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5283      0.5237     0.0308  3
  max valid BA                0.5982      0.5938     0.0364  3
  best valid F1               0.6211      0.6122     0.0180  3
  test BA                     0.5118      0.5000     0.0239  3
  test F1                     0.3915      0.5612     0.3400  3
  test sensitivity            0.6154      0.8462     0.5385  3
  test specificity            0.4082      0.1461     0.5136  3
  test precision              0.4310      0.4310     0.0158  2
  test loss                   1.2290      1.0218     0.6741  3
  FPR (FP/(FP+TN))            0.5918      0.8539     0.5136  3
  FNR (FN/(FN+TP))            0.3846      0.1538     0.5385  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7269      0.7292     0.0175  3
  max valid BA                0.7616      0.7500     0.0263  3
  best valid F1               0.6803      0.6667     0.0330  3
  test BA                     0.6759      0.6667     0.0493  3
  test F1                     0.5728      0.5393     0.0633  3
  test sensitivity            0.6574      0.6667     0.2085  3
  test specificity            0.6944      0.5972     0.1684  3
  test precision              0.5454      0.5167     0.1098  3
  test loss                   0.6728      0.6680     0.0262  3
  FPR (FP/(FP+TN))            0.3056      0.4028     0.1684  3
  FNR (FN/(FN+TP))            0.3426      0.3333     0.2085  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7059      0.7206     0.0389  3
  max valid BA                0.7598      0.7500     0.0594  3
  best valid F1               0.6835      0.6667     0.0743  3
  test BA                     0.6078      0.6471     0.1084  3
  test F1                     0.5326      0.5652     0.0772  3
  test sensitivity            0.6863      0.7059     0.0899  3
  test specificity            0.5294      0.5294     0.2647  3
  test precision              0.4536      0.4483     0.1320  3
  test loss                   0.6674      0.6752     0.0511  3
  FPR (FP/(FP+TN))            0.4706      0.4706     0.2647  3
  FNR (FN/(FN+TP))            0.3137      0.2941     0.0899  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.450     4.000              0.348         0.413   5.000               0.467          0.551
GLTP                     0.595         0.484    0.531     2.000              0.488         0.530   3.000               0.494          0.508
IP_trans                 0.727         0.726    0.557     3.000              0.719         0.546   2.667               0.664          0.385
LBP_BPI_CETP             0.721         0.811    0.601     2.000              0.812         0.610   1.667               0.792          0.496
START                    0.574         0.487    0.569     3.000              0.461         0.508   4.000               0.517          0.459
lipocalin                0.558         0.302    0.417     5.000              0.222         0.475   2.000               0.681          0.422
scp2                     0.632         0.430    0.684     2.667              0.528         0.662   2.667               0.630          0.699

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.544               0.519                  0.106                     0.090

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.535               0.508                  0.144                     0.083

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.503               0.491                  0.118                     0.103

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.531      0.511     0.530
10     0.531  0.550      0.511     0.531
49     0.531  0.536      0.511     0.540
51     0.531  0.524      0.511     0.533
120    0.531  0.544      0.511     0.535

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.666      0.042          0.656              0.699           0.043
10        0.623         0.664      0.041          0.656              0.689           0.033
49        0.623         0.676      0.053          0.656              0.701           0.046
51        0.623         0.656      0.032          0.656              0.675           0.019
120       0.623         0.676      0.052          0.656              0.705           0.050

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.450      0.348     0.413     0.525         0.555      0.030          0.589              0.632           0.043
GLTP          0.484  0.531      0.488     0.530     0.519         0.626      0.107          0.547              0.656           0.109
IP_trans      0.726  0.557      0.719     0.546     0.726         0.757      0.031          0.729              0.785           0.056
LBP_BPI_CETP  0.811  0.601      0.812     0.610     0.811         0.813      0.002          0.815              0.826           0.010
START         0.487  0.569      0.461     0.508     0.513         0.595      0.082          0.559              0.614           0.054
lipocalin     0.302  0.417      0.222     0.475     0.698         0.701      0.003          0.696              0.700           0.004
scp2          0.430  0.684      0.528     0.662     0.570         0.683      0.112          0.655              0.725           0.071

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.544               0.519                  0.106                     0.090
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.676               0.679                  0.065                     0.091
increment         0.052               0.029                  0.046                     0.047

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.535               0.508                  0.144                     0.083
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.705               0.697                  0.058                     0.079
increment_prot         0.050               0.021                  0.045                     0.036
```
